"""
Automobile Expert Database
Manages automobile expert authentication and profiles
"""

import os
import sqlite3
import bcrypt
from datetime import datetime
from typing import List, Dict, Optional

# Database path
AUTOMOBILE_EXPERTS_DB = os.path.join(os.path.dirname(__file__), 'automobile_experts.db')

class AutomobileExpertDB:
    def __init__(self):
        self.conn = sqlite3.connect(AUTOMOBILE_EXPERTS_DB, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_table()
    
    def get_conn(self):
        return sqlite3.connect(AUTOMOBILE_EXPERTS_DB, check_same_thread=False)
    
    def create_table(self):
        """Create automobile experts table"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS automobile_experts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                area_of_expertise TEXT NOT NULL,
                experience_years INTEGER NOT NULL,
                certificate_path TEXT,
                profile_photo_path TEXT,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def create_expert(self, name: str, phone: str, email: str, password: str, 
                    area_of_expertise: str, experience_years: int, 
                    certificate_path: str = None, profile_photo_path: str = None) -> int:
        """Create a new automobile expert"""
        cursor = self.conn.cursor()
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute("""
            INSERT INTO automobile_experts 
            (name, phone, email, password_hash, area_of_expertise, experience_years, 
             certificate_path, profile_photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, phone, email, password_hash, area_of_expertise, experience_years,
               certificate_path, profile_photo_path))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_expert_by_email(self, email: str) -> Optional[Dict]:
        """Get expert by email"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM automobile_experts WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_expert_by_id(self, expert_id: int) -> Optional[Dict]:
        """Get expert by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM automobile_experts WHERE id = ?", (expert_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def verify_password(self, email: str, password: str) -> Optional[Dict]:
        """Verify expert credentials"""
        expert = self.get_expert_by_email(email)
        if expert and bcrypt.checkpw(password.encode('utf-8'), expert['password_hash'].encode('utf-8')):
            return expert
        return None
    
    def update_expert_status(self, expert_id: int, status: str) -> bool:
        """Update expert status"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE automobile_experts 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (status, expert_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_all_experts(self) -> List[Dict]:
        """Get all experts"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM automobile_experts ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_experts_by_status(self, status: str) -> List[Dict]:
        """Get experts by status"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM automobile_experts WHERE status = ? ORDER BY created_at DESC", (status,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_expert_profile(self, expert_id: int, **kwargs) -> bool:
        """Update expert profile"""
        if not kwargs:
            return False
        
        cursor = self.conn.cursor()
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [expert_id]
        
        cursor.execute(f"""
            UPDATE automobile_experts 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, values)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_expert(self, expert_id: int) -> bool:
        """Delete expert"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM automobile_experts WHERE id = ?", (expert_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def search_experts(self, query: str) -> List[Dict]:
        """Search experts by name or expertise"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM automobile_experts 
            WHERE name LIKE ? OR area_of_expertise LIKE ?
            ORDER BY name
        """, (f"%{query}%", f"%{query}%"))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_expert_stats(self) -> Dict:
        """Get expert statistics"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_experts,
                SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved_experts,
                SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending_experts,
                SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected_experts
            FROM automobile_experts
        """)
        result = cursor.fetchone()
        return dict(result) if result else {}

# Create database instance
automobile_expert_db = AutomobileExpertDB()
