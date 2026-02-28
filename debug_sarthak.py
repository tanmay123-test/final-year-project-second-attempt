
import sys
import os
import sqlite3

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from worker_db import WorkerDB
from housekeeping.services.booking_service import BookingService
from housekeeping.models.database import housekeeping_db

def debug_sarthak():
    print("=== Debugging Sarthak ===")
    
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
        print("❌ Sarthak not found in WorkerDB")
        return
        
    print(f"✅ Found Sarthak: ID={sarthak['id']}, Name={sarthak['full_name']}")
    print(f"   Specialization (Raw): '{sarthak['specialization']}'")
    
    # 2. Check Services Table
    h_db = housekeeping_db
    conn = h_db.get_conn()
    services = conn.execute("SELECT name FROM services").fetchall()
    service_names = [s[0] for s in services]
    print(f"✅ Available Services in DB: {service_names}")
    conn.close()
    
    # 3. Test get_service_types
    bs = BookingService()
    filtered_services = bs.get_service_types(worker_id=sarthak['id'])
    print(f"✅ get_service_types returned {len(filtered_services)} services:")
    for s in filtered_services:
        print(f"   - {s['name']}")
        
    # 4. Check Bookings for Sarthak
    print("\n=== Checking Bookings ===")
    bookings = bs.db.get_worker_bookings(sarthak['id'])
    print(f"Found {len(bookings)} bookings for Sarthak")
    for b in bookings:
        print(f"   - ID: {b['id']}, Service: {b['service_type']}, Status: {b['status']}, Date: {b['booking_date']}, Time: {b['time_slot']}")

if __name__ == "__main__":
    debug_sarthak()
