from .enhanced_finny import EnhancedFinny
from .natural_language_finny import NaturalLanguageFinny
from .intelligent_finny import IntelligentFinny as IntelligentFinnyMain
from .budget_planner import BudgetPlanner
from .smart_loan_analyzer import SmartLoanAnalyzer
from .goal_jar.smart_goal_jar import SmartG
from .ai_groups import AIGroups

def money_service_menu(user_id, role="user"):
    """
    Money Service Main Menu - Same for both Users and Workers
    """
    finny = EnhancedFinny()
    natural_finny = NaturalLanguageFinny()
    intelligent_finny = IntelligentFinnyMain()
    budget_planner = BudgetPlanner()
    loan_analyzer = SmartLoanAnalyzer()
    goal_jar = SmartG()
    ai_groups = AIGroups()
    
    while True:
        print("\n" + "="*60)
        print("💰 MONEY SERVICE")
        print("="*60)
        print(f"👤 Logged in as: {role.title()}")
        print("-" * 60)
        print("1. 💳 Enhanced Finny - Conversational Transaction Tracker")
        print("2. 💬 Natural Language Finny - Chat Style")
        print("3. 🧠 Intelligent Finny - Advanced Analytics")
        print("4. 📊 Smart Budget Planner")
        print("5. 🏦 Smart Loan Analyzer")
        print("6. 🏆 Goal Jar - Savings Tracker")
        print("7. 🤖 AI Groups")
        print("8. ⬅️ Back to Services")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            finny.show_menu(user_id)
        elif choice == "2":
            natural_finny.show_menu(user_id)
        elif choice == "3":
            intelligent_finny.show_menu(user_id)
        elif choice == "4":
            budget_planner.show_menu(user_id)
        elif choice == "5":
            loan_analyzer.show_menu(user_id)
        elif choice == "6":
            goal_jar.show_menu(user_id)
        elif choice == "7":
            ai_groups.show_menu(user_id)
        elif choice == "8":
            return
        else:
            print("❌ Invalid choice")
