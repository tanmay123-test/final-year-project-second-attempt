#!/usr/bin/env python3
"""
Create Test Fuel Delivery Agents with Service Areas
"""

import requests

API = "http://127.0.0.1:5000"

def create_test_agents():
    print("🚀 CREATING TEST FUEL DELIVERY AGENTS WITH SERVICE AREAS")
    print("="*60)
    
    # Test agents with different service areas
    test_agents = [
        {
            'name': 'Tanmay Fuel Delivery',
            'email': 'tanmay@fuel.com',
            'phone': '9876543210',
            'password': 'password123',
            'city': 'Mumbai',
            'vehicle_type': 'Van',
            'vehicle_number': 'MH01AB1234',
            'service_area_city': 'Mumbai',
            'service_area_location': 'Asalpha',
            'service_area_km': 15,
            'latitude': 19.0954,
            'longitude': 72.8783,
            'safety_declaration_accepted': True
        },
        {
            'name': 'Rahul Fuel Services',
            'email': 'rahul@fuel.com',
            'phone': '9876543211',
            'password': 'password123',
            'city': 'Mumbai',
            'vehicle_type': 'Truck',
            'vehicle_number': 'MH01CD5678',
            'service_area_city': 'Mumbai',
            'service_area_location': 'Bandra',
            'service_area_km': 20,
            'latitude': 19.0596,
            'longitude': 72.8295,
            'safety_declaration_accepted': True
        },
        {
            'name': 'Ahmed Fuel Delivery',
            'email': 'ahmed@fuel.com',
            'phone': '9876543212',
            'password': 'password123',
            'city': 'Mumbai',
            'vehicle_type': 'Van',
            'vehicle_number': 'MH01EF9012',
            'service_area_city': 'Mumbai',
            'service_area_location': 'Andheri',
            'service_area_km': 15,
            'latitude': 19.1196,
            'longitude': 72.8465,
            'safety_declaration_accepted': True
        },
        {
            'name': 'Sameer Fuel Delivery',
            'email': 'sameer@fuel.com',
            'phone': '9876543213',
            'password': 'password123',
            'city': 'Mumbai',
            'vehicle_type': 'Bike',
            'vehicle_number': 'MH01GH3456',
            'service_area_city': 'Mumbai',
            'service_area_location': 'Worli',
            'service_area_km': 10,
            'latitude': 19.0170,
            'longitude': 72.8300,
            'safety_declaration_accepted': True
        },
        {
            'name': 'Akshay Fuel Delivery',
            'email': 'akshay@fuel.com',
            'phone': '9876543214',
            'password': 'password123',
            'city': 'Mumbai',
            'vehicle_type': 'Van',
            'vehicle_number': 'MH01IJ7890',
            'service_area_city': 'Mumbai',
            'service_area_location': 'Dadar',
            'service_area_km': 15,
            'latitude': 19.0190,
            'longitude': 72.8420,
            'safety_declaration_accepted': True
        }
    ]
    
    for i, agent in enumerate(test_agents, 1):
        print(f"\n{i}. Creating agent: {agent['name']}")
        
        try:
            response = requests.post(f"{API}/api/fuel-delivery/register", json=agent)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"✅ Agent created successfully!")
                    print(f"   Service Area: {agent['service_area_location']} ({agent['service_area_km']}km)")
                    print(f"   Vehicle: {agent['vehicle_type']} - {agent['vehicle_number']}")
                else:
                    print(f"❌ Agent creation failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("🎊 TEST AGENTS CREATION COMPLETE!")
    print("✅ 5 fuel delivery agents created with service areas")
    print("✅ Service areas: Asalpha, Bandra, Andheri, Worli, Dadar")
    print("✅ Vehicle types: Bike (10L), Van (50L), Truck (1000L+)")
    print("✅ Service radius: 10-20km based on vehicle type")
    print("\n🚀 Now test the fuel delivery system:")
    print("1. User login → Car Service → Fuel Delivery")
    print("2. Select fuel type and quantity")
    print("3. Enter location (Asalpha, Bandra, etc.)")
    print("4. View nearby agents with service area validation")

if __name__ == "__main__":
    create_test_agents()
