import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from .services import AskExpertService
from .models import db

ask_expert_bp = Blueprint('ask_expert', __name__, url_prefix='/api/car/expert')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ask_expert_bp.route('/online-experts', methods=['GET'])
def get_online_experts():
    """Get online experts, optionally filtered by category"""
    try:
        category = request.args.get('category')  # Optional category filter
        
        # Get available experts from expert availability system
        from services.car_service.expert_availability_db import expert_availability_db
        from services.car_service.automobile_expert_db import automobile_expert_db
        
        if category:
            # Map category names to database values
            category_mapping = {
                'Body & Interior Expert': 'Body & Interior',
                'Brake & Suspension Expert': 'Brake & Suspension', 
                'Electrical Expert': 'Electrical',
                'Engine Expert': 'Engine',
                'General Expert': 'General'
            }
            
            db_category = category_mapping.get(category, category)
            experts = expert_availability_db.get_available_experts_by_category(db_category)
        else:
            experts = expert_availability_db.get_available_experts()
        
        # Format expert data with proper names and specializations
        formatted_experts = []
        for expert in experts:
            # Get expert details from automobile_expert_db
            expert_details = automobile_expert_db.get_expert_by_id(expert['expert_id'])
            
            formatted_experts.append({
                'id': expert['expert_id'],
                'name': expert_details.get('name', 'Unknown') if expert_details else 'Unknown',
                'specialization': expert_details.get('area_of_expertise', 'N/A') if expert_details else 'N/A',
                'rating': expert.get('rating', 0),
                'experience': expert_details.get('experience_years', 0) if expert_details else 0,
                'category': expert_details.get('area_of_expertise', 'N/A') if expert_details else 'N/A'
            })
        
        return jsonify({'experts': formatted_experts})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ask_expert_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get expert categories"""
    try:
        categories = AskExpertService.get_expert_categories()
        return jsonify({'success': True, 'categories': categories})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@ask_expert_bp.route('/start-request', methods=['POST'])
def start_request():
    """Start a new expert request"""
    try:
        # Get user from form data or JSON (support both)
        user_id = request.form.get('user_id') if request.form else request.json.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Get data from form or JSON (support both)
        if request.form:
            expert_category = request.form.get('expert_category')
            description = request.form.get('description')
        else:
            expert_category = request.json.get('expert_category')
            description = request.json.get('description')
        
        if not expert_category or not description:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Handle file uploads
        image_paths = []
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'ask_expert')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    
                    # Store relative path
                    relative_path = os.path.join('uploads', 'ask_expert', filename)
                    image_paths.append(relative_path)
        
        result = AskExpertService.create_expert_request(
            user_id=user_id,
            expert_category=expert_category,
            description=description,
            image_paths=image_paths
        )
        
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@ask_expert_bp.route('/my-conversations', methods=['GET'])
def get_my_conversations():
    """Get user's conversations"""
    try:
        user_id = request.args.get('user_id')  # This should come from auth
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        conversations = AskExpertService.get_user_conversations(int(user_id))
        return jsonify({'success': True, 'conversations': conversations})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@ask_expert_bp.route('/request/<int:request_id>/messages', methods=['GET'])
def get_messages(request_id):
    """Get all messages for a request"""
    try:
        user_id = request.args.get('user_id')  # This should come from auth
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        messages = AskExpertService.get_request_messages(request_id, int(user_id))
        return jsonify({'messages': messages})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ask_expert_bp.route('/request/<int:request_id>', methods=['GET'])
def get_request(request_id):
    """Get request details"""
    try:
        user_id = request.args.get('user_id')  # This should come from auth
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        details = AskExpertService.get_request_details(request_id, int(user_id))
        
        if not details:
            return jsonify({'success': False, 'error': 'Request not found'}), 404
        
        return jsonify({'success': True, 'data': details})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@ask_expert_bp.route('/request/<int:request_id>/message', methods=['POST'])
def send_message(request_id):
    """Send a message"""
    try:
        user_id = request.json.get('user_id')  # This should come from auth
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        message = request.json.get('message')
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        success = AskExpertService.add_message(
            request_id=request_id,
            sender_type='USER',
            sender_id=int(user_id),
            message=message
        )
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to send message'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@ask_expert_bp.route('/request/<int:request_id>/typing', methods=['POST'])
def update_typing(request_id):
    """Update typing status"""
    try:
        user_id = request.json.get('user_id')  # This should come from auth
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        typing = request.json.get('typing', False)
        
        success = AskExpertService.update_typing_status(
            request_id=request_id,
            user_typing=typing
        )
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to update typing status'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@ask_expert_bp.route('/request/<int:request_id>/call', methods=['POST'])
def start_call(request_id):
    """Start a call session"""
    try:
        user_id = request.json.get('user_id')  # This should come from auth
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        success = AskExpertService.start_call(request_id, int(user_id))
        
        if success:
            return jsonify({'success': True, 'message': 'Call session started'})
        else:
            return jsonify({'success': False, 'error': 'Failed to start call'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@ask_expert_bp.route('/request/<int:request_id>/resolve', methods=['POST'])
def resolve_request(request_id):
    """Mark request as resolved"""
    try:
        user_id = request.json.get('user_id')  # This should come from auth
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        success = AskExpertService.resolve_request(request_id, int(user_id))
        
        if success:
            return jsonify({'success': True, 'message': 'Request resolved'})
        else:
            return jsonify({'success': False, 'error': 'Failed to resolve request'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
