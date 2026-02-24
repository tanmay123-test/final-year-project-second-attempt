"""
AI Mechanic Agent - LLM Brain for Trip Planning
Integrates calculation tools with AI reasoning for intelligent trip planning
"""

import json
from .trip_tools import *
from .knowledge_base import *

class AIMechanicAgent:
    def __init__(self):
        self.car_profile_db = None  # Will be injected from main module
        
    def set_car_db(self, car_profile_db):
        """Inject car profile database dependency"""
        self.car_profile_db = car_profile_db
    
    def generate_trip_plan(self, user_id, from_city, to_city):
        """
        Generate complete AI trip plan using tools + LLM reasoning
        Returns: Complete trip plan with calculations and AI advice
        """
        try:
            # Step 1: Get user car data
            car_data = get_user_car(user_id, self.car_profile_db)
            if not car_data:
                return {
                    "error": "No car found. Please add a car to your profile first.",
                    "status": "error"
                }
            
            brand, model, fuel_type, year = car_data
            car_age = 2025 - year
            
            # Step 2: Calculate all metrics
            distance_result = calculate_distance(from_city, to_city)
            if isinstance(distance_result, str):
                return {
                    "error": distance_result,
                    "status": "error"
                }
            
            fuel_needed, fuel_cost, fuel_error = calculate_fuel_cost(distance_result, fuel_type)
            if fuel_error:
                return {
                    "error": fuel_error,
                    "status": "error"
                }
            fuel_unit = get_fuel_unit(fuel_type)
            
            toll_cost = calculate_toll_cost(distance_result)
            food_budget = calculate_food_budget(distance_result)
            total_cost = calculate_total_trip_cost(fuel_cost, toll_cost, food_budget)
            checklist = generate_trip_checklist(distance_result, car_age)
            driving_tips = get_driving_tips(distance_result, fuel_type, car_age)
            
            # Step 3: Generate AI reasoning
            ai_analysis = self._generate_ai_analysis(
                from_city, to_city, distance_result, brand, model, 
                fuel_type, year, car_age, fuel_needed, fuel_cost,
                toll_cost, food_budget, total_cost, checklist, driving_tips
            )
            
            # Step 4: Compile complete response
            return {
                "status": "success",
                "trip_details": {
                    "from_city": from_city.title(),
                    "to_city": to_city.title(),
                    "distance_km": distance_result,
                    "vehicle": {
                        "brand": brand,
                        "model": model,
                        "fuel_type": fuel_type,
                        "year": year,
                        "age": f"{car_age} years"
                    }
                },
                "cost_breakdown": {
                    "fuel_needed": f"{fuel_needed} {fuel_unit}",
                    "fuel_cost": fuel_cost,
                    "toll_cost": toll_cost,
                    "food_budget": food_budget,
                    "total_cost": total_cost
                },
                "checklist": checklist,
                "driving_tips": driving_tips,
                "ai_analysis": ai_analysis
            }
            
        except Exception as e:
            return {
                "error": f"Trip planning failed: {str(e)}",
                "status": "error"
            }
    
    def _generate_ai_analysis(self, from_city, to_city, distance, brand, model, 
                          fuel_type, year, car_age, fuel_needed, fuel_cost,
                          toll_cost, food_budget, total_cost, checklist, tips):
        """
        Generate AI analysis and reasoning for the trip
        This simulates LLM reasoning without external API calls
        """
        
        # Route analysis
        if distance < 100:
            route_type = "short distance city drive"
            difficulty = "easy"
        elif distance < 300:
            route_type = "medium distance intercity travel"
            difficulty = "moderate"
        else:
            route_type = "long distance highway journey"
            difficulty = "challenging"
        
        # Vehicle suitability analysis
        if car_age < 3:
            vehicle_condition = "excellent for long journeys"
            reliability = "highly reliable"
        elif car_age < 7:
            vehicle_condition = "suitable for the planned distance"
            reliability = "reliable with proper maintenance"
        else:
            vehicle_condition = "requires pre-trip inspection"
            reliability = "use with caution"
        
        # Cost efficiency analysis
        cost_per_km = total_cost / distance
        if cost_per_km < 10:
            efficiency_rating = "very economical"
        elif cost_per_km < 15:
            efficiency_rating = "economical"
        else:
            efficiency_rating = "moderate cost"
        
        # Fuel-specific observations
        fuel_insights = self._get_fuel_insights(fuel_type, distance, fuel_needed)
        
        # Generate comprehensive analysis
        analysis = f"""
🧠 AI TRIP ANALYSIS

📍 Route Assessment:
Your journey from {from_city.title()} to {to_city.title()} covers {distance} km, 
classified as a {route_type} with {difficulty} complexity.

🚗 Vehicle Analysis:
Your {brand} {model} ({year}) is {vehicle_condition}. 
Reliability rating: {reliability}. Age: {car_age} years.

💰 Cost Efficiency:
Total trip cost of ₹{total_cost} breaks down to ₹{cost_per_km:.2f} per km, 
which is {efficiency_rating} for this distance.

{fuel_insights}

🎯 AI Recommendations:
• Start journey early morning to avoid traffic
• Maintain steady speed for optimal fuel efficiency  
• Plan rest stops every 2 hours for safety
• Keep emergency contacts readily accessible
• Monitor fuel levels, especially for routes with limited stations

⚠️ Risk Assessment:
{self._assess_trip_risks(distance, car_age, fuel_type)}
        """
        
        return analysis.strip()
    
    def _get_fuel_insights(self, fuel_type, distance, fuel_needed):
        """Generate fuel-specific insights"""
        if fuel_type.lower() == 'petrol':
            return f"""
⛽ Fuel Analysis:
Petrol consumption of {fuel_needed:.2f} liters is normal for {distance} km.
Consider using premium fuel for better engine performance and mileage.
        """
        elif fuel_type.lower() == 'diesel':
            return f"""
🛢️ Fuel Analysis:
Diesel consumption of {fuel_needed:.2f} liters shows good efficiency.
Avoid frequent short trips to maintain DPF system health.
        """
        elif fuel_type.lower() == 'cng':
            return f"""
⛽ Fuel Analysis:
CNG requirement of {fuel_needed:.2f} kg is economical.
Plan refueling stops as CNG stations may be limited on some routes.
        """
        elif fuel_type.lower() == 'electric':
            return f"""
🔋 Fuel Analysis:
Energy consumption of {fuel_needed:.2f} kWh for {distance} km.
Identify charging stations along the route and plan charging stops.
        """
        else:
            return f"Fuel analysis available for standard fuel types."
    
    def _assess_trip_risks(self, distance, car_age, fuel_type):
        """Assess potential risks for the trip"""
        risks = []
        
        if distance > 400:
            risks.append("Long distance fatigue - plan overnight rest if needed")
        
        if car_age > 8:
            risks.append("Vehicle age - carry emergency toolkit and contacts")
        
        if fuel_type.lower() == 'electric':
            risks.append("Charging infrastructure - verify station availability")
        
        if distance > 200 and fuel_type.lower() == 'cng':
            risks.append("Limited CNG stations on some routes")
        
        if not risks:
            return "Low risk journey with proper planning."
        
        return " | ".join([f"• {risk}" for risk in risks])

# Initialize global agent instance
ai_agent = AIMechanicAgent()
