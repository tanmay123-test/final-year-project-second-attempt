"""
Expert History and Performance API Routes
RESTful endpoints for consultation history, performance analytics, reputation, and queue management
"""

from flask import Blueprint, request, jsonify
from .expert_history_service import expert_history_service

expert_history_bp = Blueprint('expert_history', __name__, url_prefix='/api/expert-history')

# Consultation History Routes
@expert_history_bp.route('/history/<int:expert_id>', methods=['GET'])
def get_consultation_history(expert_id):
    """Get expert's consultation history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        history_data = expert_history_service.get_consultation_history(expert_id, limit)
        
        return jsonify(history_data), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_history_bp.route('/reopen/<int:expert_id>/<int:request_id>', methods=['POST'])
def reopen_consultation(expert_id, request_id):
    """Reopen a closed consultation"""
    try:
        result = expert_history_service.reopen_consultation(expert_id, request_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Performance Analytics Routes
@expert_history_bp.route('/analytics/<int:expert_id>', methods=['GET'])
def get_performance_analytics(expert_id):
    """Get expert performance analytics"""
    try:
        days = request.args.get('days', 30, type=int)
        
        analytics_data = expert_history_service.get_performance_analytics(expert_id, days)
        
        return jsonify(analytics_data), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Reputation and Badges Routes
@expert_history_bp.route('/reputation/<int:expert_id>', methods=['GET'])
def get_expert_reputation(expert_id):
    """Get expert reputation information"""
    try:
        reputation_data = expert_history_service.get_expert_reputation(expert_id)
        
        return jsonify(reputation_data), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_history_bp.route('/badges/<int:expert_id>', methods=['GET'])
def get_expert_badges(expert_id):
    """Get expert's badges"""
    try:
        reputation_data = expert_history_service.get_expert_reputation(expert_id)
        
        if reputation_data['success']:
            return jsonify({
                'success': True,
                'badges': reputation_data.get('badges', []),
                'total_badges': reputation_data.get('total_badges', 0)
            }), 200
        else:
            return jsonify(reputation_data), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Expert Status Lifecycle Routes
@expert_history_bp.route('/status/online/<int:expert_id>', methods=['POST'])
def set_expert_online(expert_id):
    """Set expert to online status"""
    try:
        result = expert_history_service.set_expert_online(expert_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_history_bp.route('/status/offline/<int:expert_id>', methods=['POST'])
def set_expert_offline(expert_id):
    """Set expert to offline status"""
    try:
        result = expert_history_service.set_expert_offline(expert_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_history_bp.route('/status/available/<int:expert_id>', methods=['POST'])
def set_expert_available(expert_id):
    """Set expert to available status"""
    try:
        result = expert_history_service.set_expert_available(expert_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_history_bp.route('/status/busy/<int:expert_id>', methods=['POST'])
def set_expert_busy(expert_id):
    """Set expert to busy status (automatic only)"""
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        
        if not request_id:
            return jsonify({'success': False, 'error': 'Request ID is required'}), 400
        
        result = expert_history_service.set_expert_busy(expert_id, request_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Report Management Routes
@expert_history_bp.route('/report/create', methods=['POST'])
def create_user_report():
    """Create a report against user"""
    try:
        data = request.get_json()
        
        expert_id = data.get('expert_id')
        user_id = data.get('user_id')
        request_id = data.get('request_id')
        reason = data.get('reason')
        description = data.get('description')
        
        if not all([expert_id, user_id, request_id, reason]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        result = expert_history_service.create_user_report(
            expert_id, user_id, request_id, reason, description
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_history_bp.route('/reports/<int:expert_id>', methods=['GET'])
def get_expert_reports(expert_id):
    """Get reports created by expert"""
    try:
        reports_data = expert_history_service.get_expert_reports(expert_id)
        
        return jsonify(reports_data), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Queue Management Routes
@expert_history_bp.route('/queue/status', methods=['GET'])
def get_queue_status():
    """Get current queue status"""
    try:
        category = request.args.get('category')
        
        queue_data = expert_history_service.get_queue_status(category)
        
        return jsonify(queue_data), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_history_bp.route('/dashboard/<int:expert_id>', methods=['GET'])
def get_expert_dashboard(expert_id):
    """Get comprehensive expert dashboard data"""
    try:
        dashboard_data = expert_history_service.get_expert_dashboard(expert_id)
        
        if dashboard_data['success']:
            return jsonify(dashboard_data), 200
        else:
            return jsonify(dashboard_data), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Performance Update Routes (Internal use)
@expert_history_bp.route('/performance/update/<int:expert_id>', methods=['POST'])
def update_expert_performance(expert_id):
    """Update expert performance metrics (internal use)"""
    try:
        data = request.get_json()
        
        consultation_completed = data.get('consultation_completed', False)
        response_time_seconds = data.get('response_time_seconds')
        duration_seconds = data.get('duration_seconds')
        user_rating = data.get('user_rating')
        
        expert_history_service.update_expert_performance(
            expert_id, consultation_completed, response_time_seconds,
            duration_seconds, user_rating
        )
        
        return jsonify({
            'success': True,
            'message': 'Performance updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Fair Assignment Score Routes
@expert_history_bp.route('/fair-score/<int:expert_id>', methods=['GET'])
def get_fair_assignment_score(expert_id):
    """Get expert's fair assignment score"""
    try:
        from .expert_history_db import expert_history_db
        
        score = expert_history_db.calculate_fair_assignment_score(expert_id)
        
        return jsonify({
            'success': True,
            'fair_assignment_score': round(score, 2),
            'score_level': 'High' if score >= 80 else 'Medium' if score >= 60 else 'Low'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Badge Management Routes
@expert_history_bp.route('/badges/award/<int:expert_id>', methods=['POST'])
def award_badge(expert_id):
    """Award badge to expert (admin use)"""
    try:
        data = request.get_json()
        
        badge_name = data.get('badge_name')
        badge_type = data.get('badge_type')
        
        if not all([badge_name, badge_type]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        from .expert_history_db import expert_history_db
        
        success = expert_history_db.award_badge(expert_id, badge_name, badge_type)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Badge "{badge_name}" awarded successfully'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to award badge or badge already exists'
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Queue Processing Routes (Internal use)
@expert_history_bp.route('/queue/process', methods=['POST'])
def process_waiting_queue():
    """Manually trigger queue processing (internal use)"""
    try:
        expert_history_service._process_waiting_queue()
        
        return jsonify({
            'success': True,
            'message': 'Queue processing triggered successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
