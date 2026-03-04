
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from housekeeping.services.booking_service import BookingService
from housekeeping.models.database import housekeeping_db
from worker_db import WorkerDB

def verify_goat_booking():
    service = BookingService()
    worker_db = WorkerDB()
    
    # 1. Get Goat Worker
    worker_id = 22
    worker = worker_db.get_worker_by_id(worker_id)
    if not worker:
        print("❌ Worker 22 not found!")
        return

    print(f"✅ Found Worker: {worker['name']} (ID: {worker['id']})")
    
    # Ensure online
    is_online = housekeeping_db.get_worker_online_status(worker_id)
    if not is_online:
        print("⚠️ Worker is offline. Setting to online for test...")
        housekeeping_db.set_worker_online(worker_id, True)
    
    # 2. Create Booking Request
    print("\nCreating Booking Request for Goat Worker...")
    user_id = 1 # Assume User 1 exists
    booking_data = {
        "user_id": user_id,
        "service_type": "Housekeeping", # Assuming this matches service specialization
        "address": "Test Address for Goat",
        "date": "2026-03-01",
        "time": "10:00 AM",
        "worker_id": worker_id,
        "booking_type": "schedule"
    }
    
    # Note: We need to bypass the 'check_availability' if slots are not set up, 
    # but create_booking_request calls check_availability internally for 'schedule'.
    # Let's try 'instant' to bypass slot check, but requires online status.
    # Or 'schedule' and hope availability logic allows it if we force it?
    # Actually, create_booking_request with worker_id checks slots for 'schedule'.
    
    # Let's mock availability or use 'instant' (since we set online).
    booking_data['booking_type'] = 'instant'
    
    result = service.create_booking_request(**booking_data)
    
    if result.get('error'):
        print(f"❌ Booking Creation Failed: {result['error']}")
        # If failed due to "Worker is not available", it might be because of existing bookings or logic.
        return

    booking_id = result['booking_id']
    print(f"✅ Booking Created! ID: {booking_id}, Status: {result['status']}")
    
    # 3. Verify Worker Dashboard Visibility
    # Dashboard queries: SELECT * FROM bookings WHERE worker_id = ? ORDER BY booking_date DESC
    # And filters in JS: b.status === 'ASSIGNED' || b.status === 'REQUESTED'
    
    worker_bookings = housekeeping_db.get_worker_bookings(worker_id)
    target_booking = next((b for b in worker_bookings if b['id'] == booking_id), None)
    
    if target_booking:
        print(f"✅ Booking visible in Worker DB. Status: {target_booking['status']}")
        if target_booking['status'] in ['ASSIGNED', 'REQUESTED']:
            print("✅ Booking should be visible on Dashboard (matches filter)")
        else:
            print(f"⚠️ Booking status {target_booking['status']} might be hidden on Dashboard")
    else:
        print("❌ Booking NOT found in Worker DB query")
        
    # 4. Simulate Accept
    print("\nSimulating Worker Accept...")
    success, msg, new_status = service.update_booking_status_by_worker(booking_id, worker_id, 'ACCEPTED')
    
    if success:
        print(f"✅ Worker Accepted Successfully! Message: {msg}")
        print(f"✅ New Status: {new_status}")
    else:
        print(f"❌ Worker Accept Failed: {msg}")

    # 5. Clean up (Optional, or leave it for manual inspection)
    # housekeeping_db.update_booking_status(booking_id, 'CANCELLED')

if __name__ == "__main__":
    verify_goat_booking()
