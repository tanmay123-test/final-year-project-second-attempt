"""
Expert History and Performance Database
Manages consultation history, performance analytics, reputation, and expert profiles
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Database path
EXPERT_HISTORY_DB = os.path.join(os.path.dirname(__file__), 'expert_history.db')

class ExpertHistoryDB:
    def __init__(self):
        self.conn = sqlite3.connect(EXPERT_HISTORY_DB, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def get_conn(self):
        return sqlite3.connect(EXPERT_HISTORY_DB, check_same_thread=False)
    
    def create_tables(self):
        """Create all required tables for expert history and performance"""
        cursor = self.conn.cursor()
        
        # Expert requests table (consultation history)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expert_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                expert_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'WAITING_QUEUE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_at TIMESTAMP,
                resolved_at TIMESTAMP,
                consultation_duration_seconds INTEGER DEFAULT 0,
                resolution_status TEXT,
                assigned_reason TEXT,
                priority_level INTEGER DEFAULT 2,
                problem_description TEXT,
                user_name TEXT,
                user_city TEXT
            )
        """)
        
        # Expert profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expert_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                is_approved BOOLEAN DEFAULT 0,
                online_status TEXT DEFAULT 'OFFLINE',
                is_busy BOOLEAN DEFAULT 0,
                rating REAL DEFAULT 0.0,
                total_consultations INTEGER DEFAULT 0,
                completed_consultations INTEGER DEFAULT 0,
                reliability_score REAL DEFAULT 0.0,
                last_active TIMESTAMP,
                total_online_hours INTEGER DEFAULT 0,
                fair_assignment_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Expert reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expert_reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                expert_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                request_id INTEGER,
                reason TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'PENDING'
            )
        """)
        
        # Expert badges table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expert_badges (
                badge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                expert_id INTEGER NOT NULL,
                badge_name TEXT NOT NULL,
                badge_type TEXT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Performance analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expert_performance_analytics (
                analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
                expert_id INTEGER NOT NULL,
                date DATE NOT NULL,
                total_consultations INTEGER DEFAULT 0,
                completed_consultations INTEGER DEFAULT 0,
                resolution_rate REAL DEFAULT 0.0,
                average_response_seconds INTEGER DEFAULT 0,
                average_duration_seconds INTEGER DEFAULT 0,
                user_satisfaction_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Queue handling table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consultation_queue (
                queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                priority_level INTEGER DEFAULT 2,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_at TIMESTAMP,
                expert_id INTEGER,
                status TEXT DEFAULT 'WAITING_QUEUE'
            )
        """)
        
        self.conn.commit()
    
    # Consultation History Management
    def get_consultation_history(self, expert_id: int, limit: int = 50) -> List[Dict]:
        """Get expert's consultation history"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                id as request_id,
                user_id,
                user_name,
                category,
                status,
                created_at,
                resolved_at,
                consultation_duration_seconds,
                resolution_status,
                assigned_reason,
                problem_description
            FROM expert_requests
            WHERE expert_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (expert_id, limit))
        return [dict(row) for row in cursor.fetchall()]
    
    def add_consultation_request(self, user_id: int, category: str, problem_description: str,
                              user_name: str, user_city: str, priority_level: int = 2) -> int:
        """Add new consultation request to queue"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO expert_requests 
            (user_id, category, problem_description, user_name, user_city, 
             priority_level, status)
            VALUES (?, ?, ?, ?, ?, ?, 'WAITING_QUEUE')
        """, (user_id, category, problem_description, user_name, user_city, priority_level))
        
        request_id = cursor.lastrowid
        
        # Add to queue
        cursor.execute("""
            INSERT INTO consultation_queue 
            (request_id, user_id, category, priority_level)
            VALUES (?, ?, ?, ?)
        """, (request_id, user_id, category, priority_level))
        
        self.conn.commit()
        return request_id
    
    def assign_consultation_request(self, request_id: int, expert_id: int, assigned_reason: str) -> bool:
        """Assign consultation request to expert"""
        cursor = self.conn.cursor()
        
        # Update request status
        cursor.execute("""
            UPDATE expert_requests 
            SET expert_id = ?, status = 'ASSIGNED', assigned_at = CURRENT_TIMESTAMP,
                assigned_reason = ?
            WHERE id = ? AND status = 'WAITING_QUEUE'
        """, (expert_id, assigned_reason, request_id))
        
        # Update queue
        cursor.execute("""
            UPDATE consultation_queue 
            SET expert_id = ?, assigned_at = CURRENT_TIMESTAMP, status = 'ASSIGNED'
            WHERE request_id = ?
        """, (expert_id, request_id))
        
        success = cursor.rowcount > 0
        self.conn.commit()
        return success
    
    def start_consultation(self, request_id: int, expert_id: int) -> bool:
        """Start consultation (IN_PROGRESS)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE expert_requests 
            SET status = 'IN_PROGRESS'
            WHERE id = ? AND expert_id = ? AND status = 'ASSIGNED'
        """, (request_id, expert_id))
        
        success = cursor.rowcount > 0
        self.conn.commit()
        return success
    
    def complete_consultation(self, request_id: int, expert_id: int, duration_seconds: int = 0) -> bool:
        """Complete consultation"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE expert_requests 
            SET status = 'RESOLVED', resolved_at = CURRENT_TIMESTAMP,
                consultation_duration_seconds = ?, resolution_status = 'COMPLETED'
            WHERE id = ? AND expert_id = ? AND status = 'IN_PROGRESS'
        """, (duration_seconds, request_id, expert_id))
        
        # Remove from queue
        cursor.execute("""
            DELETE FROM consultation_queue WHERE request_id = ?
        """, (request_id,))
        
        success = cursor.rowcount > 0
        self.conn.commit()
        return success
    
    def get_waiting_queue(self, category: str = None) -> List[Dict]:
        """Get waiting consultation queue"""
        cursor = self.conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT * FROM consultation_queue 
                WHERE status = 'WAITING_QUEUE' AND category = ?
                ORDER BY priority_level DESC, created_at ASC
            """, (category,))
        else:
            cursor.execute("""
                SELECT * FROM consultation_queue 
                WHERE status = 'WAITING_QUEUE'
                ORDER BY priority_level DESC, created_at ASC
            """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    # Expert Profile Management
    def get_expert_profile(self, expert_id: int) -> Optional[Dict]:
        """Get expert profile information"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM expert_profiles WHERE id = ?
        """, (expert_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_expert_profile(self, expert_id: int, updates: Dict) -> bool:
        """Update expert profile"""
        cursor = self.conn.cursor()
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [expert_id]
        
        cursor.execute(f"""
            UPDATE expert_profiles 
            SET {set_clause}
            WHERE id = ?
        """, values)
        
        success = cursor.rowcount > 0
        self.conn.commit()
        return success
    
    def update_expert_status(self, expert_id: int, status: str, is_busy: bool = None) -> bool:
        """Update expert online status"""
        cursor = self.conn.cursor()
        
        updates = {"online_status": status, "last_active": "CURRENT_TIMESTAMP"}
        if is_busy is not None:
            updates["is_busy"] = is_busy
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [expert_id]
        
        cursor.execute(f"""
            UPDATE expert_profiles 
            SET {set_clause}
            WHERE id = ?
        """, values)
        
        success = cursor.rowcount > 0
        self.conn.commit()
        return success
    
    # Performance Analytics
    def calculate_performance_metrics(self, expert_id: int, days: int = 30) -> Dict:
        """Calculate performance metrics for expert"""
        cursor = self.conn.cursor()
        
        # Get consultation stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_consultations,
                COUNT(CASE WHEN status = 'RESOLVED' THEN 1 END) as completed_consultations,
                AVG(CASE WHEN assigned_at IS NOT NULL AND created_at IS NOT NULL
                    THEN (julianday(assigned_at) - julianday(created_at)) * 24 * 60 * 60
                    ELSE NULL END) as avg_response_seconds,
                AVG(consultation_duration_seconds) as avg_duration_seconds
            FROM expert_requests
            WHERE expert_id = ?
            AND created_at >= date('now', '-{} days')
        """.format(days), (expert_id,))
        
        stats = cursor.fetchone()
        
        total_consultations = stats['total_consultations'] or 0
        completed_consultations = stats['completed_consultations'] or 0
        
        resolution_rate = (completed_consultations / total_consultations * 100) if total_consultations > 0 else 0
        
        return {
            'total_consultations': total_consultations,
            'completed_consultations': completed_consultations,
            'resolution_rate': round(resolution_rate, 2),
            'average_response_seconds': int(stats['avg_response_seconds'] or 0),
            'average_duration_seconds': int(stats['avg_duration_seconds'] or 0)
        }
    
    def update_performance_analytics(self, expert_id: int, metrics: Dict):
        """Update performance analytics for expert"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO expert_performance_analytics 
            (expert_id, date, total_consultations, completed_consultations,
             resolution_rate, average_response_seconds, average_duration_seconds)
            VALUES (?, date('now'), ?, ?, ?, ?, ?)
        """, (expert_id, metrics['total_consultations'], metrics['completed_consultations'],
               metrics['resolution_rate'], metrics['average_response_seconds'],
               metrics['average_duration_seconds']))
        self.conn.commit()
    
    # Fair Assignment Score
    def calculate_fair_assignment_score(self, expert_id: int) -> float:
        """Calculate fair assignment score for expert"""
        cursor = self.conn.cursor()
        
        # Get expert profile
        profile = self.get_expert_profile(expert_id)
        if not profile:
            return 0.0
        
        score = 50.0  # Base score
        
        # Factor 1: Idle time (higher if idle longer)
        if profile['last_active']:
            idle_hours = (datetime.now() - datetime.strptime(profile['last_active'], '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600
            score += min(idle_hours, 20)  # Max 20 points for idle time
        
        # Factor 2: Completion rate (higher for better completion)
        metrics = self.calculate_performance_metrics(expert_id, 30)
        if metrics['resolution_rate'] > 90:
            score += 20
        elif metrics['resolution_rate'] > 80:
            score += 10
        elif metrics['resolution_rate'] > 70:
            score += 5
        
        # Factor 3: Rating (higher for better rating)
        if profile['rating'] >= 4.5:
            score += 10
        elif profile['rating'] >= 4.0:
            score += 5
        
        return min(score, 100.0)  # Cap at 100
    
    # Badge Management
    def award_badge(self, expert_id: int, badge_name: str, badge_type: str) -> bool:
        """Award badge to expert"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO expert_badges 
            (expert_id, badge_name, badge_type)
            VALUES (?, ?, ?)
        """, (expert_id, badge_name, badge_type))
        
        success = cursor.rowcount > 0
        self.conn.commit()
        return success
    
    def get_expert_badges(self, expert_id: int) -> List[Dict]:
        """Get expert's badges"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM expert_badges 
            WHERE expert_id = ?
            ORDER BY earned_at DESC
        """, (expert_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def check_and_award_badges(self, expert_id: int):
        """Check performance and award appropriate badges"""
        metrics = self.calculate_performance_metrics(expert_id, 30)
        profile = self.get_expert_profile(expert_id)
        
        if not profile:
            return
        
        # Trusted Expert badge
        if metrics['resolution_rate'] > 90:
            self.award_badge(expert_id, "Trusted Expert", "PERFORMANCE")
        
        # Fast Responder badge
        if metrics['average_response_seconds'] < 60:
            self.award_badge(expert_id, "Fast Responder", "RESPONSE_TIME")
        
        # Top Rated badge
        if profile['rating'] >= 4.5:
            self.award_badge(expert_id, "Top Rated", "RATING")
        
        # High Volume badge
        if metrics['completed_consultations'] >= 50:
            self.award_badge(expert_id, "High Volume", "VOLUME")
    
    # Report Management
    def create_report(self, expert_id: int, user_id: int, request_id: int, 
                    reason: str, description: str = None) -> int:
        """Create a report against user"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO expert_reports 
            (expert_id, user_id, request_id, reason, description)
            VALUES (?, ?, ?, ?, ?)
        """, (expert_id, user_id, request_id, reason, description))
        
        report_id = cursor.lastrowid
        self.conn.commit()
        return report_id
    
    def get_expert_reports(self, expert_id: int) -> List[Dict]:
        """Get reports created by expert"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM expert_reports 
            WHERE expert_id = ?
            ORDER BY created_at DESC
        """, (expert_id,))
        return [dict(row) for row in cursor.fetchall()]

# Create database instance
expert_history_db = ExpertHistoryDB()
