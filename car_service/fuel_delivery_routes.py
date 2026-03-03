"""
Fuel Delivery API Routes
Handles all fuel delivery agent related endpoints
"""

from flask import Blueprint, request, jsonify
from .fuel_delivery_service import fuel_delivery_service

fuel_delivery_bp = Blueprint('fuel_delivery', __name__)

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

@fuel_delivery_bp.route('/assign', methods=['POST'])
def assign_fuel_request():
    """Assign fuel request to agent"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        request_id = data.get('request_id')
        agent_id = data.get('agent_id')
        
        if not request_id or not agent_id:
            return jsonify({'success': False, 'error': 'Request ID and agent ID required'}), 400
        
        result = fuel_delivery_service.assign_fuel_request(request_id, agent_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fuel_delivery_bp.route('/complete', methods=['POST'])
def complete_fuel_delivery():
    """Complete fuel delivery"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        request_id = data.get('request_id')
        agent_id = data.get('agent_id')
        
        if not request_id or not agent_id:
            return jsonify({'success': False, 'error': 'Request ID and agent ID required'}), 400
        
        result = fuel_delivery_service.complete_fuel_delivery(request_id, agent_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
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
