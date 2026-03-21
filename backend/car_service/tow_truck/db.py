"""
Tow Truck Database Module
Handles all database operations for tow truck operators
"""

import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

class TowTruckDB:
    """Tow Truck Database Manager"""
    
    def __init__(self):
        self.uploads_dir = "backend/uploads/tow_truck"
        self._ensure_directories()
        self._create_tables()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.uploads_dir, exist_ok=True)
    
    def _create_tables(self):
        """Create all required tables"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Operator Profiles Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tow_operator_profiles (
                    id SERIAL PRIMARY KEY,
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tow Requests Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tow_requests (
                    id SERIAL PRIMARY KEY,
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (assigned_operator_id) REFERENCES tow_operator_profiles(worker_id)
                )
            ''')
            
            # Active Jobs Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tow_active_jobs (
                    id SERIAL PRIMARY KEY,
                    request_id INTEGER UNIQUE,
                    operator_id INTEGER,
                    user_name TEXT,
                    pickup_location TEXT NOT NULL,
                    drop_location TEXT NOT NULL,
                    status TEXT DEFAULT 'ACCEPTED',
                    otp TEXT,
                    pickup_photo TEXT,
                    drop_photo TEXT,
                    start_time TIMESTAMP,
                    pickup_time TIMESTAMP,
                    drop_time TIMESTAMP,
                    completion_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (request_id) REFERENCES tow_requests(id),
                    FOREIGN KEY (operator_id) REFERENCES tow_operator_profiles(worker_id)
                )
            ''')
            
            # Earnings Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tow_earnings (
                    id SERIAL PRIMARY KEY,
                    operator_id INTEGER,
                    job_id INTEGER,
                    base_amount REAL,
                    distance_amount REAL,
                    bonus REAL DEFAULT 0,
                    final_amount REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (operator_id) REFERENCES tow_operator_profiles(worker_id),
                    FOREIGN KEY (job_id) REFERENCES tow_active_jobs(id)
                )
            ''')
            
            # Safety Alerts Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tow_safety_alerts (
                    id SERIAL PRIMARY KEY,
                    operator_id INTEGER,
                    job_id INTEGER,
                    alert_type TEXT,
                    description TEXT,
                    location TEXT,
                    is_resolved INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (operator_id) REFERENCES tow_operator_profiles(worker_id),
                    FOREIGN KEY (job_id) REFERENCES tow_active_jobs(id)
                )
            ''')
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def create_operator_profile(self, worker_id, name, truck_model, vehicle_number, capacity, city):
        """Create tow truck operator profile"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO tow_operator_profiles 
                (worker_id, name, truck_model, vehicle_number, capacity, city, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (worker_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    truck_model = EXCLUDED.truck_model,
                    vehicle_number = EXCLUDED.vehicle_number,
                    capacity = EXCLUDED.capacity,
                    city = EXCLUDED.city,
                    updated_at = EXCLUDED.updated_at
                RETURNING id
            ''', (worker_id, name, truck_model, vehicle_number, capacity, city, datetime.now(), datetime.now()))
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
    
    def get_operator_profile(self, worker_id):
        """Get operator profile by worker_id"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM tow_operator_profiles WHERE worker_id = %s', (worker_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def update_operator_status(self, worker_id, is_online=None, is_busy=None, current_location=None):
        """Update operator online/busy status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            updates = []
            params = []
            
            if is_online is not None:
                updates.append("is_online = %s")
                params.append(is_online)
            
            if is_busy is not None:
                updates.append("is_busy = %s")
                params.append(is_busy)
            
            if current_location:
                updates.append("current_location = %s")
                params.append(current_location)
            
            updates.append("updated_at = %s")
            params.append(datetime.now())
            params.append(worker_id)
            
            if updates:
                cursor.execute(f'''
                    UPDATE tow_operator_profiles 
                    SET {', '.join(updates)}
                    WHERE worker_id = %s
                ''', params)
                conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def create_tow_request(self, user_id, pickup_location, drop_location, vehicle_type, vehicle_condition, distance, estimated_earning, priority='NORMAL'):
        """Create new tow request"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO tow_requests 
                (user_id, pickup_location, drop_location, vehicle_type, vehicle_condition, distance, estimated_earning, priority, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            ''', (user_id, pickup_location, drop_location, vehicle_type, vehicle_condition, distance, estimated_earning, priority, datetime.now()))
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
    
    def get_pending_requests(self):
        """Get pending tow requests"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute('''
                SELECT tr.*, u.name as user_name, u.email as user_email
                FROM tow_requests tr
                LEFT JOIN users u ON tr.user_id = u.id
                WHERE tr.status = 'SEARCHING'
                ORDER BY tr.priority DESC, tr.created_at ASC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def assign_request(self, request_id, operator_id):
        """Assign request to operator"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            now = datetime.now()
            # Update request status
            cursor.execute('''
                UPDATE tow_requests 
                SET assigned_operator_id = %s, status = 'ASSIGNED', updated_at = %s
                WHERE id = %s
            ''', (operator_id, now, request_id))
            
            # Create active job
            cursor.execute('''
                INSERT INTO tow_active_jobs 
                (request_id, operator_id, pickup_location, drop_location, status, created_at)
                SELECT id, %s, pickup_location, drop_location, 'ACCEPTED', %s
                FROM tow_requests WHERE id = %s
            ''', (operator_id, now, request_id))
            
            # Update operator status
            cursor.execute('''
                UPDATE tow_operator_profiles 
                SET is_busy = 1, updated_at = %s
                WHERE worker_id = %s
            ''', (now, operator_id))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_active_job(self, operator_id):
        """Get active job for operator"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute('''
                SELECT taj.*, tr.pickup_location, tr.drop_location, tr.distance, tr.estimated_earning
                FROM tow_active_jobs taj
                JOIN tow_requests tr ON taj.request_id = tr.id
                WHERE taj.operator_id = %s AND taj.status NOT IN ('COMPLETED', 'CANCELLED')
                ORDER BY taj.created_at DESC
                LIMIT 1
            ''', (operator_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def generate_otp(self, job_id):
        """Generate 4-digit OTP for job"""
        import random
        otp = f"{random.randint(1000, 9999)}"
        
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE tow_active_jobs SET otp = %s WHERE id = %s', (otp, job_id))
            conn.commit()
            return otp
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def verify_otp(self, job_id, entered_otp):
        """Verify OTP for job"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT otp FROM tow_active_jobs WHERE id = %s', (job_id,))
            result = cursor.fetchone()
            
            if result and result[0] == entered_otp:
                cursor.execute('UPDATE tow_active_jobs SET status = %s, pickup_time = %s WHERE id = %s', ('LOADING', datetime.now(), job_id))
                conn.commit()
                return True
            return False
        except Exception as e:
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def complete_job(self, job_id, final_amount):
        """Complete job and update earnings"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            now = datetime.now()
            # Get job details
            cursor.execute('SELECT operator_id, request_id FROM tow_active_jobs WHERE id = %s', (job_id,))
            job = cursor.fetchone()
            
            if job:
                operator_id, request_id = job
                
                # Update job status
                cursor.execute('''
                    UPDATE tow_active_jobs 
                    SET status = 'COMPLETED', completion_time = %s
                    WHERE id = %s
                ''', (now, job_id))
                
                # Update request status
                cursor.execute('''
                    UPDATE tow_requests 
                    SET status = 'COMPLETED', updated_at = %s
                    WHERE id = %s
                ''', (now, request_id))
                
                # Update operator status
                cursor.execute('''
                    UPDATE tow_operator_profiles 
                    SET is_busy = 0, updated_at = %s
                    WHERE worker_id = %s
                ''', (now, operator_id))
                
                # Add earnings record
                cursor.execute('''
                    INSERT INTO tow_earnings 
                    (operator_id, job_id, final_amount, created_at)
                    VALUES (%s, %s, %s, %s)
                ''', (operator_id, job_id, final_amount, now))
                
                conn.commit()
                return True
            return False
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_earnings(self, operator_id, period='today'):
        """Get operator earnings"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if period == 'today':
                cursor.execute('''
                    SELECT SUM(final_amount) as total, COUNT(*) as jobs
                    FROM tow_earnings 
                    WHERE operator_id = %s AND created_at::DATE = CURRENT_DATE
                ''', (operator_id,))
            else:
                cursor.execute('''
                    SELECT SUM(final_amount) as total, COUNT(*) as jobs
                    FROM tow_earnings 
                    WHERE operator_id = %s
                ''', (operator_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else {'total': 0, 'jobs': 0}
        except Exception as e:
            print(f"DB Error: {e}")
            return {'total': 0, 'jobs': 0}
        finally:
            cursor.close()
            conn.close()
    
    def create_safety_alert(self, operator_id, job_id, alert_type, description, location=None):
        """Create safety alert"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO tow_safety_alerts 
                (operator_id, job_id, alert_type, description, location, created_at)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            ''', (operator_id, job_id, alert_type, description, location, datetime.now()))
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
    
    def get_online_operators(self):
        """Get all online operators"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute('''
                SELECT op.*, w.email, w.username
                FROM tow_operator_profiles op
                JOIN workers w ON op.worker_id = w.id
                WHERE op.is_online = 1 AND op.is_busy = 0
                ORDER BY op.rating DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

# Global instance
tow_db = TowTruckDB()
