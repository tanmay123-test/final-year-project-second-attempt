"""
Consultation Session Service Engine
Business logic for active consultation management, chat, calls, and real-time features
"""

import threading
import time
from datetime import datetime
from typing import List, Dict, Optional
from .consultation_session_db import consultation_session_db
from .expert_availability_db import expert_availability_db
from .automobile_expert_db import automobile_expert_db

class ConsultationSessionService:
    def __init__(self):
        self._lock = threading.Lock()
        self._timer_thread = None
        self._running = False
        self.start_timer_engine()
    
    def start_timer_engine(self):
        """Start the background timer engine for session duration tracking"""
        if not self._running:
            self._running = True
            self._timer_thread = threading.Thread(target=self._timer_worker, daemon=True)
            self._timer_thread.start()
    
    def stop_timer_engine(self):
        """Stop the background timer engine"""
        self._running = False
        if self._timer_thread:
            self._timer_thread.join()
    
    def _timer_worker(self):
        """Background worker for updating session durations"""
        while self._running:
            try:
                with self._lock:
                    self._update_all_active_sessions()
                time.sleep(30)  # Update every 30 seconds
            except Exception as e:
                print(f"Timer engine error: {e}")
                time.sleep(60)
    
    def _update_all_active_sessions(self):
        """Update durations for all active sessions"""
        conn = consultation_session_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT session_id FROM consultation_sessions 
                WHERE status = 'ACTIVE'
            """)
            active_sessions = cursor.fetchall()
            
            for session in active_sessions:
                consultation_session_db.update_session_duration(session[0])
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error updating session durations: {e}")
        finally:
            cursor.close()
            conn.close()
    
    # Session Management
    def start_consultation_session(self, request_id: int, user_id: int, expert_id: int) -> Dict:
        """Start a new consultation session when request is accepted"""
        with self._lock:
            try:
                # Create session
                session_id = consultation_session_db.create_consultation_session(request_id, user_id, expert_id)
                
                # Update request status to IN_PROGRESS
                expert_availability_db.start_consultation(request_id, expert_id)
                
                # Update expert status to BUSY
                expert_availability_db.update_expert_status(expert_id, 'BUSY', request_id)
                
                return {
                    'success': True,
                    'session_id': session_id,
                    'message': 'Consultation session started successfully'
                }
                
            except Exception as e:
                return {'success': False, 'error': f'Failed to start session: {str(e)}'}
    
    def get_active_session(self, expert_id: int) -> Dict:
        """Get expert's current active consultation session"""
        try:
            session = consultation_session_db.get_active_consultation_session(expert_id)
            
            if not session:
                return {'success': False, 'error': 'No active consultation session found'}
            
            # Get complete session details
            session_details = consultation_session_db.get_session_details(session['session_id'])
            
            # Calculate current duration
            duration_seconds = consultation_session_db.get_session_duration(session['session_id'])
            duration_text = self._format_duration(duration_seconds)
            
            # Count unread messages
            unread_count = len([msg for msg in session_details.get('messages', []) 
                              if msg['sender_type'] == 'USER' and not msg['is_read']])
            
            return {
                'success': True,
                'session_id': session['session_id'],
                'status': session['status'],
                'user_name': f'User_{session.get("user_id", "Unknown")}',
                'issue': session.get('issue_description', 'N/A'),
                'category': session.get('area_of_expertise', 'N/A'),
                'duration_seconds': duration_seconds,
                'duration_text': duration_text,
                'unread_messages': unread_count,
                'images_count': len(session_details.get('images', [])),
                'call_status': self._get_current_call_status(session_details.get('calls', [])),
                'typing_status': session_details.get('typing_status', {}),
                'started_at': session['started_at']
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get session: {str(e)}'}
    
    def end_consultation_session(self, session_id: int, expert_id: int) -> Dict:
        """End a consultation session"""
        with self._lock:
            try:
                # Get session details
                session = consultation_session_db.get_session_details(session_id)
                if not session:
                    return {'success': False, 'error': 'Session not found'}
                
                # Update session status to COMPLETED
                consultation_session_db.update_session_status(session_id, 'COMPLETED')
                
                # Update request status to COMPLETED
                expert_availability_db.complete_consultation(session['request_id'], expert_id)
                
                # Update expert status back to ONLINE_AVAILABLE
                expert_availability_db.update_expert_status(expert_id, 'ONLINE_AVAILABLE')
                
                # Get final duration
                final_duration = consultation_session_db.get_session_duration(session_id)
                
                return {
                    'success': True,
                    'message': 'Consultation session completed successfully',
                    'duration_seconds': final_duration,
                    'expert_status': 'ONLINE_AVAILABLE'
                }
                
            except Exception as e:
                return {'success': False, 'error': f'Failed to end session: {str(e)}'}
    
    def pause_consultation_session(self, session_id: int) -> Dict:
        """Pause a consultation session"""
        try:
            success = consultation_session_db.update_session_status(session_id, 'PAUSED')
            
            if success:
                return {'success': True, 'message': 'Consultation session paused'}
            else:
                return {'success': False, 'error': 'Failed to pause session'}
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to pause session: {str(e)}'}
    
    def resume_consultation_session(self, session_id: int) -> Dict:
        """Resume a paused consultation session"""
        try:
            success = consultation_session_db.update_session_status(session_id, 'ACTIVE')
            
            if success:
                return {'success': True, 'message': 'Consultation session resumed'}
            else:
                return {'success': False, 'error': 'Failed to resume session'}
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to resume session: {str(e)}'}
    
    # Message Management
    def send_message(self, session_id: int, sender_type: str, sender_id: int, 
                    message_text: str, message_type: str = 'TEXT') -> Dict:
        """Send a message in consultation session"""
        try:
            # Validate session exists and is active
            session = consultation_session_db.get_session_details(session_id)
            if not session:
                return {'success': False, 'error': 'Session not found'}
            
            if session['status'] not in ['ACTIVE', 'PAUSED']:
                return {'success': False, 'error': 'Cannot send message to inactive session'}
            
            # Add message
            message_id = consultation_session_db.add_message(
                session_id, sender_type, sender_id, message_text, message_type
            )
            
            return {
                'success': True,
                'message_id': message_id,
                'message': 'Message sent successfully',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to send message: {str(e)}'}
    
    def get_session_messages(self, session_id: int, limit: int = 50) -> Dict:
        """Get messages for a consultation session"""
        try:
            messages = consultation_session_db.get_session_messages(session_id, limit)
            
            # Mark user messages as read if expert is requesting
            if messages:
                consultation_session_db.mark_messages_read(session_id, None)
            
            return {
                'success': True,
                'messages': messages,
                'total_messages': len(messages)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get messages: {str(e)}'}
    
    # Typing Status Management
    def set_typing_status(self, session_id: int, user_typing: bool = None, expert_typing: bool = None) -> Dict:
        """Update typing status for consultation session"""
        try:
            consultation_session_db.set_typing_status(session_id, user_typing, expert_typing)
            
            return {
                'success': True,
                'message': 'Typing status updated'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to update typing status: {str(e)}'}
    
    def get_typing_status(self, session_id: int) -> Dict:
        """Get typing status for consultation session"""
        try:
            typing_status = consultation_session_db.get_typing_status(session_id)
            
            return {
                'success': True,
                'typing_status': typing_status or {}
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get typing status: {str(e)}'}
    
    # Call Management
    def start_call(self, session_id: int, started_by: str) -> Dict:
        """Start a voice call session"""
        try:
            # Validate session exists and is active
            session = consultation_session_db.get_session_details(session_id)
            if not session:
                return {'success': False, 'error': 'Session not found'}
            
            if session['status'] != 'ACTIVE':
                return {'success': False, 'error': 'Cannot start call in inactive session'}
            
            # Start call
            call_id = consultation_session_db.start_call(session_id, started_by)
            
            return {
                'success': True,
                'call_id': call_id,
                'message': 'Call started successfully',
                'call_status': 'ACTIVE'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to start call: {str(e)}'}
    
    def end_call(self, session_id: int, call_id: int) -> Dict:
        """End a voice call session"""
        try:
            success = consultation_session_db.end_call(call_id, session_id)
            
            if success:
                return {'success': True, 'message': 'Call ended successfully'}
            else:
                return {'success': False, 'error': 'Failed to end call'}
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to end call: {str(e)}'}
    
    def get_call_status(self, session_id: int) -> Dict:
        """Get current call status for consultation session"""
        try:
            session = consultation_session_db.get_session_details(session_id)
            calls = session.get('calls', [])
            
            return {
                'success': True,
                'call_status': self._get_current_call_status(calls),
                'calls': calls
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get call status: {str(e)}'}
    
    # Image Management
    def add_image(self, session_id: int, uploaded_by: str, file_path: str) -> Dict:
        """Add an image to consultation session"""
        try:
            # Validate session exists
            session = consultation_session_db.get_session_details(session_id)
            if not session:
                return {'success': False, 'error': 'Session not found'}
            
            # Add image
            image_id = consultation_session_db.add_image(session_id, uploaded_by, file_path)
            
            return {
                'success': True,
                'image_id': image_id,
                'message': 'Image added successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to add image: {str(e)}'}
    
    def get_session_images(self, session_id: int) -> Dict:
        """Get all images for a consultation session"""
        try:
            images = consultation_session_db.get_session_images(session_id)
            
            return {
                'success': True,
                'images': images,
                'total_images': len(images)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get images: {str(e)}'}
    
    # Notes Management
    def add_note(self, session_id: int, expert_id: int, note_text: str) -> Dict:
        """Add a note to consultation session"""
        try:
            # Validate session exists
            session = consultation_session_db.get_session_details(session_id)
            if not session:
                return {'success': False, 'error': 'Session not found'}
            
            # Add note
            note_id = consultation_session_db.add_note(session_id, expert_id, note_text)
            
            return {
                'success': True,
                'note_id': note_id,
                'message': 'Note added successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to add note: {str(e)}'}
    
    def update_note(self, note_id: int, expert_id: int, note_text: str) -> Dict:
        """Update an existing note"""
        try:
            success = consultation_session_db.update_note(note_id, expert_id, note_text)
            
            if success:
                return {'success': True, 'message': 'Note updated successfully'}
            else:
                return {'success': False, 'error': 'Failed to update note'}
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to update note: {str(e)}'}
    
    def get_session_notes(self, session_id: int) -> Dict:
        """Get all notes for a consultation session"""
        try:
            notes = consultation_session_db.get_session_notes(session_id)
            
            return {
                'success': True,
                'notes': notes,
                'total_notes': len(notes)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get notes: {str(e)}'}
    
    # Helper Methods
    def _format_duration(self, duration_seconds: int) -> str:
        """Format duration in human-readable format"""
        if duration_seconds < 60:
            return f"{duration_seconds} seconds"
        elif duration_seconds < 3600:
            minutes = duration_seconds // 60
            seconds = duration_seconds % 60
            return f"{minutes} minutes {seconds} seconds"
        else:
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            return f"{hours} hours {minutes} minutes"
    
    def _get_current_call_status(self, calls: List[Dict]) -> str:
        """Get current call status from calls list"""
        if not calls:
            return "NO_CALL"
        
        # Check for active call
        for call in calls:
            if call['call_status'] == 'ACTIVE':
                return "ACTIVE"
        
        # Check for most recent call
        latest_call = calls[0]
        return latest_call['call_status']

# Create service instance
consultation_session_service = ConsultationSessionService()
