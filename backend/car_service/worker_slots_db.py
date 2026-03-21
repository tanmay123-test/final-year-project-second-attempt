"""
Worker Slots Database
Manages mechanic availability slots for pre-bookings
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Dict, Optional

load_dotenv()

class WorkerSlotsDB:
    def __init__(self):
        self.create_table()
    
    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
    
    def create_table(self):
        """Create worker slots table"""
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS worker_slots (
                    id SERIAL PRIMARY KEY,
                    worker_id INTEGER NOT NULL,
                    slot_date TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    status TEXT DEFAULT 'AVAILABLE',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(worker_id, slot_date, start_time, end_time)
                )
            """)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def add_slot(self, worker_id: int, slot_date: str, start_time: str, end_time: str) -> bool:
        """Add a new availability slot"""
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO worker_slots (worker_id, slot_date, start_time, end_time)
                VALUES (%s, %s, %s, %s)
            """, (worker_id, slot_date, start_time, end_time))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    
    def get_worker_slots(self, worker_id: int) -> List[Dict]:
        """Get all slots for a worker"""
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM worker_slots 
                WHERE worker_id = %s
                ORDER BY slot_date, start_time
            """, (worker_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def create_slot(self, worker_id: int, date: str, start_time: str, end_time: str, 
                   max_jobs: int = 1, status: str = 'AVAILABLE') -> Optional[int]:
        """Create a new slot and return its ID"""
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO worker_slots (worker_id, slot_date, start_time, end_time, status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (worker_id, date, start_time, end_time, status))
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        except Exception:
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_available_slots(self, worker_id: int, date: str = None) -> List[Dict]:
        """Get available slots for a worker"""
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if date:
                cursor.execute("""
                    SELECT * FROM worker_slots 
                    WHERE worker_id = %s AND slot_date = %s AND status = 'AVAILABLE'
                    ORDER BY start_time
                """, (worker_id, date))
            else:
                cursor.execute("""
                    SELECT * FROM worker_slots 
                    WHERE worker_id = %s AND status = 'AVAILABLE'
                    ORDER BY slot_date, start_time
                """, (worker_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def book_slot(self, slot_id: int) -> bool:
        """Book a slot (mark as unavailable)"""
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE worker_slots 
                SET status = 'BOOKED', updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND status = 'AVAILABLE'
            """, (slot_id,))
            success = cursor.rowcount > 0
            conn.commit()
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def is_worker_available(self, worker_id: int, date: str, start_time: str, end_time: str) -> bool:
        """Check if worker is available at given time"""
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM worker_slots 
                WHERE worker_id = %s AND slot_date = %s 
                AND start_time <= %s AND end_time >= %s 
                AND status = 'BOOKED'
            """, (worker_id, date, end_time, start_time))
            result = cursor.fetchone()
            return result[0] == 0 if result else True
        except Exception as e:
            print(f"DB Error: {e}")
            return True
        finally:
            cursor.close()
            conn.close()
    
    def get_worker_slots_by_date_range(self, worker_id: int, start_date: str, end_date: str) -> List[Dict]:
        """Get worker slots within a date range"""
        conn = self.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM worker_slots 
                WHERE worker_id = %s AND slot_date BETWEEN %s AND %s
                ORDER BY slot_date, start_time
            """, (worker_id, start_date, end_date))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"DB Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def delete_slot(self, slot_id: int, worker_id: int) -> bool:
        """Delete a slot"""
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                DELETE FROM worker_slots 
                WHERE id = %s AND worker_id = %s
            """, (slot_id, worker_id))
            success = cursor.rowcount > 0
            conn.commit()
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

# Global instance
worker_slots_db = WorkerSlotsDB()