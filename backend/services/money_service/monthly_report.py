from datetime import datetime, timedelta
from .uplan_database import UPlanDatabase

class MonthlyReportGenerator:
    def __init__(self):
        self.db = UPlanDatabase()
    
    def generate_monthly_report(self, user_id, month=None, year=None):
        """Generate comprehensive monthly financial report"""
        if not month:
            current_date = datetime.now()
            month = current_date.strftime("%B")
            year = current_date.year
        
        # Get spending data
        spending_data = self.db.get_monthly_spending_data(user_id, month, year)
        
        if not spending_data:
            return None
        
        # Calculate totals and metrics
        total_spending = sum(item['total'] for item in spending_data)
        total_transactions = sum(item['count'] for item in spending_data)
        
        # Get budget data
        budget_data = self.db.get_budget_status(user_id, month, year)
        
        # Calculate daily average
        days_in_month = self._get_days_in_month(month, year)
        daily_average = total_spending / days_in_month
        
        # Find top spending category
        top_category = max(spending_data, key=lambda x: x['total']) if spending_data else None
        
        # Calculate category percentages
        for item in spending_data:
            item['percentage'] = (item['total'] / total_spending * 100) if total_spending > 0 else 0
        
        # Budget performance
        budget_performance = self._calculate_budget_performance(spending_data, budget_data)
        
        return {
            'month': month,
            'year': year,
            'total_spending': total_spending,
            'total_transactions': total_transactions,
            'daily_average': daily_average,
            'days_in_month': days_in_month,
            'spending_breakdown': spending_data,
            'top_category': top_category,
            'budget_performance': budget_performance,
            'insights': self._generate_insights(spending_data, budget_data, total_spending)
        }
    
    def _calculate_budget_performance(self, spending_data, budget_data):
        """Calculate budget performance metrics"""
        if not budget_data:
            return None
        
        performance = []
        total_budget = 0
        total_spent = 0
        
        for budget in budget_data:
            # Find corresponding spending
            spent = next((s['total'] for s in spending_data if s['category'].lower() == budget['category'].lower()), 0)
            
            budget_performance = {
                'category': budget['category'],
                'budget_amount': budget['budget_amount'],
                'spent_amount': spent,
                'remaining': budget['budget_amount'] - spent,
                'percentage_used': (spent / budget['budget_amount'] * 100) if budget['budget_amount'] > 0 else 0,
                'status': self._get_budget_status(spent, budget['budget_amount'])
            }
            
            performance.append(budget_performance)
            total_budget += budget['budget_amount']
            total_spent += spent
        
        # Overall performance
        overall_performance = {
            'total_budget': total_budget,
            'total_spent': total_spent,
            'total_remaining': total_budget - total_spent,
            'overall_percentage': (total_spent / total_budget * 100) if total_budget > 0 else 0,
            'category_performance': performance
        }
        
        return overall_performance
    
    def _get_budget_status(self, spent, budget):
        """Get budget status"""
        if budget <= 0:
            return 'NO_BUDGET'
        
        percentage = (spent / budget) * 100
        
        if percentage >= 100:
            return 'EXCEEDED'
        elif percentage >= 90:
            return 'CRITICAL'
        elif percentage >= 75:
            return 'WARNING'
        elif percentage >= 50:
            return 'MODERATE'
        else:
            return 'GOOD'
    
    def _generate_insights(self, spending_data, budget_data, total_spending):
        """Generate spending insights"""
        insights = []
        
        # Spending concentration
        if spending_data:
            top_percentage = (spending_data[0]['total'] / total_spending) * 100 if total_spending > 0 else 0
            if top_percentage > 40:
                insights.append(f"  High concentration: {spending_data[0]['category']} accounts for {top_percentage:.1f}% of spending")
            elif top_percentage > 25:
                insights.append(f"  Moderate concentration: {spending_data[0]['category']} is {top_percentage:.1f}% of spending")
        
        # Budget performance insights
        if budget_data:
            exceeded_categories = [b for b in budget_data if b['spent'] > b['budget_amount']]
            if exceeded_categories:
                insights.append(f"   {len(exceeded_categories)} category(ies) over budget")
            else:
                insights.append("  All categories within budget")
        
        # Spending level insights
        if total_spending > 0:
            if len(spending_data) >= 5:
                insights.append("  Diverse spending across multiple categories")
            elif len(spending_data) >= 3:
                insights.append("  Moderate spending diversity")
            else:
                insights.append("  Focused spending in few categories")
        
        return insights
    
    def display_monthly_report(self, user_id, month=None, year=None):
        """Display comprehensive monthly report"""
        report = self.generate_monthly_report(user_id, month, year)
        
        if not report:
            print("  No spending data available for the specified period")
            return
        
        print(f"\n" + "="*70)
        print(f"  MONTHLY SPENDING REPORT - {report['month']} {report['year']}")
        print("="*70)
        
        # Summary section
        print(f"\n  EXECUTIVE SUMMARY")
        print("-" * 50)
        print(f"  Total Spending:  {report['total_spending']:,.2f}")
        print(f"  Total Transactions: {report['total_transactions']}")
        print(f"  Daily Average:  {report['daily_average']:,.2f}")
        print(f"  Days in Month: {report['days_in_month']}")
        
        if report['top_category']:
            print(f"  Top Category: {report['top_category']['category']} ( {report['top_category']['total']:,.2f})")
        
        # Category breakdown
        print(f"\n  CATEGORY BREAKDOWN")
        print("-" * 50)
        
        for item in report['spending_breakdown']:
            # Visual bar
            bar_length = 20
            filled_length = int(item['percentage'] / 5)
            bar = ' ' * filled_length + ' ' * (bar_length - filled_length)
            
            print(f"{item['category'].title():15}  {item['total']:8,.2f} ({item['percentage']:5.1f}%) {bar}")
        
        # Budget performance
        if report['budget_performance']:
            print(f"\n  BUDGET PERFORMANCE")
            print("-" * 50)
            
            overall = report['budget_performance']
            print(f"  Overall Budget:  {overall['total_budget']:,.2f}")
            print(f"  Overall Spent:  {overall['total_spent']:,.2f}")
            print(f"  Overall Remaining:  {overall['total_remaining']:,.2f}")
            print(f"  Budget Used: {overall['overall_percentage']:.1f}%")
            
            # Category performance
            print(f"\n  CATEGORY PERFORMANCE")
            print("-" * 30)
            
            for cat_perf in overall['category_performance']:
                status_icon = self._get_status_icon(cat_perf['status'])
                print(f"{status_icon} {cat_perf['category'].title():12}  {cat_perf['spent_amount']:7,.2f} /  {cat_perf['budget_amount']:7,.2f} ({cat_perf['percentage_used']:5.1f}%)")
        
        # Insights
        if report['insights']:
            print(f"\n  SPENDING INSIGHTS")
            print("-" * 50)
            for insight in report['insights']:
                print(f"   {insight}")
        
        # Recommendations
        recommendations = self._generate_recommendations(report)
        if recommendations:
            print(f"\n  RECOMMENDATIONS")
            print("-" * 50)
            for rec in recommendations:
                print(f"   {rec}")
    
    def _get_status_icon(self, status):
        """Get status icon for budget performance"""
        icons = {
            'EXCEEDED': ' ',
            'CRITICAL': ' ',
            'WARNING': ' ',
            'MODERATE': ' ',
            'GOOD': ' ',
            'NO_BUDGET': ' '
        }
        return icons.get(status, ' ')
    
    def _generate_recommendations(self, report):
        """Generate personalized recommendations"""
        recommendations = []
        
        # Budget-based recommendations
        if report['budget_performance']:
            exceeded = [c for c in report['budget_performance']['category_performance'] if c['status'] == 'EXCEEDED']
            if exceeded:
                recommendations.append(f"  Review spending in {', '.join([c['category'] for c in exceeded])}")
            
            critical = [c for c in report['budget_performance']['category_performance'] if c['status'] == 'CRITICAL']
            if critical:
                recommendations.append(f"   Monitor {', '.join([c['category'] for c in critical])} closely")
        
        # Spending pattern recommendations
        if report['top_category']:
            top_percentage = (report['top_category']['total'] / report['total_spending']) * 100
            if top_percentage > 40:
                recommendations.append(f"  Consider diversifying spending away from {report['top_category']['category']}")
        
        # Daily average recommendations
        if report['daily_average'] > 1000:
            recommendations.append("  Consider setting daily spending limits")
        
        return recommendations
    
    def _get_days_in_month(self, month, year):
        """Get number of days in a month"""
        if isinstance(month, str):
            month_names = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            month = month_names.get(month, 1)
        
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        else:  # February
            return 29 if (year % 400 == 0 or (year % 100 != 0 and year % 4 == 0)) else 28
