"""
Authentication Routes using Organized Database Manager
Provides API endpoints for user and worker authentication
"""

from flask import Blueprint, request, jsonify
from services.auth_service import auth_service

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# User Routes
@auth_bp.route('/api/register', methods=['POST'])
def register_user():
    """Register new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "message": f"Missing required field: {field}"}), 400
        
        # Register user
        result = auth_service.register_user(
            email=data['email'],
            password=data['password'],
            name=data['name'],
            phone=data.get('phone')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Registration failed: {str(e)}"}), 500

@auth_bp.route('/api/login', methods=['POST'])
def login_user():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'email' not in data or 'password' not in data:
            return jsonify({"success": False, "message": "Email and password required"}), 400
        
        # Login user (supports both email and username)
        result = auth_service.login_user(data['email'], data['password'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Login failed: {str(e)}"}), 500

@auth_bp.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """Get user profile"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"success": False, "message": "Authentication required"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        from auth_utils import verify_token
        user_id = verify_token(token)
        if not user_id:
            return jsonify({"success": False, "message": "Invalid token"}), 401
        
        result = auth_service.get_user_profile(int(user_id))
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to get profile: {str(e)}"}), 500

@auth_bp.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    """Update user profile"""
    try:
        # Get user ID from token
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({"success": False, "message": "Authentication required"}), 401
        
        data = request.get_json()
        
        # Update user profile
        result = auth_service.update_user_profile(int(user_id), **data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Update failed: {str(e)}"}), 500

# Worker Routes
@auth_bp.route('/api/worker/register', methods=['POST'])
def register_worker():
    """Register new worker"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name', 'service_type', 'worker_type']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "message": f"Missing required field: {field}"}), 400
        
        # Register worker
        result = auth_service.register_worker(
            email=data['email'],
            password=data['password'],
            name=data['name'],
            phone=data.get('phone'),
            service_type=data['service_type'],
            worker_type=data['worker_type']
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Registration failed: {str(e)}"}), 500

@auth_bp.route('/api/worker/login', methods=['POST'])
def login_worker():
    """Login worker"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'email' not in data or 'password' not in data:
            return jsonify({"success": False, "message": "Email and password required"}), 400
        
        # Login worker
        result = auth_service.login_worker(data['email'], data['password'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Login failed: {str(e)}"}), 500

@auth_bp.route('/api/worker/profile', methods=['GET'])
def get_worker_profile():
    """Get worker profile"""
    try:
        # Get worker ID from token
        worker_id = request.headers.get('X-Worker-ID')
        if not worker_id:
            return jsonify({"success": False, "message": "Authentication required"}), 401
        
        result = auth_service.get_worker_profile(int(worker_id))
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to get profile: {str(e)}"}), 500

# Service Worker Routes
@auth_bp.route('/api/workers/<service_type>', methods=['GET'])
def get_workers_by_service(service_type):
    """Get workers by service type"""
    try:
        result = auth_service.get_workers_by_service(service_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to get workers: {str(e)}"}), 500

@auth_bp.route('/api/workers/healthcare', methods=['GET'])
def get_healthcare_workers():
    """Get healthcare workers"""
    try:
        worker_type = request.args.get('worker_type')
        result = auth_service.get_healthcare_workers(worker_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to get healthcare workers: {str(e)}"}), 500

@auth_bp.route('/api/workers/car_service', methods=['GET'])
def get_car_service_workers():
    """Get car service workers"""
    try:
        worker_type = request.args.get('worker_type')
        result = auth_service.get_car_service_workers(worker_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to get car service workers: {str(e)}"}), 500

@auth_bp.route('/api/workers/housekeeping', methods=['GET'])
def get_housekeeping_workers():
    """Get housekeeping workers"""
    try:
        result = auth_service.get_housekeeping_workers()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to get housekeeping workers: {str(e)}"}), 500

@auth_bp.route('/api/workers/freelance', methods=['GET'])
def get_freelance_workers():
    """Get freelance workers"""
    try:
        result = auth_service.get_freelance_workers()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to get freelance workers: {str(e)}"}), 500

@auth_bp.route('/api/workers/money_management', methods=['GET'])
def get_money_management_workers():
    """Get money management workers"""
    try:
        result = auth_service.get_money_management_workers()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to get money management workers: {str(e)}"}), 500

# Statistics Routes
@auth_bp.route('/api/statistics/<service_type>', methods=['GET'])
def get_service_statistics(service_type):
    """Get service statistics"""
    try:
        result = auth_service.get_service_statistics(service_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to get statistics: {str(e)}"}), 500

# Health Check Route
@auth_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check for authentication service"""
    try:
        result = auth_service.health_check()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Health check failed: {str(e)}"}), 500
