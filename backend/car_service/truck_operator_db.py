"""
Truck Operator Database
Manages truck operator authentication and profiles
"""

import os
import psycopg2
import psycopg2.extras
import bcrypt
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Optional

load_dotenv()

class TruckOperatorDB:
    def __init__(self):
        self.create_table()
    
    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
    
    def create_table(self):
        """Create truck operators table"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS truck_operators (
                    id SERIAL PRIMARY KEY,
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
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def create_operator(self, name: str, phone: str, email: str, password: str, 
                       city_name: str, vehicle_type: str, vehicle_number: str,
                       vehicle_photo_path: str = None, rc_book_photo_path: str = None, 
                       petrol_pump_auth_letter_path: str = None) -> int:
        """Create a new truck operator"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO truck_operators 
                (name, phone, email, password_hash, city_name, vehicle_type, vehicle_number, 
                 vehicle_photo_path, rc_book_photo_path, petrol_pump_auth_letter_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (name, phone, email, password_hash, city_name, vehicle_type, vehicle_number,
                   vehicle_photo_path, rc_book_photo_path, petrol_pump_auth_letter_path))
            
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
    
    def get_operator_by_email(self, email: str) -> Optional[Dict]:
        """Get operator by email"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM truck_operators WHERE email = %s", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_operator_by_id(self, operator_id: int) -> Optional[Dict]:
        """Get operator by ID"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM truck_operators WHERE id = %s", (operator_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def verify_password(self, email: str, password: str) -> Optional[Dict]:
        """Verify operator credentials"""
        operator = self.get_operator_by_email(email)
        if operator and bcrypt.checkpw(password.encode('utf-8'), operator['password_hash'].encode('utf-8')):
            return operator
        return None
    
    def update_operator_status(self, operator_id: int, status: str) -> bool:
        """Update operator status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE truck_operators 
                SET status = %s, updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
            """, (status, operator_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_all_operators(self) -> List[Dict]:
        """Get all operators"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM truck_operators ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_operators_by_status(self, status: str) -> List[Dict]:
        """Get operators by status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM truck_operators WHERE status = %s ORDER BY created_at DESC", (status,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_operator_profile(self, operator_id: int, **kwargs) -> bool:
        """Update operator profile"""
        if not kwargs:
            return False
        
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values()) + [operator_id]
            
            cursor.execute(f"""
                UPDATE truck_operators 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
            """, values)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def delete_operator(self, operator_id: int) -> bool:
        """Delete operator"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM truck_operators WHERE id = %s", (operator_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def search_operators(self, query: str) -> List[Dict]:
        """Search operators by name or vehicle type"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM truck_operators 
                WHERE name LIKE %s OR vehicle_type LIKE %s OR city_name LIKE %s
                ORDER BY name
            """, (f"%{query}%", f"%{query}%", f"%{query}%"))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_operator_stats(self) -> Dict:
        """Get operator statistics"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
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
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

# Create database instance
truck_operator_db = TruckOperatorDB()
