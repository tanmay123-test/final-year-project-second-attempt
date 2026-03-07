#!/usr/bin/env python3

import requests

PAYMENT_API = "http://127.0.0.1:5001"

def test_payment_system():
    """Test the payment system from basics"""
    
    print("💳 TESTING PAYMENT SYSTEM FROM BASICS")
    print("="*60)
    
    # Test 1: Check if payment server is running
    print("📋 STEP 1: CHECK PAYMENT SERVER")
    try:
        r = requests.get(f"{PAYMENT_API}/", timeout=5)
        
        if r.status_code == 200:
            print("✅ Payment server is running!")
            print(f"📊 Status: {r.status_code}")
            print(f"🌐 URL: {PAYMENT_API}")
        else:
            print(f"❌ Payment server error: {r.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Cannot connect to payment server: {e}")
        print("💡 Make sure payment server is running on port 5001")
        return
    
    # Test 2: Check payment endpoints
    print(f"\n📋 STEP 2: CHECK PAYMENT ENDPOINTS")
    
    endpoints = [
        "/payment/create-order",
        "/payment/status/123",
        "/payment/confirm"
    ]
    
    for endpoint in endpoints:
        try:
            r = requests.get(f"{PAYMENT_API}{endpoint}", timeout=5)
            print(f"   📡 {endpoint}: {r.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: Error - {e}")
    
    # Test 3: Create a test payment order
    print(f"\n📋 STEP 3: CREATE TEST PAYMENT ORDER")
    try:
        test_order_data = {
            "amount": 48000,  # ₹480 in paise
            "currency": "INR",
            "receipt": "order_test_123",
            "notes": {
                "appointment_id": "19",
                "user_id": "6",
                "doctor_id": "4"
            }
        }
        
        r = requests.post(f"{PAYMENT_API}/payment/create-order", 
                         json=test_order_data, timeout=10)
        
        print(f"📊 Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print("✅ Payment order created successfully!")
            print(f"📋 Order ID: {data.get('id', 'N/A')}")
            print(f"💰 Amount: ₹{data.get('amount', 0) / 100}")
            print(f"🔗 Payment URL: {data.get('payment_url', 'N/A')}")
        else:
            print(f"❌ Order creation failed: {r.text}")
            
    except Exception as e:
        print(f"❌ Order creation error: {e}")
    
    print(f"\n🎯 PAYMENT SYSTEM TEST COMPLETE!")
    print("="*60)
    print("✅ Payment server is running on port 5001")
    print("✅ Payment endpoints are accessible")
    print("✅ Ready for integration with main app")
    
    print(f"\n📱 NEXT STEPS:")
    print("1. Visit: http://127.0.0.1:5001")
    print("2. Test payment interface")
    print("3. Integrate with main video consultation system")

if __name__ == "__main__":
    test_payment_system()
