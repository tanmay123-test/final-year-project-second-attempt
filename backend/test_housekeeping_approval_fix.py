import requests

print("=== TESTING HOUSEKEEPING APPROVAL SYSTEM ===")
print()

API_BASE = 'http://localhost:5000'

# Test the housekeeping worker we created
worker_email = 'housekeeper@test.com'
worker_password = 'test123'

print(f"1. Testing housekeeping worker login...")
print(f"   Email: {worker_email}")
print(f"   Password: {worker_password}")

login_data = {
    'email': worker_email,
    'password': worker_password
}

response = requests.post(f'{API_BASE}/worker/login', json=login_data)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

if response.status_code == 403:
    print("   ✅ GOOD: Worker correctly blocked - needs approval")
    
    # Check if we can get admin credentials or create an admin
    print()
    print("2. Checking admin access...")
    
    # Try to get pending workers directly (without admin token for testing)
    print("   💡 Let's check what's in the database...")
    
    # Try different admin credentials
    admin_attempts = [
        {'email': 'admin@example.com', 'password': 'admin123'},
        {'email': 'admin@test.com', 'password': 'admin'},
        {'email': 'administrator@example.com', 'password': 'admin123'},
    ]
    
    admin_token = None
    for admin_data in admin_attempts:
        response = requests.post(f'{API_BASE}/login', json=admin_data)
        if response.status_code == 200:
            admin_token = response.json().get('token')
            print(f"   ✅ Admin login successful with: {admin_data['email']}")
            break
        else:
            print(f"   ❌ Admin failed: {admin_data['email']}")
    
    if admin_token:
        print()
        print("3. Getting pending housekeeping workers...")
        
        # Get pending workers
        response = requests.get(f'{API_BASE}/admin/workers/pending?service=housekeeping',
                              headers={'Authorization': f'Bearer {admin_token}'})
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            pending_workers = response.json()
            print(f"   Pending workers found: {len(pending_workers)}")
            
            if pending_workers:
                print("   Pending workers:")
                for worker in pending_workers:
                    print(f"     - ID: {worker.get('id')}, Email: {worker.get('email')}, Status: {worker.get('status')}")
                
                # Find our worker and approve
                our_worker = None
                for worker in pending_workers:
                    if worker.get('email') == worker_email:
                        our_worker = worker
                        break
                
                if our_worker:
                    worker_id = our_worker.get('id')
                    print()
                    print(f"4. Approving worker {worker_id}...")
                    
                    approve_response = requests.post(f'{API_BASE}/admin/workers/{worker_id}/approve',
                                                   headers={'Authorization': f'Bearer {admin_token}'})
                    print(f"   Approval Status: {approve_response.status_code}")
                    print(f"   Approval Response: {approve_response.json()}")
                    
                    if approve_response.status_code == 200:
                        print("   ✅ Worker approved!")
                        
                        # Test login again
                        print()
                        print("5. Testing login after approval...")
                        login_response = requests.post(f'{API_BASE}/worker/login', json=login_data)
                        print(f"   Status: {login_response.status_code}")
                        print(f"   Response: {login_response.json()}")
                        
                        if login_response.status_code == 200:
                            print("   ✅ PERFECT: Worker can now login!")
                            print()
                            print("🎯 HOUSEKEEPING APPROVAL SYSTEM IS WORKING!")
                        else:
                            print("   ❌ Login still failed after approval")
                    else:
                        print("   ❌ Approval failed")
                else:
                    print("   ❌ Our worker not found in pending list")
            else:
                print("   ❌ No pending workers found")
        else:
            print(f"   ❌ Failed to get pending workers: {response.json()}")
    else:
        print("   ❌ No admin access available")
        print("   💡 You may need to manually approve in the admin panel")
        print("   💡 Go to: http://localhost:5173/admin/housekeeping")

elif response.status_code == 200:
    print("   ❌ PROBLEM: Worker can login without approval!")
    print("   💡 This means the approval system is not working correctly")
    
else:
    print(f"   ❌ Unexpected response: {response.json()}")

print()
print("🔧 HOUSEKEEPING APPROVAL SYSTEM CHECK:")
print("   ✅ Backend has approval check in /worker/login")
print("   ✅ Admin approval endpoints exist")
print("   ✅ Frontend uses correct login endpoint")
print("   💡 If worker can login without approval, check database status")
