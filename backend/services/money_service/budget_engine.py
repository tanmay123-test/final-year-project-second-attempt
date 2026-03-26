from datetime import datetime, timedelta
from .uplan_database import UPlanDatabase

class BudgetEngine:
    def __init__(self):
        self.db = UPlanDatabase()
    
    def get_budget_status(self, user_id):
        """Get comprehensive budget status"""
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year
        
        budgets = self.db.get_budget_status(user_id, month, year)
        
        if not budgets:
            return None
        
        # Calculate additional metrics
        days_passed = current_date.day
        days_in_month = self._get_days_in_month(current_date.month, current_date.year)
        
        for budget in budgets:
            # Calculate percentage used
            budget['percentage_used'] = (budget['spent'] / budget['budget_amount'] * 100) if budget['budget_amount'] > 0 else 0
            
            # Calculate daily spending rate
            budget['daily_average'] = budget['spent'] / days_passed if days_passed > 0 else 0
            
            # Calculate recommended daily spending
            remaining_days = days_in_month - days_passed
            budget['recommended_daily'] = budget['remaining'] / remaining_days if remaining_days > 0 else 0
            
            # Add status indicator
            if budget['percentage_used'] >= 100:
                budget['status'] = 'EXCEEDED'
                budget['status_color'] = ' '
            elif budget['percentage_used'] >= 90:
                budget['status'] = 'CRITICAL'
                budget['status_color'] = ' '
            elif budget['percentage_used'] >= 75:
                budget['status'] = 'WARNING'
                budget['status_color'] = ' '
            else:
                budget['status'] = 'SAFE'
                budget['status_color'] = ' '
        
        return {
            'budgets': budgets,
            'days_passed': days_passed,
            'days_in_month': days_in_month,
            'month': month,
            'year': year
        }
    
    def update_budget_from_transaction(self, user_id, category, amount):
        """Update budget tracking when transaction is recorded"""
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year
        
        # Get current spending for this category
        budgets = self.db.get_budget_status(user_id, month, year)
        current_budget = next((b for b in budgets if b['category'].lower() == category.lower()), None)
        
        if current_budget:
            new_spent = current_budget['spent'] + amount
            remaining = current_budget['remaining'] - amount
            
            self.db.update_budget_tracking(user_id, category, new_spent, month, year)
            
            # Check for alerts
            alerts = self._check_budget_alerts(current_budget, new_spent, remaining)
            return alerts
        
        return []
    
    def _check_budget_alerts(self, budget, new_spent, remaining):
        """Check for budget alerts"""
        alerts = []
        percentage = (new_spent / budget['budget_amount']) * 100 if budget['budget_amount'] > 0 else 0
        
        if percentage >= 100:
            alerts.append({
                'type': 'EXCEEDED',
                'message': f"  {budget['category']} budget exceeded by  {abs(remaining):.2f}!",
                'severity': 'HIGH'
            })
        elif percentage >= 90:
            alerts.append({
                'type': 'CRITICAL',
                'message': f"   {budget['category']} budget at {percentage:.1f}% - only  {remaining:.2f} remaining!",
                'severity': 'MEDIUM'
            })
        elif percentage >= 75:
            alerts.append({
                'type': 'WARNING',
                'message': f"  {budget['category']} budget at {percentage:.1f}%",
                'severity': 'LOW'
            })
        
        return alerts
    
    def get_dynamic_budget_adjustment(self, user_id):
        """Calculate recommended daily spending based on remaining budget"""
        budget_status = self.get_budget_status(user_id)
        
        if not budget_status:
            return None
        
        adjustments = []
        current_date = datetime.now()
        remaining_days = budget_status['days_in_month'] - current_date.day
        
        for budget in budget_status['budgets']:
            if budget['remaining'] > 0 and remaining_days > 0:
                daily_limit = budget['remaining'] / remaining_days
                
                adjustment = {
                    'category': budget['category'],
                    'remaining_budget': budget['remaining'],
                    'remaining_days': remaining_days,
                    'recommended_daily': daily_limit,
                    'message': f"You should spend no more than  {daily_limit:.2f} per day to stay within your {budget['category']} budget."
                }
                adjustments.append(adjustment)
        
        return adjustments
    
    def _get_days_in_month(self, month, year):
        """Get number of days in a month"""
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        else:  # February
            return 29 if (year % 400 == 0 or (year % 100 != 0 and year % 4 == 0)) else 28
    
    def display_budget_status(self, user_id):
        """Display comprehensive budget status"""
        budget_status = self.get_budget_status(user_id)
        
        if not budget_status:
            print("  No budgets set. Create a financial plan first!")
            return
        
        print(f"\n" + "="*70)
        print(f"  BUDGET STATUS - {budget_status['month']} {budget_status['year']}")
        print("="*70)
        print(f"  Day {budget_status['days_passed']} of {budget_status['days_in_month']}")
        
        for budget in budget_status['budgets']:
            print(f"\n  {budget['category'].upper()}")
            print("-" * 40)
            print(f"  Budget:  {budget['budget_amount']:,.2f}")
            print(f"  Spent:  {budget['spent']:,.2f}")
            print(f"  Remaining:  {budget['remaining']:,.2f}")
            print(f"  Used: {budget['percentage_used']:.1f}%")
            
            # Progress bar
            bar_length = 20
            filled_length = min(int(budget['percentage_used'] / 5), bar_length)
            
            if budget['status'] == 'EXCEEDED':
                bar = ' ' * bar_length
            elif budget['status'] == 'CRITICAL':
                bar = ' ' * filled_length + ' ' * (bar_length - filled_length)
            elif budget['status'] == 'WARNING':
                bar = ' ' * filled_length + ' ' * (bar_length - filled_length)
            else:
                bar = ' ' * filled_length + ' ' * (bar_length - filled_length)
            
            print(f"   {bar} {budget['status_color']} {budget['status']}")
            
            # Daily metrics
            print(f"  Daily Average:  {budget['daily_average']:,.2f}")
            if budget['recommended_daily'] > 0:
                print(f"  Recommended Daily:  {budget['recommended_daily']:,.2f}")
    
    def display_dynamic_adjustments(self, user_id):
        """Display dynamic budget adjustments"""
        adjustments = self.get_dynamic_budget_adjustment(user_id)
        
        if not adjustments:
            print("  No budget adjustments available")
            return
        
        print(f"\n" + "="*70)
        print("  DYNAMIC BUDGET ADJUSTMENTS")
        print("="*70)
        
        for adj in adjustments:
            print(f"\n  {adj['category'].upper()}")
            print("-" * 40)
            print(f"  Remaining Budget:  {adj['remaining_budget']:,.2f}")
            print(f"  Remaining Days: {adj['remaining_days']}")
            print(f"  Recommended Daily:  {adj['recommended_daily']:,.2f}")
            print(f"  {adj['message']}")
    
    def integrate_with_finny_transaction(self, user_id, transaction_data):
        """Integrate with Finny transaction system"""
        category = transaction_data.get('category', '')
        amount = transaction_data.get('amount', 0)
        
        if category and amount > 0:
            alerts = self.update_budget_from_transaction(user_id, category, amount)
            
            if alerts:
                print("\n" + "="*50)
                print("  BUDGET ALERTS")
                print("="*50)
                for alert in alerts:
                    print(f"{alert['message']}")
                print("="*50)
            
            return alerts
        
        return []
