from flask import Blueprint, request, jsonify, send_file, render_template_string
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from auth_utils import verify_token
from user_db import UserDB
from car_service.car_profile_db import car_profile_db
from .models import ask_expert_db
from .services import create_request, add_message, get_messages, mark_resolved, get_pending_images_for_admin, approve_images, reject_images, get_approved_images
from .schemas import serialize_request_row, serialize_message_row
from .upload_system import ModernUploadSystem, create_upload_routes

ask_expert_bp = Blueprint("ask_expert", __name__)
user_db = UserDB()

# Initialize modern upload system
from .services import UPLOAD_DIR
upload_system = ModernUploadSystem(UPLOAD_DIR)


def get_current_user():
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None, ("Authentication required", 401)
    token = auth.split(" ")[1]
    username = verify_token(token)
    if not username:
        return None, ("Invalid or expired token", 401)
    user = user_db.get_user_by_username(username)
    if not user:
        return None, ("User not found", 404)
    return user, None


def is_expert(user_id: int):
    prof = ask_expert_db.get_expert_profile_by_user(user_id)
    if not prof:
        return False, None
    approved = bool(prof[1])
    return approved, prof[0]


@ask_expert_bp.route("/api/car/expert/status", methods=["GET"])
def expert_status():
    """Get current user's expert status"""
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    
    prof = ask_expert_db.get_expert_profile_by_user(user["id"])
    is_expert = prof is not None
    is_approved = bool(prof[1]) if prof else False
    online_status = prof[2] if prof else "offline"
    is_busy = bool(prof[3]) if prof else False
    
    return jsonify({
        "success": True,
        "is_expert": is_expert,
        "is_approved": is_approved,
        "online_status": online_status,
        "is_busy": is_busy
    }), 200


@ask_expert_bp.route("/api/car/expert/request", methods=["POST"])
def api_create_request():
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    description = request.form.get("problem_description", "") or (request.json or {}).get("problem_description", "")
    if not description:
        return jsonify({"error": "problem_description is required"}), 400
    prof = car_profile_db.get_car_profile(user["id"])
    city = prof[2] if prof else None
    if not city:
        return jsonify({"error": "User city not found. Setup car profile first"}), 400
    images = request.files.getlist("images") if request.files else []
    req_id = create_request(user["id"], description, city, images)
    req_row = ask_expert_db.get_request(req_id)
    return jsonify({"success": True, "request": serialize_request_row(req_row)}), 201


@ask_expert_bp.route("/api/car/expert/my-requests", methods=["GET"])
def api_my_requests():
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    rows = ask_expert_db.get_user_requests(user["id"])
    return jsonify({"success": True, "requests": [serialize_request_row(r) for r in rows]}), 200


@ask_expert_bp.route("/api/car/expert/request/<int:req_id>", methods=["GET"])
def api_get_request(req_id):
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    row = ask_expert_db.get_request(req_id)
    if not row:
        return jsonify({"error": "Request not found"}), 404
    approved, expert_profile_id = is_expert(user["id"])
    owner = row[1] == user["id"]
    assigned_to_me = approved and row[2] == expert_profile_id
    if not owner and not assigned_to_me:
        return jsonify({"error": "Forbidden"}), 403
    msgs = get_messages(req_id)
    return jsonify({
        "success": True,
        "request": serialize_request_row(row),
        "messages": [serialize_message_row(m) for m in msgs]
    }), 200


@ask_expert_bp.route("/api/car/expert/request/<int:req_id>/message", methods=["POST"])
def api_post_message(req_id):
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    row = ask_expert_db.get_request(req_id)
    if not row:
        return jsonify({"error": "Request not found"}), 404
    approved, expert_profile_id = is_expert(user["id"])
    is_owner = row[1] == user["id"]
    is_assigned_expert = approved and row[2] == expert_profile_id
    if not (is_owner or is_assigned_expert):
        return jsonify({"error": "Forbidden"}), 403
    data = request.json or {}
    text = data.get("message_text", "")
    if not text:
        return jsonify({"error": "message_text is required"}), 400
    sender_type = "EXPERT" if is_assigned_expert else "USER"
    add_message(req_id, sender_type, user["id"], text)
    return jsonify({"success": True}), 201


@ask_expert_bp.route("/api/car/expert/go-online", methods=["POST"])
def expert_go_online():
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    ask_expert_db.ensure_expert_profile(user["id"])
    prof = ask_expert_db.get_expert_profile_by_user(user["id"])
    if not prof or not bool(prof[1]):
        return jsonify({"error": "Expert not approved"}), 403
    ask_expert_db.set_online(user["id"])
    return jsonify({"success": True}), 200


@ask_expert_bp.route("/api/car/expert/go-offline", methods=["POST"])
def expert_go_offline():
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    ask_expert_db.ensure_expert_profile(user["id"])
    prof = ask_expert_db.get_expert_profile_by_user(user["id"])
    if not prof or not bool(prof[1]):
        return jsonify({"error": "Expert not approved"}), 403
    ask_expert_db.set_offline(user["id"])
    return jsonify({"success": True}), 200


@ask_expert_bp.route("/api/car/expert/incoming", methods=["GET"])
def expert_incoming():
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    prof = ask_expert_db.get_expert_profile_by_user(user["id"])
    if not prof or not bool(prof[1]):
        return jsonify({"error": "Expert not approved"}), 403
    expert_profile_id = prof[0]
    req = ask_expert_db.get_assigned_for_expert(expert_profile_id)
    if not req:
        return jsonify({"success": True, "request": None}), 200
    return jsonify({"success": True, "request": {
        "id": req[0],
        "user_id": req[1],
        "problem_description": req[2],
        "category": req[3],
        "location": req[4],
        "status": req[5],
        "created_at": req[6]
    }}), 200


@ask_expert_bp.route("/api/car/expert/request/<int:req_id>/accept", methods=["POST"])
def expert_accept(req_id):
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    prof = ask_expert_db.get_expert_profile_by_user(user["id"])
    if not prof or not bool(prof[1]):
        return jsonify({"error": "Expert not approved"}), 403
    expert_profile_id = prof[0]
    row = ask_expert_db.get_request(req_id)
    if not row:
        return jsonify({"error": "Request not found"}), 404
    if row[2] != expert_profile_id:
        return jsonify({"error": "Forbidden"}), 403
    ask_expert_db.mark_in_progress(req_id)
    return jsonify({"success": True}), 200


@ask_expert_bp.route("/api/car/expert/register", methods=["POST"])
def register_expert():
    """Register current user as an expert (for testing)"""
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    
    # Create expert profile and auto-approve for testing
    expert_id = ask_expert_db.ensure_expert_profile(user["id"])
    
    # Auto-approve for testing (in production, this would require admin approval)
    conn = ask_expert_db.get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE expert_profiles SET is_approved=1 WHERE id=?", (expert_id,))
    conn.commit()
    conn.close()
    
    return jsonify({
        "success": True,
        "message": "Expert registration successful! You are now approved.",
        "expert_id": expert_id
    }), 201


@ask_expert_bp.route("/api/car/expert/request/<int:req_id>/resolve", methods=["POST"])
def expert_resolve(req_id):
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    prof = ask_expert_db.get_expert_profile_by_user(user["id"])
    if not prof or not bool(prof[1]):
        return jsonify({"error": "Expert not approved"}), 403
    expert_profile_id = prof[0]
    row = ask_expert_db.get_request(req_id)
    if not row:
        return jsonify({"error": "Request not found"}), 404
    if row[2] != expert_profile_id:
        return jsonify({"error": "Forbidden"}), 403
    mark_resolved(req_id)
    ask_expert_db.set_busy(expert_profile_id, False)
    return jsonify({"success": True}), 200


# Admin endpoints for image approval
@ask_expert_bp.route("/api/car/expert/admin/pending-images", methods=["GET"])
def admin_pending_images():
    """Get all pending images for admin review"""
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    
    # Check if user is admin (you may want to add proper admin role check)
    # For now, we'll assume any authenticated user can access (you should secure this)
    
    try:
        pending_requests = get_pending_images_for_admin()
        return jsonify({
            "success": True,
            "pending_requests": pending_requests,
            "total": len(pending_requests)
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get pending images: {str(e)}"}), 500


@ask_expert_bp.route("/api/car/expert/admin/approve-images/<int:req_id>", methods=["POST"])
def admin_approve_images(req_id):
    """Approve images for a request"""
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    
    # Check if user is admin (add proper admin role check)
    
    try:
        success = approve_images(req_id)
        if success:
            return jsonify({
                "success": True,
                "message": f"Images for request {req_id} approved successfully"
            }), 200
        else:
            return jsonify({"error": "No pending images found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to approve images: {str(e)}"}), 500


@ask_expert_bp.route("/api/car/expert/admin/reject-images/<int:req_id>", methods=["POST"])
def admin_reject_images(req_id):
    """Reject images for a request"""
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    
    # Check if user is admin (add proper admin role check)
    
    try:
        success = reject_images(req_id)
        if success:
            return jsonify({
                "success": True,
                "message": f"Images for request {req_id} rejected"
            }), 200
        else:
            return jsonify({"error": "No pending images found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to reject images: {str(e)}"}), 500


@ask_expert_bp.route("/api/car/expert/admin/view-image/<int:req_id>/<filename>", methods=["GET"])
def admin_view_image(req_id, filename):
    """View pending image for admin review"""
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    
    # Check if user is admin
    
    try:
        from .services import UPLOAD_DIR
        pending_dir = os.path.join(UPLOAD_DIR, 'pending', f'req_{req_id}')
        file_path = os.path.join(pending_dir, filename)
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_file(file_path)
        else:
            return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to serve image: {str(e)}"}), 500


@ask_expert_bp.route("/api/car/expert/request/<int:req_id>/approved-images", methods=["GET"])
def get_request_approved_images(req_id):
    """Get approved images for a request (for experts and users)"""
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    
    try:
        # Check if user has access to this request
        row = ask_expert_db.get_request(req_id)
        if not row:
            return jsonify({"error": "Request not found"}), 404
        
        is_owner = row[1] == user["id"]
        approved, expert_profile_id = is_expert(user["id"])
        is_assigned_expert = approved and row[2] == expert_profile_id
        
        if not (is_owner or is_assigned_expert):
            return jsonify({"error": "Forbidden"}), 403
        
        # Get approved images
        approved_images = get_approved_images(req_id)
        image_urls = []
        
        for image_path in approved_images:
            # Create URL for approved image
            image_urls.append({
                "filename": os.path.basename(image_path),
                "url": f"/api/car/expert/approved-image/{req_id}/{os.path.basename(image_path)}"
            })
        
        return jsonify({
            "success": True,
            "images": image_urls,
            "total": len(image_urls)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get approved images: {str(e)}"}), 500


@ask_expert_bp.route("/api/car/expert/approved-image/<int:req_id>/<filename>", methods=["GET"])
def serve_approved_image(req_id, filename):
    """Serve approved image"""
    try:
        from .services import UPLOAD_DIR
        approved_dir = os.path.join(UPLOAD_DIR, 'approved', f'req_{req_id}')
        file_path = os.path.join(approved_dir, filename)
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_file(file_path)
        else:
            return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to serve image: {str(e)}"}), 500


# Modern Upload System Routes
@ask_expert_bp.route("/upload/file-picker", methods=["POST"])
def handle_file_picker():
    """Handle file picker upload"""
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    request_id = request.form.get('request_id')
    
    success, result = upload_system.process_uploaded_file(file, request_id, 'file_picker')
    
    if success:
        return jsonify({
            'success': True,
            'file_info': result
        })
    else:
        return jsonify({'error': result}), 400

@ask_expert_bp.route("/upload/camera", methods=["POST"])
def handle_camera_upload():
    """Handle camera capture"""
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    
    image_data = request.json.get('image_data')
    request_id = request.json.get('request_id')
    
    success, result = upload_system.handle_camera_capture(image_data, request_id)
    
    if success:
        return jsonify({
            'success': True,
            'file_info': result
        })
    else:
        return jsonify({'error': result}), 400

@ask_expert_bp.route("/upload/drag-drop", methods=["POST"])
def handle_drag_drop():
    """Handle drag and drop upload"""
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    
    files = request.files.getlist('files')
    request_id = request.form.get('request_id')
    
    results = upload_system.handle_drag_drop(files, request_id)
    
    return jsonify({
        'success': True,
        'results': results
    })

@ask_expert_bp.route("/upload/mobile", methods=["POST"])
def handle_mobile_upload():
    """Handle mobile app upload"""
    user, err = get_current_user()
    if err:
        return jsonify({"error": err[0]}), err[1]
    
    file = request.files.get('file')
    request_id = request.form.get('request_id')
    metadata = request.form.get('metadata', '{}')
    
    success, result = upload_system.process_uploaded_file(file, request_id, 'mobile')
    
    if success:
        return jsonify({
            'success': True,
            'file_info': result,
            'metadata': metadata
        })
    else:
        return jsonify({'error': result}), 400

@ask_expert_bp.route("/upload/interface", methods=["GET"])
def upload_interface():
    """Serve modern upload interface"""
    try:
        with open(os.path.join(os.path.dirname(__file__), 'upload_interface.html'), 'r') as f:
            html_content = f.read()
        return html_content
    except Exception as e:
        return jsonify({"error": f"Upload interface not available: {str(e)}"}), 500
