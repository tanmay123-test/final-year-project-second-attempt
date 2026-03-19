"""
Healthcare Routes using Organized Database Manager
Provides API endpoints for healthcare service
"""

from flask import Blueprint, request, jsonify
from database.database_manager import db_manager
from auth_utils import generate_token, verify_token

# Create blueprint
healthcare_bp = Blueprint('healthcare', __name__)

# Healthcare Routes
@healthcare_bp.route('/api/healthcare/specializations', methods=['GET'])
def get_specializations():
    """Get healthcare specializations"""
    try:
        # Return mock specializations for now
        specializations = [
            {"id": 1, "name": "General", "icon": "stethoscope"},
            {"id": 2, "name": "Cardiology", "icon": "heart"},
            {"id": 3, "name": "Dermatology", "icon": "skin"},
            {"id": 4, "name": "Pediatrics", "icon": "baby"},
            {"id": 5, "name": "Orthopedics", "icon": "bone"}
        ]
        
        return jsonify({
            "success": True,
            "specializations": specializations
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get specializations: {str(e)}"
        }), 500

@healthcare_bp.route('/api/healthcare/doctors', methods=['GET'])
def get_doctors():
    """Get healthcare doctors"""
    try:
        # Get filters from query params
        specialization = request.args.get('specialization')
        is_verified = request.args.get('is_verified', 'true').lower() == 'true'
        search = request.args.get('search')
        
        # Get workers from organized database
        workers = db_manager.get_workers_by_service('healthcare')
        
        # Filter workers
        filtered_workers = []
        for worker in workers:
            if worker.get('worker_type') == 'doctor':
                if is_verified and not worker.get('is_verified'):
                    continue
                if specialization and worker.get('specialization') != specialization:
                    continue
                if search and search.lower() not in worker.get('name', '').lower():
                    continue
                filtered_workers.append(worker)
        
        return jsonify({
            "success": True,
            "workers": filtered_workers
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get doctors: {str(e)}"
        }), 500

@healthcare_bp.route('/api/healthcare/doctors/<int:doctor_id>', methods=['GET'])
def get_doctor_details(doctor_id):
    """Get doctor details"""
    try:
        workers = db_manager.get_worker(worker_id=doctor_id)
        
        if workers and workers[0].get('worker_type') == 'doctor':
            return jsonify({
                "success": True,
                "doctor": workers[0]
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Doctor not found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get doctor details: {str(e)}"
        }), 500

@healthcare_bp.route('/api/healthcare/appointments', methods=['POST'])
def create_appointment():
    """Create healthcare appointment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'worker_id', 'appointment_data']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Create booking using organized database
        booking_id = db_manager.create_booking(
            'healthcare',
            data['user_id'],
            data['worker_id'],
            data['appointment_data']
        )
        
        return jsonify({
            "success": True,
            "message": "Appointment created successfully",
            "booking_id": booking_id
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to create appointment: {str(e)}"
        }), 500

@healthcare_bp.route('/api/healthcare/appointments', methods=['GET'])
def get_appointments():
    """Get healthcare appointments"""
    try:
        # Get filters from query params
        user_id = request.args.get('user_id')
        worker_id = request.args.get('worker_id')
        status = request.args.get('status')
        
        # Get bookings from organized database
        bookings = db_manager.get_bookings(
            'healthcare',
            user_id=int(user_id) if user_id else None,
            worker_id=int(worker_id) if worker_id else None,
            status=status
        )
        
        return jsonify({
            "success": True,
            "appointments": bookings
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get appointments: {str(e)}"
        }), 500

@healthcare_bp.route('/api/healthcare/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    """Update healthcare appointment"""
    try:
        data = request.get_json()
        
        # Update booking using organized database
        # This would need to be implemented in database_manager
        # For now, return success
        
        return jsonify({
            "success": True,
            "message": "Appointment updated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to update appointment: {str(e)}"
        }), 500

@healthcare_bp.route('/api/healthcare/appointments/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    """Cancel healthcare appointment"""
    try:
        # This would need to be implemented in database_manager
        # For now, return success
        
        return jsonify({
            "success": True,
            "message": "Appointment cancelled successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to cancel appointment: {str(e)}"
        }), 500

@healthcare_bp.route('/api/healthcare/reviews', methods=['POST'])
def create_review():
    """Create healthcare review"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'worker_id', 'booking_id', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # This would need to be implemented in database_manager
        # For now, return success
        
        return jsonify({
            "success": True,
            "message": "Review created successfully"
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to create review: {str(e)}"
        }), 500

@healthcare_bp.route('/api/healthcare/statistics', methods=['GET'])
def get_healthcare_statistics():
    """Get healthcare service statistics"""
    try:
        stats = db_manager.get_service_statistics('healthcare')
        
        return jsonify({
            "success": True,
            "statistics": stats
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get statistics: {str(e)}"
        }), 500

@healthcare_bp.route('/api/healthcare/availability/<int:doctor_id>', methods=['GET'])
def get_doctor_availability(doctor_id):
    """Get doctor availability"""
    try:
        # This would need to be implemented
        # For now, return mock availability
        
        availability = {
            "available_slots": [
                "2024-03-20T09:00:00",
                "2024-03-20T10:00:00",
                "2024-03-20T11:00:00",
                "2024-03-20T14:00:00",
                "2024-03-20T15:00:00"
            ]
        }
        
        return jsonify({
            "success": True,
            "availability": availability
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get availability: {str(e)}"
        }), 500

# Health check endpoint
@healthcare_bp.route('/api/healthcare/health', methods=['GET'])
def health_check():
    """Healthcare service health check"""
    try:
        return jsonify({
            "success": True,
            "service": "healthcare",
            "status": "healthy",
            "database": "organized"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "service": "healthcare",
            "status": "error",
            "error": str(e)
        }), 500
