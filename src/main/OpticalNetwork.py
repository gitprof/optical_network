#!/bin/python

import networkx as nx
import networkx.drawing as nxd
import matplotlib.pyplot as plt
import random
import copy
import imp
import os
from collections import Counter

running_script_dir = os.path.dirname(os.path.abspath(__file__))
Global  = imp.load_source('Global', os.path.join(running_script_dir, 'Global.py'))
from Global import *

'''
Graph attributes:
 edges attrs:
    - capacity
    - logiclinks
 logical nodes: vertex marked with attr type = logical
 logical links: edges  marked with attr logical = <num_of_logical_links_on_the_physical>
'''
GEN = 100
DEF_INC_FACTOR = 20
MAX_EDGE_CAPACITY = 10

class OpticalNetwork:
    def __init__(self, master = False):
        print(type(Global))
        self.graph = nx.Graph()
        self.B     = 0 # default
        self.l_net = LogicalNetwork()
        #self.l_net = Set()
        self.debug = register_debugger(master = master)
        self.logical_nodes = []
        self.input_graph = None


    def destroy(self):
        close_debugger()


    '''
    Assuming file of format:
    grid
    B,<val>
    M,<val>
    N,<val>
    K,<val>
    seed,<val>
    '''
    def gen_grid_graph(self, M, N, K, seed):
        num_nodes = M*N
        skip  = seed % num_nodes
        node_list = ['e' for e in range(num_nodes)]
        self.logical_nodes = []
        logical_pos = skip
        for r_ix in range(1, K+1):
            while 'e' != node_list[logical_pos]
                logical_pos += 1
            node_list[logical_pos] = r_ix
            self.logical_nodes.append(r_ix)
            logical_pos += skip
        s_ix = K + 1
        for ix in range(len(node_list)):
            if 'e' == node_list[ix]
                node_list[ix] = s_ix
                s_ix += 1
        weighted_edges = []
        for row in range(len(M)):
            for col in range(len(N)):
                capacity = (seed * row + col ) % MAX_EDGE_CAPACITY
                if row < M-1:
                    weighted_edge = (node_list[row*N+col], node_list[(row+1)*N+col], {'capacity': capacity})
                    weighted_edges.append(weighted_edge)
                if col < N-1:
                    weighted_edge = (node_list[row*N+col], node_list[row*N+col+1],   {'capacity': capacity})
                    weighted_edges.append(weighted_edge)
        return weighted_edges


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
    def create_custom_graph(self, edges_lines):
        counter=0
        for line in edges_lines:
            if (len(line) < 3) or (line[0] == '#') :
                break
            counter += 1
        self.debug.assrt(counter > 0, "bad graph file!")
        edges_lines = edges_lines[:counter]
        input_edges = {(line[0], line[1]):int(line[2]) for line in edges_lines}
        #self.debug.logger("init_graph_from_file: input_edges=%s" % input_edges)
        #input_nodes = []
        self.logical_nodes = []
        for edge in input_edges.keys():
            for i in [0,1]:
                if not (int(edge[i][1:]) in self.logical_nodes):
                    if 'r' == edge[i][0]:
                        self.logical_nodes.append(int(edge[i][1:]))
        self.debug.logger("init_graph_from_file: logical_nodes=%s" % self.logical_nodes)
        weighted_edges = [(int(edge[0][1:]), int(edge[1][1:]), {'capacity':input_edges[edge]}) for edge in input_edges.keys()]
        return weighted_edges



    def init_graph_from_file(self, graph_file):
        with open(graph_file, 'r') as f:
            lines = [tuple(i[:-1].split(',')) for i in f]
        # we added functionality for grid generating
        if "grid" == lines[0]:
            self.B = int(lines[1][1])
            M    = int(lines[2][1])
            N    = int(lines[3][1])
            K    = int(lines[4][1])
            seed = int(lines[5][1])
            weighted_edges = self.gen_grid_graph(M, N, K, seed)
        else: # regular custom graph file
            self.B = int(lines[0][1])
            edges_lines = lines[1:]
            weighted_edges = self.create_custom_graph(edges_lines)
        self.graph.add_edges_from(weighted_edges)
        self.input_graph = copy.deepcopy(self.graph)

    '''
        return all logical nodes in pairs (r1,r2) s.t. r1 < r2
    '''
    def get_logical_pairs(self):
        pairs = []
        for r1 in sorted(self.get_logical_nodes()):
            for r2 in sorted(self.get_logical_nodes()):
                if r1 >= r2:
                    continue
                pairs.append((r1,r2))
        self.debug.logger("get_logical_pairs: %s" % (pairs))
        return pairs

    def get_links_from_path(self, path):
        links = []
        for ix in range(len(path)-1):
            n1 = min(path[ix], path[ix+1])
            n2 = max(path[ix], path[ix+1])
            links.append((n1, n2))
        return links


    def create_logical_graph(self, inc_factor = DEF_INC_FACTOR):
        self.debug.logger("create_logical_graph:")
        logical_graph = nx.Graph()
        gen = GEN

        for path in self.l_net.get_paths():
            self.debug.logger("create_logical_graph: process path = %s" % (path))
            self.debug.assrt(path >= 2, "create_logical_graph: bad logical path!")
            r1, r2 = path[0], path[-1]
            logical_graph.add_node(r1)
            logical_graph.add_node(r2)
            links = self.get_links_from_path(path)
            #formatted_nodes = [node+gen for node in path if ((node != r1) and (node != r2))]
            for link in links:
                weight = int(DEF_INC_FACTOR / float(self.get_plink_capacity((link[0], link[1]))))
                a = link[0] if ((link[0] == r1) or (link[0] == r2)) else link[0]+gen
                b = link[1] if ((link[1] == r1) or (link[1] == r2)) else link[1]+gen
                self.debug.logger(link)
                logical_graph.add_edge(a, b, weight = weight)
            gen += GEN
        self.debug.logger("create_logical_graph: logical_graph = %s" % (logical_graph.edges()))

        return logical_graph

    def get_routing_paths(self):
        return self.routing_paths_list

    def set_routing_paths(self):
        logical_graph = self.create_logical_graph()
        self.debug.logger("set_routing_paths: logical_graph=%s" % (logical_graph.edges()))
        routing_paths = nx.all_pairs_dijkstra_path(logical_graph, weight = 'WEIGHT')
        #self.debug.logger("set_routing_paths: routing_paths from dijkstra: %s" % (routing_paths))
        self.routing_paths_list = []
        logical_pairs = self.get_logical_pairs()
        for r1 in routing_paths.keys():
            for r2 in routing_paths[r1].keys():
                if (r1,r2) in logical_pairs:
                    self.debug.logger("set_routing_paths: (r1,r2)=(%s,%s)" % (r1,r2))

                    # route over all pairs
                    #path = routing_paths[r1][r2]
                    #for ix in range(len(path)):
                    #    path[ix] = path[ix] % GEN

                    # or route just over pairs not in in a logical path. (switch to first if it makes problems)
                    path = None
                    for _path in self.l_net.get_paths():
                        if r1 == _path[0] and r2 == _path[1]:
                            path = copy.deepcopy(_path)
                    if path == None:
                        path = routing_paths[r1][r2]
                        for ix in range(len(path)):
                            path[ix] = path[ix] % GEN

                    self.routing_paths_list.append(path)

        self.debug.logger("set_routing_paths: routing_list=%s" % (self.routing_paths_list))
        return self.routing_paths_list


    def reset_after_link_failure(self, link):
        self.debug.logger("reset_after_link_failure: link = (%s,%s)" % (link))
        new_paths = []
        for path in self.l_net.get_paths():
            if not (link in self.get_links_from_path(path)):
                new_paths.append(path)
        self.l_net.init_from_paths(new_paths)
        return  self.set_routing_paths()

    def calc_paths_diffs(self, olds, news):
        diffs = []
        for old in olds:
            for new in news:
                if old[0] == new[0] and old[-1] == new[-1]:
                    diffs.append((old, new))
        return diffs

    def get_modified_routing_paths(self, olds, news):
        modifieds = []
        diffs = self.calc_paths_diffs(olds, news)
        for diff in diffs:
            if diff[0] != diff[1]:
                modifieds.append(diff[1])
        return modifieds


    '''
        Return a dict:
            route_path -> bw

        BW comutation:
            first we define average BW on link: link_capacity / num_of_routes_traversing
            then we define the BW of a routing path to be the minimum of all its links
    '''
    def get_routing_with_bws(self):
        link_to_bw = {}
        link_to_traversing_routes = {}
        for link in self.physical_links():
            link_to_traversing_routes[link] = 0

        for routing_path in self.routing_paths_list:
            for link in self.get_links_from_path(routing_path):
                link_to_traversing_routes[link] += 1
                link_to_bw[link] = self.get_plink_capacity(link) / float(link_to_traversing_routes[link])

        connection_data = {}
        for route in self.routing_paths_list:
            min_bw = MAX_EDGE_CAPACITY
            for link in self.get_links_from_path(route):
                min_bw = min(min_bw, link_to_bw[link])
            connection_data[(route[0],route[-1])] = {}
            connection_data[(route[0],route[-1])]['BW']    = min_bw
            connection_data[(route[0],route[-1])]['ROUTE'] = route
        self.debug.logger("connection_data=%s " % (connection_data))
        return connection_data


    def get_logical_network(self):
        return self.l_net

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
	node_colors = []
	for node in g.nodes():
	    if self.is_logical_node(node):
	        node_colors.append('g')
	    else:
	        node_colors.append('r')

        nx.draw_networkx_nodes(g, pos, nodelist=g.nodes(), node_color=node_colors, node_size=500, alpha=0.8)
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
        plt.ion()
        plt.show()


class LogicalNetwork:
    def __init__(self):
        '''
            links: this is a dict that maps  edge to num_logical_paths_traversing_e.
             # while the end point of edge can be any 2 nodes
            paths: list of paths.
             - path: list of nodes v1, v2 ... , vk.  s.t: v1 and vk are logical nodes.
                                                   and all the rest can be logical or non-logical nodes.
                                                   all nodes unique.
            routing_paths: the current paths that data is routed on. this can be different than paths
                           *** We insert it to OpticalNetwork. maybe more suitable here..
        '''
        self.debug = register_debugger()
        self.paths = []
        self.max_SRLG = None

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
        return self.max_SRLG

    def merge(self, logical_network):
        self.paths = self.paths + logical_network.get_paths()
        self.init_from_paths(self.paths)

    def init_from_paths(self, paths):
        self.paths = paths
        self.links = {}
        self.traversing_paths = {}

        for path in self.paths:
            self.debug.assrt(len(path) > 1, 'init_link_to_paths: path with length 1')
            for node_ix in range(len(path)-1):
                link = (path[node_ix], path[node_ix+1])
                if link in self.traversing_paths.keys():
                    self.traversing_paths[link].append(path)
                    self.links[link] += 1
                else:
                    self.traversing_paths[link] = [path]
                    self.links[link] = 1
        self.debug.logger("init_from_paths: links=%s. paths=%s" % (self.links, self.paths))
        return self

    # update all data according to paths
    def update(self):
        self.init_from_paths(self.paths)
        self.calc_max_SRLG()


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


    ''' return list of paths traversing via this link '''
    def get_traversing_paths(self, link):
        if not (link in self.traversing_paths.keys()):
            return []
        return self.traversing_paths[link]

    def get_paths(self):
        return self.paths

    def set_paths(self, paths_in):
        self.paths = paths_in









