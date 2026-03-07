"""
Expert Availability API Routes
RESTful endpoints for expert dashboard, availability management, and consultation system
"""

from flask import Blueprint, request, jsonify
from .expert_availability_service import expert_availability_service
from .automobile_expert_db import automobile_expert_db

expert_availability_bp = Blueprint('expert_availability', __name__, url_prefix='/api/expert-availability')

@expert_availability_bp.route('/dashboard/<int:expert_id>', methods=['GET'])
def get_expert_dashboard(expert_id):
    """Get expert dashboard data"""
    try:
        dashboard_data = expert_availability_service.get_expert_dashboard_data(expert_id)
        
        if dashboard_data['success']:
            return jsonify(dashboard_data), 200
        else:
            return jsonify(dashboard_data), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/go-online', methods=['POST'])
def go_online():
    """Set expert status to ONLINE_AVAILABLE"""
    try:
        data = request.get_json()
        expert_id = data.get('expert_id')
        
        if not expert_id:
            return jsonify({'success': False, 'error': 'Expert ID is required'}), 400
        
        result = expert_availability_service.go_online(expert_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/go-offline', methods=['POST'])
def go_offline():
    """Set expert status to OFFLINE"""
    try:
        data = request.get_json()
        expert_id = data.get('expert_id')
        
        if not expert_id:
            return jsonify({'success': False, 'error': 'Expert ID is required'}), 400
        
        result = expert_availability_service.go_offline(expert_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/status/<int:expert_id>', methods=['GET'])
def get_expert_status(expert_id):
    """Get expert current status"""
    try:
        # Verify expert exists
        expert = automobile_expert_db.get_expert_by_id(expert_id)
        if not expert:
            return jsonify({'success': False, 'error': 'Expert not found'}), 404
        
        # Get dashboard data (includes status)
        dashboard_data = expert_availability_service.get_expert_dashboard_data(expert_id)
        
        return jsonify({
            'success': True,
            'expert_id': expert_id,
            'expert_name': expert['name'],
            'status': dashboard_data.get('status', 'OFFLINE'),
            'last_status_change': dashboard_data.get('last_status_change'),
            'total_consultations': dashboard_data.get('total_consultations', 0)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/consultation-queue/<int:expert_id>', methods=['GET'])
def get_consultation_queue(expert_id):
    """Get consultation queue for expert"""
    try:
        limit = request.args.get('limit', 10, type=int)
        queue_data = expert_availability_service.get_consultation_queue(expert_id, limit)
        
        if queue_data['success']:
            return jsonify(queue_data), 200
        else:
            return jsonify(queue_data), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/consultation-requests', methods=['POST'])
def create_consultation_request():
    """Create a new consultation request (for users)"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        issue_description = data.get('issue_description')
        expert_category = data.get('expert_category')
        user_name = data.get('user_name')
        user_city = data.get('user_city')
        image_paths = data.get('image_paths', [])
        
        if not all([user_id, issue_description, expert_category]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Validate area of expertise
        valid_areas = ['Engine', 'Electrical', 'Diagnostic', 'General']
        if expert_category not in valid_areas:
            return jsonify({'success': False, 'error': 'Invalid area of expertise'}), 400
        
        # Create request with automatic priority classification
        request_id = expert_availability_service.create_consultation_request_with_priority(
            user_id, issue_description, expert_category, user_name, user_city, image_paths
        )
        
        return jsonify({
            'success': True,
            'message': 'Consultation request created successfully',
            'request_id': request_id,
            'status': 'WAITING'
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/consultation-requests/<int:request_id>', methods=['GET'])
def get_consultation_request(request_id):
    """Get consultation request details"""
    try:
        cursor = expert_availability_db.conn.cursor()
        cursor.execute("""
            SELECT cr.*, ae.name as expert_name 
            FROM consultation_requests cr
            LEFT JOIN expert_availability ea ON cr.expert_id = ea.expert_id
            LEFT JOIN automobile_experts ae ON cr.expert_id = ae.id
            WHERE cr.request_id = ?
        """, (request_id,))
        
        request_data = cursor.fetchone()
        if not request_data:
            return jsonify({'success': False, 'error': 'Request not found'}), 404
        
        return jsonify({
            'success': True,
            'request': dict(request_data)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/consultation-requests/<int:request_id>/accept', methods=['POST'])
def accept_consultation_request(request_id):
    """Accept a consultation request"""
    try:
        data = request.get_json()
        expert_id = data.get('expert_id')
        
        if not expert_id:
            return jsonify({'success': False, 'error': 'Expert ID is required'}), 400
        
        result = expert_availability_service.accept_consultation_request(expert_id, request_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/consultation-requests/<int:request_id>/reject', methods=['POST'])
def reject_consultation_request(request_id):
    """Reject a consultation request"""
    try:
        data = request.get_json()
        expert_id = data.get('expert_id')
        rejection_reason = data.get('rejection_reason')
        
        if not expert_id:
            return jsonify({'success': False, 'error': 'Expert ID is required'}), 400
        
        result = expert_availability_service.reject_consultation_request(expert_id, request_id, rejection_reason)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/consultation-requests/<int:request_id>/complete', methods=['POST'])
def complete_consultation(request_id):
    """Complete a consultation"""
    try:
        data = request.get_json()
        expert_id = data.get('expert_id')
        user_rating = data.get('user_rating')
        
        if not expert_id:
            return jsonify({'success': False, 'error': 'Expert ID is required'}), 400
        
        result = expert_availability_service.complete_consultation(expert_id, request_id, user_rating)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/consultation-requests/waiting', methods=['GET'])
def get_waiting_requests():
    """Get all waiting consultation requests"""
    try:
        area_of_expertise = request.args.get('area_of_expertise')
        limit = request.args.get('limit', 20, type=int)
        
        waiting_requests = expert_availability_db.get_waiting_requests(area_of_expertise, limit)
        
        return jsonify({
            'success': True,
            'waiting_requests': waiting_requests,
            'total_waiting': len(waiting_requests),
            'area_of_expertise': area_of_expertise
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/demand-indicators', methods=['GET'])
def get_demand_indicators():
    """Get demand indicators"""
    try:
        area_of_expertise = request.args.get('area_of_expertise')
        
        demand_data = expert_availability_service.get_demand_indicators(area_of_expertise)
        
        return jsonify(demand_data), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/experts/available', methods=['GET'])
def get_available_experts():
    """Get available experts"""
    try:
        area_of_expertise = request.args.get('area_of_expertise')
        
        available_experts = expert_availability_db.get_available_experts(area_of_expertise)
        
        return jsonify({
            'success': True,
            'available_experts': available_experts,
            'total_available': len(available_experts),
            'area_of_expertise': area_of_expertise
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/analytics/<int:expert_id>', methods=['GET'])
def get_expert_analytics(expert_id):
    """Get expert analytics"""
    try:
        days = request.args.get('days', 30, type=int)
        
        analytics_data = expert_availability_service.get_expert_analytics(expert_id, days)
        
        if analytics_data['success']:
            return jsonify(analytics_data), 200
        else:
            return jsonify(analytics_data), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/system/stats', methods=['GET'])
def get_system_stats():
    """Get system statistics"""
    try:
        stats_data = expert_availability_service.get_system_stats()
        
        return jsonify(stats_data), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/activity-logs/<int:expert_id>', methods=['GET'])
def get_expert_activity_logs(expert_id):
    """Get expert activity logs"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        activity_logs = expert_availability_db.get_expert_activity_logs(expert_id, limit)
        
        return jsonify({
            'success': True,
            'activity_logs': activity_logs,
            'total_logs': len(activity_logs)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Import expert_availability_db for direct database access
from .expert_availability_db import expert_availability_db
