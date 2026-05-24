# DSA RIDES - Ride-Sharing Application

A full-stack ride-sharing web application built with Flask, demonstrating the practical implementation of various Data Structures and Algorithms (DSA) concepts.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Data Structures Used](#data-structures-used)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Usage](#usage)

---

## Overview

DSA RIDES is an educational ride-sharing platform that showcases how fundamental data structures and algorithms can be applied to solve real-world problems. The application allows users to request rides and drivers to accept and complete them, all while utilizing priority queues, stacks, heaps, graphs, and more.

---

## Features

### User Features
- **User Registration & Authentication**: Sign up and login system with role-based access (User/Driver)
- **Ride Request**: Request rides with pickup and destination locations
- **Urgent Ride Option**: Priority booking with 1.5x fare multiplier
- **Real-time Status**: Track ride status (searching, accepted, completed)
- **Ride History**: View past completed rides using stack-based history
- **Google Maps Integration**: Interactive map for location selection

### Driver Features
- **Driver Dashboard**: Dedicated interface for drivers
- **Location Tracking**: Real-time location updates
- **Ride Queue**: View available ride requests sorted by priority and proximity
- **Accept/Reject Rides**: Manage incoming ride requests
- **Ride Completion**: Mark rides as complete
- **Statistics Dashboard**: View earnings, completed rides, and ratings

---

## Tech Stack

| Category | Technology |
|----------|------------|
| **Backend** | Python 3.x, Flask |
| **Database** | SQLite with SQLAlchemy ORM |
| **Frontend** | HTML5, CSS3, JavaScript, Tailwind CSS |
| **Maps** | Google Maps JavaScript API |
| **Authentication** | Werkzeug Security (password hashing) |

---

## Project Structure

```
Rides/
├── .venv/
│   ├── app/
│   │   ├── Algorithms/
│   │   │   ├── dijkstra.py          # Dijkstra's algorithm (placeholder)
│   │   │   ├── driver_matcher.py    # Driver matching algorithm (placeholder)
│   │   │   └── __init__.py
│   │   ├── DataStructures/
│   │   │   ├── bst.py               # Binary Search Tree implementation
│   │   │   ├── graphs.py            # Weighted Graph with Dijkstra's algorithm
│   │   │   ├── linked_list.py       # Singly Linked List implementation
│   │   │   ├── min_heap.py          # Min Heap (placeholder)
│   │   │   ├── queue.py             # Priority Queue & Ride Request Queue
│   │   │   ├── stack.py             # Stack & Ride History Manager
│   │   │   ├── trie.py              # Trie (placeholder)
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── driver.py            # Driver model
│   │   │   ├── user.py              # User model with SQLAlchemy
│   │   │   └── __init__.py
│   │   ├── routes/
│   │   │   └── routes_calculator.py # Google Maps route calculation
│   │   ├── authenticate.py          # Authentication logic
│   │   └── __init__.py
│   ├── instance/
│   │   └── users.db                 # SQLite database
│   ├── static/
│   │   ├── banner.png
│   │   ├── img.png
│   │   ├── logo.png
│   │   └── path.svg
│   ├── templates/
│   │   ├── base.html                # Base template
│   │   ├── index.html               # Landing page
│   │   ├── login.html               # Login/Signup page
│   │   ├── rider_dashboard.html     # Driver dashboard
│   │   └── user_dashboard.html      # User dashboard
│   ├── requirements.txt             # Python dependencies
│   └── run.py                       # Main Flask application
└── instance/
    └── users.db
```

---

## Data Structures Used

### 1. Priority Queue (`app/DataStructures/queue.py`)

**Purpose**: Manage ride requests with priority handling for urgent rides.

```python
class PriorityRideQueue:
    """Priority Queue using two heaps - one for urgent, one for normal rides"""
    - enqueue(ride_request, is_urgent)  # Add ride to queue
    - dequeue()                          # Get highest priority ride
    - peek()                             # View next ride without removing
    - get_all_pending()                  # Get all pending rides
    - remove_by_id(request_id)           # Remove specific ride
```

**Key Features**:
- Urgent rides are always served first (FIFO within urgent queue)
- Uses Python's `heapq` for efficient O(log n) operations
- Supports rejection tracking per driver

### 2. Min Heap (`app/DataStructures/queue.py`)

**Purpose**: Find nearest rides to a driver based on geographical distance.

```python
class NearbyRidesMinHeap:
    """Min Heap for finding nearest rides using Haversine formula"""
    - calculate_distance(lat1, lng1, lat2, lng2)  # Distance in km
    - get_nearby_rides(rider_location, all_rides, max_rides)
```

**Key Features**:
- Uses Haversine formula for accurate Earth-surface distance calculation
- Returns rides sorted by proximity to driver

### 3. Stack (`app/DataStructures/stack.py`)

**Purpose**: Store user ride history with LIFO access pattern.

```python
class RideHistoryStack:
    """Dynamic stack for storing ride history"""
    - push(ride)      # Add completed ride
    - pop()           # Remove most recent ride
    - peek()          # View most recent ride
    - get_recent(n)   # Get last n rides

class UserRideHistoryManager:
    """Manages separate history stacks for each user"""
    - get_user_stack(user_email)
    - add_completed_ride(user_email, ride)
    - get_user_history(user_email, count)
```

### 4. Weighted Graph (`app/DataStructures/graphs.py`)

**Purpose**: Represent road networks for route optimization.

```python
class WeightedGraph:
    """Adjacency list graph with weighted edges"""
    - add_edge(u, v, weight)           # Add road segment
    - dijkstra(start, end)             # Find shortest path
    - bfs(start)                       # Breadth-first traversal
    - dfs(start)                       # Depth-first traversal
```

**Key Features**:
- Dijkstra's algorithm for shortest path finding
- Path reconstruction with parent tracking
- Used in route calculation for ride navigation

### 5. Binary Search Tree (`app/DataStructures/bst.py`)

**Purpose**: Efficient data organization and searching.

```python
class BST:
    - insert(key)       # Add node
    - remove(key)       # Delete node
    - search(key)       # Find node
    - inorder()         # Sorted traversal
    - preorder()        # Pre-order traversal
    - postorder()       # Post-order traversal
```

### 6. Linked List (`app/DataStructures/linked_list.py`)

**Purpose**: Dynamic data storage with efficient insertions/deletions.

```python
class List:
    - insert_at_head(x)     # O(1) insertion at front
    - insert_at_end(x)      # O(n) insertion at end
    - insert_node(index, x) # Insert at position
    - delete_node(x)        # Remove by value
    - find_node(x)          # Search for value
```

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Google Maps API key

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Rides
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   
   Windows:
   ```bash
   .venv\Scripts\activate
   ```
   
   Linux/Mac:
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r .venv/requirements.txt
   ```

5. **Run the application**
   ```bash
   cd .venv
   python run.py
   ```

6. **Access the application**
   
   Open browser and navigate to: `http://localhost:5000`

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session secret key | `'1234'` |
| `GOOGLE_MAPS_API_KEY` | Google Maps JavaScript API key | (hardcoded) |

### Database

The application uses SQLite with automatic database creation. The database file is stored at:
```
.venv/instance/users.db
```

---

## API Reference

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/login` | Login page |
| POST | `/login` | Process login |
| POST | `/signup` | Create new account |
| GET | `/logout` | Logout user |

### User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/user_dashboard/` | User dashboard |
| POST | `/api/user/request-ride` | Request a new ride |
| GET | `/api/user/ride-status` | Get current ride status |
| GET | `/api/user/ride-history` | Get ride history |
| POST | `/api/user/cancel-ride` | Cancel active ride |
| GET | `/api/queue/status` | Get queue statistics |

### Driver Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/rider_dashboard` | Driver dashboard |
| POST | `/api/rider/update-location` | Update driver location |
| GET | `/api/rider/requests` | Get nearby ride requests |
| POST | `/api/rider/accept-ride` | Accept a ride request |
| POST | `/api/rider/reject-ride` | Reject/hide a ride request |
| POST | `/api/rider/complete-ride` | Mark ride as complete |
| GET | `/api/rider/stats` | Get driver statistics |

### Request/Response Examples

#### Request a Ride
```http
POST /api/user/request-ride
Content-Type: application/json

{
  "origin": {
    "address": "123 Main St",
    "lat": 24.8607,
    "lng": 67.0011
  },
  "destination": {
    "address": "456 Oak Ave",
    "lat": 24.8700,
    "lng": 67.0100
  },
  "distance": "5.2 km",
  "duration": "15 mins",
  "rideType": "economy",
  "fare": 350,
  "paymentMethod": "cash",
  "isUrgent": false
}
```

#### Response
```json
{
  "success": true,
  "message": "Ride requested successfully",
  "request": {
    "id": "REQ-001",
    "status": "pending",
    "is_urgent": false
  },
  "queue_size": 5
}
```

---

## Usage

### As a User

1. **Sign Up**: Create an account by selecting "User" role
2. **Login**: Enter credentials and select "User" role
3. **Request Ride**: 
   - Enter pickup location
   - Enter destination
   - Choose ride type (Economy/Premium)
   - Click "See Prices" then "Request"
   - Optionally click "Urgent" for priority (1.5x fare)
4. **Track Status**: View real-time ride status
5. **View History**: Access past rides from dashboard

### As a Driver

1. **Sign Up**: Create an account by selecting "Driver" role
2. **Login**: Enter credentials and select "Driver" role
3. **Go Online**: Toggle status to start receiving requests
4. **View Requests**: See available rides sorted by proximity
5. **Accept Ride**: Click "Accept" on a ride request
6. **Complete Ride**: Mark ride as complete after drop-off

---

## Database Schema

### User Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| name | String(200) | User's full name |
| email | String(500) | Unique email address |
| password | String(500) | Hashed password |
| role | Integer | 1 = User, 2 = Driver |
| date_created | DateTime | Account creation timestamp |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

---

## License

This project is for educational purposes demonstrating DSA concepts in a real-world application.

---

## Acknowledgments

- Google Maps Platform for mapping services
- Flask framework for web development
- Tailwind CSS for styling
