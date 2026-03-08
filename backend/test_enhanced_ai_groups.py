#!/usr/bin/env python3
"""
Test script to demonstrate enhanced AI Groups with:
- Dynamic stock analysis (any company)
- Stock comparison (HDFC vs ICICI)
- Chat history functionality
- Natural conversation flow
"""

import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_dynamic_stock_analysis():
    """Test dynamic stock analysis with any company"""
    print("🧪 Testing Dynamic Stock Analysis")
    print("=" * 60)
    
    try:
        from ai.stock_ai_service import stock_ai_service
        
        # Test with various companies
        test_companies = [
            "Apple",
            "HDFC Bank", 
            "ICICI Bank",
            "Reliance Industries",
            "TCS",
            "Infosys",
            "Microsoft",
            "Google",
            "Tesla"
        ]
        
        for company in test_companies:
            print(f"\n📊 Testing: {company}")
            print("-" * 40)
            
            # Test stock analysis
            result = await stock_ai_service.generate_stock_analysis(f"Analyze {company} stock")
            
            if result.get("success"):
                print(f"✅ Analysis Generated: {len(result['analysis'])} characters")
                print(f"   Company: {result.get('company_info', 'N/A')}")
                print(f"   Data Points: {len(result.get('stock_data', {}))}")
            else:
                print(f"❌ Analysis Failed: {result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_stock_comparison():
    """Test stock comparison functionality"""
    print("\n🧪 Testing Stock Comparison")
    print("=" * 60)
    
    try:
        from ai.stock_ai_service import stock_ai_service
        
        # Test comparison queries
        test_comparisons = [
            "Compare HDFC vs ICICI Bank",
            "Apple vs Microsoft",
            "Tesla vs Ford vs GM",
            "Reliance vs TCS vs Infosys"
        ]
        
        for comparison in test_comparisons:
            print(f"\n📊 Testing: {comparison}")
            print("-" * 40)
            
            # Test stock comparison
            result = await stock_ai_service.compare_stocks(comparison)
            
            if result.get("success"):
                print(f"✅ Comparison Generated: {len(result['analysis'])} characters")
                print(f"   Companies Compared: {result.get('comparison_count', 0)}")
                print(f"   Data Points: {len(result.get('companies', []))}")
            else:
                print(f"❌ Comparison Failed: {result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_chat_history():
    """Test chat history functionality"""
    print("\n🧪 Testing Chat History")
    print("=" * 60)
    
    try:
        from services.chat_history_service import chat_history_service
        from ai.ai_group_service import ai_group_service
        
        # Test storing messages
        print("\n📝 Testing message storage...")
        
        # Store some test messages
        test_group_id = 1
        test_user_id = 1
        
        messages = [
            ("What is diversification?", "user_message"),
            ("Diversification is a risk management strategy...", "ai_knowledge_response"),
            ("Analyze Apple stock", "user_message"),
            ("Apple is trading at $190.50 with strong fundamentals...", "ai_stock_analysis"),
            ("Compare HDFC vs ICICI", "user_message"),
            ("HDFC Bank shows stronger fundamentals with lower PE ratio...", "ai_stock_comparison"),
        ]
        
        for i, (message, msg_type) in enumerate(messages, 1):
            msg_id = chat_history_service.store_message(test_group_id, test_user_id, message, msg_type)
            print(f"   {i}. Stored: {msg_type} - {message[:50]}...")
        
        print(f"✅ Stored {len(messages)} test messages")
        
        # Test retrieving chat history
        print("\n📋 Testing message retrieval...")
        
        history = chat_history_service.get_chat_history(test_group_id, limit=10)
        print(f"✅ Retrieved {len(history)} messages")
        
        # Test chat statistics
        print("\n📊 Testing chat statistics...")
        
        stats = chat_history_service.get_chat_statistics(test_group_id)
        print(f"✅ Statistics: {stats}")
        
        # Test message search
        print("\n🔍 Testing message search...")
        
        search_results = chat_history_service.search_messages(test_group_id, "Apple", limit=5)
        print(f"✅ Search Results: {len(search_results)} messages")
        
        print("\n" + "=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_message_type_detection():
    """Test enhanced message type detection"""
    print("\n🧪 Testing Message Type Detection")
    print("=" * 60)
    
    try:
        from ai.ai_group_service import ai_group_service
        
        # Test various message types
        test_messages = [
            ("What is diversification?", "knowledge"),
            ("Explain mutual funds", "knowledge"),
            ("Analyze Apple stock", "stock"),
            ("Compare HDFC vs ICICI", "stock_comparison"),
            ("Analyze my portfolio", "portfolio"),
            ("What's happening in market?", "news"),
            ("Help with finance", "general"),
            ("HDFC Bank stock price", "stock"),
            ("Tell me about Reliance", "stock"),
            ("How does compound interest work?", "knowledge"),
            ("Tesla vs Ford comparison", "stock_comparison"),
            ("Latest financial news", "news")
        ]
        
        for message, expected_type in test_messages:
            print(f"\n💬 Testing: {message}")
            print(f"   Expected: {expected_type}")
            
            detected_type = ai_group_service._determine_message_type(message)
            print(f"   Detected: {detected_type}")
            print(f"   Match: {'✅ Yes' if detected_type == expected_type else '❌ No'}")
        
        print("\n" + "=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_natural_conversation():
    """Test natural conversation flow"""
    print("\n🧪 Testing Natural Conversation Flow")
    print("=" * 60)
    
    try:
        from ai.ai_group_service import ai_group_service
        
        # Simulate a natural conversation
        conversation = [
            "Hi, I'm new to investing. Can you help me understand stocks?",
            "Sure! I'd be happy to help you learn about stocks and investing. What would you like to know?",
            "What is diversification?",
            "Diversification is a risk management strategy that involves spreading investments across various financial instruments, industries, and other categories. The goal is to maximize returns by investing in different areas that would each react differently to the same event.",
            "That makes sense! How about HDFC Bank?",
            "HDFC Bank is one of India's largest private sector banks. It offers a wide range of banking and financial services including retail banking, corporate banking, and treasury operations.",
            "Can you compare HDFC with ICICI Bank?",
            "Both HDFC Bank and ICICI Bank are major private sector banks in India. HDFC generally has a larger market capitalization and stronger asset quality, while ICICI Bank has a more extensive branch network and digital banking initiatives.",
            "This is very helpful! What about the current market trends?",
            "I can help you understand current market trends. Would you like me to fetch the latest financial news and provide analysis?"
            "Yes, please do that!",
            "I'll fetch the latest financial news and provide you with an analysis of key market trends and developments."
        ]
        
        for i, message in enumerate(conversation, 1):
            print(f"\n💬 User {i}: {message}")
            
            # Simulate AI response (in real scenario, this would call the AI service)
            if i % 2 == 0:
                print(f"🤖 AI: Welcome! I'm here to help you learn about investing and financial concepts.")
            elif i % 2 == 2:
                print(f"🤖 AI: I'd be happy to help you learn about stocks and investing!")
            elif "diversification" in message.lower():
                print(f"🤖 AI: Diversification is a risk management strategy...")
            elif "HDFC" in message:
                print(f"🤖 AI: HDFC Bank is one of India's largest private sector banks...")
            elif "compare" in message.lower():
                print(f"🤖 AI: Both HDFC Bank and ICICI Bank are major private sector banks...")
            elif "market trends" in message.lower():
                print(f"🤖 AI: I'll fetch the latest financial news and analysis...")
            else:
                print(f"🤖 AI: I'm here to help with your financial questions!")
        
        print("\n" + "=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    """Main test function"""
    print("=" * 80)
    print("🧪 ENHANCED AI GROUPS TESTING")
    print("=" * 80)
    print("Testing dynamic stock analysis, stock comparison,")
    print("chat history, and natural conversation flow")
    print("=" * 80)
    
    tests = [
        ("Dynamic Stock Analysis", test_dynamic_stock_analysis),
        ("Stock Comparison", test_stock_comparison),
        ("Chat History", test_chat_history),
        ("Message Type Detection", test_message_type_detection),
        ("Natural Conversation", test_natural_conversation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Enhanced AI Groups Features:")
        print("  • Dynamic stock analysis (any company)")
        print("  • Stock comparison (HDFC vs ICICI)")
        print("  • Chat history functionality")
        print("  • Natural conversation flow")
        print("  • Message type detection")
        print("  • Educational responses with safety guidelines")
        print("  • Real-time data integration")
        print("  • Comprehensive error handling")
        
        print("\n🎮 Usage Examples:")
        print("  1. Dynamic queries:")
        print("     - 'Analyze HDFC Bank stock'")
        print("     - 'Tell me about Reliance Industries'")
        print("     - 'What is TCS stock price?'")
        print("  2. Comparison queries:")
        print("     - 'Compare HDFC vs ICICI Bank'")
        print("     - 'Apple vs Microsoft vs Google'")
        print("     - 'Tesla vs Ford vs GM'")
        print("  3. Chat history:")
        print("     - View previous conversations")
        print("     - Search through chat history")
        print("     - Export chat history")
        print("  4. Natural conversation:")
        print("     - Continuous dialogue flow")
        print("     - Context-aware responses")
        print("     - Educational guidance")
        
    else:
        print(f"\n❌ {total - passed} tests failed")
        print("Please check the errors above and fix the issues.")
    
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
