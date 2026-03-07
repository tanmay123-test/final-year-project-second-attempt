import os
import sqlite3
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")

class JobDB:
    def __init__(self):
        self._init_db()

    def _conn(self):
        return sqlite3.connect(DB_PATH)

    def _init_db(self):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mechanic_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mechanic_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                is_available INTEGER DEFAULT 1
            )
            """
        )
        conn.commit()
        conn.close()

    def create_job(self, user_id, mechanic_id, car_id, issue, booking_type, date=None, time=None):
        conn = self._conn()
        cur = conn.cursor()
        status = "CONFIRMED"
        cur.execute(
            """
            INSERT INTO mechanic_jobs (user_id, mechanic_id, car_id, issue, booking_type, booking_date, booking_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, mechanic_id, car_id, issue, booking_type, date, time, status),
        )
        job_id = cur.lastrowid
        conn.commit()
        conn.close()
        return job_id

    def get_user_jobs(self, user_id):
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM mechanic_jobs WHERE user_id=? ORDER BY created_at DESC", (user_id,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def get_mechanic_jobs(self, mechanic_id):
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM mechanic_jobs WHERE mechanic_id=? ORDER BY created_at DESC", (mechanic_id,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def get_completed_count_for_mechanic(self, mechanic_id):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM mechanic_jobs WHERE mechanic_id=? AND status='COMPLETED'", (mechanic_id,))
        count = cur.fetchone()[0]
        conn.close()
        return count

    def get_available_slots(self, mechanic_id):
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM mechanic_slots
            WHERE mechanic_id=? AND is_available=1
            ORDER BY date ASC, time ASC
            """,
            (mechanic_id,),
        )
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def seed_slots_if_empty(self, mechanic_id):
        slots = self.get_available_slots(mechanic_id)
        if slots:
            return slots
        conn = self._conn()
        cur = conn.cursor()
        now = datetime.now()
        times = ["10:00 AM", "02:00 PM", "05:00 PM"]
        for d in range(0, 3):
            date_str = (now + timedelta(days=d)).strftime("%Y-%m-%d")
            for t in times:
                cur.execute(
                    "INSERT INTO mechanic_slots (mechanic_id, date, time, is_available) VALUES (?, ?, ?, 1)",
                    (mechanic_id, date_str, t),
                )
        conn.commit()
        conn.close()
        return self.get_available_slots(mechanic_id)

    def mark_slot_unavailable(self, slot_id):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("UPDATE mechanic_slots SET is_available=0 WHERE id=?", (slot_id,))
        conn.commit()
        conn.close()
        return True

job_db = JobDB()
