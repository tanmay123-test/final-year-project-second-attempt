from flask import Blueprint, request, jsonify
from car_service.worker_auth.worker_db import car_worker_db
from car_service.worker_auth.document_service import document_service

car_admin_bp = Blueprint("car_admin", __name__)


def _json_error(message, code=400):
    return jsonify({"success": False, "error": message}), code


@car_admin_bp.route("/api/car/admin/workers/pending", methods=["GET"])
def get_pending_workers():
    try:
        pending_workers = car_worker_db.get_pending_workers()
        # Attach document count
        for w in pending_workers:
            docs = document_service.get_worker_documents(w["id"], w["worker_type"])
            w["document_count"] = len(docs)
        return jsonify({"success": True, "workers": pending_workers}), 200
    except Exception as e:
        return _json_error(str(e), 500)


@car_admin_bp.route("/api/car/admin/worker/<int:worker_id>/approve", methods=["PUT"])
def approve_worker(worker_id):
    try:
        success = car_worker_db.approve_worker(worker_id)
        if not success:
            return _json_error("Worker not found", 404)
        return jsonify({"success": True}), 200
    except Exception as e:
        return _json_error(str(e), 500)


@car_admin_bp.route("/api/car/admin/worker/<int:worker_id>/reject", methods=["PUT"])
def reject_worker(worker_id):
    try:
        success = car_worker_db.reject_worker(worker_id)
        if not success:
            return _json_error("Worker not found", 404)
        return jsonify({"success": True}), 200
    except Exception as e:
        return _json_error(str(e), 500)


@car_admin_bp.route("/api/car/admin/statistics", methods=["GET"])
def car_admin_statistics():
    try:
        stats = car_worker_db.get_worker_statistics()
        return jsonify({"success": True, "statistics": stats}), 200
    except Exception as e:
        return _json_error(str(e), 500)

@car_admin_bp.route("/api/car/admin/worker/<int:worker_id>/documents", methods=["GET"])
def admin_view_worker_documents(worker_id):
    try:
        worker = car_worker_db.get_worker_by_id(worker_id)
        if not worker:
            return _json_error("Worker not found", 404)
        documents = document_service.get_worker_documents(worker_id, worker["worker_type"])
        return jsonify({
            "success": True,
            "worker": {
                "id": worker["id"],
                "username": worker["username"],
                "worker_type": worker["worker_type"],
                "status": worker["status"]
            },
            "documents": documents
        }), 200
    except Exception as e:
        return _json_error(str(e), 500)
