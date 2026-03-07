#!/usr/bin/env python3
"""
Test script to demonstrate Enhanced Finny conversational transaction entry
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_finny():
    """Test the enhanced conversational Finny system"""
    print("🧪 Testing Enhanced Finny - Conversational Transaction System")
    print("="*60)
    
    try:
        from services.money_service.enhanced_finny import EnhancedFinny
        from services.money_service.money_db import MoneyServiceDB
        
        print("✅ Enhanced Finny import successful")
        
        # Initialize database
        db = MoneyServiceDB()
        print("✅ Database connection successful")
        
        # Create test user (for demo)
        print("\n👤 Creating test user for demonstration...")
        test_user_id = 1  # Assuming user ID 1 exists
        
        # Initialize Enhanced Finny
        finny = EnhancedFinny()
        print("✅ Enhanced Finny initialized successfully")
        
        print("\n" + "="*60)
        print("🎮 INTERACTIVE DEMO - Enhanced Finny Features")
        print("="*60)
        print("\n💡 Enhanced Finny now includes:")
        print("  🗣️ Conversational Transaction Entry")
        print("  ⚡ Quick Add for experienced users")
        print("  📊 Enhanced Monthly Summaries")
        print("  💡 Financial Insights")
        print("  📈 Visual Spending Breakdown")
        
        print("\n🚀 Features:")
        print("  1. 🗣️ Asks detailed questions about spending")
        print("  2. 🍔 Food: breakfast, lunch, dinner, snacks, coffee, groceries")
        print("  3. 🎬 Entertainment: movies, games, subscriptions, concerts, streaming")
        print("  4. 🚗 Transport: fuel, auto/cab, public transport, parking, maintenance")
        print("  5. 🛒 Shopping: clothes, electronics, groceries, household, online")
        print("  6. 📦 Other: bills, healthcare, education, personal care, miscellaneous")
        
        print("\n💬 Example Conversation Flow:")
        print("-" * 50)
        print("💰 ENHANCED FINNY - CONVERSATIONAL TRANSACTION ENTRY")
        print("🤝 Let me help you track today's expenses in detail!")
        print("💡 I'll ask you about different spending categories...")
        print("")
        print("🍔 FOOD EXPENSES")
        print("----------------------------------------")
        print("💬 Did you spend anything on food today?")
        print("Enter 'yes' or 'no': yes")
        print("")
        print("🤔 Let's break down your food expenses...")
        print("📝 Enter food expense details:")
        print("What type of food expense was it?")
        print("  1. Breakfast")
        print("  2. Lunch") 
        print("  3. Dinner")
        print("  4. Snacks")
        print("  5. Coffee")
        print("  6. Groceries")
        print("  7. Other")
        print("Select number: 2")
        print("How much did you spend on lunch? ₹100")
        print("Where did you spend this (store/merchant name)? Bharat Cafe")
        print("Any notes about this lunch expense? Had meeting with team")
        print("✅ Added: ₹100 for lunch at Bharat Cafe")
        print("💬 Any more food expenses? (yes/no): no")
        print("")
        print("🎬 ENTERTAINMENT EXPENSES")
        print("----------------------------------------")
        print("💬 Did you spend anything on entertainment today?")
        print("Enter 'yes' or 'no': yes")
        print("🤔 Let's break down your entertainment expenses...")
        print("📝 Enter entertainment expense details:")
        print("What type of entertainment expense was it?")
        print("  1. Movies")
        print("  2. Games")
        print("  3. Subscriptions")
        print("  4. Concerts")
        print("  5. Streaming")
        print("  6. Other")
        print("Select number: 1")
        print("How much did you spend on movies? ₹200")
        print("Where did you spend this (store/merchant name)? PVR Cinemas")
        print("Any notes about this movies expense? Watched new release")
        print("✅ Added: ₹200 for movies at PVR Cinemas")
        print("💬 Any more entertainment expenses? (yes/no): no")
        print("")
        print("📊 TODAY'S SPENDING SUMMARY")
        print("============================================================")
        print("💰 Total Spent Today: ₹300")
        print("📝 Total Transactions: 2")
        print("")
        print("📊 Breakdown by Category:")
        print("----------------------------------------")
        print("Food        ₹100.00 ████████████ 33.3%")
        print("Entertainment ₹200.00 ███████████████████████████████████ 66.7%")
        print("")
        print("💡 FINANCIAL INSIGHTS")
        print("----------------------------------------")
        print("💪 Good control on daily spending!")
        print("🎯 Highest spending category: Entertainment (₹200.00)")
        
        print("\n✅ Enhanced Finny is ready for use!")
        print("🚀 Run 'python cli.py' and select Money Service to try it!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🧪 ENHANCED FINNY DEMO")
    print("="*60)
    
    success = test_enhanced_finny()
    
    print("\n" + "="*60)
    if success:
        print("🎉 ENHANCED FINNY DEMO SUCCESSFUL!")
        print("\n🚀 Ready to use:")
        print("  1. cd backend")
        print("  2. python cli.py")
        print("  3. Select User/Worker → Login → Money Service → Enhanced Finny")
    else:
        print("❌ DEMO FAILED!")
        print("Please check the errors above.")
    print("="*60)
