"""
AI Chat Service - Personal AI Financial Assistant
Handles direct user-to-AI chat conversations
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import re

try:
    import google.generativeai as genai
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
            message_type = self._detect_message_type(message)
            
            # Generate AI response based on message type
            if message_type == "stock_analysis":
                ai_response = self._handle_stock_analysis(message)
            elif message_type == "portfolio_analysis":
                ai_response = self._handle_portfolio_analysis(user_id, message)
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
            'analyze hdfc', 'analyze reliance', 'analyze tcs', 'analyze infosys'
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
            # Extract stock symbol from message
            stock_symbol = self._extract_stock_symbol(message)
            
            if stock_symbol:
                # Use existing stock AI service (synchronous call)
                analysis = stock_ai_service.generate_stock_analysis(f"analyze stock {stock_symbol}")
                
                if analysis.get('success'):
                    return self._format_stock_response(analysis)
                else:
                    return f"I couldn't analyze {stock_symbol}. Please check the stock symbol and try again."
            else:
                return "Please specify a stock symbol for analysis. For example: 'Analyze HDFC Bank stock'"
                
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
            return f"Error retrieving knowledge: {str(e)}"
    
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
        """Extract stock symbol from user message"""
        import re
        
        # Convert to uppercase for consistent processing
        message_upper = message.upper()
        
        # Remove common words and clean up
        words_to_remove = ['ANALYZE', 'STOCK', 'SHARES', 'OF', 'THE', 'PRICE', 'PERFORMANCE', 'INFORMATION', 'COMPANY', 'BANK', 'LIMITED']
        cleaned_message = message_upper
        
        for word in words_to_remove:
            cleaned_message = cleaned_message.replace(word, ' ').strip()
        
        # Look for exact company name matches first (higher priority)
        company_mappings = {
            'HDFC': 'HDFCBANK',
            'HDFC BANK': 'HDFCBANK',
            'ICICI': 'ICICIBANK', 
            'ICICI BANK': 'ICICIBANK',
            'STATE BANK': 'SBIN',
            'SBI': 'SBIN',
            'RELIANCE': 'RELIANCE',
            'RELIANCE INDUSTRIES': 'RELIANCE',
            'TATA MOTORS': 'TATAMOTORS',
            'TATA MOTORS': 'TATAMOTORS',
            'INFOSYS': 'INFY',
            'TCS': 'TCS',
            'WIPRO': 'WIPRO',
            'APPLE': 'AAPL',
            'TESLA': 'TSLA',
            'GOOGLE': 'GOOGL',
            'MICROSOFT': 'MSFT',
            'AMAZON': 'AMZN'
        }
        
        # Check for exact company name matches
        for company, symbol in company_mappings.items():
            if company in cleaned_message:
                return symbol
        
        # Extract potential stock symbols (3-5 letter words)
        words = re.findall(r'\b[A-Z]{3,5}\b', cleaned_message)
        
        # Filter out common words that aren't stock symbols
        filtered_words = []
        for word in words:
            if word not in words_to_remove and len(word) >= 3:
                filtered_words.append(word)
        
        if filtered_words:
            return filtered_words[0]  # Return first potential symbol
        
        return None
    
    def _format_stock_response(self, analysis: Dict[str, Any]) -> str:
        """Format stock analysis response"""
        try:
            symbol = analysis.get('symbol', 'Unknown')
            price = analysis.get('price', 0)
            change = analysis.get('change', 0)
            change_percent = analysis.get('change_percent', 0)
            insights = analysis.get('insights', [])
            
            response = f"📈 {symbol} Stock Analysis\n\n"
            response += f"Current Price: ₹{price:.2f}\n"
            response += f"Change: ₹{change:.2f} ({change_percent:.2f}%)\n\n"
            
            response += "Key Insights:\n"
            for insight in insights[:3]:  # Show top 3 insights
                response += f"• {insight}\n"
            
            response += "\n💡 This analysis is for educational purposes only and not financial advice."
            response += "\n📊 Data provided by financial APIs"
            
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
            
            response = f"💼 Portfolio Analysis\n\n"
            response += f"Total Value: ₹{total_value:.2f}\n"
            response += f"Total Return: ₹{total_return:.2f} ({return_percent:.2f}%)\n\n"
            
            response += "Top Holdings:\n"
            for holding in holdings[:5]:  # Show top 5 holdings
                symbol = holding.get('symbol', 'Unknown')
                value = holding.get('value', 0)
                response += f"• {symbol}: ₹{value:.2f}\n"
            
            response += "\nPortfolio Insights:\n"
            for insight in insights[:3]:  # Show top 3 insights
                response += f"• {insight}\n"
            
            response += "\n💡 This analysis is for educational purposes only and not financial advice."
            
            return response
            
        except Exception as e:
            return f"Error formatting portfolio response: {str(e)}"
    
    def _format_news_response(self, news: Dict[str, Any]) -> str:
        """Format market news response"""
        try:
            articles = news.get('articles', [])
            
            if not articles:
                return "No market news available at the moment."
            
            response = f"📰 Market News Update\n\n"
            
            for article in articles[:5]:  # Show top 5 articles
                title = article.get('title', 'No title')
                source = article.get('source', 'Unknown source')
                response += f"• {title} ({source})\n"
            
            response += "\n💡 News summaries are for informational purposes only and not financial advice."
            response += "\n📰 Data provided by financial news APIs"
            
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
                response += "\n\n💡 This information is for educational purposes only and not financial advice."
            
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
