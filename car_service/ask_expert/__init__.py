"""
Automobile Expert Module
Complete expert system with authentication, requests, and consultations
"""

from .expert_db import expert_db
from .expert_service import expert_service
from .expert_routes import expert_bp
from .expert_cli import expert_dashboard

__all__ = ['expert_db', 'expert_service', 'expert_bp', 'expert_dashboard']
