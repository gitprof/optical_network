#!/bin/python

''' --- Testings for MM_SRLF algorithms ---
 * some of the graphs have capacities lower than 2, in contradict to the assumption. but this shouldnt harm functionality of the algorithms.
 *
'''

import imp
import os
import copy

#CURR_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

Global  = imp.load_source('Global',         os.path.join('/home/mininet', 'optical_network', 'src', 'main', 'Global.py'))
from Global import *

OptNet  = imp.load_source('OpticalNetwork', os.path.join(MAIN_DIR, 'OpticalNetwork.py'   ))
MM_SRLG = imp.load_source('MM_SRLG',        os.path.join(MAIN_DIR, 'MM_SRLG.py'          ))
Debug   = imp.load_source('Debug',          os.path.join(MAIN_DIR, 'utilities', 'Debug.py' ))

from Common import *

debug = None

''' return True if p1 'bigger or equal' than p2. else False '''
def compare_paths(p1, p2):
    for i in range(len(p1)):
        if p1[i] > p2[i]:
            return True
        if p1[i] < p2[i]:
            return False
    return len(p1) >= len(p2)


def sort_paths(paths):
    if [] == paths:
        return
    for path in paths:
        if path[0] > path[-1]:
            tmp     = path[0]
            path[0] = path[-1]
            path[-1] = tmp
    sorting_itr = list(range(len(paths)))
    sorting_itr.reverse()
    for i in sorting_itr:
        for j in range(i):
            if compare_paths(paths[j], paths[j+1]):
                tmp_path = paths[j]
                paths[j] = paths[j+1]
                paths[j] = tmp_path



'''
    Prints results and return bottom line statistics
'''
def process_results(connection_data):
    global debug
    debug.logger("\n\nOOO ***** Printing Results: ******")
    debug.logger("OOO -------------------------------")
    debug.logger("OOO {:<11} | {:<6} | {:<11}".format("Connection", "BW", "Route"))
    total_bw = 0
    for (r1,r2) in connection_data.keys():
        bw = connection_data[(r1,r2)]['BW']
        route = connection_data[(r1,r2)]['ROUTE']
        total_bw += bw
        debug.logger("OOO {}->{:<8} | {:<6} | {} ".format(r1, r2, round(bw, 2), route))
    num_connections = len(connection_data.keys())
    debug.logger("\nOOO Total Connections: %s"  % (num_connections))
    debug.logger("OOO Total BW: %s"  % (round(total_bw,2)))
    debug.logger("OOO -------------------------------")
    return (num_connections, total_bw)


def get_opt_net(graph):
    optNet = OptNet.OpticalNetwork()
    optNet.init_graph_from_file(os.path.join(GRAPH_DIR, graph))
    return optNet

def gen_test(test_num, graph, algo, fail_link):
    debug.logger('\n\n\nOOO ---gen_test %s. ---' % (test_num))
    debug.logger('\nOOO  graph: %s. algo: %s. failing link: %s.' % (graph, algo, fail_link))
    #logical_paths = [[1,4,2],[1,3,2]]
    if   'MM_SRLG' == algo:
        algo = MM_SRLG.MM_SRLG_solver()
    else:  #'DP'      == alog:
        algo = DP()
    optNet = get_opt_net(graph)
    algo.solve(optNet)
    debug.logger("gen_test: logical_paths=%s" % (optNet.get_logical_network().get_paths()))
    optNet.l_net.update()
    optNet.create_logical_graph()
    routing_paths = optNet.set_routing_paths()
    debug.logger("\n\nTEST2_INFO: routing_paths = %s" % (routing_paths))
    routing_paths = optNet.reset_after_link_failure(fail_link)
    debug.logger("\n\nTEST2_INFO: new routing_paths = %s" % (routing_paths))
    connection_data = optNet.get_routing_with_bws()
    process_results(connection_data)
    #debug.logger("test2 Done\n")


def test_link_failures(graph, algo):
    optNet = get_opt_net(graph)
    test_num = 0
    for physical_link in optNet.physical_links():
        gen_test(test_num, graph, algo, physical_link)
        test_num += 1


'''
Add here tests:
'''
def algo_tester_main():
    debug.logger('\n***** AlgoTester *****')
    test_link_failures('test1.g', 'MM_SRLG')
    #test_link_failures('test1.g', 'DP')


if "__main__" == __name__:
    debug = register_debugger(master = True)
    algo_tester_main()
    close_debugger()
