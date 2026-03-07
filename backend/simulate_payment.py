#!/usr/bin/env python3

import requests
import sqlite3

API = "http://127.0.0.1:5000"

def simulate_payment_completion():
    """Simulate payment completion for appointment #19"""
    
    print("💳 SIMULATING PAYMENT COMPLETION")
    print("="*60)
    
    # Update payment status in database directly
    try:
        conn = sqlite3.connect("data/expertease.db")
        cursor = conn.cursor()
        
        # Update appointment status to confirmed
        cursor.execute("""
            UPDATE appointments 
            SET status = 'confirmed', 
                payment_status = 'paid',
                payment_amount = 480
            WHERE id = 19
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Payment simulated successfully!")
        print("📋 Appointment #19 status: CONFIRMED")
        print("💰 Payment status: PAID")
        print("📊 Amount: ₹480")
        
    except Exception as e:
        print(f"❌ Error simulating payment: {e}")
        return
    
    print(f"\n🎯 NEXT: DOCTOR CAN NOW CREATE VIDEO SESSION!")
    print("="*60)
    print("👨‍⚕️ Doctor should now:")
    print("1. Go to Video Consultation → Create Video Session")
    print("2. Select Appointment #19")
    print("3. Get OTP and start video call")
    print("4. Patient can then join the call")

if __name__ == "__main__":
    simulate_payment_completion()
