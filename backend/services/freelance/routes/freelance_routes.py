from flask import Blueprint, request, jsonify
from ..services.freelance_service import freelance_service
from ..controllers.freelance_controller import freelance_controller
from ..controllers.ai_controller import ai_controller
from ..controllers.profile_controller import profile_controller
from auth_utils import verify_token, get_current_user_id
from user_db import UserDB
from worker_db import WorkerDB

freelance_bp = Blueprint('freelance', __name__)

# Profile Routes
@freelance_bp.route('/api/freelancer/profile/me', methods=['GET'])
def get_my_profile():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return profile_controller.get_profile(user_id)

@freelance_bp.route('/api/freelancer/profile/update', methods=['PUT'])
def update_my_profile():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return profile_controller.update_profile(user_id)

@freelance_bp.route('/api/freelancer/profile/change-password', methods=['PUT'])
def change_my_password():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return profile_controller.change_password(user_id)

@freelance_bp.route('/api/freelancer/auth/logout', methods=['POST'])
def freelancer_logout():
    return profile_controller.logout()

@freelance_bp.route('/api/freelancer/projects/create', methods=['POST'])
def create_project_v2():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return freelance_controller.create_project(user_id)

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

@freelance_bp.route('/api/freelancer/projects/my-projects', methods=['GET'])
def list_my_projects_v2():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    status = request.args.get('status')
    # Use existing service method
    projects = freelance_service.get_projects_by_client(client_id=user_id, status=status)
    return jsonify({"success": True, "projects": projects}), 200

@freelance_bp.route('/api/freelancer/bookings/my-bookings', methods=['GET'])
def list_my_bookings_v2():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    # Client side bookings
    bookings = freelance_service.get_bookings_by_client(user_id)
    return jsonify({"success": True, "bookings": bookings}), 200

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

@freelance_bp.route('/api/freelance/proposals/reject', methods=['POST'])
def reject_proposal():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    proposal_id = data.get('proposal_id')
    
    success, message = freelance_service.reject_proposal(proposal_id)
    if success:
        return jsonify({"success": True, "message": "Proposal rejected"}), 200
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
    
    stats = freelance_service.get_freelancer_stats(user_id)
    notifications = freelance_service.get_notifications(user_id)
    return jsonify({"stats": stats, "notifications": notifications}), 200

@freelance_bp.route('/api/freelancer/dashboard', methods=['GET'])
def get_freelancer_dashboard():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return freelance_controller.get_dashboard(user_id)

@freelance_bp.route('/api/freelancer/proposals/my-proposals', methods=['GET'])
def get_my_proposals():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    status = request.args.get('status', 'all')
    proposals = freelance_service.get_proposals_by_freelancer(user_id, status)
    return jsonify({"success": True, "proposals": proposals}), 200

@freelance_bp.route('/api/freelancer/proposals/<int:proposal_id>', methods=['DELETE'])
def delete_proposal(proposal_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    success, message = freelance_service.withdraw_proposal(proposal_id, user_id)
    return jsonify({"success": success, "message": message}), 200 if success else 400

@freelance_bp.route('/api/freelancer/bookings/direct', methods=['GET'])
def get_direct_bookings():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    bookings = freelance_service.get_direct_bookings_by_freelancer(user_id)
    return jsonify({"success": True, "bookings": bookings}), 200

@freelance_bp.route('/api/freelancer/bookings/<int:booking_id>/accept', methods=['PUT'])
def accept_booking(booking_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    success, message = freelance_service.update_booking_status(booking_id, user_id, 'ACCEPTED')
    return jsonify({"success": success, "message": message}), 200 if success else 400

@freelance_bp.route('/api/freelancer/work/my-work', methods=['GET'])
def get_my_work():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    work = freelance_service.get_freelancer_active_work(user_id)
    return jsonify({"success": True, "work": work}), 200

@freelance_bp.route('/api/freelancer/work/<int:project_id>/submit-milestone', methods=['POST'])
def freelancer_submit_milestone(project_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    milestone_id = request.json.get('milestoneId')
    success, message = freelance_service.submit_milestone(milestone_id=milestone_id, project_id=project_id)
    return jsonify({"success": success, "message": message}), 200 if success else 400

@freelance_bp.route('/api/freelancer/work/<int:project_id>/complete', methods=['POST'])
def freelancer_complete_project(project_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    success, message = freelance_service.complete_project(project_id, user_id)
    return jsonify({"success": success, "message": message}), 200 if success else 400

@freelance_bp.route('/api/freelancer/work/<int:project_id>/messages', methods=['GET'])
def get_messages(project_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    messages = freelance_service.get_project_messages(project_id)
    return jsonify({"success": True, "messages": messages}), 200

@freelance_bp.route('/api/freelancer/work/<int:project_id>/messages', methods=['POST'])
def freelancer_send_message(project_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    message_text = request.json.get('message')
    success, message = freelance_service.send_message(project_id=project_id, sender_id=user_id, message=message_text)
    return jsonify({"success": success, "message": message}), 200 if success else 400

@freelance_bp.route('/api/freelancer/work/<int:project_id>/deliverables', methods=['POST'])
def upload_deliverable(project_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return freelance_controller.upload_deliverable(user_id, project_id)

@freelance_bp.route('/api/freelancer/work/<int:project_id>/deliverables', methods=['GET'])
def get_deliverables(project_id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    deliverables = freelance_service.get_project_deliverables(project_id)
    return jsonify({"success": True, "deliverables": deliverables}), 200

@freelance_bp.route('/api/freelance/messages', methods=['POST'])
def send_message_v2():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    success, message = freelance_service.send_message(
        contract_id=data.get('contract_id'),
        sender_id=user_id,
        message=data.get('message'),
        file_attachment=data.get('file_attachment')
    )
    if success:
        return jsonify({"success": True}), 200
    return jsonify({"error": message}), 400

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

@freelance_bp.route('/api/freelancer/ai/generate-description', methods=['POST'])
def ai_generate_description():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return ai_controller.generate_description()

@freelance_bp.route('/api/freelancer/ai/suggest-budget', methods=['POST'])
def ai_suggest_budget():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return ai_controller.suggest_budget()

@freelance_bp.route('/api/freelancer/ai/suggest-milestones', methods=['POST'])
def ai_suggest_milestones():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return ai_controller.suggest_milestones()

@freelance_bp.route('/api/freelancer/ai/recommend-freelancers', methods=['POST'])
def ai_recommend_freelancers():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return ai_controller.recommend_freelancers()

@freelance_bp.route('/api/home/featured-freelancers', methods=['GET'])
def get_featured_freelancers():
    try:
        limit = request.args.get('limit', default=3, type=int)
        freelancers = freelance_service.get_featured_freelancers(limit=limit)
        return jsonify({"freelancers": freelancers}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@freelance_bp.route('/api/freelance/skills', methods=['GET'])
def get_skills():
    skills = freelance_service.get_all_skills()
    return jsonify({"skills": skills}), 200

@freelance_bp.route('/api/freelance/provider/skills', methods=['POST'])
def update_skills():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    skill_ids = data.get('skill_ids', [])
    
    if not skill_ids:
        return jsonify({"error": "At least one skill must be selected"}), 400
        
    if freelance_service.update_provider_skills(user_id, skill_ids):
        return jsonify({"success": True}), 200
    return jsonify({"error": "Failed to update skills"}), 500

@freelance_bp.route('/api/freelance/provider/skills', methods=['GET'])
def get_provider_skills():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    skills = freelance_service.get_provider_skills(user_id)
    return jsonify({"skills": skills}), 200

@freelance_bp.route('/api/freelance/workers', methods=['GET'])
def list_workers():
    skill_ids_str = request.args.get('skills')
    skill_ids = []
    if skill_ids_str:
        try:
            skill_ids = [int(sid) for sid in skill_ids_str.split(',')]
        except ValueError:
            return jsonify({"error": "Invalid skill IDs"}), 400
            
    workers = freelance_service.get_workers_by_skills(skill_ids)
    return jsonify({"workers": workers}), 200

@freelance_bp.route('/api/freelance/client/bookings', methods=['GET'])
def list_client_bookings():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    bookings = freelance_service.get_bookings_by_client(user_id)
    return jsonify({"bookings": bookings}), 200

@freelance_bp.route('/api/freelance/bookings', methods=['POST'])
def create_direct_booking():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    freelancer_id = data.get('freelancer_id')
    title = data.get('title')
    description = data.get('description')
    amount = data.get('amount')
    deadline = data.get('deadline')
    
    if not all([freelancer_id, title, amount]):
        return jsonify({"error": "Missing required fields"}), 400
        
    booking_id = freelance_service.create_booking_request(
        client_id=user_id,
        freelancer_id=freelancer_id,
        title=title,
        description=description,
        amount=float(amount),
        deadline=deadline
    )
    
    if booking_id:
        # Audit log for creation
        freelance_service.add_audit_log('BOOKING', booking_id, 'CREATED', None, 'AWAITING', user_id)
        return jsonify({"booking_id": booking_id, "success": True}), 201
    return jsonify({"error": "Failed to create booking"}), 500

@freelance_bp.route('/api/freelance/bookings/respond', methods=['POST'])
def respond_to_booking():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    booking_id = data.get('booking_id')
    status = data.get('status')
    
    if status not in ['ACCEPTED', 'DECLINED']:
        return jsonify({"error": "Invalid status"}), 400
        
    # Verify ownership
    booking = freelance_service.get_booking_by_id(booking_id)
    if not booking or booking['freelancer_id'] != user_id:
        return jsonify({"error": "Booking not found or unauthorized"}), 404
        
    if freelance_service.update_booking_status(booking_id, status, performer_id=user_id):
        return jsonify({"success": True, "message": f"Booking {status.lower()} successfully"}), 200
    return jsonify({"error": "Failed to update booking"}), 500
