
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from housekeeping.services.booking_service import BookingService
from housekeeping.models.database import housekeeping_db

def test_sarthak_booking_flow():
    print("=== Testing Sarthak Booking Flow ===")
    bs = BookingService()
    
    # 1. Clean up previous test bookings for Sarthak
    conn = housekeeping_db.get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE worker_id = 38 AND address = 'TEST_ADDRESS_SARTHAK'")
    conn.commit()
    conn.close()
    
    # 2. Create Booking Request
    print("\n1. Creating Booking Request for Sarthak (ID: 38)...")
    result = bs.create_booking_request(
        user_id=1, # Assuming user 1 exists
        service_type="Bathroom Cleaning",
        address="TEST_ADDRESS_SARTHAK",
        date="2026-03-01",
        time="10:00 AM",
        worker_id=38, # Sarthak
        booking_type="schedule"
    )
    
    print("Result:", result)
    
    if result.get('status') == 'FAILED':
        print("❌ Booking Creation Failed:", result.get('error'))
        return
        
    booking_id = result['booking_id']
    print(f"✅ Booking Created! ID: {booking_id}")
    
    # 3. Verify Worker Bookings
    print("\n2. Verifying Worker Bookings...")
    worker_bookings = housekeeping_db.get_worker_bookings(38)
    
    found = False
    for b in worker_bookings:
        if b['id'] == booking_id:
            found = True
            print(f"✅ Found booking {booking_id} in worker bookings.")
            print(f"   Status: {b['status']}")
            print(f"   Service: {b['service_type']}")
            
            if b['status'] == 'REQUESTED':
                print("✅ Status is CORRECT (REQUESTED)")
            else:
                print(f"❌ Status is INCORRECT (Expected REQUESTED, got {b['status']})")
            break
            
    if not found:
        print("❌ Booking NOT found in worker bookings!")
        
    # 4. Verify Service Filtering (Double Check)
    print("\n3. Verifying Service Filtering...")
    services = bs.get_service_types(worker_id=38)
    service_names = [s['name'] for s in services]
    print(f"   Services for Sarthak: {service_names}")
    
    if "Bathroom Cleaning" in service_names and "Kitchen Cleaning" in service_names:
        if "Sofa Cleaning" not in service_names:
            print("✅ Service filtering looks correct (Only selected services shown)")
        else:
             print("❌ Service filtering FAILED (Unselected services shown)")
    else:
        print("❌ Service filtering FAILED (Selected services missing)")

if __name__ == "__main__":
    test_sarthak_booking_flow()
