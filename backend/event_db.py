import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class EventDB:
    def __init__(self):
        self.create_table()

    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

    def create_table(self):
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                appointment_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """)
            # event_type: appointment_created, appointment_accepted, consultation_started, consultation_completed
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def log_event(self, appointment_id, event_type):
        """Log an event for an appointment."""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO events (appointment_id, event_type, timestamp)
            VALUES (%s, %s, %s)
            RETURNING id
            """, (appointment_id, event_type, datetime.utcnow().isoformat()))
            event_id = cursor.fetchone()[0]
            conn.commit()
            return event_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_events_for_appointment(self, appointment_id):
        """Get all events for an appointment (for debugging / UI)."""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT id, appointment_id, event_type, timestamp
            FROM events
            WHERE appointment_id=%s
            ORDER BY timestamp ASC
            """, (appointment_id,))
            rows = cursor.fetchall()
            return [
                {"id": row[0], "appointment_id": row[1], "event_type": row[2], "timestamp": row[3]}
                for row in rows
            ]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
