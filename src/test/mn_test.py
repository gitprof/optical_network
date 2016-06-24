

import imp
import os
import sys
from mininet.topo import Topo
from mininet.log import setLogLevel, info
import matplotlib.pyplot as plt


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

GRAPHS_WITH_PATHS = [
                         #  ('2paths.g', [[1,3,2],[1,4,2]]),
                          ('test8.g', [[1,4,3], [2,5,7,6,4,1], [3,4,5,2]]),
                         # ('star.g', [[1,5,6,3],[3,6,5,2],[2,5,6,4]]),
                         # ('tree.g', [[2,4,1]]),
                         # ('tmp.g', [[1,4,2], [3,4,2], [1,4,3]]),
                         # ('test2.g', [[1,3,2]]),
                         # ('test3.g', [[2,1,7]]),
                       ]

PATHING_ALGOS = ['MM_SRLG', 'DP']

debug = None


def set_figure(title, x_title, y_title, x_ticks, y_ticks):
    fig = plt.figure()
    #ax = fig.gca()
    #ax.set_xticks(numpy.arrange(0,10,1))
    #ax.set_yticks(numpy.arrange(0,60, 5))

    if x_ticks != []:
        plt.xticks(x_ticks)
    if y_ticks != []:
        plt.yticks(y_ticks)

    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.title(title, fontsize = 14)
    return fig

LOC = 'upper right'
def draw_graph(lstx, lsty, line_shape, legend_value):
    global LOC
    print("draw_graph: {}: {}, {}".format(legend_value, lstx, lsty))
    #myassert(len(lstx) > 0, "draw_graph: list X empty")
    #myassert(len(lsty) > 0, "draw_graph: list Y empty")
    #myassert(len(lstx) == len(lsty), "draw_graph: lists are not equal")
    plt.plot(lstx, lsty, line_shape, linewidth=5, label=legend_value)
    #plt.plot(lstx, lsty) #, linestyle=line_shape, linewidth=15, label=legend_value)
    plt.legend(loc=LOC)
    #LOC = 'upper right'
    #debug("End Graph")


def show_graph(hold = False):
    plt.ion()
    plt.grid()
    plt.show()



def run_mn_examples():
    tests =  EXAMPLE_TESTS
    for test in tests:
        cmd='%s/%s' % (EXAMPLE_DIR, test)
        os.system(cmd)
        #res = os.popen(cmd).read()


def test_unit(graph_file, pathing_algo, paths, controller):
    debug.logger("test_unit: graphfile=%s. " % (graph_file))
    mnInterface = MNInterface.MNInterface(opt_net_file = graph_file,
                                          pathing_algo = pathing_algo,
                                          paths        = paths)
    mnInterface.start_mn_session(controller = controller,
                               staticArp = True,
                               Cli       = False,
                               Test      = True,
                               Monitor   = False,
                               Dump      = True,
                               Hold      = False)

    return mnInterface

def test_algo_comparison(graph_file):
    total_bw_y = {}
    live_cons_y = {}
    for algo in PATHING_ALGOS:
        mnInterface =  test_unit(graph_file   = graph_file,
                                pathing_algo = algo,
                                paths        = None,
                                controller   = 'RYU')

        link_to_perf_results = mnInterface.get_last_test_results()
        total_cons        = link_to_perf_results['TOTAL_CONS']
        failed_links      = [link for link in link_to_perf_results.keys() if (link != 'TOTAL_CONS')]
        total_bw_y[algo]  = [link_to_perf_results[link]['TOTAL'][0] for link in failed_links]
        live_cons_y[algo] = [link_to_perf_results[link]['TOTAL'][1] for link in failed_links]

    ''' Printing Summary Graphs:'''
    line_shapes = ['bs', 'ro']
    # live cons:


    #failed_links = [1,2,3]
    #live_cons_y = {}
    #total_bw_y = {}
    #total_cons = 2

    x_axis = range(len(failed_links))
    enh_x_axis = range(len(failed_links)+2)
    live_cons_fig = set_figure("Live Connections", "link fail", "# live connections", enh_x_axis, range(total_cons+3))
    #plt.plot([1,2,3], [5,6,7])
    #plt.show()
    graph_name = os.path.split(graph_file)[1]
    i = 0
    for algo in PATHING_ALGOS:
        draw_graph(x_axis, live_cons_y[algo], line_shapes[i], "Graph: %s. Algorithm: %s" % (graph_name, algo))
        i += 1
    show_graph()

    i = 0
    # total bw:
    total_bw_fig  = set_figure("Total BWs", "link fail", "total BW in Mbit/s",        enh_x_axis, range(0,100,10)) # TODO: y axis (BW)
    for algo in PATHING_ALGOS:
        draw_graph(x_axis, total_bw_y[algo], line_shapes[i], "Graph: %s. Algorithm: %s" % (graph_name, algo))
        i += 1
    show_graph()

    raw_input("Press Enter to finish...")


def test_graph_comparison(pathing_algo = 'MANUAL'):
    for g_p in GRAPHS_WITH_PATHS:
        paths = g_p[1] if pathing_algo == 'MANUAL' else None

	test_unit(graph_file    = os.path.join(GRAPH_DIR, g_p[0]),
              pathing_algo  = pathing_algo,
              paths         = paths,
              controller    = 'RYU')



def run_tests():
    #run_mn_examples()
    #test_graph_comparison('MM_SRLG')
    #test_graph_comparison('DP')

    for g_p in GRAPHS_WITH_PATHS:
        test_algo_comparison(os.path.join(GRAPH_DIR, g_p[0]))


if "__main__" == __name__:
    setLogLevel( 'info' )
    debug = register_debugger()
    run_tests()
    close_debugger()


