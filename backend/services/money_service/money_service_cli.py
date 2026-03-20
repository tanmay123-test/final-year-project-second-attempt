from .unified_finny import unified_finny
from .ai_financial_assistant import ai_financial_assistant

def money_service_menu(user_id, role="user"):
    """
    Money Service Main Menu - Same for both Users and Workers
    """
    while True:
        print("\n" + "="*60)
        print("💰 MONEY SERVICE")
        print("="*60)
        print(f"👤 Logged in as: {role.title()}")
        print("-" * 60)
        print("1. 💳 Unified Finny - Smart Transaction Tracker")
        print("2. 📊 Smart Budget Planner")
        print("3. 🏦 Smart Loan Analyzer")
        print("4. 🏆 Goal Jar - Savings Tracker")
        print("5. 🤖 AI Financial Assistant")
        print("6. ⬅️ Back to Services")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            unified_finny.show_menu(user_id)
        elif choice == "2":
            from .budget_planner import BudgetPlanner
            budget_planner = BudgetPlanner()
            budget_planner.show_menu(user_id)
        elif choice == "3":
            from .smart_loan_analyzer import SmartLoanAnalyzer
            loan_analyzer = SmartLoanAnalyzer()
            loan_analyzer.show_menu(user_id)
        elif choice == "4":
            from .goal_jar import GoalJar
            goal_jar = GoalJar()
            goal_jar.show_menu(user_id)
        elif choice == "5":
            ai_financial_assistant.show_menu(user_id)
        elif choice == "6":
            return
        else:
            print("❌ Invalid choice")
