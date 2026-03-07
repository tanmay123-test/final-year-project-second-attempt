"""
Car Service Earnings API Routes
Handles earnings, stats, and fairness insights for mechanics
"""

import sys
import os
from datetime import datetime
from flask import Blueprint, request, jsonify

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_utils import verify_token
from services.car_service.job_requests_db import job_requests_db
from services.car_service.car_service_worker_db import car_service_worker_db
from services.car_service.dispatch.bonus_engine import bonus_engine

earnings_bp = Blueprint("earnings", __name__)

@earnings_bp.route("/api/car/mechanic/earnings", methods=["GET"])
def get_earnings():
    """Get mechanic earnings summary"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        # Get mechanic from unified worker database
        mechanic = car_service_worker_db.get_worker_by_email(email)
        if not mechanic or mechanic.get('role') != 'Mechanic':
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Get earnings summary
        earnings = job_requests_db.get_mechanic_earnings_summary(mechanic['id'])
        
        return jsonify({
            "success": True,
            "earnings": earnings,
            "message": "Earnings retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"❌ Get earnings error: {e}")
        return jsonify({"error": "Failed to get earnings"}), 500

@earnings_bp.route("/api/car/mechanic/earnings/history", methods=["GET"])
def get_earnings_history():
    """Get mechanic earnings history"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        mechanic = car_service_worker_db.get_worker_by_email(email)
        if not mechanic or mechanic.get('role') != 'Mechanic':
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Get limit from query params (default 20)
        limit = request.args.get('limit', 20, type=int)
        limit = min(limit, 50)  # Max 50 records
        
        # Get earnings history
        history = job_requests_db.get_mechanic_earnings_history(mechanic['id'], limit)
        
        return jsonify({
            "success": True,
            "history": history,
            "count": len(history),
            "message": "Earnings history retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"❌ Get earnings history error: {e}")
        return jsonify({"error": "Failed to get earnings history"}), 500

@earnings_bp.route("/api/car/mechanic/stats", methods=["GET"])
def get_mechanic_stats():
    """Get mechanic stats including fairness score"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        mechanic = car_service_worker_db.get_worker_by_email(email)
        if not mechanic or mechanic.get('role') != 'Mechanic':
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Get mechanic stats
        stats = job_requests_db.get_mechanic_stats(mechanic['id'])
        
        return jsonify({
            "success": True,
            "stats": stats,
            "message": "Mechanic stats retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"❌ Get mechanic stats error: {e}")
        return jsonify({"error": "Failed to get mechanic stats"}), 500

@earnings_bp.route("/api/car/mechanic/fairness-insights", methods=["GET"])
def get_fairness_insights():
    """Get fairness insights for transparency"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        mechanic = car_service_worker_db.get_worker_by_email(email)
        if not mechanic or mechanic.get('role') != 'Mechanic':
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Get fairness insights
        insights = job_requests_db.get_fairness_insights(mechanic['id'])
        
        return jsonify({
            "success": True,
            "insights": insights,
            "message": "Fairness insights retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"❌ Get fairness insights error: {e}")
        return jsonify({"error": "Failed to get fairness insights"}), 500

@earnings_bp.route("/api/car/mechanic/bonus-calculation", methods=["POST"])
def calculate_bonus():
    """Calculate bonus for a job (for testing)"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        mechanic = car_service_worker_db.get_worker_by_email(email)
        if not mechanic or mechanic.get('role') != 'Mechanic':
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Get job data from request
        job_data = request.json
        if not job_data:
            return jsonify({"error": "Job data is required"}), 400
        
        # Calculate bonus
        bonus = bonus_engine.calculate_bonus(job_data)
        breakdown = bonus_engine.get_bonus_breakdown(job_data)
        
        return jsonify({
            "success": True,
            "bonus": bonus,
            "breakdown": breakdown,
            "message": "Bonus calculated successfully"
        }), 200
        
    except Exception as e:
        print(f"❌ Calculate bonus error: {e}")
        return jsonify({"error": "Failed to calculate bonus"}), 500

@earnings_bp.route("/api/car/mechanic/commission-info", methods=["GET"])
def get_commission_info():
    """Get commission information for transparency"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        mechanic = car_service_worker_db.get_worker_by_email(email)
        if not mechanic or mechanic.get('role') != 'Mechanic':
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Return commission structure
        commission_info = {
            "platform_commission_rate": 0.20,  # 20%
            "mechanic_share_rate": 0.80,  # 80%
            "description": "Platform takes 20% commission, you keep 80%",
            "example": {
                "customer_pays": 500,
                "platform_commission": 100,
                "mechanic_earning": 400
            },
            "bonus_types": [
                {
                    "type": "Emergency Job",
                    "amount": 100,
                    "condition": "Priority emergency jobs"
                },
                {
                    "type": "Night Shift",
                    "amount": 50,
                    "condition": "10 PM - 6 AM"
                },
                {
                    "type": "Long Distance",
                    "amount": 50,
                    "condition": "More than 20 km"
                },
                {
                    "type": "Complex Job",
                    "amount": 30,
                    "condition": "Engine, transmission, electrical"
                },
                {
                    "type": "Remote Location",
                    "amount": 40,
                    "condition": "Remote areas"
                },
                {
                    "type": "Weekend",
                    "amount": 20,
                    "condition": "Saturday/Sunday"
                }
            ]
        }
        
        return jsonify({
            "success": True,
            "commission_info": commission_info,
            "message": "Commission information retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"❌ Get commission info error: {e}")
        return jsonify({"error": "Failed to get commission info"}), 500
