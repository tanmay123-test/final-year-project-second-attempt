"""
Automobile Expert API Routes
Handles authentication and profile management for automobile experts
"""

import os
import bcrypt
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from .automobile_expert_db import automobile_expert_db

automobile_expert_bp = Blueprint('automobile_expert', __name__, url_prefix='/api/automobile-expert')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@automobile_expert_bp.route('/signup', methods=['POST'])
def signup():
    """Automobile expert signup"""
    try:
        # Check if JSON data or form data
        if request.is_json:
            # JSON data from frontend
            data = request.get_json()
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            phone = data.get('phone', '').strip()
            password = data.get('password', '').strip()
            experience_years = data.get('experience_years', '').strip()
            area_of_expertise = data.get('area_of_expertise', '').strip()
            worker_type = data.get('worker_type', '').strip()
            certificate_path = data.get('certificate_path', '')
        else:
            # Form data from CLI
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            password = request.form.get('password', '').strip()
            experience_years = request.form.get('experience_years', '').strip()
            area_of_expertise = request.form.get('area_of_expertise', '').strip()
            worker_type = request.form.get('worker_type', '').strip()
            
            # Handle file uploads for form data
            certificate_path = None
            if 'certificate' in request.files:
                certificate = request.files['certificate']
                if certificate and certificate.filename and allowed_file(certificate.filename):
                    certificate_path = secure_filename(certificate.filename)
                    certificate.save(certificate_path)
        
        # Validation
        if not all([name, email, phone, password, experience_years, area_of_expertise]):
            return jsonify({'error': 'All required fields must be filled'}), 400
        
        if worker_type != 'automobile_expert':
            return jsonify({'error': 'Invalid worker type'}), 400
        
        # Check if email already exists
        if automobile_expert_db.get_expert_by_email(email):
            return jsonify({'error': 'Email already registered'}), 400
        
        if 'profile_photo' in request.files:
            profile_photo = request.files['profile_photo']
            if profile_photo and profile_photo.filename and allowed_file(profile_photo.filename):
                filename = secure_filename(profile_photo.filename)
                upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'automobile_experts')
                os.makedirs(upload_dir, exist_ok=True)
                
                profile_photo_path = os.path.join(upload_dir, f"photo_{email}_{filename}")
                profile_photo.save(profile_photo_path)
        
        # Create expert
        try:
            experience_years_int = int(experience_years)
            worker_id = automobile_expert_db.create_expert(
                name=name,
                phone=phone,
                email=email,
                password=password,
                area_of_expertise=area_of_expertise,
                experience_years=experience_years_int,
                certificate_path=certificate_path,
                profile_photo_path=profile_photo_path if 'profile_photo_path' in locals() else None
            )
            
            return jsonify({
                'success': True,
                'message': 'Expert account created successfully',
                'worker_id': worker_id,
                'status': 'PENDING'
            }), 201
            
        except ValueError:
            return jsonify({'error': 'Experience must be a valid number'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Signup failed: {str(e)}'}), 500

@automobile_expert_bp.route('/login', methods=['POST'])
def login():
    """Automobile expert login"""
    try:
        data = request.get_json() or {}
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Verify credentials
        expert = automobile_expert_db.verify_password(email, password)
        
        if not expert:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if expert['status'] != 'APPROVED':
            return jsonify({'error': f'Account is {expert["status"].lower()}. Please wait for admin approval.'}), 403
        
        # Generate token (simple implementation - in production, use JWT)
        import hashlib
        import time
        token = hashlib.sha256(f"{expert['id']}_{expert['email']}_{time.time()}".encode()).hexdigest()
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'worker_id': expert['id'],
            'name': expert['name'],
            'email': expert['email'],
            'area_of_expertise': expert['area_of_expertise'],
            'experience_years': expert['experience_years'],
            'status': expert['status'],
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@automobile_expert_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get expert profile"""
    try:
        expert_id = request.args.get('expert_id')
        if not expert_id:
            return jsonify({'error': 'Expert ID is required'}), 400
        
        expert = automobile_expert_db.get_expert_by_id(int(expert_id))
        if not expert:
            return jsonify({'error': 'Expert not found'}), 404
        
        # Remove sensitive data
        expert_data = {
            'id': expert['id'],
            'name': expert['name'],
            'email': expert['email'],
            'phone': expert['phone'],
            'area_of_expertise': expert['area_of_expertise'],
            'experience_years': expert['experience_years'],
            'status': expert['status'],
            'created_at': expert['created_at']
        }
        
        return jsonify({'success': True, 'expert': expert_data}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@automobile_expert_bp.route('/update-profile', methods=['PUT'])
def update_profile():
    """Update expert profile"""
    try:
        expert_id = request.form.get('expert_id')
        if not expert_id:
            return jsonify({'error': 'Expert ID is required'}), 400
        
        expert = automobile_expert_db.get_expert_by_id(int(expert_id))
        if not expert:
            return jsonify({'error': 'Expert not found'}), 404
        
        # Get updateable fields
        update_data = {}
        for field in ['name', 'phone', 'area_of_expertise', 'experience_years']:
            value = request.form.get(field)
            if value:
                if field == 'experience_years':
                    try:
                        update_data[field] = int(value)
                    except ValueError:
                        return jsonify({'error': 'Experience must be a valid number'}), 400
                else:
                    update_data[field] = value.strip()
        
        # Handle file uploads for form data only (CLI)
        if not request.is_json:
            certificate_path = None
            profile_photo_path = None
            
            if 'certificate' in request.files:
                certificate = request.files['certificate']
                if certificate and certificate.filename and allowed_file(certificate.filename):
                    filename = secure_filename(certificate.filename)
                    upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'automobile_experts')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    certificate_path = os.path.join(upload_dir, f"cert_{expert['email']}_{filename}")
                    certificate.save(certificate_path)
                    certificate_path = os.path.join('uploads', 'automobile_experts', f"cert_{expert['email']}_{filename}")
            
            if 'profile_photo' in request.files:
                profile_photo = request.files['profile_photo']
                if profile_photo and profile_photo.filename and allowed_file(profile_photo.filename):
                    filename = secure_filename(profile_photo.filename)
                    upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'automobile_experts')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    profile_photo_path = os.path.join(upload_dir, f"photo_{expert['email']}_{filename}")
                    profile_photo.save(profile_photo_path)
                    profile_photo_path = os.path.join('uploads', 'automobile_experts', f"photo_{expert['email']}_{filename}")
        
        success = automobile_expert_db.update_expert_profile(int(expert_id), **update_data)
        
        if success:
            return jsonify({'success': True, 'message': 'Profile updated successfully'}), 200
        else:
            return jsonify({'error': 'No updates made'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Profile update failed: {str(e)}'}), 500

@automobile_expert_bp.route('/experts', methods=['GET'])
def list_experts():
    """List all experts (for admin)"""
    try:
        status = request.args.get('status', '').strip()
        
        if status:
            experts = automobile_expert_db.get_experts_by_status(status)
        else:
            experts = automobile_expert_db.get_all_experts()
        
        # Remove sensitive data
        experts_data = []
        for expert in experts:
            expert_data = {
                'id': expert['id'],
                'name': expert['name'],
                'email': expert['email'],
                'phone': expert['phone'],
                'area_of_expertise': expert['area_of_expertise'],
                'experience_years': expert['experience_years'],
                'status': expert['status'],
                'created_at': expert['created_at']
            }
            experts_data.append(expert_data)
        
        return jsonify({'success': True, 'experts': experts_data}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to list experts: {str(e)}'}), 500

@automobile_expert_bp.route('/update-status', methods=['PUT'])
def update_status():
    """Update expert status (for admin)"""
    try:
        expert_id = request.json.get('expert_id')
        status = request.json.get('status', '').strip()
        
        if not expert_id or not status:
            return jsonify({'error': 'Expert ID and status are required'}), 400
        
        valid_statuses = ['PENDING', 'APPROVED', 'REJECTED', 'SUSPENDED']
        if status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        success = automobile_expert_db.update_expert_status(int(expert_id), status)
        
        if success:
            return jsonify({'success': True, 'message': f'Expert status updated to {status}'}), 200
        else:
            return jsonify({'error': 'Expert not found or no update made'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Status update failed: {str(e)}'}), 500

@automobile_expert_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get expert statistics"""
    try:
        stats = automobile_expert_db.get_expert_stats()
        return jsonify({'success': True, 'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500
