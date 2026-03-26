#!/usr/bin/env python3
"""
Test AI Care Endpoint Directly
"""

import requests
import json

def test_ai_care():
    print("🤕 Testing AI Care Endpoint Directly")
    print("=" * 50)
    
    # Test the healthcare AI care endpoint
    url = "http://localhost:5000/healthcare/ai-care"
    
    # Test data
    test_data = {
        "message": "I have headache",
        "user_id": "test_user_123",
        "conversation_history": []
    }
    
    try:
        print(f"📡 Sending request to: {url}")
        print(f"📝 Test message: {test_data['message']}")
        
        response = requests.post(url, json=test_data)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response received:")
            print(json.dumps(data, indent=2))
            
            # Check key fields
            if data.get('success'):
                print(f"\n🤖 AI Response: {data.get('response', 'N/A')}")
                print(f"🩺 Severity: {data.get('severity', 'N/A')}")
                print(f"👨‍⚕️ Specialist: {data.get('specializations', 'N/A')}")
                print(f"💊 First Aid: {data.get('first_aid', 'N/A')}")
                print(f"🏥 Stage: {data.get('stage', 'N/A')}")
            else:
                print(f"❌ API returned error: {data.get('message', 'Unknown error')}")
        
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running!")
        print("🚀 Please start the backend server first:")
        print("   cd backend && python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ai_care()
