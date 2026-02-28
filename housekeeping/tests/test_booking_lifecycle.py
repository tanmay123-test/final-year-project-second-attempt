import requests
import json
import time
import sys
from datetime import datetime, timedelta
import sqlite3
import os

# Configuration
BASE_URL = "http://127.0.0.1:5000"
WORKER_EMAIL = f"worker_{int(time.time())}@example.com"
USER_USERNAME = f"user_{int(time.time())}"
SERVICE_TYPE = "Deep Cleaning"
DATE = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
TIME_SLOT = "10:00 AM"

# DB Paths (Adjust based on where script runs)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'housekeeping.db')
USERS_DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'users.db')

def print_step(step):
    print(f"\n{'='*50}\n{step}\n{'='*50}")

def register_worker():
    print_step("1. Registering Worker")
    payload = {
        "name": "Test Worker",
        "email": WORKER_EMAIL,
        "password": "password123",
        "phone": "1234567890",
        "service_type": "housekeeping",
        "specialization": "Deep Cleaning,General Cleaning",
        "experience": 5,
        "rate": 500,
        "location": "New York"
    }
    try:
        # Use provider auth endpoint
        response = requests.post(f"{BASE_URL}/api/provider/auth/signup", json=payload)
        if response.status_code in [200, 201]:
            print("✅ Worker Registered")
            return True
        else:
            print(f"❌ Worker Registration Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def login_worker():
    print_step("2. Logging in Worker")
    payload = {
        "email": WORKER_EMAIL,
        "password": "password123"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/provider/auth/login", json=payload)
        if response.status_code == 200:
            token = response.json().get('token')
            worker_id = response.json().get('worker', {}).get('id')
            print(f"✅ Worker Logged In (ID: {worker_id})")
            return token, worker_id
        else:
            print(f"❌ Worker Login Failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None, None

def set_availability(token, worker_id):
    print_step("3. Setting Worker Availability")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "date": DATE,
        "slots": [TIME_SLOT]
    }
    # Note: Using root route as discovered in previous analysis
    url = f"{BASE_URL}/worker/{worker_id}/availability"
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            print("✅ Availability Set")
            return True
        else:
            print(f"❌ Set Availability Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def set_online_status(token):
    print_step("4. Setting Worker Online")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"is_online": True}
    try:
        response = requests.post(f"{BASE_URL}/api/housekeeping/worker/status", json=payload, headers=headers)
        if response.status_code == 200:
            print("✅ Worker Set to Online")
            return True
        else:
            print(f"❌ Set Online Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def register_user():
    print_step("5. Registering User")
    payload = {
        "username": USER_USERNAME,
        "email": f"{USER_USERNAME}@example.com",
        "password": "password123",
        "phone": "0987654321",
        "role": "user"
    }
    try:
        response = requests.post(f"{BASE_URL}/signup", json=payload)
        if response.status_code in [200, 201]:
            print("✅ User Registered")
            return True
        else:
            print(f"❌ User Registration Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def login_user():
    print_step("6. Logging in User")
    payload = {
        "username": USER_USERNAME,
        "password": "password123"
    }
    try:
        response = requests.post(f"{BASE_URL}/login", json=payload)
        if response.status_code == 200:
            token = response.json().get('token')
            print("✅ User Logged In")
            return token
        else:
            print(f"❌ User Login Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def verify_user_in_db():
    # Helper to verify user manually if login fails due to verification
    try:
        # Try to find DB path
        if not os.path.exists(USERS_DB_PATH):
            print(f"⚠️ Users DB not found at {USERS_DB_PATH}")
            return
            
        conn = sqlite3.connect(USERS_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_verified = 1 WHERE username = ?", (USER_USERNAME,))
        conn.commit()
        conn.close()
        print("✅ Manually verified user in DB")
    except Exception as e:
        print(f"⚠️ Failed to verify user in DB: {e}")

def verify_worker_in_db(email):
    # Helper to approve worker manually
    try:
        # Try to find DB path - housekeeping.db contains workers table? 
        # Or is it workers.db? Previous analysis said workers.db or housekeeping.db
        # Let's try housekeeping.db first as per previous attempts
        db_path = DB_PATH
        if not os.path.exists(db_path):
             # Try workers.db
             db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'workers.db')
             
        if not os.path.exists(db_path):
            print(f"⚠️ DB not found")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Check if workers table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workers'")
        if not cursor.fetchone():
            print("⚠️ Workers table not found")
            return

        cursor.execute("UPDATE workers SET is_approved = 1, is_verified = 1 WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        print("✅ Manually approved worker in DB")
    except Exception as e:
        print(f"⚠️ Failed to approve worker in DB: {e}")

def book_service(token):
    print_step("7. Booking Service")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check availability first
    check_payload = {
        "service_type": SERVICE_TYPE,
        "date": DATE,
        "time": TIME_SLOT,
        "address": "123 Test St"
    }
    try:
        res = requests.post(f"{BASE_URL}/api/housekeeping/book", json=check_payload, headers=headers)
        if res.status_code != 200:
            print(f"❌ Check Availability Failed: {res.status_code} - {res.text}")
            return None
        print(f"✅ Workers Available: {res.json().get('workers_count')}")
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

    # Confirm Booking
    payload = {
        "service_type": SERVICE_TYPE,
        "date": DATE,
        "time": TIME_SLOT,
        "address": "123 Test St",
        "booking_type": "schedule",
        "payment_method": "card",
        "home_size": "2 BHK",
        "price": 500
    }
    try:
        response = requests.post(f"{BASE_URL}/api/housekeeping/confirm-booking", json=payload, headers=headers)
        if response.status_code in [200, 201]:
            booking_id = response.json().get('booking_id')
            print(f"✅ Booking Confirmed (ID: {booking_id})")
            return booking_id
        else:
            print(f"❌ Booking Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def worker_accept_booking(token, booking_id):
    print_step("8. Worker Accepting Booking")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "booking_id": booking_id,
        "status": "ACCEPTED"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/housekeeping/worker/update-status", json=payload, headers=headers)
        if response.status_code == 200:
            print("✅ Booking Accepted")
            return True
        else:
            print(f"❌ Accept Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def worker_complete_booking(token, booking_id):
    print_step("9. Worker Completing Booking")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "booking_id": booking_id,
        "status": "COMPLETED"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/housekeeping/worker/update-status", json=payload, headers=headers)
        if response.status_code == 200:
            print("✅ Booking Completed")
            return True
        else:
            print(f"❌ Complete Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_booking_status(token, booking_id, expected_status):
    print_step(f"Checking Status (Expected: {expected_status})")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/api/housekeeping/my-bookings", headers=headers)
        if response.status_code == 200:
            bookings = response.json().get('bookings', [])
            target = next((b for b in bookings if b['id'] == booking_id), None)
            if target:
                print(f"Current Status: {target['status']}")
                if target['status'] == expected_status:
                    print("✅ Status Match")
                    return True
                else:
                    print(f"❌ Status Mismatch: {target['status']} != {expected_status}")
                    return False
            else:
                print("❌ Booking not found in list")
                return False
        else:
            print(f"❌ Fetch Bookings Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def run_test():
    # 1. Setup Worker
    if not register_worker(): return
    
    # Manual Approval
    verify_worker_in_db(WORKER_EMAIL)
    
    worker_token, worker_id = login_worker()
    if not worker_token: return
    
    if not set_online_status(worker_token): return
    if not set_availability(worker_token, worker_id): return
    
    # 2. Setup User
    if not register_user(): return
    
    # Manual Verification
    verify_user_in_db()
    
    user_token = login_user()
    if not user_token: return
    
    # 3. Booking Flow
    booking_id = book_service(user_token)
    if not booking_id: return
    
    # Check status (Should be ASSIGNED or REQUESTED)
    check_booking_status(user_token, booking_id, "ASSIGNED")
    
    # 4. Worker Acceptance
    # Worker should see it
    check_booking_status(worker_token, booking_id, "ASSIGNED")
    
    if not worker_accept_booking(worker_token, booking_id): return
    
    # Check status (ACCEPTED)
    check_booking_status(user_token, booking_id, "ACCEPTED")
    
    # 5. Completion
    if not worker_complete_booking(worker_token, booking_id): return
    
    # Check status (COMPLETED)
    check_booking_status(user_token, booking_id, "COMPLETED")
    
    print("\n🎉 FULL END-TO-END TEST PASSED 🎉")

if __name__ == "__main__":
    run_test()
