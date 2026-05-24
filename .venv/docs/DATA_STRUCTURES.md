# Data Structures Documentation

This document provides detailed documentation for all data structure implementations in the DSA RIDES application.

---

## Table of Contents

1. [Priority Queue](#1-priority-queue)
2. [Min Heap for Nearby Rides](#2-min-heap-for-nearby-rides)
3. [Ride Request Queue](#3-ride-request-queue)
4. [Stack](#4-stack)
5. [Ride History Stack](#5-ride-history-stack)
6. [Binary Search Tree](#6-binary-search-tree)
7. [Weighted Graph](#7-weighted-graph)
8. [Linked List](#8-linked-list)

---

## 1. Priority Queue

**File**: `app/DataStructures/queue.py`

### Class: `PriorityRideQueue`

A priority queue implementation that handles urgent vs normal ride requests using two separate heaps.

#### Data Members

| Member | Type | Description |
|--------|------|-------------|
| `urgent_queue` | List | Heap for urgent/priority rides |
| `normal_queue` | List | Heap for standard rides |

#### Methods

##### `enqueue(ride_request: Dict, is_urgent: bool = False) -> Dict`

Adds a ride request to the appropriate queue based on urgency.

**Parameters:**
- `ride_request`: Dictionary containing ride details
- `is_urgent`: Boolean flag for priority rides (default: False)

**Returns:** The enqueued ride request with metadata

**Time Complexity:** O(log n)

**Example:**
```python
queue = PriorityRideQueue()
ride = {"id": "REQ-001", "pickup": "Location A", "dropoff": "Location B"}
queue.enqueue(ride, is_urgent=True)
```

##### `dequeue() -> Optional[Dict]`

Removes and returns the highest priority ride. Urgent rides are served first.

**Returns:** The next ride request or None if empty

**Time Complexity:** O(log n)

##### `peek() -> Optional[Dict]`

Views the next ride without removing it from the queue.

**Returns:** The next ride request or None if empty

**Time Complexity:** O(1)

##### `get_all_pending() -> List[Dict]`

Returns all pending rides with urgent rides first.

**Returns:** List of all pending ride requests

**Time Complexity:** O(n)

##### `remove_by_id(request_id: str) -> Optional[Dict]`

Removes a specific ride by its ID. Used when a ride is accepted.

**Parameters:**
- `request_id`: The unique identifier of the ride

**Returns:** The removed ride or None if not found

**Time Complexity:** O(n) - requires heap rebuild

##### `size() -> int`

Returns total number of rides in both queues.

**Time Complexity:** O(1)

---

## 2. Min Heap for Nearby Rides

**File**: `app/DataStructures/queue.py`

### Class: `NearbyRidesMinHeap`

A utility class for finding nearest rides to a driver using a min heap sorted by distance.

#### Static Methods

##### `calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float`

Calculates the distance between two geographical points using the Haversine formula.

**Parameters:**
- `lat1`, `lng1`: Coordinates of the first point
- `lat2`, `lng2`: Coordinates of the second point

**Returns:** Distance in kilometers

**Formula:**
```
a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlng/2)
c = 2 * atan2(√a, √(1-a))
d = R * c  (where R = 6371 km, Earth's radius)
```

##### `get_nearby_rides(rider_location: Dict, all_rides: List[Dict], max_rides: int = 3) -> List[Dict]`

Returns the nearest rides to a driver's location.

**Parameters:**
- `rider_location`: Dict with `lat` and `lng` keys
- `all_rides`: List of all available rides
- `max_rides`: Maximum number of rides to return (default: 3)

**Returns:** List of nearest rides sorted by distance

**Time Complexity:** O(n log k) where k = max_rides

---

## 3. Ride Request Queue

**File**: `app/DataStructures/queue.py`

### Class: `RideRequestQueue`

Enhanced queue combining priority handling with location-based matching and rejection tracking.

#### Data Members

| Member | Type | Description |
|--------|------|-------------|
| `priority_queue` | PriorityRideQueue | Underlying priority queue |
| `request_history` | List | Completed ride history |
| `rejected_rides` | Dict | Maps driver email to rejected ride IDs |

#### Methods

##### `enqueue(ride_request: Dict, is_urgent: bool = False) -> Dict`

Adds a ride request to the queue.

##### `get_nearby_rides_for_rider(rider_location: Dict, rider_email: str, max_rides: int = 20) -> List[Dict]`

Gets nearby rides for a specific driver, excluding rides they've rejected.

**Parameters:**
- `rider_location`: Driver's current location
- `rider_email`: Driver's email for rejection filtering
- `max_rides`: Maximum rides to return (default: 20)

**Returns:** Filtered list of nearby rides

##### `reject_ride(rider_email: str, request_id: str)`

Marks a ride as rejected by a specific driver (hides it from their list).

##### `get_statistics() -> Dict`

Returns queue statistics including:
- `total_pending`: Number of pending rides
- `urgent_count`: Number of urgent rides
- `normal_count`: Number of standard rides
- `completed_count`: Number of completed rides
- `total_rejected`: Total rejection count

---

## 4. Stack

**File**: `app/DataStructures/stack.py`

### Class: `Stack`

A fixed-size stack implementation using an array.

#### Data Members

| Member | Type | Description |
|--------|------|-------------|
| `size` | int | Maximum capacity |
| `data` | List | Array storing elements |
| `top` | int | Index of top element (-1 if empty) |

#### Methods

##### `push(x)`

Pushes an element onto the stack.

**Time Complexity:** O(1)

##### `pop() -> Any`

Removes and returns the top element.

**Time Complexity:** O(1)

##### `peek() -> Any`

Returns the top element without removing it.

**Time Complexity:** O(1)

##### `is_full() -> bool`

Checks if stack is at capacity.

##### `is_empty() -> bool`

Checks if stack is empty.

##### `display_list()`

Prints all elements from top to bottom.

---

## 5. Ride History Stack

**File**: `app/DataStructures/stack.py`

### Class: `RideHistoryStack`

A dynamic stack specifically for storing ride history.

#### Methods

##### `push(ride: Dict) -> None`

Adds a completed ride to history.

##### `pop() -> Optional[Dict]`

Removes and returns the most recent ride.

##### `peek() -> Optional[Dict]`

Views the most recent ride.

##### `get_all() -> List[Dict]`

Returns all rides (most recent first).

##### `get_recent(count: int = 5) -> List[Dict]`

Returns the last `count` rides.

### Class: `UserRideHistoryManager`

Manages separate history stacks for multiple users.

#### Methods

##### `get_user_stack(user_email: str) -> RideHistoryStack`

Gets or creates a history stack for a user.

##### `add_completed_ride(user_email: str, ride: Dict) -> None`

Adds a completed ride to the user's history.

##### `get_user_history(user_email: str, count: int = None) -> List[Dict]`

Retrieves user's ride history, optionally limited to `count` rides.

##### `get_last_ride(user_email: str) -> Optional[Dict]`

Gets the user's most recent ride.

---

## 6. Binary Search Tree

**File**: `app/DataStructures/bst.py`

### Class: `BST`

A standard binary search tree implementation.

#### Node Structure

```python
class Node:
    key: Any      # Node value
    left: Node    # Left child
    right: Node   # Right child
```

#### Methods

##### `insert(key)`

Inserts a key into the BST. Duplicates are ignored.

**Time Complexity:** O(h) where h is tree height

##### `remove(key)`

Deletes a key from the BST using in-order successor for nodes with two children.

**Time Complexity:** O(h)

##### `search(key) -> bool`

Searches for a key in the BST.

**Time Complexity:** O(h)

##### Traversal Methods

| Method | Order | Use Case |
|--------|-------|----------|
| `inorder()` | Left → Root → Right | Sorted output |
| `preorder()` | Root → Left → Right | Tree copying |
| `postorder()` | Left → Right → Root | Tree deletion |

---

## 7. Weighted Graph

**File**: `app/DataStructures/graphs.py`

### Class: `WeightedGraph`

An adjacency list representation of a weighted undirected graph with Dijkstra's algorithm.

#### Constructor

```python
def __init__(self, V: int):
    """
    V: Number of vertices in the graph
    """
```

#### Methods

##### `add_edge(u: int, v: int, weight: int)`

Adds an undirected weighted edge between vertices u and v.

**Time Complexity:** O(1)

##### `dijkstra(start: int, end: int) -> Tuple[List[int], float]`

Finds the shortest path between two vertices using Dijkstra's algorithm.

**Parameters:**
- `start`: Source vertex
- `end`: Destination vertex

**Returns:** Tuple of (path as list of vertices, total distance)

**Time Complexity:** O((V + E) log V) with binary heap

**Algorithm Steps:**
1. Initialize all distances to infinity
2. Set source distance to 0
3. Use priority queue to process vertices in order of distance
4. For each vertex, relax all neighboring edges
5. Reconstruct path using parent pointers

##### `bfs(start: int = 0)`

Breadth-first search traversal.

**Time Complexity:** O(V + E)

##### `dfs(start: int = 0)`

Depth-first search traversal.

**Time Complexity:** O(V + E)

##### `print_graph()`

Prints the adjacency list representation.

---

## 8. Linked List

**File**: `app/DataStructures/linked_list.py`

### Class: `List`

A singly linked list implementation.

#### Node Structure

```python
class Node:
    data: Any    # Node value
    next: Node   # Pointer to next node
```

#### Methods

##### `insert_at_head(x) -> Node`

Inserts element at the beginning.

**Time Complexity:** O(1)

##### `insert_at_end(x) -> Node`

Inserts element at the end.

**Time Complexity:** O(n)

##### `insert_node(index: int, x) -> Node`

Inserts element at a specific position.

**Time Complexity:** O(n)

##### `find_node(x) -> bool`

Searches for an element.

**Time Complexity:** O(n)

##### `delete_node(x) -> bool`

Deletes first occurrence of an element.

**Time Complexity:** O(n)

##### `is_empty() -> bool`

Checks if list is empty.

##### `display_list()`

Prints all elements in the list.

---

## Usage in Application

### How Data Structures are Used

| Data Structure | Application Use |
|----------------|-----------------|
| Priority Queue | Managing ride requests with urgent rides first |
| Min Heap | Finding nearest rides to drivers |
| Stack | Storing user ride history (LIFO access) |
| Weighted Graph | Route optimization with Dijkstra's algorithm |
| BST | (Available for future features like fare lookup) |
| Linked List | (Available for future features) |

### Example Flow

1. **User requests ride** → Added to `PriorityRideQueue`
2. **Driver goes online** → `NearbyRidesMinHeap` finds closest rides
3. **Driver accepts ride** → Removed from queue, added to active rides
4. **Ride completed** → Added to user's `RideHistoryStack`
5. **Route calculation** → `WeightedGraph.dijkstra()` finds optimal path
