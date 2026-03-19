"""
Authentication Service using Organized Database Manager
Handles user and worker authentication for all services
"""

from database.database_manager import db_manager
from auth_utils import generate_token, verify_token
from datetime import datetime, timedelta
import json

class AuthService:
    """Centralized authentication service"""
    
    def __init__(self):
        self.db_manager = db_manager
    
    # User Authentication
    def register_user(self, email, password, name, phone=None):
        """Register new user"""
        try:
            # Check if user already exists
            existing_user = self.db_manager.get_user(email=email)
            if existing_user:
                return {"success": False, "message": "User already exists"}
            
            # Create new user
            user_id = self.db_manager.create_user(email, password, name, phone)
            
            # Generate token
            token = generate_token(str(user_id))
            
            return {
                "success": True,
                "message": "User registered successfully",
                "user_id": user_id,
                "token": token,
                "user": self.db_manager.get_user(user_id)
            }
            
        except Exception as e:
            return {"success": False, "message": f"Registration failed: {str(e)}"}
    
    def login_user(self, email_or_username, password):
        """Login user with email or username"""
        try:
            # Check if input looks like email
            if '@' in email_or_username:
                user = self.db_manager.authenticate_user(email_or_username, password)
            else:
                # Try to find user by name (username)
                user = self.get_user_by_name(email_or_username)
                if user:
                    # Authenticate with the found user's email
                    user = self.db_manager.authenticate_user(user['email'], password)
                else:
                    user = None
                    
            if user:
                token = generate_token(str(user['id']))
                return {
                    "success": True,
                    "message": "Login successful",
                    "user": user,
                    "token": token
                }
            else:
                return {"success": False, "message": "Invalid credentials"}
                
        except Exception as e:
            return {"success": False, "message": f"Login failed: {str(e)}"}
    
    def get_user_by_name(self, name):
        """Get user by name (for username support)"""
        try:
            with self.db_manager.get_connection('users') as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute('SELECT * FROM users WHERE name = ?', (name,))
                user = cursor.fetchone()
                return user if user else None
        except Exception:
            return None
    
    def get_user_profile(self, user_id):
        """Get user profile"""
        try:
            user = self.db_manager.get_user(user_id=user_id)
            if user:
                return {"success": True, "user": user}
            else:
                return {"success": False, "message": "User not found"}
                
        except Exception as e:
            return {"success": False, "message": f"Failed to get user: {str(e)}"}
    
    def update_user_profile(self, user_id, **kwargs):
        """Update user profile"""
        try:
            success = self.db_manager.update_user(user_id, **kwargs)
            if success:
                return {"success": True, "message": "Profile updated successfully"}
            else:
                return {"success": False, "message": "Failed to update profile"}
                
        except Exception as e:
            return {"success": False, "message": f"Update failed: {str(e)}"}
    
    # Worker Authentication
    def register_worker(self, email, password, name, phone, service_type, worker_type):
        """Register new worker"""
        try:
            # Check if worker already exists
            existing_workers = self.db_manager.get_worker(email=email)
            if existing_workers:
                return {"success": False, "message": "Worker already exists"}
            
            # Create new worker
            worker_id = self.db_manager.create_worker(email, password, name, phone, service_type, worker_type)
            
            # Generate token
            token = generate_token(worker_id, "worker")
            
            return {
                "success": True,
                "message": "Worker registered successfully",
                "worker_id": worker_id,
                "token": token,
                "worker": self.db_manager.get_worker(worker_id=worker_id)
            }
            
        except Exception as e:
            return {"success": False, "message": f"Registration failed: {str(e)}"}
    
    def login_worker(self, email, password):
        """Login worker"""
        try:
            worker = self.db_manager.authenticate_worker(email, password)
            if worker:
                token = generate_token(worker['id'], "worker")
                return {
                    "success": True,
                    "message": "Login successful",
                    "worker": worker,
                    "token": token
                }
            else:
                return {"success": False, "message": "Invalid credentials"}
                
        except Exception as e:
            return {"success": False, "message": f"Login failed: {str(e)}"}
    
    def get_worker_profile(self, worker_id):
        """Get worker profile"""
        try:
            workers = self.db_manager.get_worker(worker_id=worker_id)
            if workers:
                return {"success": True, "worker": workers[0]}
            else:
                return {"success": False, "message": "Worker not found"}
                
        except Exception as e:
            return {"success": False, "message": f"Failed to get worker: {str(e)}"}
    
    def get_workers_by_service(self, service_type):
        """Get all workers for a specific service"""
        try:
            workers = self.db_manager.get_workers_by_service(service_type)
            return {"success": True, "workers": workers}
                
        except Exception as e:
            return {"success": False, "message": f"Failed to get workers: {str(e)}"}
    
    # Service-Specific Worker Methods
    def get_healthcare_workers(self, worker_type=None):
        """Get healthcare workers"""
        try:
            if worker_type:
                workers = self.db_manager.get_worker(service_type="healthcare", worker_type=worker_type)
            else:
                workers = self.db_manager.get_workers_by_service("healthcare")
            return {"success": True, "workers": workers}
                
        except Exception as e:
            return {"success": False, "message": f"Failed to get healthcare workers: {str(e)}"}
    
    def get_car_service_workers(self, worker_type=None):
        """Get car service workers"""
        try:
            if worker_type == "mechanic":
                workers = self.db_manager.get_mechanics()
            elif worker_type == "fuel_delivery":
                workers = self.db_manager.get_fuel_delivery_agents()
            elif worker_type == "tow_truck":
                workers = self.db_manager.get_tow_truck_operators()
            else:
                workers = self.db_manager.get_workers_by_service("car_service")
            return {"success": True, "workers": workers}
                
        except Exception as e:
            return {"success": False, "message": f"Failed to get car service workers: {str(e)}"}
    
    def get_housekeeping_workers(self):
        """Get housekeeping workers"""
        try:
            workers = self.db_manager.get_workers_by_service("housekeeping")
            return {"success": True, "workers": workers}
                
        except Exception as e:
            return {"success": False, "message": f"Failed to get housekeeping workers: {str(e)}"}
    
    def get_freelance_workers(self):
        """Get freelance workers"""
        try:
            workers = self.db_manager.get_workers_by_service("freelance")
            return {"success": True, "workers": workers}
                
        except Exception as e:
            return {"success": False, "message": f"Failed to get freelance workers: {str(e)}"}
    
    def get_money_management_workers(self):
        """Get money management workers"""
        try:
            workers = self.db_manager.get_workers_by_service("money_management")
            return {"success": True, "workers": workers}
                
        except Exception as e:
            return {"success": False, "message": f"Failed to get money management workers: {str(e)}"}
    
    # Token Verification
    def verify_token(self, token):
        """Verify authentication token"""
        try:
            payload = verify_token(token)
            if payload:
                return {"success": True, "payload": payload}
            else:
                return {"success": False, "message": "Invalid token"}
                
        except Exception as e:
            return {"success": False, "message": f"Token verification failed: {str(e)}"}
    
    # Service Statistics
    def get_service_statistics(self, service_type):
        """Get statistics for a service"""
        try:
            stats = self.db_manager.get_service_statistics(service_type)
            return {"success": True, "statistics": stats}
                
        except Exception as e:
            return {"success": False, "message": f"Failed to get statistics: {str(e)}"}
    
    # Health Check
    def health_check(self):
        """Check authentication service health"""
        try:
            db_health = self.db_manager.check_database_health()
            return {
                "success": True,
                "service": "auth_service",
                "status": "healthy",
                "databases": db_health
            }
                
        except Exception as e:
            return {
                "success": False,
                "service": "auth_service", 
                "status": "error",
                "error": str(e)
            }

# Global instance
auth_service = AuthService()

# Convenience functions for backward compatibility
def register_user(email, password, name, phone=None):
    return auth_service.register_user(email, password, name, phone)

def login_user(email, password):
    return auth_service.login_user(email, password)

def register_worker(email, password, name, phone, service_type, worker_type):
    return auth_service.register_worker(email, password, name, phone, service_type, worker_type)

def login_worker(email, password):
    return auth_service.login_worker(email, password)

def get_workers_by_service(service_type):
    return auth_service.get_workers_by_service(service_type)
