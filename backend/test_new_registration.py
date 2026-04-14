import requests
import random

print("=== TESTING NEW HEALTHCARE WORKER REGISTRATION ===")
print()

# Generate random email to avoid duplicates
random_num = random.randint(1000, 9999)
test_email = f"newdoctor{random_num}@test.com"

print(f"Testing with email: {test_email}")
print()

# Test registration
registration_data = {
    'full_name': f'Dr. Test Doctor {random_num}',
    'email': test_email,
    'phone': f'999{random_num}000',
    'specialization': 'Test Specialization',
    'experience': '5',
    'clinic_location': 'Test Hospital',
    'license_number': f'TEST{random_num}',
    'password': '123456'
}

try:
    print("1. Registering new healthcare worker...")
    response = requests.post('http://localhost:5000/worker/healthcare/signup', data=registration_data)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Registration successful!")
        print(f"   Worker ID: {result.get('worker_id')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Message: {result.get('message')}")
        
        # Check if worker appears in system
        print("\n2. Checking worker in healthcare system...")
        response = requests.get('http://localhost:5000/healthcare/doctors')
        
        if response.status_code == 200:
            doctors = response.json().get('doctors', [])
            
            # Find our new doctor
            new_doctor = None
            for doctor in doctors:
                if doctor.get('email') == test_email:
                    new_doctor = doctor
                    break
            
            if new_doctor:
                print(f"✅ New doctor found in system:")
                print(f"   Name: {new_doctor.get('full_name')}")
                print(f"   Email: {new_doctor.get('email')}")
                print(f"   Status: {new_doctor.get('status')}")
                
                if new_doctor.get('status') == 'pending':
                    print("🎉 PERFECT! New worker is PENDING")
                    print("   ✅ Admin approval required")
                    print("   ✅ Login will be blocked until approval")
                else:
                    print(f"❌ PROBLEM: Worker status is '{new_doctor.get('status')}'")
                    print("   ⚠️  Worker is auto-approved!")
            else:
                print("❌ New doctor not found in system")
        
        # Test login (should fail for pending)
        print("\n3. Testing login (should fail for pending)...")
        login_data = {
            'email': test_email,
            'password': '123456'
        }
        
        response = requests.post('http://localhost:5000/worker/healthcare/login', json=login_data)
        print(f"   Login response: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ PERFECT! Login blocked - worker not approved yet")
        else:
            print(f"⚠️  Login response: {response.json()}")
        
        print("\n🎉 TEST COMPLETE!")
        
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"   Error: {response.json()}")
        
except requests.exceptions.ConnectionError:
    print("❌ Server not running - please start with: python app.py")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n📋 IF YOU SEE AUTO-APPROVAL:")
print("   1. You might be using an old approved account")
print("   2. Test with a completely new email")
print("   3. Check if database has default 'approved' value")
