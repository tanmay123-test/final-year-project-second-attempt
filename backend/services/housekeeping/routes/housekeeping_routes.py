"""
Housekeeping Routes using Organized Database Manager
Provides API endpoints for housekeeping service
"""

from flask import Blueprint, request, jsonify
from database.database_manager import db_manager

# Create blueprint
housekeeping_bp = Blueprint('housekeeping', __name__)

# Housekeeping Routes
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
