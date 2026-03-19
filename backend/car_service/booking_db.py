"""
Car Service Booking Database
Manages mechanic jobs and bookings
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

# Database path
CAR_JOBS_DB = os.path.join(os.path.dirname(__file__), '..', 'data', 'car_jobs.db')

class BookingDB:
    def __init__(self):
        self.conn = sqlite3.connect(CAR_JOBS_DB, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_table()
    
    def get_conn(self):
        return sqlite3.connect(CAR_JOBS_DB, check_same_thread=False)
    
    def create_table(self):
        """Create mechanic jobs table"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mechanic_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mechanic_id INTEGER NOT NULL,
                car_id INTEGER NOT NULL,
                issue TEXT NOT NULL,
                status TEXT DEFAULT 'SEARCHING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accepted_at TEXT NULL,
                started_at TEXT NULL,
                completed_at TEXT NULL,
                cancelled_at TEXT NULL,
                notes TEXT NULL,
                estimated_cost INTEGER NULL,
                final_cost INTEGER NULL,
                rating INTEGER NULL
            )
        """)
        self.conn.commit()
    
    def create_job(self, user_id: int, mechanic_id: int, car_id: int, issue: str, estimated_cost: int = None) -> int:
        """Create a new mechanic job"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO mechanic_jobs 
            (user_id, mechanic_id, car_id, issue, status, estimated_cost)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, mechanic_id, car_id, issue, 'SEARCHING', estimated_cost))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_jobs(self, user_id: int) -> List[Dict]:
        """Get all jobs for a user with hybrid data model"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT mj.*
            FROM mechanic_jobs mj
            WHERE mj.user_id = ?
            ORDER BY mj.created_at DESC
        """, (user_id,))
        
        jobs = []
        for row in cursor.fetchall():
            job = dict(row)
            
            # Hybrid model: Get real mechanic data from worker database
            try:
                from car_service.car_service_worker_db import car_service_worker_db
                mechanic = car_service_worker_db.get_worker_by_id(job['mechanic_id'])
                if mechanic:
                    job['mechanic_name'] = mechanic.get('name', f"Mechanic {job['mechanic_id']}")
                else:
                    job['mechanic_name'] = f"Mechanic {job['mechanic_id']}"
            except:
                job['mechanic_name'] = f"Mechanic {job['mechanic_id']}"
            
            # Hybrid model: Get real car data from car profile database
            try:
                from car_service.car_profile_db import car_profile_db
                car_info = car_profile_db.get_car_by_id(job['car_id'])
                if car_info:
                    job['brand'] = car_info.get('brand', 'Unknown')
                    job['model'] = car_info.get('model', 'Unknown')
                    job['registration_number'] = car_info.get('registration_number', 'Unknown')
                    job['car_info'] = car_info  # Add full car info for display
                else:
                    job['brand'] = "Unknown"
                    job['model'] = "Unknown"
                    job['registration_number'] = "Unknown"
                    job['car_info'] = None
            except:
                job['brand'] = "Unknown"
                job['model'] = "Unknown"
                job['registration_number'] = "Unknown"
                job['car_info'] = None
                
            jobs.append(job)
        return jobs
    
    def get_active_job(self, user_id: int) -> Optional[Dict]:
        """Get the active job for a user with hybrid data model"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT mj.*
            FROM mechanic_jobs mj
            WHERE mj.user_id = ? AND mj.status IN ('SEARCHING', 'ACCEPTED', 'ARRIVING', 'WORKING')
            ORDER BY mj.created_at DESC
            LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        if row:
            job = dict(row)
            
            # Hybrid model: Get real mechanic data from worker database
            try:
                from car_service.car_service_worker_db import car_service_worker_db
                mechanic = car_service_worker_db.get_worker_by_id(job['mechanic_id'])
                if mechanic:
                    job['mechanic_name'] = mechanic.get('name', f"Mechanic {job['mechanic_id']}")
                else:
                    job['mechanic_name'] = f"Mechanic {job['mechanic_id']}"
            except:
                job['mechanic_name'] = f"Mechanic {job['mechanic_id']}"
            
            # Hybrid model: Get real car data from car profile database
            try:
                from car_service.car_profile_db import car_profile_db
                car_info = car_profile_db.get_car_by_id(job['car_id'])
                if car_info:
                    job['brand'] = car_info.get('brand', 'Unknown')
                    job['model'] = car_info.get('model', 'Unknown')
                    job['registration_number'] = car_info.get('registration_number', 'Unknown')
                    job['car_info'] = car_info  # Add full car info for display
                else:
                    job['brand'] = "Unknown"
                    job['model'] = "Unknown"
                    job['registration_number'] = "Unknown"
                    job['car_info'] = None
            except:
                job['brand'] = "Unknown"
                job['model'] = "Unknown"
                job['registration_number'] = "Unknown"
                job['car_info'] = None
                
            return job
        return None
    
    def update_job_status(self, job_id: int, status: str, notes: str = None):
        """Update job status"""
        cursor = self.conn.cursor()
        
        # Add timestamp based on status
        if status == 'ACCEPTED':
            cursor.execute("""
                UPDATE mechanic_jobs 
                SET status = ?, accepted_at = ?, notes = ?
                WHERE id = ?
            """, (status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), notes, job_id))
        elif status == 'ARRIVING':
            cursor.execute("""
                UPDATE mechanic_jobs 
                SET status = ?, started_at = ?, notes = ?
                WHERE id = ?
            """, (status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), notes, job_id))
        elif status == 'COMPLETED':
            cursor.execute("""
                UPDATE mechanic_jobs 
                SET status = ?, completed_at = ?, notes = ?
                WHERE id = ?
            """, (status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), notes, job_id))
        elif status == 'CANCELLED':
            cursor.execute("""
                UPDATE mechanic_jobs 
                SET status = ?, cancelled_at = ?, notes = ?
                WHERE id = ?
            """, (status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), notes, job_id))
        else:
            cursor.execute("""
                UPDATE mechanic_jobs 
                SET status = ?, notes = ?
                WHERE id = ?
            """, (status, notes, job_id))
        
        self.conn.commit()
        print(f"✅ Job {job_id} status updated to: {status}")
    
    def get_completed_count_for_mechanic(self, mechanic_id: int) -> int:
        """Get completed jobs count for a mechanic"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM mechanic_jobs 
            WHERE mechanic_id = ? AND status = 'COMPLETED'
        """, (mechanic_id,))
        
        result = cursor.fetchone()
        return result['count'] if result else 0
    
    def update_job_cost(self, job_id: int, final_cost: int):
        """Update the final cost of a job"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE mechanic_jobs 
            SET final_cost = ?
            WHERE id = ?
        """, (final_cost, job_id))
        self.conn.commit()
    
    def rate_job(self, job_id: int, rating: int):
        """Rate a completed job"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE mechanic_jobs 
            SET rating = ?
            WHERE id = ?
        """, (rating, job_id))
        self.conn.commit()
    
    def get_mechanic_jobs(self, mechanic_id: int) -> List[Dict]:
        """Get all jobs for a mechanic"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT mj.*
            FROM mechanic_jobs mj
            WHERE mj.mechanic_id = ?
            ORDER BY mj.created_at DESC
        """, (mechanic_id,))
        
        jobs = []
        for row in cursor.fetchall():
            job = dict(row)
            # Add placeholder data
            job['user_name'] = f"User {job['user_id']}"
            job['brand'] = "Unknown"
            job['model'] = "Unknown"
            jobs.append(job)
        return jobs


# Global instance
booking_db = BookingDB()
