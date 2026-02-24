"""
Mechanic Worker Database - Car Service Module
Handles mechanic status, jobs, earnings, and performance metrics
"""

import sqlite3
import os
from datetime import datetime, timedelta

def get_mechanic_db_connection():
    """Get connection to mechanic database"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'databases', 'car_worker_auth.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_mechanic_db():
    """Initialize mechanic-related tables"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    # Mechanic Status Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mechanic_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER UNIQUE,
            online_status TEXT DEFAULT 'offline',
            is_busy BOOLEAN DEFAULT 0,
            last_location_lat REAL,
            last_location_long REAL,
            last_status_change TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (worker_id) REFERENCES workers (id)
        )
    ''')
    
    # Mechanic Jobs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mechanic_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            worker_id INTEGER,
            issue_type TEXT NOT NULL,
            required_skill TEXT NOT NULL,
            location_lat REAL,
            location_long REAL,
            distance_km REAL,
            estimated_earning_min INTEGER,
            estimated_earning_max INTEGER,
            estimated_duration INTEGER, -- in minutes
            customer_rating REAL,
            status TEXT DEFAULT 'PENDING', -- PENDING, ACCEPTED, ON_THE_WAY, ARRIVED, WORKING, COMPLETED
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accepted_at TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (worker_id) REFERENCES workers (id)
        )
    ''')
    
    # Job Proofs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_proofs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER UNIQUE,
            before_photo_path TEXT,
            after_photo_path TEXT,
            work_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES mechanic_jobs (id)
        )
    ''')
    
    # Mechanic Earnings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mechanic_earnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mechanic_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            job_amount INTEGER NOT NULL,
            platform_commission INTEGER NOT NULL,
            mechanic_earning INTEGER NOT NULL,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mechanic_id) REFERENCES workers (id),
            FOREIGN KEY (job_id) REFERENCES mechanic_jobs (id)
        )
    ''')
    
    # Mechanic Performance Metrics Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mechanic_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mechanic_id INTEGER UNIQUE,
            completion_rate REAL DEFAULT 0.0,
            on_time_rate REAL DEFAULT 0.0,
            acceptance_rate REAL DEFAULT 0.0,
            complaint_rate REAL DEFAULT 0.0,
            trust_score REAL DEFAULT 5.0,
            total_jobs INTEGER DEFAULT 0,
            completed_jobs INTEGER DEFAULT 0,
            cancelled_jobs INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mechanic_id) REFERENCES workers (id)
        )
    ''')
    
    # Emergency Alerts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mechanic_emergency_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mechanic_id INTEGER NOT NULL,
            alert_type TEXT NOT NULL,
            message TEXT,
            location_lat REAL,
            location_long REAL,
            status TEXT DEFAULT 'ACTIVE', -- ACTIVE, RESOLVED
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            FOREIGN KEY (mechanic_id) REFERENCES workers (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_mechanic_status(worker_id):
    """Create mechanic status record"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR IGNORE INTO mechanic_status (worker_id)
        VALUES (?)
    ''', (worker_id,))
    
    conn.commit()
    conn.close()

def update_mechanic_status(worker_id, online_status=None, is_busy=None, lat=None, lon=None):
    """Update mechanic status"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    updates = []
    values = []
    
    if online_status is not None:
        updates.append("online_status = ?")
        values.append(online_status)
    
    if is_busy is not None:
        updates.append("is_busy = ?")
        values.append(is_busy)
    
    if lat is not None:
        updates.append("last_location_lat = ?")
        values.append(lat)
    
    if lon is not None:
        updates.append("last_location_long = ?")
        values.append(lon)
    
    if updates:
        updates.append("last_status_change = CURRENT_TIMESTAMP")
        values.append(worker_id)
        
        query = f"UPDATE mechanic_status SET {', '.join(updates)} WHERE worker_id = ?"
        cursor.execute(query, values)
    
    conn.commit()
    conn.close()

def get_mechanic_status(worker_id):
    """Get mechanic status"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM mechanic_status WHERE worker_id = ?
    ''', (worker_id,))
    
    status = cursor.fetchone()
    conn.close()
    
    return status

def create_job_request(user_id, issue_type, required_skill, lat, lon, estimated_earning_min, estimated_earning_max, estimated_duration, customer_rating=None):
    """Create a new job request"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO mechanic_jobs 
        (user_id, issue_type, required_skill, location_lat, location_long, 
         estimated_earning_min, estimated_earning_max, estimated_duration, customer_rating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, issue_type, required_skill, lat, lon, 
          estimated_earning_min, estimated_earning_max, estimated_duration, customer_rating))
    
    job_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return job_id

def get_pending_jobs(worker_id, mechanic_skills, lat=None, lon=None, max_distance=20):
    """Get pending jobs for a mechanic"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    # For now, get all pending jobs (distance calculation can be added later)
    cursor.execute('''
        SELECT * FROM mechanic_jobs 
        WHERE status = 'PENDING' 
        AND worker_id IS NULL
        ORDER BY created_at DESC
    ''')
    
    jobs = cursor.fetchall()
    conn.close()
    
    # Filter by skills (simple matching)
    filtered_jobs = []
    for job in jobs:
        if mechanic_skills and job['required_skill'].lower() in [skill.lower() for skill in mechanic_skills]:
            filtered_jobs.append(job)
    
    return filtered_jobs

def accept_job(job_id, worker_id):
    """Accept a job"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE mechanic_jobs 
        SET worker_id = ?, status = 'ACCEPTED', accepted_at = CURRENT_TIMESTAMP
        WHERE id = ? AND status = 'PENDING'
    ''', (worker_id, job_id))
    
    # Update mechanic status to busy
    cursor.execute('''
        UPDATE mechanic_status 
        SET is_busy = 1 
        WHERE worker_id = ?
    ''', (worker_id,))
    
    conn.commit()
    conn.close()

def get_mechanic_jobs(worker_id, status=None):
    """Get mechanic's jobs"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    if status:
        cursor.execute('''
            SELECT * FROM mechanic_jobs 
            WHERE worker_id = ? AND status = ?
            ORDER BY created_at DESC
        ''', (worker_id, status))
    else:
        cursor.execute('''
            SELECT * FROM mechanic_jobs 
            WHERE worker_id = ?
            ORDER BY created_at DESC
        ''', (worker_id,))
    
    jobs = cursor.fetchall()
    conn.close()
    
    return jobs

def update_job_status(job_id, status):
    """Update job status"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    updates = ["status = ?"]
    values = [status]
    
    if status == 'COMPLETED':
        updates.append("completed_at = CURRENT_TIMESTAMP")
    
    values.append(job_id)
    
    query = f"UPDATE mechanic_jobs SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, values)
    
    # If completed, set mechanic to not busy
    if status == 'COMPLETED':
        cursor.execute('''
            UPDATE mechanic_status 
            SET is_busy = 0 
            WHERE worker_id = (SELECT worker_id FROM mechanic_jobs WHERE id = ?)
        ''', (job_id,))
    
    conn.commit()
    conn.close()

def create_job_proof(job_id, before_photo=None, after_photo=None, work_notes=None):
    """Create or update job proof"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO job_proofs 
        (job_id, before_photo_path, after_photo_path, work_notes, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (job_id, before_photo, after_photo, work_notes))
    
    conn.commit()
    conn.close()

def get_job_proof(job_id):
    """Get job proof"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM job_proofs WHERE job_id = ?
    ''', (job_id,))
    
    proof = cursor.fetchone()
    conn.close()
    
    return proof

def create_earning_record(mechanic_id, job_id, job_amount, platform_commission, mechanic_earning):
    """Create earning record"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO mechanic_earnings 
        (mechanic_id, job_id, job_amount, platform_commission, mechanic_earning, date)
        VALUES (?, ?, ?, ?, ?, CURRENT_DATE)
    ''', (mechanic_id, job_id, job_amount, platform_commission, mechanic_earning))
    
    conn.commit()
    conn.close()

def get_mechanic_earnings(mechanic_id, period='all'):
    """Get mechanic earnings"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    if period == 'today':
        cursor.execute('''
            SELECT * FROM mechanic_earnings 
            WHERE mechanic_id = ? AND date = CURRENT_DATE
        ''', (mechanic_id,))
    elif period == 'week':
        cursor.execute('''
            SELECT * FROM mechanic_earnings 
            WHERE mechanic_id = ? AND date >= date('now', '-7 days')
        ''', (mechanic_id,))
    elif period == 'month':
        cursor.execute('''
            SELECT * FROM mechanic_earnings 
            WHERE mechanic_id = ? AND date >= date('now', '-30 days')
        ''', (mechanic_id,))
    else:
        cursor.execute('''
            SELECT * FROM mechanic_earnings WHERE mechanic_id = ?
        ''', (mechanic_id,))
    
    earnings = cursor.fetchall()
    conn.close()
    
    return earnings

def update_mechanic_metrics(mechanic_id):
    """Update mechanic performance metrics"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    # Get job statistics
    cursor.execute('''
        SELECT 
            COUNT(*) as total_jobs,
            SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_jobs,
            SUM(CASE WHEN status IN ('CANCELLED', 'REJECTED') THEN 1 ELSE 0 END) as cancelled_jobs
        FROM mechanic_jobs WHERE worker_id = ?
    ''', (mechanic_id,))
    
    job_stats = cursor.fetchone()
    
    # Calculate rates
    total_jobs = job_stats['total_jobs'] or 0
    completed_jobs = job_stats['completed_jobs'] or 0
    cancelled_jobs = job_stats['cancelled_jobs'] or 0
    
    completion_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
    acceptance_rate = ((total_jobs - cancelled_jobs) / total_jobs * 100) if total_jobs > 0 else 100
    
    # Update metrics
    cursor.execute('''
        INSERT OR REPLACE INTO mechanic_metrics 
        (mechanic_id, completion_rate, acceptance_rate, total_jobs, completed_jobs, cancelled_jobs, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (mechanic_id, completion_rate, acceptance_rate, total_jobs, completed_jobs, cancelled_jobs))
    
    conn.commit()
    conn.close()

def get_mechanic_metrics(mechanic_id):
    """Get mechanic performance metrics"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM mechanic_metrics WHERE mechanic_id = ?
    ''', (mechanic_id,))
    
    metrics = cursor.fetchone()
    conn.close()
    
    return metrics

def create_emergency_alert(mechanic_id, alert_type, message, lat=None, lon=None):
    """Create emergency alert"""
    conn = get_mechanic_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO mechanic_emergency_alerts 
        (mechanic_id, alert_type, message, location_lat, location_long)
        VALUES (?, ?, ?, ?, ?)
    ''', (mechanic_id, alert_type, message, lat, lon))
    
    alert_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return alert_id

def get_demand_insights():
    """Get current demand insights (mock implementation)"""
    # This would normally analyze real-time data
    # For now, return mock data
    return {
        'demand_level': 'HIGH',
        'high_activity_zone': 'Ghatkopar',
        'priority_score': 8.5
    }

# Initialize database when module is imported
init_mechanic_db()
