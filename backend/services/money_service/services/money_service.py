from ..models.money_model import MoneyModel
from datetime import datetime, timedelta
import json

class MoneyService:
    def __init__(self):
        self.model = MoneyModel()
    
    def get_dashboard_data(self, user_id):
        """Get dashboard data including spending summary and recent transactions"""
        try:
            # Ensure user exists in money service database
            self.model._ensure_user_exists(user_id)
            
            # Get monthly spending data
            current_month = datetime.now().strftime('%Y-%m')
            monthly_data = self.model.get_monthly_spending(user_id, current_month)
            
            # Calculate total spending
            total_spending = sum(item['amount'] for item in monthly_data)
            
            # Get recent transactions
            recent_transactions = self.model.get_recent_transactions(user_id, limit=5)
            
            # Get budget status
            budgets = self.model.get_active_budgets(user_id)
            
            # Get goals progress
            goals = self.model.get_active_goals(user_id)
            
            return {
                'total_spending': total_spending,
                'categories': monthly_data,
                'recent_transactions': recent_transactions,
                'budgets': budgets,
                'goals': goals,
                'month': current_month
            }
        except Exception as e:
            raise Exception(f"Failed to get dashboard data: {str(e)}")
    
    def add_transaction(self, user_id, category, amount, description, date, transaction_type='expense', merchant=''):
        """Add a new transaction"""
        try:
            # Validate amount
            if amount <= 0:
                raise Exception("Amount must be positive")
            
            # Parse date
            if isinstance(date, str):
                transaction_date = datetime.strptime(date, '%Y-%m-%d')
            else:
                transaction_date = date
            
            # Add transaction
            transaction_id = self.model.add_transaction(
                user_id=user_id,
                category=category,
                amount=amount,
                description=description,
                date=transaction_date,
                type=transaction_type,
                merchant=merchant
            )
            
            # Check budget alerts
            self._check_budget_alerts(user_id, category, amount)
            
            return transaction_id
        except Exception as e:
            raise Exception(f"Failed to add transaction: {str(e)}")
    
    def get_transactions(self, user_id, limit=None, category=None, start_date=None, end_date=None):
        """Get user transactions with optional filters"""
        try:
            transactions = self.model.get_transactions(
                user_id=user_id,
                limit=limit,
                category=category,
                start_date=start_date,
                end_date=end_date
            )
            return transactions
        except Exception as e:
            raise Exception(f"Failed to get transactions: {str(e)}")
    
    def set_budget(self, user_id, category, amount, period='monthly'):
        """Set a budget for a category"""
        try:
            # Validate amount
            if amount <= 0:
                raise Exception("Budget amount must be positive")
            
            budget_id = self.model.set_budget(
                user_id=user_id,
                category=category,
                amount=amount,
                period=period
            )
            return budget_id
        except Exception as e:
            raise Exception(f"Failed to set budget: {str(e)}")
    
    def get_budgets(self, user_id):
        """Get user budgets"""
        try:
            budgets = self.model.get_budgets(user_id)
            return budgets
        except Exception as e:
            raise Exception(f"Failed to get budgets: {str(e)}")
    
    def create_goal(self, user_id, name, target_amount, current_amount=0, deadline=None, category=None):
        """Create a savings goal"""
        try:
            # Validate amounts
            if target_amount <= 0:
                raise Exception("Target amount must be positive")
            if current_amount < 0:
                raise Exception("Current amount cannot be negative")
            if current_amount > target_amount:
                raise Exception("Current amount cannot exceed target amount")
            
            # Parse deadline
            if isinstance(deadline, str):
                deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
            else:
                deadline_date = deadline
            
            goal_id = self.model.create_goal(
                user_id=user_id,
                name=name,
                target_amount=target_amount,
                current_amount=current_amount,
                deadline=deadline_date,
                category=category
            )
            return goal_id
        except Exception as e:
            raise Exception(f"Failed to create goal: {str(e)}")
    
    def get_goals(self, user_id):
        """Get user goals"""
        try:
            goals = self.model.get_goals(user_id)
            return goals
        except Exception as e:
            raise Exception(f"Failed to get goals: {str(e)}")
    
    def get_monthly_analytics(self, user_id, months=6):
        """Get monthly analytics for the past months"""
        try:
            analytics = self.model.get_monthly_analytics(user_id, months)
            return analytics
        except Exception as e:
            raise Exception(f"Failed to get monthly analytics: {str(e)}")
    
    def chat_with_ai(self, user_id, message):
        """Chat with AI financial assistant"""
        try:
            # Get user context
            user_data = self.model.get_user_financial_summary(user_id)
            
            # Simple AI response for now
            response = f"I understand you're asking about: {message}. Based on your financial data, I can help you track expenses and manage your budget."
            
            return response
        except Exception as e:
            raise Exception(f"Failed to process AI chat: {str(e)}")
    
    def _check_budget_alerts(self, user_id, category, amount):
        """Check if transaction exceeds budget and send alerts"""
        try:
            budget = self.model.get_budget_for_category(user_id, category)
            if budget:
                current_spending = self.model.get_category_spending(user_id, category, budget['period'])
                remaining = budget['amount'] - current_spending - amount
                
                if remaining <= 0:
                    # Budget exceeded
                    self._send_alert(user_id, f"Budget exceeded for {category}! You've spent {current_spending + amount} out of {budget['amount']}")
                elif remaining <= budget['amount'] * 0.1:  # 90% used
                    # Budget warning
                    self._send_alert(user_id, f"Budget warning for {category}! Only {remaining:.2f} remaining out of {budget['amount']}")
        except Exception as e:
            print(f"Failed to check budget alerts: {str(e)}")
    
    def _send_alert(self, user_id, message):
        """Send alert to user (implementation depends on notification system)"""
        # This would integrate with your notification service
        print(f"Alert for user {user_id}: {message}")
        # TODO: Implement actual notification sending

# Create singleton instance
money_service = MoneyService()
