import sqlite3
import os
import logging
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "expertease.db")


class AvailabilityDB:
    def __init__(self):
        self.conn = sqlite3.connect("expertease.db", check_same_thread=False)
        self.create_table()

    def _normalize_date(self, date_str):
        """
        Normalize date string to 'YYYY-MM-DD' format
        """
        if not date_str:
            return ""
        try:
            # HTML5 date inputs are YYYY-MM-DD, but let's be robust
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    continue
        except Exception as e:
            logging.error(f"Error normalizing date '{date_str}': {e}")
            
        return date_str

    def _normalize_time(self, time_str):
        """
        Normalize time string to 'HH:MM AM/PM' format (e.g., '9:00 AM' -> '09:00 AM')
        """
        if not time_str:
            return ""
        try:
            # Try to parse the time string
            # It could be '9:00 AM', '09:00 AM', '13:00', etc.
            t = None
            time_str = time_str.strip().upper()
            
            if 'AM' in time_str or 'PM' in time_str:
                # Handle AM/PM format
                try:
                    t = datetime.strptime(time_str, "%I:%M %p")
                except ValueError:
                    t = datetime.strptime(time_str, "%H:%M %p")
            else:
                # Handle 24h format
                t = datetime.strptime(time_str, "%H:%M")
                
            if t:
                return t.strftime("%I:%M %p")
        except Exception as e:
            logging.error(f"Error normalizing time '{time_str}': {e}")
            
        return time_str

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
    
    def add_availability(self, worker_id, date, time_slot):
        # Normalize inputs
        date = self._normalize_date(date)
        time_slot = self._normalize_time(time_slot)
        
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
        # Normalize inputs
        date = self._normalize_date(date)
        time_slot = self._normalize_time(time_slot)
        
        cursor = self.conn.cursor()
        cursor.execute("""
        DELETE FROM availability
        WHERE worker_id=? AND date=? AND time_slot=?
        """, (worker_id, date, time_slot))
        self.conn.commit()
        return True, "Availability removed successfully"

    # ==================================================
    # GET AVAILABILITY (OPTIONAL DATE FILTER)
    # ==================================================
    def get_availability(self, worker_id, date=None):
        # Normalize date if provided
        if date:
            date = self._normalize_date(date)
            
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
