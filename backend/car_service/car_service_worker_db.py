"""
Car Service Unified Worker Database
Stores all car service workers and filters by role
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import bcrypt
from datetime import datetime, timedelta
from typing import List, Dict, Optional

load_dotenv()

class CarServiceWorkerDB:
    def __init__(self):
        self.create_table()
    
    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
    
    def create_table(self):
        """Create unified car service workers table"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS car_service_workers (
                    id SERIAL PRIMARY KEY,
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
                    security_declaration BOOLEAN NOT NULL DEFAULT FALSE,
                    status TEXT NOT NULL DEFAULT 'PENDING',
                    is_online BOOLEAN DEFAULT FALSE,
                    is_busy BOOLEAN DEFAULT FALSE,
                    service_radius INTEGER DEFAULT 10,
                    bio TEXT,
                    specialization TEXT,
                    current_city TEXT,
                    last_status_update TEXT,
                    cooldown_until TEXT,
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
    
    def create_worker(self, name: str, email: str, phone: str, password: str, role: str,
                     age: int, city: str, address: str, experience: int, skills: str,
                     vehicle_number: str = None, vehicle_model: str = None, 
                     loading_capacity: str = None, profile_photo: str = None,
                     aadhaar_path: str = None, license_path: str = None,
                     certificate_path: str = None, vehicle_rc_path: str = None,
                     truck_photo_path: str = None, security_declaration: bool = False) -> int:
        """Create a new car service worker"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (name, email, phone, password_hash, role, age, city, address, experience, skills,
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
    
    def get_worker_by_email(self, email: str) -> Optional[Dict]:
        """Get worker by email"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM car_service_workers WHERE email = %s", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
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
            cursor.execute("SELECT * FROM car_service_workers WHERE phone = %s", (phone,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_worker_by_id(self, worker_id: int) -> Optional[Dict]:
        """Get worker by ID"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM car_service_workers WHERE id = %s", (worker_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def verify_worker(self, email: str, password: str) -> Optional[Dict]:
        """Verify worker credentials"""
        worker = self.get_worker_by_email(email)
        if worker and self.verify_password(password, worker['password_hash']):
            return worker
        return None
    
    def set_online_status(self, worker_id: int, is_online: bool) -> bool:
        """Set worker online/offline status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE car_service_workers SET is_online = %s WHERE id = %s", 
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
    
    def update_worker_status(self, worker_id: int, status: str) -> bool:
        """Update worker status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE car_service_workers SET status = %s WHERE id = %s", (status, worker_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # ===== ROLE-SPECIFIC METHODS =====
    
    def get_mechanics(self, status: str = None) -> List[Dict]:
        """Get all mechanics"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if status:
                cursor.execute("SELECT * FROM car_service_workers WHERE role = 'Mechanic' AND status = %s ORDER BY created_at DESC", (status,))
            else:
                cursor.execute("SELECT * FROM car_service_workers WHERE role = 'Mechanic' ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_fuel_agents(self, status: str = None) -> List[Dict]:
        """Get all fuel delivery agents"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if status:
                cursor.execute("SELECT * FROM car_service_workers WHERE role = 'Fuel Delivery Agent' AND status = %s ORDER BY created_at DESC", (status,))
            else:
                cursor.execute("SELECT * FROM car_service_workers WHERE role = 'Fuel Delivery Agent' ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_tow_operators(self, status: str = None) -> List[Dict]:
        """Get all tow truck operators"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if status:
                cursor.execute("SELECT * FROM car_service_workers WHERE role = 'Tow Truck Operator' AND status = %s ORDER BY created_at DESC", (status,))
            else:
                cursor.execute("SELECT * FROM car_service_workers WHERE role = 'Tow Truck Operator' ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_automobile_experts(self, status: str = None) -> List[Dict]:
        """Get all automobile experts"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if status:
                cursor.execute("SELECT * FROM car_service_workers WHERE role = 'Automobile Expert' AND status = %s ORDER BY created_at DESC", (status,))
            else:
                cursor.execute("SELECT * FROM car_service_workers WHERE role = 'Automobile Expert' ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_online_mechanics(self) -> List[Dict]:
        """Get all online mechanics"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM car_service_workers WHERE role = 'Mechanic' AND is_online = TRUE AND status = 'APPROVED'")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_online_fuel_agents(self) -> List[Dict]:
        """Get all online fuel delivery agents"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM car_service_workers WHERE role = 'Fuel Delivery Agent' AND is_online = TRUE AND status = 'APPROVED'")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_online_tow_operators(self) -> List[Dict]:
        """Get all online tow truck operators"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM car_service_workers WHERE role = 'Tow Truck Operator' AND is_online = TRUE AND status = 'APPROVED'")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_online_experts(self) -> List[Dict]:
        """Get all online automobile experts"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM car_service_workers WHERE role = 'Automobile Expert' AND is_online = TRUE AND status = 'APPROVED'")
            return [dict(row) for row in cursor.fetchall()]
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
            cursor.execute("SELECT * FROM car_service_workers ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def search_workers(self, name: str = "") -> List[Dict]:
        """Search workers by name"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if name:
                cursor.execute("""
                    SELECT * FROM car_service_workers 
                    WHERE name LIKE %s OR email LIKE %s OR role LIKE %s
                    ORDER BY created_at DESC
                """, (f"%{name}%", f"%{name}%", f"%{name}%"))
            else:
                cursor.execute("SELECT * FROM car_service_workers ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_pending_workers(self) -> List[Dict]:
        """Get all pending workers"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM car_service_workers WHERE status = 'PENDING' ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_approved_workers(self) -> List[Dict]:
        """Get all approved workers"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM car_service_workers WHERE status = 'APPROVED' ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_workers_by_role(self, role: str, status: str = None) -> List[Dict]:
        """Get workers by specific role"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if status:
                cursor.execute("SELECT * FROM car_service_workers WHERE role = %s AND status = %s ORDER BY created_at DESC", (role, status))
            else:
                cursor.execute("SELECT * FROM car_service_workers WHERE role = %s ORDER BY created_at DESC", (role,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # ===== STATUS MANAGEMENT FUNCTIONS =====
    
    def set_online(self, worker_id: int) -> bool:
        """Set worker to ONLINE status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE car_service_workers 
                SET is_online = TRUE, is_busy = FALSE, last_status_update = %s, cooldown_until = NULL
                WHERE id = %s
            """, (datetime.now().isoformat(), worker_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def set_offline(self, worker_id: int) -> bool:
        """Set worker to OFFLINE status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE car_service_workers 
                SET is_online = FALSE, is_busy = FALSE, last_status_update = %s, cooldown_until = NULL
                WHERE id = %s
            """, (datetime.now().isoformat(), worker_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def set_busy(self, worker_id: int) -> bool:
        """Set worker to BUSY status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE car_service_workers 
                SET is_busy = TRUE, last_status_update = %s
                WHERE id = %s
            """, (datetime.now().isoformat(), worker_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def set_available(self, worker_id: int) -> bool:
        """Set worker to AVAILABLE (ONLINE but not BUSY)"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE car_service_workers 
                SET is_busy = FALSE, last_status_update = %s
                WHERE id = %s
            """, (datetime.now().isoformat(), worker_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_service_radius(self, worker_id: int, radius: int) -> bool:
        """Update worker service radius"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE car_service_workers SET service_radius = %s WHERE id = %s", (radius, worker_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_current_location(self, worker_id: int, city: str) -> bool:
        """Update worker current working city"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE car_service_workers SET current_city = %s WHERE id = %s", (city, worker_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_worker_status(self, worker_id: int) -> str:
        """Get worker's current status"""
        worker = self.get_worker_by_id(worker_id)
        if not worker:
            return "UNKNOWN"
        
        is_online = worker.get('is_online', False)
        is_busy = worker.get('is_busy', False)
        
        if not is_online:
            return "OFFLINE"
        elif is_busy:
            return "BUSY"
        else:
            return "ONLINE"
    
    def get_available_workers(self) -> List[Dict]:
        """Get all available workers (ONLINE and not BUSY)"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM car_service_workers 
                WHERE is_online = TRUE AND is_busy = FALSE AND status = 'APPROVED'
                ORDER BY created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def update_worker_profile(self, worker_id: int, data: Dict) -> bool:
        """Update worker profile information"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Fields that can be updated
            allowed_fields = [
                'name', 'phone', 'age', 'city', 'address', 
                'experience', 'skills', 'bio', 'specialization',
                'service_radius', 'profile_photo'
            ]
            
            update_fields = []
            params = []
            
            for field in allowed_fields:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    params.append(data[field])
            
            if not update_fields:
                return False
                
            query = f"UPDATE car_service_workers SET {', '.join(update_fields)} WHERE id = %s"
            params.append(worker_id)
            
            cursor.execute(query, tuple(params))
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
car_service_worker_db = CarServiceWorkerDB()
