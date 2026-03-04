
import sqlite3
import os
from datetime import datetime
import sys

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
HOUSEKEEPING_DB = os.path.join(DATA_DIR, 'housekeeping.db')
WORKER_DB = os.path.join(DATA_DIR, 'workers.db')
USER_DB = os.path.join(DATA_DIR, 'users.db')

print(f"Using DB paths:\nHK: {HOUSEKEEPING_DB}\nWorker: {WORKER_DB}")

def setup_databases():
    # Ensure Sarthak exists and is online
    conn = sqlite3.connect(WORKER_DB)
    cursor = conn.cursor()
    
    # Check if Sarthak exists
    cursor.execute("SELECT id, email, specialization FROM workers WHERE full_name LIKE '%Sarthak%'")
    sarthak = cursor.fetchone()
    
    if not sarthak:
        print("Creating Sarthak worker...")
        cursor.execute("""
            INSERT INTO workers (full_name, email, password, service, specialization, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('Sarthak', 'sarthak@example.com', 'password123', 'housekeeping', 'Bathroom Cleaning,Kitchen Cleaning', 'approved'))
        worker_id = cursor.lastrowid
        conn.commit()
    else:
        worker_id = sarthak[0]
        print(f"Found Sarthak (ID: {worker_id})")
        print(f"Specialization: {sarthak[2]}")
    
    conn.close()
    
    # Set online status
    conn = sqlite3.connect(HOUSEKEEPING_DB)
    cursor = conn.cursor()
    # Check if worker_status table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='worker_status'")
    if not cursor.fetchone():
        print("Creating worker_status table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS worker_status (
            worker_id INTEGER PRIMARY KEY,
            is_online INTEGER DEFAULT 0,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
    cursor.execute("INSERT OR REPLACE INTO worker_status (worker_id, is_online, last_updated) VALUES (?, 1, CURRENT_TIMESTAMP)", (worker_id,))
    conn.commit()
    conn.close()
    
    return worker_id

def create_booking_simulation(worker_id):
    # Simulate the logic in create_booking_request
    conn = sqlite3.connect(HOUSEKEEPING_DB)
    cursor = conn.cursor()
    
    user_id = 999 # Test user
    service_type = 'Bathroom Cleaning'
    date = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%I:%M %p')
    
    print(f"Attempting to book Sarthak (ID: {worker_id}) for {service_type} at {time}...")
    
    # Check for existing conflict first
    cursor.execute("""
        SELECT id, status FROM bookings 
        WHERE worker_id = ? AND booking_date = ? AND time_slot = ? 
        AND status IN ('ACCEPTED', 'IN_PROGRESS', 'ASSIGNED', 'REQUESTED')
    """, (worker_id, date, time))
    conflict = cursor.fetchone()
    
    booking_id = None
    if conflict:
        print(f"CONFLICT FOUND! Booking ID: {conflict[0]}, Status: {conflict[1]}")
        # Create a new slot to avoid conflict for testing
        time = datetime.now().strftime('%I:%M:%S %p') # Use seconds to make unique
        print(f"Trying new time: {time}")
    
    print("Proceeding to create booking...")
    try:
        cursor.execute("""
            INSERT INTO bookings (user_id, service_type, address, booking_date, time_slot, price, status, worker_id, booking_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, service_type, '123 Test St', date, time, 500, 'REQUESTED', worker_id, 'instant'))
        booking_id = cursor.lastrowid
        conn.commit()
        print(f"Booking created! ID: {booking_id}")
    except Exception as e:
        print(f"Error inserting booking: {e}")
        
    conn.close()
    return booking_id

def check_worker_bookings(worker_id):
    conn = sqlite3.connect(HOUSEKEEPING_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, status, service_type, booking_type, worker_id FROM bookings WHERE worker_id = ?", (worker_id,))
    bookings = cursor.fetchall()
    conn.close()
    
    print(f"\nBookings for Sarthak (ID: {worker_id}):")
    found_requested = False
    for b in bookings:
        print(f"- ID: {b[0]}, Status: {b[1]}, Service: {b[2]}, Type: {b[3]}, WorkerID: {b[4]}")
        if b[1] == 'REQUESTED':
            found_requested = True
            
    if found_requested:
        print("\nSUCCESS: Found 'REQUESTED' booking for Sarthak.")
    else:
        print("\nFAILURE: No 'REQUESTED' booking found for Sarthak.")

if __name__ == "__main__":
    try:
        worker_id = setup_databases()
        create_booking_simulation(worker_id)
        check_worker_bookings(worker_id)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
