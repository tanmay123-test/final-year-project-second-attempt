from services.housekeeping.models.database import housekeeping_db
from worker_db import WorkerDB
import sqlite3

def verify_bugjoe():
    print("--- Verifying 'Dr. bugjoe025' ---")
    worker_db = WorkerDB()
    hk_db = housekeeping_db

    conn = worker_db.get_conn()
    cursor = conn.cursor()
    # Search for workers with 'bugjoe' in name
    cursor.execute("SELECT id, full_name, email, service, specialization, status FROM workers WHERE full_name LIKE '%bugjoe%'")
    workers = cursor.fetchall()
    conn.close()

    if not workers:
        print("No worker found with name like 'bugjoe'")
        return

    for w in workers:
        w_id = w[0]
        w_name = w[1]
        w_email = w[2]
        w_service = w[3]
        w_spec = w[4]
        w_status = w[5]
        
        print(f"\nWorker Found: ID={w_id}, Name={w_name}, Email={w_email}, Service={w_service}, Specs={w_spec}, Status={w_status}")

        print(f"Checking bookings for Worker ID {w_id}...")
        bookings = hk_db.get_worker_bookings(w_id)
        if bookings:
            print(f"Bookings found: {len(bookings)}")
            for b in bookings:
                # b is likely a Row object or dict
                try:
                    b_id = b['id']
                    b_status = b['status']
                    b_service = b['service_type']
                    b_date = b['booking_date']
                    b_user = b['user_id']
                except:
                    # Fallback for tuple/row
                    b_id = b[0]
                    b_status = b[4] # Index might vary
                    b_service = b[2]
                    b_date = b[5]
                    b_user = b[1]
                
                print(f" - ID: {b_id}, Status: {b_status}, Service: {b_service}, Date: {b_date}, User: {b_user}")
        else:
            print("No bookings found for this worker.")

if __name__ == "__main__":
    verify_bugjoe()
