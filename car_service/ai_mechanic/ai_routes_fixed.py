"""
AI Mechanic Routes - API Endpoints for AI Trip Planning
"""

from flask import Blueprint, request, jsonify
import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

from ai_mechanic.ai_agent import ai_agent
from car_service.car_profile_db import car_profile_db
from auth_utils import verify_token
from user_db import user_db

# Create blueprint
ai_mechanic_bp = Blueprint('ai_mechanic', __name__)

# Inject car database dependency
ai_agent.set_car_db(car_profile_db)

@ai_mechanic_bp.route('/api/car/ai/trip-plan', methods=['POST'])
def plan_trip():
    """AI Trip Planning Endpoint"""
    try:
        # Get JWT token from headers
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authentication required", "status": "error"}), 401
        
        token = auth_header.split(' ')[1]
        username = verify_token(token)
        
        if not username:
            return jsonify({"error": "Invalid or expired token", "status": "error"}), 401
        
        # Get user ID from main user database
        user = user_db.get_user_by_username(username)
        if not user:
            return jsonify({"error": "User not found", "status": "error"}), 404
        
        user_id = user['id']
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request data required", "status": "error"}), 400
        
        from_city = data.get('from_city')
        to_city = data.get('to_city')
        
        if not from_city or not to_city:
            return jsonify({"error": "Both from_city and to_city are required", "status": "error"}), 400
        
        # Generate AI trip plan
        trip_plan = ai_agent.generate_trip_plan(user_id, from_city, to_city)
        
        if trip_plan.get('status') == 'error':
            return jsonify(trip_plan), 400
        
        return jsonify({"success": True, "trip_plan": trip_plan}), 200
        
    except Exception as e:
        return jsonify({"error": f"Trip planning failed: {str(e)}", "status": "error"}), 500
