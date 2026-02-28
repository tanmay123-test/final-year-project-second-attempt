
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from housekeeping.services.booking_service import BookingService
from housekeeping.models.database import housekeeping_db
from worker_db import WorkerDB

def test_sarthak_backend():
    print("=== Testing Sarthak Backend Logic ===")
    
    # 1. Get Sarthak ID
    wdb = WorkerDB()
    worker = wdb.get_worker_by_email("sarthak@gmail.com")
    if not worker:
        print("ERROR: Sarthak not found")
        return
    
    sarthak_id = worker['id']
    print(f"Sarthak ID: {sarthak_id}")
    print(f"Sarthak Specialization: {worker['specialization']}")
    
    # 2. Test Service Filtering
    bs = BookingService()
    services = bs.get_service_types(worker_id=sarthak_id)
    print(f"\nFiltered Services for Sarthak (Should be Bathroom & Kitchen only):")
    service_names = [s['name'] for s in services]
    print(service_names)
    
    expected = ['Bathroom Cleaning', 'Kitchen Cleaning']
    # Note: DB might have them in different case or order, so we check existence
    passed_filtering = True
    for e in expected:
        if not any(s.lower() == e.lower() for s in service_names):
            print(f"MISSING: {e}")
            passed_filtering = False
            
    if 'General Cleaning' in service_names or 'Deep Cleaning' in service_names:
        print("ERROR: Unwanted services found!")
        passed_filtering = False
        
    if passed_filtering:
        print("SUCCESS: Service filtering works correctly.")
    else:
        print("FAILED: Service filtering is incorrect.")

    # 3. Test Booking Retrieval
    bookings = housekeeping_db.get_worker_bookings(sarthak_id)
    print(f"\nBookings for Sarthak (Count: {len(bookings)}):")
    for b in bookings:
        print(f"- ID: {b['id']}, Status: {b['status']}, Type: {b.get('booking_type')}, Service: {b['service_type']}")
        
    if len(bookings) > 0:
        print("SUCCESS: Bookings retrieved.")
    else:
        print("WARNING: No bookings found (Create some if needed).")

if __name__ == "__main__":
    test_sarthak_backend()
