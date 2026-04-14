import sys

# Configure stdout and stderr for UTF-8 output to fix emoji printing issues on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from flask import Flask, request, jsonify, session, send_file, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
import os
import re
import json
import bcrypt
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from functools import wraps
import requests
import logging
import time
from data.meeting_utils import generate_meeting_link as create_meeting_link
import random
from user_db import UserDB
from worker_db import WorkerDB
from appointment_db import AppointmentDB
from subscription_db import SubscriptionDB
from message_db import MessageDB
from availability_db import AvailabilityDB
from event_db import EventDB
from emergency_detector import is_emergency

from auth_utils import generate_token, verify_token
from otp_service import send_otp, verify_otp
from email_service import send_email
from config import (EXPERT_IMAGES_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE)

from video_db import VideoConsultDB
from expert_db import ExpertDB
from expert_chat_db import ExpertChatDB

import appointment_db
print("USING appointment_db FROM:", appointment_db.__file__)

from video_db import VideoConsultDB
from notification_service import notify_user, notify_doctor
# from payment_service import payment_service

# Import subscription system
# from services.subscription.subscription_service import subscription_service
from services.subscription.subscription_routes import subscription_bp

# Import video consultation system
from services.video_signaling import init_video_signaling
from services.video_session_db import video_session_db
from routes.video_routes import video_bp

# Import freelance system
from services.freelance.routes.freelance_routes import freelance_bp
from services.freelance.socket_handlers import handle_freelance_socket_events

# Import money management system
from services.money_service.routes.money_routes import money_bp

video_db = VideoConsultDB()
video_db.create_table()

from datetime import datetime

app = Flask(__name__)
from flask_cors import CORS

CORS(app, resources={r"/*": {
    "origins": ["https://final-year-project-second-attempt.vercel.app", "http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

@app.route("/")
def root():
    return jsonify({"message": "Backend is running!"}), 200

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.errorhandler(404)
def not_found(e):
    print(f"  [404 ERROR] {request.method} {request.path}")
    return jsonify({"error": "Not Found", "path": request.path}), 404

def register_blueprints(app):
    """Register all blueprints with detailed logging"""
    print("\n📦 Registering Blueprints...")
    
    # Register subscription blueprint
    try:
        app.register_blueprint(subscription_bp)
        print("  ✅ Subscription blueprint registered")
    except Exception as e:
        print(f"  ❌ Failed to register subscription blueprint: {e}")

    # Register payment blueprint
    try:
        from services.payment.payments.payment_route import payment_bp
        app.register_blueprint(payment_bp)
        print("  ✅ Payment blueprint registered")
    except ImportError as e:
        print(f"  ⚠️ Could not register payment blueprint: {e} (Using demo mode)")
    except Exception as e:
        print(f"  ❌ Error registering payment blueprint: {e}")

    # Register freelance blueprint
    try:
        app.register_blueprint(freelance_bp)
        print("  ✅ Freelance marketplace blueprint registered")
    except Exception as e:
        print(f"  ❌ Failed to register freelance blueprint: {e}")

    # Register money management blueprint
    try:
        app.register_blueprint(money_bp)
        print("  ✅ Money management blueprint registered")
    except Exception as e:
        print(f"  ❌ Failed to register money management blueprint: {e}")

    # Register healthcare blueprints
    try:
        from services.healthcare.routes.healthcare_routes import healthcare_bp
        from services.healthcare.doctor_routes import doctor_bp
        app.register_blueprint(healthcare_bp)
        app.register_blueprint(doctor_bp)
        print("  ✅ Healthcare blueprints registered")
    except Exception as e:
        print(f"  ❌ Could not register healthcare blueprints: {e}")

    # Register video consultation blueprint
    try:
        app.register_blueprint(video_bp)
        print("  ✅ Video consultation blueprint registered")
    except Exception as e:
        print(f"  ❌ Failed to register video consultation blueprint: {e}")

    # Register Housekeeping blueprints
    print("  🏠 Housekeeping:")
    try:
        from services.housekeeping.arrival.backend.controllers.arrival_controller import arrival_bp
        app.register_blueprint(arrival_bp, url_prefix='/api/arrival')
        print("    ✅ Arrival blueprint registered")
    except Exception as e:
        print(f"    ❌ Could not register Arrival blueprint: {e}")

    try:
        from services.housekeeping.provider.backend.controllers.auth_controller import provider_auth_bp
        app.register_blueprint(provider_auth_bp, url_prefix='/api/provider')
        print("    ✅ Provider Auth blueprint registered")
    except Exception as e:
        print(f"    ❌ Could not register Provider Auth blueprint: {e}")

    try:
        from services.housekeeping.controllers.booking_controller import housekeeping_bp
        app.register_blueprint(housekeeping_bp, url_prefix='/api/housekeeping')
        print("    ✅ Booking blueprint registered")
    except Exception as e:
        print(f"    ❌ Could not register Housekeeping Booking blueprint: {e}")

    try:
        from services.housekeeping.arrival.backend.controllers.ai_advisor_controller import ai_advisor_bp
        app.register_blueprint(ai_advisor_bp, url_prefix='/api/ai')
        print("    ✅ AI Advisor blueprint registered")
    except Exception as e:
        print(f"    ❌ Could not register AI Advisor blueprint: {e}")

    try:
        from housekeeping.ai_features.ai_routes import ai_features_bp
        app.register_blueprint(ai_features_bp)
        print("    ✅ AI Features blueprint registered")
    except Exception as e:
        print(f"    ❌ Could not register AI Features blueprint: {e}")

    # Register car service blueprints
    print("  🚗 Car Service:")
    try:
        from car_service.car_routes import car_bp
        app.register_blueprint(car_bp)
        print("    ✅ Car routes blueprint registered")
    except Exception as e:
        print(f"    ❌ Could not register car service blueprint: {e}")

    try:
        from car_service.car_service_worker_routes import car_service_worker_bp
        app.register_blueprint(car_service_worker_bp)
        print("    ✅ Unified worker routes blueprint registered")
    except Exception as e:
        print(f"    ❌ Could not register unified worker routes blueprint: {e}")

    # Register other car service blueprints (consolidated)
    car_blueprints = [
        ('trip_routes', 'trip_bp', 'Trip planner'),
        ('worker_routes', 'worker_bp', 'Worker routes'),
        ('mechanic_routes', 'mechanic_bp', 'Mechanic routes'),
        ('dispatch.routes', 'dispatch_bp', 'Dispatch routes'),
        ('dispatch.active_routes', 'active_bp', 'Active job routes'),
        ('dispatch.earnings_routes', 'earnings_bp', 'Earnings routes'),
        ('dispatch.performance_routes', 'performance_bp', 'Performance routes'),
        ('smart_search_routes', 'smart_search_bp', 'Smart search routes'),
        ('truck_operator_routes', 'truck_operator_bp', 'Truck operator routes'),
        ('automobile_expert_routes', 'automobile_expert_bp', 'Automobile Expert'),
        ('expert_availability_routes', 'expert_availability_bp', 'Expert Availability'),
        ('consultation_session_routes', 'consultation_session_bp', 'Consultation Session'),
        ('expert_history_routes', 'expert_history_bp', 'Expert History')
    ]
    
    for module, bp_name, label in car_blueprints:
        try:
            # First try to import from car_service
            try:
                exec(f"from car_service.{module} import {bp_name}")
                exec(f"app.register_blueprint({bp_name})")
                print(f"    ✅ {label} blueprint registered from car_service")
            except ImportError:
                # If that fails, try to import from services.car_service
                exec(f"from services.car_service.{module} import {bp_name}")
                exec(f"app.register_blueprint({bp_name})")
                print(f"    ✅ {label} blueprint registered from services.car_service")
        except Exception as e:
            print(f"    ❌ Could not register {label} blueprint: {e}")

    # Special case for Ask Expert (needs init)
    try:
        from car_service.ask_expert import ask_expert_bp, init_ask_expert_db
        app.register_blueprint(ask_expert_bp)
        init_ask_expert_db(app)
        print("    ✅ Ask Expert blueprint registered and initialized")
    except Exception as e:
        print(f"    ❌ Could not register Ask Expert blueprint: {e}")

register_blueprints(app)

# Register Fuel Delivery blueprint
try:
    from car_service.fuel_delivery_routes import fuel_delivery_bp
    app.register_blueprint(fuel_delivery_bp, url_prefix='/api/fuel-delivery')
    print("  Fuel Delivery blueprint registered")
except Exception as e:
    print(f"   Could not register Fuel Delivery blueprint: {e}")

# Register Admin blueprint
try:
    from admin.admin_routes import admin_bp
    from admin.admin_users import users_admin_bp
    from admin.admin_workers import workers_admin_bp
    from admin.admin_appointments import appts_admin_bp
    from admin.admin_healthcare import healthcare_admin_bp
    
    app.register_blueprint(admin_bp)
    app.register_blueprint(users_admin_bp, url_prefix='/admin/users')
    app.register_blueprint(workers_admin_bp, url_prefix='/admin/workers')
    app.register_blueprint(appts_admin_bp, url_prefix='/admin/appointments')
    app.register_blueprint(healthcare_admin_bp, url_prefix='/admin/healthcare-mgmt')
    
    print("  ✅ All Admin blueprints registered")
except Exception as e:
    print(f"   ❌ Could not register Admin blueprints: {e}")

# Register Tow Truck blueprint
try:
    from car_service.tow_truck_routes import tow_truck_bp
    # CORS must be applied BEFORE registration
    CORS(tow_truck_bp, origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"])
    app.register_blueprint(tow_truck_bp, url_prefix='/api/tow-truck')
    
    # NEW TOW TRUCK BLUEPRINT
    from car_service.tow_truck.routes import tow_bp
    app.register_blueprint(tow_bp)
    
    print("  Tow Truck blueprint registered")
except Exception as e:
    print(f"   Could not register Tow Truck blueprint: {e}")

# Initialize WebSocket signaling server
socketio = init_video_signaling(app)

# Initialize Housekeeping Socket
try:
    from services.housekeeping.socket_handlers import init_housekeeping_socket
    init_housekeeping_socket(socketio)
    print("  Housekeeping socket initialized")
except Exception as e:
    print(f"   Could not initialize housekeeping socket: {e}")

# Initialize Healthcare Socket
try:
    from services.healthcare.socket_handlers import init_healthcare_socket, emit_new_appointment, emit_appointment_update
    init_healthcare_socket(socketio)
    print("  Healthcare socket initialized")
except Exception as e:
    print(f"   Could not initialize healthcare socket: {e}")
    # Provide fallback empty functions to avoid NameErrors
    def emit_new_appointment(*args, **kwargs): pass
    def emit_appointment_update(*args, **kwargs): pass

# Initialize Freelance Socket
try:
    handle_freelance_socket_events(socketio)
    print("  Freelance socket initialized")
except Exception as e:
    print(f"   Could not initialize freelance socket: {e}")

# ================= DATABASE =================
user_db = UserDB()
worker_db = WorkerDB()
appt_db = AppointmentDB()
message_db = MessageDB()
availability_db = AvailabilityDB()
event_db = EventDB()
subscription_db = SubscriptionDB()
expert_db = ExpertDB()
expert_chat_db = ExpertChatDB()

# ================= AUTH =====================
def require_auth():
    auth = request.headers.get("Authorization")
    if not auth:
        return None
    try:
        return verify_token(auth.split(" ")[1])
    except:
        return None

def require_worker_auth():
    auth = request.headers.get("Authorization")
    if not auth:
        return None
    try:
        return verify_token(auth.split(" ")[1])
    except:
        return None


# ================= SERVICES =================
@app.route("/services")
def get_services():
    services = [
        {"id": "healthcare", "label": "Healthcare", "path": "/doctors"},
        {"id": "housekeeping", "label": "Housekeeping", "path": "/housekeeping/home"},
        {"id": "freelance", "label": "Freelance Marketplace", "path": "/freelance/home"},
        {"id": "car", "label": "Car Services", "path": "/worker/car/login"},
        {"id": "money", "label": "Money Management", "path": "/worker/money/login"}
    ]
    return jsonify({"services": services}), 200


# ================= USER AUTH =================
@app.route("/signup", methods=["POST"])
def signup():
    try:
        d = request.json
        
        # Handle both name and username fields
        name = d.get("name", "")
        username = d.get("username") or d.get("email", "").split("@")[0]  # Use email prefix as username
        
        if user_db.user_exists(username, d["email"]):
            return jsonify({"error": "User exists"}), 400

        user_db.create_user(name, username, d["password"], d["email"])
        send_otp(d["email"])
        return jsonify({"msg": "OTP sent"}), 201
    except Exception as e:
        print(f"User signup error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/verify-otp", methods=["POST"])
def verify_user_otp():
    ok, msg = verify_otp(request.json["email"], request.json["otp"])
    if not ok:
        return jsonify({"error": msg}), 400
    user_db.mark_verified(request.json["email"])
    return jsonify({"msg": "Verified"}), 200


@app.route("/resend-otp", methods=["POST"])
def resend_user_otp():
    send_otp(request.json["email"])
    return jsonify({"msg": "OTP resent"}), 200


@app.route("/login", methods=["POST"])
def login():
    # Accept both email and username for flexibility
    email = request.json.get("email") or request.json.get("username")
    password = request.json["password"]
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    ok, msg = user_db.verify_user(email, password)
    if not ok:
        return jsonify({"error": msg}), 401

    user_data = user_db.get_user_by_username(email)
    print(f"User data from get_user_by_username: {user_data}")  # Debug log
    
    # Handle different possible return formats
    if user_data is None:
        return jsonify({"error": "User data not found"}), 404
    
    # If user_data is an integer (ID), create basic user info
    if isinstance(user_data, int):
        return jsonify({
            "token": generate_token(email),
            "id": user_data,
            "name": email.split("@")[0],  # Use email prefix as name
            "email": email,
            "success": True
        }), 200
    
    # If user_data is a list/tuple, extract values
    if isinstance(user_data, (list, tuple)) and len(user_data) >= 2:
        return jsonify({
            "token": generate_token(email),
            "id": user_data[0],
            "name": user_data[1],
            "email": email,
            "success": True
        }), 200
    
    # If user_data is a dictionary, extract values
    if isinstance(user_data, dict):
        return jsonify({
            "token": generate_token(email),
            "id": user_data.get("id"),
            "name": user_data.get("name", email.split("@")[0]),
            "email": email,
            "success": True
        }), 200
    
    # Fallback
    return jsonify({
        "token": generate_token(email),
        "id": None,
        "name": email.split("@")[0],
        "email": email,
        "success": True
    }), 200


@app.route("/user/info")
def user_info():
    username = require_auth()
    if not username:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Get user details
    user_id = user_db.get_user_by_username(username)
    if not user_id:
        return jsonify({"error": "User not found"}), 404
    
    user_data = user_db.get_user_by_id(user_id)
    if not user_data:
        return jsonify({"error": "User details not found"}), 404
    
    return jsonify({
        "user_id": user_id,
        "user_name": user_data["name"],
        "username": username,
        "email": user_data["email"]
    }), 200


# ================= HEALTHCARE =================
@app.route("/healthcare/specializations")
def get_specializations():
    DEFAULT = [
        "Dentist","Eye Specialist","Cardiologist","Orthopedic","ENT",
        "Dermatologist","Neurologist","Psychiatrist","Gynecologist",
        "Pediatrician","General Physician","Urologist","Oncologist"
    ]
    db_specs = worker_db.get_all_specializations('healthcare') or []
    return jsonify({"specializations": sorted(set(DEFAULT + db_specs))}), 200


@app.route("/healthcare/doctors")
def get_all_doctors():
    """Get all available doctors"""
    try:
        # Only get healthcare workers
        doctors = worker_db.get_workers_by_service("healthcare")
        # Filter only approved workers
        approved_doctors = [doctor for doctor in doctors if doctor.get('status') == 'approved']
        return jsonify({"doctors": approved_doctors}), 200
    except Exception as e:
        print(f"  Error fetching doctors: {e}")
        return jsonify({"error": "Failed to fetch doctors", "doctors": []}), 500


@app.route("/healthcare/doctors/<specialization>")
def doctors_by_specialization(specialization):
    try:
        # Get healthcare workers by specialization
        all_doctors = worker_db.get_workers_by_specialization(
            specialization.lower()
        )
        # Filter only healthcare workers and approved ones
        healthcare_doctors = [doctor for doctor in all_doctors if doctor.get('service') == 'healthcare' and doctor.get('status') == 'approved']
        return jsonify({"doctors": healthcare_doctors}), 200
    except Exception as e:
        print(f"  Error fetching doctors by specialization: {e}")
        return jsonify({"error": "Failed to fetch doctors", "doctors": []}), 500


@app.route("/healthcare/search")
def search_doctors():
    return jsonify({
        "doctors": worker_db.search_workers(request.args.get("q"))
    }), 200


# ================= AVAILABILITY =================
@app.route("/worker/<int:worker_id>/availability", methods=["GET"])
def get_worker_availability(worker_id):
    date = request.args.get("date")
    availability = availability_db.get_availability(worker_id, date)
    
    # Enrich availability with booking status from Housekeeping
    try:
        from services.housekeeping.services.booking_service import BookingService
        hk_booking_service = BookingService()
        
        enriched = []
        # Open one connection for all checks
        conn = hk_booking_service.db.get_conn()
        cursor = conn.cursor()
        
        for slot in availability:
            try:
                # Check for conflicts in housekeeping bookings
                # Use standard ? placeholder for SQLite which hk_booking_service uses
                cursor.execute("""
                    SELECT count(*) FROM bookings 
                    WHERE worker_id = ? AND booking_date = ? AND time_slot = ? 
                    AND status IN ('ACCEPTED', 'IN_PROGRESS', 'ASSIGNED', 'REQUESTED')
                """, (int(worker_id), str(slot['date']), str(slot['time_slot'])))
                count = cursor.fetchone()[0]
                slot['is_booked'] = count > 0
            except Exception as e:
                print(f"  Conflict check error for slot {slot}: {e}")
                slot['is_booked'] = False
            
            enriched.append(slot)
        
        conn.close()
        return jsonify({
            "availability": enriched
        }), 200
    except Exception as e:
        print(f"   Availability enrichment error: {e}")
        return jsonify({
            "availability": availability
        }), 200


@app.route("/worker/<int:worker_id>/availability", methods=["POST"])
def add_worker_availability(worker_id):
    d = request.json
    
    # Validate input data
    if not d:
        return jsonify({"error": "No data provided"}), 400
    
    date = d.get("date", "").strip()
    time_slot = d.get("time_slot", "").strip()
    
    # Validate date
    if not date:
        return jsonify({"error": "Date is required"}), 400
    
    # Validate time slot
    if not time_slot:
        return jsonify({"error": "Time slot is required"}), 400
    
    # Validate time slot format (should be HH:MM-HH:MM)
    import re
    if not re.match(r'^\d{2}:\d{2}-\d{2}:\d{2}$', time_slot):
        return jsonify({"error": "Invalid time slot format. Use HH:MM-HH:MM format"}), 400
    
    # Validate date format (YYYY-MM-DD)
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD format"}), 400
    
    ok, msg = availability_db.add_availability(
        worker_id, date, time_slot
    )
    if not ok:
        return jsonify({"error": msg}), 400
    return jsonify({"msg": msg}), 200


@app.route("/worker/<int:worker_id>/availability", methods=["DELETE"])
def remove_worker_availability(worker_id):
    d = request.json
    availability_db.remove_availability(worker_id, d["date"], d["time_slot"])
    return jsonify({"msg": "Availability removed"}), 200


# ================= CLINIC BOOKING =================
@app.route("/appointment/book", methods=["POST"])
def book_clinic():
    d = request.json
    
    print(f"  Clinic booking request: {d}")
    print(f"  Request data types: {[(k, type(v)) for k, v in d.items()]}")

    # Validate required fields
    required_fields = ["user_id", "worker_id", "user_name", "symptoms", "date", "time_slot"]
    missing_fields = [field for field in required_fields if field not in d]
    if missing_fields:
        print(f"  Missing required fields: {missing_fields}")
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Optional insurance
    insurance_details = d.get("insurance_details")

    can_book, message = subscription_db.check_appointment_limit(d["worker_id"])
    if not can_book:
        print(f"  Subscription limit exceeded: {message}")
        return jsonify({"error": message}), 402

    ok, result = appt_db.book_clinic(
        int(d["user_id"]),
        int(d["worker_id"]),
        d["user_name"],
        d["symptoms"],
        d["date"],
        d["time_slot"],
        insurance_details
    )

    if not ok:
        print(f"  Clinic booking failed: {result}")
        return jsonify({"error": str(result)}), 409

    print(f"  Clinic booking successful: {result}")

    subscription = subscription_db.get_doctor_subscription(d["worker_id"])
    if subscription:
        subscription_db.update_subscription_usage(
            d["worker_id"], subscription["plan_id"]
        )

    try:
        send_email(
            to_email="doctor@email.com",
            subject="New Clinic Appointment",
            body=f"Appointment ID {result} awaiting approval"
        )
        print(f"  Clinic booking notification sent")
    except Exception as e:
        print(f"   Failed to send clinic booking email: {e}")

    # Emit socket event to doctor
    try:
        appointment_data = {
            "id": result,
            "user_id": d["user_id"],
            "user_name": d["user_name"],
            "symptoms": d["symptoms"],
            "date": d["date"],
            "time_slot": d["time_slot"],
            "appointment_type": "clinic",
            "status": "pending"
        }
        emit_new_appointment(socketio, appointment_data, d["worker_id"])
    except Exception as e:
        print(f"   Failed to emit clinic booking socket event: {e}")

    return jsonify({"success": True, "appointment_id": result}), 201


# ================= VIDEO BOOKING =================
@app.route("/appointment/video-request", methods=["POST"])
def video_request():
    d = request.json
    
    print(f"  Video consultation request: {d}")

    # Validate required fields
    required_fields = ["user_id", "worker_id", "user_name", "symptoms"]
    missing_fields = [field for field in required_fields if field not in d]
    if missing_fields:
        print(f"  Missing required fields: {missing_fields}")
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Optional insurance
    insurance_details = d.get("insurance_details")

    # Check appointment limit
    can_book, message = subscription_db.check_appointment_limit(d["worker_id"])
    if not can_book:
        print(f"  Subscription limit exceeded: {message}")
        return jsonify({"error": message}), 402

    apt_id = appt_db.book_video(
        d["user_id"],
        d["worker_id"],
        d["user_name"],
        d["symptoms"],
        insurance_details
    )

    print(f"  Video consultation booked with ID: {apt_id}")

    try:
        send_email(
            to_email="doctor@email.com",
            subject="  New Video Consultation Request",
            body=f"Appointment ID {apt_id} awaiting approval"
        )
        print(f"  Video consultation notification sent")
    except Exception as e:
        print(f"   Failed to send video consultation email: {e}")

    # Emit socket event to doctor
    try:
        appointment_data = {
            "id": apt_id,
            "user_id": d["user_id"],
            "user_name": d["user_name"],
            "symptoms": d["symptoms"],
            "appointment_type": "video",
            "status": "pending"
        }
        emit_new_appointment(socketio, appointment_data, d["worker_id"])
    except Exception as e:
        print(f"   Failed to emit video booking socket event: {e}")

    return jsonify({"appointment_id": apt_id}), 201


# ================= USER APPOINTMENTS =================
@app.route("/user/appointments")
def user_appointments():
    username = require_auth()
    if not username:
        return jsonify({"error": "Unauthorized"}), 401

    uid = user_db.get_user_by_username(username)
    return jsonify({"appointments": appt_db.get_by_user(uid)}), 200


# ================= WORKER AUTH =================
@app.route("/worker/signup", methods=["POST"])
def worker_register():
    try:
        import os
        from werkzeug.utils import secure_filename
        
        UPLOAD_FOLDER = 'uploads/workers/'
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        def save_file(file, prefix):
            if file and file.filename:
                filename = secure_filename(file.filename)
                unique_filename = f"{prefix}_{filename}"
                path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(path)
                return path
            return None

        # Check if request is JSON or Form Data
        if request.is_json:
            d = request.json
            files = {}
        else:
            d = request.form
            files = request.files

        service_type = d.get("service", "healthcare").lower()
        
        # Handle specialization based on service type
        specialization = d.get("specialization", "")
        if service_type != "healthcare" and not specialization:
            specialization = "General"

        # Handle file uploads for all services (especially housekeeping and freelance)
        profile_photo_path = save_file(files.get('profile_photo'), 'photo')
        aadhaar_path = save_file(files.get('aadhaar_card'), 'aadhaar')
        police_verification_path = save_file(files.get('police_verification'), 'police')
        portfolio_path = save_file(files.get('portfolio'), 'portfolio')
        skill_certificate_path = save_file(files.get('skill_certificate'), 'skill')

        wid = worker_db.register_worker(
            full_name=d["full_name"], 
            email=d["email"], 
            phone=d["phone"],
            service=service_type, 
            specialization=specialization,
            experience=d.get("experience", ""), 
            clinic_location=d.get("clinic_location", ""),
            license_number=d.get("license_number"), 
            password=d.get("password", ""),
            aadhaar=d.get("aadhaar"),
            skills=d.get("skills", ""),
            hourly_rate=d.get("hourly_rate", None),
            bio=d.get("bio", ""),
            profile_photo_path=profile_photo_path,
            aadhaar_path=aadhaar_path,
            police_verification_path=police_verification_path,
            portfolio_path=portfolio_path,
            skill_certificate_path=skill_certificate_path
        )
        
        if wid is None:
            return jsonify({"error": "Worker already exists for this service"}), 400
        return jsonify({"worker_id": wid}), 201
    except Exception as e:
        print(f"Worker signup error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/worker/healthcare/signup", methods=["POST"])
def worker_signup():
    import os
    from werkzeug.utils import secure_filename
    
    UPLOAD_FOLDER = 'uploads/healthcare/'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    def save_file(file, prefix):
        if file and file.filename:
            filename = secure_filename(file.filename)
            unique_filename = f"{prefix}_{filename}"
            path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(path)
            return path
        return None
    
    # Handle form data
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    specialization = request.form.get('specialization')
    experience = request.form.get('experience')
    clinic_location = request.form.get('clinic_location', '')
    license_number = request.form.get('license_number')
    password = request.form.get('password')
    
    # Handle file uploads
    profile_photo_path = save_file(request.files.get('profile_photo'), 'photo')
    aadhaar_path = save_file(request.files.get('aadhaar'), 'aadhaar')
    degree_path = save_file(request.files.get('degree_certificate'), 'degree')
    license_path = save_file(request.files.get('medical_license'), 'license')
    
    wid = worker_db.register_worker(
        full_name,
        email,
        phone,
        "healthcare",
        specialization,
        experience,
        clinic_location,
        license_number,
        password,
        None,
        None,
        None,
        None,
        None,
        profile_photo_path,
        aadhaar_path,
        degree_path,
        license_path
    )
    
    if wid is None:
        return jsonify({"error": "Worker already exists"}), 400
    
    # Get worker data for socket notification
    worker_data = {
        'id': wid,
        'full_name': full_name,
        'email': email,
        'specialization': specialization,
        'status': 'pending'
    }
    
    # Send socket notification to admin
    try:
        from healthcareSocket import notify_new_worker_registration
        notify_new_worker_registration(worker_data)
    except ImportError:
        print("Socket not available for notification")
    
    return jsonify({"worker_id": wid, "status": "pending", "message": "Registration submitted. Waiting for admin approval."}), 201


@app.route('/admin/healthcare/workers/pending', methods=['GET'])
def get_pending_healthcare_workers():
    """Get all pending healthcare workers for admin approval"""
    try:
        conn = worker_db.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT id, full_name, email, phone, specialization, experience, 
                   clinic_location, license_number, status, created_at,
                   profile_photo_path, aadhaar_number, degree_certificate_path, medical_license_path
            FROM workers 
            WHERE service = 'healthcare' AND status = 'pending'
            ORDER BY created_at DESC
        """)
        
        workers = cursor.fetchall()
        
        # Convert file paths to URLs
        for worker in workers:
            worker['profile_photo_url'] = f"/uploads/{worker['profile_photo_path'].split('/')[-1]}" if worker.get('profile_photo_path') else None
            worker['aadhaar_url'] = f"/uploads/{worker['aadhaar_number'].split('/')[-1]}" if worker.get('aadhaar_number') else None
            worker['degree_certificate_url'] = f"/uploads/{worker['degree_certificate_path'].split('/')[-1]}" if worker.get('degree_certificate_path') else None
            worker['medical_license_url'] = f"/uploads/{worker['medical_license_path'].split('/')[-1]}" if worker.get('medical_license_path') else None
        
        cursor.close()
        conn.close()
        
        return jsonify({"workers": workers}), 200
        
    except Exception as e:
        print(f"Error fetching pending healthcare workers: {e}")
        return jsonify({"error": "Failed to fetch pending workers"}), 500

@app.route('/admin/healthcare/workers/approved', methods=['GET'])
def get_approved_healthcare_workers():
    """Get all approved healthcare workers"""
    try:
        conn = worker_db.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT id, full_name, email, phone, specialization, experience, 
                   clinic_location, license_number, status, created_at
            FROM workers 
            WHERE service = 'healthcare' AND status = 'approved'
            ORDER BY created_at DESC
        """)
        
        workers = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({"workers": workers}), 200
        
    except Exception as e:
        print(f"Error fetching approved healthcare workers: {e}")
        return jsonify({"error": "Failed to fetch approved workers"}), 500

@app.route('/admin/healthcare/workers/approve/<int:worker_id>', methods=['POST'])
def approve_healthcare_worker(worker_id):
    """Approve a healthcare worker"""
    try:
        conn = worker_db.get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE workers 
            SET status = 'approved' 
            WHERE id = %s AND service = 'healthcare'
        """, (worker_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "Worker not found"}), 404
        
        conn.commit()
        
        # Get worker details for notification
        cursor.execute("""
            SELECT full_name, email 
            FROM workers 
            WHERE id = %s
        """, (worker_id,))
        
        worker = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Send socket notification
        try:
            from healthcareSocket import notify_worker_approval
            notify_worker_approval(worker_id, worker[0], 'approved')
        except ImportError:
            print("Socket not available for notification")
        
        return jsonify({"message": f"Worker {worker[0]} approved successfully"}), 200
        
    except Exception as e:
        print(f"Error approving healthcare worker: {e}")
        return jsonify({"error": "Failed to approve worker"}), 500

@app.route('/admin/healthcare/workers/reject/<int:worker_id>', methods=['POST'])
def reject_healthcare_worker(worker_id):
    """Reject a healthcare worker"""
    try:
        conn = worker_db.get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE workers 
            SET status = 'rejected' 
            WHERE id = %s AND service = 'healthcare'
        """, (worker_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "Worker not found"}), 404
        
        conn.commit()
        
        # Get worker details for notification
        cursor.execute("""
            SELECT full_name, email 
            FROM workers 
            WHERE id = %s
        """, (worker_id,))
        
        worker = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Send socket notification
        try:
            from healthcareSocket import notify_worker_approval
            notify_worker_approval(worker_id, worker[0], 'rejected')
        except ImportError:
            print("Socket not available for notification")
        
        return jsonify({"message": f"Worker {worker[0]} rejected successfully"}), 200
        
    except Exception as e:
        print(f"Error rejecting healthcare worker: {e}")
        return jsonify({"error": "Failed to reject worker"}), 500

@app.route('/worker/healthcare/login', methods=['POST'])
def healthcare_worker_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Use the same verification method as general worker login
    w = worker_db.verify_worker_login(email, password)
    if not w:
        return jsonify({'error': 'Worker not found'}), 404
    
    wid, status, svc, spec, name = w
    
    # Check if worker is approved
    if status != 'approved':
        return jsonify({'error': 'Worker not approved yet. Please wait for admin approval.'}), 403
    
    token = generate_token(email)
    return jsonify({
        'worker_id': wid,
        'doctor_id': wid,  # For healthcare workers, doctor_id = worker_id
        'service': svc,
        'specialization': spec,
        'name': name,
        'token': token,
        'status': status
    })


@app.route("/debug/workers", methods=["GET"])
def debug_workers():
    """Debug endpoint to see all workers in database"""
    try:
        workers = worker_db.get_workers_by_service('housekeeping')
        
        result = []
        for w in workers:
            result.append({
                'email': w['email'],
                'service': w['service'], 
                'specialization': w['specialization'],
                'status': w['status'],
                'has_password': w.get('password') is not None
            })
        
        return jsonify({"workers": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/worker/login", methods=["POST"])
def worker_login():
    email = request.json["email"]
    password = request.json.get("password")
    
    print(f"Login attempt: email={email}, password={'provided' if password else 'not provided'}")
    
    w = worker_db.verify_worker_login(email, password)
    if not w:
        return jsonify({"error": "Invalid email or password"}), 404

    wid, status, svc, spec, name = w
    
    # Check if worker is approved (all services require approval)
    if status != "approved":
        return jsonify({"error": "Worker not approved yet. Please wait for admin approval."}), 403

    # Generate token for worker
    token = generate_token(email)

    return jsonify({
        "token": token,
        "worker_id": wid,
        "service": svc,
        "specialization": spec,
        "name": name
    }), 200


@app.route("/worker/<int:worker_id>", methods=["GET"])
def get_worker_details(worker_id):
    worker = worker_db.get_worker_by_id(worker_id)
    if not worker:
        return jsonify({"error": "Worker not found"}), 404
    
    # Remove sensitive info
    worker.pop("password", None)
    return jsonify({"worker": worker}), 200


@app.route("/worker/<int:worker_id>/requests", methods=["GET"])
def worker_requests(worker_id):
    requests = appt_db.get_pending_for_worker(worker_id)
    return jsonify({"requests": requests}), 200


@app.route("/worker/<int:worker_id>/appointments", methods=["GET"])
def worker_appointments(worker_id):
    requests = appt_db.get_by_worker(worker_id)
    return jsonify({"appointments": requests}), 200


@app.route("/worker/<int:worker_id>/history", methods=["GET"])
def worker_history(worker_id):
    """Get completed consultation history for a worker"""
    history = appt_db.get_history(worker_id)
    return jsonify({"history": history}), 200


@app.route("/worker/<int:worker_id>/dashboard/stats", methods=["GET"])
def worker_dashboard_stats(worker_id):
    """Get dashboard statistics for a worker"""
    stats = appt_db.get_dashboard_stats(worker_id)
    return jsonify(stats), 200


@app.route("/worker/<int:worker_id>/status", methods=["GET", "POST"])
def worker_status(worker_id):
    """Get or update worker status"""
    if request.method == "GET":
        status = worker_db.get_worker_status(worker_id)
        return jsonify({"status": status or "offline"}), 200
    
    elif request.method == "POST":
        data = request.get_json() or {}
        new_status = data.get("status", "offline")
        if worker_db.update_worker_status(worker_id, new_status):
            return jsonify({
                "success": True,
                "status": new_status
            }), 200
        else:
            return jsonify({"success": False, "error": "Failed to update status"}), 500


# ================= ACCEPT / REJECT =================
@app.route("/worker/respond", methods=["POST"])
def respond():
    d = request.json
    appointment_id = d["appointment_id"]
    status = d["status"]

    print(f"  Doctor responding to appointment {appointment_id} with status: {status}")

    appointment = appt_db.get_by_id(appointment_id)
    if not appointment:
        print(f"  Appointment {appointment_id} not found")
        return jsonify({"error": "Appointment not found"}), 404

    # ===== SUBSCRIPTION VALIDATION =====
    if status == "accepted":
        worker_id = appointment["worker_id"]
        
        # Check subscription eligibility before accepting appointment
        # eligibility = subscription_service.check_worker_eligibility(worker_id)
        eligibility = {'valid': True}  # Subscription service disabled
        
        if not eligibility['valid']:
            print(f"  Subscription check failed for worker {worker_id}: {eligibility['error']}")
            return jsonify({
                "error": eligibility['error'],
                "subscription_required": True
            }), 402
        
        # Track usage for accepted appointment
        # subscription_service.track_appointment_acceptance(worker_id)
        print(f"  Usage tracked for worker {worker_id}")

    # Update appointment status
    appt_db.respond(appointment_id, status)
    print(f"  Appointment {appointment_id} status updated to {status}")

    # Emit socket event to user
    try:
        emit_appointment_update(socketio, appointment_id, status, user_id=appointment["user_id"])
    except Exception as e:
        print(f"   Failed to emit appointment update socket event: {e}")

    # ===== PAYMENT REQUIRED FLOW =====
    if status == "accepted":
        # Get doctor consultation fee
        doctor_fee = worker_db.get_worker_consultation_fee(appointment["worker_id"])
        
        # Update appointment with payment pending status
        appt_db.set_payment_pending(appointment_id, payment_amount=int(doctor_fee))
        
        print(f"  Payment required for appointment {appointment_id}")
        print(f"   Doctor fee:  {doctor_fee}")
        
        # ===== VIDEO CONSULTATION ACCEPTED FLOW =====
        if appointment["appointment_type"] == "video":
            print(f"  Processing video consultation acceptance for appointment {appointment_id}")

            # Don't generate meeting details yet - wait for payment
            print(f"  Video consultation accepted - payment pending:")
            print(f"   Patient: {appointment['user_name']}")
            print(f"   Payment required before consultation")

            return jsonify({
                "success": True,
                "appointment_id": appointment_id,
                "status": "accepted",
                "payment_required": True,
                "doctor_fee": doctor_fee,
                "message": "Appointment accepted. Payment required to proceed."
            }), 200
        
        # For clinic appointments
        return jsonify({
            "success": True,
            "appointment_id": appointment_id,
            "status": "accepted", 
            "payment_required": True,
            "doctor_fee": doctor_fee,
            "message": "Appointment accepted. Payment required to confirm booking."
        }), 200

    print(f"  Response recorded for appointment {appointment_id}")
    return jsonify({"msg": "Response recorded"}), 200


# ================= VIDEO START (DOCTOR) =================
@app.route("/appointment/video/start", methods=["POST"])
def start_video():
    d = request.json
    appointment_id = d["appointment_id"]
    otp = d["otp"]
    
    print(f"  Doctor starting video call for appointment {appointment_id}")

    appointment = appt_db.get_by_id(appointment_id)
    if not appointment:
        print(f"  Appointment {appointment_id} not found")
        return jsonify({"error": "Not found"}), 404

    # Check payment status before allowing video consultation
    if appointment.get("payment_status") != "paid":
        print(f"  Payment not completed for appointment {appointment_id}")
        return jsonify({"error": "Payment required before starting consultation"}), 402

    if not appt_db.verify_otp(appointment_id, otp):
        print(f"  Invalid OTP for appointment {appointment_id}")
        return jsonify({"error": "Invalid OTP"}), 403

    appt_db.respond(appointment_id, "in_consultation")
    print(f"  Video consultation started for appointment {appointment_id}")
    
    return jsonify({"msg": "Video consultation started"}), 200


# ================= VIDEO JOIN (USER) =================
@app.route("/appointment/<int:appointment_id>/video-link")
def video_link(appointment_id):
    appointment = appt_db.get_by_id(appointment_id)
    if not appointment:
        return jsonify({"error": "Not found"}), 404

    if appointment["appointment_type"] != "video":
        return jsonify({"error": "Not video"}), 400

    # Check payment status before allowing video consultation
    if appointment.get("payment_status") != "paid":
        return jsonify({"error": "Payment required before joining consultation"}), 402

    if appointment["status"] != "in_consultation":
        return jsonify({"error": "Not started"}), 403

    # Return the video call URL
    video_url = f"http://127.0.0.1:5001/video-call/{appointment_id}?role=user"
    return jsonify({"video_link": video_url}), 200

@app.route("/appointment/<int:appointment_id>", methods=["GET"])
def get_appointment_detail(appointment_id):
    """Get detailed appointment information"""
    # Get sender role from query parameter
    sender_role = request.args.get("sender_role", "user")
    
    # Require authentication based on sender role
    if sender_role == "user":
        username = require_auth()
        if not username:
            return jsonify({"error": "Authentication required"}), 401
    elif sender_role == "worker":
        worker_email = require_worker_auth()
        if not worker_email:
            return jsonify({"error": "Worker authentication required"}), 401
    
    # Get appointment details
    appointment = appt_db.get_by_id(appointment_id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404
    
    # Add payment information
    appointment_data = dict(appointment)
    
    # Get payment status if available
    # payment_info = payment_service.get_appointment_payment_status(appointment_id)
    payment_info = None  # Payment service disabled
    if payment_info:
        appointment_data.update(payment_info)
    
    return jsonify(appointment_data), 200



# ================= VIDEO END =================
@app.route("/appointment/video/end", methods=["POST"])
def end_video():
    appointment_id = request.json["appointment_id"]
    appt_db.respond(appointment_id, "completed")
    event_db.log_event(appointment_id, "consultation_completed")
    return jsonify({"msg": "Consultation completed"}), 200



@app.route("/video/start", methods=["POST"])
def start_video_call():
    data = request.json
    appointment_id = data["appointment_id"]
    otp = data["otp"]

    ok = appt_db.start_video_session(appointment_id, otp)

    if not ok:
        return jsonify({"error": "Invalid OTP"}), 400

    info = appt_db.get_email_details(appointment_id)

    return jsonify({
        "msg": "Call started",
        "meeting_link": info["meeting_link"]
    })

@app.route("/worker/video_appointments")
def worker_video_appointments():
    conn = appt_db.get_conn()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        SELECT id, user_name, status
        FROM appointments
        WHERE appointment_type='video' AND status='accepted'
        ORDER BY id DESC
    """)

    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify(rows)

# ================= AI CARE - TRUE AI-DRIVEN SYSTEM =================
from services.healthcare.ai_engine import analyze_symptoms_conversational

@app.route("/healthcare/ai-care", methods=["POST"])
def ai_care():
    """True AI-driven healthcare analysis using Gemini"""
    try:
        data = request.json
        message = data.get("message", "")
        conversation_history = data.get("conversation_history", [])
        user_id = data.get("user_id", "default")
        
        if not message.strip():
            return jsonify({
                "success": False,
                "message": "Message is required"
            }), 400
        
        # Analyze with true AI (Gemini-powered)
        ai_result = analyze_symptoms_conversational(message, user_id, conversation_history)
        
        if ai_result.get("stage") == "final":
            # Get specializations from AI result
            specializations = ai_result.get("specializations", ["General Physician"])
            
            # For now, use mock doctors to avoid database issues
            suggested_doctors = []
            if 'Neurologist' in specializations:
                suggested_doctors.append({
                    'id': 1,
                    'name': 'Dr. Test Neurologist',
                    'specialization': 'Neurologist',
                    'experience': 10,
                    'rating': 4.8,
                    'clinic_location': 'Test Hospital'
                })
            if 'General Physician' in specializations:
                suggested_doctors.append({
                    'id': 2,
                    'name': 'Dr. Test Physician',
                    'specialization': 'General Physician',
                    'experience': 8,
                    'rating': 4.5,
                    'clinic_location': 'Test Clinic'
                })
            
            return jsonify({
                "success": True,
                "response": ai_result.get("advice", ""),
                "stage": ai_result.get("stage", "final"),
                "severity": ai_result.get("severity", "medium"),
                "first_aid": ai_result.get("first_aid", ""),
                "otc_medicines": ai_result.get("otc_medicines", ""),
                "suggested_doctors": suggested_doctors,
                "specializations": specializations,
                "reasoning": ai_result.get("reasoning", ""),
                "follow_up": ai_result.get("follow_up", ""),
                "detected_language": ai_result.get("detected_language", "english")
            }), 200
        else:
            # Triage stage - return AI question
            return jsonify({
                "success": True,
                "response": ai_result.get("advice", ""),
                "stage": ai_result.get("stage", "triage"),
                "question": ai_result.get("question", ""),
                "suggested_doctors": [],
                "specializations": [],
                "detected_language": ai_result.get("detected_language", "english")
            }), 200
            
    except Exception as e:
        print(f"AI Care error: {e}")
        return jsonify({
            "success": False,
            "message": f"AI analysis failed: {str(e)}"
        }), 500

# ================= AI MECHANIC - CAR DIAGNOSTIC AI =================
@app.route("/api/ai/mechanic-diagnosis", methods=["POST"])
def ai_mechanic_diagnosis():
    data = request.json
    symptoms = data.get("symptoms", "")
    user_id = data.get("user_id", "default")
    service_type = data.get("service_type", "mechanic")

    if not symptoms:
        return jsonify({"error": "Symptoms required"}), 400

    try:
        # AI Mechanic response logic
        symptoms_lower = symptoms.lower()
        
        # Emergency car situations
        emergency_keywords = ["car won't start", "engine smoking", "brake failure", "flat tire", "overheating", "won't start", "no brakes"]
        for keyword in emergency_keywords:
            if keyword in symptoms_lower:
                return jsonify({
                    "success": True,
                    "diagnosis": f"  CAR EMERGENCY DETECTED!\n\n{keyword.title()} detected. This requires immediate attention:\n\n  Pull over safely if driving\n  Turn on hazard lights\n  Do not continue driving\n  Call roadside assistance immediately\n  Your safety is the top priority\n\nThis could be a serious mechanical issue that needs professional help right away.",
                    "severity": "emergency",
                    "recommendations": ["Stop driving immediately", "Call roadside assistance", "Do not attempt repairs yourself"]
                })

        # Common car issues and their solutions
        if "check engine" in symptoms_lower:
            response = """  CHECK ENGINE LIGHT ANALYSIS:\n\nThe check engine light can indicate various issues:\n\n  Loose gas cap (most common) - tighten and see if light goes off\n  Oxygen sensor issue - affects fuel efficiency\n  Catalytic converter problem - reduces performance\n  Spark plug issues - causes rough running\n  Mass airflow sensor - affects engine performance\n\n  What to do:\n1. Check if gas cap is tight\n2. Note any unusual sounds or performance\n3. Avoid hard acceleration\n4. Visit mechanic within 1-2 days if light stays on\n5. If flashing, stop driving immediately"""

        elif "noise" in symptoms_lower or "sound" in symptoms_lower:
            if "squealing" in symptoms_lower:
                response = """  SQUEALING NOISE DIAGNOSIS:\n\nSquealing usually indicates:\n\n  Worn brake pads - needs immediate attention\n  Loose or worn serpentine belt\n  Bad wheel bearing\n  Low brake fluid\n\n   Safety: Brake issues are critical - get checked immediately"""
            elif "clicking" in symptoms_lower:
                response = """  CLICKING NOISE DIAGNOSIS:\n\nClicking sounds typically indicate:\n\n  Low engine oil (critical)\n  Valve train issues\n  CV joint problems (when turning)\n  Bad spark plugs\n\n  Check oil level immediately if clicking from engine area"""
            else:
                response = """  GENERAL NOISE DIAGNOSIS:\n\nUnusual noises need attention:\n\n  Note when the noise occurs (acceleration, braking, turning)\n  Note the type of noise (squeak, grind, knock, click)\n  Check if noise changes with speed\n  Visit mechanic for proper diagnosis"""

        elif "battery" in symptoms_lower or "won't start" in symptoms_lower:
            response = """  BATTERY/STARTING ISSUES:\n\nCommon causes:\n\n  Dead battery - most common issue\n  Corroded battery terminals\n  Bad alternator (battery won't charge)\n  Starter motor failure\n  Bad ignition switch\n\n  Quick checks:\n1. Check if lights work (battery power)\n2. Listen for clicking sound (starter)\n3. Try jump start\n4. Check battery terminals for corrosion\n\n  If jump start works, likely battery or alternator issue"""

        elif "overheating" in symptoms_lower or "hot" in symptoms_lower:
            response = """   OVERHEATING DIAGNOSIS:\n\nSerious issue - stop driving if overheating:\n\n  Low coolant level - most common\n  Bad thermostat\n  Water pump failure\n  Radiator leak\n  Broken fan belt\n\n  IMMEDIATE ACTIONS:\n1. Pull over safely\n2. Turn off A/C, turn on heat to high\n3. Do not open radiator cap when hot!\n4. Let engine cool before checking coolant\n5. Call for assistance if temperature is high"""

        elif "brake" in symptoms_lower:
            response = """  BRAKE SYSTEM DIAGNOSIS:\n\nBrake issues are safety critical:\n\n  Squealing = worn brake pads\n  Grinding = metal-on-metal (urgent)\n  Soft pedal = brake fluid leak or air in lines\n  Pulling to one side = caliper issue\n  Vibration = warped rotors\n\n   Do not drive with brake problems!\nGet immediate professional attention."""

        elif "oil" in symptoms_lower:
            response = """   OIL ISSUES:\n\nOil is critical for engine health:\n\n  Low oil level - check and add oil immediately\n  Oil leak - look under car for puddles\n  Oil pressure light - stop engine immediately\n  Oil change overdue - schedule service\n\n  Maintenance:\n  Check oil level monthly\n  Change oil every 3,000-5,000 miles\n  Use correct oil type for your vehicle"""

        elif "tire" in symptoms_lower:
            response = """  TIRE ISSUES:\n\nTire problems affect safety and fuel economy:\n\n  Flat tire - use spare or call assistance\n  Low pressure - inflate to recommended PSI\n  Vibration at high speed - balance needed\n  Pulling to one side - alignment or tire pressure\n  Uneven wear - alignment or rotation needed\n\n  Quick checks:\n1. Check tire pressure monthly\n2. Rotate tires every 6,000-8,000 miles\n3. Replace tires when tread is worn"""

        else:
            response = """  GENERAL CAR DIAGNOSIS:\n\nI'll help you diagnose your car issue. Please provide more details:\n\n  What specific problem are you experiencing?\n  When does it occur? (starting, driving, braking, etc.)\n  Any warning lights on dashboard?\n  Any unusual sounds or smells?\n  Did this start suddenly or gradually?\n\n  Tips for better diagnosis:\n  Be specific about symptoms\n  Note when the problem occurs\n  Mention any recent repairs or maintenance\n  Describe any sounds (squeal, grind, knock, etc.)"""

        return jsonify({
            "success": True,
            "diagnosis": response,
            "severity": "moderate",
            "recommendations": ["Monitor the issue", "Schedule maintenance if needed", "Stop driving if symptoms worsen"]
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"AI diagnosis failed: {str(e)}",
            "diagnosis": "I apologize, but I'm having trouble processing your request. Please try again or describe your issue in more detail."
        }), 500


@app.route("/worker/freelance/signup", methods=["POST"])
def freelance_signup():
    d = request.json
    skill_ids = d.get("skill_ids", [])
    
    print(f"Freelance signup request: {d}")
    
    if not skill_ids:
        return jsonify({"error": "At least one skill must be selected"}), 400

    try:
        worker_id = worker_db.register_worker(
            full_name=d["full_name"],
            email=d["email"],
            phone=d["phone"],
            service="freelance",
            specialization=d.get("skills", ""),
            experience=0,
            clinic_location="",
            password=None,
            aadhaar=d.get("aadhaar"),
            id_proof=d.get("id_proof"),
            skills=d.get("skills"),
            hourly_rate=d.get("hourly_rate"),
            bio=d.get("bio")
        )
        print(f"Worker registration result: {worker_id}")
        
        if not worker_id:
            return jsonify({"error": "Freelancer exists"}), 400
    except Exception as e:
        print(f"Freelance registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500
        
    # Phase 1: Store skills in junction table
    from services.freelance.services.freelance_service import freelance_service
    freelance_service.update_provider_skills(worker_id, skill_ids)
    
    return jsonify({"worker_id": worker_id}), 201

# ================= ADMIN ROUTES =================
@app.route("/admin/workers/pending")
def admin_pending_workers():
    service = request.args.get('service')
    workers = worker_db.get_pending_workers(service)
    return jsonify(workers), 200

@app.route("/admin/workers/approved")
def admin_approved_workers():
    service = request.args.get('service')
    workers = worker_db.get_workers_by_service(service)
    return jsonify(workers), 200

@app.route("/admin/workers/all")
def admin_all_workers():
    """Get all workers regardless of status or service"""
    workers = worker_db.get_all_workers_unfiltered()
    return jsonify(workers), 200

@app.route("/admin/worker/approve/<int:worker_id>", methods=["POST"])
def admin_approve_worker(worker_id):
    worker_db.approve_worker(worker_id)
    
    # Assign free trial to approved worker
    try:
        # trial_result = subscription_service.assign_free_trial_to_worker(worker_id)
        trial_result = {'success': True, 'message': 'Free trial assigned (subscription service disabled)'}
        if trial_result['success']:
            print(f"  Free trial assigned to worker {worker_id}")
        else:
            print(f"   Failed to assign free trial to worker {worker_id}: {trial_result['message']}")
    except Exception as e:
        print(f"  Error assigning free trial: {e}")
    
    return jsonify({"msg": "Worker approved"}), 200

@app.route("/admin/worker/reject/<int:worker_id>", methods=["POST"])
def admin_reject_worker(worker_id):
    worker_db.reject_worker(worker_id)
    return jsonify({"msg": "Worker rejected"}), 200

# ================= TEST PAGES =================
@app.route("/test-payment")
def test_payment_page():
    """Test payment integration page"""
    from flask import send_from_directory
    return send_from_directory('.', 'payment_test.html')

@app.route("/test-doctor-profile")
def test_doctor_profile_page():
    """Test doctor profile management page"""
    from flask import send_from_directory
    return send_from_directory('.', 'doctor_profile_test.html')

# ================= PAYMENT ENDPOINTS =================
@app.route("/api/payment/create-order", methods=["POST"])
def create_payment_order():
    """Create Razorpay order for appointment payment"""
    data = request.json
    appointment_id = data["appointment_id"]
    
    # Get appointment details
    appointment = appt_db.get_by_id(appointment_id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404
    
    # Check if payment is already processed
    if appointment.get("payment_status") == "paid":
        return jsonify({"error": "Payment already completed"}), 400
    
    # Get doctor consultation fee
    doctor_fee = worker_db.get_worker_consultation_fee(appointment["worker_id"])
    
    # Create payment order
    try:
        # order_result = payment_service.create_payment_order(appointment_id, doctor_fee)
        order_result = {
            "amount": doctor_fee * 100,  # Convert to paise/cents
            "currency": "INR",
            "id": f"order_{appointment_id}_{int(time.time())}"
        }
        
        print(f"  Payment order created for appointment {appointment_id}")
        print(f"   Doctor fee:  {doctor_fee}")
        print(f"   Total amount:  {order_result['amount']}")
        
        return jsonify(order_result), 200
        
    except Exception as e:
        print(f"  Payment order creation failed: {e}")
        return jsonify({"error": "Failed to create payment order"}), 500

@app.route("/api/payment/confirm", methods=["POST"])
def confirm_payment():
    """Confirm payment and update appointment status"""
    data = request.json
    appointment_id = data["appointment_id"]
    razorpay_payment_id = data["razorpay_payment_id"]
    
    # Verify payment with Razorpay (additional security)
    # if not payment_service.verify_payment_with_razorpay(razorpay_payment_id):
    #     return jsonify({"error": "Payment verification failed"}), 400
    
    # Confirm payment in database
    # success = payment_service.confirm_payment(appointment_id, razorpay_payment_id)
    success = True  # Payment service disabled - auto-confirm for testing
    
    if success:
        # Get appointment details for video consultation setup
        appointment = appt_db.get_by_id(appointment_id)
        
        # Emit socket event to doctor and user about payment confirmation
        try:
            emit_appointment_update(socketio, appointment_id, 'confirmed', 
                                    worker_id=appointment["worker_id"], 
                                    user_id=appointment["user_id"])
        except Exception as e:
            print(f"   Failed to emit payment confirmation socket event: {e}")

        # If it's a video consultation, generate meeting details now
        if appointment["appointment_type"] == "video":
            meeting_link, otp, video_room = appt_db.set_video_details(appointment_id)
            
            print(f"  Video consultation details generated after payment:")
            print(f"   Meeting: {meeting_link}")
            print(f"   OTP: {otp}")
            
            return jsonify({
                "success": True,
                "message": "Payment confirmed. Appointment confirmed.",
                "appointment_status": "confirmed",
                "video_details": {
                    "meeting_link": meeting_link,
                    "otp": otp,
                    "doctor_url": f"http://127.0.0.1:5001/video-call/{appointment_id}?role=doctor",
                    "patient_url": f"http://127.0.0.1:5001/video-call/{appointment_id}?role=user"
                }
            }), 200
        
        # For clinic appointments
        return jsonify({
            "success": True,
            "message": "Payment confirmed. Appointment confirmed.",
            "appointment_status": "confirmed"
        }), 200
    else:
        return jsonify({"error": "Payment confirmation failed"}), 400

@app.route("/api/payment/status/<int:appointment_id>", methods=["GET"])
def get_payment_status(appointment_id):
    """Get payment status for an appointment"""
    # payment_info = payment_service.get_appointment_payment_status(appointment_id)
    payment_info = None  # Payment service disabled
    
    if payment_info:
        return jsonify(payment_info), 200
    else:
        return jsonify({"error": "Appointment not found"}), 404

# ================= DOCTOR PROFILE MANAGEMENT =================
@app.route("/api/doctor/update-fee", methods=["PUT"])
def update_consultation_fee():
    """Update doctor consultation fee - Doctor authentication required"""
    # Get doctor token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Authorization token required"}), 401
    
    token = auth_header.split(" ")[1]
    doctor_email = verify_token(token)
    
    if not doctor_email:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    # Get doctor ID from email
    worker = worker_db.get_worker_by_email(doctor_email)
    if not worker:
        return jsonify({"error": "Doctor not found"}), 404
    
    worker_id = worker['id']
    data = request.json
    consultation_fee = data.get("consultation_fee")
    
    # Validate consultation fee
    if not consultation_fee or not isinstance(consultation_fee, (int, float)) or consultation_fee < 0:
        return jsonify({"error": "Valid consultation fee required"}), 400
    
    # Update consultation fee
    success = worker_db.update_consultation_fee(worker_id, int(consultation_fee))
    
    if success:
        print(f"  Doctor {worker_id} updated consultation fee to  {consultation_fee}")
        return jsonify({
            "success": True,
            "message": "Consultation fee updated successfully",
            "consultation_fee": int(consultation_fee)
        }), 200
    else:
        return jsonify({"error": "Failed to update consultation fee"}), 500

@app.route("/api/doctor/profile", methods=["GET"])
def get_doctor_profile():
    """Get doctor profile including consultation fee - Doctor authentication required"""
    # Get doctor token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Authorization token required"}), 401
    
    token = auth_header.split(" ")[1]
    doctor_email = verify_token(token)
    
    if not doctor_email:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    # Get doctor ID from email
    worker = worker_db.get_worker_by_email(doctor_email)
    if not worker:
        return jsonify({"error": "Doctor not found"}), 404
    
    worker_id = worker['id']
    
    # Get doctor profile
    profile = worker_db.get_worker_profile(worker_id)
    
    if profile:
        return jsonify(profile), 200
    else:
        return jsonify({"error": "Profile not found"}), 404


# ================= EXPERT SYSTEM =================
@app.route("/expert/categories")
def get_expert_categories():
    """Get all available expert categories"""
    try:
        categories = expert_db.get_expert_categories()
        return jsonify({"categories": categories}), 200
    except Exception as e:
        print(f"  Error fetching expert categories: {e}")
        return jsonify({"error": "Failed to fetch categories", "categories": []}), 500


@app.route("/expert/online")
def get_online_experts():
    """Get all online experts, optionally filtered by category"""
    try:
        category = request.args.get("category")
        experts = expert_db.get_online_experts(category)
        return jsonify({"experts": experts}), 200
    except Exception as e:
        print(f"  Error fetching online experts: {e}")
        return jsonify({"error": "Failed to fetch experts", "experts": []}), 500


@app.route("/expert/all")
def get_all_experts():
    """Get all experts, optionally filtered by category"""
    try:
        category = request.args.get("category")
        experts = expert_db.get_all_experts(category)
        return jsonify({"experts": experts}), 200
    except Exception as e:
        print(f"  Error fetching all experts: {e}")
        return jsonify({"error": "Failed to fetch experts", "experts": []}), 500


@app.route("/expert/search")
def search_experts():
    """Search experts by query, optionally filtered by category"""
    try:
        query = request.args.get("q", "")
        category = request.args.get("category")
        if not query.strip():
            return jsonify({"error": "Search query is required"}), 400
        
        experts = expert_db.search_experts(query, category)
        return jsonify({"experts": experts}), 200
    except Exception as e:
        print(f"  Error searching experts: {e}")
        return jsonify({"error": "Failed to search experts", "experts": []}), 500


@app.route("/expert/request", methods=["POST"])
def create_expert_request():
    """Create a new expert request"""
    try:
        user = require_auth()
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        
        data = request.json
        required_fields = ["expert_id", "category", "title"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {missing_fields}"}), 400
        
        request_id = expert_db.create_expert_request(
            user_id=user["user_id"],
            expert_id=data["expert_id"],
            category=data["category"],
            title=data["title"],
            description=data.get("description", ""),
            image_url=data.get("image_url"),
            priority=data.get("priority", "normal")
        )
        
        if request_id:
            print(f"  Expert request created: {request_id}")
            return jsonify({
                "success": True,
                "request_id": request_id,
                "message": "Expert request created successfully"
            }), 201
        else:
            return jsonify({"error": "Failed to create expert request"}), 500
            
    except Exception as e:
        print(f"  Error creating expert request: {e}")
        return jsonify({"error": "Failed to create expert request"}), 500


@app.route("/expert/requests/<int:expert_id>")
def get_expert_requests(expert_id):
    """Get requests for a specific expert"""
    try:
        status = request.args.get("status")
        requests = expert_db.get_expert_requests(expert_id, status)
        return jsonify({"requests": requests}), 200
    except Exception as e:
        print(f"  Error fetching expert requests: {e}")
        return jsonify({"error": "Failed to fetch requests", "requests": []}), 500


@app.route("/expert/user/requests")
def get_user_expert_requests():
    """Get expert requests for the authenticated user"""
    try:
        user = require_auth()
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        
        status = request.args.get("status")
        requests = expert_db.get_user_requests(user["user_id"], status)
        return jsonify({"requests": requests}), 200
    except Exception as e:
        print(f"  Error fetching user expert requests: {e}")
        return jsonify({"error": "Failed to fetch requests", "requests": []}), 500


@app.route("/expert/request/<int:request_id>/status", methods=["PUT"])
def update_expert_request_status(request_id):
    """Update expert request status"""
    try:
        data = request.json
        status = data.get("status")
        
        if not status:
            return jsonify({"error": "Status is required"}), 400
        
        expert_db.update_request_status(request_id, status)
        print(f"  Expert request {request_id} status updated to: {status}")
        return jsonify({
            "success": True,
            "message": "Request status updated successfully"
        }), 200
        
    except Exception as e:
        print(f"  Error updating expert request status: {e}")
        return jsonify({"error": "Failed to update request status"}), 500


@app.route("/expert/session", methods=["POST"])
def create_expert_session():
    """Create a new expert session"""
    try:
        data = request.json
        required_fields = ["request_id", "expert_id", "user_id", "session_type"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {missing_fields}"}), 400
        
        meeting_link = None
        if data["session_type"] == "call":
            meeting_link = create_meeting_link()
        
        session_id = expert_db.create_session(
            request_id=data["request_id"],
            expert_id=data["expert_id"],
            user_id=data["user_id"],
            session_type=data["session_type"],
            meeting_link=meeting_link
        )
        
        if session_id:
            print(f"  Expert session created: {session_id}")
            return jsonify({
                "success": True,
                "session_id": session_id,
                "meeting_link": meeting_link,
                "message": "Session created successfully"
            }), 201
        else:
            return jsonify({"error": "Failed to create session"}), 500
            
    except Exception as e:
        print(f"  Error creating expert session: {e}")
        return jsonify({"error": "Failed to create session"}), 500


@app.route("/expert/sessions")
def get_expert_sessions():
    """Get active expert sessions"""
    try:
        expert_id = request.args.get("expert_id", type=int)
        user_id = request.args.get("user_id", type=int)
        
        sessions = expert_db.get_active_sessions(expert_id, user_id)
        return jsonify({"sessions": sessions}), 200
    except Exception as e:
        print(f"  Error fetching expert sessions: {e}")
        return jsonify({"error": "Failed to fetch sessions", "sessions": []}), 500


@app.route("/expert/session/<int:session_id>/end", methods=["PUT"])
def end_expert_session(session_id):
    """End an expert session"""
    try:
        expert_db.end_session(session_id)
        print(f"  Expert session {session_id} ended")
        return jsonify({
            "success": True,
            "message": "Session ended successfully"
        }), 200
        
    except Exception as e:
        print(f"  Error ending expert session: {e}")
        return jsonify({"error": "Failed to end session"}), 500


@app.route("/expert/status/<int:expert_id>", methods=["PUT"])
def update_expert_status(expert_id):
    """Update expert online/offline status"""
    try:
        data = request.json
        is_online = data.get("is_online", False)
        
        expert_db.update_expert_status(expert_id, bool(is_online))
        status = "online" if is_online else "offline"
        print(f"  Expert {expert_id} status updated to: {status}")
        return jsonify({
            "success": True,
            "message": f"Expert status updated to {status}"
        }), 200
        
    except Exception as e:
        print(f"  Error updating expert status: {e}")
        return jsonify({"error": "Failed to update expert status"}), 500


# ================= EXPERT CHAT SYSTEM =================
@app.route("/expert/chat/room", methods=["POST"])
def create_chat_room():
    """Create a new chat room for an expert session"""
    try:
        data = request.json
        required_fields = ["session_id", "expert_id", "user_id"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {missing_fields}"}), 400
        
        room_id = expert_chat_db.create_chat_room(
            session_id=data["session_id"],
            expert_id=data["expert_id"],
            user_id=data["user_id"],
            room_name=data.get("room_name")
        )
        
        if room_id:
            print(f"  Chat room created: {room_id}")
            return jsonify({
                "success": True,
                "room_id": room_id,
                "message": "Chat room created successfully"
            }), 201
        else:
            return jsonify({"error": "Failed to create chat room"}), 500
            
    except Exception as e:
        print(f"  Error creating chat room: {e}")
        return jsonify({"error": "Failed to create chat room"}), 500


@app.route("/expert/chat/room/<int:room_id>")
def get_chat_room(room_id):
    """Get chat room details"""
    try:
        room = expert_chat_db.get_chat_room(room_id)
        if room:
            return jsonify({"room": room}), 200
        else:
            return jsonify({"error": "Chat room not found"}), 404
    except Exception as e:
        print(f"  Error fetching chat room: {e}")
        return jsonify({"error": "Failed to fetch chat room"}), 500


@app.route("/expert/chat/rooms/user")
def get_user_chat_rooms():
    """Get all chat rooms for a user"""
    try:
        user = require_auth()
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        
        rooms = expert_chat_db.get_user_chat_rooms(user["user_id"])
        return jsonify({"rooms": rooms}), 200
    except Exception as e:
        print(f"  Error fetching user chat rooms: {e}")
        return jsonify({"error": "Failed to fetch chat rooms", "rooms": []}), 500


@app.route("/expert/chat/rooms/expert/<int:expert_id>")
def get_expert_chat_rooms(expert_id):
    """Get all chat rooms for an expert"""
    try:
        rooms = expert_chat_db.get_expert_chat_rooms(expert_id)
        return jsonify({"rooms": rooms}), 200
    except Exception as e:
        print(f"  Error fetching expert chat rooms: {e}")
        return jsonify({"error": "Failed to fetch chat rooms", "rooms": []}), 500


@app.route("/expert/chat/messages/<int:room_id>")
def get_chat_messages(room_id):
    """Get messages for a chat room"""
    try:
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)
        
        messages = expert_chat_db.get_room_messages(room_id, limit, offset)
        return jsonify({"messages": messages}), 200
    except Exception as e:
        print(f"  Error fetching chat messages: {e}")
        return jsonify({"error": "Failed to fetch messages", "messages": []}), 500


@app.route("/expert/chat/send", methods=["POST"])
def send_chat_message():
    """Send a message in a chat room"""
    try:
        data = request.json
        required_fields = ["room_id", "sender_id", "sender_type", "message"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {missing_fields}"}), 400
        
        message_id = expert_chat_db.send_message(
            room_id=data["room_id"],
            sender_id=data["sender_id"],
            sender_type=data["sender_type"],
            message=data["message"],
            message_type=data.get("message_type", "text"),
            file_url=data.get("file_url")
        )
        
        if message_id:
            print(f"  Message sent: {message_id}")
            return jsonify({
                "success": True,
                "message_id": message_id,
                "message": "Message sent successfully"
            }), 201
        else:
            return jsonify({"error": "Failed to send message"}), 500
            
    except Exception as e:
        print(f"  Error sending message: {e}")
        return jsonify({"error": "Failed to send message"}), 500


@app.route("/expert/chat/read/<int:room_id>", methods=["PUT"])
def mark_messages_read(room_id):
    """Mark messages as read for a participant"""
    try:
        data = request.json
        participant_id = data.get("participant_id")
        
        if not participant_id:
            return jsonify({"error": "Participant ID is required"}), 400
        
        expert_chat_db.mark_messages_read(room_id, participant_id)
        print(f"  Messages marked as read for room {room_id}")
        return jsonify({
            "success": True,
            "message": "Messages marked as read"
        }), 200
        
    except Exception as e:
        print(f"  Error marking messages as read: {e}")
        return jsonify({"error": "Failed to mark messages as read"}), 500


@app.route("/expert/chat/status/<int:room_id>", methods=["PUT"])
def update_participant_status(room_id):
    """Update participant online status in a chat room"""
    try:
        data = request.json
        participant_id = data.get("participant_id")
        is_online = data.get("is_online", False)
        
        if not participant_id:
            return jsonify({"error": "Participant ID is required"}), 400
        
        expert_chat_db.update_participant_status(room_id, participant_id, bool(is_online))
        status = "online" if is_online else "offline"
        print(f"  Participant {participant_id} status updated to {status} in room {room_id}")
        return jsonify({
            "success": True,
            "message": f"Participant status updated to {status}"
        }), 200
        
    except Exception as e:
        print(f"  Error updating participant status: {e}")
        return jsonify({"error": "Failed to update participant status"}), 500


@app.route("/expert/chat/close/<int:room_id>", methods=["PUT"])
def close_chat_room(room_id):
    """Close a chat room"""
    try:
        expert_chat_db.close_chat_room(room_id)
        print(f"  Chat room {room_id} closed")
        return jsonify({
            "success": True,
            "message": "Chat room closed successfully"
        }), 200
        
    except Exception as e:
        print(f"  Error closing chat room: {e}")
        return jsonify({"error": "Failed to close chat room"}), 500


@app.route("/expert/chat/search/<int:room_id>")
def search_chat_messages(room_id):
    """Search messages in a chat room"""
    try:
        query = request.args.get("q", "")
        if not query.strip():
            return jsonify({"error": "Search query is required"}), 400
        # TODO: Implement search functionality
        return jsonify({"messages": []}), 200
    except Exception as e:
        print(f"  Error searching chat messages: {e}")
        return jsonify({"error": "Failed to search messages", "messages": []}), 500


@app.route("/healthcare/doctors/<int:doctor_id>")
def get_doctor_details(doctor_id):
    """Get specific doctor details"""
    try:
        doctor = worker_db.get_worker_by_id(doctor_id)
        if doctor and doctor.get('service') == 'healthcare' and doctor.get('status') == 'approved':
            return jsonify({"doctor": doctor}), 200
        else:
            return jsonify({"error": "Doctor not found"}), 404
    except Exception as e:
        print(f"  Error fetching doctor details: {e}")
        return jsonify({"error": "Failed to fetch doctor details"}), 500


@app.route("/healthcare/appointments", methods=["POST"])
def create_appointment():
    """Create a new appointment"""
    try:
        data = request.json
        
        # Get user details for the appointment
        user_db = __import__('user_db').UserDB()
        user = user_db.get_user_by_id(data["patient_id"])
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        appointment_id = appt_db.book_clinic(
            user_id=data["patient_id"],
            worker_id=data["doctor_id"],
            user_name=user.get('name', 'Unknown User'),
            symptoms=data["reason"],
            date=data["date"],
            time_slot=data["time"]
        )
        
        if appointment_id and appointment_id[0]:
            return jsonify({"appointment_id": appointment_id[1], "message": "Appointment created successfully"}), 201
        else:
            return jsonify({"error": f"Failed to create appointment: {appointment_id[1] if appointment_id else 'Unknown error'}"}), 500
    except Exception as e:
        print(f"  Error creating appointment: {e}")
        return jsonify({"error": f"Failed to create appointment: {str(e)}"}), 500


@app.route("/healthcare/appointments", methods=["GET"])
def get_appointments():
    """Get appointments for a user"""
    try:
        patient_id = request.args.get("patient_id")
        doctor_id = request.args.get("doctor_id")
        
        if patient_id:
            appointments = appointment_db.get_patient_appointments(patient_id)
        elif doctor_id:
            appointments = appointment_db.get_doctor_appointments(doctor_id)
        else:
            appointments = appointment_db.get_all_appointments()
            
        return jsonify({"appointments": appointments}), 200
    except Exception as e:
        print(f"  Error fetching appointments: {e}")
        return jsonify({"error": "Failed to fetch appointments"}), 500


@app.route("/healthcare/availability/<int:doctor_id>")
def get_doctor_availability(doctor_id):
    """Get available time slots for a doctor on a specific date"""
    try:
        date = request.args.get("date")
        if not date:
            return jsonify({"error": "Date parameter is required"}), 400
        
        # Get availability for the doctor
        availability = appt_db.availability_db.get_availability(doctor_id, date)
        
        # Get existing appointments to filter out booked slots
        appointments = appt_db.get_by_worker(doctor_id)
        booked_slots = []
        for apt in appointments:
            if apt.get('booking_date') == date:
                booked_slots.append(apt.get('time_slot'))
        
        # Filter available slots (remove booked ones)
        available_slots = []
        if availability:
            for slot in availability:
                if slot['time_slot'] not in booked_slots:
                    available_slots.append(slot['time_slot'])
        
        return jsonify({"available_slots": available_slots}), 200
    except Exception as e:
        print(f"  Error fetching availability: {e}")
        return jsonify({"error": "Failed to fetch availability"}), 500


@app.route("/healthcare/availability/<int:doctor_id>", methods=["POST"])
def set_doctor_availability(doctor_id):
    """Set availability slots for a doctor"""
    try:
        data = request.json
        date = data.get("date")
        time_slots = data.get("time_slots", [])
        
        if not date or not time_slots:
            return jsonify({"error": "Date and time_slots are required"}), 400
        
        # Clear existing availability for this date
        appt_db.availability_db.remove_availability(doctor_id, date, None)
        
        # Add new availability slots
        for time_slot in time_slots:
            appt_db.availability_db.add_availability(doctor_id, date, time_slot)
        
        return jsonify({"message": f"Set {len(time_slots)} availability slots for {date}"}), 200
    except Exception as e:
        print(f"  Error setting availability: {e}")
        return jsonify({"error": "Failed to set availability"}), 500




# ================= EXPERT FILE UPLOAD =================
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/expert/upload", methods=["POST"])
def upload_expert_file():
    """Upload file for expert request"""
    try:
        user = require_auth()
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        
        # Save file
        file_path = os.path.join(EXPERT_IMAGES_DIR, unique_filename)
        file.save(file_path)
        
        # Generate URL
        file_url = f"/uploads/expert_requests/images/{unique_filename}"
        
        print(f"  File uploaded: {file_url}")
        return jsonify({
            "success": True,
            "file_url": file_url,
            "filename": unique_filename,
            "message": "File uploaded successfully"
        }), 200
        
    except Exception as e:
        print(f"  Error uploading file: {e}")
        return jsonify({"error": "Failed to upload file"}), 500


# ================= GLOBAL ERROR HANDLER =================
@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    print(traceback.format_exc())
    return jsonify({"success": False, "error": str(e)}), 500


# ================= RUN =================
# Temporary approval/reject endpoints (until server restart)
@app.route("/admin/workers/<int:worker_id>/approve", methods=["POST"])
def temp_approve_worker(worker_id):
    """Temporary approval endpoint"""
    try:
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        if worker.get('status') == 'approved':
            return jsonify({"error": "Worker is already approved"}), 400
        
        worker_db.approve_worker(worker_id)
        
        return jsonify({
            "message": "Worker approved successfully",
            "worker_id": worker_id
        }), 200
        
    except Exception as e:
        print(f"Error approving worker: {e}")
        return jsonify({"error": f"Failed to approve worker: {str(e)}"}), 500

@app.route("/admin/workers/<int:worker_id>/reject", methods=["POST"])
def temp_reject_worker(worker_id):
    """Temporary rejection endpoint"""
    try:
        data = request.json or {}
        reason = data.get('rejection_reason')
        
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        worker_db.reject_worker(worker_id, reason)
        
        return jsonify({
            "message": "Worker rejected successfully",
            "worker_id": worker_id
        }), 200
        
    except Exception as e:
        print(f"Error rejecting worker: {e}")
        return jsonify({"error": f"Failed to reject worker: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("🚀 Starting ExpertEase Backend...")
    print(f"📍 Server running on: http://localhost:{port}")
    print(f"📍 Server running on: http://127.0.0.1:{port}")
    print(f"🌐 Access from browser: http://localhost:{port}")
    print("="*50)
    
    # Run normally without socket for now
    app.run(host="0.0.0.0", port=port, debug=True)
