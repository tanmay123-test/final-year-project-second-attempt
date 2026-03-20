
from flask_socketio import emit, join_room, leave_room
from flask import request
import logging

logger = logging.getLogger(__name__)

def init_housekeeping_socket(socketio):
    """
    Initialize housekeeping socket events using the existing socketio instance.
    """
    
    @socketio.on('join_housekeeping')
    def handle_join_housekeeping(data):
        """
        Join a room specific to a user or worker for real-time updates.
        data: { 'user_type': 'user'|'worker', 'id': <id> }
        """
        user_type = data.get('user_type')
        user_id = data.get('id')
        
        if not user_type or not user_id:
            return
            
        room = f"{user_type}_{user_id}"
        join_room(room)
        logger.info(f"Client {request.sid} joined room: {room}")
        emit('room_joined', {'room': room})

    @socketio.on('leave_housekeeping')
    def handle_leave_housekeeping(data):
        user_type = data.get('user_type')
        user_id = data.get('id')
        
        if not user_type or not user_id:
            return
            
        room = f"{user_type}_{user_id}"
        leave_room(room)
        logger.info(f"Client {request.sid} left room: {room}")

def emit_booking_update(socketio, booking_id, status, worker_id=None, user_id=None, data=None):
    """
    Emit booking update to relevant parties.
    """
    payload = {
        'booking_id': booking_id,
        'status': status,
        'data': data
    }
    
    if worker_id:
        worker_room = f"worker_{worker_id}"
        socketio.emit('booking_update', payload, room=worker_room)
        logger.info(f"Emitted booking_update to {worker_room}")
        
    if user_id:
        user_room = f"user_{user_id}"
        socketio.emit('booking_update', payload, room=user_room)
        logger.info(f"Emitted booking_update to {user_room}")

def emit_new_booking(socketio, booking, worker_id):
    """
    Emit new booking event to worker.
    """
    worker_room = f"worker_{worker_id}"
    socketio.emit('new_booking', booking, room=worker_room)
    logger.info(f"Emitted new_booking to {worker_room}")
