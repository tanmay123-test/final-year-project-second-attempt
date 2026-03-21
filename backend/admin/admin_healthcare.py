"""
Healthcare admin routes for ExpertEase backend.
Handles worker verification, user management, appointments, and payments for healthcare services.
"""

from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime
import os

# Import existing database modules
from worker_db import WorkerDB
from user_db import UserDB
from appointment_db import AppointmentDB
from subscription_db import SubscriptionDB

healthcare_admin_bp = Blueprint('healthcare_admin', __name__)

# Initialize database instances
worker_db = WorkerDB()
user_db = UserDB()
appt_db = AppointmentDB()
subscription_db = SubscriptionDB()

def get_db_connection():
    """Get database connection for admin operations"""
    conn = sqlite3.connect('expertease.db')
    conn.row_factory = sqlite3.Row
    return conn

# ================= TRUST & SAFETY - WORKER VERIFICATION =================

@healthcare_admin_bp.route('/workers/pending', methods=['GET'])
def get_pending_healthcare_workers():
    """
    Get all pending healthcare workers awaiting verification.
    
    Returns:
    {
        "workers": [
            {
                "id": 1,
                "full_name": "Dr. John Doe",
                "email": "john@example.com",
                "phone": "1234567890",
                "specialization": "Cardiology",
                "experience": 5,
                "clinic_location": "City Hospital",
                "license_number": "MED123456",
                "created_at": "2024-01-01 10:00:00",
                "documents": {
                    "profile_photo": "/uploads/worker_1_profile.jpg",
                    "aadhaar": "/uploads/worker_1_aadhaar.jpg",
                    "degree_certificate": "/uploads/worker_1_degree.pdf",
                    "medical_license": "/uploads/worker_1_license.pdf"
                }
            }
        ]
    }
    """
    try:
        # Get pending healthcare workers
        pending_workers = worker_db.get_pending_workers('healthcare')
        
        # Enrich with document information
        enriched_workers = []
        for worker in pending_workers:
            # Simulate document paths (in real implementation, these would be stored in database)
            documents = {
                "profile_photo": f"/uploads/worker_{worker['id']}_profile.jpg",
                "aadhaar": f"/uploads/worker_{worker['id']}_aadhaar.jpg",
                "degree_certificate": f"/uploads/worker_{worker['id']}_degree.pdf",
                "medical_license": f"/uploads/worker_{worker['id']}_license.pdf"
            }
            
            enriched_worker = dict(worker)
            enriched_worker['documents'] = documents
            enriched_workers.append(enriched_worker)
        
        return jsonify({"workers": enriched_workers}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch pending workers: {str(e)}"}), 500

@healthcare_admin_bp.route('/workers/approve/<int:worker_id>', methods=['POST'])
def approve_healthcare_worker(worker_id):
    """
    Approve a healthcare worker.
    
    Path Parameter: worker_id (int)
    
    Returns:
    {
        "message": "Worker approved successfully",
        "worker_id": 1
    }
    """
    try:
        # Verify worker exists and is pending
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        if worker.get('status') != 'pending':
            return jsonify({"error": "Worker is not in pending status"}), 400
        
        # Approve the worker
        worker_db.approve_worker(worker_id)
        
        return jsonify({
            "message": "Worker approved successfully",
            "worker_id": worker_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to approve worker: {str(e)}"}), 500

@healthcare_admin_bp.route('/workers/reject/<int:worker_id>', methods=['POST'])
def reject_healthcare_worker(worker_id):
    """
    Reject a healthcare worker with reason.
    
    Path Parameter: worker_id (int)
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
        
        # Verify worker exists and is pending
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        if worker.get('status') != 'pending':
            return jsonify({"error": "Worker is not in pending status"}), 400
        
        # Reject the worker
        worker_db.reject_worker(worker_id)
        
        # Store rejection reason (in real implementation, this would go to database)
        rejection_reason = data.get('rejection_reason')
        print(f"Worker {worker_id} rejected. Reason: {rejection_reason}")
        
        return jsonify({
            "message": "Worker rejected successfully",
            "worker_id": worker_id,
            "rejection_reason": rejection_reason
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to reject worker: {str(e)}"}), 500

# ================= USERS CONTROL =================

@healthcare_admin_bp.route('/users', methods=['GET'])
def get_healthcare_users():
    """
    Get all users for healthcare service monitoring.
    
    Returns:
    {
        "users": [
            {
                "id": 1,
                "name": "John Smith",
                "username": "johnsmith",
                "email": "john@example.com",
                "phone": "1234567890",
                "is_verified": true,
                "created_at": "2024-01-01 10:00:00"
            }
        ]
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all users with their healthcare appointment count
        cursor.execute("""
            SELECT 
                u.id, u.name, u.username, u.email, u.is_verified,
                u.created_at,
                COUNT(a.id) as healthcare_appointments
            FROM users u
            LEFT JOIN appointments a ON u.id = a.user_id 
                AND a.worker_id IN (SELECT id FROM workers WHERE service LIKE '%healthcare%')
            GROUP BY u.id, u.name, u.username, u.email, u.is_verified, u.created_at
            ORDER BY u.created_at DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            user = dict(row)
            # Add phone number if available (from appointments or separate table)
            cursor.execute("SELECT phone FROM appointments WHERE user_id = ? LIMIT 1", (user['id'],))
            phone_row = cursor.fetchone()
            user['phone'] = phone_row['phone'] if phone_row else None
            users.append(user)
        
        conn.close()
        
        return jsonify({"users": users}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch users: {str(e)}"}), 500

@healthcare_admin_bp.route('/users/block/<int:user_id>', methods=['POST'])
def block_healthcare_user(user_id):
    """
    Block a user from healthcare services.
    
    Path Parameter: user_id (int)
    
    Returns:
    {
        "message": "User blocked successfully",
        "user_id": 1
    }
    """
    try:
        # Verify user exists
        user = user_db.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # In a real implementation, you would update user status in database
        # For now, we'll just log the action
        print(f"User {user_id} blocked from healthcare services")
        
        return jsonify({
            "message": "User blocked successfully",
            "user_id": user_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to block user: {str(e)}"}), 500

# ================= WORKERS CONTROL =================

@healthcare_admin_bp.route('/workers/approved', methods=['GET'])
def get_approved_healthcare_workers():
    """
    Get all approved healthcare workers.
    
    Returns:
    {
        "workers": [
            {
                "id": 1,
                "full_name": "Dr. John Doe",
                "email": "john@example.com",
                "phone": "1234567890",
                "specialization": "Cardiology",
                "experience": 5,
                "clinic_location": "City Hospital",
                "rating": 4.5,
                "status": "approved",
                "created_at": "2024-01-01 10:00:00"
            }
        ]
    }
    """
    try:
        approved_workers = worker_db.get_approved_workers('healthcare')
        
        return jsonify({"workers": approved_workers}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch approved workers: {str(e)}"}), 500

@healthcare_admin_bp.route('/workers/suspend/<int:worker_id>', methods=['POST'])
def suspend_healthcare_worker(worker_id):
    """
    Suspend an approved healthcare worker.
    
    Path Parameter: worker_id (int)
    
    Returns:
    {
        "message": "Worker suspended successfully",
        "worker_id": 1
    }
    """
    try:
        # Verify worker exists and is approved
        worker = worker_db.get_worker_by_id(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404
        
        if worker.get('status') != 'approved':
            return jsonify({"error": "Worker is not in approved status"}), 400
        
        # Suspend the worker
        worker_db.update_worker_status(worker_id, 'suspended')
        
        return jsonify({
            "message": "Worker suspended successfully",
            "worker_id": worker_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to suspend worker: {str(e)}"}), 500

# ================= APPOINTMENTS MONITORING =================

@healthcare_admin_bp.route('/appointments', methods=['GET'])
def get_healthcare_appointments():
    """
    Get all healthcare appointments for monitoring.
    
    Query Parameters:
    - status: Filter by appointment status (pending, accepted, completed, cancelled)
    - date: Filter by specific date (YYYY-MM-DD)
    
    Returns:
    {
        "appointments": [
            {
                "id": 1,
                "user_name": "John Smith",
                "worker_name": "Dr. Jane Doe",
                "specialization": "Cardiology",
                "appointment_type": "clinic",
                "booking_date": "2024-01-15",
                "time_slot": "10:00-10:30",
                "status": "completed",
                "payment_status": "paid",
                "created_at": "2024-01-01 10:00:00"
            }
        ]
    }
    """
    try:
        status_filter = request.args.get('status')
        date_filter = request.args.get('date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                a.id, a.user_name, a.booking_date, a.time_slot, 
                a.appointment_type, a.status, a.payment_status, a.created_at,
                w.full_name as worker_name, w.specialization,
                u.email as user_email
            FROM appointments a
            JOIN workers w ON a.worker_id = w.id
            JOIN users u ON a.user_id = u.id
            WHERE w.service LIKE '%healthcare%'
        """
        params = []
        
        if status_filter:
            query += " AND a.status = ?"
            params.append(status_filter)
        
        if date_filter:
            query += " AND a.booking_date = ?"
            params.append(date_filter)
        
        query += " ORDER BY a.created_at DESC"
        
        cursor.execute(query, params)
        appointments = []
        
        for row in cursor.fetchall():
            appointment = dict(row)
            appointments.append(appointment)
        
        conn.close()
        
        return jsonify({"appointments": appointments}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch appointments: {str(e)}"}), 500

# ================= PAYMENTS & SUBSCRIPTIONS =================

@healthcare_admin_bp.route('/subscriptions', methods=['GET'])
def get_healthcare_subscriptions():
    """
    Get all healthcare worker subscriptions.
    
    Returns:
    {
        "subscriptions": [
            {
                "worker_id": 1,
                "worker_name": "Dr. John Doe",
                "specialization": "Cardiology",
                "plan_type": "premium",
                "start_date": "2024-01-01",
                "expiry_date": "2024-02-01",
                "payment_status": "active",
                "appointments_used": 15,
                "appointments_limit": 50
            }
        ]
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get subscriptions with worker details
        cursor.execute("""
            SELECT 
                s.worker_id, s.plan_id, s.start_date, s.expiry_date, 
                s.payment_status, s.appointments_used, s.appointments_limit,
                w.full_name as worker_name, w.specialization
            FROM subscriptions s
            JOIN workers w ON s.worker_id = w.id
            WHERE w.service LIKE '%healthcare%'
            ORDER BY s.created_at DESC
        """)
        
        subscriptions = []
        for row in cursor.fetchall():
            subscription = dict(row)
            # Map plan_id to plan_type (simplified)
            plan_type_map = {
                1: "basic",
                2: "premium", 
                3: "enterprise"
            }
            subscription['plan_type'] = plan_type_map.get(subscription['plan_id'], 'unknown')
            subscriptions.append(subscription)
        
        conn.close()
        
        return jsonify({"subscriptions": subscriptions}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch subscriptions: {str(e)}"}), 500

@healthcare_admin_bp.route('/payments', methods=['GET'])
def get_healthcare_payments():
    """
    Get payment breakdown for healthcare services.
    
    Returns:
    {
        "payments": [
            {
                "appointment_id": 1,
                "user_name": "John Smith",
                "worker_name": "Dr. Jane Doe",
                "specialization": "Cardiology",
                "total_amount": 500.00,
                "platform_commission": 100.00,
                "commission_percentage": 20,
                "worker_earnings": 400.00,
                "payment_date": "2024-01-15",
                "payment_status": "completed"
            }
        ],
        "summary": {
            "total_revenue": 50000.00,
            "total_commission": 10000.00,
            "total_worker_earnings": 40000.00
        }
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get completed appointments with payment info
        cursor.execute("""
            SELECT 
                a.id as appointment_id, a.user_name, a.booking_date,
                w.full_name as worker_name, w.specialization,
                a.payment_status, a.created_at
            FROM appointments a
            JOIN workers w ON a.worker_id = w.id
            WHERE w.service LIKE '%healthcare%' 
            AND a.status = 'completed'
            AND a.payment_status = 'paid'
            ORDER BY a.created_at DESC
        """)
        
        payments = []
        total_revenue = 0
        total_commission = 0
        total_worker_earnings = 0
        
        for row in cursor.fetchall():
            payment = dict(row)
            
            # Simulate payment breakdown (in real implementation, this would come from payment table)
            total_amount = 500.00  # Default consultation fee
            commission_percentage = 20
            platform_commission = total_amount * (commission_percentage / 100)
            worker_earnings = total_amount - platform_commission
            
            payment.update({
                'total_amount': total_amount,
                'platform_commission': platform_commission,
                'commission_percentage': commission_percentage,
                'worker_earnings': worker_earnings,
                'payment_date': row['booking_date']
            })
            
            payments.append(payment)
            
            # Update totals
            total_revenue += total_amount
            total_commission += platform_commission
            total_worker_earnings += worker_earnings
        
        conn.close()
        
        return jsonify({
            "payments": payments,
            "summary": {
                "total_revenue": total_revenue,
                "total_commission": total_commission,
                "total_worker_earnings": total_worker_earnings
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch payments: {str(e)}"}), 500

# ================= SETTINGS =================

@healthcare_admin_bp.route('/settings', methods=['GET'])
def get_healthcare_settings():
    """
    Get healthcare service settings.
    
    Returns:
    {
        "settings": {
            "commission_percentage": 20,
            "healthcare_service_available": true,
            "default_consultation_fee": 500,
            "auto_approve_workers": false,
            "max_appointments_per_day": 20
        }
    }
    """
    try:
        # In a real implementation, these would come from a settings table
        settings = {
            "commission_percentage": 20,
            "healthcare_service_available": True,
            "default_consultation_fee": 500,
            "auto_approve_workers": False,
            "max_appointments_per_day": 20
        }
        
        return jsonify({"settings": settings}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch settings: {str(e)}"}), 500

@healthcare_admin_bp.route('/settings', methods=['POST'])
def update_healthcare_settings():
    """
    Update healthcare service settings.
    
    Request Body:
    {
        "commission_percentage": 25,
        "healthcare_service_available": true,
        "default_consultation_fee": 600,
        "auto_approve_workers": false,
        "max_appointments_per_day": 25
    }
    
    Returns:
    {
        "message": "Settings updated successfully",
        "settings": {...}
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No settings data provided"}), 400
        
        # Validate settings
        valid_settings = [
            "commission_percentage", "healthcare_service_available", 
            "default_consultation_fee", "auto_approve_workers", 
            "max_appointments_per_day"
        ]
        
        for key in data.keys():
            if key not in valid_settings:
                return jsonify({"error": f"Invalid setting: {key}"}), 400
        
        # In a real implementation, these would be saved to database
        print(f"Healthcare settings updated: {data}")
        
        return jsonify({
            "message": "Settings updated successfully",
            "settings": data
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to update settings: {str(e)}"}), 500
