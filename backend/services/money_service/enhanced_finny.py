from datetime import datetime
from .money_db import MoneyServiceDB
from .advanced_finny_db import AdvancedFinnyDB
from .advanced_analytics import AdvancedAnalytics

class EnhancedFinny:
    def __init__(self):
        self.db = AdvancedFinnyDB()
        self.analytics = AdvancedAnalytics()

    def conversational_transaction_entry(self, user_id):
        print("\n" + "="*60)
        print("💰 ENHANCED FINNY - CONVERSATIONAL TRANSACTION ENTRY")
        print("="*60)
        print("🤝 Let me help you track today's expenses in detail!")
        print("💡 I'll ask you about different spending categories...")
        
        transactions = []
        
        # Food expenses
        print(f"\n🍔 { 'FOOD EXPENSES' }")
        print("-" * 40)
        food_spent = self._ask_category_spending("food", [
            "breakfast", "lunch", "dinner", "snacks", "coffee", "groceries"
        ])
        
        # Entertainment expenses
        print(f"\n🎬 { 'ENTERTAINMENT EXPENSES' }")
        print("-" * 40)
        entertainment_spent = self._ask_category_spending("entertainment", [
            "movies", "games", "subscriptions", "concerts", "streaming"
        ])
        
        # Transport expenses
        print(f"\n🚗 { 'TRANSPORT EXPENSES' }")
        print("-" * 40)
        transport_spent = self._ask_category_spending("transport", [
            "fuel", "auto/cab", "public transport", "parking", "maintenance"
        ])
        
        # Shopping expenses
        print(f"\n🛒 { 'SHOPPING EXPENSES' }")
        print("-" * 40)
        shopping_spent = self._ask_category_spending("shopping", [
            "clothes", "electronics", "groceries", "household items", "online shopping"
        ])
        
        # Other expenses
        print(f"\n📦 { 'OTHER EXPENSES' }")
        print("-" * 40)
        other_spent = self._ask_category_spending("other", [
            "bills", "healthcare", "education", "personal care", "miscellaneous"
        ])
        
        # Save all transactions with intelligent features
        total_spent = 0
        for category_data in [food_spent, entertainment_spent, transport_spent, shopping_spent, other_spent]:
            for transaction in category_data:
                if transaction['amount'] > 0:
                    # Get suggested category for merchant
                    suggested_category = self.analytics.get_suggested_category(transaction['merchant'])
                    if suggested_category and suggested_category != transaction['category']:
                        print(f"💡 Suggestion: '{transaction['merchant']}' is usually categorized as '{suggested_category}'")
                        use_suggested = input("Use suggested category? (yes/no): ").strip().lower()
                        if use_suggested in ['yes', 'y']:
                            transaction['category'] = suggested_category
                    
                    # Check for duplicates and save
                    transaction_id = self.analytics.intelligent_transaction_entry(
                        user_id, transaction['amount'], transaction['category'], 
                        transaction['merchant'], transaction['date'], transaction['description']
                    )
                    
                    if transaction_id:
                        transactions.append(transaction)
                        total_spent += transaction['amount']
        
        # Summary
        self._show_transaction_summary(transactions, total_spent)
        return transactions

    def _ask_category_spending(self, category, examples):
        """Ask detailed questions about a specific spending category"""
        transactions = []
        
        print(f"\n💬 Did you spend anything on {category.upper()} today?")
        response = input("Enter 'yes' or 'no': ").strip().lower()
        
        if response not in ['yes', 'y']:
            return transactions
        
        print(f"\n🤔 Let's break down your {category} expenses...")
        
        while True:
            print(f"\n📝 Enter {category} expense details:")
            
            # Get specific type
            print(f"What type of {category} expense was it?")
            for i, example in enumerate(examples, 1):
                print(f"  {i}. {example.title()}")
            print(f"  {len(examples) + 1}. Other")
            
            try:
                type_choice = int(input("Select number: ").strip())
                if 1 <= type_choice <= len(examples):
                    expense_type = examples[type_choice - 1]
                elif type_choice == len(examples) + 1:
                    expense_type = input(f"Specify other {category} type: ").strip()
                else:
                    print("❌ Invalid choice")
                    continue
            except ValueError:
                print("❌ Please enter a number")
                continue
            
            # Get amount
            while True:
                try:
                    amount = float(input(f"How much did you spend on {expense_type}? ₹").strip())
                    if amount > 0:
                        break
                    else:
                        print("❌ Amount must be positive")
                except ValueError:
                    print("❌ Invalid amount")
            
            # Get merchant
            merchant = input(f"Where did you spend this (store/merchant name)? ").strip()
            if not merchant:
                merchant = f"{expense_type.title()} Store"
            
            # Get description
            description = input(f"Any notes about this {expense_type} expense? ").strip()
            
            # Create transaction
            transaction = {
                'amount': amount,
                'category': category,
                'merchant': merchant,
                'date': datetime.now().strftime("%Y-%m-%d"),
                'description': f"{expense_type.title()}: {description}" if description else expense_type.title()
            }
            transactions.append(transaction)
            
            print(f"✅ Added: ₹{amount} for {expense_type} at {merchant}")
            
            # Ask for more expenses in same category
            more = input(f"\n💬 Any more {category} expenses? (yes/no): ").strip().lower()
            if more not in ['yes', 'y']:
                break
        
        return transactions

    def _show_transaction_summary(self, transactions, total_spent):
        """Show summary of all entered transactions"""
        print("\n" + "="*60)
        print("📊 TODAY'S SPENDING SUMMARY")
        print("="*60)
        
        # Group by category
        category_totals = {}
        for transaction in transactions:
            category = transaction['category']
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += transaction['amount']
        
        print(f"\n💰 Total Spent Today: ₹{total_spent:.2f}")
        print(f"📝 Total Transactions: {len(transactions)}")
        
        print(f"\n📊 Breakdown by Category:")
        print("-" * 40)
        for category, amount in category_totals.items():
            percentage = (amount / total_spent * 100) if total_spent > 0 else 0
            bar_length = int(percentage / 2)
            bar = "█" * bar_length
            print(f"{category.title():12} ₹{amount:8.2f} {bar} {percentage:5.1f}%")
        
        print(f"\n📋 Transaction Details:")
        print("-" * 40)
        for i, transaction in enumerate(transactions, 1):
            print(f"[{i}] ₹{transaction['amount']:7.2f} - {transaction['merchant']}")
            print(f"     📂 {transaction['category'].title()}: {transaction['description']}")
        
        print(f"\n💡 { 'FINANCIAL INSIGHTS' }")
        print("-" * 40)
        
        if total_spent > 2000:
            print("📈 High spending day! Consider reviewing your budget.")
        elif total_spent > 1000:
            print("📊 Moderate spending. Track your expenses regularly.")
        else:
            print("💪 Good control on daily spending!")
        
        # Show highest category
        if category_totals:
            highest_category = max(category_totals, key=category_totals.get)
            print(f"🎯 Highest spending category: {highest_category.title()} (₹{category_totals[highest_category]:.2f})")

    def quick_add_transaction(self, user_id):
        """Quick transaction entry for experienced users"""
        print("\n" + "="*50)
        print("⚡ QUICK ADD TRANSACTION")
        print("="*50)
        
        try:
            amount = float(input("Amount: ₹").strip())
            if amount <= 0:
                print("❌ Amount must be positive")
                return False

            category = input("Category: ").strip()
            merchant = input("Merchant: ").strip()
            
            date_input = input("Date (YYYY-MM-DD) or Enter for today: ").strip()
            date = date_input if date_input else datetime.now().strftime("%Y-%m-%d")
            
            description = input("Description: ").strip()

            transaction_id = self.db.add_transaction(user_id, amount, category, merchant, date, description)
            
            print(f"✅ Transaction added! ID: {transaction_id}")
            print(f"💰 ₹{amount} - {category} at {merchant}")
            
            return True
            
        except ValueError:
            print("❌ Invalid amount")
            return False

    def show_menu(self, user_id):
        while True:
            print("\n" + "="*60)
            print("💰 ENHANCED FINNY - SMART TRANSACTION TRACKER")
            print("="*60)
            print("1. 🗣️ Conversational Entry (Recommended)")
            print("2. ⚡ Quick Add Transaction")
            print("3. 📋 View Transactions")
            print("4. 📊 Monthly Summary")
            print("5. 🧠 Advanced Analytics Dashboard")
            print("6. ⬅️ Back to Money Service")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self.conversational_transaction_entry(user_id)
            elif choice == "2":
                self.quick_add_transaction(user_id)
            elif choice == "3":
                self._view_transactions(user_id)
            elif choice == "4":
                self._monthly_summary(user_id)
            elif choice == "5":
                from .intelligent_finny import IntelligentFinny
                intelligent_finny = IntelligentFinny()
                intelligent_finny.show_comprehensive_dashboard(user_id)
            elif choice == "6":
                return
            else:
                print("❌ Invalid choice")
            
            input("\nPress Enter to continue...")

    def _view_transactions(self, user_id):
        """View transactions with enhanced formatting"""
        print("\n" + "="*50)
        print("💰 MY TRANSACTIONS")
        print("="*50)
        
        transactions = self.db.get_transactions(user_id)
        
        if not transactions:
            print("📭 No transactions found")
            return

        print(f"\nTotal Transactions: {len(transactions)}\n")
        
        for idx, trans in enumerate(transactions, 1):
            print(f"[{idx}] ₹{trans[2]:.2f} - {trans[3]}")
            print(f"    📂 {trans[4].title()}")
            print(f"    📅 {trans[5]}")
            if trans[6]:
                print(f"    📝 {trans[6]}")
            print("-" * 40)

    def _monthly_summary(self, user_id):
        """Enhanced monthly summary with insights"""
        print("\n" + "="*50)
        print("📊 MONTHLY SPENDING ANALYSIS")
        print("="*50)
        
        try:
            month = int(input("Month (1-12): ").strip())
            year = int(input("Year: ").strip())
        except ValueError:
            print("❌ Invalid input")
            return

        summary = self.db.get_monthly_summary(user_id, month, year)
        
        if not summary:
            print(f"📭 No transactions found for {month:02d}/{year}")
            return

        month_name = datetime(year, month, 1).strftime("%B")
        print(f"\n📊 Spending Analysis - {month_name} {year}")
        print("=" * 50)
        
        total_spending = 0
        for category, amount, count in summary:
            print(f"📂 {category.title()}: ₹{amount:.2f} ({count} transactions)")
            total_spending += amount
        
        print("=" * 50)
        print(f"💰 Total Spending: ₹{total_spending:.2f}")
        print(f"📅 Daily Average: ₹{total_spending/30:.2f}")
        
        # Enhanced insights
        print(f"\n💡 { 'SPENDING INSIGHTS' }")
        print("-" * 50)
        
        if total_spending > 50000:
            print("📈 Very high spending! Consider budget review.")
        elif total_spending > 30000:
            print("📊 High spending. Track expenses carefully.")
        elif total_spending > 15000:
            print("💪 Moderate spending. Room for improvement.")
        else:
            print("🎉 Excellent spending control!")
        
        # Top category
        if summary:
            top_category = max(summary, key=lambda x: x[1])
            print(f"🎯 Top spending: {top_category[0].title()} (₹{top_category[1]:.2f})")
            
            # Daily average for top category
            daily_avg = top_category[1] / 30
            print(f"📊 Daily {top_category[0]} average: ₹{daily_avg:.2f}")
        
        # Visual breakdown
        print(f"\n📈 Spending Breakdown:")
        for category, amount, count in summary:
            percentage = (amount / total_spending) * 100 if total_spending > 0 else 0
            bar_length = int(percentage / 2)
            bar = "█" * bar_length
            print(f"{category.title():12} {bar} {percentage:5.1f}%")
