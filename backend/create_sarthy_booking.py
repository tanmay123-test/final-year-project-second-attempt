#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'car_service'))

# Create a booking for Sarthy (user ID 6)
from booking_db import booking_db

try:
    # Create booking for Sarthy with mechanic 2 (Tanmay)
    job_id = booking_db.create_job(
        user_id=6,  # Sarthy's ID
        mechanic_id=2,  # Tanmay's ID  
        car_id=1,  # Use existing car
        issue="Engine not starting - need immediate help",
        estimated_cost=800
    )
    
    print(f"✅ Created booking for Sarthy (user 6)")
    print(f"   Job ID: {job_id}")
    print(f"   User: Sarthak Sawant (ID: 6)")
    print(f"   Mechanic: Tanmay (ID: 2)")
    print(f"   Issue: Engine not starting - need immediate help")
    print(f"   Status: SEARCHING")
    
    # Verify the booking
    jobs = booking_db.get_user_jobs(6)
    print(f"\n📋 Sarthy now has {len(jobs)} booking(s):")
    for job in jobs:
        print(f"   Job {job['id']}: {job['issue']} ({job['status']})")
        
except Exception as e:
    print(f"❌ Error creating booking: {e}")
    import traceback
    traceback.print_exc()
