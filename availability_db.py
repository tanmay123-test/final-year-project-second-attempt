import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "expertease.db")


class AvailabilityDB:
    def __init__(self):
        self.conn = sqlite3.connect("expertease.db", check_same_thread=False)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER,
            date TEXT,
            time_slot TEXT
        )
        """)
        self.conn.commit()

    # ==================================================
    # ADD AVAILABILITY (SAFE + DUPLICATE CHECK)
    # ==================================================
    def add_availability(self, worker_id, date, time_slot):
        # Check if slot already exists
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id FROM availability
        WHERE worker_id=? AND date=? AND time_slot=?
        """, (worker_id, date, time_slot))

        if cursor.fetchone():
            return False, "This time slot is already added"

        cursor.execute("""
        INSERT INTO availability (worker_id, date, time_slot)
        VALUES (?, ?, ?)
        """, (worker_id, date, time_slot))

        self.conn.commit()
        return True, "Availability added successfully"

    # ==================================================
    # REMOVE AVAILABILITY
    # ==================================================
    def remove_availability(self, worker_id, date, time_slot):
        cursor = self.conn.cursor()
        cursor.execute("""
        DELETE FROM availability
        WHERE worker_id=? AND date=? AND time_slot=?
        """, (worker_id, date, time_slot))
        self.conn.commit()

    # ==================================================
    # GET AVAILABILITY (OPTIONAL DATE FILTER)
    # ==================================================
    def get_availability(self, worker_id, date=None):
        cursor = self.conn.cursor()
        if date:
            cursor.execute("""
            SELECT date, time_slot FROM availability
            WHERE worker_id=? AND date=?
            ORDER BY time_slot
            """, (worker_id, date))
        else:
            cursor.execute("""
            SELECT date, time_slot FROM availability
            WHERE worker_id=?
            ORDER BY date, time_slot
            """, (worker_id,))

        return [
            {"date": row[0], "time_slot": row[1]}
            for row in cursor.fetchall()
        ]
