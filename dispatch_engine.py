"""
Smart Dispatch Engine Core Architecture
Production-grade Uber-inspired dispatch system for car services
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
import math
import uuid

class JobStatus(Enum):
    """Complete job lifecycle states"""
    SEARCHING = "SEARCHING"
    OFFERED = "OFFERED"
    ACCEPTED = "ACCEPTED"
    ARRIVED = "ARRIVED"
    WORKING = "WORKING"
    COMPLETED = "COMPLETED"
    CANCELLED_BY_USER = "CANCELLED_BY_USER"
    CANCELLED_BY_MECHANIC = "CANCELLED_BY_MECHANIC"
    NO_MECHANIC_FOUND = "NO_MECHANIC_FOUND"
    EXPIRED = "EXPIRED"

class MechanicStatus(Enum):
    """Mechanic availability states"""
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    BUSY = "BUSY"
    SUSPENDED = "SUSPENDED"

class OfferStatus(Enum):
    """Job offer states"""
    OFFERED = "OFFERED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class ServiceType(Enum):
    """Service types supported"""
    MECHANIC = "MECHANIC"
    FUEL_DELIVERY = "FUEL_DELIVERY"
    TOW_TRUCK = "TOW_TRUCK"
    EXPERT = "EXPERT"

@dataclass
class Location:
    """Location coordinates"""
    latitude: float
    longitude: float
    address: Optional[str] = None
    
    def distance_to(self, other: 'Location') -> float:
        """Calculate distance using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

@dataclass
class JobRequest:
    """Job request data structure"""
    id: str
    user_id: int
    issue: str
    location: Location
    service_type: ServiceType
    urgency: bool = False
    created_at: datetime = None
    status: JobStatus = JobStatus.SEARCHING
    mechanic_id: Optional[int] = None
    accepted_at: Optional[datetime] = None
    arrived_at: Optional[datetime] = None
    started_work_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    base_fee: float = 0.0
    distance_fee: float = 0.0
    emergency_bonus: float = 0.0
    total_fee: float = 0.0
    platform_commission: float = 0.0
    mechanic_earnings: float = 0.0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class Mechanic:
    """Mechanic profile and status"""
    id: int
    name: str
    phone: str
    email: str
    service_type: ServiceType
    specialization: str
    rating: float
    experience_years: int
    status: MechanicStatus = MechanicStatus.OFFLINE
    current_location: Optional[Location] = None
    last_location_update: Optional[datetime] = None

@dataclass
class JobOffer:
    """Job offer to mechanic"""
    id: str
    job_id: str
    mechanic_id: int
    offered_at: datetime
    expires_at: datetime
    status: OfferStatus = OfferStatus.OFFERED
    eta_minutes: int = 0

@dataclass
class TrackingSession:
    """Live tracking session"""
    id: str
    job_id: str
    mechanic_id: int
    start_location: Location
    current_location: Location
    started_at: datetime
    last_update: datetime
    eta_minutes: int

class SmartDispatchEngine:
    """Core dispatch engine orchestrating the entire job lifecycle"""
    
    def __init__(self):
        self.active_jobs: Dict[str, JobRequest] = {}
        self.mechanics: Dict[int, Mechanic] = {}
        self.mechanic_locations: Dict[int, Location] = {}
        self.active_offers: Dict[str, JobOffer] = {}
        self.tracking_sessions: Dict[str, TrackingSession] = {}
        
        # Configuration
        self.OFFER_TIMEOUT_SECONDS = 15
        self.SEARCH_RADIUS_KM = 10.0
        self.MAX_OFFERS_PER_JOB = 5
        self.ARRIVAL_THRESHOLD_METERS = 50
        self.AVERAGE_SPEED_KMH = 30.0
        
    def create_job_request(self, user_id: int, issue: str, location: Location, 
                           service_type: ServiceType, urgency: bool = False) -> JobRequest:
        """Phase 1: Job Request Creation Engine"""
        job_id = str(uuid.uuid4())
        job = JobRequest(
            id=job_id,
            user_id=user_id,
            issue=issue,
            location=location,
            service_type=service_type,
            urgency=urgency
        )
        
        self.active_jobs[job_id] = job
        self._log_job_event(job_id, "JOB_CREATED", f"Job created: {issue}")
        
        return job
    
    def update_mechanic_location(self, mechanic_id: int, location: Location):
        """Phase 3: Location Management Engine"""
        self.mechanic_locations[mechanic_id] = location
        
        if mechanic_id in self.mechanics:
            self.mechanics[mechanic_id].current_location = location
            self.mechanics[mechanic_id].last_location_update = datetime.utcnow()
    
    def calculate_distance_and_eta(self, origin: Location, destination: Location) -> Tuple[float, int]:
        """Phase 4: Distance & ETA Engine"""
        distance_km = origin.distance_to(destination)
        eta_minutes = int((distance_km / self.AVERAGE_SPEED_KMH) * 60)
        return distance_km, eta_minutes
    
    def get_available_mechanics(self, service_type: ServiceType, 
                              job_location: Location) -> List[Mechanic]:
        """Phase 2 & 5: Mechanic Availability & Smart Filtering Engine"""
        available_mechanics = []
        
        for mechanic in self.mechanics.values():
            # Filter by service type and status
            if (mechanic.service_type == service_type and 
                mechanic.status == MechanicStatus.ONLINE and 
                mechanic.current_location is not None):
                
                # Check if within search radius
                distance, _ = self.calculate_distance_and_eta(
                    mechanic.current_location, job_location
                )
                
                if distance <= self.SEARCH_RADIUS_KM:
                    # Check location freshness (updated within last 5 minutes)
                    if (mechanic.last_location_update and 
                        datetime.utcnow() - mechanic.last_location_update <= timedelta(minutes=5)):
                        available_mechanics.append(mechanic)
        
        return available_mechanics
    
    def rank_mechanics(self, mechanics: List[Mechanic], job_location: Location, 
                      is_emergency: bool = False) -> List[Tuple[Mechanic, float]]:
        """Phase 6: Ranking & Fairness Engine"""
        ranked_mechanics = []
        
        for mechanic in mechanics:
            distance, eta = self.calculate_distance_and_eta(
                mechanic.current_location, job_location
            )
            
            # Calculate score (lower is better for ETA, higher is better for rating)
            eta_weight = 1.0 / (eta + 1)  # Lower ETA = higher score
            rating_weight = mechanic.rating / 5.0  # Normalize rating
            performance_weight = min(mechanic.experience_years / 10.0, 1.0)  # Cap at 1.0
            fairness_weight = 1.0  # TODO: Implement fairness scoring
            
            # Emergency priority multiplier
            emergency_multiplier = 2.0 if is_emergency else 1.0
            
            score = (eta_weight * 0.4 + rating_weight * 0.3 + 
                    performance_weight * 0.2 + fairness_weight * 0.1) * emergency_multiplier
            
            ranked_mechanics.append((mechanic, score))
        
        # Sort by score (descending)
        ranked_mechanics.sort(key=lambda x: x[1], reverse=True)
        
        return ranked_mechanics[:self.MAX_OFFERS_PER_JOB]
    
    def _log_job_event(self, job_id: str, event_type: str, details: str):
        """Log job lifecycle events"""
        timestamp = datetime.utcnow().isoformat()
        print(f"[{timestamp}] JOB:{job_id} {event_type} - {details}")

# Initialize global dispatch engine
dispatch_engine = SmartDispatchEngine()
