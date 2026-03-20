"""
Truck Operator Routes
API endpoints for truck operator registration, login, and management
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from truck_operator_db import truck_operator_db
from auth_utils import generate_token

# Create blueprint
truck_operator_bp = Blueprint('truck_operator', __name__)

# Upload directories
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'truck_operators')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@truck_operator_bp.route('/api/truck-operator/signup', methods=['POST'])
def truck_operator_signup():
    """Register a new truck operator"""
    try:
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        city_name = request.form.get('city_name')
        vehicle_type = request.form.get('vehicle_type')
        vehicle_number = request.form.get('vehicle_number')
        
        # Validation
        if not all([name, email, phone, password, city_name, vehicle_type, vehicle_number]):
            return jsonify({'error': 'All required fields must be filled'}), 400
        
        # Check if email already exists
        if truck_operator_db.get_operator_by_email(email):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Check if phone already exists
        existing_operator = truck_operator_db.get_operators_by_status('ALL')
        for operator in existing_operator:
            if operator.get('phone') == phone:
                return jsonify({'error': 'Phone number already registered'}), 400
        
        # Handle file uploads
        vehicle_photo_path = None
        rc_book_path = None
        petrol_pump_auth_path = None
        
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Handle vehicle photo
        if 'vehicle_photo' in request.files:
            vehicle_photo = request.files['vehicle_photo']
            if vehicle_photo and allowed_file(vehicle_photo.filename):
                filename = secure_filename(f"vehicle_{email}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{vehicle_photo.filename.rsplit('.', 1)[1].lower()}")
                vehicle_photo_path = os.path.join(UPLOAD_FOLDER, filename)
                vehicle_photo.save(vehicle_photo_path)
        
        # Handle RC book
        if 'rc_book' in request.files:
            rc_book = request.files['rc_book']
            if rc_book and allowed_file(rc_book.filename):
                filename = secure_filename(f"rcbook_{email}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{rc_book.filename.rsplit('.', 1)[1].lower()}")
                rc_book_path = os.path.join(UPLOAD_FOLDER, filename)
                rc_book.save(rc_book_path)
        
        # Handle petrol pump authorization letter
        if 'petrol_pump_auth' in request.files:
            petrol_pump_auth = request.files['petrol_pump_auth']
            if petrol_pump_auth and allowed_file(petrol_pump_auth.filename):
                filename = secure_filename(f"auth_{email}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{petrol_pump_auth.filename.rsplit('.', 1)[1].lower()}")
                petrol_pump_auth_path = os.path.join(UPLOAD_FOLDER, filename)
                petrol_pump_auth.save(petrol_pump_auth_path)
        
        # Create operator
        operator_id = truck_operator_db.create_operator(
            name=name,
            phone=phone,
            email=email,
            password=password,
            city_name=city_name,
            vehicle_type=vehicle_type,
            vehicle_number=vehicle_number,
            vehicle_photo_path=vehicle_photo_path,
            rc_book_photo_path=rc_book_path,
            petrol_pump_auth_letter_path=petrol_pump_auth_path
        )
        
        return jsonify({
            'message': 'Truck operator registered successfully',
            'worker_id': operator_id,
            'status': 'PENDING'
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@truck_operator_bp.route('/api/truck-operator/login', methods=['POST'])
def truck_operator_login():
    """Login truck operator"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Verify credentials
        operator = truck_operator_db.verify_password(email, password)
        
        if not operator:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if operator is approved
        if operator['status'] != 'APPROVED':
            return jsonify({'error': 'Account not approved. Please wait for admin approval.'}), 403
        
        # Generate token
        token = generate_token(operator['id'], 'truck_operator')
        
        return jsonify({
            'message': 'Login successful',
            'worker_id': operator['id'],
            'name': operator['name'],
            'email': operator['email'],
            'vehicle_type': operator['vehicle_type'],
            'vehicle_number': operator['vehicle_number'],
            'city_name': operator['city_name'],
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@truck_operator_bp.route('/api/truck-operator/profile/<int:operator_id>', methods=['GET'])
def get_operator_profile(operator_id):
    """Get operator profile"""
    try:
        operator = truck_operator_db.get_operator_by_id(operator_id)
        
        if not operator:
            return jsonify({'error': 'Operator not found'}), 404
        
        # Remove sensitive information
        operator_data = {
            'id': operator['id'],
            'name': operator['name'],
            'email': operator['email'],
            'phone': operator['phone'],
            'city_name': operator['city_name'],
            'vehicle_type': operator['vehicle_type'],
            'vehicle_number': operator['vehicle_number'],
            'status': operator['status'],
            'created_at': operator['created_at']
        }
        
        return jsonify(operator_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@truck_operator_bp.route('/api/truck-operator/applications/<int:operator_id>', methods=['GET'])
def get_available_applications(operator_id):
    """Get available applications for truck operator"""
    try:
        # This is a placeholder - in a real implementation, this would query
        # a jobs/applications database for available jobs matching the operator's criteria
        applications = [
            {
                'application_id': 'APP001',
                'pickup_location': 'Mumbai',
                'dropoff_location': 'Pune',
                'cargo_type': 'Electronics',
                'payment_amount': 5000,
                'pickup_date': '2024-01-15',
                'priority_level': 2
            },
            {
                'application_id': 'APP002',
                'pickup_location': 'Delhi',
                'dropoff_location': 'Jaipur',
                'cargo_type': 'Textiles',
                'payment_amount': 3500,
                'pickup_date': '2024-01-16',
                'priority_level': 1
            }
        ]
        
        return jsonify({'applications': applications}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get applications: {str(e)}'}), 500

@truck_operator_bp.route('/api/truck-operator/applications/<string:application_id>/accept', methods=['POST'])
def accept_application(application_id):
    """Accept an application"""
    try:
        data = request.get_json()
        operator_id = data.get('operator_id')
        
        if not operator_id:
            return jsonify({'error': 'Operator ID is required'}), 400
        
        # This is a placeholder - in a real implementation, this would
        # update the application status and create a job assignment
        
        return jsonify({'message': 'Application accepted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to accept application: {str(e)}'}), 500

@truck_operator_bp.route('/api/truck-operator/active-jobs/<int:operator_id>', methods=['GET'])
def get_active_jobs(operator_id):
    """Get active jobs for truck operator"""
    try:
        # This is a placeholder - in a real implementation, this would query
        # the jobs database for active jobs assigned to this operator
        active_jobs = [
            {
                'job_id': 'JOB001',
                'pickup_location': 'Mumbai',
                'dropoff_location': 'Pune',
                'cargo_type': 'Electronics',
                'started_at': '2024-01-15 10:00:00',
                'status': 'IN_TRANSIT'
            }
        ]
        
        return jsonify({'active_jobs': active_jobs}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get active jobs: {str(e)}'}), 500

@truck_operator_bp.route('/api/truck-operator/job-history/<int:operator_id>', methods=['GET'])
def get_job_history(operator_id):
    """Get job history for truck operator"""
    try:
        # This is a placeholder - in a real implementation, this would query
        # the jobs database for completed jobs
        jobs = [
            {
                'job_id': 'JOB001',
                'pickup_location': 'Mumbai',
                'dropoff_location': 'Pune',
                'cargo_type': 'Electronics',
                'completed_date': '2024-01-15',
                'earnings': 5000,
                'status': 'COMPLETED'
            }
        ]
        
        return jsonify({'success': True, 'jobs': jobs}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get job history: {str(e)}'}), 500

@truck_operator_bp.route('/api/truck-operator/earnings/<int:operator_id>', methods=['GET'])
def get_earnings(operator_id):
    """Get earnings summary for truck operator"""
    try:
        # This is a placeholder - in a real implementation, this would calculate
        # actual earnings from the jobs database
        earnings = {
            'total_earnings': 50000,
            'jobs_completed': 15,
            'average_per_job': 3333.33,
            'this_month': 15000,
            'last_month': 12000
        }
        
        return jsonify({'success': True, **earnings}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get earnings: {str(e)}'}), 500

@truck_operator_bp.route('/api/truck-operator/analytics/<int:operator_id>', methods=['GET'])
def get_analytics(operator_id):
    """Get performance analytics for truck operator"""
    try:
        # This is a placeholder - in a real implementation, this would calculate
        # actual analytics from the jobs database
        analytics = {
            'total_jobs': 20,
            'completed_jobs': 18,
            'completion_rate': 90,
            'average_rating': 4.5,
            'avg_delivery_time': 4.5
        }
        
        return jsonify({'success': True, **analytics}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to get analytics: {str(e)}'}), 500

@truck_operator_bp.route('/api/truck-operator/performance/<int:operator_id>', methods=['GET'])
def get_performance(operator_id):
    """Get performance data for truck operator"""
    try:
        # This is a placeholder - in a real implementation, this would calculate
        # actual performance metrics
        performance = {
            'total_jobs': 20,
            'rating': 4.5,
            'total_earnings': 50000
        }
        
        return jsonify(performance), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get performance data: {str(e)}'}), 500

# Admin routes for managing truck operators
@truck_operator_bp.route('/api/admin/truck-operators', methods=['GET'])
def admin_get_all_operators():
    """Get all truck operators (admin only)"""
    try:
        operators = truck_operator_db.get_all_operators()
        
        # Remove sensitive information
        operators_data = []
        for operator in operators:
            operators_data.append({
                'id': operator['id'],
                'name': operator['name'],
                'email': operator['email'],
                'phone': operator['phone'],
                'city_name': operator['city_name'],
                'vehicle_type': operator['vehicle_type'],
                'vehicle_number': operator['vehicle_number'],
                'status': operator['status'],
                'created_at': operator['created_at']
            })
        
        return jsonify({'operators': operators_data}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get operators: {str(e)}'}), 500

@truck_operator_bp.route('/api/admin/truck-operators/<int:operator_id>/status', methods=['PUT'])
def admin_update_operator_status(operator_id):
    """Update operator status (admin only)"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({'error': 'Status is required'}), 400
        
        if status not in ['PENDING', 'APPROVED', 'REJECTED']:
            return jsonify({'error': 'Invalid status'}), 400
        
        success = truck_operator_db.update_operator_status(operator_id, status)
        
        if success:
            return jsonify({'message': f'Operator status updated to {status}'}), 200
        else:
            return jsonify({'error': 'Operator not found'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Failed to update status: {str(e)}'}), 500
