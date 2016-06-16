#!/bin/python

import networkx as nx
import networkx.drawing as nxd
import matplotlib.pyplot as plt
import random
import copy
import imp
import os
from collections import Counter

Global  = imp.load_source('Global',         os.path.join('src', 'main', 'Global.py'))
from Global import *

'''
Graph attributes:
 edges attrs:
    - capacity
    - logiclinks
 logical nodes: vertex marked with attr type = logical
 logical links: edges  marked with attr logical = <num_of_logical_links_on_the_physical>
'''
class OpticalNetwork:
    def __init__(self):
        self.graph = nx.Graph()
        self.B     = 0 # default
        self.l_net = LogicalNetwork()
        #self.l_net = Set()
        self.debug = register_debugger()
        self.logical_nodes = []
        self.input_graph = None

    '''
    Assume file of format:
    B,<B_val>
    <node1>,<node2>,<capacity>
              ...

    while:
        switch is noted by sx
        router is noted by rx
        (x is number)
    '''
    def init_graph_from_file(self, graph_file):
        print('init_graph_from_file')
        with open(graph_file, 'r') as f:
            lines = [tuple(i[:-1].split(',')) for i in f]
        self.B = int(lines[0][1])
        edges_lines = lines[1:]
        input_edges = {(line[0], line[1]):int(line[2]) for line in edges_lines}
        #input_nodes = []
        self.logical_nodes = []
        for edge in input_edges.keys():
            for i in [0,1]:
                if not (int(edge[i][1:]) in self.logical_nodes):
                    if 'r' == edge[i][0]:
                        self.logical_nodes.append(int(edge[i][1:]))
        weighted_edges = [(int(edge[0][1:]), int(edge[1][1:]), {'capacity':input_edges[edge]}) for edge in input_edges.keys()]
        self.graph.add_edges_from(weighted_edges)
        self.input_graph = copy.deepcopy(self.graph)

    def clone(self):
        print('clone:')
        new_copy               = OpticalNetwork()
        new_copy.B             = copy.deepcopy(self.B)
        new_copy.graph         = copy.deepcopy(self.graph)
        new_copy.logical_nodes = copy.deepcopy(self.logical_nodes)
        new_copy.debug         = self.debug
        return new_copy


    def verify_file_lines():
        demo=0

    def set_edge_capacity(self, edge, capacity):
        self.graph[edge[0]][edge[1]]['capacity'] = capacity

    def set_edge_logical_links(self, edge, logical_links):
        res = False
        if (self.graph[edge[0]][edge[1]]['capacity'] >= logical_links):
            self.graph[edge[0]][edge[1]]['logiclinks'] = logical_links
            res = True
        return res

    def is_edge(self, formatted_edges, n1, n2):
        return ((n1, n2) in formatted_edges) or ((n2, n1) in formatted_edges)

    def is_logical_node(self, _node):
        return _node in self.logical_nodes

    def physical_links(self):
        p_links = {(u,v):(self.graph[u][v]['capacity']) for (u,v) in self.graph.edges()}
        return p_links

    def nodes(self):
        return sorted(self.graph.nodes())

    def get_logical_nodes(self):
        return sorted(self.logical_nodes)

    #def logical_links(self):
    #    return self.l_net.

    '''
    get spanning tree that spans VL.
    we are using minimum spanning tree since this is the available method,
        but there is no need for minimum, or the capacity attr
    return type: nx.Graph()
    '''
    def create_spanning_tree(self):
        return nx.minimum_spanning_tree(self.graph, 'capacity')

    def remove_node(self, node):
        graph.remove_node(node)

    def node_degree(self, node):
        return self.graph.degree(node)

    def node_neighbors(self, node):
        return sorted(graph.neighbors(node))

    def get_plink_capacity(self, edge):
        return self.graph[edge[0]][edge[1]]['capacity']

    def set_strict_capacity(self, C):
        # print(self.graph.edges())
        for edge in self.graph.edges():
            self.graph[edge[0]][edge[1]]['capacity'] = min(C, self.input_graph[edge[0]][edge[1]]['capacity'])

    def sort_logical_paths(self):
        self.l_net.sort_paths()

    #def num_lightpaths_via_e(self, edge):
    #    return self.l_net.num_lightpaths_via_e(edge)

    def draw(self):
        g = self.graph
        pos = nx.spring_layout(self.graph,scale=2)
        nx.draw_networkx_nodes(g, pos, nodelist=g.nodes(), node_color='r', node_size=500, alpha=0.8)
        nx.draw_networkx_edges(g, pos, edgelist=g.edges(), edge_color=[( (float(g[u][v]['capacity'])*0.01)+10000 ) for (u,v) in g.edges()], edge_vmin=100, edge_vmax=1000, width=5, alpha=0.8)
        #nx.draw(self.graph,pos,font_size=8)
        #nxd.draw(self.graph)
        node_labels = {}
        for node in g.nodes():
            node_labels[node] = str(node)
        nx.draw_networkx_labels(g, pos, node_labels, font_size=10)
        edge_labels = {}
        for edge in g.edges():
            edge_labels[edge] = g[edge[0]][edge[1]]['capacity']
        nx.draw_networkx_edge_labels(g, pos, edge_labels, font_size=10)

        #nx.draw(g)
        #plt.draw()
        plt.axis('off')
        plt.show()


class LogicalNetwork:
    def __init__(self):
        '''
            links: this is a dict:
             - edge: num_logical_paths_traversing_e.
             # while the end point of edge can be any 2 nodes
            paths: list of paths.
             - path: list of nodes v1, v2 ... , vk.  s.t: v1 and vk are logical nodes.
                                                   and all the rest can be logical or non-logical nodes.
                                                   all nodes unique.
        '''
        self.debug = register_debugger('opticalNetwork')
        self.links = {}
        self.paths = []
        self.max_SRLG = None
        self.initialized = False
        self.traversing_paths = {}

    def choose_arbitrary_subset_of_size_b(self, B):
        self.debug.assrt(len(self.paths) >= B, "choose_an_arb_subset_of_size_B: not enough paths!")
        random.seed()
        sample_size = min(B, len(self.paths)) #TODO: check if can happen
        #self.paths = random.sample(self.paths, sample_size)
        self.paths = self.paths[0:sample_size]
        self.init_from_paths(self.paths)

    def calc_max_SRLG(self):
        max_srlg = 0
        max_link = None
        for link in self.links.keys():
            if self.links[link] > max_srlg:
                max_srlg = self.links[link]
                max_link = link
        self.debug.assrt(max_link != None, "calc_max_SRLG: didnt find max SRLG!")
        self.max_SRLG = max_srlg

    def get_max_SRLG(self):
        self.calc_max_SRLG()
        return self.max_SRLG

    def merge(self, logical_network):
        self.paths = self.paths + logical_network.paths
        self.init_from_paths(self.paths)

    def init_from_paths(self, paths):
        self.paths = paths
        self.links = {}
        for path in paths:
            self.debug.assrt(len(path) > 1, 'init_from_paths: path with length 1')
            for i in range(0, len(path) - 1):
                edge = (path[i], path[i+1])
                (i,j) = (min(edge[0], edge[1]), max(edge[0], edge[1]))
                if (i,j) in self.links.keys():
                    self.links[(i,j)] += 1
                else:
                    self.links[(i,j)] =  1
        self.initialized = True
        return self

    '''
        we assume here that num_lightpaths_via_e = num_logicallinks_over_e
    '''
    def num_lightpaths_via_e(self, edge):
        self.init_from_paths(self.paths)
        try:
            res = self.links[edge]
        except KeyError:
            res = 0
        return res

    ''' do: first node lower than last one '''
    def normalize_path(self, path):
        if path[0] > path[-1]:
            path.reverse()

    def normalize_paths(self):
        for path in self.paths:
            self.normalize_path(path)

    ''' do: sort from shortest to longest '''
    def sort_paths(self):
        if [] == self.paths:
            return
        sorting_itr = list(range(len(paths)))
        sorting_itr.reverse()
        for i in sorting_itr:
            for j in range(i):
                if (len(paths[j]) > len(paths[j+1])):
                    tmp_path = paths[j]
                    paths[j] = paths[j+1]
                    paths[j] = tmp_path

    def init_link_to_paths_mapping(self):
        for path in self.paths:
            for node_ix in range(len(path)-1):
                link = (path[node_ix], path[node_ix+1])
                if link in self.traversing_paths.keys():
                    self.traversing_paths[link].append(path)
                else:
                    self.traversing_paths[link] = [path]

    ''' return list of paths traversing via this link '''
    def get_traversing_paths(self, link):
        if not (link in self.traversing_paths.keys()):
            return []
        return self.traversing_paths[link]

