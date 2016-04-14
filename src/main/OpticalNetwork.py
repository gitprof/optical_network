#!/bin/python

import networkx as nx
from sets import Set
from collections import Counter
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
        with open(self.graph_file, 'r') as f:
            lines = [tuple(i.split(',')) for i in f]
        self.B = lines[0][1]
        edges = [(line[0],line[1],{'capacity':line[2]}) for line in lines]
        self.graph.add_edges_from(edges)
        self.logical_nodes = [node for node in self.graph.nodes() if self.is_logical_node(node)]
        #self.l_net.set_from_tuples()

    def set_edge_capacity(self, edge, capacity):
        self.graph[edge[0]][edge[1]]['capacity'] = capacity 

    def set_edge_logical_links(self, edge, logical_links):
        res = False
        if self.graph[edge[0][edge[1]['capacity'] >= logical_links:
            self.graph[edge[0]][edge[1]]['logiclinks'] = logical_links 
            res = True
        return res

    def is_logical_node(_node):
        return _node[0] == 'r'

    def physical_links(self):
         return self.graph.edges()

    def nodes(self):
        return self.graph.nodes()

    def logical_nodes(self):
        return self.logical_nodes

    def logical_links(self):
        #return self.l_net.get_as

    '''
    get spanning tree that spans VL.
    we are using minimum spanning tree since this is the available method, 
        but there is no need for minimum, or the capacity attr
    return type: nx.Graph()
    '''
    def create_spanning_tree(self):
        return minimum_spanning_tree(self.graph, 'capacity')

    def remove_node(self, node):
        graph.remove_node(node)

    def node_degree(self, node):
        return graph.degree(node)

    def node_neighbors(self, node):
        return graph.neighbors(node)

    def produce_cycle_aux(self, node, cycle_list):
        cycle_list.append(node)
        for neighbor in self.graph.neighbors(node):
            produce_cycle_aux(neighbor, cycle_list)

    def produce_cycle_from_tree(self):
        cycle_list = []
        start_node = None
        for node in self.nodes():
            if self.is_logical_node(node):
                start_node = node
        debug.assrt(start_node is not None, "produce_cycle_from_tree: start node is None")
        produce_cycle_aux(start_node, cycle_list)
        cycle_list.append(start_node)
        return cycle_list

    def num_lightpaths_via_e(self, edge):
        return self.l_net.num_lightpaths_via_e(edge)

class LogicalNetwork:
    def __init__(self):
        ''' 
            links: this is a dict: 
             - edge: num_logical_links.
             - while the end point of edge can be any 2 nodes
            paths: list of paths.
             - path: list of nodes, s.t. that start node and the end node are logical nodes, 
                                           and all the rest are non-logical nodes and unique.
        '''
        links = {}
        paths = []
    
    def produce_paths_from_links(self):
        #TODO

    def merge(logical_network):
        self.links = dict(Counter(logical_links) + Counter(logical_network.links))
        self.produce_paths_from_links()

    def init_from_cycle(self, cycle):
        #TODO

    '''
        we assume here that num_lightpaths_via_e = num_logicallinks_over_e
    '''
    def num_lightpaths_via_e(self, edge):
        try:
            res = self.links[edge]
        except KeyError:
            res = 0
        return res

