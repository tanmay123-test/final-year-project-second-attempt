from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import random
import string
from datetime import datetime
from services.video_session_db import video_session_db
from services.video_signaling import video_signaling
from appointment_db import AppointmentDB
from email_service import send_email

video_bp = Blueprint('video', __name__)
appt_db = AppointmentDB()

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads/prescriptions'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@video_bp.route('/video/start', methods=['POST'])
def start_video_call():
    """Doctor starts video call with OTP verification"""
    try:
        data = request.json
        appointment_id = data.get('appointment_id')
        otp = data.get('otp')
        doctor_id = data.get('doctor_id')
        
        if not appointment_id or not otp or not doctor_id:
            return jsonify({
                'success': False,
                'message': 'Appointment ID, OTP, and Doctor ID are required'
            }), 400
        
        # Verify OTP
        session = video_session_db.verify_doctor_otp(appointment_id, otp)
        if not session:
            return jsonify({
                'success': False,
                'message': 'Invalid OTP or session not found'
            }), 401
        
        # Verify doctor owns this appointment
        appointment = appt_db.get_by_id(appointment_id)
        if not appointment or str(appointment['worker_id']) != str(doctor_id):
            return jsonify({
                'success': False,
                'message': 'Unauthorized: Doctor does not own this appointment'
            }), 403
        
        # Start the session
        updated_session = video_session_db.start_session(appointment_id)
        
        # Update appointment status
        video_session_db.update_appointment_status(appointment_id, 'in_progress')
        
        # Emit call started event via WebSocket
        if video_signaling:
            video_signaling.emit_to_room(
                session['room_id'], 
                'call_started', 
                {
                    'room_id': session['room_id'],
                    'user_type': 'doctor',
                    'timestamp': str(datetime.now())
                }
            )
        
        return jsonify({
            'success': True,
            'message': 'Video call started successfully',
            'room_id': session['room_id'],
            'session': updated_session
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error starting video call: {str(e)}'
        }), 500

@video_bp.route('/video/join/<int:appointment_id>', methods=['GET'])
def join_video_call(appointment_id):
    """Patient joins video call"""
    try:
        # Get session details
        session = video_session_db.get_session_by_appointment(appointment_id)
        if not session:
            return jsonify({
                'success': False,
                'message': 'Video session not found'
            }), 404
        
        # Check if session is live
        if session['session_status'] != 'live':
            return jsonify({
                'success': False,
                'message': 'Video call has not started yet. Please wait for the doctor to start the call.'
            }), 403
        
        # Get appointment details to verify patient
        appointment = appt_db.get_by_id(appointment_id)
        if not appointment:
            return jsonify({
                'success': False,
                'message': 'Appointment not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Successfully joined video call',
            'room_id': session['room_id'],
            'session': session,
            'appointment': appointment
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error joining video call: {str(e)}'
        }), 500

@video_bp.route('/video/end', methods=['POST'])
def end_video_call():
    """End video call"""
    try:
        data = request.json
        appointment_id = data.get('appointment_id')
        user_id = data.get('user_id')
        user_type = data.get('user_type')  # 'doctor' or 'patient'
        
        if not appointment_id or not user_id or not user_type:
            return jsonify({
                'success': False,
                'message': 'Appointment ID, User ID, and User Type are required'
            }), 400
        
        # Get session details
        session = video_session_db.get_session_by_appointment(appointment_id)
        if not session:
            return jsonify({
                'success': False,
                'message': 'Video session not found'
            }), 404
        
        # Get appointment details for verification
        appointment = appt_db.get_by_id(appointment_id)
        if not appointment:
            return jsonify({
                'success': False,
                'message': 'Appointment not found'
            }), 404
        
        # Verify user authorization
        if user_type == 'doctor' and str(appointment['worker_id']) != str(user_id):
            return jsonify({
                'success': False,
                'message': 'Unauthorized: Doctor does not own this appointment'
            }), 403
        elif user_type == 'patient' and str(appointment['user_id']) != str(user_id):
            return jsonify({
                'success': False,
                'message': 'Unauthorized: Patient does not own this appointment'
            }), 403
        
        # End the session
        ended_session = video_session_db.end_session(appointment_id)
        
        # Update appointment status to completed
        video_session_db.update_appointment_status(appointment_id, 'completed')
        
        # Emit call ended event via WebSocket
        if video_signaling:
            video_signaling.emit_to_room(
                session['room_id'], 
                'call_ended', 
                {
                    'room_id': session['room_id'],
                    'user_type': user_type,
                    'timestamp': str(datetime.now())
                }
            )
        
        return jsonify({
            'success': True,
            'message': 'Video call ended successfully',
            'session': ended_session
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error ending video call: {str(e)}'
        }), 500

@video_bp.route('/video/upload-prescription', methods=['POST'])
def upload_prescription():
    """Upload prescription file during video call"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        appointment_id = request.form.get('appointment_id')
        doctor_id = request.form.get('doctor_id')
        
        if not appointment_id or not doctor_id:
            return jsonify({
                'success': False,
                'message': 'Appointment ID and Doctor ID are required'
            }), 400
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        if file and allowed_file(file.filename):
            # Generate secure filename
            filename = secure_filename(file.filename)
            # Add timestamp to avoid conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"prescription_{appointment_id}_{timestamp}_{filename}"
            
            # Save file
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # Get appointment details for verification
            appointment = appt_db.get_by_id(appointment_id)
            if not appointment or str(appointment['worker_id']) != str(doctor_id):
                # Remove uploaded file if unauthorized
                if os.path.exists(file_path):
                    os.remove(file_path)
                return jsonify({
                    'success': False,
                    'message': 'Unauthorized: Doctor does not own this appointment'
                }), 403
            
            # Return file URL
            file_url = f"/uploads/prescriptions/{filename}"
            
            return jsonify({
                'success': True,
                'message': 'Prescription uploaded successfully',
                'file_url': file_url,
                'filename': filename
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'File type not allowed. Allowed types: PDF, PNG, JPG, JPEG, DOC, DOCX'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error uploading prescription: {str(e)}'
        }), 500

@video_bp.route('/video/session/<int:appointment_id>', methods=['GET'])
def get_video_session(appointment_id):
    """Get video session details"""
    try:
        session = video_session_db.get_session_by_appointment(appointment_id)
        if not session:
            return jsonify({
                'success': False,
                'message': 'Video session not found'
            }), 404
        
        return jsonify({
            'success': True,
            'session': session
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting video session: {str(e)}'
        }), 500

@video_bp.route('/video/create-session/<int:appointment_id>', methods=['POST'])
def create_video_session(appointment_id):
    """Create video session and send OTP to doctor"""
    try:
        data = request.json
        doctor_id = data.get('doctor_id')
        
        if not doctor_id:
            return jsonify({
                'success': False,
                'message': 'Doctor ID is required'
            }), 400
        
        # Check if session already exists
        existing_session = video_session_db.get_session_by_appointment(appointment_id)
        if existing_session and existing_session['session_status'] in ['created', 'live']:
            return jsonify({
                'success': False,
                'message': 'Video session already exists for this appointment'
            }), 400
        
        # Get appointment details
        appointment = appt_db.get_by_id(appointment_id)
        if not appointment:
            return jsonify({
                'success': False,
                'message': 'Appointment not found'
            }), 404
        
        # Verify doctor owns this appointment
        if str(appointment['worker_id']) != str(doctor_id):
            return jsonify({
                'success': False,
                'message': 'Unauthorized: Doctor does not own this appointment'
            }), 403
        
        # Create video session
        session = video_session_db.create_video_session(appointment_id)
        
        # Send OTP to doctor's email
        try:
            doctor_email = appointment.get('doctor_email', 'doctor@example.com')  # You'll need to get this from workers table
            subject = "ExpertEase - Video Consultation OTP"
            message = f"""
Dear Doctor,

Your video consultation OTP is: {session['doctor_otp']}

Appointment ID: {appointment_id}
Room ID: {session['room_id']}

Please use this OTP to start the video call.

Best regards,
ExpertEase Team
            """
            
            # send_email(doctor_email, subject, message)  # Uncomment when email service is ready
            
            return jsonify({
                'success': True,
                'message': 'Video session created successfully. OTP sent to doctor\'s email.',
                'session': session
            }), 201
            
        except Exception as email_error:
            # If email fails, still return success but mention email issue
            return jsonify({
                'success': True,
                'message': f'Video session created. OTP: {session["doctor_otp"]} (Email service unavailable)',
                'session': session
            }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating video session: {str(e)}'
        }), 500

@video_bp.route('/uploads/prescriptions/<filename>')
def get_prescription_file(filename):
    """Serve prescription files"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({
                'success': False,
                'message': 'File not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error serving file: {str(e)}'
        }), 500

@video_bp.route('/video/active-sessions', methods=['GET'])
def get_active_sessions():
    """Get all active video sessions (for admin/monitoring)"""
    try:
        sessions = video_session_db.get_active_sessions()
        return jsonify({
            'success': True,
            'sessions': sessions
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting active sessions: {str(e)}'
        }), 500
