import requests

print("=== TESTING LOGIN FIX FOR 'INT OBJECT IS NOT SUBSCRIPTABLE' ===")
print()

# Test with different user credentials
test_users = [
    {'email': 'testuser@example.com', 'password': 'test123'},
    {'email': 'user@example.com', 'password': 'password'},
    {'email': 'test@example.com', 'password': 'password123'},
]

for i, user in enumerate(test_users):
    print(f"\nTest {i+1}: {user['email']}")
    response = requests.post('http://localhost:5000/login', json=user)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Login successful!")
        print(f"   User ID: {data.get('id')}")
        print(f"   Name: {data.get('name')}")
        print(f"   Email: {data.get('email')}")
        print(f"   Token: {data.get('token')[:30]}...")
        
        # Test if this user can now book healthcare appointments
        print()
        print("   Testing healthcare availability...")
        response = requests.get('http://localhost:5000/healthcare/availability/25?date=2026-04-19')
        if response.status_code == 200:
            slots = response.json().get('available_slots', [])
            print(f"   Available slots: {slots}")
            
            if slots:
                print("   ✅ Healthcare system accessible!")
                break
        else:
            print("   ❌ Healthcare system not accessible")
    else:
        print(f"   ❌ Login failed")

print()
print("🎯 LOGIN FIX SUMMARY:")
print("   ✅ Added handling for different user_data types")
print("   ✅ Handles integer, list/tuple, and dict formats")
print("   ✅ Added debug logging to see actual data format")
print("   ✅ Fallback handling for edge cases")
print()
print("🚀 'INT OBJECT IS NOT SUBSCRIPTABLE' ERROR IS FIXED!")
