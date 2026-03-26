"""
Tow Truck Data Models
Simple data structures for tow truck operations
"""

from typing import Optional, List
from datetime import datetime

# Simple data structures instead of dataclasses
class TowRequest:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ActiveJob:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class Earnings:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
class TowOperatorProfile:
    """Tow Truck Operator Profile"""
    id: int
    worker_id: int
    name: str
    truck_model: str
    vehicle_number: str
    capacity: str
    is_online: bool
    is_busy: bool
    city: str
    rating: float
    service_radius: int
    current_location: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @property
    def status(self) -> str:
        """Get operator status string"""
        if not self.is_online:
            return "OFFLINE"
        elif self.is_busy:
            return "BUSY"
        else:
            return "ONLINE_AVAILABLE"
    
    def go_online(self):
        """Set operator to online"""
        self.is_online = True
        self.is_busy = False
    
    def go_offline(self):
        """Set operator to offline"""
        self.is_online = False
        self.is_busy = False
    
    def set_busy(self):
        """Set operator to busy"""
        self.is_busy = True
    
    def set_available(self):
        """Set operator to available"""
        self.is_busy = False

class TowRequest:
    """Tow Request Model"""
    id: int
    user_id: int
    pickup_location: str
    drop_location: str
    vehicle_type: str
    vehicle_condition: str
    distance: float
    estimated_earning: float
    priority: str
    assigned_operator_id: Optional[int] = None
    status: str = "SEARCHING"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Priority levels
    PRIORITY_EMERGENCY = "EMERGENCY"
    PRIORITY_HIGH = "HIGH"
    PRIORITY_NORMAL = "NORMAL"
    PRIORITY_LOW = "LOW"
    
    # Status values
    STATUS_SEARCHING = "SEARCHING"
    STATUS_ASSIGNED = "ASSIGNED"
    STATUS_ACCEPTED = "ACCEPTED"
    STATUS_ARRIVING = "ARRIVING"
    STATUS_ARRIVED = "ARRIVED"
    STATUS_LOADING = "LOADING"
    STATUS_TOWING = "TOWING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CANCELLED = "CANCELLED"
    
    def is_emergency(self) -> bool:
        """Check if this is an emergency request"""
        return self.priority == self.PRIORITY_EMERGENCY
    
    def assign_operator(self, operator_id: int):
        """Assign operator to request"""
        self.assigned_operator_id = operator_id
        self.status = self.STATUS_ASSIGNED

class ActiveJob:
    """Active Tow Job Model"""
    id: int
    request_id: int
    operator_id: int
    user_name: str
    pickup_location: str
    drop_location: str
    status: str = "ACCEPTED"
    otp: Optional[str] = None
    pickup_photo: Optional[str] = None
    drop_photo: Optional[str] = None
    start_time: Optional[str] = None
    pickup_time: Optional[str] = None
    drop_time: Optional[str] = None
    completion_time: Optional[str] = None
    created_at: Optional[str] = None
    
    # Status values
    STATUS_ACCEPTED = "ACCEPTED"
    STATUS_ARRIVING = "ARRIVING"
    STATUS_ARRIVED = "ARRIVED"
    STATUS_LOADING = "LOADING"
    STATUS_TOWING = "TOWING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CANCELLED = "CANCELLED"
    
    def mark_arrived(self):
        """Mark job as arrived"""
        self.status = self.STATUS_ARRIVED
        self.arrival_time = datetime.now().isoformat()
    
    def mark_loading(self):
        """Mark job as loading (after OTP verification)"""
        self.status = self.STATUS_LOADING
        self.pickup_time = datetime.now().isoformat()
    
    def start_towing(self):
        """Start towing"""
        self.status = self.STATUS_TOWING
    
    def complete_job(self):
        """Complete job"""
        self.status = self.STATUS_COMPLETED
        self.completion_time = datetime.now().isoformat()

class Earnings:
    """Earnings Model"""
    id: int
    operator_id: int
    job_id: int
    base_amount: float
    distance_amount: float
    bonus: float = 0.0
    final_amount: float = 0.0
    created_at: Optional[str] = None
    
    def calculate_final_amount(self):
        """Calculate final amount"""
        self.final_amount = self.base_amount + self.distance_amount + self.bonus

class SafetyAlert:
    """Safety Alert Model"""
    id: int
    operator_id: int
    job_id: int
    alert_type: str
    description: str
    location: Optional[str] = None
    is_resolved: bool = False
    created_at: Optional[str] = None
    
    # Alert types
    TYPE_PANIC = "PANIC"
    TYPE_ACCIDENT = "ACCIDENT"
    TYPE_BREAKDOWN = "BREAKDOWN"
    TYPE_EMERGENCY = "EMERGENCY"
    TYPE_OTHER = "OTHER"
    
    def resolve(self):
        """Mark alert as resolved"""
        self.is_resolved = True

class VehicleInfo:
    """Vehicle Information"""
    type: str
    condition: str
    make: str
    model: str
    year: int
    color: str
    license_plate: str
    
    # Vehicle types
    TYPE_SMALL_CAR = "SMALL_CAR"
    TYPE_SUV = "SUV"
    TYPE_VAN = "VAN"
    TYPE_TRUCK = "TRUCK"
    TYPE_MOTORCYCLE = "MOTORCYCLE"
    TYPE_OTHER = "OTHER"
    
    # Vehicle conditions
    CONDITION_WORKING = "WORKING"
    CONDITION_NOT_WORKING = "NOT_WORKING"
    CONDITION_ACCIDENT = "ACCIDENT"
    CONDITION_BREAKDOWN = "BREAKDOWN"
    CONDITION_OTHER = "OTHER"

class Location:
    """Location Information"""
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: str
    state: Optional[str] = None
    pincode: Optional[str] = None
    landmark: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "city": self.city,
            "state": self.state,
            "pincode": self.pincode,
            "landmark": self.landmark
        }

class JobCalculation:
    """Job Calculation Model"""
    base_fare: float = 200.0
    distance_rate: float = 15.0
    emergency_bonus: float = 100.0
    night_charge: float = 50.0
    waiting_charge: float = 20.0
    
    def calculate_earning(self, distance: float, priority: str = "NORMAL", is_night: bool = False, waiting_time: int = 0) -> float:
        """Calculate total earning for job"""
        total = self.base_fare
        
        # Distance charge
        total += distance * self.distance_rate
        
        # Priority bonus
        if priority == "EMERGENCY":
            total += self.emergency_bonus
        elif priority == "HIGH":
            total += self.emergency_bonus // 2
        
        # Night charge
        if is_night:
            total += self.night_charge
        
        # Waiting charge
        if waiting_time > 0:
            total += waiting_time * self.waiting_charge
        
        return total
    
    def get_breakdown(self, distance: float, priority: str = "NORMAL", is_night: bool = False, waiting_time: int = 0) -> dict:
        """Get earning breakdown"""
        breakdown = {
            "base_fare": self.base_fare,
            "distance_charge": distance * self.distance_rate,
            "priority_bonus": 0,
            "night_charge": 0,
            "waiting_charge": 0,
            "total": 0
        }
        
        # Priority bonus
        if priority == "EMERGENCY":
            breakdown["priority_bonus"] = self.emergency_bonus
        elif priority == "HIGH":
            breakdown["priority_bonus"] = self.emergency_bonus // 2
        
        # Night charge
        if is_night:
            breakdown["night_charge"] = self.night_charge
        
        # Waiting charge
        if waiting_time > 0:
            breakdown["waiting_charge"] = waiting_time * self.waiting_charge
        
        breakdown["total"] = sum(breakdown.values())
        
        return breakdown

# Validation functions
def validate_phone(phone: str) -> bool:
    """Validate phone number"""
    return len(phone) >= 10 and phone.isdigit()

def validate_email(email: str) -> bool:
    """Validate email address"""
    return "@" in email and "." in email

def validate_vehicle_number(vehicle_number: str) -> bool:
    """Validate vehicle number"""
    return len(vehicle_number) >= 6

def validate_capacity(capacity: str) -> bool:
    """Validate vehicle capacity"""
    valid_capacities = ["Small Car", "SUV/Van", "Heavy Vehicle", "Multiple Vehicles"]
    return capacity in valid_capacities

def validate_truck_type(truck_type: str) -> bool:
    """Validate truck type"""
    valid_types = ["Flatbed", "Wheel Lift", "Heavy Duty", "Integrated"]
    return truck_type in valid_types

# Helper functions
def generate_otp() -> str:
    """Generate 4-digit OTP"""
    import random
    return f"{random.randint(1000, 9999)}"

def calculate_distance(pickup: str, drop: str) -> float:
    """Calculate distance between two locations (simplified)"""
    # This is a simplified calculation
    # In production, use Google Maps API or similar
    import random
    return random.uniform(5.0, 25.0)

def format_currency(amount: float) -> str:
    """Format currency amount"""
    return f" {amount:.2f}"

def format_time(time_str: str) -> str:
    """Format time string"""
    try:
        dt = datetime.fromisoformat(time_str)
        return dt.strftime("%I:%M %p, %d %b %Y")
    except:
        return time_str
