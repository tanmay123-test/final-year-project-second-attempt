"""
AI Mechanic Knowledge Base - Dynamic Constants for Trip Planning
Contains fuel prices, mileage data, and calculation rules for India
"""

# Fuel Prices (India average - can be updated dynamically)
PETROL_PRICE = 105  # ₹ per liter
DIESEL_PRICE = 95   # ₹ per liter  
CNG_PRICE = 75      # ₹ per kg
ELECTRIC_PRICE = 8   # ₹ per kWh

# Average Highway Mileage (km per unit)
PETROL_MILEAGE = 15  # km per liter
DIESEL_MILEAGE = 18  # km per liter
CNG_MILEAGE = 22     # km per kg
ELECTRIC_MILEAGE = 6  # km per kWh

# Toll and Food Budget Rules
TOLL_PER_KM = 1.5    # ₹ per km highway average
FOOD_BUDGET_PER_300KM = 300  # ₹ per person per 300 km

# City Coordinates for Distance Calculation (major Indian cities)
CITY_COORDINATES = {
    "mumbai": (19.0760, 72.8777),
    "pune": (18.5204, 73.8567),
    "delhi": (28.7041, 77.1025),
    "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "ahmedabad": (23.0225, 72.5714),
    "jaipur": (26.9124, 75.7873),
    "lucknow": (26.8467, 80.9462),
    "kanpur": (26.4499, 80.3319),
    "nagpur": (21.1458, 79.0882),
    "indore": (22.7196, 75.8577),
    "thane": (19.2183, 72.9781),
    "bhiwandi": (19.2948, 73.0632),
    "kolhapur": (16.7050, 74.2433),
    "nashik": (19.9975, 73.7898),
    "aurangabad": (19.8762, 75.3433),
    "solapur": (17.6599, 75.9064),
    "sangli": (16.8524, 74.5830),
    "satara": (17.6827, 74.0184),
    "ratnagiri": (16.9902, 73.3120)
}

# Known road distance overrides (km) for accuracy beyond haversine approximation
ROUTE_DISTANCE_OVERRIDES = {
    ("mumbai", "pune"): 155.0,
    ("pune", "mumbai"): 155.0,
}

# Trip Checklist Rules
LONG_DISTANCE_THRESHOLD = 300  # km - above this requires detailed checklist

# Vehicle Age Categories for Maintenance Tips
NEW_CAR_THRESHOLD = 2      # years
MID_CAR_THRESHOLD = 5       # years
OLD_CAR_THRESHOLD = 10       # years
