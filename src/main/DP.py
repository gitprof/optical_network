
import networkx as nx
import matplotlib.pyplot as plt
import itertools

import numpy as np
import imp
import math
import copy
import os
import copy
from OpticalNetwork import LogicalNetwork
from OpticalNetwork import OpticalNetwork


running_script_dir = os.path.dirname(os.path.abspath(__file__))
Global  = imp.load_source('Global', os.path.join(running_script_dir, 'Global.py'))
from Global import *

Debug = imp.load_source('Debug', os.path.join(MAIN_DIR, 'utilities', 'Debug.py'))


'''
DP:
    * there are 3 helper algorithm, and the main algorithm.
    * every algorithm that modify the original graph should deep copy it
'''

class DP:

    def solve(self, optical_network):
        print("DP solve")
        graph = copy.deepcopy(optical_network.graph)
        optical_network.l_net = self.solve_inner(graph, optical_network.get_logical_nodes() ,optical_network.B)
        print("DP solve: logical_paths=%s" % (optical_network.l_net.get_paths()))

    def solve_inner(self, graph,logicalNodes, X):
        paths = []
        sortedList = self.getSortedListOfPaths(graph,logicalNodes)
        deletedEdges = []
        progress = True
        while (len(paths) < X) and progress == True:
            progress = False
            for (u,v,path) in sortedList:
                if(len(paths) == X):
                    break
                (path,deletedEdges) = self.DisjointPaths(graph,u,v,deletedEdges)
                if(path==[]):
                    continue
                progress = True
                paths.append((u,v,path))

        logical_network = LogicalNetwork()
        list_of_paths = [x[2] for x in paths]
        logical_network.init_from_paths(list_of_paths)
        return logical_network

    def are_connected(self, graph, s, t):
        return (t in nx.algorithms.dag.descendants(graph,s))

    def DisjointPaths(self,graph,s,t,deleted_edges):

        if not self.are_connected(graph, s, t):
            for (u,v,w) in deleted_edges:
                if w > 0:
                    graph.add_edge(u,v,capacity=w)
                    deleted_edges.remove((u,v,w))
            if not self.are_connected(graph, s, t):
                return ([], deleted_edges)

        path = nx.shortest_path(graph,source=s,target=t)

        for i in range(0,(len(path))-1):
            u=path[i]
            v=path[i+1]
            #print("***** - %s %s %s" % (u,v,graph[u][v]))
            new_capacity = graph[u][v]['capacity']-1
            deleted_edges.append((u,v,new_capacity))
            graph.remove_edge(u,v)

        return (path, deleted_edges)

        for (u,v,w) in graph.edges(data='capacity'):
            if(w==0):
                graph.remove_edge(u,v)


    def getSortedListOfPaths(self, graph, logicalNodes):
        paths = nx.all_pairs_dijkstra_path(graph)
        lst = []
        for u in logicalNodes:
            for v in logicalNodes:
                if (u>=v):
                    continue
                lst.append((u,v,paths[u][v]))
        sortedList = sorted(lst, key=lambda x: len(x[2]))
        return sortedList

def test1(arg):
    if arg==1:
        graph = nx.complete_graph(25)
    if arg==2:
        graph = nx.path_graph(25)
    nodes = [1,2,5,7,13]
    res = competitor_solver.getSortedListOfPaths(graph,nodes)
    print(res)

def test2(arg):
    G = nx.Graph()
    if arg==1:
        G.add_edge(1,2,weight=2)
        G.add_edge(1,3,weight=8)
        G.add_edge(2,3,weight=3)
        (path, lst) = competitor_solver.DisjointPaths(G,1,3,[],False)
        print("path:", path)
        print("list of deleted edges:", lst)
    if arg==2:
        G.add_edge(1,2,weight=2)
        G.add_edge(1,4,weight=4)
        G.add_edge(2,3,weight=1)
        G.add_edge(2,5,weight=1)
        G.add_edge(2,3,weight=1)
        G.add_edge(3,4,weight=0)
        G.add_edge(3,5,weight=2)
        G.add_edge(4,5,weight=2)
        (paths,deletedEdges) = competitor_solver.solve(G,[1,3,5],3)
        print(paths)
        print(deletedEdges)
    if arg==3:
        G.add_edge(1,2,weight=2)
        G.add_edge(1,4,weight=3)
        G.add_edge(2,4,weight=2)
        G.add_edge(2,5,weight=2)
        G.add_edge(2,6,weight=1)
        G.add_edge(3,4,weight=4)
        G.add_edge(4,6,weight=1)
        G.add_edge(5,6,weight=2)
        (paths,deletedEdges) = competitor_solver.solve(G,[1,2,4,6],4)
        print(paths)
        print(deletedEdges)
    if arg==4:
        G.add_edge(1,2,weight=1)
        G.add_edge(2,3,weight=2)
        cs = competitor_solver()
        (paths,deletedEdges) = cs.solve(G,[1,2,3],4)
        print(paths)
        print(deletedEdges)

if "__main__"==__name__:
    arg=4
    test2(arg)
