"""
Admin routes for appointment management across all services.
"""

from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime, timedelta
from appointment_db import AppointmentDB

appointments_admin_bp = Blueprint('appointments_admin', __name__, url_prefix='/appointments')
appt_db = AppointmentDB()

def get_db_connection():
    """Get database connection for admin operations"""
    conn = sqlite3.connect('expertease.db')
    conn.row_factory = sqlite3.Row
    return conn

@appointments_admin_bp.route('/', methods=['GET'])
def get_all_appointments():
    """
    Get all appointments across all services.
    
    Query Parameters:
    - status: Filter by appointment status (pending, accepted, completed, cancelled)
    - service: Filter by service type
    - date: Filter by specific date (YYYY-MM-DD)
    - date_from: Filter from date (YYYY-MM-DD)
    - date_to: Filter to date (YYYY-MM-DD)
    
    Returns:
    {
        "appointments": [
            {
                "id": 1,
                "user_name": "John Smith",
                "worker_name": "Dr. Jane Doe",
                "service": "healthcare",
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
        service_filter = request.args.get('service')
        date_filter = request.args.get('date')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                a.id, a.user_name, a.booking_date, a.time_slot,
                a.appointment_type, a.status, a.payment_status, a.created_at,
                w.full_name as worker_name, w.service, w.specialization,
                u.email as user_email
            FROM appointments a
            JOIN workers w ON a.worker_id = w.id
            JOIN users u ON a.user_id = u.id
        """
        
        conditions = []
        params = []
        
        if status_filter:
            conditions.append("a.status = ?")
            params.append(status_filter)
        
        if service_filter:
            conditions.append("w.service LIKE ?")
            params.append(f"%{service_filter}%")
        
        if date_filter:
            conditions.append("a.booking_date = ?")
            params.append(date_filter)
        
        if date_from:
            conditions.append("a.booking_date >= ?")
            params.append(date_from)
        
        if date_to:
            conditions.append("a.booking_date <= ?")
            params.append(date_to)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
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

@appointments_admin_bp.route('/<int:appointment_id>', methods=['GET'])
def get_appointment_details(appointment_id):
    """
    Get detailed information about a specific appointment.
    
    Returns:
    {
        "appointment": {
            "id": 1,
            "user_name": "John Smith",
            "user_email": "john@example.com",
            "worker_name": "Dr. Jane Doe",
            "service": "healthcare",
            "specialization": "Cardiology",
            "appointment_type": "clinic",
            "booking_date": "2024-01-15",
            "time_slot": "10:00-10:30",
            "status": "completed",
            "payment_status": "paid",
            "patient_symptoms": "Chest pain",
            "created_at": "2024-01-01 10:00:00",
            "payment_details": {...}
        }
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get appointment details
        cursor.execute("""
            SELECT 
                a.*, w.full_name as worker_name, w.service, w.specialization,
                u.email as user_email, u.phone as user_phone
            FROM appointments a
            JOIN workers w ON a.worker_id = w.id
            JOIN users u ON a.user_id = u.id
            WHERE a.id = ?
        """, (appointment_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({"error": "Appointment not found"}), 404
        
        appointment = dict(row)
        
        # Add payment details (simulated)
        if appointment['payment_status'] == 'paid':
            appointment['payment_details'] = {
                "amount": 500.00,
                "platform_commission": 100.00,
                "worker_earnings": 400.00,
                "payment_date": appointment['booking_date']
            }
        
        conn.close()
        
        return jsonify({"appointment": appointment}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch appointment details: {str(e)}"}), 500

@appointments_admin_bp.route('/<int:appointment_id>/cancel', methods=['POST'])
def cancel_appointment(appointment_id):
    """
    Cancel an appointment (admin action).
    
    Request Body:
    {
        "cancellation_reason": "Emergency situation"
    }
    
    Returns:
    {
        "message": "Appointment cancelled successfully",
        "appointment_id": 1
    }
    """
    try:
        data = request.get_json()
        cancellation_reason = data.get('cancellation_reason', 'Admin cancellation')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if appointment exists
        cursor.execute("SELECT status FROM appointments WHERE id = ?", (appointment_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({"error": "Appointment not found"}), 404
        
        current_status = row['status']
        if current_status in ['completed', 'cancelled']:
            conn.close()
            return jsonify({"error": f"Cannot cancel appointment in {current_status} status"}), 400
        
        # Update appointment status
        cursor.execute("""
            UPDATE appointments 
            SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (appointment_id,))
        
        conn.commit()
        conn.close()
        
        print(f"Appointment {appointment_id} cancelled. Reason: {cancellation_reason}")
        
        return jsonify({
            "message": "Appointment cancelled successfully",
            "appointment_id": appointment_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to cancel appointment: {str(e)}"}), 500

@appointments_admin_bp.route('/stats', methods=['GET'])
def get_appointment_stats():
    """
    Get appointment statistics across all services.
    
    Query Parameters:
    - period: Stats period (today, week, month, year)
    
    Returns:
    {
        "stats": {
            "total_appointments": 1000,
            "pending_appointments": 50,
            "accepted_appointments": 200,
            "completed_appointments": 700,
            "cancelled_appointments": 50,
            "appointments_by_service": {
                "healthcare": 400,
                "housekeeping": 300,
                "freelance": 200,
                "car_service": 80,
                "money_management": 20
            },
            "revenue_summary": {
                "total_revenue": 500000.00,
                "total_commission": 100000.00,
                "total_worker_earnings": 400000.00
            }
        }
    }
    """
    try:
        period = request.args.get('period', 'today')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Date filter based on period
        date_condition = ""
        if period == 'today':
            date_condition = "AND DATE(a.created_at) = DATE('now')"
        elif period == 'week':
            date_condition = "AND a.created_at >= DATE('now', '-7 days')"
        elif period == 'month':
            date_condition = "AND a.created_at >= DATE('now', '-30 days')"
        elif period == 'year':
            date_condition = "AND a.created_at >= DATE('now', '-365 days')"
        
        # Get basic stats
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) as accepted,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled
            FROM appointments a
            WHERE 1=1 {date_condition}
        """)
        
        stats_row = cursor.fetchone()
        
        # Get appointments by service
        cursor.execute(f"""
            SELECT w.service, COUNT(*) as count
            FROM appointments a
            JOIN workers w ON a.worker_id = w.id
            WHERE 1=1 {date_condition}
            GROUP BY w.service
        """)
        
        appointments_by_service = {}
        for row in cursor.fetchall():
            service = row['service']
            if ',' in service:
                services = [s.strip() for s in service.split(',')]
                for s in services:
                    appointments_by_service[s] = appointments_by_service.get(s, 0) + row['count']
            else:
                appointments_by_service[service] = row['count']
        
        # Get revenue summary (simplified)
        cursor.execute(f"""
            SELECT COUNT(*) as paid_appointments
            FROM appointments a
            WHERE a.payment_status = 'paid' AND a.status = 'completed'
            {date_condition}
        """)
        
        revenue_row = cursor.fetchone()
        paid_appointments = revenue_row['paid_appointments']
        avg_appointment_fee = 500.00  # Simplified
        commission_percentage = 20
        
        total_revenue = paid_appointments * avg_appointment_fee
        total_commission = total_revenue * (commission_percentage / 100)
        total_worker_earnings = total_revenue - total_commission
        
        conn.close()
        
        stats = {
            "total_appointments": stats_row['total'],
            "pending_appointments": stats_row['pending'],
            "accepted_appointments": stats_row['accepted'],
            "completed_appointments": stats_row['completed'],
            "cancelled_appointments": stats_row['cancelled'],
            "appointments_by_service": appointments_by_service,
            "revenue_summary": {
                "total_revenue": total_revenue,
                "total_commission": total_commission,
                "total_worker_earnings": total_worker_earnings
            }
        }
        
        return jsonify({"stats": stats}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch appointment stats: {str(e)}"}), 500

@appointments_admin_bp.route('/calendar', methods=['GET'])
def get_appointment_calendar():
    """
    Get appointments in calendar format.
    
    Query Parameters:
    - month: Month (1-12)
    - year: Year (e.g., 2024)
    - service: Filter by service type
    
    Returns:
    {
        "calendar": {
            "2024-01-15": {
                "date": "2024-01-15",
                "total_appointments": 5,
                "completed": 3,
                "pending": 1,
                "cancelled": 1
            }
        }
    }
    """
    try:
        month = request.args.get('month', datetime.now().month)
        year = request.args.get('year', datetime.now().year)
        service_filter = request.args.get('service')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                DATE(booking_date) as date,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled
            FROM appointments a
            JOIN workers w ON a.worker_id = w.id
            WHERE strftime('%m', a.booking_date) = ? AND strftime('%Y', a.booking_date) = ?
        """
        
        params = [f"{int(month):02d}", str(year)]
        
        if service_filter:
            query += " AND w.service LIKE ?"
            params.append(f"%{service_filter}%")
        
        query += " GROUP BY DATE(booking_date)"
        
        cursor.execute(query, params)
        calendar = {}
        
        for row in cursor.fetchall():
            date_str = row['date']
            calendar[date_str] = {
                "date": date_str,
                "total_appointments": row['total'],
                "completed": row['completed'],
                "pending": row['pending'],
                "cancelled": row['cancelled']
            }
        
        conn.close()
        
        return jsonify({"calendar": calendar}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch appointment calendar: {str(e)}"}), 500
