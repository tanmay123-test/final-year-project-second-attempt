"""
Worker/Doctor database for healthcare professionals.
"""
import os
import psycopg2
import psycopg2.extras
from psycopg2 import pool
import bcrypt
import re
from dotenv import load_dotenv

load_dotenv()

class WorkerDB:
    _pool = None

    def __init__(self):
        if WorkerDB._pool is None:
            try:
                # Use a pool to reuse database connections (MUCH faster)
                WorkerDB._pool = psycopg2.pool.SimpleConnectionPool(
                    1, 10, # min 1, max 10 connections
                    os.environ['DATABASE_URL'],
                    sslmode='require',
                    connect_timeout=10
                )
                print("  ✅ WorkerDB Connection Pool Initialized")
            except Exception as e:
                print(f"  ❌ FAILED to initialize DB Pool: {e}")
        self.create_table()

    def get_conn(self):
        if WorkerDB._pool:
            return WorkerDB._pool.getconn()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require', connect_timeout=10)

    def release_conn(self, conn):
        if WorkerDB._pool and conn:
            WorkerDB._pool.putconn(conn)
        elif conn:
            self.release_conn(conn)

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
            self.release_conn(conn)

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
        # Clean inputs
        full_name = str(full_name).strip() if full_name else ""
        email = str(email).strip() if email else ""
        phone = str(phone).strip() if phone else ""
        service = str(service).strip() if service else ""
        specialization = str(specialization).strip() if specialization else ""
        
        print(f"register_worker called for: email='{email}', service='{service}', specialization='{specialization}'")
        
        if not self.is_valid_email(email):
            return {"error": "Invalid email format"}

        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # Check if this email is already registered for ANY service
            cursor.execute("SELECT id, service, specialization FROM workers WHERE email = %s", (email,))
            existing_worker = cursor.fetchone()
            
            if existing_worker:
                worker_id = existing_worker['id']
                existing_services = (existing_worker['service'] or "").lower()
                existing_specialization = (existing_worker['specialization'] or "").lower()
                
                service_list = [s.strip() for s in existing_services.split(',') if s.strip()]
                spec_list = [s.strip() for s in existing_specialization.split(',') if s.strip()]
                
                new_service_needed = service.lower() not in service_list
                
                # Split incoming specializations
                incoming_specs = [s.strip().lower() for s in specialization.split(',') if s.strip()]
                new_specs_to_add = [s for s in incoming_specs if s not in spec_list]
                
                if new_service_needed or new_specs_to_add:
                    # Construct new strings while preserving original case from DB where possible
                    final_services = existing_worker['service'] or ""
                    if new_service_needed:
                        final_services = f"{final_services}, {service}" if final_services else service
                        
                    final_specialization = existing_worker['specialization'] or ""
                    if new_specs_to_add:
                        # Re-add only the new ones
                        added_specs_str = ", ".join([s.strip() for s in specialization.split(',') if s.strip().lower() in new_specs_to_add])
                        final_specialization = f"{final_specialization}, {added_specs_str}" if final_specialization else added_specs_str
                    
                    # Reset status to pending when a new service or specialization is added
                    print(f"  Updating existing worker {worker_id}: new_services='{final_services}', new_specialization='{final_specialization}'")
                    cursor.execute("UPDATE workers SET service = %s, specialization = %s, status = 'pending' WHERE id = %s", (final_services, final_specialization, worker_id))
                    conn.commit()
                    return {"worker_id": worker_id}
                
                return {"error": "Worker already exists with this service and specialization"}

            # New Worker Registration
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') if password else None
            
            # Use 0 if experience is not a number
            try:
                exp_years = int(experience) if experience and str(experience).strip() else 0
            except (ValueError, TypeError):
                exp_years = 0

            # Convert hourly_rate to float, use None if empty
            try:
                h_rate = float(hourly_rate) if hourly_rate and str(hourly_rate).strip() else None
            except (ValueError, TypeError):
                h_rate = None

            cursor.execute("""
                INSERT INTO workers (
                    full_name, email, phone, service, specialization, experience, 
                    clinic_location, license_number, password, aadhaar_number, 
                    skills, hourly_rate, bio, profile_photo_path, degree_certificate_path, 
                    medical_license_path, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                full_name, email, phone, service, specialization, exp_years, 
                clinic_location, license_number, hashed_password, aadhaar, 
                skills, h_rate, bio, profile_photo_path, degree_certificate_path, 
                medical_license_path, 'pending'
            ))
            worker_id = cursor.fetchone()['id']
            conn.commit()
            print(f"  Successfully registered new worker: {worker_id}")
            return {"worker_id": worker_id}

        except psycopg2.errors.UniqueViolation as e:
            conn.rollback()
            print(f"  Duplicate key violation for {email}: {e}")
            if 'email' in str(e):
                return {"error": "Email already registered"}
            return {"error": "Duplicate entry detected (Email or Phone)"}
        except Exception as e:
            conn.rollback()
            print(f"  CRITICAL Registration failed for {email}: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
        finally:
            cursor.close()
            self.release_conn(conn)

    def get_worker_by_email(self, email):
        if not email:
            return None
        email = str(email).strip().lower()
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM workers WHERE email = %s", (email,))
            row = cursor.fetchone()
            return self._row_to_dict(row)
        except Exception as e:
            print(f"  [DB ERROR] get_worker_by_email for {email}: {e}")
            return None
        finally:
            cursor.close()
            self.release_conn(conn)

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
            self.release_conn(conn)

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
            self.release_conn(conn)

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
            self.release_conn(conn)

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
            self.release_conn(conn)

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
            self.release_conn(conn)

    def get_pending_workers(self, service_type=None):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if service_type:
                cursor.execute("SELECT * FROM workers WHERE status = 'pending' AND service ILIKE %s", (f'%{service_type}%',))
            else:
                cursor.execute("SELECT * FROM workers WHERE status = 'pending'")
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            self.release_conn(conn)

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
            self.release_conn(conn)

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
            self.release_conn(conn)

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
            self.release_conn(conn)

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
            self.release_conn(conn)

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
            self.release_conn(conn)

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
            self.release_conn(conn)

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
            self.release_conn(conn)

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
            self.release_conn(conn)

    def get_workers_by_service(self, service_type):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            query = """
                SELECT * FROM workers 
                WHERE service = %s AND status = 'approved'
            """
            cursor.execute(query, (service_type,))
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            print(f"  DB Error: {e}")
            return []
        finally:
            cursor.close()
            self.release_conn(conn)

    def get_approved_workers(self, service_type=None):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if service_type:
                cursor.execute("SELECT * FROM workers WHERE status = 'approved' AND service ILIKE %s", (f'%{service_type}%',))
            else:
                cursor.execute("SELECT * FROM workers WHERE status = 'approved'")
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            self.release_conn(conn)

    def get_rejected_workers(self, service_type=None):
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if service_type:
                cursor.execute("SELECT * FROM workers WHERE status = 'rejected' AND service ILIKE %s", (f'%{service_type}%',))
            else:
                cursor.execute("SELECT * FROM workers WHERE status = 'rejected'")
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            self.release_conn(conn)

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
            self.release_conn(conn)

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
                query += " AND service ILIKE %s"
                params.append(f'%{service_type}%')
            
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"DB Error: {e}")
            return 0
        finally:
            cursor.close()
            self.release_conn(conn)
