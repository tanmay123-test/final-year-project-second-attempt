import sqlite3
import os
from datetime import datetime


class AskExpertDB:
    def __init__(self, db_name="ask_expert.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)
        self._init_db()

    def get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self.get_conn()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS expert_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                is_approved INTEGER DEFAULT 0,
                online_status TEXT DEFAULT 'offline',
                is_busy INTEGER DEFAULT 0,
                last_assigned_at TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS expert_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                assigned_expert_id INTEGER,
                problem_description TEXT NOT NULL,
                category TEXT,
                location TEXT,
                status TEXT DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS expert_request_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_time TIMESTAMP,
                approved_by INTEGER,
                FOREIGN KEY (request_id) REFERENCES expert_requests (id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS expert_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                sender_type TEXT NOT NULL,
                sender_id INTEGER NOT NULL,
                message_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS expert_conversation_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                summary_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    # Expert profile operations
    def ensure_expert_profile(self, user_id):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id FROM expert_profiles WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO expert_profiles (user_id) VALUES (?)", (user_id,))
            conn.commit()
            row_id = cur.lastrowid
        else:
            row_id = row[0]
        conn.close()
        return row_id

    def set_online(self, user_id):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE expert_profiles SET online_status='online' WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()

    def set_offline(self, user_id):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE expert_profiles SET online_status='offline', is_busy=0 WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()

    def set_busy(self, expert_profile_id, busy=True):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE expert_profiles SET is_busy=? WHERE id=?", (1 if busy else 0, expert_profile_id))
        conn.commit()
        conn.close()

    def update_last_assigned(self, expert_profile_id):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE expert_profiles SET last_assigned_at=? WHERE id=?", (datetime.utcnow(), expert_profile_id))
        conn.commit()
        conn.close()

    def find_available_expert(self):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id FROM expert_profiles
            WHERE is_approved=1 AND online_status='online' AND is_busy=0
            ORDER BY COALESCE(last_assigned_at, '1970-01-01') ASC
            LIMIT 1
        """)
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None

    def get_expert_profile_by_user(self, user_id):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, is_approved, online_status, is_busy FROM expert_profiles WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return row

    # Request operations
    def create_request(self, user_id, description, category, location):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO expert_requests (user_id, problem_description, category, location, status)
            VALUES (?, ?, ?, ?, 'PENDING')
        """, (user_id, description, category, location))
        request_id = cur.lastrowid
        conn.commit()
        conn.close()
        return request_id

    def assign_request(self, request_id, expert_profile_id):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            UPDATE expert_requests
            SET assigned_expert_id=?, status='ASSIGNED'
            WHERE id=?
        """, (expert_profile_id, request_id))
        conn.commit()
        conn.close()

    def mark_in_progress(self, request_id):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE expert_requests SET status='IN_PROGRESS' WHERE id=?", (request_id,))
        conn.commit()
        conn.close()

    def mark_resolved(self, request_id):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE expert_requests SET status='RESOLVED', resolved_at=? WHERE id=?", (datetime.utcnow(), request_id))
        conn.commit()
        conn.close()

    def add_image_with_status(self, request_id: int, image_path: str, status: str = "pending"):
        """Add image with status tracking"""
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO expert_request_images (request_id, image_path, status)
            VALUES (?, ?, ?)
        """, (request_id, image_path, status))
        conn.commit()
        conn.close()

    def update_image_status(self, request_id: int, image_path: str, status: str, approved_by: int = None):
        """Update image status"""
        conn = self.get_conn()
        cur = conn.cursor()
        if status == "approved" and approved_by:
            cur.execute("""
                UPDATE expert_request_images 
                SET status = ?, approved_time = ?, approved_by = ?
                WHERE request_id = ? AND image_path = ?
            """, (status, datetime.utcnow(), approved_by, request_id, image_path))
        else:
            cur.execute("""
                UPDATE expert_request_images 
                SET status = ?
                WHERE request_id = ? AND image_path = ?
            """, (status, request_id, image_path))
        conn.commit()
        conn.close()

    def get_approved_images(self, request_id: int):
        """Get approved images for a request"""
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT image_path FROM expert_request_images 
            WHERE request_id = ? AND status = 'approved'
            ORDER BY upload_time ASC
        """, (request_id,))
        rows = cur.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def add_image(self, request_id: int, image_path: str):
        """Legacy method - redirects to add_image_with_status"""
        self.add_image_with_status(request_id, image_path, "pending")

    def add_message(self, request_id, sender_type, sender_id, message_text):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO expert_messages (request_id, sender_type, sender_id, message_text)
            VALUES (?, ?, ?, ?)
        """, (request_id, sender_type, sender_id, message_text))
        conn.commit()
        conn.close()

    def get_messages(self, request_id):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, sender_type, sender_id, message_text, created_at
            FROM expert_messages WHERE request_id=?
            ORDER BY created_at ASC
        """, (request_id,))
        rows = cur.fetchall()
        conn.close()
        return rows

    def get_user_requests(self, user_id):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, user_id, assigned_expert_id, problem_description, category, location, status, created_at, resolved_at
            FROM expert_requests WHERE user_id=?
            ORDER BY created_at DESC
        """, (user_id,))
        rows = cur.fetchall()
        conn.close()
        return rows

    def get_request(self, request_id):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, user_id, assigned_expert_id, problem_description, category, location, status, created_at, resolved_at
            FROM expert_requests WHERE id=?
        """, (request_id,))
        row = cur.fetchone()
        conn.close()
        return row

    def save_summary(self, request_id, summary_text):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO expert_conversation_summary (request_id, summary_text) VALUES (?, ?)", (request_id, summary_text))
        conn.commit()
        conn.close()

    def get_assigned_for_expert(self, expert_profile_id):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, user_id, problem_description, category, location, status, created_at
            FROM expert_requests
            WHERE assigned_expert_id=? AND status IN ('ASSIGNED','IN_PROGRESS')
            ORDER BY created_at ASC
            LIMIT 1
        """, (expert_profile_id,))
        row = cur.fetchone()
        conn.close()
        return row


# Singleton instance
ask_expert_db = AskExpertDB()
