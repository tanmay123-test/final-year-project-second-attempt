"""
Car Service Unified Worker Database
Stores all car service workers and filters by role
"""

import os
import sqlite3
import bcrypt
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Database path
CAR_SERVICE_WORKERS_DB = os.path.join(os.path.dirname(__file__), 'car_service_workers.db')

class CarServiceWorkerDB:
    def __init__(self):
        self.conn = sqlite3.connect(CAR_SERVICE_WORKERS_DB, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_table()
    
    def get_conn(self):
        return sqlite3.connect(CAR_SERVICE_WORKERS_DB, check_same_thread=False)
    
    def create_table(self):
        """Create unified car service workers table"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS car_service_workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('Mechanic', 'Fuel Delivery Agent', 'Tow Truck Operator', 'Automobile Expert')),
                age INTEGER NOT NULL,
                city TEXT NOT NULL,
                address TEXT NOT NULL,
                experience INTEGER NOT NULL,
                skills TEXT NOT NULL,
                
                -- Vehicle info (for fuel/tow roles)
                vehicle_number TEXT,
                vehicle_model TEXT,
                loading_capacity TEXT,
                
                -- Documents
                profile_photo TEXT,
                aadhaar_path TEXT,
                license_path TEXT,
                certificate_path TEXT,
                vehicle_rc_path TEXT,
                truck_photo_path TEXT,
                
                -- Status and metadata
                security_declaration INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'PENDING',
                is_online INTEGER DEFAULT 0,
                is_busy INTEGER DEFAULT 0,
                service_radius INTEGER DEFAULT 10,
                current_city TEXT,
                last_status_update TEXT,
                cooldown_until TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add new columns if they don't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE car_service_workers ADD COLUMN is_busy INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE car_service_workers ADD COLUMN service_radius INTEGER DEFAULT 10")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE car_service_workers ADD COLUMN current_city TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE car_service_workers ADD COLUMN last_status_update TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE car_service_workers ADD COLUMN cooldown_until TEXT")
        except sqlite3.OperationalError:
            pass
        
        self.conn.commit()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_worker(self, name: str, email: str, phone: str, password: str, role: str,
                     age: int, city: str, address: str, experience: int, skills: str,
                     vehicle_number: str = None, vehicle_model: str = None, 
                     loading_capacity: str = None, profile_photo: str = None,
                     aadhaar_path: str = None, license_path: str = None,
                     certificate_path: str = None, vehicle_rc_path: str = None,
                     truck_photo_path: str = None, security_declaration: bool = False) -> int:
        """Create a new car service worker"""
        cursor = self.conn.cursor()
        
        # Check if email already exists
        if self.get_worker_by_email(email):
            raise ValueError("Email already registered")
        
        # Check if phone already exists
        if self.get_worker_by_phone(phone):
            raise ValueError("Phone number already registered")
        
        # Hash password
        password_hash = self.hash_password(password)
        
        cursor.execute("""
            INSERT INTO car_service_workers 
            (name, email, phone, password_hash, role, age, city, address, experience, skills,
             vehicle_number, vehicle_model, loading_capacity, profile_photo, aadhaar_path,
             license_path, certificate_path, vehicle_rc_path, truck_photo_path, security_declaration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, password_hash, role, age, city, address, experience, skills,
              vehicle_number, vehicle_model, loading_capacity, profile_photo, aadhaar_path,
              license_path, certificate_path, vehicle_rc_path, truck_photo_path, 
              1 if security_declaration else 0))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_worker_by_email(self, email: str) -> Optional[Dict]:
        """Get worker by email"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * from services.car_service_workers WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_worker_by_phone(self, phone: str) -> Optional[Dict]:
        """Get worker by phone number"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * from services.car_service_workers WHERE phone = ?", (phone,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_worker_by_id(self, worker_id: int) -> Optional[Dict]:
        """Get worker by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * from services.car_service_workers WHERE id = ?", (worker_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def verify_worker(self, email: str, password: str) -> Optional[Dict]:
        """Verify worker credentials"""
        worker = self.get_worker_by_email(email)
        if worker and self.verify_password(password, worker['password_hash']):
            return worker
        return None
    
    def set_online_status(self, worker_id: int, is_online: bool) -> bool:
        """Set worker online/offline status"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE car_service_workers SET is_online = ? WHERE id = ?", 
                      (1 if is_online else 0, worker_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def update_worker_status(self, worker_id: int, status: str) -> bool:
        """Update worker status"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE car_service_workers SET status = ? WHERE id = ?", (status, worker_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # ===== ROLE-SPECIFIC METHODS =====
    
    def get_mechanics(self, status: str = None) -> List[Dict]:
        """Get all mechanics"""
        cursor = self.conn.cursor()
        if status:
            cursor.execute("SELECT * from services.car_service_workers WHERE role = 'Mechanic' AND status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * from services.car_service_workers WHERE role = 'Mechanic' ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_fuel_agents(self, status: str = None) -> List[Dict]:
        """Get all fuel delivery agents"""
        cursor = self.conn.cursor()
        if status:
            cursor.execute("SELECT * from services.car_service_workers WHERE role = 'Fuel Delivery Agent' AND status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * from services.car_service_workers WHERE role = 'Fuel Delivery Agent' ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_tow_operators(self, status: str = None) -> List[Dict]:
        """Get all tow truck operators"""
        cursor = self.conn.cursor()
        if status:
            cursor.execute("SELECT * from services.car_service_workers WHERE role = 'Tow Truck Operator' AND status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * from services.car_service_workers WHERE role = 'Tow Truck Operator' ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_automobile_experts(self, status: str = None) -> List[Dict]:
        """Get all automobile experts"""
        cursor = self.conn.cursor()
        if status:
            cursor.execute("SELECT * from services.car_service_workers WHERE role = 'Automobile Expert' AND status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * from services.car_service_workers WHERE role = 'Automobile Expert' ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_online_mechanics(self) -> List[Dict]:
        """Get all online mechanics"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * from services.car_service_workers WHERE role = 'Mechanic' AND is_online = 1 AND status = 'APPROVED'")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_online_fuel_agents(self) -> List[Dict]:
        """Get all online fuel delivery agents"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * from services.car_service_workers WHERE role = 'Fuel Delivery Agent' AND is_online = 1 AND status = 'APPROVED'")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_online_tow_operators(self) -> List[Dict]:
        """Get all online tow truck operators"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * from services.car_service_workers WHERE role = 'Tow Truck Operator' AND is_online = 1 AND status = 'APPROVED'")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_online_experts(self) -> List[Dict]:
        """Get all online automobile experts"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * from services.car_service_workers WHERE role = 'Automobile Expert' AND is_online = 1 AND status = 'APPROVED'")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_workers(self) -> List[Dict]:
        """Get all workers"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * from services.car_service_workers ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def search_workers(self, name: str = "") -> List[Dict]:
        """Search workers by name"""
        cursor = self.conn.cursor()
        if name:
            cursor.execute("""
                SELECT * from services.car_service_workers 
                WHERE name LIKE ? OR email LIKE ? OR role LIKE ?
                ORDER BY created_at DESC
            """, (f"%{name}%", f"%{name}%", f"%{name}%"))
        else:
            cursor.execute("SELECT * from services.car_service_workers ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_pending_workers(self) -> List[Dict]:
        """Get all pending workers"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * from services.car_service_workers WHERE status = 'PENDING' ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_approved_workers(self) -> List[Dict]:
        """Get all approved workers"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * from services.car_service_workers WHERE status = 'APPROVED' ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_workers_by_role(self, role: str, status: str = None) -> List[Dict]:
        """Get workers by specific role"""
        cursor = self.conn.cursor()
        if status:
            cursor.execute("SELECT * from services.car_service_workers WHERE role = ? AND status = ? ORDER BY created_at DESC", (role, status))
        else:
            cursor.execute("SELECT * from services.car_service_workers WHERE role = ? ORDER BY created_at DESC", (role,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ===== STATUS MANAGEMENT FUNCTIONS =====
    
    def set_online(self, worker_id: int) -> bool:
        """Set worker to ONLINE status"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE car_service_workers 
            SET is_online = 1, is_busy = 0, last_status_update = ?, cooldown_until = NULL
            WHERE id = ?
        """, (datetime.now().isoformat(), worker_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def set_offline(self, worker_id: int) -> bool:
        """Set worker to OFFLINE status"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE car_service_workers 
            SET is_online = 0, is_busy = 0, last_status_update = ?, cooldown_until = NULL
            WHERE id = ?
        """, (datetime.now().isoformat(), worker_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def set_busy(self, worker_id: int) -> bool:
        """Set worker to BUSY status"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE car_service_workers 
            SET is_busy = 1, last_status_update = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), worker_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def set_available(self, worker_id: int) -> bool:
        """Set worker to AVAILABLE (ONLINE but not BUSY)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE car_service_workers 
            SET is_busy = 0, last_status_update = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), worker_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def update_service_radius(self, worker_id: int, radius: int) -> bool:
        """Update worker service radius"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE car_service_workers SET service_radius = ? WHERE id = ?", (radius, worker_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def update_current_location(self, worker_id: int, city: str) -> bool:
        """Update worker current working city"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE car_service_workers SET current_city = ? WHERE id = ?", (city, worker_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_worker_status(self, worker_id: int) -> str:
        """Get worker's current status"""
        worker = self.get_worker_by_id(worker_id)
        if not worker:
            return "UNKNOWN"
        
        is_online = worker.get('is_online', 0)
        is_busy = worker.get('is_busy', 0)
        
        if not is_online:
            return "OFFLINE"
        elif is_busy:
            return "BUSY"
        else:
            return "ONLINE"
    
    def get_available_workers(self) -> List[Dict]:
        """Get all available workers (ONLINE and not BUSY)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * from services.car_service_workers 
            WHERE is_online = 1 AND is_busy = 0 AND status = 'APPROVED'
            ORDER BY created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

# Global instance
car_service_worker_db = CarServiceWorkerDB()
