import sqlite3
import bcrypt
import os
from config import USER_DB
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "expertease.db")


class UserDB:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.conn = sqlite3.connect(USER_DB, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password BLOB,
            is_verified INTEGER DEFAULT 0
        )
        """)
        self.conn.commit()

    def user_exists(self, username, email):
        self.cursor.execute(
            "SELECT id FROM users WHERE username=? OR email=?",
            (username, email)
        )
        return self.cursor.fetchone() is not None

    def create_user(self, name, username, password, email):
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.cursor.execute("""
        INSERT INTO users (name, username, email, password)
        VALUES (?, ?, ?, ?)
        """, (name, username, email, hashed))
        self.conn.commit()

    def mark_verified(self, email):
        self.cursor.execute(
            "UPDATE users SET is_verified=1 WHERE email=?",
            (email,)
        )
        self.conn.commit()

    def verify_user(self, username, password):
        self.cursor.execute("""
        SELECT password, is_verified FROM users WHERE username=?
        """, (username,))
        row = self.cursor.fetchone()

        if not row:
            return False, "User not found"

        hashed_pw, is_verified = row

        if not bcrypt.checkpw(password.encode(), hashed_pw):
            return False, "Invalid password"

        if not is_verified:
            return False, "Email not verified"

        return True, "Login successful"

    # ✅ FIXED: NOW INSIDE THE CLASS
    def get_user_by_email(self, email):
        self.cursor.execute(
            "SELECT email, is_verified FROM users WHERE email=?",
            (email,)
        )
        row = self.cursor.fetchone()

        if not row:
            return None

        return {
            "email": row[0],
            "is_verified": bool(row[1])
        }

    def get_user_by_username(self, username):
        """Get user ID by username for JWT authentication"""
        self.cursor.execute(
            "SELECT id FROM users WHERE username=?",
            (username,)
        )
        row = self.cursor.fetchone()
        if not row:
            return None
        return row[0]  # Return user_id

    def get_user_by_id(self, user_id):
        """Get user information by user ID"""
        self.cursor.execute(
            "SELECT id, name, username, email, is_verified FROM users WHERE id=?",
            (user_id,)
        )
        row = self.cursor.fetchone()
        if not row:
            return None
        
        return {
            "id": row[0],
            "name": row[1],
            "username": row[2], 
            "email": row[3],
            "is_verified": bool(row[4])
        }