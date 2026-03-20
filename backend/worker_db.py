"""
Worker/Doctor database for healthcare professionals.
"""
import sqlite3
import bcrypt
import re
from config import WORKER_DB, DATA_DIR
from pricing_config import get_worker_default_rate
import os

os.makedirs(DATA_DIR, exist_ok=True)


class WorkerDB:
    def __init__(self):
        self.conn = sqlite3.connect(WORKER_DB, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_table()

    def get_conn(self):
        return sqlite3.connect(WORKER_DB)

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                service TEXT DEFAULT 'healthcare',
                specialization TEXT,
                experience INTEGER DEFAULT 0,
                clinic_location TEXT,
                rating REAL DEFAULT 0,
                photo_url TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                license_number TEXT,
                password TEXT,
                wallet_balance REAL DEFAULT 0.0,
                aadhaar_number TEXT,
                id_proof_url TEXT,
                skills TEXT,
                portfolio_url TEXT,
                bio TEXT,
                hourly_rate REAL
            )
        """)
        # Migration: Add new columns if missing
        new_cols = [
            ("aadhaar_number", "TEXT"),
            ("id_proof_url", "TEXT"),
            ("skills", "TEXT"),
            ("portfolio_url", "TEXT"),
            ("bio", "TEXT"),
            ("hourly_rate", "REAL"),
            ("wallet_balance", "REAL DEFAULT 0.0")
        ]
        for col_name, col_type in new_cols:
            try:
                cursor.execute(f"ALTER TABLE workers ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass
            
        self.conn.commit()

    def _row_to_dict(self, row):
        if row is None:
            return None
        d = dict(row) if hasattr(row, "keys") else row
        if isinstance(d, dict):
            d["name"] = d.get("full_name") or d.get("name", "")
        return d

    def is_valid_email(self, email):
        # Basic regex for email validation
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

    def register_worker(self, full_name, email, phone, service, specialization, experience, clinic_location="", license_number=None, password=None, aadhaar=None, id_proof=None, skills=None, hourly_rate=None, bio=None):
        # Validate email format
        if not self.is_valid_email(email):
            print(f"❌ Registration failed: Invalid email format '{email}'")
            return None

        cursor = self.conn.cursor()
        
        # Check if worker already exists by email
        cursor.execute("SELECT id, service FROM workers WHERE email = ?", (email,))
        existing_worker = cursor.fetchone()
        
        if existing_worker:
            worker_id = existing_worker['id']
            existing_services = existing_worker['service'] or ""
            service_list = [s.strip() for s in existing_services.split(',') if s.strip()]
            
            if service not in service_list:
                # Add new service to the list
                service_list.append(service)
                new_service_str = ",".join(service_list)
                
                # Update worker with new service and potentially other new info
                update_fields = ["service = ?"]
                params = [new_service_str]
                
                # If they are adding freelance info, update those fields too
                if service == 'freelance':
                    if aadhaar: 
                        update_fields.append("aadhaar_number = ?")
                        params.append(aadhaar)
                    if skills:
                        update_fields.append("skills = ?")
                        params.append(skills)
                    if hourly_rate:
                        update_fields.append("hourly_rate = ?")
                        params.append(hourly_rate)
                    if bio:
                        update_fields.append("bio = ?")
                        params.append(bio)
                
                params.append(worker_id)
                cursor.execute(f"UPDATE workers SET {', '.join(update_fields)} WHERE id = ?", params)
                self.conn.commit()
                return worker_id
            else:
                # Already registered for this service
                return None

        hashed_pw = None
        # Use default hourly rate if not provided
        if hourly_rate is None:
            hourly_rate = get_worker_default_rate(service)
        
        if password:
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
            
        try:
            cursor.execute("""
                INSERT INTO workers (full_name, email, phone, service, specialization, experience, clinic_location, license_number, password, aadhaar_number, id_proof_url, skills, hourly_rate, bio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (full_name, email, phone, service, specialization, int(experience or 0), clinic_location or "", license_number, hashed_pw, aadhaar, id_proof, skills, hourly_rate, bio))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_worker_by_email(self, email):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM workers WHERE email = ?", (email,))
        row = cursor.fetchone()
        return self._row_to_dict(row)

    def verify_worker_login(self, email, password=None):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, status, service, specialization, full_name, password FROM workers WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        
        # Check password if provided and worker has a password set
        if password and row["password"]:
            try:
                if not bcrypt.checkpw(password.encode(), row["password"].encode()):
                    return None
            except:
                # If password verification fails, return None
                return None
        
        return (row["id"], row["status"], row["service"], row["specialization"] or "", row["full_name"])

    def get_all_specializations(self, service_type='healthcare'):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT specialization FROM workers WHERE specialization IS NOT NULL AND specialization != '' AND (',' || service || ',') LIKE ?", (f'%,{service_type},%',))
        return [r["specialization"] for r in cursor.fetchall()]

    def get_all_workers(self, service_type='healthcare'):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM workers WHERE status = 'approved' AND (',' || service || ',') LIKE ?", (f'%,{service_type},%',))
        return [self._row_to_dict(r) for r in cursor.fetchall()]

    def get_workers_by_specialization(self, specialization, service_type='healthcare'):
        cursor = self.conn.cursor()
        # Use LIKE for partial matching to support comma-separated specializations
        # Also check for exact match or if it's part of a list
        pattern = f"%{specialization}%"
        cursor.execute("""
            SELECT * FROM workers 
            WHERE status = 'approved' 
            AND (',' || service || ',') LIKE ? 
            AND (specialization LIKE ? OR specialization = ?)
        """, (f'%,{service_type},%', pattern, specialization))
        return [self._row_to_dict(r) for r in cursor.fetchall()]

    def search_workers(self, q, service_type='healthcare'):
        if not q or not str(q).strip():
            return self.get_all_workers(service_type)
        cursor = self.conn.cursor()
        pattern = f"%{q.strip()}%"
        cursor.execute("""
            SELECT * FROM workers WHERE status = 'approved' AND (',' || service || ',') LIKE ?
            AND (full_name LIKE ? OR specialization LIKE ? OR clinic_location LIKE ?)
        """, (f'%,{service_type},%', pattern, pattern, pattern))
        return [self._row_to_dict(r) for r in cursor.fetchall()]

    def get_pending_workers(self, service_type=None):
        cursor = self.conn.cursor()
        if service_type:
            cursor.execute("SELECT * FROM workers WHERE status = 'pending' AND (',' || service || ',') LIKE ?", (f'%,{service_type},%',))
        else:
            cursor.execute("SELECT * FROM workers WHERE status = 'pending'")
        rows = cursor.fetchall()
        if not rows:
            return []
        return [self._row_to_dict(r) for r in rows]

    def get_worker_by_id(self, worker_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM workers WHERE id = ?", (worker_id,))
        row = cursor.fetchone()
        return self._row_to_dict(row)

    def approve_worker(self, worker_id):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE workers SET status = 'approved' WHERE id = ?", (worker_id,))
        self.conn.commit()

    def reject_worker(self, worker_id):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE workers SET status = 'rejected' WHERE id = ?", (worker_id,))
        self.conn.commit()

    def update_wallet_balance(self, worker_id, amount):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE workers SET wallet_balance = wallet_balance + ? WHERE id = ?", (amount, worker_id))
        self.conn.commit()

    def get_workers_by_service(self, service_type):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM workers WHERE (',' || service || ',') LIKE ? AND status = 'approved'", (f'%,{service_type},%',))
        return [self._row_to_dict(r) for r in cursor.fetchall()]

    def update_worker_status(self, worker_id, status):
        """Update worker status (approved, rejected, pending)"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE workers SET status = ? WHERE id = ?", (status, worker_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_approved_workers(self, service_type=None):
        cursor = self.conn.cursor()
        if service_type:
            cursor.execute("SELECT * FROM workers WHERE status = 'approved' AND (',' || service || ',') LIKE ?", (f'%,{service_type},%',))
        else:
            cursor.execute("SELECT * FROM workers WHERE status = 'approved'")
        rows = cursor.fetchall()
        if not rows:
            return []
        return [self._row_to_dict(r) for r in rows]

    def get_rejected_workers(self, service_type=None):
        cursor = self.conn.cursor()
        if service_type:
            cursor.execute("SELECT * FROM workers WHERE status = 'rejected' AND (',' || service || ',') LIKE ?", (f'%,{service_type},%',))
        else:
            cursor.execute("SELECT * FROM workers WHERE status = 'rejected'")
        rows = cursor.fetchall()
        if not rows:
            return []
        return [self._row_to_dict(r) for r in rows]

    def get_all_workers_unfiltered(self):
        """Get all workers regardless of status or service type"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM workers")
        rows = cursor.fetchall()
        if not rows:
            return []
        return [self._row_to_dict(r) for r in rows]
