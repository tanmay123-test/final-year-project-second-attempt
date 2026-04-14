import requests

print('=== TESTING USER LOGIN CREDENTIALS ===')
print()

# Try different user credentials
test_users = [
    {'email': 'test@example.com', 'password': 'password123'},
    {'email': 'user@example.com', 'password': 'password'},
    {'email': 'john@example.com', 'password': 'password123'},
    {'email': 'demo@example.com', 'password': 'demo'},
]

for i, user in enumerate(test_users):
    print(f'Test {i+1}: {user["email"]}')
    response = requests.post('http://localhost:5000/login', json=user)
    print(f'   Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   ✅ Success! User ID: {data.get("id")}')
        print(f'   Name: {data.get("name")}')
        
        # Now test healthcare booking with this user
        print()
        print('Testing healthcare booking with this user...')
        
        # Test availability
        doctor_id = 25
        test_date = '2026-04-19'
        
        response = requests.get(f'http://localhost:5000/healthcare/availability/{doctor_id}?date={test_date}')
        if response.status_code == 200:
            data = response.json()
            slots = data.get('available_slots', [])
            print(f'   Available slots: {slots}')
            
            if slots:
                # Test booking
                appointment_data = {
                    'doctor_id': doctor_id,
                    'patient_id': data.get('id'),
                    'date': test_date,
                    'time': slots[0],
                    'reason': 'Test healthcare appointment',
                    'status': 'pending'
                }
                
                headers = {'Authorization': f'Bearer {data.get("token")}'}
                response = requests.post('http://localhost:5000/healthcare/appointments', 
                                        json=appointment_data, headers=headers)
                print(f'   Booking Status: {response.status_code}')
                print(f'   Booking Response: {response.json()}')
                
                if response.status_code == 201:
                    print('   ✅ Healthcare booking working!')
                else:
                    print('   ❌ Healthcare booking failed')
            else:
                print('   ❌ No slots available for booking')
        else:
            print('   ❌ Could not get availability')
        
        break
    else:
        print(f'   ❌ Failed: {response.json()}')
    print()

print('🎯 USER LOGIN TEST COMPLETE!')
