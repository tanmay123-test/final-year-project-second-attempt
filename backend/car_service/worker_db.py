"""
Car Service Worker Database
Manages worker authentication and profiles
"""

import os
import psycopg2
import psycopg2.extras
import bcrypt
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Optional

load_dotenv()

class WorkerDB:
    def __init__(self):
        self.create_table()
    
    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
    
    def create_table(self):
        """Create workers table"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workers (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    city TEXT NOT NULL,
                    address TEXT NOT NULL,
                    experience INTEGER NOT NULL,
                    skills TEXT NOT NULL,
                    vehicle_number TEXT,
                    vehicle_model TEXT,
                    loading_capacity TEXT,
                    profile_photo TEXT,
                    aadhaar_path TEXT,
                    license_path TEXT,
                    certificate_path TEXT,
                    vehicle_rc_path TEXT,
                    truck_photo_path TEXT,
                    security_declaration BOOLEAN NOT NULL DEFAULT FALSE,
                    status TEXT NOT NULL DEFAULT 'PENDING',
                    is_online BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_worker(self, name: str, phone: str, email: str, password: str, role: str,
                     age: int, city: str, address: str, experience: int, skills: str,
                     vehicle_number: str = None, vehicle_model: str = None, 
                     loading_capacity: str = None, profile_photo: str = None,
                     aadhaar_path: str = None, license_path: str = None,
                     certificate_path: str = None, vehicle_rc_path: str = None,
                     truck_photo_path: str = None, security_declaration: bool = False) -> int:
        """Create a new worker"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Check if phone already exists
            if self.get_worker_by_phone(phone):
                raise ValueError("Phone number already registered")
            
            # Check if email already exists
            if self.get_worker_by_email(email):
                raise ValueError("Email already registered")
            
            # Hash password
            password_hash = self.hash_password(password)
            
            cursor.execute("""
                INSERT INTO workers 
                (name, phone, email, password_hash, role, age, city, address, experience, skills,
                 vehicle_number, vehicle_model, loading_capacity, profile_photo, aadhaar_path,
                 license_path, certificate_path, vehicle_rc_path, truck_photo_path, security_declaration)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (name, phone, email, password_hash, role, age, city, address, experience, skills,
                  vehicle_number, vehicle_model, loading_capacity, profile_photo, aadhaar_path,
                  license_path, certificate_path, vehicle_rc_path, truck_photo_path, 
                  security_declaration))
            
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_worker_by_phone(self, phone: str) -> Optional[Dict]:
        """Get worker by phone number"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM workers WHERE phone = %s", (phone,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_worker_by_email(self, email: str) -> Optional[Dict]:
        """Get worker by email"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM workers WHERE email = %s", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def verify_worker(self, phone: str, password: str) -> Optional[Dict]:
        """Verify worker credentials"""
        worker = self.get_worker_by_phone(phone)
        if worker and self.verify_password(password, worker['password_hash']):
            return worker
        return None
    
    def verify_worker_by_email(self, email: str, password: str) -> Optional[Dict]:
        """Verify worker credentials by email"""
        worker = self.get_worker_by_email(email)
        if worker and self.verify_password(password, worker['password_hash']):
            return worker
        return None
    
    def approve_worker(self, worker_id: int) -> bool:
        """Approve a worker"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE workers SET status = 'APPROVED' WHERE id = %s", (worker_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_worker_status(self, worker_id: int, status: str) -> bool:
        """Update worker status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE workers SET status = %s WHERE id = %s", (status, worker_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_all_workers(self) -> List[Dict]:
        """Get all workers"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM workers ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_pending_workers(self) -> List[Dict]:
        """Get pending workers for admin approval"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM workers WHERE status = 'PENDING' ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_approved_workers(self) -> List[Dict]:
        """Get approved workers"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM workers WHERE status = 'APPROVED' ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_workers_by_role(self, role: str) -> List[Dict]:
        """Get workers by role"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM workers WHERE role = %s AND status = 'APPROVED' ORDER BY created_at DESC", (role,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def set_worker_online_status(self, worker_id: int, is_online: bool) -> bool:
        """Set worker online/offline status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE workers SET is_online = %s WHERE id = %s", 
                          (is_online, worker_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

# Global instance
worker_db = WorkerDB()
