"""
Portfolio Service
Business logic for portfolio management and analysis
"""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from ..models.portfolio import Portfolio
from ..stock_service import stock_service

class PortfolioService:
    """
    Service class for portfolio management and analysis
    """
    
    def __init__(self):
        self.conn = sqlite3.connect('expertease.db')
        self.conn.row_factory = sqlite3.Row
        self.create_portfolio_tables()
    
    def create_portfolio_tables(self):
        """Create portfolio tables if they don't exist"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            stock_symbol TEXT NOT NULL,
            quantity REAL NOT NULL,
            purchase_price REAL NOT NULL,
            purchase_date TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            insight TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        self.conn.commit()
    
    def add_to_portfolio(self, user_id: int, stock_symbol: str, quantity: float, purchase_price: float) -> Portfolio:
        """
        Add a stock to user's portfolio
        """
        try:
            # Validate inputs
            if not stock_symbol or not stock_symbol.strip():
                raise ValueError("Stock symbol is required")
            
            if quantity <= 0:
                raise ValueError("Quantity must be greater than 0")
            
            if purchase_price <= 0:
                raise ValueError("Purchase price must be greater than 0")
            
            # Check if user already has this stock
            existing = self.conn.execute("""
            SELECT id FROM portfolios 
            WHERE user_id = ? AND stock_symbol = ?
            """, (user_id, stock_symbol.upper())).fetchone()
            
            if existing:
                # Update existing portfolio item
                cursor = self.conn.execute("""
                UPDATE portfolios 
                SET quantity = quantity + ?, purchase_price = ?, updated_at = ?
                WHERE user_id = ? AND stock_symbol = ?
                """, (quantity, purchase_price, datetime.utcnow(), user_id, stock_symbol.upper()))
            else:
                # Create new portfolio item
                cursor = self.conn.execute("""
                INSERT INTO portfolios 
                (user_id, stock_symbol, quantity, purchase_price, purchase_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, stock_symbol.upper(), quantity, purchase_price, datetime.utcnow(), datetime.utcnow(), datetime.utcnow()))
            
            self.conn.commit()
            
            # Get the portfolio item
            cursor = self.conn.execute("""
            SELECT * FROM portfolios 
            WHERE user_id = ? AND stock_symbol = ?
            ORDER BY id DESC LIMIT 1
            """, (user_id, stock_symbol.upper()))
            
            item = cursor.fetchone()
            
            if item:
                return Portfolio(
                    id=item['id'],
                    user_id=item['user_id'],
                    stock_symbol=item['stock_symbol'],
                    quantity=item['quantity'],
                    purchase_price=item['purchase_price'],
                    purchase_date=datetime.fromisoformat(item['purchase_date']),
                    created_at=datetime.fromisoformat(item['created_at']),
                    updated_at=datetime.fromisoformat(item['updated_at'])
                )
            else:
                raise ValueError("Failed to create portfolio item")
                
        except Exception as e:
            print(f"Error getting user portfolio: {str(e)}")
            return []
    
    def get_portfolio_with_current_prices(self, user_id: int) -> Dict[str, Any]:
        """
        Get all portfolio items for a user
        """
        try:
            cursor = self.conn.execute("""
            SELECT * FROM portfolios 
            WHERE user_id = ?
            ORDER BY created_at DESC
            """, (user_id,))
            
            items = []
            for row in cursor.fetchall():
                items.append(Portfolio(
                    id=row['id'],
                    user_id=row['user_id'],
                    stock_symbol=row['stock_symbol'],
                    quantity=row['quantity'],
                    purchase_price=row['purchase_price'],
                    purchase_date=datetime.fromisoformat(row['purchase_date']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                ))
            return items
            
        except Exception as e:
            print(f"Error getting user portfolio: {str(e)}")
            return []
    
    def get_portfolio_with_current_prices(self, user_id: int) -> Dict[str, Any]:
        """
        Get user portfolio with current stock prices
        """
        try:
            portfolio = self.get_user_portfolio(user_id)
            
            if not portfolio:
                return {
                    'holdings': [],
                    'total_investment': 0,
                    'current_value': 0,
                    'portfolio_metrics': {}
                }
            
            holdings = []
            total_investment = 0
            current_value = 0
            
            for item in portfolio:
                # Get current stock data
                stock_data = stock_service.get_stock_data(item.stock_symbol)
                
                if "error" not in stock_data:
                    current_price = stock_data.get("price", item.purchase_price)
                    sector = stock_data.get("sector", "Unknown")
                else:
                    current_price = item.purchase_price
                    sector = "Unknown"
                
                current_item_value = item.quantity * current_price
                profit_loss = current_item_value - item.total_investment
                
                # Calculate percentage
                profit_loss_percentage = 0
                if item.total_investment > 0:
                    profit_loss_percentage = (profit_loss / item.total_investment) * 100
                
                holdings.append({
                    'stock_symbol': item.stock_symbol,
                    'quantity': item.quantity,
                    'purchase_price': item.purchase_price,
                    'current_price': current_price,
                    'current_value': current_item_value,
                    'profit_loss': profit_loss,
                    'profit_loss_percentage': profit_loss_percentage,
                    'days_held': item.days_held,
                    'sector': sector
                })
                
                total_investment += item.total_investment
                current_value += current_item_value
            
            return {
                'holdings': holdings,
                'total_investment': total_investment,
                'current_value': current_value,
                'portfolio_metrics': {
                    'stock_count': len(holdings),
                    'sector_count': len(set(h['sector'] for h in holdings))
                }
            }
            
        except Exception as e:
            print(f"Error getting portfolio with prices: {str(e)}")
            return {
                'holdings': [],
                'total_investment': 0,
                'current_value': 0,
                'portfolio_metrics': {}
            }
    
    def remove_from_portfolio(self, portfolio_id: int, user_id: int) -> bool:
        """
        Remove a stock from user's portfolio
        """
        try:
            # Check if portfolio item exists and belongs to user
            item = self.conn.execute("""
            SELECT * FROM portfolios 
            WHERE id = ? AND user_id = ?
            """, (portfolio_id, user_id)).fetchone()
            
            if not item:
                return False
            
            # Delete the portfolio item
            self.conn.execute("""
            DELETE FROM portfolios 
            WHERE id = ?
            """, (portfolio_id,))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error removing from portfolio: {str(e)}")
            self.conn.rollback()
            return False
    
    def update_portfolio(self, portfolio_id: int, user_id: int, quantity: Optional[float] = None, purchase_price: Optional[float] = None) -> Optional[Portfolio]:
        """
        Update a portfolio item (quantity or price)
        """
        try:
            # Check if portfolio item exists and belongs to user
            item = self.conn.execute("""
            SELECT * FROM portfolios 
            WHERE id = ? AND user_id = ?
            """, (portfolio_id, user_id)).fetchone()
            
            if not item:
                return None
            
            # Build update query
            updates = []
            params = []
            
            if quantity is not None:
                updates.append("quantity = ?")
                params.append(quantity)
            
            if purchase_price is not None:
                updates.append("purchase_price = ?")
                params.append(purchase_price)
            
            updates.append("updated_at = ?")
            params.append(datetime.utcnow())
            
            params.append(portfolio_id)
            params.append(user_id)
            
            # Execute update
            update_sql = f"UPDATE portfolios SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
            self.conn.execute(update_sql, tuple(params))
            self.conn.commit()
            
            # Get updated item
            updated_item = self.conn.execute("""
            SELECT * FROM portfolios 
            WHERE id = ? AND user_id = ?
            """, (portfolio_id, user_id)).fetchone()
            
            if updated_item:
                return Portfolio(
                    id=updated_item['id'],
                    user_id=updated_item['user_id'],
                    stock_symbol=updated_item['stock_symbol'],
                    quantity=updated_item['quantity'],
                    purchase_price=updated_item['purchase_price'],
                    purchase_date=datetime.fromisoformat(updated_item['purchase_date']),
                    created_at=datetime.fromisoformat(updated_item['created_at']),
                    updated_at=datetime.fromisoformat(updated_item['updated_at'])
                )
            
            return None
            
        except Exception as e:
            print(f"Error updating portfolio: {str(e)}")
            self.conn.rollback()
            return None
    
    def get_portfolio_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get portfolio statistics for a user
        """
        try:
            portfolio_data = self.get_portfolio_with_current_prices(user_id)
            
            if not portfolio_data['holdings']:
                return {
                    'total_investment': 0,
                    'current_value': 0,
                    'stock_count': 0,
                    'sector_count': 0,
                    'profit_loss': 0,
                    'diversification_score': 0
                }
            
            holdings = portfolio_data['holdings']
            
            # Calculate metrics
            total_investment = portfolio_data['total_investment']
            current_value = portfolio_data['current_value']
            total_profit_loss = current_value - total_investment
            profit_loss_percentage = (total_profit_loss / total_investment * 100) if total_investment > 0 else 0
            
            # Sector distribution
            sector_counts = {}
            for holding in holdings:
                sector = holding.get('sector', 'Unknown')
                sector_counts[sector] = sector_counts.get(sector, 0) + 1
            
            # Diversification score (inverse of concentration)
            max_sector_count = max(sector_counts.values()) if sector_counts else 1
            diversification_score = 100 - ((max_sector_count - 1) / len(sector_counts)) * 100
            
            # Best and worst performers
            best_performer = None
            worst_performer = None
            if holdings:
                best_performer = max(holdings, key=lambda x: x.get('profit_loss_percentage', 0))
                worst_performer = min(holdings, key=lambda x: x.get('profit_loss_percentage', 0))
            
            return {
                'total_investment': total_investment,
                'current_value': current_value,
                'stock_count': len(holdings),
                'sector_count': len(sector_counts),
                'total_profit_loss': total_profit_loss,
                'profit_loss_percentage': profit_loss_percentage,
                'diversification_score': diversification_score,
                'best_performer': best_performer.stock_symbol if best_performer else None,
                'worst_performer': worst_performer.stock_symbol if worst_performer else None
            }
            
        except Exception as e:
            print(f"Error getting portfolio statistics: {str(e)}")
            return {
                'total_investment': 0,
                'current_value': 0,
                'stock_count': 0,
                'sector_count': 0,
                'profit_loss': 0,
                'diversification_score': 0
            }
    
    def get_portfolio_performance(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get portfolio performance over specified period
        """
        try:
            portfolio_data = self.get_portfolio_with_current_prices(user_id)
            
            if not portfolio_data['holdings']:
                return {
                    'period_days': days,
                    'start_value': 0,
                    'end_value': 0,
                    'period_return': 0,
                    'period_return_percentage': 0,
                    'holdings': []
                }
            
            # Calculate performance metrics
            start_value = portfolio_data['current_value']
            end_value = portfolio_data['current_value']
            period_return = end_value - start_value
            period_return_percentage = (period_return / start_value * 100) if start_value > 0 else 0
            
            return {
                'period_days': days,
                'start_value': start_value,
                'end_value': end_value,
                'period_return': period_return,
                'period_return_percentage': period_return_percentage,
                'holdings': portfolio_data['holdings']
            }
            
        except Exception as e:
            print(f"Error getting portfolio performance: {str(e)}")
            return {
                'period_days': days,
                'start_value': 0,
                'end_value': 0,
                'period_return': 0,
                'period_return_percentage': 0,
                'holdings': []
            }
    
    def add_portfolio_insight(self, user_id: int, insight: str) -> bool:
        """
        Add AI-generated insight to portfolio
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
            INSERT INTO portfolio_insights (user_id, insight, created_at)
            VALUES (?, ?, ?)
            """, (user_id, insight, datetime.utcnow()))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error adding portfolio insight: {str(e)}")
            self.conn.rollback()
            return False
    
    def get_portfolio_insights(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get portfolio insights for a user
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
            SELECT * FROM portfolio_insights 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            
            insights = []
            for row in cursor.fetchall():
                insights.append({
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'insight': row['insight'],
                    'created_at': row['created_at']
                })
            
            return insights
            
        except Exception as e:
            print(f"Error getting portfolio insights: {str(e)}")
            return []
    
    def clear_user_portfolio(self, user_id: int) -> bool:
        """
        Clear all portfolio items for a user
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
            DELETE FROM portfolios 
            WHERE user_id = ?
            """, (user_id,))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Error clearing portfolio: {str(e)}")
            self.conn.rollback()
            return False
    
    def get_all_portfolios(self) -> List[Dict[str, Any]]:
        """
        Get all portfolios (for admin use)
        """
        try:
            cursor = self.conn.execute("""
            SELECT p.*, u.username 
            FROM portfolios p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            """)
            
            portfolios = []
            for row in cursor.fetchall():
                portfolios.append({
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'stock_symbol': row['stock_symbol'],
                    'quantity': row['quantity'],
                    'purchase_price': row['purchase_price'],
                    'purchase_date': row['purchase_date'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'username': row['username']
                })
            
            return portfolios
            
        except Exception as e:
            print(f"Error getting all portfolios: {str(e)}")
            return []

# Singleton instance for reuse
portfolio_service = PortfolioService()
