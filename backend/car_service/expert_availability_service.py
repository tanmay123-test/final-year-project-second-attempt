"""
Expert Availability Service Engine
Business logic for expert availability management, auto-assignment, and demand calculation
"""

import threading
import time
import psycopg2.extras
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from .expert_availability_db import expert_availability_db
from .automobile_expert_db import automobile_expert_db

class ExpertAvailabilityService:
    def __init__(self):
        self._lock = threading.Lock()
        self._auto_assignment_thread = None
        self._running = False
        self.start_auto_assignment_engine()
    
    def start_auto_assignment_engine(self):
        """Start the background auto-assignment engine"""
        if not self._running:
            self._running = True
            self._auto_assignment_thread = threading.Thread(target=self._auto_assignment_worker, daemon=True)
            self._auto_assignment_thread.start()
    
    def stop_auto_assignment_engine(self):
        """Stop the background auto-assignment engine"""
        self._running = False
        if self._auto_assignment_thread:
            self._auto_assignment_thread.join()
    
    def _auto_assignment_worker(self):
        """Background worker for automatic consultation assignment"""
        while self._running:
            try:
                with self._lock:
                    self._process_waiting_assignments()
                time.sleep(5)  # Check every 5 seconds
            except Exception:
                # Silently catch exceptions to prevent console spam during connection drops
                time.sleep(10)
    
    def _process_waiting_assignments(self):
        """Process waiting consultation requests and assign to available experts"""
        try:
            # Get all waiting requests
            waiting_requests = expert_availability_db.get_waiting_requests(limit=50)
            
            for request in waiting_requests:
                area_of_expertise = request.get('expert_category', request.get('area_of_expertise'))
                
                # Get available experts for this expertise
                available_experts = expert_availability_db.get_available_experts(area_of_expertise)
                
                if available_experts:
                    # Select expert (simple strategy: least busy)
                    selected_expert = self._select_best_expert(available_experts, request)
                    
                    if selected_expert:
                        # Calculate assignment reason
                        assigned_reason = self._calculate_assignment_reason(selected_expert, request)
                        
                        # Assign request to expert
                        success = expert_availability_db.assign_consultation_request(
                            request['request_id'], 
                            selected_expert['expert_id'],
                            assigned_reason
                        )
                        
                        if success:
                            print(f"Auto-assigned request {request['request_id']} to expert {selected_expert['expert_id']} ({assigned_reason})")
        except Exception:
            # Silently catch exceptions to prevent console spam
            pass
    
    def _calculate_assignment_reason(self, expert: Dict, request: Dict) -> str:
        """Calculate the assignment reason for transparency"""
        reasons = []
        
        # Check if expert is closest (simplified - would use geolocation in production)
        if expert.get('total_consultations', 0) < 5:
            reasons.append("Low workload expert")
        
        # Check if expert has highest rating
        if expert.get('rating', 0) >= 4.5:
            reasons.append("Highest rating expert")
        
        # Check if expert has special skill match
        if request.get('priority_level', 1) >= 3:  # High priority
            reasons.append("Special skill match")
        
        # Default reason
        if not reasons:
            reasons.append("Next in fairness rotation")
        
        return reasons[0]  # Return primary reason
    
    def _select_best_expert(self, available_experts: List[Dict], request: Dict) -> Optional[Dict]:
        """Select the best expert for a consultation request"""
        if not available_experts:
            return None
        
        # Simple strategy: choose expert with least total consultations
        # In future, can incorporate rating, response time, etc.
        best_expert = min(available_experts, key=lambda x: x.get('total_consultations', 0))
        return best_expert
    
    # Expert Status Management
    def classify_priority(self, issue_description: str) -> int:
        """Classify priority level based on emergency keywords"""
        emergency_keywords = [
            'accident', 'crash', 'collision', 'emergency', 'stuck', 'wont start',
            'engine failure', 'brake failure', 'fire', 'smoke', 'overheating',
            'flat tire', 'breakdown', 'dangerous', 'urgent', 'immediate'
        ]
        
        description_lower = issue_description.lower()
        
        # Check for emergency keywords
        for keyword in emergency_keywords:
            if keyword in description_lower:
                return 3  # HIGH priority
        
        # Check for medium priority keywords
        medium_keywords = ['noise', 'warning', 'check engine', 'service', 'maintenance']
        for keyword in medium_keywords:
            if keyword in description_lower:
                return 2  # NORMAL priority
        
        return 1  # LOW priority
    
    def get_queue_count(self, area_of_expertise: str) -> int:
        """Get count of waiting requests for a specific expertise area"""
        conn = expert_availability_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM consultation_requests 
                WHERE expert_category = %s AND status = 'WAITING'
            """, (area_of_expertise,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error getting queue count: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()

    # Expert Status Management
    def go_online(self, expert_id: int) -> Dict:
        """Set expert status to ONLINE_AVAILABLE"""
        with self._lock:
            # Validate expert exists
            expert = automobile_expert_db.get_expert_by_id(expert_id)
            if not expert:
                return {'success': False, 'error': 'Expert not found'}
            
            # Check if expert can go online
            current_status = expert_availability_db.get_expert_status(expert_id)
            if current_status and current_status['status'] == 'BUSY':
                return {'success': False, 'error': 'Cannot go online while busy'}
            
            # Update status
            success = expert_availability_db.update_expert_status(expert_id, 'ONLINE_AVAILABLE')
            
            if success:
                # Trigger immediate assignment check
                self._process_waiting_assignments()
                
                return {
                    'success': True,
                    'status': 'ONLINE_AVAILABLE',
                    'message': 'Expert is now online and available for consultations'
                }
            else:
                return {'success': False, 'error': 'Failed to update status'}
    
    def reject_consultation_request(self, expert_id: int, request_id: int, rejection_reason: str = None) -> Dict:
        """Reject a consultation request"""
        with self._lock:
            try:
                success = expert_availability_db.reject_consultation_request(request_id, expert_id, rejection_reason)
                
                if success:
                    # Trigger re-assignment check
                    self._process_waiting_assignments()
                    
                    return {
                        'success': True,
                        'message': 'Consultation request rejected and returned to queue',
                        'request_id': request_id
                    }
                else:
                    return {'success': False, 'error': 'Failed to reject request'}
                    
            except Exception as e:
                return {'success': False, 'error': f'Rejection failed: {str(e)}'}
    
    def create_consultation_request_with_priority(self, user_id: int, issue_description: str, 
                                                 expert_category: str, user_name: str = None, 
                                                 user_city: str = None, image_paths: list = None) -> int:
        """Create a new consultation request with automatic priority classification"""
        # Classify priority based on issue description
        priority_level = self.classify_priority(issue_description)
        
        return expert_availability_db.create_consultation_request(
            user_id, issue_description, expert_category, priority_level,
            user_name, user_city, image_paths
        )

    def go_offline(self, expert_id: int) -> Dict:
        """Set expert status to OFFLINE"""
        with self._lock:
            # Check if expert is busy
            current_status = expert_availability_db.get_expert_status(expert_id)
            if current_status and current_status['status'] == 'BUSY':
                return {'success': False, 'error': 'Cannot go offline while busy'}
            
            # Update status
            success = expert_availability_db.update_expert_status(expert_id, 'OFFLINE')
            
            if success:
                return {
                    'success': True,
                    'status': 'OFFLINE',
                    'message': 'Expert is now offline'
                }
            else:
                return {'success': False, 'error': 'Failed to update status'}
    
    def get_expert_dashboard_data(self, expert_id: int) -> Dict:
        """Get comprehensive dashboard data for an expert"""
        # Get expert info
        expert = automobile_expert_db.get_expert_by_id(expert_id)
        if not expert:
            return {'success': False, 'error': 'Expert not found'}
        
        # Get availability status
        availability = expert_availability_db.get_expert_status(expert_id) or {}
        current_status = availability.get('status', 'OFFLINE')
        
        # Get current consultation
        current_consultation = None
        if current_status == 'BUSY':
            current_consultation = expert_availability_db.get_expert_active_consultation(expert_id)
        
        # Get demand data (simplified without JOIN)
        waiting_requests = expert_availability_db.get_waiting_requests(expert['area_of_expertise'], limit=1)
        waiting_count = len(waiting_requests)
        
        # Simple demand calculation
        if waiting_count > 5:
            demand_level = 'HIGH'
        elif waiting_count > 2:
            demand_level = 'MEDIUM'
        else:
            demand_level = 'LOW'
        
        # Get performance stats
        performance_stats = expert_availability_db.get_expert_performance_stats(expert_id)
        
        # Generate suggestion
        suggestion = self._generate_suggestion(current_status, demand_level, performance_stats)
        
        return {
            'success': True,
            'expert_name': expert['name'],
            'area_of_expertise': expert['area_of_expertise'],
            'experience_years': expert['experience_years'],
            'status': current_status,
            'current_consultation': current_consultation,
            'waiting_requests_count': waiting_count,
            'demand_level': demand_level,
            'available_experts_count': 1,  # Simplified
            'performance_stats': performance_stats,
            'suggestion': suggestion,
            'last_status_change': availability.get('last_status_change'),
            'total_consultations': availability.get('total_consultations', 0)
        }
    
    def _generate_suggestion(self, current_status: str, demand_level: str, performance_stats: Dict) -> str:
        """Generate smart suggestion for the expert"""
        
        if current_status == 'OFFLINE':
            if demand_level == 'HIGH':
                return f"High demand for consultations! Consider going online to help users."
            elif demand_level == 'MEDIUM':
                return f"Moderate demand currently. Good time to go online."
            else:
                return f"Low demand currently. You can go online if available."
        
        elif current_status == 'ONLINE_AVAILABLE':
            if demand_level == 'HIGH':
                return "High demand period! Stay online to help more users."
            elif performance_stats['total_consultations'] < 5:
                return "Building your consultation history. Stay online to gain experience."
            else:
                return "You're doing great! Continue providing quality consultations."
        
        elif current_status == 'BUSY':
            return "Focus on your current consultation. Quality over quantity."
        
        return "Keep up the great work!"
    
    # Consultation Management
    def get_consultation_queue(self, expert_id: int, limit: int = 10) -> Dict:
        """Get consultation queue for expert"""
        try:
            # Get expert's pending requests using the bridge
            from .expert_request_bridge import expert_request_bridge
            requests = expert_request_bridge.get_expert_pending_requests(expert_id)
            
            # Get expert info for area
            expert = automobile_expert_db.get_expert_by_id(expert_id)
            if not expert:
                return {'success': False, 'error': 'Expert not found'}
            
            # Format for response
            formatted_requests = []
            for request in requests[:limit]:
                # Generate user name from user_id
                user_name = f'User_{request["user_id"]}'
                
                formatted_requests.append({
                    'request_id': request['request_id'],
                    'user_id': request['user_id'],
                    'user_name': user_name,
                    'category': request['area_of_expertise'],
                    'problem_description': request['issue_description'],
                    'status': request['status'],
                    'created_at': request['created_at'],
                    'priority_level': 1
                })
            
            return {
                'success': True,
                'waiting_requests': formatted_requests,
                'total_waiting': len(formatted_requests),
                'expert_area': expert['area_of_expertise']
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to load queue: {str(e)}'}
    
    def accept_consultation_request(self, expert_id: int, request_id: int) -> Dict:
        """Manually accept a consultation request and start session"""
        with self._lock:
            # Check expert status
            current_status = expert_availability_db.get_expert_status(expert_id)
            if not current_status or current_status['status'] not in ['ONLINE_AVAILABLE', 'BUSY']:
                return {'success': False, 'error': 'Expert not available'}
            
            # Get request details
            conn = expert_availability_db.get_conn()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            try:
                cursor.execute("""
                    SELECT * FROM consultation_requests 
                    WHERE request_id = %s AND status IN ('WAITING_QUEUE','WAITING','ASSIGNED')
                """, (request_id,))
                request = cursor.fetchone()
                
                if not request:
                    return {'success': False, 'error': 'Request not found or not available'}
                
                # Convert to dictionary (RealDictCursor does this)
                request_dict = dict(request)
                
                # Assign request to expert
                assigned_reason = self._calculate_assignment_reason({'expert_id': expert_id}, request_dict)
                success = expert_availability_db.assign_consultation_request(request_id, expert_id, assigned_reason)
                
                if success:
                    # Update expert performance
                    from .expert_history_service import expert_history_service
                    expert_history_service.set_expert_busy(expert_id, request_id)
                    
                    # Update user's request status in ask_expert database
                    try:
                        from .expert_request_bridge import expert_request_bridge
                        expert_request_bridge.update_request_status(request_id, 'ASSIGNED', expert_id)
                    except Exception:
                        pass  # Ignore if update fails
                    
                    # Start consultation session
                    from .consultation_session_service import consultation_session_service
                    session_result = consultation_session_service.start_consultation_session(
                        request_id, request['user_id'], expert_id
                    )
                    
                    if session_result['success']:
                        conn.commit()
                        return {
                            'success': True,
                            'message': 'Consultation request accepted and session started',
                            'request_id': request_id,
                            'session_id': session_result['session_id']
                        }
                    else:
                        conn.rollback()
                        return {'success': False, 'error': 'Failed to start session'}
                else:
                    conn.rollback()
                    return {'success': False, 'error': 'Failed to accept request'}
            except Exception as e:
                conn.rollback()
                return {'success': False, 'error': f'Failed to accept request: {str(e)}'}
            finally:
                cursor.close()
                conn.close()
    
    def complete_consultation(self, expert_id: int, request_id: int, user_rating: int = None) -> Dict:
        """Complete a consultation and end session"""
        with self._lock:
            # Get active consultation session
            from .consultation_session_db import consultation_session_db
            session = consultation_session_db.get_active_consultation_session(expert_id)
            
            if not session or session['request_id'] != request_id:
                return {'success': False, 'error': 'Consultation not found or not active'}
            
            # End consultation session
            session_result = consultation_session_service.end_consultation_session(
                session['session_id'], expert_id
            )
            
            if session_result['success']:
                # Update expert performance
                from .expert_history_service import expert_history_service
                expert_history_service.update_expert_performance(
                    expert_id, 
                    consultation_completed=True,
                    duration_seconds=session_result.get('duration_seconds', 0),
                    user_rating=user_rating
                )
                
                # Set expert available
                expert_history_service.set_expert_available(expert_id)
                
                # Update rating if provided
                if user_rating and 1 <= user_rating <= 5:
                    self._update_expert_rating(expert_id, user_rating)
                
                return {
                    'success': True,
                    'message': 'Consultation completed successfully',
                    'expert_status': 'ONLINE_AVAILABLE',
                    'duration_seconds': session_result.get('duration_seconds', 0)
                }
            else:
                return {'success': False, 'error': 'Failed to complete consultation'}
    
    def _update_expert_rating(self, expert_id: int, new_rating: int):
        """Update expert rating based on new consultation rating"""
        # Simple rating update - in production, use weighted average
        current_status = expert_availability_db.get_expert_status(expert_id)
        if current_status:
            total_consultations = current_status.get('total_consultations', 0)
            current_rating = current_status.get('rating', 0)
            
            if total_consultations > 0:
                # Weighted average
                new_avg_rating = ((current_rating * total_consultations) + new_rating) / (total_consultations + 1)
            else:
                new_avg_rating = new_rating
            
            # Update rating in database
            conn = expert_availability_db.get_conn()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE expert_availability 
                    SET rating = %s 
                    WHERE expert_id = %s
                """, (round(new_avg_rating, 2), expert_id))
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Error updating expert rating: {e}")
            finally:
                cursor.close()
                conn.close()
    
    # Demand and Analytics
    def get_demand_indicators(self, area_of_expertise: str = None) -> Dict:
        """Get demand indicators for all or specific expertise areas"""
        if area_of_expertise:
            demand_data = expert_availability_db.calculate_demand_level(area_of_expertise)
            return {'success': True, 'demand_data': demand_data}
        else:
            # Get demand for all areas
            areas = ['Engine', 'Electrical', 'Diagnostic', 'General']
            demand_data = {}
            for area in areas:
                demand_data[area] = expert_availability_db.calculate_demand_level(area)
            
            return {'success': True, 'demand_data': demand_data}
    
    def get_expert_analytics(self, expert_id: int, days: int = 30) -> Dict:
        """Get detailed analytics for an expert"""
        expert = automobile_expert_db.get_expert_by_id(expert_id)
        if not expert:
            return {'success': False, 'error': 'Expert not found'}
        
        # Performance stats
        performance_stats = expert_availability_db.get_expert_performance_stats(expert_id, days)
        
        # Activity logs
        activity_logs = expert_availability_db.get_expert_activity_logs(expert_id, limit=20)
        
        # Current status
        availability = expert_availability_db.get_expert_status(expert_id) or {}
        
        return {
            'success': True,
            'expert_info': {
                'name': expert['name'],
                'area_of_expertise': expert['area_of_expertise'],
                'experience_years': expert['experience_years']
            },
            'performance_stats': performance_stats,
            'activity_logs': activity_logs,
            'current_status': availability.get('status', 'OFFLINE'),
            'total_consultations': availability.get('total_consultations', 0),
            'rating': availability.get('rating', 0),
            'analytics_period_days': days
        }
    
    # System Management
    def get_system_stats(self) -> Dict:
        """Get overall system statistics"""
        conn = expert_availability_db.get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Expert counts by status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM expert_availability 
                GROUP BY status
            """)
            status_counts = cursor.fetchall()
            
            # Request counts by status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM consultation_requests 
                GROUP BY status
            """)
            request_counts = cursor.fetchall()
            
            # Demand by area
            demand_by_area = {}
            areas = ['Engine', 'Electrical', 'Diagnostic', 'General']
            for area in areas:
                demand = expert_availability_db.calculate_demand_level(area)
                demand_by_area[area] = demand
            
            return {
                'success': True,
                'expert_status_counts': {row['status']: row['count'] for row in status_counts},
                'request_status_counts': {row['status']: row['count'] for row in request_counts},
                'demand_by_area': demand_by_area,
                'total_experts': sum(row['count'] for row in status_counts),
                'total_requests': sum(row['count'] for row in request_counts)
            }
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()
            conn.close()

# Create service instance
expert_availability_service = ExpertAvailabilityService()
