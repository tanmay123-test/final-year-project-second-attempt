import requests

print("=== FIXING ADMIN HOUSEKEEPING VISIBILITY ISSUE ===")
print()

API_BASE = 'http://localhost:5000'

# Let's check the admin endpoints directly to see if there's an issue
print("1. Testing admin endpoints without authentication (to check if they exist)...")

endpoints = [
    '/admin/workers/pending?service=housekeeping',
    '/admin/workers/pending',
    '/admin/workers?service=housekeeping',
    '/admin/workers',
    '/admin/workers/all'
]

for endpoint in endpoints:
    response = requests.get(f'{API_BASE}{endpoint}')
    print(f"   {endpoint}: Status {response.status_code}")
    if response.status_code != 401:
        print(f"     Response: {response.json()}")
    else:
        print("     Requires authentication (expected)")

print()

# Check if there's a direct database query we can make
print("2. Creating test housekeeping worker and checking database...")

import random
random_num = random.randint(1000, 9999)
worker_data = {
    'full_name': 'Test Housekeeper DB Check',
    'email': f'dbcheck{random_num}@test.com',
    'phone': '9876543210',
    'service': 'housekeeping',
    'specialization': 'General Cleaning',
    'experience': '1 year',
    'clinic_location': 'Mumbai',
    'password': 'test123',
    'aadhaar': '123456789012'
}

response = requests.post(f'{API_BASE}/worker/signup', data=worker_data)
print(f"   Worker Registration Status: {response.status_code}")

if response.status_code == 201:
    worker_id = response.json().get('worker_id')
    print(f"   ✅ Worker registered: {worker_data['email']} (ID: {worker_id})")
    
    # Try to login to confirm it's in database
    login_response = requests.post(f'{API_BASE}/worker/login', json={
        'email': worker_data['email'],
        'password': 'test123'
    })
    print(f"   Worker Login Status: {login_response.status_code}")
    print(f"   Worker Login Response: {login_response.json()}")
    
    if login_response.status_code == 403:
        print("   ✅ Worker is in database and correctly blocked (pending approval)")
        
        print()
        print("3. Checking admin housekeeping endpoint structure...")
        
        # The issue might be in the admin endpoint query
        # Let's check the admin_workers.py file to see the query structure
        print("   💡 ISSUE ANALYSIS:")
        print("   - Worker registration: WORKING ✅")
        print("   - Worker login blocked: WORKING ✅")
        print("   - Worker exists in database: CONFIRMED ✅")
        print("   - Admin can't see worker: ISSUE ❌")
        print()
        print("   🔧 POSSIBLE CAUSES:")
        print("   1. Admin authentication issue")
        print("   2. Service filter not working correctly")
        print("   3. Admin endpoint query issue")
        print("   4. Frontend API call issue")
        print()
        print("4. SOLUTION:")
        print("   ✅ Create working admin account")
        print("   ✅ Test admin endpoints manually")
        print("   ✅ Fix service filtering if needed")
        print("   ✅ Verify frontend API calls")
        
print()
print("🔧 IMMEDIATE FIX NEEDED:")
print("   1. Create admin account with OTP verification")
print("   2. Login to admin panel: http://localhost:5173/admin/housekeeping")
print("   3. Check if pending workers appear")
print("   4. If not, debug the service filter in admin endpoint")
print()
print("📋 WORKER READY FOR APPROVAL:")
print(f"   Email: {worker_data['email']}")
print(f"   Password: test123")
print(f"   Status: Pending Approval")
print(f"   Worker ID: {worker_id}")
print()
print("🚀 NEXT STEPS:")
print("   1. Complete admin account setup")
print("   2. Test admin housekeeping visibility")
print("   3. Approve pending workers")
print("   4. Verify complete workflow")
