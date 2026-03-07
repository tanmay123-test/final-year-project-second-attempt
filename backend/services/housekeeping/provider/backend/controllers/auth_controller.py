from flask import Blueprint, request, jsonify
from services.housekeeping.provider.backend.services.auth_service import ProviderAuthService

provider_auth_bp = Blueprint('provider_auth', __name__)
auth_service = ProviderAuthService()

@provider_auth_bp.route('/auth/signup', methods=['POST'])
def signup():
    data = request.json
    required = ['name', 'email', 'password', 'service_type', 'location']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Housekeeping providers might need specific fields
    # For now, standard worker signup
    result, status = auth_service.register_provider(data)
    return jsonify(result), status

@provider_auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing email or password"}), 400
        
    result, status = auth_service.login_provider(data['email'], data['password'])
    return jsonify(result), status

@provider_auth_bp.route('/auth/me', methods=['GET'])
def get_current_provider():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing token"}), 401
    
    token = auth_header.split(' ')[1]
    result, status = auth_service.verify_provider_token(token)
    return jsonify(result), status

@provider_auth_bp.route('/auth/status', methods=['GET'])
def check_status():
    # Helper to check if token is valid (implementation depends on global auth_utils)
    return jsonify({"msg": "Auth service running"}), 200
