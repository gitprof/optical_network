
import pickle as pk
import subprocess
import imp
import os
import copy
import time
import sys
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, Node, Host
from mininet.cli import CLI
from mininet.util import custom
from mininet.log import setLogLevel, info
from mininet.link import Link, Intf, TCIntf


running_script_dir = os.path.dirname(os.path.abspath(__file__))
global_dir = os.path.join(os.path.split(running_script_dir)[0], 'main')
Global  = imp.load_source('Global', os.path.join(global_dir, 'Global.py'))
from Global import *
OptNet  = imp.load_source('OpticalNetwork', os.path.join(MAIN_DIR, 'OpticalNetwork.py'))
MmSrlg  = imp.load_source('MM_SRLG',        os.path.join(MAIN_DIR, 'MM_SRLG.py'))
DP      = imp.load_source('DP',             os.path.join(MAIN_DIR, 'DP.py'))
ProcessIperfRes  = imp.load_source('process_iperf_res',             os.path.join(TEST_DIR, 'process_iperf_res.py'))



'''
Interface Mininet<->OpticalNetwork
some pointers:
    * assuming optnet graph file contain nodes names: s1,s2,r3,s4,r5,r6 ...
        i.e: s for switch and r for router. all numbers are differnt.
        there may be skips (but why)
    * converting to mininet nodes: every sx stay sx, every rx converted to: switch named sx, and host
                name hx, connected to this switch.
    * => every host is linked to 1 switch
    * we assume that switch.dpid is just int(switch.name)

Handling Multi Python Processes:
    Problem: need to sync controller with the running mininet test session which in another process.
    Solution: not very pretty, but we use it for now. the things that need to be shared with the controller is the physical and logical
        graphs. there are 3 object define those:
         1. graph file
         2. pathing algo
         3. pathing algo params if needed. for example for 'MANUAL' "algo" we need explicit paths. for an algo
            with some random elements we need seed
        we will write those to file in 3 lines, and let the controller read it, execute the algo itself. ze ma yesh.


'''

# a bit more than 10
CAPACITY_TO_MBITS = 14
MAX_MBITS = OptNet.MAX_EDGE_CAPACITY * CAPACITY_TO_MBITS


class TopoFormat(Topo):

    def __init__(self):
        Topo.__init__(self)

    def hostid_to_mac(self, hostid):
        return "00:00:00:00:00:"+str(hex(hostid)[2:])

    # the order of the insertion of host, switches and links is important:
    # TODO: need to see how this effect mapping for mac, ids, dpids and all the rest...
    def set_topo(self, optNet, init_ip = False, init_mac = False):

        # add hosts
        hosts = {}
        for node in optNet.get_logical_nodes():
            if init_ip and init_mac:
                host = self.addHost('h%d'% node, ip='0.0.0.0', mac=self.hostid_to_mac(node)) #DONT DO IT UNLESS U SET DHCLIENTS
            elif init_ip:
                host = self.addHost('h%d'% node, ip='0.0.0.0') #DONT DO IT UNLESS U SET DHCLIENTS
            if init_mac:
                host = self.addHost('h%d'% node, mac=self.hostid_to_mac(node))
            else:
                host = self.addHost('h%d'% node)
            hosts[node] = host

        # add switches
        switches = {}
        for node in optNet.nodes():
            switches[node] = self.addSwitch('s%d' % node, mac = "")


        # link hosts to switches
        for node in optNet.get_logical_nodes():
            _bw = 2 * MAX_MBITS
            intf = custom( TCIntf, bw=_bw )
            self.addLink(switches[node], hosts[node], intf=intf )

        # link switches
        for edge in optNet.physical_links():
            if edge[0] in switches.keys() and edge[1] in switches.keys():
                _bw = CAPACITY_TO_MBITS * optNet.get_plink_capacity(edge)
                intf = custom( TCIntf, bw=_bw )
                self.addLink(switches[edge[0]], switches[edge[1]], intf=intf)


PICKLES_JAR=os.path.join(BASE_DIR, "src", "mininet", "pickles")
PICKLED_GRAPH=os.path.join(PICKLES_JAR, "graph")
PICKLED_LOGICAL_PATHS=os.path.join(PICKLES_JAR, "logical_paths")
PICKLED_HOSTS=os.path.join(PICKLES_JAR, "hosts")


RUNNING_OPT_NET = None
RUNNING_OPT_NET_FILE = os.path.join(BASE_DIR, 'running_opt_net.dump')
RUNNING_INTERFACE = None
DEFAULT_RUNNING_GRAPH_FILE = os.path.join(GRAPH_DIR, 'two.g')
DEFAULT_PATHING_ALGO='MANUAL'
DEFAULT_PATHS=[[1,3,2]]

CONTROLLER_IP='127.0.0.1'
DNS_IP="10.0.2.3/255.255.255.0"
DNS_MAC="52:54:00:12:35:03"

DUMP_NET_DATA_SCRIPT=os.path.join(BASE_DIR, 'src', 'mininet', 'dump_net_data.sh')
DUMP_NET_OUTPUT_FILE=os.path.join(BASE_DIR, 'logs', 'dump_net.log')

SSH_HOST="~/mininet/util/m"
CONTROLLER_LOG_FILE="/tmp/controller.log"
RYU_DIR="/home/mininet/ryu"
POX_DIR="/home/mininet/pox"

RESTIME = 5


class MNInterface(object):
    def __init__(self, opt_net_file = DEFAULT_RUNNING_GRAPH_FILE,
                       pathing_algo = 'MANUAL',
                       pathing_algo_params = {}):
        global RUNNING_INTERFACE
        self.debug = register_debugger()
        self.net = None
        self.host_to_ip = {}
        self.ctrlr_params = None
        self.set_running_opt_net(opt_net_file, pathing_algo, pathing_algo_params)
        RUNNING_INTERFACE = self

    def use_dhclient_controller(self):
    	return (None != self.ctrlr_params) and (self.ctrlr_params.find('topo_proactive') != -1)


    def optical_network_to_mn_topo(self):
        #self.verify()
        topoFormat = TopoFormat()
    	init_ip = self.use_dhclient_controller()
        init_mac = self.set_simple_mac
        topoFormat.set_topo(RUNNING_OPT_NET, init_ip, init_mac)
        return topoFormat

    def serialize_opt_net(self, graph_file, logical_paths, hosts):
        self.debug.logger("serialize_opt_net: hosts=%s" % (hosts))
        if not os.path.exists(PICKLES_JAR):
            os.mkdir(PICKLES_JAR)
        with open(PICKLED_GRAPH,         'wb') as f:
            pk.dump(graph_file, f)
        with open(PICKLED_LOGICAL_PATHS, 'wb') as f:
            pk.dump(logical_paths, f)
        with open(PICKLED_HOSTS,         'wb') as f:
            pk.dump(hosts, f)


    # these 2 methods probaby deprecated, we will use serialization
    def get_running_opt_net(self):
        global RUNNING_OPT_NET

        if None == RUNNING_OPT_NET:
            assert False, "get_running_opt_net: No running opt net!"
            #self.set_running_opt_net()
        self.debug.logger("get_running_opt_net: physical_opt_net=%s" % (RUNNING_OPT_NET.physical_links()))
        self.debug.logger("get_running_opt_net: logical_net=%s" % (RUNNING_OPT_NET.get_logical_network().get_paths()))
        return RUNNING_OPT_NET

    def print_logical_paths_to_file(self, pathing_algo, graph_file, logical_paths):
        graph_name=os.path.split(graph_file)[1]
        filename="%s_%s" % (pathing_algo, graph_name)
        full_file_path=os.path.join(TEST_RESULTS_DIR, filename)
        with open(full_file_path, 'w') as f:
            f.write(str(logical_paths))

    def set_running_opt_net(self, graph_file, pathing_algo, pathing_algo_params):
        global RUNNING_OPT_NET
        #self.debug.assrt((pathing_algo == 'MANUAL') != (paths == None), "set_running_opt_net: conflicts pathing_algo and paths!" )
        RUNNING_OPT_NET = OptNet.OpticalNetwork()
        RUNNING_OPT_NET.init_graph_from_file(graph_file)
        logical_paths = []
        if 'MANUAL'  == pathing_algo:   # this is for testing purposes
            #mmSrlg = MmSrlg.MM_SRLG_solver()                 # TODO: this is debug
            #logical_paths = mmSrlg.solve(RUNNING_OPT_NET)  # this is just for debugging, need to remove
            paths = pathing_algo_params['paths']
            logical_paths = paths
            RUNNING_OPT_NET.l_net.init_from_paths(logical_paths)
        elif 'MM_SRLG' == pathing_algo:
            algo = MmSrlg.MM_SRLG_solver()
            algo.solve(RUNNING_OPT_NET)
        elif 'MM_SRLG_VAR' == pathing_algo:
            algo = MmSrlg.MM_SRLG_solver()
            algo.solve(RUNNING_OPT_NET, optimized = True)
        elif 'DP'      == pathing_algo:
            algo = DP.DP()
            algo.solve(RUNNING_OPT_NET)
        else:
            self.debug.assrt(False, "set_running_opt_net: Unkown pathing algorithm!")
        self.running_opt_net = RUNNING_OPT_NET
        logical_paths = self.running_opt_net.l_net.get_paths()
        self.debug.logger("logical_paths=%s" % (logical_paths))
        self.print_logical_paths_to_file(pathing_algo, graph_file, logical_paths)
        #hosts = [host[1:] for host in self._topo.hosts()]
        hosts = self.running_opt_net.get_logical_nodes()
        self.serialize_opt_net(graph_file, logical_paths, hosts)

    def verify(self):
        self.debug.assrt(self.net != None, "MNInterface: attempt to use uninitialized mn!")
        self.debug.assrt(RUNNING_OPT_NET != None, "MNInterface: attempt to use uninitialized opt_net!")
        #raise exception()

    def set_dhclients(self):
        self.verify()
        for node in self.net.values():
            if isinstance(node, Host):
                #node.cmdPrint('dhclient '+node.defaultIntf().name)
                node.sendCmd('dhclient '+node.defaultIntf().name)
                time.sleep(2) # wait for IP allocation ...
                intf='%s-eth0' % node.name
                # ip = ni.ifaddresses(intf)[ni.AF_INET][0]['addr']
                cmd="%s %s ifconfig %s | grep inet | grep -v inet6 | cut -d: -f2 | awk '{print $1}'" % (SSH_HOST, node.name, intf)
                #os.system(cmd)  # TODO: need to replace it with subprocess.call. or at least remove the output
                ip = 0
                self.host_to_ip[node.name] = ip
                #assert (ip != "") and (ip != "0"), "Dhclient %s didnt get IP addr for %s!" % (node.name, intf)
                #self.debug.logger("IP:%s %s" % (node.name, ip) )

    def set_dns_in_arp_tables(self):
        self.verify()
        for node in self.net.values():
            if isinstance(node, Host):
                #assert self.host_to_ip != None, "set_arp_tables: host didnt assigned with IP!"
                dns_ip  = DNS_IP
                dns_mac = DNS_MAC
                self.debug.logger("set_dns_in_arp_tables: node=%s. ip=%s. mac=%s" % (node.name, dns_ip, dns_mac) )
                node.setARP(dns_ip, dns_mac)


    def set_controller_params(self):
	if 'POX' == self.ctrlr_type:
        	self.ctrlr_dir=POX_DIR
		ctrlr_params_debug="info.packet_dump log.level --DEBUG samples.pretty_log"
		#self.ctrlr_params="forwarding.l3_learning        openflow.discovery openflow.spanning_tree --no-flood --hold-down    %s" % (ctrlr_params_debug)
		self.ctrlr_params="forwarding.l3_learning        openflow.discovery			                            %s" % (ctrlr_params_debug)
		#self.ctrlr_params="forwarding.topo_proactive     openflow.discovery						    %s" % (ctrlr_params_debug)
		#self.ctrlr_params="forwarding.l3_static_routing  openflow.discovery						    %s" % (ctrlr_params_debug)
	elif 'RYU' == self.ctrlr_type:
        	self.ctrlr_dir=RYU_DIR
		ctrlr_params_debug="--verbose"
		#self.ctrlr_params="%s/ryu/app/simple_switch.py  %s" % (self.ctrlr_dir, ctrlr_params_debug)
		self.ctrlr_params="--observe-links %s/ryu/app/static_routing.py  %s" % (self.ctrlr_dir, ctrlr_params_debug)
		#self.ctrlr_params="--observe-links %s/ryu/app/shortestpath.py  %s" % (self.ctrlr_dir, ctrlr_params_debug)
		#self.ctrlr_params="ryu/topology/switches.py  %s" % (ctrlr_params_debug)
		#self.ctrlr_params="ryu/app/rest_router.py  %s" % (ctrlr_params_debug)
		#self.ctrlr_params="ryu/app/simple_switch_stp.py  %s" % (ctrlr_params_debug)
		#self.ctrlr_params="ryu/app/simple_switch_13.py  %s" % (ctrlr_params_debug) # no supported
	else:
		self.debug.assrt(False, 'set_controller_params: Unkown controller!')

    def start_controller(self):
        if   'POX' == self.ctrlr_type:
            start_controller_cmd= "%s/pox.py %s" %  (self.ctrlr_dir, self.ctrlr_params)
        elif 'RYU' == self.ctrlr_type:
            start_controller_cmd= "PYTHONPATH=. %s/bin/ryu-manager %s" %  (self.ctrlr_dir, self.ctrlr_params)
        else:
            self.debug.assrt(False, 'start_controller: Unkown controller!')

        self.controller_logfile = CONTROLLER_LOG_FILE
        dont_show="PacketIn"
        cmd="sudo xterm -geometry 200x50+10+10  -e \"%s |& egrep -v PacketIn  |& tee  %s |& grep OOO  \"  &" % (start_controller_cmd, self.controller_logfile)
        #cmd="sudo %s  &" % (start_controller_cmd)

        self.debug.logger(cmd)
        os.popen(cmd)
        self.controller_ip = CONTROLLER_IP
        time.sleep(RESTIME)
        self.net.addController( 'c0',
                    controller=RemoteController,
                    ip=self.controller_ip,
                    port=6633)


    def dump_net_data(self, _print = False):
        self.debug.logger('dumping data...')
        params=""
        os.system('echo \"--------\" > %s' % (DUMP_NET_OUTPUT_FILE))
        self.debug.logger('dumping FlowTables...')
        for sw in self._topo.switches():
            os.system('echo \"%s flow-table:\" >> %s ' % (sw, DUMP_NET_OUTPUT_FILE))
            cmd="sudo ovs-ofctl dump-flows %s | cut -d\",\" -f 7- >> %s" % (sw, DUMP_NET_OUTPUT_FILE)
            #os.popen(cmd)
            os.system(cmd)

        self.debug.logger('dumping NetAddrs...')
        os.system('echo \"---------\" >> %s' % (DUMP_NET_OUTPUT_FILE))
        for host in self._topo.hosts():
            os.system('echo \"%s IP:\"  >> %s' % (host, DUMP_NET_OUTPUT_FILE  ))
            cmd="sudo %s %s ifconfig %s-eth0 | egrep \"inet|HWaddr\" | grep -v inet6 >> %s" % (SSH_HOST, host, host, DUMP_NET_OUTPUT_FILE)  #  | cut -d: -f2 | awk '{print $1}'
            #os.popen(cmd)
            os.system(cmd)

            if False:
                self.debug.logger('dumping ARPs...')
                os.system('echo \"--------\" >> %s' % (DUMP_NET_OUTPUT_FILE))
                for host in self._topo.hosts():
                    os.system('echo \"%s ARP:\" >> %s' % (host, DUMP_NET_OUTPUT_FILE  ))
                    cmd="sudo %s %s arp >> %s" % (SSH_HOST, host, DUMP_NET_OUTPUT_FILE)  #  | cut -d: -f2 | awk '{print $1}'
                    os.system(cmd)

        self.debug.logger('Print to screen...')
        if _print:
            with file(DUMP_NET_OUTPUT_FILE) as f:
                self.debug.logger(f.read(), log_level = 1)

    def test_ping(self, hosts = None):
        self.debug.logger("test_ping: hosts=%s" % (hosts))
        #if None == hosts:
        #    hosts = self._topo.hosts()
        self.net.pingAll(timeout = RESTIME) # TODO: get host, not names.

    def test_iperf(self, hosts = None):
        self.debug.logger("test_iperf: hosts=%s" % (hosts))
        #if None == hosts:
        #    hosts = self._topo.hosts()

        self.net.iperf(hosts = hosts, l4Type = 'TCP')

    def run_link_failure_test(self, sw_id1, sw_id2):
        hosts = self.running_opt_net.get_logical_nodes()
        cmd = "link %s %s down" % (sw_id1, sw_id2)
        self.debug.logger(cmd)
        if (-1 != sw_id1):
            self.net.configLinkStatus("s%d" % sw_id1, "s%d" % sw_id2, 'down')
        time.sleep(1)
        perf_results = ProcessIperfRes.run_test(hosts)
        cmd = "link %s %s up" % (sw_id1, sw_id2)
        self.debug.logger(cmd)
        if (-1 != sw_id1):
            self.net.configLinkStatus("s%d" % sw_id1, "s%d" % sw_id2, 'up')
        time.sleep(1)
        #print("run_link_failure_test: perf_results=%s " % (perf_results))
        return perf_results

    def test_resillience(self, links_to_fail = None):
        self.debug.logger("test_resillience: links_to_fail=%s" % (links_to_fail))
        self.link_to_perf_results = {}
        if links_to_fail == None:
            links_to_fail = self.running_opt_net.physical_links().keys()
        local_links_to_fail = copy.deepcopy(links_to_fail) + [(-1,-1)]
        for (sw_id1, sw_id2) in local_links_to_fail:
            link = (sw_id1, sw_id2)
            self.link_to_perf_results[link] = self.run_link_failure_test(sw_id1, sw_id2)
            self.link_to_perf_results['TOTAL_CONS'] = self.link_to_perf_results[link]['TOTAL'][2]
            #debug_counter += 1
        #print("test_resillience: link_to_perf_res=%s " % (self.link_to_perf_results))
        return self.link_to_perf_results

    def get_last_test_results(self):
        return self.link_to_perf_results

    def clean_up(self):
        os.popen("sudo killall -9 xterm &> /dev/null") # TODO: kill by PID
        os.popen("sudo mn -c > /dev/null")

    def close_controller(self):
        os.popen("sudo killall -9 xterm > /dev/null") # TODO: kill by PID
        self.debug.logger('controller log file at %s' % (self.controller_logfile))

    def exe_cli(self):
	    CLI( self.net )

    def end_mn_session(self):
        if self.net != None:
            self.net.stop()

        if self.ctrlr_type != None:
            self.close_controller()

    def start_mn_session(self, controller = None,
                               StaticArp = False,
                               Cli  = False,
                               SanityTest = True,
                               Monitor = True,
                               Dump = True,
                               Hold = False,
                               SimpleMac = True):

        self.set_simple_mac = SimpleMac
        self.ctrlr_type = controller
        self.clean_up()
        if controller != None:
            self.set_controller_params()


        self._topo = self.optical_network_to_mn_topo()
        self.net = Mininet( topo=self._topo,  # TODO: run with --mac
                    build=False, autoStaticArp = StaticArp)


        if controller != None:
            self.start_controller()


        self.net.start()
    	time.sleep(int(RESTIME/2))

        if StaticArp == True:
            DONOTHING = 0
            #self.set_dns_in_arp_tables()

        if self.use_dhclient_controller():
	    self.set_dhclients()

        time.sleep(int(RESTIME))

        if Monitor:
            for host in self._topo.hosts():
                cmd="sudo xterm -hold -e \"%s  %s tcpdump -XX -n -i %s-eth0  | egrep -i \"arp\"  \" & " % (SSH_HOST, host, host )
                #cmd="sudo xterm -e \"%s  %s tcpdump -XX -n -i %s-eth0 \" & " % (SSH_HOST, host, host )
                self.debug.logger(cmd)
                os.system(cmd)

        if Dump:
            RUNNING_OPT_NET.draw()

        time.sleep(int(RESTIME/2))

        if Cli:
            self.exe_cli()


        if SanityTest:
            self.test_ping()
            #self.test_iperf()

        if Dump:
            Demo = 0
            #self.dump_net_data(_print = True)

        if Hold:
            raw_input("Press Enter to finish...")
        #time.sleep(RESTIME*2)



    def dpid_to_optnetid(self, dpid):
        return int(dpid)

    def optnetid_to_dpid(self, optnetid):
        return optnetid

def get_running_interface():
    assert RUNNING_INTERFACE != None, "No running mininet interface!"
    return RUNNING_INTERFACE


if "__main__" == __name__:
    setLogLevel( 'info' )
    mnInterface = MNInterface(DEFAULT_RUNNING_GRAPH_FILE, 'MANUAL', [[1,3,2]])
    mnInterface.start_mn_session()
    #sanity_test()


