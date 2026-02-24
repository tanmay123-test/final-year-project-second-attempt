"""
Automobile Expert API Routes
Complete API endpoints for expert authentication, requests, and consultations
"""

from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth_utils import verify_token, generate_token
from .expert_service import expert_service

# Create blueprint
expert_bp = Blueprint("expert", __name__)

def require_expert_auth(f):
    """Decorator to require expert authentication"""
    def wrapper(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Expert authentication required"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        username = verify_token(token)
        if not username:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Get expert profile
        expert_data = expert_service.authenticate_expert(username, "")
        if not expert_data["success"]:
            return jsonify({"error": "Expert not approved"}), 401
        
        # Add expert to request context
        request.expert = expert_data["expert"]
        request.worker = expert_data["worker"]
        return f(*args, **kwargs)
    
    wrapper.__name__ = f.__name__
    return wrapper

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

# ==================== AUTHENTICATION ====================

@expert_bp.route("/api/car/expert/signup", methods=["POST"])
def expert_signup():
    """Register new automobile expert"""
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'phone_number', 'password', 'city', 'primary_expertise']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        # Validate expertise area
        valid_expertise = ['Engine Systems', 'Electrical Systems', 'Transmission', 'Diagnostics', 'Multi-specialist']
        if data['primary_expertise'] not in valid_expertise:
            return jsonify({"error": "Invalid primary expertise area"}), 400
        
        # Validate work type
        valid_work_types = ['Garage Owner', 'Certified Technician', 'Automotive Engineer', 'Freelance Mechanic']
        work_type = data.get('work_type', '')
        if work_type and work_type not in valid_work_types:
            return jsonify({"error": "Invalid work type"}), 400
        
        # Prepare data
        user_data = {
            'full_name': data['full_name'],
            'email': data['email'],
            'phone_number': data['phone_number'],
            'password': data['password'],
            'city': data['city']
        }
        
        profile_data = {
            'primary_expertise': data['primary_expertise'],
            'years_of_experience': data.get('years_of_experience', 0),
            'work_type': work_type,
            'consultation_hours': data.get('consultation_hours', ''),
            'languages': data.get('languages', '')
        }
        
        result = expert_service.register_expert(user_data, profile_data)
        
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@expert_bp.route("/api/car/expert/login", methods=["POST"])
def expert_login():
    """Authenticate expert"""
    try:
        data = request.get_json() or {}
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        result = expert_service.authenticate_expert(email, password)
        
        if result["success"]:
            # Generate JWT token
            token = generate_token(result["expert"]["email"])
            
            return jsonify({
                "success": True,
                "message": "Login successful",
                "token": token,
                "expert": result["expert"],
                "worker": result["worker"]
            }), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

# ==================== DOCUMENT MANAGEMENT ====================

@expert_bp.route("/api/car/expert/upload-document/<int:expert_id>", methods=["POST"])
@require_expert_auth
def upload_expert_document(expert_id):
    """Upload expert document"""
    try:
        document_type = request.form.get('document_type')
        
        if not document_type:
            return jsonify({"error": "Document type is required"}), 400
        
        if 'document' not in request.files:
            return jsonify({"error": "Document file is required"}), 400
        
        file = request.files['document']
        
        result = expert_service.upload_expert_document(expert_id, document_type, file)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@expert_bp.route("/api/car/expert/document-status/<int:expert_id>", methods=["GET"])
@require_expert_auth
def get_expert_document_status(expert_id):
    """Get expert document upload and verification status"""
    try:
        result = expert_service.get_expert_document_status(expert_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to get document status: {str(e)}"}), 500

@expert_bp.route("/uploads/expert_documents/<filename>", methods=["GET"])
def serve_expert_document(filename):
    """Serve uploaded expert documents"""
    try:
        upload_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            "uploads", "expert_documents"
        )
        return send_from_directory(upload_dir, filename)
    except Exception as e:
        return jsonify({"error": f"Failed to serve file: {str(e)}"}), 500

# ==================== REQUEST MANAGEMENT ====================

@expert_bp.route("/api/car/expert/requests", methods=["POST"])
def create_expert_request():
    """Create new expert request"""
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        if not data.get('problem_description'):
            return jsonify({"error": "Problem description is required"}), 400
        
        # Get user ID from token (simplified - in production, get from user table)
        user_id = 1  # Placeholder
        
        result = expert_service.create_expert_request(user_id, data)
        
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Request creation failed: {str(e)}"}), 500

@expert_bp.route("/api/car/expert/available-experts", methods=["GET"])
def get_available_experts():
    """Get available experts for assignment"""
    try:
        category = request.args.get('category')
        
        experts = expert_service.get_available_experts(category)
        
        return jsonify({
            "success": True,
            "experts": experts,
            "total_available": len(experts)
        }), 200
            
    except Exception as e:
        return jsonify({"error": f"Failed to get experts: {str(e)}"}), 500

@expert_bp.route("/api/car/expert/assign-expert/<int:request_id>", methods=["POST"])
def assign_expert_to_request(request_id):
    """Assign expert to request"""
    try:
        data = request.get_json() or {}
        category = data.get('category')
        
        result = expert_service.assign_expert_to_request(request_id, category)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Assignment failed: {str(e)}"}), 500

# ==================== CONVERSATION MANAGEMENT ====================

@expert_bp.route("/api/car/expert/conversation/<int:request_id>", methods=["GET"])
@require_expert_auth
def get_conversation(request_id):
    """Get conversation messages"""
    try:
        result = expert_service.get_conversation(request_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to get conversation: {str(e)}"}), 500

@expert_bp.route("/api/car/expert/send-message", methods=["POST"])
@require_expert_auth
def send_message():
    """Send message in conversation"""
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        required_fields = ['request_id', 'user_id', 'message', 'sender_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400
        
        result = expert_service.send_message(
            data['request_id'],
            request.expert['id'],
            data['user_id'],
            data['message'],
            data['sender_type']
        )
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Message sending failed: {str(e)}"}), 500

@expert_bp.route("/api/car/expert/resolve-request/<int:request_id>", methods=["POST"])
@require_expert_auth
def resolve_request(request_id):
    """Resolve expert request"""
    try:
        result = expert_service.resolve_request(request_id, request.expert['id'])
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Resolution failed: {str(e)}"}), 500

# ==================== ADMIN OPERATIONS ====================

@expert_bp.route("/api/car/admin/expert/applications", methods=["GET"])
@require_admin_auth
def get_pending_applications():
    """Get pending expert applications"""
    try:
        result = expert_service.get_pending_applications()
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to get applications: {str(e)}"}), 500

@expert_bp.route("/api/car/admin/expert/approve/<int:profile_id>", methods=["POST"])
@require_admin_auth
def approve_expert_application(profile_id):
    """Approve expert application"""
    try:
        data = request.get_json() or {}
        admin_notes = data.get('admin_notes', '')
        
        result = expert_service.approve_expert_application(profile_id, admin_notes)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Approval failed: {str(e)}"}), 500

@expert_bp.route("/api/car/admin/expert/reject/<int:profile_id>", methods=["POST"])
@require_admin_auth
def reject_expert_application(profile_id):
    """Reject expert application"""
    try:
        data = request.get_json() or {}
        admin_notes = data.get('admin_notes', 'Application rejected')
        
        result = expert_service.reject_expert_application(profile_id, admin_notes)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Rejection failed: {str(e)}"}), 500

@expert_bp.route("/api/car/admin/expert/verify-document/<int:document_id>", methods=["POST"])
@require_admin_auth
def verify_expert_document(document_id):
    """Verify expert document"""
    try:
        data = request.get_json() or {}
        status = data.get('status')
        remark = data.get('admin_remark', '')
        
        if status not in ['APPROVED', 'REJECTED']:
            return jsonify({"error": "Invalid status"}), 400
        
        result = expert_service.verify_expert_document(document_id, status, remark)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Verification failed: {str(e)}"}), 500

@expert_bp.route("/api/car/admin/expert/statistics", methods=["GET"])
@require_admin_auth
def get_expert_statistics():
    """Get expert system statistics"""
    try:
        result = expert_service.get_expert_statistics()
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to get statistics: {str(e)}"}), 500

# ==================== ERROR HANDLING ====================

@expert_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@expert_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

@expert_bp.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return jsonify({"error": "Access forbidden"}), 403
