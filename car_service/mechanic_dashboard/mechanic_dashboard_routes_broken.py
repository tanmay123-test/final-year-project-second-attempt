"""
Mechanic Dashboard API Routes
Complete REST API for mechanic worker management system
"""

from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

@mechanic_dashboard_bp.route("/api/car/mechanic/update-location", methods=["POST"])
@require_mechanic_auth
def update_location():
    """Update mechanic location"""
    try:
        mechanic_id = request.current_worker['id']
        data = request.get_json() or {}
        
        lat = data.get('latitude')
        lng = data.get('longitude')
        
        if lat is None or lng is None:
            return jsonify({"error": "Latitude and longitude required"}), 400
        
        success = mechanic_dashboard_service.db.update_mechanic_status(
            mechanic_id, lat=lat, lng=lng
        )
        
        if success:
            return jsonify({"success": True, "message": "Location updated"}), 200
        else:
            return jsonify({"error": "Failed to update location"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Location update failed: {str(e)}"}), 500

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

@mechanic_dashboard_bp.route("/api/car/mechanic/reject-job/<int:job_id>", methods=["POST"])
@require_mechanic_auth
def reject_job(job_id):
    """Reject a job request"""
    try:
        mechanic_id = request.current_worker['id']
        data = request.get_json() or {}
        reason = data.get('reason', 'Not interested')
        
        # In a real system, this would log the rejection reason
        # For now, just return success
        return jsonify({
            "success": True,
            "message": "Job rejected",
            "job_id": job_id,
            "reason": reason
        }), 200
            
    except Exception as e:
        return jsonify({"error": f"Failed to reject job: {str(e)}"}), 500

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

@mechanic_dashboard_bp.route("/api/car/mechanic/update-job-status/<int:job_id>", methods=["PUT"])
@require_mechanic_auth
def update_job_status(job_id):
    """Update job status through lifecycle"""
    try:
        mechanic_id = request.current_worker['id']
        data = request.get_json() or {}
        
        new_status = data.get('status')
        if not new_status:
            return jsonify({"error": "Status is required"}), 400
        
        result = mechanic_dashboard_service.update_job_status(mechanic_id, job_id, new_status)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to update job status: {str(e)}"}), 500

# ==================== EARNINGS ====================

@mechanic_dashboard_bp.route("/api/car/mechanic/earnings", methods=["GET"])
@require_mechanic_auth
def get_earnings():
    """Get earnings insights"""
    try:
        mechanic_id = request.current_worker['id']
        period = request.args.get('period', 'all')  # today, week, month, all
        
        result = mechanic_dashboard_service.get_earnings_insights(mechanic_id, period)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get earnings: {str(e)}"}), 500

@mechanic_dashboard_bp.route("/api/car/mechanic/earnings-history", methods=["GET"])
@require_mechanic_auth
def get_earnings_history():
    """Get detailed earnings history"""
    try:
        mechanic_id = request.current_worker['id']
        period = request.args.get('period', 'month')
        limit = int(request.args.get('limit', 50))
        
        earnings = mechanic_dashboard_service.db.get_mechanic_earnings(mechanic_id, period)
        
        # Get detailed history (simplified)
        conn = mechanic_dashboard_service.db.get_conn()
        cur = conn.cursor()
        
        date_filter = ""
        params = [mechanic_id]
        
        if period == 'today':
            date_filter = "AND date = CURRENT_DATE"
        elif period == 'week':
            date_filter = "AND date >= date('now', '-7 days')"
        elif period == 'month':
            date_filter = "AND date >= date('now', '-1 month')"
        
        cur.execute(f"""
            SELECT 
                me.*,
                mj.issue_type,
                mj.customer_rating
            FROM mechanic_earnings me
            JOIN mechanic_jobs mj ON me.job_id = mj.id
            WHERE me.mechanic_id = ? {date_filter}
            ORDER BY me.date DESC
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

# ==================== PERFORMANCE & SAFETY ====================

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

@mechanic_dashboard_bp.route("/api/car/mechanic/metrics", methods=["GET"])
@require_mechanic_auth
def get_metrics():
    """Get raw performance metrics"""
    try:
        mechanic_id = request.current_worker['id']
        metrics = mechanic_dashboard_service.db.get_mechanic_metrics(mechanic_id)
        
        return jsonify({
            "success": True,
            "metrics": metrics
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get metrics: {str(e)}"}), 500

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

@mechanic_dashboard_bp.route("/api/car/mechanic/emergency-alerts", methods=["GET"])
@require_mechanic_auth
def get_emergency_alerts():
    """Get mechanic's emergency alerts"""
    try:
        mechanic_id = request.current_worker['id']
        alerts = mechanic_dashboard_service.db.get_emergency_alerts(mechanic_id)
        
        return jsonify({
            "success": True,
            "alerts": alerts
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get emergency alerts: {str(e)}"}), 500

# ==================== JOB PROOF SYSTEM ====================

@mechanic_dashboard_bp.route("/api/car/mechanic/upload-proof/<int:job_id>", methods=["POST"])
@require_mechanic_auth
def upload_job_proof(job_id):
    """Upload job completion proof"""
    try:
        mechanic_id = request.current_worker['id']
        
        # Handle file uploads
        before_file = request.files.get('before_photo')
        after_file = request.files.get('after_photo')
        notes = request.form.get('work_notes', '')
        
        if not before_file and not after_file:
            return jsonify({"error": "At least one photo is required"}), 400
        
        result = mechanic_dashboard_service.upload_job_proof(
            mechanic_id, job_id, before_file, after_file, notes
        )
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to upload proof: {str(e)}"}), 500

@mechanic_dashboard_bp.route("/api/car/mechanic/job-proofs/<int:job_id>", methods=["GET"])
@require_mechanic_auth
def get_job_proofs(job_id):
    """Get proofs for a specific job"""
    try:
        mechanic_id = request.current_worker['id']
        
        # Verify job belongs to mechanic
        active_jobs = mechanic_dashboard_service.db.get_active_jobs(mechanic_id)
        job_exists = any(job["id"] == job_id for job in active_jobs)
        
        if not job_exists:
            return jsonify({"error": "Job not found or access denied"}), 404
        
        proofs = mechanic_dashboard_service.db.get_job_proofs(job_id)
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "proofs": proofs
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get job proofs: {str(e)}"}), 500

@mechanic_dashboard_bp.route("/uploads/job_proofs/<filename>", methods=["GET"])
@require_mechanic_auth
def serve_proof_file(filename):
    """Serve uploaded proof files"""
    try:
        upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "job_proofs")
        return send_from_directory(upload_dir, filename)
    except Exception as e:
        return jsonify({"error": f"Failed to serve file: {str(e)}"}), 500

# ==================== DASHBOARD SUMMARY ====================

@mechanic_dashboard_bp.route("/api/car/mechanic/dashboard-summary", methods=["GET"])
@require_mechanic_auth
def get_dashboard_summary():
    """Get complete dashboard summary"""
    try:
        mechanic_id = request.current_worker['id']
        
        # Get all dashboard data
        status_data = mechanic_dashboard_service.get_demand_status(mechanic_id)
        jobs_data = mechanic_dashboard_service.get_transparent_job_requests(mechanic_id)
        active_data = mechanic_dashboard_service.get_active_jobs(mechanic_id)
        earnings_data = mechanic_dashboard_service.get_earnings_insights(mechanic_id, 'today')
        performance_data = mechanic_dashboard_service.get_performance_safety(mechanic_id)
        
        return jsonify({
            "success": True,
            "summary": {
                "status": status_data,
                "job_requests": jobs_data,
                "active_jobs": active_data,
                "earnings": earnings_data,
                "performance": performance_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get dashboard summary: {str(e)}"}), 500

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
