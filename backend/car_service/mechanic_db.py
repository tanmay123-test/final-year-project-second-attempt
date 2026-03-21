"""
Car Service Mechanic Database
Manages mechanic authentication and profiles
"""

import os
import psycopg2
import psycopg2.extras
import bcrypt
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Dict, Optional

load_dotenv()

class MechanicDB:
    def __init__(self):
        self.create_table()
    
    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
    
    def create_table(self):
        """Create mechanics table"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mechanics (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    city TEXT NOT NULL,
                    address TEXT,
                    experience INTEGER NOT NULL,
                    skills TEXT NOT NULL,
                    aadhaar_path TEXT,
                    license_path TEXT,
                    certificate_path TEXT,
                    profile_photo_path TEXT,
                    status TEXT NOT NULL DEFAULT 'APPROVED',
                    is_online BOOLEAN DEFAULT FALSE,
                    is_busy BOOLEAN DEFAULT FALSE,
                    service_radius INTEGER DEFAULT 10,
                    current_city TEXT,
                    role TEXT DEFAULT 'Mechanic',
                    last_status_update TEXT,
                    cooldown_until TEXT,
                    updated_at TIMESTAMP,
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
    
    def create_mechanic(self, name: str, email: str, phone: str, password: str,
                       age: int, city: str, address: str, experience: int, skills: str,
                       aadhaar_path: str = None, license_path: str = None,
                       certificate_path: str = None, profile_photo_path: str = None) -> int:
        """Create a new mechanic"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Check if email already exists
            if self.get_mechanic_by_email(email):
                raise ValueError("Email already registered")
            
            # Hash password
            password_hash = self.hash_password(password)
            
            cursor.execute("""
                INSERT INTO mechanics 
                (name, email, phone, password_hash, age, city, address, experience, skills,
                 aadhaar_path, license_path, certificate_path, profile_photo_path, status, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (name, email, phone, password_hash, age, city, address, experience, skills,
                  aadhaar_path, license_path, certificate_path, profile_photo_path, 'PENDING', 'Mechanic'))
            
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
    
    def get_mechanic_by_email(self, email: str) -> Optional[Dict]:
        """Get mechanic by email"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM mechanics WHERE email = %s", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_mechanic_by_id(self, mechanic_id: int) -> Optional[Dict]:
        """Get mechanic by ID"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM mechanics WHERE id = %s", (mechanic_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def verify_mechanic(self, email: str, password: str) -> Optional[Dict]:
        """Verify mechanic credentials"""
        mechanic = self.get_mechanic_by_email(email)
        if mechanic and self.verify_password(password, mechanic['password_hash']):
            return mechanic
        return None
    
    def set_online_status(self, mechanic_id: int, is_online: bool) -> bool:
        """Set mechanic online/offline status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE mechanics SET is_online = %s WHERE id = %s", 
                          (is_online, mechanic_id))
            conn.commit()
            return cursor.rowcount > 0
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
            cursor.execute("SELECT * FROM mechanics WHERE is_online = TRUE AND status = 'APPROVED'")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_all_mechanics(self) -> List[Dict]:
        """Get all mechanics"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM mechanics ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # ===== STATUS MANAGEMENT FUNCTIONS =====
    
    def set_online(self, mechanic_id: int) -> bool:
        """Set mechanic to ONLINE status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE mechanics 
                SET is_online = TRUE, is_busy = FALSE, last_status_update = %s, cooldown_until = NULL
                WHERE id = %s
            """, (datetime.now().isoformat(), mechanic_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def set_offline(self, mechanic_id: int) -> bool:
        """Set mechanic to OFFLINE status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE mechanics 
                SET is_online = FALSE, is_busy = FALSE, last_status_update = %s, cooldown_until = NULL
                WHERE id = %s
            """, (datetime.now().isoformat(), mechanic_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def set_busy(self, mechanic_id: int) -> bool:
        """Set mechanic to BUSY status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE mechanics 
                SET is_busy = TRUE, last_status_update = %s
                WHERE id = %s
            """, (datetime.now().isoformat(), mechanic_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def set_available(self, mechanic_id: int) -> bool:
        """Set mechanic to AVAILABLE (ONLINE but not BUSY)"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE mechanics 
                SET is_busy = FALSE, last_status_update = %s
                WHERE id = %s
            """, (datetime.now().isoformat(), mechanic_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_service_radius(self, mechanic_id: int, radius: int) -> bool:
        """Update mechanic service radius"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE mechanics SET service_radius = %s WHERE id = %s", (radius, mechanic_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_current_location(self, mechanic_id: int, city: str) -> bool:
        """Update mechanic current working city"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE mechanics SET current_city = %s WHERE id = %s", (city, mechanic_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_mechanic_status(self, mechanic_id: int) -> str:
        """Get mechanic's current status"""
        mechanic = self.get_mechanic_by_id(mechanic_id)
        if not mechanic:
            return "UNKNOWN"
        
        is_online = mechanic.get('is_online', False)
        is_busy = mechanic.get('is_busy', False)
        
        if not is_online:
            return "OFFLINE"
        elif is_busy:
            return "BUSY"
        else:
            return "ONLINE"
    
    def get_available_mechanics(self) -> List[Dict]:
        """Get all available mechanics (ONLINE and not BUSY)"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM mechanics 
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
    
    def set_cooldown(self, mechanic_id: int, cooldown_minutes: int = 30) -> bool:
        """Set mechanic cooldown (temporary unavailability)"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cooldown_until = (datetime.now() + timedelta(minutes=cooldown_minutes)).isoformat()
            cursor.execute("""
                UPDATE mechanics 
                SET is_online = FALSE, cooldown_until = %s, last_status_update = %s
                WHERE id = %s
            """, (cooldown_until, datetime.now().isoformat(), mechanic_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def is_on_cooldown(self, mechanic_id: int) -> bool:
        """Check if mechanic is on cooldown"""
        mechanic = self.get_mechanic_by_id(mechanic_id)
        if not mechanic:
            return False
        
        cooldown_until = mechanic.get('cooldown_until')
        if not cooldown_until:
            return False
        
        try:
            cooldown_time = datetime.fromisoformat(cooldown_until)
            return datetime.now() < cooldown_time
        except:
            return False
    
    def clear_cooldown(self, mechanic_id: int) -> bool:
        """Clear mechanic cooldown"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE mechanics 
                SET cooldown_until = NULL, last_status_update = %s
                WHERE id = %s
            """, (datetime.now().isoformat(), mechanic_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # ===== DEMAND HEAT INDICATOR =====
    
    def get_high_demand_areas(self) -> List[Dict]:
        """Get high demand areas (placeholder for now)"""
        # Placeholder implementation - later connect with real job data
        return [
            {"area": "Ghatkopar", "job_type": "Brake Repair", "count": 8},
            {"area": "Bandra", "job_type": "Engine Service", "count": 5},
            {"area": "Andheri", "job_type": "General Service", "count": 12}
        ]
    
    # ===== SMART ONLINE SUGGESTION =====
    
    def get_recommended_online_time(self) -> Dict:
        """Get recommended time to go online (placeholder)"""
        # Placeholder implementation - later analyze real job patterns
        return {
            "best_time_range": "9 AM - 12 PM",
            "peak_hours": ["10 AM", "11 AM", "2 PM", "3 PM"],
            "reason": "Highest job request volume during these hours"
        }
    
    def update_mechanic_status(self, mechanic_id: int, status: str) -> bool:
        """Update mechanic status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE mechanics SET status = %s WHERE id = %s", (status, mechanic_id))
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
mechanic_db = MechanicDB()
