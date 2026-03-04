"""
Super Admin Routes Module
Complete admin backend with authentication and dashboard
"""
from flask import Blueprint, request, jsonify
from functools import wraps

from admin_db import admin_db
from admin_auth import admin_required, generate_admin_token, verify_admin_token
from user_db import UserDB
from worker_db import WorkerDB
from appointment_db import AppointmentDB

# Initialize databases
user_db = UserDB()
worker_db = WorkerDB()
appt_db = AppointmentDB()

# Create blueprint
super_admin_bp = Blueprint("super_admin", __name__)

# Platform commission configuration
PLATFORM_COMMISSION = 0.20  # 20%

# ================= AUTHENTICATION ROUTES =================

@super_admin_bp.route("/admin/login", methods=["POST"])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        # Get admin from database
        admin = admin_db.get_admin_by_username(username)
        if not admin:
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Verify password
        if not admin_db.verify_password(password, admin['password_hash']):
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Check if admin is active
        if not admin.get('is_active', True):
            return jsonify({"error": "Admin account deactivated"}), 401
        
        # Update last login
        admin_db.update_last_login(admin['id'])
        
        # Generate JWT token
        token = generate_admin_token(username)
        
        return jsonify({
            "success": True,
            "token": token,
            "admin": {
                "id": admin['id'],
                "username": admin['username'],
                "email": admin.get('email'),
                "full_name": admin.get('full_name'),
                "role": admin.get('role'),
                "last_login": admin.get('last_login')
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Login failed", "details": str(e)}), 500

@super_admin_bp.route("/admin/verify-token", methods=["POST"])
def verify_admin_token_endpoint():
    """Verify admin token endpoint"""
    try:
        data = request.json
        token = data.get('token', '')
        
        if not token:
            return jsonify({"error": "Token required"}), 400
        
        admin, error = verify_admin_token(token)
        if error:
            return jsonify({"error": error}), 401
        
        return jsonify({
            "success": True,
            "admin": {
                "id": admin['id'],
                "username": admin['username'],
                "email": admin.get('email'),
                "full_name": admin.get('full_name'),
                "role": admin.get('role')
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Token verification failed", "details": str(e)}), 500

# ================= DASHBOARD STATISTICS =================

@super_admin_bp.route("/admin/dashboard/stats", methods=["GET"])
@admin_required
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get user statistics
        conn = user_db.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        conn.close()
        
        # Get worker statistics
        conn = worker_db.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM workers")
        total_workers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM workers WHERE status='pending'")
        pending_workers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM workers WHERE status='approved'")
        approved_workers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM workers WHERE status='rejected'")
        rejected_workers = cursor.fetchone()[0]
        conn.close()
        
        # Get appointment statistics
        conn = appt_db.get_conn()
        cursor = conn.cursor()
        
        # Today's appointments
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM appointments WHERE DATE(booking_date)=?", (today,))
        today_appointments = cursor.fetchone()[0]
        
        # Total appointments
        cursor.execute("SELECT COUNT(*) FROM appointments")
        total_appointments = cursor.fetchone()[0]
        
        # Completed appointments
        cursor.execute("SELECT COUNT(*) FROM appointments WHERE status='completed'")
        completed_appointments = cursor.fetchone()[0]
        
        conn.close()
        
        # Placeholder revenue calculations (will be implemented with payment system)
        total_revenue = 0
        total_commission = 0
        
        return jsonify({
            "success": True,
            "stats": {
                "users": {
                    "total": total_users,
                    "growth": "+12%"  # Placeholder
                },
                "workers": {
                    "total": total_workers,
                    "pending": pending_workers,
                    "approved": approved_workers,
                    "rejected": rejected_workers
                },
                "appointments": {
                    "total": total_appointments,
                    "today": today_appointments,
                    "completed": completed_appointments,
                    "pending": total_appointments - completed_appointments
                },
                "revenue": {
                    "total": total_revenue,
                    "commission": total_commission,
                    "pending": 0  # Placeholder for pending payments
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch statistics", "details": str(e)}), 500

@super_admin_bp.route("/admin/dashboard/recent-activity", methods=["GET"])
@admin_required
def get_recent_activity():
    """Get recent platform activity"""
    try:
        # Get recent appointments
        conn = appt_db.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_name, worker_id, booking_date, status, created_at
            FROM appointments 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        recent_appointments = []
        for row in cursor.fetchall():
            recent_appointments.append({
                "id": row[0],
                "user_name": row[1],
                "worker_id": row[2],
                "booking_date": row[3],
                "status": row[4],
                "created_at": row[5],
                "type": "appointment"
            })
        
        conn.close()
        
        # Get recent worker registrations
        conn = worker_db.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, full_name, email, specialization, status, created_at
            FROM workers 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        recent_workers = []
        for row in cursor.fetchall():
            recent_workers.append({
                "id": row[0],
                "full_name": row[1],
                "email": row[2],
                "specialization": row[3],
                "status": row[4],
                "created_at": row[5],
                "type": "worker_registration"
            })
        
        conn.close()
        
        # Combine and sort by date
        all_activity = recent_appointments + recent_workers
        all_activity.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({
            "success": True,
            "activity": all_activity[:15]  # Return latest 15 activities
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch recent activity", "details": str(e)}), 500

# ================= PLATFORM MANAGEMENT =================

@super_admin_bp.route("/admin/platform/commission", methods=["GET"])
@admin_required
def get_platform_commission():
    """Get platform commission settings"""
    return jsonify({
        "success": True,
        "commission": {
            "percentage": PLATFORM_COMMISSION * 100,
            "decimal": PLATFORM_COMMISSION,
            "description": f"{PLATFORM_COMMISSION * 100}% platform commission on all transactions"
        }
    }), 200

@super_admin_bp.route("/admin/platform/commission", methods=["PUT"])
@admin_required
def update_platform_commission():
    """Update platform commission (super admin only)"""
    try:
        admin = request.current_admin
        
        # Only super admin can update commission
        if admin.get('role') != 'superadmin':
            return jsonify({"error": "Super admin access required"}), 403
        
        data = request.json
        commission_percentage = data.get('percentage', 20)
        
        if not isinstance(commission_percentage, (int, float)) or commission_percentage < 0 or commission_percentage > 100:
            return jsonify({"error": "Invalid commission percentage"}), 400
        
        # Update commission in config (this would typically update a database table)
        global PLATFORM_COMMISSION
        PLATFORM_COMMISSION = commission_percentage / 100
        
        return jsonify({
            "success": True,
            "commission": {
                "percentage": commission_percentage,
                "decimal": PLATFORM_COMMISSION
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to update commission", "details": str(e)}), 500

# ================= WORKER MANAGEMENT =================

@super_admin_bp.route("/admin/workers", methods=["GET"])
@admin_required
def get_all_workers():
    """Get all workers with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        status = request.args.get('status', '')
        
        offset = (page - 1) * limit
        
        conn = worker_db.get_conn()
        cursor = conn.cursor()
        
        query = "SELECT * FROM workers"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        workers = [dict(row) for row in cursor.fetchall()]
        
        # Remove sensitive info
        for worker in workers:
            worker.pop('password', None)
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM workers"
        if status:
            count_query += " WHERE status = ?"
            cursor.execute(count_query, [status] if status else [])
        else:
            cursor.execute(count_query)
        
        total = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            "success": True,
            "workers": workers,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch workers", "details": str(e)}), 500

@super_admin_bp.route("/admin/workers/pending", methods=["GET"])
@admin_required
def get_pending_workers():
    """Get pending workers for approval"""
    try:
        workers = worker_db.get_pending_workers()
        return jsonify({
            "success": True,
            "workers": workers
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch pending workers", "details": str(e)}), 500

@super_admin_bp.route("/admin/worker/<int:worker_id>/approve", methods=["POST"])
@admin_required
def approve_worker(worker_id):
    """Approve worker application"""
    try:
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        worker_db.approve_worker(worker_id)
        
        return jsonify({
            "success": True,
            "message": "Worker approved successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to approve worker", "details": str(e)}), 500

@super_admin_bp.route("/admin/worker/<int:worker_id>/reject", methods=["POST"])
@admin_required
def reject_worker(worker_id):
    """Reject worker application"""
    try:
        data = request.json
        reason = data.get('reason', 'Application does not meet requirements')
        
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        worker_db.reject_worker(worker_id)
        
        return jsonify({
            "success": True,
            "message": "Worker rejected successfully",
            "reason": reason
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to reject worker", "details": str(e)}), 500

# ================= USER MANAGEMENT =================

@super_admin_bp.route("/admin/users", methods=["GET"])
@admin_required
def get_all_users():
    """Get all users with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        offset = (page - 1) * limit
        
        conn = user_db.get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, username, email, is_verified, created_at
            FROM users 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        users = [dict(row) for row in cursor.fetchall()]
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            "success": True,
            "users": users,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch users", "details": str(e)}), 500

# ================= ADMIN PROFILE =================

@super_admin_bp.route("/admin/profile", methods=["GET"])
@admin_required
def get_admin_profile():
    """Get current admin profile"""
    try:
        admin = request.current_admin
        
        return jsonify({
            "success": True,
            "admin": {
                "id": admin['id'],
                "username": admin['username'],
                "email": admin.get('email'),
                "full_name": admin.get('full_name'),
                "role": admin.get('role'),
                "last_login": admin.get('last_login'),
                "created_at": admin.get('created_at')
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch profile", "details": str(e)}), 500

@super_admin_bp.route("/admin/change-password", methods=["POST"])
@admin_required
def change_admin_password():
    """Change admin password"""
    try:
        data = request.json
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        admin = request.current_admin
        
        # Verify current password
        if not admin_db.verify_password(current_password, admin['password_hash']):
            return jsonify({"error": "Current password is incorrect"}), 400
        
        # Update password
        new_password_hash = admin_db.hash_password(new_password)
        
        conn = admin_db.get_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE admins SET password_hash = ? WHERE id = ?", 
                      (new_password_hash, admin['id']))
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Password changed successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to change password", "details": str(e)}), 500
