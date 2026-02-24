"""
Google Maps Service - Real-time mapping, geocoding, and route optimization
Integrates Google Maps API for enhanced dispatch capabilities
"""

import requests
import math
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class GoogleMapsService:
    """Google Maps API integration for dispatch system"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.request_timeout = 10
        self.cache = {}  # Simple cache for API responses
        self.cache_ttl = 300  # 5 minutes cache
        
    def geocode_address(self, address: str) -> Optional[Dict]:
        """Convert address to coordinates using Google Geocoding API"""
        cache_key = f"geocode_{address}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['data']
        
        try:
            url = f"{self.base_url}/geocode/json"
            params = {
                'address': address,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=self.request_timeout)
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                location = data['results'][0]['geometry']['location']
                result = {
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'formatted_address': data['results'][0]['formatted_address'],
                    'place_id': data['results'][0].get('place_id'),
                    'accuracy': data['results'][0].get('geometry', {}).get('location_type', 'APPROXIMATE')
                }
                
                # Cache the result
                self.cache[cache_key] = {
                    'data': result,
                    'timestamp': time.time()
                }
                
                return result
            
            return None
            
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None
    
    def reverse_geocode(self, lat: float, lng: float) -> Optional[Dict]:
        """Convert coordinates to address using Google Reverse Geocoding API"""
        cache_key = f"reverse_{lat}_{lng}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['data']
        
        try:
            url = f"{self.base_url}/geocode/json"
            params = {
                'latlng': f"{lat},{lng}",
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=self.request_timeout)
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                
                # Cache the result
                self.cache[cache_key] = {
                    'data': result,
                    'timestamp': time.time()
                }
                
                return result
            
            return None
            
        except Exception as e:
            print(f"Reverse geocoding error: {e}")
            return None
    
    def get_directions(self, origin: Tuple[float, float], destination: Tuple[float, float],
                     mode: str = 'driving', alternatives: bool = False) -> Optional[Dict]:
        """Get directions between two points using Google Directions API"""
        origin_str = f"{origin[0]},{origin[1]}"
        dest_str = f"{destination[0]},{destination[1]}"
        
        cache_key = f"directions_{origin_str}_{dest_str}_{mode}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['data']
        
        try:
            url = f"{self.base_url}/directions/json"
            params = {
                'origin': origin_str,
                'destination': dest_str,
                'mode': mode,
                'alternatives': 'true' if alternatives else 'false',
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=self.request_timeout)
            data = response.json()
            
            if data['status'] == 'OK' and data['routes']:
                main_route = data['routes'][0]
                leg = main_route['legs'][0]
                
                result = {
                    'status': 'OK',
                    'distance_meters': leg['distance']['value'],
                    'distance_km': leg['distance']['value'] / 1000,
                    'duration_seconds': leg['duration']['value'],
                    'duration_minutes': leg['duration']['value'] / 60,
                    'start_address': leg['start_address'],
                    'end_address': leg['end_address'],
                    'polyline': main_route['overview_polyline']['points'],
                    'steps': leg['steps'],
                    'traffic_condition': self._extract_traffic_info(main_route),
                    'alternatives': []
                }
                
                # Add alternative routes if available
                if alternatives and len(data['routes']) > 1:
                    for alt_route in data['routes'][1:]:
                        alt_leg = alt_route['legs'][0]
                        result['alternatives'].append({
                            'distance_km': alt_leg['distance']['value'] / 1000,
                            'duration_minutes': alt_leg['duration']['value'] / 60,
                            'polyline': alt_route['overview_polyline']['points']
                        })
                
                # Cache the result
                self.cache[cache_key] = {
                    'data': result,
                    'timestamp': time.time()
                }
                
                return result
            
            return {'status': data.get('status', 'UNKNOWN'), 'error': data.get('error_message')}
            
        except Exception as e:
            print(f"Directions error: {e}")
            return {'status': 'ERROR', 'error': str(e)}
    
    def get_distance_matrix(self, origins: List[Tuple[float, float]], 
                          destinations: List[Tuple[float, float]],
                          mode: str = 'driving') -> Optional[Dict]:
        """Get distance matrix between multiple origins and destinations"""
        try:
            origin_str = '|'.join([f"{lat},{lng}" for lat, lng in origins])
            dest_str = '|'.join([f"{lat},{lng}" for lat, lng in destinations])
            
            url = f"{self.base_url}/distancematrix/json"
            params = {
                'origins': origin_str,
                'destinations': dest_str,
                'mode': mode,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=self.request_timeout)
            data = response.json()
            
            if data['status'] == 'OK':
                result = {
                    'status': 'OK',
                    'origins': origins,
                    'destinations': destinations,
                    'rows': []
                }
                
                for i, row in enumerate(data['rows']):
                    row_data = {
                        'origin_index': i,
                        'elements': []
                    }
                    
                    for j, element in enumerate(row['elements']):
                        if element['status'] == 'OK':
                            row_data['elements'].append({
                                'destination_index': j,
                                'distance_meters': element['distance']['value'],
                                'distance_km': element['distance']['value'] / 1000,
                                'duration_seconds': element['duration']['value'],
                                'duration_minutes': element['duration']['value'] / 60
                            })
                        else:
                            row_data['elements'].append({
                                'destination_index': j,
                                'status': element['status'],
                                'error': element.get('error', 'Unknown error')
                            })
                    
                    result['rows'].append(row_data)
                
                return result
            
            return {'status': data.get('status', 'UNKNOWN'), 'error': data.get('error_message')}
            
        except Exception as e:
            print(f"Distance matrix error: {e}")
            return {'status': 'ERROR', 'error': str(e)}
    
    def find_nearby_places(self, location: Tuple[float, float], place_type: str,
                         radius: int = 5000) -> Optional[List[Dict]]:
        """Find nearby places using Google Places API"""
        try:
            lat, lng = location
            url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': radius,
                'type': place_type,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=self.request_timeout)
            data = response.json()
            
            if data['status'] == 'OK':
                places = []
                for place in data['results']:
                    places.append({
                        'place_id': place.get('place_id'),
                        'name': place['name'],
                        'vicinity': place.get('vicinity', ''),
                        'location': place['geometry']['location'],
                        'rating': place.get('rating'),
                        'user_ratings_total': place.get('user_ratings_total', 0),
                        'types': place.get('types', []),
                        'distance_meters': self._calculate_distance(
                            location, (place['geometry']['location']['lat'], 
                                      place['geometry']['location']['lng'])
                        ) * 1000
                    })
                
                return places
            
            return None
            
        except Exception as e:
            print(f"Nearby places error: {e}")
            return None
    
    def get_static_map(self, center: Tuple[float, float], zoom: int = 15,
                     size: str = '600x400', maptype: str = 'roadmap',
                     markers: List[Dict] = None) -> Optional[str]:
        """Generate static map image URL"""
        try:
            lat, lng = center
            url = f"{self.base_url}/staticmap"
            params = {
                'center': f"{lat},{lng}",
                'zoom': zoom,
                'size': size,
                'maptype': maptype,
                'key': self.api_key
            }
            
            # Add markers if provided
            if markers:
                marker_strings = []
                for marker in markers:
                    marker_str = f"{marker['lat']},{marker['lng']}"
                    if 'color' in marker:
                        marker_str += f",color:{marker['color']}"
                    if 'label' in marker:
                        marker_str += f",label:{marker['label']}"
                    if 'size' in marker:
                        marker_str += f",size:{marker['size']}"
                    marker_strings.append(marker_str)
                
                params['markers'] = '|'.join(marker_strings)
            
            # Build URL
            param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            return f"{url}?{param_string}"
            
        except Exception as e:
            print(f"Static map error: {e}")
            return None
    
    def get_traffic_layer(self, bounds: Dict) -> Optional[str]:
        """Get traffic layer URL for real-time traffic"""
        try:
            url = f"{self.base_url}/staticmap"
            params = {
                'center': f"{bounds['center_lat']},{bounds['center_lng']}",
                'zoom': bounds.get('zoom', 15),
                'size': bounds.get('size', '640x640'),
                'maptype': 'roadmap',
                'traffic': 'true',
                'key': self.api_key
            }
            
            param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            return f"{url}?{param_string}"
            
        except Exception as e:
            print(f"Traffic layer error: {e}")
            return None
    
    def calculate_optimal_route(self, waypoints: List[Tuple[float, float]],
                            optimize: bool = True) -> Optional[Dict]:
        """Calculate optimal route through multiple waypoints"""
        if len(waypoints) < 2:
            return None
        
        try:
            origin = waypoints[0]
            destination = waypoints[-1]
            
            # Build waypoint string
            if len(waypoints) > 2:
                waypoint_str = '|'.join([f"{lat},{lng}" for lat, lng in waypoints[1:-1]])
            else:
                waypoint_str = None
            
            url = f"{self.base_url}/directions/json"
            params = {
                'origin': f"{origin[0]},{origin[1]}",
                'destination': f"{destination[0]},{destination[1]}",
                'optimize': 'true' if optimize else 'false',
                'key': self.api_key
            }
            
            if waypoint_str:
                params['waypoints'] = waypoint_str
            
            response = requests.get(url, params=params, timeout=self.request_timeout)
            data = response.json()
            
            if data['status'] == 'OK' and data['routes']:
                route = data['routes'][0]
                leg = route['legs'][0]
                
                return {
                    'status': 'OK',
                    'optimized_waypoints': route.get('waypoint_order', []),
                    'total_distance_km': route['legs'][0]['distance']['value'] / 1000,
                    'total_duration_minutes': route['legs'][0]['duration']['value'] / 60,
                    'polyline': route['overview_polyline']['points'],
                    'steps': route['legs'][0]['steps']
                }
            
            return {'status': data.get('status', 'UNKNOWN'), 'error': data.get('error_message')}
            
        except Exception as e:
            print(f"Route optimization error: {e}")
            return {'status': 'ERROR', 'error': str(e)}
    
    def _extract_traffic_info(self, route: Dict) -> str:
        """Extract traffic information from route data"""
        try:
            if 'legs' in route and route['legs']:
                leg = route['legs'][0]
                if 'duration_in_traffic' in leg:
                    duration_with_traffic = leg['duration_in_traffic']['value']
                    base_duration = leg['duration']['value']
                    
                    if duration_with_traffic > base_duration:
                        delay_percentage = ((duration_with_traffic - base_duration) / base_duration) * 100
                        if delay_percentage > 50:
                            return "HEAVY_TRAFFIC"
                        elif delay_percentage > 20:
                            return "MODERATE_TRAFFIC"
                        else:
                            return "LIGHT_TRAFFIC"
            
            return "NO_TRAFFIC_DATA"
            
        except Exception:
            return "TRAFFIC_ERROR"
    
    def _calculate_distance(self, point1: Tuple[float, float], 
                          point2: Tuple[float, float]) -> float:
        """Calculate distance between two points (Haversine)"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(point1[0])
        lat2_rad = math.radians(point2[0])
        delta_lat = math.radians(point2[0] - point1[0])
        delta_lon = math.radians(point2[1] - point1[1])
        
        a = (math.sin(delta_lat/2)**2 + 
              math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def validate_api_key(self) -> bool:
        """Validate Google Maps API key"""
        try:
            # Test with a simple geocoding request
            url = f"{self.base_url}/geocode/json"
            params = {
                'address': 'New York, NY',
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=self.request_timeout)
            data = response.json()
            
            return data.get('status') == 'OK'
            
        except Exception:
            return False
    
    def get_api_usage(self) -> Optional[Dict]:
        """Get API usage statistics (requires billing account)"""
        try:
            url = f"https://maps.googleapis.com/maps/api/distancematrix/json"
            params = {
                'origins': '0,0',
                'destinations': '0,0',
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=self.request_timeout)
            
            # Check response headers for usage info
            usage_info = {
                'quota_limit': response.headers.get('X-Goog-Maps-Quota-Id'),
                'remaining_quota': response.headers.get('X-Goog-Maps-Quota-Remaining'),
                'response_code': response.status_code
            }
            
            return usage_info
            
        except Exception as e:
            print(f"API usage check error: {e}")
            return None


# Global instance (will be initialized with API key from config)
google_maps_service = None

def initialize_google_maps(api_key: str) -> GoogleMapsService:
    """Initialize Google Maps service with API key"""
    global google_maps_service
    google_maps_service = GoogleMapsService(api_key)
    
    if google_maps_service.validate_api_key():
        print("✅ Google Maps API initialized successfully")
    else:
        print("⚠️ Google Maps API key validation failed")
    
    return google_maps_service
