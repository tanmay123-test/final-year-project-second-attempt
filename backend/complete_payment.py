#!/usr/bin/env python3

import sqlite3

def complete_payment_directly():
    """Complete payment directly in database for testing"""
    
    print("💳 COMPLETING PAYMENT DIRECTLY")
    print("="*60)
    
    try:
        conn = sqlite3.connect("data/expertease.db")
        cursor = conn.cursor()
        
        # Update appointment with payment details
        cursor.execute("""
            UPDATE appointments 
            SET status = 'confirmed',
                payment_status = 'paid',
                payment_amount = 480,
                razorpay_payment_id = 'pay_TEST123456789'
            WHERE id = 19
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Payment completed successfully!")
        print("📋 Appointment #19 status: CONFIRMED")
        print("💰 Payment status: PAID")
        print("💳 Payment ID: pay_TEST123456789")
        print("📊 Amount: ₹480")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print(f"\n🎯 READY FOR VIDEO CONSULTATION!")
    print("="*60)
    print("👨‍⚕️ Doctor can now:")
    print("1. Login and go to Video Consultation")
    print("2. Create Video Session for Appointment #19")
    print("3. Get OTP and start video call")
    print("4. Patient can join the live call")
    
    print(f"\n👤 Patient can:")
    print("1. Go to Video Consultation")
    print("2. Join Live Consultation for Appointment #19")
    print("3. Connect to video call with doctor")

if __name__ == "__main__":
    complete_payment_directly()
