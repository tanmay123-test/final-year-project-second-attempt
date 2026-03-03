"""
AI Trip Planner - Geocoding and Route Calculation
Uses OpenStreetMap Nominatim API for geocoding and OSRM API for routing
"""

import requests
import time
from typing import Tuple, Dict, Optional

class TripPlanner:
    def __init__(self):
        self.nominatim_base_url = "https://nominatim.openstreetmap.org/search"
        self.osrm_base_url = "http://router.project-osrm.org/route/v1/driving"
        self.toll_rate_per_km = 0.75  # Configurable toll rate
        
    def get_coordinates(self, place_name: str) -> Optional[Tuple[float, float]]:
        """
        Convert place name to latitude and longitude using OpenStreetMap Nominatim API
        
        Args:
            place_name: Name of the place (e.g., "Mumbai", "Pune Station")
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            params = {
                'q': place_name,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'in'  # Focus on India for better results
            }
            
            headers = {
                'User-Agent': 'ExpertEase-TripPlanner/1.0'
            }
            
            response = requests.get(self.nominatim_base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                print(f"📍 Found coordinates for '{place_name}': {lat}, {lon}")
                return (lat, lon)
            else:
                print(f"❌ Location not found: '{place_name}'")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error while getting coordinates for '{place_name}': {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"❌ Error parsing coordinates for '{place_name}': {e}")
            return None
    
    def get_route_distance_duration(self, start_coords: Tuple[float, float], 
                                  end_coords: Tuple[float, float]) -> Optional[Dict]:
        """
        Get route distance and duration using OSRM API
        
        Args:
            start_coords: (latitude, longitude) of starting point
            end_coords: (latitude, longitude) of destination
            
        Returns:
            Dictionary with distance_km and duration_hours or None if failed
        """
        try:
            # OSRM expects coordinates in longitude,latitude order
            start_lon, start_lat = start_coords[1], start_coords[0]
            end_lon, end_lat = end_coords[1], end_coords[0]
            
            url = f"{self.osrm_base_url}/{start_lon},{start_lat};{end_lon},{end_lat}"
            params = {
                'overview': 'false',
                'alternatives': 'false'
            }
            
            headers = {
                'User-Agent': 'ExpertEase-TripPlanner/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            # Debug: Print the actual response
            print(f"🔍 OSRM API Status: {response.status_code}")
            print(f"🔍 OSRM Response: {response.text[:200]}...")
            
            response.raise_for_status()
            
            # Check if response is valid JSON
            try:
                data = response.json()
            except ValueError as e:
                print(f"❌ Invalid JSON response from OSRM: {e}")
                print(f"🔍 Raw response: {response.text}")
                return None
            
            if data.get('routes') and len(data['routes']) > 0:
                route = data['routes'][0]
                distance_meters = route['distance']
                duration_seconds = route['duration']
                
                distance_km = distance_meters / 1000  # Convert to km
                duration_hours = duration_seconds / 3600  # Convert to hours
                
                print(f"🛣️ Route found: {distance_km:.2f} km, {duration_hours:.2f} hours")
                
                return {
                    'distance_km': distance_km,
                    'duration_hours': duration_hours
                }
            else:
                print("❌ No route found between the specified points")
                print("🔄 Using fallback distance estimation...")
                return self._fallback_distance_calculation(start_coords, end_coords)
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error while getting route: {e}")
            print("🔄 Using fallback distance estimation...")
            
            # Fallback: Use haversine formula for straight-line distance
            # and apply a 1.3 factor for road distance
            return self._fallback_distance_calculation(start_coords, end_coords)
        except (ValueError, KeyError) as e:
            print(f"❌ Error parsing route data: {e}")
            print("🔄 Using fallback distance estimation...")
            return self._fallback_distance_calculation(start_coords, end_coords)
    
    def _fallback_distance_calculation(self, start_coords: Tuple[float, float], 
                                    end_coords: Tuple[float, float]) -> Dict:
        """
        Fallback distance calculation using haversine formula
        
        Args:
            start_coords: (latitude, longitude) of starting point
            end_coords: (latitude, longitude) of destination
            
        Returns:
            Dictionary with estimated distance_km and duration_hours
        """
        import math
        
        lat1, lon1 = start_coords
        lat2, lon2 = end_coords
        
        # Haversine formula
        R = 6371  # Earth's radius in kilometers
        
        lat_diff = math.radians(lat2 - lat1)
        lon_diff = math.radians(lon2 - lon1)
        
        a = (math.sin(lat_diff/2)**2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(lon_diff/2)**2)
        
        c = 2 * math.asin(math.sqrt(a))
        straight_distance = R * c
        
        # Apply road factor (typically 1.3-1.5 for road networks)
        road_distance = straight_distance * 1.4
        
        # Estimate duration (assuming average speed of 60 km/h)
        duration_hours = road_distance / 60
        
        print(f"🔄 Fallback: Estimated {road_distance:.2f} km, {duration_hours:.2f} hours")
        
        return {
            'distance_km': road_distance,
            'duration_hours': duration_hours
        }
    
    def calculate_fuel_cost(self, distance_km: float, mileage: float, fuel_price: float) -> Dict:
        """
        Calculate fuel needed and fuel cost
        
        Args:
            distance_km: Distance in kilometers
            mileage: Car mileage in km per liter
            fuel_price: Fuel price per liter
            
        Returns:
            Dictionary with fuel_needed and fuel_cost
        """
        if mileage <= 0:
            raise ValueError("Mileage must be greater than 0")
        
        fuel_needed = distance_km / mileage
        fuel_cost = fuel_needed * fuel_price
        
        return {
            'fuel_needed': fuel_needed,
            'fuel_cost': fuel_cost
        }
    
    def calculate_toll_cost(self, distance_km: float) -> float:
        """
        Calculate estimated toll cost based on distance
        
        Args:
            distance_km: Distance in kilometers
            
        Returns:
            Estimated toll cost
        """
        toll_cost = distance_km * self.toll_rate_per_km
        return toll_cost
    
    def generate_trip_checklist(self) -> list:
        """
        Generate a standard trip checklist
        
        Returns:
            List of checklist items
        """
        return [
            "Check tyre pressure",
            "Check engine oil level",
            "Carry all necessary documents (RC, Insurance, PUC)",
            "Carry spare tyre",
            "Check coolant level",
            "Check brake fluid",
            "Carry first aid kit",
            "Check fuel level",
            "Carry water and snacks",
            "Check battery condition"
        ]
    
    def plan_trip(self, start: str, destination: str, mileage: float, fuel_price: float) -> Optional[Dict]:
        """
        Complete trip planning function
        
        Args:
            start: Starting location name
            destination: Destination location name
            mileage: Car mileage in km per liter
            fuel_price: Fuel price per liter
            
        Returns:
            Complete trip plan dictionary or None if failed
        """
        print(f"\n🚗 Planning trip from '{start}' to '{destination}'")
        print("="*50)
        
        # Get coordinates
        start_coords = self.get_coordinates(start)
        if not start_coords:
            return None
        
        end_coords = self.get_coordinates(destination)
        if not end_coords:
            return None
        
        # Get route information
        route_info = self.get_route_distance_duration(start_coords, end_coords)
        if not route_info:
            return None
        
        distance_km = route_info['distance_km']
        duration_hours = route_info['duration_hours']
        
        # Calculate costs
        fuel_info = self.calculate_fuel_cost(distance_km, mileage, fuel_price)
        toll_cost = self.calculate_toll_cost(distance_km)
        total_cost = fuel_info['fuel_cost'] + toll_cost
        
        # Generate checklist
        checklist = self.generate_trip_checklist()
        
        # Return complete trip plan
        trip_plan = {
            'start': start,
            'destination': destination,
            'distance_km': round(distance_km, 2),
            'duration_hours': round(duration_hours, 2),
            'fuel_needed': round(fuel_info['fuel_needed'], 2),
            'fuel_cost': round(fuel_info['fuel_cost'], 2),
            'toll_cost': round(toll_cost, 2),
            'total_cost': round(total_cost, 2),
            'mileage': mileage,
            'fuel_price': fuel_price,
            'checklist': checklist,
            'start_coords': start_coords,
            'end_coords': end_coords
        }
        
        print(f"✅ Trip plan calculated successfully!")
        return trip_plan


# Global instance for use across the application
trip_planner = TripPlanner()
