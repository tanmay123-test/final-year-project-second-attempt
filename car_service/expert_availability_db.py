"""
Expert Availability Database
Manages expert availability status, consultation requests, and demand metrics
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Database path
EXPERT_AVAILABILITY_DB = os.path.join(os.path.dirname(__file__), 'expert_availability.db')

class ExpertAvailabilityDB:
    def __init__(self):
        self.conn = sqlite3.connect(EXPERT_AVAILABILITY_DB, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def get_conn(self):
        return sqlite3.connect(EXPERT_AVAILABILITY_DB, check_same_thread=False)
    
    def create_tables(self):
        """Create all required tables for expert availability system"""
        cursor = self.conn.cursor()
        
        # Expert availability table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expert_availability (
                expert_id INTEGER PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'OFFLINE',
                current_consultation_id INTEGER,
                last_status_change TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_consultations INTEGER DEFAULT 0,
                total_hours_online REAL DEFAULT 0.0,
                rating REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (current_consultation_id) REFERENCES consultation_requests (request_id)
            )
        """)
        
        # Consultation requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consultation_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_name TEXT,
                user_city TEXT,
                area_of_expertise TEXT NOT NULL,
                issue_description TEXT NOT NULL,
                image_paths TEXT,
                priority INTEGER DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'WAITING',
                assigned_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                cancelled_at TIMESTAMP,
                expert_id INTEGER,
                FOREIGN KEY (expert_id) REFERENCES expert_availability (expert_id)
            )
        """)
        
        # Activity logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                expert_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (expert_id) REFERENCES expert_availability (expert_id)
            )
        """)
        
        # Demand metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demand_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_of_expertise TEXT NOT NULL,
                waiting_requests INTEGER DEFAULT 0,
                available_experts INTEGER DEFAULT 0,
                demand_level TEXT DEFAULT 'LOW',
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    # Expert Availability Management
    def update_expert_status(self, expert_id: int, status: str, consultation_id: int = None) -> bool:
        """Update expert availability status"""
        valid_statuses = ['OFFLINE', 'ONLINE_AVAILABLE', 'BUSY']
        if status not in valid_statuses:
            return False
        
        cursor = self.conn.cursor()
        
        # Check if expert exists
        cursor.execute("SELECT status FROM expert_availability WHERE expert_id = ?", (expert_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Validate status transition
            current_status = existing['status']
            if not self._is_valid_status_transition(current_status, status):
                return False
            
            # Update existing expert
            cursor.execute("""
                UPDATE expert_availability 
                SET status = ?, current_consultation_id = ?, last_status_change = CURRENT_TIMESTAMP
                WHERE expert_id = ?
            """, (status, consultation_id, expert_id))
        else:
            # Insert new expert
            cursor.execute("""
                INSERT INTO expert_availability (expert_id, status, current_consultation_id)
                VALUES (?, ?, ?)
            """, (expert_id, status, consultation_id))
        
        self.conn.commit()
        return True
    
    def _is_valid_status_transition(self, from_status: str, to_status: str) -> bool:
        """Validate if status transition is allowed"""
        valid_transitions = {
            'OFFLINE': ['ONLINE_AVAILABLE'],
            'ONLINE_AVAILABLE': ['BUSY', 'OFFLINE', 'ONLINE_AVAILABLE'],  # Allow same status
            'BUSY': ['ONLINE_AVAILABLE', 'OFFLINE']
        }
        return to_status in valid_transitions.get(from_status, [])
    
    def get_expert_status(self, expert_id: int) -> Optional[Dict]:
        """Get expert current status"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM expert_availability WHERE expert_id = ?", (expert_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_available_experts(self, area_of_expertise: str = None) -> List[Dict]:
        """Get all available experts"""
        cursor = self.conn.cursor()
        if area_of_expertise:
            cursor.execute("""
                SELECT ea.* FROM expert_availability ea
                JOIN workers w ON ea.expert_id = w.worker_id
                WHERE ea.status = 'ONLINE_AVAILABLE' AND w.expertise = ?
            """, (area_of_expertise,))
        else:
            cursor.execute("SELECT * FROM expert_availability WHERE status = 'ONLINE_AVAILABLE'")
        
        return [dict(row) for row in cursor.fetchall()]
    
    # Consultation Request Management
    def create_consultation_request(self, user_id: int, issue_description: str, 
                                 area_of_expertise: str, priority: int = 1, 
                                 user_name: str = None, user_city: str = None,
                                 image_paths: list = None) -> int:
        """Create a new consultation request"""
        cursor = self.conn.cursor()
        
        image_paths_str = ','.join(image_paths) if image_paths else None
        
        cursor.execute("""
            INSERT INTO consultation_requests 
            (user_id, user_name, user_city, area_of_expertise, issue_description, 
             image_paths, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, user_name, user_city, area_of_expertise, 
               issue_description, image_paths_str, priority))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_waiting_requests(self, area_of_expertise: str = None, limit: int = 10) -> List[Dict]:
        """Get waiting consultation requests with enhanced fields"""
        cursor = self.conn.cursor()
        if area_of_expertise:
            cursor.execute("""
                SELECT * FROM consultation_requests 
                WHERE status = 'WAITING' AND area_of_expertise = ?
                ORDER BY priority DESC, created_at ASC
                LIMIT ?
            """, (area_of_expertise, limit))
        else:
            cursor.execute("""
                SELECT * FROM consultation_requests 
                WHERE status = 'WAITING'
                ORDER BY priority DESC, created_at ASC
                LIMIT ?
            """, (limit,))
        
        requests = [dict(row) for row in cursor.fetchall()]
        
        # Parse image paths
        for request in requests:
            if request['image_paths']:
                request['image_paths'] = request['image_paths'].split(',')
            else:
                request['image_paths'] = []
        
        return requests
    
    def assign_consultation_request(self, request_id: int, expert_id: int, assigned_reason: str = None) -> bool:
        """Assign a consultation request to an expert"""
        cursor = self.conn.cursor()
        
        # Update request status and assign expert
        cursor.execute("""
            UPDATE consultation_requests 
            SET status = 'ASSIGNED', expert_id = ?, 
                assigned_at = CURRENT_TIMESTAMP
            WHERE request_id = ? AND status = 'WAITING_QUEUE'
        """, (expert_id, request_id))
        
        success = cursor.rowcount > 0
        if success:
            # Update expert status to BUSY
            self.update_expert_status(expert_id, 'BUSY', request_id)
            
            # Log assignment
            self._log_activity(expert_id, "CONSULTATION_ASSIGNED", 
                            {"request_id": request_id, "assigned_reason": assigned_reason})
        
        self.conn.commit()
        return success
    
    def start_consultation(self, request_id: int, expert_id: int) -> bool:
        """Start a consultation"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            UPDATE consultation_requests 
            SET status = 'ACTIVE', started_at = CURRENT_TIMESTAMP
            WHERE request_id = ? AND expert_id = ? AND status = 'ASSIGNED'
        """, (request_id, expert_id))
        
        success = cursor.rowcount > 0
        if success:
            # Log start
            self._log_activity(expert_id, "CONSULTATION_STARTED", {"request_id": request_id})
        
        self.conn.commit()
        return success
    
    def complete_consultation(self, request_id: int, expert_id: int) -> bool:
        """Complete a consultation"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            UPDATE consultation_requests 
            SET status = 'COMPLETED', completed_at = CURRENT_TIMESTAMP
            WHERE request_id = ? AND expert_id = ? AND status = 'ACTIVE'
        """, (request_id, expert_id))
        
        success = cursor.rowcount > 0
        if success:
            # Update expert status back to ONLINE_AVAILABLE
            self.update_expert_status(expert_id, 'ONLINE_AVAILABLE')
            
            # Update consultation count
            cursor.execute("""
                UPDATE expert_availability 
                SET total_consultations = total_consultations + 1
                WHERE expert_id = ?
            """, (expert_id,))
            
            self.conn.commit()
            
            # Log completion
            self._log_activity(expert_id, "CONSULTATION_COMPLETED", {"request_id": request_id})
        
        return success
    
    def reject_consultation_request(self, request_id: int, expert_id: int, rejection_reason: str = None) -> bool:
        """Reject a consultation request"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            UPDATE consultation_requests 
            SET status = 'WAITING', expert_id = NULL, 
                assigned_at = NULL, assigned_reason = NULL
            WHERE request_id = ? AND expert_id = ? AND status = 'ASSIGNED'
        """, (request_id, expert_id))
        
        success = cursor.rowcount > 0
        if success:
            # Update expert status back to ONLINE_AVAILABLE
            self.update_expert_status(expert_id, 'ONLINE_AVAILABLE')
            
            # Log rejection
            self._log_activity(expert_id, "CONSULTATION_REJECTED", 
                            {"request_id": request_id, "rejection_reason": rejection_reason})
        
        self.conn.commit()
        return True
    
    def get_expert_active_consultation(self, expert_id: int) -> Optional[Dict]:
        """Get expert's current active consultation"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT cr.* FROM consultation_requests cr
            JOIN expert_availability ea ON cr.request_id = ea.current_consultation_id
            WHERE ea.expert_id = ? AND ea.status = 'BUSY'
        """, (expert_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_expert_requests(self, expert_id: int, status: str = None, limit: int = 10) -> List[Dict]:
        """Get expert's consultation requests"""
        cursor = self.conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT * FROM consultation_requests 
                WHERE expert_id = ? AND status = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (expert_id, status, limit))
        else:
            cursor.execute("""
                SELECT * FROM consultation_requests 
                WHERE expert_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (expert_id, limit))
        
        requests = [dict(row) for row in cursor.fetchall()]
        
        # Parse image paths
        for request in requests:
            if request['image_paths']:
                request['image_paths'] = request['image_paths'].split(',')
            else:
                request['image_paths'] = []
        
        return requests
    
    def get_demand_metrics(self, area_of_expertise: str) -> Dict:
        """Get current demand metrics for an area of expertise"""
        cursor = self.conn.cursor()
        
        # Count waiting requests
        cursor.execute("""
            SELECT COUNT(*) as waiting_count 
            FROM consultation_requests 
            WHERE status = 'WAITING' AND area_of_expertise = ?
        """, (area_of_expertise,))
        waiting_count = cursor.fetchone()['waiting_count']
        
        # Count available experts
        cursor.execute("""
            SELECT COUNT(*) as available_count 
            FROM expert_availability ea
            JOIN workers w ON ea.expert_id = w.worker_id
            WHERE ea.status = 'ONLINE_AVAILABLE' AND w.expertise = ?
        """, (area_of_expertise,))
        available_count = cursor.fetchone()['available_count']
        
        # Calculate demand level
        if available_count == 0:
            demand_level = 'HIGH'
        elif waiting_count > available_count * 2:
            demand_level = 'HIGH'
        elif waiting_count > available_count:
            demand_level = 'MEDIUM'
        else:
            demand_level = 'LOW'
        
        # Store metrics
        cursor.execute("""
            INSERT INTO demand_metrics 
            (area_of_expertise, waiting_requests, available_experts, demand_level)
            VALUES (?, ?, ?, ?)
        """, (area_of_expertise, waiting_count, available_count, demand_level))
        
        self.conn.commit()
        
        return {
            'area_of_expertise': area_of_expertise,
            'waiting_requests': waiting_count,
            'available_experts': available_count,
            'demand_level': demand_level
        }
    
    def get_expert_performance_stats(self, expert_id: int, days: int = 30) -> Dict:
        """Get expert performance statistics"""
        cursor = self.conn.cursor()
        
        # Get completed consultations
        cursor.execute("""
            SELECT 
                COUNT(*) as total_consultations,
                AVG(CASE WHEN cr.completed_at IS NOT NULL 
                    THEN (julianday(cr.completed_at) - julianday(cr.started_at)) * 24 * 60 
                    ELSE NULL END) as avg_duration_minutes,
                AVG(CASE WHEN cr.assigned_at IS NOT NULL AND cr.started_at IS NOT NULL
                    THEN (julianday(cr.started_at) - julianday(cr.assigned_at)) * 60
                    ELSE NULL END) as avg_response_time_minutes
            FROM consultation_requests cr
            WHERE cr.expert_id = ? 
            AND cr.status = 'COMPLETED'
            AND cr.created_at >= datetime('now', '-{} days')
        """.format(days), (expert_id,))
        
        stats = cursor.fetchone()
        
        return {
            'total_consultations': stats['total_consultations'] or 0,
            'avg_duration_minutes': round(stats['avg_duration_minutes'] or 0, 2),
            'avg_response_time_minutes': round(stats['avg_response_time_minutes'] or 0, 2),
            'days_period': days
        }
    
    def get_activity_logs(self, expert_id: int, limit: int = 50) -> List[Dict]:
        """Get expert activity logs"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM activity_logs 
            WHERE expert_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (expert_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_expert_activity_logs(self, expert_id: int, limit: int = 50) -> List[Dict]:
        """Get expert activity logs (alias for get_activity_logs)"""
        return self.get_activity_logs(expert_id, limit)
    
    def _log_activity(self, expert_id: int, event_type: str, event_data: Dict = None):
        """Log expert activity"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO activity_logs (expert_id, event_type, event_data)
            VALUES (?, ?, ?)
        """, (expert_id, event_type, str(event_data) if event_data else None))
        self.conn.commit()
    
    def get_available_experts_by_category(self, category: str) -> List[Dict]:
        """Get available experts by category"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT ea.expert_id, ea.status, ea.rating
            FROM expert_availability ea
            WHERE ea.status = 'ONLINE_AVAILABLE'
        """)
        
        experts = [dict(row) for row in cursor.fetchall()]
        
        # Filter by category using automobile_experts table
        filtered_experts = []
        for expert in experts:
            # Get expert details from automobile_experts
            import sqlite3
            try:
                expert_db_path = os.path.join(os.path.dirname(__file__), 'automobile_experts.db')
                conn = sqlite3.connect(expert_db_path)
                cursor2 = conn.cursor()
                cursor2.execute("""
                    SELECT name, area_of_expertise, experience_years 
                    FROM automobile_experts 
                    WHERE id = ? AND area_of_expertise = ?
                """, (expert['expert_id'], category))
                
                expert_details = cursor2.fetchone()
                if expert_details:
                    expert_row = dict(expert)
                    expert_row.update({
                        'name': expert_details[0],
                        'expertise': expert_details[1], 
                        'experience_years': expert_details[2]
                    })
                    filtered_experts.append(expert_row)
                
                conn.close()
            except Exception:
                # If automobile_experts.db doesn't exist or other error, skip filtering
                filtered_experts.append(expert)
        
        return filtered_experts

# Create database instance
expert_availability_db = ExpertAvailabilityDB()
