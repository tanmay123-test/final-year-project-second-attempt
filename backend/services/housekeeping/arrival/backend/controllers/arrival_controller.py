from flask import Blueprint, request, jsonify
from services.housekeeping.arrival.backend.services.arrival_service import ArrivalService

arrival_bp = Blueprint('arrival', __name__)
arrival_service = ArrivalService()

@arrival_bp.route('/home/data', methods=['GET'])
def get_home_data():
    """
    Returns data for the User Home Page:
    - Upcoming bookings
    - Top 10 Services
    """
    user_id = request.args.get('user_id') # In real app, get from token
    data = arrival_service.get_home_page_data(user_id)
    return jsonify(data), 200

@arrival_bp.route('/services', methods=['GET'])
def get_services():
    """Returns list of all cleaning services with details"""
    services = arrival_service.get_all_services()
    return jsonify({"services": services}), 200

@arrival_bp.route('/booking/create', methods=['POST'])
def create_booking_intent():
    """
    Step 1 of Booking Flow: User selects service, size, extras.
    Returns a 'draft' booking or price estimate.
    """
    data = request.json
    result = arrival_service.create_booking_intent(data)
    return jsonify(result), 200

@arrival_bp.route('/booking/confirm', methods=['POST'])
def confirm_booking():
    """
    Final Step: User confirms and pays.
    """
    data = request.json
    result, status = arrival_service.confirm_booking(data)
    return jsonify(result), status
