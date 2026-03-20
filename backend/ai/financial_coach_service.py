"""
Financial Coach Service
AI-powered financial coaching and insights generation
"""

import os
import httpx
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sqlite3

try:
    from .gemini_client import gemini_client
except ImportError:
    from ai.gemini_client import gemini_client

try:
    from services.portfolio_service import portfolio_service
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from services.portfolio_service import portfolio_service

class FinancialCoachService:
    """
    AI service for financial coaching and personalized insights
    """
    
    def __init__(self):
        self.gemini_client = gemini_client
        self.portfolio_service = portfolio_service
        
        # Financial coach prompt template
        self.coach_prompt = """You are a financial education coach providing personalized insights.

Based on the user's financial data, provide educational coaching and insights.

User Financial Data:
{financial_data}

Portfolio Analysis:
{portfolio_analysis}

Spending Patterns:
{spending_patterns}

Goals Progress:
{goals_progress}

IMPORTANT RULES:
* DO NOT give financial advice or specific recommendations
* DO NOT suggest specific investments or amounts
* Focus on education and awareness
* Provide actionable educational insights
* Explain financial concepts clearly
* Include risk awareness when appropriate
* Be encouraging and supportive

User Request:
{user_message}

Provide helpful financial education and coaching insights:"""
    
    async def generate_financial_insights(self, user_id: int, user_message: str = "") -> Dict[str, Any]:
        """
        Generate personalized financial insights for a user
        """
        try:
            # Get user's financial data
            financial_data = await self._get_user_financial_data(user_id)
            
            if not financial_data:
                return {
                    "success": False,
                    "error": "I couldn't access your financial data. Please add some portfolio items or transactions first.",
                    "suggestions": [
                        "Add stocks to your portfolio",
                        "Track your spending patterns",
                        "Set financial goals"
                    ]
                }
            
            # Get portfolio analysis
            portfolio_analysis = self._analyze_portfolio(financial_data.get("portfolio", {}))
            
            # Get spending patterns
            spending_patterns = self._analyze_spending_patterns(financial_data.get("spending", {}))
            
            # Get goals progress
            goals_progress = self._analyze_goals_progress(financial_data.get("goals", {}))
            
            # Build the full prompt
            full_prompt = self.coach_prompt.format(
                financial_data=self._format_financial_data(financial_data),
                portfolio_analysis=portfolio_analysis,
                spending_patterns=spending_patterns,
                goals_progress=goals_progress,
                user_message=user_message or "Provide general financial insights"
            )
            
            # Generate AI response
            response = await self.gemini_client.generate_ai_response(full_prompt)
            
            # Store insight in database
            insight_id = await self._store_insight(user_id, response, "financial_coach")
            
            return {
                "success": True,
                "response": response,
                "insight_id": insight_id,
                "data_summary": {
                    "portfolio_value": financial_data.get("portfolio", {}).get("current_value", 0),
                    "total_spending": financial_data.get("spending", {}).get("total_monthly", 0),
                    "goals_count": len(financial_data.get("goals", {})),
                    "insight_type": "financial_coach"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error generating financial insights: {str(e)}")
            return {
                "success": False,
                "error": "I encountered an error while generating your financial insights. Please try again later.",
                "suggestions": [
                    "Check your internet connection",
                    "Try again later",
                    "Contact support if the issue persists"
                ]
            }
    
    async def _get_user_financial_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive financial data for a user
        """
        try:
            # Get portfolio data
            portfolio_data = self.portfolio_service.get_portfolio_with_current_prices(user_id)
            
            # Get spending data (mock for now)
            spending_data = self._get_mock_spending_data(user_id)
            
            # Get goals data (mock for now)
            goals_data = self._get_mock_goals_data(user_id)
            
            return {
                "portfolio": portfolio_data,
                "spending": spending_data,
                "goals": goals_data,
                "user_id": user_id
            }
            
        except Exception as e:
            print(f"Error getting user financial data: {str(e)}")
            return {}
    
    def _analyze_portfolio(self, portfolio_data: Dict[str, Any]) -> str:
        """
        Analyze portfolio and return insights
        """
        try:
            holdings = portfolio_data.get("holdings", [])
            
            if not holdings:
                return "No portfolio data available."
            
            total_value = portfolio_data.get("current_value", 0)
            total_investment = portfolio_data.get("total_investment", 0)
            
            # Calculate sector allocation
            sectors = {}
            for holding in holdings:
                sector = holding.get("sector", "Unknown")
                sectors[sector] = sectors.get(sector, 0) + holding.get("current_value", 0)
            
            # Calculate diversification score
            max_sector_allocation = max(sectors.values()) if sectors else 0
            diversification_score = 100 - (max_sector_allocation / total_value * 100) if total_value > 0 else 0
            
            # Find best and worst performers
            best_performer = None
            worst_performer = None
            
            if holdings:
                best_performer = max(holdings, key=lambda x: x.get("profit_loss_percentage", 0))
                worst_performer = min(holdings, key=lambda x: x.get("profit_loss_percentage", 0))
            
            analysis = f"""
Portfolio Analysis:
- Total Value: ${total_value:,.2f}
- Total Investment: ${total_investment:,.2f}
- Overall Return: ${total_value - total_investment:,.2f} ({((total_value - total_investment) / total_investment * 100):.1f}%)
- Diversification Score: {diversification_score:.1f}/100
- Number of Holdings: {len(holdings)}
- Sector Allocation: {', '.join([f'{k}: {v/total_value*100:.1f}%' for k, v in sectors.items()])}
- Best Performer: {best_performer.get('stock_symbol', 'N/A')} ({best_performer.get('profit_loss_percentage', 0):.1f}%)
- Worst Performer: {worst_performer.get('stock_symbol', 'N/A')} ({worst_performer.get('profit_loss_percentage', 0):.1f}%)
"""
            
            return analysis.strip()
            
        except Exception as e:
            print(f"Error analyzing portfolio: {str(e)}")
            return "Portfolio analysis unavailable."
    
    def _analyze_spending_patterns(self, spending_data: Dict[str, Any]) -> str:
        """
        Analyze spending patterns and return insights
        """
        try:
            categories = spending_data.get("categories", {})
            total_monthly = spending_data.get("total_monthly", 0)
            
            if not categories:
                return "No spending data available."
            
            # Find top spending categories
            sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            
            analysis = f"""
Spending Analysis:
- Total Monthly Spending: ${total_monthly:,.2f}
- Top Spending Categories: {', '.join([f'{k}: ${v:,.2f}' for k, v in sorted_categories[:3]])}
- Average Daily Spending: ${total_monthly/30:,.2f}
- Number of Categories: {len(categories)}
"""
            
            return analysis.strip()
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {str(e)}")
            return "Spending analysis unavailable."
    
    def _analyze_goals_progress(self, goals_data: Dict[str, Any]) -> str:
        """
        Analyze goals progress and return insights
        """
        try:
            goals = goals_data.get("goals", [])
            
            if not goals:
                return "No goals data available."
            
            completed_goals = sum(1 for goal in goals if goal.get("completed", False))
            total_goals = len(goals)
            
            # Calculate average progress
            total_progress = sum(goal.get("progress", 0) for goal in goals)
            avg_progress = total_progress / total_goals if total_goals > 0 else 0
            
            analysis = f"""
Goals Analysis:
- Total Goals: {total_goals}
- Completed Goals: {completed_goals}
- Average Progress: {avg_progress:.1f}%
- Active Goals: {total_goals - completed_goals}
"""
            
            return analysis.strip()
            
        except Exception as e:
            print(f"Error analyzing goals progress: {str(e)}")
            return "Goals analysis unavailable."
    
    def _format_financial_data(self, financial_data: Dict[str, Any]) -> str:
        """
        Format financial data for AI prompt
        """
        try:
            portfolio = financial_data.get("portfolio", {})
            spending = financial_data.get("spending", {})
            goals = financial_data.get("goals", {})
            
            formatted_data = f"""
Portfolio Summary:
- Current Value: ${portfolio.get('current_value', 0):,.2f}
- Total Investment: ${portfolio.get('total_investment', 0):,.2f}
- Holdings Count: {len(portfolio.get('holdings', []))}
- Diversification Score: {portfolio.get('diversification_score', 0):.1f}/100

Spending Summary:
- Monthly Total: ${spending.get('total_monthly', 0):,.2f}
- Categories: {len(spending.get('categories', {}))}
- Daily Average: ${spending.get('total_monthly', 0)/30:,.2f}

Goals Summary:
- Total Goals: {len(goals.get('goals', []))}
- Completed: {sum(1 for goal in goals.get('goals', []) if goal.get('completed', False))}
- Average Progress: {sum(goal.get('progress', 0) for goal in goals.get('goals', [])) / len(goals.get('goals', [])) if goals.get('goals') else 0:.1f}%
"""
            
            return formatted_data.strip()
            
        except Exception as e:
            print(f"Error formatting financial data: {str(e)}")
            return "Financial data unavailable."
    
    def _get_mock_spending_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get mock spending data for testing
        """
        return {
            "total_monthly": 3500.00,
            "categories": {
                "Food": 800.00,
                "Transportation": 400.00,
                "Entertainment": 300.00,
                "Shopping": 600.00,
                "Bills": 1200.00,
                "Other": 200.00
            },
            "trends": {
                "food": "increasing",
                "transportation": "stable",
                "entertainment": "decreasing"
            }
        }
    
    def _get_mock_goals_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get mock goals data for testing
        """
        return {
            "goals": [
                {
                    "id": 1,
                    "name": "Emergency Fund",
                    "target": 10000.00,
                    "current": 7500.00,
                    "progress": 75.0,
                    "completed": False,
                    "deadline": "2024-12-31"
                },
                {
                    "id": 2,
                    "name": "Vacation Fund",
                    "target": 5000.00,
                    "current": 2000.00,
                    "progress": 40.0,
                    "completed": False,
                    "deadline": "2024-08-31"
                },
                {
                    "id": 3,
                    "name": "New Laptop",
                    "target": 2000.00,
                    "current": 2000.00,
                    "progress": 100.0,
                    "completed": True,
                    "deadline": "2024-03-31"
                }
            ]
        }
    
    async def _store_insight(self, user_id: int, insight: str, insight_type: str) -> int:
        """
        Store AI insight in database
        """
        try:
            conn = sqlite3.connect('expertease.db')
            cursor = conn.cursor()
            
            # Create ai_insights table if it doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                insight TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Insert insight
            cursor.execute("""
            INSERT INTO ai_insights (user_id, insight, insight_type, created_at)
            VALUES (?, ?, ?, ?)
            """, (user_id, insight, insight_type, datetime.utcnow()))
            
            insight_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return insight_id
            
        except Exception as e:
            print(f"Error storing insight: {str(e)}")
            return 0
    
    def get_user_insights(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get user's AI insights
        """
        try:
            conn = sqlite3.connect('expertease.db')
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM ai_insights 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """, (user_id, limit))
            
            insights = []
            for row in cursor.fetchall():
                insights.append({
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "insight": row["insight"],
                    "insight_type": row["insight_type"],
                    "created_at": row["created_at"]
                })
            
            conn.close()
            return insights
            
        except Exception as e:
            print(f"Error getting user insights: {str(e)}")
            return []
    
    async def test_financial_coach(self) -> bool:
        """
        Test the financial coach service
        """
        try:
            # Test with a sample user
            result = await self.generate_financial_insights(1, "Provide general financial insights")
            return result.get("success", False)
            
        except Exception as e:
            print(f"Error testing financial coach: {str(e)}")
            return False
    
    def get_coaching_topics(self) -> List[str]:
        """
        Get available coaching topics
        """
        return [
            "portfolio_analysis",
            "spending_patterns",
            "goal_progress",
            "risk_management",
            "investment_education",
            "budget_optimization",
            "savings_strategies",
            "debt_management"
        ]
    
    def get_sample_coaching_queries(self) -> List[str]:
        """
        Get sample coaching queries
        """
        return [
            "Analyze my portfolio performance",
            "How can I improve my spending habits?",
            "Am I on track with my financial goals?",
            "What are the risks in my portfolio?",
            "How can I diversify better?",
            "What should I know about budgeting?",
            "How can I save more effectively?",
            "What are common investment mistakes?"
        ]

# Singleton instance for reuse
financial_coach_service = FinancialCoachService()
