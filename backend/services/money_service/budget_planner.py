from datetime import datetime
from .money_db import MoneyServiceDB

class BudgetPlanner:
    def __init__(self):
        self.db = MoneyServiceDB()

    def create_budget(self, user_id):
        print("\n" + "="*50)
        print("📊 SMART BUDGET PLANNER - CREATE BUDGET")
        print("="*50)
        
        # Get current month/year
        current_month = datetime.now().strftime("%B")
        current_year = datetime.now().year
        
        print(f"Creating budget for {current_month} {current_year}")
        
        budgets = {}
        while True:
            category = input("\nCategory (or 'done' to finish): ").strip()
            if category.lower() == 'done':
                break
                
            try:
                limit = float(input(f"Budget limit for {category}: ₹").strip())
                if limit > 0:
                    budgets[category] = limit
                else:
                    print("❌ Budget limit must be positive")
            except ValueError:
                print("❌ Invalid amount")
        
        if not budgets:
            print("❌ No budgets created")
            return False
        
        # Save budgets
        for category, limit in budgets.items():
            self.db.create_budget(user_id, category, limit, current_month, current_year)
        
        print(f"\n✅ Budget created successfully!")
        print(f"📊 {len(budgets)} category budgets set for {current_month} {current_year}")
        
        for category, limit in budgets.items():
            print(f"  📂 {category}: ₹{limit:.2f}")
        
        return True

    def view_budgets(self, user_id):
        print("\n" + "="*50)
        print("📊 SMART BUDGET PLANNER - MY BUDGETS")
        print("="*50)
        
        current_month = datetime.now().strftime("%B")
        current_year = datetime.now().year
        
        budgets = self.db.get_budgets(user_id, current_month, current_year)
        
        if not budgets:
            print(f"📭 No budgets found for {current_month} {current_year}")
            print("💡 Create a budget first!")
            return
        
        print(f"\n📊 Budget Status - {current_month} {current_year}")
        print("=" * 60)
        
        for budget in budgets:
            category = budget[2]
            limit = budget[3]
            spent = budget[4]
            remaining = limit - spent
            percentage_used = (spent / limit) * 100 if limit > 0 else 0
            
            # Status indicator
            if percentage_used >= 100:
                status = "🔴 OVER BUDGET"
            elif percentage_used >= 80:
                status = "🟡 WARNING"
            else:
                status = "🟢 GOOD"
            
            print(f"\n📂 {category}")
            print(f"   💰 Budget: ₹{limit:.2f}")
            print(f"   💸 Spent: ₹{spent:.2f}")
            print(f"   💵 Remaining: ₹{remaining:.2f}")
            print(f"   📊 Used: {percentage_used:.1f}% {status}")
            
            # Progress bar
            bar_length = 20
            filled_length = int((percentage_used / 100) * bar_length)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            print(f"   [{bar}]")

    def show_menu(self, user_id):
        while True:
            print("\n" + "="*50)
            print("📊 SMART BUDGET PLANNER")
            print("="*50)
            print("1. 📝 Create Budget")
            print("2. 📋 View Budgets")
            print("3. ⬅️ Back to Money Service")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self.create_budget(user_id)
            elif choice == "2":
                self.view_budgets(user_id)
            elif choice == "3":
                return
            else:
                print("❌ Invalid choice")
            
            input("\nPress Enter to continue...")
