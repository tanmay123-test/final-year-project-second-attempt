import sys
import os
import requests
import json
from datetime import datetime, timedelta
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configuration
BASE_URL = "http://localhost:5000"
timestamp = int(time.time())
WORKER_EMAIL = f"cleaner_avail_{timestamp}@example.com"
USER_EMAIL = f"user_avail_{timestamp}@example.com"

def test_availability_flow():
    print("🚀 Starting Availability Flow Test...")

    # 1. Register Worker
    print("\n1. Registering Worker...")
    worker_data = {
        "email": WORKER_EMAIL,
        "password": "password123",
        "name": "Avail Test Worker",
        "phone": "9998887776",
        "service_type": "housekeeping",
        "specialization": "Deep Cleaning", # Single specialization for test
        "experience": 3,
        "location": "Mumbai"
    }
    
    # Clean up existing
    # (Assuming we can't easily delete, we'll just try to login or register)
    
    session = requests.Session()
    
    # Try login first
    try:
        res = session.post(f"{BASE_URL}/api/provider/auth/login", json={
            "email": WORKER_EMAIL, "password": "password123"
        })
        if res.status_code == 200:
            worker_id = res.json()['worker']['id']
            print(f"✅ Logged in as Worker ID: {worker_id}")
        else:
            # Register
            res = session.post(f"{BASE_URL}/api/provider/auth/signup", json=worker_data)
            if res.status_code == 201:
                worker_id = res.json()['worker_id']
                print(f"✅ Registered Worker ID: {worker_id}")
                
                # Approve worker manually (hack for test)
                try:
                    import sqlite3
                    # Try correct path based on config
                    db_paths = ['data/workers.db', 'expertease.db']
                    approved = False
                    for db_path in db_paths:
                        if os.path.exists(db_path):
                            try:
                                conn = sqlite3.connect(db_path)
                                c = conn.cursor()
                                # Check if table exists
                                c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workers'")
                                if c.fetchone():
                                    c.execute("UPDATE workers SET status='approved' WHERE id=?", (worker_id,))
                                    if c.rowcount > 0:
                                        conn.commit()
                                        print(f"✅ Manually approved worker in {db_path}")
                                        approved = True
                                conn.close()
                                if approved: break
                            except Exception as db_e:
                                print(f"⚠️ DB Error {db_path}: {db_e}")
                    
                    if not approved:
                        print("⚠️ Could not find worker in any DB to approve")

                    # Login to get token
                    res = session.post(f"{BASE_URL}/api/provider/auth/login", json={
                        "email": WORKER_EMAIL, "password": "password123"
                    })
                    if res.status_code == 200:
                        token = res.json().get('token')
                        session.headers.update({"Authorization": f"Bearer {token}"})
                        print("✅ Logged in and got token")
                    else:
                        print(f"❌ Login failed after approval: {res.text}")
                        return
                except Exception as e:
                    print(f"⚠️ Failed to approve worker: {e}")

            else:
                print(f"❌ Registration failed: {res.text}")
                return
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # 2. Add Availability (Simulating Frontend Loop)
    print("\n2. Adding Availability Slots...")
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    slots = ["09:00 AM", "10:00 AM", "11:00 AM"]
    
    # Add for today
    for slot in slots:
        res = session.post(f"{BASE_URL}/worker/{worker_id}/availability", json={
            "date": today,
            "time_slot": slot
        })
        if res.status_code == 200 or res.status_code == 201:
            print(f"   Added {today} {slot}")
        else:
            print(f"   ❌ Failed to add {today} {slot}: {res.text}")

    # Add for tomorrow (Recurring simulation)
    for slot in slots:
        res = session.post(f"{BASE_URL}/worker/{worker_id}/availability", json={
            "date": tomorrow,
            "time_slot": slot
        })
        if res.status_code == 200 or res.status_code == 201:
            print(f"   Added {tomorrow} {slot}")

    # 3. Get Availability (Simulating Week View)
    print("\n3. Verifying Availability Fetch...")
    res = session.get(f"{BASE_URL}/worker/{worker_id}/availability?date={today}")
    data = res.json()
    print(f"   Today's slots: {len(data.get('availability', []))}")
    if len(data.get('availability', [])) == 3:
        print("✅ Today's slots verified")
    else:
        print("❌ Today's slots mismatch")

    res = session.get(f"{BASE_URL}/worker/{worker_id}/availability?date={tomorrow}")
    data = res.json()
    print(f"   Tomorrow's slots: {len(data.get('availability', []))}")
    if len(data.get('availability', [])) == 3:
        print("✅ Tomorrow's slots verified")
    else:
        print("❌ Tomorrow's slots mismatch")

    # 4. Check Booking Availability (User Side)
    print("\n4. Checking User Booking Availability...")
    
    # Ensure worker is Online
    # Need to be authenticated as worker for this endpoint
    session.post(f"{BASE_URL}/api/housekeeping/worker/status", json={"is_online": True})
    
    # Check valid slot
    # This endpoint requires USER authentication
    # We need to login as a user first or mock the token
    # Let's try to login as a user
    
    user_session = requests.Session()
    # Assuming we have a user login endpoint
    # Or we can just mock headers if we know how to generate token
    # But for e2e, better to use existing user or register one
    
    # Register/Login User
    user_username = f"testuser_avail_{timestamp}"
    user_data = {
        "email": USER_EMAIL,
        "password": "password123",
        "name": "Test User",
        "username": user_username
    }
    
    # Try login
    res = user_session.post(f"{BASE_URL}/login", json={"username": user_username, "password": "password123"})
    if res.status_code != 200:
        # Register
        res = user_session.post(f"{BASE_URL}/signup", json=user_data)
        if res.status_code == 201:
             print("✅ User registered")
             # Verify user manually (hack for test)
             try:
                 import sqlite3
                 # Try both paths just in case
                 db_paths = ['data/users.db', 'expertease.db']
                 verified = False
                 for db_path in db_paths:
                     if os.path.exists(db_path):
                         try:
                             conn = sqlite3.connect(db_path)
                             c = conn.cursor()
                             # Check if table exists
                             c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
                             if c.fetchone():
                                 c.execute("UPDATE users SET is_verified=1 WHERE username=?", (user_username,))
                                 if c.rowcount > 0:
                                     conn.commit()
                                     print(f"✅ Manually verified user in {db_path}")
                                     verified = True
                             conn.close()
                             if verified: break
                         except Exception as db_e:
                             print(f"⚠️ DB Error {db_path}: {db_e}")
                 
                 if not verified:
                     print("⚠️ Could not find user in any DB to verify")

                 # Login again
                 res = user_session.post(f"{BASE_URL}/login", json={"username": user_username, "password": "password123"})
             except Exception as e:
                 print(f"⚠️ Failed to verify user: {e}")
    
    if res.status_code == 200:
        token = res.json().get('token')
        user_session.headers.update({"Authorization": f"Bearer {token}"})
        print("✅ User logged in")
    else:
        print(f"⚠️ User login failed: {res.status_code}. Using unauthenticated request (might fail if auth required)")

    res = user_session.post(f"{BASE_URL}/api/housekeeping/book", json={
        "service_type": "Deep Cleaning",
        "date": today,
        "time": "09:00 AM",
        "address": "Mumbai"
    })
    
    if res.status_code == 200:
        print("✅ User can see availability for 09:00 AM")
    else:
        print(f"❌ User CANNOT see availability for 09:00 AM: {res.status_code} {res.text}")

    # Check INVALID slot (time not added)
    res = user_session.post(f"{BASE_URL}/api/housekeeping/book", json={
        "service_type": "Deep Cleaning",
        "date": today,
        "time": "08:00 PM", # Not in our list
        "address": "Mumbai"
    })
    
    if res.status_code == 404:
        print("✅ User correctly blocked for 08:00 PM (No Slot)")
    else:
        print(f"❌ User WRONGLY sees availability for 08:00 PM: {res.status_code} {res.text}")

    # 5. Check Offline Status Restriction
    print("\n5. Checking Offline Status Restriction...")
    # Set worker offline
    session.post(f"{BASE_URL}/api/housekeeping/worker/status", json={"is_online": False})
    
    res = user_session.post(f"{BASE_URL}/api/housekeeping/book", json={
        "service_type": "Deep Cleaning",
        "date": today,
        "time": "09:00 AM", # Valid slot, but worker offline
        "address": "Mumbai"
    })
    
    if res.status_code == 404:
        print("✅ User blocked when worker is Offline")
    elif res.status_code == 200:
        print("⚠️ Endpoint returned 200 (Other workers might be available)")
    else:
        print(f"❌ Unexpected status: {res.status_code}")

    print("\nTest Complete!")

if __name__ == "__main__":
    test_availability_flow()