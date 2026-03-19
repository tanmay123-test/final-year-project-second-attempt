"""
Fuel Delivery API Routes
Handles all fuel delivery agent related endpoints
"""

from flask import Blueprint, request, jsonify
from .fuel_delivery_service import fuel_delivery_service

fuel_delivery_bp = Blueprint('fuel_delivery_api', __name__)

@fuel_delivery_bp.route('/agents/available', methods=['GET'])
def get_available_agents():
    """Public endpoint: list all APPROVED + ONLINE_AVAILABLE agents for client-side filtering"""
    try:
        agents = fuel_delivery_service.get_available_agents()
        return jsonify({'success': True, 'agents': agents}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/register', methods=['POST'])
def register_fuel_agent():
    """Register new fuel delivery agent"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        result = fuel_delivery_service.register_agent(data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/login', methods=['POST'])
def login_fuel_agent():
    """Login fuel delivery agent"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        result = fuel_delivery_service.authenticate_agent(email, password)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/status', methods=['POST'])
def update_agent_status():
    """Update fuel delivery agent status"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        agent_id = data.get('agent_id')
        status = data.get('status')
        
        if not agent_id or not status:
            return jsonify({'success': False, 'error': 'Agent ID and status required'}), 400
        
        result = fuel_delivery_service.update_agent_status(agent_id, status)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/requests', methods=['GET'])
def get_fuel_requests():
    """Get fuel delivery requests queue"""
    try:
        # Get agent location from query params (optional)
        agent_lat = request.args.get('lat')
        agent_lon = request.args.get('lon')
        
        requests = fuel_delivery_service.get_fuel_requests_queue(agent_lat, agent_lon)
        
        return jsonify({
            'success': True,
            'requests': requests
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/requests/accept', methods=['POST'])
def accept_fuel_request():
    """Accept a fuel delivery request"""
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        agent_id = data.get('agent_id')
        
        if not request_id or not agent_id:
            return jsonify({'success': False, 'error': 'request_id and agent_id are required'}), 400
            
        db = FuelDeliveryDB()
        result = db.assign_fuel_request(request_id, agent_id)
        
        if result:
            return jsonify({'success': True, 'message': 'Request accepted successfully'}), 200
        return jsonify({'success': False, 'error': 'Could not accept request'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/requests/start', methods=['POST'])
def start_fuel_delivery():
    """Start the fuel delivery (requires OTP)"""
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        agent_id = data.get('agent_id')
        otp = data.get('otp')
        
        if not all([request_id, agent_id, otp]):
            return jsonify({'success': False, 'error': 'request_id, agent_id and otp are required'}), 400
            
        db = FuelDeliveryDB()
        if db.verify_otp(request_id, otp):
            if db.start_fuel_delivery(request_id, agent_id):
                return jsonify({'success': True, 'message': 'Delivery started successfully'}), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid OTP'}), 401
            
        return jsonify({'success': False, 'error': 'Could not start delivery'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/requests/complete', methods=['POST'])
def complete_fuel_delivery():
    """Mark the fuel delivery as completed"""
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        
        if not request_id:
            return jsonify({'success': False, 'error': 'request_id is required'}), 400
            
        db = FuelDeliveryDB()
        if db.complete_fuel_delivery(request_id):
            return jsonify({'success': True, 'message': 'Delivery completed successfully'}), 200
        return jsonify({'success': False, 'error': 'Could not complete delivery'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/requests/status/<int:request_id>', methods=['GET'])
def get_request_status(request_id):
    """Get status of a specific fuel delivery request"""
    try:
        db = FuelDeliveryDB()
        cursor = db.conn.cursor()
        cursor.execute('''
            SELECT status, otp, agent_id FROM fuel_delivery_requests WHERE id = ?
        ''', (request_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return jsonify({
                'success': True, 
                'status': result[0], 
                'otp': result[1],
                'agent_id': result[2]
            }), 200
        return jsonify({'success': False, 'error': 'Request not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/history/<int:agent_id>', methods=['GET'])
def get_delivery_history(agent_id):
    """Get fuel delivery history for agent"""
    try:
        # This would need to be implemented in service layer
        # For now, return empty history
        return jsonify({
            'success': True,
            'history': [],
            'total_deliveries': 0,
            'total_earnings': 0.0
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/performance/<int:agent_id>', methods=['GET'])
def get_agent_performance(agent_id):
    """Get fuel delivery agent performance"""
    try:
        performance = fuel_delivery_service.get_agent_performance(agent_id)
        
        return jsonify({
            'success': True,
            'performance': performance
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/nearby-agents', methods=['GET'])
def get_nearby_agents():
    """Get nearby fuel delivery agents"""
    try:
        user_lat = request.args.get('latitude')
        user_lon = request.args.get('longitude')
        radius_km = request.args.get('radius', 10)  # Default 10km radius
        
        if not user_lat or not user_lon:
            return jsonify({'success': False, 'error': 'Latitude and longitude required'}), 400
        
        agents = fuel_delivery_service.get_nearby_agents(float(user_lat), float(user_lon), float(radius_km))
        
        return jsonify({
            'success': True,
            'agents': agents
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/create-request', methods=['POST'])
def create_fuel_request():
    """Create new fuel delivery request"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        result = fuel_delivery_service.create_fuel_request(data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Admin endpoints
@fuel_delivery_bp.route('/admin/pending', methods=['GET'])
def get_pending_agents():
    """Get all pending fuel delivery agents for admin"""
    try:
        agents = fuel_delivery_service.get_pending_agents()
        return jsonify(agents), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/admin/approved', methods=['GET'])
def get_approved_agents():
    """Get all approved fuel delivery agents for admin"""
    try:
        agents = fuel_delivery_service.get_approved_agents()
        return jsonify(agents), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/admin/agent/<int:agent_id>', methods=['GET'])
def get_agent_details(agent_id):
    """Get specific fuel delivery agent details for admin"""
    try:
        agent = fuel_delivery_service.get_agent_by_id(agent_id)
        if agent:
            return jsonify(agent), 200
        else:
            return jsonify({'error': 'Agent not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/admin/approve', methods=['POST'])
def approve_agent():
    """Approve fuel delivery agent"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({'success': False, 'error': 'Agent ID required'}), 400
        
        result = fuel_delivery_service.approve_agent(agent_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/admin/reject', methods=['POST'])
def reject_agent():
    """Reject fuel delivery agent"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({'success': False, 'error': 'Agent ID required'}), 400
        
        result = fuel_delivery_service.reject_agent(agent_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Availability Engine Routes
@fuel_delivery_bp.route('/status', methods=['POST'])
def update_agent_status():
    """Update agent online status (Go Online/Offline)"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        new_status = data.get('status')
        
        if not agent_id or not new_status:
            return jsonify({'success': False, 'error': 'Agent ID and status required'}), 400
        
        result = fuel_delivery_service.update_agent_status(agent_id, new_status)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/agent/<int:agent_id>/status', methods=['GET'])
def get_agent_status(agent_id):
    """Get current agent status and availability"""
    try:
        result = fuel_delivery_service.get_agent_status(agent_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/requests', methods=['GET'])
def get_fuel_requests_queue():
    """Get eligible fuel requests for agent"""
    try:
        agent_id = request.args.get('agent_id')
        if not agent_id:
            return jsonify({'success': False, 'error': 'Agent ID required'}), 400
        
        result = fuel_delivery_service.get_eligible_requests(agent_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/demand-insights', methods=['GET'])
def get_demand_insights():
    """Get demand indicators and smart suggestions"""
    try:
        region = request.args.get('region', 'default')
        result = fuel_delivery_service.get_demand_insights(region)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/accept-request', methods=['POST'])
def accept_fuel_request():
    """Accept a fuel delivery request"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        request_id = data.get('request_id')
        
        if not agent_id or not request_id:
            return jsonify({'success': False, 'error': 'Agent ID and Request ID required'}), 400
        
        result = fuel_delivery_service.accept_request(agent_id, request_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/reject-request', methods=['POST'])
def reject_fuel_request():
    """Reject a fuel delivery request"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        request_id = data.get('request_id')
        
        if not agent_id or not request_id:
            return jsonify({'success': False, 'error': 'Agent ID and Request ID required'}), 400
        
        result = fuel_delivery_service.reject_request(agent_id, request_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Fuel Request Queue and Smart Dispatch Routes
@fuel_delivery_bp.route('/queue/available', methods=['GET'])
def get_available_requests():
    """Get available fuel requests for an agent with smart filtering"""
    try:
        agent_id = request.args.get('agent_id')
        if not agent_id:
            return jsonify({'success': False, 'error': 'Agent ID required'}), 400
        
        # Import here to avoid circular import
        from .fuel_request_queue_service import fuel_request_queue_service
        result = fuel_request_queue_service.get_available_fuel_requests(int(agent_id))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/queue/assign', methods=['POST'])
def assign_fuel_request():
    """Assign a fuel request to an agent"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        request_id = data.get('request_id')
        
        if not agent_id or not request_id:
            return jsonify({'success': False, 'error': 'Agent ID and Request ID required'}), 400
        
        from .fuel_request_queue_service import fuel_request_queue_service
        result = fuel_request_queue_service.assign_fuel_request(int(agent_id), int(request_id))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/queue/reject', methods=['POST'])
def reject_fuel_request_queue():
    """Reject a fuel request and reassign to next agent"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        request_id = data.get('request_id')
        
        if not agent_id or not request_id:
            return jsonify({'success': False, 'error': 'Agent ID and Request ID required'}), 400
        
        from .fuel_request_queue_service import fuel_request_queue_service
        result = fuel_request_queue_service.reject_fuel_request(int(agent_id), int(request_id))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/queue/auto-dispatch', methods=['POST'])
def auto_dispatch_waiting_requests():
    """Automatically dispatch waiting requests to available agents"""
    try:
        from .fuel_request_queue_service import fuel_request_queue_service
        result = fuel_request_queue_service.auto_dispatch_waiting_requests()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/active-delivery/<int:agent_id>', methods=['GET'])
def get_active_delivery(agent_id):
    """Get active delivery for an agent"""
    try:
        active_delivery = fuel_delivery_service.get_active_delivery(agent_id)
        if active_delivery:
            return jsonify({'success': True, 'delivery': active_delivery}), 200
        else:
            return jsonify({'success': True, 'delivery': None}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/history/<int:agent_id>', methods=['GET'])
def get_delivery_history(agent_id):
    """Get delivery history and earnings for an agent"""
    try:
        history = fuel_delivery_service.get_delivery_history(agent_id)
        earnings = fuel_delivery_service.get_agent_earnings(agent_id)
        
        return jsonify({
            'success': True,
            'history': history,
            'earnings': earnings
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/performance/<int:agent_id>', methods=['GET'])
def get_agent_performance(agent_id):
    """Get agent performance metrics and reputation"""
    try:
        performance = fuel_delivery_service.get_agent_performance(agent_id)
        return jsonify({'success': True, 'performance': performance}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Active Delivery Engine Routes
@fuel_delivery_bp.route('/delivery/start-arrival', methods=['POST'])
def start_arrival():
    """Agent starts navigation to delivery location"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        request_id = data.get('request_id')
        
        if not agent_id or not request_id:
            return jsonify({'success': False, 'error': 'Agent ID and Request ID required'}), 400
        
        from .active_delivery_service import active_delivery_service
        result = active_delivery_service.start_arrival(int(agent_id), int(request_id))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/delivery/start-delivery', methods=['POST'])
def start_delivery():
    """Agent starts fuel delivery"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        request_id = data.get('request_id')
        
        if not agent_id or not request_id:
            return jsonify({'success': False, 'error': 'Agent ID and Request ID required'}), 400
        
        from .active_delivery_service import active_delivery_service
        result = active_delivery_service.start_delivery(int(agent_id), int(request_id))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/delivery/complete', methods=['POST'])
def complete_delivery():
    """Complete fuel delivery and calculate earnings"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        request_id = data.get('request_id')
        
        if not agent_id or not request_id:
            return jsonify({'success': False, 'error': 'Agent ID and Request ID required'}), 400
        
        from .active_delivery_service import active_delivery_service
        result = active_delivery_service.complete_delivery(int(agent_id), int(request_id))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/delivery/update-location', methods=['POST'])
def update_agent_location():
    """Update agent live location"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not agent_id or latitude is None or longitude is None:
            return jsonify({'success': False, 'error': 'Agent ID, latitude, and longitude required'}), 400
        
        from .active_delivery_service import active_delivery_service
        result = active_delivery_service.update_agent_location(int(agent_id), float(latitude), float(longitude))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/delivery/upload-proof', methods=['POST'])
def upload_delivery_proof():
    """Upload delivery proof image"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        request_id = data.get('request_id')
        proof_image_path = data.get('proof_image_path')
        
        if not agent_id or not request_id or not proof_image_path:
            return jsonify({'success': False, 'error': 'Agent ID, Request ID, and proof path required'}), 400
        
        from .active_delivery_service import active_delivery_service
        result = active_delivery_service.upload_delivery_proof(int(agent_id), int(request_id), proof_image_path)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Performance Engine Routes
@fuel_delivery_bp.route('/performance/earnings/<int:agent_id>', methods=['GET'])
def get_agent_earnings():
    """Get agent earnings summary"""
    try:
        agent_id = request.view_args['agent_id']
        period = request.args.get('period', 'daily')
        
        from .performance_engine_service import performance_engine_service
        result = performance_engine_service.get_agent_earnings_summary(int(agent_id), period)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/performance/update', methods=['POST'])
def update_agent_performance():
    """Update agent performance metrics"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({'success': False, 'error': 'Agent ID required'}), 400
        
        from .performance_engine_service import performance_engine_service
        performance_data = performance_engine_service.get_agent_performance(int(agent_id))
        
        return jsonify({'success': True, 'performance': performance_data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/performance/award-badge', methods=['POST'])
def award_agent_badge():
    """Award a badge to an agent"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        badge_name = data.get('badge_name')
        
        if not agent_id or not badge_name:
            return jsonify({'success': False, 'error': 'Agent ID and badge name required'}), 400
        
        from .performance_engine_service import performance_engine_service
        result = performance_engine_service.award_badge(int(agent_id), badge_name)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/performance/flag-review', methods=['POST'])
def flag_agent_for_review():
    """Flag agent for admin review"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')
        reason = data.get('reason')
        
        if not agent_id or not reason:
            return jsonify({'success': False, 'error': 'Agent ID and reason required'}), 400
        
        from .performance_engine_service import performance_engine_service
        result = performance_engine_service.flag_agent_for_review(int(agent_id), reason)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# User-side Fuel Delivery Routes
@fuel_delivery_bp.route('/agents/available', methods=['GET'])
def get_available_agents():
    """Get all available fuel delivery agents"""
    try:
        from .fuel_delivery_service import fuel_delivery_service
        agents = fuel_delivery_service.get_available_agents()
        return jsonify({'success': True, 'agents': agents}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/requests/create', methods=['POST'])
def create_fuel_request():
    """Create fuel delivery request"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        fuel_type = data.get('fuel_type')
        fuel_quantity = data.get('fuel_quantity')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        agent_id = data.get('agent_id')  # Optional for manual selection
        
        if not all([user_id, fuel_type, fuel_quantity, latitude, longitude]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        from .fuel_delivery_service import fuel_delivery_service
        result = fuel_delivery_service.create_fuel_request(
            user_id, fuel_type, fuel_quantity, latitude, longitude, agent_id
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/requests/user/<int:user_id>', methods=['GET'])
def get_user_fuel_requests(user_id):
    """Get fuel requests for a user"""
    try:
        from .fuel_delivery_service import fuel_delivery_service
        requests = fuel_delivery_service.get_user_requests(user_id)
        return jsonify({'success': True, 'requests': requests}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/requests/<int:request_id>/status', methods=['GET'])
def get_request_status(request_id):
    """Get fuel request status"""
    try:
        from .fuel_delivery_service import fuel_delivery_service
        request_data = fuel_delivery_service.get_request_status(request_id)
        return jsonify({'success': True, 'request': request_data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/agent/<int:agent_id>/active-jobs', methods=['GET'])
def get_agent_active_jobs(agent_id):
    """Get agent's active jobs count and earnings"""
    try:
        from .fuel_delivery_service import fuel_delivery_service
        
        # Get active jobs count
        active_delivery = fuel_delivery_service.get_active_delivery(agent_id)
        jobs_count = 1 if active_delivery else 0
        
        # Get total earnings from history
        earnings_data = fuel_delivery_service.get_agent_earnings(agent_id)
        total_earnings = earnings_data.get('total_earnings', 0)
        
        return jsonify({
            'success': True,
            'jobsAccepted': jobs_count,
            'earnings': total_earnings
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/accept-request', methods=['POST'])
def accept_fuel_delivery_request():
    """Accept a fuel delivery request"""
    try:
        from .fuel_delivery_service import fuel_delivery_service
        
        data = request.get_json()
        request_id = data.get('request_id')
        agent_id = data.get('agent_id')
        
        if not request_id or not agent_id:
            return jsonify({'success': False, 'error': 'Missing request_id or agent_id'}), 400
        
        result = fuel_delivery_service.accept_delivery_request(request_id, agent_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/reject-request', methods=['POST'])
def reject_fuel_delivery_request():
    """Reject a fuel delivery request"""
    try:
        from .fuel_delivery_service import fuel_delivery_service
        
        data = request.get_json()
        request_id = data.get('request_id')
        agent_id = data.get('agent_id')
        
        if not request_id or not agent_id:
            return jsonify({'success': False, 'error': 'Missing request_id or agent_id'}), 400
        
        result = fuel_delivery_service.reject_delivery_request(request_id, agent_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
