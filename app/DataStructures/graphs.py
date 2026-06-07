from collections import deque
import heapq

class WeightedGraph:
    def __init__(self, V):
        self.V = V
        # List of lists: har node store karega (neighbor, weight)
        self.adj = [[] for _ in range(V)] 
    
    def add_edge(self, u, v, weight):
        """Do points ke darmiyan rasta aur uska weight add karein"""
        # Check if edge already exists to avoid duplicates
        if not any(neighbor == v for neighbor, _ in self.adj[u]):
            self.adj[u].append((v, weight))
        if not any(neighbor == u for neighbor, _ in self.adj[v]):
            self.adj[v].append((u, weight))  # Undirected graph ke liye
        
    def dijkstra(self, start, end):
        """Sab se sasta/chota rasta dhoondne ke liye"""
        
        distances = [float('inf')] * self.V
        distances[start] = 0
        
        
        parent = [-1] * self.V
        
        
        pq = [(0, start)]
        
        while pq:
            current_distance, u = heapq.heappop(pq)
            
            
            if current_distance > distances[u]:
                continue
                
            
            for neighbor, weight in self.adj[u]:
                distance = current_distance + weight
                
                # Agar naya rasta purane se chota hai (Relaxation)
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    parent[neighbor] = u
                    heapq.heappush(pq, (distance, neighbor))
        
        # Path reconstruction
        path = []
        curr = end
        if distances[end] == float('inf'):
            return None, float('inf')  # Rasta nahi mila
            
        while curr != -1:
            path.append(curr)
            curr = parent[curr]
            
        return path[::-1], distances[end]
    
    def print_graph(self):
        """Print the adjacency list representation of the graph"""
        for v in range(self.V):
            print(f"Adjacency list of vertex {v}")
            print("head", end="")
            for neighbor, weight in self.adj[v]:  # FIXED: Unpack tuple
                print(f" -> ({neighbor}, w:{weight})", end="")
            print()
    
    def bfs(self, start=0):
        """Breadth-First Search traversal starting from vertex 'start'"""
        queue = deque()
        visited = [False] * self.V
        
        queue.append(start)
        visited[start] = True
        
        print("BFS Traversal:", end=" ")
        while queue:
            u = queue.popleft()
            print(u, end=" ")
            
            for neighbor, weight in self.adj[u]:  # FIXED: Unpack tuple
                if not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)
        
        print()
    
    def _dfs_helper(self, u, visited):
        """Helper function for DFS traversal"""
        visited[u] = True
        print(u, end=" ")
        
        for neighbor, weight in self.adj[u]:  # FIXED: Unpack tuple
            if not visited[neighbor]:
                self._dfs_helper(neighbor, visited)
    
    def dfs(self, start=0):
        """Depth-First Search traversal starting from vertex 'start'"""
        visited = [False] * self.V
        print("DFS Traversal:", end=" ")
        
        # Handle disconnected graph
        for i in range(self.V):
            if not visited[i]:
                self._dfs_helper(i, visited)
        
        print()
    
    def dfs_from_vertex(self, start):
        """DFS traversal starting from a specific vertex"""
        visited = [False] * self.V
        print(f"DFS from vertex {start}:", end=" ")
        self._dfs_helper(start, visited)
        print()
    
    def has_path(self, u, v):
        """Check if there's a path between vertices u and v using BFS"""
        if u == v:
            return True
        
        visited = [False] * self.V
        queue = deque([u])
        visited[u] = True
        
        while queue:
            current = queue.popleft()
            
            if current == v:
                return True
            
            for neighbor, weight in self.adj[current]:  
                if not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)
        
        return False
    
    def shortest_path_unweighted(self, start, end):
        """Find shortest path between start and end vertices using BFS (unweighted)"""
        if start == end:
            return [start]
        
        visited = [False] * self.V
        parent = [-1] * self.V
        queue = deque([start])
        visited[start] = True
        
        while queue:
            u = queue.popleft()
            
            for neighbor, weight in self.adj[u]:  
                if not visited[neighbor]:
                    visited[neighbor] = True
                    parent[neighbor] = u
                    queue.append(neighbor)
                    
                    if neighbor == end:
                        # Reconstruct path
                        path = []
                        current = end
                        while current != -1:
                            path.append(current)
                            current = parent[current]
                        return path[::-1]
        
        return None  # No path found
    
    def is_connected(self):
        """Check if the graph is connected"""
        if self.V == 0:
            return True
        
        visited = [False] * self.V
        self._dfs_helper(0, visited)
        
        return all(visited)
    
    def count_components(self):
        """Count the number of connected components"""
        visited = [False] * self.V
        count = 0
        
        for i in range(self.V):
            if not visited[i]:
                self._dfs_helper(i, visited)
                count += 1
        
        return count
    
    def get_all_nodes(self):
        """Get all node IDs in the graph"""
        return list(range(self.V))
    
    def get_neighbors(self, node):
        """Get all neighbors of a node with their weights"""
        return self.adj[node]