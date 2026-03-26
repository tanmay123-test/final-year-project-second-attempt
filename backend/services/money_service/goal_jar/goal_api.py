from flask import Flask, request, jsonify
from .goal_engine import GoalEngine
from datetime import datetime, timedelta
from auth_utils import verify_token
from user_db import UserDB

def _get_user_id_from_token():
    """Extract authenticated user_id from JWT token"""
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    token = auth.split(' ')[1]
    username = verify_token(token)
    if not username:
        return None
    return UserDB().get_user_by_username(username)

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
                return jsonify({'success': success, 'data': {'message': f'Transferred ₹{amount:.2f}' if success else 'Transfer failed'}})
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
