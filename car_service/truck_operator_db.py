"""
Truck Operator Database
Manages truck operator authentication and profiles
"""

import os
import sqlite3
import bcrypt
from datetime import datetime
from typing import List, Dict, Optional

# Database path
TRUCK_OPERATORS_DB = os.path.join(os.path.dirname(__file__), 'truck_operators.db')

class TruckOperatorDB:
    def __init__(self):
        self.conn = sqlite3.connect(TRUCK_OPERATORS_DB, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_table()
    
    def get_conn(self):
        return sqlite3.connect(TRUCK_OPERATORS_DB, check_same_thread=False)
    
    def create_table(self):
        """Create truck operators table"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS truck_operators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                city_name TEXT NOT NULL,
                vehicle_type TEXT NOT NULL,
                vehicle_number TEXT NOT NULL,
                vehicle_photo_path TEXT,
                rc_book_photo_path TEXT,
                petrol_pump_auth_letter_path TEXT,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def create_operator(self, name: str, phone: str, email: str, password: str, 
                       city_name: str, vehicle_type: str, vehicle_number: str,
                       vehicle_photo_path: str = None, rc_book_photo_path: str = None, 
                       petrol_pump_auth_letter_path: str = None) -> int:
        """Create a new truck operator"""
        cursor = self.conn.cursor()
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute("""
            INSERT INTO truck_operators 
            (name, phone, email, password_hash, city_name, vehicle_type, vehicle_number, 
             vehicle_photo_path, rc_book_photo_path, petrol_pump_auth_letter_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, phone, email, password_hash, city_name, vehicle_type, vehicle_number,
               vehicle_photo_path, rc_book_photo_path, petrol_pump_auth_letter_path))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_operator_by_email(self, email: str) -> Optional[Dict]:
        """Get operator by email"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM truck_operators WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_operator_by_id(self, operator_id: int) -> Optional[Dict]:
        """Get operator by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM truck_operators WHERE id = ?", (operator_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def verify_password(self, email: str, password: str) -> Optional[Dict]:
        """Verify operator credentials"""
        operator = self.get_operator_by_email(email)
        if operator and bcrypt.checkpw(password.encode('utf-8'), operator['password_hash'].encode('utf-8')):
            return operator
        return None
    
    def update_operator_status(self, operator_id: int, status: str) -> bool:
        """Update operator status"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE truck_operators 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (status, operator_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_all_operators(self) -> List[Dict]:
        """Get all operators"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM truck_operators ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_operators_by_status(self, status: str) -> List[Dict]:
        """Get operators by status"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM truck_operators WHERE status = ? ORDER BY created_at DESC", (status,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_operator_profile(self, operator_id: int, **kwargs) -> bool:
        """Update operator profile"""
        if not kwargs:
            return False
        
        cursor = self.conn.cursor()
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [operator_id]
        
        cursor.execute(f"""
            UPDATE truck_operators 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, values)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_operator(self, operator_id: int) -> bool:
        """Delete operator"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM truck_operators WHERE id = ?", (operator_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def search_operators(self, query: str) -> List[Dict]:
        """Search operators by name or vehicle type"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM truck_operators 
            WHERE name LIKE ? OR vehicle_type LIKE ? OR city_name LIKE ?
            ORDER BY name
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_operator_stats(self) -> Dict:
        """Get operator statistics"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_operators,
                SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved_operators,
                SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending_operators,
                SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected_operators
            FROM truck_operators
        """)
        result = cursor.fetchone()
        return dict(result) if result else {}

# Create database instance
truck_operator_db = TruckOperatorDB()
