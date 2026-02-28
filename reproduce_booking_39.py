import requests
import sqlite3
import sys
import os
import datetime
from auth_utils import generate_token

# Configuration
BASE_URL = "http://localhost:5000"
WORKER_ID = 39

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def reproduce_booking():
    print(f"=== Reproducing Booking for Worker {WORKER_ID} ===")
    
    # 1. Create a User Token
    token = generate_token("testuser_repro")
    if isinstance(token, bytes):
        token = token.decode('utf-8')
        
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. Create Booking Payload
    payload = {
        "service_type": "Bathroom Cleaning", # Matching the one in DB
        "address": "Test Address Repro",
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "time": "11:00 AM",
        "worker_id": WORKER_ID,
        "booking_type": "schedule" # Try schedule first
    }
    
    print(f"🚀 Sending booking request...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/housekeeping/confirm-booking",
            json=payload,
            headers=headers
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            booking_id = data.get('booking_id')
            status = data.get('status')
            print(f"✅ Booking Created! ID: {booking_id}")
            print(f"   Returned Status: {status}")
            
            # Verify in DB
            from housekeeping.models.database import HousekeepingDatabase
            hk_db = HousekeepingDatabase()
            booking = hk_db.get_booking_by_id(booking_id)
            print(f"   DB Status: {booking['status']}")
            
            if booking['status'] == 'ACCEPTED':
                print("🚨 ISSUE REPRODUCED: Booking created with ACCEPTED status!")
            else:
                print("✅ Booking created correctly with non-ACCEPTED status.")
                
        else:
            print(f"❌ Failed to create booking: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    reproduce_booking()
