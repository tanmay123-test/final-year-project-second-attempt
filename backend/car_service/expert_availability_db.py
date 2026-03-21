"""
Expert Availability Database
Manages expert availability status, consultation requests, and demand metrics
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Dict, Optional

load_dotenv()

class ExpertAvailabilityDB:
    def __init__(self):
        self.create_tables()
    
    def get_conn(self):
        load_dotenv()
        return psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
    
    def create_tables(self):
        """Create all required tables for expert availability system"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Expert availability table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expert_availability (
                    expert_id INTEGER PRIMARY KEY,
                    status TEXT NOT NULL DEFAULT 'OFFLINE',
                    current_consultation_id INTEGER,
                    last_status_change TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_consultations INTEGER DEFAULT 0,
                    total_hours_online FLOAT DEFAULT 0.0,
                    rating FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Consultation requests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consultation_requests (
                    request_id SERIAL PRIMARY KEY,
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
                    log_id SERIAL PRIMARY KEY,
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
                    metric_id SERIAL PRIMARY KEY,
                    area_of_expertise TEXT NOT NULL,
                    waiting_requests INTEGER DEFAULT 0,
                    available_experts INTEGER DEFAULT 0,
                    demand_level TEXT DEFAULT 'LOW',
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    # Expert Availability Management
    def update_expert_status(self, expert_id: int, status: str, consultation_id: int = None) -> bool:
        """Update expert availability status"""
        valid_statuses = ['OFFLINE', 'ONLINE_AVAILABLE', 'BUSY']
        if status not in valid_statuses:
            return False
        
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Check if expert exists
            cursor.execute("SELECT status FROM expert_availability WHERE expert_id = %s", (expert_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Validate status transition
                current_status = existing['status']
                if not self._is_valid_status_transition(current_status, status):
                    return False
                
                # Update existing expert
                cursor.execute("""
                    UPDATE expert_availability 
                    SET status = %s, current_consultation_id = %s, last_status_change = CURRENT_TIMESTAMP
                    WHERE expert_id = %s
                """, (status, consultation_id, expert_id))
            else:
                # Insert new expert
                cursor.execute("""
                    INSERT INTO expert_availability (expert_id, status, current_consultation_id)
                    VALUES (%s, %s, %s)
                """, (expert_id, status, consultation_id))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
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
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM expert_availability WHERE expert_id = %s", (expert_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_available_experts(self, area_of_expertise: str = None) -> List[Dict]:
        """Get all available experts"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if area_of_expertise:
                # Assuming workers table exists in the same PostgreSQL database
                cursor.execute("""
                    SELECT ea.* FROM expert_availability ea
                    JOIN car_service_workers w ON ea.expert_id = w.id
                    WHERE ea.status = 'ONLINE_AVAILABLE' AND w.skills LIKE %s
                """, (f"%{area_of_expertise}%",))
            else:
                cursor.execute("SELECT * FROM expert_availability WHERE status = 'ONLINE_AVAILABLE'")
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # Consultation Request Management
    def create_consultation_request(self, user_id: int, issue_description: str, 
                                 area_of_expertise: str, priority: int = 1, 
                                 user_name: str = None, user_city: str = None,
                                 image_paths: list = None) -> int:
        """Create a new consultation request"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            image_paths_str = ','.join(image_paths) if image_paths else None
            
            cursor.execute("""
                INSERT INTO consultation_requests 
                (user_id, user_name, user_city, area_of_expertise, issue_description, 
                 image_paths, priority)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING request_id
            """, (user_id, user_name, user_city, area_of_expertise, 
                   issue_description, image_paths_str, priority))
            
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_waiting_requests(self, area_of_expertise: str = None, limit: int = 10) -> List[Dict]:
        """Get waiting consultation requests with enhanced fields"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if area_of_expertise:
                cursor.execute("""
                    SELECT * FROM consultation_requests 
                    WHERE status = 'WAITING' AND area_of_expertise = %s
                    ORDER BY priority DESC, created_at ASC
                    LIMIT %s
                """, (area_of_expertise, limit))
            else:
                cursor.execute("""
                    SELECT * FROM consultation_requests 
                    WHERE status = 'WAITING'
                    ORDER BY priority DESC, created_at ASC
                    LIMIT %s
                """, (limit,))
            
            requests = [dict(row) for row in cursor.fetchall()]
            
            # Parse image paths
            for request in requests:
                if request['image_paths']:
                    request['image_paths'] = request['image_paths'].split(',')
                else:
                    request['image_paths'] = []
            
            return requests
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def assign_consultation_request(self, request_id: int, expert_id: int, assigned_reason: str = None) -> bool:
        """Assign a consultation request to an expert"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            # Update request status and assign expert
            cursor.execute("""
                UPDATE consultation_requests 
                SET status = 'ASSIGNED', expert_id = %s, 
                    assigned_at = CURRENT_TIMESTAMP
                WHERE request_id = %s AND status = 'WAITING'
            """, (expert_id, request_id))
            
            success = cursor.rowcount > 0
            if success:
                # Update expert status to BUSY
                self.update_expert_status(expert_id, 'BUSY', request_id)
                
                # Log assignment
                self._log_activity(expert_id, "CONSULTATION_ASSIGNED", 
                                {"request_id": request_id, "assigned_reason": assigned_reason})
            
            conn.commit()
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def start_consultation(self, request_id: int, expert_id: int) -> bool:
        """Start a consultation"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE consultation_requests 
                SET status = 'ACTIVE', started_at = CURRENT_TIMESTAMP
                WHERE request_id = %s AND expert_id = %s AND status = 'ASSIGNED'
            """, (request_id, expert_id))
            
            success = cursor.rowcount > 0
            if success:
                # Log start
                self._log_activity(expert_id, "CONSULTATION_STARTED", {"request_id": request_id})
            
            conn.commit()
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def complete_consultation(self, request_id: int, expert_id: int) -> bool:
        """Complete a consultation"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE consultation_requests 
                SET status = 'COMPLETED', completed_at = CURRENT_TIMESTAMP
                WHERE request_id = %s AND expert_id = %s AND status = 'ACTIVE'
            """, (request_id, expert_id))
            
            success = cursor.rowcount > 0
            if success:
                # Update expert status back to ONLINE_AVAILABLE
                self.update_expert_status(expert_id, 'ONLINE_AVAILABLE')
                
                # Update consultation count
                cursor.execute("""
                    UPDATE expert_availability 
                    SET total_consultations = total_consultations + 1
                    WHERE expert_id = %s
                """, (expert_id,))
                
                # Log completion
                self._log_activity(expert_id, "CONSULTATION_COMPLETED", {"request_id": request_id})
            
            conn.commit()
            return success
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def reject_consultation_request(self, request_id: int, expert_id: int, rejection_reason: str = None) -> bool:
        """Reject a consultation request"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE consultation_requests 
                SET status = 'WAITING', expert_id = NULL, 
                    assigned_at = NULL, assigned_reason = NULL
                WHERE request_id = %s AND expert_id = %s AND status = 'ASSIGNED'
            """, (request_id, expert_id))
            
            success = cursor.rowcount > 0
            if success:
                # Update expert status back to ONLINE_AVAILABLE
                self.update_expert_status(expert_id, 'ONLINE_AVAILABLE')
                
                # Log rejection
                self._log_activity(expert_id, "CONSULTATION_REJECTED", 
                                {"request_id": request_id, "rejection_reason": rejection_reason})
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_expert_active_consultation(self, expert_id: int) -> Optional[Dict]:
        """Get expert's current active consultation"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT cr.* FROM consultation_requests cr
                JOIN expert_availability ea ON cr.request_id = ea.current_consultation_id
                WHERE ea.expert_id = %s AND ea.status = 'BUSY'
            """, (expert_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_expert_requests(self, expert_id: int, status: str = None, limit: int = 10) -> List[Dict]:
        """Get expert's consultation requests"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            if status:
                cursor.execute("""
                    SELECT * FROM consultation_requests 
                    WHERE expert_id = %s AND status = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (expert_id, status, limit))
            else:
                cursor.execute("""
                    SELECT * FROM consultation_requests 
                    WHERE expert_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (expert_id, limit))
            
            requests = [dict(row) for row in cursor.fetchall()]
            
            # Parse image paths
            for request in requests:
                if request['image_paths']:
                    request['image_paths'] = request['image_paths'].split(',')
                else:
                    request['image_paths'] = []
            
            return requests
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_demand_metrics(self, area_of_expertise: str) -> Dict:
        """Get current demand metrics for an area of expertise"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Count waiting requests
            cursor.execute("""
                SELECT COUNT(*) as waiting_count 
                FROM consultation_requests 
                WHERE status = 'WAITING' AND area_of_expertise = %s
            """, (area_of_expertise,))
            waiting_count = cursor.fetchone()['waiting_count']
            
            # Count available experts
            cursor.execute("""
                SELECT COUNT(*) as available_count 
                FROM expert_availability ea
                JOIN car_service_workers w ON ea.expert_id = w.id
                WHERE ea.status = 'ONLINE_AVAILABLE' AND w.skills LIKE %s
            """, (f"%{area_of_expertise}%",))
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
                VALUES (%s, %s, %s, %s)
            """, (area_of_expertise, waiting_count, available_count, demand_level))
            
            conn.commit()
            
            return {
                'area_of_expertise': area_of_expertise,
                'waiting_requests': waiting_count,
                'available_experts': available_count,
                'demand_level': demand_level
            }
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_expert_performance_stats(self, expert_id: int, days: int = 30) -> Dict:
        """Get expert performance statistics"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Get completed consultations
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_consultations,
                    AVG(CASE WHEN cr.completed_at IS NOT NULL 
                        THEN EXTRACT(EPOCH FROM (cr.completed_at - cr.started_at)) / 60
                        ELSE NULL END) as avg_duration_minutes,
                    AVG(CASE WHEN cr.assigned_at IS NOT NULL AND cr.started_at IS NOT NULL
                        THEN EXTRACT(EPOCH FROM (cr.started_at - cr.assigned_at)) / 60
                        ELSE NULL END) as avg_response_time_minutes
                FROM consultation_requests cr
                WHERE cr.expert_id = %s 
                AND cr.status = 'COMPLETED'
                AND cr.created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            """, (expert_id, days))
            
            stats = cursor.fetchone()
            
            return {
                'total_consultations': stats['total_consultations'] or 0,
                'avg_duration_minutes': round(float(stats['avg_duration_minutes'] or 0), 2),
                'avg_response_time_minutes': round(float(stats['avg_response_time_minutes'] or 0), 2),
                'days_period': days
            }
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_activity_logs(self, expert_id: int, limit: int = 50) -> List[Dict]:
        """Get expert activity logs"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM activity_logs 
                WHERE expert_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """, (expert_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_expert_activity_logs(self, expert_id: int, limit: int = 50) -> List[Dict]:
        """Get expert activity logs (alias for get_activity_logs)"""
        return self.get_activity_logs(expert_id, limit)
    
    def _log_activity(self, expert_id: int, event_type: str, event_data: Dict = None):
        """Log expert activity"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO activity_logs (expert_id, event_type, event_data)
                VALUES (%s, %s, %s)
            """, (expert_id, event_type, str(event_data) if event_data else None))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_available_experts_by_category(self, category: str) -> List[Dict]:
        """Get available experts by category"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT ea.expert_id, ea.status, ea.rating, ae.name, ae.area_of_expertise as expertise, ae.experience_years
                FROM expert_availability ea
                JOIN automobile_experts ae ON ea.expert_id = ae.id
                WHERE ea.status = 'ONLINE_AVAILABLE' AND ae.area_of_expertise = %s
            """, (category,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            conn.rollback()
            print(f"DB Error: {e}")
            # If automobile_experts table doesn't exist or other error, fallback to general search
            try:
                cursor.execute("""
                    SELECT ea.expert_id, ea.status, ea.rating
                    FROM expert_availability ea
                    WHERE ea.status = 'ONLINE_AVAILABLE'
                """)
                return [dict(row) for row in cursor.fetchall()]
            except:
                return []
        finally:
            cursor.close()
            conn.close()

    def get_expert_consultation_history(self, expert_id: int, limit: int = 100) -> list:
        """Get expert's completed consultation history"""
        load_dotenv()
        conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Query the consultation history
            cursor.execute("""
                SELECT 
                    cr.request_id,
                    cr.user_name,
                    cr.user_city,
                    cr.issue_description,
                    cr.area_of_expertise,
                    cr.created_at,
                    cr.assigned_at,
                    cr.started_at,
                    cr.completed_at,
                    cr.status,
                    cr.expert_id
            FROM consultation_requests cr
            WHERE cr.expert_id = %s 
            AND cr.status = 'COMPLETED'
            ORDER BY cr.completed_at DESC
            LIMIT %s
        """, (expert_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"Error in get_expert_consultation_history: {str(e)}")
            return []
        finally:
            cursor.close()
            conn.close()

# Create database instance
expert_availability_db = ExpertAvailabilityDB()
