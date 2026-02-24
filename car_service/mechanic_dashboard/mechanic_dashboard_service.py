"""
Mechanic Dashboard Service Layer
Complete business logic for mechanic worker management system
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from werkzeug.utils import secure_filename

from .mechanic_dashboard_db import mechanic_dashboard_db

class MechanicDashboardService:
    """Complete service layer for Mechanic Dashboard System"""
    
    def __init__(self):
        self.db = mechanic_dashboard_db
        self.upload_folder = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "job_proofs")
        os.makedirs(self.upload_folder, exist_ok=True)
    
    # ==================== ONLINE STATUS MANAGEMENT ====================
    
    def toggle_online_status(self, mechanic_id: int) -> Dict:
        """Toggle mechanic online/offline status"""
        current_status = self.db.get_mechanic_status(mechanic_id)
        
        if not current_status:
            return {"success": False, "error": "Mechanic not found"}
        
        new_status = "OFFLINE" if current_status["online_status"] == "ONLINE" else "ONLINE"
        
        # Update status
        success = self.db.update_mechanic_status(mechanic_id, online_status=new_status)
        
        if success:
            # Calculate and update priority score
            priority = self.db.calculate_priority_score(mechanic_id)
            
            return {
                "success": True,
                "new_status": new_status,
                "priority_score": priority,
                "message": f"Status updated to {new_status}"
            }
        
        return {"success": False, "error": "Failed to update status"}
    
    def get_demand_status(self, mechanic_id: int) -> Dict:
        """Get comprehensive demand status for mechanic"""
        # Get market demand analysis
        demand_analysis = self.db.get_demand_analysis()
        
        # Get mechanic's current status
        mechanic_status = self.db.get_mechanic_status(mechanic_id)
        
        # Calculate potential earnings
        pending_jobs = self.db.get_pending_jobs()
        mechanic_skill = self._get_mechanic_skill(mechanic_id)
        
        # Filter jobs by mechanic's skill
        relevant_jobs = [job for job in pending_jobs 
                       if mechanic_skill.lower() in job["required_skill"].lower()]
        
        # Calculate potential earnings
        potential_earnings = sum(
            (job["estimated_earning_min"] + job["estimated_earning_max"]) / 2 
            for job in relevant_jobs[:3]  # Top 3 jobs
        )
        
        # Fairness transparency
        fairness_score = self._calculate_fairness_score(mechanic_id)
        
        return {
            "success": True,
            "demand_level": demand_analysis["demand_level"],
            "online_mechanics": demand_analysis["online_mechanics"],
            "peak_hour": demand_analysis["peak_hour"],
            "priority_score": mechanic_status.get("priority_score", 0) if mechanic_status else 0,
            "potential_earnings_today": potential_earnings,
            "fairness_score": fairness_score,
            "skill_demand": demand_analysis["skill_demand"],
            "current_status": mechanic_status["online_status"] if mechanic_status else "OFFLINE",
            "is_busy": mechanic_status["is_busy"] if mechanic_status else False
        }
    
    def _get_mechanic_skill(self, mechanic_id: int) -> str:
        """Get mechanic's primary skill"""
        # This would typically come from worker profile
        # For now, default to general mechanic
        return "General Mechanic"
    
    def _calculate_fairness_score(self, mechanic_id: int) -> float:
        """Calculate fairness transparency score"""
        metrics = self.db.get_mechanic_metrics(mechanic_id)
        
        if not metrics:
            return 50.0  # Default score
        
        # Fairness based on performance consistency
        completion_score = metrics["completion_rate"]
        on_time_score = metrics["on_time_rate"]
        
        # Calculate fairness score (0-100)
        fairness = (completion_score * 0.6) + (on_time_score * 0.4)
        return round(fairness, 2)
    
    # ==================== JOB REQUEST MANAGEMENT ====================
    
    def get_transparent_job_requests(self, mechanic_id: int) -> Dict:
        """Get transparent job requests with full details"""
        pending_jobs = self.db.get_pending_jobs(skill=self._get_mechanic_skill(mechanic_id))
        mechanic_status = self.db.get_mechanic_status(mechanic_id)
        
        # Enhance each job with transparency data
        enhanced_jobs = []
        for job in pending_jobs:
            # Calculate distance (simplified - would use actual location in production)
            distance = self._calculate_distance(
                mechanic_status.get("last_location_lat", 0),
                mechanic_status.get("last_location_long", 0),
                job["location_lat"],
                job["location_long"]
            )
            
            # Calculate profitability score
            avg_earning = (job["estimated_earning_min"] + job["estimated_earning_max"]) / 2
            profitability_score = self._calculate_profitability_score(avg_earning, job["estimated_duration"])
            
            # Risk assessment
            risk_level = self._assess_job_risk(job)
            
            enhanced_job = {
                **job,
                "distance_km": round(distance, 2),
                "profitability_score": profitability_score,
                "risk_level": risk_level,
                "assignment_reason": self._get_assignment_reason(job, mechanic_id)
            }
            
            enhanced_jobs.append(enhanced_job)
        
        # Sort by priority (profitability + proximity)
        enhanced_jobs.sort(key=lambda x: (x["profitability_score"], -x["distance_km"]), reverse=True)
        
        return {
            "success": True,
            "jobs": enhanced_jobs,
            "total_jobs": len(enhanced_jobs),
            "mechanic_status": "ONLINE" if mechanic_status and mechanic_status["online_status"] == "ONLINE" else "OFFLINE"
        }
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates (simplified)"""
        # Simplified distance calculation - would use proper haversine in production
        return abs(lat1 - lat2) * 111 + abs(lng1 - lng2) * 111
    
    def _calculate_profitability_score(self, avg_earning: float, duration: int) -> float:
        """Calculate job profitability score"""
        if duration <= 0:
            return 0
        
        earning_per_hour = avg_earning / (duration / 60)  # Convert minutes to hours
        return min(100, earning_per_hour)  # Cap at 100
    
    def _assess_job_risk(self, job: Dict) -> str:
        """Assess job risk level"""
        # Risk factors
        earning_variance = job["estimated_earning_max"] - job["estimated_earning_min"]
        duration = job["estimated_duration"]
        
        # Risk assessment logic
        if earning_variance > 500 or duration > 240:  # 4+ hours
            return "HIGH"
        elif earning_variance > 200 or duration > 120:  # 2+ hours
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_assignment_reason(self, job: Dict, mechanic_id: int) -> str:
        """Get transparent assignment reason"""
        distance = self._calculate_distance(0, 0, job["location_lat"], job["location_long"])
        
        if distance < 2:
            return "Nearest available mechanic"
        elif job["estimated_earning_max"] > 800:
            return "High value job match"
        else:
            return "Skill and availability match"
    
    def accept_job_request(self, mechanic_id: int, job_id: int) -> Dict:
        """Accept job request with full validation"""
        # Check if mechanic can accept job
        mechanic_status = self.db.get_mechanic_status(mechanic_id)
        
        if not mechanic_status:
            return {"success": False, "error": "Mechanic not found"}
        
        if mechanic_status["is_busy"]:
            return {"success": False, "error": "Mechanic is currently busy"}
        
        if mechanic_status["online_status"] != "ONLINE":
            return {"success": False, "error": "Mechanic must be online to accept jobs"}
        
        # Accept the job
        success = self.db.accept_job(job_id, mechanic_id)
        
        if success:
            return {
                "success": True,
                "message": "Job accepted successfully",
                "job_id": job_id,
                "next_status": "ON_THE_WAY",
                "estimated_arrival": self._calculate_arrival_time(mechanic_id, job_id)
            }
        
        return {"success": False, "error": "Failed to accept job"}
    
    def _calculate_arrival_time(self, mechanic_id: int, job_id: int) -> str:
        """Calculate estimated arrival time"""
        # Simplified - would use actual routing in production
        return datetime.now() + timedelta(minutes=30).strftime("%I:%M %p")
    
    # ==================== ACTIVE JOB MANAGEMENT ====================
    
    def get_active_jobs(self, mechanic_id: int) -> Dict:
        """Get mechanic's active jobs with full lifecycle"""
        active_jobs = self.db.get_active_jobs(mechanic_id)
        
        # Enhance with next actions and progress
        enhanced_jobs = []
        for job in active_jobs:
            enhanced_job = {
                **job,
                "progress_percentage": self._calculate_job_progress(job),
                "next_actions": self._get_next_actions(job["status"]),
                "time_in_status": self._calculate_time_in_status(job),
                "estimated_completion": self._estimate_completion_time(job)
            }
            enhanced_jobs.append(enhanced_job)
        
        return {
            "success": True,
            "jobs": enhanced_jobs,
            "total_active": len(enhanced_jobs)
        }
    
    def _calculate_job_progress(self, job: Dict) -> int:
        """Calculate job progress percentage"""
        status_progress = {
            "ACCEPTED": 10,
            "ON_THE_WAY": 30,
            "ARRIVED": 50,
            "WORKING": 80,
            "COMPLETED": 100
        }
        return status_progress.get(job["status"], 0)
    
    def _get_next_actions(self, status: str) -> List[str]:
        """Get next available actions for job status"""
        actions = {
            "ACCEPTED": ["Start Journey", "Contact Customer"],
            "ON_THE_WAY": ["Update Location", "Notify Arrival"],
            "ARRIVED": ["Start Work", "Upload Before Photo"],
            "WORKING": ["Complete Work", "Upload After Photo"],
            "COMPLETED": ["Submit Proof", "Rate Customer"]
        }
        return actions.get(status, [])
    
    def _calculate_time_in_status(self, job: Dict) -> str:
        """Calculate how long job has been in current status"""
        if not job.get("created_at"):
            return "Unknown"
        
        # Simplified time calculation
        created = datetime.strptime(job["created_at"], "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        time_diff = now - created
        
        hours = time_diff.total_seconds() / 3600
        if hours < 1:
            return f"{int(time_diff.total_seconds() / 60)} minutes"
        else:
            return f"{int(hours)} hours {int((hours % 1) * 60)} minutes"
    
    def _estimate_completion_time(self, job: Dict) -> str:
        """Estimate job completion time"""
        duration = job.get("estimated_duration", 60)  # Default 1 hour
        return (datetime.now() + timedelta(minutes=duration)).strftime("%I:%M %p")
    
    def update_job_status(self, mechanic_id: int, job_id: int, new_status: str) -> Dict:
        """Update job status with validation"""
        valid_transitions = {
            "ACCEPTED": ["ON_THE_WAY"],
            "ON_THE_WAY": ["ARRIVED"],
            "ARRIVED": ["WORKING"],
            "WORKING": ["COMPLETED"]
        }
        
        # Get current job
        active_jobs = self.db.get_active_jobs(mechanic_id)
        current_job = next((job for job in active_jobs if job["id"] == job_id), None)
        
        if not current_job:
            return {"success": False, "error": "Job not found or not active"}
        
        # Validate transition
        if new_status not in valid_transitions.get(current_job["status"], []):
            return {"success": False, "error": f"Invalid status transition from {current_job['status']}"}
        
        # Update status
        success = self.db.update_job_status(job_id, new_status, mechanic_id)
        
        if success:
            # If job is completed, process earnings
            if new_status == "COMPLETED":
                self._process_job_completion(mechanic_id, job_id)
            
            return {
                "success": True,
                "message": f"Job status updated to {new_status}",
                "next_actions": self._get_next_actions(new_status)
            }
        
        return {"success": False, "error": "Failed to update job status"}
    
    def _process_job_completion(self, mechanic_id: int, job_id: int) -> None:
        """Process job completion and earnings"""
        # Get job details for earning calculation
        active_jobs = self.db.get_active_jobs(mechanic_id)
        job = next((job for job in active_jobs if job["id"] == job_id), None)
        
        if job:
            # Calculate final earning (average of min/max)
            final_earning = (job["estimated_earning_min"] + job["estimated_earning_max"]) / 2
            self.db.add_earning(mechanic_id, job_id, final_earning)
    
    # ==================== EARNINGS & FAIRNESS ====================
    
    def get_earnings_insights(self, mechanic_id: int, period: str = 'all') -> Dict:
        """Get comprehensive earnings insights"""
        # Get basic earnings
        earnings = self.db.get_mechanic_earnings(mechanic_id, period)
        
        # Get additional insights
        metrics = self.db.get_mechanic_metrics(mechanic_id)
        
        # Calculate advanced metrics
        insights = {
            **earnings,
            "income_stability_score": self._calculate_income_stability(mechanic_id),
            "earnings_trend": self._calculate_earnings_trend(mechanic_id),
            "tax_estimation": self._estimate_tax(earnings.get("net_earnings", 0)),
            "savings_suggestion": self._suggest_savings(earnings.get("net_earnings", 0)),
            "most_profitable_service": self._get_most_profitable_service(mechanic_id),
            "peak_earning_day": self._get_peak_earning_day(mechanic_id),
            "commission_breakdown": {
                "total_commission": earnings.get("total_commission", 0),
                "commission_rate": "20%",
                "net_percentage": "80%"
            }
        }
        
        return {
            "success": True,
            "period": period,
            "insights": insights
        }
    
    def _calculate_income_stability(self, mechanic_id: int) -> float:
        """Calculate income stability score (0-100)"""
        # Simplified - would use historical data
        return 75.0  # Default score
    
    def _calculate_earnings_trend(self, mechanic_id: int) -> str:
        """Calculate earnings trend"""
        # Simplified - would compare last week vs current week
        return "STABLE"  # Default trend
    
    def _estimate_tax(self, net_earnings: float) -> Dict:
        """Estimate yearly tax"""
        yearly_earnings = net_earnings * 52  # Weekly to yearly approximation
        tax_rate = 0.15  # 15% tax rate (simplified)
        estimated_tax = yearly_earnings * tax_rate
        
        return {
            "yearly_earnings": yearly_earnings,
            "estimated_tax": estimated_tax,
            "after_tax_income": yearly_earnings - estimated_tax,
            "tax_rate": f"{tax_rate * 100}%"
        }
    
    def _suggest_savings(self, net_earnings: float) -> Dict:
        """Suggest savings percentage"""
        suggestions = {
            "conservative": {"rate": 10, "amount": net_earnings * 0.10},
            "moderate": {"rate": 20, "amount": net_earnings * 0.20},
            "aggressive": {"rate": 30, "amount": net_earnings * 0.30}
        }
        return suggestions
    
    def _get_most_profitable_service(self, mechanic_id: int) -> str:
        """Get most profitable service type"""
        # Simplified - would analyze actual job data
        return "General Repairs"
    
    def _get_peak_earning_day(self, mechanic_id: int) -> str:
        """Get peak earning day"""
        # Simplified - would analyze historical data
        return "Friday"
    
    # ==================== PERFORMANCE & SAFETY ====================
    
    def get_performance_safety(self, mechanic_id: int) -> Dict:
        """Get comprehensive performance and safety insights"""
        metrics = self.db.get_mechanic_metrics(mechanic_id)
        emergency_alerts = self.db.get_emergency_alerts(mechanic_id)
        
        # Generate tips based on metrics
        tips = self._generate_performance_tips(metrics)
        
        # Calculate safety score
        safety_score = self._calculate_safety_score(metrics, emergency_alerts)
        
        return {
            "success": True,
            "metrics": metrics,
            "safety_score": safety_score,
            "emergency_alerts": emergency_alerts,
            "performance_tips": tips,
            "improvement_areas": self._identify_improvement_areas(metrics)
        }
    
    def _generate_performance_tips(self, metrics: Dict) -> List[str]:
        """Generate performance improvement tips"""
        tips = []
        
        if metrics.get("completion_rate", 0) < 90:
            tips.append("Focus on completing all accepted jobs to improve completion rate")
        
        if metrics.get("on_time_rate", 0) < 85:
            tips.append("Work on time management to improve on-time performance")
        
        if metrics.get("acceptance_rate", 0) < 70:
            tips.append("Consider accepting more jobs to increase acceptance rate")
        
        # Weekend demand tip
        demand_analysis = self.db.get_demand_analysis()
        if demand_analysis.get("peak_hour"):
            tips.append("Weekend demand is high - consider being available during peak hours")
        
        return tips
    
    def _calculate_safety_score(self, metrics: Dict, emergency_alerts: List[Dict]) -> float:
        """Calculate safety score"""
        base_score = metrics.get("trust_score", 50)
        
        # Deduct points for emergency alerts
        recent_alerts = len([alert for alert in emergency_alerts 
                           if (datetime.now() - datetime.strptime(alert["alert_time"], "%Y-%m-%d %H:%M:%S")).days <= 30])
        
        safety_score = max(0, base_score - (recent_alerts * 5))
        return round(safety_score, 2)
    
    def _identify_improvement_areas(self, metrics: Dict) -> List[str]:
        """Identify areas needing improvement"""
        areas = []
        
        if metrics.get("completion_rate", 0) < 85:
            areas.append("Job Completion")
        
        if metrics.get("on_time_rate", 0) < 80:
            areas.append("Time Management")
        
        if metrics.get("acceptance_rate", 0) < 60:
            areas.append("Job Acceptance")
        
        return areas
    
    # ==================== EMERGENCY SOS ====================
    
    def trigger_emergency_sos(self, mechanic_id: int, latitude: float, longitude: float) -> Dict:
        """Trigger emergency SOS alert"""
        success = self.db.create_emergency_alert(mechanic_id, latitude, longitude)
        
        if success:
            return {
                "success": True,
                "message": "Emergency alert triggered successfully",
                "alert_id": self._get_latest_alert_id(mechanic_id),
                "location": {"lat": latitude, "lng": longitude},
                "timestamp": datetime.now().isoformat()
            }
        
        return {"success": False, "error": "Failed to trigger emergency alert"}
    
    def _get_latest_alert_id(self, mechanic_id: int) -> int:
        """Get latest emergency alert ID"""
        alerts = self.db.get_emergency_alerts(mechanic_id)
        return alerts[0]["id"] if alerts else 0
    
    # ==================== JOB PROOF SYSTEM ====================
    
    def upload_job_proof(self, mechanic_id: int, job_id: int, 
                      before_file=None, after_file=None, notes: str = "") -> Dict:
        """Upload job completion proof with file handling"""
        try:
            # Handle file uploads
            before_path = None
            after_path = None
            
            if before_file:
                filename = secure_filename(before_file.filename)
                before_path = os.path.join(self.upload_folder, f"before_{job_id}_{filename}")
                before_file.save(before_path)
            
            if after_file:
                filename = secure_filename(after_file.filename)
                after_path = os.path.join(self.upload_folder, f"after_{job_id}_{filename}")
                after_file.save(after_path)
            
            # Save to database
            success = self.db.upload_job_proof(job_id, before_path, after_path, notes)
            
            if success:
                return {
                    "success": True,
                    "message": "Job proof uploaded successfully",
                    "proof_id": self._get_latest_proof_id(job_id),
                    "files": {
                        "before_photo": before_path,
                        "after_photo": after_path
                    }
                }
            
            return {"success": False, "error": "Failed to upload proof"}
            
        except Exception as e:
            return {"success": False, "error": f"Upload error: {str(e)}"}
    
    def _get_latest_proof_id(self, job_id: int) -> int:
        """Get latest proof ID for job"""
        proofs = self.db.get_job_proofs(job_id)
        return proofs[0]["id"] if proofs else 0

# Initialize service instance
mechanic_dashboard_service = MechanicDashboardService()
