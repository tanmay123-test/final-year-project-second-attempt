"""
Tow Truck Driver Authentication Routes
Complete API endpoints for tow truck driver authentication and verification
"""

from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth_utils import verify_token, generate_token
from .tow_truck_auth_service import tow_truck_auth_service

# Create blueprint
tow_truck_auth_bp = Blueprint("tow_truck_auth", __name__)

def require_admin_auth(f):
    """Decorator to require admin authentication"""
    def wrapper(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Admin authentication required"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token (simplified - in production, check admin role)
        username = verify_token(token)
        if not username:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Add admin to request context
        request.admin_user = username
        return f(*args, **kwargs)
    
    wrapper.__name__ = f.__name__
    return wrapper

# ==================== DRIVER REGISTRATION ====================

@tow_truck_auth_bp.route("/api/car/tow-truck/signup", methods=["POST"])
def tow_truck_signup():
    """Register new tow truck driver with complete verification"""
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'phone_number', 'password', 'city']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        # Validate truck information
        truck_fields = ['truck_type', 'truck_registration_number', 'truck_model', 
                       'truck_capacity', 'insurance_expiry_date', 'fitness_expiry_date']
        for field in truck_fields:
            if not data.get(field):
                return jsonify({"error": f"Truck {field} is required"}), 400
        
        # Validate truck type
        valid_truck_types = ['FLATBED', 'WHEEL_LIFT', 'HEAVY_DUTY']
        if data['truck_type'] not in valid_truck_types:
            return jsonify({"error": "Invalid truck type"}), 400
        
        # Validate truck capacity
        valid_capacities = ['SMALL_CAR', 'SUV', 'HEAVY_VEHICLE']
        if data['truck_capacity'] not in valid_capacities:
            return jsonify({"error": "Invalid truck capacity"}), 400
        
        # Register driver
        basic_info = {
            'full_name': data['full_name'],
            'email': data['email'],
            'phone_number': data['phone_number'],
            'password': data['password'],
            'city': data['city'],
            'service_radius_km': data.get('service_radius_km', 10)
        }
        
        truck_info = {
            'truck_type': data['truck_type'],
            'truck_registration_number': data['truck_registration_number'],
            'truck_model': data['truck_model'],
            'truck_capacity': data['truck_capacity'],
            'insurance_expiry_date': data['insurance_expiry_date'],
            'fitness_expiry_date': data['fitness_expiry_date']
        }
        
        result = tow_truck_auth_service.register_tow_truck_driver(basic_info, truck_info)
        
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

# ==================== DRIVER LOGIN ====================

@tow_truck_auth_bp.route("/api/car/tow-truck/login", methods=["POST"])
def tow_truck_login():
    """Authenticate tow truck driver"""
    try:
        data = request.get_json() or {}
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        result = tow_truck_auth_service.authenticate_driver(email, password)
        
        if result["success"]:
            # Generate JWT token
            token = generate_token(result["driver"]["email"])
            
            return jsonify({
                "success": True,
                "message": "Login successful",
                "token": token,
                "driver": result["driver"],
                "worker": result["worker"],
                "expiry_alerts": result.get("expiry_alerts", [])
            }), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

# ==================== DOCUMENT UPLOAD ====================

@tow_truck_auth_bp.route("/api/car/tow-truck/upload-document/<int:driver_id>", methods=["POST"])
def upload_driver_document(driver_id):
    """Upload document for tow truck driver"""
    try:
        # Get document type and expiry date
        document_type = request.form.get('document_type')
        expiry_date = request.form.get('expiry_date')
        
        if not document_type:
            return jsonify({"error": "Document type is required"}), 400
        
        # Get file
        if 'document' not in request.files:
            return jsonify({"error": "Document file is required"}), 400
        
        file = request.files['document']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Upload document
        result = tow_truck_auth_service.upload_driver_document(
            driver_id, document_type, file, expiry_date
        )
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@tow_truck_auth_bp.route("/api/car/tow-truck/document-status/<int:driver_id>", methods=["GET"])
def get_driver_document_status(driver_id):
    """Get document upload and verification status"""
    try:
        result = tow_truck_auth_service.get_driver_document_status(driver_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to get document status: {str(e)}"}), 500

@tow_truck_auth_bp.route("/uploads/tow_truck_documents/<filename>", methods=["GET"])
def serve_driver_document(filename):
    """Serve uploaded driver documents"""
    try:
        upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "tow_truck_documents")
        return send_from_directory(upload_dir, filename)
    except Exception as e:
        return jsonify({"error": f"Failed to serve file: {str(e)}"}), 500

# ==================== ADMIN VERIFICATION ====================

@tow_truck_auth_bp.route("/api/car/admin/tow-truck/applications", methods=["GET"])
@require_admin_auth
def get_pending_applications():
    """Get all pending tow truck driver applications"""
    try:
        result = tow_truck_auth_service.get_pending_applications()
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to get applications: {str(e)}"}), 500

@tow_truck_auth_bp.route("/api/car/admin/tow-truck/approve/<int:driver_id>", methods=["POST"])
@require_admin_auth
def approve_driver_application(driver_id):
    """Approve tow truck driver application"""
    try:
        data = request.get_json() or {}
        admin_notes = data.get('admin_notes', '')
        
        result = tow_truck_auth_service.approve_driver_application(driver_id, admin_notes)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Approval failed: {str(e)}"}), 500

@tow_truck_auth_bp.route("/api/car/admin/tow-truck/reject/<int:driver_id>", methods=["POST"])
@require_admin_auth
def reject_driver_application(driver_id):
    """Reject tow truck driver application"""
    try:
        data = request.get_json() or {}
        admin_notes = data.get('admin_notes', 'Application rejected')
        
        result = tow_truck_auth_service.reject_driver_application(driver_id, admin_notes)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Rejection failed: {str(e)}"}), 500

@tow_truck_auth_bp.route("/api/car/admin/tow-truck/verify-document/<int:document_id>", methods=["POST"])
@require_admin_auth
def verify_driver_document(document_id):
    """Verify individual driver document"""
    try:
        data = request.get_json() or {}
        status = data.get('status')
        admin_remark = data.get('admin_remark', '')
        
        if status not in ['APPROVED', 'REJECTED']:
            return jsonify({"error": "Invalid status"}), 400
        
        result = tow_truck_auth_service.verify_driver_document(document_id, status, admin_remark)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Verification failed: {str(e)}"}), 500

# ==================== DRIVER MANAGEMENT ====================

@tow_truck_auth_bp.route("/api/car/admin/tow-truck/drivers", methods=["GET"])
@require_admin_auth
def get_approved_drivers():
    """Get all approved tow truck drivers"""
    try:
        result = tow_truck_auth_service.get_approved_drivers()
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to get drivers: {str(e)}"}), 500

@tow_truck_auth_bp.route("/api/car/admin/tow-truck/statistics", methods=["GET"])
@require_admin_auth
def get_driver_statistics():
    """Get tow truck driver statistics"""
    try:
        result = tow_truck_auth_service.get_driver_statistics()
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to get statistics: {str(e)}"}), 500

# ==================== FRAUD PROTECTION ====================

@tow_truck_auth_bp.route("/api/car/tow-truck/log-fraud-incident/<int:driver_id>", methods=["POST"])
def log_fraud_incident(driver_id):
    """Log fraud incident for tow truck driver"""
    try:
        data = request.get_json() or {}
        incident_type = data.get('incident_type')
        incident_data = data.get('incident_data', {})
        
        if not incident_type:
            return jsonify({"error": "Incident type is required"}), 400
        
        result = tow_truck_auth_service.log_fraud_incident(driver_id, incident_type, incident_data)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to log incident: {str(e)}"}), 500

@tow_truck_auth_bp.route("/api/car/tow-truck/fraud-risk/<int:driver_id>", methods=["GET"])
def check_driver_fraud_risk(driver_id):
    """Check fraud risk for tow truck driver"""
    try:
        result = tow_truck_auth_service.check_driver_fraud_risk(driver_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to check fraud risk: {str(e)}"}), 500

# ==================== VEHICLE COMPATIBILITY ====================

@tow_truck_auth_bp.route("/api/car/tow-truck/check-compatibility/<int:driver_id>", methods=["POST"])
def check_vehicle_compatibility(driver_id):
    """Check if driver's truck is compatible with vehicle type"""
    try:
        data = request.get_json() or {}
        vehicle_type = data.get('vehicle_type')
        
        if not vehicle_type:
            return jsonify({"error": "Vehicle type is required"}), 400
        
        result = tow_truck_auth_service.check_vehicle_compatibility(driver_id, vehicle_type)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to check compatibility: {str(e)}"}), 500

# ==================== EXPIRY MONITORING ====================

@tow_truck_auth_bp.route("/api/car/tow-truck/expiry-alerts/<int:driver_id>", methods=["GET"])
def get_driver_expiry_alerts(driver_id):
    """Get expiry alerts for tow truck driver"""
    try:
        result = tow_truck_auth_service.get_driver_expiry_alerts(driver_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to get expiry alerts: {str(e)}"}), 500

@tow_truck_auth_bp.route("/api/car/admin/tow-truck/run-expiry-monitoring", methods=["POST"])
@require_admin_auth
def run_expiry_monitoring():
    """Run automated expiry monitoring"""
    try:
        result = tow_truck_auth_service.run_expiry_monitoring()
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Expiry monitoring failed: {str(e)}"}), 500

# ==================== ERROR HANDLING ====================

@tow_truck_auth_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@tow_truck_auth_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

@tow_truck_auth_bp.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return jsonify({"error": "Access forbidden"}), 403
