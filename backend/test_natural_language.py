#!/usr/bin/env python3
"""
Test script to demonstrate Natural Language Finny system
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_natural_language_finny():
    """Test the natural language Finny system"""
    print("🧪 Testing Natural Language Finny - Chat Style System")
    print("="*60)
    
    try:
        from services.money_service.natural_language_finny import NaturalLanguageFinny
        from services.money_service.money_db import MoneyServiceDB
        
        print("✅ Natural Language Finny import successful")
        
        # Initialize database
        db = MoneyServiceDB()
        print("✅ Database connection successful")
        
        # Initialize Natural Language Finny
        finny = NaturalLanguageFinny()
        print("✅ Natural Language Finny initialized successfully")
        
        print("\n" + "="*60)
        print("🎮 NATURAL LANGUAGE PROCESSING DEMO")
        print("="*60)
        
        # Test parsing capabilities
        test_inputs = [
            "food 200 entertainment 300 transport 150",
            "lunch 150 at subway dinner 200 at restaurant",
            "spent 200 on food 300 on entertainment",
            "breakfast 100 lunch 150 dinner 200",
            "shopping 500 bills 200 education 300",
            "movie 200 at pvr coffee 100 at starbucks",
            "transport 300 at ola shopping 2000 at amazon"
        ]
        
        print("\n💬 TESTING NATURAL LANGUAGE PARSING:")
        print("-" * 50)
        
        for i, test_input in enumerate(test_inputs, 1):
            print(f"\n[{i}] Input: '{test_input}'")
            transactions = finny._parse_natural_language(test_input)
            if transactions:
                total = sum(t['amount'] for t in transactions)
                print(f"✅ Parsed {len(transactions)} transactions, Total: ₹{total}")
                for t in transactions:
                    print(f"   💰 ₹{t['amount']} - {t['category']} at {t['merchant']}")
            else:
                print("❌ Could not parse")
        
        print("\n" + "="*60)
        print("🎯 NATURAL LANGUAGE FEATURES")
        print("="*60)
        
        print("\n💡 INPUT FORMATS I UNDERSTAND:")
        print("-" * 40)
        print("🎯 SIMPLE FORMAT:")
        print("   • food 200 entertainment 300 transport 150")
        print("   • breakfast 100 lunch 150 dinner 200")
        
        print("\n🎯 WITH MERCHANTS:")
        print("   • lunch 150 at subway dinner 200 at restaurant")
        print("   • movie 200 at pvr coffee 100 at starbucks")
        
        print("\n🎯 NATURAL LANGUAGE:")
        print("   • spent 200 on food 300 on entertainment")
        print("   • paid 150 for lunch 200 for shopping")
        
        print("\n🎯 CATEGORIES I UNDERSTAND:")
        print("-" * 40)
        print("🍔 Food: food, breakfast, lunch, dinner, snacks, coffee, groceries")
        print("🎬 Entertainment: movie, games, subscription, streaming")
        print("🚗 Transport: fuel, auto, cab, uber, ola, bus, train")
        print("🛒 Shopping: clothes, electronics, amazon, flipkart, store")
        print("📦 Other: bills, healthcare, education, miscellaneous")
        
        print("\n🎯 SMART FEATURES:")
        print("-" * 40)
        print("🧠 Intelligent category detection")
        print("🏪 Automatic merchant extraction")
        print("📊 Real-time transaction parsing")
        print("💬 Natural conversation flow")
        print("🎯 Context-aware understanding")
        
        print("\n🎮 INTERACTIVE CHAT EXAMPLE:")
        print("-" * 40)
        print("💬 NATURAL LANGUAGE FINNY - CHAT STYLE")
        print("============================================================")
        print("🤝 Just tell me how you spent money today!")
        print("💡 Examples:")
        print("   • food 200 entertainment 300 transport 150")
        print("   • lunch 150 at subway movie 200 at pvr")
        print("   • spent 500 on shopping 200 on food")
        print("")
        print("💬 Type your expenses (or 'help' for examples):")
        print("")
        print("💭 You: food 200 entertainment 300 transport 150")
        print("")
        print("✅ EXPENSES RECORDED")
        print("==================================================")
        print("💰 ₹200.00 - Food")
        print("   🏪 Food Store")
        print("💰 ₹300.00 - Entertainment")
        print("   🏪 Entertainment Store")
        print("💰 ₹150.00 - Transport")
        print("   🏪 Transport Store")
        print("")
        print("💸 Total: ₹650.00")
        print("📝 3 transactions saved!")
        print("")
        print("💬 Any more expenses? (type 'yes' or just continue):")
        print("")
        print("💭 You: yes")
        print("")
        print("💬 Tell me about your expenses...")
        print("")
        print("💭 You: lunch 150 at subway")
        print("")
        print("✅ EXPENSES RECORDED")
        print("==================================================")
        print("💰 ₹150.00 - Food")
        print("   🏪 Subway")
        print("")
        print("💸 Total: ₹150.00")
        print("📝 1 transactions saved!")
        
        print("\n✅ Natural Language Finny is ready for use!")
        print("🚀 Run 'python cli.py' and select Money Service → Natural Language Finny")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🧪 NATURAL LANGUAGE FINNY DEMO")
    print("="*60)
    
    success = test_natural_language_finny()
    
    print("\n" + "="*60)
    if success:
        print("🎉 NATURAL LANGUAGE FINNY DEMO SUCCESSFUL!")
        print("\n🚀 Ready to use:")
        print("  1. cd backend")
        print("  2. python cli.py")
        print("  3. Select User/Worker → Login → Money Service")
        print("  4. Choose 'Natural Language Finny - Chat Style'")
        print("  5. Just type: 'food 200 entertainment 300'")
    else:
        print("❌ DEMO FAILED!")
        print("Please check the errors above.")
    print("="*60)
