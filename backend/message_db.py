import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class MessageDB:
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
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                appointment_id INTEGER NOT NULL,
                sender_role TEXT NOT NULL,
                sender_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """)
            # sender_role: 'user' or 'worker'
            # sender_id: user_id if sender_role='user', worker_id if sender_role='worker'
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def send_message(self, appointment_id, sender_role, sender_id, message):
        """Store a message in the database"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO messages (appointment_id, sender_role, sender_id, message, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """, (appointment_id, sender_role, sender_id, message, datetime.utcnow().isoformat()))
            message_id = cursor.fetchone()[0]
            conn.commit()
            return message_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_messages(self, appointment_id):
        """Get all messages for an appointment, ordered by timestamp"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT id, appointment_id, sender_role, sender_id, message, timestamp
            FROM messages
            WHERE appointment_id=%s
            ORDER BY timestamp ASC
            """, (appointment_id,))
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "appointment_id": row[1],
                    "sender_role": row[2],
                    "sender_id": row[3],
                    "message": row[4],
                    "timestamp": row[5]
                }
                for row in rows
            ]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_appointment_messages_count(self, appointment_id):
        """Get count of messages for an appointment (for validation)"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT COUNT(*) FROM messages WHERE appointment_id=%s
            """, (appointment_id,))
            return cursor.fetchone()[0]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()
