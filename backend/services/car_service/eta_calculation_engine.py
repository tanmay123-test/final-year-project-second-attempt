"""
ETA Calculation Engine
Calculates distance and ETA using OSRM routing service
"""

import requests
import math
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from .location_resolution_engine import Location

@dataclass
class ETAResult:
    distance_km: float
    eta_minutes: int
    success: bool
    error_message: Optional[str] = None
    raw_response: Optional[Dict] = None

class ETACalculationEngine:
    def __init__(self):
        # OSRM public server (for development)
        # In production, you'd want to host your own OSRM server
        self.osrm_base_url = "https://router.project-osrm.org"
        self.fallback_speed_kmh = 30  # Average city driving speed
        
        # Cache for ETA calculations to avoid repeated API calls
        self.eta_cache = {}
    
    def calculate_eta(self, origin: Location, destination: Location) -> ETAResult:
        """
        Calculate ETA between two locations using OSRM
        
        Args:
            origin: Starting location
            destination: Destination location
        
        Returns:
            ETAResult with distance, ETA, and success status
        """
        # Check cache first
        cache_key = self._get_cache_key(origin, destination)
        if cache_key in self.eta_cache:
            return self.eta_cache[cache_key]
        
        try:
            # Call OSRM API
            eta_result = self._call_osrm_api(origin, destination)
            
            # Cache the result
            self.eta_cache[cache_key] = eta_result
            
            return eta_result
        
        except Exception as e:
            # Fallback to straight-line distance calculation
            return self._fallback_eta_calculation(origin, destination, str(e))
    
    def _call_osrm_api(self, origin: Location, destination: Location) -> ETAResult:
        """Call OSRM routing API"""
        # Build OSRM URL
        coordinates = f"{origin.longitude},{origin.latitude};{destination.longitude},{destination.latitude}"
        url = f"{self.osrm_base_url}/route/v1/driving/{coordinates}"
        
        params = {
            "overview": "false",  # Don't return geometry
            "alternatives": "false",  # Don't return alternative routes
            "steps": "false"  # Don't return turn-by-turn directions
        }
        
        try:
            response = requests.get(
                url,
                params=params,
                timeout=10,
                headers={"User-Agent": "ExpertEase-CarService/1.0"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("code") == "Ok" and data.get("routes"):
                    route = data["routes"][0]
                    distance_meters = route["distance"]
                    duration_seconds = route["duration"]
                    
                    # Convert to kilometers and minutes
                    distance_km = distance_meters / 1000
                    eta_minutes = int(duration_seconds / 60)
                    
                    return ETAResult(
                        distance_km=distance_km,
                        eta_minutes=eta_minutes,
                        success=True,
                        raw_response=data
                    )
                else:
                    return ETAResult(
                        distance_km=0,
                        eta_minutes=0,
                        success=False,
                        error_message=data.get("message", "OSRM API error")
                    )
            
            else:
                return ETAResult(
                    distance_km=0,
                    eta_minutes=0,
                    success=False,
                    error_message=f"OSRM API error: {response.status_code}"
                )
        
        except requests.RequestException as e:
            return ETAResult(
                distance_km=0,
                eta_minutes=0,
                success=False,
                error_message=f"Network error: {str(e)}"
            )
    
    def _fallback_eta_calculation(self, origin: Location, destination: Location, error: str) -> ETAResult:
        """
        Fallback ETA calculation using straight-line distance
        
        This is used when OSRM API is unavailable
        """
        # Calculate straight-line distance
        distance_km = self._calculate_straight_line_distance(origin, destination)
        
        # Estimate ETA using fallback speed
        eta_minutes = int((distance_km / self.fallback_speed_kmh) * 60)
        
        return ETAResult(
            distance_km=distance_km,
            eta_minutes=eta_minutes,
            success=True,  # Still successful, just using fallback
            error_message=f"OSRM unavailable, using fallback: {error}"
        )
    
    def _calculate_straight_line_distance(self, origin: Location, destination: Location) -> float:
        """Calculate straight-line distance between two locations"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(origin.latitude)
        lat2_rad = math.radians(destination.latitude)
        delta_lat = math.radians(destination.latitude - origin.latitude)
        delta_lon = math.radians(destination.longitude - origin.longitude)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _get_cache_key(self, origin: Location, destination: Location) -> str:
        """Generate cache key for ETA calculation"""
        return f"{origin.latitude:.4f},{origin.longitude:.4f}_to_{destination.latitude:.4f},{destination.longitude:.4f}"
    
    def calculate_multiple_etas(self, origin: Location, destinations: list) -> Dict[int, ETAResult]:
        """
        Calculate ETA from origin to multiple destinations
        
        Returns:
            Dict mapping destination index to ETAResult
        """
        results = {}
        
        for i, destination in enumerate(destinations):
            results[i] = self.calculate_eta(origin, destination)
        
        return results
    
    def get_eta_statistics(self, origin: Location, destinations: list) -> Dict:
        """Get statistics for multiple ETA calculations"""
        etas = self.calculate_multiple_etas(origin, destinations)
        
        successful_etas = [eta for eta in etas.values() if eta.success]
        failed_etas = [eta for eta in etas.values() if not eta.success]
        
        if successful_etas:
            distances = [eta.distance_km for eta in successful_etas]
            times = [eta.eta_minutes for eta in successful_etas]
            
            return {
                "total_destinations": len(destinations),
                "successful_calculations": len(successful_etas),
                "failed_calculations": len(failed_etas),
                "average_distance_km": sum(distances) / len(distances),
                "average_eta_minutes": sum(times) / len(times),
                "min_distance_km": min(distances),
                "max_distance_km": max(distances),
                "min_eta_minutes": min(times),
                "max_eta_minutes": max(times),
                "fallback_used": any(eta.error_message and "fallback" in eta.error_message.lower() for eta in successful_etas)
            }
        else:
            return {
                "total_destinations": len(destinations),
                "successful_calculations": 0,
                "failed_calculations": len(failed_etas),
                "error": "All ETA calculations failed"
            }
    
    def clear_cache(self):
        """Clear the ETA calculation cache"""
        self.eta_cache.clear()
    
    def get_cache_size(self) -> int:
        """Get the current cache size"""
        return len(self.eta_cache)

# Global instance
eta_calculation_engine = ETACalculationEngine()
