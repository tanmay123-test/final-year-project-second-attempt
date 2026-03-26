from flask import Blueprint, request, jsonify
from ..services.money_service import money_service
from auth_utils import verify_token
from user_db import UserDB
from worker_db import WorkerDB

money_bp = Blueprint('money', __name__)

def get_current_user_id():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    from auth_utils import verify_token
    username_or_email = verify_token(token)
    if not username_or_email:
        return None
    try:
        from user_db import UserDB
        user_db = UserDB()
        # Try username first
        user_id = user_db.get_user_by_username(username_or_email)
        if not user_id:
            # Try email fallback
            user = user_db.get_user_by_email(username_or_email)
            if user:
                user_id = user.get('id') or user.get('user_id')
        return user_id
    except Exception as e:
        print(f"get_current_user_id error: {e}")
        return None

@money_bp.route('/api/money/dashboard', methods=['GET'])
def get_dashboard_data():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        dashboard_data = money_service.get_dashboard_data(user_id)
        return jsonify(dashboard_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@money_bp.route('/api/money/transactions', methods=['POST'])
def add_transaction():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    try:
        transaction_id = money_service.add_transaction(
            user_id=user_id,
            category=data.get('category'),
            amount=data.get('amount'),
            description=data.get('description', ''),
            date=data.get('date'),
            transaction_type=data.get('type', 'expense'),
            merchant=data.get('merchant', '')
        )
        return jsonify({"success": True, "transaction_id": transaction_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@money_bp.route('/api/money/transactions', methods=['GET'])
def get_transactions():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Pass query params as filters
        category   = request.args.get('category')
        start_date = request.args.get('start_date')
        end_date   = request.args.get('end_date')
        limit      = request.args.get('limit', type=int)

        transactions = money_service.get_transactions(
            user_id,
            limit=limit,
            category=category,
            start_date=start_date,
            end_date=end_date
        )
        return jsonify({"transactions": transactions}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@money_bp.route('/api/money/budget', methods=['POST'])
def set_budget():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    try:
        budget_id = money_service.set_budget(
            user_id=user_id,
            category=data.get('category'),
            amount=data.get('amount'),
            period=data.get('period', 'monthly')
        )
        return jsonify({"success": True, "budget_id": budget_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@money_bp.route('/api/money/budget', methods=['GET'])
def get_budgets():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        budgets = money_service.get_budgets(user_id)
        return jsonify({"budgets": budgets}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@money_bp.route('/api/money/goals', methods=['POST'])
def create_goal():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    try:
        goal_id = money_service.create_goal(
            user_id=user_id,
            name=data.get('name'),
            target_amount=data.get('target_amount'),
            current_amount=data.get('current_amount', 0),
            deadline=data.get('deadline'),
            category=data.get('category')
        )
        return jsonify({"success": True, "goal_id": goal_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@money_bp.route('/api/money/goals', methods=['GET'])
def get_goals():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        goals = money_service.get_goals(user_id)
        return jsonify({"goals": goals}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@money_bp.route('/api/money/analytics/monthly', methods=['GET'])
def get_monthly_analytics():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        months = request.args.get('months', 6, type=int)
        analytics = money_service.get_monthly_analytics(user_id, months)
        return jsonify(analytics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@money_bp.route('/api/money/chat', methods=['POST'])
def chat_with_ai():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    message = data.get('message')
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    try:
        response = money_service.chat_with_ai(user_id, message)
        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
