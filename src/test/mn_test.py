

import imp
import os
from mininet.topo import Topo
from mininet.log import setLogLevel, info

running_script_dir = os.path.dirname(os.path.abspath(__file__))
global_dir = os.path.join(os.path.split(running_script_dir)[0], 'main')
Global  = imp.load_source('Global', os.path.join(global_dir, 'Global.py'))
from Global import *
OptNet  = imp.load_source('OpticalNetwork', os.path.join(MAIN_DIR, 'OpticalNetwork.py'))
MmSrlg  = imp.load_source('MM_SRLG',        os.path.join(MAIN_DIR, 'MM_SRLG.py'))
MNInterface = imp.load_source('mn_interface',        os.path.join(BASE_DIR, 'src', 'mininet', 'mn_interface.py'))


EXAMPLE_DIR="~/mininet/examples/test"
EXAMPLE_TESTS = ['test_multiping.py', 'test_multitest.py', 'test_simpleperf.py', 'test_clusterSanity.py']

debug = None

def run_mn_examples():
    tests =  EXAMPLE_TESTS
    for test in tests:
        cmd='%s/%s' % (EXAMPLE_DIR, test)
        os.system(cmd)
        #res = os.popen(cmd).read()  
    

def mn_test(graph_file, controller, pathing_algo, paths):
    debug.logger("mn_test: graphfile=%s. " % (graph_file))
    mnInterface = MNInterface.MNInterface()
    mnInterface.start_mn_session(opt_net_file = graph_file, controller = controller, pathing_algo = pathing_algo, paths = paths)

def mn_generic_tests():
    graphs_and_paths = [
                       # (GRAPH_2PATHS, [[1,3,2]]), 
                        (GRAPH_STAR, [[1,5,6,3]]),
                        (GRAPH_TREE, [[5,1,4,2]]),
                       ]
    for g_p in graphs_and_paths:
	mn_test(graph_file = g_p[0], controller = 'MANUAL', pathing_algo = 'MANUAL', paths = g_p[1] )

def run_tests():
    run_mn_examples()
    mn_generic_tests()


if "__main__" == __name__:
    #setLogLevel( 'info' )
    debug = register_debugger()
    run_tests()
    close_debugger()


