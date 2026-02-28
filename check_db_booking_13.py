import sqlite3
import os

# Use the absolute path to DB
DB_PATH = r"d:\cdata13-04-2023\Downloads\ExpertEase\ExpertEase\data\housekeeping.db"

try:
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bookings WHERE id=13')
        row = cursor.fetchone()
        
        if row:
            print(f"Booking 13 found:")
            for key in row.keys():
                print(f"{key}: {row[key]}")
        else:
            print("Booking 13 not found")
        
        conn.close()
except Exception as e:
    print(f"Error: {e}")