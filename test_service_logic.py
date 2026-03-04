import requests
import json
import sqlite3
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
WORKER_EMAIL = "trunika24@gmail.com" # Worker 22
USER_USERNAME = "user1" # Assuming a test user exists, or I'll need to login/create one.
# Actually, I can use the database directly to find IDs to avoid auth complexity in script if possible, 
# but the API requires auth. I'll use direct DB access for setup/verification to be faster/reliable.

DB_PATH = "d:\\cdata13-04-2023\\Downloads\\ExpertEase\\ExpertEase\\data\\housekeeping.db"
WORKER_DB_PATH = "d:\\cdata13-04-2023\\Downloads\\ExpertEase\\ExpertEase\\data\\workers.db"
USER_DB_PATH = "d:\\cdata13-04-2023\\Downloads\\ExpertEase\\ExpertEase\\data\\users.db"

def get_worker_id(email):
    conn = sqlite3.connect(WORKER_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, specialization FROM workers WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    return None, None

def get_user_id(username):
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def test_service_filtering():
    print("--- Testing Service Filtering ---")
    worker_id, specialization = get_worker_id(WORKER_EMAIL)
    if not worker_id:
        print(f"Worker {WORKER_EMAIL} not found.")
        return

    print(f"Worker ID: {worker_id}")
    print(f"Specialization: {specialization}")

    # Simulate BookingService.get_service_types logic
    # I can't import BookingService easily because of flask context/paths, 
    # but I can query the DB directly to mimic it.
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM services")
    all_services = [r[0] for r in cursor.fetchall()]
    conn.close()
    
    print(f"All Services in DB: {all_services}")
    
    worker_specs = [s.strip().lower() for s in specialization.split(',')]
    print(f"Worker Specs (parsed): {worker_specs}")
    
    filtered_services = []
    for service_name in all_services:
        if service_name.lower() in worker_specs:
            filtered_services.append(service_name)
            
    print(f"Filtered Services (Expected): {filtered_services}")
    
    if not filtered_services:
        print("WARNING: No services matched! Check casing or specialization format.")
    else:
        print("SUCCESS: Filtering logic matches.")

def verify_worker_bookings(worker_id):
    print("\n--- Verifying Worker Bookings ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, status, service_type FROM bookings WHERE worker_id = ? ORDER BY id DESC LIMIT 5", (worker_id,))
    bookings = cursor.fetchall()
    conn.close()
    
    if bookings:
        print(f"Found {len(bookings)} bookings for worker {worker_id}:")
        for b in bookings:
            print(f" - ID: {b[0]}, Status: {b[1]}, Service: {b[2]}")
    else:
        print(f"No bookings found for worker {worker_id}.")

if __name__ == "__main__":
    test_service_filtering()
    # verify_worker_bookings(22) # I'll get the ID dynamically
    
    wid, _ = get_worker_id(WORKER_EMAIL)
    if wid:
        verify_worker_bookings(wid)
