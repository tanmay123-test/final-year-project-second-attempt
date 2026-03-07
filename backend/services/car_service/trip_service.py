"""
AI Trip Planner Service
Service layer for trip planning functionality
"""

from typing import Dict, Optional
from services.car_service.trip_planner import trip_planner

class TripService:
    def __init__(self):
        self.planner = trip_planner
    
    def validate_trip_request(self, start: str, destination: str, mileage: float, fuel_price: float) -> Dict:
        """
        Validate trip planning request parameters
        
        Args:
            start: Starting location
            destination: Destination location
            mileage: Car mileage in km per liter
            fuel_price: Fuel price per liter
            
        Returns:
            Dictionary with validation result and errors if any
        """
        errors = []
        
        if not start or not start.strip():
            errors.append("Starting location is required")
        
        if not destination or not destination.strip():
            errors.append("Destination location is required")
        
        if start.strip().lower() == destination.strip().lower():
            errors.append("Starting and destination locations cannot be the same")
        
        if mileage <= 0:
            errors.append("Mileage must be greater than 0")
        
        if fuel_price <= 0:
            errors.append("Fuel price must be greater than 0")
        
        if mileage > 100:  # Reasonable upper limit
            errors.append("Mileage seems too high (maximum 100 km/liter)")
        
        if fuel_price > 500:  # Reasonable upper limit for India
            errors.append("Fuel price seems too high (maximum ₹500/liter)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def plan_trip(self, start: str, destination: str, mileage: float, fuel_price: float) -> Optional[Dict]:
        """
        Plan a trip with validation and error handling
        
        Args:
            start: Starting location name
            destination: Destination location name
            mileage: Car mileage in km per liter
            fuel_price: Fuel price per liter
            
        Returns:
            Complete trip plan dictionary or None if failed
        """
        # Validate input
        validation = self.validate_trip_request(start, destination, mileage, fuel_price)
        if not validation["valid"]:
            print("❌ Validation errors:")
            for error in validation["errors"]:
                print(f"   • {error}")
            return None
        
        # Plan the trip
        try:
            trip_plan = self.planner.plan_trip(start, destination, mileage, fuel_price)
            return trip_plan
        except Exception as e:
            print(f"❌ Error planning trip: {e}")
            return None
    
    def format_trip_plan_for_display(self, trip_plan: Dict) -> str:
        """
        Format trip plan for CLI display
        
        Args:
            trip_plan: Trip plan dictionary
            
        Returns:
            Formatted string for display
        """
        if not trip_plan:
            return "❌ No trip plan available"
        
        formatted = []
        formatted.append("\n" + "="*60)
        formatted.append("🚗 AI TRIP PLANNER - YOUR JOURNEY PLAN")
        formatted.append("="*60)
        formatted.append(f"📍 From: {trip_plan['start']}")
        formatted.append(f"🎯 To: {trip_plan['destination']}")
        formatted.append("")
        formatted.append("📊 JOURNEY DETAILS:")
        formatted.append(f"   🛣️  Distance: {trip_plan['distance_km']} km")
        formatted.append(f"   ⏱️  ETA: {trip_plan['duration_hours']} hours")
        formatted.append("")
        formatted.append("💰 COST BREAKDOWN:")
        formatted.append(f"   ⛽ Fuel needed: {trip_plan['fuel_needed']} liters")
        formatted.append(f"   💸 Fuel cost: ₹{trip_plan['fuel_cost']}")
        formatted.append(f"   🛣️  Estimated toll: ₹{trip_plan['toll_cost']}")
        formatted.append(f"   💳 Total cost: ₹{trip_plan['total_cost']}")
        formatted.append("")
        formatted.append("📋 TRIP CHECKLIST:")
        for i, item in enumerate(trip_plan['checklist'], 1):
            formatted.append(f"   {i}. {item}")
        formatted.append("")
        formatted.append("🚗 VEHICLE INFO:")
        formatted.append(f"   ⛽ Mileage: {trip_plan['mileage']} km/liter")
        formatted.append(f"   💵 Fuel price: ₹{trip_plan['fuel_price']}/liter")
        formatted.append("")
        formatted.append("🌟 Have a safe and pleasant journey!")
        formatted.append("="*60)
        
        return "\n".join(formatted)
    
    def get_trip_summary(self, trip_plan: Dict) -> Dict:
        """
        Get a summary of the trip plan
        
        Args:
            trip_plan: Trip plan dictionary
            
        Returns:
            Summary dictionary
        """
        if not trip_plan:
            return {}
        
        return {
            "route": f"{trip_plan['start']} → {trip_plan['destination']}",
            "distance": f"{trip_plan['distance_km']} km",
            "duration": f"{trip_plan['duration_hours']} hours",
            "total_cost": f"₹{trip_plan['total_cost']}",
            "fuel_needed": f"{trip_plan['fuel_needed']} liters"
        }


# Global service instance
trip_service = TripService()
