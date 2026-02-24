"""
Mechanic Worker API Routes - Car Service Module
Handles mechanic dashboard, jobs, earnings, and performance
"""

import os
import json
from datetime import datetime, timedelta
from flask import request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from .worker_routes import worker_auth_bp, verify_token, is_admin
from .mechanic_db import (
    create_mechanic_status, update_mechanic_status, get_mechanic_status,
    create_job_request, get_pending_jobs, accept_job, get_mechanic_jobs,
    update_job_status, create_job_proof, get_job_proof,
    create_earning_record, get_mechanic_earnings, update_mechanic_metrics,
    get_mechanic_metrics, create_emergency_alert, get_demand_insights
)
from .worker_db import get_worker_by_username

# Configuration
UPLOAD_FOLDER = 'uploads/job_proofs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@worker_auth_bp.route("/api/car/mechanic/status", methods=["GET", "PUT"])
def mechanic_status():
    """Get or update mechanic status"""
    try:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"success": False, "error": "Authorization required"}), 401
        
        token = auth.split(" ")[1]
        username = verify_token(token)
        if not username:
            return jsonify({"success": False, "error": "Invalid token"}), 401
        
        worker = get_worker_by_username(username)
        if not worker or worker['worker_type'] != 'MECHANIC':
            return jsonify({"success": False, "error": "Mechanic access required"}), 403
        
        if worker['status'] != 'APPROVED':
            return jsonify({"success": False, "error": "Worker not approved"}), 403
        
        worker_id = worker['id']
        
        if request.method == "GET":
            # Get mechanic status
            status = get_mechanic_status(worker_id)
            if not status:
                create_mechanic_status(worker_id)
                status = get_mechanic_status(worker_id)
            
            # Get demand insights
            insights = get_demand_insights()
            
            return jsonify({
                "success": True,
                "status": {
                    "online_status": status['online_status'],
                    "is_busy": status['is_busy'],
                    "last_location_lat": status['last_location_lat'],
                    "last_location_long": status['last_location_long'],
                    "last_status_change": status['last_status_change']
                },
                "demand": insights
            })
        
        elif request.method == "PUT":
            # Update mechanic status
            data = request.get_json()
            online_status = data.get('online_status')
            is_busy = data.get('is_busy')
            lat = data.get('lat')
            lon = data.get('lon')
            
            update_mechanic_status(worker_id, online_status, is_busy, lat, lon)
            
            return jsonify({
                "success": True,
                "message": "Status updated successfully"
            })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@worker_auth_bp.route("/api/car/mechanic/jobs", methods=["GET"])
def mechanic_jobs():
    """Get mechanic's jobs"""
    try:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"success": False, "error": "Authorization required"}), 401
        
        token = auth.split(" ")[1]
        username = verify_token(token)
        if not username:
            return jsonify({"success": False, "error": "Invalid token"}), 401
        
        worker = get_worker_by_username(username)
        if not worker or worker['worker_type'] != 'MECHANIC':
            return jsonify({"success": False, "error": "Mechanic access required"}), 403
        
        if worker['status'] != 'APPROVED':
            return jsonify({"success": False, "error": "Worker not approved"}), 403
        
        worker_id = worker['id']
        status_filter = request.args.get('status')
        
        jobs = get_mechanic_jobs(worker_id, status_filter)
        
        return jsonify({
            "success": True,
            "jobs": [dict(job) for job in jobs]
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@worker_auth_bp.route("/api/car/mechanic/pending-jobs", methods=["GET"])
def pending_jobs():
    """Get pending jobs for mechanic"""
    try:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"success": False, "error": "Authorization required"}), 401
        
        token = auth.split(" ")[1]
        username = verify_token(token)
        if not username:
            return jsonify({"success": False, "error": "Invalid token"}), 401
        
        worker = get_worker_by_username(username)
        if not worker or worker['worker_type'] != 'MECHANIC':
            return jsonify({"success": False, "error": "Mechanic access required"}), 403
        
        if worker['status'] != 'APPROVED':
            return jsonify({"success": False, "error": "Worker not approved"}), 403
        
        worker_id = worker['id']
        
        # Get mechanic skills from documents (simplified)
        mechanic_skills = ['engine', 'transmission', 'brakes', 'electrical']  # Mock skills
        
        jobs = get_pending_jobs(worker_id, mechanic_skills)
        
        return jsonify({
            "success": True,
            "jobs": [dict(job) for job in jobs]
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@worker_auth_bp.route("/api/car/mechanic/accept-job", methods=["POST"])
def accept_mechanic_job():
    """Accept a job"""
    try:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"success": False, "error": "Authorization required"}), 401
        
        token = auth.split(" ")[1]
        username = verify_token(token)
        if not username:
            return jsonify({"success": False, "error": "Invalid token"}), 401
        
        worker = get_worker_by_username(username)
        if not worker or worker['worker_type'] != 'MECHANIC':
            return jsonify({"success": False, "error": "Mechanic access required"}), 403
        
        if worker['status'] != 'APPROVED':
            return jsonify({"success": False, "error": "Worker not approved"}), 403
        
        data = request.get_json()
        job_id = data.get('job_id')
        
        if not job_id:
            return jsonify({"success": False, "error": "Job ID required"}), 400
        
        worker_id = worker['id']
        accept_job(job_id, worker_id)
        
        return jsonify({
            "success": True,
            "message": "Job accepted successfully"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@worker_auth_bp.route("/api/car/mechanic/update-job-status", methods=["PUT"])
def update_mechanic_job_status():
    """Update job status"""
    try:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"success": False, "error": "Authorization required"}), 401
        
        token = auth.split(" ")[1]
        username = verify_token(token)
        if not username:
            return jsonify({"success": False, "error": "Invalid token"}), 401
        
        worker = get_worker_by_username(username)
        if not worker or worker['worker_type'] != 'MECHANIC':
            return jsonify({"success": False, "error": "Mechanic access required"}), 403
        
        if worker['status'] != 'APPROVED':
            return jsonify({"success": False, "error": "Worker not approved"}), 403
        
        data = request.get_json()
        job_id = data.get('job_id')
        status = data.get('status')
        
        if not job_id or not status:
            return jsonify({"success": False, "error": "Job ID and status required"}), 400
        
        valid_statuses = ['ON_THE_WAY', 'ARRIVED', 'WORKING', 'COMPLETED']
        if status not in valid_statuses:
            return jsonify({"success": False, "error": "Invalid status"}), 400
        
        update_job_status(job_id, status)
        
        # Update metrics when job is completed
        if status == 'COMPLETED':
            worker_id = worker['id']
            update_mechanic_metrics(worker_id)
        
        return jsonify({
            "success": True,
            "message": f"Job status updated to {status}"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@worker_auth_bp.route("/api/car/mechanic/upload-proof", methods=["POST"])
def upload_job_proof():
    """Upload job proof (before/after photos and notes)"""
    try:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"success": False, "error": "Authorization required"}), 401
        
        token = auth.split(" ")[1]
        username = verify_token(token)
        if not username:
            return jsonify({"success": False, "error": "Invalid token"}), 401
        
        worker = get_worker_by_username(username)
        if not worker or worker['worker_type'] != 'MECHANIC':
            return jsonify({"success": False, "error": "Mechanic access required"}), 403
        
        if worker['status'] != 'APPROVED':
            return jsonify({"success": False, "error": "Worker not approved"}), 403
        
        job_id = request.form.get('job_id')
        work_notes = request.form.get('work_notes', '')
        
        if not job_id:
            return jsonify({"success": False, "error": "Job ID required"}), 400
        
        # Handle file uploads
        before_photo = None
        after_photo = None
        
        if 'before_photo' in request.files:
            file = request.files['before_photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"before_{job_id}_{file.filename}")
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                before_photo = filename
        
        if 'after_photo' in request.files:
            file = request.files['after_photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"after_{job_id}_{file.filename}")
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                after_photo = filename
        
        create_job_proof(job_id, before_photo, after_photo, work_notes)
        
        return jsonify({
            "success": True,
            "message": "Job proof uploaded successfully"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@worker_auth_bp.route("/api/car/mechanic/earnings", methods=["GET"])
def mechanic_earnings():
    """Get mechanic earnings"""
    try:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"success": False, "error": "Authorization required"}), 401
        
        token = auth.split(" ")[1]
        username = verify_token(token)
        if not username:
            return jsonify({"success": False, "error": "Invalid token"}), 401
        
        worker = get_worker_by_username(username)
        if not worker or worker['worker_type'] != 'MECHANIC':
            return jsonify({"success": False, "error": "Mechanic access required"}), 403
        
        if worker['status'] != 'APPROVED':
            return jsonify({"success": False, "error": "Worker not approved"}), 403
        
        worker_id = worker['id']
        period = request.args.get('period', 'all')
        
        earnings = get_mechanic_earnings(worker_id, period)
        
        # Calculate summary
        total_earnings = sum(e['mechanic_earning'] for e in earnings)
        total_jobs = len(earnings)
        avg_earning = total_earnings / total_jobs if total_jobs > 0 else 0
        
        return jsonify({
            "success": True,
            "earnings": [dict(e) for e in earnings],
            "summary": {
                "total_earnings": total_earnings,
                "total_jobs": total_jobs,
                "average_earning_per_job": avg_earning
            }
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@worker_auth_bp.route("/api/car/mechanic/metrics", methods=["GET"])
def mechanic_performance_metrics():
    """Get mechanic performance metrics"""
    try:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"success": False, "error": "Authorization required"}), 401
        
        token = auth.split(" ")[1]
        username = verify_token(token)
        if not username:
            return jsonify({"success": False, "error": "Invalid token"}), 401
        
        worker = get_worker_by_username(username)
        if not worker or worker['worker_type'] != 'MECHANIC':
            return jsonify({"success": False, "error": "Mechanic access required"}), 403
        
        if worker['status'] != 'APPROVED':
            return jsonify({"success": False, "error": "Worker not approved"}), 403
        
        worker_id = worker['id']
        metrics = get_mechanic_metrics(worker_id)
        
        if not metrics:
            # Create initial metrics
            update_mechanic_metrics(worker_id)
            metrics = get_mechanic_metrics(worker_id)
        
        # Generate suggestions based on metrics
        suggestions = []
        if metrics['completion_rate'] < 90:
            suggestions.append("💡 Improve completion rate to receive more jobs.")
        if metrics['acceptance_rate'] < 80:
            suggestions.append("💡 Accept more jobs to improve your rating.")
        if metrics['complaint_rate'] > 5:
            suggestions.append("💡 Focus on customer satisfaction to reduce complaints.")
        
        return jsonify({
            "success": True,
            "metrics": dict(metrics),
            "suggestions": suggestions
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@worker_auth_bp.route("/api/car/mechanic/emergency-alert", methods=["POST"])
def emergency_alert():
    """Create emergency alert"""
    try:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"success": False, "error": "Authorization required"}), 401
        
        token = auth.split(" ")[1]
        username = verify_token(token)
        if not username:
            return jsonify({"success": False, "error": "Invalid token"}), 401
        
        worker = get_worker_by_username(username)
        if not worker or worker['worker_type'] != 'MECHANIC':
            return jsonify({"success": False, "error": "Mechanic access required"}), 403
        
        if worker['status'] != 'APPROVED':
            return jsonify({"success": False, "error": "Worker not approved"}), 403
        
        data = request.get_json()
        alert_type = data.get('alert_type', 'EMERGENCY')
        message = data.get('message', 'Emergency alert from mechanic')
        lat = data.get('lat')
        lon = data.get('lon')
        
        worker_id = worker['id']
        alert_id = create_emergency_alert(worker_id, alert_type, message, lat, lon)
        
        return jsonify({
            "success": True,
            "message": "🚨 Admin has been notified.",
            "alert_id": alert_id
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@worker_auth_bp.route("/api/car/mechanic/job-proof/<int:job_id>", methods=["GET"])
def get_job_proof_api(job_id):
    """Get job proof for a specific job"""
    try:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"success": False, "error": "Authorization required"}), 401
        
        token = auth.split(" ")[1]
        username = verify_token(token)
        if not username:
            return jsonify({"success": False, "error": "Invalid token"}), 401
        
        worker = get_worker_by_username(username)
        if not worker or worker['worker_type'] != 'MECHANIC':
            return jsonify({"success": False, "error": "Mechanic access required"}), 403
        
        if worker['status'] != 'APPROVED':
            return jsonify({"success": False, "error": "Worker not approved"}), 403
        
        proof = get_job_proof(job_id)
        
        if not proof:
            return jsonify({"success": False, "error": "Job proof not found"}), 404
        
        return jsonify({
            "success": True,
            "proof": dict(proof)
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@worker_auth_bp.route("/uploads/job_proofs/<filename>")
def uploaded_file(filename):
    """Serve uploaded proof files"""
    return send_from_directory(UPLOAD_FOLDER, filename)
