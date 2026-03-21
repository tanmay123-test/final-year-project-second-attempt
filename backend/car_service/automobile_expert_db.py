"""
Automobile Expert Database
Manages automobile expert authentication and profiles
"""

import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
import bcrypt
from datetime import datetime
from typing import List, Dict, Optional

load_dotenv()

class AutomobileExpertDB:
    def __init__(self):
        self.create_table()
    
    def create_table(self):
        """Create automobile experts table"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS automobile_experts (
                    id SERIAL PRIMARY KEY,
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
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def create_expert(self, name: str, phone: str, email: str, password: str, 
                    area_of_expertise: str, experience_years: int, 
                    certificate_path: str = None, profile_photo_path: str = None) -> int:
        """Create a new automobile expert"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO automobile_experts 
                (name, phone, email, password_hash, area_of_expertise, experience_years, 
                 certificate_path, profile_photo_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (name, phone, email, password_hash, area_of_expertise, experience_years,
                   certificate_path, profile_photo_path))
            
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
    
    def get_expert_by_email(self, email: str) -> Optional[Dict]:
        """Get expert by email"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM automobile_experts WHERE email = %s", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_expert_by_id(self, expert_id: int) -> Optional[Dict]:
        """Get expert by ID"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM automobile_experts WHERE id = %s", (expert_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def verify_password(self, email: str, password: str) -> Optional[Dict]:
        """Verify expert credentials"""
        expert = self.get_expert_by_email(email)
        if expert and bcrypt.checkpw(password.encode('utf-8'), expert['password_hash'].encode('utf-8')):
            return expert
        return None
    
    def update_expert_status(self, expert_id: int, status: str) -> bool:
        """Update expert status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE automobile_experts 
                SET status = %s, updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
            """, (status, expert_id))
            success = cursor.rowcount > 0
            conn.commit()
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_all_experts(self) -> List[Dict]:
        """Get all experts"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM automobile_experts ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_experts_by_status(self, status: str) -> List[Dict]:
        """Get experts by status"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM automobile_experts WHERE status = %s ORDER BY created_at DESC", (status,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def update_expert_profile(self, expert_id: int, **kwargs) -> bool:
        """Update expert profile"""
        if not kwargs:
            return False
        
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values()) + [expert_id]
            
            cursor.execute(f"""
                UPDATE automobile_experts 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
            """, values)
            success = cursor.rowcount > 0
            conn.commit()
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def delete_expert(self, expert_id: int) -> bool:
        """Delete expert"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM automobile_experts WHERE id = %s", (expert_id,))
            success = cursor.rowcount > 0
            conn.commit()
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def search_experts(self, query: str) -> List[Dict]:
        """Search experts by name or expertise"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            pattern = f"%{query}%"
            cursor.execute("""
                SELECT * FROM automobile_experts 
                WHERE name LIKE %s OR area_of_expertise LIKE %s
                ORDER BY name
            """, (pattern, pattern))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_expert_stats(self) -> Dict:
        """Get expert statistics"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
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
        except Exception as e:
            print(f"DB Error: {e}")
            return {}
        finally:
            cursor.close()
            conn.close()

# Create database instance
automobile_expert_db = AutomobileExpertDB()
