"""
Fuel Delivery Agent Service Layer
Complete business logic for fuel delivery agent management system
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from werkzeug.utils import secure_filename

from .fuel_agent_db import fuel_agent_db

class FuelAgentService:
    """Complete service layer for Fuel Delivery Agent System"""
    
    def __init__(self):
        self.db = fuel_agent_db
        self.upload_folder = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "fuel_delivery_proofs")
        os.makedirs(self.upload_folder, exist_ok=True)
    
    # ==================== ONLINE STATUS MANAGEMENT ====================
    
    def toggle_fuel_agent_online_status(self, agent_id: int) -> Dict:
        """Toggle fuel agent online/offline status"""
        current_status = self.db.get_fuel_agent_status(agent_id)
        
        if not current_status:
            return {"success": False, "error": "Fuel agent not found"}
        
        new_status = "OFFLINE" if current_status["online_status"] == "ONLINE" else "ONLINE"
        
        # Update status
        success = self.db.update_fuel_agent_status(agent_id, online_status=new_status)
        
        if success:
            # Calculate and update priority score
            priority = self.db.calculate_fuel_agent_priority_score(agent_id)
            
            return {
                "success": True,
                "new_status": new_status,
                "priority_score": priority,
                "message": f"Status updated to {new_status}"
            }
        
        return {"success": False, "error": "Failed to update status"}
    
    def get_fuel_demand_status(self, agent_id: int) -> Dict:
        """Get comprehensive fuel demand status for agent"""
        # Get market demand analysis
        demand_analysis = self.db.get_fuel_demand_analysis()
        
        # Get agent's current status
        agent_status = self.db.get_fuel_agent_status(agent_id)
        
        # Calculate potential earnings
        pending_orders = self.db.get_pending_fuel_orders()
        relevant_orders = [order for order in pending_orders]  # All orders are relevant for fuel agents
        
        # Calculate potential earnings
        potential_earnings = sum(
            (order["estimated_earning_min"] + order["estimated_earning_max"]) / 2 
            for order in relevant_orders[:5]  # Top 5 orders
        )
        
        # Fairness transparency
        fairness_score = self._calculate_fuel_fairness_score(agent_id)
        
        # High delivery zone detection
        high_delivery_zone = self._identify_high_delivery_zone(demand_analysis['fuel_demand'])
        
        return {
            "success": True,
            "demand_level": demand_analysis["demand_level"],
            "online_agents": demand_analysis["online_agents"],
            "peak_hour": demand_analysis["peak_hour"],
            "priority_score": agent_status.get("priority_score", 0) if agent_status else 0,
            "potential_earnings_today": potential_earnings,
            "fairness_score": fairness_score,
            "fuel_demand": demand_analysis["fuel_demand"],
            "current_status": agent_status["online_status"] if agent_status else "OFFLINE",
            "is_busy": agent_status["is_busy"] if agent_status else False,
            "high_delivery_zone": high_delivery_zone,
            "fuel_shortage_alert": demand_analysis["fuel_shortage_alert"]
        }
    
    def _calculate_fuel_fairness_score(self, agent_id: int) -> float:
        """Calculate fairness transparency score for fuel agent"""
        metrics = self.db.get_fuel_agent_metrics(agent_id)
        
        if not metrics:
            return 50.0  # Default score
        
        # Fairness based on performance consistency
        completion_score = metrics["completion_rate"]
        on_time_score = metrics["on_time_rate"]
        
        # Calculate fairness score (0-100)
        fairness = (completion_score * 0.6) + (on_time_score * 0.4)
        return round(fairness, 2)
    
    def _identify_high_delivery_zone(self, fuel_demand: List[Dict]) -> str:
        """Identify high delivery zone based on demand"""
        if not fuel_demand:
            return "No active zones"
        
        # Find fuel type with highest demand
        highest_demand = max(fuel_demand, key=lambda x: x['pending_count'])
        
        if highest_demand['fuel_type'] == 'PETROL':
            return "Petrol delivery zone active"
        elif highest_demand['fuel_type'] == 'DIESEL':
            return "Diesel delivery zone active"
        
        return "Mixed fuel demand"
    
    # ==================== FUEL ORDER MANAGEMENT ====================
    
    def get_transparent_fuel_orders(self, agent_id: int) -> Dict:
        """Get transparent fuel orders with full details"""
        pending_orders = self.db.get_pending_fuel_orders()
        agent_status = self.db.get_fuel_agent_status(agent_id)
        
        # Enhance each order with transparency data
        enhanced_orders = []
        for order in pending_orders:
            # Calculate distance (simplified - would use actual location in production)
            distance = self._calculate_distance(
                agent_status.get("last_location_lat", 0),
                agent_status.get("last_location_long", 0),
                order["location_lat"],
                order["location_long"]
            )
            
            # Calculate profitability score
            avg_earning = (order["estimated_earning_min"] + order["estimated_earning_max"]) / 2
            profitability_score = self._calculate_fuel_profitability_score(avg_earning, order["estimated_duration"])
            
            # Risk assessment
            risk_level = self._assess_fuel_order_risk(order)
            
            # Assignment reason
            assignment_reason = self._get_fuel_assignment_reason(order, agent_id)
            
            # Delivery efficiency score
            efficiency_score = self._calculate_delivery_efficiency(order)
            
            enhanced_order = {
                **order,
                "distance_km": round(distance, 2),
                "profitability_score": profitability_score,
                "risk_level": risk_level,
                "assignment_reason": assignment_reason,
                "delivery_efficiency": efficiency_score,
                "fuel_shortage_risk": self._check_fuel_shortage_risk(order)
            }
            
            enhanced_orders.append(enhanced_order)
        
        # Sort by priority (profitability + efficiency + proximity)
        enhanced_orders.sort(key=lambda x: (x["profitability_score"], x["delivery_efficiency"], -x["distance_km"]), reverse=True)
        
        return {
            "success": True,
            "orders": enhanced_orders,
            "total_orders": len(enhanced_orders),
            "agent_status": "ONLINE" if agent_status and agent_status["online_status"] == "ONLINE" else "OFFLINE"
        }
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates (simplified)"""
        return abs(lat1 - lat2) * 111 + abs(lng1 - lng2) * 111
    
    def _calculate_fuel_profitability_score(self, avg_earning: float, duration: int) -> float:
        """Calculate fuel order profitability score"""
        if duration <= 0:
            return 0
        
        earning_per_minute = avg_earning / duration
        return min(100, earning_per_minute * 10)  # Scale to 0-100
    
    def _assess_fuel_order_risk(self, order: Dict) -> str:
        """Assess fuel order risk level"""
        # Risk factors for fuel delivery
        earning_variance = order["estimated_earning_max"] - order["estimated_earning_min"]
        quantity = order["quantity_liters"]
        duration = order["estimated_duration"]
        
        # Risk assessment logic
        if earning_variance > 100 or quantity > 50 or duration > 60:
            return "HIGH"
        elif earning_variance > 50 or quantity > 25 or duration > 30:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_fuel_assignment_reason(self, order: Dict, agent_id: int) -> str:
        """Get transparent assignment reason for fuel order"""
        distance = self._calculate_distance(0, 0, order["location_lat"], order["location_long"])
        
        if distance < 3:
            return "Nearest available fuel agent"
        elif order["estimated_earning_max"] > 300:
            return "High value fuel delivery"
        elif order["fuel_type"] == "PETROL":
            return "Petrol specialist assignment"
        else:
            return "Availability and proximity match"
    
    def _calculate_delivery_efficiency(self, order: Dict) -> float:
        """Calculate delivery efficiency score"""
        quantity = order["quantity_liters"]
        duration = order["estimated_duration"]
        
        if duration <= 0:
            return 0
        
        # Efficiency based on quantity per minute
        efficiency = quantity / duration
        return min(100, efficiency * 5)  # Scale to 0-100
    
    def _check_fuel_shortage_risk(self, order: Dict) -> bool:
        """Check if there's fuel shortage risk for this order"""
        demand_analysis = self.db.get_fuel_demand_analysis()
        
        # Check if this fuel type has high demand
        for fuel_demand in demand_analysis['fuel_demand']:
            if fuel_demand['fuel_type'] == order['fuel_type'] and fuel_demand['pending_count'] > 10:
                return True
        
        return False
    
    def accept_fuel_order_request(self, agent_id: int, order_id: int) -> Dict:
        """Accept fuel order request with full validation"""
        # Check if agent can accept order
        agent_status = self.db.get_fuel_agent_status(agent_id)
        
        if not agent_status:
            return {"success": False, "error": "Fuel agent not found"}
        
        if agent_status["is_busy"]:
            return {"success": False, "error": "Fuel agent is currently busy"}
        
        if agent_status["online_status"] != "ONLINE":
            return {"success": False, "error": "Fuel agent must be online to accept orders"}
        
        # Accept the order
        success = self.db.accept_fuel_order(order_id, agent_id)
        
        if success:
            return {
                "success": True,
                "message": "Fuel order accepted successfully",
                "order_id": order_id,
                "next_status": "ON_THE_WAY",
                "estimated_arrival": self._calculate_fuel_arrival_time(agent_id, order_id),
                "fuel_shortage_alert": self._check_fuel_shortage_risk({"fuel_type": "PETROL"})
            }
        
        return {"success": False, "error": "Failed to accept fuel order"}
    
    def _calculate_fuel_arrival_time(self, agent_id: int, order_id: int) -> str:
        """Calculate estimated arrival time for fuel delivery"""
        # Simplified - would use actual routing in production
        return datetime.now() + timedelta(minutes=25).strftime("%I:%M %p")
    
    # ==================== ACTIVE DELIVERY MANAGEMENT ====================
    
    def get_active_fuel_deliveries(self, agent_id: int) -> Dict:
        """Get fuel agent's active deliveries with full lifecycle"""
        active_deliveries = self.db.get_active_fuel_deliveries(agent_id)
        
        # Enhance with next actions and progress
        enhanced_deliveries = []
        for delivery in active_deliveries:
            enhanced_delivery = {
                **delivery,
                "progress_percentage": self._calculate_fuel_delivery_progress(delivery),
                "next_actions": self._get_fuel_delivery_next_actions(delivery["status"]),
                "time_in_status": self._calculate_fuel_time_in_status(delivery),
                "estimated_completion": self._estimate_fuel_delivery_completion(delivery),
                "route_efficiency": self._calculate_route_efficiency(delivery),
                "delivery_speed_score": self._calculate_delivery_speed_score(delivery),
                "upsell_opportunities": self._get_fuel_upsell_suggestions(delivery)
            }
            enhanced_deliveries.append(enhanced_delivery)
        
        return {
            "success": True,
            "deliveries": enhanced_deliveries,
            "total_active": len(enhanced_deliveries)
        }
    
    def _calculate_fuel_delivery_progress(self, delivery: Dict) -> int:
        """Calculate fuel delivery progress percentage"""
        status_progress = {
            "ACCEPTED": 10,
            "ON_THE_WAY": 30,
            "ARRIVED": 50,
            "DELIVERED": 100
        }
        return status_progress.get(delivery["status"], 0)
    
    def _get_fuel_delivery_next_actions(self, status: str) -> List[str]:
        """Get next available actions for fuel delivery status"""
        actions = {
            "ACCEPTED": ["Start Delivery", "Contact Customer", "Check Fuel Availability"],
            "ON_THE_WAY": ["Update Location", "Notify Arrival", "Check Traffic"],
            "ARRIVED": ["Start Fuel Delivery", "Upload Fuel Meter Photo", "Verify Customer Location"],
            "DELIVERED": ["Upload Delivery Confirmation", "Rate Customer", "Complete Delivery"]
        }
        return actions.get(status, [])
    
    def _calculate_fuel_time_in_status(self, delivery: Dict) -> str:
        """Calculate how long delivery has been in current status"""
        if not delivery.get("created_at"):
            return "Unknown"
        
        created = datetime.strptime(delivery["created_at"], "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        time_diff = now - created
        
        hours = time_diff.total_seconds() / 3600
        if hours < 1:
            return f"{int(time_diff.total_seconds() / 60)} minutes"
        else:
            return f"{int(hours)} hours {int((hours % 1) * 60)} minutes"
    
    def _estimate_fuel_delivery_completion(self, delivery: Dict) -> str:
        """Estimate fuel delivery completion time"""
        duration = delivery.get("estimated_duration", 30)  # Default 30 minutes
        return (datetime.now() + timedelta(minutes=duration)).strftime("%I:%M %p")
    
    def _calculate_route_efficiency(self, delivery: Dict) -> float:
        """Calculate route efficiency score"""
        distance = delivery.get("distance_km", 0)
        quantity = delivery.get("quantity_liters", 0)
        
        if distance <= 0:
            return 0
        
        # Efficiency based on quantity per km
        efficiency = quantity / distance
        return min(100, efficiency * 10)  # Scale to 0-100
    
    def _calculate_delivery_speed_score(self, delivery: Dict) -> float:
        """Calculate delivery speed score"""
        duration = delivery.get("estimated_duration", 30)
        distance = delivery.get("distance_km", 0)
        
        if duration <= 0:
            return 0
        
        # Speed in km per minute
        speed = distance / duration
        return min(100, speed * 20)  # Scale to 0-100
    
    def _get_fuel_upsell_suggestions(self, delivery: Dict) -> List[str]:
        """Get upsell suggestions for fuel delivery"""
        suggestions = []
        fuel_type = delivery.get("fuel_type", "")
        quantity = delivery.get("quantity_liters", 0)
        
        if fuel_type == "PETROL":
            suggestions.append("Offer engine oil check")
            suggestions.append("Suggest fuel additives")
        elif fuel_type == "DIESEL":
            suggestions.append("Offer diesel filter check")
            suggestions.append("Suggest fuel system cleaning")
        
        if quantity > 20:
            suggestions.append("Suggest fuel tank cleaning")
        
        if quantity < 5:
            suggestions.append("Offer fuel subscription plan")
        
        return suggestions
    
    def update_fuel_delivery_status(self, agent_id: int, order_id: int, new_status: str) -> Dict:
        """Update fuel delivery status with validation"""
        valid_transitions = {
            "ACCEPTED": ["ON_THE_WAY"],
            "ON_THE_WAY": ["ARRIVED"],
            "ARRIVED": ["DELIVERED"]
        }
        
        # Get current order
        active_deliveries = self.db.get_active_fuel_deliveries(agent_id)
        current_delivery = next((delivery for delivery in active_deliveries if delivery["id"] == order_id), None)
        
        if not current_delivery:
            return {"success": False, "error": "Delivery not found or not active"}
        
        # Validate transition
        if new_status not in valid_transitions.get(current_delivery["status"], []):
            return {"success": False, "error": f"Invalid status transition from {current_delivery['status']}"}
        
        # Update status
        success = self.db.update_fuel_order_status(order_id, new_status, agent_id)
        
        if success:
            # If delivered, process earnings
            if new_status == "DELIVERED":
                self._process_fuel_delivery_completion(agent_id, order_id)
            
            return {
                "success": True,
                "message": f"Delivery status updated to {new_status}",
                "next_actions": self._get_fuel_delivery_next_actions(new_status)
            }
        
        return {"success": False, "error": "Failed to update delivery status"}
    
    def _process_fuel_delivery_completion(self, agent_id: int, order_id: int) -> None:
        """Process fuel delivery completion and earnings"""
        # Get order details for earning calculation
        active_deliveries = self.db.get_active_fuel_deliveries(agent_id)
        delivery = next((delivery for delivery in active_deliveries if delivery["id"] == order_id), None)
        
        if delivery:
            # Calculate final earning (average of min/max)
            final_earning = (delivery["estimated_earning_min"] + delivery["estimated_earning_max"]) / 2
            self.db.add_fuel_earning(agent_id, order_id, final_earning)
    
    # ==================== EARNINGS & DELIVERY INSIGHTS ====================
    
    def get_fuel_earnings_insights(self, agent_id: int, period: str = 'all') -> Dict:
        """Get comprehensive fuel earnings insights"""
        # Get basic earnings
        earnings = self.db.get_fuel_agent_earnings(agent_id, period)
        
        # Get additional insights
        metrics = self.db.get_fuel_agent_metrics(agent_id)
        
        # Calculate advanced metrics
        insights = {
            **earnings,
            "income_stability_score": self._calculate_fuel_income_stability(agent_id),
            "earnings_trend": self._calculate_fuel_earnings_trend(agent_id),
            "tax_estimation": self._estimate_fuel_tax(earnings.get("net_earnings", 0)),
            "savings_suggestion": self._suggest_fuel_savings(earnings.get("net_earnings", 0)),
            "most_profitable_fuel_type": self._get_most_profitable_fuel_type(agent_id),
            "peak_earning_time": self._get_fuel_peak_earning_time(agent_id),
            "commission_breakdown": {
                "total_commission": earnings.get("total_commission", 0),
                "commission_rate": "20%",
                "net_percentage": "80%"
            },
            "delivery_efficiency_index": self._calculate_delivery_efficiency_index(agent_id)
        }
        
        return {
            "success": True,
            "period": period,
            "insights": insights
        }
    
    def _calculate_fuel_income_stability(self, agent_id: int) -> float:
        """Calculate fuel delivery income stability score (0-100)"""
        # Simplified - would use historical data
        return 80.0  # Default score
    
    def _calculate_fuel_earnings_trend(self, agent_id: int) -> str:
        """Calculate fuel earnings trend"""
        # Simplified - would compare last week vs current week
        return "STABLE"  # Default trend
    
    def _estimate_fuel_tax(self, net_earnings: float) -> Dict:
        """Estimate yearly tax for fuel agent"""
        yearly_earnings = net_earnings * 52  # Weekly to yearly approximation
        tax_rate = 0.15  # 15% tax rate (simplified)
        estimated_tax = yearly_earnings * tax_rate
        
        return {
            "yearly_earnings": yearly_earnings,
            "estimated_tax": estimated_tax,
            "after_tax_income": yearly_earnings - estimated_tax,
            "tax_rate": f"{tax_rate * 100}%"
        }
    
    def _suggest_fuel_savings(self, net_earnings: float) -> Dict:
        """Suggest savings percentage for fuel agent"""
        suggestions = {
            "conservative": {"rate": 10, "amount": net_earnings * 0.10},
            "moderate": {"rate": 20, "amount": net_earnings * 0.20},
            "aggressive": {"rate": 30, "amount": net_earnings * 0.30}
        }
        return suggestions
    
    def _get_most_profitable_fuel_type(self, agent_id: int) -> str:
        """Get most profitable fuel type for agent"""
        # Simplified - would analyze actual order data
        return "Petrol"  # Default
    
    def _get_fuel_peak_earning_time(self, agent_id: int) -> str:
        """Get peak earning time for fuel agent"""
        # Simplified - would analyze historical data
        return "Evening"  # Default
    
    def _calculate_delivery_efficiency_index(self, agent_id: int) -> float:
        """Calculate overall delivery efficiency index"""
        metrics = self.db.get_fuel_agent_metrics(agent_id)
        
        if not metrics:
            return 50.0
        
        # Efficiency based on completion and on-time rates
        efficiency = (metrics.get("completion_rate", 0) + metrics.get("on_time_rate", 0)) / 2
        return round(efficiency, 2)
    
    # ==================== PERFORMANCE & SAFETY ====================
    
    def get_fuel_performance_safety(self, agent_id: int) -> Dict:
        """Get comprehensive fuel performance and safety insights"""
        metrics = self.db.get_fuel_agent_metrics(agent_id)
        emergency_alerts = self.db.get_fuel_emergency_alerts(agent_id)
        
        # Generate tips based on metrics
        tips = self._generate_fuel_performance_tips(metrics)
        
        # Calculate safety score
        safety_score = self._calculate_fuel_safety_score(metrics, emergency_alerts)
        
        return {
            "success": True,
            "metrics": metrics,
            "safety_score": safety_score,
            "emergency_alerts": emergency_alerts,
            "performance_tips": tips,
            "improvement_areas": self._identify_fuel_improvement_areas(metrics),
            "fuel_shortage_alerts": self._get_fuel_shortage_alerts()
        }
    
    def _generate_fuel_performance_tips(self, metrics: Dict) -> List[str]:
        """Generate fuel delivery performance improvement tips"""
        tips = []
        
        if metrics.get("completion_rate", 0) < 90:
            tips.append("Focus on completing all accepted deliveries to improve completion rate")
        
        if metrics.get("on_time_rate", 0) < 85:
            tips.append("Improve route planning to enhance on-time performance")
        
        if metrics.get("acceptance_rate", 0) < 70:
            tips.append("Consider accepting more fuel orders to increase acceptance rate")
        
        # Fuel-specific tips
        demand_analysis = self.db.get_fuel_demand_analysis()
        if demand_analysis.get("fuel_shortage_alert"):
            tips.append("Stay updated on fuel station availability during high demand")
        
        # Peak hour tips
        if demand_analysis.get("peak_hour"):
            tips.append("Peak delivery hours are active - maximize availability")
        
        return tips
    
    def _calculate_fuel_safety_score(self, metrics: Dict, emergency_alerts: List[Dict]) -> float:
        """Calculate safety score for fuel agent"""
        base_score = metrics.get("trust_score", 50)
        
        # Deduct points for emergency alerts
        recent_alerts = len([alert for alert in emergency_alerts 
                           if (datetime.now() - datetime.strptime(alert["alert_time"], "%Y-%m-%d %H:%M:%S")).days <= 30])
        
        safety_score = max(0, base_score - (recent_alerts * 5))
        return round(safety_score, 2)
    
    def _identify_fuel_improvement_areas(self, metrics: Dict) -> List[str]:
        """Identify areas needing improvement for fuel agent"""
        areas = []
        
        if metrics.get("completion_rate", 0) < 85:
            areas.append("Delivery Completion")
        
        if metrics.get("on_time_rate", 0) < 80:
            areas.append("Time Management")
        
        if metrics.get("acceptance_rate", 0) < 60:
            areas.append("Order Acceptance")
        
        if metrics.get("cancellation_rate", 0) > 10:
            areas.append("Order Cancellation")
        
        return areas
    
    def _get_fuel_shortage_alerts(self) -> List[Dict]:
        """Get fuel shortage alerts"""
        demand_analysis = self.db.get_fuel_demand_analysis()
        alerts = []
        
        if demand_analysis.get("fuel_shortage_alert"):
            alerts.append({
                "type": "FUEL_SHORTAGE",
                "message": "High petrol demand detected - check fuel station availability",
                "severity": "HIGH",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    # ==================== EMERGENCY SOS ====================
    
    def trigger_fuel_emergency_sos(self, agent_id: int, latitude: float, longitude: float) -> Dict:
        """Trigger emergency SOS alert for fuel agent"""
        success = self.db.create_fuel_emergency_alert(agent_id, latitude, longitude)
        
        if success:
            return {
                "success": True,
                "message": "Emergency alert triggered successfully",
                "alert_id": self._get_latest_fuel_alert_id(agent_id),
                "location": {"lat": latitude, "lng": longitude},
                "timestamp": datetime.now().isoformat(),
                "admin_notified": True
            }
        
        return {"success": False, "error": "Failed to trigger emergency alert"}
    
    def _get_latest_fuel_alert_id(self, agent_id: int) -> int:
        """Get latest emergency alert ID for fuel agent"""
        alerts = self.db.get_fuel_emergency_alerts(agent_id)
        return alerts[0]["id"] if alerts else 0
    
    # ==================== DELIVERY PROOF SYSTEM ====================
    
    def upload_fuel_delivery_proof(self, agent_id: int, order_id: int, 
                                fuel_meter_file=None, delivery_photo_file=None, notes: str = "") -> Dict:
        """Upload fuel delivery completion proof with file handling"""
        try:
            # Handle file uploads
            fuel_meter_path = None
            delivery_photo_path = None
            
            if fuel_meter_file:
                filename = secure_filename(fuel_meter_file.filename)
                fuel_meter_path = os.path.join(self.upload_folder, f"fuel_meter_{order_id}_{filename}")
                fuel_meter_file.save(fuel_meter_path)
            
            if delivery_photo_file:
                filename = secure_filename(delivery_photo_file.filename)
                delivery_photo_path = os.path.join(self.upload_folder, f"delivery_{order_id}_{filename}")
                delivery_photo_file.save(delivery_photo_path)
            
            # Save to database
            success = self.db.upload_delivery_proof(order_id, fuel_meter_path, delivery_photo_path, notes)
            
            if success:
                return {
                    "success": True,
                    "message": "Fuel delivery proof uploaded successfully",
                    "proof_id": self._get_latest_fuel_proof_id(order_id),
                    "files": {
                        "fuel_meter_photo": fuel_meter_path,
                        "delivery_confirmation_photo": delivery_photo_path
                    }
                }
            
            return {"success": False, "error": "Failed to upload proof"}
            
        except Exception as e:
            return {"success": False, "error": f"Upload error: {str(e)}"}
    
    def _get_latest_fuel_proof_id(self, order_id: int) -> int:
        """Get latest proof ID for fuel order"""
        proofs = self.db.get_delivery_proofs(order_id)
        return proofs[0]["id"] if proofs else 0

# Initialize service instance
fuel_agent_service = FuelAgentService()
