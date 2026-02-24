"""
Car Service Worker Authentication Routes
Handles signup, login, and admin approval for Car Service workers
"""

from flask import Blueprint, request, jsonify, send_file
import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth_utils import verify_token
from .worker_db import car_worker_db
from .document_service import document_service

worker_auth_bp = Blueprint("car_worker_auth", __name__)

def get_current_worker():
    """Get current authenticated worker"""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None, ("Authentication required", 401)
    
    token = auth.split(" ")[1]
    username = verify_token(token)
    if not username:
        return None, ("Invalid or expired token", 401)
    
    worker = car_worker_db.get_worker_by_username(username)
    if not worker:
        return None, ("Worker not found", 404)
    
    return worker, None

def is_admin():
    """Check if current user is admin - simplified for CLI"""
    # For CLI admin access, we'll use a simple check
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        token = auth.split(" ")[1]
        # For CLI admin, accept a simple admin token
        return token in ['admin_token', 'admin123', 'admin']
    return False

@worker_auth_bp.route("/api/car/worker/signup", methods=["POST"])
def worker_signup():
    """Worker signup with document upload"""
    try:
        # Get form data
        worker_data = {
            'username': request.form.get('username', '').strip(),
            'email': request.form.get('email', '').strip(),
            'password': request.form.get('password', ''),
            'phone': request.form.get('phone', '').strip(),
            'worker_type': request.form.get('worker_type', '').strip().upper(),
            'city': request.form.get('city', '').strip(),
            'service_area': request.form.get('service_area', '').strip()
        }
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'phone', 'worker_type', 'city', 'service_area']
        for field in required_fields:
            if not worker_data[field]:
                return jsonify({"error": f"{field.replace('_', ' ').title()} is required"}), 400
        
        # Validate worker type
        valid_types = ['MECHANIC', 'FUEL_AGENT', 'TOW_TRUCK', 'EXPERT']
        if worker_data['worker_type'] not in valid_types:
            return jsonify({"error": f"Invalid worker type. Must be one of: {', '.join(valid_types)}"}), 400
        
        # Route TOW_TRUCK to specialized tow truck signup API (skip generic document processing)
        if worker_data['worker_type'] == 'TOW_TRUCK':
            try:
                # Import tow truck auth service
                from ..tow_truck.tow_truck_auth_service import tow_truck_auth_service
                
                # Prepare tow truck specific data
                truck_info = {
                    'truck_type': request.form.get('truck_type', 'FLATBED'),
                    'truck_registration_number': request.form.get('truck_registration_number', ''),
                    'truck_model': request.form.get('truck_model', ''),
                    'truck_capacity': request.form.get('truck_capacity', 'SMALL_CAR'),
                    'insurance_expiry_date': request.form.get('insurance_expiry_date', ''),
                    'fitness_expiry_date': request.form.get('fitness_expiry_date', '')
                }
                
                basic_info = {
                    'full_name': request.form.get('full_name', worker_data['username']),
                    'email': worker_data['email'],
                    'phone_number': worker_data['phone'],
                    'password': worker_data['password'],
                    'city': worker_data['city'],
                    'service_radius_km': request.form.get('service_radius_km', '10')
                }
                
                # Register tow truck driver
                result = tow_truck_auth_service.register_tow_truck_driver(basic_info, truck_info)
                
                if result['success']:
                    return jsonify({
                        "success": True,
                        "message": "Tow truck driver application submitted successfully. Waiting for admin approval.",
                        "driver_id": result['profile_id'],
                        "status": "PENDING_VERIFICATION"
                    }), 201
                else:
                    return jsonify({
                        "error": result.get('error', 'Registration failed')
                    }), 400
                    
            except ImportError:
                return jsonify({"error": "Tow truck service not available"}), 500
            except Exception as e:
                return jsonify({"error": f"Tow truck registration failed: {str(e)}"}), 500
        
        # Process document uploads for other worker types
        files_dict = {}
        worker_requirements = document_service.DOCUMENT_REQUIREMENTS[worker_data['worker_type']]
        
        for doc_type in worker_requirements:
            if doc_type in ['skills', 'specialization', 'years_experience']:
                # Text fields
                files_dict[doc_type] = request.form.get(doc_type, '')
            else:
                # File uploads
                files = request.files.getlist(doc_type)
                if files:
                    files_dict[doc_type] = files[0]  # Take first file
        
        # Process documents
        doc_result = document_service.process_document_upload(files_dict, worker_data['worker_type'], 0)
        
        if not doc_result['success']:
            return jsonify({
                "error": "Document validation failed",
                "details": doc_result['errors']
            }), 400
        
        # Route EXPERT to specialized expert service
        if worker_data['worker_type'] == 'EXPERT':
            try:
                # Import expert service
                from ..ask_expert.expert_service import expert_service
                
                # Prepare expert profile data
                profile_data = {
                    'primary_expertise': request.form.get('primary_expertise', ''),
                    'years_of_experience': request.form.get('years_of_experience', '0'),
                    'work_type': request.form.get('work_type', ''),
                    'consultation_hours': request.form.get('consultation_hours', ''),
                    'languages': request.form.get('languages', '')
                }
                
                basic_info = {
                    'full_name': request.form.get('full_name', worker_data['username']),
                    'username': worker_data['username'],
                    'email': worker_data['email'],
                    'phone_number': worker_data['phone'],
                    'password': worker_data['password'],
                    'city': worker_data['city']
                }
                
                result = expert_service.register_expert(basic_info, profile_data)
                
                if result['success']:
                    return jsonify({
                        "success": True,
                        "message": "Expert application submitted successfully. Waiting for admin approval.",
                        "profile_id": result['profile_id'],
                        "worker_id": result['worker_id']
                    }), 201
                else:
                    return jsonify({
                        "error": result.get('error', 'Registration failed')
                    }), 400
                    
            except ImportError:
                return jsonify({"error": "Expert service not available"}), 500
            except Exception as e:
                return jsonify({"error": f"Expert registration failed: {str(e)}"}), 500
        
        # Create regular worker (MECHANIC, FUEL_AGENT)
        try:
            worker_id = car_worker_db.create_worker(worker_data, doc_result['documents'])
            return jsonify({
                "success": True,
                "message": "Application submitted successfully. Waiting for admin approval.",
                "worker_id": worker_id,
                "status": "PENDING"
            }), 201
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Registration failed. Please try again."}), 500
            
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@worker_auth_bp.route("/api/car/worker/login", methods=["POST"])
def worker_login():
    """Worker login"""
    try:
        data = request.get_json() or {}
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Allow either username or email
        identifier = username or email
        
        if not identifier or not password:
            return jsonify({"error": "Username/Email and password are required"}), 400
        
        # Authenticate worker
        worker = car_worker_db.authenticate_worker(identifier, password)
        
        if not worker:
            return jsonify({"error": "Invalid credentials or application not approved"}), 401
        
        # Generate JWT token (reuse existing auth_utils)
        from auth_utils import generate_token
        token = generate_token(worker['username'])
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "token": token,
            "worker": {
                "id": worker['id'],
                "username": worker['username'],
                "email": worker['email'],
                "worker_type": worker['worker_type'],
                "city": worker['city'],
                "service_area": worker['service_area'],
                "status": worker['status']
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

@worker_auth_bp.route("/api/car/worker/profile", methods=["GET"])
def worker_profile():
    """Get worker profile"""
    worker, err = get_current_worker()
    if err:
        return jsonify({"error": err[0]}), err[1]
    
    # Get documents
    documents = document_service.get_worker_documents(worker['id'], worker['worker_type'])
    
    return jsonify({
        "success": True,
        "worker": {
            "id": worker['id'],
            "username": worker['username'],
            "email": worker['email'],
            "phone": worker['phone'],
            "worker_type": worker['worker_type'],
            "city": worker['city'],
            "service_area": worker['service_area'],
            "status": worker['status'],
            "created_at": worker['created_at'],
            "approved_at": worker['approved_at']
        },
        "documents": documents
    }), 200

@worker_auth_bp.route("/api/car/worker/profile", methods=["PUT"])
def update_worker_profile():
    """Update worker profile"""
    worker, err = get_current_worker()
    if err:
        return jsonify({"error": err[0]}), err[1]
    
    try:
        updates = {}
        
        # Get updatable fields
        if 'phone' in request.json:
            updates['phone'] = request.json['phone']
        if 'city' in request.json:
            updates['city'] = request.json['city']
        if 'service_area' in request.json:
            updates['service_area'] = request.json['service_area']
        
        if not updates:
            return jsonify({"error": "No valid fields to update"}), 400
        
        success = car_worker_db.update_worker_profile(worker['id'], updates)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Profile updated successfully"
            }), 200
        else:
            return jsonify({"error": "Update failed"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Update failed: {str(e)}"}), 500

# Admin endpoints
@worker_auth_bp.route("/api/car/admin/workers/pending", methods=["GET"])
def admin_pending_workers():
    """Get all pending workers for admin review"""
    if not is_admin():
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        pending_workers = car_worker_db.get_pending_workers()
        
        # Add document info for each worker
        for worker in pending_workers:
            documents = json.loads(worker.get('documents_json', '{}'))
            worker['documents'] = documents
            worker['document_count'] = len(documents)
        
        return jsonify({
            "success": True,
            "workers": pending_workers,
            "total": len(pending_workers)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get pending workers: {str(e)}"}), 500

@worker_auth_bp.route("/api/car/admin/worker/<int:worker_id>/approve", methods=["PUT"])
def admin_approve_worker(worker_id):
    """Approve worker application"""
    if not is_admin():
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        success = car_worker_db.approve_worker(worker_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Worker {worker_id} approved successfully"
            }), 200
        else:
            return jsonify({"error": "Worker not found"}), 404
            
    except Exception as e:
        return jsonify({"error": f"Approval failed: {str(e)}"}), 500

@worker_auth_bp.route("/api/car/admin/worker/<int:worker_id>/reject", methods=["PUT"])
def admin_reject_worker(worker_id):
    """Reject worker application"""
    if not is_admin():
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        success = car_worker_db.reject_worker(worker_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Worker {worker_id} rejected"
            }), 200
        else:
            return jsonify({"error": "Worker not found"}), 404
            
    except Exception as e:
        return jsonify({"error": f"Rejection failed: {str(e)}"}), 500

@worker_auth_bp.route("/api/car/admin/worker/<int:worker_id>/documents", methods=["GET"])
def admin_view_documents(worker_id):
    """View worker documents"""
    if not is_admin():
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        worker = car_worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        documents = document_service.get_worker_documents(worker_id, worker['worker_type'])
        
        return jsonify({
            "success": True,
            "worker": {
                "id": worker['id'],
                "username": worker['username'],
                "worker_type": worker['worker_type'],
                "status": worker['status']
            },
            "documents": documents
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get documents: {str(e)}"}), 500

@worker_auth_bp.route("/api/car/admin/worker/<int:worker_id>/document/<doc_type>", methods=["GET"])
def admin_view_document(worker_id, doc_type):
    """View specific worker document"""
    if not is_admin():
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        worker = car_worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        doc_info = document_service.get_document_info(worker_id, worker['worker_type'], doc_type)
        
        if 'error' in doc_info:
            return jsonify({"error": doc_info['error']}), 404
        
        # Serve file
        return send_file(doc_info['path'])
        
    except Exception as e:
        return jsonify({"error": f"Failed to serve document: {str(e)}"}), 500

@worker_auth_bp.route("/api/car/admin/statistics", methods=["GET"])
def admin_statistics():
    """Get worker statistics"""
    if not is_admin():
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        stats = car_worker_db.get_worker_statistics()
        return jsonify({
            "success": True,
            "statistics": stats
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get statistics: {str(e)}"}), 500

@worker_auth_bp.route("/api/car/worker/types", methods=["GET"])
def get_worker_types():
    """Get available worker types and their document requirements"""
    try:
        return jsonify({
            "success": True,
            "worker_types": {
                "MECHANIC": {
                    "name": "Mechanic",
                    "description": "Field mechanic for vehicle repairs",
                    "documents": list(document_service.DOCUMENT_REQUIREMENTS['MECHANIC'].keys())
                },
                "FUEL_AGENT": {
                    "name": "Fuel Delivery Agent",
                    "description": "Fuel delivery service provider",
                    "documents": list(document_service.DOCUMENT_REQUIREMENTS['FUEL_AGENT'].keys())
                },
                "EXPERT": {
                    "name": "Automobile Expert",
                    "description": "Remote consultation expert",
                    "documents": list(document_service.DOCUMENT_REQUIREMENTS['EXPERT'].keys())
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to get worker types: " + str(e)}), 500
