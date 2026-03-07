from datetime import datetime
from .smart_budget_planner import SmartBudgetPlanner

class BudgetPlanner:
    def __init__(self):
        self.smart_planner = SmartBudgetPlanner()
    
    def show_menu(self, user_id):
        """Main menu for Budget Planner - now uses Smart Budget Planner"""
        self.smart_planner.show_menu(user_id)
