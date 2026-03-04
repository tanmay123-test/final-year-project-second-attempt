from housekeeping.models.database import housekeeping_db
from worker_db import WorkerDB

def verify_r71():
    print("--- Verifying Worker ID 39 (R71) ---")
    worker_db = WorkerDB()
    hk_db = housekeeping_db

    w = worker_db.get_worker_by_email('bugjoe025@gmail.com')
    if not w:
        print("Worker bugjoe025@gmail.com not found")
        return

    print(f"Worker Details: {w}")
    
    print(f"Checking bookings for Worker ID {w['id']}...")
    bookings = hk_db.get_worker_bookings(w['id'])
    if bookings:
        print(f"Bookings found: {len(bookings)}")
        for b in bookings:
            try:
                print(f" - ID: {b['id']}, Status: {b['status']}, Service: {b['service_type']}")
            except:
                 print(f" - {b}")
    else:
        print("No bookings found for this worker.")

if __name__ == "__main__":
    verify_r71()
