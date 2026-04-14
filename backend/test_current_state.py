import requests

print("=== TESTING CURRENT HEALTHCARE LOGIN STATE ===")
print()

# Test the current login endpoint
login_data = {
    'email': 'approvedworker73751@test.com',
    'password': 'test123'
}

print("1. Testing healthcare worker login endpoint...")
response = requests.post('http://localhost:5000/worker/healthcare/login', json=login_data)
print(f'   Status: {response.status_code}')

if response.status_code == 200:
    result = response.json()
    print(f'   ✅ Login successful!')
    print(f'   Worker ID: {result.get("worker_id")}')
    print(f'   Doctor ID: {result.get("doctor_id")}')
    print(f'   Name: {result.get("name")}')
    print(f'   Service: {result.get("service")}')
    print(f'   Token: {result.get("token")[:30]}...')
    
    # Test availability with this worker ID
    worker_id = result.get('worker_id')
    if worker_id:
        print()
        print("2. Testing availability endpoint...")
        headers = {'Authorization': f'Bearer {result.get("token")}'}
        
        response = requests.get(f'http://localhost:5000/worker/{worker_id}/availability', headers=headers)
        print(f'   Status: {response.status_code}')
        
        if response.status_code == 200:
            print('   ✅ Availability endpoint working!')
            data = response.json()
            print(f'   Current slots: {len(data.get("availability", []))}')
        else:
            print(f'   ❌ Error: {response.json()}')
        
        print()
        print("3. Testing add time slot...")
        slot_data = {
            'date': '2026-04-22',
            'time_slot': '11:00-12:00'
        }
        
        response = requests.post(f'http://localhost:5000/worker/{worker_id}/availability', 
                                json=slot_data, headers=headers)
        print(f'   Status: {response.status_code}')
        print(f'   Response: {response.json()}')
        
        if response.status_code == 200:
            print('   ✅ Time slot added successfully!')
        else:
            print('   ❌ Failed to add time slot')
    
else:
    print(f'   ❌ Login failed: {response.json()}')

print()
print("🔍 BROWSER TROUBLESHOOTING:")
print("   If backend test passes, the issue is browser cache:")
print()
print("   STEP 1: Open browser where error occurs")
print("   STEP 2: Press F12 → Console tab")
print("   STEP 3: Type exactly: localStorage.clear()")
print("   STEP 4: Press Enter")
print("   STEP 5: Type: location.reload()")
print("   STEP 6: Press Enter")
print("   STEP 7: Go to: http://localhost:5173/worker/healthcare/login")
print("   STEP 8: Login with: approvedworker73751@test.com / test123")
print()
print("   The page should now work correctly!")
