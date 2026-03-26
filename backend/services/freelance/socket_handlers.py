from flask_socketio import emit, join_room, leave_room
from flask import request
from .services.freelance_service import freelance_service
from .models.database import freelance_db
import psycopg2
from datetime import datetime

# Store online users
online_users = {}

def handle_freelance_socket_events(socketio):

    @socketio.on('join_freelance_project')
    def handle_join_project(data):
        """Join a project room for real-time messaging"""
        try:
            project_id = data.get('project_id')
            user_id = data.get('user_id')
            
            if not project_id or not user_id:
                emit('error', {'message': 'Project ID and User ID required'})
                return
            
            # Join the project room
            room = f"project_{project_id}"
            join_room(room)
            
            # Add user to online users
            online_users[user_id] = {
                'room': room,
                'joined_at': datetime.now().isoformat(),
                'socket_id': request.sid
            }
            
            # Notify others in the room
            emit('user_joined', {
                'user_id': user_id,
                'message': f'User {user_id} joined the project'
            }, room=room, include_self=False)
            
            # Send confirmation to user
            emit('joined_project', {
                'project_id': project_id,
                'message': f'Successfully joined project {project_id}'
            })
            
            print(f"User {user_id} joined project room {project_id}")
            
        except Exception as e:
            print(f"Error joining project: {e}")
            emit('error', {'message': 'Failed to join project'})

    @socketio.on('leave_freelance_project')
    def handle_leave_project(data):
        """Leave a project room"""
        try:
            project_id = data.get('project_id')
            user_id = data.get('user_id')
            
            if not project_id or not user_id:
                return
            
            room = f"project_{project_id}"
            leave_room(room)
            
            # Remove from online users
            if user_id in online_users:
                del online_users[user_id]
            
            # Notify others
            emit('user_left', {
                'user_id': user_id,
                'message': f'User {user_id} left the project'
            }, room=room, include_self=False)
            
            print(f"User {user_id} left project room {project_id}")
            
        except Exception as e:
            print(f"Error leaving project: {e}")

    @socketio.on('send_freelance_message')
    def handle_send_message(data):
        """Send a real-time message in a project"""
        try:
            project_id = data.get('project_id')
            sender_id = data.get('sender_id')
            message = data.get('message')
            file_attachment = data.get('file_attachment')
            
            if not all([project_id, sender_id, message]):
                emit('error', {'message': 'Missing required fields'})
                return
            
            # Save message to database
            success, result = freelance_service.send_message(
                project_id=project_id,
                sender_id=sender_id,
                message=message,
                file_attachment=file_attachment
            )
            
            if not success:
                emit('error', {'message': 'Failed to send message'})
                return
            
            # Get message details for broadcasting
            conn = freelance_db.get_conn()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT fm.*, u.name as sender_name 
                    FROM freelance_messages fm
                    LEFT JOIN users u ON fm.sender_id = u.id
                    WHERE fm.id = %s
                """, (result,))
                message_data = cursor.fetchone()
                
                if message_data:
                    message_dict = freelance_db._row_to_dict(message_data, cursor)
                    
                    # Broadcast to all users in the project room
                    room = f"project_{project_id}"
                    emit('new_message', message_dict, room=room)
                    
                    print(f"Message sent in project {project_id} by user {sender_id}")
                    
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            print(f"Error sending message: {e}")
            emit('error', {'message': 'Failed to send message'})

    @socketio.on('typing_start')
    def handle_typing_start(data):
        """Handle typing indicator start"""
        try:
            project_id = data.get('project_id')
            user_id = data.get('user_id')
            
            if not project_id or not user_id:
                return
            
            room = f"project_{project_id}"
            emit('user_typing', {
                'user_id': user_id,
                'is_typing': True
            }, room=room, include_self=False)
            
        except Exception as e:
            print(f"Error handling typing start: {e}")

    @socketio.on('typing_stop')
    def handle_typing_stop(data):
        """Handle typing indicator stop"""
        try:
            project_id = data.get('project_id')
            user_id = data.get('user_id')
            
            if not project_id or not user_id:
                return
            
            room = f"project_{project_id}"
            emit('user_typing', {
                'user_id': user_id,
                'is_typing': False
            }, room=room, include_self=False)
            
        except Exception as e:
            print(f"Error handling typing stop: {e}")

    @socketio.on('get_online_users')
    def handle_get_online_users(data):
        """Get list of online users in a project"""
        try:
            project_id = data.get('project_id')
            
            # Get online users in this project
            project_online_users = [
                {'user_id': uid, **info} 
                for uid, info in online_users.items() 
                if info['room'] == f"project_{project_id}"
            ]
            
            emit('online_users_list', {
                'project_id': project_id,
                'users': project_online_users
            })
            
        except Exception as e:
            print(f"Error getting online users: {e}")
            emit('error', {'message': 'Failed to get online users'})

    @socketio.on('mark_messages_read')
    def handle_mark_messages_read(data):
        """Mark messages as read for a user"""
        try:
            project_id = data.get('project_id')
            user_id = data.get('user_id')
            
            if not project_id or not user_id:
                return
            
            # Mark messages as read in database
            conn = freelance_db.get_conn()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE freelance_messages 
                    SET is_read = TRUE 
                    WHERE project_id = %s 
                    AND sender_id != %s 
                    AND is_read = FALSE
                """, (project_id, user_id))
                conn.commit()
                
                # Notify other user that messages were read
                room = f"project_{project_id}"
                emit('messages_read', {
                    'project_id': project_id,
                    'read_by': user_id
                }, room=room, include_self=False)
                
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            print(f"Error marking messages read: {e}")

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle user disconnection"""
        try:
            # Find and remove user from online users
            user_to_remove = None
            for user_id, info in online_users.items():
                if info['socket_id'] == request.sid:
                    user_to_remove = user_id
                    break
            
            if user_to_remove:
                room = online_users[user_to_remove]['room']
                del online_users[user_to_remove]
                
                # Notify others in the room
                emit('user_left', {
                    'user_id': user_to_remove,
                    'message': f'User {user_to_remove} disconnected'
                }, room=room, include_self=False)
                
                print(f"User {user_to_remove} disconnected from {room}")
                
        except Exception as e:
            print(f"Error handling disconnect: {e}")

    return socketio
