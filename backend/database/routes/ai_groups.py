"""
AI Groups FastAPI Routes
REST API endpoints for AI Groups functionality
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..ai_groups_connection import get_db
from ..models.ai_group import AIGroup
from ..models.group_member import GroupMember
from ..models.group_message import GroupMessage
from ..schemas.ai_group_schema import (
    CreateGroupRequest, 
    GroupResponse, 
    GroupListResponse, 
    GroupDetailResponse,
    APIResponse
)
from ..schemas.group_member_schema import GroupMemberResponse
from ..schemas.group_message_schema import (
    SendMessageRequest,
    MessageResponse,
    MessageListResponse,
    MessageFilterRequest
)
from ..services.ai_groups_service import AIGroupsService

router = APIRouter(prefix="/ai-groups", tags=["AI Groups"])

@router.post("/create", response_model=APIResponse)
async def create_group(
    group_request: CreateGroupRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new AI group
    """
    try:
        service = AIGroupsService(db)
        group = service.create_group(group_request)
        
        return APIResponse(
            success=True,
            message="Group created successfully",
            data={"group_id": group.id}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list", response_model=GroupListResponse)
async def list_groups(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=1000, description="Number of groups to return"),
    offset: int = Query(0, ge=0, description="Number of groups to skip"),
    db: Session = Depends(get_db)
):
    """
    Get list of all available groups
    """
    try:
        service = AIGroupsService(db)
        groups, total = service.list_groups(category, limit, offset)
        
        group_responses = [GroupResponse(**group.to_dict()) for group in groups]
        
        return GroupListResponse(
            groups=group_responses,
            total=total
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/join", response_model=APIResponse)
async def join_group(
    join_request: dict,
    db: Session = Depends(get_db)
):
    """
    User joins a group
    """
    try:
        service = AIGroupsService(db)
        member = service.join_group(join_request)
        
        return APIResponse(
            success=True,
            message="Joined group successfully",
            data={"member_id": member.id}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{group_id}", response_model=GroupDetailResponse)
async def get_group_details(
    group_id: int,
    db: Session = Depends(get_db)
):
    """
    Get group details including members and messages
    """
    try:
        service = AIGroupsService(db)
        group_details = service.get_group_details(group_id)
        
        if not group_details:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Convert group to response
        group_response = GroupResponse(**group_details['group'].to_dict())
        
        # Convert members to response
        members_response = [
            GroupMemberResponse(**member.to_dict()) 
            for member in group_details['members']
        ]
        
        # Convert messages to response
        messages_response = [
            MessageResponse(**message.to_dict()) 
            for message in group_details['messages']
        ]
        
        return GroupDetailResponse(
            group=group_response,
            members=members_response,
            messages=messages_response
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/message", response_model=APIResponse)
async def send_message(
    message_request: SendMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Send a message to a group with AI assistant response
    """
    try:
        # Import AI service
        from ai.ai_group_service import ai_group_service
        
        service = AIGroupsService(db)
        
        # Store user message
        message = service.send_message(message_request)
        
        # Check if AI should respond and generate response
        ai_response = await ai_group_service.handle_ai_group_message(
            group_id=message_request.group_id,
            message=message_request.message
        )
        
        # Prepare response data
        response_data = {
            "user_message_id": message.id
        }
        
        if ai_response:
            response_data["ai_message_id"] = ai_response["id"]
            response_data["ai_response"] = ai_response["message"]
        
        return APIResponse(
            success=True,
            message="Message sent successfully",
            data=response_data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{group_id}/messages", response_model=MessageListResponse)
async def get_group_messages(
    group_id: int,
    message_type: Optional[str] = Query(None, description="Filter by message type"),
    limit: int = Query(50, ge=1, le=1000, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    db: Session = Depends(get_db)
):
    """
    Get messages for a specific group
    """
    try:
        service = AIGroupsService(db)
        
        # Create filter request
        filter_request = MessageFilterRequest(
            group_id=group_id,
            message_type=message_type,
            limit=limit,
            offset=offset
        )
        
        messages, total = service.get_group_messages(filter_request)
        
        messages_response = [
            MessageResponse(**message.to_dict()) 
            for message in messages
        ]
        
        return MessageListResponse(
            messages=messages_response,
            total=total,
            page=(offset // limit) + 1,
            per_page=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{group_id}/members", response_model=List[GroupMemberResponse])
async def get_group_members(
    group_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all members of a group
    """
    try:
        service = AIGroupsService(db)
        members = service.get_group_members(group_id)
        
        return [
            GroupMemberResponse(**member.to_dict()) 
            for member in members
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{group_id}/leave", response_model=APIResponse)
async def leave_group(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    User leaves a group
    """
    try:
        service = AIGroupsService(db)
        success = service.leave_group(group_id, user_id)
        
        if success:
            return APIResponse(
                success=True,
                message="Left group successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Group membership not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI Assistant Endpoints

@router.post("/{group_id}/ai/add", response_model=APIResponse)
async def add_ai_to_group(
    group_id: int,
    db: Session = Depends(get_db)
):
    """
    Add AI assistant to a group
    """
    try:
        from ai.ai_group_service import ai_group_service
        
        success = await ai_group_service.add_ai_to_group(group_id)
        
        if success:
            return APIResponse(
                success=True,
                message="AI assistant added to group successfully"
            )
        else:
            return APIResponse(
                success=False,
                message="Failed to add AI assistant to group"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{group_id}/ai/remove", response_model=APIResponse)
async def remove_ai_from_group(
    group_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove AI assistant from a group
    """
    try:
        from ai.ai_group_service import ai_group_service
        
        success = await ai_group_service.remove_ai_from_group(group_id)
        
        if success:
            return APIResponse(
                success=True,
                message="AI assistant removed from group successfully"
            )
        else:
            return APIResponse(
                success=False,
                message="Failed to remove AI assistant from group"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{group_id}/ai/statistics", response_model=dict)
async def get_ai_statistics(
    group_id: int,
    db: Session = Depends(get_db)
):
    """
    Get AI assistant statistics for a group
    """
    try:
        from ai.ai_group_service import ai_group_service
        
        stats = await ai_group_service.get_ai_statistics(group_id)
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{group_id}/ai/quality", response_model=dict)
async def get_ai_response_quality(
    group_id: int,
    db: Session = Depends(get_db)
):
    """
    Get AI response quality metrics
    """
    try:
        from ai.ai_group_service import ai_group_service
        
        quality = await ai_group_service.get_ai_response_quality(group_id)
        
        return {
            "success": True,
            "data": quality
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai/keywords", response_model=dict)
async def get_ai_trigger_keywords():
    """
    Get AI trigger keywords and categories
    """
    try:
        from ai.ai_group_service import ai_group_service
        
        keywords_info = ai_group_service.get_trigger_keywords()
        
        return {
            "success": True,
            "data": keywords_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/test", response_model=dict)
async def test_ai_connection():
    """
    Test connection to AI service
    """
    try:
        from ai.gemini_client import gemini_client
        
        is_connected = await gemini_client.test_connection()
        
        return {
            "success": True,
            "data": {
                "connected": is_connected,
                "status": "Connected" if is_connected else "Disconnected"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Stock Analysis Endpoints

@router.post("/stock/analyze", response_model=dict)
async def analyze_stock(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Analyze a stock using AI
    """
    try:
        from ai.stock_ai_service import stock_ai_service
        
        user_message = request.get("message", "")
        if not user_message:
            return {
                "success": False,
                "error": "Message is required"
            }
        
        result = await stock_ai_service.generate_stock_analysis(user_message)
        
        return {
            "success": result.get("success", False),
            "data": result,
            "error": result.get("error") if not result.get("success") else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stock/search", response_model=dict)
async def search_stocks(
    request: dict,
    db: Session = Depends(get_db)
):
    """
    Search for stocks
    """
    try:
        from ai.stock_ai_service import stock_ai_service
        
        user_message = request.get("message", "")
        if not user_message:
            return {
                "success": False,
                "error": "Search query is required"
            }
        
        result = await stock_ai_service.search_and_analyze(user_message)
        
        return {
            "success": result.get("success", False),
            "data": result,
            "error": result.get("error") if not result.get("success") else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/data/{symbol}", response_model=dict)
async def get_stock_data(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Get stock data for a symbol
    """
    try:
        from services.stock_service import stock_service
        
        stock_data = await stock_service.get_stock_data(symbol)
        
        return {
            "success": "error" not in stock_data,
            "data": stock_data,
            "error": stock_data.get("error") if "error" in stock_data else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/supported", response_model=dict)
async def get_supported_companies():
    """
    Get list of supported companies for testing
    """
    try:
        from ai.stock_ai_service import stock_ai_service
        
        companies = stock_ai_service.get_supported_companies()
        sample_queries = stock_ai_service.get_sample_queries()
        
        return {
            "success": True,
            "data": {
                "companies": companies,
                "sample_queries": sample_queries
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stock/test", response_model=dict)
async def test_stock_service():
    """
    Test stock service connection
    """
    try:
        from services.stock_service import stock_service
        from ai.stock_ai_service import stock_ai_service
        
        # Test stock service
        stock_connected = await stock_service.test_connection()
        
        # Test stock AI service
        ai_connected = await stock_ai_service.test_stock_analysis()
        
        return {
            "success": True,
            "data": {
                "stock_service_connected": stock_connected,
                "stock_ai_service_connected": ai_connected,
                "overall_status": "Connected" if stock_connected and ai_connected else "Disconnected"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
