"""
AI Financial Assistant - Personal AI Chat System
Direct user-to-AI financial assistant interface
"""

from datetime import datetime
from ai.ai_chat_service import ai_chat_service

class AIFinancialAssistant:
    """Personal AI Financial Assistant"""
    
    def __init__(self):
        self.ai_service = ai_chat_service
    
    def show_menu(self, user_id):
        """Main menu for AI Financial Assistant"""
        while True:
            print(f"""
======================================================================
🤖 AI FINANCIAL ASSISTANT
======================================================================
1. 💬 Chat with AI
2. 📈 Analyze Stock
3. 💼 Analyze Portfolio
4. 📰 Market News
5. 📜 Chat History
6. ⬅️ Back to Money Service

Select option: """)
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self._chat_with_ai(user_id)
            elif choice == "2":
                self._analyze_stock(user_id)
            elif choice == "3":
                self._analyze_portfolio(user_id)
            elif choice == "4":
                self._get_market_news(user_id)
            elif choice == "5":
                self._view_chat_history(user_id)
            elif choice == "6":
                return
            else:
                print("❌ Invalid choice")
            
            input("\nPress Enter to continue...")
    
    def _chat_with_ai(self, user_id):
        """Direct chat with AI assistant"""
        print("\n" + "="*60)
        print("💬 CHAT WITH AI FINANCIAL ASSISTANT")
        print("="*60)
        print("🤝 Ask me anything about finance, stocks, investments, or financial concepts!")
        print("💡 Examples:")
        print("   • Explain HDFC Bank stock")
        print("   • What is diversification?")
        print("   • How does compound interest work?")
        print("   • What are mutual funds?")
        print("   • Explain risk management")
        print("   • Type 'exit' to return to menu")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\n💭 You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'back']:
                    break
                
                if not user_input:
                    print("❌ Please enter a message")
                    continue
                
                print("🤖 AI: Thinking...")
                
                # Get AI response
                result = self.ai_service.handle_user_chat(user_id, user_input)
                
                if result['success']:
                    print(f"\n🤖 AI: {result['ai_response']}")
                    print(f"📊 Type: {result['message_type']}")
                else:
                    print(f"❌ Error: {result['error']}")
                
                print("-" * 60)
                
            except KeyboardInterrupt:
                print("\n👋 Returning to menu...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _analyze_stock(self, user_id):
        """Analyze specific stock"""
        print("\n" + "="*60)
        print("📈 STOCK ANALYSIS")
        print("="*60)
        print("💡 You can enter either:")
        print("   • Stock symbol (e.g., HDFCBANK, RELIANCE)")
        print("   • Natural language (e.g., 'analyze HDFC stock')")
        print("   • Company name (e.g., 'analyze HDFC Bank')")
        print("-" * 60)
        
        try:
            stock_input = input("📊 Enter stock symbol or query: ").strip()
            
            if not stock_input:
                print("❌ Stock input is required")
                return
            
            # Extract stock symbol using AI chat service
            stock_symbol = self.ai_service._extract_stock_symbol(stock_input)
            
            if stock_symbol:
                print(f"🤖 AI: Analyzing {stock_symbol}...")
                
                # Get stock analysis
                message = f"analyze stock {stock_symbol}"
                result = self.ai_service.handle_user_chat(user_id, message)
                
                if result['success']:
                    print(f"\n📈 {stock_symbol} Analysis:")
                    print("-" * 50)
                    print(result['ai_response'])
                    print("-" * 50)
                    print("💡 This analysis is for educational purposes only and not financial advice.")
                else:
                    print(f"❌ Error: {result['error']}")
            else:
                print("❌ Could not detect stock symbol from your input.")
                print("💡 Try examples like:")
                print("   • HDFCBANK")
                print("   • analyze HDFC stock")
                print("   • analyze HDFC Bank")
                print("   • RELIANCE")
                print("   • analyze reliance")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _analyze_portfolio(self, user_id):
        """Analyze user's portfolio"""
        print("\n" + "="*60)
        print("💼 PORTFOLIO ANALYSIS")
        print("="*60)
        
        try:
            print("🤖 AI: Analyzing your portfolio...")
            
            # Get portfolio analysis
            message = "analyze my portfolio"
            result = self.ai_service.handle_user_chat(user_id, message)
            
            if result['success']:
                print(f"\n💼 Portfolio Analysis:")
                print("-" * 50)
                print(result['ai_response'])
                print("-" * 50)
                print("💡 This analysis is for educational purposes only and not financial advice.")
            else:
                print(f"❌ Error: {result['error']}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _get_market_news(self, user_id):
        """Get market news"""
        print("\n" + "="*60)
        print("📰 MARKET NEWS")
        print("="*60)
        
        try:
            print("🤖 AI: Fetching latest market news...")
            
            # Get market news
            message = "what's happening in the market today"
            result = self.ai_service.handle_user_chat(user_id, message)
            
            if result['success']:
                print(f"\n📰 Market News:")
                print("-" * 50)
                print(result['ai_response'])
                print("-" * 50)
                print("💡 News summaries are for informational purposes only and not financial advice.")
            else:
                print(f"❌ Error: {result['error']}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _view_chat_history(self, user_id):
        """View chat history"""
        print("\n" + "="*60)
        print("📜 CHAT HISTORY")
        print("="*60)
        
        try:
            # Get chat history
            history = self.ai_service.get_chat_history(user_id, limit=20)
            
            if not history:
                print("📭 No chat history found")
                return
            
            print(f"📊 Recent Conversations ({len(history)} messages):")
            print("-" * 60)
            
            for i, msg in enumerate(history, 1):
                sender = "👤 You" if msg['sender'] == 'user' else "🤖 AI"
                timestamp = msg.get('created_at', '')[:19] if msg.get('created_at') else 'Unknown'
                content = msg.get('content', '')
                
                # Truncate long messages
                if len(content) > 100:
                    content = content[:100] + "..."
                
                print(f"{i}. {sender} - {timestamp}")
                print(f"   {content}")
                print("-" * 60)
            
            # Show statistics
            stats = self.ai_service.get_chat_statistics(user_id)
            if stats:
                print(f"\n📊 Chat Statistics:")
                print(f"   Total Messages: {stats.get('total_messages', 0)}")
                print(f"   Your Messages: {stats.get('user_messages', 0)}")
                print(f"   AI Responses: {stats.get('ai_responses', 0)}")
                print(f"   Recent Activity (7 days): {stats.get('recent_messages_7_days', 0)}")
                print(f"   Engagement Score: {stats.get('engagement_score', 0):.1f}/100")
                
        except Exception as e:
            print(f"❌ Error: {e}")

# Singleton instance
ai_financial_assistant = AIFinancialAssistant()
