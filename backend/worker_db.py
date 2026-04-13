"""
Worker/Doctor database for healthcare professionals.
"""
import os
import psycopg2
import psycopg2.extras
import bcrypt
import re
from dotenv import load_dotenv

load_dotenv()

class WorkerDB:
    def __init__(self):
        self.create_table()

    def get_conn(self):
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='prefer')

    def create_table(self):
        conn = self.get_conn()
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
                    experience INTEGER,
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
                    rejection_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    password TEXT,
                    clinic_location TEXT,
                    aadhaar_number TEXT,
                    id_proof_url TEXT,
                    skills TEXT,
                    profile_photo_path TEXT,
                    degree_certificate_path TEXT,
                    medical_license_path TEXT,
                    aadhaar_path TEXT,
                    police_verification_path TEXT,
                    portfolio_path TEXT,
                    skill_certificate_path TEXT
                )
            """)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"PostgreSQL table creation failed: {e}")
            raise
        finally:
            conn.close()

    def _row_to_dict(self, row):
        if row is None:
            return None
        d = dict(row)
        if isinstance(d, dict):
            d["name"] = d.get("full_name") or d.get("name", "")
        return d

    def is_valid_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

    def register_worker(self, full_name, email, phone, service, specialization, experience, clinic_location="", license_number=None, password=None, aadhaar=None, id_proof=None, skills=None, hourly_rate=None, bio=None, profile_photo_path=None, aadhaar_path=None, degree_certificate_path=None, medical_license_path=None, police_verification_path=None, portfolio_path=None, skill_certificate_path=None):
        print(f"register_worker called with: email={email}, service={service}")
        
        if not self.is_valid_email(email):
            print(f"  Registration failed: Invalid email format '{email}'")
            return None

        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # For freelancers, allow different emails to register for same service
            if service.lower() != 'freelancer':
                cursor.execute("SELECT id, service, specialization FROM workers WHERE email = %s", (email,))
                existing_worker = cursor.fetchone()
                
                if existing_worker:
                    worker_id = existing_worker['id']
                    existing_services = existing_worker['service'] or ""
                    existing_specialization = existing_worker['specialization'] or ""
                    service_list = [s.strip() for s in existing_services.split(',') if s.strip()]
                    
                    if service not in service_list:
                        new_services = f"{existing_services}, {service}" if existing_services else service
                        new_specialization = f"{existing_specialization}, {specialization}" if existing_specialization else specialization
                        cursor.execute("UPDATE workers SET service = %s, specialization = %s WHERE id = %s", (new_services, new_specialization, worker_id))
                        conn.commit()
                        return worker_id
                    return None

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') if password else None
            
            # Use 0 if experience is not a number
            try:
                exp_years = int(experience)
            except (ValueError, TypeError):
                exp_years = 0

            cursor.execute("""
                INSERT INTO workers (
                    full_name, email, phone, service, specialization, experience, 
                    clinic_location, license_number, password, aadhaar_number, 
                    skills, hourly_rate, bio, profile_photo_path, degree_certificate_path, 
                    medical_license_path
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                full_name, email, phone, service, specialization, exp_years, 
                clinic_location, license_number, hashed_password, aadhaar, 
                skills, hourly_rate, bio, profile_photo_path, degree_certificate_path, 
                medical_license_path
            ))
            worker_id = cursor.fetchone()['id']
            conn.commit()
            return worker_id
        except Exception as e:
            conn.rollback()
            print(f"Registration failed: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_worker_by_email(self, email):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM workers WHERE email = %s", (email,))
            row = cursor.fetchone()
            return self._row_to_dict(row)
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def verify_worker_login(self, email, password=None):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(
                "SELECT id, status, service, specialization, full_name, password FROM workers WHERE email = %s",
                (email,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            
            if password and row["password"]:
                try:
                    if not bcrypt.checkpw(password.encode(), row["password"].encode()):
                        return None
                except Exception:
                    return None
            elif password and not row["password"]:
                return None
            
            return (row["id"], row["status"], row["service"], row["specialization"] or "", row["full_name"])
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_all_specializations(self, service_type='healthcare'):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT DISTINCT specialization FROM workers WHERE specialization IS NOT NULL AND specialization != '' AND CONCAT(',', service, ',') LIKE %s", (f'%,{service_type},%',))
            return [r["specialization"] for r in cursor.fetchall()]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_all_workers(self, service_type='healthcare'):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM workers WHERE status = 'approved' AND CONCAT(',', service, ',') LIKE %s", (f'%,{service_type},%',))
            return [self._row_to_dict(r) for r in cursor.fetchall()]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_workers_by_specialization(self, specialization, service_type='healthcare'):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            pattern = f"%{specialization}%"
            cursor.execute("""
                SELECT * FROM workers 
                WHERE status = 'approved' 
                AND CONCAT(',', service, ',') LIKE %s 
                AND (specialization LIKE %s OR specialization = %s)
            """, (f'%,{service_type},%', pattern, specialization))
            return [self._row_to_dict(r) for r in cursor.fetchall()]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def search_workers(self, q, service_type='healthcare'):
        if not q or not str(q).strip():
            return self.get_all_workers(service_type)
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            pattern = f"%{q.strip()}%"
            cursor.execute("""
                SELECT * FROM workers WHERE status = 'approved' AND CONCAT(',', service, ',') LIKE %s
                AND (full_name LIKE %s OR specialization LIKE %s OR clinic_location LIKE %s)
            """, (f'%,{service_type},%', pattern, pattern, pattern))
            return [self._row_to_dict(r) for r in cursor.fetchall()]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_pending_workers(self, service_type=None):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if service_type:
                cursor.execute("SELECT * FROM workers WHERE status = 'pending' AND service LIKE %s", (f'%{service_type}%',))
            else:
                cursor.execute("SELECT * FROM workers WHERE status = 'pending'")
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_worker_by_id(self, worker_id):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM workers WHERE id = %s", (worker_id,))
            row = cursor.fetchone()
            return self._row_to_dict(row)
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_worker_consultation_fee(self, worker_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT consultation_fee FROM workers WHERE id = %s", (worker_id,))
            row = cursor.fetchone()
            return float(row[0]) if row and row[0] is not None else 500.0
        except Exception as e:
            print(f"DB Error: {e}")
            return 500.0
        finally:
            cursor.close()
            conn.close()

    def approve_worker(self, worker_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE workers SET status = 'approved' WHERE id = %s", (worker_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_worker_status(self, worker_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT status FROM workers WHERE id = %s", (worker_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(f"DB Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def update_worker_status(self, worker_id, status):
        conn = self.get_conn()
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

    def update_consultation_fee(self, worker_id, fee):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE workers SET consultation_fee = %s WHERE id = %s", (fee, worker_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_worker_profile(self, worker_id):
        worker = self.get_worker_by_id(worker_id)
        if worker:
            # Remove sensitive info
            worker.pop("password", None)
        return worker

    def reject_worker(self, worker_id, reason=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE workers SET status = 'rejected', rejection_reason = %s WHERE id = %s", (reason, worker_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def update_wallet_balance(self, worker_id, amount):
        conn = self.get_conn()
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
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            query = """
                SELECT * FROM workers 
                WHERE (service ILIKE %s OR specialization ILIKE %s OR service ILIKE %s OR specialization ILIKE %s)
            """
            pattern1 = f"%{service_type}%"
            pattern2 = "%cleaning%"
            cursor.execute(query, (pattern1, pattern1, pattern2, pattern2))
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            print(f"  DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_approved_workers(self, service_type=None):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if service_type:
                cursor.execute("SELECT * FROM workers WHERE status = 'approved' AND service LIKE %s", (f'%{service_type}%',))
            else:
                cursor.execute("SELECT * FROM workers WHERE status = 'approved'")
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_rejected_workers(self, service_type=None):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if service_type:
                cursor.execute("SELECT * FROM workers WHERE status = 'rejected' AND service LIKE %s", (f'%{service_type}%',))
            else:
                cursor.execute("SELECT * FROM workers WHERE status = 'rejected'")
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_all_workers_unfiltered(self):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM workers")
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_worker_count(self, status=None, service_type=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            query = "SELECT COUNT(*) FROM workers WHERE 1=1"
            params = []
            if status:
                query += " AND status = %s"
                params.append(status)
            if service_type:
                query += " AND service LIKE %s"
                params.append(f'%{service_type}%')
            
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"DB Error: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()
