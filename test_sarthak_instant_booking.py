
import sys
import os
import json
import sqlite3
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from app import app
from housekeeping.services.booking_service import BookingService
from worker_db import WorkerDB
from user_db import UserDB
from auth_utils import generate_token

def test_sarthak_instant_booking():
    print("=== Testing Sarthak Instant Booking Flow ===\n")
    
    with app.app_context():
        booking_service = BookingService()
        worker_db = WorkerDB()
        user_db = UserDB()
        
        # 1. Find Sarthak
        print("1. Finding Sarthak...")
        sarthak = worker_db.get_worker_by_email("sarthak@gmail.com") # Assuming email from memory/context
        if not sarthak:
            # Try to find by name if email not exact
            conn = worker_db.get_conn()
            c = conn.cursor()
            c.execute("SELECT * FROM workers WHERE name LIKE '%Sarthak%'")
            sarthak_data = c.fetchone()
            conn.close()
            if sarthak_data:
                sarthak = worker_db.get_worker_by_id(sarthak_data[0])
            
        if not sarthak:
            print("❌ Sarthak not found!")
            return
            
        print(f"✅ Found Sarthak: ID={sarthak['id']}, Email={sarthak['email']}")
        print(f"   Specialization: {sarthak['specialization']}")
        
        # 2. Ensure Sarthak is Online
        print("\n2. Checking Online Status...")
        is_online = booking_service.db.get_worker_online_status(sarthak['id'])
        print(f"   Current Status: {'Online' if is_online else 'Offline'}")
        
        if not is_online:
            print("   Setting Sarthak to Online...")
            booking_service.db.set_worker_online(sarthak['id'], True)
            print("   ✅ Sarthak is now Online")
            
        # 3. Create a Test User
        print("\n3. Setting up Test User...")
        user_email = "test_user_sarthak_flow@example.com"
        user_id = user_db.get_user_by_username(user_email)
        if not user_id:
            user_db.create_user("Test User", user_email, "password123", user_email)
            user_id = user_db.get_user_by_username(user_email)
            print(f"   Created User ID: {user_id}")
        else:
            print(f"   Using existing User ID: {user_id}")
            
        user_token = generate_token(user_email)
        
        # 4. Check Availability (Instant)
        print("\n4. Checking Availability (Instant)...")
        client = app.test_client()
        
        # Service type must be one of Sarthak's
        service_type = "Bathroom Cleaning" 
        
        check_payload = {
            "service_type": service_type,
            "worker_id": sarthak['id'],
            "booking_type": "instant",
            "address": "Test Address 123",
            "date": datetime.now().strftime('%Y-%m-%d'),
            "time": datetime.now().strftime('%I:%M %p')
        }
        
        headers = {"Authorization": f"Bearer {user_token}"}
        
        res = client.post('/api/housekeeping/check-availability', 
                          data=json.dumps(check_payload),
                          headers=headers,
                          content_type='application/json')
        
        print(f"   Status Code: {res.status_code}")
        print(f"   Response: {res.json}")
        
        if res.status_code != 200:
            print("❌ Availability check failed!")
            return

        # 5. Confirm Booking (Instant)
        print("\n5. Confirming Booking (Instant)...")
        confirm_payload = check_payload.copy()
        confirm_payload['home_size'] = '2 BHK'
        confirm_payload['add_ons'] = "[]"
        
        res = client.post('/api/housekeeping/confirm-booking',  
                          data=json.dumps(confirm_payload),
                          headers=headers,
                          content_type='application/json')
        
        print(f"   Status Code: {res.status_code}")
        print(f"   Response: {res.json}")
        
        if res.status_code != 201:
            print("❌ Booking confirmation failed!")
            return
            
        booking_id = res.json['booking_id']
        print(f"   ✅ Booking Created! ID: {booking_id}")
        
        # 6. Check Worker Dashboard (My Bookings)
        print("\n6. Checking Worker Dashboard...")
        sarthak_token = generate_token(sarthak['email'])
        worker_headers = {"Authorization": f"Bearer {sarthak_token}"}
        
        res = client.get('/api/housekeeping/my-bookings', headers=worker_headers)
        
        print(f"   Status Code: {res.status_code}")
        bookings = res.json.get('bookings', [])
        print(f"   Found {len(bookings)} bookings")
        
        # Find our booking
        found = False
        for b in bookings:
            if b['id'] == booking_id:
                found = True
                print(f"   ✅ Found Booking {booking_id} in Worker Dashboard!")
                print(f"      Status: {b['status']}")
                print(f"      Worker ID: {b['worker_id']}")
                print(f"      Service: {b['service_type']}")
                
                if b['status'] not in ['REQUESTED', 'ASSIGNED']:
                    print(f"      ⚠️ WARNING: Status {b['status']} might not show up in pending requests!")
                break
        
        if not found:
            print(f"❌ Booking {booking_id} NOT found in Worker Dashboard!")

if __name__ == "__main__":
    test_sarthak_instant_booking()
