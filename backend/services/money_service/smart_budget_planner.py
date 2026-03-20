from datetime import datetime
from .uplan_engine import UPlanEngine
from .budget_engine import BudgetEngine
from .burn_rate import BurnRateIndicator
from .monthly_report import MonthlyReportGenerator
from .gamification import BudgetGamification
from .leftover_manager import LeftoverBudgetManager

class SmartBudgetPlanner:
    def __init__(self):
        self.uplan_engine = UPlanEngine()
        self.budget_engine = BudgetEngine()
        self.burn_rate = BurnRateIndicator()
        self.monthly_report = MonthlyReportGenerator()
        self.gamification = BudgetGamification()
        self.leftover_manager = LeftoverBudgetManager()
    
    def show_menu(self, user_id):
        """Main menu for Smart Budget Planner"""
        while True:
            print("\n" + "="*70)
            print("🎯 SMART BUDGET PLANNER - U-PLAN FINANCIAL SYSTEM")
            print("="*70)
            print("1. 📋 Create Financial Plan (U-Plan)")
            print("2. 💰 Budget Status & Monitoring")
            print("3. 🔥 Burn Rate Analysis")
            print("4. 📊 Monthly Spending Report")
            print("5. 🏆 Budget Gamification & Rewards")
            print("6. 💵 Leftover Budget Management")
            print("7. 📈 Dynamic Budget Adjustments")
            print("8. ⬅️ Back to Money Service")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self._create_financial_plan(user_id)
            elif choice == "2":
                self._show_budget_status(user_id)
            elif choice == "3":
                self._show_burn_rate(user_id)
            elif choice == "4":
                self._show_monthly_report(user_id)
            elif choice == "5":
                self._show_gamification(user_id)
            elif choice == "6":
                self._manage_leftover_budgets(user_id)
            elif choice == "7":
                self._show_dynamic_adjustments(user_id)
            elif choice == "8":
                return
            else:
                print("❌ Invalid choice")
            
            input("\nPress Enter to continue...")
    
    def _create_financial_plan(self, user_id):
        """Create U-Plan financial plan"""
        result = self.uplan_engine.create_financial_plan(user_id)
        
        if result:
            plan, allocation, category_budgets = result
            print(f"\n✅ Financial plan created successfully!")
            print(f"💡 Your budgets are now active and being monitored")
            
            # Show summary
            summary = self.uplan_engine.get_financial_plan_summary(user_id)
            if summary:
                print(f"\n📊 Plan Summary:")
                print(f"   💰 Monthly Income: ₹{summary['plan']['monthly_income']:,.2f}")
                print(f"   💸 Fixed Expenses: ₹{summary['plan']['fixed_expenses_total']:,.2f}")
                print(f"   💵 Disposable Income: ₹{summary['plan']['disposable_income']:,.2f}")
                print(f"   🎯 Savings Target: ₹{summary['plan']['savings_target']:,.2f}")
    
    def _show_budget_status(self, user_id):
        """Show comprehensive budget status"""
        self.budget_engine.display_budget_status(user_id)
    
    def _show_burn_rate(self, user_id):
        """Show burn rate analysis"""
        self.burn_rate.display_burn_rate_analysis(user_id)
    
    def _show_monthly_report(self, user_id):
        """Show monthly spending report"""
        # Ask for month/year
        current_date = datetime.now()
        print(f"\n📅 Generate report for which month?")
        print(f"Press Enter for current month ({current_date.strftime('%B %Y')})")
        
        month_input = input("Month (e.g., March): ").strip()
        year_input = input("Year (e.g., 2026): ").strip()
        
        month = month_input if month_input else current_date.strftime("%B")
        year = int(year_input) if year_input else current_date.year
        
        self.monthly_report.display_monthly_report(user_id, month, year)
    
    def _show_gamification(self, user_id):
        """Show gamification dashboard"""
        self.gamification.display_reward_dashboard(user_id)
    
    def _manage_leftover_budgets(self, user_id):
        """Manage leftover budgets"""
        print(f"\n" + "="*50)
        print("💵 LEFTOVER BUDGET MANAGEMENT")
        print("="*50)
        print("1. 📋 Check Monthly Leftovers")
        print("2. 🎯 View Goal Jars")
        print("3. 💡 Get Goal Suggestions")
        print("4. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            self.leftover_manager.display_leftover_suggestions(user_id)
        elif choice == "2":
            self.leftover_manager.display_goal_jars(user_id)
        elif choice == "3":
            self.leftover_manager.suggest_goal_jar_ideas(user_id)
    
    def _manage_goal_jars(self, user_id):
        """Manage goal jars"""
        self.leftover_manager.display_goal_jars(user_id)
        
        print(f"\n🎯 GOAL JAR ACTIONS:")
        print("1. Create New Goal Jar")
        print("2. Add Money to Goal Jar")
        print("3. ⬅️ Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            self.leftover_manager._create_custom_goal_jar(user_id)
        elif choice == "2":
            self._add_to_goal_jar(user_id)
    
    def _add_to_goal_jar(self, user_id):
        """Add money to existing goal jar"""
        goal_jars = self.leftover_manager.get_goal_jars_status(user_id)
        
        if not goal_jars:
            print("📭 No goal jars found. Create one first!")
            return
        
        print(f"\n📋 Select Goal Jar:")
        for i, jar in enumerate(goal_jars, 1):
            print(f"{i}. {jar['goal_name']} (₹{jar['current_amount']:,.2f}/₹{jar['target_amount']:,.2f})")
        
        try:
            choice = int(input("\nSelect goal jar: ")) - 1
            if 0 <= choice < len(goal_jars):
                jar = goal_jars[choice]
                try:
                    amount = float(input(f"💰 Amount to add to {jar['goal_name']}: ₹"))
                    if amount > 0:
                        success = self.leftover_manager.db.update_goal_jar(user_id, jar['goal_name'], amount)
                        if success:
                            print(f"✅ Added ₹{amount:.2f} to {jar['goal_name']}")
                        else:
                            print("❌ Failed to add amount")
                    else:
                        print("❌ Amount must be greater than 0")
                except ValueError:
                    print("❌ Invalid amount")
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid selection")
    
    def _show_dynamic_adjustments(self, user_id):
        """Show dynamic budget adjustments"""
        self.budget_engine.display_dynamic_adjustments(user_id)
    
    def integrate_transaction(self, user_id, transaction_data):
        """Integrate new transaction with budget system"""
        # Update budget tracking
        alerts = self.budget_engine.integrate_with_finny_transaction(user_id, transaction_data)
        
        # Check for new rewards
        self.gamification.check_budget_master_reward(user_id)
        self.gamification.check_savings_hero_reward(user_id)
        self.gamification.check_discipline_streak_reward(user_id)
        
        return alerts
    
    def get_dashboard_data(self, user_id):
        """Get comprehensive dashboard data"""
        current_date = datetime.now()
        month = current_date.strftime("%B")
        year = current_date.year
        
        # Financial plan summary
        plan_summary = self.uplan_engine.get_financial_plan_summary(user_id)
        
        # Budget status
        budget_status = self.budget_engine.get_budget_status(user_id)
        
        # Burn rate
        burn_rate_data = self.burn_rate.get_overall_burn_rate(user_id)
        
        # Monthly report
        monthly_data = self.monthly_report.generate_monthly_report(user_id, month, year)
        
        # Rewards
        rewards_data = self.gamification.get_user_rewards(user_id)
        
        # Goal jars
        goal_jars = self.leftover_manager.get_goal_jars_status(user_id)
        
        return {
            'plan_summary': plan_summary,
            'budget_status': budget_status,
            'burn_rate': burn_rate_data,
            'monthly_report': monthly_data,
            'rewards': rewards_data,
            'goal_jars': goal_jars,
            'current_month': month,
            'current_year': year
        }
