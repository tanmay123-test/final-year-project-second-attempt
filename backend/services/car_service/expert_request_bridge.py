"""
Expert Request Bridge
Synchronizes requests between ask_expert and expert_availability systems
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict

class ExpertRequestBridge:
    def __init__(self):
        self.ask_expert_db_path = os.path.join(os.path.dirname(__file__), 'ask_expert', 'ask_expert.db')
        self.expert_availability_db_path = os.path.join(os.path.dirname(__file__), 'expert_availability.db')
    
    def sync_pending_requests(self):
        """Sync pending requests from ask_expert to expert_availability"""
        try:
            # Get pending requests from ask_expert
            ask_conn = sqlite3.connect(self.ask_expert_db_path)
            ask_cursor = ask_conn.cursor()
            
            ask_cursor.execute("""
                SELECT id, user_id, expert_category, problem_description, status, created_at
                FROM expert_requests 
                WHERE status IN ('WAITING_QUEUE', 'ASSIGNED') 
                AND id NOT IN (
                    SELECT request_id FROM consultation_requests 
                    WHERE request_id IS NOT NULL
                )
                ORDER BY created_at ASC
            """)
            
            pending_requests = ask_cursor.fetchall()
            ask_conn.close()
            
            if not pending_requests:
                return {"synced": 0, "message": "No pending requests to sync"}
            
            # Insert into expert_availability system
            av_conn = sqlite3.connect(self.expert_availability_db_path)
            av_cursor = av_conn.cursor()
            
            synced_count = 0
            for request in pending_requests:
                request_id, user_id, category, description, status, created_at = request
                
                # Map category names
                category_mapping = {
                    'Body & Interior Expert': 'Body & Interior',
                    'Brake & Suspension Expert': 'Brake & Suspension', 
                    'Electrical Expert': 'Electrical',
                    'Engine Expert': 'Engine',
                    'General Expert': 'General'
                }
                
                mapped_category = category_mapping.get(category, category)
                
                # Insert into consultation_requests
                av_cursor.execute("""
                    INSERT OR REPLACE INTO consultation_requests 
                    (request_id, user_id, issue_description, area_of_expertise, 
                     priority, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (request_id, user_id, description, mapped_category, 
                       1, status, created_at))
                
                synced_count += 1
            
            av_conn.commit()
            av_conn.close()
            
            return {"synced": synced_count, "message": f"Synced {synced_count} requests"}
            
        except Exception as e:
            return {"synced": 0, "error": str(e)}
    
    def get_all_pending_requests(self) -> List[Dict]:
        """Get all pending requests from both systems"""
        try:
            # Get from expert_availability
            av_conn = sqlite3.connect(self.expert_availability_db_path)
            av_cursor = av_conn.cursor()
            
            av_cursor.execute("""
                SELECT request_id, user_id, area_of_expertise, issue_description, 
                       status, created_at, assigned_at
                FROM consultation_requests 
                WHERE status = 'WAITING'
                ORDER BY created_at ASC
            """)
            
            av_requests = [dict(row) for row in av_cursor.fetchall()]
            av_conn.close()
            
            # Get from ask_expert
            ask_conn = sqlite3.connect(self.ask_expert_db_path)
            ask_cursor = ask_conn.cursor()
            
            ask_cursor.execute("""
                SELECT id, user_id, expert_category, problem_description, 
                       status, created_at
                FROM expert_requests 
                WHERE status = 'WAITING_QUEUE'
                ORDER BY created_at ASC
            """)
            
            ask_requests = []
            for row in ask_cursor.fetchall():
                ask_requests.append({
                    'request_id': row[0],
                    'user_id': row[1],
                    'area_of_expertise': row[2],
                    'issue_description': row[3],
                    'status': row[4],
                    'created_at': row[5],
                    'assigned_at': None,
                    'source': 'ask_expert'
                })
            
            ask_conn.close()
            
            # Combine and sort by created_at
            all_requests = av_requests + ask_requests
            all_requests.sort(key=lambda x: x.get('created_at', ''))
            
            return all_requests
            
        except Exception as e:
            print(f"Error getting requests: {e}")
            return []
    
    def assign_request_to_expert(self, request_id: int, expert_id: int, expert_name: str) -> bool:
        """Assign a request to an expert"""
        try:
            av_conn = sqlite3.connect(self.expert_availability_db_path)
            av_cursor = av_conn.cursor()
            
            # Update consultation_requests
            av_cursor.execute("""
                UPDATE consultation_requests 
                SET assigned_expert_id = ?, assigned_at = CURRENT_TIMESTAMP, status = 'ASSIGNED'
                WHERE request_id = ? AND status = 'WAITING'
            """, (expert_id, request_id))
            
            success = av_cursor.rowcount > 0
            av_conn.commit()
            av_conn.close()
            
            if success:
                # Also update ask_expert database if exists
                try:
                    ask_conn = sqlite3.connect(self.ask_expert_db_path)
                    ask_cursor = ask_conn.cursor()
                    
                    ask_cursor.execute("""
                        UPDATE expert_requests 
                        SET assigned_expert_id = ?, status = 'ASSIGNED'
                        WHERE id = ?
                    """, (expert_id, request_id))
                    
                    ask_conn.commit()
                    ask_conn.close()
                except:
                    pass  # Ignore if ask_expert doesn't have this column
            
            return success
            
        except Exception as e:
            print(f"Error assigning request: {e}")
            return False
    
    def get_expert_pending_requests(self, expert_id: int) -> List[Dict]:
        """Get pending requests for a specific expert"""
        try:
            av_conn = sqlite3.connect(self.expert_availability_db_path)
            av_cursor = av_conn.cursor()
            
            # Get expert's area of expertise
            from automobile_expert_db import automobile_expert_db
            expert = automobile_expert_db.get_expert_by_id(expert_id)
            
            if not expert:
                av_conn.close()
                return []
            
            expertise = expert.get('area_of_expertise', 'General')
            
            av_cursor.execute("""
                SELECT request_id, user_id, area_of_expertise, issue_description, 
                       status, created_at
                FROM consultation_requests 
                WHERE status = 'WAITING_QUEUE' AND area_of_expertise = ?
                ORDER BY created_at ASC
            """, (expertise,))
            
            requests = []
            for row in av_cursor.fetchall():
                requests.append({
                    'request_id': row[0],
                    'user_id': row[1],
                    'area_of_expertise': row[2],
                    'issue_description': row[3],
                    'status': row[4],
                    'created_at': row[5]
                })
            av_conn.close()
            
            return requests
            
        except Exception as e:
            print(f"Error getting expert requests: {e}")
            return []

    def update_request_status(self, request_id: int, status: str, expert_id: int = None) -> bool:
        """Update request status in ask_expert database"""
        try:
            ask_conn = sqlite3.connect(self.ask_expert_db_path)
            ask_cursor = ask_conn.cursor()
            
            if expert_id:
                ask_cursor.execute("""
                    UPDATE expert_requests 
                    SET status = ?, assigned_expert_id = ?
                    WHERE id = ?
                """, (status, expert_id, request_id))
            else:
                ask_cursor.execute("""
                    UPDATE expert_requests 
                    SET status = ?
                    WHERE id = ?
                """, (status, request_id))
            
            success = ask_cursor.rowcount > 0
            ask_conn.commit()
            ask_conn.close()
            
            return success
            
        except Exception as e:
            print(f"Error updating request status: {e}")
            return False

# Create bridge instance
expert_request_bridge = ExpertRequestBridge()
