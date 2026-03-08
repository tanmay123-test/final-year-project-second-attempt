"""
AI Groups Module
Phase 1: AI Groups Core Infrastructure

This module provides intelligent group management and chat functionality
with AI assistant integration for collaborative discussions.

Features:
- Group creation and management
- Member role management
- Real-time messaging
- AI assistant integration (Phase 2)
- System insights and analytics (Phase 2)
"""

from .ai_groups_engine import AIGroupsEngine
from .ai_groups_api import AIGroupsAPI
from .ai_groups_service import AIGroupsService
from .smart_ai_groups import SmartAIGroups

__all__ = [
    'AIGroupsEngine',
    'AIGroupsAPI', 
    'AIGroupsService',
    'SmartAIGroups'
]

__version__ = '1.0.0'
__description__ = 'AI Groups - Intelligent group management and collaboration system'
