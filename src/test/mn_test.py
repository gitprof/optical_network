
import argparse
import imp
import random
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


debug = None

DEFAULT_DEBUG_MOD=0

CURR_FIGURE = 1

def set_figure(title, x_title, y_title, x_ticks, x_values, y_ticks):
    fig = plt.figure(CURR_FIGURE)
    #ax = fig.gca()
    #ax.set_xticks(numpy.arrange(0,10,1))
    #ax.set_yticks(numpy.arrange(0,60, 5))

    if x_ticks != []:
        plt.xticks(x_ticks, x_values)
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
    plt.figure(CURR_FIGURE)
    plt.plot(lstx, lsty, line_shape, linewidth=5, label=legend_value)
    #plt.plot(lstx, lsty) #, linestyle=line_shape, linewidth=15, label=legend_value)
    plt.legend(loc=LOC)
    #LOC = 'upper right'
    #debug("End Graph")


def show_graph(hold = False, _text = None):
    plt.ion()
    plt.grid()
    if _text != None:
        plt.text(-0.5, -0.5, _text)
    plt.show()

def wait_for_user(location):
    raw_input("Press any key to finish")
    raw_input("Press any key to finish")
    raw_input("Press any key to finish")

def run_mn_examples():
    tests =  EXAMPLE_TESTS
    for test in tests:
        cmd='%s/%s' % (EXAMPLE_DIR, test)
        os.system(cmd)
        #res = os.popen(cmd).read()

TEST_PINGALL       = 1
TEST_IPERF_ALL2ALL = 2
TEST_RESSILIENCE   = 3

def test_unit(graph_file,
              pathing_algo,
              pathing_algo_params = {},
              test      = None,
              test_params = {},
              controller = None,
              StaticArp = True,
              Cli       = False,
              Monitor   = False,
              Dump      = True,
              Hold      = False):

    debug.logger("test_unit: graphfile=%s. algorithm=%s." % (graph_file, pathing_algo))
    graph_file_full_path = os.path.join(GRAPH_DIR, graph_file)

    mnInterface = MNInterface.MNInterface(opt_net_file = graph_file_full_path,
                                          pathing_algo = pathing_algo,
                                          pathing_algo_params = pathing_algo_params)

    mnInterface.start_mn_session(controller = controller,
                                 StaticArp = StaticArp,
                                 Cli       = Cli,
                                 SanityTest = False,
                                 Monitor   = Monitor,
                                 Dump      = Dump,
                                 Hold      = Hold)

    test_results = None
    if TEST_RESSILIENCE == test:
        links_to_fail = test_params['links_to_fail']
        test_results = mnInterface.test_resillience(links_to_fail)
    elif TEST_PINGALL == test:
        mnInterface.test_ping()
    elif TEST_IPERF_ALL2ALL == test:
        mnInterface.test_iperf()

    mnInterface.end_mn_session()
    return test_results

MAX_LINKS_TO_FAIL = 12 # default 11
SEED = 213

def links_to_fail_from_graph(graph):
    graph_file_full_path = os.path.join(GRAPH_DIR, graph)
    opt_net = OptNet.OpticalNetwork()
    opt_net.init_graph_from_file(graph_file_full_path)
    links = opt_net.physical_links().keys()
    num_links = min(MAX_LINKS_TO_FAIL, len(links))
    random.seed(SEED)
    links_to_fail = random.sample(links, num_links)
    return links_to_fail


def test_algo_comparison(graph_file, draw_graphs = True):
    global CURR_FIGURE
    setLogLevel( 'warning' )
    total_bw_y = {}
    live_cons_y = {}
    links_to_fail = links_to_fail_from_graph(graph_file)
    # just specific case i want to check ...
    if ((15,16) not in links_to_fail) and ((16,15) not in links_to_fail) and (graph_file == "test8.g"):
        links_to_fail += [(15,16)]
    for algo in PATHING_ALGOS:
        link_to_perf_results = test_unit(graph_file   = graph_file,
                                        pathing_algo = algo,
                                        pathing_algo_params = {'links_to_fail':links_to_fail},
                                        test = TEST_RESSILIENCE,
                                        test_params = {'links_to_fail':links_to_fail},
                                        controller   = 'RYU')
        total_cons        = link_to_perf_results['TOTAL_CONS']
        failed_links      = [link for link in sorted(link_to_perf_results.keys()) if (link != 'TOTAL_CONS')]
        total_bw_y[algo]  = [link_to_perf_results[link]['TOTAL'][0] for link in failed_links]
        live_cons_y[algo] = [link_to_perf_results[link]['TOTAL'][1] for link in failed_links]

    if draw_graphs:
        ''' Printing Summary Graphs:'''
        x_axis = range(len(failed_links))
        graph_name = os.path.split(graph_file)[1]

        # live cons:
        CURR_FIGURE += 1
        live_cons_fig = set_figure("Live Connections (Total:%s)" % (total_cons), "link fail", "# live connections", x_axis, failed_links, range(total_cons+3))
        _text = "Average\n"
        for algo in PATHING_ALGOS:
            #avg = sum(live_cons_y[algo]) / float(len(live_cons_y[algo]))
            draw_graph(x_axis, live_cons_y[algo], ALGO_TO_LINE_SHAPE[algo], "Graph: %s. Algorithm: %s" % (graph_name, algo))
            #_text+="%s: %s\n" % (algo, str(avg))
            _text = None
        show_graph(False, _text)

        # total bw:
        max_bw = 0
        for algo in PATHING_ALGOS:
            max_bw = max(int(max(total_bw_y[algo])), max_bw)
        CURR_FIGURE += 1
        total_bw_fig  = set_figure("Total BWs",                     "link fail", "total BW in Mbit/s",              x_axis, failed_links, range(0,max_bw,20)) # TODO: y axis (BW)
        _text = "Average\n"
        for algo in PATHING_ALGOS:
            draw_graph(x_axis, total_bw_y[algo], ALGO_TO_LINE_SHAPE[algo], "Graph: %s. Algorithm: %s" % (graph_name, algo))
            #avg = sum(total_bw_y[algo]) / float(len(total_bw_y[algo]))
            #_text+="%s: %s\n" % (algo, str(avg))
            _text = None
        show_graph(False, _text)

    algo_to_graph_results = {}
    for algo in PATHING_ALGOS:
        algo_to_graph_results[algo] = {}
        algo_to_graph_results[algo]['TOTAL_BW']   = sum(total_bw_y[algo])
        algo_to_graph_results[algo]['TOTAL_CONS'] = sum(live_cons_y[algo])

    #wait_for_user("finished algo comparison")
    return algo_to_graph_results


def test_full_regression():
    graph_names = []
    algo_to_bw   = {}
    algo_to_cons = {}
    for algo in PATHING_ALGOS:
        algo_to_bw[algo]   = []
        algo_to_cons[algo] = []
    for g_p in GRAPHS_WITH_PATHS:
        graph_names.append(g_p[0])
        algo_to_graph_results = test_algo_comparison(g_p[0], True)
        for algo in PATHING_ALGOS:
            algo_to_bw  [algo].append(algo_to_graph_results[algo]['TOTAL_BW'])
            algo_to_cons[algo].append(algo_to_graph_results[algo]['TOTAL_CONS'])

    return
    ''' Printing Summary Graphs:'''

    # live cons:
    x_axis = range(len(GRAPHS_WITH_PATHS))
    CURR_FIGURE += 1
    live_cons_fig = set_figure("Live Connections (Total:%s)" % (total_cons), "graph", "# live connections", x_axis, graph_names, range(total_cons+3))
    graph_name = os.path.split(graph_file)[1]
    for algo in PATHING_ALGOS:
        draw_graph(x_axis, algo_to_cons[algo], ALGO_TO_LINE_SHAPE[algo], "Algorithm: %s" % (algo))
    show_graph()

    # total bw:
    max_bw = 0
    for algo in PATHING_ALGOS:
        max_bw = max(int(max(total_bw_y[algo])), max_bw)

    CURR_FIGURE += 1
    total_bw_fig  = set_figure("Total BWs",                     "graph", "total BW in Mbit/s",               x_axis, graph_names, range(0,max_bw,100)) # TODO: y axis (BW)
    for algo in PATHING_ALGOS:
        draw_graph(x_axis, algo_to_bw[algo], ALGO_TO_LINE_SHAPE[algo], "Algorithm: %s" % (algo))
    show_graph()

def test_graph_comparison(pathing_algo = 'MANUAL'):
    for g_p in GRAPHS_WITH_PATHS:
        paths = g_p[1] if pathing_algo == 'MANUAL' else None

	test_unit(graph_file    = g_p[0],
              pathing_algo  = pathing_algo,
              pathing_algo_params = {'paths':paths},
              controller    = 'RYU')

def test_interactive(graph, pathing_algo, ):
	test_unit(graph_file    = graph,
              pathing_algo  = pathing_algo,
              pathing_algo_params = {},
              test          = False,
              test_params   = {},
              controller    = 'RYU',
              StaticArp     = True,
              Cli           = True)

def run_tests(test_mode, graph, algo):
    if   'INTERACTIVE' == test_mode:
        test_interactive(graph, algo)
    elif 'GRAPH_CMP'   == test_mode:
        test_graph_comparison(algo)
    elif 'ALGO_CMP'    == test_mode:
        test_algo_comparison(graph)
    elif 'REGRESSION' == test_mode:
        test_full_regression()
    elif 'MN_EXAMPLES' == test_mode:
        run_mn_examples()
    else:
        debug.assrt(False, 'unkown test_mode!')
    wait_for_user("finished algo comparison")


def arg_parsing():
    parser = argparse.ArgumentParser(description='--- Generic Mininet Test ---\nExecute Mininet, run different perftests and produce results statistics and diagrams.')
    parser.add_argument('--test_mode', nargs=1, choices=['INTERACTIVE', 'GRAPH_CMP', 'ALGO_CMP', 'REGRESSION', 'MN_EXAMPLES'], help='test mode.\n  interactive: run mn and execute mn shell.\n  graph_cmp: run the given algorithm on different graphs.\n  algo_cmp: run different algorithms on the given graph.\n  regression: runs all algorithms on each graphs, produce results per graphs, and total summary.\n mn_examples: run some basic mn examples.\n # see src/mainGlobal.py file for list of all pathing algorithms and graphs')
    parser.add_argument('--graph',     nargs=1,                                                                  help='graph file name. the file should be located in the \'graphs\' dir, and should be of a familiar format. see OpticalNetwork for details. available only for test_mode interactive or algo_comparison. default %s.' % (GRAPHS_WITH_PATHS[0][0]))
    parser.add_argument('--algo',      nargs=1, choices=['MM_SRLG','MM_SRLG_VAR', 'DP'],                         help='routing algorithm. available only for test_mode interactive or graph_comparison. default MM_SRLG')
    parser.add_argument('--debug_mod', nargs=1, choices=['0', '1', '2', '3', '4'],                               help='debug_mod: 0 - debug. 1 - info. 2 - warnings. 3 - errors. 4 - silent')
    args = parser.parse_args()
    test_mode = args.test_mode[0] if args.test_mode  is not None else 'INTERACTIVE'
    graph     = args.graph[0]     if args.graph      is not None else GRAPHS_WITH_PATHS[0][0]
    algo      = args.algo[0]      if args.algo       is not None else 'MM_SRLG'
    debug_mod = args.debug_mod[0] if args.debug_mod  is not None else DEFAULT_DEBUG_MOD
    #self.debug.logger(str(type(args.op)))
    return (test_mode, graph, algo, int(debug_mod))


if "__main__" == __name__:
    debug = register_debugger(master = True)
    try:
        (test_mode, graph, algo, debug_mod) = arg_parsing()
        if debug_mod != None:
            #debug.change_mod(debug_mod)
            todo = 'update debugger'
        run_tests(test_mode, graph, algo)
    except:
         close_debugger()
         raise
    raw_input("Press Enter to continue...")
    close_debugger()


