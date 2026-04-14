import requests

print("=== CREATING ADMIN AND TESTING HOUSEKEEPING VISIBILITY ===")
print()

API_BASE = 'http://localhost:5000'

# Step 1: Create admin user
print("1. Creating admin user...")
admin_data = {
    'name': 'System Administrator',
    'email': 'admin@expertease.com',
    'password': 'admin123'
}

print(f"   Admin Email: {admin_data['email']}")
print(f"   Admin Password: {admin_data['password']}")

response = requests.post(f'{API_BASE}/signup', json=admin_data)
print(f"   Admin Signup Status: {response.status_code}")
print(f"   Admin Signup Response: {response.json()}")

if response.status_code == 201:
    print("   ✅ Admin user created (pending OTP verification)")
    
    # Try to login anyway (some systems don't require OTP for admin)
    login_response = requests.post(f'{API_BASE}/login', json={
        'email': admin_data['email'],
        'password': admin_data['password']
    })
    print(f"   Admin Login Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        admin_token = login_response.json().get('token')
        print("   ✅ Admin login successful!")
        
        # Step 2: Create a new housekeeping worker
        print()
        print("2. Creating housekeeping worker...")
        import random
        random_num = random.randint(1000, 9999)
        worker_data = {
            'full_name': 'Test Housekeeper for Admin',
            'email': f'admintest{random_num}@test.com',
            'phone': '9876543210',
            'service': 'housekeeping',
            'specialization': 'Office Cleaning',
            'experience': '2 years',
            'clinic_location': 'Delhi',
            'password': 'test123',
            'aadhaar': '123456789012'
        }
        
        response = requests.post(f'{API_BASE}/worker/signup', data=worker_data)
        print(f"   Worker Registration Status: {response.status_code}")
        
        if response.status_code == 201:
            worker_id = response.json().get('worker_id')
            print(f"   ✅ Worker registered: {worker_data['email']} (ID: {worker_id})")
            
            # Step 3: Check admin housekeeping endpoints
            print()
            print("3. Testing admin housekeeping endpoints...")
            
            endpoints = [
                '/admin/workers/pending?service=housekeeping',
                '/admin/workers/pending',
                '/admin/workers?service=housekeeping&status=pending'
            ]
            
            for endpoint in endpoints:
                print(f"   Testing: {endpoint}")
                response = requests.get(f'{API_BASE}{endpoint}',
                                      headers={'Authorization': f'Bearer {admin_token}'})
                print(f"     Status: {response.status_code}")
                
                if response.status_code == 200:
                    workers = response.json()
                    if isinstance(workers, list):
                        print(f"     Pending workers: {len(workers)}")
                        
                        # Look for our worker
                        our_worker = None
                        for worker in workers:
                            if worker.get('email') == worker_data['email']:
                                our_worker = worker
                                break
                        
                        if our_worker:
                            print(f"     ✅ Found our worker: ID {our_worker.get('id')}, Status: {our_worker.get('status')}")
                            
                            # Step 4: Approve the worker
                            print()
                            print("4. Approving worker...")
                            approve_response = requests.post(f'{API_BASE}/admin/workers/{our_worker.get("id")}/approve',
                                                           headers={'Authorization': f'Bearer {admin_token}'})
                            print(f"     Approval Status: {approve_response.status_code}")
                            print(f"     Approval Response: {approve_response.json()}")
                            
                            if approve_response.status_code == 200:
                                print("     ✅ Worker approved!")
                                
                                # Test worker login
                                login_response = requests.post(f'{API_BASE}/worker/login', json={
                                    'email': worker_data['email'],
                                    'password': 'test123'
                                })
                                print(f"     Worker Login Status: {login_response.status_code}")
                                
                                if login_response.status_code == 200:
                                    print("     ✅ Worker can now login!")
                                    print()
                                    print("🎯 HOUSEKEEPING ADMIN SYSTEM WORKING PERFECTLY!")
                                else:
                                    print(f"     ❌ Worker login failed: {login_response.json()}")
                        else:
                            print(f"     ❌ Our worker not found")
                            print(f"     Available workers: {[w.get('email') for w in workers[:3]]}")
                    else:
                        print(f"     Response: {workers}")
                else:
                    print(f"     Error: {response.json()}")
                print()
        else:
            print(f"   ❌ Worker registration failed: {response.json()}")
    
    else:
        print(f"   ❌ Admin login failed: {login_response.json()}")
        print("   💡 Admin may need OTP verification")

else:
    print(f"   ❌ Admin creation failed: {response.json()}")

print()
print("🔧 ADMIN CREDENTIALS CREATED:")
print(f"   Email: {admin_data['email']}")
print(f"   Password: {admin_data['password']}")
print()
print("📋 NEXT STEPS:")
print("   1. Use these admin credentials to login")
print("   2. Go to: http://localhost:5173/admin/housekeeping")
print("   3. You should see pending housekeeping workers")
print("   4. Approve them to enable worker login")
