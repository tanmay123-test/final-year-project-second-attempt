import requests
import json

def test_user_info():
    """Test the user info endpoint with the token"""
    
    # First login to get token
    login_url = "http://localhost:5000/login"
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    try:
        print("🔍 Step 1: Getting login token...")
        login_response = requests.post(login_url, json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return
            
        token = login_response.json()["token"]
        print(f"✅ Got token: {token[:50]}...")
        
        # Now test user info
        print("\n🔍 Step 2: Testing user info endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        info_response = requests.get("http://localhost:5000/user/info", headers=headers, timeout=10)
        
        print(f"Status Code: {info_response.status_code}")
        print(f"Response: {info_response.text}")
        
        if info_response.status_code == 200:
            print("✅ User info endpoint working!")
        else:
            print(f"❌ User info endpoint failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_user_info()
