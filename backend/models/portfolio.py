"""
Portfolio Model
SQLAlchemy model for user portfolio tracking
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.base import Base

class Portfolio(Base):
    """
    Portfolio table model for tracking user investments
    """
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    stock_symbol = Column(String(10), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
    purchase_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    insights = relationship("PortfolioInsight", back_populates="portfolio", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, user_id={self.user_id}, symbol={self.stock_symbol}, quantity={self.quantity})>"
    
    def to_dict(self):
        """Convert to dictionary with calculated fields"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'stock_symbol': self.stock_symbol,
            'quantity': self.quantity,
            'purchase_price': self.purchase_price,
            'purchase_date': self.purchase_date,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        # Add calculated fields
        result['total_investment'] = self.total_investment
        result['days_held'] = self.days_held
        
        return result
    
    @property
    def total_investment(self):
        """Calculate total investment amount"""
        return self.quantity * self.purchase_price
    
    @property
    def days_held(self):
        """Calculate days since purchase"""
        if self.purchase_date:
            return (datetime.utcnow() - self.purchase_date).days
        return 0

class PortfolioInsight(Base, TimestampMixin):
    """
    Portfolio insights table for storing AI-generated analysis
    """
    __tablename__ = "portfolio_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    insight = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="portfolio_insights")
    
    def __repr__(self):
        return f"<PortfolioInsight(id={self.id}, user_id={self.user_id})>"
