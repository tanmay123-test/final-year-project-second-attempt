# payment_service.py
# Razorpay Payment Integration for ExpertEase Healthcare

import os
import razorpay
from dotenv import load_dotenv
from datetime import datetime
import sqlite3
from config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, PLATFORM_COMMISSION_RATE

load_dotenv()

class PaymentService:
    def __init__(self):
        self.client = razorpay.Client(auth=(
            RAZORPAY_KEY_ID,
            RAZORPAY_KEY_SECRET
        ))
        self.platform_commission = PLATFORM_COMMISSION_RATE  # 20% platform commission
    
    def calculate_payment_amount(self, doctor_fee):
        """
        Calculate total payment amount including platform commission
        Backend ONLY calculation - never trust frontend
        """
        platform_fee = int(doctor_fee * self.platform_commission)
        total_amount = doctor_fee + platform_fee
        
        return {
            "doctor_fee": doctor_fee,
            "platform_fee": platform_fee,
            "total_amount": total_amount
        }
    
    def create_payment_order(self, appointment_id, doctor_fee):
        """
        Create Razorpay order for appointment payment
        """
        # Calculate pricing
        pricing = self.calculate_payment_amount(doctor_fee)
        total_amount = pricing["total_amount"]
        
        # Create Razorpay order
        order = self.client.order.create({
            "amount": total_amount * 100,  # Razorpay uses paise
            "currency": "INR",
            "receipt": f"APT_{appointment_id}",
            "payment_capture": 1,
            "notes": {
                "appointment_id": str(appointment_id),
                "doctor_fee": str(doctor_fee),
                "platform_fee": str(pricing["platform_fee"])
            }
        })
        
        # Update appointment with order details
        self._save_order_to_appointment(appointment_id, order["id"], total_amount)
        
        return {
            "order_id": order["id"],
            "amount": total_amount,
            "currency": "INR",
            "key": RAZORPAY_KEY_ID,
            "pricing_breakdown": pricing
        }
    
    def _save_order_to_appointment(self, appointment_id, order_id, amount):
        """Save order details to appointment record"""
        conn = sqlite3.connect("data/expertease.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE appointments 
            SET razorpay_order_id=?, payment_amount=?, payment_status='payment_pending'
            WHERE id=?
        """, (order_id, amount, appointment_id))
        
        conn.commit()
        conn.close()
    
    def confirm_payment(self, appointment_id, razorpay_payment_id):
        """
        Confirm payment and update appointment status
        Temporary method - will be replaced by webhook
        """
        conn = sqlite3.connect("data/expertease.db")
        cursor = conn.cursor()
        
        # Update appointment with payment confirmation
        cursor.execute("""
            UPDATE appointments 
            SET razorpay_payment_id=?, payment_status='paid', status='confirmed'
            WHERE id=? AND payment_status='payment_pending'
        """, (razorpay_payment_id, appointment_id))
        
        conn.commit()
        
        # Check if update was successful
        cursor.execute("SELECT changes()")
        changes = cursor.fetchone()[0]
        
        conn.close()
        
        return changes > 0
    
    def get_appointment_payment_status(self, appointment_id):
        """Get payment status for an appointment"""
        conn = sqlite3.connect("data/expertease.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT payment_status, payment_amount, razorpay_order_id, 
                   razorpay_payment_id, payout_status
            FROM appointments WHERE id=?
        """, (appointment_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "payment_status": result[0],
                "payment_amount": result[1],
                "razorpay_order_id": result[2],
                "razorpay_payment_id": result[3],
                "payout_status": result[4]
            }
        return None
    
    def verify_payment_with_razorpay(self, razorpay_payment_id):
        """
        Verify payment with Razorpay API
        Additional security check
        """
        # Skip Razorpay verification for test payments
        if razorpay_payment_id.startswith('test_payment_'):
            print(f"⚠️ Skipping Razorpay verification for test payment: {razorpay_payment_id}")
            return True
            
        try:
            payment = self.client.payment.fetch(razorpay_payment_id)
            return payment.get('status') == 'captured'
        except Exception as e:
            print(f"Payment verification failed: {e}")
            return False

# Global payment service instance
payment_service = PaymentService()
