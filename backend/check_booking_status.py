import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'data', 'housekeeping.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

print(f"Checking bookings for Worker 8 in {db_path}")
c.execute("SELECT id, status, service_type, booking_date, time_slot FROM bookings WHERE worker_id=8")
rows = c.fetchall()

print(f"Found {len(rows)} bookings:")
for row in rows:
    print(f"ID: {row[0]}, Status: {row[1]}, Service: {row[2]}, Date: {row[3]}, Time: {row[4]}")

conn.close()
