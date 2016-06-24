
import os
import imp
import sys

from mininet.topo import Topo
from mininet.log import setLogLevel, info

sys.path.append("/home/mininet/optical_network")
sys.path.append("/home/mininet/optical_network/src")
#sys.path.append("/home/mininet/optical_network/src/mininet")

running_script_dir = os.path.dirname(os.path.abspath(__file__))
global_dir = os.path.join(os.path.split(running_script_dir)[0], 'main')
Global  = imp.load_source('Global', os.path.join(global_dir, 'Global.py'))
from Global import *



SUMMARY_FILE=os.path.join(BASE_DIR, "test_logs", "summary.log")
IPERF_TOOL=os.path.join(TEST_DIR, "run_test.sh")

class IperfTester:

    def __init__(self):
        self.debug = register_debugger()

    '''
    Hosts: host list by numbers
    '''
    def run_iperf_test(self, hosts):
        host_param=""
        for host in hosts:
            host_param += " "+str(host)
        os.system("%s %s " % (IPERF_TOOL, host_param))

    ''' Return Dict perf_results:
            con -> bw/fail
            'TOTAL' -> (total_bw, live_cons, total_cons)
    '''
    def process_results(self, summary_file):
        perf_results = {}
        live_connections = 0
        fail_connections = 0
        total_bw = 0
        with open(summary_file) as f:
            lines = f.readlines()
        for line in lines:
            if line[0] == '*':
                continue
            (con, res) = line.split(',')
            if (res.find('fail') != -1) or (res == ''):
                fail_connections += 1
                bw = 'fail'
            else:
                bw = round(float(res), 2)
                total_bw += bw
                live_connections += 1
            perf_results[con] = bw
        num_connections = live_connections + fail_connections
        perf_results['TOTAL'] = (total_bw, live_connections, num_connections)
        self.debug.logger('Live Connections: %s/%s' % (live_connections, num_connections))
        self.debug.logger('Total BW: %s Mbit/s' % (total_bw))
        self.debug.logger('perf_results: ' % (perf_results))
        return perf_results


def run_test(hosts):
    test = IperfTester()
    test.run_iperf_test(hosts)
    return test.process_results(SUMMARY_FILE)



def main_performance_tester():
    run_test([1,2,3,4,5,6,7,8])

debug = None

if "__main__" == __name__:
    debug = register_debugger(master = True)
    main_performance_tester()
    close_debugger()
