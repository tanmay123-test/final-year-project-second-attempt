"""
Car Service Mechanic Database
Manages mechanic authentication and profiles
"""

import os
import sqlite3
import bcrypt
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Database path
MECHANICS_DB = os.path.join(os.path.dirname(__file__), 'mechanics.db')

class MechanicDB:
    def __init__(self):
        self.conn = sqlite3.connect(MECHANICS_DB, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_table()
    
    def get_conn(self):
        return sqlite3.connect(MECHANICS_DB, check_same_thread=False)
    
    def create_table(self):
        """Create mechanics table"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mechanics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                age INTEGER NOT NULL,
                city TEXT NOT NULL,
                experience INTEGER NOT NULL,
                skills TEXT NOT NULL,
                aadhaar_path TEXT,
                license_path TEXT,
                certificate_path TEXT,
                profile_photo_path TEXT,
                status TEXT NOT NULL DEFAULT 'APPROVED',
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
            cursor.execute("ALTER TABLE mechanics ADD COLUMN is_busy INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE mechanics ADD COLUMN service_radius INTEGER DEFAULT 10")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE mechanics ADD COLUMN current_city TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE mechanics ADD COLUMN last_status_update TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("ALTER TABLE mechanics ADD COLUMN cooldown_until TEXT")
        except sqlite3.OperationalError:
            pass
        
        self.conn.commit()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_mechanic(self, name: str, email: str, phone: str, password: str,
                       age: int, city: str, experience: int, skills: str,
                       aadhaar_path: str = None, license_path: str = None,
                       certificate_path: str = None, profile_photo_path: str = None) -> int:
        """Create a new mechanic"""
        cursor = self.conn.cursor()
        
        # Check if email already exists
        if self.get_mechanic_by_email(email):
            raise ValueError("Email already registered")
        
        # Hash password
        password_hash = self.hash_password(password)
        
        cursor.execute("""
            INSERT INTO mechanics 
            (name, email, phone, password_hash, age, city, experience, skills,
             aadhaar_path, license_path, certificate_path, profile_photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, password_hash, age, city, experience, skills,
              aadhaar_path, license_path, certificate_path, profile_photo_path))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_mechanic_by_email(self, email: str) -> Optional[Dict]:
        """Get mechanic by email"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM mechanics WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_mechanic_by_id(self, mechanic_id: int) -> Optional[Dict]:
        """Get mechanic by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM mechanics WHERE id = ?", (mechanic_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def verify_mechanic(self, email: str, password: str) -> Optional[Dict]:
        """Verify mechanic credentials"""
        mechanic = self.get_mechanic_by_email(email)
        if mechanic and self.verify_password(password, mechanic['password_hash']):
            return mechanic
        return None
    
    def set_online_status(self, mechanic_id: int, is_online: bool) -> bool:
        """Set mechanic online/offline status"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE mechanics SET is_online = ? WHERE id = ?", 
                      (1 if is_online else 0, mechanic_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_online_mechanics(self) -> List[Dict]:
        """Get all online mechanics"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM mechanics WHERE is_online = 1 AND status = 'APPROVED'")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_mechanics(self) -> List[Dict]:
        """Get all mechanics"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM mechanics ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def update_mechanic_status(self, mechanic_id: int) -> bool:
        """Update last status update timestamp"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE mechanics SET last_status_update = ? WHERE id = ?", 
                      (datetime.now().isoformat(), mechanic_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # ===== STATUS MANAGEMENT FUNCTIONS =====
    
    def set_online(self, mechanic_id: int) -> bool:
        """Set mechanic to ONLINE status"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE mechanics 
            SET is_online = 1, is_busy = 0, last_status_update = ?, cooldown_until = NULL
            WHERE id = ?
        """, (datetime.now().isoformat(), mechanic_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def set_offline(self, mechanic_id: int) -> bool:
        """Set mechanic to OFFLINE status"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE mechanics 
            SET is_online = 0, is_busy = 0, last_status_update = ?, cooldown_until = NULL
            WHERE id = ?
        """, (datetime.now().isoformat(), mechanic_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def set_busy(self, mechanic_id: int) -> bool:
        """Set mechanic to BUSY status"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE mechanics 
            SET is_busy = 1, last_status_update = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), mechanic_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def set_available(self, mechanic_id: int) -> bool:
        """Set mechanic to AVAILABLE (ONLINE but not BUSY)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE mechanics 
            SET is_busy = 0, last_status_update = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), mechanic_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def update_service_radius(self, mechanic_id: int, radius: int) -> bool:
        """Update mechanic service radius"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE mechanics SET service_radius = ? WHERE id = ?", (radius, mechanic_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def update_current_location(self, mechanic_id: int, city: str) -> bool:
        """Update mechanic current working city"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE mechanics SET current_city = ? WHERE id = ?", (city, mechanic_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_mechanic_status(self, mechanic_id: int) -> str:
        """Get mechanic's current status"""
        mechanic = self.get_mechanic_by_id(mechanic_id)
        if not mechanic:
            return "UNKNOWN"
        
        is_online = mechanic.get('is_online', 0)
        is_busy = mechanic.get('is_busy', 0)
        
        if not is_online:
            return "OFFLINE"
        elif is_busy:
            return "BUSY"
        else:
            return "ONLINE"
    
    def get_available_mechanics(self) -> List[Dict]:
        """Get all available mechanics (ONLINE and not BUSY)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM mechanics 
            WHERE is_online = 1 AND is_busy = 0 AND status = 'APPROVED'
            ORDER BY created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def set_cooldown(self, mechanic_id: int, cooldown_minutes: int = 30) -> bool:
        """Set mechanic cooldown (temporary unavailability)"""
        cursor = self.conn.cursor()
        cooldown_until = (datetime.now() + datetime.timedelta(minutes=cooldown_minutes)).isoformat()
        cursor.execute("""
            UPDATE mechanics 
            SET is_online = 0, cooldown_until = ?, last_status_update = ?
            WHERE id = ?
        """, (cooldown_until, datetime.now().isoformat(), mechanic_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
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
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE mechanics 
            SET cooldown_until = NULL, last_status_update = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), mechanic_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
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
        cursor = self.conn.cursor()
        cursor.execute("UPDATE mechanics SET status = ? WHERE id = ?", (status, mechanic_id))
        self.conn.commit()
        return cursor.rowcount > 0

# Global instance
mechanic_db = MechanicDB()
