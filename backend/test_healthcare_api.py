#!/usr/bin/env python3
"""
Test script for Healthcare API endpoints
"""

import requests
import json

def test_healthcare_endpoints():
    """Test all healthcare API endpoints"""
    
    base_url = "http://localhost:5000"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test_token'
    }
    
    endpoints = [
        {
            'name': 'Get All Doctors',
            'url': f'{base_url}/healthcare/doctors',
            'method': 'GET'
        },
        {
            'name': 'Get Specializations',
            'url': f'{base_url}/healthcare/specializations',
            'method': 'GET'
        },
        {
            'name': 'Search Doctors',
            'url': f'{base_url}/healthcare/search?q=cardiologist',
            'method': 'GET'
        },
        {
            'name': 'Get Doctors by Specialization',
            'url': f'{base_url}/healthcare/doctors/Cardiology',
            'method': 'GET'
        }
    ]
    
    print('🔍 Testing Healthcare API Endpoints...')
    print('=' * 60)
    
    for endpoint in endpoints:
        print(f'\n📡 {endpoint["name"]}')
        print(f'   {endpoint["method"]} {endpoint["url"]}')
        print('-' * 40)
        
        try:
            response = requests.request(
                endpoint['method'],
                endpoint['url'],
                headers=headers
            )
            
            print(f'Status: {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                print(f'✅ Success: {data.get("success", False)}')
                
                # Show sample data
                if 'doctors' in data:
                    doctors = data['doctors'] if isinstance(data['doctors'], list) else [data['doctors']]
                    print(f'Doctors found: {len(doctors)}')
                    if doctors:
                        print(f'Sample: {doctors[0].get("name", "Unknown")}')
                elif 'specializations' in data:
                    specs = data['specializations'] if isinstance(data['specializations'], list) else [data['specializations']]
                    print(f'Specializations: {len(specs)}')
                    if specs:
                        print(f'Sample: {specs[0] if isinstance(specs[0], str) else specs[0].get("name", "Unknown")}')
                else:
                    print(f'Data keys: {list(data.keys())}')
            else:
                print(f'❌ Error: {response.text}')
                
        except requests.exceptions.ConnectionError:
            print('⚠️ Backend server not running')
            print('   Start with: python app.py')
        except Exception as e:
            print(f'❌ Request failed: {str(e)}')
    
    print('\n' + '=' * 60)
    print('🎯 API Testing Complete!')

if __name__ == "__main__":
    test_healthcare_endpoints()
