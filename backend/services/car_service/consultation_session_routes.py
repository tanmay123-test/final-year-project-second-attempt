"""
Consultation Session API Routes
RESTful endpoints for active consultation management, chat, calls, and real-time features
"""

from flask import Blueprint, request, jsonify
from .consultation_session_service import consultation_session_service
from .expert_availability_db import expert_availability_db

consultation_session_bp = Blueprint('consultation_session', __name__, url_prefix='/api/consultation-session')

@consultation_session_bp.route('/start', methods=['POST'])
def start_consultation_session():
    """Start a new consultation session"""
    try:
        data = request.get_json()
        
        request_id = data.get('request_id')
        user_id = data.get('user_id')
        expert_id = data.get('expert_id')
        
        if not all([request_id, user_id, expert_id]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        result = consultation_session_service.start_consultation_session(request_id, user_id, expert_id)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@consultation_session_bp.route('/active/<int:expert_id>', methods=['GET'])
def get_active_session(expert_id):
    """Get expert's current active consultation session"""
    try:
        session_data = consultation_session_service.get_active_session(expert_id)
        
        if session_data['success']:
            return jsonify(session_data), 200
        else:
            return jsonify(session_data), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@consultation_session_bp.route('/details/<int:session_id>', methods=['GET'])
def get_session_details(session_id):
    """Get complete session details including messages, images, notes"""
    try:
        session_details = consultation_session_db.get_session_details(session_id)
        
        if session_details:
            return jsonify({
                'success': True,
                'session_details': session_details
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@consultation_session_bp.route('/end/<int:session_id>', methods=['POST'])
def end_consultation_session(session_id):
    """End a consultation session"""
    try:
        data = request.get_json()
        expert_id = data.get('expert_id')
        
        if not expert_id:
            return jsonify({'success': False, 'error': 'Expert ID is required'}), 400
        
        result = consultation_session_service.end_consultation_session(session_id, expert_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@consultation_session_bp.route('/pause/<int:session_id>', methods=['POST'])
def pause_consultation_session(session_id):
    """Pause a consultation session"""
    try:
        result = consultation_session_service.pause_consultation_session(session_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@consultation_session_bp.route('/resume/<int:session_id>', methods=['POST'])
def resume_consultation_session(session_id):
    """Resume a paused consultation session"""
    try:
        result = consultation_session_service.resume_consultation_session(session_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Message Management
@consultation_session_bp.route('/messages/<int:session_id>', methods=['POST'])
def send_message(session_id):
    """Send a message in consultation session"""
    try:
        data = request.get_json()
        
        sender_type = data.get('sender_type')
        sender_id = data.get('sender_id')
        message_text = data.get('message_text')
        message_type = data.get('message_type', 'TEXT')
        
        if not all([sender_type, sender_id, message_text]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        result = consultation_session_service.send_message(
            session_id, sender_type, sender_id, message_text, message_type
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@consultation_session_bp.route('/messages/<int:session_id>', methods=['GET'])
def get_session_messages(session_id):
    """Get messages for a consultation session"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        messages_data = consultation_session_service.get_session_messages(session_id, limit)
        
        return jsonify(messages_data), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Typing Status Management
@consultation_session_bp.route('/typing/<int:session_id>', methods=['POST'])
def set_typing_status(session_id):
    """Update typing status for consultation session"""
    try:
        data = request.get_json()
        
        user_typing = data.get('user_typing')
        expert_typing = data.get('expert_typing')
        
        result = consultation_session_service.set_typing_status(
            session_id, user_typing, expert_typing
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@consultation_session_bp.route('/typing/<int:session_id>', methods=['GET'])
def get_typing_status(session_id):
    """Get typing status for consultation session"""
    try:
        typing_data = consultation_session_service.get_typing_status(session_id)
        
        return jsonify(typing_data), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Call Management
@consultation_session_bp.route('/call/start/<int:session_id>', methods=['POST'])
def start_call(session_id):
    """Start a voice call session"""
    try:
        data = request.get_json()
        started_by = data.get('started_by')
        
        if not started_by:
            return jsonify({'success': False, 'error': 'Started by is required'}), 400
        
        result = consultation_session_service.start_call(session_id, started_by)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@consultation_session_bp.route('/call/end/<int:session_id>', methods=['POST'])
def end_call(session_id):
    """End a voice call session"""
    try:
        data = request.get_json()
        call_id = data.get('call_id')
        
        if not call_id:
            return jsonify({'success': False, 'error': 'Call ID is required'}), 400
        
        result = consultation_session_service.end_call(session_id, call_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@consultation_session_bp.route('/call/status/<int:session_id>', methods=['GET'])
def get_call_status(session_id):
    """Get current call status for consultation session"""
    try:
        call_data = consultation_session_service.get_call_status(session_id)
        
        return jsonify(call_data), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Image Management
@consultation_session_bp.route('/images/<int:session_id>', methods=['POST'])
def add_image(session_id):
    """Add an image to consultation session"""
    try:
        data = request.get_json()
        
        uploaded_by = data.get('uploaded_by')
        file_path = data.get('file_path')
        
        if not all([uploaded_by, file_path]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        result = consultation_session_service.add_image(session_id, uploaded_by, file_path)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@consultation_session_bp.route('/images/<int:session_id>', methods=['GET'])
def get_session_images(session_id):
    """Get all images for a consultation session"""
    try:
        images_data = consultation_session_service.get_session_images(session_id)
        
        return jsonify(images_data), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Notes Management
@consultation_session_bp.route('/notes/<int:session_id>', methods=['POST'])
def add_note(session_id):
    """Add a note to consultation session"""
    try:
        data = request.get_json()
        
        expert_id = data.get('expert_id')
        note_text = data.get('note_text')
        
        if not all([expert_id, note_text]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        result = consultation_session_service.add_note(session_id, expert_id, note_text)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@consultation_session_bp.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update an existing note"""
    try:
        data = request.get_json()
        
        expert_id = data.get('expert_id')
        note_text = data.get('note_text')
        
        if not all([expert_id, note_text]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        result = consultation_session_service.update_note(note_id, expert_id, note_text)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@consultation_session_bp.route('/notes/<int:session_id>', methods=['GET'])
def get_session_notes(session_id):
    """Get all notes for a consultation session"""
    try:
        notes_data = consultation_session_service.get_session_notes(session_id)
        
        return jsonify(notes_data), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Timer Management
@consultation_session_bp.route('/duration/<int:session_id>', methods=['GET'])
def get_session_duration(session_id):
    """Get current session duration"""
    try:
        duration_seconds = consultation_session_db.get_session_duration(session_id)
        
        return jsonify({
            'success': True,
            'duration_seconds': duration_seconds,
            'duration_text': consultation_session_service._format_duration(duration_seconds)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@consultation_session_bp.route('/duration/<int:session_id>', methods=['PUT'])
def update_session_duration(session_id):
    """Update session duration"""
    try:
        success = consultation_session_db.update_session_duration(session_id)
        
        if success:
            duration_seconds = consultation_session_db.get_session_duration(session_id)
            return jsonify({
                'success': True,
                'duration_seconds': duration_seconds,
                'duration_text': consultation_session_service._format_duration(duration_seconds),
                'message': 'Duration updated successfully'
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to update duration'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
