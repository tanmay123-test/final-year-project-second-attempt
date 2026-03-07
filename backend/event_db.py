import sqlite3
import os
from datetime import datetime

DB_PATH = "data/events.db"

class EventDB:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """)
        # event_type: appointment_created, appointment_accepted, consultation_started, consultation_completed
        self.conn.commit()

    def log_event(self, appointment_id, event_type):
        """Log an event for an appointment."""
        self.cursor.execute("""
        INSERT INTO events (appointment_id, event_type, timestamp)
        VALUES (?, ?, ?)
        """, (appointment_id, event_type, datetime.utcnow().isoformat()))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_events_for_appointment(self, appointment_id):
        """Get all events for an appointment (for debugging / UI)."""
        self.cursor.execute("""
        SELECT id, appointment_id, event_type, timestamp
        FROM events
        WHERE appointment_id=?
        ORDER BY timestamp ASC
        """, (appointment_id,))
        rows = self.cursor.fetchall()
        return [
            {"id": row[0], "appointment_id": row[1], "event_type": row[2], "timestamp": row[3]}
            for row in rows
        ]
