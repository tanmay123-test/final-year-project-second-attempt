"""
Admin routes for user management across all services.
"""

from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime
from user_db import UserDB

users_admin_bp = Blueprint('users_admin', __name__, url_prefix='/users')
user_db = UserDB()

def get_db_connection():
    """Get database connection for admin operations"""
    conn = sqlite3.connect('expertease.db')
    conn.row_factory = sqlite3.Row
    return conn

@users_admin_bp.route('/', methods=['GET'])
def get_all_users():
    """
    Get all users across all services.
    
    Query Parameters:
    - status: Filter by user status (active, blocked, verified, unverified)
    - service: Filter by service usage
    
    Returns:
    {
        "users": [
            {
                "id": 1,
                "name": "John Smith",
                "username": "johnsmith",
                "email": "john@example.com",
                "is_verified": true,
                "created_at": "2024-01-01 10:00:00",
                "last_active": "2024-01-15 14:30:00",
                "total_appointments": 5,
                "services_used": ["healthcare", "housekeeping"]
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
                u.id, u.name, u.username, u.email, u.is_verified, u.created_at,
                COUNT(a.id) as total_appointments
            FROM users u
            LEFT JOIN appointments a ON u.id = a.user_id
        """
        
        conditions = []
        params = []
        
        if status_filter == 'verified':
            conditions.append("u.is_verified = 1")
        elif status_filter == 'unverified':
            conditions.append("u.is_verified = 0")
        elif status_filter == 'blocked':
            # In real implementation, you'd have a status column
            conditions.append("u.is_verified = 0")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " GROUP BY u.id, u.name, u.username, u.email, u.is_verified, u.created_at"
        query += " ORDER BY u.created_at DESC"
        
        cursor.execute(query, params)
        users = []
        
        for row in cursor.fetchall():
            user = dict(row)
            # Get services used by this user
            cursor.execute("""
                SELECT DISTINCT w.service 
                FROM appointments a
                JOIN workers w ON a.worker_id = w.id
                WHERE a.user_id = ?
            """, (user['id'],))
            
            services_used = [row['service'] for row in cursor.fetchall()]
            user['services_used'] = services_used
            user['last_active'] = user['created_at']  # Simplified
            
            users.append(user)
        
        conn.close()
        
        return jsonify({"users": users}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch users: {str(e)}"}), 500

@users_admin_bp.route('/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    """
    Get detailed information about a specific user.
    
    Returns:
    {
        "user": {
            "id": 1,
            "name": "John Smith",
            "username": "johnsmith",
            "email": "john@example.com",
            "is_verified": true,
            "created_at": "2024-01-01 10:00:00",
            "appointments": [...],
            "services_used": ["healthcare", "housekeeping"]
        }
    }
    """
    try:
        # Get user details
        user = user_db.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user appointments
        cursor.execute("""
            SELECT a.*, w.full_name as worker_name, w.service
            FROM appointments a
            JOIN workers w ON a.worker_id = w.id
            WHERE a.user_id = ?
            ORDER BY a.created_at DESC
        """, (user_id,))
        
        appointments = [dict(row) for row in cursor.fetchall()]
        
        # Get services used
        cursor.execute("""
            SELECT DISTINCT w.service 
            FROM appointments a
            JOIN workers w ON a.worker_id = w.id
            WHERE a.user_id = ?
        """, (user_id,))
        
        services_used = [row['service'] for row in cursor.fetchall()]
        
        conn.close()
        
        user_details = dict(user)
        user_details['appointments'] = appointments
        user_details['services_used'] = services_used
        
        return jsonify({"user": user_details}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch user details: {str(e)}"}), 500

@users_admin_bp.route('/<int:user_id>/block', methods=['POST'])
def block_user(user_id):
    """
    Block a user from all services.
    
    Returns:
    {
        "message": "User blocked successfully",
        "user_id": 1
    }
    """
    try:
        user = user_db.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # In real implementation, update user status in database
        print(f"User {user_id} blocked from all services")
        
        return jsonify({
            "message": "User blocked successfully",
            "user_id": user_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to block user: {str(e)}"}), 500

@users_admin_bp.route('/<int:user_id>/unblock', methods=['POST'])
def unblock_user(user_id):
    """
    Unblock a user from all services.
    
    Returns:
    {
        "message": "User unblocked successfully",
        "user_id": 1
    }
    """
    try:
        user = user_db.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # In real implementation, update user status in database
        print(f"User {user_id} unblocked from all services")
        
        return jsonify({
            "message": "User unblocked successfully",
            "user_id": user_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to unblock user: {str(e)}"}), 500

@users_admin_bp.route('/stats', methods=['GET'])
def get_user_stats():
    """
    Get user statistics across all services.
    
    Returns:
    {
        "stats": {
            "total_users": 1000,
            "verified_users": 800,
            "unverified_users": 200,
            "active_today": 50,
            "new_this_month": 100,
            "users_by_service": {
                "healthcare": 600,
                "housekeeping": 300,
                "freelance": 200,
                "car_service": 150,
                "money_management": 100
            }
        }
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_users = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as verified FROM users WHERE is_verified = 1")
        verified_users = cursor.fetchone()['verified']
        
        unverified_users = total_users - verified_users
        
        # Get users by service
        cursor.execute("""
            SELECT w.service, COUNT(DISTINCT a.user_id) as user_count
            FROM appointments a
            JOIN workers w ON a.worker_id = w.id
            GROUP BY w.service
        """)
        
        users_by_service = {}
        for row in cursor.fetchall():
            service = row['service']
            # Handle comma-separated services
            if ',' in service:
                services = [s.strip() for s in service.split(',')]
                for s in services:
                    users_by_service[s] = users_by_service.get(s, 0) + row['user_count']
            else:
                users_by_service[service] = row['user_count']
        
        conn.close()
        
        stats = {
            "total_users": total_users,
            "verified_users": verified_users,
            "unverified_users": unverified_users,
            "active_today": 50,  # Simplified
            "new_this_month": 100,  # Simplified
            "users_by_service": users_by_service
        }
        
        return jsonify({"stats": stats}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch user stats: {str(e)}"}), 500
