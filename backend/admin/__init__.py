"""
Admin module for ExpertEase backend.
Provides administrative APIs for managing users, workers, appointments, and platform settings.
"""

from .admin_routes import admin_bp

__all__ = ['admin_bp']
