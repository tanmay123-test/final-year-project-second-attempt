#!/usr/bin/env python3
"""
Script to add sample mechanics to the car service database
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from car_service.car_mechanics_db import car_mechanics_db

def add_sample_mechanics():
    """Add sample mechanics to the database"""
    
    sample_mechanics = [
        {
            'name': 'Rajesh Kumar',
            'email': 'rajesh.kumar@autocare.com',
            'phone': '9876543210',
            'specialization': 'Engine Specialist',
            'experience': 8,
            'service_center': 'AutoCare Powai',
            'location': 'Powai',
            'rating': 4.5,
            'consultation_fee': 400,
            'status': 'approved',
            'password': 'mechanic123'
        },
        {
            'name': 'Amit Sharma',
            'email': 'amit.sharma@carfix.com',
            'phone': '9876543211',
            'specialization': 'General Mechanic',
            'experience': 5,
            'service_center': 'CarFix Asalpha',
            'location': 'Asalpha',
            'rating': 4.2,
            'consultation_fee': 350,
            'status': 'approved',
            'password': 'mechanic123'
        },
        {
            'name': 'Vijay Patil',
            'email': 'vijay.patil@motorworks.com',
            'phone': '9876543212',
            'specialization': 'Brake Specialist',
            'experience': 12,
            'service_center': 'MotorWorks Andheri',
            'location': 'Andheri',
            'rating': 4.8,
            'consultation_fee': 500,
            'status': 'approved',
            'password': 'mechanic123'
        },
        {
            'name': 'Suresh Reddy',
            'email': 'suresh.reddy@quickfix.com',
            'phone': '9876543213',
            'specialization': 'Electrical Specialist',
            'experience': 6,
            'service_center': 'QuickFix Bhandup',
            'location': 'Bhandup',
            'rating': 4.0,
            'consultation_fee': 380,
            'status': 'approved',
            'password': 'mechanic123'
        },
        {
            'name': 'Mohammed Ali',
            'email': 'mohammed.ali@expertgarage.com',
            'phone': '9876543214',
            'specialization': 'Transmission Specialist',
            'experience': 10,
            'service_center': 'ExpertGoregaon',
            'location': 'Goregaon',
            'rating': 4.6,
            'consultation_fee': 450,
            'status': 'approved',
            'password': 'mechanic123'
        }
    ]
    
    print("🔧 ADDING SAMPLE MECHANICS")
    print("=" * 40)
    
    try:
        for i, mech in enumerate(sample_mechanics, 1):
            print(f"\n{i}. Adding: {mech['name']}")
            print(f"   📍 Location: {mech['location']}")
            print(f"   🔧 Specialization: {mech['specialization']}")
            print(f"   ⭐ Rating: {mech['rating']}")
            print(f"   💰 Fee: ₹{mech['consultation_fee']}")
            
            # Add mechanic to database
            result = car_mechanics_db.add_mechanic(
                name=mech['name'],
                email=mech['email'],
                phone=mech['phone'],
                specialization=mech['specialization'],
                experience=mech['experience'],
                service_center=mech['service_center'],
                location=mech['location'],
                rating=mech['rating'],
                consultation_fee=mech['consultation_fee'],
                status=mech['status'],
                password=mech['password']
            )
            
            if result:
                print(f"   ✅ Added successfully")
            else:
                print(f"   ❌ Failed to add (might already exist)")
        
        print(f"\n🎉 Sample mechanics addition completed!")
        
        # Verify mechanics were added
        print(f"\n🔍 VERIFYING MECHANICS IN DATABASE")
        print("=" * 40)
        
        mechanics = car_mechanics_db.get_mechanics(status='approved')
        print(f"📊 Total approved mechanics: {len(mechanics)}")
        
        if mechanics:
            print(f"\n📋 Available Mechanics:")
            for mech in mechanics:
                print(f"   👨‍🔧 {mech[1]} - {mech[4]} ({mech[7]})")
        
        print(f"\n✅ Database is now ready for testing!")
        
    except Exception as e:
        print(f"❌ Error adding mechanics: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_sample_mechanics()
