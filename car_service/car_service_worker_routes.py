"""
Car Service Unified Worker API Routes
Handles all car service worker types (Mechanic, Fuel, Tow, Expert)
"""

import os
import sys
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_utils import verify_token
from car_service.car_service_worker_db import car_service_worker_db

car_service_worker_bp = Blueprint("car_service_worker", __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}

# Upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'car_service_workers')
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

@car_service_worker_bp.route("/api/car/service/worker/signup", methods=["POST"])
def worker_signup():
    """Unified car service worker signup endpoint"""
    try:
        # Get form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
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
        if not all([name, email, phone, password, role, age, city, address, experience, skills]):
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
            worker_id = car_service_worker_db.create_worker(
                name=name, email=email, phone=phone, password=password, role=role,
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
        print(f"❌ Worker signup error: {e}")
        return jsonify({"error": "Failed to create worker account"}), 500

@car_service_worker_bp.route("/api/car/service/worker/login", methods=["POST"])
def worker_login():
    """Unified car service worker login endpoint"""
    try:
        email = request.json.get("email", "").strip()
        password = request.json.get("password", "").strip()
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Verify worker
        worker = car_service_worker_db.verify_worker(email, password)
        if not worker:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Check if approved
        if worker.get("status") != "APPROVED":
            return jsonify({
                "error": "Your account is pending admin approval",
                "status": worker.get("status")
            }), 403
        
        # Generate token
        from auth_utils import generate_token
        token = generate_token(email)
        
        # Remove sensitive data
        worker_data = {
            "id": worker["id"],
            "name": worker["name"],
            "email": worker["email"],
            "phone": worker["phone"],
            "role": worker["role"],
            "city": worker["city"],
            "experience": worker["experience"],
            "skills": worker["skills"],
            "is_online": worker["is_online"]
        }
        
        return jsonify({
            "success": True,
            "token": token,
            "worker": worker_data
        }), 200
        
    except Exception as e:
        print(f"❌ Worker login error: {e}")
        return jsonify({"error": "Login failed"}), 500

@car_service_worker_bp.route("/api/car/service/worker/status", methods=["GET"])
def get_worker_status():
    """Get worker status"""
    try:
        # Get worker from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        worker = car_service_worker_db.get_worker_by_email(email)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        # Determine current status
        is_online = worker.get("is_online", 0)
        is_busy = worker.get("is_busy", 0)
        
        if not is_online:
            status = "OFFLINE"
        elif is_busy:
            status = "BUSY"
        else:
            status = "ONLINE"
        
        return jsonify({
            "status": status,
            "is_online": is_online,
            "is_busy": is_busy,
            "service_radius": worker.get("service_radius", 10),
            "city": worker.get("city", "Not set"),
            "current_city": worker.get("current_city", "Not set"),
            "last_status_update": worker.get("last_status_update"),
            "cooldown_until": worker.get("cooldown_until")
        }), 200
        
    except Exception as e:
        print(f"❌ Get worker status error: {e}")
        return jsonify({"error": "Failed to get status"}), 500

@car_service_worker_bp.route("/api/car/service/worker/status", methods=["PUT"])
def update_worker_admin_status():
    """Update worker status (admin only) - public endpoint for CLI"""
    try:
        worker_id = request.json.get("worker_id")
        status = request.json.get("status")
        
        if not worker_id or not status:
            return jsonify({"error": "Worker ID and status are required"}), 400
        
        if status not in ["PENDING", "APPROVED", "REJECTED"]:
            return jsonify({"error": "Invalid status"}), 400
        
        success = car_service_worker_db.update_worker_status(int(worker_id), status)
        if success:
            return jsonify({"success": True, "message": f"Worker status updated to {status}"}), 200
        else:
            return jsonify({"error": "Worker not found"}), 404
            
    except Exception as e:
        print(f"❌ Update worker status error: {e}")
        return jsonify({"error": "Failed to update status"}), 500

@car_service_worker_bp.route("/api/car/service/workers/approved", methods=["GET"])
def get_approved_workers():
    """Get all approved workers"""
    try:
        workers = car_service_worker_db.get_approved_workers()
        
        # Remove sensitive data
        clean_workers = []
        for worker in workers:
            clean_worker = dict(worker)
            clean_worker.pop("password_hash", None)
            clean_workers.append(clean_worker)
        
        return jsonify({"workers": clean_workers}), 200
        
    except Exception as e:
        print(f"❌ Get approved workers error: {e}")
        return jsonify({"error": "Failed to get approved workers"}), 500

@car_service_worker_bp.route("/api/car/service/worker/availability", methods=["PUT"])
def update_worker_availability():
    """Update worker availability status (online/offline/busy)"""
    try:
        # Get worker from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        worker = car_service_worker_db.get_worker_by_email(email)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        # Get new status values
        is_online = request.json.get("is_online", worker.get("is_online", 0))
        is_busy = request.json.get("is_busy", worker.get("is_busy", 0))
        service_radius = request.json.get("service_radius", worker.get("service_radius", 10))
        current_city = request.json.get("current_city", worker.get("current_city"))
        
        # Update status
        cursor = car_service_worker_db.conn.cursor()
        
        # Update online status if provided
        if "is_online" in request.json:
            cursor.execute("UPDATE car_service_workers SET is_online = ?, last_status_update = ? WHERE id = ?", 
                          (1 if is_online else 0, datetime.now().isoformat(), worker["id"]))
        
        # Update busy status if provided
        if "is_busy" in request.json:
            cursor.execute("UPDATE car_service_workers SET is_busy = ?, last_status_update = ? WHERE id = ?", 
                          (1 if is_busy else 0, datetime.now().isoformat(), worker["id"]))
        
        # Update service radius if provided
        if "service_radius" in request.json:
            cursor.execute("UPDATE car_service_workers SET service_radius = ? WHERE id = ?", 
                          (service_radius, worker["id"]))
        
        # Update current city if provided
        if "current_city" in request.json:
            cursor.execute("UPDATE car_service_workers SET current_city = ? WHERE id = ?", 
                          (current_city, worker["id"]))
        
        car_service_worker_db.conn.commit()
        
        # Determine status message
        if is_online and not is_busy:
            status = "ONLINE"
            message = "You are now ONLINE"
        elif not is_online:
            status = "OFFLINE"
            message = "You are now OFFLINE"
        elif is_busy:
            status = "BUSY"
            message = "Status changed to BUSY"
        else:
            status = "UNKNOWN"
            message = "Status updated"
        
        return jsonify({
            "success": True,
            "message": message,
            "status": status,
            "is_online": is_online,
            "is_busy": is_busy,
            "service_radius": service_radius,
            "current_city": current_city
        }), 200
            
    except Exception as e:
        print(f"❌ Update worker availability error: {e}")
        return jsonify({"error": "Failed to update availability"}), 500

@car_service_worker_bp.route("/api/car/service/worker/status", methods=["PUT"])
def update_worker_admin_status():
    """Update worker status (admin only) - public endpoint for CLI"""
    try:
        worker_id = request.json.get("worker_id")
        status = request.json.get("status")
        
        if not worker_id or not status:
            return jsonify({"error": "Worker ID and status are required"}), 400
        
        if status not in ["PENDING", "APPROVED", "REJECTED"]:
            return jsonify({"error": "Invalid status"}), 400
        
        success = car_service_worker_db.update_worker_status(int(worker_id), status)
        if success:
            return jsonify({"success": True, "message": f"Worker status updated to {status}"}), 200
        else:
            return jsonify({"error": "Worker not found"}), 404
            
    except Exception as e:
        print(f"❌ Update worker status error: {e}")
        return jsonify({"error": "Failed to update status"}), 500
