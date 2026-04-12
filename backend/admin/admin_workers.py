"""
Admin routes for worker management across all services.
"""

from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime
from worker_db import WorkerDB

workers_admin_bp = Blueprint('workers_admin', __name__, url_prefix='/workers')
worker_db = WorkerDB()

def get_db_connection():
    """Get database connection for admin operations"""
    conn = sqlite3.connect('expertease.db')
    conn.row_factory = sqlite3.Row
    return conn

@workers_admin_bp.route('/', methods=['GET'])
def get_all_workers():
    """
    Get all workers across all services.
    
    Query Parameters:
    - status: Filter by worker status (pending, approved, rejected, suspended)
    - service: Filter by service type
    
    Returns:
    {
        "workers": [
            {
                "id": 1,
                "full_name": "Dr. John Doe",
                "email": "john@example.com",
                "phone": "1234567890",
                "service": "healthcare",
                "specialization": "Cardiology",
                "experience": 5,
                "rating": 4.5,
                "status": "approved",
                "created_at": "2024-01-01 10:00:00",
                "total_appointments": 50,
                "wallet_balance": 5000.00
            }
        ]
    }
    """
    try:
        status_filter = request.args.get('status')
        service_filter = request.args.get('service')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                w.*, COUNT(a.id) as total_appointments
            FROM workers w
            LEFT JOIN appointments a ON w.id = a.worker_id
        """
        
        conditions = []
        params = []
        
        if status_filter:
            conditions.append("w.status = ?")
            params.append(status_filter)
        
        if service_filter:
            conditions.append("w.service LIKE ?")
            params.append(f"%{service_filter}%")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " GROUP BY w.id ORDER BY w.created_at DESC"
        
        cursor.execute(query, params)
        workers = []
        
        for row in cursor.fetchall():
            worker = dict(row)
            workers.append(worker)
        
        conn.close()
        
        return jsonify({"workers": workers}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch workers: {str(e)}"}), 500

@workers_admin_bp.route('/<int:worker_id>', methods=['GET'])
def get_worker_details(worker_id):
    """
    Get detailed information about a specific worker.
    
    Returns:
    {
        "worker": {
            "id": 1,
            "full_name": "Dr. John Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "service": "healthcare",
            "specialization": "Cardiology",
            "experience": 5,
            "clinic_location": "City Hospital",
            "rating": 4.5,
            "status": "approved",
            "created_at": "2024-01-01 10:00:00",
            "appointments": [...],
            "wallet_balance": 5000.00,
            "documents": {...}
        }
    }
    """
    try:
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get worker appointments
        cursor.execute("""
            SELECT a.*, u.name as user_name
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE a.worker_id = ?
            ORDER BY a.created_at DESC
        """, (worker_id,))
        
        appointments = [dict(row) for row in cursor.fetchall()]
        
        # Get documents (simulated)
        documents = {
            "profile_photo": f"/uploads/worker_{worker_id}_profile.jpg",
            "aadhaar": f"/uploads/worker_{worker_id}_aadhaar.jpg",
            "id_proof": f"/uploads/worker_{worker_id}_id.pdf"
        }
        
        if worker.get('service') == 'healthcare':
            documents.update({
                "degree_certificate": f"/uploads/worker_{worker_id}_degree.pdf",
                "medical_license": f"/uploads/worker_{worker_id}_license.pdf"
            })
        
        conn.close()
        
        worker_details = dict(worker)
        worker_details['appointments'] = appointments
        worker_details['documents'] = documents
        
        return jsonify({"worker": worker_details}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch worker details: {str(e)}"}), 500

@workers_admin_bp.route('/<int:worker_id>/approve', methods=['POST'])
def approve_worker(worker_id):
    """
    Approve a worker.
    
    Returns:
    {
        "message": "Worker approved successfully",
        "worker_id": 1
    }
    """
    try:
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        if worker.get('status') != 'pending':
            return jsonify({"error": "Worker is not in pending status"}), 400
        
        worker_db.approve_worker(worker_id)
        
        return jsonify({
            "message": "Worker approved successfully",
            "worker_id": worker_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to approve worker: {str(e)}"}), 500

@workers_admin_bp.route('/<int:worker_id>/reject', methods=['POST'])
def reject_worker(worker_id):
    """
    Reject a worker with reason.
    
    Request Body:
    {
        "rejection_reason": "Documents not verified"
    }
    
    Returns:
    {
        "message": "Worker rejected successfully",
        "worker_id": 1,
        "rejection_reason": "Documents not verified"
    }
    """
    try:
        data = request.get_json()
        if not data or not data.get('rejection_reason'):
            return jsonify({"error": "Rejection reason is required"}), 400
        
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        if worker.get('status') != 'pending':
            return jsonify({"error": "Worker is not in pending status"}), 400
        
        # Reject the worker
        rejection_reason = data.get('rejection_reason')
        worker_db.reject_worker(worker_id, rejection_reason)
        
        print(f"Worker {worker_id} rejected. Reason: {rejection_reason}")
        
        return jsonify({
            "message": "Worker rejected successfully",
            "worker_id": worker_id,
            "rejection_reason": rejection_reason
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to reject worker: {str(e)}"}), 500

@workers_admin_bp.route('/<int:worker_id>/suspend', methods=['POST'])
def suspend_worker(worker_id):
    """
    Suspend an approved worker.
    
    Returns:
    {
        "message": "Worker suspended successfully",
        "worker_id": 1
    }
    """
    try:
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        if worker.get('status') != 'approved':
            return jsonify({"error": "Worker is not in approved status"}), 400
        
        worker_db.update_worker_status(worker_id, 'suspended')
        
        return jsonify({
            "message": "Worker suspended successfully",
            "worker_id": worker_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to suspend worker: {str(e)}"}), 500

@workers_admin_bp.route('/<int:worker_id>/unsuspend', methods=['POST'])
def unsuspend_worker(worker_id):
    """
    Unsuspend a suspended worker.
    
    Returns:
    {
        "message": "Worker unsuspended successfully",
        "worker_id": 1
    }
    """
    try:
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        if worker.get('status') != 'suspended':
            return jsonify({"error": "Worker is not in suspended status"}), 400
        
        worker_db.update_worker_status(worker_id, 'approved')
        
        return jsonify({
            "message": "Worker unsuspended successfully",
            "worker_id": worker_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to unsuspend worker: {str(e)}"}), 500

@workers_admin_bp.route('/<int:worker_id>/wallet/update', methods=['POST'])
def update_worker_wallet(worker_id):
    """
    Update worker wallet balance.
    
    Request Body:
    {
        "amount": 1000.00,
        "transaction_type": "credit|debit",
        "reason": "Payment for services"
    }
    
    Returns:
    {
        "message": "Wallet updated successfully",
        "worker_id": 1,
        "new_balance": 6000.00
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        amount = data.get('amount')
        transaction_type = data.get('transaction_type')
        reason = data.get('reason', 'Wallet update')
        
        if not amount or not transaction_type:
            return jsonify({"error": "Amount and transaction type required"}), 400
        
        if transaction_type not in ['credit', 'debit']:
            return jsonify({"error": "Invalid transaction type"}), 400
        
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        # Update wallet balance
        if transaction_type == 'credit':
            worker_db.update_wallet_balance(worker_id, amount)
        else:
            worker_db.update_wallet_balance(worker_id, -amount)
        
        # Get updated balance
        updated_worker = worker_db.get_worker_by_id(worker_id)
        new_balance = updated_worker.get('wallet_balance', 0)
        
        return jsonify({
            "message": "Wallet updated successfully",
            "worker_id": worker_id,
            "new_balance": new_balance
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to update wallet: {str(e)}"}), 500

@workers_admin_bp.route('/stats', methods=['GET'])
def get_worker_stats():
    """
    Get worker statistics across all services.
    
    Returns:
    {
        "stats": {
            "total_workers": 500,
            "pending_workers": 50,
            "approved_workers": 400,
            "rejected_workers": 30,
            "suspended_workers": 20,
            "workers_by_service": {
                "healthcare": 200,
                "housekeeping": 150,
                "freelance": 100,
                "car_service": 80,
                "money_management": 50
            },
            "new_this_month": 25
        }
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute("SELECT COUNT(*) as total FROM workers")
        total_workers = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as pending FROM workers WHERE status = 'pending'")
        pending_workers = cursor.fetchone()['pending']
        
        cursor.execute("SELECT COUNT(*) as approved FROM workers WHERE status = 'approved'")
        approved_workers = cursor.fetchone()['approved']
        
        cursor.execute("SELECT COUNT(*) as rejected FROM workers WHERE status = 'rejected'")
        rejected_workers = cursor.fetchone()['rejected']
        
        cursor.execute("SELECT COUNT(*) as suspended FROM workers WHERE status = 'suspended'")
        suspended_workers = cursor.fetchone()['suspended']
        
        # Get workers by service
        cursor.execute("SELECT service, COUNT(*) as count FROM workers GROUP BY service")
        workers_by_service = {}
        for row in cursor.fetchall():
            service = row['service']
            if ',' in service:
                services = [s.strip() for s in service.split(',')]
                for s in services:
                    workers_by_service[s] = workers_by_service.get(s, 0) + row['count']
            else:
                workers_by_service[service] = row['count']
        
        conn.close()
        
        stats = {
            "total_workers": total_workers,
            "pending_workers": pending_workers,
            "approved_workers": approved_workers,
            "rejected_workers": rejected_workers,
            "suspended_workers": suspended_workers,
            "workers_by_service": workers_by_service,
            "new_this_month": 25  # Simplified
        }
        
        return jsonify({"stats": stats}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch worker stats: {str(e)}"}), 500
