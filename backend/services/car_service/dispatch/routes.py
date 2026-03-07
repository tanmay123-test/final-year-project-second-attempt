"""
Car Service Dispatch API Routes
Handles job requests and dispatch operations
"""

import os
import sys
import random
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_utils import verify_token
from services.car_service.job_requests_db import job_requests_db
from services.car_service.dispatch.job_queue import job_queue

dispatch_bp = Blueprint("dispatch", __name__)

def _calculate_earning_from_issue(issue: str) -> float:
    """Calculate estimated earning based on issue description"""
    issue_lower = issue.lower()
    
    # Base rates for different issue types
    if any(keyword in issue_lower for keyword in ['engine', 'motor', 'starting']):
        return 800
    elif any(keyword in issue_lower for keyword in ['brake', 'braking']):
        return 500
    elif any(keyword in issue_lower for keyword in ['battery', 'electrical']):
        return 400
    elif any(keyword in issue_lower for keyword in ['tire', 'puncture', 'wheel']):
        return 350
    elif any(keyword in issue_lower for keyword in ['ac', 'air conditioning', 'cooling']):
        return 600
    elif any(keyword in issue_lower for keyword in ['transmission', 'gear', 'clutch']):
        return 1000
    elif any(keyword in issue_lower for keyword in ['suspension', 'shock', 'strut']):
        return 600
    else:
        return 400  # Default for general issues

def _classify_issue_type(issue: str) -> str:
    """Classify issue type based on description"""
    issue_lower = issue.lower()
    
    if any(keyword in issue_lower for keyword in ['engine', 'motor', 'starting']):
        return 'engine repair'
    elif any(keyword in issue_lower for keyword in ['brake', 'braking']):
        return 'brake service'
    elif any(keyword in issue_lower for keyword in ['battery', 'electrical']):
        return 'electrical'
    elif any(keyword in issue_lower for keyword in ['tire', 'puncture', 'wheel']):
        return 'tire service'
    elif any(keyword in issue_lower for keyword in ['ac', 'air conditioning', 'cooling']):
        return 'ac service'
    elif any(keyword in issue_lower for keyword in ['transmission', 'gear', 'clutch']):
        return 'transmission'
    elif any(keyword in issue_lower for keyword in ['suspension', 'shock', 'strut']):
        return 'suspension'
    else:
        return 'general service'

def _is_emergency_issue(issue: str) -> bool:
    """Check if issue is an emergency"""
    emergency_keywords = ['brake failure', 'engine stopped', 'accident', 'emergency', 
                        'wont start', 'break down', 'stuck', 'dangerous', 'smoke', 
                        'fire', 'leaking', 'overheating']
    
    issue_lower = issue.lower()
    return any(keyword in issue_lower for keyword in emergency_keywords)

@dispatch_bp.route("/api/car/mechanic/jobs", methods=["GET"])
def get_mechanic_jobs():
    """Get pending job requests for a mechanic"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        # Get mechanic from unified worker database
        from services.car_service.car_service_worker_db import car_service_worker_db
        mechanic = car_service_worker_db.get_worker_by_email(email)
        if not mechanic or mechanic.get('role') != 'Mechanic':
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Get real user bookings from booking_db instead of test job requests
        from services.car_service.booking_db import booking_db
        from services.car_service.car_profile_db import car_profile_db
        from user_db import UserDB
        
        # Get jobs assigned to this mechanic
        mechanic_jobs = booking_db.get_mechanic_jobs(mechanic['id'])
        
        # Filter for pending/active jobs only
        pending_jobs = [job for job in mechanic_jobs if job['status'] in ['SEARCHING', 'ACCEPTED']]
        
        # Format jobs for display with real user data
        formatted_jobs = []
        user_db = UserDB()
        
        for job in pending_jobs:
            # Get real user information
            user_info = user_db.get_user_by_id(job['user_id'])
            user_name = user_info.get('name', f"User {job['user_id']}") if user_info else f"User {job['user_id']}"
            user_email = user_info.get('email', 'No email') if user_info else 'No email'
            
            # Get car service profile for additional details (phone, city, etc.)
            user_profile = car_profile_db.get_car_profile(job['user_id'])
            user_phone = user_profile.get('emergency_contact_phone', 'No phone') if user_profile else 'No phone'
            user_city = user_profile.get('city', 'Unknown') if user_profile else 'Unknown'
            
            # Get car information
            car_info = car_profile_db.get_car_by_id(job['car_id'])
            car_model = f"{car_info.get('brand', 'Unknown')} {car_info.get('model', 'Unknown')}" if car_info else "Unknown Car"
            
            # Calculate estimated earning based on issue type
            estimated_earning = _calculate_earning_from_issue(job['issue'])
            
            formatted_job = {
                'id': job['id'],
                'user_name': user_name,
                'user_email': user_email,
                'user_phone': user_phone,
                'car_model': car_model,
                'issue': job['issue'],
                'issue_type': _classify_issue_type(job['issue']),
                'user_city': user_city,
                'distance_km': 5.0,  # Default distance - would be calculated with real GPS
                'eta_minutes': 15,   # Default ETA - would be calculated with real routing
                'estimated_earning': estimated_earning,
                'priority': 'EMERGENCY' if _is_emergency_issue(job['issue']) else 'NORMAL',
                'assignment_reason': 'User booking assignment',
                'created_at': job['created_at'],
                'response_deadline': (datetime.now() + timedelta(minutes=30)).isoformat()
            }
            formatted_jobs.append(formatted_job)
        
        return jsonify({"jobs": formatted_jobs}), 200
        
    except Exception as e:
        print(f"❌ Get mechanic jobs error: {e}")
        return jsonify({"error": "Failed to get jobs"}), 500

@dispatch_bp.route("/api/car/mechanic/job/accept", methods=["POST"])
def accept_job():
    """Accept a job request"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        # Get mechanic from unified worker database
        from services.car_service.car_service_worker_db import car_service_worker_db
        mechanic = car_service_worker_db.get_worker_by_email(email)
        if not mechanic or mechanic.get('role') != 'Mechanic':
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Get job ID
        job_id = request.json.get("job_id")
        if not job_id:
            return jsonify({"error": "Job ID is required"}), 400
        
        # Accept job using real booking system
        from services.car_service.booking_db import booking_db
        booking_db.update_job_status(job_id, "ACCEPTED", "Job accepted by mechanic")
        
        # Set mechanic to busy in worker database
        car_service_worker_db.set_busy(mechanic['id'])
        
        return jsonify({
            "success": True,
            "message": "Job accepted",
            "status": "BUSY",
            "note": "Status changed to BUSY - You will not receive new jobs until current job completes"
        }), 200
        
    except Exception as e:
        print(f"❌ Accept job error: {e}")
        return jsonify({"error": "Failed to accept job"}), 500

@dispatch_bp.route("/api/car/mechanic/job/reject", methods=["POST"])
def reject_job():
    """Reject a job request"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        # Get mechanic from unified worker database
        from services.car_service.car_service_worker_db import car_service_worker_db
        mechanic = car_service_worker_db.get_worker_by_email(email)
        if not mechanic or mechanic.get('role') != 'Mechanic':
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Get job ID and reason
        job_id = request.json.get("job_id")
        reason = request.json.get("reason", "Mechanic unavailable")
        
        if not job_id:
            return jsonify({"error": "Job ID is required"}), 400
        
        # Reject job using real booking system
        from services.car_service.booking_db import booking_db
        booking_db.update_job_status(job_id, "CANCELLED", f"Rejected by mechanic: {reason}")
        
        return jsonify({
            "success": True,
            "message": "Job rejected",
            "note": "Job cancelled and marked as unavailable"
        }), 200
        
    except Exception as e:
        print(f"❌ Reject job error: {e}")
        return jsonify({"error": "Failed to reject job"}), 500

@dispatch_bp.route("/api/car/mechanic/job/complete", methods=["POST"])
def complete_job():
    """Complete a job"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        # Get mechanic from unified worker database
        from services.car_service.car_service_worker_db import car_service_worker_db
        mechanic = car_service_worker_db.get_worker_by_email(email)
        if not mechanic or mechanic.get('role') != 'Mechanic':
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Get job ID
        job_id = request.json.get("job_id")
        if not job_id:
            return jsonify({"error": "Job ID is required"}), 400
        
        # Complete job using real booking system
        from services.car_service.booking_db import booking_db
        booking_db.update_job_status(job_id, "COMPLETED", "Job completed by mechanic")
        
        # Set mechanic to available in worker database
        car_service_worker_db.set_available(mechanic['id'])
        
        return jsonify({
            "success": True,
            "message": "Job completed",
            "status": "ONLINE",
            "note": "Status changed to ONLINE - You can now receive new jobs"
        }), 200
        
    except Exception as e:
        print(f"❌ Complete job error: {e}")
        return jsonify({"error": "Failed to complete job"}), 500

@dispatch_bp.route("/api/car/mechanic/job/statistics", methods=["GET"])
def get_job_statistics():
    """Get job statistics for a mechanic"""
    try:
        # Get mechanic from token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"error": "Invalid token"}), 401
        
        # Get mechanic from unified worker database
        from services.car_service.car_service_worker_db import car_service_worker_db
        mechanic = car_service_worker_db.get_worker_by_email(email)
        if not mechanic or mechanic.get('role') != 'Mechanic':
            return jsonify({"error": "Mechanic not found"}), 404
        
        # Get statistics
        stats = job_queue.get_job_statistics(mechanic['id'])
        
        return jsonify({"statistics": stats}), 200
        
    except Exception as e:
        print(f"❌ Get job statistics error: {e}")
        return jsonify({"error": "Failed to get statistics"}), 500

@dispatch_bp.route("/api/car/dispatch/assign-job", methods=["POST"])
def assign_job():
    """Assign a job to a mechanic (for testing)"""
    try:
        # Get job details
        user_id = request.json.get("user_id", 1)
        
        # Create more realistic test data with different users
        import random
        test_users = [
            {"name": "Rahul Sharma", "car": "Honda City", "issue": "Brake failure", "city": "Mumbai"},
            {"name": "Priya Patel", "car": "Hyundai i20", "issue": "Battery dead", "city": "Pune"},
            {"name": "Amit Kumar", "car": "Maruti Dzire", "issue": "AC not working", "city": "Thane"},
            {"name": "Sneha Reddy", "car": "Toyota Innova", "issue": "Engine noise", "city": "Mumbai"},
            {"name": "Vikram Singh", "car": "Tata Nexon", "issue": "Puncture", "city": "Navi Mumbai"}
        ]
        
        # Use provided data or random test data
        if request.json:
            user_name = request.json.get("user_name", test_users[0]["name"])
            car_model = request.json.get("car_model", test_users[0]["car"])
            issue = request.json.get("issue", test_users[0]["issue"])
            issue_type = request.json.get("issue_type", "engine repair")
            user_city = request.json.get("user_city", test_users[0]["city"])
        else:
            # Use random test data for variety
            test_user = random.choice(test_users)
            user_name = test_user["name"]
            car_model = test_user["car"]
            issue = test_user["issue"]
            issue_type = "engine repair" if "engine" in issue.lower() else "general repair"
            user_city = test_user["city"]
        
        # Assign job
        job_id = job_queue.assign_job_to_mechanic(
            user_id=user_id,
            user_name=user_name,
            car_model=car_model,
            issue=issue,
            issue_type=issue_type,
            user_city=user_city
        )
        
        if job_id:
            return jsonify({
                "success": True,
                "message": "Job assigned successfully",
                "job_id": job_id
            }), 200
        else:
            return jsonify({"error": "No available mechanics"}), 404
        
    except Exception as e:
        print(f"❌ Assign job error: {e}")
        return jsonify({"error": "Failed to assign job"}), 500

@dispatch_bp.route("/api/car/dispatch/check-expired", methods=["POST"])
def check_expired_jobs():
    """Check and reassign expired jobs"""
    try:
        job_queue.check_expired_jobs()
        return jsonify({
            "success": True,
            "message": "Expired jobs checked and reassigned"
        }), 200
        
    except Exception as e:
        print(f"❌ Check expired jobs error: {e}")
        return jsonify({"error": "Failed to check expired jobs"}), 500
