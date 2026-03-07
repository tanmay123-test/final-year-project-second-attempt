#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'car_service'))

from car_profile_db import car_profile_db

# Create a car service profile for user 1 (vedant)
user_id = 1
city = "Mumbai"
address = "Andheri West, Mumbai"
emergency_name = "Family Contact"
emergency_phone = "9876543210"

try:
    # Create profile
    car_profile_db.create_car_profile(user_id, city, address, emergency_name, emergency_phone)
    print(f"Created car service profile for user {user_id}")
    
    # Add a car for this user
    car_id = car_profile_db.add_car(
        user_id=user_id,
        brand="Tata",
        model="Tiago",
        year=2022,
        fuel="Petrol",
        reg="MH01AB1234",
        set_default=True
    )
    print(f"Added car with ID: {car_id}")
    
    # Verify the profile
    profile = car_profile_db.get_car_profile(user_id)
    if profile:
        print("\nProfile details:")
        for key, value in profile.items():
            print(f"  {key}: {value}")
    
    # Verify the car
    car = car_profile_db.get_car_by_id(car_id)
    if car:
        print("\nCar details:")
        for key, value in car.items():
            print(f"  {key}: {value}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
