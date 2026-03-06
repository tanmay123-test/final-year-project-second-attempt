#!/usr/bin/env python3
"""
Create sample fuel delivery requests for testing
"""

import requests
import json

API = "http://127.0.0.1:5000"

# Sample fuel delivery requests
sample_requests = [
    {
        "user_id": 1,
        "user_name": "Rahul Sharma",
        "user_phone": "9876543210",
        "fuel_type": "Petrol",
        "quantity": 5.0,
        "latitude": 19.0760,
        "longitude": 72.8777,
        "address": "Andheri East, Mumbai",
        "priority_level": 3
    },
    {
        "user_id": 2,
        "user_name": "Priya Patel",
        "user_phone": "9876543211",
        "fuel_type": "Diesel",
        "quantity": 25.0,
        "latitude": 19.0860,
        "longitude": 72.8877,
        "address": "Bandra West, Mumbai",
        "priority_level": 4
    },
    {
        "user_id": 3,
        "user_name": "Amit Kumar",
        "user_phone": "9876543212",
        "fuel_type": "Petrol",
        "quantity": 8.0,
        "latitude": 19.0960,
        "longitude": 72.8977,
        "address": "Worli, Mumbai",
        "priority_level": 2
    }
]

print("🔧 CREATING SAMPLE FUEL DELIVERY REQUESTS")
print("="*50)

for i, request in enumerate(sample_requests, 1):
    try:
        response = requests.post(f"{API}/api/fuel-delivery/create-request", json=request)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Request {i}: {request['fuel_type']} - {request['quantity']}L for {request['user_name']}")
            else:
                print(f"❌ Request {i} failed: {result.get('error')}")
        else:
            print(f"❌ Request {i} failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request {i} error: {e}")

print("\n" + "="*50)
print("✅ Sample requests created successfully!")
print("🎯 You can now test the fuel delivery agent queue system!")
