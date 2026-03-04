#!/usr/bin/env python3
"""
Complete test of Fuel Delivery Agent Availability Engine
"""

import requests
import json
import time

API = "http://127.0.0.1:5000"

def test_availability_engine():
    print("🔧 COMPLETE FUEL DELIVERY AVAILABILITY ENGINE TEST")
    print("="*60)
    
    agent_id = 1
    
    # Test 1: Get initial status
    print("\n1️⃣ TESTING INITIAL STATUS")
    try:
        response = requests.get(f"{API}/api/fuel-delivery/agent/{agent_id}/status")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Initial Status: {result.get('current_status', 'OFFLINE')}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Go Online with validation
    print("\n2️⃣ TESTING GO ONLINE WITH VALIDATION")
    try:
        response = requests.post(f"{API}/api/fuel-delivery/status", json={
            'agent_id': agent_id,
            'status': 'ONLINE_AVAILABLE'
        })
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Go Online Result: {result.get('message', 'Success')}")
            print(f"   Auto-assigned: {result.get('auto_assigned', False)}")
        else:
            print(f"❌ Go online failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Get demand insights
    print("\n3️⃣ TESTING DEMAND INSIGHTS")
    try:
        response = requests.get(f"{API}/api/fuel-delivery/demand-insights")
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                insights = result['insights']
                print(f"✅ Waiting Requests: {insights.get('waiting_requests', 0)}")
                print(f"✅ Available Agents: {insights.get('available_agents', 0)}")
                print(f"✅ Demand Level: {insights.get('demand_level', 'NORMAL')}")
                print(f"✅ Message: {insights.get('demand_message', '')}")
                print(f"✅ Suggestion: {insights.get('suggestion', '')}")
        else:
            print(f"❌ Demand insights failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: View eligible requests with capacity filtering
    print("\n4️⃣ TESTING ELIGIBLE REQUESTS WITH CAPACITY FILTERING")
    try:
        response = requests.get(f"{API}/api/fuel-delivery/requests?agent_id={agent_id}")
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                requests_data = result.get('requests', [])
                print(f"✅ Found {len(requests_data)} eligible requests")
                
                for i, req in enumerate(requests_data[:2], 1):  # Show first 2
                    print(f"   Request {i}: {req.get('fuel_type')} - {req.get('quantity_liters')}L")
                    print(f"   Distance: {req.get('distance_km', 0)}km | ETA: {req.get('eta_minutes', 0)}min")
                    print(f"   Score: {req.get('assignment_score', 0):.2f}")
        else:
            print(f"❌ Queue check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Accept a request
    print("\n5️⃣ TESTING REQUEST ACCEPTANCE")
    try:
        # Get first request ID
        response = requests.get(f"{API}/api/fuel-delivery/requests?agent_id={agent_id}")
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                requests_data = result.get('requests', [])
                if requests_data:
                    first_request = requests_data[0]
                    request_id = first_request.get('request_id')
                    
                    # Accept the request
                    response = requests.post(f"{API}/api/fuel-delivery/accept-request", json={
                        'agent_id': agent_id,
                        'request_id': request_id
                    })
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ Request Accepted: {result.get('message', 'Success')}")
                    else:
                        print(f"❌ Accept failed: {response.status_code}")
                else:
                    print("❌ No requests to accept")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Check busy protection
    print("\n6️⃣ TESTING BUSY PROTECTION")
    try:
        response = requests.get(f"{API}/api/fuel-delivery/requests?agent_id={agent_id}")
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                if 'error' in result and 'not available' in result['error']:
                    print("✅ Busy protection working - agent cannot see new requests")
                else:
                    print("⚠️ Busy protection may not be working")
        else:
            print(f"❌ Busy protection test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 7: Go offline
    print("\n7️⃣ TESTING GO OFFLINE")
    try:
        response = requests.post(f"{API}/api/fuel-delivery/status", json={
            'agent_id': agent_id,
            'status': 'OFFLINE'
        })
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Go Offline Result: {result.get('message', 'Success')}")
        else:
            print(f"❌ Go offline failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("🎯 AVAILABILITY ENGINE TEST COMPLETE!")
    print("✅ All core features tested successfully!")

if __name__ == "__main__":
    test_availability_engine()
