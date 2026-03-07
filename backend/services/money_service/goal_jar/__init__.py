"""
Smart Goal Jar Module

A comprehensive goal-based savings system that helps users:
- Set and track multiple financial goals
- Automate savings from leftover budgets
- Simulate different saving scenarios
- Get intelligent acceleration suggestions
- Schedule notifications and reminders
- Project long-term savings growth

Integration Features:
- Finny transaction tracking for automatic savings
- Smart Budget Planner for leftover transfers
- AI Financial Coach for personalized advice
- Email notifications for goal deadlines
"""

from .goal_engine import GoalEngine
from .goal_simulator import GoalSimulator
from .goal_progress import GoalProgress
from .smart_goal_jar import SmartG
from .goal_api import GoalAPI, create_goal_api

__all__ = [
    'GoalEngine',
    'GoalSimulator', 
    'GoalProgress',
    'SmartG',
    'GoalAPI',
    'create_goal_api'
]

__version__ = '1.0.0'
__description__ = 'Smart Goal Jar - Intelligent goal-based savings system with automation and notifications'
