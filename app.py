import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime
from app.models.user import db, User
from app.models.mongo_setup import live_locations_collection, ride_logs_collection
from app.DataStructures.queue import RideRequestQueue
from app.DataStructures.stack import UserRideHistoryManager
from auth import auth_bp

app = Flask(__name__)

# --- Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
# Ensure instance directory exists
instance_path = os.path.join(basedir, 'instance')
os.makedirs(instance_path, exist_ok=True)
# --- PostgreSQL Database Configuration ---
# Set database URI to PostgreSQL instead of SQLite
PG_USER = os.environ.get("PG_USER", "postgres")
PG_PASSWORD = os.environ.get("PG_PASSWORD", "password")
PG_DB = os.environ.get("PG_DB", "rides_db")
PG_HOST = os.environ.get("PG_HOST", "localhost")
PG_PORT = os.environ.get("PG_PORT", "5432")

# We leave the SQLite URI here as a fallback for development if Postgres is not set up
USE_POSTGRES = os.environ.get("USE_POSTGRES", "False").lower() in ["true", "1"]

if USE_POSTGRES:
    # Vercel provides POSTGRES_URL. SQLAlchemy requires `postgresql://` instead of `postgres://`
    database_url = os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}'
else:
    db_path = os.path.join(instance_path, 'users.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '1234') 
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', "AIzaSyDwpdSiu8lCLt9Y5ttql_MujzlSJgt-ig0")

# Initialize db with this app
db.init_app(app)        

# Create tables
with app.app_context():
    db.create_all()

# Register auth blueprint
app.register_blueprint(auth_bp)

# Initialize global queue and storage
ride_queue = RideRequestQueue()
active_rides = {}
rider_locations = {}  # Store rider locations
request_counter = 0
user_ride_history = UserRideHistoryManager()  # Stack-based ride history
user_active_requests = {}  # Track user's active ride requests {user_email: request_data}

# --- Authentication Routes ---

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/user_dashboard/")
def user_dashboard():
    # Check authentication
    if 'user_email' not in session:
        flash("Please login to access the dashboard")
        return redirect(url_for('auth.login'))
    
    user_name = session.get('user_name') or 'Guest'
    return render_template("user_dashboard.html", api_key=GOOGLE_MAPS_API_KEY, name=user_name)



# --- Rider Dashboard Routes ---

@app.route("/rider_dashboard/")
def rider_dashboard():
    """Rider dashboard page"""
    # Check authentication and role
    if 'user_email' not in session:
        flash("Please login to access the dashboard")
        return redirect(url_for('auth.login'))
    
    user_name = session.get('user_name') or 'Driver'
    return render_template("rider_dashboard.html", api_key=GOOGLE_MAPS_API_KEY, name=user_name)

@app.route("/api/rider/update-location", methods=["POST"])
def update_rider_location():
    """Update rider's current location"""
    try:
        data = request.json
        rider_email = session.get('user_email')
        
        if not rider_email:
            return jsonify({"error": "Not authenticated"}), 401
        
        location = {
            'lat': data.get('lat'),
            'lng': data.get('lng'),
            'updated_at': datetime.now().isoformat()
        }
        
        # In-memory update
        rider_locations[rider_email] = location
        
        # DISTRIBUTED DB DEMO (MongoDB)
        # Store high-frequency streaming geo-events in MongoDB
        if live_locations_collection is not None:
            try:
                live_locations_collection.insert_one({
                    "rider_email": rider_email,
                    "role": "rider",
                    "location": {
                        "type": "Point",
                        # Notice how MongoDB represents coordinates as [longitude, latitude]
                        "coordinates": [float(data.get('lng')), float(data.get('lat'))]
                    },
                    "timestamp": datetime.utcnow()
                })
            except Exception as e:
                print(f"MongoDB warning: {e}")
        
        return jsonify({
            "success": True,
            "message": "Location updated"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/rider/requests", methods=["GET"])
def get_rider_requests():
    """Get nearby ride requests for rider based on location"""
    try:
        rider_email = session.get('user_email')
        
        if not rider_email:
            return jsonify({"error": "Not authenticated"}), 401
        
        # Get rider's location
        rider_location = rider_locations.get(rider_email)
        
        if not rider_location:
            # Return all pending if location not available, but still filter rejected rides
            all_pending = ride_queue.get_all_pending()
            # Filter out rides this rider has rejected
            rejected_ids = ride_queue.rejected_rides.get(rider_email, [])
            pending_requests = [r for r in all_pending if r['id'] not in rejected_ids]
        else:
            # Get nearby rides - show up to 20 rides, sorted by distance
            pending_requests = ride_queue.get_nearby_rides_for_rider(
                rider_location, 
                rider_email, 
                max_rides=20  
            )
        
        return jsonify({
            "success": True,
            "requests": pending_requests,
            "queue_size": ride_queue.size(),
            "has_location": rider_location is not None
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/rider/accept-ride", methods=["POST"])
def accept_ride():
    """Accept a ride request - removes from queue"""
    try:
        data = request.json
        request_id = data.get('requestId')
        rider_email = session.get('user_email')
        
        if not rider_email:
            return jsonify({"error": "Not authenticated"}), 401
        
        if not request_id:
            return jsonify({"error": "Request ID is required"}), 400
        
        # Check if rider already has an active ride
        if rider_email in active_rides:
            return jsonify({"error": "You already have an active ride. Please complete it first."}), 400
        
        # Remove from queue
        ride_request = ride_queue.remove_by_id(request_id)
        
        if not ride_request:
            return jsonify({"error": "Request not found in queue"}), 404
        
        # Update request status
        ride_request['status'] = 'accepted'
        ride_request['rider_email'] = rider_email
        ride_request['accepted_at'] = datetime.now().isoformat()
        
        # Add to active rides
        active_rides[rider_email] = ride_request
        
        return jsonify({
            "success": True,
            "message": "Ride accepted successfully",
            "ride": ride_request,
            "remaining_in_queue": ride_queue.size()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/rider/reject-ride", methods=["POST"])
def reject_ride():
    """Reject a ride - hides it from this rider only"""
    try:
        data = request.json
        request_id = data.get('requestId')
        rider_email = session.get('user_email')
        
        if not request_id:
            return jsonify({"error": "Request ID is required"}), 400
        
        # Mark as rejected for this rider
        ride_queue.reject_ride(rider_email, request_id)
        
        return jsonify({
            "success": True,
            "message": "Ride hidden from your list"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/rider/stats", methods=["GET"])
def get_rider_stats():
    """Get rider statistics"""
    try:
        rider_email = session.get('user_email')
        queue_stats = ride_queue.get_statistics()
        
        stats = {
            "completed_rides": queue_stats['completed_count'],
            "today_earnings": queue_stats['completed_count'] * 350,
            "hours_online": 0,
            "rating": 4.8,
            "pending_requests": queue_stats['total_pending'],
            "urgent_requests": queue_stats['urgent_count']
        }
        
        return jsonify({
            "success": True,
            "stats": stats
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- User Route Request Routes ---

@app.route("/api/user/request-ride", methods=["POST"])
def request_ride():
    """User requests a ride - adds to priority queue"""
    global request_counter
    try:
        data = request.json
        
        if not data or "origin" not in data or "destination" not in data:
            return jsonify({"error": "Origin and destination are required"}), 400
        
        request_counter += 1
        user_name = session.get('user_name', data.get("userName", "Guest User"))
        is_urgent = data.get("isUrgent", False)
        
        # Create ride request
        ride_request = {
            "id": f"{'URG' if is_urgent else 'REQ'}-{request_counter:03d}",
            "user_email": session.get('user_email', 'guest'),
            "userName": user_name,
            "userRating": 4.8,
            "pickup": data["origin"].get("address", "Unknown"),
            "dropoff": data["destination"].get("address", "Unknown"),
            "pickupCoords": {
                "lat": data["origin"]["lat"],
                "lng": data["origin"]["lng"]
            },
            "dropoffCoords": {
                "lat": data["destination"]["lat"],
                "lng": data["destination"]["lng"]
            },
            "distance": data.get("distance", "N/A"),
            "duration": data.get("duration", "N/A"),
            "rideType": data.get("rideType", "economy"),
            "fare": data.get("fare", 0),
            "paymentMethod": data.get("paymentMethod", "cash"),
            "status": "pending",
            "time": "Just now",
            "is_urgent": is_urgent,  # Ensure is_urgent flag is set
            "created_at": datetime.now().isoformat()
        }
        
        # Add to priority queue
        queued_request = ride_queue.enqueue(ride_request, is_urgent=is_urgent)
        
        # Track user's active request
        user_email = session.get('user_email', 'guest')
        user_active_requests[user_email] = ride_request
        
        # ---------------------------------------------------------
        # DISTRIBUTED DB DEMO (MongoDB)
        # Unstructured Log of a new request
        # ---------------------------------------------------------
        if ride_logs_collection is not None:
            try:
                ride_logs_collection.insert_one({
                    "event": "ride_requested",
                    "ride_id": ride_request["id"],
                    "user_email": user_email,
                    "is_urgent": is_urgent,
                    "pickup": ride_request["pickup"],
                    "dropoff": ride_request["dropoff"],
                    "timestamp": datetime.utcnow()
                })
            except Exception as e:
                print(f"MongoDB warning: {e}")
                
        return jsonify({
            "success": True,
            "message": f"{'Urgent ' if is_urgent else ''}Ride requested successfully",
            "request": queued_request,
            "queue_size": ride_queue.size(),
            "is_urgent": is_urgent
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/queue/status", methods=["GET"])
def get_queue_status():
    """Get current queue status and statistics"""
    try:
        stats = ride_queue.get_statistics()
        
        return jsonify({
            "success": True,
            "queue_size": ride_queue.size(),
            "statistics": stats,
            "next_request": ride_queue.peek()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- User Ride Status & History Routes ---a

@app.route("/api/user/ride-status", methods=["GET"])
def get_user_ride_status():
    """Get current ride status for user - checking if ride is pending or accepted"""
    try:
        user_email = session.get('user_email', 'guest')
        
        # Check if user has an active request
        active_request = user_active_requests.get(user_email)
        
        if not active_request:
            return jsonify({
                "success": True,
                "has_active_ride": False,
                "status": "none",
                "message": "No active ride request"
            }), 200
        
        request_id = active_request.get('id')
        
        # Check if ride is still in queue (pending)
        pending_rides = ride_queue.get_all_pending()
        is_pending = any(r['id'] == request_id for r in pending_rides)
        
        if is_pending:
            return jsonify({
                "success": True,
                "has_active_ride": True,
                "status": "searching",
                "message": "Finding a driver for you...",
                "ride": active_request
            }), 200
        
        # Check if ride was accepted by a rider
        for rider_email, ride in active_rides.items():
            if ride.get('id') == request_id:
                # Get rider details
                rider = User.query.filter_by(email=rider_email).first()
                rider_name = rider.name if rider else "Your Driver"
                
                return jsonify({
                    "success": True,
                    "has_active_ride": True,
                    "status": "accepted",
                    "message": "Driver found!",
                    "ride": ride,
                    "rider": {
                        "name": rider_name,
                        "email": rider_email,
                        "rating": 4.8,
                        "vehicle": "Toyota Corolla",
                        "plate_number": "ABC-1234"
                    }
                }), 200
        
        # Check if ride was actually completed (in history)
        user_history = user_ride_history.get_user_history(user_email)
        completed_ride = None
        for ride in user_history:
            if ride.get('id') == request_id and ride.get('status') == 'completed':
                completed_ride = ride
                break
        
        if completed_ride:
            # Ride was actually completed
            return jsonify({
                "success": True,
                "has_active_ride": False,
                "status": "completed",
                "message": "Ride completed",
                "ride": completed_ride
            }), 200
        else:
            # Ride was cancelled or doesn't exist - clear the active request
            if user_email in user_active_requests:
                del user_active_requests[user_email]
            return jsonify({
                "success": True,
                "has_active_ride": False,
                "status": "cancelled",
                "message": "Ride was cancelled or not found"
            }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/user/ride-history", methods=["GET"])
def get_user_ride_history():
    """Get user's ride history from stack"""
    try:
        user_email = session.get('user_email', 'guest')
        count = request.args.get('count', type=int)
        
        # Get history from stack
        history = user_ride_history.get_user_history(user_email, count)
        
        return jsonify({
            "success": True,
            "history": history,
            "total_rides": len(user_ride_history.get_user_history(user_email))
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/user/cancel-ride", methods=["POST"])
def cancel_user_ride():
    """Cancel user's active ride request"""
    try:
        user_email = session.get('user_email', 'guest')
        active_request = user_active_requests.get(user_email)
        
        if not active_request:
            return jsonify({"error": "No active ride to cancel"}), 404
        
        request_id = active_request.get('id')
        
        # Remove from queue
        ride_queue.remove_by_id(request_id)
        
        # Remove from user's active requests
        del user_active_requests[user_email]
        
        return jsonify({
            "success": True,
            "message": "Ride cancelled successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update complete-ride to also update user's history
@app.route("/api/rider/complete-ride", methods=["POST"])
def complete_ride():
    """Complete an active ride - adds to user's ride history stack"""
    try:
        data = request.json
        request_id = data.get('requestId')
        rider_email = session.get('user_email')
        
        if not rider_email:
            return jsonify({"error": "Not authenticated"}), 401
        
        if rider_email not in active_rides:
            return jsonify({"error": "No active ride found"}), 404
        
        completed_ride = active_rides[rider_email]
        
        # Verify request_id matches if provided
        if request_id and completed_ride.get('id') != request_id:
            return jsonify({"error": "Request ID mismatch"}), 400
        
        completed_ride['status'] = 'completed'
        completed_ride['completed_at'] = datetime.now().isoformat()
        
        # Get rider details to add to completed ride
        rider = User.query.filter_by(email=rider_email).first()
        completed_ride['rider_name'] = rider.name if rider else "Driver"
        completed_ride['rider_rating'] = 4.8
        
        # Add to queue's history
        ride_queue.request_history.append(completed_ride)
        
        # Add to USER's ride history stack
        user_email = completed_ride.get('user_email', 'guest')
        user_ride_history.add_completed_ride(user_email, completed_ride)
        
        # Clear user's active request
        if user_email in user_active_requests:
            del user_active_requests[user_email]
        
        # Remove from active rides
        del active_rides[rider_email]
        
        # ---------------------------------------------------------
        # DISTRIBUTED DB DEMO (MongoDB)
        # Store permanent ride receipts (flexible structure)
        # ---------------------------------------------------------
        if ride_logs_collection is not None:
            try:
                ride_logs_collection.insert_one({
                    "event": "ride_completed",
                    "ride_id": completed_ride.get("id"),
                    "rider_email": rider_email, # driver
                    "user_email": user_email,   # passenger
                    "completed_at": datetime.utcnow(),
                    "ride_details": completed_ride
                })
            except Exception as e:
                print(f"MongoDB warning: {e}")
        
        return jsonify({
            "success": True,
            "message": "Ride completed successfully"
        }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)