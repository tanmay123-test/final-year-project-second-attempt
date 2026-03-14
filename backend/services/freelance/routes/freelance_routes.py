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
    username_or_email = verify_token(token)
    if not username_or_email:
        return None
    
    # 1. Check UserDB (for clients)
    user_db = UserDB()
    user_id = user_db.get_user_by_username(username_or_email)
    if user_id:
        return user_id
        
    # 2. Check WorkerDB (for freelancers)
    worker_db = WorkerDB()
    worker = worker_db.get_worker_by_email(username_or_email)
    if worker:
        return worker['id']
        
    return None

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
            exp_level=data.get('experience_level'),
            milestones=data.get('milestones')
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
        return jsonify({"error": "Unauthorized - Please login again"}), 401
    
    data = request.json
    try:
        # Validate required fields
        project_id = data.get('project_id')
        price = data.get('proposed_price')
        
        if not project_id or not price:
            return jsonify({"error": "Missing required fields: project_id and proposed_price"}), 400

        proposal_id = freelance_service.submit_proposal(
            project_id=int(project_id),
            freelancer_id=user_id,
            price=float(price),
            delivery_time=data.get('delivery_time'),
            message=data.get('cover_message')
        )
        return jsonify({"success": True, "proposal_id": proposal_id}), 201
    except Exception as e:
        print(f"Error in submit_proposal: {str(e)}")
        return jsonify({"error": str(e)}), 400

@freelance_bp.route('/api/freelance/my-projects', methods=['GET'])
def list_my_projects():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    status = request.args.get('status')
    projects = freelance_service.get_projects_by_client(client_id=user_id, status=status)
    return jsonify({"projects": projects}), 200

@freelance_bp.route('/api/freelance/projects/<int:project_id>/proposals', methods=['GET'])
def list_project_proposals(project_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    proposals = freelance_service.get_proposals_by_project(project_id=project_id)
    return jsonify({"proposals": proposals}), 200

@freelance_bp.route('/api/freelance/proposals/accept', methods=['POST'])
def accept_proposal():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    proposal_id = data.get('proposal_id')
    
    success, message = freelance_service.accept_proposal(proposal_id)
    if success:
        return jsonify({"success": True, "message": "Proposal accepted and contract created"}), 200
    return jsonify({"error": message}), 400

@freelance_bp.route('/api/freelance/my-proposals', methods=['GET'])
def list_my_proposals():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    proposals = freelance_service.get_proposals_by_freelancer(freelancer_id=user_id)
    return jsonify({"proposals": proposals}), 200

@freelance_bp.route('/api/freelance/active-work', methods=['GET'])
def list_active_work():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    contracts = freelance_service.get_contracts_by_freelancer(freelancer_id=user_id)
    return jsonify({"contracts": contracts}), 200

@freelance_bp.route('/api/freelance/stats', methods=['GET'])
def get_stats():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    stats = freelance_service.get_freelancer_stats(freelancer_id=user_id)
    notifications = freelance_service.get_notifications(user_id=user_id)
    return jsonify({"stats": stats, "notifications": notifications}), 200

@freelance_bp.route('/api/freelance/milestones/submit', methods=['POST'])
def submit_milestone():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    milestone_id = data.get('milestone_id')
    if freelance_service.submit_milestone(milestone_id):
        return jsonify({"success": True}), 200
    return jsonify({"error": "Failed to submit milestone"}), 400

@freelance_bp.route('/api/freelance/messages', methods=['POST'])
def send_message():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    if freelance_service.send_message(
        contract_id=data.get('contract_id'),
        sender_id=user_id,
        message=data.get('message'),
        file_attachment=data.get('file_attachment')
    ):
        return jsonify({"success": True}), 200
    return jsonify({"error": "Failed to send message"}), 400

# --- Direct Booking Routes ---
@freelance_bp.route('/api/freelance/bookings', methods=['POST'])
def create_booking():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    try:
        booking_id = freelance_service.create_booking_request(
            client_id=user_id,
            freelancer_id=data.get('freelancer_id'),
            title=data.get('title'),
            description=data.get('description'),
            amount=data.get('amount')
        )
        return jsonify({"success": True, "booking_id": booking_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@freelance_bp.route('/api/freelance/my-bookings', methods=['GET'])
def list_my_bookings():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    status = request.args.get('status', 'PENDING')
    bookings = freelance_service.get_booking_requests_by_freelancer(freelancer_id=user_id, status=status)
    return jsonify({"bookings": bookings}), 200

@freelance_bp.route('/api/freelance/bookings/respond', methods=['POST'])
def respond_to_booking():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    booking_id = data.get('booking_id')
    status = data.get('status') # 'ACCEPTED' or 'DECLINED'
    
    if freelance_service.update_booking_status(booking_id, status):
        return jsonify({"success": True}), 200
    return jsonify({"error": "Failed to respond to booking request"}), 400
