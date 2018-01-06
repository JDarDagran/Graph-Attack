import random
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from scipy.stats import bernoulli
from abc import ABCMeta, abstractmethod

class Node(object):
    def __init__(self, number):
        self.x = np.random.uniform(0,1)
        self.y = np.random.uniform(0,1)
        self.number = number
        self.neighbors = []
        self.visited = None
        
    def __repr__(self):
        return "%s, %s, nr = %s" % (self.x, self.y, self.number)

class GeneratedGraph(object):
    __metaclass__ = ABCMeta
    f = plt.figure(figsize=(7, 7), dpi=100)
    sp = f.add_subplot(111)
    no_of_nodes = 50
    
    def __init__(self):
        self.generate_nodes()
        checked_nodes = []
        for node1 in self.nodes:
            checked_nodes.append(node1)
            for node2 in self.nodes:
                if node2 in checked_nodes:
                    continue
                if self.check_connection(node1, node2):
                    self.connect_nodes(node1, node2)
                    
        self.find_largest_connected_graph()
        checked_nodes = []
        for node1 in self.nodes:
            checked_nodes.append(node1)
            for node2 in self.nodes:
                if node2 in checked_nodes:
                    continue
                if node2 in node1.neighbors:
#                     self.connect_nodes(node1, node2)
                    self.draw_connected_nodes(node1, node2)
    
    def generate_nodes(self):
        self.nodes = [Node(i) for i in range(0, self.no_of_nodes)]
        
    def draw_nodes(self, nodes = None, color = "C0"):
        if not nodes:
            nodes = self.nodes
        elif not isinstance(nodes, list):
            nodes = [nodes]
        self.sp.plot([el.x for el in nodes], [el.y for el in nodes], color+'o', markersize=2)
    
    @abstractmethod
    def check_connection(self, node1, node2):
        pass
        
    def connect_nodes(self, node1, node2):
        node1.neighbors.append(node2)
        node2.neighbors.append(node1)
        
    def draw_connected_nodes(self, node1, node2, color = "C0"):
        self.sp.plot([node1.x, node2.x], [node1.y, node2.y], color+"-", lw=0.2)
    
    def find_highest_degree(self):
        return max(self.nodes, key=lambda x: len(x.neighbors))
    
    def bfs(self):
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
#         print nodes
        return nodes
    
    def find_largest_connected_graph(self):
        to_throw = set(self.nodes) - self.bfs()
#         print set(self.nodes) - self.bfs(), len(set(self.nodes) - self.bfs())
        self.nodes = [node for node in self.nodes if not node in to_throw]
        print len(self.nodes)


#     def remove_node(self, node, from_whom):
#         for neighbor in node.neighbors:
#             if neighbor is not from_whom:
#                 print neighbor.number
#                 self.remove_node(neighbor, node)
#             self.draw_connected_nodes(neighbor, node, color="C1")
#             try:
#                 self.nodes.remove(node)
#             except:
#                 pass
#         self.draw_nodes(node, color="C3")
#         self.draw_nodes(node.neighbors, color="C1")
        
        
class BernoulliGraph(GeneratedGraph):
    r = 0.15
    
    def calc_dist(self, node1, node2):
        return math.sqrt(math.pow(node1.x-node2.x, 2)+math.pow(node1.y-node2.y, 2))
    
    def check_connection(self, node1, node2):
        return self.calc_dist(node1, node2) <= self.r
    
class ERGraph(GeneratedGraph):
    p = 0.05
    
    def check_connection(self, node1, node2):
        return bernoulli.rvs(self.p)