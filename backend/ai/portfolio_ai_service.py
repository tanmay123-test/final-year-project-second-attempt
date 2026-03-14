"""
Portfolio AI Service
Handles portfolio analysis for AI Financial Assistant
"""

import sqlite3
from typing import Dict, Any, List
from datetime import datetime

class PortfolioAIService:
    """Service for analyzing user portfolios"""
    
    def __init__(self):
        self.db_path = 'expertease.db'
        self._init_database()
    
    def _init_database(self):
        """Initialize portfolio database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create portfolio table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                stock_symbol TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                purchase_price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create ai_insights table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                insight TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing portfolio database: {str(e)}")
    
    def analyze_portfolio(self, user_id: int) -> Dict[str, Any]:
        """
        Analyze user's portfolio
        
        Args:
            user_id: User ID
            
        Returns:
            Portfolio analysis results
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get user's portfolio
            cursor.execute("""
            SELECT stock_symbol, quantity, purchase_price, created_at
            FROM portfolio
            WHERE user_id = ?
            ORDER BY created_at DESC
            """, (user_id,))
            
            holdings = cursor.fetchall()
            
            if not holdings:
                return {
                    'success': False,
                    'error': 'No portfolio found. Please add stocks to your portfolio first.'
                }
            
            # Calculate portfolio metrics
            total_value = 0
            total_cost = 0
            holdings_data = []
            
            for holding in holdings:
                symbol = holding['stock_symbol']
                quantity = holding['quantity']
                purchase_price = holding['purchase_price']
                
                # Get current price (mock for now - in real implementation, call stock API)
                current_price = self._get_current_price(symbol)
                
                holding_value = quantity * current_price
                holding_cost = quantity * purchase_price
                holding_return = holding_value - holding_cost
                holding_return_percent = (holding_return / holding_cost) * 100 if holding_cost > 0 else 0
                
                total_value += holding_value
                total_cost += holding_cost
                
                holdings_data.append({
                    'symbol': symbol,
                    'quantity': quantity,
                    'purchase_price': purchase_price,
                    'current_price': current_price,
                    'value': holding_value,
                    'cost': holding_cost,
                    'return': holding_return,
                    'return_percent': holding_return_percent
                })
            
            # Calculate overall portfolio metrics
            total_return = total_value - total_cost
            return_percent = (total_return / total_cost) * 100 if total_cost > 0 else 0
            
            # Generate insights
            insights = self._generate_portfolio_insights(holdings_data, total_value, total_return)
            
            # Store insight
            self._store_insight(user_id, f"Portfolio analysis completed. Total value: ₹{total_value:.2f}", "portfolio_analysis")
            
            conn.close()
            
            return {
                'success': True,
                'total_value': total_value,
                'total_cost': total_cost,
                'total_return': total_return,
                'return_percent': return_percent,
                'holdings': holdings_data,
                'insights': insights
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error analyzing portfolio: {str(e)}"
            }
    
    def add_to_portfolio(self, user_id: int, stock_symbol: str, quantity: int, purchase_price: float) -> Dict[str, Any]:
        """
        Add stock to user's portfolio
        
        Args:
            user_id: User ID
            stock_symbol: Stock symbol
            quantity: Number of shares
            purchase_price: Purchase price per share
            
        Returns:
            Result of the operation
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO portfolio (user_id, stock_symbol, quantity, purchase_price)
            VALUES (?, ?, ?, ?)
            """, (user_id, stock_symbol.upper(), quantity, purchase_price))
            
            portfolio_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Store insight
            self._store_insight(user_id, f"Added {quantity} shares of {stock_symbol} at ₹{purchase_price}", "portfolio_add")
            
            return {
                'success': True,
                'portfolio_id': portfolio_id,
                'message': f"Successfully added {quantity} shares of {stock_symbol} to portfolio"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error adding to portfolio: {str(e)}"
            }
    
    def get_portfolio_holdings(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get user's portfolio holdings
        
        Args:
            user_id: User ID
            
        Returns:
            List of portfolio holdings
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM portfolio
            WHERE user_id = ?
            ORDER BY created_at DESC
            """, (user_id,))
            
            holdings = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return holdings
            
        except Exception as e:
            print(f"Error getting portfolio holdings: {str(e)}")
            return []
    
    def _get_current_price(self, stock_symbol: str) -> float:
        """
        Get current stock price (mock implementation)
        
        Args:
            stock_symbol: Stock symbol
            
        Returns:
            Current price
        """
        # Mock prices - in real implementation, call stock API
        mock_prices = {
            'HDFCBANK': 1585.75,
            'ICICIBANK': 987.65,
            'RELIANCE': 2845.30,
            'TCS': 3689.45,
            'INFY': 1456.80,
            'WIPRO': 445.80,
            'SBIN': 600.0,
            'TATAMOTORS': 400.0
        }
        
        return mock_prices.get(stock_symbol.upper(), 1000.0)
    
    def _generate_portfolio_insights(self, holdings: List[Dict], total_value: float, total_return: float) -> List[str]:
        """
        Generate portfolio insights
        
        Args:
            holdings: Portfolio holdings
            total_value: Total portfolio value
            total_return: Total return
            
        Returns:
            List of insights
        """
        insights = []
        
        # Performance insights
        if total_return > 0:
            insights.append(f"📈 Your portfolio is profitable with ₹{total_return:.2f} total return")
        else:
            insights.append(f"📉 Your portfolio has a loss of ₹{abs(total_return):.2f}")
        
        # Diversification insights
        if len(holdings) == 1:
            insights.append("⚠️ Your portfolio is concentrated in a single stock. Consider diversifying.")
        elif len(holdings) < 5:
            insights.append("💡 Consider adding more stocks to improve diversification.")
        else:
            insights.append("👍 Good diversification with multiple stocks.")
        
        # Top performer
        if holdings:
            top_performer = max(holdings, key=lambda x: x['return_percent'])
            if top_performer['return_percent'] > 10:
                insights.append(f"🏆 {top_performer['symbol']} is your best performer with {top_performer['return_percent']:.1f}% return")
        
        # Risk warning
        total_return_percent = (total_return / (total_value - total_return)) * 100 if (total_value - total_return) > 0 else 0
        if abs(total_return_percent) > 20:
            insights.append("⚠️ Your portfolio shows high volatility. Consider reviewing your risk tolerance.")
        
        return insights
    
    def _store_insight(self, user_id: int, insight: str, insight_type: str):
        """
        Store AI insight
        
        Args:
            user_id: User ID
            insight: Insight text
            insight_type: Type of insight
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO ai_insights (user_id, insight, insight_type)
            VALUES (?, ?, ?)
            """, (user_id, insight, insight_type))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error storing insight: {str(e)}")
    
    def get_insights(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get AI insights for user
        
        Args:
            user_id: User ID
            limit: Maximum number of insights
            
        Returns:
            List of insights
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM ai_insights
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """, (user_id, limit))
            
            insights = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return insights
            
        except Exception as e:
            print(f"Error getting insights: {str(e)}")
            return []

# Singleton instance
portfolio_ai_service = PortfolioAIService()
