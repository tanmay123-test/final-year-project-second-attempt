#!/usr/bin/env python3
"""
Test Fuel Delivery Availability Engine Flow
"""

import requests
import json

API = "http://127.0.0.1:5000"

def test_complete_flow():
    print('🔧 TESTING COMPLETE AVAILABILITY ENGINE FLOW')
    print('='*50)
    
    agent_id = 1
    
    # Step 1: Go offline first
    print('\n1️⃣ Go Offline First')
    try:
        response = requests.post(f"{API}/api/fuel-delivery/status", json={
            'agent_id': agent_id,
            'status': 'OFFLINE'
        })
        print(f'Status: {response.status_code}')
        result = response.json()
        print(f'Response: {result.get("message", "Failed")}')
    except Exception as e:
        print(f'Error: {e}')
    
    # Step 2: Go online (should work now)
    print('\n2️⃣ Go Online (should work)')
    try:
        response = requests.post(f"{API}/api/fuel-delivery/status", json={
            'agent_id': agent_id,
            'status': 'ONLINE_AVAILABLE'
        })
        print(f'Status: {response.status_code}')
        result = response.json()
        print(f'Response: {result.get("message", "Failed")}')
        print(f'Auto-assigned: {result.get("auto_assigned", False)}')
    except Exception as e:
        print(f'Error: {e}')
    
    # Step 3: Get requests
    print('\n3️⃣ Get Requests')
    try:
        response = requests.get(f"{API}/api/fuel-delivery/requests?agent_id={agent_id}")
        print(f'Status: {response.status_code}')
        result = response.json()
        if result['success']:
            requests_data = result.get('requests', [])
            print(f'Found {len(requests_data)} requests')
            if requests_data:
                print(f'First request ID: {requests_data[0].get("request_id")}')
    except Exception as e:
        print(f'Error: {e}')
    
    # Step 4: Accept first request
    print('\n4️⃣ Accept First Request')
    try:
        response = requests.post(f"{API}/api/fuel-delivery/accept-request", json={
            'agent_id': agent_id,
            'request_id': 1
        })
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            result = response.json()
            print(f'Response: {result.get("message", "Failed")}')
        else:
            print(f'Error: {response.text[:100]}')
    except Exception as e:
        print(f'Error: {e}')
    
    print('\n' + '='*50)
    print('🎯 AVAILABILITY ENGINE TEST COMPLETE!')

if __name__ == "__main__":
    test_complete_flow()
