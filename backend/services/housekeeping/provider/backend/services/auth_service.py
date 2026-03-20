import bcrypt
from worker_db import WorkerDB
import auth_utils 
from services.housekeeping.models.database import housekeeping_db

class ProviderAuthService:
    def __init__(self):
        self.worker_db = WorkerDB()
        self.hk_db = housekeeping_db

    def register_provider(self, data):
        # 1. Check if worker exists
        if self.worker_db.get_worker_by_email(data['email']):
            return {"error": "Email already registered"}, 400
            
        # 2. Register worker (Pending Admin Approval)
        try:
            # register_worker(self, full_name, email, phone, service, specialization, experience, clinic_location="", license_number=None, password=None)
            worker_id = self.worker_db.register_worker(
                full_name=data['name'], 
                email=data['email'], 
                phone=data.get('phone', ''),
                service=data['service_type'], 
                specialization=data.get('specialization', 'General'),
                experience=data.get('experience', 0),
                clinic_location=data.get('location', ''),
                password=data['password']
            )
            
            if worker_id:
                # Add to housekeeping specific status if needed
                # Ensure hk_db has this method, if not, skip or implement
                try:
                    self.hk_db.set_worker_online(worker_id, False)
                except AttributeError:
                    pass # Method might not exist yet
                
                return {"message": "Registration successful. Pending admin approval.", "worker_id": worker_id}, 201
            else:
                return {"error": "Registration failed"}, 500
        except Exception as e:
            print(f"Error registering provider: {e}")
            return {"error": str(e)}, 500

    def login_provider(self, email, password):
        # 1. Verify credentials
        worker = self.worker_db.get_worker_by_email(email)
        if not worker:
            return {"error": "Invalid credentials"}, 401
            
        # Verify password
        stored_pw = worker.get('password')
        if not stored_pw:
            return {"error": "Invalid credentials (no password set)"}, 401

        # Handle stored password type (bytes vs string)
        if isinstance(stored_pw, str):
            stored_pw = stored_pw.encode('utf-8')
            
        if not bcrypt.checkpw(password.encode('utf-8'), stored_pw):
            return {"error": "Invalid credentials"}, 401
            
        # 2. Check approval status
        status = worker.get('status', '').lower()
        if status != 'approved':
            return {"error": f"Account status: {status}. Pending approval."}, 403
            
        # 3. Generate Token
        token = auth_utils.generate_token(email)
        return {
            "token": token, 
            "worker": {
                "id": worker['id'], 
                "name": worker['name'],
                "service": worker['service'],
                "specialization": worker.get('specialization')
            }
        }, 200

    def verify_provider_token(self, token):
        try:
            email = auth_utils.verify_token(token)
            if not email:
                return {"error": "Invalid token"}, 401
            
            worker = self.worker_db.get_worker_by_email(email)
            if not worker:
                return {"error": "Worker not found"}, 404
                
            return {
                "id": worker['id'], 
                "name": worker['name'],
                "email": worker['email'],
                "service": worker['service'],
                "specialization": worker.get('specialization'),
                "status": worker.get('status', 'pending')
            }, 200
        except Exception as e:
            return {"error": str(e)}, 500
