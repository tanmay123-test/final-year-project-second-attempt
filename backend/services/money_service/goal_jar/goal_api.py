from flask import Flask, request, jsonify
from .goal_engine import GoalEngine
from datetime import datetime, timedelta
from auth_utils import verify_token, get_current_user_id
from user_db import UserDB

def _get_user_id_from_token():
    """Extract authenticated user_id from JWT token — delegates to shared auth_utils"""
    return get_current_user_id()

class GoalAPI:
    """REST API endpoints for goal jar management"""
    
    def __init__(self, app=None):
        self.app = app
        self.goal_engine = GoalEngine()
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Flask app with goal API endpoints"""
        self.app = app
        self.register_routes()
    
    def register_routes(self):
        """Register all API routes"""
        
        @self.app.route('/api/goal/create', methods=['POST'])
        def create_goal():
            """Create a new goal"""
            try:
                user_id = _get_user_id_from_token()
                if not user_id:
                    return jsonify({'error': 'Unauthorized'}), 401

                data = request.get_json()
                required_fields = ['goal_name', 'target_amount', 'monthly_contribution']
                for field in required_fields:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                goal_name = data['goal_name']
                target_amount = float(data['target_amount'])
                monthly_contribution = float(data['monthly_contribution'])
                target_date = data.get('target_date')
                
                if target_amount <= 0 or monthly_contribution <= 0:
                    return jsonify({'error': 'Target amount and monthly contribution must be positive'}), 400
                
                goal_id = self.goal_engine.create_goal(
                    user_id, goal_name, target_amount, monthly_contribution, target_date
                )
                
                return jsonify({
                    'success': True,
                    'data': {'goal_id': goal_id, 'message': 'Goal created successfully'}
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/goal/list', methods=['GET'])
        def list_goals():
            """Get all user goals"""
            try:
                user_id = _get_user_id_from_token()
                if not user_id:
                    return jsonify({'error': 'Unauthorized'}), 401
                
                goals = self.goal_engine.get_user_goals(user_id)
                summary = self.goal_engine.get_goal_summary(user_id)
                
                return jsonify({
                    'success': True,
                    'data': {'goals': goals, 'summary': summary}
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/goal/add-savings', methods=['POST'])
        def add_savings():
            """Add money to a goal"""
            try:
                user_id = _get_user_id_from_token()
                if not user_id:
                    return jsonify({'error': 'Unauthorized'}), 401

                data = request.get_json()
                required_fields = ['goal_id', 'amount']
                for field in required_fields:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                goal_id = data['goal_id']
                amount = float(data['amount'])
                payment_method = data.get('payment_method', 'manual')
                notes = data.get('notes', '')
                
                if amount <= 0:
                    return jsonify({'error': 'Amount must be positive'}), 400
                
                success = self.goal_engine.add_savings(user_id, goal_id, amount, payment_method, notes)
                
                return jsonify({
                    'success': success,
                    'data': {'message': 'Savings added successfully' if success else 'Failed to add savings'}
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/goal/payment/create-order', methods=['POST'])
        def goal_create_payment_order():
            """Create Razorpay order for goal savings"""
            try:
                user_id = _get_user_id_from_token()
                if not user_id:
                    # Debug: check what the token contains
                    auth = request.headers.get('Authorization', '')
                    print(f"[goal payment] Auth header present: {bool(auth)}, user_id resolved: {user_id}")
                    return jsonify({'error': 'Authentication failed — please log in again'}), 401

                data = request.get_json() or {}
                amount = data.get('amount')
                goal_id = data.get('goal_id')

                if not amount or not goal_id:
                    return jsonify({'error': 'amount and goal_id are required'}), 400

                amount = float(amount)
                if amount <= 0:
                    return jsonify({'error': 'Amount must be positive'}), 400

                import sys, os as _os
                _backend = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))))
                if _backend not in sys.path:
                    sys.path.insert(0, _backend)
                
                # Import config for the key
                try:
                    from config import RAZORPAY_KEY_ID
                except ImportError:
                    RAZORPAY_KEY_ID = _os.getenv('RAZORPAY_KEY_ID')

                from payment.payments.razor_service import create_order

                order = create_order(int(amount), f'goal_{goal_id}_user_{user_id}')
                return jsonify({
                    'success': True,
                    'order_id': order['id'],
                    'amount': int(amount),
                    'currency': 'INR',
                    'key': RAZORPAY_KEY_ID,
                })
            except Exception as e:
                print(f"Goal Payment Order Error: {str(e)}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/goal/payment/verify', methods=['POST'])
        def goal_verify_payment():
            """Verify Razorpay signature and record savings"""
            try:
                user_id = _get_user_id_from_token()
                if not user_id:
                    return jsonify({'error': 'Unauthorized'}), 401

                data = request.get_json() or {}
                order_id   = data.get('razorpay_order_id')
                payment_id = data.get('razorpay_payment_id')
                signature  = data.get('razorpay_signature')
                goal_id    = data.get('goal_id')
                amount     = data.get('amount')

                if not all([order_id, payment_id, signature, goal_id, amount]):
                    return jsonify({'error': 'Missing required fields'}), 400

                import hmac, hashlib, os as _os
                
                # Try to get secret from config
                try:
                    from config import RAZORPAY_KEY_SECRET
                    key_secret = RAZORPAY_KEY_SECRET
                except ImportError:
                    key_secret = _os.getenv('RAZORPAY_KEY_SECRET', '')

                body = f"{order_id}|{payment_id}"
                expected = hmac.new(key_secret.encode(), body.encode(), hashlib.sha256).hexdigest()

                if expected != signature:
                    return jsonify({'error': 'Payment verification failed'}), 400

                # Record savings
                self.goal_engine.add_savings(
                    user_id=user_id,
                    goal_id=int(goal_id),
                    amount=float(amount),
                    payment_method='razorpay',
                    notes=f'Razorpay {payment_id}'
                )
                return jsonify({'success': True, 'message': f'₹{amount} added to your goal!'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/goal/simulate', methods=['POST'])
        def simulate_goal():
            try:
                data = request.get_json()
                for field in ['target_amount', 'monthly_contribution']:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                target_amount = float(data['target_amount'])
                monthly_contribution = float(data['monthly_contribution'])
                if target_amount <= 0 or monthly_contribution <= 0:
                    return jsonify({'error': 'Invalid input values'}), 400
                timelines = self.goal_engine.simulate_timeline(target_amount, monthly_contribution)
                return jsonify({'success': True, 'data': {'timelines': timelines}})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/goal/progress', methods=['GET'])
        def get_goal_progress():
            try:
                user_id = _get_user_id_from_token()
                if not user_id:
                    return jsonify({'error': 'Unauthorized'}), 401
                goal_id = request.args.get('goal_id', type=int)
                if goal_id:
                    goal = self.goal_engine.get_goal_progress(user_id, goal_id)
                    return jsonify({'success': True, 'data': goal})
                else:
                    summary = self.goal_engine.get_goal_summary(user_id)
                    return jsonify({'success': True, 'data': summary})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/goal/transfer-leftover', methods=['POST'])
        def transfer_leftover():
            try:
                user_id = _get_user_id_from_token()
                if not user_id:
                    return jsonify({'error': 'Unauthorized'}), 401
                data = request.get_json()
                for field in ['goal_id', 'amount', 'source_category']:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                amount = float(data['amount'])
                if amount <= 0:
                    return jsonify({'error': 'Amount must be positive'}), 400
                success = self.goal_engine.transfer_leftover_to_goal(
                    user_id, data['goal_id'], amount, data['source_category']
                )
                return jsonify({
                    'success': success,
                    'data': {
                        'message': f'Transferred ₹{amount:.2f} from {data["source_category"]} to goal' if success else 'Transfer failed'
                    }
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/goal/notifications', methods=['GET'])
        def get_notifications():
            try:
                user_id = _get_user_id_from_token()
                if not user_id:
                    return jsonify({'error': 'Unauthorized'}), 401
                notifications = self.goal_engine.get_pending_notifications(user_id)
                return jsonify({'success': True, 'data': {'notifications': notifications}})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/goal/acceleration', methods=['GET'])
        def get_acceleration_suggestions():
            try:
                user_id = _get_user_id_from_token()
                if not user_id:
                    return jsonify({'error': 'Unauthorized'}), 401
                suggestions = self.goal_engine.get_goal_acceleration_suggestions(user_id)
                return jsonify({'success': True, 'data': {'suggestions': suggestions}})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/goal/projection', methods=['GET'])
        def get_savings_projection():
            try:
                user_id = _get_user_id_from_token()
                if not user_id:
                    return jsonify({'error': 'Unauthorized'}), 401
                goal_id = request.args.get('goal_id', type=int)
                months = request.args.get('months', 24, type=int)
                if not goal_id:
                    return jsonify({'error': 'goal_id parameter required'}), 400
                projections = self.goal_engine.calculate_savings_projection(user_id, goal_id, months)
                return jsonify({'success': True, 'data': {'projections': projections}})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

# Helper function to initialize API with Flask app
def create_goal_api(app):
    """Create and initialize goal API with Flask app"""
    api = GoalAPI(app)
    return api
