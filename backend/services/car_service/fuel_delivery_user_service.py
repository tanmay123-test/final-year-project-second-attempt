"""
Uber-style Fuel Delivery User Service
"""

import requests
import time
import math

API = "http://127.0.0.1:5000"

class FuelDeliveryUserService:
    def __init__(self):
        self.user_info = None
    
    def geocode_location(self, location_name):
        """Convert location name to coordinates (simplified geocoding)"""
        # In production, use Google Geocoding API
        # For now, using simplified Mumbai coordinates
        location_coords = {
            'asalpha': (19.0954, 72.8783),
            'bandra': (19.0596, 72.8295),
            'andheri': (19.1196, 72.8465),
            'worli': (19.0170, 72.8300),
            'dadar': (19.0190, 72.8420),
            'kurla': (19.0726, 72.8761),
            'goregaon': (19.1661, 72.8576),
            'bkc': (19.0681, 72.8407)
        }
        
        location_lower = location_name.lower()
        if location_lower in location_coords:
            return location_coords[location_lower]
        else:
            # Default to Asalpha if not found
            return location_coords.get('asalpha', (19.0954, 72.8783))
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def find_nearby_agents(self, user_lat, user_lon, fuel_quantity):
        """Find nearby fuel delivery agents with service area and capacity validation"""
        try:
            # Get all available agents
            response = requests.get(f"{API}/api/fuel-delivery/agents/available")
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    agents = result['agents']
                    nearby_agents = []
                    
                    for agent in agents:
                        agent_lat = agent.get('latitude', 0)
                        agent_lon = agent.get('longitude', 0)
                        service_area_km = agent.get('service_area_km', 15)
                        
                        # Calculate distance
                        distance = self.calculate_distance(user_lat, user_lon, agent_lat, agent_lon)
                        
                        # Service area validation
                        if distance <= service_area_km:
                            # Capacity validation
                            vehicle_type = agent.get('vehicle_type', 'Bike')
                            max_capacity = self.get_max_capacity(vehicle_type)
                            
                            if fuel_quantity <= max_capacity:
                                # Calculate ETA (3 minutes per km)
                                eta_minutes = int(distance * 3)
                                
                                nearby_agents.append({
                                    'agent_id': agent.get('id'),
                                    'name': agent.get('name', 'N/A'),
                                    'vehicle_type': vehicle_type,
                                    'distance_km': round(distance, 2),
                                    'eta_minutes': eta_minutes,
                                    'rating': agent.get('rating', 0),
                                    'completion_rate': agent.get('completion_rate', 0),
                                    'service_area_km': service_area_km
                                })
                    
                    # Sort by distance, then rating
                    nearby_agents.sort(key=lambda x: (x['distance_km'], -x['rating']))
                    
                    return nearby_agents[:5]  # Return top 5
            
            return []
            
        except Exception as e:
            print(f"❌ Error finding nearby agents: {e}")
            return []
    
    def get_max_capacity(self, vehicle_type):
        """Get maximum fuel capacity for vehicle type"""
        capacities = {
            'Bike': 10,
            'Van': 50,
            'Truck': 1000
        }
        return capacities.get(vehicle_type, 10)
    
    def create_fuel_request(self, user_id, fuel_type, fuel_quantity, latitude, longitude, agent_id=None):
        """Create fuel delivery request"""
        try:
            request_data = {
                'user_id': user_id,
                'fuel_type': fuel_type,
                'fuel_quantity': fuel_quantity,
                'latitude': latitude,
                'longitude': longitude,
                'agent_id': agent_id
            }
            
            response = requests.post(f"{API}/api/fuel-delivery/requests/create", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                return {'success': False, 'error': 'Failed to create request'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def auto_dispatch_request(self, user_id, fuel_type, fuel_quantity, latitude, longitude):
        """Auto-dispatch to best agent using fair scoring"""
        try:
            nearby_agents = self.find_nearby_agents(latitude, longitude, fuel_quantity)
            
            if not nearby_agents:
                return {'success': False, 'error': 'No nearby agents available'}
            
            # Calculate dispatch scores
            best_agent = None
            best_score = -1
            
            for agent in nearby_agents:
                # Calculate scores
                eta_score = max(0, 1 - (agent['eta_minutes'] / 30))  # Lower ETA = higher score
                rating_score = agent['rating'] / 5.0  # Normalize to 0-1
                fairness_score = 0.5  # Placeholder for fairness algorithm
                completion_score = agent['completion_rate'] / 100.0  # Normalize to 0-1
                
                # Calculate total score
                total_score = (
                    0.35 * eta_score +
                    0.30 * rating_score +
                    0.20 * fairness_score +
                    0.15 * completion_score
                )
                
                if total_score > best_score:
                    best_score = total_score
                    best_agent = agent
            
            if best_agent:
                # Create request with best agent
                return self.create_fuel_request(
                    user_id, fuel_type, fuel_quantity, 
                    latitude, longitude, best_agent['agent_id']
                )
            else:
                return {'success': False, 'error': 'No suitable agent found'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Create service instance
fuel_delivery_user_service = FuelDeliveryUserService()
