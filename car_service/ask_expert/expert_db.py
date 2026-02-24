"""
Automobile Expert Database
Handles expert profiles, documents, requests, and consultations
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple

class ExpertDB:
    """Database operations for Automobile Experts"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default path in car_service directory
            self.db_path = os.path.join(os.path.dirname(__file__), "expert_system.db")
        else:
            self.db_path = db_path
        
        self.init_database()
    
    def get_conn(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize expert system tables"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        # 1. Expert Profiles Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expert_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                primary_expertise TEXT NOT NULL,
                years_of_experience INTEGER DEFAULT 0,
                work_type TEXT,
                consultation_hours TEXT,
                languages TEXT,
                approval_status TEXT DEFAULT 'PENDING',
                rating REAL DEFAULT 0.0,
                total_cases_handled INTEGER DEFAULT 0,
                trust_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES workers(id)
            )
        """)
        
        # 2. Expert Documents Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expert_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expert_id INTEGER NOT NULL,
                document_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verification_status TEXT DEFAULT 'PENDING',
                admin_remark TEXT,
                FOREIGN KEY (expert_id) REFERENCES expert_profiles(id)
            )
        """)
        
        # 3. Expert Requests Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expert_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                problem_description TEXT NOT NULL,
                category TEXT,
                user_city TEXT,
                assigned_expert_id INTEGER NULL,
                status TEXT DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_at TIMESTAMP NULL,
                accepted_at TIMESTAMP NULL,
                in_progress_at TIMESTAMP NULL,
                resolved_at TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (assigned_expert_id) REFERENCES expert_profiles(id)
            )
        """)
        
        # 4. Expert Conversations Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expert_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                expert_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                sender_type TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (request_id) REFERENCES expert_requests(id),
                FOREIGN KEY (expert_id) REFERENCES expert_profiles(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # 5. Expert Conversation Summaries Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expert_conversation_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                expert_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                summary TEXT NOT NULL,
                category TEXT,
                resolution_time INTEGER,
                difficulty_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES expert_conversations(id),
                FOREIGN KEY (expert_id) REFERENCES expert_profiles(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Indexes for performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_expert_approval ON expert_profiles(approval_status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_expert_requests_status ON expert_requests(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_expert_requests_assigned ON expert_requests(assigned_expert_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_conversation_request ON expert_conversations(request_id)")
        
        conn.commit()
        conn.close()
    
    # ==================== EXPERT PROFILE OPERATIONS ====================
    
    def create_expert_profile(self, user_id: int, profile_data: Dict) -> int:
        """Create new expert profile"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO expert_profiles 
                (user_id, primary_expertise, years_of_experience, work_type, 
                 consultation_hours, languages, approval_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                profile_data['primary_expertise'],
                profile_data.get('years_of_experience', 0),
                profile_data.get('work_type', ''),
                profile_data.get('consultation_hours', ''),
                profile_data.get('languages', ''),
                'PENDING'
            ))
            
            profile_id = cur.lastrowid
            conn.commit()
            conn.close()
            
            return profile_id
            
        except Exception as e:
            print(f"Error creating expert profile: {e}")
            return 0
    
    def get_expert_profile(self, user_id: int) -> Optional[Dict]:
        """Get expert profile by user ID"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT ep.*, w.username, w.email, w.worker_type, w.status as worker_status
            FROM expert_profiles ep
            JOIN workers w ON ep.user_id = w.id
            WHERE ep.user_id = ?
        """, (user_id,))
        
        result = cur.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def update_expert_approval(self, profile_id: int, status: str, remark: str = '') -> bool:
        """Update expert approval status"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            update_data = {'approval_status': status}
            if status == 'APPROVED':
                update_data['approved_at'] = datetime.now().isoformat()
            
            set_clauses = [f"{k} = ?" for k in update_data.keys()]
            values = list(update_data.values()) + [profile_id]
            
            cur.execute(f"""
                UPDATE expert_profiles 
                SET {', '.join(set_clauses)}
                WHERE id = ?
            """, values)
            
            success = cur.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            print(f"Error updating expert approval: {e}")
            return False
    
    # ==================== EXPERT DOCUMENT OPERATIONS ====================
    
    def upload_expert_document(self, expert_id: int, document_type: str, file_path: str) -> int:
        """Upload expert document"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO expert_documents 
                (expert_id, document_type, file_path, verification_status)
                VALUES (?, ?, ?, ?)
            """, (expert_id, document_type, file_path, 'PENDING'))
            
            doc_id = cur.lastrowid
            conn.commit()
            conn.close()
            
            return doc_id
            
        except Exception as e:
            print(f"Error uploading expert document: {e}")
            return 0
    
    def get_expert_documents(self, expert_id: int) -> List[Dict]:
        """Get all expert documents"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM expert_documents 
            WHERE expert_id = ? 
            ORDER BY uploaded_at DESC
        """, (expert_id,))
        
        results = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        return results
    
    def verify_expert_document(self, document_id: int, status: str, remark: str = '') -> bool:
        """Verify expert document"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE expert_documents 
                SET verification_status = ?, admin_remark = ?
                WHERE id = ?
            """, (status, remark, document_id))
            
            success = cur.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            print(f"Error verifying expert document: {e}")
            return False
    
    # ==================== EXPERT REQUEST OPERATIONS ====================
    
    def create_expert_request(self, user_id: int, request_data: Dict) -> int:
        """Create new expert request"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO expert_requests 
                (user_id, problem_description, category, user_city)
                VALUES (?, ?, ?, ?)
            """, (
                user_id,
                request_data['problem_description'],
                request_data.get('category', ''),
                request_data.get('user_city', '')
            ))
            
            request_id = cur.lastrowid
            conn.commit()
            conn.close()
            
            return request_id
            
        except Exception as e:
            print(f"Error creating expert request: {e}")
            return 0
    
    def assign_expert_to_request(self, request_id: int, expert_id: int) -> bool:
        """Assign expert to request"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE expert_requests 
                SET assigned_expert_id = ?, status = 'ASSIGNED', assigned_at = ?
                WHERE id = ?
            """, (expert_id, datetime.now().isoformat(), request_id))
            
            success = cur.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            print(f"Error assigning expert to request: {e}")
            return False
    
    def get_pending_requests(self, expert_id: int) -> List[Dict]:
        """Get pending requests for expert"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM expert_requests 
            WHERE assigned_expert_id = ? AND status = 'ASSIGNED'
            ORDER BY created_at DESC
        """, (expert_id,))
        
        results = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        return results
    
    # ==================== CONVERSATION OPERATIONS ====================
    
    def create_conversation_message(self, request_id: int, expert_id: int, user_id: int, 
                              message: str, sender_type: str, message_type: str = 'text', 
                              file_path: str = None) -> int:
        """Create conversation message"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO expert_conversations 
                (request_id, expert_id, user_id, message, sender_type, message_type, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (request_id, expert_id, user_id, message, sender_type, message_type, file_path))
            
            message_id = cur.lastrowid
            conn.commit()
            conn.close()
            
            return message_id
            
        except Exception as e:
            print(f"Error creating conversation message: {e}")
            return 0
    
    def get_conversation_messages(self, request_id: int) -> List[Dict]:
        """Get all messages in conversation"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM expert_conversations 
            WHERE request_id = ? 
            ORDER BY created_at ASC
        """, (request_id,))
        
        results = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        return results
    
    def update_request_status(self, request_id: int, status: str) -> bool:
        """Update request status"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            update_data = {'status': status}
            if status == 'IN_PROGRESS':
                update_data['in_progress_at'] = datetime.now().isoformat()
            elif status == 'RESOLVED':
                update_data['resolved_at'] = datetime.now().isoformat()
            
            set_clauses = [f"{k} = ?" for k in update_data.keys()]
            values = list(update_data.values()) + [request_id]
            
            cur.execute(f"""
                UPDATE expert_requests 
                SET {', '.join(set_clauses)}
                WHERE id = ?
            """, values)
            
            success = cur.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            print(f"Error updating request status: {e}")
            return False
    
    # ==================== ADMIN OPERATIONS ====================
    
    def get_pending_expert_applications(self) -> List[Dict]:
        """Get all pending expert applications"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT ep.*, w.username, w.email, w.phone
            FROM expert_profiles ep
            JOIN workers w ON ep.user_id = w.id
            WHERE ep.approval_status = 'PENDING'
            ORDER BY ep.created_at DESC
        """)
        
        results = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        return results
    
    def get_expert_statistics(self) -> Dict:
        """Get expert statistics"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        # Total experts by status
        cur.execute("""
            SELECT approval_status, COUNT(*) as count
            FROM expert_profiles
            GROUP BY approval_status
        """)
        status_stats = {row['approval_status']: row['count'] for row in cur.fetchall()}
        
        # Experts by expertise
        cur.execute("""
            SELECT primary_expertise, COUNT(*) as count
            FROM expert_profiles
            WHERE approval_status = 'APPROVED'
            GROUP BY primary_expertise
        """)
        expertise_stats = {row['primary_expertise']: row['count'] for row in cur.fetchall()}
        
        conn.close()
        
        return {
            'by_status': status_stats,
            'by_expertise': expertise_stats,
            'total_pending': status_stats.get('PENDING', 0),
            'total_approved': status_stats.get('APPROVED', 0),
            'total_rejected': status_stats.get('REJECTED', 0)
        }


# Global instance
expert_db = ExpertDB()
