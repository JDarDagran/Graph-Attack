import random
import numpy as np
import math
import matplotlib.pyplot as plt
import json
import datetime
from matplotlib.figure import Figure
from scipy.stats import bernoulli
import os
from abc import abstractmethod, ABCMeta

class Node(object):
    """
    Class for node object.
    """
    def __init__(self, number):
        self.x = np.random.uniform(0,1)
        self.y = np.random.uniform(0,1)
        self.number = number
        self.neighbors = []
        self.visited = None
        
    def __repr__(self):
        return "%s, %s, nr = %s" % (self.x, self.y, self.number)


class GeneratedGraph(object):
    """
    Parent class for random generated graphs.
    
    Example usages: 
    
    >>> ChildGraph(stat = 0.1, no_of_nodes = 1000)
    >>> ChildGraph(stat = 0.05, draw_flag = True) #draws plots self.f1, self.f2, self.f3
    >>> ChildGraph(load_graph = 'ChildGraph_100_20180111210321.graph') #loads graph from text file
    
    To show graphs run:  >>> self.f1.show()
    """
    
    ### Mark as abstract class (require implementation of abstract method).
    __metaclass__ = ABCMeta
    
    ### How faded objects from second plan should be
    faded_alpha = 0.3
    
    ### Graph specific parameter name (only for drawing purpose)
    parameter_name = "param"
    
    def __init__(self, stat = None, no_of_nodes = 100, load_graph = None, draw_flag = None):
        self.nodes_to_save = no_of_nodes
        if draw_flag:
            ### Init plots
            self.f1 = plt.figure(figsize=(10, 10), dpi=100)
            self.f2 = plt.figure(figsize=(10, 10), dpi=100)
            self.f3 = plt.figure(figsize=(10, 10), dpi=100)
            self.sp1 = self.f1.add_subplot(111)
            self.sp2 = self.f2.add_subplot(111)
            self.sp3 = self.f3.add_subplot(111)
        else:
            self.sp1 = None
            self.sp2 = None
            self.sp3 = None
        self.no_of_nodes = no_of_nodes
        self.draw_flag = draw_flag
        
        if load_graph:
            self.load_nodes_from_file(load_graph)
        else:
            self.generate_nodes()
            
        self.stat = stat
        
        ### Draw all generated nodes
        self.draw_nodes(self.sp1, self.nodes, alpha=1.0)
        
        if load_graph is None:
            ### Generate connection, connect nodes (and draw connections)
            for i in  range(0, len(self.nodes)):
                node1 = self.nodes[i]
                if i % 1000 == 0 and i>0:
                    print i
                for j in range(i, len(self.nodes)):
                    node2 = self.nodes[j]
                    if self.check_connection(node1, node2):
                        self.connect_nodes(node1, node2)
                        self.draw_connected_nodes(self.sp1, node1, node2, color="C0")
            self.draw_nodes(self.sp2, self.nodes, alpha=0.1)
            
        else:
            ### Connect nodes (and draw connections)
            for i in range(0, len(self.nodes)):
                node1 = self.nodes[i]
                for j in range(i, len(self.nodes)):
                    node2 = self.nodes[j]
                    if node1.number in node2.neighbors:
                        self.connect_nodes(node1, node2)
                        self.draw_connected_nodes(self.sp1, node1, node2, color="C0")
                node1.neighbors = [el for el in  node1.neighbors if not isinstance(el, int)]
        
        self.no_of_edges = 0
        
        self.nodes = self.find_largest_connected_graph()
        for i in  range(0, len(self.nodes)):
            node1 = self.nodes[i]
            for j in range(i, len(self.nodes)):
                node2 = self.nodes[j]
                if node2 in node1.neighbors:
                    self.draw_connected_nodes(self.sp2, node1, node2, color="C1")
                    self.no_of_edges += 1
                    
        ### Draw largest graph's nodes
        self.draw_nodes(self.sp2, self.nodes, color="C1")
        
        
        ### Set some descriptions
        if draw_flag:
            self.sp1.set_title(self._u('{0}, liczba wierzchołków: {1}'.format(self.__class__.__name__, self.nodes_to_save)))
            self.sp2.set_title(self._u('{}, liczba wierzchołków: {}, liczba wierzchołków największego spójnego grafu {}, {}={:0.5f}'.format(self.__class__.__name__, self.nodes_to_save, self.no_of_nodes, self.parameter_name, self.stat)))
    
    def _u(self, t):
        """
        Util method. Decode ASCII to UTF-8.
        """
        return t.decode('UTF-8', 'replace') if isinstance(t, str) else t
    
    @staticmethod
    def to_dict(node):
        """
        Write node as dictionary (for save to file purpose).
        """
        return {"number": node.number, "x": node.x, "y": node.y, "neighbors": [el.number for el in node.neighbors]}
    
    @staticmethod
    def from_dict(nodes_dict):
        """
        Load node from dictionary (for load from file purpose).
        """
        n = Node(nodes_dict["number"])
        n.x = nodes_dict["x"]
        n.y = nodes_dict["y"]
        n.neighbors = nodes_dict["neighbors"]
        return n
    
    def load_nodes_from_file(self, nodes_file):
        """
        Load nodes from nodes_file.
        """
        with open(nodes_file, "r") as f:
            nodes = [GeneratedGraph.from_dict(el) for el in json.load(f)]
        self.nodes = nodes
        self.no_of_nodes = len(nodes)
    
    def write_nodes_to_file(self, directory = "graphs", filename = None):
        """
        Write graph to text file (extension .graph).
        If directory does not exist, create it.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not filename:
            filename = self.__class__.__name__+"_"+str(self.nodes_to_save)+"_"+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+".graph"
        with open(os.path.join(directory, filename), "w+") as f:
            json.dump([GeneratedGraph.to_dict(el) for el in self.nodes], f)
    
    def generate_nodes(self):
        """
        Generate nodes
        """
        self.nodes = [Node(i) for i in range(0, self.no_of_nodes)]
        
    def draw_nodes(self, fig, nodes = None, color = "C0", alpha = 1.0):
        """
        Draw nodes on [0,1]x[0,1] plain.
        """
        if not self.draw_flag:
            return
        if not nodes:
            nodes = self.nodes
        elif not isinstance(nodes, list):
            nodes = [nodes]
        fig.plot([el.x for el in nodes], [el.y for el in nodes], 'o', alpha=alpha, color=color, markersize=2)
    
    @abstractmethod
    def check_connection(self, node1, node2):
        """
        Abstract method. Implement connection between nodes condition here.
        """
        pass
        
    def connect_nodes(self, node1, node2):
        """
        Append nodes to each others neighbors if connected.
        """
        node1.neighbors.append(node2)
        node2.neighbors.append(node1)
        
    def draw_connected_nodes(self, fig, node1, node2, color = "C0", alpha = 1.0, linestyle = '-', lw=0.2):
        if not self.draw_flag:
            return
        fig.plot([node1.x, node2.x], [node1.y, node2.y], linestyle = linestyle, color=color, alpha = alpha, lw=lw)
    
    def find_highest_degree(self):
        """
        Find highest degree node from unvisited nodes.
        """
        return max([node for node in self.nodes if node.visited != True], key=lambda x: len(x.neighbors))
    
    def bfs(self):
        """
        Breadth-first search algorithm implementation.
        Return all visited nodes.
        """
        q = [self.find_highest_degree()]
        q[0].visited = True
        nodes = set(q)
        while len(q) > 0:
            v = q.pop()
            for node in v.neighbors:
                if not node.visited:
                    q.append(node)
                    node.visited = True
                    nodes.add(node)
        self.set_visited_flag(self.nodes, False)
        return nodes
    
    def find_largest_connected_graph(self):
        largest_connected_graph = set()
        while len(largest_connected_graph) < len(self.nodes):
            largest_connected_graph = self.bfs()
            to_throw = set(self.nodes) - self.bfs()
            self.nodes = [node for node in self.nodes if not node in to_throw]
            self.no_of_nodes = len(self.nodes)
        return list(largest_connected_graph)
        
    def disable_nodes(self, q):
        """
        Pick random sample from all nodes and set visited flag to True.
        """
        attacked_nodes = random.sample(self.nodes, int(q*len(self.nodes)))
        self.set_visited_flag(attacked_nodes, True)
        self.draw_nodes(self.sp3, attacked_nodes, "#0F0F0F", alpha=0.3)
        return len([node for node in self.nodes if node.visited == True])
        
    def set_visited_flag(self, nodes, flag):
        map(lambda x: setattr(x, "visited", flag), nodes)
        
    def make_an_attack(self,q):
        """
        Single attack method.
        
        Uses breadth-first search algorithm to check if attack succeeded.
        """
        no_of_attacked = self.disable_nodes(q)
        self.draw_attacked_graph(self.sp3, self.nodes)
        connected_graph = self.bfs()
        if self.sp3:
            self.sp3.set_title(self._u('{}, liczba wierzchołków: {}, liczba zaatakowanych wierzchołków: {}, atak: {}'.format(self.__class__.__name__, self.no_of_nodes, no_of_attacked, "UDANY" if len(self.nodes) - no_of_attacked != len(connected_graph) else "NIEUDANY")))
        return len(self.nodes), no_of_attacked, len(connected_graph), len(self.nodes) - no_of_attacked != len(connected_graph)
    
    def draw_attacked_graph(self, fig, nodes):
        """
        Draw attacked graph.
        
        Attacked nodes are less transparent and in different color. Also connection between them and other nodes are not included.
        """
        if not self.draw_flag:
            return
        self.draw_nodes(self.sp3, [node for node in self.nodes if node.visited != True], color="C1")
        self.draw_nodes(self.sp3, [node for node in self.nodes if node.visited == True], color = "#C0C0C0", alpha=self.faded_alpha)
        checked_nodes = []
        for node1 in nodes:
            checked_nodes.append(node1)
            for node2 in self.nodes:
                if node2 in checked_nodes:
                    continue
                if (node1.visited or node2.visited) and node2 in node1.neighbors:
                    self.draw_connected_nodes(self.sp3, node1, node2, alpha=0.3,  color = "#C0C0C0", linestyle = '--', lw=0.2)
                    continue
                if node2 in node1.neighbors:
                    self.draw_connected_nodes(self.sp3, node1, node2,  color = "C5")
        
        
class EuclideanGraph(GeneratedGraph):
    """
    Euclidean graph implementation.
    """
    parameter_name = "r"
    def calc_dist(self, node1, node2):
        return math.sqrt(math.pow(node1.x-node2.x, 2)+math.pow(node1.y-node2.y, 2))
    
    def check_connection(self, node1, node2):
        return self.calc_dist(node1, node2) <= self.stat
    
class ERGraph(GeneratedGraph):
    """
    Erdos–Renyi graph implementation.
    """
    parameter_name = "p"
    def check_connection(self, node1, node2):
        return bernoulli.rvs(self.stat)