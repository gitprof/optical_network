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

GRAPH_DIR      = os.path.join(BASE_DIR,  'graphs')
GRAPH_SIMPLE   = os.path.join(GRAPH_DIR, 'simple.g')
GRAPH_BASIC    = os.path.join(GRAPH_DIR, 'basic.g')
GRAPH_ADVANCED = os.path.join(GRAPH_DIR, 'advanced.g')
GRAPH_TMP      = os.path.join(GRAPH_DIR, 'tmp.g')
GRAPH_SPECIAL  = os.path.join(GRAPH_DIR, 'special.g')
GRAPH_2PATHS   = os.path.join(GRAPH_DIR, '2paths.g')
GRAPH_STAR     = os.path.join(GRAPH_DIR, 'star.g')

NO_COLOR = 1

Debug = imp.load_source('Debug', os.path.join(MAIN_DIR, 'utilities', 'Debug.py'))

''' Scratchpad '''



global_debug = None
def register_debugger(master = False):
    global global_debug
    if None == global_debug:
        global_debug = Debug.Debug()
    return global_debug

def close_debugger():
    global global_debug
    global_debug.close_debugger()

