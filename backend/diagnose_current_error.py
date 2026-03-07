#!/usr/bin/env python3

import requests
import json

def diagnose_current_error():
    """Diagnose the current error the user is facing"""
    
    print("🔍 DIAGNOSING CURRENT ERROR")
    print("="*60)
    
    # Test 1: Check if server is actually responding correctly
    print("📋 Test 1: Server Health Check")
    try:
        r = requests.get("http://127.0.0.1:5000/", timeout=5)
        print(f"   Root endpoint status: {r.status_code}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
    
    # Test 2: Check subscription endpoint
    print("\n📋 Test 2: Subscription Endpoint")
    try:
        r = requests.get("http://127.0.0.1:5000/api/subscription/plans", timeout=5)
        if r.status_code == 200:
            print("   ✅ Subscription API working")
            plans = r.json()
            print(f"   Available plans: {len(plans.get('plans', []))}")
        else:
            print(f"   ❌ Subscription API error: {r.status_code}")
    except Exception as e:
        print(f"   ❌ Subscription API error: {e}")
    
    # Test 3: Check payment endpoint specifically
    print("\n📋 Test 3: Payment Endpoint")
    try:
        r = requests.post("http://127.0.0.1:5000/create-order", 
                         json={"amount": 99900, "booking_id": "test_diagnosis"}, 
                         timeout=5)
        print(f"   Payment endpoint status: {r.status_code}")
        if r.status_code == 200:
            response = r.json()
            print("   ✅ Payment endpoint working")
            print(f"   Order ID: {response.get('order_id')}")
        elif r.status_code == 500:
            print("   ❌ Payment endpoint server error")
            print("   This suggests SQL or import issues")
        else:
            print(f"   ❌ Unexpected status: {r.status_code}")
    except Exception as e:
        print(f"   ❌ Payment endpoint error: {e}")
    
    # Test 4: Check what error CLI might be seeing
    print("\n📋 Test 4: CLI Subscription Flow")
    try:
        # Simulate what CLI does
        worker_id = 4
        
        # Get current subscription
        r = requests.get(f"http://127.0.0.1:5000/api/subscription/current?worker_id={worker_id}", timeout=5)
        print(f"   Current subscription status: {r.status_code}")
        
        if r.status_code == 200:
            current = r.json()
            print("   ✅ Current subscription API working")
        else:
            print(f"   ❌ Current subscription error: {r.status_code}")
            print(f"   Response: {r.text}")
            
    except Exception as e:
        print(f"   ❌ Current subscription error: {e}")
    
    print("\n🎯 POSSIBLE ERROR CAUSES:")
    print("="*60)
    print("If you're still seeing errors, it could be:")
    print("1. ❌ Server startup errors (check console)")
    print("2. ❌ Database connection issues")
    print("3. ❌ Import errors in payment system")
    print("4. ❌ Environment variable issues")
    print("5. ❌ Port conflicts or connection issues")
    
    print("\n🔧 IMMEDIATE CHECKS:")
    print("="*60)
    print("1. Check server console for error messages")
    print("2. Verify .env file has correct credentials")
    print("3. Check if database.db has payments table")
    print("4. Try restarting the server")
    print("5. Test with simple curl commands")

if __name__ == "__main__":
    diagnose_current_error()
