"""
AI Group Service
Handles AI assistant functionality within AI Groups
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import sqlite3
import re

try:
    from .gemini_client import gemini_client
    from .stock_ai_service import stock_ai_service
    from .knowledge_ai_service import knowledge_ai_service
    from .financial_coach_service import financial_coach_service
    from ..services.news_service import news_service
    from ..services.chat_history_service import chat_history_service
except ImportError:
    from ai.gemini_client import gemini_client
    from ai.stock_ai_service import stock_ai_service
    from ai.knowledge_ai_service import knowledge_ai_service
    from ai.financial_coach_service import financial_coach_service
    from services.news_service import news_service
    from services.chat_history_service import chat_history_service

class AIGroupService:
    """
    Service for handling AI assistant functionality in groups
    """
    
    def __init__(self):
        self.gemini_client = gemini_client
        self.ai_user_id = -1  # Special user ID for AI assistant
    
    async def handle_ai_group_message(self, group_id: int, message: str) -> Optional[Dict[str, Any]]:
        """
        Handle AI response to user message in group with comprehensive AI services
        
        Args:
            group_id: Group ID where message was sent
            message: User message
            user_id: User ID who sent the message
            
        Returns:
            AI response message object or None
        """
        try:
            # Store user message in chat history
            chat_history_service.store_message(group_id, user_id, message, "user_message")
            
            # Check if AI should respond
            if not self._should_ai_respond(message):
                return None
            
            # Check if AI is a member of group
            if not self._is_ai_member_of_group(group_id):
                return None
            
            # Determine message type and handle accordingly
            message_type = self._determine_message_type(message)
            ai_response = None
            response_type = "ai_response"
            
            if message_type == "stock":
                # Check if it's a comparison query
                if "vs" in message.lower() or "compare" in message.lower():
                    # Handle stock comparison
                    comparison_result = await stock_ai_service.compare_stocks(message)
                    
                    if comparison_result.get("success"):
                        ai_response = comparison_result["analysis"]
                        response_type = "ai_stock_comparison"
                    else:
                        ai_response = comparison_result.get("error", "I couldn't compare those stocks. Please provide valid company names.")
                        response_type = "ai_stock_comparison"
                else:
                    # Handle regular stock analysis
                    stock_result = await stock_ai_service.generate_stock_analysis(message)
                    
                    if stock_result.get("success"):
                        ai_response = stock_result["analysis"]
                        response_type = "ai_stock_analysis"
                    else:
                        ai_response = stock_result.get("error", "I couldn't analyze that stock. Please provide a company name or stock symbol.")
                        response_type = "ai_stock_analysis"
            
            elif message_type == "portfolio":
                # Handle portfolio analysis
                # Extract user_id from context (for demo, use 1)
                user_id = 1  # In production, this would come from the message context
                portfolio_result = await financial_coach_service.generate_financial_insights(user_id, message)
                
                if portfolio_result.get("success"):
                    ai_response = portfolio_result["response"]
                    response_type = "ai_portfolio_analysis"
                else:
                    ai_response = portfolio_result.get("error", "I couldn't access your portfolio. Please add some portfolio items first.")
                    response_type = "ai_portfolio_analysis"
            
            elif message_type == "knowledge":
                # Handle knowledge-based response
                knowledge_result = await knowledge_ai_service.generate_knowledge_response(message)
                
                if knowledge_result.get("success"):
                    ai_response = knowledge_result["response"]
                    response_type = "ai_knowledge_response"
                else:
                    ai_response = knowledge_result.get("error", "I couldn't find relevant information for your question.")
                    response_type = "ai_knowledge_response"
            
            elif message_type == "news":
                # Handle news summarization
                news_articles = await news_service.fetch_market_news(limit=5)
                news_result = await news_service.summarize_news(news_articles, message)
                
                if news_result.get("success"):
                    ai_response = news_result["summary"]
                    response_type = "ai_news_summary"
                else:
                    ai_response = "I couldn't fetch the latest financial news. Please try again later."
                    response_type = "ai_news_summary"
            
            else:
                # Regular financial education response
                ai_response = await self.gemini_client.generate_ai_response(message)
                response_type = "ai_response"
            
            # Store AI response in chat history
            if ai_response:
                chat_history_service.store_message(group_id, self.ai_user_id, ai_response, response_type)
            
            # Store AI response in database (for backward compatibility)
            conn = sqlite3.connect('expertease.db')
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO group_messages (group_id, user_id, message, message_type, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (group_id, self.ai_user_id, ai_response, response_type, datetime.utcnow()))
            
            ai_message_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Return AI message data
            return {
                'id': ai_message_id,
                'group_id': group_id,
                'user_id': self.ai_user_id,
                'message': ai_response,
                'message_type': response_type,
                'created_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error handling AI group message: {str(e)}")
            return None
    
    def get_chat_history(self, group_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get chat history for a group
        
        Args:
            group_id: Group ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages
        """
        return chat_history_service.get_chat_history(group_id, limit)
    
    def get_chat_statistics(self, group_id: int) -> Dict[str, Any]:
        """
        Get chat statistics for a group
        
        Args:
            group_id: Group ID
            
        Returns:
            Dictionary with chat statistics
        """
        return chat_history_service.get_chat_statistics(group_id)
    
    def _should_ai_respond(self, message: str) -> bool:
        """
        Check if AI should respond to the message
        
        Args:
            message: User message
            
        Returns:
            True if AI should respond
        """
        # Check financial keywords (existing logic)
        if self.gemini_client.should_respond_to_message(message):
            return True
        
        # Check stock keywords
        if self._is_stock_query(message):
            return True
        
        # Check knowledge keywords
        if self._is_knowledge_query(message):
            return True
        
        # Check portfolio keywords
        if self._is_portfolio_query(message):
            return True
        
        # Check news keywords
        if self._is_news_query(message):
            return True
        
        return False
    
    def _determine_message_type(self, message: str) -> str:
        """
        Determine the type of message for appropriate AI service routing
        """
        message_lower = message.lower()
        
        # Check for stock queries first (most specific)
        if self._is_stock_query(message):
            return "stock"
        
        # Check for portfolio queries
        if self._is_portfolio_query(message):
            return "portfolio"
        
        # Check for news queries
        if self._is_news_query(message):
            return "news"
        
        # Check for knowledge queries
        if self._is_knowledge_query(message):
            return "knowledge"
        
        # Default to general response
        return "general"
    
    def _is_stock_query(self, message: str) -> bool:
        """
        Check if message is asking about stocks
        
        Args:
            message: User message
            
        Returns:
            True if message is stock-related
        """
        try:
            from services.stock_service import stock_service
            return stock_service.is_stock_query(message)
        except ImportError:
            # Fallback if stock service not available
            stock_keywords = [
                "stock", "stocks", "share", "shares", "equity", "equities",
                "ticker", "symbol", "market cap", "pe ratio", "dividend",
                "analyze", "analysis", "fundamentals", "valuation",
                "price", "trading", "investing", "investment", "portfolio"
            ]
            
            message_lower = message.lower()
            return any(keyword in message_lower for keyword in stock_keywords)
    
    def _is_ai_member_of_group(self, group_id: int) -> bool:
        """
        Check if AI assistant is a member of the group
        
        Args:
            group_id: Group ID
            
        Returns:
            True if AI is a member
        """
        try:
            conn = sqlite3.connect('expertease.db')
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT id FROM group_members 
            WHERE group_id = ? AND user_id = ? AND role = ?
            """, (group_id, self.ai_user_id, "ai_assistant"))
            
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
            
        except Exception as e:
            print(f"Error checking AI membership: {str(e)}")
            return False
    
    async def add_ai_to_group(self, group_id: int) -> bool:
        """
        Add AI assistant to a group
        
        Args:
            group_id: Group ID
            
        Returns:
            True if AI was added successfully
        """
        try:
            # Check if AI is already a member
            if self._is_ai_member_of_group(group_id):
                return True
            
            conn = sqlite3.connect('expertease.db')
            cursor = conn.cursor()
            
            # Add AI as member
            cursor.execute("""
            INSERT INTO group_members (group_id, user_id, role, joined_at)
            VALUES (?, ?, ?, ?)
            """, (group_id, self.ai_user_id, "ai_assistant", datetime.utcnow()))
            
            # Send welcome message
            welcome_msg = "  Hello! I'm your financial education assistant. I'm here to help explain financial concepts and answer your questions about investing and markets. Remember, I provide educational information only, not financial advice!"
            
            cursor.execute("""
            INSERT INTO group_messages (group_id, user_id, message, message_type, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (group_id, self.ai_user_id, welcome_msg, "ai_response", datetime.utcnow()))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error adding AI to group: {str(e)}")
            return False
    
    async def remove_ai_from_group(self, group_id: int) -> bool:
        """
        Remove AI assistant from a group
        
        Args:
            group_id: Group ID
            
        Returns:
            True if AI was removed successfully
        """
        try:
            conn = sqlite3.connect('expertease.db')
            cursor = conn.cursor()
            
            # Remove AI member
            cursor.execute("""
            DELETE FROM group_members 
            WHERE group_id = ? AND user_id = ? AND role = ?
            """, (group_id, self.ai_user_id, "ai_assistant"))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error removing AI from group: {str(e)}")
            return False
    
    async def get_ai_statistics(self, group_id: int) -> Dict[str, Any]:
        """
        Get AI assistant statistics for a group
        
        Args:
            group_id: Group ID
            
        Returns:
            AI statistics dictionary
        """
        try:
            conn = sqlite3.connect('expertease.db')
            cursor = conn.cursor()
            
            # Get AI messages count
            cursor.execute("""
            SELECT COUNT(*) as count FROM group_messages
            WHERE group_id = ? AND user_id = ? AND message_type = ?
            """, (group_id, self.ai_user_id, "ai_response"))
            
            ai_messages_count = cursor.fetchone()[0]
            
            # Get total messages count
            cursor.execute("""
            SELECT COUNT(*) as count FROM group_messages
            WHERE group_id = ?
            """, (group_id,))
            
            total_messages_count = cursor.fetchone()[0]
            
            # Calculate AI participation rate
            participation_rate = 0
            if total_messages_count > 0:
                participation_rate = (ai_messages_count / total_messages_count) * 100
            
            # Get recent AI activity (last 24 hours)
            from datetime import timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            cursor.execute("""
            SELECT COUNT(*) as count FROM group_messages
            WHERE group_id = ? AND user_id = ? AND message_type = ? AND created_at >= ?
            """, (group_id, self.ai_user_id, "ai_response", yesterday))
            
            recent_ai_messages = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "ai_messages_count": ai_messages_count,
                "total_messages_count": total_messages_count,
                "participation_rate": round(participation_rate, 2),
                "recent_ai_messages_24h": recent_ai_messages,
                "is_ai_member": self._is_ai_member_of_group(group_id)
            }
            
        except Exception as e:
            print(f"Error getting AI statistics: {str(e)}")
            return {
                "ai_messages_count": 0,
                "total_messages_count": 0,
                "participation_rate": 0,
                "recent_ai_messages_24h": 0,
                "is_ai_member": False
            }
    
    async def get_ai_response_quality(self, group_id: int) -> Dict[str, Any]:
        """
        Analyze AI response quality metrics
        
        Args:
            group_id: Group ID
            
        Returns:
            Response quality metrics
        """
        try:
            conn = sqlite3.connect('expertease.db')
            cursor = conn.cursor()
            
            # Get recent AI messages
            from datetime import timedelta
            last_week = datetime.utcnow() - timedelta(days=7)
            
            cursor.execute("""
            SELECT message FROM group_messages
            WHERE group_id = ? AND user_id = ? AND message_type = ? AND created_at >= ?
            """, (group_id, self.ai_user_id, "ai_response", last_week))
            
            recent_messages = cursor.fetchall()
            
            if not recent_messages:
                return {
                    "avg_response_length": 0,
                    "total_responses": 0,
                    "quality_score": 0
                }
            
            # Calculate average response length
            total_length = sum(len(msg[0]) for msg in recent_messages)
            avg_length = total_length / len(recent_messages)
            
            # Simple quality score based on response length and variety
            quality_score = min(100, (avg_length / 10))  # Normalize to 0-100
            
            conn.close()
            
            return {
                "avg_response_length": round(avg_length, 2),
                "total_responses": len(recent_messages),
                "quality_score": round(quality_score, 2)
            }
            
        except Exception as e:
            print(f"Error getting AI response quality: {str(e)}")
            return {
                "avg_response_length": 0,
                "total_responses": 0,
                "quality_score": 0
            }
    
    def get_trigger_keywords(self) -> Dict[str, Any]:
        """
        Get AI trigger keywords and statistics
        
        Returns:
            Trigger keywords information
        """
        keywords = self.gemini_client.get_financial_keywords()
        
        return {
            "trigger_keywords": keywords,
            "total_keywords": len(keywords),
            "categories": {
                "basic_concepts": ["explain", "what is", "how does", "why"],
                "investment_terms": ["stock", "investment", "market", "trading"],
                "financial_products": ["bond", "mutual fund", "etf", "portfolio"],
                "economic_concepts": ["economy", "inflation", "interest", "risk"],
                "personal_finance": ["money", "budget", "saving", "dividend"]
            }
        }

# Singleton instance for reuse
ai_group_service = AIGroupService()
