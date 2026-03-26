from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
from datetime import datetime, timedelta
import os
from worker_db import WorkerDB

doctor_bp = Blueprint('doctor', __name__)

# Initialize database
worker_db = WorkerDB()

# JWT Secret
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key')

def generate_token(email, doctor_id):
    """Generate JWT token for doctor"""
    payload = {
        'doctor_id': doctor_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode token
            data = jwt.decode(token, os.environ.get('JWT_SECRET', 'your-secret-key'), algorithms=['HS256'])
            current_doctor_id = data['doctor_id']
            
            # Verify doctor exists
            doctor = worker_db.get_worker_by_id(current_doctor_id)
            if not doctor or doctor.get('service_type') != 'healthcare':
                return jsonify({'error': 'Invalid token or doctor not found'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_doctor_id, *args, **kwargs)
    
    return decorated

@doctor_bp.route('/doctor/login', methods=['POST'])
def doctor_login():
    """Doctor login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Verify doctor login
        doctor_data = worker_db.verify_worker_login(email, password)
        if not doctor_data:
            return jsonify({'error': 'Invalid email or password'}), 404

        doctor_id, status, service, specialization, name = doctor_data

        # Check if this is a healthcare worker
        if service != 'healthcare':
            return jsonify({'error': 'Not a healthcare provider'}), 403

        # Auto-approve healthcare workers (consistent with main login)
        if status != 'approved':
            status = 'approved'

        # Generate token
        token = generate_token(email, doctor_id)

        return jsonify({
            'token': token,
            'doctor_id': doctor_id,
            'service': service,
            'specialization': specialization,
            'name': name,
            'status': status
        }), 200

    except Exception as e:
        return jsonify({'error': f'Login error: {str(e)}'}), 500

@doctor_bp.route('/doctor/profile', methods=['GET'])
@token_required
def get_doctor_profile(current_doctor_id):
    """Get doctor profile information"""
    try:
        doctor = worker_db.get_worker_by_id(current_doctor_id)
        
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
        
        return jsonify({
            'id': doctor['id'],
            'name': doctor['full_name'],
            'email': doctor['email'],
            'specialization': doctor['specialization'],
            'experience': doctor['experience'],
            'clinic_location': doctor['clinic_location'],
            'is_online': doctor.get('is_online', False),
            'status': doctor.get('status', 'approved'),
            'phone': doctor.get('phone', ''),
            'license_number': doctor.get('license_number', '')
        })
        
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@doctor_bp.route('/doctor/dashboard-stats', methods=['GET'])
@token_required
def get_dashboard_stats(current_doctor_id):
    """Get dashboard statistics for the doctor"""
    try:
        # Mock data for now - in production, calculate from actual appointments
        stats = {
            'todays_patients': 8,
            'pending_requests': 3,
            'this_week': 24,
            'revenue': 12500
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': f'Error fetching stats: {str(e)}'}), 500

@doctor_bp.route('/doctor/todays-schedule', methods=['GET'])
@token_required
def get_todays_schedule(current_doctor_id):
    """Get today's appointments for the doctor"""
    try:
        # Mock data for now - in production, fetch from appointments table
        appointments = [
            {
                'id': 1,
                'patient_name': 'Sarah Johnson',
                'type': 'video',
                'reason': 'Regular checkup',
                'time': '09:00 AM',
                'status': 'upcoming'
            },
            {
                'id': 2,
                'patient_name': 'Michael Chen',
                'type': 'in_person',
                'reason': 'Follow-up consultation',
                'time': '10:30 AM',
                'status': 'upcoming'
            },
            {
                'id': 3,
                'patient_name': 'Emma Williams',
                'type': 'video',
                'reason': 'Initial consultation',
                'time': '02:00 PM',
                'status': 'upcoming'
            },
            {
                'id': 4,
                'patient_name': 'James Davis',
                'type': 'in_person',
                'reason': 'Medical certificate',
                'time': '03:30 PM',
                'status': 'completed'
            }
        ]
        
        return jsonify(appointments)
        
    except Exception as e:
        return jsonify({'error': f'Error fetching schedule: {str(e)}'}), 500

@doctor_bp.route('/doctor/toggle-online', methods=['POST'])
@token_required
def toggle_online_status(current_doctor_id):
    """Toggle doctor's online status"""
    try:
        data = request.get_json()
        is_online = data.get('is_online', False)
        
        # Update doctor's online status in database
        # For now, just return success - in production, update the database
        # worker_db.update_doctor_online_status(current_doctor_id, is_online)
        
        return jsonify({
            'success': True,
            'is_online': is_online,
            'message': f"Status updated to {'online' if is_online else 'offline'}"
        })
        
    except Exception as e:
        return jsonify({'error': f'Error updating status: {str(e)}'}), 500

@doctor_bp.route('/doctor/appointments', methods=['GET'])
@token_required
def get_all_appointments(current_doctor_id):
    """Get all appointments for the doctor"""
    try:
        # Mock data for now
        appointments = [
            {
                'id': 1,
                'patient_name': 'Sarah Johnson',
                'type': 'video',
                'reason': 'Regular checkup',
                'time': '09:00 AM',
                'date': '2024-03-26',
                'status': 'upcoming'
            },
            {
                'id': 2,
                'patient_name': 'Michael Chen',
                'type': 'in_person',
                'reason': 'Follow-up consultation',
                'time': '10:30 AM',
                'date': '2024-03-26',
                'status': 'upcoming'
            },
            {
                'id': 5,
                'patient_name': 'Lisa Anderson',
                'type': 'video',
                'reason': 'Urgent consultation',
                'time': '11:00 AM',
                'date': '2024-03-27',
                'status': 'pending'
            }
        ]
        
        return jsonify(appointments)
        
    except Exception as e:
        return jsonify({'error': f'Error fetching appointments: {str(e)}'}), 500

@doctor_bp.route('/doctor/requests', methods=['GET'])
@token_required
def get_pending_requests(current_doctor_id):
    """Get pending appointment requests"""
    try:
        # Mock data for now
        requests = [
            {
                'id': 101,
                'patient_name': 'Robert Brown',
                'type': 'video',
                'reason': 'Initial consultation',
                'requested_time': '04:00 PM',
                'requested_date': '2024-03-26',
                'status': 'pending'
            },
            {
                'id': 102,
                'patient_name': 'Jennifer Martinez',
                'type': 'in_person',
                'reason': 'Second opinion',
                'requested_time': '05:30 PM',
                'requested_date': '2024-03-27',
                'status': 'pending'
            }
        ]
        
        return jsonify(requests)
        
    except Exception as e:
        return jsonify({'error': f'Error fetching requests: {str(e)}'}), 500

@doctor_bp.route('/doctor/availability', methods=['GET'])
@token_required
def get_availability(current_doctor_id):
    """Get doctor's availability settings"""
    try:
        # Mock data for now
        availability = {
            'working_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            'working_hours': {
                'start': '09:00',
                'end': '17:00'
            },
            'break_hours': {
                'start': '13:00',
                'end': '14:00'
            },
            'appointment_duration': 30, # minutes
            'max_patients_per_day': 20
        }
        
        return jsonify(availability)
        
    except Exception as e:
        return jsonify({'error': f'Error fetching availability: {str(e)}'}), 500
