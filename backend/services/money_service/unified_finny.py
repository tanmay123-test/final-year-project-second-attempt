"""
Unified Finny - All transaction tracking modes in one place
Combines Enhanced, Natural Language, and Intelligent Finny features
"""

from datetime import datetime
from .advanced_finny_db import AdvancedFinnyDB
from .advanced_analytics import AdvancedAnalytics

class UnifiedFinny:
    """Unified Finny - All transaction tracking modes in one interface"""
    
    def __init__(self):
        self.db = AdvancedFinnyDB()
        self.analytics = AdvancedAnalytics()
    
    def show_menu(self, user_id):
        """Main menu for Unified Finny"""
        while True:
            print("\n" + "="*70)
            print("  UNIFIED FINNY - SMART TRANSACTION TRACKER")
            print("="*70)
            print("  Choose your preferred way to track expenses:")
            print("")
            print("1.   QUICK MODE - Fast & Simple")
            print("     Quick add transactions")
            print("     View transactions")
            print("     Monthly summary")
            print("     Advanced analytics")
            print("")
            print("2.   CHAT MODE - Natural Language")
            print("     Chat-style expense entry")
            print("     View transactions")
            print("     Today's summary")
            print("     Help & examples")
            print("     Advanced analytics")
            print("")
            print("3.   ANALYTICS MODE - Deep Insights")
            print("     Comprehensive dashboard")
            print("     Budget setup & monitoring")
            print("     Weekly analysis")
            print("     Spending predictions")
            print("     Financial health score")
            print("")
            print("4.    Back to Money Service")
            
            choice = input("\nSelect mode (1-4): ").strip()
            
            if choice == "1":
                self._quick_mode(user_id)
            elif choice == "2":
                self._chat_mode(user_id)
            elif choice == "3":
                self._analytics_mode(user_id)
            elif choice == "4":
                return
            else:
                print("  Invalid choice. Please select 1-4.")
    
    def _quick_mode(self, user_id):
        """Quick Mode - Fast & Simple transaction tracking"""
        while True:
            print("\n" + "="*60)
            print("  QUICK MODE - Fast & Simple")
            print("="*60)
            print("1.   Quick Add Transaction")
            print("2.   View Transactions")
            print("3.   Monthly Summary")
            print("4.   Advanced Analytics Dashboard")
            print("5.    Back to Finny Modes")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self._quick_add_transaction(user_id)
            elif choice == "2":
                self._view_transactions(user_id)
            elif choice == "3":
                self._show_monthly_summary(user_id)
            elif choice == "4":
                self._show_advanced_dashboard(user_id)
            elif choice == "5":
                return
            else:
                print("  Invalid choice")
            
            input("\nPress Enter to continue...")
    
    def _chat_mode(self, user_id):
        """Chat Mode - Natural Language expense tracking"""
        while True:
            print("\n" + "="*60)
            print("  CHAT MODE - Natural Language")
            print("="*60)
            print("1.   Chat Entry (Natural Language)")
            print("2.   View Transactions")
            print("3.   Today's Summary")
            print("4.   Help & Examples")
            print("5.   Advanced Analytics Dashboard")
            print("6.    Back to Finny Modes")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self._chat_entry(user_id)
            elif choice == "2":
                self._view_transactions(user_id)
            elif choice == "3":
                self._show_today_summary(user_id)
            elif choice == "4":
                self._show_help_examples()
            elif choice == "5":
                self._show_advanced_dashboard(user_id)
            elif choice == "6":
                return
            else:
                print("  Invalid choice")
            
            input("\nPress Enter to continue...")
    
    def _analytics_mode(self, user_id):
        """Analytics Mode - Deep Financial Insights"""
        while True:
            print("\n" + "="*60)
            print("  ANALYTICS MODE - Deep Insights")
            print("="*60)
            print("1.   Comprehensive Dashboard")
            print("2.   Budget Setup & Monitoring")
            print("3.   Weekly Analysis")
            print("4.   Spending Predictions")
            print("5.   Financial Health Score")
            print("6.    Back to Finny Modes")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self._show_comprehensive_dashboard(user_id)
            elif choice == "2":
                self._budget_setup_monitoring(user_id)
            elif choice == "3":
                self._show_weekly_analysis(user_id)
            elif choice == "4":
                self._show_spending_predictions(user_id)
            elif choice == "5":
                self._show_financial_health_score(user_id)
            elif choice == "6":
                return
            else:
                print("  Invalid choice")
            
            input("\nPress Enter to continue...")
    
    # Quick Mode Methods
    def _quick_add_transaction(self, user_id):
        """Quick transaction entry"""
        print("\n" + "="*50)
        print("  QUICK ADD TRANSACTION")
        print("="*50)
        
        try:
            amount = float(input("Amount:  ").strip())
            if amount <= 0:
                print("  Amount must be positive")
                return

            category = input("Category: ").strip()
            merchant = input("Merchant: ").strip()
            
            date_input = input("Date (YYYY-MM-DD) or Enter for today: ").strip()
            date = date_input if date_input else datetime.now().strftime("%Y-%m-%d")
            
            description = input("Description (optional): ").strip()

            # Check for duplicates
            is_duplicate = self.analytics.check_duplicate_transaction(user_id, amount, category, merchant, date)
            
            if is_duplicate:
                print(f"\n   Possible duplicate transaction detected!")
                print(f"  Amount:  {amount}")
                print(f"  Category: {category}")
                print(f"  Merchant: {merchant}")
                print(f"  Date: {date}")
                
                confirm = input("Confirm save? (yes/no): ").strip().lower()
                if confirm not in ['yes', 'y']:
                    print("  Transaction cancelled")
                    return
            
            # Save transaction
            transaction_id = self.db.add_transaction(user_id, amount, category, merchant, date, description)
            
            print(f"  Transaction added successfully!")
            print(f"   {amount} - {category} at {merchant}")
            
        except ValueError:
            print("  Invalid amount")
    
    def _view_transactions(self, user_id):
        """View all transactions"""
        print("\n" + "="*50)
        print("  MY TRANSACTIONS")
        print("="*50)
        
        transactions = self.db.get_transactions(user_id)
        
        if not transactions:
            print("  No transactions found")
            return
        
        print(f"Total Transactions: {len(transactions)}")
        print("-" * 50)
        
        for i, trans in enumerate(transactions, 1):
            print(f"[{i}]  {trans['amount']:.2f} - {trans['category']}")
            print(f"      {trans['merchant']}")
            print(f"      {trans['date']}")
            if trans.get('description'):
                print(f"      {trans['description']}")
            print("-" * 50)
    
    def _show_monthly_summary(self, user_id):
        """Show monthly spending summary"""
        print("\n" + "="*50)
        print("  MONTHLY SUMMARY")
        print("="*50)
        
        current_date = datetime.now()
        month = current_date.month
        year = current_date.year
        
        summary = self.db.get_monthly_summary(user_id, month, year)
        
        if not summary:
            print(f"  No transactions found for {month:02d}/{year}")
            return

        month_name = datetime(year, month, 1).strftime("%B")
        print(f"  Spending Analysis - {month_name} {year}")
        print("=" * 50)
        
        total_spending = 0
        for category, amount, count in summary:
            print(f"  {category.title()}:  {amount:.2f} ({count} transactions)")
            total_spending += amount
        
        print("=" * 50)
        print(f"  Total Spending:  {total_spending:.2f}")
        print(f"  Daily Average:  {total_spending/30:.2f}")
        
        # Visual breakdown
        print(f"\n  Spending Breakdown:")
        for category, amount, count in summary:
            percentage = (amount / total_spending) * 100 if total_spending > 0 else 0
            bar_length = int(percentage / 2)
            bar = " " * bar_length
            print(f"{category.title():12} {bar} {percentage:5.1f}%")
    
    def _show_advanced_dashboard(self, user_id):
        """Show advanced analytics dashboard"""
        print("\n" + "="*80)
        print("  ADVANCED ANALYTICS DASHBOARD")
        print("="*80)
        
        dashboard = self.analytics.get_comprehensive_dashboard(user_id)
        
        # Daily Summary
        daily = dashboard['daily_summary']
        print(f"\n  DAILY SUMMARY - {daily['date']}")
        print("-" * 40)
        print(f"  Total Spent:  {daily['total_spent']:.2f}")
        print(f"  Transactions: {daily['transaction_count']}")
        
        # Weekly Analysis
        weekly = dashboard['weekly_summary']
        print(f"\n  WEEKLY ANALYSIS")
        print("-" * 40)
        for week_data in weekly.get('weekly_breakdown', []):
            print(f"Week {week_data['week']}:  {week_data['amount']:.2f}")
        
        # Monthly Summary
        monthly = dashboard['monthly_summary']
        print(f"\n  MONTHLY SUMMARY")
        print("-" * 40)
        print(f"  Total Spent:  {monthly['total_spent']:.2f}")
        print(f"  Transactions: {monthly['transaction_count']}")
        print(f"  Predicted Monthly:  {monthly['predicted_monthly']:.2f}")
        
        # Financial Health Score
        health = dashboard['financial_health_score']
        print(f"\n  FINANCIAL HEALTH SCORE")
        print("-" * 40)
        print(f"  Overall Score: {health['overall_score']}/100 ({health['grade']})")
        print(f"  Budget Adherence: {health['components']['budget_adherence']:.1f}/100")
        print(f"  Spending Stability: {health['components']['spending_stability']:.1f}/100")
        print(f"   Category Balance: {health['components']['category_balance']:.1f}/100")
    
    # Chat Mode Methods
    def _chat_entry(self, user_id):
        """Natural language chat entry"""
        print("\n" + "="*60)
        print("  CHAT ENTRY - NATURAL LANGUAGE")
        print("="*60)
        print("  Just tell me how you spent money today!")
        print("  Examples:")
        print("     food 200 entertainment 300 transport 150")
        print("     lunch 150 at subway movie 200 at pvr")
        print("     spent 500 on shopping 200 on food")
        print("     breakfast 100 lunch 150 dinner 200")
        print("\n  Type your expenses (or 'help' for examples):")
        
        while True:
            user_input = input("\n  You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'back']:
                break
            elif user_input.lower() == 'help':
                self._show_help_examples()
                continue
            elif user_input.lower() == 'today':
                self._show_today_summary(user_id)
                continue
            
            # Parse the input
            transactions = self._parse_natural_language(user_input)
            
            if not transactions:
                print("  I couldn't understand that. Try examples like:")
                print("     food 200 entertainment 300")
                print("     lunch 150 at subway")
                print("     spent 500 on shopping")
                continue
            
            # Save transactions
            saved_transactions = []
            for trans in transactions:
                # Check for duplicates
                is_duplicate = self.analytics.check_duplicate_transaction(
                    user_id, trans['amount'], trans['category'], 
                    trans['merchant'], trans['date']
                )
                
                if is_duplicate:
                    print(f"\n   Possible duplicate transaction detected!")
                    print(f"  Amount:  {trans['amount']}")
                    print(f"  Category: {trans['category']}")
                    print(f"  Merchant: {trans['merchant']}")
                    print(f"  Date: {trans['date']}")
                    
                    confirm = input("Confirm save? (yes/no): ").strip().lower()
                    if confirm not in ['yes', 'y']:
                        print("  Transaction cancelled")
                        continue
                
                # Save transaction
                transaction_id = self.db.add_transaction(
                    user_id, trans['amount'], trans['category'], 
                    trans['merchant'], trans['date'], trans['description']
                )
                
                if transaction_id:
                    trans['id'] = transaction_id
                    saved_transactions.append(trans)
                    print(f"  Transaction saved successfully! ID: {transaction_id}")
            
            # Show summary
            self._show_parsed_summary(saved_transactions)
            
            # Ask if more expenses
            more = input("\n  Any more expenses? (type 'yes' or just continue): ").strip()
            if more.lower() not in ['yes', 'y', '']:
                break
    
    def _parse_natural_language(self, user_input):
        """Parse natural language input into transactions"""
        import re
        
        transactions = []
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Pattern to match: amount category [at merchant]
        pattern = r'(\d+(?:\.\d+)?)\s+([a-zA-Z]+)(?:\s+at\s+([a-zA-Z\s]+))?'
        
        matches = re.findall(pattern, user_input.lower())
        
        for amount_str, category, merchant in matches:
            try:
                amount = float(amount_str)
                
                # Map common categories
                category_map = {
                    'food': 'food', 'breakfast': 'food', 'lunch': 'food', 'dinner': 'food',
                    'snacks': 'food', 'coffee': 'food', 'groceries': 'food',
                    'entertainment': 'entertainment', 'movie': 'entertainment', 'movies': 'entertainment',
                    'transport': 'transport', 'fuel': 'transport', 'auto': 'transport', 'cab': 'transport',
                    'shopping': 'shopping', 'clothes': 'shopping', 'electronics': 'shopping',
                    'other': 'other', 'bills': 'other', 'healthcare': 'other', 'education': 'other'
                }
                
                mapped_category = category_map.get(category, category.title())
                merchant_name = merchant.strip() if merchant else f"Unknown {mapped_category}"
                
                transactions.append({
                    'amount': amount,
                    'category': mapped_category,
                    'merchant': merchant_name,
                    'date': today,
                    'description': f"Natural language entry: {user_input}"
                })
                
            except ValueError:
                continue
        
        return transactions
    
    def _show_parsed_summary(self, transactions):
        """Show summary of parsed transactions"""
        if not transactions:
            return
        
        print(f"\n  Successfully saved {len(transactions)} transactions:")
        print("-" * 50)
        
        total = 0
        for trans in transactions:
            print(f"   {trans['amount']:.2f} - {trans['category']} at {trans['merchant']}")
            total += trans['amount']
        
        print("-" * 50)
        print(f"  Total:  {total:.2f}")
    
    def _show_today_summary(self, user_id):
        """Show today's spending summary"""
        print("\n" + "="*50)
        print("  TODAY'S SUMMARY")
        print("="*50)
        
        today = datetime.now().strftime("%Y-%m-%d")
        transactions = self.db.get_transactions(user_id)
        
        today_transactions = [t for t in transactions if t['date'] == today]
        
        if not today_transactions:
            print(f"  No expenses recorded for today ({today})")
            return
        
        total_spent = sum(t['amount'] for t in today_transactions)
        
        print(f"  Date: {today}")
        print(f"  Total Spent:  {total_spent:.2f}")
        print(f"  Transactions: {len(today_transactions)}")
        print("-" * 50)
        
        # Category breakdown
        categories = {}
        for trans in today_transactions:
            cat = trans['category']
            if cat not in categories:
                categories[cat] = {'amount': 0, 'count': 0}
            categories[cat]['amount'] += trans['amount']
            categories[cat]['count'] += 1
        
        for category, data in categories.items():
            print(f"  {category.title()}:  {data['amount']:.2f} ({data['count']} transactions)")
    
    def _show_help_examples(self):
        """Show help and examples for natural language entry"""
        print("\n" + "="*60)
        print("  HOW TO TELL ME ABOUT EXPENSES")
        print("="*60)
        
        print("  SIMPLE FORMAT:")
        print("   food 200 entertainment 300 transport 150")
        print("   breakfast 100 lunch 150 dinner 200")
        print("   shopping 500 bills 200 education 300")
        print("")
        print("  WITH MERCHANTS:")
        print("   lunch 150 at subway dinner 200 at restaurant")
        print("   movie 200 at pvr coffee 100 at starbucks")
        print("   transport 300 at ola shopping 2000 at amazon")
        print("")
        print("  NATURAL LANGUAGE:")
        print("   spent 200 on food 300 on entertainment")
        print("   paid 150 for lunch 200 for shopping")
        print("   bought groceries for 500 fuel for 1000")
        print("")
        print("  QUICK COMMANDS:")
        print("   help - Show this help")
        print("   today - Show today's summary")
        print("   exit/quit - Go back")
        print("")
        print("  CATEGORIES I UNDERSTAND:")
        print("   Food: food, breakfast, lunch, dinner, snacks, coffee, groceries")
        print("   Entertainment: movie, games, subscription, streaming")
        print("   Transport: fuel, auto, cab, uber, ola, bus, train")
        print("   Shopping: clothes, electronics, amazon, flipkart, store")
        print("   Other: bills, healthcare, education, miscellaneous")
    
    # Analytics Mode Methods
    def _show_comprehensive_dashboard(self, user_id):
        """Show comprehensive financial dashboard"""
        print("\n" + "="*80)
        print("  COMPREHENSIVE FINANCIAL DASHBOARD")
        print("="*80)
        
        dashboard = self.analytics.get_comprehensive_dashboard(user_id)
        
        # Daily Summary
        daily = dashboard['daily_summary']
        print(f"\n  DAILY SUMMARY - {daily['date']}")
        print("-" * 50)
        print(f"  Total Spent:  {daily['total_spent']:.2f}")
        print(f"  Transactions: {daily['transaction_count']}")
        
        # Weekly Analysis
        weekly = dashboard['weekly_summary']
        print(f"\n  WEEKLY ANALYSIS")
        print("-" * 50)
        for insight in weekly.get('trend_insights', []):
            print(f"   {insight}")
        
        # Monthly Summary
        monthly = dashboard['monthly_summary']
        print(f"\n  MONTHLY SUMMARY")
        print("-" * 50)
        print(f"  Total Spent:  {monthly['total_spent']:.2f}")
        print(f"  Transactions: {monthly['transaction_count']}")
        print(f"  Predicted Monthly:  {monthly['predicted_monthly']:.2f}")
        
        # Top Merchants
        top_merchants = dashboard['top_merchants']
        print(f"\n  TOP MERCHANTS")
        print("-" * 50)
        print(f"  Top: {top_merchants['top_merchant']['name']} -  {top_merchants['top_merchant']['amount']:.2f}")
        
        # Spending Predictions
        predictions = dashboard['spending_predictions']
        print(f"\n  SPENDING PREDICTIONS")
        print("-" * 50)
        for pred in predictions[:5]:  # Show top 5
            print(f"{pred['category'].title()}:  {pred['current_spending']:.2f}    {pred['predicted_spending']:.2f}")
        
        # Spending Spikes
        spikes = dashboard['spending_spikes']
        if spikes:
            print(f"\n  SPENDING SPIKES")
            print("-" * 50)
            for spike in spikes[:3]:  # Show top 3
                print(spike['insight'])
        
        # Financial Health Score
        health = dashboard['financial_health_score']
        print(f"\n  FINANCIAL HEALTH SCORE")
        print("-" * 50)
        print(f"  Overall Score: {health['overall_score']}/100 ({health['grade']})")
        print(f"  Budget Adherence: {health['components']['budget_adherence']:.1f}/100")
        print(f"  Spending Stability: {health['components']['spending_stability']:.1f}/100")
        print(f"   Category Balance: {health['components']['category_balance']:.1f}/100")
        
        # Insights
        print(f"\n  Financial Insights:")
        print("-" * 50)
        if health['overall_score'] >= 80:
            print("     Excellent financial health!")
        elif health['overall_score'] >= 60:
            print("     Good financial health with room for improvement")
        else:
            print("      Room for improvement - focus on budget adherence")
    
    def _budget_setup_monitoring(self, user_id):
        """Budget setup and monitoring"""
        current_date = datetime.now()
        month_name = current_date.strftime("%B")
        year = current_date.year
        
        print(f"\n" + "="*60)
        print(f"  MONTHLY BUDGET SETUP")
        print("="*60)
        print(f"  Setting budgets for {month_name} {year}")
        print("  Based on your spending patterns, here are some suggestions:")
        print("")
        
        # Get current spending for suggestions
        current_date = datetime.now()
        month_num = current_date.month
        year = current_date.year
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM transactions 
        WHERE user_id=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
        GROUP BY category
        """, (user_id, f"{month_num:02d}", str(year)))
        
        current_spending = dict(cursor.fetchall())
        
        # Budget categories
        categories = ['Food', 'Transport', 'Shopping', 'Entertainment', 'Other']
        budgets = {}
        
        print("  Enter budget amounts (enter 0 to skip):")
        for category in categories:
            suggestion = current_spending.get(category.lower(), 0)
            if suggestion > 0:
                suggested = int(suggestion * 1.2)  # Suggest 20% more than current
                budget_input = input(f"{category}:  {suggested} (suggested) ").strip()
            else:
                budget_input = input(f"{category}:  ").strip()
            
            try:
                budget = float(budget_input) if budget_input else 0
                if budget > 0:
                    budgets[category] = budget
                    print(f"     {category}:  {budget:.2f}")
                else:
                    print(f"      Skipping {category.lower()}")
            except ValueError:
                print(f"      Skipping {category.lower()}")
        
        # Save budgets
        if budgets:
            for category, amount in budgets.items():
                self.db.set_monthly_budget(user_id, category.lower(), month_num, year, amount)
            print(f"\n  Budgets set for {len(budgets)} categories")
        else:
            print(f"\n   No budgets set for {month_name} {year}")
        
        input("\nPress Enter to continue...")
        
        # Show budget monitoring
        self._show_budget_monitoring(user_id)
    
    def _show_budget_monitoring(self, user_id):
        """Show budget monitoring"""
        print("\n" + "="*60)
        print("  BUDGET MONITORING")
        print("="*60)
        
        current_date = datetime.now()
        month_name = current_date.strftime("%B")
        month_num = current_date.month
        year = current_date.year
        
        alerts = self.analytics.get_budget_alerts(user_id, month_name, year)
        
        if not alerts:
            print("  No budgets set for this month")
            print("  Set budgets first to enable monitoring")
            return
        
        print(f"  Budget Status - {month_name} {year}")
        print("-" * 50)
        
        for alert in alerts:
            status_emoji = " " if alert['level'] == 'ON_TRACK' else ("  " if alert['level'] == 'WARNING' else " ")
            print(f"{status_emoji} {alert['category'].title()}:  {alert['spent']:.2f} /  {alert['budget']:.2f}")
            
            if alert['level'] != 'ON_TRACK':
                print(f"   {alert['message']}")
                print(f"     Budget:  {alert['budget']:.2f}")
                print(f"     Spent:  {alert['spent']:.2f}")
                print(f"     Remaining:  {alert['remaining']:.2f}")
    
    def _show_weekly_analysis(self, user_id):
        """Show weekly spending analysis"""
        print("\n" + "="*60)
        print("  WEEKLY ANALYSIS")
        print("="*60)
        
        current_date = datetime.now()
        weekly_data = self.analytics.get_weekly_summary(user_id, current_date.year, current_date.month)
        
        print(f"  Weekly Breakdown - {current_date.strftime('%B %Y')}")
        print("-" * 50)
        
        for week_data in weekly_data.get('weekly_breakdown', []):
            print(f"Week {week_data['week']}:  {week_data['amount']:.2f}")
        
        print(f"\n  Insights:")
        print("-" * 30)
        for insight in weekly_data.get('trend_insights', []):
            print(f"   {insight}")
    
    def _show_spending_predictions(self, user_id):
        """Show spending predictions"""
        print("\n" + "="*60)
        print("  SPENDING PREDICTIONS")
        print("="*60)
        
        current_date = datetime.now()
        month_name = current_date.strftime("%B")
        year = current_date.year
        
        predictions = self.analytics.get_spending_predictions(user_id, month_name, year)
        
        if not predictions:
            print("  No spending data available for predictions")
            return
        
        print(f"  End-of-Month Predictions - {month_name} {year}")
        print("-" * 50)
        
        total_current = sum(p['current_spending'] for p in predictions)
        total_predicted = sum(p['predicted_spending'] for p in predictions)
        
        for prediction in predictions:
            current = prediction['current_spending']
            predicted = prediction['predicted_spending']
            remaining = prediction['remaining_predicted']
            
            print(f"\n  {prediction['category'].title()}")
            print(f"     Current:  {current:.2f}")
            print(f"     Predicted:  {predicted:.2f}")
            print(f"     Remaining:  {remaining:.2f}")
            
            # Progress indicator
            progress = (current / predicted) * 100 if predicted > 0 else 0
            bar_length = 15
            filled_length = min(int(progress / 100 * bar_length), bar_length)
            bar = " " * filled_length + " " * (bar_length - filled_length)
            print(f"     [{bar}] {progress:.1f}% complete")
        
        print(f"\n  TOTAL PREDICTIONS")
        print("-" * 30)
        print(f"  Current Total:  {total_current:.2f}")
        print(f"  Predicted Total:  {total_predicted:.2f}")
        print(f"  Remaining:  {total_predicted - total_current:.2f}")
        
        # Days remaining
        days_in_month = 31 if current_date.month in [1,3,5,7,8,10,12] else (30 if current_date.month != 2 else 28)
        days_remaining = days_in_month - current_date.day
        print(f"  Days Remaining: {days_remaining}")
    
    def _show_financial_health_score(self, user_id):
        """Show detailed financial health analysis"""
        print("\n" + "="*60)
        print("  FINANCIAL HEALTH ANALYSIS")
        print("="*60)
        
        current_date = datetime.now()
        month_name = current_date.strftime("%B")
        year = current_date.year
        
        health = self.analytics.get_financial_health_analysis(user_id, month_name, year)
        
        print(f"\n  Overall Financial Health Score: {health['overall_score']}/100")
        print(f"  Grade: {health['grade']}")
        
        # Visual score representation
        score_bars = int(health['overall_score'] / 10)
        bar = " " * score_bars + " " * (10 - score_bars)
        print(f"  [{bar}]")
        
        print(f"\n  Component Breakdown:")
        print("-" * 40)
        print(f"  Budget Adherence: {health['components']['budget_adherence']:.1f}/100")
        print(f"  Spending Stability: {health['components']['spending_stability']:.1f}/100")
        print(f"   Category Balance: {health['components']['category_balance']:.1f}/100")
        
        print(f"\n  Recommendations:")
        print("-" * 30)
        
        if health['overall_score'] >= 80:
            print("     Excellent financial health!")
            print("     Keep up the great work!")
        elif health['overall_score'] >= 60:
            print("     Good financial health")
            print("     Focus on improving budget adherence")
        elif health['overall_score'] >= 40:
            print("      Moderate financial health")
            print("     Consider setting and following budgets")
        else:
            print("     Financial health needs attention")
            print("     Focus on budgeting and spending control")
        
        # Component-specific advice
        components = health['components']
        
        if components['budget_adherence'] < 60:
            print("     Set realistic budgets and track spending")
        
        if components['spending_stability'] < 60:
            print("     Try to maintain consistent spending patterns")
        
        if components['category_balance'] < 60:
            print("      Diversify spending across categories")

# Singleton instance for reuse
unified_finny = UnifiedFinny()
