#!/bin/python

import networkx as nx


'''
Graph attributes:
 edges capacity: attr weight of the edge
 logical nodes: vertex marked with attr type = logical
 logical links: edges  marked with attr logical = <num_of_logical_links_on_the_physical>
'''
class OpticalNetwork:
    def __init__(self, graph_file_in):
        graph_file = graph_file_in
        graph = nx.Graph()
        B     = 0 # defau;t

    def set_edges_capacity(self, capacity):
        for edge in graph.edges:
            edge['weight'] = capacity

    def edges(self):
         return graph.edges()

    def nodes(self):
        return graph.nodes()

    def logical_links(self):
        return
