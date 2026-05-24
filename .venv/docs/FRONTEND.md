# Frontend Documentation

Documentation for the frontend templates and user interface of DSA RIDES application.

---

## Overview

The frontend consists of HTML templates with embedded CSS and JavaScript, using the Flask Jinja2 templating engine. Tailwind CSS is used for the login page styling.

---

## Templates

### Directory Structure

```
templates/
├── base.html              # Base template (empty/placeholder)
├── index.html             # Landing/Home page
├── login.html             # Login & Signup page
├── user_dashboard.html    # User (passenger) dashboard
└── rider_dashboard.html   # Driver dashboard
```

---

## 1. Landing Page (`index.html`)

### Description

The home page introducing DSA RIDES with navigation to login/signup.

### Features

- Hero section with app branding
- "Get a ride" and "Apply to drive" buttons
- Login and Sign Up navigation buttons
- Responsive design

### Key Elements

| Element | Class/ID | Description |
|---------|----------|-------------|
| Logo | `.logo` | App logo in navigation |
| Sign Up Button | `.SignUp` | Navigate to signup |
| Login Button | `.logIn` | Navigate to login |
| CTA Buttons | `.btn` | Main action buttons |

### Styling

- Custom CSS with flexbox layout
- System fonts (UberMove, Helvetica, Arial)
- Light gray background (`#f3f3f3`)
- Black and white color scheme

---

## 2. Login Page (`login.html`)

### Description

Combined login and signup page with form switching animation.

### Features

- Login form
- Signup form
- Forgot password form
- Role selection (User/Driver)
- Smooth form transitions
- Responsive design

### Form Views

| View ID | Description |
|---------|-------------|
| `login-view` | Login form |
| `signup-view` | Registration form |
| `forgot-view` | Password reset form |

### JavaScript Functions

#### `switchView(view)`

Switches between login, signup, and forgot password forms.

```javascript
function switchView(view) {
    // Hide current form
    // Show target form
    // Update title
}
```

### Form Fields

#### Login Form

| Field | Name | Type |
|-------|------|------|
| Email | `login-email` | email |
| Password | `login-password` | password |
| Role | `role` | select |

#### Signup Form

| Field | Name | Type |
|-------|------|------|
| Email | `signup-email` | email |
| Password | `signup-password` | password |
| Name | `signup-name` | text |
| Role | `role` | select |

### Styling

- Tailwind CSS
- Dark theme (gray-950 background)
- Custom color palette:
  - `uber-black`: #1E1E1E
  - `uber-gray`: #303030
  - `uber-accent`: #00B3A6
  - `uber-text`: #EAEAEA

---

## 3. User Dashboard (`user_dashboard.html`)

### Description

Main interface for passengers to request rides and view status.

### Features

- Google Maps integration
- Pickup/Destination input with autocomplete
- Ride type selection
- Fare display
- Ride request buttons (Normal & Urgent)
- Real-time ride status
- Ride history display

### Layout

```
┌─────────────────────────────────────────────────────┐
│  Navigation Bar                           [Logout]  │
├────────────────────────┬────────────────────────────┤
│  Left Panel            │  Right Panel              │
│  - Location Inputs     │  - Google Map             │
│  - Ride Options        │                           │
│  - Price Display       │                           │
│  - Request Buttons     │                           │
│  - Status Display      │                           │
│  - Ride History        │                           │
└────────────────────────┴────────────────────────────┘
```

### Key Elements

| Element | ID/Class | Description |
|---------|----------|-------------|
| Pickup Input | `#pickup` | Origin location input |
| Destination Input | `#destination` | Destination input |
| Map Container | `#map` | Google Maps display |
| Request Button | `#requestBtn` | Normal ride request |
| Urgent Button | `#urgentBtn` | Urgent ride request |
| Ride Status | `#rideStatus` | Current ride status |
| History Container | `#rideHistory` | Past rides list |

### JavaScript Functions

#### Map Functions

```javascript
// Initialize Google Map
function initMap()

// Setup autocomplete for inputs
function setupAutocomplete()

// Calculate and display route
function calculateRoute()

// Get directions between points
function getDirections(origin, destination)
```

#### Ride Functions

```javascript
// Request a ride
function requestRide(isUrgent = false)

// Check current ride status
function checkRideStatus()

// Load ride history
function loadRideHistory()

// Cancel active ride
function cancelRide()
```

### Google Maps Integration

```html
<script async defer 
    src="https://maps.googleapis.com/maps/api/js?key={{api_key}}&libraries=places&callback=initMap">
</script>
```

### Status Indicators

| Status | Display |
|--------|---------|
| `searching` | "Finding a driver..." with loading animation |
| `accepted` | Driver details card |
| `completed` | Completion message |
| `cancelled` | Cancellation message |

---

## 4. Driver Dashboard (`rider_dashboard.html`)

### Description

Interface for drivers to view and manage ride requests.

### Features

- Online/Offline status toggle
- Location tracking
- Available ride requests
- Statistics display (earnings, completed rides)
- Accept/Reject ride controls
- Active ride management

### Layout

```
┌─────────────────────────────────────────────────────┐
│  Navigation Bar        [Status Toggle]    [Logout]  │
├────────────────────────┬────────────────────────────┤
│  Statistics Section    │  Available Requests       │
│  - Completed Rides     │  - Request Cards          │
│  - Today's Earnings    │    - User Info            │
│  - Rating              │    - Pickup/Dropoff       │
│  - Hours Online        │    - Distance/Fare        │
│                        │    - Accept/Reject Btns   │
├────────────────────────┴────────────────────────────┤
│  Active Ride Section (when ride accepted)           │
└─────────────────────────────────────────────────────┘
```

### Key Elements

| Element | ID/Class | Description |
|---------|----------|-------------|
| Status Toggle | `.toggle-status` | Online/Offline switch |
| Status Indicator | `.status-indicator` | Green/Red status dot |
| Stats Grid | `.stats-grid` | Statistics cards |
| Requests List | `.requests-list` | Available ride cards |
| Request Card | `.request-card` | Individual ride request |
| Accept Button | Accept button | Accept ride |
| Reject Button | Reject button | Hide ride |

### JavaScript Functions

#### Status Functions

```javascript
// Toggle online/offline status
function toggleStatus()

// Update driver location
function updateLocation()

// Start/stop location tracking
function startLocationTracking()
function stopLocationTracking()
```

#### Request Functions

```javascript
// Fetch available ride requests
function fetchRequests()

// Accept a ride request
function acceptRide(requestId)

// Reject/hide a ride request
function rejectRide(requestId)

// Complete active ride
function completeRide()
```

#### Statistics Functions

```javascript
// Update statistics display
function updateStats()

// Format currency
function formatCurrency(amount)
```

### Request Card Structure

```html
<div class="request-card">
    <div class="request-header">
        <span class="request-id">REQ-001</span>
        <span class="request-time">Just now</span>
    </div>
    <div class="request-user">
        <span>John Doe</span>
        <span>⭐ 4.8</span>
    </div>
    <div class="request-locations">
        <div>📍 Pickup Location</div>
        <div>📍 Dropoff Location</div>
    </div>
    <div class="request-details">
        <span>5.2 km</span>
        <span>Rs. 350</span>
    </div>
    <div class="request-actions">
        <button onclick="acceptRide('REQ-001')">Accept</button>
        <button onclick="rejectRide('REQ-001')">Reject</button>
    </div>
</div>
```

### Urgent Ride Styling

```css
.request-card.urgent {
    border-color: #ef4444;
    background: linear-gradient(135deg, #fef2f2 0%, #fff 100%);
}
```

---

## Static Assets

### Directory Structure

```
static/
├── banner.png    # Banner image
├── img.png       # General image
├── logo.png      # App logo
└── path.svg      # Path/route icon (favicon)
```

### Usage

```html
<!-- Logo -->
<img src="{{ url_for('static', filename='logo.png') }}" alt="Logo">

<!-- Favicon -->
<link rel="icon" type="image/png" href="{{ url_for('static', filename='path.svg') }}">
```

---

## Responsive Design

### Breakpoints

| Breakpoint | Width | Description |
|------------|-------|-------------|
| Desktop | > 768px | Full layout |
| Tablet | 480-768px | Adjusted padding |
| Mobile | < 480px | Single column |

### Mobile Styles (Login Page)

```css
@media (max-width: 768px) {
    .w-full.max-w-md {
        max-width: 100%;
        padding: 24px;
    }
}

@media (max-width: 480px) {
    .w-full.max-w-md {
        padding: 16px;
    }
}
```

---

## Flash Messages

Flask flash messages are displayed for user feedback.

```html
{% with messages = get_flashed_messages() %}
    {% if messages %}
        {% for message in messages %}
            <div class="alert">{{ message }}</div>
        {% endfor %}
    {% endif %}
{% endwith %}
```

---

## Template Variables

### Passed from Flask

| Variable | Template | Description |
|----------|----------|-------------|
| `api_key` | user_dashboard, rider_dashboard | Google Maps API key |
| `name` | user_dashboard | User's display name |

### Example

```python
# In Flask route
return render_template("user_dashboard.html", 
                       api_key=GOOGLE_MAPS_API_KEY, 
                       name=user_name)
```

```html
<!-- In template -->
<h1>Welcome, {{ name }}!</h1>
<script src="https://maps.googleapis.com/maps/api/js?key={{ api_key }}"></script>
```
