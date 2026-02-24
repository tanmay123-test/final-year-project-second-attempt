#!/usr/bin/env python3
"""
Quick fix to add Tanmay directly to mechanics database
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def add_tanmay_directly():
    """Add Tanmay directly to car mechanics database"""
    try:
        from car_service.car_mechanics_db import car_mechanics_db
        
        print("🔧 ADDING TANMAY DIRECTLY TO MECHANICS DATABASE")
        print("=" * 50)
        
        # Add Tanmay with your details
        result = car_mechanics_db.add_mechanic(
            name="Tanmay Kumar",
            email="tanmay@example.com",  # Use your actual email
            phone="9876543215",          # Use your actual phone
            specialization="General Mechanic",
            experience=3,
            service_center="Tanmay AutoCare",
            location="Asalpha",           # This is key for location search
            rating=4.0,
            consultation_fee=320,
            status="approved",           # Direct approval - no pending
            password="mechanic123"
        )
        
        if result:
            print(f"✅ Tanmay added successfully!")
            print(f"🆔 Mechanic ID: {result}")
            print(f"📍 Location: Asalpha")
            print(f"🔧 Specialization: General Mechanic")
            print(f"💰 Fee: ₹320/hour")
            print(f"✅ Status: Approved (will show in search)")
        else:
            print("❌ Tanmay already exists or failed to add")
            
        # Verify addition
        print("\n🔍 VERIFYING TANMAY IN DATABASE:")
        mechanics = car_mechanics_db.get_mechanics(status='approved')
        
        tanmay_found = False
        for mech in mechanics:
            if 'Tanmay' in mech[1]:
                tanmay_found = True
                print(f"✅ Found Tanmay: {mech[1]} - {mech[4]} ({mech[7]})")
        
        if not tanmay_found:
            print("❌ Tanmay not found in approved mechanics")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_tanmay_directly()
