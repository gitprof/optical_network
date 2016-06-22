

import imp
import os
import sys
from mininet.topo import Topo
from mininet.log import setLogLevel, info

sys.path.append("/home/mininet/optical_network")
sys.path.append("/home/mininet/optical_network/src")
#sys.path.append("/home/mininet/optical_network/src/mininet")
import src.mininet.mn_interface as MNInterface
#MNInterface = imp.load_source('mn_interface',        os.path.join(BASE_DIR, 'src', 'mininet', 'mn_interface.py'))



running_script_dir = os.path.dirname(os.path.abspath(__file__))
global_dir = os.path.join(os.path.split(running_script_dir)[0], 'main')
Global  = imp.load_source('Global', os.path.join(global_dir, 'Global.py'))
from Global import *
OptNet  = imp.load_source('OpticalNetwork', os.path.join(MAIN_DIR, 'OpticalNetwork.py'))
MmSrlg  = imp.load_source('MM_SRLG',        os.path.join(MAIN_DIR, 'MM_SRLG.py'))




EXAMPLE_DIR="~/mininet/examples/test"
EXAMPLE_TESTS = [
			'test_multiping.py',
			'test_multilink.py',
			'test_multitest.py',
			'test_simpleperf.py',
			'test_clusterSanity.py'
		]

debug = None

def run_mn_examples():
    tests =  EXAMPLE_TESTS
    for test in tests:
        cmd='%s/%s' % (EXAMPLE_DIR, test)
        os.system(cmd)
        #res = os.popen(cmd).read()


def mn_test(graph_file, pathing_algo, paths, controller):
    debug.logger("mn_test: graphfile=%s. " % (graph_file))
    mnInterface = MNInterface.MNInterface(opt_net_file = graph_file,
                                          pathing_algo = pathing_algo,
                                          paths        = paths)
    mnInterface.start_mn_session(controller = controller,
                               staticArp = False,
                               Cli  = True,
                               Test = False,
                               Monitor = False,
                               Dump = False,
                               Hold = False)


def mn_generic_tests():
    graphs_and_paths = [
                         # ('2paths.g', [[1,3,2]]),
                         # ('complex.g', [[1,4,3], [2,5,7,6,4,1], [3,4,5,2]]),
                         # ('star.g', [[1,5,6,3],[3,6,5,2],[2,5,6,4]]),
                         # ('tree.g', [[5,1,4,2]]),
                          ('tmp.g', [[1,4,2], [3,4,2], [1,4,3]]),
                         # ('two.g', [[1,3,2]]),
                       ]
    for g_p in graphs_and_paths:
	mn_test(graph_file   = os.path.join(GRAPH_DIR, g_p[0]),
	        pathing_algo = 'MANUAL',
		    paths        = g_p[1],
	        controller   = 'RYU')

def run_tests():
    #run_mn_examples()
    mn_generic_tests()


if "__main__" == __name__:
    setLogLevel( 'info' )
    debug = register_debugger()
    run_tests()
    close_debugger()


