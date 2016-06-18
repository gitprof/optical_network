
import networkx as nx
import matplotlib.pyplot as plt
import itertools
from pulp import *
#from scipy.optimize import linprog
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
MM_SRLG:
    * there are 3 helper algorithm, and the main algorithm.
    * every algorithm that modify the original graph should deep copy it
'''
class MM_SRLG_solver:
    def __init__(self):
        self.debug = register_debugger('MM_SRLG')

    def ALG(self, opt_network):
        logical_network = LogicalNetwork()
        return logical_network

    def mm_srlg_arb(self, opt_network):
        self.debug.assrt(opt_network != None, 'mm_slrg_arb: optical_network is None!')
        # print(opt_network.graph.edges())
        half_b = int(math.ceil(opt_network.B/2))
        logical_network = None
        print('mm_srlg_arb: half_b = '+str(half_b))
        for C in range(1, half_b+1):
            print('C: '+str(C))
            opt_network.set_strict_capacity(C)
            logical_network = self.ALG(opt_network)
            if len(logical_network.paths) >= opt_network.B:
                break
        self.debug.assrt(logical_network != None, 'mm_slrg_arb: logical_network is None!')
        logical_network.choose_arbitrary_subset_of_size_b(opt_network.B)
        self.debug.logger('mm_srlg_arb: produced logical network: ')
        self.debug.logger(logical_network.paths)
        return logical_network

    def produce_cycle_aux(self, tree, cycle, ans, node):
        cycle.append((node, True))
        print('cycle_debug = ', cycle)
        next_neighbors = tree.neighbors(node)
        print('nbrs: ', node, '-', next_neighbors)
        if ans != node:
            next_neighbors.remove(ans)
        for neighbor in next_neighbors:
            cycle = self.produce_cycle_aux(tree, cycle, node, neighbor)
            cycle.append((node, False))
        return cycle

    def produce_cycle_from_tree(self, opt_network, tree):
        cycle = []
        start_node = None
        for node in opt_network.nodes():
            if opt_network.is_logical_node(node):
                start_node = node
                break
        self.debug.assrt(start_node is not None, "produce_cycle_from_tree: start node is None")
        self.produce_cycle_aux(tree, cycle, start_node, start_node)
        cycle.pop()
        cycle.append((start_node, True))
        self.debug.assrt((cycle != None) and (len(cycle) > 0), 'produce_cycle_from_tree: bad cycle')
        return cycle

    '''
    Params:
     cycle: list of nodes, first and last are the same logical node. all the logical nodes should be in the cycle
                all nodes are UNIQUE, except first and last
    '''
    def produce_subpaths_from_cycle(self, opt_network, cycle):
        curr_path = []
        paths = []
        last_logical_node = None
        first_node = True
        for (node, is_end_point) in cycle:
            curr_path.append(node)
            if first_node:
                first_node = False
                continue
            if opt_network.is_logical_node(node) and is_end_point:
                paths.append(curr_path)
                curr_path = [node]
        return paths


    def mm_srlg_cycle(self, opt_network):
        self.debug.logger('mm_srlg_cycle: optical_network: %s' % opt_network.physical_links())
        spanning_tree = opt_network.create_spanning_tree()
        self.debug.logger('mm_srlg_cycle: initial_tree: %s' % spanning_tree.edges())
        # print("mm_srlg_cycle:")
        # print(opt_network.get_logical_nodes())
        leaves = [node for node in spanning_tree.nodes() if ((spanning_tree.degree(node) == 1) and (not opt_network.is_logical_node(node)))]
        #self.debug.assrt((leaves != None) and (len(leaves) > 0), 'mm_srlg: no leaves!')
        while leaves != []:
            leaf = leaves.pop()
            neighbors = spanning_tree.neighbors(leaf)
            spanning_tree.remove_node(leaf)
            leaves = leaves + [node for node in neighbors if ((opt_network.node_degree(node) == 1) and (not opt_network.is_logical_node(node)))]

        self.debug.logger('mm_srlg_cycle: prunned_tree: %s' % spanning_tree.edges())
        cycle = self.produce_cycle_from_tree(opt_network, spanning_tree)
        self.debug.logger('mm_srlg_cycle: cycle: %s' % cycle)
        paths = self.produce_subpaths_from_cycle(opt_network, cycle)
        self.debug.assrt((paths != None) and (len(paths) > 0), 'mm_srlg_cycle: bad paths!')
        logical_network = LogicalNetwork().init_from_paths(paths)
        self.debug.logger('mm_srlg_cycle: produced logical network: %s ' % logical_network.get_paths())
        return logical_network

    def mm_srlg(self, opt_network):
        self.debug.assrt(opt_network.B >= len(opt_network.get_logical_nodes()), "mm_srlg: B must be bigger than num of logical nodes!")
        cycle_net = opt_network.clone()
        self.debug.assrt((opt_network != None) and (opt_network.B == cycle_net.B), 'mm_slrg: opt_network invalid!')
        EL_cycle  = self.mm_srlg_cycle(cycle_net)
        for e in sorted(opt_network.physical_links().keys()):
            num_lightpaths = EL_cycle.num_lightpaths_via_e(e)
            new_capacity   = cycle_net.get_plink_capacity(e) - num_lightpaths
            cycle_net.set_edge_capacity(e, new_capacity)
        opt_network.B = opt_network.B - len(opt_network.get_logical_nodes())
        print('mm_srlg: B left after cycle = '+str(opt_network.B))
        EL_arb        = self.mm_srlg_arb(opt_network) if (opt_network.B > 0) else LogicalNetwork()
        EL_arb.merge(EL_cycle)
        return EL_arb

    ''' Here we assume only 1 logical path between 2 routers
    '''
    def process_alg_output(self, prob, routers, nodes, edges):
        # self.debug.logger('process_alg_output:')
        self.debug.assrt("Optimal" == LpStatus[prob.status], "process_alg_output: ALG failed to find optimal solution!")

        paths_indicators = {}
        links_indicators = {}
        for v in prob.variables():
            s = v.name.split('_')
            if 'r' == s[0]:
                links_indicators[(int(s[2]), int(s[3]), int(s[4]), int(s[5]))] = v.varValue
            if 'l' == s[0]:
                paths_indicators[(int(s[1]), int(s[2]))]                       = v.varValue

        logical_paths = []
        #print(routers)
        #print(nodes)
        # print('paths_indicators:')
        # print(paths_indicators)

        for r1 in routers:
            for r2 in routers:
                if r1 >= r2 or paths_indicators[(r1,r2)] == 0:
                    continue
                curr_node = r1
                curr_path = [curr_node]
                while curr_node != r2:
                    next_node = None
                    for n in nodes:
                        try:
                            if (((curr_node, n) in edges) or ((n, curr_node) in edges)) and links_indicators[(r1,r2,curr_node,n)] > 0:
                                next_node = n
                                break
                        except KeyError:
                            donothing = 0
                    self.debug.assrt(next_node != None, "process_alg_output: didnt find next node in path!")
                    curr_path.append(next_node)
                    links_indicators[(r1,r2,curr_node,next_node)] = 0
                    curr_node = next_node

                logical_paths.append(curr_path)
                paths_indicators[(r1,r2)] = 0
        self.debug.assrt(value(prob.objective) == len(logical_paths), "process_alg_output: didnt find enough logical paths!")
        return logical_paths


    def ALG(self, opt_network):
        self.debug.logger('ALG:')
        V_p            = opt_network.nodes()
        physical_links = opt_network.physical_links()
        E_p            = physical_links.keys()
        V_l            = opt_network.get_logical_nodes()
        edge_to_capacity = copy.deepcopy(physical_links)
        for (i,j) in physical_links.keys():
            edge_to_capacity[(j,i)] = physical_links[(i,j)]
        logical_paths = self.ALG_inner(V_p, E_p, V_l, edge_to_capacity)
        logical_network = LogicalNetwork()
        logical_network.init_from_paths(logical_paths)
        self.debug.logger('ALG: produced logical network: ')
        self.debug.logger(logical_network.paths)
        return logical_network


    def ALG_inner(self, V_p, E_p, V_l, edge_to_capacity):
        # print("\nALG_inner:")
        # print(V_p)
        # print(E_p)
        # print(V_l)

        #create two networkX graphs
        G = nx.Graph()
        G_log = nx.Graph()

        G.add_nodes_from(V_p)
        G.add_edges_from(E_p)

        G_log.add_nodes_from(V_l)
        #G_log is the logical graph(clique)
        G_log.add_edges_from(list(itertools.combinations(V_l ,2)))

        #debug - draw graph
        #nx.draw(G)
        #plt.show()

        #add l_u_v variables as var attributes on G_log's edges
        for (_u,_v) in G_log.edges():
            u = min(_u, _v)
            v = max(_u, _v)
            G_log[u][v]['l_var'] = LpVariable("l_%d_%d" % (u,v), 0, 1,LpInteger)
            G_log[u][v]['r_vars'] = {}

        #add r_e_i_j_u_v variables as r_vars dictionary on G's edges
        #r_e_i_j_u_v meaning - is the logical link u,v passes on the physical link i,j
        for i,j in G.edges():
            G[i][j]['c'] = edge_to_capacity[(i,j)]
            G[i][j]['r_vars'] = {}
            for _u,_v in G_log.edges():
                u = min(_u, _v)
                v = max(_u, _v)
                #add 2 r_e vars one for i,j the other for j,i
                var1 = LpVariable("r_e_%d_%d_%d_%d" % (u,v,i,j), 0, 1,LpInteger)
                var2 = LpVariable("r_e_%d_%d_%d_%d" % (u,v,j,i), 0, 1,LpInteger)
                #add reference both from G and G_log
                G[i][j]['r_vars']['%d_%d' % (u,v)]  = [var1, var2]
                G_log[u][v]['r_vars']['%d_%d' % (i,j)] = var1
                G_log[u][v]['r_vars']['%d_%d' % (j,i)] = var2

        #init problem as a maximiztion problem using Pulp
        prob = LpProblem("ALG",LpMaximize)
        L_var = LpVariable("L",cat = LpInteger)

        #add objective function to prob
        prob += L_var

        #add capacity constraints
        for i,j in G.edges():
            r_vars = []
            for (var1,var2) in G[i][j]['r_vars'].values():
                r_vars.extend([var1,var2])
            prob += sum(r_vars) <= G[i][j]['c'], "%d_%d capacity constaraint" % (i,j)

        #add logical link number constraint
        prob += sum(G_log[u][v]['l_var'] for u,v in G_log.edges()) == L_var, "L_var constraint"

        #add valid path constraints
        for _u,_v in G_log.edges():
            u = min(_u, _v)
            v = max(_u, _v)
            for i in G.nodes():
                edges_in = []
                edges_out = []
                for j in G.neighbors(i):
                    edges_in.append(G_log[u][v]['r_vars']['%d_%d' % (j,i)])
                    edges_out.append(G_log[u][v]['r_vars']['%d_%d' % (i,j)])

                if i == u:
                    prob += sum(edges_in) - sum(edges_out) == - G_log[u][v]['l_var'],"path constarint (u,v,i) = (%d,%d,%d)" % (u,v,i)
                elif i == v:
                    prob += sum(edges_in) - sum(edges_out) ==  G_log[u][v]['l_var'],"path constarint (u,v,i) = (%d,%d,%d)" % (u,v,i)
                else:
                    prob += sum(edges_in) - sum(edges_out) == 0 ,"path constarint (u,v,i) = (%d,%d,%d)" % (u,v,i)

        prob.solve()

        #print("Status:", LpStatus[prob.status])
        # The optimised objective function value is printed to the screen
        #print("L = ", value(prob.objective))
        # Each of the variables is printed with it's resolved optimum value
        #for v in prob.variables():
        #    print(v.name, "=", v.varValue)

        # print("ALG_inner: end")
        logical_paths = self.process_alg_output(prob, V_l, V_p, E_p)
        return logical_paths
