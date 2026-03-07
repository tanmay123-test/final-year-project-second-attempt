import sqlite3
from services.housekeeping.models.database import HousekeepingDatabase

db = HousekeepingDatabase()
conn = db.get_conn()
cursor = conn.cursor()

print("--- Adding columns to bookings table ---")

columns_to_add = [
    ("home_size", "TEXT"),
    ("add_ons", "TEXT"),
    ("booking_type", "TEXT")
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE bookings ADD COLUMN {col_name} {col_type}")
        print(f"Added column {col_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print(f"Column {col_name} already exists")
        else:
            print(f"Error adding {col_name}: {e}")

conn.commit()
conn.close()
