import requests
import json

def test_login():
    """Test the login endpoint directly"""
    
    url = "http://localhost:5000/login"
    data = {
        "username": "testuser",
        "password": "password123"
    }
    
    try:
        print("🔍 Testing login endpoint...")
        response = requests.post(url, json=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if "token" in result:
                print("✅ Login successful!")
                print(f"Token: {result['token'][:50]}...")
            else:
                print("⚠️ Login response missing token")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on port 5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login()
