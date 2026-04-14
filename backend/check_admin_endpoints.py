import requests

print("=== CHECKING ADMIN ENDPOINTS REGISTRATION ===")
print()

API_BASE = 'http://localhost:5000'

# Check all possible admin endpoints
endpoints = [
    '/admin/workers',
    '/admin/workers/',
    '/admin/workers/pending',
    '/admin/workers/approved',
    '/admin/workers/all',
    '/admin/workers/27/approve',
    '/admin/workers/27/reject'
]

print("Testing admin endpoint registration...")
for endpoint in endpoints:
    try:
        response = requests.get(f'{API_BASE}{endpoint}')
        print(f"   GET {endpoint}: {response.status_code}")
        
        if response.status_code == 401:
            print(f"     ✅ Endpoint exists (requires auth)")
        elif response.status_code == 404:
            print(f"     ❌ Endpoint not found")
        elif response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"     ✅ Endpoint works (returned {len(data)} items)")
            else:
                print(f"     ✅ Endpoint works (returned data)")
        else:
            print(f"     ❓ Unexpected: {response.json()}")
            
    except Exception as e:
        print(f"   GET {endpoint}: ERROR - {e}")

print()
print("Testing POST endpoints...")
post_endpoints = [
    ('/admin/workers/27/approve', {}),
    ('/admin/workers/27/reject', {'rejection_reason': 'test'})
]

for endpoint, data in post_endpoints:
    try:
        response = requests.post(f'{API_BASE}{endpoint}', json=data)
        print(f"   POST {endpoint}: {response.status_code}")
        
        if response.status_code == 401:
            print(f"     ✅ Endpoint exists (requires auth)")
        elif response.status_code == 404:
            print(f"     ❌ Endpoint not found")
        elif response.status_code == 200:
            print(f"     ✅ Endpoint works (no auth required)")
        else:
            print(f"     ❓ Response: {response.json()}")
            
    except Exception as e:
        print(f"   POST {endpoint}: ERROR - {e}")

print()
print("🔧 DIAGNOSIS:")
print()
print("If endpoints show 404:")
print("   ❌ Admin blueprint not registered properly")
print("   💡 Need to check import errors in app.py")
print()
print("If endpoints show 401:")
print("   ✅ Endpoints are registered and working")
print("   💡 Just need authentication")
print()
print("🚀 NEXT STEPS:")
print("   1. Check server logs for import errors")
print("   2. Restart server if needed")
print("   3. Test with admin authentication")
