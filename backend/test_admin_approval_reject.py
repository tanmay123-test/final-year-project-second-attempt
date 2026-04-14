import requests

print("=== TESTING ADMIN APPROVAL/REJECT FUNCTIONALITY ===")
print()

API_BASE = 'http://localhost:5000'

# First, get a housekeeping worker to test with
print("1. Getting housekeeping workers for testing...")
response = requests.get(f'{API_BASE}/admin/workers/pending?service=housekeeping')
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    workers = response.json()
    print(f"   Found {len(workers)} housekeeping workers")
    
    if workers:
        test_worker = workers[0]
        worker_id = test_worker.get('id')
        worker_email = test_worker.get('email')
        print(f"   Testing with: {worker_email} (ID: {worker_id})")
        
        # Test approval endpoint without auth (should fail)
        print()
        print("2. Testing approval endpoint without authentication...")
        approve_response = requests.post(f'{API_BASE}/admin/workers/{worker_id}/approve')
        print(f"   Status: {approve_response.status_code}")
        print(f"   Response: {approve_response.json()}")
        
        # Test reject endpoint without auth (should fail)
        print()
        print("3. Testing reject endpoint without authentication...")
        reject_response = requests.post(f'{API_BASE}/admin/workers/{worker_id}/reject', 
                                       json={'rejection_reason': 'Test rejection'})
        print(f"   Status: {reject_response.status_code}")
        print(f"   Response: {reject_response.json()}")
        
        # Check if endpoints exist at all
        if approve_response.status_code == 404:
            print("   ❌ APPROVAL ENDPOINT NOT FOUND!")
            print("   💡 The approval endpoints may not be registered properly")
        
        if reject_response.status_code == 404:
            print("   ❌ REJECT ENDPOINT NOT FOUND!")
            print("   💡 The reject endpoints may not be registered properly")
        
        # Check if the admin blueprint is properly registered
        print()
        print("4. Checking admin blueprint registration...")
        
        # Try to access the base admin workers endpoint
        base_response = requests.get(f'{API_BASE}/admin/workers')
        print(f"   Base admin endpoint: {base_response.status_code}")
        
        if base_response.status_code == 404:
            print("   ❌ ADMIN BLUEPRINT NOT REGISTERED!")
            print("   💡 The workers_admin_bp blueprint may not be registered")
        
        # Test worker login to make sure worker exists
        print()
        print("5. Testing worker login (should be blocked)...")
        login_response = requests.post(f'{API_BASE}/worker/login', json={
            'email': worker_email,
            'password': 'test123'
        })
        print(f"   Worker login status: {login_response.status_code}")
        print(f"   Worker login response: {login_response.json()}")
        
    else:
        print("   ❌ No housekeeping workers found")
else:
    print(f"   ❌ Error getting workers: {response.json()}")

print()
print("🔧 APPROVAL/REJECT ISSUE ANALYSIS:")
print()
print("📋 POSSIBLE CAUSES:")
print("   1. ❌ Admin blueprint not registered")
print("   2. ❌ Approval/reject endpoints not found (404)")
print("   3. ❌ Authentication required but not provided")
print("   4. ❌ Backend routes not properly configured")
print()
print("✅ SOLUTION NEEDED:")
print("   1. Check admin blueprint registration in app.py")
print("   2. Verify approval/reject endpoints exist")
print("   3. Test with proper admin authentication")
print("   4. Fix any routing issues")
