"""
Mechanic Dashboard Database Module
Complete database operations for mechanic worker management system
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import json

class MechanicDashboardDB:
    """Complete database operations for Mechanic Dashboard System"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default path in car_service directory
            self.db_path = os.path.join(os.path.dirname(__file__), "mechanic_dashboard.db")
        else:
            self.db_path = db_path
        
        self.init_database()
    
    def get_conn(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize all mechanic dashboard tables"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        # 1. Mechanic Status Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mechanic_status (
                worker_id INTEGER PRIMARY KEY,
                online_status TEXT DEFAULT 'OFFLINE' CHECK (online_status IN ('ONLINE', 'OFFLINE')),
                is_busy BOOLEAN DEFAULT FALSE,
                last_location_lat REAL,
                last_location_long REAL,
                priority_score REAL DEFAULT 0.0,
                last_status_change TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (worker_id) REFERENCES workers (id)
            )
        """)
        
        # 2. Mechanic Jobs Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mechanic_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                assigned_mechanic_id INTEGER,
                issue_type TEXT NOT NULL,
                required_skill TEXT NOT NULL,
                location_lat REAL NOT NULL,
                location_long REAL NOT NULL,
                distance_km REAL,
                estimated_earning_min REAL,
                estimated_earning_max REAL,
                estimated_duration INTEGER,
                customer_rating REAL,
                status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'ACCEPTED', 'ON_THE_WAY', 'ARRIVED', 'WORKING', 'COMPLETED', 'CANCELLED')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (assigned_mechanic_id) REFERENCES workers (id)
            )
        """)
        
        # 3. Job Proofs Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS job_proofs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                before_photo_path TEXT,
                after_photo_path TEXT,
                work_notes TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES mechanic_jobs (id)
            )
        """)
        
        # 4. Mechanic Earnings Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mechanic_earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mechanic_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                job_amount REAL NOT NULL,
                platform_commission REAL NOT NULL,
                mechanic_earning REAL NOT NULL,
                date DATE NOT NULL,
                FOREIGN KEY (mechanic_id) REFERENCES workers (id),
                FOREIGN KEY (job_id) REFERENCES mechanic_jobs (id)
            )
        """)
        
        # 5. Mechanic Metrics Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mechanic_metrics (
                mechanic_id INTEGER PRIMARY KEY,
                completion_rate REAL DEFAULT 0.0,
                on_time_rate REAL DEFAULT 0.0,
                acceptance_rate REAL DEFAULT 0.0,
                complaint_rate REAL DEFAULT 0.0,
                trust_score REAL DEFAULT 0.0,
                total_jobs INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mechanic_id) REFERENCES workers (id)
            )
        """)
        
        # 6. Emergency Alerts Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mechanic_emergency_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mechanic_id INTEGER NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                alert_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'RESOLVED')),
                FOREIGN KEY (mechanic_id) REFERENCES workers (id)
            )
        """)
        
        # Create indexes for performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON mechanic_jobs (status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_jobs_mechanic ON mechanic_jobs (assigned_mechanic_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_earnings_mechanic ON mechanic_earnings (mechanic_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_earnings_date ON mechanic_earnings (date)")
        
        conn.commit()
        conn.close()
    
    # ==================== MECHANIC STATUS OPERATIONS ====================
    
    def update_mechanic_status(self, worker_id: int, online_status: str = None, 
                           is_busy: bool = None, lat: float = None, 
                           lng: float = None) -> bool:
        """Update mechanic online status and location"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            # Build update query dynamically
            updates = []
            params = []
            
            if online_status is not None:
                updates.append("online_status = ?")
                params.append(online_status)
            
            if is_busy is not None:
                updates.append("is_busy = ?")
                params.append(is_busy)
            
            if lat is not None:
                updates.append("last_location_lat = ?")
                params.append(lat)
            
            if lng is not None:
                updates.append("last_location_long = ?")
                params.append(lng)
            
            if updates:
                updates.append("last_status_change = CURRENT_TIMESTAMP")
                params.append(worker_id)
                
                query = f"UPDATE mechanic_status SET {', '.join(updates)} WHERE worker_id = ?"
                cur.execute(query, params)
                conn.commit()
            
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating mechanic status: {e}")
            return False
    
    def get_mechanic_status(self, worker_id: int) -> Optional[Dict]:
        """Get mechanic current status"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT ms.*, w.username, w.email 
            FROM mechanic_status ms
            JOIN workers w ON ms.worker_id = w.id
            WHERE ms.worker_id = ?
        """, (worker_id,))
        
        row = cur.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def calculate_priority_score(self, worker_id: int) -> float:
        """Calculate priority score based on metrics"""
        try:
            metrics = self.get_mechanic_metrics(worker_id)
            if not metrics:
                return 0.0
            
            # Priority formula as specified
            priority = (metrics['completion_rate'] * 0.4) + \
                     (metrics['on_time_rate'] * 0.3) + \
                     (metrics['acceptance_rate'] * 0.3)
            
            # Update in database
            conn = self.get_conn()
            cur = conn.cursor()
            cur.execute("UPDATE mechanic_status SET priority_score = ? WHERE worker_id = ?", 
                      (priority, worker_id))
            conn.commit()
            conn.close()
            
            return round(priority, 2)
        except Exception as e:
            print(f"Error calculating priority score: {e}")
            return 0.0
    
    # ==================== JOB OPERATIONS ====================
    
    def create_job_request(self, user_id: int, issue_type: str, required_skill: str,
                       lat: float, lng: float, estimated_min: float, 
                       estimated_max: float, duration: int) -> int:
        """Create new job request"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO mechanic_jobs 
            (user_id, issue_type, required_skill, location_lat, location_long, 
             estimated_earning_min, estimated_earning_max, estimated_duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, issue_type, required_skill, lat, lng, 
               estimated_min, estimated_max, duration))
        
        job_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        return job_id
    
    def get_pending_jobs(self, mechanic_id: int = None, skill: str = None) -> List[Dict]:
        """Get pending job requests with optional filtering"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        query = """
            SELECT mj.*, u.username as customer_name, u.email as customer_email
            FROM mechanic_jobs mj
            JOIN users u ON mj.user_id = u.id
            WHERE mj.status = 'PENDING'
        """
        params = []
        
        if skill:
            query += " AND mj.required_skill LIKE ?"
            params.append(f"%{skill}%")
        
        query += " ORDER BY mj.created_at DESC"
        
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def accept_job(self, job_id: int, mechanic_id: int) -> bool:
        """Accept a job request"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE mechanic_jobs 
                SET assigned_mechanic_id = ?, status = 'ACCEPTED'
                WHERE id = ? AND status = 'PENDING'
            """, (mechanic_id, job_id))
            
            # Mark mechanic as busy
            self.update_mechanic_status(mechanic_id, is_busy=True)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error accepting job: {e}")
            return False
    
    def update_job_status(self, job_id: int, status: str, mechanic_id: int) -> bool:
        """Update job status through lifecycle"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE mechanic_jobs 
                SET status = ? 
                WHERE id = ? AND assigned_mechanic_id = ?
            """, (status, job_id, mechanic_id))
            
            # If job is completed, set completion time
            if status == 'COMPLETED':
                cur.execute("""
                    UPDATE mechanic_jobs 
                    SET completed_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (job_id,))
                
                # Mark mechanic as not busy
                self.update_mechanic_status(mechanic_id, is_busy=False)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating job status: {e}")
            return False
    
    def get_active_jobs(self, mechanic_id: int) -> List[Dict]:
        """Get mechanic's active jobs"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT mj.*, u.username as customer_name, u.email as customer_email
            FROM mechanic_jobs mj
            JOIN users u ON mj.user_id = u.id
            WHERE mj.assigned_mechanic_id = ? 
            AND mj.status IN ('ACCEPTED', 'ON_THE_WAY', 'ARRIVED', 'WORKING')
            ORDER BY mj.created_at DESC
        """, (mechanic_id,))
        
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== EARNINGS OPERATIONS ====================
    
    def add_earning(self, mechanic_id: int, job_id: int, job_amount: float) -> bool:
        """Add job earning with commission calculation"""
        try:
            # Platform commission (20%)
            commission_rate = 0.20
            platform_commission = job_amount * commission_rate
            mechanic_earning = job_amount - platform_commission
            
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO mechanic_earnings 
                (mechanic_id, job_id, job_amount, platform_commission, mechanic_earning, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (mechanic_id, job_id, job_amount, platform_commission, 
                   mechanic_earning, datetime.now().date()))
            
            conn.commit()
            conn.close()
            
            # Update metrics
            self.update_job_completion_metrics(mechanic_id)
            return True
        except Exception as e:
            print(f"Error adding earning: {e}")
            return False
    
    def get_mechanic_earnings(self, mechanic_id: int, period: str = 'all') -> Dict:
        """Get mechanic earnings with period filtering"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        # Date filtering
        date_filter = ""
        params = [mechanic_id]
        
        if period == 'today':
            date_filter = "AND date = CURRENT_DATE"
        elif period == 'week':
            date_filter = "AND date >= date('now', '-7 days')"
        elif period == 'month':
            date_filter = "AND date >= date('now', '-1 month')"
        
        cur.execute(f"""
            SELECT 
                SUM(job_amount) as total_earnings,
                SUM(platform_commission) as total_commission,
                SUM(mechanic_earning) as net_earnings,
                COUNT(*) as job_count,
                AVG(mechanic_earning) as avg_earning
            FROM mechanic_earnings 
            WHERE mechanic_id = ? {date_filter}
        """, params)
        
        row = cur.fetchone()
        conn.close()
        
        return dict(row) if row else {
            'total_earnings': 0, 'total_commission': 0, 
            'net_earnings': 0, 'job_count': 0, 'avg_earning': 0
        }
    
    # ==================== METRICS OPERATIONS ====================
    
    def get_mechanic_metrics(self, mechanic_id: int) -> Optional[Dict]:
        """Get mechanic performance metrics"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM mechanic_metrics WHERE mechanic_id = ?
        """, (mechanic_id,))
        
        row = cur.fetchone()
        conn.close()
        
        return dict(row) if row else {
            'completion_rate': 0.0, 'on_time_rate': 0.0, 
            'acceptance_rate': 0.0, 'complaint_rate': 0.0,
            'trust_score': 0.0, 'total_jobs': 0
        }
    
    def update_job_completion_metrics(self, mechanic_id: int) -> None:
        """Update metrics after job completion"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            # Calculate new metrics
            cur.execute("""
                SELECT 
                    COUNT(*) as total_jobs,
                    SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_jobs,
                    SUM(CASE WHEN status = 'COMPLETED' AND 
                        julianday(completed_at) - julianday(created_at) <= estimated_duration THEN 1 ELSE 0 END) as on_time_jobs
                FROM mechanic_jobs 
                WHERE assigned_mechanic_id = ?
            """, (mechanic_id,))
            
            row = cur.fetchone()
            total_jobs = row['total_jobs'] or 0
            completed_jobs = row['completed_jobs'] or 0
            on_time_jobs = row['on_time_jobs'] or 0
            
            # Calculate rates
            completion_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
            on_time_rate = (on_time_jobs / completed_jobs * 100) if completed_jobs > 0 else 0
            
            # Update metrics
            cur.execute("""
                INSERT OR REPLACE INTO mechanic_metrics 
                (mechanic_id, completion_rate, on_time_rate, total_jobs, last_updated)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (mechanic_id, completion_rate, on_time_rate, total_jobs))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating metrics: {e}")
    
    # ==================== EMERGENCY OPERATIONS ====================
    
    def create_emergency_alert(self, mechanic_id: int, lat: float, lng: float) -> bool:
        """Create emergency SOS alert"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO mechanic_emergency_alerts 
                (mechanic_id, latitude, longitude)
                VALUES (?, ?, ?)
            """, (mechanic_id, lat, lng))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating emergency alert: {e}")
            return False
    
    def get_emergency_alerts(self, mechanic_id: int) -> List[Dict]:
        """Get mechanic's emergency alerts"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM mechanic_emergency_alerts 
            WHERE mechanic_id = ? 
            ORDER BY alert_time DESC
        """, (mechanic_id,))
        
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ==================== DEMAND ANALYSIS ====================
    
    def get_demand_analysis(self) -> Dict:
        """Get current market demand analysis"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        # Count pending jobs by skill
        cur.execute("""
            SELECT 
                required_skill,
                COUNT(*) as pending_count,
                AVG(estimated_earning_min) as avg_min_earning,
                AVG(estimated_earning_max) as avg_max_earning
            FROM mechanic_jobs 
            WHERE status = 'PENDING'
            GROUP BY required_skill
            ORDER BY pending_count DESC
        """)
        
        skill_demand = [dict(row) for row in cur.fetchall()]
        
        # Get online mechanics count
        cur.execute("""
            SELECT COUNT(*) as online_count FROM mechanic_status 
            WHERE online_status = 'ONLINE' AND is_busy = FALSE
        """)
        
        online_count = cur.fetchone()['online_count']
        
        conn.close()
        
        return {
            'skill_demand': skill_demand,
            'online_mechanics': online_count,
            'demand_level': self._calculate_demand_level(len(skill_demand)),
            'peak_hour': self._is_peak_hour()
        }
    
    def _calculate_demand_level(self, pending_jobs_count: int) -> str:
        """Calculate demand level based on pending jobs"""
        if pending_jobs_count >= 10:
            return 'HIGH'
        elif pending_jobs_count >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _is_peak_hour(self) -> bool:
        """Check if current time is peak hour"""
        current_hour = datetime.now().hour
        return 8 <= current_hour <= 18  # Business hours
    
    # ==================== JOB PROOF OPERATIONS ====================
    
    def upload_job_proof(self, job_id: int, before_photo: str, 
                      after_photo: str, notes: str) -> bool:
        """Upload job completion proof"""
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO job_proofs 
                (job_id, before_photo_path, after_photo_path, work_notes)
                VALUES (?, ?, ?, ?)
            """, (job_id, before_photo, after_photo, notes))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error uploading job proof: {e}")
            return False
    
    def get_job_proofs(self, job_id: int) -> List[Dict]:
        """Get proofs for a specific job"""
        conn = self.get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT * FROM job_proofs WHERE job_id = ?
            ORDER BY uploaded_at DESC
        """, (job_id,))
        
        rows = cur.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

# Initialize database instance
mechanic_dashboard_db = MechanicDashboardDB()
