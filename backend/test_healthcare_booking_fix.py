import requests

print("=== CREATING TEST USER FOR HEALTHCARE BOOKING ===")
print()

# First, let's create a test user
signup_data = {
    'name': 'Test User',
    'email': 'testuser@example.com',
    'password': 'test123'
}

print("1. Creating test user...")
response = requests.post('http://localhost:5000/signup', json=signup_data)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

if response.status_code == 201:
    print("   ✅ Test user created successfully!")
    
    # Now test login
    print()
    print("2. Testing login...")
    login_data = {
        'email': 'testuser@example.com',
        'password': 'test123'
    }
    
    response = requests.post('http://localhost:5000/login', json=login_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"   ✅ Login successful!")
        print(f"   User ID: {user_data.get('id')}")
        print(f"   Name: {user_data.get('name')}")
        
        # Test healthcare booking
        print()
        print("3. Testing healthcare booking...")
        
        # Test availability
        doctor_id = 25
        test_date = '2026-04-19'
        
        response = requests.get(f'http://localhost:5000/healthcare/availability/{doctor_id}?date={test_date}')
        if response.status_code == 200:
            data = response.json()
            slots = data.get('available_slots', [])
            print(f"   Available slots: {slots}")
            
            if slots:
                # Test booking
                appointment_data = {
                    'doctor_id': doctor_id,
                    'patient_id': user_data.get('id'),
                    'date': test_date,
                    'time': slots[0],
                    'reason': 'Test healthcare appointment booking',
                    'status': 'pending'
                }
                
                headers = {'Authorization': f'Bearer {user_data.get("token")}'}
                response = requests.post('http://localhost:5000/healthcare/appointments', 
                                        json=appointment_data, headers=headers)
                print(f"   Booking Status: {response.status_code}")
                print(f"   Booking Response: {response.json()}")
                
                if response.status_code == 201:
                    print("   ✅ Healthcare booking working perfectly!")
                else:
                    print("   ❌ Healthcare booking failed")
            else:
                print("   ❌ No slots available")
        else:
            print(f"   ❌ Could not get availability: {response.json()}")
    
    else:
        print(f"   ❌ Login failed: {response.json()}")

else:
    print(f"   ❌ User creation failed: {response.json()}")

print()
print("🎯 HEALTHCARE BOOKING SYSTEM TEST COMPLETE!")
