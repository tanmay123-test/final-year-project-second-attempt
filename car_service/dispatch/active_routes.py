"""
Car Service Active Job API Routes
Handles active job lifecycle management
"""

import os
import sys
from datetime import datetime
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_utils import verify_token
from car_service.job_requests_db import job_requests_db
from car_service.car_service_worker_db import car_service_worker_db

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads', 'job_proofs')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

active_bp = Blueprint("active", __name__)

@active_bp.route("/api/car/mechanic/active-job", methods=["GET"])
def get_active_job():
    """Get mechanic's current active job"""
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
        
        # Get active job
        active_job = job_requests_db.get_active_job(mechanic['id'])
        
        if active_job:
            # Calculate repair time if working
            if active_job['status'] == 'WORKING':
                active_job['repair_time'] = job_requests_db.calculate_repair_time(active_job['id'])
            else:
                active_job['repair_time'] = "Not started"
            
            return jsonify({"active_job": active_job}), 200
        else:
            return jsonify({"active_job": None, "message": "No active job"}), 200
        
    except Exception as e:
        print(f"❌ Get active job error: {e}")
        return jsonify({"error": "Failed to get active job"}), 500

@active_bp.route("/api/car/mechanic/mark-arrived", methods=["POST"])
def mark_arrived():
    """Mark mechanic as arrived at job location"""
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
        
        # Get active job
        active_job = job_requests_db.get_active_job(mechanic['id'])
        if not active_job:
            return jsonify({"error": "No active job"}), 404
        
        # Update status to ARRIVED
        success = job_requests_db.update_active_job_status(
            active_job['id'], 
            'ARRIVED',
            arrival_time=datetime.now().isoformat()
        )
        
        if success:
            return jsonify({
                "success": True,
                "message": "Marked as arrived",
                "status": "ARRIVED",
                "note": "Ask user for OTP to start job"
            }), 200
        else:
            return jsonify({"error": "Failed to mark arrived"}), 500
        
    except Exception as e:
        print(f"❌ Mark arrived error: {e}")
        return jsonify({"error": "Failed to mark arrived"}), 500

@active_bp.route("/api/car/mechanic/start-job", methods=["POST"])
def start_job():
    """Start job with OTP verification"""
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
        
        # Get OTP from request
        otp = request.json.get("otp")
        if not otp:
            return jsonify({"error": "OTP is required"}), 400
        
        # Get active job
        active_job = job_requests_db.get_active_job(mechanic['id'])
        if not active_job:
            return jsonify({"error": "No active job"}), 404
        
        # Verify OTP
        if not job_requests_db.verify_otp(active_job['id'], otp):
            return jsonify({"error": "Invalid OTP"}), 400
        
        # Update status to WORKING
        success = job_requests_db.update_active_job_status(
            active_job['id'], 
            'WORKING',
            start_time=datetime.now().isoformat()
        )
        
        if success:
            return jsonify({
                "success": True,
                "message": "Job started successfully",
                "status": "WORKING",
                "note": "Repair timer started"
            }), 200
        else:
            return jsonify({"error": "Failed to start job"}), 500
        
    except Exception as e:
        print(f"❌ Start job error: {e}")
        return jsonify({"error": "Failed to start job"}), 500

@active_bp.route("/api/car/mechanic/upload-before", methods=["POST"])
def upload_before_photo():
    """Upload before repair photo"""
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
        
        # Get active job
        active_job = job_requests_db.get_active_job(mechanic['id'])
        if not active_job:
            return jsonify({"error": "No active job"}), 404
        
        # Handle file upload
        if 'photo' not in request.files:
            return jsonify({"error": "No photo file provided"}), 400
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({"error": "No photo selected"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"before_{timestamp}_{filename}"
            
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Update database
            success = job_requests_db.update_active_job_status(
                active_job['id'], 
                'WORKING',
                before_photo=filepath
            )
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Before photo uploaded",
                    "photo_path": filename
                }), 200
            else:
                return jsonify({"error": "Failed to save photo"}), 500
        else:
            return jsonify({"error": "Invalid file type"}), 400
        
    except Exception as e:
        print(f"❌ Upload before photo error: {e}")
        return jsonify({"error": "Failed to upload photo"}), 500

@active_bp.route("/api/car/mechanic/upload-after", methods=["POST"])
def upload_after_photo():
    """Upload after repair photo"""
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
        
        # Get active job
        active_job = job_requests_db.get_active_job(mechanic['id'])
        if not active_job:
            return jsonify({"error": "No active job"}), 404
        
        # Handle file upload
        if 'photo' not in request.files:
            return jsonify({"error": "No photo file provided"}), 400
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({"error": "No photo selected"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"after_{timestamp}_{filename}"
            
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Update database
            success = job_requests_db.update_active_job_status(
                active_job['id'], 
                'WORKING',
                after_photo=filepath
            )
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "After photo uploaded",
                    "photo_path": filename
                }), 200
            else:
                return jsonify({"error": "Failed to save photo"}), 500
        else:
            return jsonify({"error": "Invalid file type"}), 400
        
    except Exception as e:
        print(f"❌ Upload after photo error: {e}")
        return jsonify({"error": "Failed to upload photo"}), 500

@active_bp.route("/api/car/mechanic/complete-job", methods=["POST"])
def complete_job():
    """Complete active job"""
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
        
        # Get active job
        active_job = job_requests_db.get_active_job(mechanic['id'])
        if not active_job:
            return jsonify({"error": "No active job"}), 404
        
        # Validate required photos
        if not active_job.get('before_photo') or not active_job.get('after_photo'):
            return jsonify({"error": "Both before and after photos are required"}), 400
        
        # Complete the job
        success = job_requests_db.update_active_job_status(
            active_job['id'], 
            'COMPLETED',
            completion_time=datetime.now().isoformat()
        )
        
        if success:
            # Update job_requests table
            job_requests_db.complete_job(active_job['job_request_id'])
            
            # Calculate bonus
            from car_service.dispatch.bonus_engine import bonus_engine
            job_data = {
                'priority': active_job.get('priority', 'NORMAL'),
                'created_at': active_job.get('created_at', datetime.now().isoformat()),
                'distance_km': active_job.get('distance_km', 0),
                'issue_type': active_job.get('issue_type', ''),
                'user_city': active_job.get('user_city', '')
            }
            bonus = bonus_engine.calculate_bonus(job_data)
            
            # Insert detailed earning record
            job_requests_db.insert_earning(
                mechanic_id=mechanic['id'],
                job_id=active_job['job_request_id'],
                base_amount=active_job['estimated_earning'],
                commission_rate=0.20,
                bonus=bonus,
                distance=active_job.get('distance_km'),
                job_time_minutes=None  # Will be calculated later
            )
            
            # Update mechanic stats
            job_requests_db.update_mechanic_stats(mechanic['id'], job_completed=True)
            
            # Update performance metrics
            # Calculate response time (time from job assignment to completion)
            try:
                job_start_time = datetime.fromisoformat(active_job.get('created_at', datetime.now().isoformat()))
                completion_time = datetime.now()
                response_seconds = (completion_time - job_start_time).total_seconds()
                job_requests_db.update_mechanic_performance(
                    mechanic_id=mechanic['id'], 
                    job_completed=True, 
                    response_time=response_seconds
                )
            except:
                job_requests_db.update_mechanic_performance(mechanic['id'], job_completed=True)
            
            # Set mechanic to available
            car_service_worker_db.set_available(mechanic['id'])
            
            return jsonify({
                "success": True,
                "message": "Job completed successfully",
                "status": "COMPLETED",
                "earning": active_job['estimated_earning'],
                "bonus": bonus,
                "final_amount": active_job['estimated_earning'] - (active_job['estimated_earning'] * 0.20) + bonus,
                "note": "Status changed to ONLINE - You can now receive new jobs"
            }), 200
        else:
            return jsonify({"error": "Failed to complete job"}), 500
        
    except Exception as e:
        print(f"❌ Complete job error: {e}")
        return jsonify({"error": "Failed to complete job"}), 500

@active_bp.route("/uploads/job_proofs/<filename>", methods=["GET"])
def get_job_proof(filename):
    """Serve uploaded job proof files"""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        print(f"❌ Serve file error: {e}")
        return jsonify({"error": "File not found"}), 404
