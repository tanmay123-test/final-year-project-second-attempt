#!/usr/bin/env python3
"""
Create Test Fuel Delivery Agent Directly in Database
"""

import sqlite3

def create_test_agent_direct():
    print("🚀 CREATING TEST FUEL DELIVERY AGENT DIRECTLY IN DATABASE")
    print("="*60)
    
    try:
        # Connect to database
        conn = sqlite3.connect('expertisease.db')
        cursor = conn.cursor()
        
        # Create test agent with service area
        cursor.execute('''
            INSERT OR REPLACE INTO fuel_delivery_agents 
            (name, email, phone_number, password_hash, city, vehicle_type, 
             vehicle_number, service_area_city, service_area_location, service_area_km,
             latitude, longitude, approval_status, online_status, rating, 
             total_deliveries, completion_rate, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Tanmay Fuel Delivery',
            'tanmay@fuel.com',
            '9876543210',
            'hashed_password',  # Simplified for testing
            'Mumbai',
            'Van',
            'MH01AB1234',
            'Mumbai',
            'Asalpha',
            15,  # 15km service radius
            19.0954,  # Asalpha coordinates
            72.8783,
            'APPROVED',  # Already approved for testing
            'ONLINE_AVAILABLE',  # Online and available
            4.8,  # High rating
            25,  # Some deliveries
            95.0,  # High completion rate
            1  # Verified
        ))
        
        # Create more test agents
        test_agents = [
            ('Rahul Fuel Services', 'rahul@fuel.com', '9876543211', 'Mumbai', 'Truck', 'MH01CD5678', 'Bandra', 20, 19.0596, 72.8295),
            ('Ahmed Fuel Delivery', 'ahmed@fuel.com', '9876543212', 'Mumbai', 'Van', 'MH01EF9012', 'Andheri', 15, 19.1196, 72.8465),
            ('Sameer Fuel Delivery', 'sameer@fuel.com', '9876543213', 'Mumbai', 'Bike', 'MH01GH3456', 'Worli', 10, 19.0170, 72.8300),
            ('Akshay Fuel Delivery', 'akshay@fuel.com', '9876543214', 'Mumbai', 'Van', 'MH01IJ7890', 'Dadar', 15, 19.0190, 72.8420)
        ]
        
        for agent in test_agents:
            cursor.execute('''
                INSERT OR REPLACE INTO fuel_delivery_agents 
                (name, email, phone_number, password_hash, city, vehicle_type, 
                 vehicle_number, service_area_city, service_area_location, service_area_km,
                 latitude, longitude, approval_status, online_status, rating, 
                 total_deliveries, completion_rate, is_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent[0], agent[1], agent[2], 'hashed_password', 'Mumbai', agent[3],
                agent[4], 'Mumbai', agent[5], agent[6], agent[7], agent[8],
                'APPROVED', 'ONLINE_AVAILABLE', 4.5, 20, 92.0, 1
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Test agents created successfully!")
        print("\n📍 Service Areas Created:")
        print("   1. Tanmay Fuel Delivery - Asalpha (15km) - Van")
        print("   2. Rahul Fuel Services - Bandra (20km) - Truck")
        print("   3. Ahmed Fuel Delivery - Andheri (15km) - Van")
        print("   4. Sameer Fuel Delivery - Worli (10km) - Bike")
        print("   5. Akshay Fuel Delivery - Dadar (15km) - Van")
        
        print("\n🚀 Now test the fuel delivery system:")
        print("1. User login → Car Service → Fuel Delivery")
        print("2. Select fuel type and quantity")
        print("3. Enter location (Asalpha, Bandra, etc.)")
        print("4. View nearby agents with service area validation")
        
        print("\n✅ All agents are APPROVED and ONLINE_AVAILABLE")
        print("✅ Service area validation will work correctly now!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_test_agent_direct()
