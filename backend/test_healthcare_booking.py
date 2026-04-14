import requests

print("=== TESTING HEALTHCARE BOOKING SYSTEM ===")
print()

# First login as a regular user
user_login_data = {
    'email': 'test@example.com',
    'password': 'password123'
}

print("1. Logging in as user...")
response = requests.post('http://localhost:5000/login', json=user_login_data)
if response.status_code == 200:
    user_data = response.json()
    user_token = user_data.get('token')
    user_id = user_data.get('id')
    user_headers = {'Authorization': f'Bearer {user_token}'}
    
    print(f"   ✅ User logged in - ID: {user_id}")
    
    # Test healthcare availability
    doctor_id = 25  # Use our approved healthcare worker
    test_date = '2026-04-19'
    
    print()
    print("2. Testing healthcare availability...")
    response = requests.get(f'http://localhost:5000/healthcare/availability/{doctor_id}?date={test_date}')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Available slots: {data.get('available_slots', [])}")
        
        if data.get('available_slots'):
            # Test booking an appointment
            print()
            print("3. Testing healthcare appointment booking...")
            
            appointment_data = {
                'doctor_id': doctor_id,
                'patient_id': user_id,
                'date': test_date,
                'time': data['available_slots'][0],  # Use first available slot
                'reason': 'Test appointment from healthcare booking system',
                'status': 'pending'
            }
            
            print(f"   Booking data: {appointment_data}")
            
            response = requests.post('http://localhost:5000/healthcare/appointments', 
                                    json=appointment_data, headers=user_headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            
            if response.status_code == 201:
                print("   ✅ Appointment booked successfully!")
            else:
                print("   ❌ Booking failed")
        else:
            print("   ❌ No available slots found")
    else:
        print(f"   ❌ Error getting availability: {response.json()}")
        
else:
    print(f"   ❌ User login failed: {response.json()}")

print()
print("🎯 HEALTHCARE BOOKING TEST COMPLETE!")
print("   If any step failed, that's the issue to fix.")
