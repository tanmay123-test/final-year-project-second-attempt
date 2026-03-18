"""
Tow Truck Operator Routes
API endpoints for tow truck operator registration, login, and management
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import os

# Create blueprint
tow_truck_bp = Blueprint('tow_truck_api', __name__)

# Database paths
TOW_TRUCK_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'tow_truck_operators.db')
CAR_SERVICE_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'car_service_workers.db')

# Import car service worker DB to ensure table creation
from .car_service_worker_db import CarServiceWorkerDB

class TowTruckDB:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        """Initialize tow truck operators database"""
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        # Create tow_truck_operators table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tow_truck_operators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                city TEXT NOT NULL,
                experience TEXT NOT NULL,
                truck_type TEXT NOT NULL,
                truck_registration TEXT NOT NULL,
                truck_model TEXT NOT NULL,
                truck_capacity TEXT NOT NULL,
                license_path TEXT,
                insurance_path TEXT,
                fitness_cert_path TEXT,
                pollution_cert_path TEXT,
                is_online INTEGER DEFAULT 0,
                approval_status TEXT DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create tow_requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tow_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                customer_address TEXT NOT NULL,
                vehicle_type TEXT NOT NULL,
                issue_description TEXT,
                operator_id INTEGER,
                status TEXT DEFAULT 'pending',
                amount REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (operator_id) REFERENCES tow_truck_operators(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_operator(self, operator_data):
        """Register a new tow truck operator"""
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO tow_truck_operators 
                (name, email, phone, password_hash, city, experience, truck_type, 
                 truck_registration, truck_model, truck_capacity, license_path,
                 insurance_path, fitness_cert_path, pollution_cert_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                operator_data['name'],
                operator_data['email'],
                operator_data['phone'],
                operator_data['password_hash'],
                operator_data['city'],
                operator_data['experience'],
                operator_data['truck_type'],
                operator_data['truck_registration'],
                operator_data['truck_model'],
                operator_data['truck_capacity'],
                operator_data.get('license_path'),
                operator_data.get('insurance_path'),
                operator_data.get('fitness_cert_path'),
                operator_data.get('pollution_cert_path')
            ))
            
            operator_id = cursor.lastrowid
            conn.commit()
            
            return {'success': True, 'operator_id': operator_id}
            
        except sqlite3.IntegrityError as e:
            if 'email' in str(e):
                return {'success': False, 'error': 'Email already exists'}
            elif 'phone' in str(e):
                return {'success': False, 'error': 'Phone number already exists'}
            else:
                return {'success': False, 'error': 'Registration failed'}
        finally:
            conn.close()
    
    def authenticate_operator(self, email, password):
        """Authenticate tow truck operator"""
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, email, phone, password_hash, approval_status
            FROM tow_truck_operators 
            WHERE email = ? AND approval_status = 'APPROVED'
        ''', (email,))
        
        operator = cursor.fetchone()
        conn.close()
        
        if operator and check_password_hash(operator[4], password):
            return {
                'success': True,
                'operator': {
                    'id': operator[0],
                    'name': operator[1],
                    'email': operator[2],
                    'phone': operator[3],
                    'approval_status': operator[5]
                }
            }
        
        return {'success': False, 'error': 'Invalid email or password'}
    
    def get_pending_operators(self):
        """Get all pending tow truck operators"""
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, email, phone, city, experience, truck_type,
                   truck_registration, truck_model, truck_capacity, 
                   approval_status, created_at
            FROM tow_truck_operators 
            WHERE approval_status = 'PENDING'
            ORDER BY created_at DESC
        ''')
        
        operators = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': op[0], 'name': op[1], 'email': op[2], 'phone': op[3],
                'city': op[4], 'experience': op[5], 'truck_type': op[6],
                'truck_registration': op[7], 'truck_model': op[8], 
                'truck_capacity': op[9], 'approval_status': op[10],
                'created_at': op[11]
            }
            for op in operators
        ]
    
    def get_approved_operators(self):
        """Get all approved tow truck operators"""
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, email, phone, city, experience, truck_type,
                   truck_registration, truck_model, truck_capacity, 
                   approval_status, created_at
            FROM tow_truck_operators 
            WHERE approval_status = 'APPROVED'
            ORDER BY created_at DESC
        ''')
        
        operators = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': op[0], 'name': op[1], 'email': op[2], 'phone': op[3],
                'city': op[4], 'experience': op[5], 'truck_type': op[6],
                'truck_registration': op[7], 'truck_model': op[8], 
                'truck_capacity': op[9], 'approval_status': op[10],
                'created_at': op[11]
            }
            for op in operators
        ]
    
    def approve_operator(self, operator_id):
        """Approve a tow truck operator"""
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tow_truck_operators 
            SET approval_status = 'APPROVED', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (operator_id,))
        
        conn.commit()
        changes = cursor.rowcount
        conn.close()
        
        return changes > 0

# Initialize database
tow_truck_db = TowTruckDB()

@tow_truck_bp.route('/register', methods=['POST'])
def register_tow_truck_operator():
    """Register a new tow truck operator"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = [
            'name', 'email', 'phone', 'password', 'city', 'experience',
            'truck_type', 'truck_registration', 'truck_model', 'truck_capacity'
        ]
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Hash password
        data['password_hash'] = generate_password_hash(data['password'])
        del data['password']
        
        # Register operator
        result = tow_truck_db.register_operator(data)
        
        if result['success']:
            # Also create a corresponding unified car service worker entry for admin approval
            car_worker_id = None
            try:
                car_service_db = CarServiceWorkerDB()
                car_worker_id = car_service_db.create_worker(
                    name=data['name'],
                    email=data['email'],
                    phone=data['phone'],
                    password=data['password_hash'],  # Use the same hash
                    role="Tow Truck Operator",
                    age=25,  # default age if not provided
                    city=data['city'],
                    address="Not provided",
                    experience=int(data['experience']) if data['experience'].isdigit() else 0,
                    skills="Towing, Vehicle Recovery, Roadside Assistance",
                    vehicle_number=data['truck_registration'],
                    vehicle_model=data['truck_model'],
                    loading_capacity=data['truck_capacity'],
                    profile_photo=None,
                    aadhaar_path=None,
                    license_path=data.get('license_path'),
                    certificate_path=None,
                    vehicle_rc_path=None,
                    truck_photo_path=None,
                    security_declaration=True
                )
            except Exception as e:
                print(f"⚠️ Could not create unified car service worker record: {e}")
                # Try to get existing worker
                try:
                    car_service_db = CarServiceWorkerDB()
                    existing = car_service_db.get_worker_by_email(data['email'])
                    if existing:
                        car_worker_id = existing.get('id')
                except Exception:
                    pass
            
            return jsonify({
                'success': True,
                'message': 'Registration successful! Please wait for admin approval.',
                'operator_id': result['operator_id'],
                'car_worker_id': car_worker_id
            }), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/status', methods=['PUT'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174'], methods=['PUT'])
def update_operator_status():
    """Update tow truck operator online/offline status"""
    try:
        data = request.get_json()
        operator_id = data.get('operator_id')
        is_online = data.get('is_online')
        
        if not operator_id or is_online is None:
            return jsonify({'success': False, 'error': 'Operator ID and status required'}), 400
        
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tow_truck_operators 
            SET is_online = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (1 if is_online else 0, operator_id))
        
        conn.commit()
        changes = cursor.rowcount
        conn.close()
        
        if changes > 0:
            message = 'Status updated successfully'
            note = 'Your status has been updated. You are now ' + ('online' if is_online else 'offline')
            return jsonify({'success': True, 'message': message, 'note': note}), 200
        else:
            return jsonify({'success': False, 'error': 'Operator not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/active-jobs/<int:operator_id>', methods=['GET', 'OPTIONS'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174'], methods=['GET', 'OPTIONS'])
def get_operator_active_jobs(operator_id):
    if request.method == 'OPTIONS':
        return '', 200
    """Get operator's active jobs count and earnings"""
    try:
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        # Get active jobs count
        cursor.execute('''
            SELECT COUNT(*) as active_jobs
            FROM tow_requests 
            WHERE operator_id = ? AND status IN ('pending', 'accepted', 'in_progress')
        ''', (operator_id,))
        
        active_jobs_result = cursor.fetchone()
        active_jobs = active_jobs_result[0] if active_jobs_result else 0
        
        # Get total earnings from completed jobs
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) as total_earnings
            FROM tow_requests 
            WHERE operator_id = ? AND status = 'completed'
        ''', (operator_id,))
        
        earnings_result = cursor.fetchone()
        total_earnings = earnings_result[0] if earnings_result else 0
        
        # Get completed today jobs
        cursor.execute('''
            SELECT COUNT(*) as completed_today
            FROM tow_requests 
            WHERE operator_id = ? AND status = 'completed' AND DATE(created_at) = DATE('now')
        ''', (operator_id,))
        
        today_result = cursor.fetchone()
        completed_today = today_result[0] if today_result else 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'activeJobs': active_jobs,
            'totalEarnings': total_earnings,
            'completedToday': completed_today
        }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tow_truck_bp.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174'], methods=['POST', 'OPTIONS'])
def login_tow_truck_operator():
    if request.method == 'OPTIONS':
        return '', 200
    """Login tow truck operator"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        result = tow_truck_db.authenticate_operator(email, password)
        
        if result['success']:
            # Generate token (you might want to use JWT here)
            token = f"tow_truck_token_{result['operator']['id']}"
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'token': token,
                'operator': result['operator']
            }), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/status', methods=['PUT'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174'], methods=['PUT'])
def update_operator_status():
    """Update tow truck operator online/offline status"""
    try:
        data = request.get_json()
        operator_id = data.get('operator_id')
        is_online = data.get('is_online')
        
        if not operator_id or is_online is None:
            return jsonify({'success': False, 'error': 'Operator ID and status required'}), 400
        
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tow_truck_operators 
            SET is_online = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (1 if is_online else 0, operator_id))
        
        conn.commit()
        changes = cursor.rowcount
        conn.close()
        
        if changes > 0:
            message = 'Status updated successfully'
            note = 'Your status has been updated. You are now ' + ('online' if is_online else 'offline')
            return jsonify({'success': True, 'message': message, 'note': note}), 200
        else:
            return jsonify({'success': False, 'error': 'Operator not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/active-jobs/<int:operator_id>', methods=['GET', 'OPTIONS'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174'], methods=['GET', 'OPTIONS'])
def get_operator_active_jobs(operator_id):
    if request.method == 'OPTIONS':
        return '', 200
    """Get operator's active jobs count and earnings"""
    try:
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        # Get active jobs count
        cursor.execute('''
            SELECT COUNT(*) as active_jobs
            FROM tow_requests 
            WHERE operator_id = ? AND status IN ('pending', 'accepted', 'in_progress')
        ''', (operator_id,))
        
        active_jobs_result = cursor.fetchone()
        active_jobs = active_jobs_result[0] if active_jobs_result else 0
        
        # Get total earnings from completed jobs
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) as total_earnings
            FROM tow_requests 
            WHERE operator_id = ? AND status = 'completed'
        ''', (operator_id,))
        
        earnings_result = cursor.fetchone()
        total_earnings = earnings_result[0] if earnings_result else 0
        
        # Get completed today jobs
        cursor.execute('''
            SELECT COUNT(*) as completed_today
            FROM tow_requests 
            WHERE operator_id = ? AND status = 'completed' AND DATE(created_at) = DATE('now')
        ''', (operator_id,))
        
        today_result = cursor.fetchone()
        completed_today = today_result[0] if today_result else 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'activeJobs': active_jobs,
            'totalEarnings': total_earnings,
            'completedToday': completed_today
        }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tow_truck_bp.route('/admin/pending', methods=['GET'])
def get_pending_tow_truck_operators():
    """Get all pending tow truck operators for admin"""
    try:
        operators = tow_truck_db.get_pending_operators()
        return jsonify(operators), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/status', methods=['PUT'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174'], methods=['PUT'])
def update_operator_status():
    """Update tow truck operator online/offline status"""
    try:
        data = request.get_json()
        operator_id = data.get('operator_id')
        is_online = data.get('is_online')
        
        if not operator_id or is_online is None:
            return jsonify({'success': False, 'error': 'Operator ID and status required'}), 400
        
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tow_truck_operators 
            SET is_online = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (1 if is_online else 0, operator_id))
        
        conn.commit()
        changes = cursor.rowcount
        conn.close()
        
        if changes > 0:
            message = 'Status updated successfully'
            note = 'Your status has been updated. You are now ' + ('online' if is_online else 'offline')
            return jsonify({'success': True, 'message': message, 'note': note}), 200
        else:
            return jsonify({'success': False, 'error': 'Operator not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/active-jobs/<int:operator_id>', methods=['GET', 'OPTIONS'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174'], methods=['GET', 'OPTIONS'])
def get_operator_active_jobs(operator_id):
    if request.method == 'OPTIONS':
        return '', 200
    """Get operator's active jobs count and earnings"""
    try:
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        # Get active jobs count
        cursor.execute('''
            SELECT COUNT(*) as active_jobs
            FROM tow_requests 
            WHERE operator_id = ? AND status IN ('pending', 'accepted', 'in_progress')
        ''', (operator_id,))
        
        active_jobs_result = cursor.fetchone()
        active_jobs = active_jobs_result[0] if active_jobs_result else 0
        
        # Get total earnings from completed jobs
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) as total_earnings
            FROM tow_requests 
            WHERE operator_id = ? AND status = 'completed'
        ''', (operator_id,))
        
        earnings_result = cursor.fetchone()
        total_earnings = earnings_result[0] if earnings_result else 0
        
        # Get completed today jobs
        cursor.execute('''
            SELECT COUNT(*) as completed_today
            FROM tow_requests 
            WHERE operator_id = ? AND status = 'completed' AND DATE(created_at) = DATE('now')
        ''', (operator_id,))
        
        today_result = cursor.fetchone()
        completed_today = today_result[0] if today_result else 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'activeJobs': active_jobs,
            'totalEarnings': total_earnings,
            'completedToday': completed_today
        }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tow_truck_bp.route('/admin/approved', methods=['GET'])
def get_approved_tow_truck_operators():
    """Get all approved tow truck operators for admin"""
    try:
        operators = tow_truck_db.get_approved_operators()
        return jsonify(operators), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/status', methods=['PUT'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174'], methods=['PUT'])
def update_operator_status():
    """Update tow truck operator online/offline status"""
    try:
        data = request.get_json()
        operator_id = data.get('operator_id')
        is_online = data.get('is_online')
        
        if not operator_id or is_online is None:
            return jsonify({'success': False, 'error': 'Operator ID and status required'}), 400
        
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tow_truck_operators 
            SET is_online = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (1 if is_online else 0, operator_id))
        
        conn.commit()
        changes = cursor.rowcount
        conn.close()
        
        if changes > 0:
            message = 'Status updated successfully'
            note = 'Your status has been updated. You are now ' + ('online' if is_online else 'offline')
            return jsonify({'success': True, 'message': message, 'note': note}), 200
        else:
            return jsonify({'success': False, 'error': 'Operator not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/active-jobs/<int:operator_id>', methods=['GET', 'OPTIONS'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174'], methods=['GET', 'OPTIONS'])
def get_operator_active_jobs(operator_id):
    if request.method == 'OPTIONS':
        return '', 200
    """Get operator's active jobs count and earnings"""
    try:
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        # Get active jobs count
        cursor.execute('''
            SELECT COUNT(*) as active_jobs
            FROM tow_requests 
            WHERE operator_id = ? AND status IN ('pending', 'accepted', 'in_progress')
        ''', (operator_id,))
        
        active_jobs_result = cursor.fetchone()
        active_jobs = active_jobs_result[0] if active_jobs_result else 0
        
        # Get total earnings from completed jobs
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) as total_earnings
            FROM tow_requests 
            WHERE operator_id = ? AND status = 'completed'
        ''', (operator_id,))
        
        earnings_result = cursor.fetchone()
        total_earnings = earnings_result[0] if earnings_result else 0
        
        # Get completed today jobs
        cursor.execute('''
            SELECT COUNT(*) as completed_today
            FROM tow_requests 
            WHERE operator_id = ? AND status = 'completed' AND DATE(created_at) = DATE('now')
        ''', (operator_id,))
        
        today_result = cursor.fetchone()
        completed_today = today_result[0] if today_result else 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'activeJobs': active_jobs,
            'totalEarnings': total_earnings,
            'completedToday': completed_today
        }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tow_truck_bp.route('/admin/approve', methods=['POST'])
def approve_tow_truck_operator():
    """Approve tow truck operator"""
    try:
        data = request.get_json()
        operator_id = data.get('operator_id')
        
        if not operator_id:
            return jsonify({'success': False, 'error': 'Operator ID required'}), 400
        
        if tow_truck_db.approve_operator(operator_id):
            return jsonify({'success': True, 'message': 'Operator approved successfully'}), 200
        else:
            return jsonify({'success': False, 'error': 'Operator not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/status', methods=['PUT'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174'], methods=['PUT'])
def update_operator_status():
    """Update tow truck operator online/offline status"""
    try:
        data = request.get_json()
        operator_id = data.get('operator_id')
        is_online = data.get('is_online')
        
        if not operator_id or is_online is None:
            return jsonify({'success': False, 'error': 'Operator ID and status required'}), 400
        
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tow_truck_operators 
            SET is_online = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (1 if is_online else 0, operator_id))
        
        conn.commit()
        changes = cursor.rowcount
        conn.close()
        
        if changes > 0:
            message = 'Status updated successfully'
            note = 'Your status has been updated. You are now ' + ('online' if is_online else 'offline')
            return jsonify({'success': True, 'message': message, 'note': note}), 200
        else:
            return jsonify({'success': False, 'error': 'Operator not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/active-jobs/<int:operator_id>', methods=['GET', 'OPTIONS'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174'], methods=['GET', 'OPTIONS'])
def get_operator_active_jobs(operator_id):
    if request.method == 'OPTIONS':
        return '', 200
    """Get operator's active jobs count and earnings"""
    try:
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        # Get active jobs count
        cursor.execute('''
            SELECT COUNT(*) as active_jobs
            FROM tow_requests 
            WHERE operator_id = ? AND status IN ('pending', 'accepted', 'in_progress')
        ''', (operator_id,))
        
        active_jobs_result = cursor.fetchone()
        active_jobs = active_jobs_result[0] if active_jobs_result else 0
        
        # Get total earnings from completed jobs
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) as total_earnings
            FROM tow_requests 
            WHERE operator_id = ? AND status = 'completed'
        ''', (operator_id,))
        
        earnings_result = cursor.fetchone()
        total_earnings = earnings_result[0] if earnings_result else 0
        
        # Get completed today jobs
        cursor.execute('''
            SELECT COUNT(*) as completed_today
            FROM tow_requests 
            WHERE operator_id = ? AND status = 'completed' AND DATE(created_at) = DATE('now')
        ''', (operator_id,))
        
        today_result = cursor.fetchone()
        completed_today = today_result[0] if today_result else 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'activeJobs': active_jobs,
            'totalEarnings': total_earnings,
            'completedToday': completed_today
        }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tow_truck_bp.route('/admin/reject', methods=['POST'])
def reject_tow_truck_operator():
    """Reject tow truck operator"""
    try:
        data = request.get_json()
        operator_id = data.get('operator_id')
        
        if not operator_id:
            return jsonify({'success': False, 'error': 'Operator ID required'}), 400
        
        # For now, just delete operator (you could implement a soft delete)
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM tow_truck_operators WHERE id = ?', (operator_id,))
        conn.commit()
        changes = cursor.rowcount
        conn.close()
        
        if changes > 0:
            return jsonify({'success': True, 'message': 'Operator rejected successfully'}), 200
        else:
            return jsonify({'success': False, 'error': 'Operator not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/status', methods=['PUT'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174'], methods=['PUT'])
def update_operator_status():
    """Update tow truck operator online/offline status"""
    try:
        data = request.get_json()
        operator_id = data.get('operator_id')
        is_online = data.get('is_online')
        
        if not operator_id or is_online is None:
            return jsonify({'success': False, 'error': 'Operator ID and status required'}), 400
        
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tow_truck_operators 
            SET is_online = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (1 if is_online else 0, operator_id))
        
        conn.commit()
        changes = cursor.rowcount
        conn.close()
        
        if changes > 0:
            message = 'Status updated successfully'
            note = 'Your status has been updated. You are now ' + ('online' if is_online else 'offline')
            return jsonify({'success': True, 'message': message, 'note': note}), 200
        else:
            return jsonify({'success': False, 'error': 'Operator not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tow_truck_bp.route('/active-jobs/<int:operator_id>', methods=['GET', 'OPTIONS'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:5174', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174'], methods=['GET', 'OPTIONS'])
def get_operator_active_jobs(operator_id):
    if request.method == 'OPTIONS':
        return '', 200
    """Get operator's active jobs count and earnings"""
    try:
        conn = sqlite3.connect(TOW_TRUCK_DB_PATH)
        cursor = conn.cursor()
        
        # Get active jobs count
        cursor.execute('''
            SELECT COUNT(*) as active_jobs
            FROM tow_requests 
            WHERE operator_id = ? AND status IN ('pending', 'accepted', 'in_progress')
        ''', (operator_id,))
        
        active_jobs_result = cursor.fetchone()
        active_jobs = active_jobs_result[0] if active_jobs_result else 0
        
        # Get total earnings from completed jobs
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) as total_earnings
            FROM tow_requests 
            WHERE operator_id = ? AND status = 'completed'
        ''', (operator_id,))
        
        earnings_result = cursor.fetchone()
        total_earnings = earnings_result[0] if earnings_result else 0
        
        # Get completed today jobs
        cursor.execute('''
            SELECT COUNT(*) as completed_today
            FROM tow_requests 
            WHERE operator_id = ? AND status = 'completed' AND DATE(created_at) = DATE('now')
        ''', (operator_id,))
        
        today_result = cursor.fetchone()
        completed_today = today_result[0] if today_result else 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'activeJobs': active_jobs,
            'totalEarnings': total_earnings,
            'completedToday': completed_today
        }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
