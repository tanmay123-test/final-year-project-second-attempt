#!/usr/bin/env python3
"""
Test script for AI Care API endpoint
"""

import requests
import json

def test_ai_care_api():
    """Test the AI Care API endpoint"""
    
    test_data = {
        'message': 'I have tooth pain and swollen gums',
        'user_id': 'test_user_123',
        'conversation_history': []
    }
    
    print('🌐 Testing AI Care API Endpoint...')
    print('=' * 50)
    
    try:
        response = requests.post(
            'http://localhost:5000/healthcare/ai-care',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f'Status Code: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ API Response Received:')
            print(f'  Success: {data.get("success", False)}')
            print(f'  Stage: {data.get("stage", "unknown")}')
            print(f'  Severity: {data.get("severity", "unknown")}')
            print(f'  Specializations: {data.get("specializations", [])}')
            print(f'  Doctors Found: {len(data.get("suggested_doctors", []))}')
            print(f'  Response: {data.get("response", "No response")[:100]}...')
        else:
            print(f'❌ Error Response: {response.text}')
            
    except requests.exceptions.ConnectionError:
        print('⚠️ Backend server not running. Start with: python app.py')
    except Exception as e:
        print(f'❌ Test Error: {str(e)}')
    
    print('\n' + '=' * 50)
    print('🎯 API Test Complete!')

if __name__ == "__main__":
    test_ai_care_api()
