"""
Expert Availability API Routes
RESTful endpoints for expert dashboard, availability management, and consultation system
"""

from flask import Blueprint, request, jsonify
from .expert_availability_service import expert_availability_service
from .automobile_expert_db import automobile_expert_db
from datetime import datetime

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

@expert_availability_bp.route('/consultation-history/<int:expert_id>', methods=['GET'])
def get_consultation_history(expert_id):
    """Get expert consultation history and earnings - CLI compatible"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        # Get completed consultations for the expert
        consultations = expert_availability_db.get_expert_consultation_history(expert_id, limit)
        
        # Transform to match CLI format
        cli_format_consultations = []
        for consultation in consultations:
            cli_format = {
                'request_id': consultation.get('request_id'),
                'user_name': consultation.get('user_name', 'N/A'),
                'category': consultation.get('area_of_expertise', 'N/A'),
                'date': consultation.get('completed_at') or consultation.get('created_at', 'N/A'),
                'duration_seconds': consultation.get('duration_seconds', 0),
                'status': consultation.get('status', 'N/A'),
                'resolution_status': 'COMPLETED' if consultation.get('status') == 'COMPLETED' else 'PENDING',
                'assigned_reason': consultation.get('assigned_reason', ''),
                'proposed_fee': consultation.get('proposed_fee', 0),
                'user_rating': consultation.get('user_rating', 0),
                'issue_description': consultation.get('issue_description', ''),
                'user_city': consultation.get('user_city', ''),
                'started_at': consultation.get('started_at'),
                'completed_at': consultation.get('completed_at')
            }
            cli_format_consultations.append(cli_format)
        
        return jsonify({
            'success': True,
            'consultations': cli_format_consultations,
            'total_consultations': len(cli_format_consultations)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/performance-analytics/<int:expert_id>', methods=['GET'])
def get_performance_analytics(expert_id):
    """Get expert performance analytics - CLI compatible"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Get performance stats
        performance_stats = expert_availability_db.get_expert_performance_stats(expert_id, days)
        consultation_history = expert_availability_db.get_expert_consultation_history(expert_id, 100)
        
        # Calculate analytics matching CLI format
        total_consultations = len(consultation_history)
        completed_consultations = len([c for c in consultation_history if c.get('status') == 'COMPLETED'])
        resolution_rate = (completed_consultations / total_consultations * 100) if total_consultations > 0 else 0
        
        analytics = {
            'analysis_period_days': days,
            'total_consultations': total_consultations,
            'completed_consultations': completed_consultations,
            'resolution_rate': round(resolution_rate, 2),
            'average_response_seconds': performance_stats.get('avg_response_time_minutes', 0) * 60,
            'average_duration_seconds': performance_stats.get('avg_duration_minutes', 0) * 60,
            'online_hours': performance_stats.get('online_hours', 0),
            'reliability_score': round(performance_stats.get('reliability_score', 4.5), 1),
            'totalConsultations': total_consultations,
            'totalEarnings': sum(c.get('proposed_fee', 0) for c in consultation_history),
            'avgRating': sum(c.get('user_rating', 0) for c in consultation_history) / completed_consultations if completed_consultations > 0 else 0,
            'avgResponseTime': performance_stats.get('avg_response_time_minutes', 0),
            'avgDuration': performance_stats.get('avg_duration_minutes', 0),
            'monthlyStats': [],
            'categoryStats': []
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/reputation/<int:expert_id>', methods=['GET'])
def get_reputation_data(expert_id):
    """Get expert reputation and badges data - CLI compatible"""
    try:
        consultation_history = expert_availability_db.get_expert_consultation_history(expert_id, 100)
        performance_stats = expert_availability_db.get_expert_performance_stats(expert_id)
        
        # Calculate reputation metrics matching CLI format
        total_ratings = len([c for c in consultation_history if c.get('user_rating')])
        avg_rating = sum(c.get('user_rating', 0) for c in consultation_history) / total_ratings if total_ratings > 0 else 0
        completed_consultations = len([c for c in consultation_history if c.get('status') == 'COMPLETED'])
        
        # Rating distribution
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for consultation in consultation_history:
            rating = consultation.get('user_rating')
            if rating and rating in rating_distribution:
                rating_distribution[rating] += 1
        
        # Generate badges based on performance
        badges = []
        if avg_rating >= 4.5:
            badges.append("⭐ Top Rated")
        if performance_stats.get('avg_response_time_minutes', 999) < 1:
            badges.append("⚡ Fast Responder")
        if completed_consultations >= 50:
            badges.append("📊 High Volume")
        if (completed_consultations / len(consultation_history) * 100) >= 90 if consultation_history else 0:
            badges.append("🏆 Trusted Expert")
        
        reputation = {
            'approval_status': True,  # Would check from database
            'online_hours': performance_stats.get('online_hours', 0),
            'consultations_completed': completed_consultations,
            'rating': round(avg_rating, 1),
            'reliability_score': round(performance_stats.get('reliability_score', 4.5), 1),
            'fair_assignment_score': 95,  # Would calculate from assignment data
            'badges': badges,
            'avgRating': avg_rating,
            'totalRatings': total_ratings,
            'ratingDistribution': rating_distribution,
            'achievements': [],
            'reputationScore': avg_rating * 100
        }
        
        return jsonify({
            'success': True,
            'reputation': reputation
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/recent-users/<int:expert_id>', methods=['GET'])
def get_recent_users(expert_id):
    """Get recent users for reporting"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # Get recent consultations
        recent_consultations = expert_availability_db.get_expert_consultation_history(expert_id, limit)
        
        users = []
        for consultation in recent_consultations:
            users.append({
                'request_id': consultation['request_id'],
                'user_id': f"user_{consultation['request_id']}",  # Generate user ID
                'user_name': consultation['user_name'],
                'issue_description': consultation['issue_description'],
                'created_at': consultation['created_at']
            })
        
        return jsonify({
            'success': True,
            'users': users
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/report-user', methods=['POST'])
def report_user():
    """Submit user report - CLI compatible"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('expert_id') or not data.get('description'):
            return jsonify({'success': False, 'error': 'Expert ID and description are required'}), 400
        
        # Map CLI categories to backend format
        category_mapping = {
            '👤 User Abuse': 'USER_ABUSE',
            '🔧 Technical Issue': 'TECHNICAL_ISSUE', 
            '📞 General Support': 'GENERAL_SUPPORT'
        }
        
        category = data.get('category')
        mapped_category = category_mapping.get(category, 'GENERAL_SUPPORT')
        
        # Generate report ID
        report_id = f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Log the report (in production, save to database)
        print(f"User report received: {report_id}")
        print(f"Expert ID: {data.get('expert_id')}")
        print(f"User ID: {data.get('reported_user_id')}")
        print(f"Request ID: {data.get('consultation_id')}")
        print(f"Reason: {mapped_category}")
        print(f"Description: {data.get('description')}")
        
        return jsonify({
            'success': True,
            'message': 'Report submitted successfully',
            'report_id': report_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@expert_availability_bp.route('/queue-status/<int:expert_id>', methods=['GET'])
def get_queue_status(expert_id):
    """Get queue status information - CLI compatible"""
    try:
        # Get dashboard data
        dashboard_data = expert_availability_service.get_expert_dashboard_data(expert_id)
        
        if not dashboard_data['success']:
            return jsonify({'success': False, 'error': 'Failed to get queue status'}), 404
        
        # Get waiting requests for category breakdown
        waiting_requests = expert_availability_db.get_waiting_requests('all', limit=50)
        
        # Calculate category breakdown
        category_breakdown = {}
        for request in waiting_requests:
            category = request.get('area_of_expertise', 'General')
            category_breakdown[category] = category_breakdown.get(category, 0) + 1
        
        # Find oldest and newest requests
        oldest_request = waiting_requests[-1] if waiting_requests else None
        newest_request = waiting_requests[0] if waiting_requests else None
        
        queue_status = {
            'total_waiting': dashboard_data.get('waiting_requests_count', 0),
            'category_breakdown': category_breakdown,
            'oldest_request': {
                'request_id': oldest_request.get('request_id') if oldest_request else None,
                'category': oldest_request.get('area_of_expertise') if oldest_request else None,
                'created_at': oldest_request.get('created_at') if oldest_request else None,
                'priority_level': 'NORMAL'
            } if oldest_request else None,
            'newest_request': {
                'request_id': newest_request.get('request_id') if newest_request else None,
                'category': newest_request.get('area_of_expertise') if newest_request else None,
                'created_at': newest_request.get('created_at') if newest_request else None,
                'priority_level': 'NORMAL'
            } if newest_request else None,
            'waitingRequests': dashboard_data.get('waiting_requests_count', 0),
            'activeConsultations': 1 if dashboard_data.get('current_consultation') else 0,
            'demandLevel': dashboard_data.get('demand_level', 'LOW'),
            'avgWaitTime': 5,  # Placeholder - would calculate from actual data
            'queueTrends': [],
            'expertStatus': dashboard_data.get('status', 'OFFLINE'),
            'lastUpdated': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'queue_status': queue_status
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Import expert_availability_db for direct database access
from .expert_availability_db import expert_availability_db
