import socketio
import requests
import jwt
import datetime
import time
import sys
import os
import sqlite3
import json
import threading

# Configuration
BASE_URL = "http://localhost:5000"
JWT_SECRET = "super-secret-key"  # From config.py
DB_PATH = "data/housekeeping.db"
USER_DB_PATH = "data/users.db"
WORKER_DB_PATH = "data/workers.db"

# Setup logging
def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")

# Token Generation
def generate_token(username):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# Database Helpers
def get_test_user():
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users LIMIT 1")
    user = cursor.fetchone()
    conn.close()
    if user:
        return {"id": user[0], "username": user[1], "email": user[2]}
    return None

def get_test_worker():
    conn = sqlite3.connect(WORKER_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, email, service FROM workers WHERE service='housekeeping' LIMIT 1")
    worker = cursor.fetchone()
    conn.close()
    if worker:
        return {"id": worker[0], "name": worker[1], "email": worker[2], "service": worker[3]}
    return None

# WebSocket Clients
user_sio = socketio.Client()
worker_sio = socketio.Client()

events_received = {
    "user_booking_update": False,
    "worker_new_booking": False,
    "worker_booking_update": False
}

@user_sio.on('connect')
def user_connect():
    log("User connected to WebSocket")

@user_sio.on('booking_update')
def user_booking_update(data):
    log(f"User received booking_update: {data}")
    events_received["user_booking_update"] = True

@worker_sio.on('connect')
def worker_connect():
    log("Worker connected to WebSocket")

@worker_sio.on('new_booking')
def worker_new_booking(data):
    log(f"Worker received new_booking: {data}")
    events_received["worker_new_booking"] = True

@worker_sio.on('booking_update')
def worker_booking_update(data):
    log(f"Worker received booking_update: {data}")
    events_received["worker_booking_update"] = True

def main():
    log("Starting WebSocket Monitoring Test...")
    
    # 1. Get Test Data
    user = get_test_user()
    worker = get_test_worker()
    
    if not user or not worker:
        log("Error: Could not find test user or worker in DB.")
        sys.exit(1)
        
    log(f"Test User: {user['username']} (ID: {user['id']})")
    log(f"Test Worker: {worker['name']} (ID: {worker['id']})")
    
    user_token = generate_token(user['username'])
    worker_token = generate_token(worker['email'])
    
    # 2. Connect WebSockets
    try:
        user_sio.connect(BASE_URL)
        worker_sio.connect(BASE_URL)
        
        # Join Rooms
        user_sio.emit('join_housekeeping', {'user_type': 'user', 'id': user['id']})
        worker_sio.emit('join_housekeeping', {'user_type': 'worker', 'id': worker['id']})
        
        time.sleep(1) # Wait for join
        
    except Exception as e:
        log(f"Error connecting to WebSocket: {e}")
        sys.exit(1)

    # 2.5 Set Worker Online
    log("Setting worker online...")
    worker_headers = {"Authorization": f"Bearer {worker_token}"}
    try:
        requests.post(f"{BASE_URL}/api/housekeeping/worker/status", json={"is_online": True}, headers=worker_headers)
    except Exception as e:
        log(f"Warning: Failed to set worker online: {e}")

    # 3. Create Booking (User -> API)
    log("Creating booking request...")
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {
        "service_type": "General Cleaning",
        "address": "123 Test St",
        "date": datetime.datetime.now().strftime('%Y-%m-%d'),
        "time": datetime.datetime.now().strftime('%I:%M %p'),
        "worker_id": worker['id'],
        "booking_type": "instant"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/housekeeping/confirm-booking", json=payload, headers=headers)
        if response.status_code == 201:
            booking_data = response.json()
            booking_id = booking_data['booking_id']
            log(f"Booking created successfully (ID: {booking_id})")
        else:
            log(f"Failed to create booking: {response.text}")
            sys.exit(1)
    except Exception as e:
        log(f"API Error: {e}")
        sys.exit(1)
        
    # Wait for Worker to receive 'new_booking'
    time.sleep(2)
    if events_received["worker_new_booking"]:
        log("  PASS: Worker received new_booking event")
    else:
        log("  FAIL: Worker did NOT receive new_booking event")

    # 4. Worker Accepts Booking (Worker -> API)
    log("Worker accepting booking...")
    worker_headers = {"Authorization": f"Bearer {worker_token}"}
    status_payload = {
        "booking_id": booking_id,
        "status": "ACCEPTED"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/housekeeping/worker/update-status", json=status_payload, headers=worker_headers)
        if response.status_code == 200:
            log("Booking status updated to ACCEPTED")
        else:
            log(f"Failed to update status: {response.text}")
            sys.exit(1)
    except Exception as e:
        log(f"API Error: {e}")
        sys.exit(1)

    # Wait for User to receive 'booking_update'
    time.sleep(2)
    if events_received["user_booking_update"]:
        log("  PASS: User received booking_update event (ACCEPTED)")
    else:
        log("  FAIL: User did NOT receive booking_update event")
        
    # Reset flag for next test
    events_received["user_booking_update"] = False

    # 5. Cancel Booking (User -> API)
    log("User cancelling booking...")
    
    # Reset flags
    events_received["worker_booking_update"] = False
    events_received["user_booking_update"] = False
    
    cancel_payload = {"booking_id": booking_id}
    try:
        response = requests.post(f"{BASE_URL}/api/housekeeping/cancel-booking", json=cancel_payload, headers=headers)
        if response.status_code == 200:
             log("Booking cancelled successfully")
        else:
             log(f"Failed to cancel booking: {response.text}")
    except Exception as e:
        log(f"API Error: {e}")

    # Wait for updates
    time.sleep(2)
    if events_received["worker_booking_update"]:
        log("  PASS: Worker received booking_update (CANCELLED)")
    else:
        log("  FAIL: Worker did NOT receive booking_update (CANCELLED)")
        
    if events_received["user_booking_update"]:
        log("  PASS: User received booking_update (CANCELLED)")
    else:
        log("  FAIL: User did NOT receive booking_update (CANCELLED)")

    # Cleanup
    user_sio.disconnect()
    worker_sio.disconnect()
    log("Test Complete.")

if __name__ == "__main__":
    main()
