"""
Smart Search Engine
Main engine that combines all components for nearby mechanic discovery
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
from datetime import datetime, timedelta

from .location_resolution_engine import LocationResolutionEngine, Location
from .skill_detection_engine import SkillDetectionEngine
from .smart_search_db import SmartSearchDB
from .eta_calculation_engine import ETACalculationEngine, ETAResult
from .car_service_worker_db import car_service_worker_db

@dataclass
class SearchRequest:
    issue_description: str
    location_data: Dict
    search_radius_km: float = 5.0
    max_results: int = 10

@dataclass
class MechanicResult:
    mechanic_id: int
    name: str
    skill: str
    distance_km: float
    eta_minutes: int
    rating: float
    experience: int
    phone: str
    email: str
    status: str
    confidence_score: float = 1.0

class SmartSearchEngine:
    def __init__(self):
        self.location_engine = LocationResolutionEngine()
        self.skill_engine = SkillDetectionEngine()
        self.db = SmartSearchDB()
        self.eta_engine = ETACalculationEngine()
        self.worker_db = car_service_worker_db
        
        # Configuration
        self.default_search_radius = 5.0  # km
        self.max_search_results = 10
        self.cache_duration_minutes = 5
    
    def search_nearby_mechanics(self, search_request: SearchRequest) -> Dict:
        """
        Main search method that finds nearby mechanics based on issue and location
        
        Args:
            search_request: SearchRequest with issue description and location
        
        Returns:
            Dict with search results
        """
        try:
            # Step 1: Resolve location
            user_location = self.location_engine.resolve_location(search_request.location_data)
            
            # Step 2: Detect required skill
            required_skill, skill_confidence = self.skill_engine.detect_skill(search_request.issue_description)
            
            # Step 3: Check cache first
            cached_results = self.db.get_cached_results(
                user_location.latitude, 
                user_location.longitude,
                required_skill,
                search_request.search_radius_km
            )
            
            if cached_results:
                return self._format_search_response(user_location, required_skill, cached_results, from_cache=True)
            
            # Step 4: Get available mechanics
            available_mechanics = self._get_available_mechanics(required_skill)
            
            # Step 5: Filter by location and calculate ETA
            nearby_mechanics = self._filter_and_calculate_eta(user_location, available_mechanics, search_request.search_radius_km)
            
            # Step 6: Sort by ETA (closest first)
            nearby_mechanics.sort(key=lambda x: x.eta_minutes)
            
            # Step 7: Limit results
            nearby_mechanics = nearby_mechanics[:search_request.max_results]
            
            # Step 8: Cache results
            if nearby_mechanics:
                self.db.cache_search_results(
                    user_location.latitude,
                    user_location.longitude,
                    required_skill,
                    [self._mechanic_to_dict(m) for m in nearby_mechanics],
                    search_request.search_radius_km,
                    self.cache_duration_minutes
                )
            
            return self._format_search_response(user_location, required_skill, nearby_mechanics)
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Search failed. Please try again."
            }
    
    def _get_available_mechanics(self, required_skill: str) -> List[Dict]:
        """Get mechanics who are online, available, and have the required skill"""
        # Get all online mechanics
        mechanics = self.worker_db.get_online_mechanics()
        
        # Filter by availability (not busy)
        mechanics = [m for m in mechanics if not m.get('is_busy', False)]
        
        # Filter by skill matching
        skilled_mechanics = []
        for mechanic in mechanics:
            mechanic_skills = mechanic.get('skills', '').lower()
            
            # Check if mechanic has the required skill
            if self._skill_matches(mechanic_skills, required_skill):
                skilled_mechanics.append(mechanic)
        
        return skilled_mechanics
    
    def _skill_matches(self, mechanic_skills: str, required_skill: str) -> bool:
        """Check if mechanic's skills match the required skill"""
        if not mechanic_skills or not required_skill:
            return True  # Default to true if no specific skill required
        
        mechanic_skills_lower = mechanic_skills.lower()
        required_skill_lower = required_skill.lower()
        
        # Direct skill match
        if required_skill_lower in mechanic_skills_lower:
            return True
        
        # Check skill keywords
        skill_keywords = self.skill_engine.get_skill_keywords(required_skill)
        for keyword in skill_keywords:
            if keyword.lower() in mechanic_skills_lower:
                return True
        
        # Check for "general" or "all" skills
        if any(general in mechanic_skills_lower for general in ['general', 'all', 'multi']):
            return True
        
        # Check for "engine" matching "engine expert"
        if 'engine' in required_skill_lower and 'engine' in mechanic_skills_lower:
            return True
        
        # Check for "expert" matching any specialist
        if 'expert' in mechanic_skills_lower:
            return True
        
        # Check for partial matches
        if any(word in mechanic_skills_lower for word in required_skill_lower.split()):
            return True
        
        # Enhanced matching: Any expert should handle basic issues
        if 'expert' in mechanic_skills_lower and required_skill_lower in ['brake specialist', 'general mechanic', 'electrical specialist', 'tire specialist']:
            return True
        
        # Enhanced matching: Check if mechanic can handle the issue category
        if 'expert' in mechanic_skills_lower:
            # Engine expert should handle engine, brake, and general issues
            if any(issue in required_skill_lower for issue in ['engine', 'brake', 'general']):
                return True
        
        return False
    
    def _filter_and_calculate_eta(self, user_location: Location, mechanics: List[Dict], radius_km: float) -> List[MechanicResult]:
        """Filter mechanics by distance and calculate ETA"""
        results = []
        user_loc = Location(user_location.latitude, user_location.longitude, user_location.name)
        
        for mechanic in mechanics:
            # Get mechanic's location
            mechanic_location = self.db.get_mechanic_location(mechanic['id'])
            
            if not mechanic_location:
                # Skip mechanics without location data
                continue
            
            # Check if location is recent (within 2 hours)
            location_time = datetime.fromisoformat(mechanic_location['updated_at'])
            if datetime.now() - location_time > timedelta(hours=2):
                continue
            
            # Calculate distance
            distance = self.db.calculate_distance(
                user_location.latitude, user_location.longitude,
                mechanic_location['latitude'], mechanic_location['longitude']
            )
            
            # Filter by radius
            if distance > radius_km:
                continue
            
            # Calculate ETA
            mechanic_loc = Location(
                mechanic_location['latitude'],
                mechanic_location['longitude'],
                f"Mechanic {mechanic['id']}"
            )
            
            eta_result = self.eta_engine.calculate_eta(user_loc, mechanic_loc)
            
            if eta_result.success:
                result = MechanicResult(
                    mechanic_id=mechanic['id'],
                    name=mechanic.get('name', 'Unknown'),
                    skill=mechanic.get('skills', 'General Mechanic'),
                    distance_km=distance,
                    eta_minutes=eta_result.eta_minutes,
                    rating=float(mechanic.get('rating', 0.0)),
                    experience=int(mechanic.get('experience', 0)),
                    phone=mechanic.get('phone', 'Not available'),
                    email=mechanic.get('email', 'Not available'),
                    status='ONLINE' if mechanic.get('is_online') else 'OFFLINE'
                )
                results.append(result)
        
        return results
    
    def _format_search_response(self, user_location: Location, required_skill: str, mechanics: List, from_cache: bool = False) -> Dict:
        """Format search response for API"""
        if not mechanics:
            return {
                "success": True,
                "user_location": user_location.name,
                "user_coordinates": {
                    "latitude": user_location.latitude,
                    "longitude": user_location.longitude
                },
                "required_skill": required_skill,
                "mechanics": [],
                "message": "No mechanics available within your area.",
                "from_cache": from_cache,
                "total_results": 0
            }
        
        # Handle both MechanicResult objects and dictionaries
        if mechanics and hasattr(mechanics[0], 'mechanic_id'):
            # List of MechanicResult objects
            mechanic_dicts = [self._mechanic_to_dict(m) for m in mechanics]
        else:
            # List of dictionaries (from cache)
            mechanic_dicts = mechanics
        
        return {
            "success": True,
            "user_location": user_location.name,
            "user_coordinates": {
                "latitude": user_location.latitude,
                "longitude": user_location.longitude
            },
            "required_skill": required_skill,
            "mechanics": mechanic_dicts,
            "from_cache": from_cache,
            "total_results": len(mechanic_dicts),
            "search_radius_km": self.default_search_radius
        }
    
    def _mechanic_to_dict(self, mechanic: MechanicResult) -> Dict:
        """Convert MechanicResult to dictionary"""
        return {
            "mechanic_id": mechanic.mechanic_id,
            "name": mechanic.name,
            "skill": mechanic.skill,
            "distance_km": round(mechanic.distance_km, 2),
            "eta_minutes": mechanic.eta_minutes,
            "rating": round(mechanic.rating, 1),
            "experience": mechanic.experience,
            "phone": mechanic.phone,
            "email": mechanic.email,
            "status": mechanic.status,
            "confidence_score": mechanic.confidence_score
        }
    
    def search_by_keyword(self, keyword: str) -> List[Dict]:
        """Search mechanics by keyword using FTS5"""
        return self.db.search_mechanics_fts(keyword)
    
    def update_mechanic_location(self, mechanic_id: int, latitude: float, longitude: float) -> bool:
        """Update mechanic's live location"""
        return self.db.update_mechanic_location(mechanic_id, latitude, longitude)
    
    def get_search_statistics(self) -> Dict:
        """Get search engine statistics"""
        return {
            "cache_size": self.db.get_cached_results_count(),
            "eta_cache_size": self.eta_engine.get_cache_size(),
            "total_mechanics": len(self.worker_db.get_all_workers()),
            "online_mechanics": len(self.worker_db.get_online_mechanics()),
            "available_mechanics": len([w for w in self.worker_db.get_online_mechanics() if not w.get('is_busy', False)])
        }

# Global instance
smart_search_engine = SmartSearchEngine()
