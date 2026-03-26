"""
AI Chat Service - Personal AI Financial Assistant
Handles direct user-to-AI chat conversations
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import re

try:
    from .gemini_client import gemini_client
    from .stock_ai_service import stock_ai_service
    from .portfolio_ai_service import portfolio_ai_service
    from .knowledge_ai_service import knowledge_ai_service
    from ..services.news_service import news_service
    from ..services.chat_history_service import chat_history_service
except ImportError:
    from ai.gemini_client import gemini_client
    from ai.stock_ai_service import stock_ai_service
    from ai.portfolio_ai_service import portfolio_ai_service
    from ai.knowledge_ai_service import knowledge_ai_service
    from services.news_service import news_service
    from services.chat_history_service import chat_history_service

class AIChatService:
    """
    Personal AI Financial Assistant Service
    Handles direct user-to-AI conversations
    """
    
    def __init__(self):
        self.gemini_client = gemini_client
        self.ai_user_id = -1  # Special user ID for AI assistant
    
    def handle_user_chat(self, user_id: int, message: str) -> Dict[str, Any]:
        """
        Handle user chat message and generate AI response
        
        Args:
            user_id: User ID
            message: User message
            
        Returns:
            Dictionary with AI response and metadata
        """
        try:
            # Store user message in chat history
            chat_history_service.store_message(0, user_id, message, "user_message")
            
            # Detect message type and route to appropriate service
            message_type = self._detect_intent(message)
            
            # Generate AI response based on message type
            if message_type == "stock_analysis":
                ai_response = self._handle_stock_analysis(message)
            elif message_type == "portfolio_analysis":
                ai_response = self._handle_portfolio_analysis(user_id, message)
            elif message_type == "financial_coach":
                ai_response = self._handle_financial_coach(user_id, message)
            elif message_type == "knowledge_query":
                ai_response = self._handle_knowledge_query(message)
            elif message_type == "market_news":
                ai_response = self._handle_market_news()
            else:
                ai_response = self._handle_general_query(message)
            
            # Store AI response in chat history
            response_id = chat_history_service.store_message(0, user_id, ai_response, "ai_response")
            
            return {
                'success': True,
                'ai_response': ai_response,
                'message_type': message_type,
                'response_id': response_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error processing chat message: {str(e)}"
            }
    
    def _detect_intent(self, message: str) -> str:
        msg = message.lower().strip()
        import re
        stock_patterns = [
            r'\b(analyze|analysis|check|look up|tell me about|explain)\b.*\b(stock|share|equity|nse|bse)\b',
            r'\b(stock|share|equity)\b.*\b(of|for)\b',   # "stock of zomato"
            r'\b(stock|share|price|performance)\b.*\b[a-z]{3,}\b',
            r'\b(hdfc|reliance|tcs|infy|wipro|sbi|icici|tatamotors|zomato|paytm|nykaa|swiggy|ola|irctc|indigo|bajaj|kotak|axis|hul|itc|maruti|cipla|adani|ongc|ntpc|nestle|titan|dmart)\b',
        ]
        portfolio_patterns = [
            r'\b(my portfolio|my investments|my holdings|my stocks)\b',
            r'\b(portfolio|holdings|allocation|rebalance|diversif)\b',
        ]
        coach_patterns = [
            r'\b(advice|suggest|recommend|should i|what should|help me|guide me)\b',
            r'\b(goal|save|saving|budget|plan|retire|retirement)\b',
        ]
        news_patterns = [
            r'\b(news|today|market update|latest|happening|trending)\b',
            r'\b(market|sensex|nifty|dow|nasdaq)\b.*\b(today|now|current|live)\b',
        ]
        knowledge_patterns = [
            r'\b(what is|what are|explain|define|how does|how do|tell me about|describe)\b',
            r'\b(mutual fund|sip|etf|bond|derivative|option|future|ipo|dividend)\b',
        ]
        for p in stock_patterns:
            if re.search(p, msg, re.IGNORECASE): return 'stock_analysis'
        for p in portfolio_patterns:
            if re.search(p, msg, re.IGNORECASE): return 'portfolio_analysis'
        for p in coach_patterns:
            if re.search(p, msg, re.IGNORECASE): return 'financial_coach'
        for p in news_patterns:
            if re.search(p, msg, re.IGNORECASE): return 'market_news'
        for p in knowledge_patterns:
            if re.search(p, msg, re.IGNORECASE): return 'knowledge_query'
        return 'general_query'

    def _detect_message_type(self, message: str) -> str:
        """
        Detect the type of user message based on keywords
        
        Args:
            message: User message
            
        Returns:
            Message type string
        """
        message_lower = message.lower()
        
        # Stock analysis keywords
        stock_keywords = [
            'analyze stock', 'stock analysis', 'stock price', 'stock performance',
            'explain stock', 'stock information', 'company stock', 'share price',
            'analyze hdfc', 'analyze reliance', 'analyze tcs', 'analyze infosys',
            'explain hdfc', 'explain reliance', 'explain tcs', 'explain infosys',
            'hdfc stock', 'reliance stock', 'tcs stock', 'infosys stock',
            'hdfc shares', 'reliance shares', 'tcs shares', 'infosys shares',
            'analyze wipro', 'analyze wipro stock', 'wipro stock', 'wipro shares',
            'analyze icici', 'analyze icici stock', 'icici stock', 'icici shares',
            'analyze sbi', 'analyze sbi stock', 'sbi stock', 'sbi shares'
        ]
        
        # Portfolio analysis keywords
        portfolio_keywords = [
            'portfolio', 'my portfolio', 'analyze portfolio', 'portfolio performance',
            'my investments', 'investment portfolio', 'portfolio analysis'
        ]
        
        # Knowledge query keywords
        knowledge_keywords = [
            'what is', 'explain', 'how does', 'define', 'meaning of',
            'tell me about', 'understand', 'concept', 'financial concept'
        ]
        
        # Market news keywords
        news_keywords = [
            'news', 'market today', 'market news', 'stock market', 'market update',
            'financial news', 'economic news', 'market analysis'
        ]
        
        # Check for each type
        if any(keyword in message_lower for keyword in stock_keywords):
            return "stock_analysis"
        elif any(keyword in message_lower for keyword in portfolio_keywords):
            return "portfolio_analysis"
        elif any(keyword in message_lower for keyword in knowledge_keywords):
            return "knowledge_query"
        elif any(keyword in message_lower for keyword in news_keywords):
            return "market_news"
        else:
            return "general_query"
    
    def _handle_stock_analysis(self, message: str) -> str:
        """Handle stock analysis requests"""
        try:
            stock_symbol = self._extract_stock_symbol(message)

            if stock_symbol:
                analysis = stock_ai_service.generate_stock_analysis_sync(f"analyze stock {stock_symbol}")
                if analysis.get('success'):
                    return self._format_stock_response(analysis)
                # Stock API failed — fall through to Gemini with company name

            # Extract company name from message for Gemini fallback
            import re
            # Try to pull the company name out of the message
            company_match = re.search(
                r'(?:analyze|analysis|check|tell me about|explain|stock of|shares of)\s+([a-zA-Z0-9 &]+?)(?:\s+stock|\s+share|\s+equity|$)',
                message, re.IGNORECASE
            )
            company_name = company_match.group(1).strip() if company_match else (stock_symbol or message)

            prompt = f"""You are a financial education assistant.

The user asked: "{message}"

Provide an educational overview of {company_name} as a company. Include:
- What the company does (business model)
- Which sector/industry it operates in
- Key facts about its market position
- General financial characteristics if known
- Any notable recent developments you're aware of

Important rules:
- Do NOT give investment advice
- Do NOT say "buy", "sell", "hold", or "recommend"
- Clearly state this is educational information only
- If you don't have recent price data, say so and explain why general knowledge is still useful
- Add a disclaimer at the end

Keep the response clear and helpful for someone learning about this company."""

            return gemini_client.generate_response(prompt)

        except Exception as e:
            return f"Error analyzing stock: {str(e)}"
    
    def _handle_portfolio_analysis(self, user_id: int, message: str) -> str:
        """Handle portfolio analysis requests"""
        try:
            # Use portfolio AI service (synchronous call)
            analysis = portfolio_ai_service.analyze_portfolio(user_id)
            
            if analysis.get('success'):
                return self._format_portfolio_response(analysis)
            else:
                return "I couldn't analyze your portfolio. Please add some stocks to your portfolio first."
                
        except Exception as e:
            return f"Error analyzing portfolio: {str(e)}"
    
    def _handle_financial_coach(self, user_id: int, message: str) -> str:
        """Handle financial coaching requests"""
        try:
            from .financial_coach_service import financial_coach_service
            result = financial_coach_service.get_financial_advice(user_id, message)
            
            if result.get('success'):
                return result.get('advice', 'I can help you with your financial planning.')
            else:
                return "I couldn't provide financial advice at the moment. Please try again."
                
        except Exception as e:
            return f"Error providing financial advice: {str(e)}"
    
    def _handle_knowledge_query(self, message: str) -> str:
        """Handle knowledge and educational queries"""
        try:
            # Use knowledge AI service (simplified call)
            response = knowledge_ai_service.get_financial_knowledge(message)
            
            if response.get('success'):
                return response.get('response', 'I could not find information on that topic.')
            else:
                # Fallback to general AI with educational focus
                return self._get_educational_response(message)
                
        except Exception as e:
            # Fallback to basic educational response
            return self._get_basic_educational_response(message)
    
    def _get_basic_educational_response(self, message: str) -> str:
        """Get basic educational response for common financial concepts"""
        message_lower = message.lower()
        
        # Basic educational responses for common concepts
        educational_responses = {
            "diversification": """
**Diversification - Educational Overview**

Diversification is a risk management strategy that involves spreading investments across various assets, industries, and geographic areas.

**Key Points:**
- Reduces portfolio risk by not putting all eggs in one basket
- Different assets perform differently under various market conditions
- Helps protect against significant losses in any single investment

**Example:**
Instead of investing all money in one stock, diversify across:
- Multiple stocks from different sectors
- Bonds and fixed income
- Real estate or commodities
- International markets

**Important Note:**
This information is for educational purposes only and not financial advice.
""",
            "compound interest": """
**Compound Interest - Educational Overview**

Compound interest is the process where interest earns interest, creating exponential growth over time.

**How It Works:**
- You earn interest on your principal amount
- You also earn interest on accumulated interest
- This creates a snowball effect of growing wealth

**Example:**
If you invest  10,000 at 8% annual compound interest:
- Year 1:  10,800
- Year 2:  11,664 (interest on interest)
- Year 3:  12,597 (compounding continues)

**Key Insight:**
The earlier you start, the more powerful compound interest becomes.

**Important Note:**
This information is for educational purposes only and not financial advice.
""",
            "mutual funds": """
**Mutual Funds - Educational Overview**

Mutual funds are investment vehicles that pool money from multiple investors to purchase a diversified portfolio of stocks, bonds, or other securities.

**How They Work:**
- Professional fund managers handle investment decisions
- Investors buy shares representing ownership in the fund
- Returns depend on the fund's performance

**Types of Mutual Funds:**
- Equity funds (stocks)
- Debt funds (bonds)
- Hybrid funds (balanced approach)
- Index funds (track market indices)

**Benefits:**
- Professional management
- Diversification
- Liquidity
- Affordable entry point

**Important Note:**
This information is for educational purposes only and not financial advice.
"""
        }
        
        # Check for matching concepts
        for concept, response in educational_responses.items():
            if concept in message_lower:
                return response.strip()
        
        # Generic response for other concepts
        return f"""
**Financial Education - {message.title()}**

I apologize, but I'm unable to provide detailed information on "{message}" at the moment.

**What I can help with:**
- Stock analysis (e.g., "analyze HDFC stock")
- Basic concepts like diversification, compound interest, mutual funds
- Market news and updates

**Suggestions:**
- Try rephrasing your question
- Be more specific about the financial concept
- Check if the concept is spelled correctly

**Important Note:**
This information is for educational purposes only and not financial advice.
"""
    
    def _handle_market_news(self) -> str:
        """Handle market news requests"""
        try:
            # Use news service
            news = news_service.get_market_news()
            
            if news.get('success'):
                return self._format_news_response(news)
            else:
                return "I couldn't fetch the latest market news. Please try again later."
                
        except Exception as e:
            return f"Error fetching market news: {str(e)}"
    
    def _handle_general_query(self, message: str) -> str:
        """Handle general financial queries"""
        try:
            # Use Gemini for general queries with financial education focus
            prompt = self._build_financial_education_prompt(message)
            response = gemini_client.generate_response(prompt)
            
            return response
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _extract_stock_symbol(self, message: str) -> Optional[str]:
        import re
        # Expanded Indian + global company → NSE/BSE/NYSE symbol map
        symbol_map = {
            # Indian large caps
            'hdfc': 'HDFCBANK', 'hdfc bank': 'HDFCBANK',
            'icici': 'ICICIBANK', 'icici bank': 'ICICIBANK',
            'sbi': 'SBIN', 'state bank': 'SBIN',
            'reliance': 'RELIANCE', 'ril': 'RELIANCE',
            'tcs': 'TCS', 'tata consultancy': 'TCS',
            'infosys': 'INFY', 'infy': 'INFY',
            'wipro': 'WIPRO',
            'tatamotors': 'TATAMOTORS', 'tata motors': 'TATAMOTORS',
            'bajaj': 'BAJFINANCE', 'bajaj finance': 'BAJFINANCE',
            'kotak': 'KOTAKBANK', 'kotak bank': 'KOTAKBANK',
            'axis bank': 'AXISBANK', 'axis': 'AXISBANK',
            'hul': 'HINDUNILVR', 'hindustan unilever': 'HINDUNILVR',
            'itc': 'ITC',
            'maruti': 'MARUTI', 'maruti suzuki': 'MARUTI',
            'sun pharma': 'SUNPHARMA', 'sun pharmaceutical': 'SUNPHARMA',
            'dr reddy': 'DRREDDY', "dr. reddy": 'DRREDDY',
            'cipla': 'CIPLA',
            'adani': 'ADANIENT', 'adani enterprises': 'ADANIENT',
            'adani ports': 'ADANIPORTS',
            'adani green': 'ADANIGREEN',
            'adani power': 'ADANIPOWER',
            'ongc': 'ONGC',
            'ntpc': 'NTPC',
            'power grid': 'POWERGRID',
            'bhel': 'BHEL',
            'coal india': 'COALINDIA',
            'hindalco': 'HINDALCO',
            'jsw steel': 'JSWSTEEL', 'jsw': 'JSWSTEEL',
            'tata steel': 'TATASTEEL',
            'ultratech': 'ULTRACEMCO', 'ultratech cement': 'ULTRACEMCO',
            'asian paints': 'ASIANPAINT',
            'nestle': 'NESTLEIND',
            'britannia': 'BRITANNIA',
            'titan': 'TITAN',
            'dmart': 'DMART', 'avenue supermarts': 'DMART',
            'nykaa': 'NYKAA', 'fss': 'NYKAA',
            'paytm': 'PAYTM', 'one97': 'PAYTM',
            'zomato': 'ZOMATO',
            'swiggy': 'SWIGGY',
            'ola': 'OLA',
            'policybazaar': 'POLICYBZR',
            'freshworks': 'FRSH',
            'indigo': 'INDIGO', 'interglobe': 'INDIGO',
            'spicejet': 'SPICEJET',
            'irctc': 'IRCTC',
            'lti': 'LTIM', 'ltimindtree': 'LTIM',
            'hcl': 'HCLTECH', 'hcl tech': 'HCLTECH',
            'tech mahindra': 'TECHM',
            'mphasis': 'MPHASIS',
            'persistent': 'PERSISTENT',
            'coforge': 'COFORGE',
            # Global
            'apple': 'AAPL',
            'tesla': 'TSLA',
            'google': 'GOOGL', 'alphabet': 'GOOGL',
            'microsoft': 'MSFT',
            'amazon': 'AMZN',
            'meta': 'META', 'facebook': 'META',
            'nvidia': 'NVDA',
            'netflix': 'NFLX',
            'uber': 'UBER',
            'airbnb': 'ABNB',
            'shopify': 'SHOP',
            'paypal': 'PYPL',
            'intel': 'INTC',
            'amd': 'AMD',
            'samsung': '005930.KS',
            'toyota': 'TM',
        }
        msg_lower = message.lower()
        # Sort by length descending so "hdfc bank" matches before "hdfc"
        for name in sorted(symbol_map.keys(), key=len, reverse=True):
            if name in msg_lower:
                return symbol_map[name]
        # Fallback: uppercase ticker in message (e.g. "ZOMATO", "AAPL")
        match = re.search(r'\b([A-Z]{2,8})\b', message)
        if match:
            return match.group(1)
        return None
    
    def _format_stock_response(self, analysis: Dict[str, Any]) -> str:
        """Format stock analysis response"""
        try:
            # Handle different response structures
            if 'analysis' in analysis:
                # New format with nested analysis
                stock_data = analysis.get('stock_data', {})
                ai_analysis = analysis.get('analysis', '')
                
                symbol = stock_data.get('symbol', 'Unknown')
                price = stock_data.get('price', 0)
                change = stock_data.get('change', 0)
                change_percent = stock_data.get('change_percent', 0)
                
                response = f"  {symbol} Stock Analysis\n\n"
                response += f"Current Price:  {price:.2f}\n"
                response += f"Change:  {change:.2f} ({change_percent:.2f}%)\n\n"
                response += f"AI Analysis:\n{ai_analysis}\n"
                
            else:
                # Legacy format
                symbol = analysis.get('symbol', 'Unknown')
                price = analysis.get('price', 0)
                change = analysis.get('change', 0)
                change_percent = analysis.get('change_percent', 0)
                insights = analysis.get('insights', [])
                
                response = f"  {symbol} Stock Analysis\n\n"
                response += f"Current Price:  {price:.2f}\n"
                response += f"Change:  {change:.2f} ({change_percent:.2f}%)\n\n"
                
                response += "Key Insights:\n"
                for insight in insights[:3]:  # Show top 3 insights
                    response += f"  {insight}\n"
            
            response += "\n  This analysis is for educational purposes only and not financial advice."
            response += "\n  Data provided by financial APIs"
            
            return response
            
        except Exception as e:
            return f"Error formatting stock response: {str(e)}"
    
    def _format_portfolio_response(self, analysis: Dict[str, Any]) -> str:
        """Format portfolio analysis response"""
        try:
            total_value = analysis.get('total_value', 0)
            total_return = analysis.get('total_return', 0)
            return_percent = analysis.get('return_percent', 0)
            holdings = analysis.get('holdings', [])
            insights = analysis.get('insights', [])
            
            response = f"  Portfolio Analysis\n\n"
            response += f"Total Value:  {total_value:.2f}\n"
            response += f"Total Return:  {total_return:.2f} ({return_percent:.2f}%)\n\n"
            
            response += "Top Holdings:\n"
            for holding in holdings[:5]:  # Show top 5 holdings
                symbol = holding.get('symbol', 'Unknown')
                value = holding.get('value', 0)
                response += f"  {symbol}:  {value:.2f}\n"
            
            response += "\nPortfolio Insights:\n"
            for insight in insights[:3]:  # Show top 3 insights
                response += f"  {insight}\n"
            
            response += "\n  This analysis is for educational purposes only and not financial advice."
            
            return response
            
        except Exception as e:
            return f"Error formatting portfolio response: {str(e)}"
    
    def _format_news_response(self, news: Dict[str, Any]) -> str:
        """Format market news response"""
        try:
            articles = news.get('articles', [])
            
            if not articles:
                return "No market news available at the moment."
            
            response = "📰 Market News Update\n\n"
            
            for article in articles[:5]:
                # Finnhub uses 'headline', mock data uses 'title' — handle both
                title = article.get('headline') or article.get('title') or ''
                source = article.get('source', 'Unknown source')
                summary = article.get('summary', '')
                if title:
                    response += f"• {title} ({source})\n"
                    if summary:
                        response += f"  {summary[:120]}...\n" if len(summary) > 120 else f"  {summary}\n"
            
            response += "\n  News summaries are for informational purposes only and not financial advice."
            response += "\n  Data provided by financial news APIs"
            
            return response
            
        except Exception as e:
            return f"Error formatting news response: {str(e)}"
    
    def _build_financial_education_prompt(self, user_message: str) -> str:
        """Build prompt for financial education responses"""
        prompt = f"""
You are a financial education assistant. Your role is to provide educational insights about financial concepts, explain how things work, and help users understand financial topics.

User question: {user_message}

Rules:
1. Provide educational insights only
2. Explain financial concepts clearly
3. Never give financial advice
4. Never say "buy" or "sell" specific investments
5. Explain risks and fundamentals
6. Use simple, easy-to-understand language
7. Include relevant examples when helpful
8. Mention that this is educational information only

Please provide a helpful, educational response to the user's question.
"""
        return prompt
    
    def _get_educational_response(self, message: str) -> str:
        """Get educational response for general queries"""
        try:
            prompt = self._build_financial_education_prompt(message)
            response = gemini_client.generate_response(prompt)
            
            # Add educational disclaimer
            if not any(disclaimer in response.lower() for disclaimer in ['educational', 'not financial advice']):
                response += "\n\n  This information is for educational purposes only and not financial advice."
            
            return response
            
        except Exception as e:
            return "I apologize, but I'm having trouble providing a response right now. Please try again later."
    
    def get_chat_history(self, user_id: int, limit: int = 50) -> list:
        """Get chat history for a user"""
        try:
            return chat_history_service.get_chat_history(0, user_id, limit)
        except Exception as e:
            return []
    
    def get_chat_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get chat statistics for a user"""
        try:
            return chat_history_service.get_chat_statistics(0, user_id)
        except Exception as e:
            return {}

# Singleton instance
ai_chat_service = AIChatService()
