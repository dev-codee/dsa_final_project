import heapq
from datetime import datetime
from typing import List, Dict, Optional
import math

class PriorityRideQueue:
    """Priority Queue for handling urgent vs normal rides"""
    
    def __init__(self):
        self.urgent_queue = []  # High priority
        self.normal_queue = []  # Normal priority
        
    def enqueue(self, ride_request: Dict, is_urgent: bool = False):
        """Add ride to appropriate queue"""
        ride_request['is_urgent'] = is_urgent
        ride_request['enqueued_at'] = datetime.now().isoformat()
        
        if is_urgent:
            # Urgent rides: priority by time (FIFO within urgent)
            heapq.heappush(self.urgent_queue, (
                ride_request['created_at'],
                ride_request
            ))
        else:
            # Normal rides: priority by time (FIFO)
            heapq.heappush(self.normal_queue, (
                ride_request['created_at'],
                ride_request
            ))
        
        return ride_request
    
    def dequeue(self) -> Optional[Dict]:
        """Remove and return highest priority ride"""
        # Always serve urgent rides first
        if self.urgent_queue:
            _, ride = heapq.heappop(self.urgent_queue)
            return ride
        elif self.normal_queue:
            _, ride = heapq.heappop(self.normal_queue)
            return ride
        return None
    
    def peek(self) -> Optional[Dict]:
        """View next ride without removing"""
        if self.urgent_queue:
            return self.urgent_queue[0][1]
        elif self.normal_queue:
            return self.normal_queue[0][1]
        return None
    
    def get_all_pending(self) -> List[Dict]:
        """Get all pending rides (urgent first)"""
        urgent_rides = [ride for _, ride in self.urgent_queue]
        normal_rides = [ride for _, ride in self.normal_queue]
        return urgent_rides + normal_rides
    
    def remove_by_id(self, request_id: str) -> Optional[Dict]:
        """Remove specific ride by ID"""
        # Check urgent queue - rebuild heap without the matching item
        found_ride = None
        new_urgent_queue = []
        for priority, ride in self.urgent_queue:
            if ride['id'] == request_id:
                found_ride = ride
            else:
                new_urgent_queue.append((priority, ride))
        
        if found_ride:
            self.urgent_queue = new_urgent_queue
            heapq.heapify(self.urgent_queue)
            return found_ride
        
        # Check normal queue - rebuild heap without the matching item
        new_normal_queue = []
        for priority, ride in self.normal_queue:
            if ride['id'] == request_id:
                found_ride = ride
            else:
                new_normal_queue.append((priority, ride))
        
        if found_ride:
            self.normal_queue = new_normal_queue
            heapq.heapify(self.normal_queue)
            return found_ride
        
        return None
    
    def size(self) -> int:
        """Total rides in queue"""
        return len(self.urgent_queue) + len(self.normal_queue)


class NearbyRidesMinHeap:
    """Min Heap for finding nearest rides to rider"""
    
    @staticmethod
    def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance in km using Haversine formula"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    def get_nearby_rides(rider_location: Dict, all_rides: List[Dict], max_rides: int = 3) -> List[Dict]:
        """Get nearest rides using min heap"""
        if not rider_location or not all_rides:
            return []
        
        rider_lat = rider_location['lat']
        rider_lng = rider_location['lng']
        
        # Create min heap with (distance, ride) tuples
        heap = []
        
        for ride in all_rides:
            if 'pickupCoords' in ride:
                pickup_lat = ride['pickupCoords']['lat']
                pickup_lng = ride['pickupCoords']['lng']
                
                distance = NearbyRidesMinHeap.calculate_distance(
                    rider_lat, rider_lng, pickup_lat, pickup_lng
                )
                
                # Add distance info to ride
                ride['distance_to_pickup'] = round(distance, 2)
                ride['distance_to_pickup_text'] = f"{round(distance, 1)} km away"
                
                heapq.heappush(heap, (distance, ride))
        
        # Extract nearest rides (max_rides count)
        nearest_rides = []
        for _ in range(min(max_rides, len(heap))):
            if heap:
                distance, ride = heapq.heappop(heap)
                nearest_rides.append(ride)
        
        return nearest_rides


class RideRequestQueue:
    """Enhanced queue with priority and location-based matching"""
    
    def __init__(self):
        self.priority_queue = PriorityRideQueue()
        self.request_history = []
        self.rejected_rides = {}  # rider_email -> [rejected_request_ids]
    
    def enqueue(self, ride_request: Dict, is_urgent: bool = False):
        """Add ride request to queue"""
        if is_urgent:
            ride_request['is_urgent'] = True
        
        return self.priority_queue.enqueue(ride_request, is_urgent)
    
    def get_nearby_rides_for_rider(self, rider_location: Dict, rider_email: str, max_rides: int = 20) -> List[Dict]:
        """Get nearby rides for specific rider, excluding rejected ones"""
        all_pending = self.priority_queue.get_all_pending()
        
        # Filter out rides this rider has rejected
        rejected_ids = self.rejected_rides.get(rider_email, [])
        available_rides = [r for r in all_pending if r['id'] not in rejected_ids]
        if len(available_rides) <= max_rides:
            # Show all available rides, but still calculate distances for sorting
            nearby = NearbyRidesMinHeap.get_nearby_rides(
                rider_location, 
                available_rides, 
                len(available_rides)  # Return all, not just max_rides
            )
        else:
            # Get nearest rides (limited to max_rides)
            nearby = NearbyRidesMinHeap.get_nearby_rides(
                rider_location, 
                available_rides, 
                max_rides
            )
        
        return nearby
    
    def reject_ride(self, rider_email: str, request_id: str):
        """Mark ride as rejected by this rider (hide it for them)"""
        if rider_email not in self.rejected_rides:
            self.rejected_rides[rider_email] = []
        
        if request_id not in self.rejected_rides[rider_email]:
            self.rejected_rides[rider_email].append(request_id)
    
    def remove_by_id(self, request_id: str) -> Optional[Dict]:
        """Remove ride from queue (when accepted)"""
        ride = self.priority_queue.remove_by_id(request_id)
        
        # Clear this ride from all rejection lists
        if ride:
            for rider_email in self.rejected_rides:
                if request_id in self.rejected_rides[rider_email]:
                    self.rejected_rides[rider_email].remove(request_id)
        
        return ride
    
    def dequeue(self) -> Optional[Dict]:
        """Get next ride from queue"""
        return self.priority_queue.dequeue()
    
    def peek(self) -> Optional[Dict]:
        """View next ride"""
        return self.priority_queue.peek()
    
    def get_all_pending(self) -> List[Dict]:
        """Get all pending rides"""
        return self.priority_queue.get_all_pending()
    
    def size(self) -> int:
        """Queue size"""
        return self.priority_queue.size()
    
    def get_statistics(self) -> Dict:
        """Get queue statistics"""
        all_pending = self.get_all_pending()
        urgent_count = sum(1 for r in all_pending if r.get('is_urgent', False))
        
        return {
            "total_pending": len(all_pending),
            "urgent_count": urgent_count,
            "normal_count": len(all_pending) - urgent_count,
            "completed_count": len(self.request_history),
            "total_rejected": sum(len(v) for v in self.rejected_rides.values())
        }