"""
Expert database for managing various types of experts.
"""
import sqlite3
import bcrypt
from config import WORKER_DB, DATA_DIR
import os
from datetime import datetime

os.makedirs(DATA_DIR, exist_ok=True)


class ExpertDB:
    def __init__(self):
        self.conn = sqlite3.connect(WORKER_DB, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def get_conn(self):
        return sqlite3.connect(WORKER_DB)

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Create experts table (extends workers table)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                bio TEXT,
                hourly_rate INTEGER DEFAULT 0,
                availability_status TEXT DEFAULT 'offline',
                last_active TIMESTAMP,
                rating REAL DEFAULT 0,
                total_jobs INTEGER DEFAULT 0,
                is_online BOOLEAN DEFAULT 0,
                FOREIGN KEY (worker_id) REFERENCES workers (id)
            )
        """)
        
        # Create expert_requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expert_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                expert_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                image_url TEXT,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'normal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (expert_id) REFERENCES experts (id)
            )
        """)
        
        # Create expert_sessions table for active sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expert_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                expert_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                session_type TEXT DEFAULT 'chat',
                status TEXT DEFAULT 'active',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                meeting_link TEXT,
                FOREIGN KEY (request_id) REFERENCES expert_requests (id),
                FOREIGN KEY (expert_id) REFERENCES experts (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        self.conn.commit()

    def register_expert(self, worker_id, category, subcategory=None, bio="", hourly_rate=0):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO experts (worker_id, category, subcategory, bio, hourly_rate)
                VALUES (?, ?, ?, ?, ?)
            """, (worker_id, category, subcategory, bio, int(hourly_rate)))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_expert_by_worker_id(self, worker_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT e.*, w.full_name, w.email, w.phone, w.photo_url, w.rating as worker_rating
            FROM experts e
            JOIN workers w ON e.worker_id = w.id
            WHERE e.worker_id = ? AND w.status = 'approved'
        """, (worker_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_online_experts(self, category=None):
        cursor = self.conn.cursor()
        if category:
            cursor.execute("""
                SELECT e.*, w.full_name, w.email, w.phone, w.photo_url, w.rating as worker_rating
                FROM experts e
                JOIN workers w ON e.worker_id = w.id
                WHERE e.is_online = 1 AND w.status = 'approved' AND e.category = ?
                ORDER BY e.last_active DESC
            """, (category,))
        else:
            cursor.execute("""
                SELECT e.*, w.full_name, w.email, w.phone, w.photo_url, w.rating as worker_rating
                FROM experts e
                JOIN workers w ON e.worker_id = w.id
                WHERE e.is_online = 1 AND w.status = 'approved'
                ORDER BY e.last_active DESC
            """)
        return [dict(row) for row in cursor.fetchall()]

    def get_all_experts(self, category=None):
        cursor = self.conn.cursor()
        if category:
            cursor.execute("""
                SELECT e.*, w.full_name, w.email, w.phone, w.photo_url, w.rating as worker_rating
                FROM experts e
                JOIN workers w ON e.worker_id = w.id
                WHERE w.status = 'approved' AND e.category = ?
                ORDER BY e.rating DESC, e.total_jobs DESC
            """, (category,))
        else:
            cursor.execute("""
                SELECT e.*, w.full_name, w.email, w.phone, w.photo_url, w.rating as worker_rating
                FROM experts e
                JOIN workers w ON e.worker_id = w.id
                WHERE w.status = 'approved'
                ORDER BY e.rating DESC, e.total_jobs DESC
            """)
        return [dict(row) for row in cursor.fetchall()]

    def update_expert_status(self, expert_id, is_online):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE experts 
            SET is_online = ?, last_active = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (is_online, expert_id))
        self.conn.commit()

    def create_expert_request(self, user_id, expert_id, category, title, description="", image_url=None, priority="normal"):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO expert_requests (user_id, expert_id, category, title, description, image_url, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, expert_id, category, title, description, image_url, priority))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_expert_requests(self, expert_id, status=None):
        cursor = self.conn.cursor()
        if status:
            cursor.execute("""
                SELECT er.*, u.name as user_name, u.email as user_email
                FROM expert_requests er
                JOIN users u ON er.user_id = u.id
                WHERE er.expert_id = ? AND er.status = ?
                ORDER BY er.created_at DESC
            """, (expert_id, status))
        else:
            cursor.execute("""
                SELECT er.*, u.name as user_name, u.email as user_email
                FROM expert_requests er
                JOIN users u ON er.user_id = u.id
                WHERE er.expert_id = ?
                ORDER BY er.created_at DESC
            """, (expert_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_user_requests(self, user_id, status=None):
        cursor = self.conn.cursor()
        if status:
            cursor.execute("""
                SELECT er.*, e.worker_id, w.full_name as expert_name
                FROM expert_requests er
                JOIN experts e ON er.expert_id = e.id
                JOIN workers w ON e.worker_id = w.id
                WHERE er.user_id = ? AND er.status = ?
                ORDER BY er.created_at DESC
            """, (user_id, status))
        else:
            cursor.execute("""
                SELECT er.*, e.worker_id, w.full_name as expert_name
                FROM expert_requests er
                JOIN experts e ON er.expert_id = e.id
                JOIN workers w ON e.worker_id = w.id
                WHERE er.user_id = ?
                ORDER BY er.created_at DESC
            """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]

    def update_request_status(self, request_id, status):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE expert_requests 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, request_id))
        self.conn.commit()

    def create_session(self, request_id, expert_id, user_id, session_type="chat", meeting_link=None):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO expert_sessions (request_id, expert_id, user_id, session_type, meeting_link)
            VALUES (?, ?, ?, ?, ?)
        """, (request_id, expert_id, user_id, session_type, meeting_link))
        self.conn.commit()
        return cursor.lastrowid

    def get_active_sessions(self, expert_id=None, user_id=None):
        cursor = self.conn.cursor()
        if expert_id:
            cursor.execute("""
                SELECT es.*, er.title, er.category
                FROM expert_sessions es
                JOIN expert_requests er ON es.request_id = er.id
                WHERE es.expert_id = ? AND es.status = 'active'
                ORDER BY es.started_at DESC
            """, (expert_id,))
        elif user_id:
            cursor.execute("""
                SELECT es.*, er.title, er.category
                FROM expert_sessions es
                JOIN expert_requests er ON es.request_id = er.id
                WHERE es.user_id = ? AND es.status = 'active'
                ORDER BY es.started_at DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT es.*, er.title, er.category
                FROM expert_sessions es
                JOIN expert_requests er ON es.request_id = er.id
                WHERE es.status = 'active'
                ORDER BY es.started_at DESC
            """)
        return [dict(row) for row in cursor.fetchall()]

    def end_session(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE expert_sessions 
            SET status = 'completed', ended_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (session_id,))
        self.conn.commit()

    def get_expert_categories(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM experts")
        return [row["category"] for row in cursor.fetchall()]

    def search_experts(self, query, category=None):
        cursor = self.conn.cursor()
        pattern = f"%{query.strip()}%"
        if category:
            cursor.execute("""
                SELECT e.*, w.full_name, w.email, w.phone, w.photo_url, w.rating as worker_rating
                FROM experts e
                JOIN workers w ON e.worker_id = w.id
                WHERE w.status = 'approved' AND e.category = ?
                AND (w.full_name LIKE ? OR e.subcategory LIKE ? OR e.bio LIKE ?)
                ORDER BY e.rating DESC
            """, (category, pattern, pattern, pattern))
        else:
            cursor.execute("""
                SELECT e.*, w.full_name, w.email, w.phone, w.photo_url, w.rating as worker_rating
                FROM experts e
                JOIN workers w ON e.worker_id = w.id
                WHERE w.status = 'approved'
                AND (w.full_name LIKE ? OR e.category LIKE ? OR e.subcategory LIKE ? OR e.bio LIKE ?)
                ORDER BY e.rating DESC
            """, (pattern, pattern, pattern, pattern))
        return [dict(row) for row in cursor.fetchall()]


# Global instance
expert_db = ExpertDB()
