"""
Location Resolution Engine
Handles GPS coordinates and geocoding from location names
"""

import requests
import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Location:
    latitude: float
    longitude: float
    name: str
    resolved: bool = True

class LocationResolutionEngine:
    def __init__(self):
        # OpenStreetMap Nominatim API (free, no API key required)
        self.geocoding_api = "https://nominatim.openstreetmap.org/search"
        self.reverse_geocoding_api = "https://nominatim.openstreetmap.org/reverse"
        
        # Common Mumbai area coordinates for fallback
        self.mumbai_coordinates = {
            "asalpha": (19.0954, 72.8783),
            "ghatkopar": (19.0836, 72.8896),
            "andheri": (19.1197, 72.8465),
            "bandra": (19.0596, 72.8295),
            "borivali": (19.2307, 72.8567),
            "kurla": (19.0728, 72.8846),
            "chembur": (19.0460, 72.8495),
            "vashi": (19.0760, 73.0085),
            "nerul": (19.0422, 73.0199),
            "kharghar": (19.0372, 73.0647),
            "mumbai": (19.0760, 72.8777),
            "thane": (19.1883, 72.9765),
            "navi mumbai": (19.0330, 73.0297)
        }
    
    def resolve_location(self, location_data: Dict) -> Location:
        """
        Resolve location from either coordinates or location name
        
        Args:
            location_data: Dict containing either:
                - latitude and longitude
                - location_name
        
        Returns:
            Location object with coordinates and name
        """
        # Check if coordinates are provided
        if "latitude" in location_data and "longitude" in location_data:
            lat = float(location_data["latitude"])
            lon = float(location_data["longitude"])
            
            # Validate coordinates
            if not self._is_valid_coordinates(lat, lon):
                raise ValueError(f"Invalid coordinates: {lat}, {lon}")
            
            # Get location name from reverse geocoding
            name = self._reverse_geocode(lat, lon) or f"Lat: {lat}, Lon: {lon}"
            
            return Location(
                latitude=lat,
                longitude=lon,
                name=name,
                resolved=True
            )
        
        # Check if location name is provided
        elif "location_name" in location_data:
            location_name = location_data["location_name"].strip()
            
            # Try to geocode the location name
            coords = self._geocode_location(location_name)
            
            if coords:
                lat, lon = coords
                return Location(
                    latitude=lat,
                    longitude=lon,
                    name=location_name,
                    resolved=True
                )
            else:
                raise ValueError(f"Could not resolve location: {location_name}")
        
        else:
            raise ValueError("Either latitude/longitude or location_name must be provided")
    
    def _is_valid_coordinates(self, latitude: float, longitude: float) -> bool:
        """Validate latitude and longitude coordinates"""
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    
    def _geocode_location(self, location_name: str) -> Optional[Tuple[float, float]]:
        """
        Convert location name to coordinates using geocoding
        
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        # First try local Mumbai coordinates cache
        location_lower = location_name.lower()
        for area, coords in self.mumbai_coordinates.items():
            if area in location_lower:
                return coords
        
        # Try OpenStreetMap Nominatim API
        try:
            params = {
                "q": location_name,
                "format": "json",
                "limit": 1,
                "countrycodes": "in"  # Limit to India
            }
            
            response = requests.get(
                self.geocoding_api,
                params=params,
                timeout=10,
                headers={"User-Agent": "ExpertEase-CarService/1.0"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    result = data[0]
                    lat = float(result["lat"])
                    lon = float(result["lon"])
                    return (lat, lon)
        
        except Exception as e:
            print(f"Geocoding error for '{location_name}': {e}")
        
        return None
    
    def _reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Convert coordinates to location name using reverse geocoding
        
        Returns:
            Location name or None if not found
        """
        try:
            params = {
                "lat": latitude,
                "lon": longitude,
                "format": "json",
                "zoom": 18  # Street level detail
            }
            
            response = requests.get(
                self.reverse_geocoding_api,
                params=params,
                timeout=10,
                headers={"User-Agent": "ExpertEase-CarService/1.0"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and "display_name" in data:
                    return data["display_name"]
        
        except Exception as e:
            print(f"Reverse geocoding error for {latitude}, {longitude}: {e}")
        
        return None
    
    def validate_location_input(self, location_data: Dict) -> Tuple[bool, str]:
        """
        Validate location input data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check coordinates
        if "latitude" in location_data and "longitude" in location_data:
            try:
                lat = float(location_data["latitude"])
                lon = float(location_data["longitude"])
                
                if not self._is_valid_coordinates(lat, lon):
                    return False, f"Invalid coordinates: {lat}, {lon}"
                
                return True, ""
            
            except (ValueError, TypeError):
                return False, "Invalid coordinate format"
        
        # Check location name
        elif "location_name" in location_data:
            location_name = location_data["location_name"].strip()
            
            if not location_name:
                return False, "Location name cannot be empty"
            
            if len(location_name) < 2:
                return False, "Location name too short"
            
            return True, ""
        
        else:
            return False, "Either latitude/longitude or location_name must be provided"
    
    def get_distance_between_locations(self, loc1: Location, loc2: Location) -> float:
        """
        Calculate distance between two locations in kilometers
        
        Uses Haversine formula
        """
        import math
        
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(loc1.latitude)
        lat2_rad = math.radians(loc2.latitude)
        delta_lat = math.radians(loc2.latitude - loc1.latitude)
        delta_lon = math.radians(loc2.longitude - loc1.longitude)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def format_location_display(self, location: Location) -> str:
        """Format location for display"""
        if location.resolved:
            if location.name and not location.name.startswith("Lat:"):
                return f"{location.name} ({location.latitude:.4f}, {location.longitude:.4f})"
            else:
                return f"({location.latitude:.4f}, {location.longitude:.4f})"
        else:
            return "Unknown Location"

# Global instance
location_resolution_engine = LocationResolutionEngine()
