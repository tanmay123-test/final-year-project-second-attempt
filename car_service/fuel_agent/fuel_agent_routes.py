"""
Fuel Delivery Agent API Routes
Complete REST API for fuel delivery agent management system
"""

from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth_utils import verify_token
from ..worker_auth.worker_routes import get_current_worker, car_worker_db
from .fuel_agent_service import fuel_agent_service

# Create blueprint
fuel_agent_bp = Blueprint("fuel_agent", __name__)

def require_fuel_agent_auth(f):
    """Decorator to require authenticated fuel agent"""
    def wrapper(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authentication required"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        username = verify_token(token)
        if not username:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Get worker and validate it's a fuel agent
        worker = car_worker_db.get_worker_by_username(username)
        if not worker or worker['worker_type'] != 'FUEL_AGENT':
            return jsonify({"error": "Fuel agent access required"}), 403
        
        if worker['status'] != 'APPROVED':
            return jsonify({"error": "Fuel agent account not approved"}), 403
        
        # Add worker to request context
        request.current_worker = worker
        return f(*args, **kwargs)
    
    wrapper.__name__ = f.__name__
    return wrapper

# ==================== ONLINE STATUS & DEMAND ====================

@fuel_agent_bp.route("/api/car/fuel-agent/status", methods=["GET"])
@require_fuel_agent_auth
def get_fuel_agent_status():
    """Get fuel agent current status and demand analysis"""
    try:
        agent_id = request.current_worker['id']
        result = fuel_agent_service.get_fuel_demand_status(agent_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get status: {str(e)}"}), 500

@fuel_agent_bp.route("/api/car/fuel-agent/toggle-online", methods=["POST"])
@require_fuel_agent_auth
def toggle_fuel_agent_online_status():
    """Toggle fuel agent online/offline status"""
    try:
        agent_id = request.current_worker['id']
        result = fuel_agent_service.toggle_fuel_agent_online_status(agent_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to toggle status: {str(e)}"}), 500

@fuel_agent_bp.route("/api/car/fuel-agent/update-location", methods=["POST"])
@require_fuel_agent_auth
def update_fuel_agent_location():
    """Update fuel agent location"""
    try:
        agent_id = request.current_worker['id']
        data = request.get_json() or {}
        
        lat = data.get('latitude')
        lng = data.get('longitude')
        
        if lat is None or lng is None:
            return jsonify({"error": "Latitude and longitude required"}), 400
        
        success = fuel_agent_service.db.update_fuel_agent_status(
            agent_id, lat=lat, lng=lng
        )
        
        if success:
            return jsonify({"success": True, "message": "Location updated"}), 200
        else:
            return jsonify({"error": "Failed to update location"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Location update failed: {str(e)}"}), 500

# ==================== FUEL ORDERS ====================

@fuel_agent_bp.route("/api/car/fuel-agent/fuel-orders", methods=["GET"])
@require_fuel_agent_auth
def get_fuel_orders():
    """Get transparent fuel orders"""
    try:
        agent_id = request.current_worker['id']
        result = fuel_agent_service.get_transparent_fuel_orders(agent_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get fuel orders: {str(e)}"}), 500

@fuel_agent_bp.route("/api/car/fuel-agent/accept-order/<int:order_id>", methods=["POST"])
@require_fuel_agent_auth
def accept_fuel_order(order_id):
    """Accept a fuel order request"""
    try:
        agent_id = request.current_worker['id']
        result = fuel_agent_service.accept_fuel_order_request(agent_id, order_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to accept fuel order: {str(e)}"}), 500

@fuel_agent_bp.route("/api/car/fuel-agent/reject-order/<int:order_id>", methods=["POST"])
@require_fuel_agent_auth
def reject_fuel_order(order_id):
    """Reject a fuel order request"""
    try:
        agent_id = request.current_worker['id']
        data = request.get_json() or {}
        reason = data.get('reason', 'Not interested')
        
        # In a real system, this would log the rejection reason
        # For now, just return success
        return jsonify({
            "success": True,
            "message": "Fuel order rejected",
            "order_id": order_id,
            "reason": reason
        }), 200
            
    except Exception as e:
        return jsonify({"error": f"Failed to reject fuel order: {str(e)}"}), 500

# ==================== ACTIVE DELIVERIES ====================

@fuel_agent_bp.route("/api/car/fuel-agent/active-deliveries", methods=["GET"])
@require_fuel_agent_auth
def get_active_fuel_deliveries():
    """Get fuel agent's active deliveries"""
    try:
        agent_id = request.current_worker['id']
        result = fuel_agent_service.get_active_fuel_deliveries(agent_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get active deliveries: {str(e)}"}), 500

@fuel_agent_bp.route("/api/car/fuel-agent/update-delivery-status/<int:order_id>", methods=["PUT"])
@require_fuel_agent_auth
def update_fuel_delivery_status(order_id):
    """Update fuel delivery status through lifecycle"""
    try:
        agent_id = request.current_worker['id']
        data = request.get_json() or {}
        
        new_status = data.get('status')
        if not new_status:
            return jsonify({"error": "Status is required"}), 400
        
        result = fuel_agent_service.update_fuel_delivery_status(agent_id, order_id, new_status)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to update delivery status: {str(e)}"}), 500

# ==================== EARNINGS ====================

@fuel_agent_bp.route("/api/car/fuel-agent/earnings", methods=["GET"])
@require_fuel_agent_auth
def get_fuel_earnings():
    """Get fuel earnings insights"""
    try:
        agent_id = request.current_worker['id']
        period = request.args.get('period', 'all')  # today, week, month, all
        
        result = fuel_agent_service.get_fuel_earnings_insights(agent_id, period)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get earnings: {str(e)}"}), 500

@fuel_agent_bp.route("/api/car/fuel-agent/earnings-history", methods=["GET"])
@require_fuel_agent_auth
def get_fuel_earnings_history():
    """Get detailed fuel earnings history"""
    try:
        agent_id = request.current_worker['id']
        period = request.args.get('period', 'month')
        limit = int(request.args.get('limit', 50))
        
        earnings = fuel_agent_service.db.get_fuel_agent_earnings(agent_id, period)
        
        # Get detailed history (simplified)
        conn = fuel_agent_service.db.get_conn()
        cur = conn.cursor()
        
        date_filter = ""
        params = [agent_id]
        
        if period == 'today':
            date_filter = "AND date = CURRENT_DATE"
        elif period == 'week':
            date_filter = "AND date >= date('now', '-7 days')"
        elif period == 'month':
            date_filter = "AND date >= date('now', '-1 month')"
        
        cur.execute(f"""
            SELECT 
                fae.*,
                fo.fuel_type,
                fo.quantity_liters,
                fo.customer_rating
            FROM fuel_agent_earnings fae
            JOIN fuel_orders fo ON fae.order_id = fo.id
            WHERE fae.agent_id = ? {date_filter}
            ORDER BY fae.date DESC
            LIMIT ?
        """, params + [limit])
        
        rows = cur.fetchall()
        conn.close()
        
        history = [dict(row) for row in rows]
        
        return jsonify({
            "success": True,
            "period": period,
            "history": history,
            "summary": earnings
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get earnings history: {str(e)}"}), 500

# ==================== PERFORMANCE & SAFETY ====================

@fuel_agent_bp.route("/api/car/fuel-agent/performance", methods=["GET"])
@require_fuel_agent_auth
def get_fuel_performance():
    """Get fuel performance metrics and safety insights"""
    try:
        agent_id = request.current_worker['id']
        result = fuel_agent_service.get_fuel_performance_safety(agent_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get performance: {str(e)}"}), 500

@fuel_agent_bp.route("/api/car/fuel-agent/metrics", methods=["GET"])
@require_fuel_agent_auth
def get_fuel_metrics():
    """Get raw fuel performance metrics"""
    try:
        agent_id = request.current_worker['id']
        metrics = fuel_agent_service.db.get_fuel_agent_metrics(agent_id)
        
        return jsonify({
            "success": True,
            "metrics": metrics
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get metrics: {str(e)}"}), 500

# ==================== EMERGENCY SOS ====================

@fuel_agent_bp.route("/api/car/fuel-agent/emergency-alert", methods=["POST"])
@require_fuel_agent_auth
def trigger_fuel_emergency():
    """Trigger emergency SOS alert"""
    try:
        agent_id = request.current_worker['id']
        data = request.get_json() or {}
        
        lat = data.get('latitude')
        lng = data.get('longitude')
        
        if lat is None or lng is None:
            return jsonify({"error": "Location coordinates required"}), 400
        
        result = fuel_agent_service.trigger_fuel_emergency_sos(agent_id, lat, lng)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to trigger emergency: {str(e)}"}), 500

@fuel_agent_bp.route("/api/car/fuel-agent/emergency-alerts", methods=["GET"])
@require_fuel_agent_auth
def get_fuel_emergency_alerts():
    """Get fuel agent's emergency alerts"""
    try:
        agent_id = request.current_worker['id']
        alerts = fuel_agent_service.db.get_fuel_emergency_alerts(agent_id)
        
        return jsonify({
            "success": True,
            "alerts": alerts
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get emergency alerts: {str(e)}"}), 500

# ==================== DELIVERY PROOF SYSTEM ====================

@fuel_agent_bp.route("/api/car/fuel-agent/upload-delivery-proof/<int:order_id>", methods=["POST"])
@require_fuel_agent_auth
def upload_fuel_delivery_proof(order_id):
    """Upload fuel delivery completion proof"""
    try:
        agent_id = request.current_worker['id']
        
        # Handle file uploads
        fuel_meter_file = request.files.get('fuel_meter_photo')
        delivery_photo_file = request.files.get('delivery_confirmation_photo')
        notes = request.form.get('delivery_notes', '')
        
        if not fuel_meter_file and not delivery_photo_file:
            return jsonify({"error": "At least one photo is required"}), 400
        
        result = fuel_agent_service.upload_fuel_delivery_proof(
            agent_id, order_id, fuel_meter_file, delivery_photo_file, notes
        )
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to upload proof: {str(e)}"}), 500

@fuel_agent_bp.route("/api/car/fuel-agent/delivery-proofs/<int:order_id>", methods=["GET"])
@require_fuel_agent_auth
def get_fuel_delivery_proofs(order_id):
    """Get proofs for a specific fuel order"""
    try:
        agent_id = request.current_worker['id']
        
        # Verify order belongs to agent
        active_deliveries = fuel_agent_service.db.get_active_fuel_deliveries(agent_id)
        order_exists = any(delivery["id"] == order_id for delivery in active_deliveries)
        
        if not order_exists:
            return jsonify({"error": "Order not found or access denied"}), 404
        
        proofs = fuel_agent_service.db.get_delivery_proofs(order_id)
        
        return jsonify({
            "success": True,
            "order_id": order_id,
            "proofs": proofs
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get delivery proofs: {str(e)}"}), 500

@fuel_agent_bp.route("/uploads/fuel_delivery_proofs/<filename>", methods=["GET"])
@require_fuel_agent_auth
def serve_fuel_proof_file(filename):
    """Serve uploaded fuel proof files"""
    try:
        upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "fuel_delivery_proofs")
        return send_from_directory(upload_dir, filename)
    except Exception as e:
        return jsonify({"error": f"Failed to serve file: {str(e)}"}), 500

# ==================== DASHBOARD SUMMARY ====================

@fuel_agent_bp.route("/api/car/fuel-agent/dashboard-summary", methods=["GET"])
@require_fuel_agent_auth
def get_fuel_dashboard_summary():
    """Get complete fuel dashboard summary"""
    try:
        agent_id = request.current_worker['id']
        
        # Get all dashboard data
        status_data = fuel_agent_service.get_fuel_demand_status(agent_id)
        orders_data = fuel_agent_service.get_transparent_fuel_orders(agent_id)
        active_data = fuel_agent_service.get_active_fuel_deliveries(agent_id)
        earnings_data = fuel_agent_service.get_fuel_earnings_insights(agent_id, 'today')
        performance_data = fuel_agent_service.get_fuel_performance_safety(agent_id)
        
        return jsonify({
            "success": True,
            "summary": {
                "status": status_data,
                "fuel_orders": orders_data,
                "active_deliveries": active_data,
                "earnings": earnings_data,
                "performance": performance_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get dashboard summary: {str(e)}"}), 500

# ==================== ERROR HANDLING ====================

@fuel_agent_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@fuel_agent_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

@fuel_agent_bp.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return jsonify({"error": "Access forbidden"}), 403
