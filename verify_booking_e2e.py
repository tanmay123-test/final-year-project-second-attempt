import requests
import time
import sys
import sqlite3
import os

# Base URL
BASE_URL = "http://localhost:5000"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "users.db")

def ensure_test_user():
    print("👤 Setting up test user...")
    username = "test_e2e"
    email = "test_e2e@example.com"
    password = "password123"
    
    # 1. Try to login
    try:
        res = requests.post(f"{BASE_URL}/login", json={
            "username": username,
            "password": password
        })
        if res.status_code == 200:
            print("✅ User already exists and logged in")
            return res.json().get('token')
    except Exception as e:
        print(f"⚠️ Login check failed: {e}")

    # 2. Register if login failed
    print("📝 Registering new user...")
    res = requests.post(f"{BASE_URL}/signup", json={
        "name": "Test User E2E",
        "username": username,
        "email": email,
        "password": password
    })
    
    if res.status_code not in [200, 201, 400]: # 400 might mean user exists but password wrong
        print(f"❌ Registration failed: {res.text}")
        return None
        
    # 3. Manually verify in DB
    print("🔓 Verifying user in DB...")
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET is_verified=1 WHERE username=?", (username,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ DB update failed: {e}")
        return None
        
    # 4. Login again
    print("🔑 Logging in...")
    res = requests.post(f"{BASE_URL}/login", json={
        "username": username,
        "password": password
    })
    
    if res.status_code != 200:
        print(f"❌ Login failed: {res.text}")
        return None
        
    return res.json().get('token')

def test_booking_flow():
    print("🚀 Starting E2E Booking Flow Test...")
    
    token = ensure_test_user()
    if not token:
        print("❌ Could not get auth token")
        return
        
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Services
    print("\n🔍 Fetching services...")
    res = requests.get(f"{BASE_URL}/api/housekeeping/services", headers=headers)
    if res.status_code != 200:
        print(f"❌ Failed to fetch services: {res.text}")
        return
    services = res.json().get('services', [])
    if not services:
        print("❌ No services found")
        return
    service = services[0]['name']
    print(f"✅ Found service: {service}")

    # 3. Check Availability (Instant)
    print("\n⚡ Checking Instant Availability...")
    check_data = {
        "service_type": service,
        "address": "123 Test St",
        "booking_type": "instant"
    }
    res = requests.post(f"{BASE_URL}/api/housekeeping/check-availability", json=check_data, headers=headers)
    
    if res.status_code == 404:
        print("⚠️ No workers available for instant booking. Trying Schedule...")
        # Try Schedule
        check_data['booking_type'] = 'schedule'
        check_data['date'] = '2026-03-01' # Future date
        check_data['time'] = '10:00 AM'
        res = requests.post(f"{BASE_URL}/api/housekeeping/check-availability", json=check_data, headers=headers)
        
    if res.status_code != 200:
        print(f"❌ Availability check failed: {res.text}")
        return
    
    avail_data = res.json()
    print(f"✅ Availability confirmed: {avail_data.get('workers_count', 0)} workers")

    # 4. Confirm Booking
    print("\n📝 Confirming Booking...")
    confirm_data = check_data.copy()
    confirm_data['home_size'] = '2 BHK'
    confirm_data['price'] = 500
    confirm_data['worker_id'] = None # Should be handled by backend for instant
    
    res = requests.post(f"{BASE_URL}/api/housekeeping/confirm-booking", json=confirm_data, headers=headers)
    if res.status_code != 201:
        print(f"❌ Booking confirmation failed: {res.text}")
        return
        
    booking = res.json()
    print(f"✅ Booking Confirmed! ID: {booking.get('booking_id')}")
    print(f"   Status: {booking.get('status')}")
    
if __name__ == "__main__":
    test_booking_flow()
