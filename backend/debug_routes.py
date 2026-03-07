#!/usr/bin/env python3
"""
Test what routes are actually registered
"""

import requests

def test_simple_endpoints():
    print('🔧 TESTING SIMPLE ENDPOINTS TO DEBUG')
    print('='*50)
    
    # Test base fuel delivery endpoint
    try:
        response = requests.get('http://127.0.0.1:5000/api/fuel-delivery/')
        print(f'Base endpoint: {response.status_code}')
    except Exception as e:
        print(f'Base endpoint error: {e}')
    
    # Test login endpoint (should work)
    try:
        response = requests.post('http://127.0.0.1:5000/api/fuel-delivery/login', json={
            'email': 'test@test.com',
            'password': 'test'
        })
        print(f'Login endpoint: {response.status_code}')
    except Exception as e:
        print(f'Login endpoint error: {e}')
    
    # Test register endpoint
    try:
        response = requests.post('http://127.0.0.1:5000/api/fuel-delivery/register', json={
            'name': 'Test',
            'email': 'test@test.com',
            'password': 'test'
        })
        print(f'Register endpoint: {response.status_code}')
    except Exception as e:
        print(f'Register endpoint error: {e}')
    
    # Test status endpoint with different URL
    try:
        response = requests.post('http://127.0.0.1:5000/api/fuel-delivery/update-status', json={
            'agent_id': 1,
            'status': 'OFFLINE'
        })
        print(f'Update-status endpoint: {response.status_code}')
    except Exception as e:
        print(f'Update-status endpoint error: {e}')

if __name__ == "__main__":
    test_simple_endpoints()
