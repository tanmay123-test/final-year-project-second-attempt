import psycopg2
import psycopg2.extras
import bcrypt
import os
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv

load_dotenv()

class AuthDB:
    def __init__(self):
        self.create_tables()
        self.SECRET_KEY = os.environ.get("JWT_SECRET", "your-secret-key-change-in-production")

    def create_tables(self):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password BYTEA,
                is_verified INTEGER DEFAULT 0,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Workers table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS workers (
                id SERIAL PRIMARY KEY,
                name TEXT,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password BYTEA,
                is_verified INTEGER DEFAULT 0,
                role TEXT DEFAULT 'worker',
                service_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    def create_user(self, name, username, password, email):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            cursor.execute("""
            INSERT INTO users (name, username, email, password, role)
            VALUES (%s, %s, %s, %s, 'user') RETURNING id
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

    def create_worker(self, name, username, password, email, service_type=None):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            cursor.execute("""
            INSERT INTO workers (name, username, email, password, service_type, role)
            VALUES (%s, %s, %s, %s, %s, 'worker') RETURNING id
            """, (name, username, email, hashed, service_type))
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

    def authenticate_user(self, username, password):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT id, password, is_verified, role FROM users WHERE username=%s
            """, (username,))
            row = cursor.fetchone()
            
            if not row:
                return None, "User not found"
            
            user_id, hashed_pw, is_verified, role = row
            
            if isinstance(hashed_pw, memoryview):
                hashed_pw = hashed_pw.tobytes()

            if not bcrypt.checkpw(password.encode(), hashed_pw):
                return None, "Invalid password"
            
            if not is_verified:
                return None, "Email not verified"
            
            return {"id": user_id, "username": username, "role": role}, "Login successful"
        except Exception as e:
            print(f"DB Error: {e}")
            return None, str(e)
        finally:
            cursor.close()
            conn.close()

    def authenticate_worker(self, username, password):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT id, password, is_verified, role, service_type FROM workers WHERE username=%s
            """, (username,))
            row = cursor.fetchone()
            
            if not row:
                return None, "Worker not found"
            
            worker_id, hashed_pw, is_verified, role, service_type = row
            
            if isinstance(hashed_pw, memoryview):
                hashed_pw = hashed_pw.tobytes()

            if not bcrypt.checkpw(password.encode(), hashed_pw):
                return None, "Invalid password"
            
            if not is_verified:
                return None, "Email not verified"
            
            return {"id": worker_id, "username": username, "role": role, "service_type": service_type}, "Login successful"
        except Exception as e:
            print(f"DB Error: {e}")
            return None, str(e)
        finally:
            cursor.close()
            conn.close()

    def generate_token(self, user_data):
        payload = {
            'user_id': user_data['id'],
            'username': user_data['username'],
            'role': user_data['role'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.SECRET_KEY, algorithm='HS256')

    def verify_token(self, token):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
