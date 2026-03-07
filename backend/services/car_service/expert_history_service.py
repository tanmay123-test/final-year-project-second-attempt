"""
Expert History and Performance Service
Business logic for consultation history, performance analytics, reputation, and queue handling
"""

import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from .expert_history_db import expert_history_db
from .expert_availability_db import expert_availability_db

class ExpertHistoryService:
    def __init__(self):
        self._lock = threading.Lock()
        self._queue_processor_running = False
        self.start_queue_processor()
    
    def start_queue_processor(self):
        """Start background queue processor for automatic assignment"""
        if not self._queue_processor_running:
            self._queue_processor_running = True
            threading.Thread(target=self._queue_processor_worker, daemon=True).start()
    
    def _queue_processor_worker(self):
        """Background worker for processing waiting queue"""
        while self._queue_processor_running:
            try:
                with self._lock:
                    self._process_waiting_queue()
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"Queue processor error: {e}")
                time.sleep(30)
    
    def _process_waiting_queue(self):
        """Process waiting queue and assign to available experts"""
        try:
            # Get waiting requests
            waiting_requests = expert_history_db.get_waiting_queue()
            
            for request in waiting_requests:
                # Find available expert for this category
                expert = self._find_best_available_expert(request['category'])
                
                if expert:
                    # Assign request to expert
                    success = expert_history_db.assign_consultation_request(
                        request['request_id'], expert['id'], expert['assignment_reason']
                    )
                    
                    if success:
                        # Update expert status to BUSY
                        expert_history_db.update_expert_status(
                            expert['id'], 'ONLINE_AVAILABLE', is_busy=True
                        )
                        
                        # Update availability engine
                        expert_availability_db.update_expert_status(expert['id'], 'BUSY')
                        
                        print(f"Auto-assigned request {request['request_id']} to expert {expert['id']}")
                        
        except Exception as e:
            print(f"Error processing queue: {e}")
    
    def _find_best_available_expert(self, category: str) -> Optional[Dict]:
        """Find best available expert for category using fair assignment"""
        try:
            # Get available experts for category
            available_experts = expert_availability_db.get_available_experts_by_category(category)
            
            if not available_experts:
                # Try general expert if no category expert available
                if category != 'GENERAL_EXPERT':
                    available_experts = expert_availability_db.get_available_experts_by_category('GENERAL_EXPERT')
                
                if not available_experts:
                    return None
            
            # Calculate fair assignment scores for all available experts
            expert_scores = []
            for expert in available_experts:
                score = expert_history_db.calculate_fair_assignment_score(expert['expert_id'])
                expert_scores.append({
                    'expert': expert,
                    'score': score
                })
            
            # Sort by score (highest first)
            expert_scores.sort(key=lambda x: x['score'], reverse=True)
            
            best_expert = expert_scores[0]['expert']
            
            # Determine assignment reason
            if expert_scores[0]['score'] >= 80:
                assignment_reason = "Highest priority assignment"
            elif expert_scores[0]['score'] >= 60:
                assignment_reason = "Fair assignment rotation"
            else:
                assignment_reason = "Available expert assignment"
            
            best_expert['assignment_reason'] = assignment_reason
            return best_expert
            
        except Exception as e:
            print(f"Error finding best expert: {e}")
            return None
    
    # Consultation History Management
    def get_consultation_history(self, expert_id: int, limit: int = 50) -> Dict:
        """Get expert's consultation history"""
        try:
            consultations = expert_history_db.get_consultation_history(expert_id, limit)
            
            # Format consultations for response
            formatted_consultations = []
            for consultation in consultations:
                formatted_consultations.append({
                    'request_id': consultation['request_id'],
                    'user_name': consultation['user_name'] or 'Unknown User',
                    'category': consultation['category'],
                    'date': consultation['created_at'].split(' ')[0],  # Just date part
                    'duration_seconds': consultation['consultation_duration_seconds'] or 0,
                    'status': consultation['status'],
                    'resolution_status': consultation['resolution_status'],
                    'assigned_reason': consultation['assigned_reason']
                })
            
            return {
                'success': True,
                'consultations': formatted_consultations,
                'total_consultations': len(formatted_consultations)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get history: {str(e)}'}
    
    def reopen_consultation(self, expert_id: int, request_id: int) -> Dict:
        """Reopen a closed consultation session"""
        try:
            # Get consultation details
            consultations = expert_history_db.get_consultation_history(expert_id, 100)
            target_consultation = None
            
            for consultation in consultations:
                if consultation['request_id'] == request_id:
                    target_consultation = consultation
                    break
            
            if not target_consultation:
                return {'success': False, 'error': 'Consultation not found'}
            
            if target_consultation['status'] not in ['RESOLVED', 'CANCELLED']:
                return {'success': False, 'error': 'Consultation cannot be reopened'}
            
            # Update consultation status back to IN_PROGRESS
            cursor = expert_history_db.conn.cursor()
            cursor.execute("""
                UPDATE expert_requests 
                SET status = 'IN_PROGRESS', resolved_at = NULL
                WHERE id = ? AND expert_id = ?
            """, (request_id, expert_id))
            
            success = cursor.rowcount > 0
            expert_history_db.conn.commit()
            
            if success:
                # Update expert status to BUSY
                expert_history_db.update_expert_status(expert_id, 'ONLINE_AVAILABLE', is_busy=True)
                expert_availability_db.update_expert_status(expert_id, 'BUSY')
                
                return {
                    'success': True,
                    'message': 'Consultation reopened successfully',
                    'request_id': request_id
                }
            else:
                return {'success': False, 'error': 'Failed to reopen consultation'}
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to reopen: {str(e)}'}
    
    # Performance Analytics
    def get_performance_analytics(self, expert_id: int, days: int = 30) -> Dict:
        """Get expert performance analytics"""
        try:
            metrics = expert_history_db.calculate_performance_metrics(expert_id, days)
            profile = expert_history_db.get_expert_profile(expert_id)
            
            # Calculate additional metrics
            if profile:
                online_hours = profile.get('total_online_hours', 0)
                reliability_score = profile.get('reliability_score', 0.0)
            else:
                online_hours = 0
                reliability_score = 0.0
            
            return {
                'success': True,
                'total_consultations': metrics['total_consultations'],
                'completed_consultations': metrics['completed_consultations'],
                'resolution_rate': metrics['resolution_rate'],
                'average_response_seconds': metrics['average_response_seconds'],
                'average_duration_seconds': metrics['average_duration_seconds'],
                'online_hours': online_hours,
                'reliability_score': round(reliability_score, 2),
                'analysis_period_days': days
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get analytics: {str(e)}'}
    
    # Reputation and Badges
    def get_expert_reputation(self, expert_id: int) -> Dict:
        """Get expert reputation information"""
        try:
            profile = expert_history_db.get_expert_profile(expert_id)
            badges = expert_history_db.get_expert_badges(expert_id)
            
            if not profile:
                return {'success': False, 'error': 'Expert profile not found'}
            
            # Extract badge names
            badge_names = [badge['badge_name'] for badge in badges]
            
            return {
                'success': True,
                'approval_status': profile.get('is_approved', False),
                'online_hours': profile.get('total_online_hours', 0),
                'consultations_completed': profile.get('completed_consultations', 0),
                'reliability_score': round(profile.get('reliability_score', 0.0), 2),
                'rating': round(profile.get('rating', 0.0), 2),
                'fair_assignment_score': round(profile.get('fair_assignment_score', 0.0), 2),
                'badges': badge_names,
                'total_badges': len(badge_names)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get reputation: {str(e)}'}
    
    def update_expert_performance(self, expert_id: int, consultation_completed: bool, 
                              response_time_seconds: int = None, duration_seconds: int = None,
                              user_rating: int = None):
        """Update expert performance metrics"""
        try:
            with self._lock:
                profile = expert_history_db.get_expert_profile(expert_id)
                if not profile:
                    return
                
                updates = {}
                
                # Update consultation counts
                if consultation_completed:
                    updates['completed_consultations'] = profile.get('completed_consultations', 0) + 1
                
                updates['total_consultations'] = profile.get('total_consultations', 0) + 1
                
                # Update rating if provided
                if user_rating and 1 <= user_rating <= 5:
                    current_rating = profile.get('rating', 0.0)
                    current_completed = profile.get('completed_consultations', 0)
                    
                    # Calculate new average rating
                    new_rating = ((current_rating * current_completed) + user_rating) / (current_completed + 1)
                    updates['rating'] = round(new_rating, 2)
                
                # Update reliability score based on completion rate
                metrics = expert_history_db.calculate_performance_metrics(expert_id, 30)
                if metrics['resolution_rate'] > 90:
                    updates['reliability_score'] = 5.0
                elif metrics['resolution_rate'] > 80:
                    updates['reliability_score'] = 4.0
                elif metrics['resolution_rate'] > 70:
                    updates['reliability_score'] = 3.0
                else:
                    updates['reliability_score'] = 2.0
                
                # Update fair assignment score
                updates['fair_assignment_score'] = expert_history_db.calculate_fair_assignment_score(expert_id)
                
                # Apply updates
                expert_history_db.update_expert_profile(expert_id, updates)
                
                # Check and award badges
                expert_history_db.check_and_award_badges(expert_id)
                
                # Update performance analytics
                expert_history_db.update_performance_analytics(expert_id, metrics)
                
        except Exception as e:
            print(f"Error updating performance: {e}")
    
    # Expert Status Lifecycle Management
    def set_expert_online(self, expert_id: int) -> Dict:
        """Set expert to online status"""
        try:
            # Update profile
            success = expert_history_db.update_expert_status(expert_id, 'ONLINE_AVAILABLE', is_busy=False)
            
            if success:
                # Update availability engine
                expert_availability_db.update_expert_status(expert_id, 'ONLINE_AVAILABLE')
                
                # Process queue immediately for new expert
                self._process_waiting_queue()
                
                return {
                    'success': True,
                    'message': 'Expert is now online and available',
                    'status': 'ONLINE_AVAILABLE'
                }
            else:
                return {'success': False, 'error': 'Failed to set online'}
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to go online: {str(e)}'}
    
    def set_expert_offline(self, expert_id: int) -> Dict:
        """Set expert to offline status"""
        try:
            # Check if expert is in consultation
            profile = expert_history_db.get_expert_profile(expert_id)
            if profile and profile.get('is_busy', False):
                return {'success': False, 'error': 'Cannot go offline while busy'}
            
            # Update profile
            success = expert_history_db.update_expert_status(expert_id, 'OFFLINE', is_busy=False)
            
            if success:
                # Update availability engine
                expert_availability_db.update_expert_status(expert_id, 'OFFLINE')
                
                return {
                    'success': True,
                    'message': 'Expert is now offline',
                    'status': 'OFFLINE'
                }
            else:
                return {'success': False, 'error': 'Failed to set offline'}
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to go offline: {str(e)}'}
    
    def set_expert_busy(self, expert_id: int, request_id: int) -> Dict:
        """Set expert to busy status (automatic only)"""
        try:
            # Update profile
            success = expert_history_db.update_expert_status(expert_id, 'ONLINE_AVAILABLE', is_busy=True)
            
            if success:
                # Update availability engine
                expert_availability_db.update_expert_status(expert_id, 'BUSY')
                
                return {
                    'success': True,
                    'message': 'Expert is now busy',
                    'status': 'BUSY',
                    'current_request_id': request_id
                }
            else:
                return {'success': False, 'error': 'Failed to set busy'}
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to set busy: {str(e)}'}
    
    def set_expert_available(self, expert_id: int) -> Dict:
        """Set expert to available status (after consultation completion)"""
        try:
            # Update profile
            success = expert_history_db.update_expert_status(expert_id, 'ONLINE_AVAILABLE', is_busy=False)
            
            if success:
                # Update availability engine
                expert_availability_db.update_expert_status(expert_id, 'ONLINE_AVAILABLE')
                
                # Process queue for newly available expert
                self._process_waiting_queue()
                
                return {
                    'success': True,
                    'message': 'Expert is now available',
                    'status': 'ONLINE_AVAILABLE'
                }
            else:
                return {'success': False, 'error': 'Failed to set available'}
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to set available: {str(e)}'}
    
    # Report Management
    def create_user_report(self, expert_id: int, user_id: int, request_id: int, 
                        reason: str, description: str = None) -> Dict:
        """Create a report against user"""
        try:
            valid_reasons = ['USER_ABUSE', 'TECHNICAL_ISSUE', 'GENERAL_SUPPORT']
            if reason not in valid_reasons:
                return {'success': False, 'error': 'Invalid report reason'}
            
            report_id = expert_history_db.create_report(
                expert_id, user_id, request_id, reason, description
            )
            
            return {
                'success': True,
                'message': 'Report submitted successfully',
                'report_id': report_id
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to create report: {str(e)}'}
    
    def get_expert_reports(self, expert_id: int) -> Dict:
        """Get reports created by expert"""
        try:
            reports = expert_history_db.get_expert_reports(expert_id)
            
            return {
                'success': True,
                'reports': reports,
                'total_reports': len(reports)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get reports: {str(e)}'}
    
    # Queue Management
    def get_queue_status(self, category: str = None) -> Dict:
        """Get current queue status"""
        try:
            waiting_requests = expert_history_db.get_waiting_queue(category)
            
            # Group by category
            category_counts = {}
            for request in waiting_requests:
                cat = request['category']
                if cat not in category_counts:
                    category_counts[cat] = 0
                category_counts[cat] += 1
            
            return {
                'success': True,
                'total_waiting': len(waiting_requests),
                'category_breakdown': category_counts,
                'oldest_request': waiting_requests[0] if waiting_requests else None,
                'newest_request': waiting_requests[-1] if waiting_requests else None
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get queue status: {str(e)}'}
    
    def get_expert_dashboard(self, expert_id: int) -> Dict:
        """Get comprehensive expert dashboard data"""
        try:
            # Get profile
            profile = expert_history_db.get_expert_profile(expert_id)
            if not profile:
                return {'success': False, 'error': 'Expert profile not found'}
            
            # Get performance metrics
            metrics = expert_history_db.calculate_performance_metrics(expert_id, 30)
            
            # Get badges
            badges = expert_history_db.get_expert_badges(expert_id)
            badge_names = [badge['badge_name'] for badge in badges]
            
            # Get queue status for expert's category
            queue_status = self.get_queue_status(profile.get('category'))
            
            # Get current consultation
            current_consultation = expert_availability_db.get_expert_active_consultation(expert_id)
            
            return {
                'success': True,
                'expert_status': profile.get('online_status', 'OFFLINE'),
                'is_busy': profile.get('is_busy', False),
                'consultations_completed': metrics['completed_consultations'],
                'rating': round(profile.get('rating', 0.0), 2),
                'reliability_score': round(profile.get('reliability_score', 0.0), 2),
                'fair_assignment_score': round(profile.get('fair_assignment_score', 0.0), 2),
                'resolution_rate': metrics['resolution_rate'],
                'badges': badge_names,
                'waiting_queue_count': queue_status.get('total_waiting', 0),
                'current_consultation': current_consultation,
                'total_online_hours': profile.get('total_online_hours', 0)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get dashboard: {str(e)}'}

# Create service instance
expert_history_service = ExpertHistoryService()
