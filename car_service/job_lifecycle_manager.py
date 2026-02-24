"""
Job Lifecycle Manager - Manages job status transitions and workflow
Handles all job state changes with validation and logging
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

class JobStatus(Enum):
    """Job status enumeration"""
    PENDING = "PENDING"
    OFFERED = "OFFERED"
    ACCEPTED = "ACCEPTED"
    ON_THE_WAY = "ON_THE_WAY"
    ARRIVED = "ARRIVED"
    WORKING = "WORKING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class JobLifecycleManager:
    """Manages complete job lifecycle with state validation"""
    
    def __init__(self):
        # Define valid status transitions
        self.valid_transitions = {
            JobStatus.PENDING: [JobStatus.OFFERED, JobStatus.CANCELLED],
            JobStatus.OFFERED: [JobStatus.ACCEPTED, JobStatus.REJECTED, JobStatus.CANCELLED],
            JobStatus.ACCEPTED: [JobStatus.ON_THE_WAY, JobStatus.CANCELLED],
            JobStatus.ON_THE_WAY: [JobStatus.ARRIVED, JobStatus.CANCELLED],
            JobStatus.ARRIVED: [JobStatus.WORKING, JobStatus.CANCELLED],
            JobStatus.WORKING: [JobStatus.COMPLETED, JobStatus.CANCELLED],
            JobStatus.COMPLETED: [],  # Terminal state
            JobStatus.CANCELLED: [],   # Terminal state
            JobStatus.REJECTED: []      # Terminal state
        }
        
        # Status change reasons
        self.status_reasons = {
            JobStatus.PENDING: "Job created and waiting for dispatch",
            JobStatus.OFFERED: "Job offered to worker",
            JobStatus.ACCEPTED: "Worker accepted the job",
            JobStatus.ON_THE_WAY: "Worker is en route to location",
            JobStatus.ARRIVED: "Worker has arrived at location",
            JobStatus.WORKING: "Work has started",
            JobStatus.COMPLETED: "Job has been completed successfully",
            JobStatus.CANCELLED: "Job was cancelled",
            JobStatus.REJECTED: "Worker rejected the job offer"
        }
    
    def create_job(self, user_id: int, user_lat: float, user_long: float,
                  issue_text: str, service_type: str, priority: str = 'NORMAL') -> Dict:
        """Create new job with initial status"""
        try:
            conn = sqlite3.connect('car_service.db')
            cursor = conn.cursor()
            
            # Insert new job
            cursor.execute("""
                INSERT INTO mechanic_jobs 
                (user_id, user_lat, user_long, issue_text, service_type, 
                 priority, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, user_lat, user_long, issue_text, service_type,
                   priority, JobStatus.PENDING.value, datetime.now()))
            
            job_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Log status change
            self._log_status_change(job_id, None, JobStatus.PENDING.value, 
                                "Job created", None)
            
            return {
                'success': True,
                'job_id': job_id,
                'status': JobStatus.PENDING.value,
                'message': 'Job created successfully'
            }
            
        except Exception as e:
            print(f"Error creating job: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_job_status(self, job_id: int, new_status: str, worker_id: int = None,
                        reason: str = None, metadata: Dict = None) -> Dict:
        """Update job status with validation"""
        try:
            # Get current status
            current_status = self.get_job_status(job_id)
            if not current_status:
                return {'success': False, 'error': 'Job not found'}
            
            # Validate transition
            validation = self._validate_status_transition(
                current_status['status'], new_status
            )
            
            if not validation['valid']:
                return {
                    'success': False,
                    'error': f'Invalid status transition: {validation["reason"]}'
                }
            
            # Update job status
            conn = sqlite3.connect('car_service.db')
            cursor = conn.cursor()
            
            # Build update query based on status
            update_fields = ['status = ?', 'updated_at = ?']
            update_values = [new_status, datetime.now()]
            
            # Add status-specific fields
            if new_status == JobStatus.ACCEPTED.value:
                update_fields.append('worker_id = ?')
                update_fields.append('accepted_at = ?')
                update_values.extend([worker_id, datetime.now()])
            
            elif new_status == JobStatus.ON_THE_WAY.value:
                update_fields.append('started_at = ?')
                update_values.append(datetime.now())
            
            elif new_status == JobStatus.ARRIVED.value:
                update_fields.append('arrived_at = ?')
                update_values.append(datetime.now())
            
            elif new_status == JobStatus.WORKING.value:
                update_fields.append('work_started_at = ?')
                update_values.append(datetime.now())
            
            elif new_status == JobStatus.COMPLETED.value:
                update_fields.append('completion_time = ?')
                update_values.append(datetime.now())
            
            elif new_status == JobStatus.CANCELLED.value:
                update_fields.append('cancelled_at = ?')
                update_fields.append('cancellation_reason = ?')
                update_values.extend([datetime.now(), reason or 'User cancelled'])
            
            # Execute update
            update_values.append(job_id)
            cursor.execute(f"""
                UPDATE mechanic_jobs
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, update_values)
            
            conn.commit()
            conn.close()
            
            # Log status change
            log_reason = reason or self.status_reasons.get(JobStatus(new_status), "Status updated")
            self._log_status_change(job_id, worker_id, new_status, log_reason, metadata)
            
            return {
                'success': True,
                'job_id': job_id,
                'old_status': current_status['status'],
                'new_status': new_status,
                'message': f'Status updated to {new_status}'
            }
            
        except Exception as e:
            print(f"Error updating job status: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_job_status(self, job_id: int) -> Optional[Dict]:
        """Get current job status"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT status, worker_id, created_at, updated_at
                FROM mechanic_jobs
                WHERE id = ?
            """, (job_id,))
            
            job = cursor.fetchone()
            conn.close()
            
            if job:
                return dict(job)
            return None
            
        except Exception as e:
            print(f"Error getting job status: {e}")
            return None
    
    def _validate_status_transition(self, current_status: str, new_status: str) -> Dict:
        """Validate if status transition is allowed"""
        try:
            current_enum = JobStatus(current_status)
            new_enum = JobStatus(new_status)
            
            valid_next_states = self.valid_transitions.get(current_enum, [])
            
            if new_enum in valid_next_states:
                return {'valid': True}
            else:
                return {
                    'valid': False,
                    'reason': f'Cannot transition from {current_status} to {new_status}',
                    'allowed_states': [state.value for state in valid_next_states]
                }
                
        except ValueError as e:
            return {
                'valid': False,
                'reason': f'Invalid status: {str(e)}'
            }
    
    def _log_status_change(self, job_id: int, worker_id: Optional[int], 
                         new_status: str, reason: str, metadata: Optional[Dict]):
        """Log status change for audit trail"""
        try:
            conn = sqlite3.connect('car_service.db')
            cursor = conn.cursor()
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT INTO job_status_logs 
                (job_id, worker_id, status, reason, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (job_id, worker_id, new_status, reason, metadata_json, 
                   datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error logging status change: {e}")
    
    def get_job_history(self, job_id: int) -> List[Dict]:
        """Get complete job status history"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM job_status_logs
                WHERE job_id = ?
                ORDER BY timestamp ASC
            """, (job_id,))
            
            history = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return history
            
        except Exception as e:
            print(f"Error getting job history: {e}")
            return []
    
    def get_active_jobs(self, worker_id: int = None, user_id: int = None) -> List[Dict]:
        """Get all active jobs"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM mechanic_jobs
                WHERE status IN ('PENDING', 'OFFERED', 'ACCEPTED', 
                               'ON_THE_WAY', 'ARRIVED', 'WORKING')
            """
            params = []
            
            if worker_id:
                query += " AND worker_id = ?"
                params.append(worker_id)
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            jobs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return jobs
            
        except Exception as e:
            print(f"Error getting active jobs: {e}")
            return []
    
    def get_completed_jobs(self, worker_id: int = None, user_id: int = None,
                         days: int = 30) -> List[Dict]:
        """Get completed jobs"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM mechanic_jobs
                WHERE status = 'COMPLETED'
                AND completion_time > datetime('now', '-{} days')
            """.format(days)
            
            params = []
            
            if worker_id:
                query += " AND worker_id = ?"
                params.append(worker_id)
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            query += " ORDER BY completion_time DESC"
            
            cursor.execute(query, params)
            jobs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return jobs
            
        except Exception as e:
            print(f"Error getting completed jobs: {e}")
            return []
    
    def cancel_job(self, job_id: int, reason: str, cancelled_by: str,
                  cancelled_by_id: int) -> Dict:
        """Cancel job with proper validation"""
        try:
            current_status = self.get_job_status(job_id)
            if not current_status:
                return {'success': False, 'error': 'Job not found'}
            
            # Check if job can be cancelled
            if current_status['status'] in [JobStatus.COMPLETED.value, 
                                       JobStatus.CANCELLED.value]:
                return {
                    'success': False,
                    'error': f'Cannot cancel job in {current_status["status"]} status'
                }
            
            # Update job status
            conn = sqlite3.connect('car_service.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE mechanic_jobs
                SET status = 'CANCELLED', cancelled_at = ?, 
                    cancellation_reason = ?, cancelled_by = ?, cancelled_by_id = ?
                WHERE id = ?
            """, (datetime.now(), reason, cancelled_by, cancelled_by_id, job_id))
            
            conn.commit()
            conn.close()
            
            # Log cancellation
            metadata = {
                'cancelled_by': cancelled_by,
                'cancelled_by_id': cancelled_by_id,
                'original_status': current_status['status']
            }
            
            self._log_status_change(job_id, None, JobStatus.CANCELLED.value, 
                                reason, metadata)
            
            # If worker was assigned, make them available again
            if current_status.get('worker_id'):
                self._make_worker_available(current_status['worker_id'])
            
            return {
                'success': True,
                'job_id': job_id,
                'message': 'Job cancelled successfully',
                'reason': reason
            }
            
        except Exception as e:
            print(f"Error cancelling job: {e}")
            return {'success': False, 'error': str(e)}
    
    def _make_worker_available(self, worker_id: int):
        """Make worker available again"""
        try:
            conn = sqlite3.connect('car_service.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE mechanics
                SET is_busy = 0
                WHERE id = ?
            """, (worker_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error making worker available: {e}")
    
    def get_job_metrics(self, worker_id: int = None, days: int = 30) -> Dict:
        """Get job performance metrics"""
        try:
            conn = sqlite3.connect('car_service.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Base query
            where_clause = "created_at > datetime('now', '-{} days')".format(days)
            params = []
            
            if worker_id:
                where_clause += " AND worker_id = ?"
                params.append(worker_id)
            
            # Get job statistics
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_jobs,
                    SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_jobs,
                    SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END) as cancelled_jobs,
                    SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected_jobs,
                    AVG(CASE WHEN status = 'COMPLETED' 
                          AND completion_time IS NOT NULL 
                          AND accepted_at IS NOT NULL
                          THEN (julianday(completion_time) - julianday(accepted_at)) * 24 * 60 
                          ELSE NULL END) as avg_completion_minutes
                FROM mechanic_jobs
                WHERE {where_clause}
            """, params)
            
            metrics = cursor.fetchone()
            conn.close()
            
            total_jobs = metrics['total_jobs'] or 0
            completed_jobs = metrics['completed_jobs'] or 0
            cancelled_jobs = metrics['cancelled_jobs'] or 0
            rejected_jobs = metrics['rejected_jobs'] or 0
            
            completion_rate = (completed_jobs / total_jobs) if total_jobs > 0 else 0
            cancellation_rate = (cancelled_jobs / total_jobs) if total_jobs > 0 else 0
            
            return {
                'period_days': days,
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'cancelled_jobs': cancelled_jobs,
                'rejected_jobs': rejected_jobs,
                'completion_rate': round(completion_rate * 100, 2),
                'cancellation_rate': round(cancellation_rate * 100, 2),
                'avg_completion_minutes': round(metrics['avg_completion_minutes'] or 0, 2)
            }
            
        except Exception as e:
            print(f"Error getting job metrics: {e}")
            return {'error': str(e)}
    
    def auto_cancel_stale_jobs(self, hours: int = 2):
        """Automatically cancel jobs that have been pending too long"""
        try:
            conn = sqlite3.connect('car_service.db')
            cursor = conn.cursor()
            
            # Cancel jobs pending for more than specified hours
            cursor.execute("""
                UPDATE mechanic_jobs
                SET status = 'CANCELLED', cancelled_at = ?,
                    cancellation_reason = 'Auto-cancelled due to timeout'
                WHERE status = 'PENDING'
                AND created_at < datetime('now', '-{} hours')
            """.format(hours), (datetime.now(),))
            
            cancelled_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"Auto-cancelled {cancelled_count} stale jobs")
            
        except Exception as e:
            print(f"Error auto-cancelling jobs: {e}")


# Global instance
job_lifecycle_manager = JobLifecycleManager()
