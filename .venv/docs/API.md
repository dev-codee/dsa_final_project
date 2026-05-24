# API Documentation

Complete API reference for DSA RIDES application.

---

## Base URL

```
http://localhost:5000
```

---

## Authentication

The application uses Flask session-based authentication. After successful login, the following session variables are set:

| Variable | Description |
|----------|-------------|
| `user_email` | User's email address |
| `user_name` | User's display name |
| `user_role` | Either "user" or "driver" |

---

## Endpoints

### Authentication

#### GET `/`

**Description:** Home/Landing page

**Response:** HTML page with signup/login options

---

#### GET `/login`

**Description:** Display login page

**Response:** HTML login form

---

#### POST `/login`

**Description:** Authenticate user

**Request Body (form data):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `login-email` | string | Yes | User's email |
| `login-password` | string | Yes | User's password |
| `role` | string | Yes | "user" or "driver" |

**Response:** 
- Success: Redirect to appropriate dashboard
- Failure: Flash message and return to login page

---

#### POST `/signup`

**Description:** Create new user account

**Request Body (form data):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `signup-email` | string | Yes | User's email |
| `signup-password` | string | Yes | User's password |
| `signup-name` | string | Yes | User's full name |
| `role` | string | Yes | "user" or "driver" |

**Response:**
- Success: Redirect to login with success message
- Failure: Redirect to home with error message

---

#### GET `/logout`

**Description:** Log out current user

**Response:** Redirect to home page

---

### User Dashboard

#### GET `/user_dashboard/`

**Description:** Display user dashboard (requires authentication)

**Response:** 
- Success: HTML dashboard page
- Unauthorized: Redirect to login

---

### User API Endpoints

#### POST `/api/user/request-ride`

**Description:** Request a new ride

**Authentication:** Required (session)

**Request Body (JSON):**

```json
{
  "origin": {
    "address": "string",
    "lat": "number",
    "lng": "number"
  },
  "destination": {
    "address": "string",
    "lat": "number",
    "lng": "number"
  },
  "distance": "string",
  "duration": "string",
  "rideType": "string",
  "fare": "number",
  "paymentMethod": "string",
  "isUrgent": "boolean"
}
```

**Response:**

Success (200):
```json
{
  "success": true,
  "message": "Ride requested successfully",
  "request": {
    "id": "REQ-001",
    "user_email": "user@example.com",
    "userName": "John Doe",
    "userRating": 4.8,
    "pickup": "123 Main St",
    "dropoff": "456 Oak Ave",
    "pickupCoords": {"lat": 24.86, "lng": 67.00},
    "dropoffCoords": {"lat": 24.87, "lng": 67.01},
    "distance": "5.2 km",
    "duration": "15 mins",
    "rideType": "economy",
    "fare": 350,
    "paymentMethod": "cash",
    "status": "pending",
    "is_urgent": false,
    "created_at": "2025-12-30T10:30:00"
  },
  "queue_size": 5,
  "is_urgent": false
}
```

Error (400):
```json
{
  "error": "Origin and destination are required"
}
```

---

#### GET `/api/user/ride-status`

**Description:** Get current ride status for logged-in user

**Authentication:** Required (session)

**Response:**

No active ride:
```json
{
  "success": true,
  "has_active_ride": false,
  "status": "none",
  "message": "No active ride request"
}
```

Searching for driver:
```json
{
  "success": true,
  "has_active_ride": true,
  "status": "searching",
  "message": "Finding a driver for you...",
  "ride": { /* ride object */ }
}
```

Driver found:
```json
{
  "success": true,
  "has_active_ride": true,
  "status": "accepted",
  "message": "Driver found!",
  "ride": { /* ride object */ },
  "rider": {
    "name": "Driver Name",
    "email": "driver@example.com",
    "rating": 4.8,
    "vehicle": "Toyota Corolla",
    "plate_number": "ABC-1234"
  }
}
```

Ride completed:
```json
{
  "success": true,
  "has_active_ride": false,
  "status": "completed",
  "message": "Ride completed",
  "ride": { /* completed ride object */ }
}
```

---

#### GET `/api/user/ride-history`

**Description:** Get user's ride history

**Authentication:** Required (session)

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `count` | integer | No | Limit number of results |

**Response:**

```json
{
  "success": true,
  "history": [
    {
      "id": "REQ-001",
      "pickup": "Location A",
      "dropoff": "Location B",
      "fare": 350,
      "status": "completed",
      "completed_at": "2025-12-29T15:30:00",
      "rider_name": "Driver Name",
      "rider_rating": 4.8
    }
  ],
  "total_rides": 15
}
```

---

#### POST `/api/user/cancel-ride`

**Description:** Cancel active ride request

**Authentication:** Required (session)

**Response:**

Success (200):
```json
{
  "success": true,
  "message": "Ride cancelled successfully"
}
```

Error (404):
```json
{
  "error": "No active ride to cancel"
}
```

---

### Driver Dashboard

#### GET `/rider_dashboard`

**Description:** Display driver dashboard (requires driver role)

**Response:**
- Success: HTML dashboard page
- Unauthorized: Redirect to login
- Wrong role: Redirect to user dashboard

---

### Driver API Endpoints

#### POST `/api/rider/update-location`

**Description:** Update driver's current location

**Authentication:** Required (session, driver role)

**Request Body (JSON):**

```json
{
  "lat": "number",
  "lng": "number"
}
```

**Response:**

Success (200):
```json
{
  "success": true,
  "message": "Location updated"
}
```

Error (401):
```json
{
  "error": "Not authenticated"
}
```

---

#### GET `/api/rider/requests`

**Description:** Get nearby ride requests for driver

**Authentication:** Required (session, driver role)

**Response:**

```json
{
  "success": true,
  "requests": [
    {
      "id": "REQ-001",
      "userName": "John Doe",
      "userRating": 4.8,
      "pickup": "123 Main St",
      "dropoff": "456 Oak Ave",
      "pickupCoords": {"lat": 24.86, "lng": 67.00},
      "dropoffCoords": {"lat": 24.87, "lng": 67.01},
      "distance": "5.2 km",
      "fare": 350,
      "is_urgent": false,
      "distance_to_pickup": 1.5,
      "distance_to_pickup_text": "1.5 km away"
    }
  ],
  "queue_size": 10,
  "has_location": true
}
```

---

#### POST `/api/rider/accept-ride`

**Description:** Accept a ride request

**Authentication:** Required (session, driver role)

**Request Body (JSON):**

```json
{
  "requestId": "REQ-001"
}
```

**Response:**

Success (200):
```json
{
  "success": true,
  "message": "Ride accepted successfully",
  "ride": { /* ride object with status: "accepted" */ },
  "remaining_in_queue": 9
}
```

Error (400):
```json
{
  "error": "You already have an active ride. Please complete it first."
}
```

Error (404):
```json
{
  "error": "Request not found in queue"
}
```

---

#### POST `/api/rider/reject-ride`

**Description:** Reject/hide a ride from driver's list

**Authentication:** Required (session, driver role)

**Request Body (JSON):**

```json
{
  "requestId": "REQ-001"
}
```

**Response:**

Success (200):
```json
{
  "success": true,
  "message": "Ride hidden from your list"
}
```

---

#### POST `/api/rider/complete-ride`

**Description:** Mark active ride as complete

**Authentication:** Required (session, driver role)

**Request Body (JSON):**

```json
{
  "requestId": "REQ-001"
}
```

**Response:**

Success (200):
```json
{
  "success": true,
  "message": "Ride completed successfully"
}
```

Error (404):
```json
{
  "error": "No active ride found"
}
```

---

#### GET `/api/rider/stats`

**Description:** Get driver statistics

**Authentication:** Required (session, driver role)

**Response:**

```json
{
  "success": true,
  "stats": {
    "completed_rides": 25,
    "today_earnings": 8750,
    "hours_online": 0,
    "rating": 4.8,
    "pending_requests": 10,
    "urgent_requests": 2
  }
}
```

---

### Queue Status

#### GET `/api/queue/status`

**Description:** Get current queue status and statistics

**Response:**

```json
{
  "success": true,
  "queue_size": 10,
  "statistics": {
    "total_pending": 10,
    "urgent_count": 2,
    "normal_count": 8,
    "completed_count": 50,
    "total_rejected": 15
  },
  "next_request": { /* next ride in queue */ }
}
```

---

## Error Handling

All API endpoints return errors in the following format:

```json
{
  "error": "Error message description"
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 401 | Unauthorized (not logged in) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Data Models

### Ride Request Object

```json
{
  "id": "string",
  "user_email": "string",
  "userName": "string",
  "userRating": "number",
  "pickup": "string",
  "dropoff": "string",
  "pickupCoords": {
    "lat": "number",
    "lng": "number"
  },
  "dropoffCoords": {
    "lat": "number",
    "lng": "number"
  },
  "distance": "string",
  "duration": "string",
  "rideType": "string",
  "fare": "number",
  "paymentMethod": "string",
  "status": "string",
  "is_urgent": "boolean",
  "created_at": "ISO 8601 string",
  "enqueued_at": "ISO 8601 string"
}
```

### Ride Status Values

| Status | Description |
|--------|-------------|
| `pending` | Waiting in queue for driver |
| `accepted` | Driver has accepted the ride |
| `completed` | Ride has been completed |
| `cancelled` | Ride was cancelled |

### Ride Types

| Type | Description |
|------|-------------|
| `economy` | Standard ride |
| `premium` | Premium/luxury ride |
