"""
AI Trip Planner API Routes
Flask routes for trip planning functionality
"""

import os
import sys
from flask import Blueprint, request, jsonify
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_utils import verify_token
from user_db import UserDB
from car_service.trip_service import trip_service

# Create Blueprint
trip_bp = Blueprint('trip_planner', __name__)

def _current_user_id():
    """Get current authenticated user ID"""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth.split(" ")[1]
    username = verify_token(token)
    if not username:
        return None
    db = UserDB()
    user = db.get_user_by_username(username)
    return user.get('user_id') if user else None

@trip_bp.route('/api/car/ai/trip-plan', methods=['POST'])
def plan_trip():
    """
    Plan a trip with AI assistance
    
    Expected JSON payload:
    {
        "start": "Mumbai",
        "destination": "Pune", 
        "mileage": 20,
        "fuel_price": 105
    }
    
    Returns:
    {
        "success": true,
        "trip_plan": {
            "start": "Mumbai",
            "destination": "Pune",
            "distance_km": 150.5,
            "duration_hours": 3.2,
            "fuel_needed": 7.5,
            "fuel_cost": 787.5,
            "toll_cost": 112.9,
            "total_cost": 900.4,
            "checklist": ["Check tyre pressure", ...]
        }
    }
    """
    try:
        # Get authenticated user
        user_id = _current_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Extract required fields
        start = data.get('start', '').strip()
        destination = data.get('destination', '').strip()
        mileage = data.get('mileage', 0)
        fuel_price = data.get('fuel_price', 0)
        
        # Validate required fields
        missing_fields = []
        if not start:
            missing_fields.append('start')
        if not destination:
            missing_fields.append('destination')
        if mileage <= 0:
            missing_fields.append('mileage (must be > 0)')
        if fuel_price <= 0:
            missing_fields.append('fuel_price (must be > 0)')
        
        if missing_fields:
            return jsonify({
                "error": f"Missing or invalid required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Plan the trip
        trip_plan = trip_service.plan_trip(start, destination, mileage, fuel_price)
        
        if not trip_plan:
            return jsonify({
                "error": "Failed to plan trip. Please check the locations and try again."
            }), 400
        
        # Return success response
        return jsonify({
            "success": True,
            "trip_plan": trip_plan
        }), 200
        
    except Exception as e:
        print(f"❌ Error in trip planning API: {e}")
        return jsonify({
            "error": "Internal server error while planning trip"
        }), 500

@trip_bp.route('/api/car/ai/trip-validate', methods=['POST'])
def validate_trip_request():
    """
    Validate trip planning request without actually planning the trip
    
    Expected JSON payload:
    {
        "start": "Mumbai",
        "destination": "Pune",
        "mileage": 20,
        "fuel_price": 105
    }
    
    Returns:
    {
        "valid": true,
        "errors": []
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Extract fields
        start = data.get('start', '').strip()
        destination = data.get('destination', '').strip()
        mileage = data.get('mileage', 0)
        fuel_price = data.get('fuel_price', 0)
        
        # Validate
        validation = trip_service.validate_trip_request(start, destination, mileage, fuel_price)
        
        return jsonify(validation), 200
        
    except Exception as e:
        print(f"❌ Error in trip validation API: {e}")
        return jsonify({
            "error": "Internal server error while validating trip"
        }), 500

@trip_bp.route('/api/car/ai/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for trip planner service
    
    Returns:
    {
        "status": "healthy",
        "service": "AI Trip Planner"
    }
    """
    try:
        return jsonify({
            "status": "healthy",
            "service": "AI Trip Planner",
            "version": "1.0.0"
        }), 200
    except Exception as e:
        print(f"❌ Error in health check: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500
