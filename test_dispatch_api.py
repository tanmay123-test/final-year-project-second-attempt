#!/usr/bin/env python3
"""
Test Dispatch API
Simple test to verify dispatch system is working
"""

import requests
import json

def test_dispatch_api():
    """Test the dispatch API endpoints"""
    API = "http://127.0.0.1:5001"
    
    print("🧪 TESTING DISPATCH API")
    print("=" * 40)
    
    # Test 1: Create job request
    print("\n1. Testing Job Creation...")
    job_data = {
        "user_id": 1,
        "issue": "Brake failure - urgent repair needed",
        "service_type": "MECHANIC",
        "urgency": False,
        "location_name": "Asalpha"
    }
    
    try:
        response = requests.post(f"{API}/api/dispatch/job/create", json=job_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('job_id')
            print(f"✅ Job created successfully: {job_id}")
            
            # Test 2: Check job status
            print(f"\n2. Testing Job Status...")
            status_response = requests.get(f"{API}/api/dispatch/job/status/{job_id}")
            print(f"Status Code: {status_response.status_code}")
            print(f"Response: {status_response.json()}")
            
        else:
            print("❌ Job creation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_dispatch_api()
