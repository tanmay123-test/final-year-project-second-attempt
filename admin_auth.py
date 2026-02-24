"""
Admin Authentication Module
JWT-based authentication for admin users
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

from auth_utils import JWT_SECRET, JWT_ALGORITHM
from admin_db import admin_db

# Admin token expiration (24 hours)
ADMIN_TOKEN_EXPIRY = 24 * 60 * 60  # 24 hours in seconds

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, password_hash):
    """Verify password against hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except:
        return False

def generate_admin_token(username):
    """Generate JWT token for admin"""
    payload = {
        'username': username,
        'role': 'admin',
        'exp': datetime.utcnow() + timedelta(seconds=ADMIN_TOKEN_EXPIRY),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_admin_token(token):
    """Verify admin JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Check if token has admin role
        if payload.get('role') != 'admin':
            return None, "Invalid token role"
        
        # Check if admin exists and is active
        admin = admin_db.get_admin_by_username(payload.get('username'))
        if not admin:
            return None, "Admin not found"
        
        if not admin.get('is_active', True):
            return None, "Admin account deactivated"
        
        return admin, None
        
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"
    except Exception as e:
        return None, f"Token verification failed: {str(e)}"

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "Authorization header required"}), 401
        
        # Extract token from "Bearer <token>" format
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({"error": "Invalid authorization header format"}), 401
        
        # Verify token
        admin, error = verify_admin_token(token)
        if error:
            return jsonify({"error": error}), 401
        
        # Add admin info to request context
        request.current_admin = admin
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_admin():
    """Get current admin from request context"""
    return getattr(request, 'current_admin', None)

def admin_login_required(f):
    """Alternative decorator name for admin_required"""
    return admin_required(f)

# Utility functions for admin session management
def refresh_admin_token(token):
    """Refresh admin token if still valid"""
    admin, error = verify_admin_token(token)
    if error:
        return None, error
    
    # Generate new token with extended expiry
    new_token = generate_admin_token(admin['username'])
    return new_token, None

def logout_admin(token):
    """Logout admin (token invalidation - client-side)"""
    # In a real implementation, you might maintain a blacklist
    # For now, we rely on client-side token deletion
    return True
