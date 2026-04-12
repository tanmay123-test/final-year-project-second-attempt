"""
Main admin routes module for ExpertEase backend.
Handles admin authentication and service selection.
"""

from flask import Blueprint, request, jsonify, session
from functools import wraps
import jwt
from datetime import datetime, timedelta
import os

# Import database instances
from user_db import UserDB
from worker_db import WorkerDB

# Initialize database instances
user_db = UserDB()
worker_db = WorkerDB()

# Hardcoded admin credentials (simple authentication)
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

# JWT Secret for admin tokens
JWT_SECRET = os.environ.get('JWT_SECRET', 'admin_secret_key_change_in_production')

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/stats', methods=['GET'])
@admin_auth_required
def get_dashboard_stats():
    """Get global dashboard statistics for admin"""
    try:
        total_workers = worker_db.get_worker_count()
        pending_approvals = worker_db.get_worker_count(status='pending')
        total_users = user_db.get_user_count()
        
        # Service-specific counts
        healthcare_total = worker_db.get_worker_count(service_type='healthcare')
        healthcare_pending = worker_db.get_worker_count(status='pending', service_type='healthcare')
        
        car_total = worker_db.get_worker_count(service_type='car')
        car_pending = worker_db.get_worker_count(status='pending', service_type='car')
        
        housekeeping_total = worker_db.get_worker_count(service_type='housekeeping')
        housekeeping_pending = worker_db.get_worker_count(status='pending', service_type='housekeeping')
        
        freelance_total = worker_db.get_worker_count(service_type='freelance')
        freelance_pending = worker_db.get_worker_count(status='pending', service_type='freelance')
        
        money_total = worker_db.get_worker_count(service_type='money')
        money_pending = worker_db.get_worker_count(status='pending', service_type='money')

        return jsonify({
            "total_workers": total_workers,
            "pending_approvals": pending_approvals,
            "total_users": total_users,
            "active_services": 5,
            "services": {
                "healthcare": {"total": healthcare_total, "pending": healthcare_pending},
                "car_service": {"total": car_total, "pending": car_pending},
                "housekeeping": {"total": housekeeping_total, "pending": housekeeping_pending},
                "freelance": {"total": freelance_total, "pending": freelance_pending},
                "money_management": {"total": money_total, "pending": money_pending}
            }
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch stats: {str(e)}"}), 500

def admin_auth_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No authorization token provided"}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Verify JWT token
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            if payload.get('role') != 'admin':
                return jsonify({"error": "Invalid token role"}), 401
                
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
    return decorated_function

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """
    Admin login endpoint.
    
    Request Body:
    {
        "username": "admin",
        "password": "admin123"
    }
    
    Returns:
    {
        "token": "jwt_token",
        "message": "Login successful"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        # Verify hardcoded credentials
        if (username == ADMIN_CREDENTIALS['username'] and 
            password == ADMIN_CREDENTIALS['password']):
            
            # Generate JWT token
            payload = {
                'username': username,
                'role': 'admin',
                'exp': datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry
            }
            
            token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
            
            return jsonify({
                "token": token,
                "message": "Login successful"
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
            
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

@admin_bp.route('/services', methods=['GET'])
@admin_auth_required
def get_admin_services():
    """
    Get available services for admin management.
    
    Returns:
    {
        "services": [
            {"id": "healthcare", "name": "Healthcare", "description": "..."},
            {"id": "car_service", "name": "Car Service", "description": "..."},
            ...
        ]
    }
    """
    services = [
        {
            "id": "healthcare",
            "name": "Healthcare",
            "description": "Manage doctors, appointments, and medical services"
        },
        {
            "id": "car_service",
            "name": "Car Service",
            "description": "Manage mechanics, towing, and automotive services"
        },
        {
            "id": "housekeeping",
            "name": "Housekeeping",
            "description": "Manage housekeeping professionals and bookings"
        },
        {
            "id": "freelance",
            "name": "Freelance Marketplace",
            "description": "Manage freelancers and freelance projects"
        },
        {
            "id": "money_management",
            "name": "Money Management",
            "description": "Manage financial advisors and money services"
        }
    ]
    
    return jsonify({"services": services}), 200

@admin_bp.route('/verify-token', methods=['POST'])
def verify_admin_token():
    """
    Verify admin token validity.
    
    Request Body:
    {
        "token": "jwt_token"
    }
    
    Returns:
    {
        "valid": true,
        "username": "admin"
    }
    """
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({"valid": False, "error": "No token provided"}), 400
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Verify JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        
        if payload.get('role') != 'admin':
            return jsonify({"valid": False, "error": "Invalid token role"}), 401
        
        return jsonify({
            "valid": True,
            "username": payload.get('username')
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"valid": False, "error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

@admin_bp.route('/logout', methods=['POST'])
@admin_auth_required
def admin_logout():
    """
    Admin logout endpoint.
    (In a real implementation, you might want to blacklist the token)
    
    Returns:
    {
        "message": "Logout successful"
    }
    """
    return jsonify({"message": "Logout successful"}), 200

# Import healthcare admin routes
try:
    from .admin_healthcare import healthcare_admin_bp
    admin_bp.register_blueprint(healthcare_admin_bp, url_prefix='/healthcare')
    print("  Healthcare admin blueprint registered")
except ImportError as e:
    print(f"   Could not register healthcare admin blueprint: {e}")

# Import other admin modules
try:
    from .admin_users import users_admin_bp
    admin_bp.register_blueprint(users_admin_bp)
    print("  Users admin blueprint registered")
except ImportError as e:
    print(f"   Could not register users admin blueprint: {e}")

try:
    from .admin_workers import workers_admin_bp
    admin_bp.register_blueprint(workers_admin_bp)
    print("  Workers admin blueprint registered")
except ImportError as e:
    print(f"   Could not register workers admin blueprint: {e}")

try:
    from .admin_appointments import appointments_admin_bp
    admin_bp.register_blueprint(appointments_admin_bp)
    print("  Appointments admin blueprint registered")
except ImportError as e:
    print(f"   Could not register appointments admin blueprint: {e}")

try:
    from .admin_payments import payments_admin_bp
    admin_bp.register_blueprint(payments_admin_bp)
    print("  Payments admin blueprint registered")
except ImportError as e:
    print(f"   Could not register payments admin blueprint: {e}")

try:
    from .admin_settings import settings_admin_bp
    admin_bp.register_blueprint(settings_admin_bp)
    print("  Settings admin blueprint registered")
except ImportError as e:
    print(f"   Could not register settings admin blueprint: {e}")
