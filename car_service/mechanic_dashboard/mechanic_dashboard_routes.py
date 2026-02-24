"""
Mechanic Dashboard API Routes - Fixed Version
Complete REST API for mechanic worker management system
"""

from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth_utils import verify_token
from ..worker_auth.worker_routes import get_current_worker, car_worker_db
from .mechanic_dashboard_service import mechanic_dashboard_service

# Create blueprint
mechanic_dashboard_bp = Blueprint("mechanic_dashboard", __name__)

def require_mechanic_auth(f):
    """Decorator to require authenticated mechanic"""
    def wrapper(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authentication required"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        username = verify_token(token)
        if not username:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Get worker and validate it's a mechanic
        worker = car_worker_db.get_worker_by_username(username)
        if not worker or worker['worker_type'] != 'MECHANIC':
            return jsonify({"error": "Mechanic access required"}), 403
        
        if worker['status'] != 'APPROVED':
            return jsonify({"error": "Mechanic account not approved"}), 403
        
        # Add worker to request context
        request.current_worker = worker
        return f(*args, **kwargs)
    
    wrapper.__name__ = f.__name__
    return wrapper

# ==================== ONLINE STATUS & DEMAND ====================

@mechanic_dashboard_bp.route("/api/car/mechanic/status", methods=["GET"])
@require_mechanic_auth
def get_mechanic_status():
    """Get mechanic current status and demand analysis"""
    try:
        mechanic_id = request.current_worker['id']
        result = mechanic_dashboard_service.get_demand_status(mechanic_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get status: {str(e)}"}), 500

@mechanic_dashboard_bp.route("/api/car/mechanic/toggle-online", methods=["POST"])
@require_mechanic_auth
def toggle_online_status():
    """Toggle mechanic online/offline status"""
    try:
        mechanic_id = request.current_worker['id']
        result = mechanic_dashboard_service.toggle_online_status(mechanic_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to toggle status: {str(e)}"}), 500

# ==================== JOB REQUESTS ====================

@mechanic_dashboard_bp.route("/api/car/mechanic/job-requests", methods=["GET"])
@require_mechanic_auth
def get_job_requests():
    """Get transparent job requests"""
    try:
        mechanic_id = request.current_worker['id']
        result = mechanic_dashboard_service.get_transparent_job_requests(mechanic_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get job requests: {str(e)}"}), 500

@mechanic_dashboard_bp.route("/api/car/mechanic/accept-job/<int:job_id>", methods=["POST"])
@require_mechanic_auth
def accept_job(job_id):
    """Accept a job request"""
    try:
        mechanic_id = request.current_worker['id']
        result = mechanic_dashboard_service.accept_job_request(mechanic_id, job_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to accept job: {str(e)}"}), 500

# ==================== ACTIVE JOBS ====================

@mechanic_dashboard_bp.route("/api/car/mechanic/active-jobs", methods=["GET"])
@require_mechanic_auth
def get_active_jobs():
    """Get mechanic's active jobs"""
    try:
        mechanic_id = request.current_worker['id']
        result = mechanic_dashboard_service.get_active_jobs(mechanic_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get active jobs: {str(e)}"}), 500

# ==================== EARNINGS ====================

@mechanic_dashboard_bp.route("/api/car/mechanic/earnings", methods=["GET"])
@require_mechanic_auth
def get_earnings():
    """Get earnings insights"""
    try:
        mechanic_id = request.current_worker['id']
        period = request.args.get('period', 'all')
        result = mechanic_dashboard_service.get_earnings_insights(mechanic_id, period)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get earnings: {str(e)}"}), 500

# ==================== PERFORMANCE ====================

@mechanic_dashboard_bp.route("/api/car/mechanic/performance", methods=["GET"])
@require_mechanic_auth
def get_performance():
    """Get performance metrics and safety insights"""
    try:
        mechanic_id = request.current_worker['id']
        result = mechanic_dashboard_service.get_performance_safety(mechanic_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get performance: {str(e)}"}), 500

# ==================== EMERGENCY SOS ====================

@mechanic_dashboard_bp.route("/api/car/mechanic/emergency-alert", methods=["POST"])
@require_mechanic_auth
def trigger_emergency():
    """Trigger emergency SOS alert"""
    try:
        mechanic_id = request.current_worker['id']
        data = request.get_json() or {}
        
        lat = data.get('latitude')
        lng = data.get('longitude')
        
        if lat is None or lng is None:
            return jsonify({"error": "Location coordinates required"}), 400
        
        result = mechanic_dashboard_service.trigger_emergency_sos(mechanic_id, lat, lng)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to trigger emergency: {str(e)}"}), 500

# ==================== ERROR HANDLING ====================

@mechanic_dashboard_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@mechanic_dashboard_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

@mechanic_dashboard_bp.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return jsonify({"error": "Access forbidden"}), 403
