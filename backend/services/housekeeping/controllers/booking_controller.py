from flask import Blueprint, request, jsonify, current_app
import random
import time
from services.housekeeping.services.booking_service import BookingService
from auth_utils import verify_token
from user_db import UserDB
from worker_db import WorkerDB
from services.housekeeping.socket_handlers import emit_new_booking, emit_booking_update

housekeeping_bp = Blueprint('housekeeping', __name__)
booking_service = BookingService()
user_db = UserDB()
worker_db = WorkerDB()

def get_socketio():
    try:
        return current_app.extensions.get('socketio')
    except:
        return None

def get_current_user():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None, "Missing token"
    
    try:
        token = auth_header.split(" ")[1]
        username = verify_token(token)
        if not username:
            return None, "Invalid token"
        
        # Check if user exists (User or Worker)
        # PRIORITIZE WORKER CHECK to prevent identity conflicts (e.g. if user has same email/username)
        # This ensures workers always see their dashboard correctly
        worker = worker_db.get_worker_by_email(username)
        if worker:
             return {"type": "worker", "data": {"id": worker['id'], "email": worker['email'], "service": worker['service']}}, None

        try:
            user_id = user_db.get_user_by_username(username)
            if user_id:
                return {"type": "user", "data": {"id": user_id, "username": username}}, None
        except AttributeError:
            pass 
        except Exception:
            pass 

        return None, "User not found"
    except Exception as e:
        return None, str(e)

@housekeeping_bp.route('/worker/status', methods=['GET', 'POST'])
def worker_status():
    user, error = get_current_user()
    if not user or user['type'] != 'worker':
        return jsonify({"error": "Unauthorized"}), 401
    
    worker_id = user['data']['id']
    
    if request.method == 'POST':
        data = request.json
        is_online = data.get('is_online', False)
        print(f"[DEBUG] Setting worker {worker_id} status to {is_online}")
        try:
            booking_service.db.set_worker_online(worker_id, is_online)
            return jsonify({"message": "Status updated", "is_online": is_online}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    else:
        is_online = booking_service.db.get_worker_online_status(worker_id)
        return jsonify({"is_online": is_online}), 200

@housekeeping_bp.route('/worker/balance', methods=['GET'])
def get_wallet_balance():
    user, error = get_current_user()
    if not user or user['type'] != 'worker':
        return jsonify({"error": "Unauthorized"}), 401
    
    worker = worker_db.get_worker_by_id(user['data']['id'])
    if not worker:
        return jsonify({"error": "Worker not found"}), 404
        
    return jsonify({"balance": worker.get('wallet_balance', 0.0)}), 200

@housekeeping_bp.route('/recommendations/workers', methods=['GET'])
def get_recommended_workers():
    import random
    service_type = request.args.get('service_type')
    date = request.args.get('date')
    time_slot = request.args.get('time')
    booking_type = request.args.get('booking_type', 'schedule')
    address = request.args.get('address')
    
    if not service_type:
        return jsonify({"error": "service_type is required"}), 400
        
    # If date and time are provided, we filter by actual availability for that slot
    if date and time_slot:
        all_workers = booking_service.check_availability(
            service_type, date, time_slot, address, booking_type=booking_type
        )
    else:
        # Fallback to general list of workers who offer this service
        all_workers = worker_db.get_workers_by_service('housekeeping')
    
    recommended = []
    for w in all_workers:
        # Check if worker offers specific sub-service (e.g. Deep Cleaning)
        # Note: check_availability already checks this, but general fallback doesn't
        if not (date and time_slot) and not booking_service.db.worker_offers_service(w['id'], service_type):
            continue
            
        # Add online status
        w['is_online'] = booking_service.db.get_worker_online_status(w['id'])
        
        # Mock some matching data for the UI
        w['rating'] = w.get('rating', round(random.uniform(4.0, 5.0), 1))
        w['completed_jobs'] = w.get('completed_jobs', random.randint(10, 100))
        w['score'] = random.uniform(0.8, 0.99) # Matching score
        
        recommended.append(w)
            
    # Sort: online first, then by rating
    recommended.sort(key=lambda x: (x.get('is_online', False), x.get('rating', 0)), reverse=True)
    
    return jsonify(recommended), 200

@housekeeping_bp.route('/services', methods=['GET'])
def list_services():
    worker_id = request.args.get('worker_id')
    services = booking_service.get_service_types(worker_id=worker_id)
    top_cleaners = booking_service.get_top_cleaners()
    return jsonify({
        "services": services,
        "top_cleaners": top_cleaners
    }), 200

@housekeeping_bp.route('/worker/services', methods=['GET', 'POST'])
def manage_worker_services():
    user, error = get_current_user()
    if not user or user['type'] != 'worker':
        return jsonify({"error": "Unauthorized"}), 401
    
    worker_id = user['data']['id']
    
    if request.method == 'GET':
        services = booking_service.db.get_services_for_worker(worker_id)
        return jsonify({"services": services}), 200
    
    data = request.json or {}
    services = data.get('services', [])
    ok = booking_service.db.upsert_worker_services(worker_id, services)
    if not ok:
        return jsonify({"error": "Failed to save services"}), 400
    return jsonify({"success": True}), 200

@housekeeping_bp.route('/slots', methods=['GET'])
def get_available_slots():
    service_type = request.args.get('service_type')
    date = request.args.get('date')
    worker_id = request.args.get('worker_id')
    
    if not service_type or not date:
        return jsonify({"error": "Missing service_type or date"}), 400
        
    slots = booking_service.get_aggregated_slots(service_type, date, worker_id=worker_id)
            
    return jsonify({"slots": slots}), 200

@housekeeping_bp.route('/check-availability', methods=['POST'])
def check_availability():
    user, error = get_current_user()
    if not user or user['type'] != 'user':
        return jsonify({"error": "Unauthorized: Only users can check availability"}), 401

    data = request.json
    booking_type = data.get('booking_type', 'schedule')
    
    if booking_type == 'instant':
        from datetime import datetime
        if not data.get('date'):
            data['date'] = datetime.now().strftime('%Y-%m-%d')
        if not data.get('time'):
            data['time'] = datetime.now().strftime('%I:%M %p')
            
    required = ['service_type', 'address', 'date', 'time']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    # Check availability
    workers = booking_service.check_availability(
        data['service_type'], 
        data['date'], 
        data['time'], 
        data.get('address'),
        worker_id=data.get('worker_id'),
        booking_type=data.get('booking_type', 'schedule')
    )
    
    if not workers:
        return jsonify({"error": "No workers available for this slot", "retry": True}), 404
        
    return jsonify({"success": True, "workers_count": len(workers)}), 200

@housekeeping_bp.route('/confirm-booking', methods=['POST'])
def confirm_booking():
    user, error = get_current_user()
    if not user or user['type'] != 'user':
        return jsonify({"error": "Unauthorized: Only users can book services"}), 401

    data = request.json
    booking_type = data.get('booking_type', 'schedule')
    
    if booking_type == 'instant':
        from datetime import datetime
        if not data.get('date'):
            data['date'] = datetime.now().strftime('%Y-%m-%d')
        if not data.get('time'):
            data['time'] = datetime.now().strftime('%I:%M %p')
            
    required = ['service_type', 'address', 'date', 'time']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    # 1. Check availability
    worker_id = data.get('worker_id')
    if not worker_id:
        return jsonify({"error": "A professional must be selected to complete the booking"}), 400

    workers = booking_service.check_availability(
        data['service_type'], 
        data['date'], 
        data['time'], 
        data.get('address'),
        worker_id=worker_id,
        booking_type=booking_type
    )
    
    # Strictly verify that the SELECTED worker is in the available list
    is_available = any(str(w['id']) == str(worker_id) for w in workers)
    if not is_available:
        return jsonify({"error": "The selected professional is no longer available for this slot. Please try another professional or slot.", "retry": True}), 404

    # 2. Create booking request
    result = booking_service.create_booking_request(
        user['data']['id'], 
        data['service_type'], 
        data['address'], 
        data['date'], 
        data['time'], 
        worker_id=worker_id,
        home_size=data.get('home_size'),
        add_ons=data.get('add_ons'),
        booking_type=booking_type
    )
    
    if result.get('error'):
        return jsonify(result), 400
        
    # Notify via WebSocket
    socketio = get_socketio()
    if socketio:
        try:
            # Notify Worker
            if result.get('worker_id'):
                emit_new_booking(socketio, result, result['worker_id'])
            
            # Notify User (Confirmation)
            emit_booking_update(socketio, result['booking_id'], result['status'], user_id=user['data']['id'])
        except Exception as e:
            print(f"[WS ERROR] Failed to emit booking events: {e}")

    return jsonify(result), 201

@housekeeping_bp.route('/cancel-booking', methods=['POST'])
def cancel_booking():
    user, error = get_current_user()
    if not user:
        return jsonify({"error": error}), 401
    
    data = request.json
    booking_id = data.get('booking_id')
    
    if not booking_id:
        return jsonify({"error": "Missing booking_id"}), 400
        
    # Fetch booking to get worker_id for notification
    booking = booking_service.db.get_booking_by_id(booking_id)
        
    success, message = booking_service.cancel_booking(booking_id, user['data']['id'])
    
    if success:
        # Emit WebSocket event to Worker and User (self)
        socketio = get_socketio()
        if socketio and booking:
            try:
                # Notify User (confirmation on other devices)
                emit_booking_update(socketio, booking_id, 'CANCELLED', user_id=user['data']['id'])
                
                # Notify Worker if assigned
                if booking.get('worker_id'):
                    emit_booking_update(socketio, booking_id, 'CANCELLED', worker_id=booking['worker_id'])
            except Exception as e:
                print(f"[WS ERROR] Failed to emit cancel update: {e}")
                
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"error": message}), 400

@housekeeping_bp.route('/my-bookings', methods=['GET'])
def my_bookings():
    user, error = get_current_user()
    if not user:
        return jsonify({"error": error}), 401
    
    print(f"[DEBUG] my_bookings called for user: {user['data']['id']} ({user['type']})")

    if user['type'] == 'user':
        bookings = booking_service.db.get_user_bookings(user['data']['id'], visible_only=True)
    else:
        bookings = booking_service.db.get_worker_bookings(user['data']['id'])
        print(f"[DEBUG] Found {len(bookings)} bookings for worker {user['data']['id']}")
    
    # Enrich bookings with worker_name using WorkerDB
    enriched = []
    for b in bookings:
        try:
            wid = b.get('worker_id') if isinstance(b, dict) else None
            name = None
            if wid:
                w = worker_db.get_worker_by_id(wid)
                if w:
                    name = w.get('full_name') or w.get('name')
            if isinstance(b, dict):
                b['worker_name'] = name or b.get('worker_name') or 'Assigned Provider'
                enriched.append(b)
            else:
                enriched.append(b)
        except Exception:
            if isinstance(b, dict):
                b['worker_name'] = b.get('worker_name') or 'Assigned Provider'
            enriched.append(b)
        
    return jsonify({"bookings": enriched}), 200

@housekeeping_bp.route('/user/accept-booking', methods=['POST'])
def user_accept_booking():
    user, error = get_current_user()
    if not user or user['type'] != 'user':
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json or {}
    booking_id = data.get('booking_id')
    if not booking_id:
        return jsonify({"error": "Missing booking_id"}), 400
    success = booking_service.db.accept_booking_by_user(booking_id, user['data']['id'])
    if success:
        # Emit update to refresh user's other devices
        socketio = get_socketio()
        if socketio:
            try:
                emit_booking_update(socketio, booking_id, 'ACCEPTED_BY_USER', user_id=user['data']['id'])
            except Exception as e:
                print(f"[WS ERROR] Failed to emit user accept update: {e}")
        return jsonify({"success": True}), 200
    return jsonify({"error": "Booking not found or not owned by user"}), 404

@housekeeping_bp.route('/worker/update-status', methods=['POST'])
def update_status():
    user, error = get_current_user()
    if not user or user['type'] != 'worker':
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    booking_id = data.get('booking_id')
    status = data.get('status')
    
    if not booking_id or not status:
        return jsonify({"error": "Missing booking_id or status"}), 400
        
    # Fetch booking to get user_id for notification
    booking = booking_service.db.get_booking_by_id(booking_id)
    
    success, msg, final_status = booking_service.update_booking_status_by_worker(booking_id, user['data']['id'], status)
    
    if success:
        # Emit WebSocket event to User
        socketio = get_socketio()
        if socketio and booking:
            try:
                emit_booking_update(socketio, booking_id, final_status, user_id=booking['user_id'])
            except Exception as e:
                print(f"[WS ERROR] Failed to emit update: {e}")
                
        return jsonify({"success": True, "message": msg, "status": final_status}), 200
    else:
        return jsonify({"error": msg}), 400

@housekeeping_bp.route('/worker/start-job', methods=['POST'])
def start_job():
    user, error = get_current_user()
    if not user or user['type'] != 'worker':
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    booking_id = data.get('booking_id')
    if not booking_id:
        return jsonify({"error": "Missing booking_id"}), 400
        
    success, msg, otp = booking_service.start_job(booking_id, user['data']['id'])
    
    if success:
        # Emit WebSocket event to User
        socketio = get_socketio()
        if socketio:
            try:
                # Fetch booking to get user_id
                booking = booking_service.db.get_booking_by_id(booking_id)
                emit_booking_update(socketio, booking_id, 'IN_PROGRESS', user_id=booking['user_id'])
            except Exception as e:
                print(f"[WS ERROR] Failed to emit update: {e}")
                
        # In a real app, we don't return OTP to worker, but for demo/testing it helps
        return jsonify({"success": True, "message": msg, "otp": otp}), 200
    else:
        return jsonify({"error": msg}), 400

@housekeeping_bp.route('/worker/complete-job', methods=['POST'])
def complete_job():
    user, error = get_current_user()
    if not user or user['type'] != 'worker':
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    booking_id = data.get('booking_id')
    otp = data.get('otp')
    
    if not booking_id or not otp:
        return jsonify({"error": "Missing booking_id or otp"}), 400
        
    success, msg = booking_service.complete_job(booking_id, user['data']['id'], otp)
    
    if success:
        # Emit WebSocket event to User
        socketio = get_socketio()
        if socketio:
            try:
                # Fetch booking to get user_id
                booking = booking_service.db.get_booking_by_id(booking_id)
                emit_booking_update(socketio, booking_id, 'COMPLETED', user_id=booking['user_id'])
            except Exception as e:
                print(f"[WS ERROR] Failed to emit update: {e}")
                
        return jsonify({"success": True, "message": msg}), 200
    else:
        return jsonify({"error": msg}), 400
