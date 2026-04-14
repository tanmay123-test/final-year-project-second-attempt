import requests

print("=== DEBUGGING ADMIN HOUSEKEEPING VISIBILITY ISSUE ===")
print()

API_BASE = 'http://localhost:5000'

# Step 1: Create a new housekeeping worker
print("1. Creating new housekeeping worker...")
import random
random_num = random.randint(1000, 9999)
new_worker = {
    'full_name': 'Test Housekeeper Admin',
    'email': f'adminhousekeeper{random_num}@test.com',
    'phone': '9876543210',
    'service': 'housekeeping',
    'specialization': 'Deep Cleaning',
    'experience': '3 years',
    'clinic_location': 'Mumbai',
    'password': 'test123',
    'aadhaar': '123456789012'
}

print(f"   Email: {new_worker['email']}")
print(f"   Password: {new_worker['password']}")

response = requests.post(f'{API_BASE}/worker/signup', data=new_worker)
print(f"   Registration Status: {response.status_code}")
print(f"   Registration Response: {response.json()}")

if response.status_code == 201:
    worker_id = response.json().get('worker_id')
    print(f"   ✅ Worker registered with ID: {worker_id}")
    
    # Step 2: Try different admin credentials
    print()
    print("2. Testing admin credentials...")
    
    admin_attempts = [
        {'email': 'admin@example.com', 'password': 'admin123'},
        {'email': 'admin@test.com', 'password': 'admin'},
        {'email': 'administrator@example.com', 'password': 'admin123'},
        {'email': 'superadmin@example.com', 'password': 'admin123'},
    ]
    
    admin_token = None
    working_admin = None
    
    for admin_data in admin_attempts:
        response = requests.post(f'{API_BASE}/login', json=admin_data)
        print(f"   Admin {admin_data['email']}: Status {response.status_code}")
        
        if response.status_code == 200:
            admin_token = response.json().get('token')
            working_admin = admin_data
            print(f"   ✅ Admin login successful: {admin_data['email']}")
            break
        else:
            print(f"   ❌ Failed: {response.json()}")
    
    if admin_token:
        print()
        print("3. Checking admin housekeeping endpoints...")
        
        # Test different admin endpoints
        endpoints = [
            f'/admin/workers/pending?service=housekeeping',
            f'/admin/workers/pending',
            f'/admin/workers?service=housekeeping&status=pending',
            f'/admin/workers?status=pending',
            f'/admin/workers/all?service=housekeeping',
            f'/admin/workers/all'
        ]
        
        for endpoint in endpoints:
            print(f"   Testing: {endpoint}")
            response = requests.get(f'{API_BASE}{endpoint}', 
                                  headers={'Authorization': f'Bearer {admin_token}'})
            print(f"     Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"     Workers found: {len(data)}")
                    
                    # Check if our worker is in the list
                    our_worker = None
                    for worker in data:
                        if worker.get('email') == new_worker['email']:
                            our_worker = worker
                            break
                    
                    if our_worker:
                        print(f"     ✅ Our worker found: ID {our_worker.get('id')}, Status: {our_worker.get('status')}")
                    else:
                        print(f"     ❌ Our worker NOT found in this list")
                        
                        # Show first few workers for debugging
                        print(f"     Sample workers: {[{'id': w.get('id'), 'email': w.get('email'), 'status': w.get('status')} for w in data[:3]]}")
                else:
                    print(f"     Response: {data}")
            else:
                print(f"     Error: {response.json()}")
            print()
        
        # Step 4: Try to approve directly if found
        print("4. Testing direct approval...")
        if worker_id:
            approve_response = requests.post(f'{API_BASE}/admin/workers/{worker_id}/approve',
                                           headers={'Authorization': f'Bearer {admin_token}'})
            print(f"   Direct Approval Status: {approve_response.status_code}")
            print(f"   Direct Approval Response: {approve_response.json()}")
            
            if approve_response.status_code == 200:
                print("   ✅ Worker approved successfully!")
                
                # Test login after approval
                login_data = {'email': new_worker['email'], 'password': 'test123'}
                login_response = requests.post(f'{API_BASE}/worker/login', json=login_data)
                print(f"   Login After Approval Status: {login_response.status_code}")
                print(f"   Login After Approval Response: {login_response.json()}")
                
                if login_response.status_code == 200:
                    print("   ✅ Worker can now login!")
    
    else:
        print("   ❌ No admin credentials working")
        print("   💡 You need to check admin login credentials")
        print("   💡 Or create an admin user")
    
else:
    print(f"   ❌ Worker registration failed: {response.json()}")

print()
print("🔧 TROUBLESHOOTING TIPS:")
print("   1. Check admin login credentials")
print("   2. Verify admin endpoints are working")
print("   3. Check database for pending workers")
print("   4. Ensure service filter is working correctly")
print("   5. Check frontend API calls")
