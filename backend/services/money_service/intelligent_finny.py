from datetime import datetime
from .advanced_finny_db import AdvancedFinnyDB
from .advanced_analytics import AdvancedAnalytics

class IntelligentFinny:
    def __init__(self):
        self.db = AdvancedFinnyDB()
        self.analytics = AdvancedAnalytics()
    
    def intelligent_transaction_entry(self, user_id, amount, category, merchant, date, description=""):
        """Smart transaction entry with duplicate detection and learning"""
        
        # Check for duplicates
        is_duplicate = self.analytics.check_duplicate_transaction(user_id, amount, category, merchant, date)
        
        if is_duplicate:
            print(f"\n⚠️ Possible duplicate transaction detected!")
            print(f"💰 Amount: ₹{amount}")
            print(f"📂 Category: {category}")
            print(f"🏪 Merchant: {merchant}")
            print(f"📅 Date: {date}")
            
            confirm = input("Confirm save? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("❌ Transaction cancelled")
                return None
        
        # Learn merchant-category mapping
        self.analytics.learn_merchant_category(merchant, category)
        
        # Save transaction
        transaction_id = self.db.add_transaction(user_id, amount, category, merchant, date, description)
        
        print(f"✅ Transaction saved successfully!")
        print(f"📝 Transaction ID: {transaction_id}")
        
        # Check budget alerts
        self.check_and_show_budget_alerts(user_id, category)
        
        return transaction_id
    
    def check_and_show_budget_alerts(self, user_id, category):
        """Check and display budget alerts for a category"""
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year
        
        alerts = self.analytics.get_budget_alerts(user_id, month, year)
        category_alerts = [alert for alert in alerts if alert['category'] == category]
        
        if category_alerts:
            for alert in category_alerts:
                print(f"\n{alert['message']}")
                print(f"💰 Budget: ₹{alert['budget']:.2f}")
                print(f"💸 Spent: ₹{alert['spent']:.2f}")
                print(f"📊 Remaining: ₹{alert['remaining']:.2f}")
    
    def set_budgets(self, user_id):
        """Set monthly budgets with smart suggestions"""
        print("\n" + "="*60)
        print("💰 MONTHLY BUDGET SETUP")
        print("="*60)
        
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year
        
        print(f"\n📅 Setting budgets for {month} {year}")
        print("💡 Based on your spending patterns, here are some suggestions:")
        
        # Get spending from previous month for suggestions
        if current_date.month == 1:
            prev_month = 12
            prev_year = current_date.year - 1
        else:
            prev_month = current_date.month - 1
            prev_year = current_date.year
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM transactions 
        WHERE user_id=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
        GROUP BY category
        """, (user_id, f"{prev_month:02d}", str(prev_year)))
        
        prev_spending = cursor.fetchall()
        
        # Show suggestions
        if prev_spending:
            print("\n💡 Suggested budgets based on last month:")
            for category, amount in prev_spending:
                suggested = amount * 1.1  # 10% buffer
                print(f"   {category.title()}: ₹{suggested:.2f} (was ₹{amount:.2f})")
        
        print("\n📝 Enter budget amounts (enter 0 to skip):")
        
        categories = ['food', 'transport', 'shopping', 'entertainment', 'other']
        budgets_set = []
        
        for category in categories:
            # Show current budget if exists
            current_budgets = self.db.get_monthly_budgets(user_id, month, year)
            current_budget = next((b[1] for b in current_budgets if b[0] == category), 0)
            
            if current_budget > 0:
                prompt = f"{category.title()} (current: ₹{current_budget:.2f}): ₹"
            else:
                prompt = f"{category.title()}: ₹"
            
            try:
                budget_amount = float(input(prompt).strip())
                if budget_amount > 0:
                    self.db.set_monthly_budget(user_id, category, budget_amount, month, year)
                    budgets_set.append((category, budget_amount))
                    print(f"✅ Budget set for {category}: ₹{budget_amount:.2f}")
            except ValueError:
                print(f"⏭️ Skipping {category}")
        
        if budgets_set:
            print(f"\n✅ {len(budgets_set)} budgets set for {month} {year}")
            print("💰 Budget monitoring is now active!")
        else:
            print(f"\n⏭️ No budgets set for {month} {year}")
    
    def show_comprehensive_dashboard(self, user_id):
        """Display complete analytics dashboard"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE FINANCIAL DASHBOARD")
        print("="*80)
        
        dashboard = self.analytics.get_comprehensive_dashboard(user_id)
        
        # Daily Summary
        print(f"\n📅 DAILY SUMMARY - {dashboard['daily_summary']['date']}")
        print("-" * 40)
        daily = dashboard['daily_summary']
        print(f"💰 Total Spent: ₹{daily['total_spent']:.2f}")
        print(f"📝 Transactions: {daily['transaction_count']}")
        
        if daily['category_breakdown']:
            print("📂 Categories:")
            for category, amount, count in daily['category_breakdown']:
                print(f"   {category.title()}: ₹{amount:.2f} ({count} transactions)")
        
        # Weekly Summary
        print(f"\n📈 WEEKLY ANALYSIS")
        print("-" * 40)
        weekly = dashboard['weekly_summary']
        for week_data in weekly['weekly_data']:
            print(f"Week {week_data['week']}: ₹{week_data['total']:.2f}")
        
        if weekly['trend_insights']:
            print("💡 Insights:")
            for insight in weekly['trend_insights']:
                print(f"   {insight}")
        
        # Monthly Summary
        print(f"\n📊 MONTHLY SUMMARY - {dashboard['monthly_summary']['month']} {dashboard['monthly_summary']['year']}")
        print("-" * 40)
        monthly = dashboard['monthly_summary']
        print(f"💰 Total Spent: ₹{monthly['total_spent']:.2f}")
        print(f"📝 Transactions: {monthly['transaction_count']}")
        print(f"📅 Daily Average: ₹{monthly['daily_average']:.2f}")
        print(f"🔮 Predicted Monthly: ₹{monthly['predicted_monthly']:.2f}")
        
        # Budget Alerts
        if dashboard['budget_alerts']:
            print(f"\n🚨 BUDGET ALERTS")
            print("-" * 40)
            for alert in dashboard['budget_alerts']:
                print(f"{alert['message']}")
                print(f"   Budget: ₹{alert['budget']:.2f} | Spent: ₹{alert['spent']:.2f}")
        
        # Top Merchants
        print(f"\n🏆 TOP MERCHANTS")
        print("-" * 40)
        top_merchant = dashboard['top_merchants']['top_merchant']
        if top_merchant['name']:
            print(f"🥇 Top: {top_merchant['name']} - ₹{top_merchant['amount']:.2f} ({top_merchant['transactions']} visits)")
        
        # Spending Predictions
        print(f"\n🔮 SPENDING PREDICTIONS")
        print("-" * 40)
        for prediction in dashboard['spending_predictions'][:5]:  # Top 5
            print(f"{prediction['category'].title()}: ₹{prediction['current_spending']:.2f} → ₹{prediction['predicted_spending']:.2f}")
        
        # Spending Spikes
        if dashboard['spending_spikes']:
            print(f"\n⚡ SPENDING SPIKES")
            print("-" * 40)
            for spike in dashboard['spending_spikes']:
                print(f"{spike['insight']}")
        
        # Financial Health Score
        print(f"\n💚 FINANCIAL HEALTH SCORE")
        print("-" * 40)
        health = dashboard['financial_health_score']
        print(f"🎯 Overall Score: {health['overall_score']}/100 ({health['grade']})")
        print(f"📊 Budget Adherence: {health['components']['budget_adherence']:.1f}/100")
        print(f"📈 Spending Stability: {health['components']['spending_stability']:.1f}/100")
        print(f"⚖️ Category Balance: {health['components']['category_balance']:.1f}/100")
        
        print("\n💡 Financial Insights:")
        for insight in health['insights']:
            print(f"   {insight}")
    
    def show_budget_monitoring(self, user_id):
        """Show detailed budget monitoring"""
        print("\n" + "="*60)
        print("💰 BUDGET MONITORING")
        print("="*60)
        
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year
        
        budgets = self.db.get_monthly_budgets(user_id, month, year)
        
        if not budgets:
            print("📭 No budgets set for this month")
            print("💡 Set budgets first to enable monitoring")
            return
        
        print(f"\n📅 Budget Status - {month} {year}")
        print("-" * 50)
        
        for category, budget_amount in budgets:
            budget_amount, current_spending, percentage = self.db.get_budget_status(user_id, category, month, year)
            remaining = budget_amount - current_spending
            
            # Progress bar
            bar_length = 20
            filled_length = min(int(percentage / 5), bar_length)
            if percentage >= 100:
                bar = "🔴" * bar_length
            elif percentage >= 80:
                bar = "🟡" * filled_length + "⚪" * (bar_length - filled_length)
            else:
                bar = "🟢" * filled_length + "⚪" * (bar_length - filled_length)
            
            print(f"\n📂 {category.title()}")
            print(f"   💰 Budget: ₹{budget_amount:.2f}")
            print(f"   💸 Spent: ₹{current_spending:.2f} ({percentage:.1f}%)")
            print(f"   📊 [{bar}]")
            print(f"   📈 Remaining: ₹{remaining:.2f}")
            
            # Alert
            if percentage >= 100:
                print(f"   🚨 BUDGET EXCEEDED!")
            elif percentage >= 90:
                print(f"   ⚠️ APPROACHING LIMIT!")
            elif percentage >= 75:
                print(f"   💡 Watch spending")
    
    def show_weekly_analysis(self, user_id):
        """Show detailed weekly spending analysis"""
        print("\n" + "="*60)
        print("📈 WEEKLY SPENDING ANALYSIS")
        print("="*60)
        
        current_date = datetime.now()
        weekly_data = self.analytics.get_weekly_summary(user_id, current_date.year, current_date.month)
        
        print(f"\n📅 Weekly Breakdown - {current_date.strftime('%B %Y')}")
        print("-" * 50)
        
        total_monthly = 0
        for i, week_data in enumerate(weekly_data['weekly_data']):
            print(f"Week {week_data['week']} ({week_data['start_date']} to {week_data['end_date']})")
            print(f"   💰 Total: ₹{week_data['total']:.2f}")
            
            if i > 0:
                prev_total = weekly_data['weekly_data'][i-1]['total']
                if prev_total > 0:
                    change = ((week_data['total'] - prev_total) / prev_total) * 100
                    if change > 0:
                        print(f"   📈 Up {change:.1f}% from previous week")
                    else:
                        print(f"   📉 Down {abs(change):.1f}% from previous week")
            
            total_monthly += week_data['total']
            print()
        
        print(f"📊 Month Total (so far): ₹{total_monthly:.2f}")
        
        if weekly_data['trend_insights']:
            print("\n💡 Weekly Insights:")
            for insight in weekly_data['trend_insights']:
                print(f"   {insight}")
    
    def show_spending_predictions(self, user_id):
        """Show spending predictions for current month"""
        print("\n" + "="*60)
        print("🔮 SPENDING PREDICTIONS")
        print("="*60)
        
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year
        
        predictions = self.analytics.get_spending_predictions(user_id, month, year)
        
        if not predictions:
            print("📭 No spending data available for predictions")
            return
        
        print(f"\n📅 End-of-Month Predictions - {month} {year}")
        print("-" * 50)
        
        total_current = sum(p['current_spending'] for p in predictions)
        total_predicted = sum(p['predicted_spending'] for p in predictions)
        
        for prediction in predictions:
            current = prediction['current_spending']
            predicted = prediction['predicted_spending']
            remaining = prediction['remaining_predicted']
            
            print(f"\n📂 {prediction['category'].title()}")
            print(f"   💰 Current: ₹{current:.2f}")
            print(f"   🔮 Predicted: ₹{predicted:.2f}")
            print(f"   📈 Remaining: ₹{remaining:.2f}")
            
            # Progress indicator
            progress = (current / predicted) * 100 if predicted > 0 else 0
            bar_length = 15
            filled_length = min(int(progress / 100 * bar_length), bar_length)
            bar = "🟢" * filled_length + "⚪" * (bar_length - filled_length)
            print(f"   📊 [{bar}] {progress:.1f}% complete")
        
        print(f"\n📊 TOTAL PREDICTIONS")
        print("-" * 30)
        print(f"💰 Current Total: ₹{total_current:.2f}")
        print(f"🔮 Predicted Total: ₹{total_predicted:.2f}")
        print(f"📈 Remaining: ₹{total_predicted - total_current:.2f}")
        
        # Days remaining
        days_in_month = 31 if current_date.month in [1,3,5,7,8,10,12] else (30 if current_date.month != 2 else 28)
        days_remaining = days_in_month - current_date.day
        print(f"📅 Days Remaining: {days_remaining}")
    
    def show_menu(self, user_id):
        """Main menu for Intelligent Finny"""
        while True:
            print("\n" + "="*60)
            print("🧠 INTELLIGENT FINNY - ADVANCED ANALYTICS")
            print("="*60)
            print("1. 📊 Comprehensive Dashboard")
            print("2. 💰 Budget Setup & Monitoring")
            print("3. 📈 Weekly Analysis")
            print("4. 🔮 Spending Predictions")
            print("5. 💚 Financial Health Score")
            print("6. ⬅️ Back to Money Service")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self.show_comprehensive_dashboard(user_id)
            elif choice == "2":
                self.set_budgets(user_id)
                self.show_budget_monitoring(user_id)
            elif choice == "3":
                self.show_weekly_analysis(user_id)
            elif choice == "4":
                self.show_spending_predictions(user_id)
            elif choice == "5":
                self.show_financial_health_details(user_id)
            elif choice == "6":
                return
            else:
                print("❌ Invalid choice")
            
            input("\nPress Enter to continue...")
    
    def show_financial_health_details(self, user_id):
        """Show detailed financial health analysis"""
        print("\n" + "="*60)
        print("💚 FINANCIAL HEALTH ANALYSIS")
        print("="*60)
        
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year
        
        health = self.analytics.get_financial_health_analysis(user_id, month, year)
        
        print(f"\n🎯 Overall Financial Health Score: {health['overall_score']}/100")
        print(f"📊 Grade: {health['grade']}")
        
        # Visual score representation
        score_bars = int(health['overall_score'] / 10)
        bar = "💚" * score_bars + "⚪" * (10 - score_bars)
        print(f"📈 [{bar}]")
        
        print(f"\n📋 Component Breakdown:")
        print("-" * 40)
        print(f"📊 Budget Adherence: {health['components']['budget_adherence']:.1f}/100")
        print(f"📈 Spending Stability: {health['components']['spending_stability']:.1f}/100")
        print(f"⚖️ Category Balance: {health['components']['category_balance']:.1f}/100")
        
        print(f"\n💡 Insights & Recommendations:")
        print("-" * 40)
        for insight in health['insights']:
            print(f"   {insight}")
        
        # Recommendations based on score
        if health['overall_score'] < 60:
            print(f"\n🎯 Recommendations for Improvement:")
            print("   • Set and monitor budgets regularly")
            print("   • Review spending patterns weekly")
            print("   • Diversify spending across categories")
            print("   • Avoid impulse purchases")
