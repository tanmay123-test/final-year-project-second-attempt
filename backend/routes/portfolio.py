"""
Portfolio Routes
REST API endpoints for portfolio management and analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database.ai_groups_connection import get_db
from ..models.portfolio import Portfolio, PortfolioInsight
from ..schemas.portfolio_schema import (
    AddPortfolioRequest, 
    UpdatePortfolioRequest, 
    PortfolioResponse,
    PortfolioListResponse,
    PortfolioAnalysisRequest,
    PortfolioAnalysisResponse,
    APIResponse,
    PortfolioInsightResponse,
    PortfolioInsightListResponse
)
from ..services.portfolio_service import PortfolioService
from ..ai.portfolio_ai_service import PortfolioAIService

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

@router.post("/add", response_model=APIResponse)
async def add_to_portfolio(
    request: AddPortfolioRequest,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Add a stock to user's portfolio
    """
    try:
        service = PortfolioService(db)
        
        portfolio_item = service.add_to_portfolio(
            user_id=user_id,
            stock_symbol=request.stock_symbol,
            quantity=request.quantity,
            purchase_price=request.purchase_price
        )
        
        return APIResponse(
            success=True,
            message="Stock added to portfolio successfully",
            data={"portfolio_id": portfolio_item.id}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=PortfolioListResponse)
async def get_user_portfolio(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user's complete portfolio
    """
    try:
        service = PortfolioService(db)
        
        portfolios = service.get_user_portfolio(user_id)
        
        portfolio_responses = [PortfolioResponse(**item.to_dict()) for item in portfolios]
        
        return PortfolioListResponse(
            portfolios=portfolio_responses,
            total=len(portfolios)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{portfolio_id}", response_model=APIResponse)
async def remove_from_portfolio(
    portfolio_id: int,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Remove a stock from user's portfolio
    """
    try:
        service = PortfolioService(db)
        
        success = service.remove_from_portfolio(portfolio_id, user_id)
        
        if success:
            return APIResponse(
                success=True,
                message="Stock removed from portfolio successfully"
            )
        else:
            raise HTTPException(
                status_code=404, 
                detail="Portfolio item not found or access denied"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{portfolio_id}", response_model=APIResponse)
async def update_portfolio_item(
    portfolio_id: int,
    request: UpdatePortfolioRequest,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Update a portfolio item (quantity or price)
    """
    try:
        service = PortfolioService(db)
        
        portfolio_item = service.update_portfolio(
            portfolio_id=portfolio_id,
            user_id=user_id,
            quantity=request.quantity,
            purchase_price=request.purchase_price
        )
        
        if portfolio_item:
            return APIResponse(
                success=True,
                message="Portfolio item updated successfully",
                data={"portfolio_id": portfolio_item.id}
            )
        else:
            raise HTTPException(
                status_code=404, 
                detail="Portfolio item not found or access denied"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/{user_id}", response_model=PortfolioAnalysisResponse)
async def analyze_portfolio(
    user_id: int,
    request: PortfolioAnalysisRequest = None,
    db: Session = Depends(get_db)
):
    """
    Analyze user's portfolio with AI insights
    """
    try:
        # Use provided request or create default
        if request is None:
            request = PortfolioAnalysisRequest(user_id=user_id)
        
        service = PortfolioService(db)
        ai_service = PortfolioAIService()
        
        # Get portfolio data
        portfolio_data = service.get_portfolio_with_current_prices(user_id)
        
        if not portfolio_data:
            return PortfolioAnalysisResponse(
                user_id=user_id,
                portfolio_metrics=PortfolioMetrics(
                    total_investment=0,
                    current_value=0,
                    total_profit_loss=0,
                    profit_loss_percentage=0,
                    diversification_score=0,
                    sector_allocations=[],
                    stock_count=0,
                    best_performer=None,
                    worst_performer=None,
                    insights=[]
                ),
                holdings=[],
                insights=["You currently do not have any investments saved. Add stocks to your portfolio to receive analysis."],
                analysis_timestamp=datetime.utcnow()
            )
        
        # Generate AI analysis
        analysis_result = await ai_service.analyze_user_portfolio(user_id, portfolio_data)
        
        if analysis_result.get("success"):
            return PortfolioAnalysisResponse(
                user_id=user_id,
                portfolio_metrics=analysis_result["portfolio_metrics"],
                holdings=analysis_result["holdings"],
                insights=analysis_result["insights"],
                analysis_timestamp=datetime.utcnow()
            )
        else:
            return PortfolioAnalysisResponse(
                user_id=user_id,
                portfolio_metrics=PortfolioMetrics(
                    total_investment=0,
                    current_value=0,
                    total_profit_loss=0,
                    profit_loss_percentage=0,
                    diversification_score=0,
                    sector_allocations=[],
                    stock_count=0,
                    best_performer=None,
                    worst_performer=None,
                    insights=[analysis_result.get("error", "Unable to analyze portfolio")]
                ),
                holdings=[],
                insights=[analysis_result.get("error", "Unable to analyze portfolio")],
                analysis_timestamp=datetime.utcnow()
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/insights", response_model=PortfolioInsightListResponse)
async def get_portfolio_insights(
    user_id: int,
    limit: int = Query(10, ge=1, le=100, description="Number of insights to return"),
    offset: int = Query(0, ge=0, description="Number of insights to skip"),
    db: Session = Depends(get_db)
):
    """
    Get user's portfolio insights
    """
    try:
        from ..models.portfolio import PortfolioInsight
        
        # Get insights from database
        insights = db.query(PortfolioInsight).filter(
            PortfolioInsight.user_id == user_id
        ).order_by(PortfolioInsight.created_at.desc()).offset(offset).limit(limit).all()
        
        insight_responses = [PortfolioInsightResponse(**insight.to_dict()) for insight in insights]
        
        # Get total count
        total = db.query(PortfolioInsight).filter(PortfolioInsight.user_id == user_id).count()
        
        return PortfolioInsightListResponse(
            insights=insight_responses,
            total=total
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/metrics", response_model=PortfolioMetrics)
async def get_portfolio_metrics(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get portfolio metrics without AI analysis
    """
    try:
        service = PortfolioService(db)
        
        portfolio_data = service.get_portfolio_with_current_prices(user_id)
        
        if not portfolio_data:
            return PortfolioMetrics(
                total_investment=0,
                current_value=0,
                total_profit_loss=0,
                profit_loss_percentage=0,
                diversification_score=0,
                sector_allocations=[],
                stock_count=0,
                best_performer=None,
                worst_performer=None,
                insights=[]
            )
        
        # Calculate metrics without AI
        from ..schemas.portfolio_schema import PortfolioMetrics, StockHolding, SectorAllocation
        
        holdings = []
        total_investment = 0
        current_value = 0
        sector_allocations = {}
        
        for item in portfolio_data["holdings"]:
            total_investment += item["total_investment"]
            current_value += item.get("current_value", 0)
            
            holdings.append(StockHolding(
                stock_symbol=item["stock_symbol"],
                quantity=item["quantity"],
                purchase_price=item["purchase_price"],
                current_price=item.get("current_price"),
                current_value=item.get("current_value", 0),
                profit_loss=item.get("profit_loss", 0),
                profit_loss_percentage=item.get("profit_loss_percentage", 0),
                days_held=item.get("days_held", 0)
            ))
        
        # Calculate total profit/loss
        total_profit_loss = current_value - total_investment
        profit_loss_percentage = (total_profit_loss / total_investment * 100) if total_investment > 0 else 0
        
        # Calculate sector allocations
        for item in portfolio_data["holdings"]:
            sector = item.get("sector", "Unknown")
            value = item.get("current_value", 0)
            sector_allocations[sector] = sector_allocations.get(sector, 0) + value
        
        # Calculate sector percentages
        for sector in sector_allocations:
            sector_allocations[sector] = (sector_allocations[sector] / current_value * 100) if current_value > 0 else 0
        
        # Simple diversification score (inverse of concentration)
        max_allocation = max(sector_allocations.values()) if sector_allocations else 0
        diversification_score = 100 - max_allocation if max_allocation <= 100 else 0
        
        # Find best and worst performers
        best_performer = None
        worst_performer = None
        if holdings:
            best_performer = max(holdings, key=lambda x: x.get("profit_loss_percentage", 0))
            worst_performer = min(holdings, key=lambda x: x.get("profit_loss_percentage", 0))
        
        return PortfolioMetrics(
            total_investment=total_investment,
            current_value=current_value,
            total_profit_loss=total_profit_loss,
            profit_loss_percentage=profit_loss_percentage,
            diversification_score=diversification_score,
            sector_allocations=[
                SectorAllocation(sector=k, allocation_percentage=v)
                for k, v in sector_allocations.items()
            ],
            stock_count=len(holdings),
            best_performer=best_performer,
            worst_performer=worst_performer,
            insights=[]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supported-stocks", response_model=dict)
async def get_supported_stocks():
    """
    Get list of commonly supported stocks for testing
    """
    try:
        from ..ai.portfolio_ai_service import portfolio_ai_service
        
        companies = portfolio_ai_service.get_supported_companies()
        sample_queries = portfolio_ai_service.get_sample_queries()
        
        return {
            "success": True,
            "data": {
                "companies": companies,
                "sample_queries": sample_queries
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test", response_model=dict)
async def test_portfolio_service():
    """
    Test portfolio service connection
    """
    try:
        from ..services.portfolio_service import PortfolioService
        from ..ai.portfolio_ai_service import PortfolioAIService
        
        # Test portfolio service
        service = PortfolioService()
        test_portfolio = service.get_user_portfolio(1)  # Test with user_id=1
        
        # Test portfolio AI service
        ai_connected = await portfolio_ai_service.test_portfolio_analysis()
        
        return {
            "success": True,
            "data": {
                "portfolio_service_connected": True,
                "portfolio_ai_service_connected": ai_connected,
                "test_portfolio_count": len(test_portfolio),
                "overall_status": "Connected"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
