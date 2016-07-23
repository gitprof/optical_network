#!/usr/bin/python



#from utilities.Debug import Debug
import imp
import os

running_script_dir = os.path.dirname(os.path.abspath(__file__))

if 'nt' == os.name:
	path_dirs = ['']
else:
    path_dirs = running_script_dir

path1 = os.path.split(running_script_dir)[0]
path2 = os.path.split(path1)[0]

BASE_DIR = path2 # os.path.join(*(path2))
MAIN_DIR = os.path.join(BASE_DIR, 'src', 'main')
TEST_DIR = os.path.join(BASE_DIR, 'src', 'test')
TEST_RESULTS_DIR = os.path.join(BASE_DIR, 'test_results')

GRAPH_DIR      = os.path.join(BASE_DIR,  'graphs')
GRAPH_SIMPLE   = os.path.join(GRAPH_DIR, 'simple.g')
GRAPH_BASIC    = os.path.join(GRAPH_DIR, 'basic.g')
GRAPH_ADVANCED = os.path.join(GRAPH_DIR, 'advanced.g')
GRAPH_TMP      = os.path.join(GRAPH_DIR, 'tmp.g')
GRAPH_SPECIAL  = os.path.join(GRAPH_DIR, 'special.g')
GRAPH_2PATHS   = os.path.join(GRAPH_DIR, '2paths.g')
GRAPH_STAR     = os.path.join(GRAPH_DIR, 'star.g')
GRAPH_2PATHS     = os.path.join(GRAPH_DIR, '2paths.g')
GRAPH_TREE     = os.path.join(GRAPH_DIR, 'tree.g')

NO_COLOR = 1

Debug = imp.load_source('Debug', os.path.join(MAIN_DIR, 'utilities', 'Debug.py'))

''' Scratchpad '''


PATHING_ALGOS = ['MM_SRLG', 'MM_SRLG_VAR', 'DP']

GRAPHS_WITH_PATHS = [
                         #  ('2paths.g', [[1,3,2],[1,4,2]]),
                          ('test8.g', [[1,4,3], [2,5,7,6,4,1], [3,4,5,2]]),
                         # ('test9.g', []),
                         # ('test10.g', []),
                         # ('test11.g', []),
                         # ('test12.g', []),
                         # ('test13.g', []),
                         # ('test14.g', []),
                         # ('test15.g', []),
                         # ('test16.g', []),
                         # ('test17.g', []),
                         # ('star.g', [[1,5,6,3],[3,6,5,2],[2,5,6,4]]),
                         # ('tree.g', [[2,4,1]]),
                         # ('tmp.g', [[1,4,2], [3,4,2], [1,4,3]]),
                         # ('test2.g', [[1,3,2]]),
                         # ('test3.g', [[2,1,7]]),
                       ]



global_debug = None
def register_debugger(master = False):
    global global_debug
    if None == global_debug:
        global_debug = Debug.Debug()
    return global_debug

def close_debugger():
    global global_debug
    global_debug.close_debugger()


