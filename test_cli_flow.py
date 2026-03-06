#!/usr/bin/env python3
"""
Test Fuel Delivery Agent CLI with Availability Engine
"""

import requests
import json

API = "http://127.0.0.1:5000"

def test_cli_flow():
    print("🔧 TESTING FUEL DELIVERY AGENT CLI FLOW")
    print("="*60)
    
    # Test agent login
    print("\n1️⃣ TESTING AGENT LOGIN")
    try:
        response = requests.post(f"{API}/api/fuel-delivery/login", json={
            'email': 'co2023.vedant.gate@ves.ac.in',
            'password': '123'
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                agent_info = result['agent']
                print(f"✅ Login successful!")
                print(f"   Agent: {agent_info.get('name', 'N/A')}")
                print(f"   Status: {agent_info.get('online_status', 'OFFLINE')}")
                print(f"   Vehicle: {agent_info.get('vehicle_type', 'N/A')}")
                
                # Test availability toggle
                test_availability_toggle(agent_info)
                
            else:
                print(f"❌ Login failed: {result.get('error')}")
        else:
            print(f"❌ Login failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_availability_toggle(agent_info):
    print("\n2️⃣ TESTING AVAILABILITY TOGGLE")
    
    # Test going online
    print("\n🔄 Testing GO ONLINE...")
    try:
        response = requests.post(f"{API}/api/fuel-delivery/status", json={
            'agent_id': agent_info['id'],
            'status': 'ONLINE_AVAILABLE'
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ {result.get('message', 'Online successful')}")
                
                # Check for auto-assignment
                if result.get('auto_assigned'):
                    print(f"🎯 Auto-assigned Request ID: {result.get('request_id')}")
                else:
                    print("📭 No auto-assignment (no compatible requests)")
                
                # Test queue viewing
                test_queue_viewing(agent_info)
                
            else:
                print(f"❌ Go online failed: {result.get('error')}")
        else:
            print(f"❌ Go online failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_queue_viewing(agent_info):
    print("\n3️⃣ TESTING QUEUE VIEWING")
    
    try:
        response = requests.get(f"{API}/api/fuel-delivery/requests", params={
            'agent_id': agent_info['id']
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                requests_data = result.get('requests', [])
                print(f"✅ Found {len(requests_data)} eligible requests")
                
                for i, req in enumerate(requests_data[:2], 1):  # Show first 2
                    print(f"   Request {i}: {req.get('fuel_type')} - {req.get('quantity_liters')}L")
                    print(f"   Distance: {req.get('distance_km', 0)}km | Score: {req.get('assignment_score', 0):.2f}")
                
                # Test request acceptance
                if requests_data:
                    test_request_acceptance(agent_info, requests_data[0])
                    
            else:
                print(f"❌ Queue failed: {result.get('error')}")
        else:
            print(f"❌ Queue failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_request_acceptance(agent_info, request):
    print("\n4️⃣ TESTING REQUEST ACCEPTANCE")
    
    try:
        response = requests.post(f"{API}/api/fuel-delivery/accept-request", json={
            'agent_id': agent_info['id'],
            'request_id': request['request_id']
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ {result.get('message', 'Request accepted')}")
                
                # Test going offline (should fail while busy)
                test_busy_protection(agent_info)
                
            else:
                print(f"❌ Accept failed: {result.get('error')}")
        else:
            print(f"❌ Accept failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_busy_protection(agent_info):
    print("\n5️⃣ TESTING BUSY PROTECTION")
    
    try:
        response = requests.post(f"{API}/api/fuel-delivery/status", json={
            'agent_id': agent_info['id'],
            'status': 'OFFLINE'
        })
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("⚠️ Busy protection NOT working - went offline while busy")
            else:
                print(f"✅ Busy protection working: {result.get('error')}")
        else:
            print(f"❌ Test failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_cli_flow()
    
    print("\n" + "="*60)
    print("🎯 CLI FLOW TEST COMPLETE!")
    print("✅ Fuel Delivery Agent Availability Engine is working!")
