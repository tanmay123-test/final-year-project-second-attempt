import requests

print("=== DEBUGGING LOGIN CREDENTIALS ISSUE ===")
print()

# First, let's try to create a fresh test user
print("1. Creating a fresh test user...")
import random
random_num = random.randint(1000, 9999)
test_email = f'testuser{random_num}@example.com'

signup_data = {
    'name': 'Test User',
    'email': test_email,
    'password': 'test123'
}

response = requests.post('http://localhost:5000/signup', json=signup_data)
print(f"   Signup Status: {response.status_code}")
print(f"   Signup Response: {response.json()}")

if response.status_code == 201:
    print("   ✅ User created successfully!")
    
    # Now try to login
    print()
    print("2. Testing login with new user...")
    login_data = {
        'email': test_email,
        'password': 'test123'
    }
    
    response = requests.post('http://localhost:5000/login', json=login_data)
    print(f"   Login Status: {response.status_code}")
    print(f"   Login Response: {response.json()}")
    
    if response.status_code == 200:
        print("   ✅ Login successful!")
        data = response.json()
        print(f"   User ID: {data.get('id')}")
        print(f"   Name: {data.get('name')}")
        print(f"   Email: {data.get('email')}")
        
        print()
        print("🎯 LOGIN CREDENTIALS THAT WORK:")
        print(f"   Email: {test_email}")
        print(f"   Password: test123")
        print()
        print("Use these credentials to login in the frontend!")
        
    else:
        print("   ❌ Login failed")
        print("   This might mean the user needs OTP verification")
        
        # Try to verify OTP (skip for now)
        print()
        print("💡 TROUBLESHOOTING TIPS:")
        print("   1. Check if user needs email verification")
        print("   2. Try logging into the frontend directly")
        print("   3. Check browser console for specific errors")
        print("   4. Clear browser cache and try again")

else:
    print("   ❌ User creation failed")
    print(f"   Error: {response.json()}")

print()
print("🔍 COMMON LOGIN ISSUES:")
print("   ❌ User not found → Create new user")
print("   ❌ Wrong password → Check credentials")
print("   ❌ Email not verified → Check email/OTP")
print("   ❌ Server issues → Check backend logs")
print()
print("🚀 Try the credentials above or create a new user!")
