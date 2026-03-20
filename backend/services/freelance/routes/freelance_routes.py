from flask import Blueprint, request, jsonify
from ..services.freelance_service import freelance_service
from auth_utils import verify_token
from user_db import UserDB
from worker_db import WorkerDB

freelance_bp = Blueprint('freelance', __name__)

def get_current_user_id():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    username = verify_token(token)
    if not username:
        return None
    user_db = UserDB()
    user = user_db.get_user_by_username(username)
    return user['id'] if user else None

@freelance_bp.route('/api/freelance/projects', methods=['POST'])
def create_project():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    try:
        project_id = freelance_service.create_project(
            client_id=user_id,
            title=data.get('title'),
            description=data.get('description'),
            category=data.get('category'),
            budget_type=data.get('budget_type'),
            budget_amount=data.get('budget_amount'),
            deadline=data.get('deadline'),
            skills=data.get('skills'),
            exp_level=data.get('experience_level')
        )
        return jsonify({"success": True, "project_id": project_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@freelance_bp.route('/api/freelance/projects', methods=['GET'])
def list_projects():
    category = request.args.get('category')
    projects = freelance_service.get_projects(category=category)
    return jsonify({"projects": projects}), 200

@freelance_bp.route('/api/freelance/proposals', methods=['POST'])
def submit_proposal():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    try:
        proposal_id = freelance_service.submit_proposal(
            project_id=data.get('project_id'),
            freelancer_id=user_id,
            price=data.get('proposed_price'),
            delivery_time=data.get('delivery_time'),
            message=data.get('cover_message')
        )
        return jsonify({"success": True, "proposal_id": proposal_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@freelance_bp.route('/api/freelance/my-projects', methods=['GET'])
def list_my_projects():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    projects = freelance_service.get_projects_by_client(client_id=user_id)
    return jsonify({"projects": projects}), 200

@freelance_bp.route('/api/freelance/proposals/accept', methods=['POST'])
def accept_proposal():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    proposal_id = data.get('proposal_id')
    
    if freelance_service.accept_proposal(proposal_id):
        return jsonify({"success": True, "message": "Proposal accepted and contract created"}), 200
    return jsonify({"error": "Failed to accept proposal"}), 400
