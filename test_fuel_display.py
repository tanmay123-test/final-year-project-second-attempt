#!/usr/bin/env python3
"""
Test script to verify the fixed fuel delivery admin display
"""

import requests
import json

API = "http://127.0.0.1:5000"

print("🔧 TESTING FIXED FUEL DELIVERY ADMIN DISPLAY")
print("="*50)

try:
    # Test pending agents display
    print("\n1. Testing pending agents display...")
    response = requests.get(f"{API}/api/fuel-delivery/admin/pending")
    
    if response.status_code == 200:
        agents = response.json()
        
        if agents:
            agent = agents[0]
            print(f"✅ Agent display test:")
            print(f"   🆔 ID: {agent['id']}")
            print(f"   👤 Name: {agent['name']}")
            print(f"   📧 Email: {agent['email']}")
            print(f"   📱 Phone: {agent['phone_number']}")
            print(f"   🏙️ City: {agent['city']}")
            print(f"   🚗 Vehicle: {agent['vehicle_type']} - {agent['vehicle_number']}")
            print(f"   📊 Status: {agent['approval_status']}")
            print(f"   📅 Applied: {agent['created_at']}")
            
            print("\n✅ All fields displayed correctly!")
            print("🎯 The phone field error should now be fixed!")
        else:
            print("📭 No pending agents found")
    else:
        print(f"❌ Failed: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
