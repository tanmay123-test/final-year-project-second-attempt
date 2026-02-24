"""
Automobile Expert Service
Business logic for expert authentication, requests, and consultations
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from werkzeug.utils import secure_filename
import bcrypt

from .expert_db import expert_db

class ExpertService:
    """Service for Automobile Expert operations"""
    
    def __init__(self):
        self.db = expert_db
        self.upload_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            "uploads", "expert_documents"
        )
        os.makedirs(self.upload_dir, exist_ok=True)
    
    # ==================== AUTHENTICATION ====================
    
    def register_expert(self, user_data: Dict, profile_data: Dict) -> Dict:
        """Register new automobile expert"""
        try:
            # Check if email already exists in workers table
            from ..worker_auth.worker_db import car_worker_db
            existing_worker = car_worker_db.get_worker_by_email(user_data['email'])
            if existing_worker:
                return {"success": False, "error": "Email already registered"}
            
            # Hash password
            password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create worker entry first
            worker_data_for_db = {
                'username': user_data.get('username', user_data['email']),
                'email': user_data['email'],
                'password': user_data['password'],
                'phone': user_data.get('phone_number', user_data.get('phone', '')),
                'worker_type': 'EXPERT',
                'service': 'Car Service',
                'specialization': 'Automobile Expert',
                'experience': profile_data.get('years_of_experience', '0'),
                'clinic_location': user_data.get('city', ''),
                'rating': '0.0',
                'status': 'PENDING_VERIFICATION',
                'license_number': f"EXP-{uuid.uuid4().hex[:8].upper()}"
            }
            
            worker_id = car_worker_db.create_worker(worker_data_for_db, {})
            
            if not worker_id:
                return {"success": False, "error": "Failed to create worker account"}
            
            # Create expert profile
            profile_data_for_db = {
                'primary_expertise': profile_data['primary_expertise'],
                'years_of_experience': profile_data.get('years_of_experience', 0),
                'work_type': profile_data.get('work_type', ''),
                'consultation_hours': profile_data.get('consultation_hours', ''),
                'languages': profile_data.get('languages', '')
            }
            
            profile_id = self.db.create_expert_profile(worker_id, profile_data_for_db)
            
            if not profile_id:
                # Rollback worker creation
                car_worker_db.delete_worker(worker_id)
                return {"success": False, "error": "Failed to create expert profile"}
            
            return {
                "success": True,
                "message": "Expert application submitted successfully. Waiting for admin approval.",
                "profile_id": profile_id,
                "worker_id": worker_id
            }
            
        except Exception as e:
            return {"success": False, "error": f"Registration failed: {str(e)}"}
    
    def authenticate_expert(self, email: str, password: str) -> Dict:
        """Authenticate expert with approval check"""
        try:
            from ..worker_auth.worker_db import car_worker_db
            
            # Get worker and expert profile
            worker = car_worker_db.get_worker_by_email(email)
            if not worker:
                return {"success": False, "error": "Invalid credentials"}
            
            # Verify password
            if not car_worker_db.verify_password(password, worker['password_hash']):
                return {"success": False, "error": "Invalid credentials"}
            
            # Check if worker type is EXPERT
            if worker['worker_type'] != 'EXPERT':
                return {"success": False, "error": "Invalid worker type"}
            
            # Get expert profile
            expert_profile = self.db.get_expert_profile(worker['id'])
            if not expert_profile:
                return {"success": False, "error": "Expert profile not found"}
            
            # Check approval status
            if expert_profile['approval_status'] != 'APPROVED':
                return {
                    "success": False, 
                    "error": "Application under review",
                    "approval_status": expert_profile['approval_status']
                }
            
            return {
                "success": True,
                "message": "Login successful",
                "expert": expert_profile,
                "worker": worker
            }
            
        except Exception as e:
            return {"success": False, "error": f"Authentication failed: {str(e)}"}
    
    # ==================== DOCUMENT UPLOAD ====================
    
    def upload_expert_document(self, expert_id: int, document_type: str, file) -> Dict:
        """Upload expert document with validation"""
        try:
            # Validate file
            if not file or file.filename == '':
                return {"success": False, "error": "No file selected"}
            
            # Validate file type
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx']
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                return {"success": False, "error": f"File type {file_ext} not allowed"}
            
            # Validate file size (5MB max)
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()  # Get size
            file.seek(0)  # Reset to beginning
            
            if file_size > 5 * 1024 * 1024:
                return {"success": False, "error": "File too large. Max 5MB allowed"}
            
            # Generate secure filename
            filename = secure_filename(file.filename)
            unique_filename = f"{document_type}_{expert_id}_{uuid.uuid4().hex[:8]}{file_ext}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Save file
            file.save(file_path)
            
            # Upload to database
            doc_id = self.db.upload_expert_document(expert_id, document_type, unique_filename)
            
            if doc_id:
                return {
                    "success": True,
                    "message": "Document uploaded successfully",
                    "document_id": doc_id,
                    "file_path": unique_filename
                }
            else:
                return {"success": False, "error": "Failed to save document"}
                
        except Exception as e:
            return {"success": False, "error": f"Upload failed: {str(e)}"}
    
    def get_expert_document_status(self, expert_id: int) -> Dict:
        """Get expert document upload and verification status"""
        try:
            documents = self.db.get_expert_documents(expert_id)
            
            # Check if all required documents are uploaded
            required_docs = ['government_id', 'technical_proof']
            uploaded_docs = [doc['document_type'] for doc in documents]
            
            missing_docs = [doc for doc in required_docs if doc not in uploaded_docs]
            pending_docs = [doc['document_type'] for doc in documents if doc['verification_status'] == 'PENDING']
            
            return {
                "success": True,
                "documents": documents,
                "missing_documents": missing_docs,
                "pending_documents": pending_docs,
                "upload_complete": len(missing_docs) == 0,
                "verification_complete": len(pending_docs) == 0
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get document status: {str(e)}"}
    
    # ==================== REQUEST HANDLING ====================
    
    def create_expert_request(self, user_id: int, request_data: Dict) -> Dict:
        """Create new expert request"""
        try:
            request_id = self.db.create_expert_request(user_id, request_data)
            
            if request_id:
                return {
                    "success": True,
                    "message": "Request created successfully",
                    "request_id": request_id
                }
            else:
                return {"success": False, "error": "Failed to create request"}
                
        except Exception as e:
            return {"success": False, "error": f"Request creation failed: {str(e)}"}
    
    def get_available_experts(self, category: str = None) -> List[Dict]:
        """Get available experts for assignment"""
        try:
            from ..worker_auth.worker_db import car_worker_db
            
            # Get all approved experts
            conn = self.db.get_conn()
            cur = conn.cursor()
            
            query = """
                SELECT ep.*, w.username, w.email
                FROM expert_profiles ep
                JOIN workers w ON ep.user_id = w.id
                WHERE ep.approval_status = 'APPROVED'
            """
            params = []
            
            if category:
                query += " AND ep.primary_expertise = ?"
                params.append(category)
            
            query += " ORDER BY ep.trust_score DESC, ep.rating DESC"
            
            cur.execute(query, params)
            results = [dict(row) for row in cur.fetchall()]
            conn.close()
            
            return results
            
        except Exception as e:
            print(f"Error getting available experts: {e}")
            return []
    
    def assign_expert_to_request(self, request_id: int, category: str = None) -> Dict:
        """Assign best available expert to request"""
        try:
            # Get available experts for category
            experts = self.get_available_experts(category)
            
            if not experts:
                return {"success": False, "error": "No available experts"}
            
            # Select best expert (highest trust score, then rating)
            best_expert = experts[0]
            
            # Assign expert to request
            success = self.db.assign_expert_to_request(request_id, best_expert['id'])
            
            if success:
                return {
                    "success": True,
                    "message": "Expert assigned successfully",
                    "expert": best_expert
                }
            else:
                return {"success": False, "error": "Failed to assign expert"}
                
        except Exception as e:
            return {"success": False, "error": f"Assignment failed: {str(e)}"}
    
    # ==================== CONVERSATION MANAGEMENT ====================
    
    def send_message(self, request_id: int, expert_id: int, user_id: int, 
                   message: str, sender_type: str, file_path: str = None) -> Dict:
        """Send message in conversation"""
        try:
            message_id = self.db.create_conversation_message(
                request_id, expert_id, user_id, message, sender_type, 'text', file_path
            )
            
            if message_id:
                return {
                    "success": True,
                    "message": "Message sent successfully",
                    "message_id": message_id
                }
            else:
                return {"success": False, "error": "Failed to send message"}
                
        except Exception as e:
            return {"success": False, "error": f"Message sending failed: {str(e)}"}
    
    def get_conversation(self, request_id: int) -> Dict:
        """Get full conversation"""
        try:
            messages = self.db.get_conversation_messages(request_id)
            
            return {
                "success": True,
                "messages": messages,
                "total_messages": len(messages)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get conversation: {str(e)}"}
    
    def resolve_request(self, request_id: int, expert_id: int) -> Dict:
        """Resolve expert request and update stats"""
        try:
            # Update request status
            success = self.db.update_request_status(request_id, 'RESOLVED')
            
            if success:
                # Update expert stats
                conn = self.db.get_conn()
                cur = conn.cursor()
                
                cur.execute("""
                    UPDATE expert_profiles 
                    SET total_cases_handled = total_cases_handled + 1,
                        trust_score = CASE 
                            WHEN trust_score + 5.0 > 100.0 THEN 100.0
                            ELSE trust_score + 5.0
                        END
                    WHERE id = ?
                """, (expert_id,))
                
                conn.commit()
                conn.close()
                
                return {
                    "success": True,
                    "message": "Request resolved successfully"
                }
            else:
                return {"success": False, "error": "Failed to resolve request"}
                
        except Exception as e:
            return {"success": False, "error": f"Resolution failed: {str(e)}"}
    
    # ==================== ADMIN OPERATIONS ====================
    
    def get_pending_applications(self) -> Dict:
        """Get pending expert applications for admin"""
        try:
            applications = self.db.get_pending_expert_applications()
            
            return {
                "success": True,
                "applications": applications,
                "total_pending": len(applications)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get applications: {str(e)}"}
    
    def approve_expert_application(self, profile_id: int, admin_notes: str = '') -> Dict:
        """Approve expert application"""
        try:
            success = self.db.update_expert_approval(profile_id, 'APPROVED', admin_notes)
            
            if success:
                return {
                    "success": True,
                    "message": "Expert application approved successfully"
                }
            else:
                return {"success": False, "error": "Failed to approve application"}
                
        except Exception as e:
            return {"success": False, "error": f"Approval failed: {str(e)}"}
    
    def reject_expert_application(self, profile_id: int, admin_notes: str = '') -> Dict:
        """Reject expert application"""
        try:
            success = self.db.update_expert_approval(profile_id, 'REJECTED', admin_notes)
            
            if success:
                return {
                    "success": True,
                    "message": "Expert application rejected successfully"
                }
            else:
                return {"success": False, "error": "Failed to reject application"}
                
        except Exception as e:
            return {"success": False, "error": f"Rejection failed: {str(e)}"}
    
    def verify_expert_document(self, document_id: int, status: str, remark: str = '') -> Dict:
        """Verify expert document"""
        try:
            success = self.db.verify_expert_document(document_id, status, remark)
            
            if success:
                return {
                    "success": True,
                    "message": f"Document {status.lower()} successfully"
                }
            else:
                return {"success": False, "error": "Failed to verify document"}
                
        except Exception as e:
            return {"success": False, "error": f"Verification failed: {str(e)}"}
    
    def get_expert_statistics(self) -> Dict:
        """Get expert system statistics"""
        try:
            stats = self.db.get_expert_statistics()
            
            return {
                "success": True,
                "statistics": stats
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get statistics: {str(e)}"}


# Global instance
expert_service = ExpertService()
