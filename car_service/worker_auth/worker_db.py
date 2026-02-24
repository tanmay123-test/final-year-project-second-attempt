"""
Car Service Worker Authentication Database
Handles Mechanic, Fuel Agent, and Expert worker authentication
"""

import sqlite3
import os
import bcrypt
import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple

class CarWorkerDB:
    """Database operations for Car Service workers"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default path in car_service directory
            self.db_path = os.path.join(os.path.dirname(__file__), "car_worker_auth.db")
        else:
            self.db_path = db_path
        
        self.init_database()
    
    def get_conn(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with workers table"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        # Create workers table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                phone TEXT NOT NULL,
                worker_type TEXT NOT NULL CHECK (worker_type IN ('MECHANIC', 'FUEL_AGENT', 'EXPERT')),
                status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
                city TEXT NOT NULL,
                service_area TEXT NOT NULL,
                documents_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add indexes for performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_username ON workers(username)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_email ON workers(email)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_status ON workers(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_worker_type ON workers(worker_type)")
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def create_worker(self, worker_data: Dict, documents: Dict) -> int:
        """Create new worker with documents"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        try:
            # Hash password
            password_hash = self.hash_password(worker_data['password'])
            
            # Prepare documents JSON
            documents_json = json.dumps(documents) if documents else "{}"
            
            # Insert worker
            cur.execute("""
                INSERT INTO workers (
                    username, email, password_hash, phone, worker_type,
                    status, city, service_area, documents_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                worker_data['username'],
                worker_data['email'],
                password_hash,
                worker_data['phone'],
                worker_data['worker_type'],
                'PENDING',  # Always start as pending
                worker_data['city'],
                worker_data['service_area'],
                documents_json
            ))
            
            worker_id = cur.lastrowid
            conn.commit()
            return worker_id
            
        except sqlite3.IntegrityError as e:
            conn.rollback()
            if "username" in str(e):
                raise ValueError("Username already exists")
            elif "email" in str(e):
                raise ValueError("Email already exists")
            else:
                raise ValueError("Database constraint violation")
        finally:
            conn.close()
    
    def get_worker_by_username(self, username: str) -> Optional[Dict]:
        """Get worker by username"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM workers WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_worker_by_email(self, email: str) -> Optional[Dict]:
        """Get worker by email"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM workers WHERE email = ?", (email,))
        row = cur.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_worker_by_id(self, worker_id: int) -> Optional[Dict]:
        """Get worker by ID"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM workers WHERE id = ?", (worker_id,))
        row = cur.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def authenticate_worker(self, identifier: str, password: str) -> Optional[Dict]:
        """Authenticate worker with username or email and password"""
        # Try username first, then email
        worker = self.get_worker_by_username(identifier)
        if not worker:
            worker = self.get_worker_by_email(identifier)
        
        if not worker:
            return None
        
        if not self.verify_password(password, worker['password_hash']):
            return None
        
        # Check if worker is approved
        if worker['status'] != 'APPROVED':
            return None
        
        return worker
    
    def get_pending_workers(self) -> List[Dict]:
        """Get all pending workers for admin review"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, username, email, phone, worker_type, city, 
                   service_area, created_at, documents_json
            FROM workers 
            WHERE status = 'PENDING'
            ORDER BY created_at DESC
        """)
        
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def approve_worker(self, worker_id: int) -> bool:
        """Approve worker application"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                UPDATE workers 
                SET status = 'APPROVED', approved_at = ?, updated_at = ?
                WHERE id = ?
            """, (datetime.utcnow(), datetime.utcnow(), worker_id))
            
            success = cur.rowcount > 0
            conn.commit()
            return success
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def reject_worker(self, worker_id: int) -> bool:
        """Reject worker application"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                UPDATE workers 
                SET status = 'REJECTED', updated_at = ?
                WHERE id = ?
            """, (datetime.utcnow(), worker_id))
            
            success = cur.rowcount > 0
            conn.commit()
            return success
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_workers_by_type(self, worker_type: str) -> List[Dict]:
        """Get workers by type (only approved)"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, username, email, phone, city, service_area, created_at
            FROM workers 
            WHERE worker_type = ? AND status = 'APPROVED'
            ORDER BY username ASC
        """, (worker_type,))
        
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_worker_profile(self, worker_id: int, updates: Dict) -> bool:
        """Update worker profile"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        try:
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key in ['phone', 'city', 'service_area']:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            set_clauses.append("updated_at = ?")
            values.append(datetime.utcnow())
            values.append(worker_id)
            
            cur.execute(f"""
                UPDATE workers 
                SET {', '.join(set_clauses)}
                WHERE id = ?
            """, values)
            
            success = cur.rowcount > 0
            conn.commit()
            return success
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_worker_statistics(self) -> Dict:
        """Get worker statistics"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        # Total workers by status
        cur.execute("""
            SELECT status, COUNT(*) as count
            FROM workers
            GROUP BY status
        """)
        status_stats = {row['status']: row['count'] for row in cur.fetchall()}
        
        # Workers by type (approved only)
        cur.execute("""
            SELECT worker_type, COUNT(*) as count
            FROM workers
            WHERE status = 'APPROVED'
            GROUP BY worker_type
        """)
        type_stats = {row['worker_type']: row['count'] for row in cur.fetchall()}
        
        conn.close()
        
        return {
            'by_status': status_stats,
            'by_type': type_stats,
            'total_pending': status_stats.get('PENDING', 0),
            'total_approved': status_stats.get('APPROVED', 0),
            'total_rejected': status_stats.get('REJECTED', 0)
        }
    
    def delete_worker(self, worker_id: int) -> bool:
        """Delete worker account"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("DELETE FROM workers WHERE id = ?", (worker_id,))
            
            success = cur.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
        except Exception as e:
            print(f"Error deleting worker: {e}")
            return False
    
    def update_worker_status(self, worker_id: int, status_data: Dict) -> bool:
        """Update worker status (online_status, last_status_change, etc.)"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            # Build update query dynamically
            set_clauses = []
            values = []
            
            for key, value in status_data.items():
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            if set_clauses:
                query = f"UPDATE workers SET {', '.join(set_clauses)} WHERE id = ?"
                values.append(worker_id)
                
                cur.execute(query, values)
                conn.commit()
                success = cur.rowcount > 0
            else:
                success = False
            
            conn.close()
            return success
            
        except Exception as e:
            print(f"Error updating worker status: {e}")
            return False


# Global instance
car_worker_db = CarWorkerDB()
