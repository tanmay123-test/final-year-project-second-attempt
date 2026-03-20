from flask import Blueprint, request, jsonify
from .subscription_service import subscription_service
from .subscription_db import subscription_db

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/api/subscription/plans', methods=['GET'])
def get_subscription_plans():
    """Get all available subscription plans"""
    try:
        include_trial = request.args.get('include_trial', 'false').lower() == 'true'
        plans = subscription_service.get_available_plans(include_trial)
        
        return jsonify({
            "success": True,
            "plans": plans
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@subscription_bp.route('/api/subscription/current', methods=['GET'])
def get_current_subscription():
    """Get worker's current subscription status"""
    try:
        # Get worker_id from authentication (you'll need to implement this)
        worker_id = request.args.get('worker_id')
        if not worker_id:
            return jsonify({
                "success": False,
                "error": "Worker ID required"
            }), 400
        
        subscription_status = subscription_db.get_current_subscription(int(worker_id))
        
        if subscription_status:
            return jsonify({
                "success": True,
                "subscription": subscription_status
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "No active subscription found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@subscription_bp.route('/api/subscription/create-order', methods=['POST'])
def create_subscription_order():
    """Create subscription payment order"""
    try:
        data = request.get_json()
        worker_id = data.get('worker_id')
        plan_id = data.get('plan_id')
        
        if not worker_id or not plan_id:
            return jsonify({
                "success": False,
                "error": "Worker ID and Plan ID required"
            }), 400
        
        # Check if worker already has active subscription
        current_sub = subscription_db.get_current_subscription(int(worker_id))
        
        # Allow upgrades - if user has active subscription, allow upgrade to higher plan
        if current_sub and current_sub['status'] == 'active':
            # Get current and new plan details
            current_plan_id = current_sub['plan_id']
            new_plan_id = int(plan_id)
            
            # Get plan details to check if this is an upgrade
            plans = subscription_db.get_subscription_plans()
            current_plan = next((p for p in plans if p['id'] == current_plan_id), None)
            new_plan = next((p for p in plans if p['id'] == new_plan_id), None)
            
            if current_plan and new_plan:
                # Allow if upgrading to higher tier or same price (downgrade allowed)
                if new_plan['price'] < current_plan['price']:
                    return jsonify({
                        "success": False,
                        "error": "Cannot downgrade to lower priced plan. Please contact support."
                    }), 400
        
        order = subscription_service.create_subscription_order(int(worker_id), int(plan_id))
        
        return jsonify({
            "success": True,
            "order": order
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@subscription_bp.route('/api/subscription/confirm', methods=['POST'])
def confirm_subscription_payment():
    """Confirm subscription payment (temporary API)"""
    try:
        data = request.get_json()
        worker_id = data.get('worker_id')
        order_id = data.get('order_id')
        payment_id = data.get('payment_id')
        
        if not worker_id or not order_id or not payment_id:
            return jsonify({
                "success": False,
                "error": "Worker ID, Order ID, and Payment ID required"
            }), 400
        
        result = subscription_service.confirm_subscription_payment(
            int(worker_id), order_id, payment_id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@subscription_bp.route('/api/subscription/check-eligibility/<int:worker_id>', methods=['GET'])
def check_subscription_eligibility(worker_id):
    """Check if worker is eligible to accept appointments"""
    try:
        eligibility = subscription_service.check_worker_eligibility(worker_id)
        
        return jsonify({
            "success": True,
            "eligible": eligibility['valid'],
            "error": eligibility.get('error'),
            "subscription": eligibility.get('subscription')
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@subscription_bp.route('/api/subscription/track-usage', methods=['POST'])
def track_appointment_usage():
    """Track appointment usage when worker accepts appointment"""
    try:
        data = request.get_json()
        worker_id = data.get('worker_id')
        
        if not worker_id:
            return jsonify({
                "success": False,
                "error": "Worker ID required"
            }), 400
        
        success = subscription_service.track_appointment_acceptance(int(worker_id))
        
        return jsonify({
            "success": success,
            "message": "Usage tracked successfully" if success else "Failed to track usage"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@subscription_bp.route('/api/subscription/assign-trial/<int:worker_id>', methods=['POST'])
def assign_free_trial(worker_id):
    """Assign free trial to worker (called after admin approval)"""
    try:
        result = subscription_service.assign_free_trial_to_worker(worker_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@subscription_bp.route('/api/subscription/cancel/<int:worker_id>', methods=['POST'])
def cancel_subscription(worker_id):
    """Cancel worker's subscription"""
    try:
        result = subscription_service.cancel_worker_subscription(worker_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@subscription_bp.route('/api/subscription/stats/<int:worker_id>', methods=['GET'])
def get_subscription_stats(worker_id):
    """Get subscription usage statistics"""
    try:
        stats = subscription_service.get_worker_subscription_status(worker_id)
        
        if stats:
            return jsonify({
                "success": True,
                "stats": stats
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "No subscription found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
