"""
Admin routes for worker management across all services.
"""

from flask import Blueprint, request, jsonify
import psycopg2
import psycopg2.extras
import os
from datetime import datetime
from worker_db import WorkerDB

workers_admin_bp = Blueprint('workers_admin', __name__)
worker_db = WorkerDB()

def get_db_connection():
    """Get database connection for admin operations"""
    return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

@workers_admin_bp.route('/', methods=['GET'])
def get_all_workers():
    """
    Get all workers across all services.
    
    Query Parameters:
    - status: Filter by worker status (pending, approved, rejected, suspended)
    - service: Filter by service type
    """
    try:
        status_filter = request.args.get('status')
        service_filter = request.args.get('service')
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        query = """
            SELECT 
                w.*, COUNT(a.id) as total_appointments
            FROM workers w
            LEFT JOIN appointments a ON w.id = a.worker_id
        """
        
        conditions = []
        params = []
        
        if status_filter:
            conditions.append("w.status = %s")
            params.append(status_filter)
        
        if service_filter:
            conditions.append("w.service ILIKE %s")
            params.append(f"%{service_filter.lower()}%")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " GROUP BY w.id ORDER BY w.created_at DESC"
        
        cursor.execute(query, params)
        workers = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({"workers": workers}), 200
        
    except Exception as e:
        print(f"Error fetching workers: {e}")
        return jsonify({"error": f"Failed to fetch workers: {str(e)}"}), 500

@workers_admin_bp.route('/pending', methods=['GET'])
def get_pending_workers():
    """Get all workers with pending status"""
    try:
        service_filter = request.args.get('service')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        query = "SELECT * FROM workers WHERE (status = 'pending' OR status IS NULL)"
        params = []
        if service_filter:
            query += " AND service ILIKE %s"
            params.append(f"%{service_filter.lower()}%")
        
        cursor.execute(query, params)
        workers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(workers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workers_admin_bp.route('/approved', methods=['GET'])
def get_approved_workers():
    """Get all workers with approved status"""
    try:
        service_filter = request.args.get('service')
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        query = "SELECT * FROM workers WHERE status = 'approved'"
        params = []
        if service_filter:
            query += " AND service ILIKE %s"
            params.append(f"%{service_filter.lower()}%")
        
        cursor.execute(query, params)
        workers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(workers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workers_admin_bp.route('/<int:worker_id>', methods=['GET'])
def get_worker_details(worker_id):
    """
    Get detailed information about a specific worker.
    """
    try:
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get worker appointments
        cursor.execute("""
            SELECT a.*, u.name as user_name
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE a.worker_id = %s
            ORDER BY a.created_at DESC
        """, (worker_id,))
        
        appointments = [dict(row) for row in cursor.fetchall()]
        
        # Get documents
        documents = {
            "profile_photo": worker.get('profile_photo_path'),
            "aadhaar": worker.get('aadhaar_path'),
            "police_verification": worker.get('police_verification_path'),
            "portfolio": worker.get('portfolio_path'),
            "skill_certificate": worker.get('skill_certificate_path'),
            "id_proof": worker.get('degree_path') or worker.get('license_path') or worker.get('aadhaar_path')
        }
        
        conn.close()
        
        worker_details = dict(worker)
        worker_details['appointments'] = appointments
        worker_details['documents'] = documents
        
        return jsonify({"worker": worker_details}), 200
        
    except Exception as e:
        print(f"Error fetching worker details: {e}")
        return jsonify({"error": f"Failed to fetch worker details: {str(e)}"}), 500

@workers_admin_bp.route('/<int:worker_id>/approve', methods=['POST'])
def approve_worker(worker_id):
    """
    Approve a worker.
    """
    try:
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        # In this project, status can be 'pending', 'approved', etc.
        # Let's check the current status in DB
        if worker.get('status') == 'approved':
            return jsonify({"error": "Worker is already approved"}), 400
        
        worker_db.approve_worker(worker_id)
        
        return jsonify({
            "message": "Worker approved successfully",
            "worker_id": worker_id
        }), 200
        
    except Exception as e:
        print(f"Error approving worker: {e}")
        return jsonify({"error": f"Failed to approve worker: {str(e)}"}), 500

@workers_admin_bp.route('/<int:worker_id>/reject', methods=['POST'])
def reject_worker(worker_id):
    """
    Reject a worker.
    """
    try:
        data = request.json or {}
        reason = data.get('rejection_reason')
        
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        worker_db.reject_worker(worker_id, reason)
        
        return jsonify({
            "message": "Worker rejected successfully",
            "worker_id": worker_id
        }), 200
        
    except Exception as e:
        print(f"Error rejecting worker: {e}")
        return jsonify({"error": f"Failed to reject worker: {str(e)}"}), 500

@workers_admin_bp.route('/stats', methods=['GET'])
def get_worker_stats():
    """
    Get worker statistics.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("SELECT COUNT(*) as total FROM workers")
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as pending FROM workers WHERE status = 'pending' OR status IS NULL")
        pending = cursor.fetchone()['pending']
        
        cursor.execute("SELECT COUNT(*) as approved FROM workers WHERE status = 'approved'")
        approved = cursor.fetchone()['approved']
        
        cursor.execute("SELECT AVG(rating) as avg_rating FROM workers WHERE rating IS NOT NULL")
        rating = cursor.fetchone()['avg_rating'] or 0.0
        
        conn.close()
        
        return jsonify({
            "total_workers": total,
            "pending_review": pending,
            "approved_workers": approved,
            "platform_rating": round(float(rating), 1)
        }), 200
    except Exception as e:
        print(f"Error fetching worker stats: {e}")
        return jsonify({"error": str(e)}), 500
