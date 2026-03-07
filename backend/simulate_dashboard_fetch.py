import requests
import json
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from auth_utils import generate_token

def simulate_frontend_logic():
    # 1. Authenticate as Worker 8
    worker_email = "worker_8@example.com" # Verified email
    token = generate_token(worker_email)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    api_url = "http://127.0.0.1:5000/api/housekeeping/my-bookings"
    
    print(f"Fetching bookings from {api_url} for {worker_email}...")
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            print(f"Error: API returned {response.status_code}")
            print(response.text)
            return

        data = response.json()
        all_bookings = data.get('bookings', [])
        print(f"Total bookings received: {len(all_bookings)}")
        
        # 2. Replicate Frontend Filtering Logic
        # const pending = allBookings.filter(b => {
        #     const s = (b.status || '').toUpperCase();
        #     return s === 'ASSIGNED' || s === 'REQUESTED';
        # });
        
        pending = []
        for b in all_bookings:
            status = (b.get('status') or '').upper()
            if status == 'ASSIGNED' or status == 'REQUESTED':
                pending.append(b)
        
        print(f"Pending requests (filtered): {len(pending)}")
        
        # 3. Replicate Frontend Mapping Logic
        # const mappedRequests = pending.map(req => {
        #     let image = '🧹';
        #     const serviceType = req.service_type || req.service || 'General Cleaning';
        #     // ... image logic ...
        #     return {
        #         ...req,
        #         service: serviceType,
        #         image: image,
        #         date: req.booking_date || req.date,
        #         time: req.time_slot || req.time
        #     };
        # });
        
        mapped_requests = []
        for req in pending:
            service_type = req.get('service_type') or req.get('service') or 'General Cleaning'
            
            mapped_req = req.copy()
            mapped_req['service'] = service_type
            mapped_req['date'] = req.get('booking_date') or req.get('date')
            mapped_req['time'] = req.get('time_slot') or req.get('time')
            
            mapped_requests.append(mapped_req)
            
        print("\n--- Mapped Requests (What should be displayed) ---")
        for req in mapped_requests:
            print(f"ID: {req.get('id')}")
            print(f"  Service: {req.get('service')}")
            print(f"  Date: {req.get('date')}")
            print(f"  Time: {req.get('time')}")
            print(f"  Status: {req.get('status')}")
            print(f"  Price: {req.get('price')}")
            print("-" * 20)
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    simulate_frontend_logic()
