from flask import Blueprint, request, jsonify
from worker_db import WorkerDB
from email_service import send_email

admin_bp = Blueprint("admin", __name__)
worker_db = WorkerDB()

# ================= PENDING WORKERS =================

@admin_bp.route("/admin/workers/pending", methods=["GET"])
def pending_workers():
    service = request.args.get('service')
    workers = worker_db.get_pending_workers(service)
    return jsonify(workers), 200

# ================= APPROVE WORKER =================

@admin_bp.route("/admin/worker/approve/<int:worker_id>", methods=["POST"])
def approve_worker(worker_id):
    worker = worker_db.get_worker_by_id(worker_id)
    if not worker:
        return jsonify({"error": "Worker not found"}), 404

    worker_db.approve_worker(worker_id)

    send_email(
        to_email=worker["email"],
        subject="✅ ExpertEase Verification Approved",
        body=f"""
Hello {worker['full_name']},

Your documents have been verified successfully.

You are now APPROVED as a healthcare professional on ExpertEase.

You may now login and start accepting appointments.

— ExpertEase Team
"""
    )

    return jsonify({"msg": "Worker approved & email sent"}), 200

# ================= REJECT WORKER =================

@admin_bp.route("/admin/worker/reject/<int:worker_id>", methods=["POST"])
def reject_worker(worker_id):
    worker = worker_db.get_worker_by_id(worker_id)
    if not worker:
        return jsonify({"error": "Worker not found"}), 404

    worker_db.reject_worker(worker_id)

    send_email(
        to_email=worker["email"],
        subject="❌ ExpertEase Verification Rejected",
        body=f"""
Hello {worker['full_name']},

Unfortunately, your verification request has been rejected.

You may re-apply after correcting the documents.

— ExpertEase Team
"""
    )

    return jsonify({"msg": "Worker rejected & email sent"}), 200
