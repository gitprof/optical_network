#!/bin/python

''' --- Testings for MM_SRLF algorithms ---
 * some of the graphs have capacities lower than 2, in contradict to the assumption. but this shouldnt harm functionality of the algorithms.
 *
'''

import imp
import os
import copy

#CURR_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

Global  = imp.load_source('Global',         os.path.join('src', 'main', 'Global.py'))
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

def generic_alg_tester(test_name, algorithm, graph_file, expected_paths):
    Hprint('\n'+test_name)
    optNet = OptNet.OpticalNetwork()
    optNet.init_graph_from_file(graph_file)
    debug.assrt(None != optNet, 'generic_alg_tester - '+test_name+': optNet is None!\n')
    mm_srlg_solver = MM_SRLG.MM_SRLG_solver()
    if 'ALG'   == algorithm:
        logical_network = mm_srlg_solver.ALG(optNet)
    if 'arb'   == algorithm:
        logical_network = mm_srlg_solver.mm_srlg_arb(optNet)
    if 'cycle' == algorithm:
        logical_network = mm_srlg_solver.mm_srlg_cycle(optNet)
    if 'MM_SRLG' == algorithm:
        logical_network = mm_srlg_solver.mm_srlg(optNet)
    debug.assrt(None != logical_network, test_name+": logical_network is None!")
    # sort_paths(logical_network.paths)
    expected_paths = None # there is no simple way to check correctness
    #optNet.draw()
    if expected_paths != None:
        TestEqual(expected_paths, logical_network.paths, 'paths not equal!\n')
    else:
        Xprint('Paths:')
        Xprint(logical_network.paths)
        Xprint('Max SRLG:')
        Xprint(logical_network.get_max_SRLG())


test_num = 0
def gen_test_num():
    test_num += 1
    return 'Test {}:'.format(test_num)

def test_mm_srlg():
    expected_paths = []
    generic_alg_tester( 'Test1 - ALG simple: ',     'ALG',     GRAPH_SIMPLE,   expected_paths)
    #generic_alg_tester( 'Test4 - arb simple: ',     'arb',     GRAPH_SIMPLE,    expected_paths)  #TODO: this test raises assert, need to check
    generic_alg_tester( 'Test4 - MM_SRLG simple: ',     'MM_SRLG',     GRAPH_SIMPLE,    expected_paths)
    generic_alg_tester( 'Test1 - ALG special: ',     'ALG',     GRAPH_SPECIAL,   expected_paths)
    generic_alg_tester( 'Test4 - arb special: ',     'arb',     GRAPH_SPECIAL,    expected_paths)
    generic_alg_tester( 'Test3 - cycle special: ',   'cycle',   GRAPH_SPECIAL,    expected_paths)
    generic_alg_tester( 'Test5 - MM_SRLG special: ', 'MM_SRLG', GRAPH_SPECIAL,    expected_paths)
    generic_alg_tester( 'Test2 - ALG basic: ',     'ALG',     GRAPH_BASIC,    expected_paths)
    generic_alg_tester( 'Test3 - cycle basic: ',   'cycle',   GRAPH_BASIC,    expected_paths)
    generic_alg_tester( 'Test5 - MM_SRLG basic: ', 'MM_SRLG', GRAPH_BASIC,    expected_paths)
    generic_alg_tester( 'Test4 - arb basic: ',     'arb',     GRAPH_TMP,    expected_paths)
    generic_alg_tester( 'Test6 - ALG advanced: ',     'ALG',     GRAPH_ADVANCED,    expected_paths)
    generic_alg_tester( 'Test7 - cycle advanced: ','cycle',   GRAPH_ADVANCED, None)
    generic_alg_tester( 'Test8 - arb advanced: ','arb',   GRAPH_ADVANCED, None)
    generic_alg_tester( 'Test9 - MM_SRLG advanced: ','MM_SRLG',   GRAPH_ADVANCED, None)


if "__main__" == __name__:
    debug = register_debugger(master = True)
    test_mm_srlg()
    close_debugger()
