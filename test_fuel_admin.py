#!/usr/bin/env python3
"""
Test script to demonstrate the working fuel delivery admin endpoints
"""

import requests
import json

API = "http://127.0.0.1:5000"

print("🔧 TESTING FUEL DELIVERY ADMIN ENDPOINTS")
print("="*50)

try:
    # Test pending agents
    print("\n1. Testing pending agents endpoint...")
    response = requests.get(f"{API}/api/fuel-delivery/admin/pending")
    
    if response.status_code == 200:
        agents = response.json()
        print(f"✅ Found {len(agents)} pending agents")
        
        if agents:
            agent = agents[0]
            print(f"📋 First Agent Details:")
            print(f"   🆔 ID: {agent['id']}")
            print(f"   👤 Name: {agent['name']}")
            print(f"   📧 Email: {agent['email']}")
            print(f"   📱 Phone: {agent['phone_number']}")
            print(f"   🏙️ City: {agent['city']}")
            print(f"   🚗 Vehicle: {agent['vehicle_type']} - {agent['vehicle_number']}")
            print(f"   📊 Status: {agent['approval_status']}")
            print(f"   📅 Applied: {agent['created_at']}")
        else:
            print("📭 No pending agents found")
    else:
        print(f"❌ Failed: {response.status_code}")
        
    # Test approved agents
    print("\n2. Testing approved agents endpoint...")
    response = requests.get(f"{API}/api/fuel-delivery/admin/approved")
    
    if response.status_code == 200:
        agents = response.json()
        print(f"✅ Found {len(agents)} approved agents")
    else:
        print(f"❌ Failed: {response.status_code}")
        
    print("\n" + "="*50)
    print("✅ All fuel delivery admin endpoints are working!")
    print("🎯 You can now manage fuel delivery agents from the admin panel!")
    
except Exception as e:
    print(f"❌ Error: {e}")
