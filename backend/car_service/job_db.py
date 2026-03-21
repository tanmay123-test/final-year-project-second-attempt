import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class JobDB:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor()
        try:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS mechanic_jobs (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    mechanic_id INTEGER NOT NULL,
                    car_id INTEGER,
                    issue TEXT NOT NULL,
                    booking_type TEXT NOT NULL,
                    booking_date TEXT,
                    booking_time TEXT,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS mechanic_slots (
                    id SERIAL PRIMARY KEY,
                    mechanic_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    is_available BOOLEAN DEFAULT TRUE
                )
                """
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def create_job(self, user_id, mechanic_id, car_id, issue, booking_type, date=None, time=None):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor()
        try:
            status = "CONFIRMED"
            cur.execute(
                """
                INSERT INTO mechanic_jobs (user_id, mechanic_id, car_id, issue, booking_type, booking_date, booking_time, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (user_id, mechanic_id, car_id, issue, booking_type, date, time, status),
            )
            job_id = cur.fetchone()[0]
            conn.commit()
            return job_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def get_user_jobs(self, user_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("SELECT * FROM mechanic_jobs WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
            rows = [dict(r) for r in cur.fetchall()]
            return rows
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def get_mechanic_jobs(self, mechanic_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("SELECT * FROM mechanic_jobs WHERE mechanic_id=%s ORDER BY created_at DESC", (mechanic_id,))
            rows = [dict(r) for r in cur.fetchall()]
            return rows
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def get_completed_count_for_mechanic(self, mechanic_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM mechanic_jobs WHERE mechanic_id=%s AND status='COMPLETED'", (mechanic_id,))
            count = cur.fetchone()[0]
            return count
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def get_available_slots(self, mechanic_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute(
                """
                SELECT * FROM mechanic_slots
                WHERE mechanic_id=%s AND is_available=TRUE
                ORDER BY date ASC, time ASC
                """,
                (mechanic_id,),
            )
            rows = [dict(r) for r in cur.fetchall()]
            return rows
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def seed_slots_if_empty(self, mechanic_id):
        slots = self.get_available_slots(mechanic_id)
        if slots:
            return slots
        
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor()
        try:
            now = datetime.now()
            times = ["10:00 AM", "02:00 PM", "05:00 PM"]
            for d in range(0, 3):
                date_str = (now + timedelta(days=d)).strftime("%Y-%m-%d")
                for t in times:
                    cur.execute(
                        "INSERT INTO mechanic_slots (mechanic_id, date, time, is_available) VALUES (%s, %s, %s, TRUE)",
                        (mechanic_id, date_str, t),
                    )
            conn.commit()
            return self.get_available_slots(mechanic_id)
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def mark_slot_unavailable(self, slot_id):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cur = conn.cursor()
        try:
            cur.execute("UPDATE mechanic_slots SET is_available=FALSE WHERE id=%s", (slot_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cur.close()
            conn.close()

job_db = JobDB()
