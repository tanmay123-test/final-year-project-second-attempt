"""
Worker Slots Database
Manages mechanic availability slots for pre-bookings
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Database path
WORKER_SLOTS_DB = os.path.join(os.path.dirname(__file__), '..', 'data', 'worker_slots.db')

class WorkerSlotsDB:
    def __init__(self):
        self.conn = sqlite3.connect(WORKER_SLOTS_DB, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_table()
    
    def create_table(self):
        """Create worker slots table"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS worker_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        self.conn.commit()
    
    def add_slot(self, worker_id: int, slot_date: str, start_time: str, end_time: str) -> bool:
        """Add a new availability slot"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO worker_slots (worker_id, slot_date, start_time, end_time)
                VALUES (?, ?, ?, ?)
            """, (worker_id, slot_date, start_time, end_time))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_available_slots(self, worker_id: int, date: str = None) -> List[Dict]:
        """Get available slots for a worker"""
        cursor = self.conn.cursor()
        if date:
            cursor.execute("""
                SELECT * FROM worker_slots 
                WHERE worker_id = ? AND slot_date = ? AND status = 'AVAILABLE'
                ORDER BY start_time
            """, (worker_id, date))
        else:
            cursor.execute("""
                SELECT * FROM worker_slots 
                WHERE worker_id = ? AND status = 'AVAILABLE'
                ORDER BY slot_date, start_time
            """, (worker_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def book_slot(self, slot_id: int) -> bool:
        """Book a slot (mark as unavailable)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE worker_slots 
            SET status = 'BOOKED', updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'AVAILABLE'
        """, (slot_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def is_worker_available(self, worker_id: int, date: str, start_time: str, end_time: str) -> bool:
        """Check if worker is available at given time"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM worker_slots 
            WHERE worker_id = ? AND slot_date = ? 
            AND start_time <= ? AND end_time >= ? 
            AND status = 'BOOKED'
        """, (worker_id, date, end_time, start_time))
        
        return cursor.fetchone()[0] == 0
    
    def get_worker_slots_by_date_range(self, worker_id: int, start_date: str, end_date: str) -> List[Dict]:
        """Get worker slots within a date range"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM worker_slots 
            WHERE worker_id = ? AND slot_date BETWEEN ? AND ?
            ORDER BY slot_date, start_time
        """, (worker_id, start_date, end_date))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_slot(self, slot_id: int, worker_id: int) -> bool:
        """Delete a slot"""
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM worker_slots 
            WHERE id = ? AND worker_id = ?
        """, (slot_id, worker_id))
        self.conn.commit()
        return cursor.rowcount > 0

# Global instance
worker_slots_db = WorkerSlotsDB()
