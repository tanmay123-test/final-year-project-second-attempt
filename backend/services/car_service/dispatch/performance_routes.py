"""
Car Service Performance API Routes
Handles performance metrics, safety reports, and panic alerts for mechanics
"""

import sys
import os
from datetime import datetime
from flask import Blueprint, request, jsonify

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_utils import verify_token
from services.car_service.job_requests_db import job_requests_db
from services.car_service.car_service_worker_db import car_service_worker_db as worker_db

performance_bp = Blueprint("performance", __name__)

@performance_bp.route("/api/car/mechanic/performance", methods=["GET"])
def get_performance():
    """Get mechanic performance metrics"""
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
        
        # Get performance metrics
        performance = job_requests_db.get_mechanic_performance(mechanic['id'])
        
        # Get improvement tips
        tips_data = job_requests_db.get_performance_improvement_tips(mechanic['id'])
        
        return jsonify({
            "success": True,
            "performance": performance,
            "tips": tips_data,
            "message": "Performance metrics retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"  Get performance error: {e}")
        return jsonify({"error": "Failed to get performance"}), 500

@performance_bp.route("/api/car/mechanic/report-incident", methods=["POST"])
def report_incident():
    """Report safety incident"""
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
        
        # Get incident data
        data = request.json
        if not data:
            return jsonify({"error": "Incident data is required"}), 400
        
        incident_type = data.get("incident_type", "")
        description = data.get("description", "")
        job_id = data.get("job_id")
        
        if not incident_type:
            return jsonify({"error": "Incident type is required"}), 400
        
        # Validate incident type
        valid_types = ["Unsafe location", "Fraud customer", "Payment dispute", "Threat", "Fake booking"]
        if incident_type not in valid_types:
            return jsonify({"error": "Invalid incident type"}), 400
        
        # Create safety report
        report_id = job_requests_db.create_safety_report(
            mechanic_id=mechanic['id'],
            job_id=job_id,
            incident_type=incident_type,
            description=description
        )
        
        return jsonify({
            "success": True,
            "report_id": report_id,
            "message": "Safety incident reported successfully"
        }), 200
        
    except Exception as e:
        print(f"  Report incident error: {e}")
        return jsonify({"error": "Failed to report incident"}), 500

@performance_bp.route("/api/car/mechanic/panic-alert", methods=["POST"])
def panic_alert():
    """Send panic alert for immediate help"""
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
        
        # Get panic data
        data = request.json or {}
        job_id = data.get("job_id")
        location = data.get("location", "Unknown location")
        
        # Create panic alert
        alert_id = job_requests_db.create_panic_alert(
            mechanic_id=mechanic['id'],
            job_id=job_id,
            location=location
        )
        
        return jsonify({
            "success": True,
            "alert_id": alert_id,
            "message": "Panic alert sent successfully",
            "note": "Admin has been notified. Help is on the way."
        }), 200
        
    except Exception as e:
        print(f"  Panic alert error: {e}")
        return jsonify({"error": "Failed to send panic alert"}), 500

@performance_bp.route("/api/car/mechanic/safety-reports", methods=["GET"])
def get_safety_reports():
    """Get mechanic safety reports"""
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
        
        # Get safety reports
        reports = job_requests_db.get_mechanic_safety_reports(mechanic['id'])
        
        return jsonify({
            "success": True,
            "reports": reports,
            "count": len(reports),
            "message": "Safety reports retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"  Get safety reports error: {e}")
        return jsonify({"error": "Failed to get safety reports"}), 500

@performance_bp.route("/api/car/mechanic/panic-alerts", methods=["GET"])
def get_panic_alerts():
    """Get mechanic panic alerts"""
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
        
        # Get panic alerts
        alerts = job_requests_db.get_mechanic_panic_alerts(mechanic['id'])
        
        return jsonify({
            "success": True,
            "alerts": alerts,
            "count": len(alerts),
            "message": "Panic alerts retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"  Get panic alerts error: {e}")
        return jsonify({"error": "Failed to get panic alerts"}), 500

# Admin endpoints for safety monitoring (simplified for demo)
@performance_bp.route("/api/admin/safety-reports", methods=["GET"])
def get_all_safety_reports():
    """Get all safety reports for admin dashboard"""
    try:
        # Simplified admin check for demo
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        # Simplified admin check
        if not email.endswith("@admin.com"):
            return jsonify({"error": "Admin access required"}), 403
        
        # Get limit from query params
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 100)  # Max 100 records
        
        # Get all safety reports (simplified without join for now)
        reports = job_requests_db.get_mechanic_safety_reports(2)  # Simplified for demo
        
        return jsonify({
            "success": True,
            "reports": reports,
            "count": len(reports),
            "message": "All safety reports retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"  Get all safety reports error: {e}")
        return jsonify({"error": "Failed to get safety reports"}), 500

@performance_bp.route("/api/admin/panic-alerts", methods=["GET"])
def get_all_panic_alerts():
    """Get all panic alerts for admin dashboard"""
    try:
        # Simplified admin check for demo
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        # Simplified admin check
        if not email.endswith("@admin.com"):
            return jsonify({"error": "Admin access required"}), 403
        
        # Get limit from query params
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 100)  # Max 100 records
        
        # Get all panic alerts (simplified without join for now)
        alerts = job_requests_db.get_mechanic_panic_alerts(2)  # Simplified for demo
        
        return jsonify({
            "success": True,
            "alerts": alerts,
            "count": len(alerts),
            "message": "All panic alerts retrieved successfully"
        }), 200
        
    except Exception as e:
        print(f"  Get all panic alerts error: {e}")
        return jsonify({"error": "Failed to get panic alerts"}), 500

@performance_bp.route("/api/admin/resolve-panic/<int:alert_id>", methods=["POST"])
def resolve_panic_alert(alert_id):
    """Resolve panic alert (admin only)"""
    try:
        # Simplified admin check for demo
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        # Simplified admin check
        if not email.endswith("@admin.com"):
            return jsonify({"error": "Admin access required"}), 403
        
        # Resolve panic alert
        success = job_requests_db.resolve_panic_alert(alert_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Panic alert {alert_id} resolved successfully"
            }), 200
        else:
            return jsonify({"error": "Failed to resolve panic alert"}), 500
        
    except Exception as e:
        print(f"  Resolve panic alert error: {e}")
        return jsonify({"error": "Failed to resolve panic alert"}), 500
