"""
Tow Truck Operator Routes
API endpoints for tow truck operator registration, login, and management
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import jwt
from .tow_truck_db import tow_truck_db
from .car_service_worker_db import car_service_worker_db

# Create blueprint
tow_truck_bp = Blueprint('tow_truck_api', __name__)

@tow_truck_bp.route('/register', methods=['POST'])
@cross_origin()
def register_operator():
    """Register a new tow truck operator"""
    try:
        data = request.get_json()
        
        # Required fields
        required_fields = ['name', 'email', 'phone', 'password', 'city', 'experience', 
                          'truck_type', 'truck_registration', 'truck_model', 'truck_capacity']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Check if email or phone already exists
        if tow_truck_db.get_operator_by_email(data['email']):
            return jsonify({'success': False, 'error': 'Email already registered'}), 400
            
        # Hash password
        data['password_hash'] = generate_password_hash(data['password'])
        
        # Register in tow_truck_operators table
        operator_id = tow_truck_db.register_operator(data)
        
        if operator_id:
            # Also register in car_service_workers for unified admin management
            try:
                car_service_worker_db.create_worker(
                    name=data['name'],
                    email=data['email'],
                    phone=data['phone'],
                    password=data['password'],
                    role='Tow Truck Operator',
                    age=0,  # Not provided in tow truck form
                    city=data['city'],
                    address=data['city'],
                    experience=int(data['experience'].split()[0]) if data['experience'].split() else 0,
                    skills='Towing, Recovery',
                    vehicle_number=data['truck_registration'],
                    vehicle_model=data['truck_model'],
                    loading_capacity=data['truck_capacity'],
                    security_declaration=True
                )
            except Exception as e:
                print(f"⚠️ Unified worker registration failed: {e}")
                
            return jsonify({
                'success': True, 
                'message': 'Registration successful! Please wait for admin approval.',
                'operator_id': operator_id
            }), 201
        
        return jsonify({'success': False, 'error': 'Registration failed'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/login', methods=['POST'])
@cross_origin()
def login_operator():
    """Login tow truck operator"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
            
        operator = tow_truck_db.get_operator_by_email(email)
        
        if not operator or not check_password_hash(operator['password_hash'], password):
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
            
        if operator['approval_status'] != 'APPROVED':
            return jsonify({
                'success': False, 
                'error': f"Your account status is: {operator['approval_status']}. Please wait for admin approval.",
                'status': operator['approval_status']
            }), 403
            
        # Generate token
        token = jwt.encode({
            'operator_id': operator['id'],
            'email': operator['email'],
            'role': 'Tow Truck Operator',
            'exp': datetime.utcnow().timestamp() + (24 * 3600)
        }, 'your-secret-key', algorithm='HS256')
        
        # Remove sensitive data
        operator_data = {
            'id': operator['id'],
            'name': operator['name'],
            'email': operator['email'],
            'phone': operator['phone'],
            'city': operator['city'],
            'truck_type': operator['truck_type'],
            'is_online': operator['is_online']
        }
        
        return jsonify({
            'success': True,
            'token': token,
            'operator': operator_data
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/status', methods=['POST'])
@cross_origin()
def update_status():
    """Update operator online/offline status"""
    try:
        data = request.get_json()
        operator_id = data.get('operator_id')
        is_online = data.get('is_online')
        
        if operator_id is None or is_online is None:
            return jsonify({'success': False, 'error': 'operator_id and is_online required'}), 400
            
        success = tow_truck_db.update_operator_status(operator_id, is_online)
        
        if success:
            return jsonify({
                'success': True, 
                'message': f"Status updated to {'ONLINE' if is_online else 'OFFLINE'}"
            }), 200
            
        return jsonify({'success': False, 'error': 'Failed to update status'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/requests', methods=['GET'])
@cross_origin()
def get_requests():
    """Get all available tow requests for operator's city"""
    try:
        city = request.args.get('city')
        
        conn = tow_truck_db.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        query = "SELECT * FROM tow_requests WHERE status = 'pending'"
        params = []
        
        if city:
            query += " AND customer_address LIKE %s"
            params.append(f"%{city}%")
            
        cursor.execute(query, params)
        requests = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'requests': [dict(r) for r in requests]}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/requests/<int:request_id>/accept', methods=['POST'])
@cross_origin()
def accept_request(request_id):
    """Accept a tow request"""
    try:
        data = request.get_json()
        operator_id = data.get('operator_id')
        
        if not operator_id:
            return jsonify({'success': False, 'error': 'operator_id required'}), 400
            
        conn = tow_truck_db.get_conn()
        cursor = conn.cursor()
        
        # Check if already accepted
        cursor.execute("SELECT status FROM tow_requests WHERE id = %s", (request_id,))
        row = cursor.fetchone()
        if not row or row[0] != 'pending':
            return jsonify({'success': False, 'error': 'Request no longer available'}), 400
            
        # Update status
        cursor.execute('''
            UPDATE tow_requests 
            SET status = 'accepted', operator_id = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (operator_id, request_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Request accepted successfully'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/history/<int:operator_id>', methods=['GET'])
@cross_origin()
def get_history(operator_id):
    """Get operator's tow history"""
    try:
        conn = tow_truck_db.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT * FROM tow_requests 
            WHERE operator_id = %s 
            ORDER BY created_at DESC
        ''', (operator_id,))
        
        history = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'history': [dict(h) for h in history]}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
