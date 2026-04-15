"""
Housekeeping Routes using Organized Database Manager
Provides API endpoints for housekeeping service
"""

import time
from flask import Blueprint, request, jsonify
from database.database_manager import db_manager

# Create blueprint
housekeeping_bp = Blueprint('housekeeping', __name__)

# Housekeeping Routes
@housekeeping_bp.route('/api/housekeeping/services', methods=['GET'])
def get_services():
    """Get housekeeping services and cleaners"""
    try:
        # Get workers from organized database
        workers = db_manager.get_workers_by_service('housekeeping')
        
        # Filter for cleaners
        cleaners = [w for w in workers if w.get('worker_type') == 'cleaner']
        
        # Get services (mock data for now)
        services = [
            {
                "id": 1,
                "name": "General Cleaning",
                "description": "Complete home cleaning service",
                "price": 500,
                "available_count": len(cleaners)
            },
            {
                "id": 2,
                "name": "Deep Cleaning",
                "description": "Thorough deep cleaning service",
                "price": 800,
                "available_count": len(cleaners)
            },
            {
                "id": 3,
                "name": "Kitchen Cleaning",
                "description": "Kitchen specialized cleaning",
                "price": 600,
                "available_count": len(cleaners)
            },
            {
                "id": 4,
                "name": "Bathroom Cleaning",
                "description": "Bathroom specialized cleaning",
                "price": 400,
                "available_count": len(cleaners)
            }
        ]
        
        return jsonify({
            "success": True,
            "services": services,
            "top_cleaners": cleaners
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get services: {str(e)}"
        }), 500

@housekeeping_bp.route('/api/housekeeping/cleaners', methods=['GET'])
def get_cleaners():
    """Get housekeeping cleaners"""
    try:
        # Get workers from organized database
        workers = db_manager.get_workers_by_service('housekeeping')
        
        # Filter for cleaners
        cleaners = [w for w in workers if w.get('worker_type') == 'cleaner']
        
        return jsonify({
            "success": True,
            "workers": cleaners
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get cleaners: {str(e)}"
        }), 500

@housekeeping_bp.route('/api/housekeeping/bookings', methods=['POST'])
def create_booking():
    """Create housekeeping booking"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'worker_id', 'booking_data']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Create booking using organized database
        booking_id = db_manager.create_booking(
            'housekeeping',
            data['user_id'],
            data['worker_id'],
            data['booking_data']
        )
        
        return jsonify({
            "success": True,
            "message": "Booking created successfully",
            "booking_id": booking_id
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to create booking: {str(e)}"
        }), 500

@housekeeping_bp.route('/api/housekeeping/bookings', methods=['GET'])
def get_bookings():
    """Get housekeeping bookings"""
    try:
        # Get filters from query params
        user_id = request.args.get('user_id')
        worker_id = request.args.get('worker_id')
        status = request.args.get('status')
        
        # Get bookings from organized database
        bookings = db_manager.get_bookings(
            'housekeeping',
            user_id=int(user_id) if user_id else None,
            worker_id=int(worker_id) if worker_id else None,
            status=status
        )
        
        return jsonify({
            "success": True,
            "bookings": bookings
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get bookings: {str(e)}"
        }), 500

@housekeeping_bp.route('/api/housekeeping/statistics', methods=['GET'])
def get_housekeeping_statistics():
    """Get housekeeping service statistics"""
    try:
        stats = db_manager.get_service_statistics('housekeeping')
        
        return jsonify({
            "success": True,
            "statistics": stats
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to get statistics: {str(e)}"
        }), 500

@housekeeping_bp.route('/api/housekeeping/check-availability', methods=['POST'])
def check_availability():
    """Check availability for housekeeping service"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['service_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        service_type = data.get('service_type')
        worker_id = data.get('worker_id')
        booking_type = data.get('booking_type', 'schedule')
        
        # Get available workers for the service
        available_workers = db_manager.get_workers_by_service('housekeeping')
        
        # Filter by worker_id if specified
        if worker_id:
            available_workers = [w for w in available_workers if str(w.get('id')) == str(worker_id)]
        
        # For instant booking, check if worker is online
        if booking_type == 'instant' and worker_id:
            worker = next((w for w in available_workers if str(w.get('id')) == str(worker_id)), None)
            if not worker or not worker.get('is_online', False):
                return jsonify({
                    "success": False,
                    "error": "Selected worker is not available for instant booking"
                }), 400
        
        # Count available workers
        workers_count = len(available_workers)
        
        return jsonify({
            "success": True,
            "data": {
                "workers_count": workers_count,
                "available": workers_count > 0,
                "message": f"{workers_count} professionals available"
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to check availability: {str(e)}"
        }), 500

@housekeeping_bp.route('/api/housekeeping/confirm-booking', methods=['POST'])
def confirm_booking():
    """Confirm housekeeping booking"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['service_type', 'address']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Create booking using organized database
        user_id = data.get('user_id', 'demo_user')  # Get from session or default
        worker_id = data.get('worker_id')
        
        # For instant booking, assign worker immediately
        if data.get('booking_type') == 'instant' and worker_id:
            # Check if worker is still available
            workers = db_manager.get_workers_by_service('housekeeping')
            worker = next((w for w in workers if str(w.get('id')) == str(worker_id)), None)
            
            if not worker or not worker.get('is_online', False):
                return jsonify({
                    "success": False,
                    "error": "Worker is no longer available"
                }), 400
        
        # Create booking record
        booking_data = {
            'user_id': user_id,
            'worker_id': worker_id,
            'service_type': data.get('service_type'),
            'address': data.get('address'),
            'booking_type': data.get('booking_type', 'schedule'),
            'date': data.get('date'),
            'time': data.get('time'),
            'home_size': data.get('home_size'),
            'add_ons': data.get('add_ons', '[]'),
            'price': data.get('price', 0),
            'status': 'confirmed'
        }
        
        # Store booking (this would need to be implemented in db_manager)
        # For now, just return success
        return jsonify({
            "success": True,
            "data": {
                "booking_id": f"bk_{user_id}_{int(time.time())}",
                "status": "confirmed",
                "message": "Booking confirmed successfully"
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to confirm booking: {str(e)}"
        }), 500

@housekeeping_bp.route('/api/housekeeping/health', methods=['GET'])
def health_check():
    """Housekeeping service health check"""
    try:
        return jsonify({
            "success": True,
            "service": "housekeeping",
            "status": "healthy",
            "database": "organized"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "service": "housekeeping",
            "status": "error",
            "error": str(e)
        }), 500
