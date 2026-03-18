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
from car_service.mechanic_db import mechanic_db

mechanic_bp = Blueprint("mechanic", __name__)

@mechanic_bp.route("/api/auth/car/mechanic/signup", methods=["POST"])
def mechanic_signup():
    """Mechanic signup endpoint"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            name = data.get("full_name", "").strip()
            email = data.get("email", "").strip()
            phone = data.get("phone", "").strip()
            password = data.get("password", "").strip()
            age = data.get("age", "").strip()
            city = data.get("city", "").strip()
            address = data.get("address", "").strip()
            experience = data.get("experience", "").strip()
            skills = data.get("skills", "").strip()
            
            # For JSON requests, files will be uploaded separately
            aadhaar_path = None
            license_path = None
            certificate_path = None
            profile_photo_path = None
        else:
            # Handle form data with file uploads
            name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            password = request.form.get("password", "").strip()
            age = request.form.get("age", "").strip()
            city = request.form.get("city", "").strip()
            address = request.form.get("address", "").strip()
            experience = request.form.get("experience", "").strip()
            skills = request.form.get("skills", "").strip()
            
            # Handle file uploads
            aadhaar_path = None
            license_path = None
            certificate_path = None
            profile_photo_path = None
            
            # Save uploaded files
            if 'aadhaar_file' in request.files:
                aadhaar_file = request.files['aadhaar_file']
                if aadhaar_file:
                    import os
                    from werkzeug.utils import secure_filename
                    filename = secure_filename(aadhaar_file.filename)
                    upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    aadhaar_path = os.path.join(upload_folder, f"aadhaar_{filename}")
                    aadhaar_file.save(aadhaar_path)
            
            if 'license_file' in request.files:
                license_file = request.files['license_file']
                if license_file:
                    import os
                    from werkzeug.utils import secure_filename
                    filename = secure_filename(license_file.filename)
                    upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    license_path = os.path.join(upload_folder, f"license_{filename}")
                    license_file.save(license_path)
            
            if 'certificate_file' in request.files:
                cert_file = request.files['certificate_file']
                if cert_file:
                    import os
                    from werkzeug.utils import secure_filename
                    filename = secure_filename(cert_file.filename)
                    upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    certificate_path = os.path.join(upload_folder, f"cert_{filename}")
                    cert_file.save(certificate_path)
            
            if 'profile_photo_file' in request.files:
                photo_file = request.files['profile_photo_file']
                if photo_file:
                    import os
                    from werkzeug.utils import secure_filename
                    filename = secure_filename(photo_file.filename)
                    upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    profile_photo_path = os.path.join(upload_folder, f"photo_{filename}")
                    photo_file.save(profile_photo_path)
        
        # Validation
        if not all([name, email, phone, password, age, city, experience, skills]):
            return jsonify({"error": "All required fields must be filled"}), 400
        
        # Create mechanic
        try:
            mechanic_id = mechanic_db.create_mechanic(
                name=name, email=email, phone=phone, password=password,
                age=int(age), city=city, address=address, experience=int(experience), skills=skills,
                aadhaar_path=aadhaar_path, license_path=license_path,
                certificate_path=certificate_path, profile_photo_path=profile_photo_path
            )
            return jsonify({
                "message": "Mechanic registered successfully",
                "mechanic_id": mechanic_id,
                "worker_id": mechanic_id
            }), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": f"Registration failed: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@mechanic_bp.route("/api/car/service/workers/pending", methods=["GET"])
def get_pending_workers():
    """Get all pending workers for admin approval"""
    try:
        cursor = mechanic_db.conn.cursor()
        cursor.execute("""
            SELECT id, name, email, phone, age, city, address, experience, skills,
                   profile_photo_path, aadhaar_path, license_path, certificate_path,
                   created_at, role
            FROM mechanics 
            WHERE status = 'PENDING'
            ORDER BY created_at DESC
        """)
        
        workers = []
        for row in cursor.fetchall():
            workers.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'age': row[4],
                'city': row[5],
                'address': row[6],
                'experience': row[7],
                'skills': row[8],
                'profile_photo': row[9],
                'aadhaar_path': row[10],
                'license_path': row[11],
                'certificate_path': row[12],
                'created_at': row[13],
                'role': row[14],
                'worker_type': 'Regular Worker'
            })
        
        return jsonify({"workers": workers}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@mechanic_bp.route("/api/car/service/workers/approved", methods=["GET"])
def get_approved_workers():
    """Get all approved workers"""
    try:
        cursor = mechanic_db.conn.cursor()
        cursor.execute("""
            SELECT id, name, email, phone, age, city, address, experience, skills,
                   profile_photo_path, aadhaar_path, license_path, certificate_path,
                   created_at, role
            FROM mechanics 
            WHERE status = 'APPROVED'
            ORDER BY created_at DESC
        """)
        
        workers = []
        for row in cursor.fetchall():
            workers.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'age': row[4],
                'city': row[5],
                'address': row[6],
                'experience': row[7],
                'skills': row[8],
                'profile_photo': row[9],
                'aadhaar_path': row[10],
                'license_path': row[11],
                'certificate_path': row[12],
                'created_at': row[13],
                'role': row[14],
                'worker_type': 'Regular Worker'
            })
        
        return jsonify({"workers": workers}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@mechanic_bp.route("/api/car/service/worker/status", methods=["PUT"])
def update_worker_status():
    """Update worker status (approve/reject)"""
    try:
        data = request.get_json()
        worker_id = data.get('worker_id')
        status = data.get('status')  # APPROVED or REJECTED
        
        if not worker_id or not status:
            return jsonify({"error": "worker_id and status are required"}), 400
        
        if status not in ['APPROVED', 'REJECTED']:
            return jsonify({"error": "Invalid status. Must be APPROVED or REJECTED"}), 400
        
        # Update worker status
        cursor = mechanic_db.conn.cursor()
        cursor.execute("""
            UPDATE mechanics 
            SET status = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (status, worker_id))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Worker not found"}), 404
        
        mechanic_db.conn.commit()
        
        return jsonify({
            "message": f"Worker status updated to {status}",
            "worker_id": worker_id,
            "status": status
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@mechanic_bp.route("/api/car/service/worker/stats", methods=["GET"])
def get_worker_stats():
    """Get worker statistics"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        # For now, we'll return mock data
        # In production, you'd decode the token and get real stats
        
        return jsonify({
            "totalJobs": 45,
            "completedJobs": 38,
            "pendingJobs": 7,
            "earnings": 12500
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@mechanic_bp.route("/api/auth/car/mechanic/login", methods=["POST"])
def mechanic_login():
    """Mechanic login endpoint"""
    try:
        # Get data from JSON or form
        if request.is_json:
            data = request.get_json()
            email = data.get("email", "").strip()
            password = data.get("password", "").strip()
        else:
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()
        
        # Validate input
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Authenticate mechanic
        mechanic = mechanic_db.verify_mechanic(email, password)
        
        print(f"🔍 Login attempt for email: {email}")
        print(f"🔍 Mechanic found: {mechanic is not None}")
        if mechanic:
            print(f"🔍 Mechanic status: {mechanic.get('status')}")
            print(f"🔍 Mechanic data: {mechanic}")
        
        # If not found in mechanic DB, try worker DB for mechanics
        if not mechanic:
            print(f"🔍 Trying worker database...")
            from car_service.worker_db import worker_db
            worker = worker_db.verify_worker_by_email(email, password)
            print(f"🔍 Worker found: {worker is not None}")
            if worker:
                print(f"🔍 Worker status: {worker.get('status')}")
                print(f"🔍 Worker data: {worker}")
                if worker.get("role") == "Mechanic":
                    print(f"🔍 Found mechanic in worker DB")
                    # Check if approved
                    if worker.get("status") != "APPROVED":
                        print(f"🔍 Blocking login - worker status not approved: {worker.get('status')}")
                        return jsonify({
                            "error": "Your account is pending admin approval. Please wait for approval before logging in.",
                            "status": worker.get("status"),
                            "requires_approval": True
                        }), 403
                    else:
                        print(f"🔍 Worker approved - allowing login")
                        # Convert worker to mechanic format
                        mechanic = {
                            'id': worker["id"],
                            'name': worker["name"],
                            'email': worker["email"],
                            'status': worker["status"],
                            'role': worker.get("role", "Mechanic")
                        }
        
        if not mechanic:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Check if mechanic is approved
        if mechanic.get('status') != 'APPROVED':
            print(f"🔍 Blocking login - status not approved: {mechanic.get('status')}")
            return jsonify({
                "error": "Your account is pending admin approval. Please wait for approval before logging in.",
                "status": mechanic.get('status'),
                "requires_approval": True
            }), 403
        
        # Generate JWT token
        import jwt
        from datetime import datetime, timedelta
        
        token_payload = {
            'mechanic_id': mechanic['id'],
            'email': mechanic['email'],
            'role': mechanic.get('role', 'Mechanic'),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(token_payload, 'your-secret-key', algorithm='HS256')
        
        # Remove password hash from response
        mechanic_data = {k: v for k, v in mechanic.items() if k != 'password_hash'}
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "mechanic": mechanic_data
        }), 200
        
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
        from car_service.worker_db import worker_db
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
