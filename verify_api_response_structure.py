import requests
import json
import os
import sys
from auth_utils import generate_token

# Use the correct worker ID for "Worker 8"
WORKER_ID = 8
WORKER_EMAIL = "worker_8@example.com"

def get_worker_token(worker_id, email):
    # auth_utils.generate_token expects a string (username/email), not a dict payload
    return generate_token(email)

def verify_response_structure():
    token = get_worker_token(WORKER_ID, WORKER_EMAIL)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = "http://127.0.0.1:5000/api/housekeeping/my-bookings"
    
    print(f"🔍 Requesting: {url}")
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            bookings = data.get("bookings", [])
            print(f"✅ Success! Found {len(bookings)} bookings.")
            
            if bookings:
                print("\n🔍 First Booking Structure:")
                first_booking = bookings[0]
                print(json.dumps(first_booking, indent=4))
                
                # Check critical fields
                status = first_booking.get('status', '').upper()
                service_type = first_booking.get('service_type')
                booking_date = first_booking.get('booking_date')
                time_slot = first_booking.get('time_slot')
                
                print("\n🔍 Critical Field Check:")
                print(f"   - Status: '{status}' (Expected: ASSIGNED or REQUESTED)")
                print(f"   - Service Type: '{service_type}'")
                print(f"   - Booking Date: '{booking_date}'")
                print(f"   - Time Slot: '{time_slot}'")
                
                if status in ['ASSIGNED', 'REQUESTED']:
                    print("✅ Status matches filter criteria.")
                else:
                    print("❌ Status does NOT match filter criteria!")
            else:
                print("⚠️ No bookings found to inspect.")
                
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    verify_response_structure()
