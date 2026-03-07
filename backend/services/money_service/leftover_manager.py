from datetime import datetime, timedelta
from .uplan_database import UPlanDatabase

class LeftoverBudgetManager:
    def __init__(self):
        self.db = UPlanDatabase()
    
    def check_monthly_leftover(self, user_id):
        """Check leftover budget at end of month"""
        current_date = datetime.now()
        
        # Check if it's near end of month (last 3 days)
        days_in_month = self._get_days_in_month(current_date.month, current_date.year)
        days_remaining = days_in_month - current_date.day
        
        if days_remaining > 3:
            return None, "Not yet time for leftover budget analysis"
        
        month = current_date.strftime("%B")
        year = current_date.year
        
        # Get budget status
        budgets = self.db.get_budget_status(user_id, month, year)
        
        if not budgets:
            return None, "No budgets set"
        
        leftover_suggestions = []
        total_leftover = 0
        
        for budget in budgets:
            if budget['remaining'] > 0:
                leftover_suggestions.append({
                    'category': budget['category'],
                    'budget_amount': budget['budget_amount'],
                    'spent_amount': budget['spent'],
                    'remaining_amount': budget['remaining'],
                    'suggestion': f"You saved ₹{budget['remaining']:.2f} in {budget['category']}. Move this to your savings jar?"
                })
                total_leftover += budget['remaining']
        
        return {
            'leftover_suggestions': leftover_suggestions,
            'total_leftover': total_leftover,
            'month': month,
            'year': year,
            'days_remaining': days_remaining
        }, f"Found {len(leftover_suggestions)} categories with leftover budget"
    
    def move_leftover_to_goal_jar(self, user_id, category, amount):
        """Move leftover budget to goal jar"""
        # Create or update goal jar
        goal_name = f"{category} Savings"
        
        # Check if goal jar exists
        goal_jars = self.db.get_goal_jars(user_id)
        existing_goal = next((g for g in goal_jars if g['goal_name'] == goal_name), None)
        
        if existing_goal:
            # Update existing goal
            success = self.db.update_goal_jar(user_id, goal_name, amount)
            if success:
                return True, f"✅ Added ₹{amount:.2f} to {goal_name}"
            else:
                return False, "❌ Failed to update goal jar"
        else:
            # Create new goal jar with target amount (double the amount as default)
            target_amount = amount * 2
            goal_id = self.db.create_goal_jar(user_id, goal_name, target_amount)
            
            if goal_id:
                # Update with initial amount
                self.db.update_goal_jar(user_id, goal_name, amount)
                return True, f"✅ Created {goal_name} goal jar with ₹{amount:.2f}"
            else:
                return False, "❌ Failed to create goal jar"
    
    def get_goal_jars_status(self, user_id):
        """Get status of all goal jars"""
        goal_jars = self.db.get_goal_jars(user_id)
        
        for jar in goal_jars:
            # Add status indicators
            if jar['percentage'] >= 100:
                jar['status'] = 'COMPLETED'
                jar['status_color'] = '🟢'
            elif jar['percentage'] >= 75:
                jar['status'] = 'NEAR_GOAL'
                jar['status_color'] = '🟡'
            elif jar['percentage'] >= 50:
                jar['status'] = 'IN_PROGRESS'
                jar['status_color'] = '🔵'
            else:
                jar['status'] = 'JUST_STARTED'
                jar['status_color'] = '⚪'
            
            # Add progress bar
            bar_length = 20
            filled_length = min(int(jar['percentage'] / 5), bar_length)
            jar['progress_bar'] = '█' * filled_length + '░' * (bar_length - filled_length)
        
        return goal_jars
    
    def display_leftover_suggestions(self, user_id):
        """Display leftover budget suggestions"""
        leftover_data, message = self.check_monthly_leftover(user_id)
        
        if not leftover_data:
            print(f"\n💡 {message}")
            return
        
        print(f"\n" + "="*70)
        print(f"💰 LEFTOVER BUDGET SUGGESTIONS - {leftover_data['month']} {leftover_data['year']}")
        print("="*70)
        print(f"📅 {leftover_data['days_remaining']} days remaining in month")
        print(f"💰 Total Leftover: ₹{leftover_data['total_leftover']:,.2f}")
        
        if not leftover_data['leftover_suggestions']:
            print("\n📭 No leftover budget found in any category")
            return
        
        print(f"\n📋 CATEGORY LEFTOVERS")
        print("-" * 50)
        
        for i, suggestion in enumerate(leftover_data['leftover_suggestions'], 1):
            print(f"\n{i}. 📂 {suggestion['category'].upper()}")
            print("-" * 30)
            print(f"💰 Budget: ₹{suggestion['budget_amount']:,.2f}")
            print(f"💸 Spent: ₹{suggestion['spent_amount']:,.2f}")
            print(f"💵 Remaining: ₹{suggestion['remaining_amount']:,.2f}")
            print(f"💡 {suggestion['suggestion']}")
        
        # Ask for action
        print(f"\n🎯 ACTION OPTIONS")
        print("-" * 50)
        print("1. Move all leftovers to goal jars")
        print("2. Select specific categories to move")
        print("3. Skip for now")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            self._move_all_leftovers(user_id, leftover_data['leftover_suggestions'])
        elif choice == "2":
            self._select_categories_to_move(user_id, leftover_data['leftover_suggestions'])
        else:
            print("⏭️ Skipped leftover budget management")
    
    def _move_all_leftovers(self, user_id, suggestions):
        """Move all leftover amounts to goal jars"""
        print(f"\n🔄 Moving leftovers to goal jars...")
        
        moved_count = 0
        total_moved = 0
        
        for suggestion in suggestions:
            success, message = self.move_leftover_to_goal_jar(
                user_id, suggestion['category'], suggestion['remaining_amount']
            )
            
            if success:
                moved_count += 1
                total_moved += suggestion['remaining_amount']
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        
        print(f"\n🎉 Successfully moved {moved_count} leftovers totaling ₹{total_moved:,.2f} to goal jars!")
    
    def _select_categories_to_move(self, user_id, suggestions):
        """Let user select specific categories to move"""
        print(f"\n📋 Select categories to move (comma-separated numbers):")
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion['category']} (₹{suggestion['remaining_amount']:,.2f})")
        
        try:
            selected = input("Enter numbers: ").strip()
            if not selected:
                return
            
            selected_indices = [int(x.strip()) - 1 for x in selected.split(',')]
            
            moved_count = 0
            total_moved = 0
            
            for index in selected_indices:
                if 0 <= index < len(suggestions):
                    suggestion = suggestions[index]
                    success, message = self.move_leftover_to_goal_jar(
                        user_id, suggestion['category'], suggestion['remaining_amount']
                    )
                    
                    if success:
                        moved_count += 1
                        total_moved += suggestion['remaining_amount']
                        print(f"✅ {message}")
                    else:
                        print(f"❌ {message}")
            
            print(f"\n🎉 Successfully moved {moved_count} leftovers totaling ₹{total_moved:,.2f} to goal jars!")
            
        except (ValueError, IndexError):
            print("❌ Invalid selection")
    
    def display_goal_jars(self, user_id):
        """Display all goal jars with progress"""
        goal_jars = self.get_goal_jars_status(user_id)
        
        if not goal_jars:
            print("\n📭 No goal jars created yet")
            return
        
        print(f"\n" + "="*70)
        print("🏆 GOAL JARS STATUS")
        print("="*70)
        
        for jar in goal_jars:
            print(f"\n🎯 {jar['goal_name'].upper()}")
            print("-" * 40)
            print(f"💰 Target: ₹{jar['target_amount']:,.2f}")
            print(f"💵 Current: ₹{jar['current_amount']:,.2f}")
            print(f"📊 Progress: {jar['percentage']:.1f}%")
            print(f"   {jar['progress_bar']} {jar['status_color']} {jar['status']}")
            
            if jar['status'] == 'COMPLETED':
                print(f"🎉 Congratulations! Goal achieved!")
            elif jar['status'] == 'NEAR_GOAL':
                remaining = jar['target_amount'] - jar['current_amount']
                print(f"🔥 Almost there! ₹{remaining:.2f} to go!")
            else:
                remaining = jar['target_amount'] - jar['current_amount']
                print(f"💡 ₹{remaining:.2f} remaining to reach goal")
    
    def suggest_goal_jar_ideas(self, user_id):
        """Suggest goal jar ideas based on spending patterns"""
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year
        
        # Get spending data
        spending_data = self.db.get_monthly_spending_data(user_id, month, year)
        
        if not spending_data:
            print("📭 No spending data available for suggestions")
            return
        
        print(f"\n" + "="*70)
        print("💡 GOAL JAR SUGGESTIONS")
        print("="*70)
        
        suggestions = []
        
        # High spending categories
        for item in spending_data:
            if item['total'] > 2000:  # Threshold for significant spending
                monthly_target = item['total'] * 0.8  # 80% of current spending as goal
                suggestions.append({
                    'category': item['category'],
                    'current_spending': item['total'],
                    'suggested_target': monthly_target,
                    'reason': f"Reduce {item['category']} spending by 20%"
                })
        
        if suggestions:
            print(f"\n🎯 BASED ON YOUR SPENDING PATTERNS:")
            print("-" * 50)
            
            for i, suggestion in enumerate(suggestions, 1):
                print(f"\n{i}. 📂 {suggestion['category'].title()}")
                print(f"   💸 Current Spending: ₹{suggestion['current_spending']:,.2f}")
                print(f"   🎯 Suggested Target: ₹{suggestion['suggested_target']:,.2f}")
                print(f"   💡 Reason: {suggestion['reason']}")
        
        # General suggestions
        print(f"\n🌟 GENERAL GOAL IDEAS:")
        print("-" * 50)
        print("🏖️ Vacation Fund - Save for your dream vacation")
        print("💻 Emergency Fund - Build 6-month expense cushion")
        print("🎁 Gift Fund - Save for special occasions")
        print("🏠 Home Improvement - Save for home projects")
        print("📚 Education Fund - Invest in learning and development")
        print("🚗 Vehicle Fund - Save for car maintenance or upgrade")
        print("💰 Investment Fund - Build your investment portfolio")
        
        create_goal = input("\n💭 Would you like to create a new goal jar? (yes/no): ").strip().lower()
        if create_goal in ['yes', 'y']:
            self._create_custom_goal_jar(user_id)
    
    def _create_custom_goal_jar(self, user_id):
        """Create a custom goal jar"""
        print(f"\n🎯 CREATE CUSTOM GOAL JAR")
        print("-" * 40)
        
        goal_name = input("📝 Goal name: ").strip()
        if not goal_name:
            print("❌ Goal name is required")
            return
        
        try:
            target_amount = float(input("💰 Target amount: ₹").strip())
            if target_amount <= 0:
                print("❌ Target amount must be greater than 0")
                return
        except ValueError:
            print("❌ Invalid target amount")
            return
        
        # Create goal jar
        goal_id = self.db.create_goal_jar(user_id, goal_name, target_amount)
        
        if goal_id:
            print(f"✅ Created '{goal_name}' goal jar with target ₹{target_amount:,.2f}")
            
            # Ask if want to add initial amount
            add_initial = input("💵 Add initial amount? (yes/no): ").strip().lower()
            if add_initial in ['yes', 'y']:
                try:
                    initial_amount = float(input("💰 Initial amount: ₹").strip())
                    if initial_amount > 0:
                        self.db.update_goal_jar(user_id, goal_name, initial_amount)
                        print(f"✅ Added ₹{initial_amount:.2f} to {goal_name}")
                except ValueError:
                    print("❌ Invalid amount")
        else:
            print("❌ Failed to create goal jar")
    
    def _get_days_in_month(self, month, year):
        """Get number of days in a month"""
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        else:  # February
            return 29 if (year % 400 == 0 or (year % 100 != 0 and year % 4 == 0)) else 28
