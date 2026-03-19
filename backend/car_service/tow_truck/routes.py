"""
Tow Truck API Routes
API endpoints for tow truck operations
"""

from flask import Blueprint, request, jsonify

tow_bp = Blueprint("tow_bp", __name__)

@tow_bp.route("/api/car/tow/go-online", methods=["POST"]) 
def go_online(): 
    data = request.json 
    worker_id = data.get("worker_id") 

    from .services import set_online 
    set_online(worker_id) 

    return jsonify({"message": "Now ONLINE"}) 

@tow_bp.route("/api/car/tow/go-offline", methods=["POST"]) 
def go_offline(): 
    data = request.json 
    worker_id = data.get("worker_id") 

    from .services import set_offline 
    set_offline(worker_id) 

    return jsonify({"message": "Now OFFLINE"}) 

@tow_bp.route("/api/car/tow/requests", methods=["GET"]) 
def get_requests(): 
    from .services import fetch_requests 
    data = fetch_requests() 
    return jsonify(data) 

@tow_bp.route("/api/car/tow/active-jobs", methods=["GET"])
def active_jobs():
    worker_id = request.args.get("worker_id")
    if not worker_id:
        return jsonify({"error": "worker_id is required"}), 400
    from .services import fetch_active_jobs
    data = fetch_active_jobs(worker_id)
    return jsonify(data)

@tow_bp.route("/api/car/tow/earnings", methods=["GET"])
def earnings():
    worker_id = request.args.get("worker_id")
    if not worker_id:
        return jsonify({"error": "worker_id is required"}), 400
    from .services import fetch_earnings
    data = fetch_earnings(worker_id)
    return jsonify(data)

@tow_bp.route("/api/car/tow/accept", methods=["POST"])
def accept_tow_job():
    data = request.json
    worker_id = data.get("worker_id")
    request_id = data.get("request_id")
    from .services import accept_job
    res = accept_job(worker_id, request_id)
    return jsonify(res)

@tow_bp.route("/api/car/tow/start", methods=["POST"])
def start_tow_job():
    data = request.json
    worker_id = data.get("worker_id")
    job_id = data.get("job_id")
    otp = data.get("otp")
    from .services import start_job
    res = start_job(worker_id, job_id, otp)
    return jsonify(res)

@tow_bp.route("/api/car/tow/complete", methods=["POST"])
def complete_tow_job():
    data = request.json
    worker_id = data.get("worker_id")
    job_id = data.get("job_id")
    from .services import complete_job
    res = complete_job(worker_id, job_id)
    return jsonify(res)

@tow_bp.route("/api/car/tow/job-status/<int:request_id>", methods=["GET"])
def job_status(request_id):
    from .services import get_job_status
    res = get_job_status(request_id)
    return jsonify(res)

@tow_bp.route("/api/car/tow/create-request", methods=["POST"])
def create_tow_request():
    data = request.json
    from .db import TowTruckDB
    db = TowTruckDB()
    req_id = db.create_tow_request(
        user_id=data.get('user_id'),
        pickup_location=data.get('pickup'),
        drop_location=data.get('drop'),
        vehicle_type=data.get('vehicle'),
        vehicle_condition=data.get('condition', 'Unknown'),
        distance=data.get('distance', 0),
        estimated_earning=data.get('earning', 500)
    )
    return jsonify({"success": True, "request_id": req_id})

