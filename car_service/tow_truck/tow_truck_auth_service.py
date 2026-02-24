"""
Tow Truck Driver Authentication Service
Complete authentication and verification system for tow truck drivers
"""

import os
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from werkzeug.utils import secure_filename

from .tow_truck_profile_db import tow_truck_profile_db
from ..worker_auth.worker_db import car_worker_db

class TowTruckAuthService:
    """Complete authentication service for Tow Truck Drivers"""
    
    def __init__(self):
        self.db = tow_truck_profile_db
        self.worker_db = car_worker_db
        self.upload_folder = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "tow_truck_documents")
        os.makedirs(self.upload_folder, exist_ok=True)
    
    # ==================== DRIVER REGISTRATION ====================
    
    def register_tow_truck_driver(self, basic_info: Dict, truck_info: Dict) -> Dict:
        """Register new tow truck driver with complete verification"""
        try:
            # Check if email already exists
            existing_profile = self.db.get_tow_driver_profile(email=basic_info['email'])
            if existing_profile:
                return {"success": False, "error": "Email already registered"}
            
            # Hash password
            password_hash = bcrypt.hashpw(basic_info['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create worker entry first
            worker_data = {
                'username': basic_info['email'],
                'email': basic_info['email'],
                'password': basic_info['password'],
                'worker_type': 'TOW_TRUCK',
                'service': 'Car Service',
                'specialization': 'Tow Truck Operation',
                'experience': '0',
                'clinic_location': basic_info['city'],
                'rating': '0.0',
                'status': 'PENDING_VERIFICATION',
                'license_number': truck_info['truck_registration_number']
            }
            
            # Create worker with empty documents (will be uploaded separately)
            worker_id = self.worker_db.create_worker(worker_data, {})
            
            if not worker_id:
                return {"success": False, "error": "Failed to create worker account"}
            
            # Create tow truck profile
            profile_data = {
                'user_id': worker_id,
                'full_name': basic_info['full_name'],
                'email': basic_info['email'],
                'phone_number': basic_info['phone_number'],
                'password_hash': password_hash,
                'city': basic_info['city'],
                'service_radius_km': basic_info.get('service_radius_km', 10),
                'truck_type': truck_info['truck_type'],
                'truck_registration_number': truck_info['truck_registration_number'],
                'truck_model': truck_info['truck_model'],
                'truck_capacity': truck_info['truck_capacity'],
                'insurance_expiry_date': truck_info['insurance_expiry_date'],
                'fitness_expiry_date': truck_info['fitness_expiry_date']
            }
            
            profile_id = self.db.create_tow_driver_profile(worker_id, profile_data)
            
            if not profile_id:
                # Rollback worker creation
                self.worker_db.delete_worker(worker_id)
                return {"success": False, "error": "Failed to create tow truck profile"}
            
            return {
                "success": True,
                "message": "Tow truck driver registration successful",
                "worker_id": worker_id,
                "profile_id": profile_id,
                "status": "PENDING_VERIFICATION",
                "next_step": "Upload required documents"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Registration failed: {str(e)}"}
    
    # ==================== DOCUMENT UPLOAD ====================
    
    def upload_driver_document(self, driver_id: int, document_type: str, 
                             file, expiry_date: str = None) -> Dict:
        """Upload document for tow truck driver"""
        try:
            # Validate document type
            valid_types = [
                'AADHAAR', 'PAN', 'DRIVING_LICENSE', 'VEHICLE_RC', 
                'INSURANCE', 'FITNESS_CERTIFICATE', 'TRUCK_FRONT', 
                'TRUCK_SIDE', 'TRUCK_NUMBER_PLATE'
            ]
            
            if document_type not in valid_types:
                return {"success": False, "error": "Invalid document type"}
            
            # Generate secure filename
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            secure_filename = f"{document_type}_{driver_id}_{timestamp}_{filename}"
            
            # Save file
            file_path = os.path.join(self.upload_folder, secure_filename)
            file.save(file_path)
            
            # Store in database
            doc_id = self.db.upload_tow_driver_document(
                driver_id, document_type, file_path, expiry_date
            )
            
            if doc_id:
                return {
                    "success": True,
                    "message": f"{document_type} uploaded successfully",
                    "document_id": doc_id,
                    "file_path": file_path
                }
            else:
                # Remove file if database insert failed
                if os.path.exists(file_path):
                    os.remove(file_path)
                return {"success": False, "error": "Failed to save document"}
                
        except Exception as e:
            return {"success": False, "error": f"Upload failed: {str(e)}"}
    
    def get_driver_document_status(self, driver_id: int) -> Dict:
        """Get document upload and verification status"""
        try:
            doc_status = self.db.check_required_documents(driver_id)
            
            # Calculate overall status
            total_required = len(doc_status)
            uploaded_count = sum(1 for doc in doc_status.values() if doc['uploaded'])
            verified_count = sum(1 for doc in doc_status.values() if doc['verified'])
            
            # Check expiry alerts
            expiry_alerts = self.db.check_expiry_alerts(driver_id)
            
            return {
                "success": True,
                "document_status": doc_status,
                "summary": {
                    "total_required": total_required,
                    "uploaded": uploaded_count,
                    "verified": verified_count,
                    "pending_upload": total_required - uploaded_count,
                    "pending_verification": uploaded_count - verified_count,
                    "completion_percentage": (uploaded_count / total_required * 100) if total_required > 0 else 0,
                    "verification_percentage": (verified_count / total_required * 100) if total_required > 0 else 0
                },
                "expiry_alerts": expiry_alerts,
                "ready_for_approval": uploaded_count == total_required
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get document status: {str(e)}"}
    
    # ==================== AUTHENTICATION ====================
    
    def authenticate_driver(self, email: str, password: str) -> Dict:
        """Authenticate tow truck driver with enhanced security"""
        try:
            # Get profile
            profile = self.db.get_tow_driver_profile(email=email)
            
            if not profile:
                return {"success": False, "error": "Driver not found"}
            
            # Check approval status
            if profile['approval_status'] == 'PENDING_VERIFICATION':
                return {
                    "success": False, 
                    "error": "Account under verification",
                    "status": "PENDING_VERIFICATION",
                    "message": "Your application is being reviewed. Please wait for admin approval."
                }
            elif profile['approval_status'] == 'REJECTED':
                return {
                    "success": False, 
                    "error": "Application rejected",
                    "status": "REJECTED",
                    "message": "Your application was rejected. Please contact support."
                }
            elif profile['approval_status'] == 'SUSPENDED':
                return {
                    "success": False, 
                    "error": "Account suspended",
                    "status": "SUSPENDED",
                    "message": "Your account has been suspended. Please contact support."
                }
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), profile['password_hash'].encode('utf-8')):
                return {"success": False, "error": "Invalid credentials"}
            
            # Check for expiry alerts
            expiry_alerts = self.db.check_expiry_alerts(profile['id'])
            
            # Update last login
            self.db.update_tow_driver_profile(profile['id'], {'last_login': datetime.now().isoformat()})
            
            # Get worker info for token generation
            worker = self.worker_db.get_worker_by_username(email)
            
            return {
                "success": True,
                "message": "Authentication successful",
                "driver": {
                    "id": profile['id'],
                    "user_id": profile['user_id'],
                    "full_name": profile['full_name'],
                    "email": profile['email'],
                    "phone_number": profile['phone_number'],
                    "city": profile['city'],
                    "truck_type": profile['truck_type'],
                    "truck_capacity": profile['truck_capacity'],
                    "service_radius_km": profile['service_radius_km'],
                    "approval_status": profile['approval_status']
                },
                "worker": {
                    "id": worker['id'],
                    "username": worker['username'],
                    "worker_type": worker['worker_type'],
                    "status": worker['status']
                },
                "expiry_alerts": expiry_alerts
            }
            
        except Exception as e:
            return {"success": False, "error": f"Authentication failed: {str(e)}"}
    
    # ==================== ADMIN VERIFICATION ====================
    
    def get_pending_applications(self) -> Dict:
        """Get all pending tow truck driver applications"""
        try:
            applications = self.db.get_pending_applications()
            
            # Enhance with document status
            enhanced_apps = []
            for app in applications:
                doc_status = self.db.check_required_documents(app['id'])
                
                enhanced_app = {
                    **app,
                    "document_status": doc_status,
                    "documents_uploaded": sum(1 for doc in doc_status.values() if doc['uploaded']),
                    "documents_verified": sum(1 for doc in doc_status.values() if doc['verified']),
                    "ready_for_review": all(doc['uploaded'] for doc in doc_status.values())
                }
                enhanced_apps.append(enhanced_app)
            
            return {
                "success": True,
                "applications": enhanced_apps,
                "total_pending": len(enhanced_apps)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get applications: {str(e)}"}
    
    def approve_driver_application(self, driver_id: int, admin_notes: str = None) -> Dict:
        """Approve tow truck driver application"""
        try:
            # Check document verification status
            doc_status = self.db.check_required_documents(driver_id)
            
            # Verify all required documents are uploaded and verified
            for doc_type, status in doc_status.items():
                if not status['uploaded']:
                    return {
                        "success": False,
                        "error": f"Missing required document: {doc_type}"
                    }
                if not status['verified']:
                    return {
                        "success": False,
                        "error": f"Document not verified: {doc_type}"
                    }
            
            # Update approval status
            success = self.db.update_approval_status(driver_id, 'APPROVED', admin_notes)
            
            if success:
                # Update worker status
                profile = self.db.get_tow_driver_profile(driver_id)
                if profile:
                    self.worker_db.update_worker_status(profile['user_id'], 'APPROVED')
                
                return {
                    "success": True,
                    "message": "Driver application approved successfully",
                    "driver_id": driver_id
                }
            else:
                return {"success": False, "error": "Failed to approve application"}
                
        except Exception as e:
            return {"success": False, "error": f"Approval failed: {str(e)}"}
    
    def reject_driver_application(self, driver_id: int, admin_notes: str = None) -> Dict:
        """Reject tow truck driver application"""
        try:
            # Update approval status
            success = self.db.update_approval_status(driver_id, 'REJECTED', admin_notes)
            
            if success:
                # Update worker status
                profile = self.db.get_tow_driver_profile(driver_id)
                if profile:
                    self.worker_db.update_worker_status(profile['user_id'], 'REJECTED')
                
                return {
                    "success": True,
                    "message": "Driver application rejected",
                    "driver_id": driver_id
                }
            else:
                return {"success": False, "error": "Failed to reject application"}
                
        except Exception as e:
            return {"success": False, "error": f"Rejection failed: {str(e)}"}
    
    def verify_driver_document(self, document_id: int, status: str, admin_remark: str = None) -> Dict:
        """Verify individual driver document"""
        try:
            success = self.db.verify_document(document_id, status, admin_remark)
            
            if success:
                return {
                    "success": True,
                    "message": f"Document {status.lower()} successfully",
                    "document_id": document_id
                }
            else:
                return {"success": False, "error": "Failed to verify document"}
                
        except Exception as e:
            return {"success": False, "error": f"Verification failed: {str(e)}"}
    
    # ==================== FRAUD PROTECTION ====================
    
    def log_fraud_incident(self, driver_id: int, incident_type: str, incident_data: Dict) -> Dict:
        """Log fraud incident for driver"""
        try:
            success = self.db.log_fraud_incident(driver_id, incident_type, incident_data)
            
            if success:
                # Check if driver should be suspended based on fraud risk
                fraud_risk = self.db.check_fraud_risk(driver_id)
                
                if fraud_risk['risk_level'] == 'HIGH':
                    self.db.update_approval_status(driver_id, 'SUSPENDED', 'Auto-suspended due to high fraud risk')
                
                return {
                    "success": True,
                    "message": "Fraud incident logged successfully",
                    "fraud_risk": fraud_risk
                }
            else:
                return {"success": False, "error": "Failed to log incident"}
                
        except Exception as e:
            return {"success": False, "error": f"Failed to log incident: {str(e)}"}
    
    def check_driver_fraud_risk(self, driver_id: int) -> Dict:
        """Check fraud risk for driver"""
        try:
            return self.db.check_fraud_risk(driver_id)
        except Exception as e:
            return {"success": False, "error": f"Failed to check fraud risk: {str(e)}"}
    
    # ==================== VEHICLE COMPATIBILITY ====================
    
    def check_vehicle_compatibility(self, driver_id: int, vehicle_type: str) -> Dict:
        """Check if driver's truck is compatible with vehicle type"""
        try:
            is_compatible = self.db.check_vehicle_compatibility(driver_id, vehicle_type)
            
            return {
                "success": True,
                "compatible": is_compatible,
                "driver_id": driver_id,
                "vehicle_type": vehicle_type,
                "message": "Compatible" if is_compatible else "Not compatible with your truck type"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to check compatibility: {str(e)}"}
    
    # ==================== EXPIRY MONITORING ====================
    
    def run_expiry_monitoring(self) -> Dict:
        """Run automated expiry monitoring"""
        try:
            # Suspend drivers with expired documents
            suspended_drivers = self.db.suspend_expired_documents()
            
            return {
                "success": True,
                "message": "Expiry monitoring completed",
                "suspended_drivers": suspended_drivers,
                "suspended_count": len(suspended_drivers)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Expiry monitoring failed: {str(e)}"}
    
    def get_driver_expiry_alerts(self, driver_id: int) -> Dict:
        """Get expiry alerts for driver"""
        try:
            alerts = self.db.check_expiry_alerts(driver_id)
            
            return {
                "success": True,
                "alerts": alerts,
                "alert_count": len(alerts),
                "has_critical_alerts": any(alert['alert_level'] == 'CRITICAL' for alert in alerts)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get expiry alerts: {str(e)}"}
    
    # ==================== DRIVER MANAGEMENT ====================
    
    def get_driver_statistics(self) -> Dict:
        """Get tow truck driver statistics"""
        try:
            return self.db.get_driver_statistics()
        except Exception as e:
            return {"success": False, "error": f"Failed to get statistics: {str(e)}"}
    
    def get_approved_drivers(self) -> Dict:
        """Get all approved tow truck drivers"""
        try:
            drivers = self.db.get_approved_drivers()
            
            # Enhance with additional info
            enhanced_drivers = []
            for driver in drivers:
                doc_status = self.db.check_required_documents(driver['id'])
                fraud_risk = self.db.check_fraud_risk(driver['id'])
                expiry_alerts = self.db.check_expiry_alerts(driver['id'])
                
                enhanced_driver = {
                    **driver,
                    "document_compliance": all(doc['verified'] for doc in doc_status.values()),
                    "fraud_risk_level": fraud_risk['risk_level'],
                    "has_expiry_alerts": len(expiry_alerts) > 0,
                    "last_login": driver.get('last_login')
                }
                enhanced_drivers.append(enhanced_driver)
            
            return {
                "success": True,
                "drivers": enhanced_drivers,
                "total_count": len(enhanced_drivers)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get drivers: {str(e)}"}

# Initialize service instance
tow_truck_auth_service = TowTruckAuthService()
