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
    no_of_nodes = 1000
    
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
#         checked_nodes = []
#         for node1 in self.nodes:
#             checked_nodes.append(node1)
#             for node2 in self.nodes:
#                 if node2 in checked_nodes:
#                     continue
#                 if node2 in node1.neighbors:
# #                     self.connect_nodes(node1, node2)
#                     self.draw_connected_nodes(node1, node2)
    
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
        return max([node for node in self.nodes if node.visited != True], key=lambda x: len(x.neighbors))
    
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
        self.set_visited_flag(self.nodes, False)
        return nodes
    
    def find_largest_connected_graph(self):
        to_throw = set(self.nodes) - self.bfs()
        self.nodes = [node for node in self.nodes if not node in to_throw]
        print len(self.nodes)
        
    def disable_nodes(self, q):
        attacked_nodes = random.sample(self.nodes, int(q*len(self.nodes)))
        self.set_visited_flag(attacked_nodes, True)
        return len([node for node in self.nodes if node.visited == True])
        
    def set_visited_flag(self, nodes, flag):
        map(lambda x: setattr(x, "visited", flag), nodes)
        
    def make_an_attack(self,q):
        no_of_attacked = self.disable_nodes(q)
        connected_graph = self.bfs()
        print len(self.nodes), no_of_attacked, len(connected_graph)
        return len(self.nodes) - no_of_attacked == len(connected_graph)
        
        
class BernoulliGraph(GeneratedGraph):
    r = 0.05
    
    def calc_dist(self, node1, node2):
        return math.sqrt(math.pow(node1.x-node2.x, 2)+math.pow(node1.y-node2.y, 2))
    
    def check_connection(self, node1, node2):
        return self.calc_dist(node1, node2) <= self.r
    
class ERGraph(GeneratedGraph):
    p = 0.05
    
    def check_connection(self, node1, node2):
        return bernoulli.rvs(self.p)