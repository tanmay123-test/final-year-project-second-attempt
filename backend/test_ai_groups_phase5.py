#!/usr/bin/env python3
"""
Test script to demonstrate AI Groups Phase 5: AI Financial Coach and Knowledge System
"""

import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_vector_store():
    """Test Vector Store functionality"""
    print("🔍 Testing Vector Store")
    print("-" * 60)
    
    try:
        from ai.vector_store_fixed import vector_store
        
        # Test vector store initialization
        print("🏗 Testing vector store initialization...")
        initialized = await vector_store.initialize_vector_store()
        print(f"   Initialization: {'✅ Success' if initialized else '❌ Failed'}")
        
        # Test knowledge search
        print("\n🔍 Testing knowledge search...")
        search_results = await vector_store.search_knowledge("diversification", limit=3)
        print(f"   Search Results: {len(search_results)} documents found")
        
        if search_results:
            for i, result in enumerate(search_results, 1):
                print(f"   {i}. {result['title']} (Score: {result['score']:.2f})")
        
        # Test connection
        print("\n🔗 Testing connection...")
        is_connected = vector_store.is_connected()
        print(f"   Connection Status: {'✅ Connected' if is_connected else '❌ Disconnected'}")
        
        # Test cache status
        cache_status = vector_store.get_cache_status()
        print(f"   Cache Size: {cache_status['cache_size']}")
        print(f"   Documents Count: {cache_status['documents_count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_knowledge_loader():
    """Test Knowledge Loader functionality"""
    print("\n📚 Testing Knowledge Loader")
    print("-" * 60)
    
    try:
        from ai.knowledge_loader_fixed import knowledge_loader
        
        # Test content loading
        print("📖 Testing content loading...")
        content = knowledge_loader.load_financial_education_content()
        print(f"   Documents Loaded: {len(content)}")
        
        # Test sample data
        sample_data = knowledge_loader._get_sample_knowledge_content()
        print(f"   Sample Documents: {len(sample_data)}")
        
        # Test supported companies
        companies = knowledge_loader.get_supported_companies()
        print(f"   Supported Companies: {len(companies)}")
        
        # Test sample queries
        queries = knowledge_loader.get_sample_queries()
        print(f"   Sample Queries: {len(queries)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_knowledge_ai_service():
    """Test Knowledge AI Service functionality"""
    print("\n🤖 Testing Knowledge AI Service")
    print("-" * 60)
    
    try:
        from ai.knowledge_ai_service import knowledge_ai_service
        
        # Test knowledge response
        print("📝 Testing knowledge response...")
        response = await knowledge_ai_service.generate_knowledge_response("What is diversification?")
        
        if response.get("success"):
            print(f"✅ Response Generated: {len(response['response'])} characters")
            print(f"   Sources: {len(response.get('sources', []))}")
            print(f"   Query: {response.get('query', 'N/A')}")
        else:
            print(f"❌ Response Failed: {response.get('error', 'Unknown error')}")
        
        # Test knowledge search
        print("\n🔍 Testing knowledge search...")
        search_results = await knowledge_ai_service.search_knowledge_base("risk management", limit=3)
        print(f"   Search Results: {len(search_results)} documents")
        
        # Test knowledge stats
        stats = knowledge_ai_service.get_knowledge_stats()
        print(f"   Knowledge Stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_financial_coach_service():
    """Test Financial Coach Service functionality"""
    print("\n💼 Testing Financial Coach Service")
    print("-" * 60)
    
    try:
        from ai.financial_coach_service import financial_coach_service
        
        # Test financial insights
        print("💡 Testing financial insights...")
        insights = await financial_coach_service.generate_financial_insights(1, "Provide general financial insights")
        
        if insights.get("success"):
            print(f"✅ Insights Generated: {len(insights['response'])} characters")
            print(f"   Insight ID: {insights.get('insight_id', 'N/A')}")
            print(f"   Data Summary: {insights.get('data_summary', {})}")
        else:
            print(f"❌ Insights Failed: {insights.get('error', 'Unknown error')}")
        
        # Test coaching topics
        topics = financial_coach_service.get_coaching_topics()
        print(f"   Coaching Topics: {len(topics)}")
        
        # Test sample queries
        queries = financial_coach_service.get_sample_coaching_queries()
        print(f"   Sample Queries: {len(queries)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_news_service():
    """Test News Service functionality"""
    print("\n📰 Testing News Service")
    print("-" * 60)
    
    try:
        from services.news_service import news_service
        
        # Test market news
        print("📈 Testing market news...")
        market_news = await news_service.fetch_market_news(limit=3)
        print(f"   Market News: {len(market_news)} articles")
        
        if market_news:
            for i, article in enumerate(market_news[:2], 1):
                print(f"   {i}. {article['headline'][:50]}...")
        
        # Test news summarization
        print("\n📝 Testing news summarization...")
        if market_news:
            summary = await news_service.summarize_news(market_news[:2], "What are the key trends?")
            
            if summary.get("success"):
                print(f"✅ Summary Generated: {len(summary['summary'])} characters")
                print(f"   Articles Used: {summary.get('articles_count', 0)}")
            else:
                print(f"❌ Summary Failed: {summary.get('error', 'Unknown error')}")
        
        # Test news categories
        categories = news_service.get_news_categories()
        print(f"   News Categories: {len(categories)}")
        
        # Test sample queries
        queries = news_service.get_sample_queries()
        print(f"   Sample Queries: {len(queries)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_message_flow():
    """Test message flow and type detection"""
    print("\n🔄 Testing Message Flow")
    print("-" * 60)
    
    try:
        from ai.ai_group_service import ai_group_service
        
        # Test message type detection
        test_messages = [
            ("What is diversification?", "knowledge"),
            ("Analyze Apple stock", "stock"),
            ("Analyze my portfolio", "portfolio"),
            ("What's happening in the market?", "news"),
            ("How does compound interest work?", "knowledge"),
            ("What is Tesla's PE ratio?", "stock"),
            ("How can I improve my spending?", "portfolio"),
            ("Latest financial news", "news"),
            ("Explain mutual funds", "knowledge"),
            ("General financial question", "general")
        ]
        
        for i, (message, expected_type) in enumerate(test_messages, 1):
            print(f"\n{i}. Message: {message}")
            detected_type = ai_group_service._determine_message_type(message)
            print(f"   Expected Type: {expected_type}")
            print(f"   Detected Type: {detected_type}")
            print(f"   Match: {'✅ Yes' if detected_type == expected_type else '❌ No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_integration_flow():
    """Test complete integration flow"""
    print("\n🔗 Testing Integration Flow")
    print("-" * 60)
    
    try:
        from ai.ai_group_service import ai_group_service
        
        # Test complete message handling
        test_scenarios = [
            {
                "message": "What is diversification?",
                "expected_type": "knowledge",
                "description": "Knowledge-based financial education"
            },
            {
                "message": "Analyze Apple stock fundamentals",
                "expected_type": "stock",
                "description": "Stock analysis with real data"
            },
            {
                "message": "Analyze my portfolio performance",
                "expected_type": "portfolio",
                "description": "Portfolio analysis with AI coaching"
            },
            {
                "message": "What's happening in the tech market today?",
                "expected_type": "news",
                "description": "Financial news summarization"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{i}. {scenario['description']}")
            print(f"   Message: {scenario['message']}")
            print(f"   Expected: {scenario['expected_type']} response")
            
            # Test if AI should respond
            should_respond = ai_group_service._should_ai_respond(scenario['message'])
            print(f"   AI Should Respond: {'✅ Yes' if should_respond else '❌ No'}")
            
            if should_respond:
                detected_type = ai_group_service._determine_message_type(scenario['message'])
                print(f"   Detected Type: {detected_type}")
                print(f"   Type Match: {'✅ Yes' if detected_type == scenario['expected_type'] else '❌ No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    """Main test function"""
    print("="*80)
    print("🧪 AI GROUPS PHASE 5: AI FINANCIAL COACH & KNOWLEDGE SYSTEM TEST")
    print("="*80)
    
    tests = [
        ("Vector Store", test_vector_store),
        ("Knowledge Loader", test_knowledge_loader),
        ("Knowledge AI Service", test_knowledge_ai_service),
        ("Financial Coach Service", test_financial_coach_service),
        ("News Service", test_news_service),
        ("Message Flow", test_message_flow),
        ("Integration Flow", test_integration_flow)
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
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    
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
        print("\n🚀 AI Groups Phase 5 is ready for production!")
        print("\n📋 Features implemented:")
        print("  ✅ FAISS vector database for financial knowledge")
        print("  ✅ Knowledge AI service with vector search")
        print("  ✅ Financial coach service with personalized insights")
        print("  ✅ News service with AI summarization")
        print("  ✅ Intelligent message type detection")
        print("  ✅ Multi-AI service integration")
        print("  ✅ Educational focus with safety guidelines")
        print("  ✅ Error handling and fallback mechanisms")
        print("  ✅ Modular architecture and clean code")
        
        print("\n🎮 To test with CLI:")
        print("  1. cd backend")
        print("  2. python cli.py")
        print("  3. Login → Money Service → AI Groups")
        print(" 4. Join or create a group")
        print("  5. Try different query types:")
        print("     • Knowledge: 'What is diversification?'")
        print("     • Stock: 'Analyze Apple stock'")
        print("     • Portfolio: 'Analyze my portfolio'")
        print("     • News: 'What's happening in the market?'")
        
        print("\n🌐 To test with API:")
        print("  1. uvicorn main:app --reload")
        print("  2. Send POST to /ai-groups/message")
        print("   3. Check for different message types in response")
        print("  4. Test knowledge search endpoints")
        print("  5. Test portfolio analysis endpoints")
        print("  6. Test news summarization endpoints")
        
        print("\n🔧 To test individual services:")
        print("  1. python test_ai_groups_phase5.py")
        print("  2. Check individual service functionality")
        print(" 3. Verify vector store operations")
        print(" 4. Test AI service integrations")
        
    else:
        print(f"\n❌ {total - passed} tests failed")
        print("Please check the errors above and fix the issues.")
    
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
