class Node:

    def __init__(self, coords, id):
        self.coords = coords
        self.id = id
        self.edges = []
        self.distance = float("inf")
        self.visited = False 
        self.previous = None
        self.previous_edge = None
        self.traversals = 0
    
    def set_distance(self, dist):
        self.distance = dist
    
    def get_distance(self):
        return self.distance

    def set_visited(self):
        self.visited = True
    
    def get_id(self):
        return self.id
    
    def get_coords(self):
        return self.coords
    
    # def get_geo(self):
        # return rh.Point3d(self.get_coords())
        # return self.get_coords()
    
    def get_dist(self, p):
        p2 = self.get_coords()
        return ((p[0] - p2[0])**2 + (p[1] - p2[1])**2 + (p[2] - p2[2])**2) ** .5
    
    def get_edges(self):
        return self.edges
    
    def get_adjacent(self):
        adjacent = []
        edges = []
        for edge in self.get_edges():
            for node in edge.get_nodes():
                if node not in adjacent and node != self:
                    adjacent.append(node)
                    edges.append(edge)
        return adjacent, edges
    
    def set_previous(self, prev):
        self.previous = prev
    
    def get_previous(self):
        return self.previous
    
    def set_previous_edge(self, prev):
        self.previous_edge = prev
    
    def add_edge(self, edge):
        if edge not in self.get_edges():
            self.edges.append(edge)
    
    def add_traversal(self, weight = 1):
        self.traversals += weight
    
    def get_traversal(self):
        return self.traversals
    
    def reset(self):
        self.distance = float("inf")
        self.visited = False 
        self.previous = None 
        self.previous_edge = None 

class Edge:

    def __init__(self, nodes, id):
        self.nodes = nodes
        self.id = id
        self.cost = nodes[0].get_dist(nodes[1].get_coords())
        self.traversals = 0
    
    def get_id(self):
        return self.id
    
    def get_cost(self):
        return self.cost
    
    def get_nodes(self):
        return self.nodes
    
    def add_traversal(self, weight = 1):
        self.traversals += weight
    
    def get_traversal(self):
        return self.traversals
    
    # def get_geo(self):
        # return rh.Line(self.nodes[0].get_geo(), self.nodes[1].get_geo())

class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def find_node(self, p, err):
        for node in self.nodes:
            if node.get_dist(p) < err:
                return node
        return None

    def find_closest_node(self, p, err):
        min_dist = float("inf")
        min_node = None
        for node in self.nodes:
            if node.get_dist(p) < min_dist:
                min_dist = node.get_dist(p)
                min_node = node
        return min_node
    
    def get_edges(self):
        return self.edges
    
    def get_nodes(self):
        return self.nodes

    def add_node(self, p):
        node_id = len(self.get_nodes())
        new_node = Node(p, node_id)
        self.nodes.append(new_node)
        return new_node

    def add_edge(self, line, err):
        edge_id = len(self.get_edges())
        
        l = line.ToNurbsCurve()
        
        nodes = []
        for i, p in enumerate([l.PointAtStart, l.PointAtEnd]):
            nodes.append(self.find_node(p, err))
            if nodes[-1] is None:
                nodes[-1] = self.add_node(p)
        
        new_edge = Edge(nodes, edge_id)
        self.edges.append(new_edge)
        
        for node in nodes:
            node.add_edge(new_edge)
    
    def reset(self):
        for node in self.get_nodes():
            node.reset()
    
    def __str__(self):
        output = []
        
        output.append("---nodes---")
        for node in self.get_nodes():
            nodeString = "%2i --> coords: %s, edges: %s" % (node.get_id(), node.get_coords(), ", ".join([str(x.get_id()) for x in node.get_edges()]))
            output.append(nodeString)
        
        output.append("---edges---")
        for edge in self.get_edges():
            edgeString = "%2i --> cost: %0.2f, nodes: %s" % (edge.get_id(), edge.get_cost(), ", ".join([str(x.get_id()) for x in edge.get_nodes()]))
            output.append(edgeString)
        
        return "\n".join(output)

def lines2graph(lines, err=0.001):
    graph = Graph()

    for line in lines:
        graph.add_edge(line, err)

    return graph

#DIJKSTRA shortest path implementation
#http://www.bogotobogo.com/python/python_Dijkstras_Shortest_Path_Algorithm.php

def shortest(v, path_nodes, path_edges):
    ''' make shortest path from v.previous'''
    
    if v.previous:
        path_nodes.append(v.previous)
        path_edges.append(v.previous_edge)
        shortest(v.previous, path_nodes, path_edges)
    return

import heapq

def dijkstra(graph, start):
    # Set the distance for the start node to zero 
    start.set_distance(0)

    # Put tuple pair into the priority queue
    unvisited_queue = [(v.get_distance(),v) for v in graph.get_nodes()]
    heapq.heapify(unvisited_queue)

    while len(unvisited_queue):
        # Pops a vertex with the smallest distance 
        uv = heapq.heappop(unvisited_queue)
        current = uv[1]
        current.set_visited()

        adjacent, edges = current.get_adjacent()
        
        for i, next in enumerate(adjacent):
            # if visited, skip
            if next.visited:
                continue
            new_dist = current.get_distance() + edges[i].get_cost()
            
            if new_dist < next.get_distance():
                next.set_distance(new_dist)
                next.set_previous(current)
                next.set_previous_edge(edges[i])
        
        # Rebuild heap
        # 1. Pop every item
        while len(unvisited_queue):
            heapq.heappop(unvisited_queue)
        # 2. Put all vertices not visited into the queue
        unvisited_queue = [(v.get_distance(),v) for v in graph.get_nodes() if not v.visited]
        heapq.heapify(unvisited_queue)