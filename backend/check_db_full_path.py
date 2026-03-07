import sqlite3
import os

# Use the relative path from where I run the script
DB_PATH = r"housekeeping/models/data/housekeeping.db"
# Or try to find it dynamically
if not os.path.exists(DB_PATH):
    # Try alternate location
    DB_PATH = r"data/housekeeping.db"

print(f"Checking DB at: {DB_PATH}")

try:
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bookings WHERE id=10')
        row = cursor.fetchone()
        
        if row:
            print(f"Booking 10 found:")
            for key in row.keys():
                print(f"{key}: {row[key]}")
        else:
            print("Booking 10 not found")
            
        conn.close()
except Exception as e:
    print(f"Error: {e}")
