"""
Tow Truck Driver API Routes
Complete REST API for tow truck driver management system
"""

from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth_utils import verify_token
from ..worker_auth.worker_routes import get_current_worker, car_worker_db
from .tow_truck_service import tow_truck_service

# Create blueprint
tow_truck_bp = Blueprint("tow_truck", __name__)

def require_tow_truck_auth(f):
    """Decorator to require authenticated tow truck driver"""
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
        
        # Get worker and validate it's a tow truck driver
        worker = car_worker_db.get_worker_by_username(username)
        if not worker or worker['worker_type'] != 'TOW_TRUCK':
            return jsonify({"error": "Tow truck driver access required"}), 403
        
        if worker['status'] != 'APPROVED':
            return jsonify({"error": "Tow truck driver account not approved"}), 403
        
        # Add worker to request context
        request.current_worker = worker
        return f(*args, **kwargs)
    
    wrapper.__name__ = f.__name__
    return wrapper

# ==================== ONLINE STATUS & EMERGENCY ZONE ====================

@tow_truck_bp.route("/api/car/tow-driver/status", methods=["GET"])
@require_tow_truck_auth
def get_tow_driver_status():
    """Get tow driver current status and emergency zone analysis"""
    try:
        driver_id = request.current_worker['id']
        result = tow_truck_service.get_emergency_zone_status(driver_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get status: {str(e)}"}), 500

@tow_truck_bp.route("/api/car/tow-driver/toggle-online", methods=["POST"])
@require_tow_truck_auth
def toggle_tow_driver_online_status():
    """Toggle tow driver online/offline status"""
    try:
        driver_id = request.current_worker['id']
        result = tow_truck_service.toggle_tow_driver_online_status(driver_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to toggle status: {str(e)}"}), 500

@tow_truck_bp.route("/api/car/tow-driver/update-location", methods=["POST"])
@require_tow_truck_auth
def update_tow_driver_location():
    """Update tow driver location"""
    try:
        driver_id = request.current_worker['id']
        data = request.get_json() or {}
        
        lat = data.get('latitude')
        lng = data.get('longitude')
        
        if lat is None or lng is None:
            return jsonify({"error": "Latitude and longitude required"}), 400
        
        success = tow_truck_service.db.update_tow_driver_status(
            driver_id, lat=lat, lng=lng
        )
        
        if success:
            return jsonify({"success": True, "message": "Location updated"}), 200
        else:
            return jsonify({"error": "Failed to update location"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Location update failed: {str(e)}"}), 500

@tow_truck_bp.route("/api/car/tow-driver/update-truck-type", methods=["POST"])
@require_tow_truck_auth
def update_tow_driver_truck_type():
    """Update tow driver truck type"""
    try:
        driver_id = request.current_worker['id']
        data = request.get_json() or {}
        
        truck_type = data.get('truck_type')
        if truck_type not in ['FLATBED', 'WHEEL_LIFT', 'HEAVY_DUTY']:
            return jsonify({"error": "Invalid truck type"}), 400
        
        success = tow_truck_service.db.update_tow_driver_status(
            driver_id, truck_type=truck_type
        )
        
        if success:
            return jsonify({"success": True, "message": f"Truck type updated to {truck_type}"}), 200
        else:
            return jsonify({"error": "Failed to update truck type"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Truck type update failed: {str(e)}"}), 500

# ==================== EMERGENCY TOW REQUESTS ====================

@tow_truck_bp.route("/api/car/tow-driver/emergency-requests", methods=["GET"])
@require_tow_truck_auth
def get_emergency_tow_requests():
    """Get emergency tow requests"""
    try:
        driver_id = request.current_worker['id']
        result = tow_truck_service.get_emergency_tow_requests(driver_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get emergency requests: {str(e)}"}), 500

@tow_truck_bp.route("/api/car/tow-driver/accept-request/<int:request_id>", methods=["POST"])
@require_tow_truck_auth
def accept_tow_request(request_id):
    """Accept an emergency tow request"""
    try:
        driver_id = request.current_worker['id']
        result = tow_truck_service.accept_tow_request(driver_id, request_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to accept tow request: {str(e)}"}), 500

@tow_truck_bp.route("/api/car/tow-driver/reject-request/<int:request_id>", methods=["POST"])
@require_tow_truck_auth
def reject_tow_request(request_id):
    """Reject an emergency tow request"""
    try:
        driver_id = request.current_worker['id']
        data = request.get_json() or {}
        reason = data.get('reason', 'Not available')
        
        # In a real system, this would log the rejection reason
        # For now, just return success
        return jsonify({
            "success": True,
            "message": "Tow request rejected",
            "request_id": request_id,
            "reason": reason
        }), 200
            
    except Exception as e:
        return jsonify({"error": f"Failed to reject tow request: {str(e)}"}), 500

# ==================== ACTIVE TOWING OPERATIONS ====================

@tow_truck_bp.route("/api/car/tow-driver/active-operations", methods=["GET"])
@require_tow_truck_auth
def get_active_tow_operations():
    """Get tow driver's active towing operations"""
    try:
        driver_id = request.current_worker['id']
        result = tow_truck_service.get_active_tow_operations(driver_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get active operations: {str(e)}"}), 500

@tow_truck_bp.route("/api/car/tow-driver/update-operation-status/<int:request_id>", methods=["PUT"])
@require_tow_truck_auth
def update_tow_operation_status(request_id):
    """Update tow operation status through lifecycle"""
    try:
        driver_id = request.current_worker['id']
        data = request.get_json() or {}
        
        new_status = data.get('status')
        if not new_status:
            return jsonify({"error": "Status is required"}), 400
        
        result = tow_truck_service.update_tow_operation_status(driver_id, request_id, new_status)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to update operation status: {str(e)}"}), 500

# ==================== EARNINGS & DISTANCE INSIGHTS ====================

@tow_truck_bp.route("/api/car/tow-driver/earnings", methods=["GET"])
@require_tow_truck_auth
def get_tow_earnings():
    """Get tow earnings and distance insights"""
    try:
        driver_id = request.current_worker['id']
        period = request.args.get('period', 'all')  # today, week, month, all
        
        result = tow_truck_service.get_tow_earnings_insights(driver_id, period)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get earnings: {str(e)}"}), 500

@tow_truck_bp.route("/api/car/tow-driver/earnings-history", methods=["GET"])
@require_tow_truck_auth
def get_tow_earnings_history():
    """Get detailed tow earnings history"""
    try:
        driver_id = request.current_worker['id']
        period = request.args.get('period', 'month')
        limit = int(request.args.get('limit', 50))
        
        earnings = tow_truck_service.db.get_tow_driver_earnings(driver_id, period)
        
        # Get detailed history (simplified)
        conn = tow_truck_service.db.get_conn()
        cur = conn.cursor()
        
        date_filter = ""
        params = [driver_id]
        
        if period == 'today':
            date_filter = "AND date = CURRENT_DATE"
        elif period == 'week':
            date_filter = "AND date >= date('now', '-7 days')"
        elif period == 'month':
            date_filter = "AND date >= date('now', '-1 month')"
        
        cur.execute(f"""
            SELECT 
                tde.*,
                tr.vehicle_type,
                tr.issue_type,
                tr.distance_km,
                tr.risk_level
            FROM tow_driver_earnings tde
            JOIN tow_requests tr ON tde.tow_request_id = tr.id
            WHERE tde.driver_id = ? {date_filter}
            ORDER BY tde.date DESC
            LIMIT ?
        """, params + [limit])
        
        rows = cur.fetchall()
        conn.close()
        
        history = [dict(row) for row in rows]
        
        return jsonify({
            "success": True,
            "period": period,
            "history": history,
            "summary": earnings
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get earnings history: {str(e)}"}), 500

# ==================== PERFORMANCE, SAFETY & RISK SUPPORT ====================

@tow_truck_bp.route("/api/car/tow-driver/performance", methods=["GET"])
@require_tow_truck_auth
def get_tow_performance():
    """Get tow performance metrics and safety insights"""
    try:
        driver_id = request.current_worker['id']
        result = tow_truck_service.get_tow_performance_safety(driver_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get performance: {str(e)}"}), 500

@tow_truck_bp.route("/api/car/tow-driver/metrics", methods=["GET"])
@require_tow_truck_auth
def get_tow_metrics():
    """Get raw tow performance metrics"""
    try:
        driver_id = request.current_worker['id']
        metrics = tow_truck_service.db.get_tow_driver_metrics(driver_id)
        
        return jsonify({
            "success": True,
            "metrics": metrics
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get metrics: {str(e)}"}), 500

# ==================== EMERGENCY SOS ====================

@tow_truck_bp.route("/api/car/tow-driver/emergency-alert", methods=["POST"])
@require_tow_truck_auth
def trigger_tow_emergency():
    """Trigger emergency SOS alert"""
    try:
        driver_id = request.current_worker['id']
        data = request.get_json() or {}
        
        lat = data.get('latitude')
        lng = data.get('longitude')
        
        if lat is None or lng is None:
            return jsonify({"error": "Location coordinates required"}), 400
        
        result = tow_truck_service.trigger_tow_emergency_sos(driver_id, lat, lng)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to trigger emergency: {str(e)}"}), 500

@tow_truck_bp.route("/api/car/tow-driver/emergency-alerts", methods=["GET"])
@require_tow_truck_auth
def get_tow_emergency_alerts():
    """Get tow driver's emergency alerts"""
    try:
        driver_id = request.current_worker['id']
        alerts = tow_truck_service.db.get_tow_emergency_alerts(driver_id)
        
        return jsonify({
            "success": True,
            "alerts": alerts
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get emergency alerts: {str(e)}"}), 500

# ==================== TOWING PROOF SYSTEM ====================

@tow_truck_bp.route("/api/car/tow-driver/upload-towing-proof/<int:request_id>", methods=["POST"])
@require_tow_truck_auth
def upload_towing_proof(request_id):
    """Upload tow operation completion proof"""
    try:
        driver_id = request.current_worker['id']
        
        # Handle file uploads
        pickup_file = request.files.get('pickup_photo')
        loaded_file = request.files.get('vehicle_loaded_photo')
        drop_file = request.files.get('drop_photo')
        notes = request.form.get('damage_notes', '')
        
        if not pickup_file and not loaded_file and not drop_file:
            return jsonify({"error": "At least one photo is required"}), 400
        
        result = tow_truck_service.upload_towing_proof(
            driver_id, request_id, pickup_file, loaded_file, drop_file, notes
        )
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to upload proof: {str(e)}"}), 500

@tow_truck_bp.route("/api/car/tow-driver/towing-proofs/<int:request_id>", methods=["GET"])
@require_tow_truck_auth
def get_towing_proofs(request_id):
    """Get proofs for a specific tow request"""
    try:
        driver_id = request.current_worker['id']
        
        # Verify request belongs to driver
        active_operations = tow_truck_service.db.get_active_tow_operations(driver_id)
        request_exists = any(op["id"] == request_id for op in active_operations)
        
        if not request_exists:
            return jsonify({"error": "Tow request not found or access denied"}), 404
        
        proofs = tow_truck_service.db.get_towing_proofs(request_id)
        
        return jsonify({
            "success": True,
            "request_id": request_id,
            "proofs": proofs
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get towing proofs: {str(e)}"}), 500

@tow_truck_bp.route("/uploads/tow_truck_proofs/<filename>", methods=["GET"])
@require_tow_truck_auth
def serve_tow_proof_file(filename):
    """Serve uploaded tow proof files"""
    try:
        upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "tow_truck_proofs")
        return send_from_directory(upload_dir, filename)
    except Exception as e:
        return jsonify({"error": f"Failed to serve file: {str(e)}"}), 500

# ==================== MANUAL CHARGE REQUEST ====================

@tow_truck_bp.route("/api/car/tow-driver/request-extra-charge/<int:request_id>", methods=["POST"])
@require_tow_truck_auth
def request_extra_charge(request_id):
    """Request manual extra charge (requires user approval)"""
    try:
        driver_id = request.current_worker['id']
        data = request.get_json() or {}
        
        amount = data.get('amount')
        reason = data.get('reason')
        
        if not amount or not reason:
            return jsonify({"error": "Amount and reason are required"}), 400
        
        # In a real system, this would send notification to user for approval
        # For now, just simulate the request
        return jsonify({
            "success": True,
            "message": "Extra charge request sent to user for approval",
            "request_id": request_id,
            "extra_amount": amount,
            "reason": reason,
            "status": "PENDING_USER_APPROVAL"
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to request extra charge: {str(e)}"}), 500

# ==================== DASHBOARD SUMMARY ====================

@tow_truck_bp.route("/api/car/tow-driver/dashboard-summary", methods=["GET"])
@require_tow_truck_auth
def get_tow_dashboard_summary():
    """Get complete tow dashboard summary"""
    try:
        driver_id = request.current_worker['id']
        
        # Get all dashboard data
        status_data = tow_truck_service.get_emergency_zone_status(driver_id)
        requests_data = tow_truck_service.get_emergency_tow_requests(driver_id)
        active_data = tow_truck_service.get_active_tow_operations(driver_id)
        earnings_data = tow_truck_service.get_tow_earnings_insights(driver_id, 'today')
        performance_data = tow_truck_service.get_tow_performance_safety(driver_id)
        
        return jsonify({
            "success": True,
            "summary": {
                "status": status_data,
                "emergency_requests": requests_data,
                "active_operations": active_data,
                "earnings": earnings_data,
                "performance": performance_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get dashboard summary: {str(e)}"}), 500

# ==================== ERROR HANDLING ====================

@tow_truck_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@tow_truck_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

@tow_truck_bp.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return jsonify({"error": "Access forbidden"}), 403
