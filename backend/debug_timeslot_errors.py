import requests

print('=== CHECKING TIME SLOT ERRORS ===')
print()

# Test with our approved worker
worker_email = 'approvedworker73751@test.com'
worker_password = 'test123'
worker_id = 25

# Login
login_data = {
    'email': worker_email,
    'password': worker_password
}

response = requests.post('http://localhost:5000/worker/healthcare/login', json=login_data)
if response.status_code == 200:
    worker_data = response.json()
    token = worker_data.get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    print('✅ Worker logged in')
    
    # Test different time slot scenarios
    test_scenarios = [
        {'date': '2026-04-18', 'time_slot': '09:00-10:00', 'desc': 'Valid slot'},
        {'date': '2026-04-18', 'time_slot': '09:00 AM', 'desc': 'Old format'},
        {'date': '2026-04-18', 'time_slot': '09:00-10:00', 'desc': 'Duplicate slot'},
        {'date': '', 'time_slot': '10:00-11:00', 'desc': 'Empty date'},
        {'date': '2026-04-18', 'time_slot': '', 'desc': 'Empty time'},
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f'Test {i+1}: {scenario["desc"]}')
        print(f'   Data: date={scenario["date"]}, time={scenario["time_slot"]}')
        
        try:
            response = requests.post(f'http://localhost:5000/worker/{worker_id}/availability', 
                                    json=scenario, headers=headers)
            print(f'   Status: {response.status_code}')
            print(f'   Response: {response.json()}')
            
            if response.status_code == 200:
                print('   ✅ Success')
            elif response.status_code == 400:
                print('   ⚠️ Bad Request')
            else:
                print('   ❌ Error')
        except Exception as e:
            print(f'   ❌ Exception: {e}')
        print()
    
    # Check current availability
    print('Current availability:')
    response = requests.get(f'http://localhost:5000/worker/{worker_id}/availability', headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f'   {data}')
    
else:
    print('❌ Login failed:', response.json())
