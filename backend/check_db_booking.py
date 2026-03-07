import sqlite3
import os

try:
    conn = sqlite3.connect('housekeeping.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE id=10')
    row = cursor.fetchone()
    
    if row:
        # Get column names
        col_names = [description[0] for description in cursor.description]
        print(f"Columns: {col_names}")
        print(f"Booking 10: {row}")
    else:
        print("Booking 10 not found")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
