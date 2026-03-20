from datetime import datetime, timedelta
from .advanced_finny_db import AdvancedFinnyDB

class AdvancedAnalytics:
    def __init__(self):
        self.db = AdvancedFinnyDB()
    
    def get_comprehensive_dashboard(self, user_id):
        """Get complete analytics dashboard"""
        current_date = datetime.now()
        month_name = current_date.strftime("%B")
        month_num = current_date.month
        year = current_date.year
        
        dashboard = {
            'daily_summary': self.get_daily_summary(user_id),
            'weekly_summary': self.get_weekly_summary(user_id, year, month_num),
            'monthly_summary': self.get_monthly_summary(user_id, month_num, year),
            'budget_alerts': self.get_budget_alerts(user_id, month_name, year),
            'top_merchants': self.get_top_merchants_analysis(user_id, month_num, year),
            'spending_predictions': self.get_spending_predictions(user_id, month_name, year),
            'spending_spikes': self.get_spending_spikes(user_id, month_num, year),
            'financial_health_score': self.get_financial_health_analysis(user_id, month_name, year)
        }
        
        return dashboard
    
    def get_daily_summary(self, user_id):
        """Get today's spending summary"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT category, SUM(amount) as total, COUNT(*) as count
        FROM transactions 
        WHERE user_id=? AND date=?
        GROUP BY category
        ORDER BY total DESC
        """, (user_id, today))
        
        daily_transactions = cursor.fetchall()
        
        total_spent = sum(trans[1] for trans in daily_transactions)
        
        return {
            'date': today,
            'total_spent': total_spent,
            'transaction_count': sum(trans[2] for trans in daily_transactions),
            'category_breakdown': daily_transactions
        }
    
    def get_weekly_summary(self, user_id, year, month):
        """Get weekly spending analysis"""
        weekly_data = self.db.get_weekly_spending(user_id, year, month)
        
        # Calculate trends
        if len(weekly_data) > 1:
            totals = [w['total'] for w in weekly_data]
            week_over_week_changes = []
            
            for i in range(1, len(totals)):
                if totals[i-1] > 0:
                    change = ((totals[i] - totals[i-1]) / totals[i-1]) * 100
                else:
                    change = 100 if totals[i] > 0 else 0
                week_over_week_changes.append(change)
        else:
            week_over_week_changes = []
        
        return {
            'weekly_data': weekly_data,
            'week_over_week_changes': week_over_week_changes,
            'trend_insights': self.generate_weekly_trend_insights(weekly_data, week_over_week_changes)
        }
    
    def generate_weekly_trend_insights(self, weekly_data, changes):
        """Generate insights from weekly spending patterns"""
        insights = []
        
        if len(weekly_data) >= 2:
            # Check overall trend
            totals = [w['total'] for w in weekly_data]
            if len(totals) >= 3:
                recent_avg = sum(totals[-2:]) / 2
                earlier_avg = sum(totals[:-2]) / (len(totals) - 2) if len(totals) > 2 else totals[0]
                
                if recent_avg > earlier_avg * 1.2:
                    insights.append("📈 Spending increased in recent weeks")
                elif recent_avg < earlier_avg * 0.8:
                    insights.append("📉 Spending decreased in recent weeks")
                else:
                    insights.append("➡️ Spending stable across weeks")
            
            # Check for volatility
            if changes and max(abs(c) for c in changes) > 50:
                insights.append("⚡ High spending volatility detected")
        
        return insights
    
    def get_monthly_summary(self, user_id, month, year):
        """Get detailed monthly summary"""
        cursor = self.db.conn.cursor()
        
        # Category totals
        cursor.execute("""
        SELECT category, SUM(amount) as total, COUNT(*) as count
        FROM transactions 
        WHERE user_id=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
        GROUP BY category
        ORDER BY total DESC
        """, (user_id, f"{month:02d}", str(year)))
        
        category_data = cursor.fetchall()
        
        total_spent = sum(cat[1] for cat in category_data)
        
        # Daily average
        days_in_month = 31 if month in [1,3,5,7,8,10,12] else (30 if month != 2 else 28)
        current_day = datetime.now().day
        daily_average = total_spent / current_day if current_day > 0 else 0
        
        return {
            'month': month,
            'year': year,
            'total_spent': total_spent,
            'transaction_count': sum(cat[2] for cat in category_data),
            'daily_average': daily_average,
            'category_breakdown': category_data,
            'predicted_monthly': daily_average * days_in_month
        }
    
    def get_budget_alerts(self, user_id, month, year):
        """Get budget status alerts"""
        budgets = self.db.get_monthly_budgets(user_id, month, year)
        alerts = []
        
        for category, budget_amount in budgets:
            budget_amount, current_spending, percentage = self.db.get_budget_status(user_id, category, month, year)
            
            if percentage >= 90:
                alerts.append({
                    'level': 'CRITICAL',
                    'category': category,
                    'message': f"🚨 {category.title()} spending has reached {percentage:.1f}% of budget!",
                    'budget': budget_amount,
                    'spent': current_spending,
                    'remaining': budget_amount - current_spending
                })
            elif percentage >= 75:
                alerts.append({
                    'level': 'WARNING',
                    'category': category,
                    'message': f"⚠️ {category.title()} spending has reached {percentage:.1f}% of budget.",
                    'budget': budget_amount,
                    'spent': current_spending,
                    'remaining': budget_amount - current_spending
                })
            elif percentage >= 100:
                alerts.append({
                    'level': 'EXCEEDED',
                    'category': category,
                    'message': f"💸 {category.title()} budget exceeded by {percentage - 100:.1f}%!",
                    'budget': budget_amount,
                    'spent': current_spending,
                    'remaining': budget_amount - current_spending
                })
        
        return alerts
    
    def get_top_merchants_analysis(self, user_id, month_num, year):
        """Get top merchants analysis"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT merchant, SUM(amount) as total, COUNT(*) as count
        FROM transactions 
        WHERE user_id=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
        GROUP BY merchant
        ORDER BY total DESC
        LIMIT 10
        """, (user_id, f"{month_num:02d}", str(year)))
        
        top_merchants = cursor.fetchall()
        
        # Get top merchant
        top_merchant = top_merchants[0] if top_merchants else (None, 0, 0)
        
        return {
            'top_merchant': {
                'name': top_merchant[0],
                'amount': top_merchant[1],
                'transactions': top_merchant[2]
            },
            'top_10': top_merchants,
            'insights': self.generate_merchant_insights(top_merchants)
        }
    
    def generate_merchant_insights(self, merchants):
        """Generate insights from merchant data"""
        insights = []
        
        if not merchants:
            return insights
        
        # Check concentration
        top_merchant_amount = merchants[0][1]
        total_amount = sum(m[1] for m in merchants)
        concentration = (top_merchant_amount / total_amount) * 100 if total_amount > 0 else 0
        
        if concentration > 50:
            insights.append(f"🎯 High concentration: {merchants[0][0]} accounts for {concentration:.1f}% of spending")
        
        # Check frequency
        if len(merchants) > 0 and merchants[0][2] > 10:
            insights.append(f"🔄 Frequent visits: {merchants[0][0]} visited {merchants[0][2]} times")
        
        return insights
    
    def get_spending_predictions(self, user_id, month_name, year):
        """Get spending predictions for all categories"""
        # Convert month name to month number
        month_num = datetime.strptime(month_name, "%B").month
        
        cursor = self.db.conn.cursor()
        
        cursor.execute("""
        SELECT DISTINCT category FROM transactions 
        WHERE user_id=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
        """, (user_id, f"{month_num:02d}", str(year)))
        
        categories = [row[0] for row in cursor.fetchall()]
        predictions = []
        
        for category in categories:
            current_spending, predicted_spending = self.db.predict_monthly_spending(user_id, category, month_num, year)
            
            predictions.append({
                'category': category,
                'current_spending': current_spending,
                'predicted_spending': predicted_spending,
                'remaining_predicted': predicted_spending - current_spending
            })
        
        return predictions
    
    def get_spending_spikes(self, user_id, month, year):
        """Detect spending spikes compared to previous month"""
        cursor = self.db.conn.cursor()
        
        cursor.execute("""
        SELECT DISTINCT category FROM transactions 
        WHERE user_id=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
        """, (user_id, f"{month:02d}", str(year)))
        
        categories = [row[0] for row in cursor.fetchall()]
        spikes = []
        
        for category in categories:
            prev_spending, current_spending, change_percent = self.db.get_month_comparison(
                user_id, category, month, year
            )
            
            if abs(change_percent) > 50:  # Significant change threshold
                direction = "📈 increased" if change_percent > 0 else "📉 decreased"
                spikes.append({
                    'category': category,
                    'previous_month': prev_spending,
                    'current_month': current_spending,
                    'change_percent': change_percent,
                    'insight': f"{category.title()} spending {direction} by {abs(change_percent):.1f}%"
                })
        
        return spikes
    
    def get_financial_health_analysis(self, user_id, month, year):
        """Get comprehensive financial health analysis"""
        overall_score, budget_adherence, spending_stability, category_balance = \
            self.db.calculate_financial_health_score(user_id, month, year)
        
        # Generate insights based on score
        insights = []
        
        if overall_score >= 80:
            insights.append("🎉 Excellent financial health!")
        elif overall_score >= 60:
            insights.append("💪 Good financial management")
        elif overall_score >= 40:
            insights.append("⚠️ Room for improvement")
        else:
            insights.append("🚨 Financial health needs attention")
        
        # Component insights
        if budget_adherence >= 80:
            insights.append("✅ Great budget adherence")
        elif budget_adherence >= 60:
            insights.append("📊 Budget adherence is good")
        else:
            insights.append("💸 Budget adherence needs improvement")
        
        if spending_stability >= 80:
            insights.append("📈 Stable spending patterns")
        elif spending_stability >= 60:
            insights.append("⚡ Spending patterns are moderate")
        else:
            insights.append("🎢 Spending patterns are volatile")
        
        if category_balance >= 80:
            insights.append("⚖️ Well-balanced spending")
        elif category_balance >= 60:
            insights.append("📊 Category balance is moderate")
        else:
            insights.append("🎯 Spending is concentrated in few categories")
        
        return {
            'overall_score': overall_score,
            'components': {
                'budget_adherence': budget_adherence,
                'spending_stability': spending_stability,
                'category_balance': category_balance
            },
            'insights': insights,
            'grade': self.get_score_grade(overall_score)
        }
    
    def get_score_grade(self, score):
        """Get letter grade for score"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def check_duplicate_transaction(self, user_id, amount, category, merchant, date):
        """Check for duplicate transaction"""
        duplicate_id = self.db.detect_duplicate_transaction(user_id, amount, category, merchant, date)
        return duplicate_id is not None
    
    def learn_merchant_category(self, merchant, category):
        """Learn merchant-category mapping"""
        self.db.learn_merchant_category(merchant, category)
    
    def get_suggested_category(self, merchant):
        """Get suggested category for merchant"""
        return self.db.get_learned_category(merchant)
