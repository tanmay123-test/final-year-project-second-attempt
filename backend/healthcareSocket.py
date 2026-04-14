from flask_socketio import SocketIO, emit, join_room, leave_room
import os

# Initialize SocketIO (will be initialized later with app)
socketio = None

def init_socketio(app):
    """Initialize SocketIO with Flask app"""
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*")
    return socketio

# Socket event handlers (will be registered after socketio is initialized)
def register_socket_events(socketio_instance):
    """Register socket events after socketio is initialized"""
    
    @socketio_instance.on('connect')
    def handle_connect():
        print(f"Client connected: {request.sid}")
        socketio_instance.emit('connected', {'message': 'Connected to healthcare socket'})

    @socketio_instance.on('disconnect')
    def handle_disconnect():
        print(f"Client disconnected: {request.sid}")

    @socketio_instance.on('join_healthcare_room')
    def handle_join_healthcare_room(data):
        """Join a room for healthcare updates"""
        room = data.get('room', 'healthcare_general')
        join_room(room)
        socketio_instance.emit('joined_room', {'room': room})

    @socketio_instance.on('leave_healthcare_room')
    def handle_leave_healthcare_room(data):
        """Leave a healthcare room"""
        room = data.get('room', 'healthcare_general')
        leave_room(room)
        socketio_instance.emit('left_room', {'room': room})

def notify_worker_approval(worker_id, worker_name, status):
    """Notify when a worker is approved/rejected"""
    if socketio:
        socketio.emit('worker_approval_update', {
            'worker_id': worker_id,
            'worker_name': worker_name,
            'status': status,
            'message': f'Dr. {worker_name} has been {status}!'
        }, room='healthcare_admin')

def notify_new_worker_registration(worker_data):
    """Notify admin about new worker registration"""
    if socketio:
        socketio.emit('new_worker_registration', {
            'worker_id': worker_data.get('id'),
            'worker_name': worker_data.get('full_name'),
            'email': worker_data.get('email'),
            'specialization': worker_data.get('specialization'),
            'message': f'New healthcare worker registration: Dr. {worker_data.get("full_name")}'
        }, room='healthcare_admin')

def notify_availability_update(worker_id, date, slots):
    """Notify about availability updates"""
    if socketio:
        socketio.emit('availability_updated', {
            'worker_id': worker_id,
            'date': date,
            'slots': slots,
            'message': f'Availability updated for {date}'
        }, room=f'worker_{worker_id}')

def notify_appointment_booking(worker_id, appointment_data):
    """Notify worker about new appointment booking"""
    if socketio:
        socketio.emit('new_appointment', {
            'appointment_id': appointment_data.get('id'),
            'patient_name': appointment_data.get('patient_name'),
            'date': appointment_data.get('date'),
            'time': appointment_data.get('time'),
            'message': f'New appointment booked for {appointment_data.get("date")} at {appointment_data.get("time")}'
        }, room=f'worker_{worker_id}')
