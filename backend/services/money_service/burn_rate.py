from datetime import datetime, timedelta
from .uplan_database import UPlanDatabase

class BurnRateIndicator:
    def __init__(self):
        self.db = UPlanDatabase()
    
    def calculate_burn_rate(self, user_id):
        """Calculate comprehensive burn rate analysis"""
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year
        
        days_passed = current_date.day
        days_in_month = self._get_days_in_month(current_date.month, current_date.year)
        
        # Get budget status
        budgets = self.db.get_budget_status(user_id, month, year)
        
        if not budgets:
            return None
        
        burn_analysis = []
        
        for budget in budgets:
            # Calculate expected spending
            expected_spending = budget['budget_amount'] * (days_passed / days_in_month)
            
            # Calculate actual spending
            actual_spending = budget['spent']
            
            # Calculate burn rate
            if expected_spending > 0:
                burn_rate = (actual_spending / expected_spending) * 100
            else:
                burn_rate = 100 if actual_spending > 0 else 0
            
            # Predict end-of-month spending
            if days_passed > 0:
                daily_rate = actual_spending / days_passed
                predicted_spending = daily_rate * days_in_month
            else:
                predicted_spending = 0
            
            # Calculate variance
            variance = predicted_spending - budget['budget_amount']
            variance_percentage = (variance / budget['budget_amount'] * 100) if budget['budget_amount'] > 0 else 0
            
            burn_data = {
                'category': budget['category'],
                'budget_amount': budget['budget_amount'],
                'actual_spending': actual_spending,
                'expected_spending': expected_spending,
                'burn_rate': burn_rate,
                'predicted_spending': predicted_spending,
                'variance': variance,
                'variance_percentage': variance_percentage,
                'days_passed': days_passed,
                'days_in_month': days_in_month
            }
            
            # Add burn status
            if burn_rate >= 120:
                burn_data['status'] = 'CRITICAL'
                burn_data['status_color'] = '🔴'
                burn_data['alert'] = '🚨 Critical burn rate! You\'re spending much faster than planned.'
            elif burn_rate >= 110:
                burn_data['status'] = 'HIGH'
                burn_data['status_color'] = '🟡'
                burn_data['alert'] = '⚠️ High burn rate! You may exceed your budget.'
            elif burn_rate >= 90:
                burn_data['status'] = 'NORMAL'
                burn_data['status_color'] = '🟢'
                burn_data['alert'] = '✅ Normal spending rate.'
            else:
                burn_data['status'] = 'LOW'
                burn_data['status_color'] = '🔵'
                burn_data['alert'] = '💡 Low spending rate - great job staying under budget!'
            
            burn_analysis.append(burn_data)
        
        return {
            'burn_analysis': burn_analysis,
            'days_passed': days_passed,
            'days_in_month': days_in_month,
            'month': month,
            'year': year
        }
    
    def get_overall_burn_rate(self, user_id):
        """Get overall burn rate across all categories"""
        burn_data = self.calculate_burn_rate(user_id)
        
        if not burn_data:
            return None
        
        total_budget = sum(b['budget_amount'] for b in burn_data['burn_analysis'])
        total_spent = sum(b['actual_spending'] for b in burn_data['burn_analysis'])
        total_expected = sum(b['expected_spending'] for b in burn_data['burn_analysis'])
        
        # Overall burn rate
        if total_expected > 0:
            overall_burn_rate = (total_spent / total_expected) * 100
        else:
            overall_burn_rate = 100 if total_spent > 0 else 0
        
        # Overall prediction
        days_passed = burn_data['days_passed']
        days_in_month = burn_data['days_in_month']
        
        if days_passed > 0:
            daily_rate = total_spent / days_passed
            overall_predicted = daily_rate * days_in_month
        else:
            overall_predicted = 0
        
        overall_variance = overall_predicted - total_budget
        overall_variance_percentage = (overall_variance / total_budget * 100) if total_budget > 0 else 0
        
        # Determine overall status
        if overall_burn_rate >= 120:
            overall_status = 'CRITICAL'
            overall_color = '🔴'
            overall_message = '🚨 Critical! You\'re burning through your budget very quickly!'
        elif overall_burn_rate >= 110:
            overall_status = 'HIGH'
            overall_color = '🟡'
            overall_message = '⚠️ High burn rate! Consider reducing spending.'
        elif overall_burn_rate >= 90:
            overall_status = 'NORMAL'
            overall_color = '🟢'
            overall_message = '✅ Good spending pace - keep it up!'
        else:
            overall_status = 'LOW'
            overall_color = '🔵'
            overall_message = '💡 Excellent! You\'re spending slower than planned.'
        
        return {
            'total_budget': total_budget,
            'total_spent': total_spent,
            'total_expected': total_expected,
            'overall_burn_rate': overall_burn_rate,
            'overall_predicted': overall_predicted,
            'overall_variance': overall_variance,
            'overall_variance_percentage': overall_variance_percentage,
            'overall_status': overall_status,
            'overall_color': overall_color,
            'overall_message': overall_message,
            'days_passed': days_passed,
            'days_in_month': days_in_month,
            'month': burn_data['month'],
            'year': burn_data['year']
        }
    
    def display_burn_rate_analysis(self, user_id):
        """Display comprehensive burn rate analysis"""
        burn_data = self.calculate_burn_rate(user_id)
        
        if not burn_data:
            print("📭 No budget data available for burn rate analysis")
            return
        
        print(f"\n" + "="*70)
        print(f"🔥 BURN RATE ANALYSIS - {burn_data['month']} {burn_data['year']}")
        print("="*70)
        print(f"📅 Progress: Day {burn_data['days_passed']} of {burn_data['days_in_month']}")
        
        for category in burn_data['burn_analysis']:
            print(f"\n📂 {category['category'].upper()}")
            print("-" * 50)
            print(f"💰 Budget: ₹{category['budget_amount']:,.2f}")
            print(f"💸 Spent: ₹{category['actual_spending']:,.2f}")
            print(f"📊 Expected: ₹{category['expected_spending']:,.2f}")
            print(f"🔥 Burn Rate: {category['burn_rate']:.1f}%")
            print(f"🔮 Predicted: ₹{category['predicted_spending']:,.2f}")
            
            # Burn rate visual
            burn_percentage = min(category['burn_rate'] / 2, 100)  # Scale to 100%
            bar_length = 20
            filled_length = int(burn_percentage / 5)
            
            if category['status'] == 'CRITICAL':
                bar = '🔴' * filled_length + '⚪' * (bar_length - filled_length)
            elif category['status'] == 'HIGH':
                bar = '🟡' * filled_length + '⚪' * (bar_length - filled_length)
            elif category['status'] == 'NORMAL':
                bar = '🟢' * filled_length + '⚪' * (bar_length - filled_length)
            else:
                bar = '🔵' * filled_length + '⚪' * (bar_length - filled_length)
            
            print(f"   {bar} {category['status_color']} {category['burn_rate']:.1f}%")
            
            # Variance
            if category['variance'] > 0:
                print(f"📈 Over Budget: ₹{category['variance']:,.2f} (+{category['variance_percentage']:.1f}%)")
            elif category['variance'] < 0:
                print(f"📉 Under Budget: ₹{abs(category['variance']):,.2f} ({category['variance_percentage']:.1f}%)")
            else:
                print(f"📊 On Track: No variance")
            
            print(f"💡 {category['alert']}")
        
        # Overall summary
        overall = self.get_overall_burn_rate(user_id)
        if overall:
            print(f"\n" + "="*70)
            print("📊 OVERALL BURN RATE SUMMARY")
            print("="*70)
            print(f"💰 Total Budget: ₹{overall['total_budget']:,.2f}")
            print(f"💸 Total Spent: ₹{overall['total_spent']:,.2f}")
            print(f"🔥 Overall Burn Rate: {overall['overall_burn_rate']:.1f}%")
            print(f"🔮 Predicted Total: ₹{overall['overall_predicted']:,.2f}")
            
            # Overall burn rate visual
            overall_percentage = min(overall['overall_burn_rate'] / 2, 100)
            bar_length = 30
            filled_length = int(overall_percentage / 3.33)
            
            if overall['overall_status'] == 'CRITICAL':
                bar = '🔴' * filled_length + '⚪' * (bar_length - filled_length)
            elif overall['overall_status'] == 'HIGH':
                bar = '🟡' * filled_length + '⚪' * (bar_length - filled_length)
            elif overall['overall_status'] == 'NORMAL':
                bar = '🟢' * filled_length + '⚪' * (bar_length - filled_length)
            else:
                bar = '🔵' * filled_length + '⚪' * (bar_length - filled_length)
            
            print(f"   {bar}")
            print(f"   {overall['overall_color']} {overall['overall_burn_rate']:.1f}% - {overall['overall_status']}")
            
            if overall['overall_variance'] > 0:
                print(f"📈 Projected Over Budget: ₹{overall['overall_variance']:,.2f}")
            elif overall['overall_variance'] < 0:
                print(f"📉 Projected Under Budget: ₹{abs(overall['overall_variance']):,.2f}")
            
            print(f"\n💡 {overall['overall_message']}")
    
    def _get_days_in_month(self, month, year):
        """Get number of days in a month"""
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        else:  # February
            return 29 if (year % 400 == 0 or (year % 100 != 0 and year % 4 == 0)) else 28
