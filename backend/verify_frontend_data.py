
import requests
import json
import sys
import os

# Since we can't make actual HTTP requests to the running server easily without it running,
# we will simulate the backend call by importing the service.
# This is what the controller does.

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from services.housekeeping.services.booking_service import BookingService

def verify_data_structure():
    print("=== Verifying Backend Data Structure ===")
    bs = BookingService()
    workers = bs.get_top_cleaners()
    
    if not workers:
        print("❌ No workers found!")
        return
        
    print(f"✅ Found {len(workers)} workers.")
    first_worker = workers[0]
    print("Sample Worker Data Keys:", first_worker.keys())
    print("Sample Worker Data:", first_worker)
    
    if 'id' not in first_worker:
        print("❌ 'id' field MISSING in worker data!")
    else:
        print(f"✅ 'id' field present: {first_worker['id']}")
        
    # Check Sarthak specifically
    sarthak = next((w for w in workers if 'sarthak' in w['name'].lower()), None)
    if sarthak:
        print("\nSarthak Data:")
        print(sarthak)
        if 'id' in sarthak:
            print(f"✅ Sarthak ID: {sarthak['id']}")
        else:
            print("❌ Sarthak ID MISSING")
    else:
        print("\n❌ Sarthak not found in top_cleaners")

if __name__ == "__main__":
    verify_data_structure()
