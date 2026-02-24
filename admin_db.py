"""
Admin Database Module
Handles admin authentication and management
"""
import sqlite3
import bcrypt
import os
from datetime import datetime
from config import DATA_DIR

# Ensure admin database directory exists
os.makedirs(DATA_DIR, exist_ok=True)

ADMIN_DB = os.path.join(DATA_DIR, "admin.db")

class AdminDB:
    def __init__(self):
        self.conn = sqlite3.connect(ADMIN_DB, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_table()
        self.create_default_admin()

    def get_conn(self):
        return sqlite3.connect(ADMIN_DB)

    def create_table(self):
        """Create admins table"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                full_name TEXT,
                role TEXT DEFAULT 'admin',
                is_active BOOLEAN DEFAULT 1,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def create_admin(self, username, password, email=None, full_name=None, role='admin'):
        """Create new admin user"""
        cursor = self.conn.cursor()
        password_hash = self.hash_password(password)
        
        try:
            cursor.execute("""
                INSERT INTO admins (username, password_hash, email, full_name, role)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password_hash, email, full_name, role))
            
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None  # Username already exists

    def get_admin_by_username(self, username):
        """Get admin by username"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, username, password_hash, email, full_name, role, is_active, last_login, created_at
            FROM admins WHERE username = ?
        """, (username,))
        
        result = cursor.fetchone()
        if result:
            return dict(result)
        return None

    def update_last_login(self, admin_id):
        """Update last login timestamp"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE admins SET last_login = ? WHERE id = ?
        """, (datetime.now(), admin_id))
        self.conn.commit()

    def get_all_admins(self):
        """Get all admins (for super admin management)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, username, email, full_name, role, is_active, last_login, created_at
            FROM admins ORDER BY created_at DESC
        """)
        
        return [dict(row) for row in cursor.fetchall()]

    def deactivate_admin(self, admin_id):
        """Deactivate admin account"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE admins SET is_active = 0 WHERE id = ?", (admin_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def create_default_admin(self):
        """Create default super admin if not exists"""
        if not self.get_admin_by_username('superadmin'):
            admin_id = self.create_admin(
                username='superadmin',
                password='admin123',
                email='admin@expertease.com',
                full_name='Super Administrator',
                role='superadmin'
            )
            if admin_id:
                print(f"✅ Default super admin created (ID: {admin_id})")
            else:
                print("❌ Failed to create default admin")
        else:
            print("✅ Default super admin already exists")

# Singleton instance
admin_db = AdminDB()
