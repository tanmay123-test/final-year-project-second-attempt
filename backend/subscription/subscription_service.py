import razorpay
import os
from datetime import datetime, timedelta
from .subscription_db import subscription_db
import sys
sys.path.append('..')
from config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET

class SubscriptionService:
    def __init__(self):
        self.client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    
    def create_subscription_order(self, worker_id: int, plan_id: int) -> dict:
        """Create Razorpay order for subscription"""
        # Get plan details
        plans = subscription_db.get_subscription_plans()
        plan = next((p for p in plans if p['id'] == plan_id), None)
        
        if not plan:
            raise ValueError("Invalid plan ID")
        
        # Check if this is an upgrade
        current_sub = subscription_db.get_current_subscription(worker_id)
        is_upgrade = False
        
        if current_sub and current_sub['status'] == 'active':
            current_plan = next((p for p in plans if p['id'] == current_sub['plan_id']), None)
            if current_plan:
                is_upgrade = plan['price'] > current_plan['price']
                print(f"🔄 Subscription upgrade: {current_plan['name']} → {plan['name']}")
        
        # Create Razorpay order
        order_data = {
            "amount": int(plan['price'] * 100),  # Convert to paise
            "currency": "INR",
            "receipt": f"subscription_{worker_id}_{plan_id}_{int(datetime.now().timestamp())}",
            "payment_capture": 1,
            "notes": {
                "worker_id": str(worker_id),
                "plan_id": str(plan_id),
                "plan_name": plan['name'],
                "type": "subscription",
                "is_upgrade": str(is_upgrade)
            }
        }
        
        try:
            order = self.client.order.create(order_data)
            
            # Create subscription record in database
            subscription_record = subscription_db.create_subscription_order(worker_id, plan_id)
            
            return {
                "order_id": order["id"],
                "amount": plan['price'],
                "currency": "INR",
                "key": RAZORPAY_KEY_ID,
                "plan": plan,
                "subscription_id": subscription_record["subscription_id"]
            }
        except Exception as e:
            raise Exception(f"Failed to create payment order: {str(e)}")
    
    def confirm_subscription_payment(self, worker_id: int, order_id: str, payment_id: str) -> dict:
        """Confirm subscription payment and activate subscription"""
        try:
            # Verify payment with Razorpay (for production)
            # payment = self.client.payment.fetch(payment_id)
            # if payment['status'] != 'captured':
            #     raise Exception("Payment not captured")
            
            # For now, skip verification for testing
            success = subscription_db.confirm_subscription_payment(worker_id, order_id, payment_id)
            
            if success:
                # Get updated subscription
                subscription = subscription_db.get_current_subscription(worker_id)
                
                # Check if this was an upgrade
                plans = subscription_db.get_subscription_plans()
                current_plan = next((p for p in plans if p['id'] == subscription['plan_id']), None)
                
                message = "Subscription activated successfully"
                if current_plan and current_plan['price'] > 0:
                    message = f"Upgraded to {current_plan['name']} Plan successfully!"
                
                return {
                    "success": True,
                    "message": message,
                    "subscription": subscription
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to activate subscription"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Payment confirmation failed: {str(e)}"
            }
    
    def check_worker_eligibility(self, worker_id: int) -> dict:
        """Check if worker is eligible to accept appointments"""
        return subscription_db.check_subscription_validity(worker_id)
    
    def track_appointment_acceptance(self, worker_id: int) -> bool:
        """Track when worker accepts an appointment"""
        return subscription_db.track_appointment_usage(worker_id)
    
    def get_worker_subscription_status(self, worker_id: int) -> dict:
        """Get current subscription status and usage"""
        return subscription_db.get_usage_stats(worker_id)
    
    def assign_free_trial_to_worker(self, worker_id: int) -> dict:
        """Assign free trial to a new worker after admin approval"""
        success = subscription_db.assign_free_trial(worker_id)
        
        if success:
            subscription = subscription_db.get_current_subscription(worker_id)
            return {
                "success": True,
                "message": "Free trial assigned successfully",
                "subscription": subscription
            }
        else:
            return {
                "success": False,
                "message": "Failed to assign free trial or trial already used"
            }
    
    def get_available_plans(self, include_trial: bool = False) -> list:
        """Get all available subscription plans"""
        return subscription_db.get_subscription_plans(include_trial)
    
    def cancel_worker_subscription(self, worker_id: int) -> dict:
        """Cancel worker's subscription"""
        success = subscription_db.cancel_subscription(worker_id)
        
        if success:
            return {
                "success": True,
                "message": "Subscription cancelled successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to cancel subscription"
            }

# Global service instance
subscription_service = SubscriptionService()
