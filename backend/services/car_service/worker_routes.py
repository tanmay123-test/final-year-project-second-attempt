"""
Car Service Worker API Routes
Handles worker signup, login, and profile management
"""

import os
import sys
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_utils import verify_token
from services.car_service.worker_db import worker_db

worker_bp = Blueprint("worker", __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}

# Upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'workers')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, prefix=""):
    """Save uploaded file with unique name"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{prefix}_{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_DIR, unique_filename)
        file.save(filepath)
        return unique_filename
    return None

@worker_bp.route("/api/car/worker/signup", methods=["POST"])
def worker_signup():
    """Worker signup endpoint"""
    try:
        # Get form data
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "").strip()
        age = request.form.get("age", "").strip()
        city = request.form.get("city", "").strip()
        address = request.form.get("address", "").strip()
        experience = request.form.get("experience", "").strip()
        skills = request.form.get("skills", "").strip()
        
        # Vehicle info (optional)
        vehicle_number = request.form.get("vehicle_number", "").strip() or None
        vehicle_model = request.form.get("vehicle_model", "").strip() or None
        loading_capacity = request.form.get("loading_capacity", "").strip() or None
        
        # Security declaration
        security_declaration = request.form.get("security_declaration", "0") == "1"
        
        # Validation
        if not all([name, phone, email, password, role, age, city, address, experience, skills]):
            return jsonify({"error": "All required fields must be filled"}), 400
        
        if role not in ["Mechanic", "Fuel Delivery Agent", "Tow Truck Operator", "Automobile Expert"]:
            return jsonify({"error": "Invalid role selected"}), 400
        
        if not security_declaration:
            return jsonify({"error": "Security declaration must be accepted"}), 400
        
        # Handle file uploads
        profile_photo = save_file(request.files.get("profile_photo"), "profile")
        aadhaar_path = save_file(request.files.get("aadhaar_card"), "aadhaar")
        license_path = save_file(request.files.get("driving_license"), "license")
        certificate_path = save_file(request.files.get("certificate"), "certificate")
        vehicle_rc_path = save_file(request.files.get("vehicle_rc"), "vehicle_rc")
        truck_photo_path = save_file(request.files.get("truck_photos"), "truck")
        
        # Required documents
        if not all([profile_photo, aadhaar_path, license_path]):
            return jsonify({"error": "Profile photo, Aadhaar card, and driving license are required"}), 400
        
        # Additional required documents based on role
        if role in ["Fuel Delivery Agent", "Tow Truck Operator"]:
            if not all([vehicle_number, vehicle_model, vehicle_rc_path]):
                return jsonify({"error": "Vehicle info and RC are required for this role"}), 400
        
        if role == "Tow Truck Operator" and not truck_photo_path:
            return jsonify({"error": "Truck photos are required for tow truck operators"}), 400
        
        # Create worker
        try:
            worker_id = worker_db.create_worker(
                name=name, phone=phone, email=email, password=password, role=role,
                age=int(age), city=city, address=address, experience=int(experience), skills=skills,
                vehicle_number=vehicle_number, vehicle_model=vehicle_model, 
                loading_capacity=loading_capacity, profile_photo=profile_photo,
                aadhaar_path=aadhaar_path, license_path=license_path,
                certificate_path=certificate_path, vehicle_rc_path=vehicle_rc_path,
                truck_photo_path=truck_photo_path, security_declaration=security_declaration
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
        return jsonify({
            "success": True,
            "message": "Worker signup successful. Await admin approval.",
            "worker_id": worker_id
        }), 201
        
    except Exception as e:
        print(f"  Worker signup error: {e}")
        return jsonify({"error": "Failed to create worker account"}), 500

@worker_bp.route("/api/car/worker/login", methods=["POST"])
def worker_login():
    """Worker login endpoint"""
    try:
        email = request.json.get("email", "").strip()
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        # Get worker by email (no password verification)
        cursor = worker_db.conn.cursor()
        cursor.execute("SELECT * FROM workers WHERE email = ?", (email,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({"error": "Email not found"}), 401
        
        worker = dict(row)
        
        # Check if approved
        if worker.get("status") != "APPROVED":
            return jsonify({
                "error": "Your account is pending admin approval",
                "status": worker.get("status")
            }), 403
        
        # Generate token (reuse existing auth utils)
        from auth_utils import generate_token
        token = generate_token(email)
        
        # Remove sensitive data
        worker_data = {
            "id": worker["id"],
            "name": worker["name"],
            "phone": worker["phone"],
            "email": worker["email"],
            "role": worker["role"],
            "city": worker["city"],
            "experience": worker["experience"]
        }
        
        return jsonify({
            "success": True,
            "token": token,
            "worker": worker_data
        }), 200
        
    except Exception as e:
        print(f"  Worker login error: {e}")
        return jsonify({"error": "Login failed"}), 500

@worker_bp.route("/api/car/worker/profile", methods=["GET"])
def get_worker_profile():
    """Get worker profile"""
    try:
        # Get worker from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        phone = verify_token(token)
        if not phone:
            return jsonify({"error": "Invalid token"}), 401
        
        worker = worker_db.get_worker_by_phone(phone)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        # Remove sensitive data
        worker_data = dict(worker)
        worker_data.pop("password_hash", None)
        
        return jsonify({"worker": worker_data}), 200
        
    except Exception as e:
        print(f"  Get worker profile error: {e}")
        return jsonify({"error": "Failed to get profile"}), 500

@worker_bp.route("/api/car/worker/status", methods=["PUT"])
def update_worker_status():
    """Update worker status (admin only)"""
    try:
        worker_id = request.json.get("worker_id")
        status = request.json.get("status")
        
        if not worker_id or not status:
            return jsonify({"error": "Worker ID and status are required"}), 400
        
        if status not in ["PENDING", "APPROVED", "REJECTED"]:
            return jsonify({"error": "Invalid status"}), 400
        
        success = worker_db.update_worker_status(int(worker_id), status)
        if success:
            return jsonify({"success": True, "message": f"Worker status updated to {status}"}), 200
        else:
            return jsonify({"error": "Worker not found"}), 404
            
    except Exception as e:
        print(f"  Update worker status error: {e}")
        return jsonify({"error": "Failed to update status"}), 500

@worker_bp.route("/api/car/workers/pending", methods=["GET"])
def get_pending_workers():
    """Get all pending workers for admin approval"""
    try:
        workers = worker_db.get_pending_workers()
        
        # Remove sensitive data
        clean_workers = []
        for worker in workers:
            clean_worker = dict(worker)
            clean_worker.pop("password_hash", None)
            clean_workers.append(clean_worker)
        
        return jsonify({"workers": clean_workers}), 200
        
    except Exception as e:
        print(f"  Get pending workers error: {e}")
        return jsonify({"error": "Failed to get pending workers"}), 500

@worker_bp.route("/api/car/workers/approved", methods=["GET"])
def get_approved_workers():
    """Get all approved workers"""
    try:
        workers = worker_db.get_approved_workers()
        
        # Remove sensitive data
        clean_workers = []
        for worker in workers:
            clean_worker = dict(worker)
            clean_worker.pop("password_hash", None)
            clean_workers.append(clean_worker)
        
        return jsonify({"workers": clean_workers}), 200
        
    except Exception as e:
        print(f"  Get approved workers error: {e}")
        return jsonify({"error": "Failed to get approved workers"}), 500
