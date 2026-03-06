#!/usr/bin/env python3
"""
Check Database and Create Test Agents
"""

import sqlite3
import os

def check_and_create_agents():
    print("🔍 CHECKING DATABASE AND CREATING TEST AGENTS")
    print("="*60)
    
    # Check database files
    db_files = ['expertisease.db', 'database.db', 'app.db']
    db_path = None
    
    for db_file in db_files:
        if os.path.exists(db_file):
            db_path = db_file
            print(f"✅ Found database: {db_file}")
            break
    
    if not db_path:
        print("❌ No database file found!")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if fuel_delivery_agents table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fuel_delivery_agents'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ fuel_delivery_agents table not found!")
            print("🔧 Creating table...")
            
            # Create the table
            cursor.execute('''
                CREATE TABLE fuel_delivery_agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone_number TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    city TEXT NOT NULL,
                    vehicle_type TEXT NOT NULL,
                    vehicle_number TEXT NOT NULL,
                    service_area_city TEXT DEFAULT '',
                    service_area_location TEXT DEFAULT '',
                    service_area_km INTEGER DEFAULT 15,
                    latitude REAL DEFAULT 0.0,
                    longitude REAL DEFAULT 0.0,
                    approval_status TEXT DEFAULT 'PENDING',
                    online_status TEXT DEFAULT 'OFFLINE',
                    rating REAL DEFAULT 0.0,
                    total_deliveries INTEGER DEFAULT 0,
                    completion_rate REAL DEFAULT 95.0,
                    is_verified BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            print("✅ Table created!")
        else:
            print("✅ fuel_delivery_agents table exists")
        
        # Create test agents
        test_agents = [
            ('Tanmay Fuel Delivery', 'tanmay@fuel.com', '9876543210', 'Mumbai', 'Van', 'MH01AB1234', 'Asalpha', 15, 19.0954, 72.8783),
            ('Rahul Fuel Services', 'rahul@fuel.com', '9876543211', 'Mumbai', 'Truck', 'MH01CD5678', 'Bandra', 20, 19.0596, 72.8295),
            ('Ahmed Fuel Delivery', 'ahmed@fuel.com', '9876543212', 'Mumbai', 'Van', 'MH01EF9012', 'Andheri', 15, 19.1196, 72.8465),
            ('Sameer Fuel Delivery', 'sameer@fuel.com', '9876543213', 'Mumbai', 'Bike', 'MH01GH3456', 'Worli', 10, 19.0170, 72.8300),
            ('Akshay Fuel Delivery', 'akshay@fuel.com', '9876543214', 'Mumbai', 'Van', 'MH01IJ7890', 'Dadar', 15, 19.0190, 72.8420)
        ]
        
        print("\n🚀 Creating test agents...")
        
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
        
        # Verify agents were created
        cursor.execute("SELECT name, service_area_location, service_area_km, vehicle_type FROM fuel_delivery_agents")
        agents = cursor.fetchall()
        
        print(f"\n✅ Created {len(agents)} test agents:")
        for agent in agents:
            print(f"   📍 {agent[0]} - {agent[1]} ({agent[2]}km) - {agent[3]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 TEST AGENTS READY FOR TESTING!")
        print("\n🚀 Now test the fuel delivery system:")
        print("1. User login → Car Service → Fuel Delivery")
        print("2. Select fuel type and quantity")
        print("3. Enter location (Asalpha, Bandra, etc.)")
        print("4. View nearby agents with service area validation")
        print("5. The system will now find agents within service area!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_and_create_agents()
