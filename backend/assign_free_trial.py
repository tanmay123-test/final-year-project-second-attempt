#!/usr/bin/env python3

import requests
import sys

API = "http://127.0.0.1:5000"

def assign_free_trial_to_existing_workers():
    """Assign free trial to existing approved workers"""
    
    print("🎁 ASSIGNING FREE TRIALS TO EXISTING WORKERS")
    print("="*60)
    
    # Get all workers (you may need to adjust this based on your API)
    try:
        # For now, let's manually assign to worker ID 4 (the one we tested with)
        worker_id = 4
        
        print(f"📝 Assigning free trial to worker {worker_id}...")
        
        r = requests.post(f"{API}/api/subscription/assign-trial/{worker_id}")
        
        if r.status_code == 200:
            result = r.json()
            if result['success']:
                print("✅ Free trial assigned successfully!")
                subscription = result['subscription']
                print(f"   Plan: {subscription['plan_name']}")
                print(f"   End Date: {subscription['end_date'][:10] if subscription['end_date'] else 'N/A'}")
                print(f"   Daily Limit: {subscription['daily_appointment_limit']}")
            else:
                print(f"❌ Failed to assign trial: {result['message']}")
        else:
            print(f"❌ API call failed: {r.status_code}")
            print(r.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Free trial assignment completed!")

if __name__ == "__main__":
    assign_free_trial_to_existing_workers()
