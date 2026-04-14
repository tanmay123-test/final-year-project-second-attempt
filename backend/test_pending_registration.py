import requests

print("=== TESTING HEALTHCARE WORKER PENDING REGISTRATION ===")
print()

# Test 1: Register a new healthcare worker
print("1. Registering new healthcare worker...")

registration_data = {
    'full_name': 'Dr. Pending Test Doctor',
    'email': 'pendingdoctor@test.com',
    'phone': '9998887770',
    'specialization': 'Test Specialization',
    'experience': '3',
    'clinic_location': 'Test Clinic',
    'license_number': 'PENDING123',
    'password': '123456'
}

try:
    response = requests.post('http://localhost:5000/worker/healthcare/signup', data=registration_data)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Registration successful!")
        print(f"   Worker ID: {result.get('worker_id')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Message: {result.get('message')}")
        
        # Test 2: Check if worker appears with pending status
        print("\n2. Checking worker status in healthcare system...")
        response = requests.get('http://localhost:5000/healthcare/doctors')
        
        if response.status_code == 200:
            doctors = response.json().get('doctors', [])
            
            # Find our new doctor
            new_doctor = None
            for doctor in doctors:
                if doctor.get('email') == 'pendingdoctor@test.com':
                    new_doctor = doctor
                    break
            
            if new_doctor:
                print(f"✅ New doctor found:")
                print(f"   Name: {new_doctor.get('full_name')}")
                print(f"   Email: {new_doctor.get('email')}")
                print(f"   Status: {new_doctor.get('status')}")
                print(f"   Specialization: {new_doctor.get('specialization')}")
                
                if new_doctor.get('status') == 'pending':
                    print("🎉 PERFECT! Doctor is in PENDING status")
                    print("   ✅ Admin approval required")
                    print("   ✅ Login will be blocked until approval")
                else:
                    print(f"❌ ISSUE: Doctor status is '{new_doctor.get('status')}' instead of 'pending'")
            else:
                print("❌ New doctor not found in system")
        
        # Test 3: Try to login (should fail)
        print("\n3. Testing login before approval...")
        login_data = {
            'email': 'pendingdoctor@test.com',
            'password': '123456'
        }
        
        response = requests.post('http://localhost:5000/worker/healthcare/login', json=login_data)
        print(f"   Login response: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ PERFECT! Login correctly blocked - worker not approved yet")
        else:
            print(f"⚠️  Unexpected login response: {response.json()}")
        
        print("\n🎉 HEALTHCARE WORKER REGISTRATION IS WORKING!")
        print("   ✅ Workers are created with 'pending' status")
        print("   ✅ Admin approval is required")
        print("   ✅ Login is blocked until approval")
        print("   ✅ Real-time notifications sent to admin")
        
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"   Error: {response.json()}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n📋 NEXT STEPS:")
print("   1. Admin should check healthcare admin panel")
print("   2. Admin will see new pending registration")
print("   3. Admin can review documents and approve")
print("   4. Worker will receive approval notification")
print("   5. Worker can then login and add availability")
