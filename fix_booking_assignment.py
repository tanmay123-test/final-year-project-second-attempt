#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'car_service'))

from booking_db import booking_db

# Update the existing booking to be assigned to mechanic 2 (Tanmay)
try:
    conn = booking_db.get_conn()
    cursor = conn.cursor()
    
    # Update the job to assign it to mechanic 2
    cursor.execute("UPDATE mechanic_jobs SET mechanic_id = 2 WHERE id = 1")
    conn.commit()
    
    # Verify the update
    cursor.execute("SELECT * FROM mechanic_jobs WHERE id = 1")
    job = cursor.fetchone()
    
    if job:
        print(f"Updated job ID 1:")
        print(f"User ID: {job[1]}")
        print(f"Mechanic ID: {job[2]}")
        print(f"Car ID: {job[3]}")
        print(f"Issue: {job[4]}")
        print(f"Status: {job[5]}")
    else:
        print("Job not found")
    
    conn.close()
    print("\nBooking assignment updated successfully!")
    
except Exception as e:
    print(f"Error: {e}")
