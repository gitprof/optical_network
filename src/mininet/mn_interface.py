

import imp
import os
import time
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, Node, Host
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import Link, Intf


running_script_dir = os.path.dirname(os.path.abspath(__file__))
global_dir = os.path.join(os.path.split(running_script_dir)[0], 'main')
Global  = imp.load_source('Global', os.path.join(global_dir, 'Global.py'))
from Global import *
OptNet  = imp.load_source('OpticalNetwork', os.path.join(MAIN_DIR, 'OpticalNetwork.py'))
MmSrlg  = imp.load_source('MM_SRLG',        os.path.join(MAIN_DIR, 'MM_SRLG.py'))


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

'''

''' topo-2paths '''
def create_topo1(net):
    # Add hosts and switches
    h1 = net.addHost( 'h1', ip='0.0.0.0' )
    h2 = net.addHost( 'h2', ip='0.0.0.0' )
    s1 = net.addSwitch( 's1' )
    s2 = net.addSwitch( 's2' )
    s3 = net.addSwitch( 's3' )
    s4 = net.addSwitch( 's4' )
    s5 = net.addSwitch( 's5' )
    s6 = net.addSwitch( 's6' )

    # Add links
    net.addLink( h1, s1 )
    net.addLink( h2, s2 )
    net.addLink( s1, s3 )
    net.addLink( s1, s5 )
    net.addLink( s2, s4 )
    net.addLink( s2, s6 )
    net.addLink( s3, s4 )
    net.addLink( s5, s6 )



class TopoFormat(Topo):

    def __init__(self):
        Topo.__init__(self)

    def set_topo(self, optNet):
        switches = {}
        for node in optNet.nodes():
            switches[node] = self.addSwitch('s%d' % node, mac = "")

        for edge in optNet.physical_links():
            self.addLink(switches[edge[0]], switches[edge[1]])

        for node in optNet.get_logical_nodes():
            host = self.addHost('h%d'% node, ip='0.0.0.0')
            self.addLink(switches[node], host)

HOST_CMD="~/mininet/util/m"
RUNNING_OPT_NET = None
#RUNNING_OPT_NET_FILE = GRAPH_2PATHS
RUNNING_OPT_NET_FILE = GRAPH_STAR
CONTROLLER_IP='127.0.0.1'

class MNInterface(object):
    def __init__(self):
        demo = 0
        self.debug = register_debugger()
        self.net = None
        self.host_to_ip = {}
        #self.running_opt_net = RUNNING_OPT_NET

    def optical_network_to_mn_topo(self):
        #self.verify()
        topoFormat = TopoFormat()
        topoFormat.set_topo(RUNNING_OPT_NET)
        return topoFormat

    def get_running_opt_net(self):
        global RUNNING_OPT_NET

        if None == RUNNING_OPT_NET:
            set_running_opt_net()
        return RUNNING_OPT_NET


    def set_running_opt_net(self, graph_file, pathing_algo):
        global RUNNING_OPT_NET
        RUNNING_OPT_NET = OptNet.OpticalNetwork()
        RUNNING_OPT_NET.init_graph_from_file(graph_file)
        logical_paths = []
        if   'MANUAL'  == pathing_algo:   # this is for testing purposes
            logical_paths = [[1,5,6,3], [2,5,6,4]]
        elif 'MM_SRLG' == pathing_algo:
            mmSrlg = MmSrlg.MM_SRLG_solver()
            logical_paths = mmSrlg.mm_srlg(RUNNING_OPT_NET)
        else:
            self.debug.assrt(False, "set_running_opt_net: Unkown pathing algorithm!")
        RUNNING_OPT_NET.l_net = logical_paths

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
                cmd="%s %s ifconfig %s | grep inet | grep -v inet6 | cut -d: -f2 | awk '{print $1}'" % (HOST_CMD, node.name, intf)
                ip = os.popen(cmd).read() # TODO: need to replace it with subprocess.call. or at least remove the output
                self.host_to_ip[node.name] = ip
                assert (ip != "") and (ip != "0"), "Dhclient %s didnt get IP addr for %s!" % (node.name, intf)
                self.debug.logger("IP:%s %s" % (node.name, ip) )


    def set_arp_tables(self):
        self.verify()
        for node in self.net.values():
            if isinstance(node, Host):
                assert self.host_to_ip != None, "set_arp_tables: host didnt assigned with IP!"
                ip  = self.host_to_ip[node]
                mac = node.MAC()
                self.debug.logger("set_arp_tables: node=%s. ip=%s. mac=%s" % (node.name, ip, mac) )
                node.setARP(ip, mac)


    def start_mn_session(self, opt_net_file = RUNNING_OPT_NET_FILE, controller = None):
        self.set_running_opt_net(opt_net_file, 'MANUAL')

        _topo = self.optical_network_to_mn_topo()
        self.net = Mininet( topo=_topo,
                    build=False)

        if controller != None:
            POX_DIR="~/pox"
            start_controller_cmd="%s %s/pox.py" % (POX_DIR)
            cmd="sudo xterm %s" % (start_controller_cmd)
            os.popen(cmd)
            self.controller_ip = CONTROLLER_IP
            self.net.addController( 'c0',
                            controller=RemoteController,
                            ip=self.controller_ip,
                            port=6633)

        #create_topo2(net)
        self.net.start()
        # self.set_dhclients()
        CLI( self.net )
        self.net.stop()


    def dpid_to_optnetid(self, dpid):
        return int(dpid)

    def optnetid_to_dpid(self, optnetid):
        return optnetid

if "__main__" == __name__:
    setLogLevel( 'info' )
    mnInterface = MNInterface()
    mnInterface.start_mn_session()
    #sanity_test()


