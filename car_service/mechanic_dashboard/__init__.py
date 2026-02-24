"""
Mechanic Dashboard Module
Complete mechanic worker management system
"""

from .mechanic_dashboard_db import mechanic_dashboard_db
from .mechanic_dashboard_service import mechanic_dashboard_service
from .mechanic_dashboard_routes import mechanic_dashboard_bp

__all__ = [
    'mechanic_dashboard_db',
    'mechanic_dashboard_service', 
    'mechanic_dashboard_bp'
]
