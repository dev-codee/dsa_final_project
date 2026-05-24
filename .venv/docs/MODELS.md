# Models Documentation

Documentation for database models used in DSA RIDES application.

---

## Overview

The application uses SQLAlchemy ORM with SQLite database. Models are defined in the `app/models/` directory.

---

## User Model

**File:** `app/models/user.py`

The User model stores information for both riders (users) and drivers.

### Schema

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(500), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    role = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique identifier |
| `name` | String(200) | Not Null | User's full name |
| `email` | String(500) | Not Null, Unique | User's email address |
| `password` | String(500) | Not Null | Hashed password (Werkzeug) |
| `role` | Integer | Not Null | 1 = User, 2 = Driver |
| `date_created` | DateTime | Default: UTC now | Account creation timestamp |

### Role Values

| Value | Role |
|-------|------|
| 1 | Regular User (Passenger) |
| 2 | Driver |

### Methods

#### `__repr__()`

Returns string representation of the user.

```python
def __repr__(self) -> str:
    return f"{self.name} - {self.email}"
```

### Usage Examples

#### Create a new user

```python
from app.models.user import db, User
from werkzeug.security import generate_password_hash

# Create user
new_user = User(
    name="John Doe",
    email="john@example.com",
    password=generate_password_hash("securepassword"),
    role=1  # Regular user
)

db.session.add(new_user)
db.session.commit()
```

#### Query user by email

```python
user = User.query.filter_by(email="john@example.com").first()
if user:
    print(f"Found user: {user.name}")
```

#### Query all drivers

```python
drivers = User.query.filter_by(role=2).all()
for driver in drivers:
    print(f"Driver: {driver.name}")
```

#### Check password

```python
from werkzeug.security import check_password_hash

user = User.query.filter_by(email="john@example.com").first()
if user and check_password_hash(user.password, "inputpassword"):
    print("Password correct!")
```

---

## Driver Model

**File:** `app/models/driver.py`

> **Note:** This model exists but is not currently used in the application. The User model with `role=2` is used for drivers instead.

### Schema

```python
class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(500), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
```

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique identifier |
| `name` | String(200) | Not Null | Driver's full name |
| `email` | String(500) | Not Null, Unique | Driver's email address |
| `password` | String(500) | Not Null | Hashed password |
| `date_created` | DateTime | Default: UTC now | Account creation timestamp |

---

## In-Memory Data Structures

In addition to database models, the application uses in-memory data structures for real-time data:

### Active Rides

**Location:** `run.py`

```python
active_rides = {}  # rider_email -> ride_request dict
```

Stores currently active rides indexed by driver email.

### Rider Locations

**Location:** `run.py`

```python
rider_locations = {}  # rider_email -> location dict
```

Stores real-time driver locations.

```python
# Location structure
location = {
    'lat': 24.8607,
    'lng': 67.0011,
    'updated_at': '2025-12-30T10:30:00'
}
```

### User Active Requests

**Location:** `run.py`

```python
user_active_requests = {}  # user_email -> ride_request dict
```

Tracks each user's current active ride request.

### Ride Queue

**Location:** `run.py`

```python
ride_queue = RideRequestQueue()
```

Priority queue for managing ride requests.

### User Ride History

**Location:** `run.py`

```python
user_ride_history = UserRideHistoryManager()
```

Stack-based storage for completed ride history per user.

---

## Database Configuration

**Location:** `run.py`

```python
# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')
os.makedirs(instance_path, exist_ok=True)
db_path = os.path.join(instance_path, 'users.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()
```

### Database Location

```
.venv/instance/users.db
```

---

## Authentication Module

**File:** `app/authenticate.py`

### Functions

#### `checklogin(username, password, role) -> bool`

Validates user credentials and role.

**Parameters:**
- `username`: User's email
- `password`: Plain text password
- `role`: "user" or "driver"

**Returns:** `True` if authentication successful, `False` otherwise

**Logic:**
1. Query user by email
2. Verify password hash
3. Check role matches (1 for user, 2 for driver)

#### `signup(name, email, password, role) -> bool`

Creates a new user account.

**Parameters:**
- `name`: User's full name
- `email`: User's email
- `password`: Plain text password (will be hashed)
- `role`: "user" or "driver"

**Returns:** `True` if signup successful, `False` if email exists

**Logic:**
1. Check if email already exists
2. Hash the password
3. Create User with role (1 for user, 2 for driver)
4. Commit to database

---

## Future Improvements

Consider adding these models for enhanced functionality:

### Vehicle Model (Proposed)

```python
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.Integer)
    plate_number = db.Column(db.String(20))
    color = db.Column(db.String(50))
```

### Ride Model (Proposed)

```python
class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pickup_address = db.Column(db.String(500))
    dropoff_address = db.Column(db.String(500))
    pickup_lat = db.Column(db.Float)
    pickup_lng = db.Column(db.Float)
    dropoff_lat = db.Column(db.Float)
    dropoff_lng = db.Column(db.Float)
    fare = db.Column(db.Float)
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    accepted_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
```

### Rating Model (Proposed)

```python
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.id'))
    rater_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ratee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Integer)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
```
