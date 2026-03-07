"""
Car Service Mechanic API Routes
Handles mechanic signup, login, and profile management
"""

import os
import sys
from datetime import datetime
from flask import Blueprint, request, jsonify
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_utils import verify_token
from services.car_service.mechanic_db import mechanic_db

mechanic_bp = Blueprint("mechanic", __name__)

@mechanic_bp.route("/api/car/mechanic/signup", methods=["POST"])
def mechanic_signup():
    """Mechanic signup endpoint"""
    try:
        # Get form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()
        age = request.form.get("age", "").strip()
        city = request.form.get("city", "").strip()
        experience = request.form.get("experience", "").strip()
        skills = request.form.get("skills", "").strip()
        
        # Document paths
        aadhaar_path = request.form.get("aadhaar_path", "").strip() or None
        license_path = request.form.get("license_path", "").strip() or None
        certificate_path = request.form.get("certificate_path", "").strip() or None
        profile_photo_path = request.form.get("profile_photo_path", "").strip() or None
        
        # Validation
        if not all([name, email, phone, password, age, city, experience, skills]):
            return jsonify({"error": "All required fields must be filled"}), 400
        
        # Validate file paths exist
        for path, field_name in [(aadhaar_path, "Aadhaar"), (license_path, "License"), 
                                 (certificate_path, "Certificate"), (profile_photo_path, "Profile photo")]:
            if path and not os.path.exists(path):
                return jsonify({"error": f"{field_name} file not found: {path}"}), 400
        
        # Create mechanic
        try:
            mechanic_id = mechanic_db.create_mechanic(
                name=name, email=email, phone=phone, password=password,
                age=int(age), city=city, experience=int(experience), skills=skills,
                aadhaar_path=aadhaar_path, license_path=license_path,
                certificate_path=certificate_path, profile_photo_path=profile_photo_path
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
        return jsonify({
            "success": True,
            "message": "Signup successful. You can now login.",
            "mechanic_id": mechanic_id
        }), 201
        
    except Exception as e:
        print(f"❌ Mechanic signup error: {e}")
        return jsonify({"error": "Failed to create mechanic account"}), 500

@mechanic_bp.route("/api/car/mechanic/login", methods=["POST"])
def mechanic_login():
    """Mechanic login endpoint"""
    try:
        email = request.json.get("email", "").strip()
        password = request.json.get("password", "").strip()
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # First try mechanic database
        mechanic = mechanic_db.verify_mechanic(email, password)
        if mechanic:
            # Check if approved
            if mechanic.get("status") != "APPROVED":
                return jsonify({
                    "error": "Your account is not approved",
                    "status": mechanic.get("status")
                }), 403
            
            # Generate token
            from auth_utils import generate_token
            token = generate_token(email)
            
            # Remove sensitive data
            mechanic_data = {
                "id": mechanic["id"],
                "name": mechanic["name"],
                "email": mechanic["email"],
                "phone": mechanic["phone"],
                "city": mechanic["city"],
                "experience": mechanic["experience"],
                "skills": mechanic["skills"],
                "is_online": mechanic["is_online"]
            }
            
            return jsonify({
                "success": True,
                "token": token,
                "mechanic": mechanic_data
            }), 200
        
        # If not found in mechanic DB, try worker DB for mechanics
        from services.car_service.worker_db import worker_db
        worker = worker_db.verify_worker_by_email(email, password)
        if worker and worker.get("role") == "Mechanic":
            # Check if approved
            if worker.get("status") != "APPROVED":
                return jsonify({
                    "error": "Your account is not approved",
                    "status": worker.get("status")
                }), 403
            
            # Generate token
            from auth_utils import generate_token
            token = generate_token(email)
            
            # Convert worker data to mechanic format
            mechanic_data = {
                "id": worker["id"],
                "name": worker["name"],
                "email": worker["email"],
                "phone": worker["phone"],
                "city": worker["city"],
                "experience": worker["experience"],
                "skills": worker["skills"],
                "is_online": 0  # Workers don't have online status
            }
            
            return jsonify({
                "success": True,
                "token": token,
                "mechanic": mechanic_data
            }), 200
        
        return jsonify({"error": "Invalid email or password"}), 401
        
    except Exception as e:
        print(f"❌ Mechanic login error: {e}")
        return jsonify({"error": "Login failed"}), 500

@mechanic_bp.route("/api/car/mechanic/status", methods=["PUT"])
def update_mechanic_status():
    """Update mechanic online/offline status"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        # Get new status
        is_online = request.json.get("is_online", False)
        
        # First try mechanic database
        mechanic = mechanic_db.get_mechanic_by_email(email)
        if mechanic:
            # Update status in mechanic database
            success = mechanic_db.set_online_status(mechanic["id"], is_online)
            if success:
                return jsonify({
                    "success": True,
                    "message": f"You are now {'ONLINE' if is_online else 'OFFLINE'}",
                    "is_online": is_online
                }), 200
            else:
                return jsonify({"error": "Failed to update status"}), 500
        
        # If not in mechanic DB, try worker DB
        from services.car_service.worker_db import worker_db
        worker = worker_db.get_worker_by_email(email)
        if worker and worker.get("role") == "Mechanic":
            # Update worker online status
            success = worker_db.set_worker_online_status(worker["id"], is_online)
            if success:
                return jsonify({
                    "success": True,
                    "message": f"You are now {'ONLINE' if is_online else 'OFFLINE'}",
                    "is_online": is_online
                }), 200
            else:
                return jsonify({"error": "Failed to update worker status"}), 500
        
        return jsonify({"error": "Mechanic not found"}), 404
            
    except Exception as e:
        print(f"❌ Update mechanic status error: {e}")
        return jsonify({"error": "Failed to update status"}), 500

@mechanic_bp.route("/api/car/mechanic/profile", methods=["GET"])
def get_mechanic_profile():
    """Get mechanic profile"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        mechanic = mechanic_db.get_mechanic_by_email(email)
        if not mechanic:
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Remove sensitive data
        mechanic_data = dict(mechanic)
        mechanic_data.pop("password_hash", None)
        
        return jsonify({"mechanic": mechanic_data}), 200
        
    except Exception as e:
        print(f"❌ Get mechanic profile error: {e}")
        return jsonify({"error": "Failed to get profile"}), 500

@mechanic_bp.route("/api/car/mechanics/online", methods=["GET"])
def get_online_mechanics():
    """Get all online mechanics"""
    try:
        mechanics = mechanic_db.get_online_mechanics()
        
        # Remove sensitive data
        clean_mechanics = []
        for mechanic in mechanics:
            clean_mechanic = dict(mechanic)
            clean_mechanic.pop("password_hash", None)
            clean_mechanics.append(clean_mechanic)
        
        return jsonify({"mechanics": clean_mechanics}), 200
        
    except Exception as e:
        print(f"❌ Get online mechanics error: {e}")
        return jsonify({"error": "Failed to get online mechanics"}), 500

# ===== STATUS MANAGEMENT ENDPOINTS =====

@mechanic_bp.route("/api/car/mechanic/go-online", methods=["PUT"])
def go_online():
    """Set mechanic to ONLINE status"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        mechanic = mechanic_db.get_mechanic_by_email(email)
        if not mechanic:
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Set to ONLINE
        success = mechanic_db.set_online(mechanic["id"])
        if success:
            return jsonify({
                "success": True,
                "message": "You are now ONLINE",
                "status": "ONLINE"
            }), 200
        else:
            return jsonify({"error": "Failed to go online"}), 500
            
    except Exception as e:
        print(f"❌ Go online error: {e}")
        return jsonify({"error": "Failed to update status"}), 500

@mechanic_bp.route("/api/car/mechanic/go-offline", methods=["PUT"])
def go_offline():
    """Set mechanic to OFFLINE status"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        mechanic = mechanic_db.get_mechanic_by_email(email)
        if not mechanic:
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Set to OFFLINE
        success = mechanic_db.set_offline(mechanic["id"])
        if success:
            return jsonify({
                "success": True,
                "message": "You are now OFFLINE",
                "status": "OFFLINE"
            }), 200
        else:
            return jsonify({"error": "Failed to go offline"}), 500
            
    except Exception as e:
        print(f"❌ Go offline error: {e}")
        return jsonify({"error": "Failed to update status"}), 500

@mechanic_bp.route("/api/car/mechanic/set-busy", methods=["PUT"])
def set_busy():
    """Set mechanic to BUSY status"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        mechanic = mechanic_db.get_mechanic_by_email(email)
        if not mechanic:
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Set to BUSY
        success = mechanic_db.set_busy(mechanic["id"])
        if success:
            return jsonify({
                "success": True,
                "message": "Status changed to BUSY",
                "status": "BUSY",
                "note": "You will not receive new jobs until current job completes"
            }), 200
        else:
            return jsonify({"error": "Failed to set busy status"}), 500
            
    except Exception as e:
        print(f"❌ Set busy error: {e}")
        return jsonify({"error": "Failed to update status"}), 500

@mechanic_bp.route("/api/car/mechanic/set-available", methods=["PUT"])
def set_available():
    """Set mechanic to AVAILABLE status"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        mechanic = mechanic_db.get_mechanic_by_email(email)
        if not mechanic:
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Set to AVAILABLE
        success = mechanic_db.set_available(mechanic["id"])
        if success:
            return jsonify({
                "success": True,
                "message": "Job completed",
                "status": "ONLINE",
                "note": "You can now receive new jobs"
            }), 200
        else:
            return jsonify({"error": "Failed to set available status"}), 500
            
    except Exception as e:
        print(f"❌ Set available error: {e}")
        return jsonify({"error": "Failed to update status"}), 500

@mechanic_bp.route("/api/car/mechanic/status", methods=["GET"])
def get_mechanic_status():
    """Get mechanic's current status"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        mechanic = mechanic_db.get_mechanic_by_email(email)
        if not mechanic:
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Get current status
        status = mechanic_db.get_mechanic_status(mechanic["id"])
        
        return jsonify({
            "status": status,
            "is_online": mechanic.get("is_online", 0),
            "is_busy": mechanic.get("is_busy", 0),
            "service_radius": mechanic.get("service_radius", 10),
            "current_city": mechanic.get("current_city", "Not set"),
            "last_status_update": mechanic.get("last_status_update"),
            "cooldown_until": mechanic.get("cooldown_until")
        }), 200
        
    except Exception as e:
        print(f"❌ Get mechanic status error: {e}")
        return jsonify({"error": "Failed to get status"}), 500

@mechanic_bp.route("/api/car/mechanics/available", methods=["GET"])
def get_available_mechanics():
    """Get all available mechanics (ONLINE and not BUSY)"""
    try:
        mechanics = mechanic_db.get_available_mechanics()
        
        # Remove sensitive data
        clean_mechanics = []
        for mechanic in mechanics:
            clean_mechanic = dict(mechanic)
            clean_mechanic.pop("password_hash", None)
            clean_mechanics.append(clean_mechanic)
        
        return jsonify({"mechanics": clean_mechanics}), 200
        
    except Exception as e:
        print(f"❌ Get available mechanics error: {e}")
        return jsonify({"error": "Failed to get available mechanics"}), 500

# ===== ADDITIONAL FEATURES =====

@mechanic_bp.route("/api/car/mechanic/service-radius", methods=["PUT"])
def update_service_radius():
    """Update mechanic service radius"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        mechanic = mechanic_db.get_mechanic_by_email(email)
        if not mechanic:
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Get new radius
        radius = request.json.get("radius", 10)
        
        try:
            radius = int(radius)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid radius value"}), 400
        
        # Update service radius
        success = mechanic_db.update_service_radius(mechanic["id"], radius)
        if success:
            return jsonify({
                "success": True,
                "message": f"Service radius updated to {radius} km",
                "service_radius": radius
            }), 200
        else:
            return jsonify({"error": "Failed to update service radius"}), 500
            
    except Exception as e:
        print(f"❌ Update service radius error: {e}")
        return jsonify({"error": "Failed to update service radius"}), 500

@mechanic_bp.route("/api/car/mechanic/location", methods=["PUT"])
def update_current_location():
    """Update mechanic current working city"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        mechanic = mechanic_db.get_mechanic_by_email(email)
        if not mechanic:
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Get new city
        city = request.json.get("city", "").strip()
        
        if not city:
            return jsonify({"error": "City is required"}), 400
        
        # Update current city
        success = mechanic_db.update_current_location(mechanic["id"], city)
        if success:
            return jsonify({
                "success": True,
                "message": f"Current location updated to {city}",
                "current_city": city
            }), 200
        else:
            return jsonify({"error": "Failed to update location"}), 500
            
    except Exception as e:
        print(f"❌ Update location error: {e}")
        return jsonify({"error": "Failed to update location"}), 500

# ===== WOW FEATURES =====

@mechanic_bp.route("/api/car/mechanics/high-demand-areas", methods=["GET"])
def get_high_demand_areas():
    """Get high demand areas"""
    try:
        areas = mechanic_db.get_high_demand_areas()
        return jsonify({"areas": areas}), 200
        
    except Exception as e:
        print(f"❌ Get high demand areas error: {e}")
        return jsonify({"error": "Failed to get demand data"}), 500

@mechanic_bp.route("/api/car/mechanics/recommended-online-time", methods=["GET"])
def get_recommended_online_time():
    """Get recommended time to go online"""
    try:
        recommendation = mechanic_db.get_recommended_online_time()
        return jsonify(recommendation), 200
        
    except Exception as e:
        print(f"❌ Get recommended online time error: {e}")
        return jsonify({"error": "Failed to get recommendation"}), 500
