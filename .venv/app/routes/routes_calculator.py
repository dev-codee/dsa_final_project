import googlemaps
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from ..DataStructures.graphs import WeightedGraph # Import your WeightedGraph class

@dataclass
class Location:
    lat: float
    lng: float
    name: str = ""

class DijkstraRouteFinder:
    def __init__(self, api_key: str):
        self.gmaps = googlemaps.Client(key=api_key)
        self.graph = None
        self.location_to_id = {}
        self.id_to_location = {}
        
    def _build_graph_from_routes(self, routes_info: List[Dict]):
        """Build a graph structure from extracted routes using WeightedGraph class"""
        # First, collect all unique locations and create a mapping
        location_to_id = {}
        id_to_location = {}
        node_id = 0
        
        # Extract all unique locations
        for route in routes_info:
            for leg in route.get("legs", []):
                for step in leg.get("steps", []):
                    start = (
                        round(step["start_location"]["lat"], 6),
                        round(step["start_location"]["lng"], 6)
                    )
                    end = (
                        round(step["end_location"]["lat"], 6),
                        round(step["end_location"]["lng"], 6)
                    )
                    
                    if start not in location_to_id:
                        location_to_id[start] = node_id
                        id_to_location[node_id] = start
                        node_id += 1
                    
                    if end not in location_to_id:
                        location_to_id[end] = node_id
                        id_to_location[node_id] = end
                        node_id += 1
        
        # Create WeightedGraph with the number of unique nodes
        self.graph = WeightedGraph(node_id)
        self.location_to_id = location_to_id
        self.id_to_location = id_to_location
        
        # Add edges to the graph
        for route in routes_info:
            for leg in route.get("legs", []):
                for step in leg.get("steps", []):
                    start = (
                        round(step["start_location"]["lat"], 6),
                        round(step["start_location"]["lng"], 6)
                    )
                    end = (
                        round(step["end_location"]["lat"], 6),
                        round(step["end_location"]["lng"], 6)
                    )
                    # Distance in meters
                    distance = step["distance"]["value"]
                    
                    # Get node IDs
                    start_id = location_to_id[start]
                    end_id = location_to_id[end]
                    
                    # Add edge using WeightedGraph's add_edge method
                    self.graph.add_edge(start_id, end_id, distance)
    
    def _find_closest_node(self, location: Tuple[float, float]) -> Optional[int]:
        """Find the closest node in the graph to the given location"""
        if not self.location_to_id:
            return None
        
        min_distance = float('inf')
        closest_node = None
        
        for graph_location, node_id in self.location_to_id.items():
            # Simple Euclidean distance (for small distances this is acceptable)
            dist = ((location[0] - graph_location[0])**2 + 
                   (location[1] - graph_location[1])**2)**0.5
            
            if dist < min_distance:
                min_distance = dist
                closest_node = node_id
        
        return closest_node
    
    def get_route_with_waypoints(self, origin: Location, destination: Location, 
                                 waypoints: List[Location] = None) -> Dict:
        """
        Get route using Google Directions API and then apply Dijkstra's algorithm
        """
        try:
            # Build the request for Google Directions API
            waypoint_locs = None
            if waypoints:
                waypoint_locs = [f"{wp.lat},{wp.lng}" for wp in waypoints]
            
            # Get directions from Google Maps
            directions = self.gmaps.directions(
                origin=f"{origin.lat},{origin.lng}",
                destination=f"{destination.lat},{destination.lng}",
                waypoints=waypoint_locs,
                mode="driving",
                alternatives=True  # Get alternative routes
            )
            
            if not directions:
                raise Exception("No routes found")
            
            # Extract route information
            routes_info = self._extract_route_info(directions)
            
            # Build graph from routes
            self._build_graph_from_routes(routes_info)
            
            # Find closest nodes to origin and destination in our graph
            origin_coords = (round(origin.lat, 6), round(origin.lng, 6))
            dest_coords = (round(destination.lat, 6), round(destination.lng, 6))
            
            start_node = self._find_closest_node(origin_coords)
            end_node = self._find_closest_node(dest_coords)
            
            if start_node is None or end_node is None:
                raise Exception("Could not find nodes in graph")
            
            # Apply Dijkstra's algorithm
            path_nodes, total_distance = self.graph.dijkstra(start_node, end_node)
            
            if path_nodes is None:
                raise Exception("No path found using Dijkstra")
            
            # Convert path back to coordinates
            path_coordinates = [self.id_to_location[node] for node in path_nodes]
            
            return {
                "algorithm_used": "Dijkstra",
                "total_distance_meters": total_distance,
                "total_distance_km": round(total_distance / 1000, 2),
                "path_nodes": path_nodes,
                "path_coordinates": path_coordinates,
                "google_routes": routes_info,
                "graph_stats": {
                    "total_nodes": self.graph.V,
                    "start_node": start_node,
                    "end_node": end_node
                }
            }
            
        except Exception as e:
            raise Exception(f"Route calculation failed: {str(e)}")
    
    def _extract_route_info(self, directions: List[Dict]) -> List[Dict]:
        """Extract relevant information from Google Directions API response"""
        routes_info = []
        
        for route in directions:
            route_data = {
                "summary": route.get("summary", ""),
                "legs": [],
                "total_distance": 0,
                "total_duration": 0
            }
            
            for leg in route.get("legs", []):
                leg_data = {
                    "distance": leg["distance"]["value"],
                    "duration": leg["duration"]["value"],
                    "start_address": leg.get("start_address", ""),
                    "end_address": leg.get("end_address", ""),
                    "steps": []
                }
                
                route_data["total_distance"] += leg["distance"]["value"]
                route_data["total_duration"] += leg["duration"]["value"]
                
                for step in leg.get("steps", []):
                    step_data = {
                        "distance": step["distance"],
                        "duration": step["duration"],
                        "start_location": {
                            "lat": step["start_location"]["lat"],
                            "lng": step["start_location"]["lng"]
                        },
                        "end_location": {
                            "lat": step["end_location"]["lat"],
                            "lng": step["end_location"]["lng"]
                        },
                        "instructions": step.get("html_instructions", "")
                    }
                    leg_data["steps"].append(step_data)
                
                route_data["legs"].append(leg_data)
            
            routes_info.append(route_data)
        
        return routes_info
    
    def calculate_simple_distance(self, origin: Location, destination: Location) -> Dict:
        """
        Calculate simple distance using Google Distance Matrix API
        """
        try:
            result = self.gmaps.distance_matrix(
                origins=[(origin.lat, origin.lng)],
                destinations=[(destination.lat, destination.lng)],
                mode="driving"
            )
            
            if result["rows"][0]["elements"][0]["status"] == "OK":
                element = result["rows"][0]["elements"][0]
                return {
                    "distance_meters": element["distance"]["value"],
                    "distance_text": element["distance"]["text"],
                    "duration_seconds": element["duration"]["value"],
                    "duration_text": element["duration"]["text"],
                    "origin": {"lat": origin.lat, "lng": origin.lng},
                    "destination": {"lat": destination.lat, "lng": destination.lng}
                }
            else:
                raise Exception("Could not calculate distance")
                
        except Exception as e:
            raise Exception(f"Distance calculation failed: {str(e)}")
    
    def compare_routes(self, routes: List[Tuple[Location, Location]]) -> Dict:
        """
        Compare multiple routes and find the shortest
        """
        results = []
        
        for origin, destination in routes:
            try:
                distance_info = self.calculate_simple_distance(origin, destination)
                results.append({
                    "origin": {"lat": origin.lat, "lng": origin.lng, "name": origin.name},
                    "destination": {"lat": destination.lat, "lng": destination.lng, "name": destination.name},
                    "distance": distance_info["distance_meters"],
                    "distance_text": distance_info["distance_text"],
                    "duration_text": distance_info["duration_text"]
                })
            except Exception as e:
                results.append({
                    "origin": {"lat": origin.lat, "lng": origin.lng, "name": origin.name},
                    "destination": {"lat": destination.lat, "lng": destination.lng, "name": destination.name},
                    "error": str(e)
                })
        
        # Find shortest route
        valid_results = [r for r in results if "error" not in r]
        if valid_results:
            shortest = min(valid_results, key=lambda x: x["distance"])
            return {
                "all_routes": results,
                "shortest_route": shortest,
                "total_routes": len(results)
            }
        else:
            raise Exception("No valid routes found")