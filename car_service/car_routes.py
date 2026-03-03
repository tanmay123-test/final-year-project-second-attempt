import os
import sys
from flask import Blueprint, request, jsonify
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_utils import verify_token
from user_db import UserDB
from car_service.car_profile_db import car_profile_db

car_bp = Blueprint("car", __name__)

def _current_user_id():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth.split(" ")[1]
    username = verify_token(token)
    if not username:
        return None
    db = UserDB()
    return db.get_user_by_username(username)

@car_bp.route("/api/car/setup-profile", methods=["POST"])
def setup_profile():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json() or {}
    city = data.get("city", "").strip()
    address = data.get("address", "").strip()
    emergency_name = data.get("emergency_contact_name", "").strip()
    emergency_phone = data.get("emergency_contact_phone", "").strip()
    brand = data.get("brand", "").strip()
    model = data.get("model", "").strip()
    year = data.get("year")
    fuel = data.get("fuel_type", "").strip()
    reg = data.get("registration_number", "").strip()
    if not all([city, address, emergency_name, emergency_phone, brand, model, year, fuel, reg]):
        return jsonify({"error": "All fields are required"}), 400
    car_profile_db.create_car_profile(user_id, city, address, emergency_name, emergency_phone)
    car_profile_db.add_car(user_id, brand, model, int(year), fuel, reg, set_default=True)
    return jsonify({"success": True}), 201

@car_bp.route("/api/car/profile", methods=["GET"])
def get_profile():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    profile = car_profile_db.get_car_profile(user_id)
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    return jsonify({"profile": profile}), 200

@car_bp.route("/api/car/cars", methods=["GET"])
def get_cars():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    cars = car_profile_db.get_user_cars(user_id)
    return jsonify({"cars": cars}), 200

@car_bp.route("/api/car/add-car", methods=["POST"])
def add_car():
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json() or {}
    brand = data.get("brand", "").strip()
    model = data.get("model", "").strip()
    year = data.get("year")
    fuel = data.get("fuel_type", "").strip()
    reg = data.get("registration_number", "").strip()
    if not all([brand, model, year, fuel, reg]):
        return jsonify({"error": "All fields are required"}), 400
    car_profile_db.add_car(user_id, brand, model, int(year), fuel, reg, set_default=False)
    return jsonify({"success": True}), 201

# ================= BOOKING MANAGEMENT =================

@car_bp.route("/api/car/jobs", methods=["GET"])
def get_user_jobs():
    """Get all jobs for current user"""
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    from .booking_db import booking_db
    jobs = booking_db.get_user_jobs(user_id)
    return jsonify({"jobs": jobs}), 200

@car_bp.route("/api/car/jobs/active", methods=["GET"])
def get_active_job():
    """Get active job for current user"""
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    from .booking_db import booking_db
    active_job = booking_db.get_active_job(user_id)
    if active_job:
        return jsonify({"job": active_job}), 200
    else:
        return jsonify({"job": None}), 200

@car_bp.route("/api/car/jobs/<int:job_id>/notes", methods=["PUT"])
def add_job_notes(job_id):
    """Add notes to a job"""
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    notes = data.get("notes", "").strip()
    
    if not notes:
        return jsonify({"error": "Notes cannot be empty"}), 400
    
    from .booking_db import booking_db
    booking_db.update_job_status(job_id, "WORKING", notes)
    return jsonify({"success": True}), 200

@car_bp.route("/api/car/jobs/<int:job_id>/cancel", methods=["PUT"])
def cancel_job(job_id):
    """Cancel a job"""
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    reason = data.get("reason", "User cancelled").strip()
    
    from .booking_db import booking_db
    booking_db.update_job_status(job_id, "CANCELLED", reason)
    return jsonify({"success": True}), 200

# ================= PROFILE MANAGEMENT =================

@car_bp.route("/api/car/profile", methods=["PUT"])
def update_profile():
    """Update user car service profile"""
    user_id = _current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    city = data.get("city", "").strip()
    address = data.get("address", "").strip()
    emergency_name = data.get("emergency_contact_name", "").strip()
    emergency_phone = data.get("emergency_contact_phone", "").strip()
    
    if not city or not address or not emergency_name or not emergency_phone:
        return jsonify({"error": "All fields are required"}), 400
    
    from .car_profile_db import car_profile_db
    success = car_profile_db.update_profile(user_id, city, address, emergency_name, emergency_phone)
    
    if success:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Failed to update profile"}), 500
