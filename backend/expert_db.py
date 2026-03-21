"""
Expert database for managing various types of experts.
"""
import os
import psycopg2
import psycopg2.extras
import bcrypt
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class ExpertDB:
    def __init__(self):
        self.create_tables()

    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

    def create_tables(self):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Create experts table (extends workers table)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experts (
                    id SERIAL PRIMARY KEY,
                    worker_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    bio TEXT,
                    hourly_rate INTEGER DEFAULT 0,
                    availability_status TEXT DEFAULT 'offline',
                    last_active TIMESTAMP,
                    rating FLOAT DEFAULT 0,
                    total_jobs INTEGER DEFAULT 0,
                    is_online BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Create expert_requests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expert_requests (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    expert_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    image_url TEXT,
                    status TEXT DEFAULT 'pending',
                    priority TEXT DEFAULT 'normal',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create expert_sessions table for active sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expert_sessions (
                    id SERIAL PRIMARY KEY,
                    request_id INTEGER NOT NULL,
                    expert_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    session_type TEXT DEFAULT 'chat',
                    status TEXT DEFAULT 'active',
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP,
                    meeting_link TEXT
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

    def register_expert(self, worker_id, category, subcategory=None, bio="", hourly_rate=0):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO experts (worker_id, category, subcategory, bio, hourly_rate)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (worker_id, category, subcategory, bio, int(hourly_rate)))
            expert_id = cursor.fetchone()[0]
            conn.commit()
            return expert_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_expert_by_worker_id(self, worker_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT e.*, w.full_name, w.email, w.phone, w.photo_url, w.rating as worker_rating
                FROM experts e
                JOIN workers w ON e.worker_id = w.id
                WHERE e.worker_id = %s AND w.status = 'approved'
            """, (worker_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_online_experts(self, category=None):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if category:
                cursor.execute("""
                    SELECT e.*, w.full_name, w.email, w.phone, w.photo_url, w.rating as worker_rating
                    FROM experts e
                    JOIN workers w ON e.worker_id = w.id
                    WHERE e.is_online = TRUE AND w.status = 'approved' AND e.category = %s
                    ORDER BY e.last_active DESC
                """, (category,))
            else:
                cursor.execute("""
                    SELECT e.*, w.full_name, w.email, w.phone, w.photo_url, w.rating as worker_rating
                    FROM experts e
                    JOIN workers w ON e.worker_id = w.id
                    WHERE e.is_online = TRUE AND w.status = 'approved'
                    ORDER BY e.last_active DESC
                """)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_all_experts(self, category=None):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if category:
                cursor.execute("""
                    SELECT e.*, w.full_name, w.email, w.phone, w.photo_url, w.rating as worker_rating
                    FROM experts e
                    JOIN workers w ON e.worker_id = w.id
                    WHERE w.status = 'approved' AND e.category = %s
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
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def update_expert_status(self, expert_id, is_online):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE experts 
                SET is_online = %s, last_active = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (is_online, expert_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def create_expert_request(self, user_id, expert_id, category, title, description="", image_url=None, priority="normal"):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO expert_requests (user_id, expert_id, category, title, description, image_url, priority)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (user_id, expert_id, category, title, description, image_url, priority))
            request_id = cursor.fetchone()[0]
            conn.commit()
            return request_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_expert_requests(self, expert_id, status=None):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if status:
                cursor.execute("""
                    SELECT er.*, u.name as user_name, u.email as user_email
                    FROM expert_requests er
                    JOIN users u ON er.user_id = u.id
                    WHERE er.expert_id = %s AND er.status = %s
                    ORDER BY er.created_at DESC
                """, (expert_id, status))
            else:
                cursor.execute("""
                    SELECT er.*, u.name as user_name, u.email as user_email
                    FROM expert_requests er
                    JOIN users u ON er.user_id = u.id
                    WHERE er.expert_id = %s
                    ORDER BY er.created_at DESC
                """, (expert_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_user_requests(self, user_id, status=None):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if status:
                cursor.execute("""
                    SELECT er.*, e.worker_id, w.full_name as expert_name
                    FROM expert_requests er
                    JOIN experts e ON er.expert_id = e.id
                    JOIN workers w ON e.worker_id = w.id
                    WHERE er.user_id = %s AND er.status = %s
                    ORDER BY er.created_at DESC
                """, (user_id, status))
            else:
                cursor.execute("""
                    SELECT er.*, e.worker_id, w.full_name as expert_name
                    FROM expert_requests er
                    JOIN experts e ON er.expert_id = e.id
                    JOIN workers w ON e.worker_id = w.id
                    WHERE er.user_id = %s
                    ORDER BY er.created_at DESC
                """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def update_request_status(self, request_id, status):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE expert_requests 
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (status, request_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def create_session(self, request_id, expert_id, user_id, session_type="chat", meeting_link=None):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO expert_sessions (request_id, expert_id, user_id, session_type, meeting_link)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (request_id, expert_id, user_id, session_type, meeting_link))
            session_id = cursor.fetchone()[0]
            conn.commit()
            return session_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_active_sessions(self, expert_id=None, user_id=None):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if expert_id:
                cursor.execute("""
                    SELECT es.*, er.title, er.category
                    FROM expert_sessions es
                    JOIN expert_requests er ON es.request_id = er.id
                    WHERE es.expert_id = %s AND es.status = 'active'
                    ORDER BY es.started_at DESC
                """, (expert_id,))
            elif user_id:
                cursor.execute("""
                    SELECT es.*, er.title, er.category
                    FROM expert_sessions es
                    JOIN expert_requests er ON es.request_id = er.id
                    WHERE es.user_id = %s AND es.status = 'active'
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
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def end_session(self, session_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE expert_sessions 
                SET status = 'completed', ended_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (session_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_expert_categories(self):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT DISTINCT category FROM experts")
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def search_experts(self, query, category=None):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            pattern = f"%{query.strip()}%"
            if category:
                cursor.execute("""
                    SELECT e.*, w.full_name, w.email, w.phone, w.photo_url, w.rating as worker_rating
                    FROM experts e
                    JOIN workers w ON e.worker_id = w.id
                    WHERE w.status = 'approved' AND e.category = %s
                    AND (w.full_name LIKE %s OR e.subcategory LIKE %s OR e.bio LIKE %s)
                    ORDER BY e.rating DESC
                """, (category, pattern, pattern, pattern))
            else:
                cursor.execute("""
                    SELECT e.*, w.full_name, w.email, w.phone, w.photo_url, w.rating as worker_rating
                    FROM experts e
                    JOIN workers w ON e.worker_id = w.id
                    WHERE w.status = 'approved'
                    AND (w.full_name LIKE %s OR e.category LIKE %s OR e.subcategory LIKE %s OR e.bio LIKE %s)
                    ORDER BY e.rating DESC
                """, (pattern, pattern, pattern, pattern))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()


# Global instance
expert_db = ExpertDB()
