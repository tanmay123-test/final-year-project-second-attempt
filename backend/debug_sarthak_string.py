
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from worker_db import WorkerDB
from services.housekeeping.services.booking_service import BookingService

def debug_sarthak_string_id():
    print("=== Debugging Sarthak with String ID ===")
    
    # 1. Find Sarthak
    w_db = WorkerDB()
    workers = w_db.conn.execute("SELECT * FROM workers").fetchall()
    
    sarthak = None
    for w in workers:
        w_dict = w_db._row_to_dict(w)
        if 'sarthak' in w_dict['full_name'].lower() or 'sarthak' in w_dict.get('name', '').lower():
            sarthak = w_dict
            break
            
    if not sarthak:
        print("❌ Sarthak not found")
        return
        
    sarthak_id_str = str(sarthak['id'])
    print(f"Testing with ID: '{sarthak_id_str}' (type: {type(sarthak_id_str)})")
    
    # 2. Test get_service_types
    bs = BookingService()
    filtered_services = bs.get_service_types(worker_id=sarthak_id_str)
    print(f"✅ get_service_types returned {len(filtered_services)} services:")
    for s in filtered_services:
        print(f"   - {s['name']}")

if __name__ == "__main__":
    debug_sarthak_string_id()
