import psycopg2
import psycopg2.extras
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

class UserDB:
    def __init__(self):
        # Initial table creation
        self.create_table()

    def create_table(self):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password BYTEA,
                is_verified INTEGER DEFAULT 0
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

    def user_exists(self, username, email):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM users WHERE username=%s OR email=%s",
                (username, email)
            )
            result = cursor.fetchone() is not None
            return result
        except Exception as e:
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def create_user(self, name, username, password, email):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            cursor.execute("""
            INSERT INTO users (name, username, email, password)
            VALUES (%s, %s, %s, %s) RETURNING id
            """, (name, username, email, hashed))
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

    def mark_verified(self, email):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE users SET is_verified=1 WHERE email=%s",
                (email,)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def verify_user(self, username, password):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT password, is_verified FROM users WHERE username=%s
            """, (username,))
            row = cursor.fetchone()

            if not row:
                return False, "User not found"

            hashed_pw, is_verified = row

            # Convert memoryview/bytes from BYTEA if necessary, bcrypt handles bytes
            if isinstance(hashed_pw, memoryview):
                hashed_pw = hashed_pw.tobytes()

            if not bcrypt.checkpw(password.encode(), hashed_pw):
                return False, "Invalid password"

            if not is_verified:
                return False, "Email not verified"

            return True, "Login successful"
        except Exception as e:
            print(f"DB Error: {e}")
            return False, str(e)
        finally:
            cursor.close()
            conn.close()

    def get_user_by_email(self, email):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(
                "SELECT id, email, is_verified FROM users WHERE email=%s",
                (email,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return dict(row)
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_user_by_username(self, username):
        """Get user ID by username for JWT authentication"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM users WHERE username=%s",
                (username,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return row[0]
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_user_by_id(self, user_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(
                "SELECT id, name, username, email, is_verified FROM users WHERE id=%s",
                (user_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return dict(row)
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
