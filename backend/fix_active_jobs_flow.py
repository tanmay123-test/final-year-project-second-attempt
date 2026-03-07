#!/usr/bin/env python3
"""
Fix the active jobs flow by moving accepted jobs to active_jobs table
"""

import sqlite3
import os
from datetime import datetime

print("🔧 Fixing Active Jobs Flow...")

# Database paths
booking_db_path = os.path.join(os.path.dirname(__file__), 'data', 'car_jobs.db')
active_jobs_db_path = os.path.join(os.path.dirname(__file__), 'car_service', 'job_requests.db')

print(f"📁 Booking DB: {booking_db_path}")
print(f"📁 Active Jobs DB: {active_jobs_db_path}")

# Connect to both databases
booking_conn = sqlite3.connect(booking_db_path)
active_conn = sqlite3.connect(active_jobs_db_path)

# Get accepted jobs that aren't in active_jobs yet
booking_cursor = booking_conn.cursor()
active_cursor = active_conn.cursor()

print("\n🔍 Checking for accepted jobs not in active_jobs...")

# Get job ID 2 (the one Tanmay accepted)
booking_cursor.execute("""
    SELECT id, user_id, mechanic_id, issue, estimated_cost, status, created_at, accepted_at
    FROM mechanic_jobs 
    WHERE id = 2 AND status = 'ACCEPTED'
""")
accepted_job = booking_cursor.fetchone()

if accepted_job:
    job_id, user_id, mechanic_id, issue, estimated_cost, status, created_at, accepted_at = accepted_job
    print(f"✅ Found accepted job: {job_id}")
    print(f"   User ID: {user_id}")
    print(f"   Mechanic ID: {mechanic_id}")
    print(f"   Issue: {issue}")
    print(f"   Status: {status}")
    
    # Check if already in active_jobs
    active_cursor.execute("""
        SELECT id FROM active_jobs 
        WHERE mechanic_id = ? AND job_request_id = ?
    """, (mechanic_id, job_id))
    existing_active = active_cursor.fetchone()
    
    if not existing_active:
        print(f"📝 Moving job to active_jobs table...")
        
        # Insert into active_jobs table
        active_cursor.execute("""
            INSERT INTO active_jobs (
                job_request_id, user_id, mechanic_id, status, created_at
            ) VALUES (?, ?, ?, 'ARRIVING', ?)
        """, (job_id, user_id, mechanic_id, datetime.now().isoformat()))
        
        active_conn.commit()
        print(f"✅ Job {job_id} moved to active_jobs!")
        
        # Also need to create a job_requests entry for the active job
        active_cursor.execute("""
            INSERT INTO job_requests (
                user_id, mechanic_id, issue, issue_type, car_model, estimated_earning, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, mechanic_id, issue, 'GENERAL', 'Unknown Car', estimated_cost, 'ACCEPTED', created_at
        ))
        
        active_conn.commit()
        print(f"✅ Job request entry created!")
        
    else:
        print(f"ℹ️ Job {job_id} already in active_jobs table")
        
else:
    print("❌ Job ID 2 not found in booking database")

# Close connections
booking_conn.close()
active_conn.close()

print("\n🎯 Fix Applied!")
print("💡 Now Active Jobs section should show the accepted job")
