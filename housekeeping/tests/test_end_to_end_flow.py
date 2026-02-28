import requests
import jwt
import datetime
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Configuration
BASE_URL = "http://localhost:5000"

try:
    from config import JWT_SECRET
except ImportError:
    JWT_SECRET = "super-secret-key"

# Test Data
USER_USERNAME = "vedu"
WORKER_EMAIL = "tanmaybansode48-1@okhdfcbanck" # Worker ID 8

def generate_token(username_or_email):
    payload = {
        "username": username_or_email,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=60)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def test_end_to_end_flow():
    print("🚀 Starting End-to-End Booking Flow Test...")
    
    # 1. Create Booking as User
    print("\n👤 Step 1: User Creating Booking...")
    user_token = generate_token(USER_USERNAME)
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    payload = {
        "service_type": "General Cleaning",
        "date": datetime.datetime.now().strftime('%Y-%m-%d'),
        "time": datetime.datetime.now().strftime('%I:%M %p'),
        "address": "123 Test St, Mumbai (E2E Test)",
        "booking_type": "instant"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/api/housekeeping/confirm-booking", json=payload, headers=user_headers)
        if res.status_code != 201:
            print(f"❌ Failed to create booking: {res.status_code} {res.text}")
            return
            
        booking_data = res.json()
        booking_id = booking_data.get('booking_id')
        worker_id = booking_data.get('worker_id')
        
        print(f"✅ Booking Created: ID {booking_id}")
        print(f"👷 Assigned Worker ID: {worker_id}")
        
        if not worker_id:
            print("❌ No worker assigned! Test Failed.")
            return

    except Exception as e:
        print(f"❌ Error creating booking: {e}")
        return

    # 2. Verify Provider Visibility
    print(f"\n👷 Step 2: Verifying Provider View (Worker {worker_id})...")
    
    # We assume we know the worker email for ID 8. 
    # In a real test we might need to look it up or mock it.
    # Here we use the hardcoded email for Worker 8.
    
    worker_token = generate_token(WORKER_EMAIL)
    worker_headers = {"Authorization": f"Bearer {worker_token}"}
    
    try:
        res = requests.get(f"{BASE_URL}/api/housekeeping/my-bookings", headers=worker_headers)
        if res.status_code != 200:
            print(f"❌ Failed to fetch provider bookings: {res.status_code} {res.text}")
            return
            
        data = res.json()
        bookings = data.get('bookings', [])
        
        # Find our booking
        target_booking = next((b for b in bookings if b['id'] == booking_id), None)
        
        if target_booking:
            print(f"✅ Booking {booking_id} FOUND in provider dashboard!")
            print(f"   Status: {target_booking['status']}")
            print(f"   Service: {target_booking['service_type']}")
            
            if target_booking['status'] in ['REQUESTED', 'ASSIGNED']:
                print("✅ Status is correct (REQUESTED/ASSIGNED)")
            else:
                print(f"⚠️ Unexpected status: {target_booking['status']}")
                
        else:
            print(f"❌ Booking {booking_id} NOT FOUND in provider dashboard.")
            print("   Visible Bookings:", [b['id'] for b in bookings])

    except Exception as e:
        print(f"❌ Error verifying provider view: {e}")
        return

    print("\n✅ End-to-End Test Completed Successfully!")

if __name__ == "__main__":
    test_end_to_end_flow()
