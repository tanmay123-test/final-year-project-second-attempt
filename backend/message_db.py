import sqlite3
import os
from datetime import datetime

DB_PATH = "data/messages.db"

class MessageDB:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER NOT NULL,
            sender_role TEXT NOT NULL,
            sender_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """)
        # sender_role: 'user' or 'worker'
        # sender_id: user_id if sender_role='user', worker_id if sender_role='worker'
        self.conn.commit()

    def send_message(self, appointment_id, sender_role, sender_id, message):
        """Store a message in the database"""
        self.cursor.execute("""
        INSERT INTO messages (appointment_id, sender_role, sender_id, message, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """, (appointment_id, sender_role, sender_id, message, datetime.utcnow().isoformat()))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_messages(self, appointment_id):
        """Get all messages for an appointment, ordered by timestamp"""
        self.cursor.execute("""
        SELECT id, appointment_id, sender_role, sender_id, message, timestamp
        FROM messages
        WHERE appointment_id=?
        ORDER BY timestamp ASC
        """, (appointment_id,))
        rows = self.cursor.fetchall()
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

    def get_appointment_messages_count(self, appointment_id):
        """Get count of messages for an appointment (for validation)"""
        self.cursor.execute("""
        SELECT COUNT(*) FROM messages WHERE appointment_id=?
        """, (appointment_id,))
        return self.cursor.fetchone()[0]
