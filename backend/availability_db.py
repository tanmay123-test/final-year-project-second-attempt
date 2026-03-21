import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()

class AvailabilityDB:
    def __init__(self):
        self.create_table()

    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')

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
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS availability (
                id SERIAL PRIMARY KEY,
                worker_id INTEGER,
                date TEXT,
                time_slot TEXT
            )
            """)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def add_availability(self, worker_id, date, time_slot):
        # Normalize inputs
        date = self._normalize_date(date)
        time_slot = self._normalize_time(time_slot)
        
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Check if slot already exists
            cursor.execute("""
            SELECT id FROM availability
            WHERE worker_id=%s AND date=%s AND time_slot=%s
            """, (worker_id, date, time_slot))

            if cursor.fetchone():
                return False, "This time slot is already added"

            cursor.execute("""
            INSERT INTO availability (worker_id, date, time_slot)
            VALUES (%s, %s, %s)
            """, (worker_id, date, time_slot))

            conn.commit()
            return True, "Availability added successfully"
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False, f"Database error: {e}"
        finally:
            cursor.close()
            conn.close()

    # ==================================================
    # REMOVE AVAILABILITY
    # ==================================================
    def remove_availability(self, worker_id, date, time_slot):
        # Normalize inputs
        date = self._normalize_date(date)
        time_slot = self._normalize_time(time_slot)
        
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
            DELETE FROM availability
            WHERE worker_id=%s AND date=%s AND time_slot=%s
            """, (worker_id, date, time_slot))
            conn.commit()
            return True, "Availability removed successfully"
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False, f"Database error: {e}"
        finally:
            cursor.close()
            conn.close()

    # ==================================================
    # GET AVAILABILITY (OPTIONAL DATE FILTER)
    # ==================================================
    def get_availability(self, worker_id, date=None):
        # Normalize date if provided
        if date:
            date = self._normalize_date(date)
            
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            if date:
                cursor.execute("""
                SELECT date, time_slot FROM availability
                WHERE worker_id=%s AND date=%s
                ORDER BY time_slot
                """, (worker_id, date))
            else:
                cursor.execute("""
                SELECT date, time_slot FROM availability
                WHERE worker_id=%s
                ORDER BY date, time_slot
                """, (worker_id,))

            return [
                {"date": row[0], "time_slot": row[1]}
                for row in cursor.fetchall()
            ]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
