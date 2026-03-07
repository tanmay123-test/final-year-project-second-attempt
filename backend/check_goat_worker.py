from worker_db import WorkerDB
from services.housekeeping.models.database import housekeeping_db

w_db = WorkerDB()
worker = w_db.get_worker_by_id(22)
print("Worker Details:")
print(worker)

print("\nOnline Status:")
is_online = housekeeping_db.get_worker_online_status(22)
print(f"Is Online: {is_online}")

print("\nBookings:")
bookings = housekeeping_db.get_worker_bookings(22)
print(f"Total Bookings: {len(bookings)}")
for b in bookings:
    print(b)
