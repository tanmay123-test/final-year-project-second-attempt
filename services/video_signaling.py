from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import json
import logging
from services.video_session_db import video_session_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoSignalingServer:
    def __init__(self, app):
        self.socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
        self.setup_socket_events()
        logger.info("Video signaling server initialized")
    
    def setup_socket_events(self):
        """Setup all WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            logger.info(f"Client connected: {request.sid}")
            emit('connected', {'message': 'Connected to video signaling server'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            logger.info(f"Client disconnected: {request.sid}")
            # Notify room that user left
            # Note: We don't know which room, so frontend should handle this
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            """Handle user joining a video room"""
            room_id = data.get('room_id')
            user_type = data.get('user_type')  # 'doctor' or 'patient'
            user_id = data.get('user_id')
            
            if not room_id:
                emit('error', {'message': 'Room ID is required'})
                return
            
            # Verify session exists and is live
            session = video_session_db.get_session_by_room(room_id)
            if not session:
                emit('error', {'message': 'Invalid room'})
                return
            
            if session['session_status'] != 'live':
                emit('error', {'message': 'Session is not live yet'})
                return
            
            # Join the room
            join_room(room_id)
            
            # Notify others in room
            emit('user_joined', {
                'user_type': user_type,
                'user_id': user_id,
                'sid': request.sid
            }, room=room_id, include_self=False)
            
            # Confirm to user
            emit('room_joined', {
                'room_id': room_id,
                'user_type': user_type,
                'session': session
            })
            
            logger.info(f"{user_type} {user_id} joined room {room_id}")
        
        @self.socketio.on('leave_room')
        def handle_leave_room(data):
            """Handle user leaving a video room"""
            room_id = data.get('room_id')
            user_type = data.get('user_type')
            user_id = data.get('user_id')
            
            if room_id:
                leave_room(room_id)
                
                # Notify others in room
                emit('user_left', {
                    'user_type': user_type,
                    'user_id': user_id,
                    'sid': request.sid
                }, room=room_id, include_self=False)
                
                logger.info(f"{user_type} {user_id} left room {room_id}")
        
        @self.socketio.on('webrtc_offer')
        def handle_webrtc_offer(data):
            """Handle WebRTC offer signaling"""
            room_id = data.get('room_id')
            offer = data.get('offer')
            target_sid = data.get('target_sid')
            
            if not room_id or not offer:
                emit('error', {'message': 'Room ID and offer are required'})
                return
            
            # Forward offer to specific target or broadcast to room
            if target_sid:
                emit('webrtc_offer', {
                    'offer': offer,
                    'sender_sid': request.sid
                }, room=target_sid)
            else:
                emit('webrtc_offer', {
                    'offer': offer,
                    'sender_sid': request.sid
                }, room=room_id, include_self=False)
            
            logger.info(f"WebRTC offer sent in room {room_id}")
        
        @self.socketio.on('webrtc_answer')
        def handle_webrtc_answer(data):
            """Handle WebRTC answer signaling"""
            room_id = data.get('room_id')
            answer = data.get('answer')
            target_sid = data.get('target_sid')
            
            if not room_id or not answer:
                emit('error', {'message': 'Room ID and answer are required'})
                return
            
            # Forward answer to specific target or broadcast to room
            if target_sid:
                emit('webrtc_answer', {
                    'answer': answer,
                    'sender_sid': request.sid
                }, room=target_sid)
            else:
                emit('webrtc_answer', {
                    'answer': answer,
                    'sender_sid': request.sid
                }, room=room_id, include_self=False)
            
            logger.info(f"WebRTC answer sent in room {room_id}")
        
        @self.socketio.on('ice_candidate')
        def handle_ice_candidate(data):
            """Handle ICE candidate signaling"""
            room_id = data.get('room_id')
            candidate = data.get('candidate')
            target_sid = data.get('target_sid')
            
            if not room_id or not candidate:
                emit('error', {'message': 'Room ID and candidate are required'})
                return
            
            # Forward ICE candidate to specific target or broadcast to room
            if target_sid:
                emit('ice_candidate', {
                    'candidate': candidate,
                    'sender_sid': request.sid
                }, room=target_sid)
            else:
                emit('ice_candidate', {
                    'candidate': candidate,
                    'sender_sid': request.sid
                }, room=room_id, include_self=False)
            
            logger.info(f"ICE candidate sent in room {room_id}")
        
        @self.socketio.on('chat_message')
        def handle_chat_message(data):
            """Handle chat messages during video call"""
            room_id = data.get('room_id')
            message = data.get('message')
            user_type = data.get('user_type')
            user_id = data.get('user_id')
            
            if not room_id or not message:
                emit('error', {'message': 'Room ID and message are required'})
                return
            
            # Broadcast message to room
            emit('chat_message', {
                'message': message,
                'user_type': user_type,
                'user_id': user_id,
                'timestamp': str(datetime.now()),
                'sender_sid': request.sid
            }, room=room_id)
            
            logger.info(f"Chat message in room {room_id}: {message}")
        
        @self.socketio.on('start_call')
        def handle_start_call(data):
            """Handle call start notification"""
            room_id = data.get('room_id')
            user_type = data.get('user_type')
            
            if not room_id:
                emit('error', {'message': 'Room ID is required'})
                return
            
            # Broadcast call started to room
            emit('call_started', {
                'room_id': room_id,
                'user_type': user_type,
                'timestamp': str(datetime.now())
            }, room=room_id)
            
            logger.info(f"Call started in room {room_id} by {user_type}")
        
        @self.socketio.on('end_call')
        def handle_end_call(data):
            """Handle call end notification"""
            room_id = data.get('room_id')
            user_type = data.get('user_type')
            
            if not room_id:
                emit('error', {'message': 'Room ID is required'})
                return
            
            # Broadcast call ended to room
            emit('call_ended', {
                'room_id': room_id,
                'user_type': user_type,
                'timestamp': str(datetime.now())
            }, room=room_id)
            
            logger.info(f"Call ended in room {room_id} by {user_type}")
        
        @self.socketio.on('ping')
        def handle_ping():
            """Handle ping for connection health check"""
            emit('pong', {'timestamp': str(datetime.now())})
    
    def emit_to_room(self, room_id, event, data):
        """Emit event to specific room"""
        self.socketio.emit(event, data, room=room_id)
    
    def get_socketio_instance(self):
        """Get SocketIO instance for Flask app"""
        return self.socketio

# Global instance
video_signaling = None

def init_video_signaling(app):
    """Initialize video signaling server"""
    global video_signaling
    video_signaling = VideoSignalingServer(app)
    return video_signaling.get_socketio_instance()

# Import datetime for timestamp
from datetime import datetime
