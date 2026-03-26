#!/usr/bin/env python3
"""
Test script for worker profile API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.freelance.services.freelance_service import freelance_service

def test_worker_profile():
    """Test worker profile functionality"""
    print("🧪 Testing Worker Profile API...")
    
    try:
        # Test getting all workers first
        print("\n1. Testing get_workers_by_skills...")
        workers = freelance_service.get_workers_by_skills()
        print(f"✅ Found {len(workers)} workers")
        
        if workers:
            # Test getting a specific worker
            worker_id = workers[0]['id']
            print(f"\n2. Testing get_worker_by_id with ID: {worker_id}")
            
            worker = freelance_service.get_worker_by_id(worker_id)
            if worker:
                print("✅ Worker profile fetched successfully!")
                print(f"   • Name: {worker.get('full_name', 'N/A')}")
                print(f"   • Specialization: {worker.get('specialization', 'N/A')}")
                print(f"   • Skills: {worker.get('skills', 'N/A')}")
                print(f"   • Skills List: {worker.get('skills_list', [])}")
                print(f"   • Location: {worker.get('clinic_location', 'N/A')}")
                print(f"   • Hourly Rate: {worker.get('hourly_rate', 'N/A')}")
                return True
            else:
                print("❌ Failed to fetch worker profile")
                return False
        else:
            print("❌ No workers found to test with")
            return False
            
    except Exception as e:
        print(f"❌ Error testing worker profile: {e}")
        return False

if __name__ == "__main__":
    success = test_worker_profile()
    if success:
        print("\n🎉 Worker profile API is working!")
        print("\n📋 Testing Steps:")
        print("1. Go to /freelance/home?tab=find")
        print("2. Click on any freelancer name")
        print("3. Check the debug info on the profile page")
        print("4. Verify the name and skills are displayed correctly")
    else:
        print("\n❌ Worker profile API test failed")
        sys.exit(1)
