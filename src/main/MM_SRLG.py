
import math
import copy

class MM_SRLG:
    def __init__(self):



    def alg(self, opt_network):
        

    def mm_srlg_arb(self, opt_network):
        half_b = math.ceil()
        for C in range(1, half_b+1):
            new_c = min(C, )

    def mm_srlg_cycle(self, opt_network):
        opt_network.create_spanning_tree()
        leaves = [node for node in opt_network if ((opt_network.node_degree(node) == 1) and (not opt_network.is_logical_node(node)))]
        while leaves is not []:
            leaf = leaves.pop()
            neighbors = opt_network.node_neighbours(leaf)
            opt_network.remove_node(leaf)
            leaves = leaves + [node for node in neighbors if ((opt_network.node_degree(node) == 1) and (not opt_network.is_logical_node(node)))]
        cycle_list       = opt_network.produce_cycle_from_tree()
        logical_netowork = LogicalNetwork().init_from_cycle(cycle_list)
        return logical_network

    def mm_srlg(self, opt_network):
        cycle_net = copy.deecopy(opt_network)
        EL_cycle  = self.mm_srlg_cycle(cycle_net)
        for e in opt_network.physical_links():
            num_lightpaths = EL_cycle.num_lightpahts_via_e(e)
            new_capacity   = cycle_net.get_plink_capacity(e) - num_lightpaths
            cycle_net.set_plink_capacity(e, new_capacity)
        opt_network.B = opt_network.B - opt_network.num_logical_nodes()
        EL_arb        = self.mm_srlg_arb(opt_network)
        return EL_arb.merge(EL_cycle)
        
            
