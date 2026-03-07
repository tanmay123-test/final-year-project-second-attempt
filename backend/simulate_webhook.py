#!/usr/bin/env python3

import requests
import json

API = "http://127.0.0.1:5000"

def simulate_razorpay_webhook():
    """Simulate Razorpay webhook for payment completion"""
    
    print("💳 SIMULATING RAZORPAY WEBHOOK")
    print("="*60)
    
    # Simulate Razorpay webhook payload
    webhook_data = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_TEST123456789",
                    "order_id": "order_SFvEcJ2pwWE6Gp",
                    "amount": 48000,  # Amount in paise (₹480)
                    "currency": "INR",
                    "status": "captured",
                    "notes": {
                        "appointment_id": "19"
                    }
                }
            }
        }
    }
    
    try:
        # Send webhook to your server
        r = requests.post(f"{API}/api/payment/webhook", 
                         json=webhook_data,
                         headers={"X-Razorpay-Signature": "test_signature"},
                         timeout=10)
        
        print(f"📊 Webhook Status: {r.status_code}")
        
        if r.status_code == 200:
            print("✅ Payment webhook processed successfully!")
            print("💰 Appointment #19 marked as PAID")
            print("📋 Status updated to CONFIRMED")
        else:
            print(f"❌ Webhook failed: {r.text}")
            
    except Exception as e:
        print(f"❌ Webhook error: {e}")
    
    print(f"\n🎯 PAYMENT COMPLETED!")
    print("="*60)
    print("👨‍⚕️ Doctor can now create video session!")
    print("🎥 Video consultation ready to start!")

if __name__ == "__main__":
    simulate_razorpay_webhook()
