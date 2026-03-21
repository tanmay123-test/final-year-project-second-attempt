"""
Car Service Dispatch Job Queue
Handles job assignment and queue management
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

# Import databases
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from car_service.job_requests_db import job_requests_db
from car_service.car_service_worker_db import car_service_worker_db

class JobQueue:
    def __init__(self):
        self.job_requests_db = job_requests_db
        self.worker_db = car_service_worker_db
    
    def get_pending_jobs(self, mechanic_id: int) -> List[Dict]:
        """Get pending job requests for a mechanic"""
        return self.job_requests_db.get_pending_jobs(mechanic_id)
    
    def assign_job_to_mechanic(self, user_id: int, user_name: str, car_model: str, 
                              issue: str, issue_type: str, user_city: str) -> Optional[int]:
        """Assign a job to the best available mechanic"""
        
        # Get available mechanics
        available_mechanics = self.worker_db.get_available_workers()
        if not available_mechanics:
            return None
        
        # Find the best mechanic based on multiple factors
        best_mechanic = self._find_best_mechanic(available_mechanics, user_city, issue_type, issue)
        
        if not best_mechanic:
            return None
        
        # Calculate distance and ETA (simplified for now)
        distance_km = self._calculate_distance(best_mechanic.get('current_city', best_mechanic['city']), user_city)
        eta_minutes = int(distance_km * 3)  # 3 minutes per km
        estimated_earning = self._calculate_earning(issue_type, distance_km)
        
        # Determine priority
        priority = 'EMERGENCY' if self._is_emergency(issue) else 'NORMAL'
        
        # Create assignment reason
        assignment_reason = self._create_assignment_reason(best_mechanic, distance_km, issue_type)
        
        # Create job request
        job_id = self.job_requests_db.create_job_request(
            user_id=user_id,
            mechanic_id=best_mechanic['id'],
            user_name=user_name,
            car_model=car_model,
            issue=issue,
            issue_type=issue_type,
            user_city=user_city,
            distance_km=distance_km,
            eta_minutes=eta_minutes,
            estimated_earning=estimated_earning,
            priority=priority,
            assignment_reason=assignment_reason
        )
        
        # Update mechanic's job count
        self._update_mechanic_job_count(best_mechanic['id'])
        
        return job_id
    
    def _find_best_mechanic(self, mechanics: List[Dict], user_city: str, 
                           issue_type: str, issue: str) -> Optional[Dict]:
        """Find the best mechanic for a job using multiple factors"""
        
        if not mechanics:
            return None
        
        # Score each mechanic
        scored_mechanics = []
        for mechanic in mechanics:
            score = 0
            
            # Factor 1: Distance (closer is better)
            mechanic_city = mechanic.get('current_city', mechanic.get('city', ''))
            distance = self._calculate_distance(mechanic_city, user_city)
            distance_score = max(0, 50 - distance * 5)  # 50 points max, decreasing with distance
            score += distance_score
            
            # Factor 2: Skills match
            if issue_type.lower() in mechanic.get('skills', '').lower():
                score += 30
            
            # Factor 3: Fairness (use stats-based fairness score)
            stats = self.job_requests_db.get_mechanic_stats(mechanic['id'])
            fairness_score = stats.get('fairness_score', 100)
            fairness_points = (fairness_score / 100) * 20  # Convert to 0-20 points
            score += fairness_points
            
            # Factor 4: Acceptance rate bonus
            acceptance_rate = stats.get('acceptance_rate', 0)
            acceptance_points = acceptance_rate * 10  # Convert to 0-10 points
            score += acceptance_points
            
            # Factor 5: Emergency priority for experienced mechanics
            if self._is_emergency(issue) and mechanic.get('experience', 0) >= 3:
                score += 20
            
            # Get jobs today for display
            jobs_today = self._get_mechanics_jobs_today(mechanic['id'])
            
            scored_mechanics.append({
                'mechanic': mechanic,
                'score': score,
                'distance': distance,
                'jobs_today': jobs_today
            })
        
        # Sort by score (highest first)
        scored_mechanics.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_mechanics[0]['mechanic'] if scored_mechanics else None
    
    def _calculate_distance(self, city1: str, city2: str) -> float:
        """Calculate distance between two cities (simplified)"""
        # Simplified distance calculation - in real implementation, use Google Maps API
        city_distances = {
            ('Mumbai', 'Mumbai'): 0,
            ('Mumbai', 'Delhi'): 1400,
            ('Mumbai', 'Bangalore'): 980,
            ('Mumbai', 'Pune'): 150,
            ('Mumbai', 'Ghatkopar'): 8,
            ('Mumbai', 'Bandra'): 12,
            ('Mumbai', 'Andheri'): 15,
            ('Delhi', 'Delhi'): 0,
            ('Delhi', 'Bangalore'): 2100,
            ('Delhi', 'Pune'): 1400,
            ('Bangalore', 'Bangalore'): 0,
            ('Bangalore', 'Pune'): 700,
            ('Pune', 'Pune'): 0,
        }
        
        # Normalize city names
        city1_norm = city1.strip().title()
        city2_norm = city2.strip().title()
        
        # Check both directions
        distance = city_distances.get((city1_norm, city2_norm))
        if distance is None:
            distance = city_distances.get((city2_norm, city1_norm))
        
        # Default distance if not found
        return distance if distance is not None else 50.0
    
    def _calculate_earning(self, issue_type: str, distance_km: float) -> float:
        """Calculate estimated earning for a job"""
        base_rates = {
            'engine repair': 800,
            'brake service': 500,
            'general service': 400,
            'battery replacement': 300,
            'tire service': 350,
            'ac service': 600,
            'electrical': 700,
            'transmission': 1000,
            'suspension': 600
        }
        
        base_rate = base_rates.get(issue_type.lower(), 400)
        distance_bonus = distance_km * 10  # 10 rupees per km
        
        return base_rate + distance_bonus
    
    def _is_emergency(self, issue: str) -> bool:
        """Check if issue is an emergency"""
        emergency_keywords = ['brake failure', 'engine stopped', 'accident', 'emergency', 
                            'wont start', 'break down', 'stuck', 'dangerous', 'smoke']
        
        issue_lower = issue.lower()
        return any(keyword in issue_lower for keyword in emergency_keywords)
    
    def _create_assignment_reason(self, mechanic: Dict, distance_km: float, issue_type: str) -> str:
        """Create assignment reason for transparency"""
        reasons = []
        
        # Distance reason
        if distance_km < 5:
            reasons.append(f"Closest mechanic ({distance_km:.1f} km)")
        
        # Skills match
        if issue_type.lower() in mechanic.get('skills', '').lower():
            reasons.append(f"{issue_type} specialist skill match")
        
        # Performance reason
        experience = mechanic.get('experience', 0)
        if experience >= 5:
            reasons.append("High performance rating")
        
        # Fairness reason
        jobs_today = self._get_mechanics_jobs_today(mechanic['id'])
        if jobs_today <= 2:
            reasons.append("Fairness priority applied")
        
        return " | ".join(reasons) if reasons else "Available mechanic"
    
    def _get_mechanics_jobs_today(self, mechanic_id: int) -> int:
        """Get number of jobs assigned to mechanic today"""
        today = datetime.now().date().isoformat()
        conn = self.job_requests_db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM job_requests 
                WHERE mechanic_id = %s AND DATE(created_at) = %s
            """, (mechanic_id, today))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error getting jobs today: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()
    
    def _update_mechanic_job_count(self, mechanic_id: int):
        """Update mechanic's job count for the day"""
        # This could be stored in a separate table or in the worker table
        # For now, we'll calculate it dynamically
        pass
    
    def accept_job(self, job_id: int, mechanic_id: int) -> bool:
        """Accept a job and set mechanic to busy"""
        # Update job status
        success = self.job_requests_db.accept_job(job_id)
        
        if success:
            # Get job details
            job = self.job_requests_db.get_job_request(job_id)
            if job:
                # Create active job
                self.job_requests_db.create_active_job(
                    job_request_id=job_id,
                    user_id=job['user_id'],
                    mechanic_id=mechanic_id,
                    user_name=job['user_name'],
                    user_phone=None,  # Will be updated when user provides
                    user_lat=None,    # Will be updated when user provides
                    user_long=None,   # Will be updated when user provides
                    mechanic_lat=None, # Will be updated with GPS
                    mechanic_long=None # Will be updated with GPS
                )
            
            # Set mechanic to busy
            self.worker_db.set_busy(mechanic_id)
            return True
        
        return False
    
    def reject_job(self, job_id: int, mechanic_id: int, reason: str = None) -> bool:
        """Reject a job and reassign to next mechanic"""
        # Update job status
        success = self.job_requests_db.reject_job(job_id, reason)
        
        if success:
            # Get job details
            job = self.job_requests_db.get_job_request(job_id)
            if job:
                # Find next best mechanic
                self._reassign_job(job_id, job)
            return True
        
        return False
    
    def _reassign_job(self, job_id: int, job: Dict):
        """Reassign a job to the next available mechanic"""
        # Get available mechanics (excluding the one who rejected)
        available_mechanics = self.worker_db.get_available_workers()
        available_mechanics = [m for m in available_mechanics if m['id'] != job['mechanic_id']]
        
        if available_mechanics:
            best_mechanic = self._find_best_mechanic(
                available_mechanics, 
                job['user_city'], 
                job['issue_type'], 
                job['issue']
            )
            
            if best_mechanic:
                # Recalculate assignment reason
                distance_km = self._calculate_distance(
                    best_mechanic.get('current_city', best_mechanic['city']), 
                    job['user_city']
                )
                assignment_reason = self._create_assignment_reason(
                    best_mechanic, 
                    distance_km, 
                    job['issue_type']
                )
                
                # Reassign job
                self.job_requests_db.reassign_job(
                    job_id, 
                    best_mechanic['id'], 
                    f"Previous mechanic rejected | {assignment_reason}"
                )
    
    def complete_job(self, job_id: int, mechanic_id: int) -> bool:
        """Complete a job and set mechanic to available"""
        # Update job status
        success = self.job_requests_db.complete_job(job_id)
        
        if success:
            # Set mechanic to available
            self.worker_db.set_available(mechanic_id)
            return True
        
        return False
    
    def check_expired_jobs(self):
        """Check for expired jobs and reassign them"""
        expired_jobs = self.job_requests_db.get_expired_jobs()
        
        for job in expired_jobs:
            # Reassign expired job
            self._reassign_job(job['id'], job)
    
    def get_job_statistics(self, mechanic_id: int) -> Dict:
        """Get job statistics for a mechanic"""
        return self.job_requests_db.get_job_statistics(mechanic_id)

# Global instance
job_queue = JobQueue()
