"""
AI Mechanic Trip Tools - Core Calculation Functions
Handles distance, fuel cost, toll, food budget, and trip calculations
"""

import math
from .knowledge_base import *

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r

def get_user_car(user_id, car_profile_db):
    """
    Fetch user's default car from database
    Returns: (brand, model, fuel_type, year)
    """
    try:
        cars = car_profile_db.get_user_cars(user_id)
        if cars:
            # Find default car or first car
            default_car = next((car for car in cars if car[6]), cars[0])
            return (
                default_car[2],  # brand
                default_car[3],  # model  
                default_car[5],  # fuel_type
                default_car[4]   # year
            )
        return None
    except Exception as e:
        print(f"Error fetching user car: {e}")
        return None

def calculate_distance(from_city, to_city):
    """
    Calculate distance between two Indian cities
    Works for any cities in CITY_COORDINATES
    Returns: distance in km
    """
    try:
        from_city = from_city.lower().strip()
        to_city = to_city.lower().strip()
        
        # Use route overrides if available
        override = ROUTE_DISTANCE_OVERRIDES.get((from_city, to_city))
        if override:
            return round(override, 2)
        
        if from_city not in CITY_COORDINATES:
            return f"City '{from_city}' not found in database"
        if to_city not in CITY_COORDINATES:
            return f"City '{to_city}' not found in database"
            
        lat1, lon1 = CITY_COORDINATES[from_city]
        lat2, lon2 = CITY_COORDINATES[to_city]
        
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        
        # Add 30% for real road conditions (approximate route factor)
        actual_distance = distance * 1.30
        
        return round(actual_distance, 2)
        
    except Exception as e:
        return f"Error calculating distance: {e}"

def calculate_fuel_cost(distance, fuel_type):
    """
    Calculate fuel cost based on distance and fuel type
    Returns: (fuel_needed, fuel_cost)
    """
    try:
        fuel_type = fuel_type.lower().strip()
        
        # Get mileage and price based on fuel type
        if fuel_type == 'petrol':
            mileage = PETROL_MILEAGE
            price = PETROL_PRICE
        elif fuel_type == 'diesel':
            mileage = DIESEL_MILEAGE
            price = DIESEL_PRICE
        elif fuel_type == 'cng':
            mileage = CNG_MILEAGE
            price = CNG_PRICE
        elif fuel_type == 'electric':
            mileage = ELECTRIC_MILEAGE
            price = ELECTRIC_PRICE
        else:
            return (0, 0, f"Unsupported fuel type: {fuel_type}")
        
        # Calculate fuel needed and cost
        fuel_needed = distance / mileage
        fuel_cost = fuel_needed * price
        
        return (round(fuel_needed, 2), round(fuel_cost, 2), None)
        
    except Exception as e:
        return (0, 0, f"Error calculating fuel cost: {e}")

def get_fuel_unit(fuel_type):
    """Return proper unit for fuel type"""
    fuel_type = fuel_type.lower().strip()
    if fuel_type == 'petrol' or fuel_type == 'diesel':
        return 'liters'
    if fuel_type == 'cng':
        return 'kg'
    if fuel_type == 'electric':
        return 'kWh'
    return 'units'

def calculate_toll_cost(distance):
    """
    Calculate toll cost based on distance
    Returns: toll_cost in ₹
    """
    try:
        toll_cost = distance * TOLL_PER_KM
        return round(toll_cost, 2)
    except Exception as e:
        return f"Error calculating toll cost: {e}"

def calculate_food_budget(distance):
    """
    Calculate food budget based on distance
    Returns: food_budget in ₹
    """
    try:
        stops = distance / FOOD_BUDGET_PER_300KM
        food_budget = stops * FOOD_BUDGET_PER_300KM
        return round(food_budget, 2)
    except Exception as e:
        return f"Error calculating food budget: {e}"

def calculate_total_trip_cost(fuel_cost, toll_cost, food_budget):
    """
    Calculate total trip expense
    Returns: total_cost in ₹
    """
    try:
        total_cost = fuel_cost + toll_cost + food_budget
        return round(total_cost, 2)
    except Exception as e:
        return f"Error calculating total cost: {e}"

def generate_trip_checklist(distance, car_age):
    """
    Generate trip checklist based on distance and car age
    Returns: list of checklist items
    """
    try:
        checklist = []
        
        # Basic checklist for all trips
        checklist.extend([
            "Check tyre pressure",
            "Verify fuel level", 
            "Carry vehicle documents",
            "Check brake fluid",
            "Test headlights and indicators"
        ])
        
        # Long distance additions
        if distance > LONG_DISTANCE_THRESHOLD:
            checklist.extend([
                "Carry spare tyre",
                "Check coolant level",
                "Inspect engine oil",
                "Pack emergency toolkit",
                "Check battery terminals",
                "Plan rest stops every 2 hours"
            ])
        
        # Age-specific additions
        if car_age > OLD_CAR_THRESHOLD:
            checklist.extend([
                "Extra coolant and oil",
                "Check timing belt condition",
                "Inspect suspension components"
            ])
        elif car_age > MID_CAR_THRESHOLD:
            checklist.extend([
                "Check brake pad wear",
                "Inspect tyre tread depth"
            ])
        
        return checklist
        
    except Exception as e:
        return [f"Error generating checklist: {e}"]

def get_driving_tips(distance, fuel_type, car_age):
    """
    Generate driving tips based on trip and vehicle
    Returns: list of driving tips
    """
    try:
        tips = []
        
        # Distance-based tips
        if distance > 200:
            tips.append("Plan rest stops every 2 hours for safety")
            tips.append("Start early to avoid traffic congestion")
        
        if distance > 500:
            tips.append("Consider overnight rest for very long trips")
            tips.append("Check weather forecast for the route")
        
        # Fuel-type specific tips
        fuel_type = fuel_type.lower()
        if fuel_type == 'petrol':
            tips.append("Use high-octane fuel for better performance")
        elif fuel_type == 'diesel':
            tips.append("Avoid frequent short trips to maintain DPF health")
        elif fuel_type == 'cng':
            tips.append("Plan CNG refilling stops in advance")
        elif fuel_type == 'electric':
            tips.append("Identify charging stations along the route")
        
        # Age-based tips
        if car_age > 5:
            tips.append("Monitor engine temperature closely")
            tips.append("Keep emergency contact numbers handy")
        
        # General tips
        tips.extend([
            "Maintain steady speed for better fuel efficiency",
            "Avoid sudden acceleration and braking",
            "Keep safe following distance"
        ])
        
        return tips[:6]  # Return top 6 tips
        
    except Exception as e:
        return [f"Error generating tips: {e}"]
