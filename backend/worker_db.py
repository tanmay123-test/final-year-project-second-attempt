"""
Worker/Doctor database for healthcare professionals.
"""
import os
import sqlite3
import psycopg2
import psycopg2.extras
import bcrypt
import re
from dotenv import load_dotenv
from pricing_config import get_worker_default_rate

load_dotenv('.env.local')  # Load local config first
load_dotenv()  # Then load regular .env

class WorkerDB:
    def __init__(self):
        self.use_postgres = os.environ.get('DATABASE_URL') and not os.environ.get('USE_SQLITE', '').lower() == 'true'
        self.create_table()

    def get_conn(self):
        if self.use_postgres:
            try:
                return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='prefer')
            except Exception as e:
                print(f"PostgreSQL connection failed: {e}")
                print("Falling back to SQLite...")
                self.use_postgres = False
                return self.get_sqlite_conn()
        else:
            return self.get_sqlite_conn()

    def get_sqlite_conn(self):
        db_path = os.environ.get('DATABASE_PATH', './data')
        if not os.path.exists(db_path):
            os.makedirs(db_path, exist_ok=True)
        
        return sqlite3.connect(os.path.join(db_path, 'workers.db'))

    def create_table(self):
        if self.use_postgres:
            conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='prefer')
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS workers (
                        id SERIAL PRIMARY KEY,
                        full_name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        phone TEXT,
                        service TEXT,
                        specialization TEXT,
                        bio TEXT,
                        experience_years INTEGER,
                        education TEXT,
                        license_number TEXT,
                        address TEXT,
                        city TEXT,
                        state TEXT,
                        pincode TEXT,
                        pricing_model TEXT,
                        hourly_rate DECIMAL,
                        consultation_fee DECIMAL,
                        availability TEXT,
                        languages TEXT,
                        profile_image TEXT,
                        is_verified BOOLEAN DEFAULT FALSE,
                        rating DECIMAL DEFAULT 0.0,
                        total_reviews INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
            except Exception as e:
                print(f"PostgreSQL table creation failed: {e}")
                print("Falling back to SQLite...")
                self.use_postgres = False
                conn.close()
                self.create_sqlite_table()
                return
            finally:
                conn.close()
        else:
            self.create_sqlite_table()

    def create_sqlite_table(self):
        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                service TEXT,
                specialization TEXT,
                bio TEXT,
                experience_years INTEGER,
                education TEXT,
                license_number TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                pincode TEXT,
                pricing_model TEXT,
                hourly_rate REAL,
                consultation_fee REAL,
                availability TEXT,
                languages TEXT,
                profile_image TEXT,
                is_verified BOOLEAN DEFAULT 0,
                rating REAL DEFAULT 0.0,
                total_reviews INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _row_to_dict(self, row):
        if row is None:
            return None
        
        if self.use_postgres:
            # PostgreSQL returns dict-like rows
            d = dict(row)
        else:
            # SQLite returns tuples, need to get column names
            if hasattr(row, 'keys'):
                d = dict(zip(row.keys(), row))
            else:
                # Fallback for older SQLite versions
                columns = ['id', 'full_name', 'email', 'phone', 'service', 'specialization', 
                          'bio', 'experience_years', 'education', 'license_number', 'address',
                          'city', 'state', 'pincode', 'pricing_model', 'hourly_rate',
                          'consultation_fee', 'availability', 'languages', 'profile_image',
                          'is_verified', 'rating', 'total_reviews', 'status', 'created_at', 'updated_at']
                d = dict(zip(columns, row)) if len(row) == len(columns) else {}
        
        if isinstance(d, dict):
            d["name"] = d.get("full_name") or d.get("name", "")
        return d

    def is_valid_email(self, email):
        # Basic regex for email validation
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

    def register_worker(self, full_name, email, phone, service, specialization, experience, clinic_location="", license_number=None, password=None, aadhaar=None, id_proof=None, skills=None, hourly_rate=None, bio=None):
        # Validate email format
        if not self.is_valid_email(email):
            print(f"  Registration failed: Invalid email format '{email}'")
            return None

        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # Check if worker already exists by email
            cursor.execute("SELECT id, service FROM workers WHERE email = %s", (email,))
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
                    update_fields = ["service = %s"]
                    params = [new_service_str]
                    
                    # If they are adding freelance info, update those fields too
                    if service == 'freelance':
                        if aadhaar: 
                            update_fields.append("aadhaar_number = %s")
                            params.append(aadhaar)
                        if skills:
                            update_fields.append("skills = %s")
                            params.append(skills)
                        if hourly_rate:
                            update_fields.append("hourly_rate = %s")
                            params.append(hourly_rate)
                        if bio:
                            update_fields.append("bio = %s")
                            params.append(bio)
                    
                    params.append(worker_id)
                    cursor.execute(f"UPDATE workers SET {', '.join(update_fields)} WHERE id = %s", params)
                    conn.commit()
                    return worker_id
                else:
                    # Already registered for this service
                    return None

            hashed_pw = None
            # Use default hourly rate if not provided
            
            if password:
                hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
                
            # Auto-approve healthcare workers
            status = "approved" if service == "healthcare" else "pending"
            
            cursor.execute("""
                INSERT INTO workers (full_name, email, phone, service, specialization, experience, clinic_location, license_number, password, aadhaar_number, id_proof_url, skills, hourly_rate, bio, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (full_name, email, phone, service, specialization, int(experience or 0), clinic_location or "", license_number, hashed_pw, aadhaar, id_proof, skills, hourly_rate, bio, status))
            worker_id = cursor.fetchone()['id']
            conn.commit()
            return worker_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_worker_by_email(self, email):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM workers WHERE email = %s", (email,))
            row = cursor.fetchone()
            return self._row_to_dict(row)
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def verify_worker_login(self, email, password=None):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(
                "SELECT id, status, service, specialization, full_name, password FROM workers WHERE email = %s",
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
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_all_specializations(self, service_type='healthcare'):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT DISTINCT specialization FROM workers WHERE specialization IS NOT NULL AND specialization != '' AND CONCAT(',', service, ',') LIKE %s", (f'%,{service_type},%',))
            return [r["specialization"] for r in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_all_workers(self, service_type='healthcare'):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM workers WHERE status = 'approved' AND CONCAT(',', service, ',') LIKE %s", (f'%,{service_type},%',))
            return [self._row_to_dict(r) for r in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_workers_by_specialization(self, specialization, service_type='healthcare'):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Use LIKE for partial matching to support comma-separated specializations
            # Also check for exact match or if it's part of a list
            pattern = f"%{specialization}%"
            cursor.execute("""
                SELECT * FROM workers 
                WHERE status = 'approved' 
                AND CONCAT(',', service, ',') LIKE %s 
                AND (specialization LIKE %s OR specialization = %s)
            """, (f'%,{service_type},%', pattern, specialization))
            return [self._row_to_dict(r) for r in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def search_workers(self, q, service_type='healthcare'):
        if not q or not str(q).strip():
            return self.get_all_workers(service_type)
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            pattern = f"%{q.strip()}%"
            cursor.execute("""
                SELECT * FROM workers WHERE status = 'approved' AND CONCAT(',', service, ',') LIKE %s
                AND (full_name LIKE %s OR specialization LIKE %s OR clinic_location LIKE %s)
            """, (f'%,{service_type},%', pattern, pattern, pattern))
            return [self._row_to_dict(r) for r in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_pending_workers(self, service_type=None):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if service_type:
                cursor.execute("SELECT * FROM workers WHERE status = 'pending' AND service_type = %s", (service_type,))
            else:
                cursor.execute("SELECT * FROM workers WHERE status = 'pending'")
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_worker_by_id(self, worker_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM workers WHERE id = %s", (worker_id,))
            row = cursor.fetchone()
            return self._row_to_dict(row)
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def approve_worker(self, worker_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE workers SET status = 'approved' WHERE id = %s", (worker_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def reject_worker(self, worker_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE workers SET status = 'rejected' WHERE id = %s", (worker_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def update_wallet_balance(self, worker_id, amount):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE workers SET wallet_balance = wallet_balance + %s WHERE id = %s", (amount, worker_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_workers_by_service(self, service_type):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Broad search for housekeeping or cleaning services
            query = """
                SELECT * FROM workers 
                WHERE (service ILIKE %s OR specialization ILIKE %s OR service ILIKE %s OR specialization ILIKE %s)
            """
            pattern1 = f"%{service_type}%"
            pattern2 = "%cleaning%"
            cursor.execute(query, (pattern1, pattern1, pattern2, pattern2))
            rows = cursor.fetchall()
            workers = [self._row_to_dict(r) for r in rows]
            print(f"[DEBUG] get_workers_by_service('{service_type}'): Found {len(workers)} workers")
            return workers
        except Exception as e:
            conn.rollback()
            print(f"  DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def update_worker_status(self, worker_id, status):
        """Update worker status (approved, rejected, pending)"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE workers SET status = %s WHERE id = %s", (status, worker_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_approved_workers(self, service_type=None):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if service_type:
                cursor.execute("SELECT * FROM workers WHERE status = 'approved' AND CONCAT(',', service, ',') LIKE %s", (f'%,{service_type},%',))
            else:
                cursor.execute("SELECT * FROM workers WHERE status = 'approved'")
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_rejected_workers(self, service_type=None):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if service_type:
                cursor.execute("SELECT * FROM workers WHERE status = 'rejected' AND CONCAT(',', service, ',') LIKE %s", (f'%,{service_type},%',))
            else:
                cursor.execute("SELECT * FROM workers WHERE status = 'rejected'")
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_all_workers_unfiltered(self):
        """Get all workers regardless of status or service type"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM workers")
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
