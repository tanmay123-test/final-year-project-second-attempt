"""
Car Service Job Requests Database
Manages job requests queue for mechanics
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random

load_dotenv()

class JobRequestsDB:
    def __init__(self):
        self.create_table()
    
    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
    
    def create_table(self):
        """Create job requests and active jobs tables"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_requests (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    mechanic_id INTEGER NOT NULL,
                    user_name TEXT NOT NULL,
                    car_model TEXT NOT NULL,
                    issue TEXT NOT NULL,
                    issue_type TEXT NOT NULL,
                    user_city TEXT NOT NULL,
                    distance_km FLOAT,
                    eta_minutes INTEGER,
                    estimated_earning FLOAT,
                    priority TEXT NOT NULL DEFAULT 'NORMAL',
                    status TEXT NOT NULL DEFAULT 'SEARCHING',
                    assignment_reason TEXT,
                    response_deadline TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create active jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS active_jobs (
                    id SERIAL PRIMARY KEY,
                    job_request_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    mechanic_id INTEGER NOT NULL,
                    user_name TEXT NOT NULL,
                    user_phone TEXT,
                    user_lat FLOAT,
                    user_long FLOAT,
                    mechanic_lat FLOAT,
                    mechanic_long FLOAT,
                    status TEXT NOT NULL DEFAULT 'ARRIVING',
                    otp TEXT,
                    before_photo TEXT,
                    after_photo TEXT,
                    start_time TEXT,
                    arrival_time TEXT,
                    completion_time TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_request_id) REFERENCES job_requests (id)
                )
            """)
            
            # Create mechanic earnings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mechanic_earnings (
                    id SERIAL PRIMARY KEY,
                    mechanic_id INTEGER NOT NULL,
                    job_id INTEGER NOT NULL,
                    base_amount FLOAT NOT NULL,
                    platform_commission FLOAT NOT NULL,
                    mechanic_earning FLOAT NOT NULL,
                    bonus FLOAT DEFAULT 0,
                    final_amount FLOAT NOT NULL,
                    distance FLOAT,
                    job_time_minutes INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES job_requests (id)
                )
            """)
            
            # Create mechanic stats table for fairness tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mechanic_stats (
                    mechanic_id INTEGER PRIMARY KEY,
                    total_jobs INTEGER DEFAULT 0,
                    completed_jobs INTEGER DEFAULT 0,
                    cancelled_jobs INTEGER DEFAULT 0,
                    acceptance_rate FLOAT DEFAULT 0,
                    completion_rate FLOAT DEFAULT 0,
                    fairness_score FLOAT DEFAULT 100,
                    rating FLOAT DEFAULT 5,
                    total_earnings FLOAT DEFAULT 0,
                    last_job_time TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create mechanic performance table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mechanic_performance (
                    mechanic_id INTEGER PRIMARY KEY,
                    rating FLOAT DEFAULT 5.0,
                    total_jobs INTEGER DEFAULT 0,
                    completed_jobs INTEGER DEFAULT 0,
                    cancelled_jobs INTEGER DEFAULT 0,
                    acceptance_rate FLOAT DEFAULT 0,
                    completion_rate FLOAT DEFAULT 0,
                    avg_response_time FLOAT DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create mechanic safety reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mechanic_safety_reports (
                    id SERIAL PRIMARY KEY,
                    mechanic_id INTEGER NOT NULL,
                    job_id INTEGER,
                    incident_type TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'OPEN',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES job_requests (id)
                )
            """)
            
            # Create mechanic panic alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mechanic_panic_alerts (
                    id SERIAL PRIMARY KEY,
                    mechanic_id INTEGER NOT NULL,
                    job_id INTEGER,
                    location TEXT,
                    status TEXT DEFAULT 'ACTIVE',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES job_requests (id)
                )
            """)
            
            # Add indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mechanic_status ON job_requests(mechanic_id, status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority_status ON job_requests(priority, status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON job_requests(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_active_mechanic ON active_jobs(mechanic_id, status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_active_job_request ON active_jobs(job_request_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_earnings_mechanic ON mechanic_earnings(mechanic_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_earnings_date ON mechanic_earnings(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stats_mechanic ON mechanic_stats(mechanic_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_mechanic ON mechanic_performance(mechanic_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_safety_mechanic ON mechanic_safety_reports(mechanic_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_panic_mechanic ON mechanic_panic_alerts(mechanic_id)")
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def create_job_request(self, user_id: int, mechanic_id: int, user_name: str, 
                          car_model: str, issue: str, issue_type: str, 
                          user_city: str, distance_km: float = None, 
                          eta_minutes: int = None, estimated_earning: float = None,
                          priority: str = 'NORMAL', assignment_reason: str = None) -> int:
        """Create a new job request"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Set response deadline (30 seconds from now)
            response_deadline = (datetime.now() + timedelta(seconds=30)).isoformat()
            
            # Auto-detect emergency priority
            if any(keyword in issue.lower() for keyword in ['brake failure', 'engine stopped', 'accident', 'emergency']):
                priority = 'EMERGENCY'
            
            cursor.execute("""
                INSERT INTO job_requests 
                (user_id, mechanic_id, user_name, car_model, issue, issue_type, 
                 user_city, distance_km, eta_minutes, estimated_earning, priority, 
                 status, assignment_reason, response_deadline)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ASSIGNED', %s, %s)
                RETURNING id
            """, (user_id, mechanic_id, user_name, car_model, issue, issue_type, 
                  user_city, distance_km, eta_minutes, estimated_earning, priority, 
                  assignment_reason, response_deadline))
            
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
    
    def get_pending_jobs(self, mechanic_id: int) -> List[Dict]:
        """Get pending job requests for a mechanic"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM job_requests 
                WHERE mechanic_id = %s AND status = 'ASSIGNED'
                ORDER BY priority DESC, created_at ASC
            """, (mechanic_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_job_request(self, job_id: int) -> Optional[Dict]:
        """Get a specific job request"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM job_requests WHERE id = %s", (job_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def accept_job(self, job_id: int) -> bool:
        """Accept a job request"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE job_requests 
                SET status = 'ACCEPTED', updated_at = %s
                WHERE id = %s AND status = 'ASSIGNED'
            """, (datetime.now().isoformat(), job_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def reject_job(self, job_id: int, reason: str = None) -> bool:
        """Reject a job request"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE job_requests 
                SET status = 'REJECTED', updated_at = %s, assignment_reason = %s
                WHERE id = %s AND status = 'ASSIGNED'
            """, (datetime.now().isoformat(), reason, job_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def complete_job(self, job_id: int) -> bool:
        """Mark a job as completed"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE job_requests 
                SET status = 'COMPLETED', updated_at = %s
                WHERE id = %s AND status = 'ACCEPTED'
            """, (datetime.now().isoformat(), job_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_expired_jobs(self) -> List[Dict]:
        """Get jobs that have passed their response deadline"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            current_time = datetime.now().isoformat()
            cursor.execute("""
                SELECT * FROM job_requests 
                WHERE status = 'ASSIGNED' AND response_deadline < %s
            """, (current_time,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def reassign_job(self, job_id: int, new_mechanic_id: int, reason: str = None) -> bool:
        """Reassign a job to a new mechanic"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Set new response deadline
            response_deadline = (datetime.now() + timedelta(seconds=30)).isoformat()
            
            cursor.execute("""
                UPDATE job_requests 
                SET mechanic_id = %s, status = 'ASSIGNED', updated_at = %s, 
                    response_deadline = %s, assignment_reason = %s
                WHERE id = %s
            """, (new_mechanic_id, datetime.now().isoformat(), response_deadline, reason, job_id))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_job_statistics(self, mechanic_id: int) -> Dict:
        """Get job statistics for a mechanic"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Total jobs today
            today = datetime.now().date().isoformat()
            cursor.execute("""
                SELECT COUNT(*) as total_today FROM job_requests 
                WHERE mechanic_id = %s AND CAST(created_at AS DATE) = %s
            """, (mechanic_id, today))
            total_today = cursor.fetchone()['total_today']
            
            # Completed jobs today
            cursor.execute("""
                SELECT COUNT(*) as completed_today FROM job_requests 
                WHERE mechanic_id = %s AND status = 'COMPLETED' AND CAST(created_at AS DATE) = %s
            """, (mechanic_id, today))
            completed_today = cursor.fetchone()['completed_today']
            
            # Total earnings today
            cursor.execute("""
                SELECT COALESCE(SUM(estimated_earning), 0) as earnings_today FROM job_requests 
                WHERE mechanic_id = %s AND status = 'COMPLETED' AND CAST(created_at AS DATE) = %s
            """, (mechanic_id, today))
            earnings_today = cursor.fetchone()['earnings_today']
            
            return {
                'total_today': total_today,
                'completed_today': completed_today,
                'earnings_today': float(earnings_today),
                'success_rate': (completed_today / total_today * 100) if total_today > 0 else 0
            }
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_all_jobs(self, status: str = None) -> List[Dict]:
        """Get all job requests (for admin)"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if status:
                cursor.execute("SELECT * FROM job_requests WHERE status = %s ORDER BY created_at DESC", (status,))
            else:
                cursor.execute("SELECT * FROM job_requests ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # ===== ACTIVE JOB MANAGEMENT =====
    
    def create_active_job(self, job_request_id: int, user_id: int, mechanic_id: int, 
                         user_name: str, user_phone: str = None, user_lat: float = None, 
                         user_long: float = None, mechanic_lat: float = None, 
                         mechanic_long: float = None) -> int:
        """Create an active job when mechanic accepts a job"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Generate 4-digit OTP
            otp = f"{random.randint(1000, 9999)}"
            
            cursor.execute("""
                INSERT INTO active_jobs 
                (job_request_id, user_id, mechanic_id, user_name, user_phone, 
                 user_lat, user_long, mechanic_lat, mechanic_long, otp, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ARRIVING')
                RETURNING id
            """, (job_request_id, user_id, mechanic_id, user_name, user_phone, 
                  user_lat, user_long, mechanic_lat, mechanic_long, otp))
            
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
    
    def get_active_job(self, mechanic_id: int) -> Optional[Dict]:
        """Get current active job for a mechanic"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT aj.*, jr.issue, jr.issue_type, jr.car_model, jr.estimated_earning
                FROM active_jobs aj
                JOIN job_requests jr ON aj.job_request_id = jr.id
                WHERE aj.mechanic_id = %s AND aj.status IN ('ARRIVING', 'ARRIVED', 'WORKING')
                ORDER BY aj.created_at DESC
                LIMIT 1
            """, (mechanic_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_active_job_status(self, active_job_id: int, status: str, **kwargs) -> bool:
        """Update active job status and additional fields"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Build dynamic update query
            update_fields = ["status = %s", "updated_at = %s"]
            update_values = [status, datetime.now().isoformat()]
            
            # Add optional fields
            if 'arrival_time' in kwargs:
                update_fields.append("arrival_time = %s")
                update_values.append(kwargs['arrival_time'])
            
            if 'start_time' in kwargs:
                update_fields.append("start_time = %s")
                update_values.append(kwargs['start_time'])
            
            if 'completion_time' in kwargs:
                update_fields.append("completion_time = %s")
                update_values.append(kwargs['completion_time'])
            
            if 'before_photo' in kwargs:
                update_fields.append("before_photo = %s")
                update_values.append(kwargs['before_photo'])
            
            if 'after_photo' in kwargs:
                update_fields.append("after_photo = %s")
                update_values.append(kwargs['after_photo'])
            
            update_values.append(active_job_id)
            
            cursor.execute(f"""
                UPDATE active_jobs 
                SET {', '.join(update_fields)}
                WHERE id = %s
            """, update_values)
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def verify_otp(self, active_job_id: int, otp: str) -> bool:
        """Verify OTP for job start"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT otp FROM active_jobs WHERE id = %s", (active_job_id,))
            row = cursor.fetchone()
            
            if row and row['otp'] == otp:
                return True
            return False
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def add_mechanic_earning(self, mechanic_id: int, job_id: int, amount: float) -> bool:
        """Add mechanic earning record"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO mechanic_earnings 
                (mechanic_id, job_id, amount, date)
                VALUES (%s, %s, %s, %s)
            """, (mechanic_id, job_id, amount, datetime.now().date().isoformat()))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_mechanic_earnings(self, mechanic_id: int, date: str = None) -> List[Dict]:
        """Get mechanic earnings"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if date:
                cursor.execute("""
                    SELECT * FROM mechanic_earnings 
                    WHERE mechanic_id = %s AND date = %s
                    ORDER BY created_at DESC
                """, (mechanic_id, date))
            else:
                cursor.execute("""
                    SELECT * FROM mechanic_earnings 
                    WHERE mechanic_id = %s
                    ORDER BY created_at DESC
                """, (mechanic_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_mechanic_daily_earnings(self, mechanic_id: int) -> float:
        """Get total earnings for today"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            today = datetime.now().date().isoformat()
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) as total
                FROM mechanic_earnings 
                WHERE mechanic_id = %s AND date = %s
            """, (mechanic_id, today))
            result = cursor.fetchone()
            return float(result['total']) if result else 0.0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def calculate_repair_time(self, active_job_id: int) -> str:
        """Calculate elapsed repair time"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT start_time FROM active_jobs WHERE id = %s AND status = 'WORKING'
            """, (active_job_id,))
            row = cursor.fetchone()
            
            if row and row['start_time']:
                try:
                    start_time = datetime.fromisoformat(row['start_time'])
                    elapsed = datetime.now() - start_time
                    minutes = int(elapsed.total_seconds() / 60)
                    return f"{minutes} minutes"
                except:
                    return "0 minutes"
            
            return "0 minutes"
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # ===== EARNINGS MANAGEMENT =====
    
    def insert_earning(self, mechanic_id: int, job_id: int, 
                      base_amount: float, commission_rate: float = 0.20, 
                      bonus: float = 0, distance: float = None, 
                      job_time_minutes: int = None) -> int:
        """Insert earning record with transparent commission calculation"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Calculate commission and earnings
            platform_commission = base_amount * commission_rate
            mechanic_earning = base_amount - platform_commission
            final_amount = mechanic_earning + bonus
            
            cursor.execute("""
                INSERT INTO mechanic_earnings 
                (mechanic_id, job_id, base_amount, platform_commission, 
                 mechanic_earning, bonus, final_amount, distance, job_time_minutes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (mechanic_id, job_id, base_amount, platform_commission, 
                  mechanic_earning, bonus, final_amount, distance, job_time_minutes))
            
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
    
    def get_mechanic_earnings_summary(self, mechanic_id: int) -> Dict:
        """Get mechanic earnings summary"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Today's earnings
            today = datetime.now().date().isoformat()
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(final_amount), 0) as today_earnings,
                    COUNT(*) as today_jobs,
                    COALESCE(SUM(bonus), 0) as today_bonus,
                    COALESCE(SUM(platform_commission), 0) as today_commission
                FROM mechanic_earnings 
                WHERE mechanic_id = %s AND CAST(created_at AS DATE) = %s
            """, (mechanic_id, today))
            
            today_data = cursor.fetchone()
            
            # Total earnings
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(final_amount), 0) as total_earnings,
                    COUNT(*) as total_jobs,
                    COALESCE(SUM(bonus), 0) as total_bonus,
                    COALESCE(SUM(platform_commission), 0) as total_commission
                FROM mechanic_earnings 
                WHERE mechanic_id = %s
            """, (mechanic_id,))
            
            total_data = cursor.fetchone()
            
            return {
                'today_earnings': float(today_data['today_earnings']),
                'today_jobs': today_data['today_jobs'],
                'today_bonus': float(today_data['today_bonus']),
                'today_commission': float(today_data['today_commission']),
                'total_earnings': float(total_data['total_earnings']),
                'total_jobs': total_data['total_jobs'],
                'total_bonus': float(total_data['total_bonus']),
                'total_commission': float(total_data['total_commission'])
            }
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_mechanic_earnings_history(self, mechanic_id: int, limit: int = 20) -> List[Dict]:
        """Get mechanic earnings history"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT me.*, jr.user_name, jr.car_model, jr.issue
                FROM mechanic_earnings me
                JOIN job_requests jr ON me.job_id = jr.id
                WHERE me.mechanic_id = %s
                ORDER BY me.created_at DESC
                LIMIT %s
            """, (mechanic_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # ===== MECHANIC STATS MANAGEMENT =====
    
    def get_mechanic_stats(self, mechanic_id: int) -> Dict:
        """Get mechanic stats including fairness score"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM mechanic_stats WHERE mechanic_id = %s
            """, (mechanic_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            else:
                # Initialize stats for new mechanic
                self.initialize_mechanic_stats(mechanic_id)
                return self.get_mechanic_stats(mechanic_id)
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def initialize_mechanic_stats(self, mechanic_id: int):
        """Initialize stats for new mechanic"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO mechanic_stats 
                (mechanic_id, total_jobs, completed_jobs, cancelled_jobs, 
                 acceptance_rate, completion_rate, fairness_score, rating, total_earnings)
                VALUES (%s, 0, 0, 0, 0, 0, 100, 5, 0)
                ON CONFLICT (mechanic_id) DO NOTHING
            """, (mechanic_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_mechanic_stats(self, mechanic_id: int, job_completed: bool = True):
        """Update mechanic stats after job completion/cancellation"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Get current stats
            stats = self.get_mechanic_stats(mechanic_id)
            
            # Update job counts
            total_jobs = stats['total_jobs'] + 1
            if job_completed:
                completed_jobs = stats['completed_jobs'] + 1
                cancelled_jobs = stats['cancelled_jobs']
            else:
                completed_jobs = stats['completed_jobs']
                cancelled_jobs = stats['cancelled_jobs'] + 1
            
            # Calculate rates
            acceptance_rate = (completed_jobs + cancelled_jobs) / total_jobs if total_jobs > 0 else 0
            completion_rate = completed_jobs / total_jobs if total_jobs > 0 else 0
            
            # Calculate fairness score (decreases with more recent jobs)
            recent_jobs_weight = min(total_jobs * 2, 50)  # Max 50 points penalty
            fairness_score = max(50, 100 - recent_jobs_weight)  # Minimum 50
            
            # Update earnings
            earnings_summary = self.get_mechanic_earnings_summary(mechanic_id)
            total_earnings = earnings_summary['total_earnings']
            
            cursor.execute("""
                UPDATE mechanic_stats 
                SET total_jobs = %s, completed_jobs = %s, cancelled_jobs = %s,
                    acceptance_rate = %s, completion_rate = %s, fairness_score = %s,
                    total_earnings = %s, last_job_time = %s, updated_at = %s
                WHERE mechanic_id = %s
            """, (total_jobs, completed_jobs, cancelled_jobs, acceptance_rate, 
                  completion_rate, fairness_score, total_earnings, 
                  datetime.now().isoformat(), datetime.now(), mechanic_id))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_fairness_insights(self, mechanic_id: int) -> Dict:
        """Get fairness insights for transparency"""
        stats = self.get_mechanic_stats(mechanic_id)
        
        insights = {
            'fairness_score': stats['fairness_score'],
            'completion_rate': stats['completion_rate'] * 100,
            'total_jobs': stats['total_jobs'],
            'rating': stats['rating'],
            'recent_job_activity': stats['last_job_time'],
            'dispatch_factors': [],
            'improvement_suggestions': []
        }
        
        # Add dispatch factors
        if stats['fairness_score'] > 80:
            insights['dispatch_factors'].append("High fairness score increases job priority")
        if stats['completion_rate'] > 0.9:
            insights['dispatch_factors'].append("Excellent completion rate")
        if stats['rating'] > 4.5:
            insights['dispatch_factors'].append("High customer rating")
        
        # Add improvement suggestions
        if stats['fairness_score'] < 70:
            insights['improvement_suggestions'].append("Complete more jobs to improve fairness score")
        if stats['completion_rate'] < 0.8:
            insights['improvement_suggestions'].append("Maintain higher completion rate")
        if stats['rating'] < 4.0:
            insights['improvement_suggestions'].append("Focus on customer satisfaction")
        
        return insights
    
    # ===== PERFORMANCE MANAGEMENT =====
    
    def get_mechanic_performance(self, mechanic_id: int) -> Dict:
        """Get mechanic performance metrics"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM mechanic_performance WHERE mechanic_id = %s
            """, (mechanic_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            else:
                # Initialize performance for new mechanic
                self.initialize_mechanic_performance(mechanic_id)
                return self.get_mechanic_performance(mechanic_id)
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def initialize_mechanic_performance(self, mechanic_id: int):
        """Initialize performance for new mechanic"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO mechanic_performance 
                (mechanic_id, rating, total_jobs, completed_jobs, cancelled_jobs, 
                 acceptance_rate, completion_rate, avg_response_time)
                VALUES (%s, 5.0, 0, 0, 0, 0, 0, 0)
                ON CONFLICT (mechanic_id) DO UPDATE SET
                rating = EXCLUDED.rating,
                total_jobs = EXCLUDED.total_jobs,
                completed_jobs = EXCLUDED.completed_jobs,
                cancelled_jobs = EXCLUDED.cancelled_jobs,
                acceptance_rate = EXCLUDED.acceptance_rate,
                completion_rate = EXCLUDED.completion_rate,
                avg_response_time = EXCLUDED.avg_response_time
            """, (mechanic_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_mechanic_performance(self, mechanic_id: int, job_completed: bool = True, 
                                response_time: float = None):
        """Update mechanic performance after job"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Get current performance
            current = self.get_mechanic_performance(mechanic_id)
            
            # Update job counts
            total_jobs = current['total_jobs'] + 1
            if job_completed:
                completed_jobs = current['completed_jobs'] + 1
                cancelled_jobs = current['cancelled_jobs']
            else:
                completed_jobs = current['completed_jobs']
                cancelled_jobs = current['cancelled_jobs'] + 1
            
            # Calculate rates
            acceptance_rate = (completed_jobs + cancelled_jobs) / total_jobs if total_jobs > 0 else 0
            completion_rate = completed_jobs / total_jobs if total_jobs > 0 else 0
            
            # Update average response time
            avg_response_time = current['avg_response_time']
            if response_time is not None:
                avg_response_time = (avg_response_time + response_time) / 2
            
            cursor.execute("""
                UPDATE mechanic_performance 
                SET total_jobs = %s, completed_jobs = %s, cancelled_jobs = %s,
                    acceptance_rate = %s, completion_rate = %s, avg_response_time = %s,
                    last_updated = %s
                WHERE mechanic_id = %s
            """, (total_jobs, completed_jobs, cancelled_jobs, acceptance_rate, 
                  completion_rate, avg_response_time, datetime.now(), mechanic_id))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_performance_improvement_tips(self, mechanic_id: int) -> Dict:
        """Get performance improvement suggestions"""
        performance = self.get_mechanic_performance(mechanic_id)
        
        tips = []
        
        # Response time tips
        if performance['avg_response_time'] > 15:
            tips.append("Respond faster to job requests to increase priority")
        elif performance['avg_response_time'] > 10:
            tips.append("Good response time! Keep it up to get more jobs")
        
        # Completion rate tips
        if performance['completion_rate'] < 0.8:
            tips.append("Maintain higher completion rate for better dispatch priority")
        elif performance['completion_rate'] > 0.95:
            tips.append("Excellent completion rate! You're a top performer")
        
        # Acceptance rate tips
        if performance['acceptance_rate'] < 0.7:
            tips.append("Accept more job requests to increase earnings")
        elif performance['acceptance_rate'] > 0.9:
            tips.append("Great acceptance rate! Keep up the good work")
        
        # Rating tips
        if performance['rating'] < 4.0:
            tips.append("Focus on customer service to improve rating")
        elif performance['rating'] > 4.7:
            tips.append("Outstanding rating! You're highly valued")
        
        # Job volume tips
        if performance['total_jobs'] < 10:
            tips.append("Complete more jobs to build reputation")
        elif performance['total_jobs'] > 50:
            tips.append("High job volume! Consider taking breaks to maintain quality")
        
        return {
            'tips': tips,
            'performance_level': self._calculate_performance_level(performance)
        }
    
    def _calculate_performance_level(self, performance: Dict) -> str:
        """Calculate performance level based on metrics"""
        score = 0
        
        # Rating component (40%)
        score += (performance['rating'] / 5.0) * 40
        
        # Completion rate component (30%)
        score += performance['completion_rate'] * 30
        
        # Acceptance rate component (20%)
        score += performance['acceptance_rate'] * 20
        
        # Response time component (10%)
        response_score = max(0, 10 - performance['avg_response_time'])
        score += response_score
        
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Average"
        else:
            return "Needs Improvement"
    
    # ===== SAFETY MANAGEMENT =====
    
    def create_safety_report(self, mechanic_id: int, job_id: int = None, 
                           incident_type: str = "", description: str = "") -> int:
        """Create safety incident report"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO mechanic_safety_reports 
                (mechanic_id, job_id, incident_type, description, status)
                VALUES (%s, %s, %s, %s, 'OPEN')
                RETURNING id
            """, (mechanic_id, job_id, incident_type, description))
            
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
    
    def create_panic_alert(self, mechanic_id: int, job_id: int = None, 
                        location: str = "") -> int:
        """Create panic alert for immediate admin help"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO mechanic_panic_alerts 
                (mechanic_id, job_id, location, status)
                VALUES (%s, %s, %s, 'ACTIVE')
                RETURNING id
            """, (mechanic_id, job_id, location))
            
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
    
    def get_mechanic_safety_reports(self, mechanic_id: int) -> List[Dict]:
        """Get mechanic safety reports"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM mechanic_safety_reports 
                WHERE mechanic_id = %s
                ORDER BY created_at DESC
                LIMIT 20
            """, (mechanic_id,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_mechanic_panic_alerts(self, mechanic_id: int) -> List[Dict]:
        """Get mechanic panic alerts"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM mechanic_panic_alerts 
                WHERE mechanic_id = %s
                ORDER BY created_at DESC
                LIMIT 10
            """, (mechanic_id,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def resolve_panic_alert(self, alert_id: int):
        """Resolve panic alert"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE mechanic_panic_alerts 
                SET status = 'RESOLVED', resolved_at = %s
                WHERE id = %s
            """, (datetime.now(), alert_id))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_all_safety_reports(self, limit: int = 50) -> List[Dict]:
        """Get all safety reports for admin dashboard"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT sr.*, w.name as mechanic_name, w.email as mechanic_email
                FROM mechanic_safety_reports sr
                LEFT JOIN car_service_workers w ON sr.mechanic_id = w.id
                ORDER BY sr.created_at DESC
                LIMIT %s
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_all_panic_alerts(self, limit: int = 50) -> List[Dict]:
        """Get all panic alerts for admin dashboard"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT pa.*, w.name as mechanic_name, w.email as mechanic_email
                FROM mechanic_panic_alerts pa
                LEFT JOIN car_service_workers w ON pa.mechanic_id = w.id
                ORDER BY pa.created_at DESC
                LIMIT %s
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

# Global instance
job_requests_db = JobRequestsDB()
