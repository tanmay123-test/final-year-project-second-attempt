"""
Admin routes for payment and subscription management across all services.
"""

from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime, timedelta
from subscription_db import SubscriptionDB

payments_admin_bp = Blueprint('payments_admin', __name__, url_prefix='/payments')
subscription_db = SubscriptionDB()

def get_db_connection():
    """Get database connection for admin operations"""
    conn = sqlite3.connect('expertease.db')
    conn.row_factory = sqlite3.Row
    return conn

@payments_admin_bp.route('/transactions', methods=['GET'])
def get_all_transactions():
    """
    Get all payment transactions across all services.
    
    Query Parameters:
    - status: Filter by payment status (pending, paid, failed, refunded)
    - service: Filter by service type
    - date_from: Filter from date (YYYY-MM-DD)
    - date_to: Filter to date (YYYY-MM-DD)
    
    Returns:
    {
        "transactions": [
            {
                "id": 1,
                "appointment_id": 1,
                "user_name": "John Smith",
                "worker_name": "Dr. Jane Doe",
                "service": "healthcare",
                "amount": 500.00,
                "platform_commission": 100.00,
                "worker_earnings": 400.00,
                "commission_percentage": 20,
                "payment_status": "paid",
                "payment_date": "2024-01-15 10:30:00",
                "payment_method": "credit_card"
            }
        ]
    }
    """
    try:
        status_filter = request.args.get('status')
        service_filter = request.args.get('service')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                a.id as transaction_id, a.id as appointment_id,
                a.user_name, a.booking_date, a.payment_status, a.created_at,
                w.full_name as worker_name, w.service, w.specialization
            FROM appointments a
            JOIN workers w ON a.worker_id = w.id
            WHERE a.status = 'completed'
        """
        
        conditions = []
        params = []
        
        if status_filter:
            conditions.append("a.payment_status = ?")
            params.append(status_filter)
        
        if service_filter:
            conditions.append("w.service LIKE ?")
            params.append(f"%{service_filter}%")
        
        if date_from:
            conditions.append("a.booking_date >= ?")
            params.append(date_from)
        
        if date_to:
            conditions.append("a.booking_date <= ?")
            params.append(date_to)
        
        if conditions:
            query += " AND " + " AND ".join(conditions)
        
        query += " ORDER BY a.created_at DESC"
        
        cursor.execute(query, params)
        transactions = []
        
        for row in cursor.fetchall():
            transaction = dict(row)
            
            # Calculate payment breakdown (simplified)
            if transaction['payment_status'] == 'paid':
                amount = 500.00  # Default consultation fee
                commission_percentage = 20
                platform_commission = amount * (commission_percentage / 100)
                worker_earnings = amount - platform_commission
                
                transaction.update({
                    'amount': amount,
                    'platform_commission': platform_commission,
                    'worker_earnings': worker_earnings,
                    'commission_percentage': commission_percentage,
                    'payment_date': transaction['booking_date'],
                    'payment_method': 'credit_card'  # Simplified
                })
            
            transactions.append(transaction)
        
        conn.close()
        
        return jsonify({"transactions": transactions}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch transactions: {str(e)}"}), 500

@payments_admin_bp.route('/subscriptions', methods=['GET'])
def get_all_subscriptions():
    """
    Get all worker subscriptions across all services.
    
    Query Parameters:
    - service: Filter by service type
    - status: Filter by subscription status (active, expired, cancelled)
    
    Returns:
    {
        "subscriptions": [
            {
                "id": 1,
                "worker_id": 1,
                "worker_name": "Dr. Jane Doe",
                "service": "healthcare",
                "specialization": "Cardiology",
                "plan_type": "premium",
                "start_date": "2024-01-01",
                "expiry_date": "2024-02-01",
                "payment_status": "active",
                "appointments_used": 15,
                "appointments_limit": 50,
                "monthly_fee": 2000.00
            }
        ]
    }
    """
    try:
        service_filter = request.args.get('service')
        status_filter = request.args.get('status')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                s.id, s.worker_id, s.plan_id, s.start_date, s.expiry_date,
                s.payment_status, s.appointments_used, s.appointments_limit, s.created_at,
                w.full_name as worker_name, w.service, w.specialization
            FROM subscriptions s
            JOIN workers w ON s.worker_id = w.id
        """
        
        conditions = []
        params = []
        
        if service_filter:
            conditions.append("w.service LIKE ?")
            params.append(f"%{service_filter}%")
        
        if status_filter:
            conditions.append("s.payment_status = ?")
            params.append(status_filter)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY s.created_at DESC"
        
        cursor.execute(query, params)
        subscriptions = []
        
        for row in cursor.fetchall():
            subscription = dict(row)
            
            # Map plan_id to plan_type and monthly fee
            plan_details = {
                1: {"type": "basic", "fee": 1000.00},
                2: {"type": "premium", "fee": 2000.00},
                3: {"type": "enterprise", "fee": 5000.00}
            }
            
            plan_info = plan_details.get(subscription['plan_id'], {"type": "unknown", "fee": 0.00})
            subscription['plan_type'] = plan_info['type']
            subscription['monthly_fee'] = plan_info['fee']
            
            subscriptions.append(subscription)
        
        conn.close()
        
        return jsonify({"subscriptions": subscriptions}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch subscriptions: {str(e)}"}), 500

@payments_admin_bp.route('/subscriptions/<int:subscription_id>/cancel', methods=['POST'])
def cancel_subscription(subscription_id):
    """
    Cancel a worker subscription.
    
    Returns:
    {
        "message": "Subscription cancelled successfully",
        "subscription_id": 1
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if subscription exists
        cursor.execute("SELECT worker_id FROM subscriptions WHERE id = ?", (subscription_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({"error": "Subscription not found"}), 404
        
        # Update subscription status
        cursor.execute("""
            UPDATE subscriptions 
            SET payment_status = 'cancelled', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (subscription_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "message": "Subscription cancelled successfully",
            "subscription_id": subscription_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to cancel subscription: {str(e)}"}), 500

@payments_admin_bp.route('/subscriptions/<int:subscription_id>/renew', methods=['POST'])
def renew_subscription(subscription_id):
    """
    Renew a worker subscription.
    
    Request Body:
    {
        "new_expiry_date": "2024-03-01",
        "plan_id": 2
    }
    
    Returns:
    {
        "message": "Subscription renewed successfully",
        "subscription_id": 1
    }
    """
    try:
        data = request.get_json()
        new_expiry_date = data.get('new_expiry_date')
        plan_id = data.get('plan_id')
        
        if not new_expiry_date:
            return jsonify({"error": "New expiry date is required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if subscription exists
        cursor.execute("SELECT worker_id FROM subscriptions WHERE id = ?", (subscription_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({"error": "Subscription not found"}), 404
        
        # Update subscription
        update_fields = ["expiry_date = ?", "payment_status = 'active'"]
        params = [new_expiry_date]
        
        if plan_id:
            update_fields.append("plan_id = ?")
            params.append(plan_id)
        
        params.append(subscription_id)
        
        cursor.execute(f"""
            UPDATE subscriptions 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, params)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "message": "Subscription renewed successfully",
            "subscription_id": subscription_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to renew subscription: {str(e)}"}), 500

@payments_admin_bp.route('/stats', methods=['GET'])
def get_payment_stats():
    """
    Get payment statistics across all services.
    
    Query Parameters:
    - period: Stats period (today, week, month, year)
    
    Returns:
    {
        "stats": {
            "total_revenue": 500000.00,
            "total_commission": 100000.00,
            "total_worker_earnings": 400000.00,
            "total_transactions": 1000,
            "successful_transactions": 950,
            "failed_transactions": 50,
            "revenue_by_service": {
                "healthcare": 200000.00,
                "housekeeping": 150000.00,
                "freelance": 100000.00,
                "car_service": 40000.00,
                "money_management": 10000.00
            },
            "subscription_revenue": 50000.00,
            "active_subscriptions": 200
        }
    }
    """
    try:
        period = request.args.get('period', 'month')
        
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
        
        # Get transaction stats
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(CASE WHEN a.payment_status = 'paid' THEN 1 ELSE 0 END) as successful_transactions,
                SUM(CASE WHEN a.payment_status = 'failed' THEN 1 ELSE 0 END) as failed_transactions
            FROM appointments a
            WHERE a.status = 'completed' {date_condition}
        """)
        
        transaction_stats = cursor.fetchone()
        
        # Get revenue by service
        cursor.execute(f"""
            SELECT 
                w.service, 
                COUNT(*) as paid_appointments
            FROM appointments a
            JOIN workers w ON a.worker_id = w.id
            WHERE a.status = 'completed' AND a.payment_status = 'paid'
            {date_condition}
            GROUP BY w.service
        """)
        
        revenue_by_service = {}
        total_revenue = 0
        
        for row in cursor.fetchall():
            service = row['service']
            paid_appointments = row['paid_appointments']
            avg_fee = 500.00  # Simplified
            service_revenue = paid_appointments * avg_fee
            total_revenue += service_revenue
            
            # Handle comma-separated services
            if ',' in service:
                services = [s.strip() for s in service.split(',')]
                for s in services:
                    revenue_by_service[s] = revenue_by_service.get(s, 0) + service_revenue / len(services)
            else:
                revenue_by_service[service] = service_by_service.get(service, 0) + service_revenue
        
        # Calculate commission and earnings
        commission_percentage = 20
        total_commission = total_revenue * (commission_percentage / 100)
        total_worker_earnings = total_revenue - total_commission
        
        # Get subscription stats
        cursor.execute("""
            SELECT 
                COUNT(*) as active_subscriptions,
                SUM(CASE 
                    WHEN plan_id = 1 THEN 1000.00
                    WHEN plan_id = 2 THEN 2000.00
                    WHEN plan_id = 3 THEN 5000.00
                    ELSE 0.00
                END) as subscription_revenue
            FROM subscriptions
            WHERE payment_status = 'active'
        """)
        
        subscription_stats = cursor.fetchone()
        
        conn.close()
        
        stats = {
            "total_revenue": total_revenue,
            "total_commission": total_commission,
            "total_worker_earnings": total_worker_earnings,
            "total_transactions": transaction_stats['total_transactions'],
            "successful_transactions": transaction_stats['successful_transactions'],
            "failed_transactions": transaction_stats['failed_transactions'],
            "revenue_by_service": revenue_by_service,
            "subscription_revenue": subscription_stats['subscription_revenue'] or 0,
            "active_subscriptions": subscription_stats['active_subscriptions']
        }
        
        return jsonify({"stats": stats}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch payment stats: {str(e)}"}), 500

@payments_admin_bp.route('/refunds', methods=['GET'])
def get_refunds():
    """
    Get all refund requests and processed refunds.
    
    Returns:
    {
        "refunds": [
            {
                "id": 1,
                "appointment_id": 1,
                "user_name": "John Smith",
                "worker_name": "Dr. Jane Doe",
                "service": "healthcare",
                "amount": 500.00,
                "refund_reason": "Service not provided",
                "status": "approved",
                "processed_date": "2024-01-16",
                "processed_by": "admin"
            }
        ]
    }
    """
    try:
        # In a real implementation, this would come from a refunds table
        # For now, return empty list as placeholder
        refunds = []
        
        return jsonify({"refunds": refunds}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch refunds: {str(e)}"}), 500

@payments_admin_bp.route('/refunds/<int:refund_id>/process', methods=['POST'])
def process_refund(refund_id):
    """
    Process a refund request.
    
    Request Body:
    {
        "action": "approve|reject",
        "reason": "Refund approved due to service cancellation"
    }
    
    Returns:
    {
        "message": "Refund processed successfully",
        "refund_id": 1
    }
    """
    try:
        data = request.get_json()
        action = data.get('action')
        reason = data.get('reason', '')
        
        if not action or action not in ['approve', 'reject']:
            return jsonify({"error": "Valid action (approve/reject) is required"}), 400
        
        # In a real implementation, this would update the refunds table
        print(f"Refund {refund_id} {action}ed. Reason: {reason}")
        
        return jsonify({
            "message": f"Refund {action}d successfully",
            "refund_id": refund_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to process refund: {str(e)}"}), 500
