import sqlite3
import bcrypt
import os
from datetime import datetime, timedelta
import jwt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "expertease.db")

class AuthDB:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_tables()
        self.SECRET_KEY = "your-secret-key-change-in-production"

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password BLOB,
            is_verified INTEGER DEFAULT 0,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Workers table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password BLOB,
            is_verified INTEGER DEFAULT 0,
            role TEXT DEFAULT 'worker',
            service_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        self.conn.commit()

    def create_user(self, name, username, password, email):
        cursor = self.conn.cursor()
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        cursor.execute("""
        INSERT INTO users (name, username, email, password, role)
        VALUES (?, ?, ?, ?, 'user')
        """, (name, username, email, hashed))
        self.conn.commit()
        return cursor.lastrowid

    def create_worker(self, name, username, password, email, service_type=None):
        cursor = self.conn.cursor()
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        cursor.execute("""
        INSERT INTO workers (name, username, email, password, service_type, role)
        VALUES (?, ?, ?, ?, ?, 'worker')
        """, (name, username, email, hashed, service_type))
        self.conn.commit()
        return cursor.lastrowid

    def authenticate_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, password, is_verified, role FROM users WHERE username=?
        """, (username,))
        row = cursor.fetchone()
        
        if not row:
            return None, "User not found"
        
        user_id, hashed_pw, is_verified, role = row
        
        if not bcrypt.checkpw(password.encode(), hashed_pw):
            return None, "Invalid password"
        
        if not is_verified:
            return None, "Email not verified"
        
        return {"id": user_id, "username": username, "role": role}, "Login successful"

    def authenticate_worker(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, password, is_verified, role, service_type FROM workers WHERE username=?
        """, (username,))
        row = cursor.fetchone()
        
        if not row:
            return None, "Worker not found"
        
        worker_id, hashed_pw, is_verified, role, service_type = row
        
        if not bcrypt.checkpw(password.encode(), hashed_pw):
            return None, "Invalid password"
        
        if not is_verified:
            return None, "Email not verified"
        
        return {"id": worker_id, "username": username, "role": role, "service_type": service_type}, "Login successful"

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
