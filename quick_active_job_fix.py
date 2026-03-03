#!/usr/bin/env python3
"""
Quick fix for active jobs - move accepted job to active_jobs table
"""

import sqlite3
import os
from datetime import datetime

print("🔧 Quick Active Job Fix...")

# Database paths
booking_db_path = os.path.join(os.path.dirname(__file__), 'data', 'car_jobs.db')
active_jobs_db_path = os.path.join(os.path.dirname(__file__), 'car_service', 'job_requests.db')

try:
    # Connect to databases
    booking_conn = sqlite3.connect(booking_db_path)
    active_conn = sqlite3.connect(active_jobs_db_path)
    
    # Get Tanmay's accepted job (ID 2)
    booking_cursor = booking_conn.cursor()
    booking_cursor.execute("SELECT * FROM mechanic_jobs WHERE id = 2 AND status = 'ACCEPTED'")
    accepted_job = booking_cursor.fetchone()
    
    if accepted_job:
        print(f"✅ Found accepted job: {accepted_job[0]}")
        print(f"   User ID: {accepted_job[1]}")
        print(f"   Mechanic ID: {accepted_job[2]}")
        print(f"   Issue: {accepted_job[4]}")
        
        # Get Tanmay's location from smart_search_db
        location_cursor = active_conn.cursor()
        location_cursor.execute("SELECT latitude, longitude FROM mechanic_live_locations WHERE mechanic_id = 2")
        location_data = location_cursor.fetchone()
        
        if location_data:
            mechanic_lat, mechanic_long = location_data[0], location_data[1]
            print(f"   Mechanic location: {mechanic_lat}, {mechanic_long}")
        
        # Create job_requests entry first
        active_cursor.execute("""
            INSERT INTO job_requests (
                user_id, mechanic_id, issue, issue_type, car_model, estimated_earning, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            accepted_job[1], accepted_job[2], accepted_job[4], 'Unknown Car', accepted_job[12], 'ACCEPTED', accepted_job[6]
        ))
        
        # Get the job_request_id we just created
        job_request_id = active_cursor.lastrowid
        active_conn.commit()
        print(f"✅ Job request entry created with ID: {job_request_id}")
        
        # Now insert into active_jobs with the job_request_id
        active_cursor.execute("""
            INSERT OR IGNORE INTO active_jobs (
                job_request_id, user_id, mechanic_id, status, created_at
            ) VALUES (?, ?, ?, ?, ?)
        """, (job_request_id, accepted_job[1], accepted_job[2], 'ARRIVING', datetime.now().isoformat()))
        
        active_conn.commit()
        print(f"✅ Job {accepted_job[0]} moved to active_jobs!")
        
        print(f"\n🎯 ACTIVE JOB FIX APPLIED!")
        print(f"💡 Job ID 2 should now appear in Active Jobs section")
        print(f"📱 Status: ARRIVING")
        print(f"🔍 Check: Mechanic Dashboard → Active Jobs")
        
    else:
        print("❌ Job ID 2 not found in booking database")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Close connections
    booking_conn.close()
    active_conn.close()

print("\n✅ Quick fix completed!")
