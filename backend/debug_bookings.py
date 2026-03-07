
import sqlite3
from services.housekeeping.models.database import HousekeepingDatabase

def check_latest_bookings():
    db = HousekeepingDatabase()
    conn = db.get_conn()
    cursor = conn.cursor()
    
    print("\n--- Latest 5 Bookings ---")
    cursor.execute("""
        SELECT id, user_id, worker_id, service_type, status, booking_date, time_slot, created_at 
        FROM bookings 
        ORDER BY id DESC 
        LIMIT 5
    """)
    rows = cursor.fetchall()
    
    if not rows:
        print("No bookings found.")
    
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"  User ID: {row[1]}")
        print(f"  Worker ID: {row[2]}")
        print(f"  Service: {row[3]}")
        print(f"  Status: {row[4]}")
        print(f"  Date/Time: {row[5]} {row[6]}")
        print(f"  Created: {row[7]}")
        print("-" * 30)

    print("\n--- Worker Status Check ---")
    # Check if worker 39 (R71 from previous turn) or others are online
    cursor.execute("SELECT * FROM worker_status ORDER BY last_updated DESC LIMIT 5")
    w_rows = cursor.fetchall()
    for w in w_rows:
         print(f"Worker {w[0]}: Online={w[1]}, LastUpdated={w[2]}")

    conn.close()

if __name__ == "__main__":
    check_latest_bookings()
