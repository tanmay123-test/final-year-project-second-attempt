import requests
import json
from worker_db import WorkerDB

BASE_URL = "http://127.0.0.1:5000"

def test_sarthak_issues():
    print("=== Testing Sarthak Issues ===\n")

    # 1. Get Sarthak's ID
    wdb = WorkerDB()
    w_conn = wdb.conn
    cursor = w_conn.cursor()
    cursor.execute("SELECT id, full_name, specialization FROM workers WHERE full_name LIKE '%Sarthak%'")
    sarthak = cursor.fetchone()
    
    if not sarthak:
        print("❌ Sarthak not found in DB")
        return
    
    sarthak_id = sarthak[0]
    print(f"Found Sarthak: ID={sarthak_id}, Spec={sarthak[2]}\n")

    # 2. Test Service Filtering (Backend API)
    print("--- Testing Service Filtering ---")
    try:
        # Simulate GET /api/housekeeping/services?worker_id=38
        # We need to construct the URL manually or use python requests if server is running.
        # Since I cannot assume server is running on port 5000 reachable from here, 
        # I will instantiate BookingService directly like in unit tests.
        
        from housekeeping.services.booking_service import BookingService
        bs = BookingService()
        
        services = bs.get_service_types(worker_id=sarthak_id)
        service_names = [s['name'] for s in services]
        print(f"Services returned for Sarthak: {service_names}")
        
        expected = ['Bathroom Cleaning', 'Kitchen Cleaning']
        # Check if ONLY expected services are present (case insensitive)
        returned_lower = [s.lower() for s in service_names]
        expected_lower = [s.lower() for s in expected]
        
        # Check for unwanted services
        unwanted = ['General Cleaning', 'Deep Cleaning']
        failed_filtering = False
        for u in unwanted:
            if u.lower() in returned_lower:
                print(f"❌ FAILED: Found unwanted service '{u}'")
                failed_filtering = True
        
        if not failed_filtering:
            print("✅ Service filtering PASSED (Unwanted services hidden)")
            
    except Exception as e:
        print(f"❌ Error testing filtering: {e}")

    # 3. Test Check Availability (Simulating Frontend Bug)
    print("\n--- Testing Check Availability (Frontend Bug Simulation) ---")
    try:
        # Frontend calls checkAvailability with empty date/time and DEFAULT booking_type='schedule'
        # when user clicks "Check Availability" for Instant Booking.
        
        # Calling check_availability(service_type, date, time, address, worker_id, booking_type='schedule')
        # date='', time=''
        
        available = bs.check_availability(
            service_type="Bathroom Cleaning",
            date="",
            time="",
            address="Test Address",
            worker_id=sarthak_id,
            booking_type="schedule" # Default
        )
        
        print(f"check_availability (date='', type='schedule') returned: {len(available)} workers")
        if len(available) == 0:
            print("⚠️ Result: 0 workers. This confirms the frontend bug causes '0 professionals available' display.")
            print("   However, the user can still proceed to confirm.")
        else:
            print("   Result: Found workers? Unexpected if date is empty.")

    except Exception as e:
        print(f"❌ Error testing availability: {e}")

    # 4. Test Booking Creation (Instant)
    print("\n--- Testing Booking Creation (Instant) ---")
    try:
        # User clicks Confirm. Frontend calls confirmBooking -> create_booking_request
        # booking_type='instant', date/time might be empty or None?
        # In confirmBooking frontend code: ...formData.
        # formData has date='', time=''.
        
        result = bs.create_booking_request(
            user_id=1,
            service_type="Bathroom Cleaning",
            address="Test Address Instant",
            date="", # Empty string from frontend
            time="", # Empty string from frontend
            worker_id=sarthak_id,
            booking_type="instant"
        )
        
        print(f"create_booking_request result: {result}")
        
        if result.get('status') == 'FAILED':
            print(f"❌ Booking Failed: {result.get('error')}")
        else:
            print(f"✅ Booking Created! ID: {result.get('booking_id')}")
            print(f"   Status: {result.get('status')}")
            
            # Check if it appears in worker bookings with REQUESTED status
            # We can check DB directly
            from housekeeping.models.database import housekeeping_db
            conn = housekeeping_db.get_conn()
            c = conn.cursor()
            c.execute("SELECT status FROM bookings WHERE id=?", (result.get('booking_id'),))
            status = c.fetchone()[0]
            print(f"   DB Status: {status}")
            conn.close()
            
            if status == 'REQUESTED':
                print("✅ Status is REQUESTED. Worker should see this.")
            else:
                print(f"❌ Status is {status}. Worker might NOT see this.")

    except Exception as e:
        print(f"❌ Error testing booking creation: {e}")

if __name__ == "__main__":
    test_sarthak_issues()
