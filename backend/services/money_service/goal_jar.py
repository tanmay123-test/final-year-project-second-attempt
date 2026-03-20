from datetime import datetime
from .money_db import MoneyServiceDB

class GoalJar:
    def __init__(self):
        self.db = MoneyServiceDB()

    def create_goal(self, user_id):
        print("\n" + "="*50)
        print("🏆 GOAL JAR - CREATE SAVINGS GOAL")
        print("="*50)
        
        goal_name = input("Goal Name (e.g., Buy Bike, Vacation, Emergency Fund): ").strip()
        if not goal_name:
            print("❌ Goal name is required")
            return False
        
        try:
            target_amount = float(input("Target Amount (₹): ").strip())
            if target_amount <= 0:
                print("❌ Target amount must be positive")
                return False
                
            monthly_saving = float(input("Monthly Saving (₹): ").strip())
            if monthly_saving <= 0:
                print("❌ Monthly saving must be positive")
                return False
                
        except ValueError:
            print("❌ Invalid amount")
            return False
        
        # Calculate estimated time to reach goal
        months_needed = target_amount / monthly_saving
        years_needed = months_needed / 12
        
        # Create goal
        goal_id = self.db.create_goal_jar(user_id, goal_name, target_amount, monthly_saving)
        
        print(f"\n✅ Goal created successfully!")
        print(f"🏆 Goal ID: {goal_id}")
        print(f"🎯 Goal: {goal_name}")
        print(f"💰 Target: ₹{target_amount:,.2f}")
        print(f"💵 Monthly Saving: ₹{monthly_saving:,.2f}")
        print(f"📅 Estimated Time: {months_needed:.1f} months ({years_needed:.1f} years)")
        
        return True

    def view_goals(self, user_id):
        print("\n" + "="*50)
        print("🏆 GOAL JAR - MY SAVINGS GOALS")
        print("="*50)
        
        goals = self.db.get_goal_jars(user_id)
        
        if not goals:
            print("📭 No savings goals found")
            print("💡 Create your first goal!")
            return
        
        print(f"\nActive Goals: {len(goals)}\n")
        
        for idx, goal in enumerate(goals, 1):
            goal_id = goal[0]
            goal_name = goal[2]
            target_amount = goal[3]
            current_amount = goal[4]
            monthly_saving = goal[5]
            created_date = goal[6]
            
            progress_percentage = (current_amount / target_amount) * 100 if target_amount > 0 else 0
            remaining_amount = target_amount - current_amount
            months_remaining = remaining_amount / monthly_saving if monthly_saving > 0 else float('inf')
            
            # Status
            if progress_percentage >= 100:
                status = "🎉 COMPLETED!"
            elif progress_percentage >= 75:
                status = "🔥 Almost there!"
            elif progress_percentage >= 50:
                status = "💪 Halfway there!"
            elif progress_percentage >= 25:
                status = "📈 Good progress!"
            else:
                status = "🌱 Just started"
            
            print(f"[{idx}] {goal_name}")
            print(f"    💰 Progress: ₹{current_amount:,.2f} / ₹{target_amount:,.2f}")
            print(f"    📊 {progress_percentage:.1f}% Complete {status}")
            
            # Progress bar
            bar_length = 20
            filled_length = int((progress_percentage / 100) * bar_length)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            print(f"    [{bar}]")
            
            print(f"    💵 Remaining: ₹{remaining_amount:,.2f}")
            if months_remaining != float('inf'):
                print(f"    📅 {months_remaining:.1f} months remaining at current rate")
            print(f"    💸 Monthly saving: ₹{monthly_saving:,.2f}")
            print("-" * 40)

    def add_to_goal(self, user_id):
        print("\n" + "="*50)
        print("➕ GOAL JAR - ADD TO GOAL")
        print("="*50)
        
        goals = self.db.get_goal_jars(user_id)
        
        if not goals:
            print("📭 No goals found. Create a goal first!")
            return False
        
        print("Select a goal to add to:")
        for idx, goal in enumerate(goals, 1):
            goal_name = goal[2]
            current_amount = goal[4]
            target_amount = goal[3]
            print(f"[{idx}] {goal_name} (₹{current_amount:.2f} / ₹{target_amount:.2f})")
        
        try:
            choice = int(input("\nSelect goal: ").strip())
            if choice < 1 or choice > len(goals):
                print("❌ Invalid choice")
                return False
                
            amount = float(input("Amount to add (₹): ").strip())
            if amount <= 0:
                print("❌ Amount must be positive")
                return False
                
        except ValueError:
            print("❌ Invalid input")
            return False
        
        selected_goal = goals[choice - 1]
        goal_id = selected_goal[0]
        goal_name = selected_goal[2]
        
        # Update goal
        self.db.update_goal_jar(goal_id, amount)
        
        print(f"\n✅ Added ₹{amount:.2f} to '{goal_name}'")
        
        # Show updated progress
        updated_goals = self.db.get_goal_jars(user_id)
        updated_goal = next(g for g in updated_goals if g[0] == goal_id)
        
        new_progress = (updated_goal[4] / updated_goal[3]) * 100
        print(f"📊 New Progress: {new_progress:.1f}% (₹{updated_goal[4]:.2f} / ₹{updated_goal[3]:.2f})")
        
        return True

    def show_menu(self, user_id):
        while True:
            print("\n" + "="*50)
            print("🏆 GOAL JAR - SAVINGS TRACKER")
            print("="*50)
            print("1. 🎯 Create Goal")
            print("2. 📋 View Goals")
            print("3. ➕ Add to Goal")
            print("4. ⬅️ Back to Money Service")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self.create_goal(user_id)
            elif choice == "2":
                self.view_goals(user_id)
            elif choice == "3":
                self.add_to_goal(user_id)
            elif choice == "4":
                return
            else:
                print("❌ Invalid choice")
            
            input("\nPress Enter to continue...")
