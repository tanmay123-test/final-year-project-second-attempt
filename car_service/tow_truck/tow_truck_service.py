"""
Tow Truck Driver Service Layer
Complete business logic for tow truck driver management system
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from werkzeug.utils import secure_filename

from .tow_truck_db import tow_truck_db

class TowTruckService:
    """Complete service layer for Tow Truck Driver System"""
    
    def __init__(self):
        self.db = tow_truck_db
        self.upload_folder = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "tow_truck_proofs")
        os.makedirs(self.upload_folder, exist_ok=True)
    
    # ==================== ONLINE STATUS & EMERGENCY ZONE MANAGEMENT ====================
    
    def toggle_tow_driver_online_status(self, driver_id: int) -> Dict:
        """Toggle tow driver online/offline status"""
        current_status = self.db.get_tow_driver_status(driver_id)
        
        if not current_status:
            return {"success": False, "error": "Tow driver not found"}
        
        new_status = "OFFLINE" if current_status["online_status"] == "ONLINE" else "ONLINE"
        
        # Update status
        success = self.db.update_tow_driver_status(driver_id, online_status=new_status)
        
        if success:
            # Calculate and update priority score
            priority = self.db.calculate_tow_driver_priority_score(driver_id)
            
            return {
                "success": True,
                "new_status": new_status,
                "priority_score": priority,
                "message": f"Status updated to {new_status}"
            }
        
        return {"success": False, "error": "Failed to update status"}
    
    def get_emergency_zone_status(self, driver_id: int) -> Dict:
        """Get comprehensive emergency zone status for tow driver"""
        # Get emergency zone analysis
        zone_analysis = self.db.get_emergency_zone_analysis()
        
        # Get driver's current status
        driver_status = self.db.get_tow_driver_status(driver_id)
        
        # Calculate potential earnings
        pending_requests = self.db.get_pending_tow_requests()
        relevant_requests = [request for request in pending_requests]  # All requests are relevant
        
        # Calculate potential earnings
        potential_earnings = sum(
            (request["estimated_price_min"] + request["estimated_price_max"]) / 2 
            for request in relevant_requests[:5]  # Top 5 requests
        )
        
        # Fairness transparency
        fairness_score = self._calculate_tow_fairness_score(driver_id)
        
        # High incident zone detection
        high_incident_zone = self._identify_high_incident_zone(zone_analysis['high_incident_zones'])
        
        # Risk bonus multiplier
        risk_multiplier = self._calculate_risk_bonus_multiplier(zone_analysis['risk_demand'])
        
        return {
            "success": True,
            "emergency_demand_level": zone_analysis["emergency_demand_level"],
            "online_drivers": zone_analysis["online_drivers"],
            "priority_score": driver_status.get("priority_score", 0) if driver_status else 0,
            "potential_earnings_today": potential_earnings,
            "fairness_score": fairness_score,
            "risk_demand": zone_analysis["risk_demand"],
            "current_status": driver_status["online_status"] if driver_status else "OFFLINE",
            "is_busy": driver_status["is_busy"] if driver_status else False,
            "truck_type": driver_status["truck_type"] if driver_status else "FLATBED",
            "high_incident_zone": high_incident_zone,
            "heavy_vehicle_alert": zone_analysis["heavy_vehicle_alert"],
            "surge_pricing_active": zone_analysis["surge_pricing_active"],
            "risk_bonus_multiplier": risk_multiplier
        }
    
    def _calculate_tow_fairness_score(self, driver_id: int) -> float:
        """Calculate fairness transparency score for tow driver"""
        metrics = self.db.get_tow_driver_metrics(driver_id)
        
        if not metrics:
            return 50.0  # Default score
        
        # Fairness based on performance consistency
        completion_score = metrics["completion_rate"]
        on_time_score = metrics["on_time_rate"]
        risk_score = metrics["risk_handling_score"]
        
        # Calculate fairness score (0-100)
        fairness = (completion_score * 0.4) + (on_time_score * 0.3) + (risk_score * 0.3)
        return round(fairness, 2)
    
    def _identify_high_incident_zone(self, high_incident_zones: List[Dict]) -> str:
        """Identify high incident zone"""
        if not high_incident_zones:
            return "No active zones"
        
        highest_zone = max(high_incident_zones, key=lambda x: x['incident_count'])
        return f"{highest_zone['zone']} ({highest_zone['incident_count']} incidents)"
    
    def _calculate_risk_bonus_multiplier(self, risk_demand: List[Dict]) -> float:
        """Calculate risk bonus multiplier based on demand"""
        high_risk_count = sum(demand['pending_count'] for demand in risk_demand if demand['risk_level'] == 'HIGH')
        
        if high_risk_count >= 5:
            return 1.5  # 50% bonus
        elif high_risk_count >= 3:
            return 1.3  # 30% bonus
        elif high_risk_count >= 1:
            return 1.15  # 15% bonus
        else:
            return 1.0  # No bonus
    
    # ==================== EMERGENCY TOW REQUESTS ====================
    
    def get_emergency_tow_requests(self, driver_id: int) -> Dict:
        """Get emergency tow requests with full transparency"""
        pending_requests = self.db.get_pending_tow_requests()
        driver_status = self.db.get_tow_driver_status(driver_id)
        
        # Enhance each request with transparency data
        enhanced_requests = []
        for request in pending_requests:
            # Calculate distance (simplified - would use actual location in production)
            pickup_distance = self._calculate_distance(
                driver_status.get("last_location_lat", 0),
                driver_status.get("last_location_long", 0),
                request["pickup_lat"],
                request["pickup_long"]
            )
            
            # Calculate risk bonus
            risk_bonus = self._calculate_request_risk_bonus(request)
            
            # Assignment reason
            assignment_reason = self._get_tow_assignment_reason(request, driver_id)
            
            # Customer rating (simplified - would come from user data)
            customer_rating = 4.5  # Default rating
            
            # Route efficiency
            route_efficiency = self._calculate_route_efficiency(request)
            
            enhanced_request = {
                **request,
                "pickup_distance_km": round(pickup_distance, 2),
                "risk_bonus": risk_bonus,
                "assignment_reason": assignment_reason,
                "customer_rating": customer_rating,
                "route_efficiency": route_efficiency,
                "estimated_total_earning": (request["estimated_price_min"] + request["estimated_price_max"]) / 2 + risk_bonus,
                "urgency_level": self._calculate_urgency_level(request),
                "truck_compatibility": self._check_truck_compatibility(request, driver_status.get("truck_type", "FLATBED"))
            }
            
            enhanced_requests.append(enhanced_request)
        
        # Sort by priority (urgency + risk bonus + proximity)
        enhanced_requests.sort(key=lambda x: (x["urgency_level"], x["risk_bonus"], -x["pickup_distance_km"]), reverse=True)
        
        return {
            "success": True,
            "requests": enhanced_requests,
            "total_requests": len(enhanced_requests),
            "driver_status": "ONLINE" if driver_status and driver_status["online_status"] == "ONLINE" else "OFFLINE",
            "truck_type": driver_status.get("truck_type", "FLATBED") if driver_status else "FLATBED"
        }
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates (simplified)"""
        return abs(lat1 - lat2) * 111 + abs(lng1 - lng2) * 111
    
    def _calculate_request_risk_bonus(self, request: Dict) -> float:
        """Calculate risk bonus for specific tow request"""
        base_price = (request["estimated_price_min"] + request["estimated_price_max"]) / 2
        
        if request["risk_level"] == "HIGH":
            return base_price * 0.3  # 30% risk bonus
        elif request["risk_level"] == "MEDIUM":
            return base_price * 0.15  # 15% risk bonus
        else:
            return 0.0
    
    def _get_tow_assignment_reason(self, request: Dict, driver_id: int) -> str:
        """Get transparent assignment reason for tow request"""
        distance = self._calculate_distance(0, 0, request["pickup_lat"], request["pickup_long"])
        
        if distance < 3:
            return "Nearest available tow truck"
        elif request["risk_level"] == "HIGH":
            return "High-risk emergency assignment"
        elif request["vehicle_type"] in ["TRUCK", "BUS"]:
            return "Heavy vehicle specialist required"
        else:
            return "Availability and proximity match"
    
    def _calculate_route_efficiency(self, request: Dict) -> float:
        """Calculate route efficiency score"""
        total_distance = request["distance_km"]
        estimated_duration = request["estimated_duration"]
        
        if estimated_duration <= 0:
            return 0
        
        # Efficiency based on distance per minute
        efficiency = total_distance / estimated_duration
        return min(100, efficiency * 10)  # Scale to 0-100
    
    def _calculate_urgency_level(self, request: Dict) -> int:
        """Calculate urgency level (1-10)"""
        urgency = 5  # Base urgency
        
        if request["risk_level"] == "HIGH":
            urgency += 3
        elif request["risk_level"] == "MEDIUM":
            urgency += 1
        
        if request["vehicle_type"] in ["TRUCK", "BUS"]:
            urgency += 2
        
        return min(10, urgency)
    
    def _check_truck_compatibility(self, request: Dict, truck_type: str) -> bool:
        """Check if truck type is compatible with vehicle"""
        vehicle_type = request["vehicle_type"]
        
        if truck_type == "HEAVY_DUTY":
            return vehicle_type in ["TRUCK", "BUS", "HEAVY_VEHICLE", "SUV"]
        elif truck_type == "FLATBED":
            return vehicle_type in ["SUV", "SEDAN", "HATCHBACK", "MOTORCYCLE"]
        elif truck_type == "WHEEL_LIFT":
            return vehicle_type in ["SEDAN", "HATCHBACK", "MOTORCYCLE"]
        
        return False
    
    def accept_tow_request(self, driver_id: int, request_id: int) -> Dict:
        """Accept emergency tow request with full validation"""
        # Check if driver can accept request
        driver_status = self.db.get_tow_driver_status(driver_id)
        
        if not driver_status:
            return {"success": False, "error": "Tow driver not found"}
        
        if driver_status["is_busy"]:
            return {"success": False, "error": "Tow driver is currently busy"}
        
        if driver_status["online_status"] != "ONLINE":
            return {"success": False, "error": "Tow driver must be online to accept requests"}
        
        # Accept the request
        success = self.db.accept_tow_request(request_id, driver_id)
        
        if success:
            return {
                "success": True,
                "message": "Emergency tow request accepted successfully",
                "request_id": request_id,
                "next_status": "ON_THE_WAY",
                "estimated_arrival": self._calculate_tow_arrival_time(driver_id, request_id),
                "risk_bonus_applied": self._calculate_request_risk_bonus({"risk_level": "HIGH"})  # Simplified
            }
        
        return {"success": False, "error": "Failed to accept tow request"}
    
    def _calculate_tow_arrival_time(self, driver_id: int, request_id: int) -> str:
        """Calculate estimated arrival time for tow"""
        # Simplified - would use actual routing in production
        return datetime.now() + timedelta(minutes=20).strftime("%I:%M %p")
    
    # ==================== ACTIVE TOWING OPERATIONS ====================
    
    def get_active_tow_operations(self, driver_id: int) -> Dict:
        """Get tow driver's active towing operations with full lifecycle"""
        active_operations = self.db.get_active_tow_operations(driver_id)
        
        # Enhance with next actions and progress
        enhanced_operations = []
        for operation in active_operations:
            enhanced_operation = {
                **operation,
                "progress_percentage": self._calculate_tow_progress(operation),
                "next_actions": self._get_tow_next_actions(operation["status"]),
                "time_in_status": self._calculate_tow_time_in_status(operation),
                "estimated_completion": self._estimate_tow_completion(operation),
                "route_efficiency": self._calculate_route_efficiency(operation),
                "risk_bonus_earned": self._calculate_operation_risk_bonus(operation),
                "manual_charge_allowed": operation["status"] in ["ARRIVED", "LOADING"],
                "safety_alerts": self._get_operation_safety_alerts(operation)
            }
            enhanced_operations.append(enhanced_operation)
        
        return {
            "success": True,
            "operations": enhanced_operations,
            "total_active": len(enhanced_operations)
        }
    
    def _calculate_tow_progress(self, operation: Dict) -> int:
        """Calculate tow operation progress percentage"""
        status_progress = {
            "ACCEPTED": 10,
            "ON_THE_WAY": 25,
            "ARRIVED": 40,
            "LOADING": 60,
            "IN_TRANSIT": 80,
            "COMPLETED": 100
        }
        return status_progress.get(operation["status"], 0)
    
    def _get_tow_next_actions(self, status: str) -> List[str]:
        """Get next available actions for tow operation status"""
        actions = {
            "ACCEPTED": ["Start Tow Operation", "Contact Customer", "Check Equipment"],
            "ON_THE_WAY": ["Update Location", "Notify Arrival ETA", "Check Traffic"],
            "ARRIVED": ["Upload Pickup Photo", "Assess Vehicle Condition", "Prepare Loading"],
            "LOADING": ["Upload Vehicle Loaded Photo", "Secure Vehicle", "Document Damage"],
            "IN_TRANSIT": ["Update Location", "Notify Drop ETA", "Monitor Vehicle"],
            "COMPLETED": ["Upload Drop Photo", "Add Damage Notes", "Complete Operation"]
        }
        return actions.get(status, [])
    
    def _calculate_tow_time_in_status(self, operation: Dict) -> str:
        """Calculate how long operation has been in current status"""
        if not operation.get("created_at"):
            return "Unknown"
        
        created = datetime.strptime(operation["created_at"], "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        time_diff = now - created
        
        hours = time_diff.total_seconds() / 3600
        if hours < 1:
            return f"{int(time_diff.total_seconds() / 60)} minutes"
        else:
            return f"{int(hours)} hours {int((hours % 1) * 60)} minutes"
    
    def _estimate_tow_completion(self, operation: Dict) -> str:
        """Estimate tow operation completion time"""
        duration = operation.get("estimated_duration", 45)  # Default 45 minutes
        return (datetime.now() + timedelta(minutes=duration)).strftime("%I:%M %p")
    
    def _calculate_operation_risk_bonus(self, operation: Dict) -> float:
        """Calculate risk bonus for current operation"""
        base_price = (operation["estimated_price_min"] + operation["estimated_price_max"]) / 2
        
        if operation["risk_level"] == "HIGH":
            return base_price * 0.3
        elif operation["risk_level"] == "MEDIUM":
            return base_price * 0.15
        else:
            return 0.0
    
    def _get_operation_safety_alerts(self, operation: Dict) -> List[str]:
        """Get safety alerts for current operation"""
        alerts = []
        
        if operation["risk_level"] == "HIGH":
            alerts.append("High-risk operation - use extra caution")
        
        if operation["vehicle_type"] in ["TRUCK", "BUS"]:
            alerts.append("Heavy vehicle - ensure proper equipment")
        
        if operation["distance_km"] > 20:
            alerts.append("Long distance tow - check fuel and equipment")
        
        return alerts
    
    def update_tow_operation_status(self, driver_id: int, request_id: int, new_status: str) -> Dict:
        """Update tow operation status with validation"""
        valid_transitions = {
            "ACCEPTED": ["ON_THE_WAY"],
            "ON_THE_WAY": ["ARRIVED"],
            "ARRIVED": ["LOADING"],
            "LOADING": ["IN_TRANSIT"],
            "IN_TRANSIT": ["COMPLETED"]
        }
        
        # Get current operation
        active_operations = self.db.get_active_tow_operations(driver_id)
        current_operation = next((op for op in active_operations if op["id"] == request_id), None)
        
        if not current_operation:
            return {"success": False, "error": "Tow operation not found or not active"}
        
        # Validate transition
        if new_status not in valid_transitions.get(current_operation["status"], []):
            return {"success": False, "error": f"Invalid status transition from {current_operation['status']}"}
        
        # Update status
        success = self.db.update_tow_request_status(request_id, new_status, driver_id)
        
        if success:
            # If completed, process earnings
            if new_status == "COMPLETED":
                self._process_tow_completion(driver_id, request_id)
            
            return {
                "success": True,
                "message": f"Tow operation status updated to {new_status}",
                "next_actions": self._get_tow_next_actions(new_status)
            }
        
        return {"success": False, "error": "Failed to update tow operation status"}
    
    def _process_tow_completion(self, driver_id: int, request_id: int) -> None:
        """Process tow operation completion and earnings"""
        # Get operation details for earning calculation
        active_operations = self.db.get_active_tow_operations(driver_id)
        operation = next((op for op in active_operations if op["id"] == request_id), None)
        
        if operation:
            # Calculate final earning
            final_price = (operation["estimated_price_min"] + operation["estimated_price_max"]) / 2
            risk_bonus = self._calculate_operation_risk_bonus(operation)
            distance_km = operation["distance_km"]
            
            self.db.add_tow_earning(driver_id, request_id, final_price, distance_km, risk_bonus)
    
    # ==================== EARNINGS & DISTANCE INSIGHTS ====================
    
    def get_tow_earnings_insights(self, driver_id: int, period: str = 'all') -> Dict:
        """Get comprehensive tow earnings and distance insights"""
        # Get basic earnings
        earnings = self.db.get_tow_driver_earnings(driver_id, period)
        
        # Get additional insights
        metrics = self.db.get_tow_driver_metrics(driver_id)
        
        # Calculate advanced metrics
        insights = {
            **earnings,
            "distance_profitability_score": self._calculate_distance_profitability(earnings),
            "heavy_vehicle_bonus": self._calculate_heavy_vehicle_bonus(driver_id, period),
            "earnings_trend": self._calculate_tow_earnings_trend(driver_id),
            "tax_projection": self._estimate_tow_tax(earnings.get("net_earnings", 0)),
            "surge_performance_score": self._calculate_surge_performance(driver_id),
            "most_profitable_vehicle_type": self._get_most_profitable_vehicle_type(driver_id),
            "avg_earning_per_km": earnings.get("avg_earning", 0) / max(earnings.get("avg_distance", 1), 1),
            "commission_breakdown": {
                "total_commission": earnings.get("total_commission", 0),
                "commission_rate": "20%",
                "risk_bonus_total": earnings.get("total_risk_bonus", 0),
                "net_percentage": "80% + Risk Bonus"
            }
        }
        
        return {
            "success": True,
            "period": period,
            "insights": insights
        }
    
    def _calculate_distance_profitability(self, earnings: Dict) -> float:
        """Calculate distance profitability score"""
        total_distance = earnings.get("total_distance", 0)
        net_earnings = earnings.get("net_earnings", 0)
        
        if total_distance <= 0:
            return 0
        
        # Profitability per km
        profit_per_km = net_earnings / total_distance
        return min(100, profit_per_km * 2)  # Scale to 0-100
    
    def _calculate_heavy_vehicle_bonus(self, driver_id: int, period: str) -> float:
        """Calculate heavy vehicle bonus earnings"""
        # Simplified - would analyze actual tow data
        return 150.0  # Default bonus
    
    def _calculate_tow_earnings_trend(self, driver_id: int) -> str:
        """Calculate tow earnings trend"""
        # Simplified - would compare last week vs current week
        return "INCREASING"  # Default trend
    
    def _estimate_tow_tax(self, net_earnings: float) -> Dict:
        """Estimate yearly tax for tow driver"""
        yearly_earnings = net_earnings * 52  # Weekly to yearly approximation
        tax_rate = 0.18  # 18% tax rate (simplified)
        estimated_tax = yearly_earnings * tax_rate
        
        return {
            "yearly_earnings": yearly_earnings,
            "estimated_tax": estimated_tax,
            "after_tax_income": yearly_earnings - estimated_tax,
            "tax_rate": f"{tax_rate * 100}%"
        }
    
    def _calculate_surge_performance(self, driver_id: int) -> float:
        """Calculate surge pricing performance score"""
        # Simplified - would analyze actual surge performance
        return 75.0  # Default score
    
    def _get_most_profitable_vehicle_type(self, driver_id: int) -> str:
        """Get most profitable vehicle type for tow driver"""
        # Simplified - would analyze actual tow data
        return "SUV"  # Default
    
    # ==================== PERFORMANCE, SAFETY & RISK SUPPORT ====================
    
    def get_tow_performance_safety(self, driver_id: int) -> Dict:
        """Get comprehensive tow performance and safety insights"""
        metrics = self.db.get_tow_driver_metrics(driver_id)
        emergency_alerts = self.db.get_tow_emergency_alerts(driver_id)
        
        # Generate tips based on metrics
        tips = self._generate_tow_performance_tips(metrics)
        
        # Calculate safety score
        safety_score = self._calculate_tow_safety_score(metrics, emergency_alerts)
        
        # Risk assessment
        risk_assessment = self._assess_driver_risk_profile(metrics)
        
        return {
            "success": True,
            "metrics": metrics,
            "safety_score": safety_score,
            "emergency_alerts": emergency_alerts,
            "performance_tips": tips,
            "improvement_areas": self._identify_tow_improvement_areas(metrics),
            "risk_assessment": risk_assessment,
            "night_risk_alert": self._check_night_risk_alert(),
            "unsafe_zone_alerts": self._get_unsafe_zone_alerts()
        }
    
    def _generate_tow_performance_tips(self, metrics: Dict) -> List[str]:
        """Generate tow operation performance improvement tips"""
        tips = []
        
        if metrics.get("completion_rate", 0) < 90:
            tips.append("Focus on completing all accepted tows to improve completion rate")
        
        if metrics.get("on_time_rate", 0) < 85:
            tips.append("Improve route planning and traffic awareness for better on-time performance")
        
        if metrics.get("acceptance_rate", 0) < 70:
            tips.append("Consider accepting more emergency tows to increase acceptance rate")
        
        if metrics.get("risk_handling_score", 0) < 80:
            tips.append("Take additional safety training for high-risk towing operations")
        
        # Tow-specific tips
        zone_analysis = self.db.get_emergency_zone_analysis()
        if zone_analysis.get("emergency_demand_level") == "HIGH":
            tips.append("High emergency demand - maximize availability during peak hours")
        
        return tips
    
    def _calculate_tow_safety_score(self, metrics: Dict, emergency_alerts: List[Dict]) -> float:
        """Calculate safety score for tow driver"""
        base_score = metrics.get("trust_score", 50)
        
        # Add risk handling bonus
        risk_bonus = metrics.get("risk_handling_score", 0) * 0.2
        
        # Deduct points for emergency alerts
        recent_alerts = len([alert for alert in emergency_alerts 
                           if (datetime.now() - datetime.strptime(alert["alert_time"], "%Y-%m-%d %H:%M:%S")).days <= 30])
        
        safety_score = max(0, base_score + risk_bonus - (recent_alerts * 3))
        return round(safety_score, 2)
    
    def _assess_driver_risk_profile(self, metrics: Dict) -> Dict:
        """Assess driver's risk profile"""
        risk_score = 50  # Base score
        
        if metrics.get("risk_handling_score", 0) > 80:
            risk_score -= 20  # Lower risk
        elif metrics.get("risk_handling_score", 0) < 60:
            risk_score += 20  # Higher risk
        
        if metrics.get("completion_rate", 0) > 95:
            risk_score -= 10
        elif metrics.get("completion_rate", 0) < 85:
            risk_score += 15
        
        risk_level = "LOW" if risk_score < 40 else "MEDIUM" if risk_score < 60 else "HIGH"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "recommendation": "Suitable for high-risk operations" if risk_level == "LOW" else "Focus on safety training"
        }
    
    def _identify_tow_improvement_areas(self, metrics: Dict) -> List[str]:
        """Identify areas needing improvement for tow driver"""
        areas = []
        
        if metrics.get("completion_rate", 0) < 85:
            areas.append("Tow Completion")
        
        if metrics.get("on_time_rate", 0) < 80:
            areas.append("Time Management")
        
        if metrics.get("acceptance_rate", 0) < 60:
            areas.append("Request Acceptance")
        
        if metrics.get("risk_handling_score", 0) < 70:
            areas.append("Risk Handling")
        
        return areas
    
    def _check_night_risk_alert(self) -> bool:
        """Check if night risk alert should be active"""
        current_hour = datetime.now().hour
        return 22 <= current_hour or current_hour <= 5  # 10 PM to 5 AM
    
    def _get_unsafe_zone_alerts(self) -> List[Dict]:
        """Get unsafe zone alerts"""
        # Simplified - would use actual incident data
        alerts = []
        
        current_hour = datetime.now().hour
        if 22 <= current_hour or current_hour <= 5:
            alerts.append({
                "type": "NIGHT_RISK",
                "message": "Night operations detected - use extra caution",
                "severity": "MEDIUM",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    # ==================== EMERGENCY SOS ====================
    
    def trigger_tow_emergency_sos(self, driver_id: int, latitude: float, longitude: float) -> Dict:
        """Trigger emergency SOS alert for tow driver"""
        success = self.db.create_tow_emergency_alert(driver_id, latitude, longitude)
        
        if success:
            return {
                "success": True,
                "message": "Emergency alert triggered successfully",
                "alert_id": self._get_latest_tow_alert_id(driver_id),
                "location": {"lat": latitude, "lng": longitude},
                "timestamp": datetime.now().isoformat(),
                "admin_notified": True
            }
        
        return {"success": False, "error": "Failed to trigger emergency alert"}
    
    def _get_latest_tow_alert_id(self, driver_id: int) -> int:
        """Get latest emergency alert ID for tow driver"""
        alerts = self.db.get_tow_emergency_alerts(driver_id)
        return alerts[0]["id"] if alerts else 0
    
    # ==================== TOWING PROOF SYSTEM ====================
    
    def upload_towing_proof(self, driver_id: int, request_id: int, 
                          pickup_file=None, loaded_file=None, drop_file=None, notes: str = "") -> Dict:
        """Upload tow operation completion proof with file handling"""
        try:
            # Handle file uploads
            pickup_path = None
            loaded_path = None
            drop_path = None
            
            if pickup_file:
                filename = secure_filename(pickup_file.filename)
                pickup_path = os.path.join(self.upload_folder, f"pickup_{request_id}_{filename}")
                pickup_file.save(pickup_path)
            
            if loaded_file:
                filename = secure_filename(loaded_file.filename)
                loaded_path = os.path.join(self.upload_folder, f"loaded_{request_id}_{filename}")
                loaded_file.save(loaded_path)
            
            if drop_file:
                filename = secure_filename(drop_file.filename)
                drop_path = os.path.join(self.upload_folder, f"drop_{request_id}_{filename}")
                drop_file.save(drop_path)
            
            # Save to database
            success = self.db.upload_towing_proof(request_id, pickup_path, loaded_path, drop_path, notes)
            
            if success:
                return {
                    "success": True,
                    "message": "Tow operation proof uploaded successfully",
                    "proof_id": self._get_latest_tow_proof_id(request_id),
                    "files": {
                        "pickup_photo": pickup_path,
                        "vehicle_loaded_photo": loaded_path,
                        "drop_photo": drop_path
                    }
                }
            
            return {"success": False, "error": "Failed to upload proof"}
            
        except Exception as e:
            return {"success": False, "error": f"Upload error: {str(e)}"}
    
    def _get_latest_tow_proof_id(self, request_id: int) -> int:
        """Get latest proof ID for tow request"""
        proofs = self.db.get_towing_proofs(request_id)
        return proofs[0]["id"] if proofs else 0

# Initialize service instance
tow_truck_service = TowTruckService()
