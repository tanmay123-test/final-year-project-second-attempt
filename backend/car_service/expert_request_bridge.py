"""
Expert Request Bridge
Synchronizes requests between ask_expert and expert_availability systems
"""

import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import List, Dict
from .expert_availability_db import expert_availability_db
from expert_db import ExpertDB

class ExpertRequestBridge:
    def __init__(self):
        self.expert_db = ExpertDB()
    
    def sync_pending_requests(self):
        """Sync pending requests from ask_expert to expert_availability"""
        try:
            # Both tables are in the same database now
            conn = self.expert_db.get_conn()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            try:
                # Get pending requests from expert_requests (ask_expert system)
                cursor.execute("""
                    SELECT id, user_id, category as expert_category, description as problem_description, status, created_at
                    FROM expert_requests 
                    WHERE status IN ('WAITING_QUEUE', 'ASSIGNED', 'pending') 
                    AND id NOT IN (
                        SELECT request_id FROM consultation_requests 
                        WHERE request_id IS NOT NULL
                    )
                    ORDER BY created_at ASC
                """)
                
                pending_requests = cursor.fetchall()
                
                if not pending_requests:
                    return {"synced": 0, "message": "No pending requests to sync"}
                
                synced_count = 0
                for request in pending_requests:
                    # Map category names if needed
                    category_mapping = {
                        'Body & Interior Expert': 'Body & Interior',
                        'Brake & Suspension Expert': 'Brake & Suspension', 
                        'Electrical Expert': 'Electrical',
                        'Engine Expert': 'Engine',
                        'General Expert': 'General'
                    }
                    
                    mapped_category = category_mapping.get(request['expert_category'], request['expert_category'])
                    
                    # Insert into consultation_requests (expert_availability system)
                    cursor.execute("""
                        INSERT INTO consultation_requests 
                        (request_id, user_id, issue_description, area_of_expertise, 
                         priority, status, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (request_id) DO UPDATE SET
                        issue_description = EXCLUDED.issue_description,
                        area_of_expertise = EXCLUDED.area_of_expertise,
                        status = EXCLUDED.status
                    """, (request['id'], request['user_id'], request['problem_description'], 
                           mapped_category, 1, request['status'], request['created_at']))
                    
                    synced_count += 1
                
                conn.commit()
                return {"synced": synced_count, "message": f"Synced {synced_count} requests"}
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            return {"synced": 0, "error": str(e)}
    
    def get_all_pending_requests(self) -> List[Dict]:
        """Get all pending requests from both systems"""
        try:
            conn = self.expert_db.get_conn()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            try:
                # Get from consultation_requests
                cursor.execute("""
                    SELECT request_id, user_id, area_of_expertise, issue_description, 
                           status, created_at, assigned_at
                    FROM consultation_requests 
                    WHERE status = 'WAITING'
                    ORDER BY created_at ASC
                """)
                av_requests = [dict(row) for row in cursor.fetchall()]
                
                # Get from expert_requests
                cursor.execute("""
                    SELECT id as request_id, user_id, category as area_of_expertise, 
                           description as issue_description, status, created_at
                    FROM expert_requests 
                    WHERE status = 'WAITING_QUEUE' OR status = 'pending'
                    ORDER BY created_at ASC
                """)
                ask_requests = []
                for row in cursor.fetchall():
                    ask_requests.append({
                        'request_id': row['request_id'],
                        'user_id': row['user_id'],
                        'area_of_expertise': row['area_of_expertise'],
                        'issue_description': row['issue_description'],
                        'status': row['status'],
                        'created_at': row['created_at'],
                        'assigned_at': None,
                        'source': 'ask_expert'
                    })
                
                # Combine and sort by created_at
                all_requests = av_requests + ask_requests
                all_requests.sort(key=lambda x: str(x.get('created_at', '')))
                
                return all_requests
            finally:
                cursor.close()
                conn.close()
            
        except Exception as e:
            print(f"Error getting requests: {e}")
            return []
    
    def assign_request_to_expert(self, request_id: int, expert_id: int, expert_name: str) -> bool:
        """Assign a request to an expert"""
        try:
            conn = self.expert_db.get_conn()
            cursor = conn.cursor()
            
            try:
                # Update consultation_requests
                cursor.execute("""
                    UPDATE consultation_requests 
                    SET expert_id = %s, assigned_at = CURRENT_TIMESTAMP, status = 'ASSIGNED'
                    WHERE request_id = %s AND status = 'WAITING'
                """, (expert_id, request_id))
                
                success = cursor.rowcount > 0
                
                # Also update expert_requests
                cursor.execute("""
                    UPDATE expert_requests 
                    SET expert_id = %s, status = 'ASSIGNED', updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (expert_id, request_id))
                
                conn.commit()
                return success
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            print(f"Error assigning request: {e}")
            return False
    
    def get_expert_pending_requests(self, expert_id: int) -> List[Dict]:
        """Get pending requests for a specific expert"""
        try:
            conn = self.expert_db.get_conn()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            try:
                # Get expert's category
                cursor.execute("SELECT category FROM experts WHERE id = %s", (expert_id,))
                row = cursor.fetchone()
                if not row:
                    return []
                
                expertise = row['category']
                
                cursor.execute("""
                    SELECT request_id, user_id, area_of_expertise, issue_description, 
                           status, created_at
                    FROM consultation_requests 
                    WHERE status = 'WAITING_QUEUE' AND area_of_expertise = %s
                    ORDER BY created_at ASC
                """, (expertise,))
                
                requests = [dict(row) for row in cursor.fetchall()]
                return requests
            finally:
                cursor.close()
                conn.close()
            
        except Exception as e:
            print(f"Error getting expert requests: {e}")
            return []

    def update_request_status(self, request_id: int, status: str, expert_id: int = None) -> bool:
        """Update request status in ask_expert database"""
        try:
            conn = self.expert_db.get_conn()
            cursor = conn.cursor()
            
            try:
                if expert_id:
                    cursor.execute("""
                        UPDATE expert_requests 
                        SET status = %s, expert_id = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (status, expert_id, request_id))
                else:
                    cursor.execute("""
                        UPDATE expert_requests 
                        SET status = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (status, request_id))
                
                success = cursor.rowcount > 0
                conn.commit()
                return success
            finally:
                cursor.close()
                conn.close()
            
        except Exception as e:
            print(f"Error updating request status: {e}")
            return False

# Create bridge instance
expert_request_bridge = ExpertRequestBridge()