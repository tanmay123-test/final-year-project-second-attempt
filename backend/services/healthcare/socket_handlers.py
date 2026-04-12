
from flask_socketio import emit, join_room, leave_room
from flask import request
import logging

logger = logging.getLogger(__name__)

def init_healthcare_socket(socketio):
    """
    Initialize healthcare socket events using the existing socketio instance.
    """
    
    @socketio.on('join_healthcare')
    def handle_join_healthcare(data):
        """
        Join a room specific to a user or doctor for real-time updates.
        data: { 'user_type': 'user'|'worker', 'id': <id> }
        """
        user_type = data.get('user_type')
        user_id = data.get('id')
        
        if not user_type or not user_id:
            logger.warning(f"Invalid join_healthcare data: {data}")
            return
            
        room = f"healthcare_{user_type}_{user_id}"
        join_room(room)
        logger.info(f"Client {request.sid} joined healthcare room: {room}")
        emit('room_joined', {'room': room})

    @socketio.on('leave_healthcare')
    def handle_leave_healthcare(data):
        user_type = data.get('user_type')
        user_id = data.get('id')
        
        if not user_type or not user_id:
            return
            
        room = f"healthcare_{user_type}_{user_id}"
        leave_room(room)
        logger.info(f"Client {request.sid} left healthcare room: {room}")

def emit_appointment_update(socketio, appointment_id, status, worker_id=None, user_id=None, data=None):
    """
    Emit appointment update to relevant parties.
    """
    payload = {
        'appointment_id': appointment_id,
        'status': status,
        'data': data
    }
    
    if worker_id:
        worker_room = f"healthcare_worker_{worker_id}"
        socketio.emit('appointment_update', payload, room=worker_room)
        logger.info(f"Emitted appointment_update to {worker_room}")
        
    if user_id:
        user_room = f"healthcare_user_{user_id}"
        socketio.emit('appointment_update', payload, room=user_room)
        logger.info(f"Emitted appointment_update to {user_room}")

def emit_new_appointment(socketio, appointment, worker_id):
    """
    Emit new appointment event to doctor.
    """
    worker_room = f"healthcare_worker_{worker_id}"
    socketio.emit('new_appointment', appointment, room=worker_room)
    logger.info(f"Emitted new_appointment to {worker_room}")
