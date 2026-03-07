#!/usr/bin/env python3
"""
Test script to verify Money Service functionality in backend
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_money_service_modules():
    """Test all Money Service modules"""
    print("🧪 Testing Money Service Modules in Backend...")
    
    try:
        # Test imports
        from services.money_service.finny import Finny
        from services.money_service.budget_planner import BudgetPlanner
        from services.money_service.loan_analyzer import LoanAnalyzer
        from services.money_service.goal_jar import GoalJar
        from services.money_service.ai_groups import AIGroups
        from services.money_service.money_service_cli import money_service_menu
        
        print("✅ All imports successful")
        
        # Test initialization
        finny = Finny()
        budget = BudgetPlanner()
        loan = LoanAnalyzer()
        goal = GoalJar()
        ai = AIGroups()
        
        print("✅ All modules initialized successfully")
        
        # Test database
        from services.money_service.money_db import MoneyServiceDB
        db = MoneyServiceDB()
        print("✅ Database connection successful")
        
        print("\n🎉 Money Service is ready in Backend!")
        print("\n📋 Available Features:")
        print("  1. 💳 Finny - Transaction Management")
        print("  2. 📊 Smart Budget Planner")
        print("  3. 🏦 Smart Loan Analyzer")
        print("  4. 🏆 Goal Jar - Savings Tracker")
        print("  5. 🤖 AI Groups (Placeholder)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_auth_modules():
    """Test authentication modules"""
    print("\n🧪 Testing Authentication Modules in Backend...")
    
    try:
        from auth.auth_db import AuthDB
        from auth.worker_auth import worker_menu, worker_login, worker_signup
        
        print("✅ Auth imports successful")
        
        # Test database
        auth_db = AuthDB()
        print("✅ Auth database connection successful")
        
        print("✅ Authentication modules ready!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🧪 MONEY SERVICE PHASE-1 TESTING - BACKEND")
    print("="*60)
    
    money_ok = test_money_service_modules()
    auth_ok = test_auth_modules()
    
    print("\n" + "="*60)
    if money_ok and auth_ok:
        print("🎉 ALL TESTS PASSED!")
        print("\n🚀 You can now run:")
        print("  python cli.py")
        print("\nAnd navigate to:")
        print("  1. User/Worker → Login → Money Service")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the errors above.")
    print("="*60)
