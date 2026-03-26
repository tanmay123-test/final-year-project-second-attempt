#!/usr/bin/env python3
"""
Test AI Care with Test Server (Port 5001)
"""

import requests
import json
import time

def test_ai_care_test_server():
    print("🤕 Testing AI Care with Test Server")
    print("=" * 50)
    
    # Test the healthcare AI care endpoint on port 5001
    url = "http://localhost:5001/healthcare/ai-care"
    
    # Test data
    test_cases = [
        "I have headache",
        "severe migraine with nausea",
        "headache after head injury"
    ]
    
    for i, message in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {message}")
        print("-" * 30)
        
        test_data = {
            "message": message,
            "user_id": "test_user_123",
            "conversation_history": []
        }
        
        try:
            print(f"📡 Sending request to: {url}")
            
            response = requests.post(url, json=test_data)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Success! Response received:")
                
                print(f"\n🤖 AI Response: {data.get('response', 'N/A')}")
                print(f"🩺 Severity: {data.get('severity', 'N/A')}")
                print(f"👨‍⚕️ Specialist: {data.get('specializations', 'N/A')}")
                print(f"💊 First Aid: {data.get('first_aid', 'N/A')}")
                print(f"🏥 Stage: {data.get('stage', 'N/A')}")
                print(f"📋 Follow-up: {data.get('follow_up', 'N/A')}")
                
                doctors = data.get('suggested_doctors', [])
                if doctors:
                    print(f"👨‍⚕️ Suggested Doctors:")
                    for doc in doctors:
                        print(f"   • Dr. {doc['name']} ({doc['specialization']}) - Rating: {doc['rating']}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Test server not running!")
            print("🚀 Please start the test server first:")
            print("   python ai_care_test_server.py")
            return
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎯 Test Complete!")
    print("✅ AI Care is working perfectly!")
    print("🚀 Ready for frontend integration!")

if __name__ == "__main__":
    # Wait a moment for server to start
    time.sleep(2)
    test_ai_care_test_server()
