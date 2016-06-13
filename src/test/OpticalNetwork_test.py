#!/bin/python

import imp

Global  = imp.load_source('Global',         os.path.join('src', 'main', 'Global.py'))
from Global import *

OpticalNetwork = imp.load_source('OpticalNetwork', os.path.join(MAIN_DIR, 'OpticalNetwork.py'))
#OpticalNetwork = imp.load_source('OpticalNetwork', '/home/yakir/optical_network_proj/optical_network/src/main/OpticalNetwork.py')

def xprint(msg):
    print(msg)

def test1():
    xprint('\n---Test1---')
    optNet = OptNet.OpticalNetwork()
    optNet.init_graph_from_file(GRAPH_BASIC)
    xprint('Node:')
    xprint(optNet.nodes())
    xprint('Edges:')
    xprint(optNet.physical_links())
    xprint('Drawing Graph...')
    optNet.draw()

def test_optical_network():
    test1()

if "__main__" == __name__:
    test_optical_network()
    
