import socketio
import time
import requests
import json
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from housekeeping.services.booking_service import BookingService
from worker_db import WorkerDB
from user_db import UserDB

# Configuration
BASE_URL = 'http://localhost:5000'
SIO_URL = 'http://localhost:5000'

# Initialize Socket Clients
sio_worker = socketio.Client()
sio_user = socketio.Client()

worker_events = []
user_events = []

@sio_worker.event
def connect():
    print("✅ Worker Socket Connected")

@sio_worker.on('new_booking')
def on_new_booking(data):
    print(f"🔔 Worker received new_booking: {data}")
    worker_events.append(('new_booking', data))

@sio_worker.on('booking_update')
def on_worker_booking_update(data):
    print(f"🔄 Worker received booking_update: {data}")
    worker_events.append(('booking_update', data))

@sio_user.event
def connect():
    print("✅ User Socket Connected")

@sio_user.on('booking_update')
def on_user_booking_update(data):
    print(f"🔄 User received booking_update: {data}")
    user_events.append(('booking_update', data))

def test_sarthak_socket_flow():
    print("=== Testing Sarthak Socket Flow ===")
    
    # 1. Setup Data
    wdb = WorkerDB()
    udb = UserDB()
    bs = BookingService()
    
    # Get Sarthak
    conn = wdb.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM workers WHERE name LIKE '%Sarthak%'")
    sarthak = cursor.fetchone()
    conn.close()
    
    if not sarthak:
        print("❌ Sarthak not found in DB")
        return
        
    sarthak_id = sarthak[0]
    print(f"found Sarthak: ID={sarthak_id}")
    
    # Create Test User
    user_email = f"test_socket_{int(time.time())}@example.com"
    user_id = udb.create_user("Socket User", user_email, "password", "user")
    print(f"Created User: ID={user_id}")
    
    # 2. Connect Sockets
    try:
        sio_worker.connect(SIO_URL)
        sio_user.connect(SIO_URL)
        
        # Join Rooms
        sio_worker.emit('join_housekeeping', {'user_type': 'worker', 'id': sarthak_id})
        sio_user.emit('join_housekeeping', {'user_type': 'user', 'id': user_id})
        
        time.sleep(1) # Wait for join
        
        # 3. Create Booking via API (simulating frontend)
        # We need to use requests to hit the actual running server
        # But if the server is not running, we can't test sockets fully end-to-end like this.
        # However, the environment says "You can use RunCommand tool".
        # But I cannot easily start the server and run this script in parallel in the same tool call sequence 
        # without blocking or complex management.
        
        # Alternative: Simulate the backend logic that emits events.
        # But we want to verify the integration.
        
        # For now, let's assume the server IS running? 
        # The prompt says "You can use this tool to show the available preview URL to user if you have started a local server successfully".
        # I haven't started it yet in this session.
        
        # I will start the server in the background using RunCommand.
        
    except Exception as e:
        print(f"❌ Socket Connection Failed: {e}")
        return

if __name__ == "__main__":
    # We can't run this without the server. 
    # This file is just for reference/future use if I start the server.
    pass
