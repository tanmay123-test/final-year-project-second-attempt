"""
Portfolio Pydantic Schemas
Request and response models for Portfolio API
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class AddPortfolioRequest(BaseModel):
    """Request schema for adding stock to portfolio"""
    stock_symbol: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    quantity: float = Field(..., gt=0, description="Number of shares")
    purchase_price: float = Field(..., gt=0, description="Purchase price per share")
    
    @validator('stock_symbol')
    def validate_symbol(cls, v):
        if not v or not v.strip():
            raise ValueError('Stock symbol cannot be empty')
        return v.strip().upper()
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v
    
    @validator('purchase_price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Purchase price must be greater than 0')
        return v

class UpdatePortfolioRequest(BaseModel):
    """Request schema for updating portfolio item"""
    quantity: Optional[float] = Field(None, gt=0, description="New quantity (optional)")
    purchase_price: Optional[float] = Field(None, gt=0, description="New purchase price (optional)")
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v
    
    @validator('purchase_price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Purchase price must be greater than 0')
        return v

class PortfolioResponse(BaseModel):
    """Response schema for portfolio data"""
    id: int
    user_id: int
    stock_symbol: str
    quantity: float
    purchase_price: float
    purchase_date: datetime
    total_investment: float
    days_held: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PortfolioListResponse(BaseModel):
    """Response schema for portfolio list"""
    portfolios: List[PortfolioResponse]
    total: int
    
    class Config:
        from_attributes = True

class PortfolioAnalysisRequest(BaseModel):
    """Request schema for portfolio analysis"""
    user_id: int = Field(..., gt=0, description="User ID")

class StockHolding(BaseModel):
    """Individual stock holding in portfolio"""
    stock_symbol: str
    quantity: float
    purchase_price: float
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percentage: Optional[float] = None
    days_held: int
    
    class Config:
        from_attributes = True

class SectorAllocation(BaseModel):
    """Sector allocation data"""
    sector: str
    allocation_percentage: float
    total_value: float
    
    class Config:
        from_attributes = True

class PortfolioMetrics(BaseModel):
    """Portfolio metrics and analysis"""
    total_investment: float
    current_value: float
    total_profit_loss: float
    profit_loss_percentage: float
    diversification_score: float
    sector_allocations: List[SectorAllocation]
    stock_count: int
    best_performer: Optional[StockHolding]
    worst_performer: Optional[StockHolding]
    insights: List[str]
    
    class Config:
        from_attributes = True

class PortfolioAnalysisResponse(BaseModel):
    """Response schema for portfolio analysis"""
    user_id: int
    portfolio_metrics: PortfolioMetrics
    holdings: List[StockHolding]
    insights: List[str]
    analysis_timestamp: datetime
    
    class Config:
        from_attributes = True

class APIResponse(BaseModel):
    """Generic API response schema"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class PortfolioInsightResponse(BaseModel):
    """Response schema for portfolio insights"""
    id: int
    user_id: int
    insight: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PortfolioInsightListResponse(BaseModel):
    """Response schema for portfolio insights list"""
    insights: List[PortfolioInsightResponse]
    total: int
    
    class Config:
        from_attributes = True
