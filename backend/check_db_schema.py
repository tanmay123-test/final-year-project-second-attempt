import sqlite3
from services.housekeeping.models.database import HousekeepingDatabase

db = HousekeepingDatabase()
conn = db.get_conn()
cursor = conn.cursor()

print("--- Checking bookings table columns ---")
try:
    cursor.execute("PRAGMA table_info(bookings)")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
except Exception as e:
    print(f"Error: {e}")

conn.close()
