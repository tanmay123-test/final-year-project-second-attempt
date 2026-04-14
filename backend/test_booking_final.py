import requests

print('=== TESTING HEALTHCARE BOOKING FINAL ===')
print()

# Try to login with existing user
login_data = {
    'email': 'testuser@example.com',
    'password': 'test123'
}

response = requests.post('http://localhost:5000/login', json=login_data)
print(f'Login Status: {response.status_code}')
print(f'Login Response: {response.json()}')

if response.status_code == 200:
    user_data = response.json()
    print('✅ Login successful!')
    print(f'User ID: {user_data.get("id")}')
    
    # Test healthcare booking
    print()
    print('Testing healthcare booking...')
    
    doctor_id = 25
    test_date = '2026-04-19'
    
    # Get availability
    response = requests.get(f'http://localhost:5000/healthcare/availability/{doctor_id}?date={test_date}')
    if response.status_code == 200:
        data = response.json()
        slots = data.get('available_slots', [])
        print(f'Available slots: {slots}')
        
        if slots:
            # Book appointment
            appointment_data = {
                'doctor_id': doctor_id,
                'patient_id': user_data.get('id'),
                'date': test_date,
                'time': slots[0],
                'reason': 'Test healthcare booking',
                'status': 'pending'
            }
            
            headers = {'Authorization': f'Bearer {user_data.get("token")}'}
            response = requests.post('http://localhost:5000/healthcare/appointments', 
                                    json=appointment_data, headers=headers)
            print(f'Booking Status: {response.status_code}')
            print(f'Booking Response: {response.json()}')
            
            if response.status_code == 201:
                print('✅ HEALTHCARE BOOKING WORKING!')
            else:
                print('❌ Booking failed')
        else:
            print('❌ No slots available')
    else:
        print(f'❌ Availability error: {response.json()}')

else:
    print('❌ Login failed')

print()
print('🎯 HEALTHCARE BOOKING TEST COMPLETE!')
