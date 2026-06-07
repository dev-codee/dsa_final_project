import os

try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None

# Set up MongoDB connection
# You can change the connection URI via environment variable later if hosting on Atlas
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

# Initialize the client
try:
    if MongoClient is None:
        raise ImportError("pymongo module is not installed")
        
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # The database for our project
    mongo_db = mongo_client['rides_cluster']

    # Collections designed for horizontal scaling / unstructured data:
    
    # 1. Store rapid ingestion coordinates for live tracking
    live_locations_collection = mongo_db['live_locations']
    
    # 2. Store loosely coupled records like ride history, logs, and reviews
    ride_logs_collection = mongo_db['ride_logs']

    # Enable 2dsphere index for geospatial queries (e.g., matching drivers within a distance)
    live_locations_collection.create_index([("location", "2dsphere")])

except Exception as e:
    print(f"MongoDB connection warning: {e}")
    mongo_client = None
    mongo_db = None
    live_locations_collection = None
    ride_logs_collection = None
