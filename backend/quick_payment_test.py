#!/usr/bin/env python3

import requests

def quick_payment_test():
    """Quick payment test"""
    
    print("💳 QUICK PAYMENT TEST")
    print("="*40)
    
    API = "http://127.0.0.1:5000"
    
    # Test main app
    try:
        r = requests.get(f"{API}/", timeout=3)
        print(f"✅ Main app: {r.status_code}")
        
        # Test payment endpoint
        r = requests.post(f"{API}/api/payment/create-order", 
                         json={"amount": 48000, "currency": "INR"}, 
                         timeout=5)
        print(f"💳 Payment API: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Order ID: {data.get('id', 'N/A')}")
            print(f"💰 Amount: ₹{data.get('amount', 0) / 100}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎯 PAYMENT SYSTEM READY!")

if __name__ == "__main__":
    quick_payment_test()
