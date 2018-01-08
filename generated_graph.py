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
    f1 = plt.figure(figsize=(10, 10), dpi=100)
    f2 = plt.figure(figsize=(10, 10), dpi=100)
    f3 = plt.figure(figsize=(10, 10), dpi=100)
    sp1 = f1.add_subplot(111)
    sp2 = f2.add_subplot(111)
    sp3 = f3.add_subplot(111)
    faded_alpha = 0.3
#     no_of_nodes = 100
    
    def __init__(self, stat, no_of_nodes = 100, nodes = None, draw_flag = None):
        self.no_of_nodes = no_of_nodes
        self.draw_flag = draw_flag
        if nodes:
            self.nodes = nodes
        else:
            self.generate_nodes()
        self.stat = stat
        self.draw_nodes(self.sp1, self.nodes, alpha=1.0)
        checked_nodes = []
        for node1 in self.nodes:
            checked_nodes.append(node1)
            for node2 in self.nodes:
                if node2 in checked_nodes:
                    continue
                if self.check_connection(node1, node2):
                    self.connect_nodes(node1, node2)
                    self.draw_connected_nodes(self.sp1, node1, node2, color="C0")
                    
        self.draw_nodes(self.sp2, self.nodes, alpha=0.1)
        
        self.no_of_edges = 0
        self.nodes = self.find_largest_connected_graph()
        checked_nodes = []
        for node1 in self.nodes:
            checked_nodes.append(node1)
            for node2 in self.nodes:
                if node2 in checked_nodes:
                    continue
                if node2 in node1.neighbors:
                    self.draw_connected_nodes(self.sp2, node1, node2, color="C1")
                    self.no_of_edges += 1
        self.draw_nodes(self.sp2, self.nodes, color="C1")
    
    
    def generate_nodes(self):
        self.nodes = [Node(i) for i in range(0, self.no_of_nodes)]
        
    def draw_nodes(self, fig, nodes = None, color = "C0", alpha = 1.0):
        if not self.draw_flag:
            return
        if not nodes:
            nodes = self.nodes
        elif not isinstance(nodes, list):
            nodes = [nodes]
        fig.plot([el.x for el in nodes], [el.y for el in nodes], 'o', alpha=alpha, color=color, markersize=2)
    
    @abstractmethod
    def check_connection(self, node1, node2):
        pass
        
    def connect_nodes(self, node1, node2):
        node1.neighbors.append(node2)
        node2.neighbors.append(node1)
        
    def draw_connected_nodes(self, fig, node1, node2, color = "C0", alpha = 1.0, linestyle = '-', lw=0.2):
        if not self.draw_flag:
            return
        fig.plot([node1.x, node2.x], [node1.y, node2.y], linestyle = linestyle, color=color, alpha = alpha, lw=lw)
    
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
        largest_connected_graph = set()
        while len(largest_connected_graph) < len(self.nodes):
            largest_connected_graph = self.bfs()
            to_throw = set(self.nodes) - self.bfs()
            self.nodes = [node for node in self.nodes if not node in to_throw]
        print len(largest_connected_graph)
        return list(largest_connected_graph)
        
    def disable_nodes(self, q):
        attacked_nodes = random.sample(self.nodes, int(q*len(self.nodes)))
        self.set_visited_flag(attacked_nodes, True)
        self.draw_nodes(self.sp3, attacked_nodes, "#0F0F0F", alpha=0.3)
        return len([node for node in self.nodes if node.visited == True])
        
    def set_visited_flag(self, nodes, flag):
        map(lambda x: setattr(x, "visited", flag), nodes)
        
    def make_an_attack(self,q):
        no_of_attacked = self.disable_nodes(q)
        self.draw_attacked_graph(self.sp3, self.nodes)
        connected_graph = self.bfs()
#         self.draw_nodes(list(connected_graph), color="C5")
        print len(self.nodes), no_of_attacked, len(connected_graph)
        return len(self.nodes) - no_of_attacked != len(connected_graph)
    
    def draw_attacked_graph(self, fig, nodes):
        if not self.draw_flag:
            return
        self.draw_nodes(self.sp3, [node for node in self.nodes if node.visited != True], color="C1")
        self.draw_nodes(self.sp3, [node for node in self.nodes if node.visited == True], color = "#C0C0C0", alpha=self.faded_alpha)
        checked_nodes = []
        for node1 in nodes:
            checked_nodes.append(node1)
#             if node1.visited:
#                 continue
            for node2 in self.nodes:
                if node2 in checked_nodes:
                    continue
                if (node1.visited or node2.visited) and node2 in node1.neighbors:
                    self.draw_connected_nodes(self.sp3, node1, node2, alpha=0.3,  color = "#C0C0C0", linestyle = '--', lw=0.2)
                    continue
                if node2 in node1.neighbors:
                    self.draw_connected_nodes(self.sp3, node1, node2,  color = "C5")
        
        
class BernoulliGraph(GeneratedGraph):
    
    def calc_dist(self, node1, node2):
        return math.sqrt(math.pow(node1.x-node2.x, 2)+math.pow(node1.y-node2.y, 2))
    
    def check_connection(self, node1, node2):
        return self.calc_dist(node1, node2) <= self.stat
    
class ERGraph(GeneratedGraph):
    def check_connection(self, node1, node2):
        return bernoulli.rvs(self.stat)