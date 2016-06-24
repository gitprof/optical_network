import networkx as nx
import copy
from OpticalNetwork import LogicalNetwork
from OpticalNetwork import OpticalNetwork

class DP:
    def slove(optical_network):
        graph = copy.deepcopy(optical_network.graph)
        optical_network.l_net = self.solve_inner(graph, optical_network.get_logical_nodes() ,optical_network.B)
    def solve_inner(self,graph,logicalNodes,X):
        paths = []
        counter = 0;
        sortedList = self.getSortedListOfPaths(graph,logicalNodes)
        deletedEdges = []
        for (u,v,path) in sortedList:
            if(counter >= X):
                break
            else:
                counter+=1        
                (path,deletedEdges) = self.DisjointPaths(graph,u,v,deletedEdges,False)
                if(path==[]):
                    continue
                else:
                    paths.append((u,v,path))    
        logical_network = LogicalNetwork()
        list_of_paths = [x[2] for x in paths]
        logical_network.init_from_path(list_of_paths)
        return logical_network
    
    def DisjointPaths(self,graph,s,t,deletedEdges,restored):
        for (u,v,w) in graph.edges(data='weight'):
                if(w==0):
                    graph.remove_edge(u,v)
        
        #if t is not reachable from s
        if (t in nx.algorithms.dag.descendants(graph,s))==False:
            if restored==True:
                return ([],deletedEdges)
            #restore deleted edges:        
            for (u,v,w) in deletedEdges:
                graph.add_edge(u,v,weight=w)
                return self.DisjointPaths(graph,s,t,deletedEdges,True)
            
        else:
            path = nx.shortest_path(graph,source=s,target=t)
            for i in range(0,(len(path))-1):
            #while (len(path)>1):        
                u=path[i]
                v=path[i+1]
                #del path[0]
                deletedEdges.append((u,v,graph[u][v]['weight']-1))              
                graph.remove_edge(u,v)
            return (path, deletedEdges)   
			
    def getSortedListOfPaths(self,graph,logicalNodes):
        path = nx.all_pairs_dijkstra_path(graph)
        lst = []
        for u in logicalNodes:
            for v in logicalNodes:
                if (u>=v):
                    continue
                lst.append((u,v,path[u][v]))
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