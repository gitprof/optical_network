#!/bin/python

import imp

import os

Global  = imp.load_source('Global',         os.path.join('/home/mininet', 'optical_network', 'src', 'main', 'Global.py'))
from Global import *

OpticalNetwork = imp.load_source('OpticalNetwork', os.path.join(MAIN_DIR, 'OpticalNetwork.py'))
#OpticalNetwork = imp.load_source('OpticalNetwork', '/home/yakir/optical_network_proj/optical_network/src/main/OpticalNetwork.py')

debug = None

def xprint(msg):
    print(msg)


def print_results(connection_data):
    global debug
    debug.logger("\n\n***** Printin Results: ******")
    debug.logger("-------------------------------")
    debug.logger("{:<11} | {:<6} | {:<11}".format("Connection", "BW", "Route"))
    total_bw = 0
    for (r1,r2) in connection_data.keys():
        bw = connection_data[(r1,r2)]['BW']
        route = connection_data[(r1,r2)]['ROUTE']
        total_bw += bw
        debug.logger("{}->{:<8} | {:<6} | {} ".format(r1, r2, bw, route))
    debug.logger("\nTotal Connections: %s"  % (len(connection_data.keys())))
    debug.logger("Total BW: %s"  % (total_bw))
    debug.logger("-------------------------------")



def test2():
    xprint('\n---Test1---')
    optNet = OpticalNetwork.OpticalNetwork()
    optNet.init_graph_from_file(os.path.join(GRAPH_DIR, "2paths.g"))
    logical_paths = [[1,4,2],[1,3,2]]
    optNet.l_net.set_paths(logical_paths)
    optNet.l_net.update()
    #optNet.create_logical_graph()
    routing_paths = optNet.set_routing_paths()
    xprint("\n\nTEST2_INFO: routing_paths = %s" % (routing_paths))
    routing_paths = optNet.reset_after_link_failure((3,2))
    xprint("\n\nTEST2_INFO: new routing_paths = %s" % (routing_paths))
    connection_data = optNet.get_routing_with_bws()
    print_results(connection_data)
    xprint("test2 Done\n")


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
    #test1()
    test2()

if "__main__" == __name__:
    global debug
    debug = register_debugger(master = True)
    test_optical_network()
    close_debugger()

