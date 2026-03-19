"""
Tow Truck Database Module
Handles all database operations for tow truck operators
"""

import sqlite3
import os
from datetime import datetime
import json
from database.database_manager import db_manager

TOW_TRUCK_DB_PATH = "backend/database/databases/car_service_workers/tow_truck.db"

def get_connection():
    """Get a connection to the tow truck database"""
    os.makedirs(os.path.dirname(TOW_TRUCK_DB_PATH), exist_ok=True)
    return sqlite3.connect(TOW_TRUCK_DB_PATH)

class TowTruckDB:
    """Tow Truck Database Manager"""
    
    def __init__(self):
        self.db_path = TOW_TRUCK_DB_PATH
        self.uploads_dir = "backend/uploads/tow_truck"
        self._ensure_directories()
        self._create_tables()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.uploads_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _create_tables(self):
        """Create all required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Operator Profiles Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tow_operator_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    worker_id INTEGER UNIQUE,
                    name TEXT NOT NULL,
                    truck_model TEXT,
                    vehicle_number TEXT,
                    capacity TEXT,
                    is_online INTEGER DEFAULT 0,
                    is_busy INTEGER DEFAULT 0,
                    city TEXT,
                    rating REAL DEFAULT 5.0,
                    service_radius INTEGER DEFAULT 10,
                    current_location TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (worker_id) REFERENCES workers(id)
                )
            ''')
            
            # Tow Requests Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tow_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    pickup_location TEXT NOT NULL,
                    drop_location TEXT NOT NULL,
                    vehicle_type TEXT,
                    vehicle_condition TEXT,
                    distance REAL,
                    estimated_earning REAL,
                    priority TEXT DEFAULT 'NORMAL',
                    assigned_operator_id INTEGER,
                    status TEXT DEFAULT 'SEARCHING',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (assigned_operator_id) REFERENCES tow_operator_profiles(worker_id)
                )
            ''')
            
            # Active Jobs Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tow_active_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id INTEGER UNIQUE,
                    operator_id INTEGER,
                    user_name TEXT,
                    pickup_location TEXT NOT NULL,
                    drop_location TEXT NOT NULL,
                    status TEXT DEFAULT 'ACCEPTED',
                    otp TEXT,
                    pickup_photo TEXT,
                    drop_photo TEXT,
                    start_time TEXT,
                    pickup_time TEXT,
                    drop_time TEXT,
                    completion_time TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (request_id) REFERENCES tow_requests(id),
                    FOREIGN KEY (operator_id) REFERENCES tow_operator_profiles(worker_id)
                )
            ''')
            
            # Earnings Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tow_earnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operator_id INTEGER,
                    job_id INTEGER,
                    base_amount REAL,
                    distance_amount REAL,
                    bonus REAL DEFAULT 0,
                    final_amount REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (operator_id) REFERENCES tow_operator_profiles(worker_id),
                    FOREIGN KEY (job_id) REFERENCES tow_active_jobs(id)
                )
            ''')
            
            # Safety Alerts Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tow_safety_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operator_id INTEGER,
                    job_id INTEGER,
                    alert_type TEXT,
                    description TEXT,
                    location TEXT,
                    is_resolved INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (operator_id) REFERENCES tow_operator_profiles(worker_id),
                    FOREIGN KEY (job_id) REFERENCES tow_active_jobs(id)
                )
            ''')
            
            conn.commit()
    
    def create_operator_profile(self, worker_id, name, truck_model, vehicle_number, capacity, city):
        """Create tow truck operator profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO tow_operator_profiles 
                (worker_id, name, truck_model, vehicle_number, capacity, city, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (worker_id, name, truck_model, vehicle_number, capacity, city, datetime.now(), datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def get_operator_profile(self, worker_id):
        """Get operator profile by worker_id"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tow_operator_profiles WHERE worker_id = ?', (worker_id,))
            return cursor.fetchone()
    
    def update_operator_status(self, worker_id, is_online=None, is_busy=None, current_location=None):
        """Update operator online/busy status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if is_online is not None:
                updates.append("is_online = ?")
                params.append(is_online)
            
            if is_busy is not None:
                updates.append("is_busy = ?")
                params.append(is_busy)
            
            if current_location:
                updates.append("current_location = ?")
                params.append(current_location)
            
            updates.append("updated_at = ?")
            params.append(datetime.now())
            params.append(worker_id)
            
            if updates:
                cursor.execute(f'''
                    UPDATE tow_operator_profiles 
                    SET {', '.join(updates)}
                    WHERE worker_id = ?
                ''', params)
                conn.commit()
    
    def create_tow_request(self, user_id, pickup_location, drop_location, vehicle_type, vehicle_condition, distance, estimated_earning, priority='NORMAL'):
        """Create new tow request"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tow_requests 
                (user_id, pickup_location, drop_location, vehicle_type, vehicle_condition, distance, estimated_earning, priority, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, pickup_location, drop_location, vehicle_type, vehicle_condition, distance, estimated_earning, priority, datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def get_pending_requests(self):
        """Get pending tow requests"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tr.*, u.name as user_name, u.phone as user_phone
                FROM tow_requests tr
                LEFT JOIN users u ON tr.user_id = u.id
                WHERE tr.status = 'SEARCHING'
                ORDER BY tr.priority DESC, tr.created_at ASC
            ''')
            return cursor.fetchall()
    
    def assign_request(self, request_id, operator_id):
        """Assign request to operator"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Update request status
            cursor.execute('''
                UPDATE tow_requests 
                SET assigned_operator_id = ?, status = 'ASSIGNED', updated_at = ?
                WHERE id = ?
            ''', (operator_id, datetime.now(), request_id))
            
            # Create active job
            cursor.execute('''
                INSERT INTO tow_active_jobs 
                (request_id, operator_id, pickup_location, drop_location, status, created_at)
                SELECT id, ?, pickup_location, drop_location, 'ACCEPTED', ?
                FROM tow_requests WHERE id = ?
            ''', (operator_id, datetime.now(), request_id))
            
            # Update operator status
            cursor.execute('''
                UPDATE tow_operator_profiles 
                SET is_busy = 1, updated_at = ?
                WHERE worker_id = ?
            ''', (datetime.now(), operator_id))
            
            conn.commit()
    
    def get_active_job(self, operator_id):
        """Get active job for operator"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT taj.*, tr.user_name, tr.pickup_location, tr.drop_location, tr.distance, tr.estimated_earning
                FROM tow_active_jobs taj
                JOIN tow_requests tr ON taj.request_id = tr.id
                WHERE taj.operator_id = ? AND taj.status NOT IN ('COMPLETED', 'CANCELLED')
                ORDER BY taj.created_at DESC
                LIMIT 1
            ''', (operator_id,))
            return cursor.fetchone()
    
    def generate_otp(self, job_id):
        """Generate 4-digit OTP for job"""
        import random
        otp = f"{random.randint(1000, 9999)}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE tow_active_jobs SET otp = ? WHERE id = ?', (otp, job_id))
            conn.commit()
        
        return otp
    
    def verify_otp(self, job_id, entered_otp):
        """Verify OTP for job"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT otp FROM tow_active_jobs WHERE id = ?', (job_id,))
            result = cursor.fetchone()
            
            if result and result[0] == entered_otp:
                cursor.execute('UPDATE tow_active_jobs SET status = ?, pickup_time = ? WHERE id = ?', ('LOADING', datetime.now(), job_id))
                conn.commit()
                return True
            return False
    
    def complete_job(self, job_id, final_amount):
        """Complete job and update earnings"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get job details
            cursor.execute('SELECT operator_id, request_id FROM tow_active_jobs WHERE id = ?', (job_id,))
            job = cursor.fetchone()
            
            if job:
                operator_id, request_id = job
                
                # Update job status
                cursor.execute('''
                    UPDATE tow_active_jobs 
                    SET status = 'COMPLETED', completion_time = ?
                    WHERE id = ?
                ''', (datetime.now(), job_id))
                
                # Update request status
                cursor.execute('''
                    UPDATE tow_requests 
                    SET status = 'COMPLETED', updated_at = ?
                    WHERE id = ?
                ''', (datetime.now(), request_id))
                
                # Update operator status
                cursor.execute('''
                    UPDATE tow_operator_profiles 
                    SET is_busy = 0, updated_at = ?
                    WHERE worker_id = ?
                ''', (datetime.now(), operator_id))
                
                # Add earnings record
                cursor.execute('''
                    INSERT INTO tow_earnings 
                    (operator_id, job_id, final_amount, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (operator_id, job_id, final_amount, datetime.now()))
                
                conn.commit()
                return True
            return False
    
    def get_earnings(self, operator_id, period='today'):
        """Get operator earnings"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if period == 'today':
                cursor.execute('''
                    SELECT SUM(final_amount) as total, COUNT(*) as jobs
                    FROM tow_earnings 
                    WHERE operator_id = ? AND DATE(created_at) = DATE('now')
                ''', (operator_id,))
            else:
                cursor.execute('''
                    SELECT SUM(final_amount) as total, COUNT(*) as jobs
                    FROM tow_earnings 
                    WHERE operator_id = ?
                ''', (operator_id,))
            
            return cursor.fetchone()
    
    def create_safety_alert(self, operator_id, job_id, alert_type, description, location=None):
        """Create safety alert"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tow_safety_alerts 
                (operator_id, job_id, alert_type, description, location, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (operator_id, job_id, alert_type, description, location, datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def get_online_operators(self):
        """Get all online operators"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT op.*, w.email, w.phone
                FROM tow_operator_profiles op
                JOIN workers w ON op.worker_id = w.id
                WHERE op.is_online = 1 AND op.is_busy = 0
                ORDER BY op.rating DESC
            ''')
            return cursor.fetchall()

# Global instance
tow_db = TowTruckDB()
