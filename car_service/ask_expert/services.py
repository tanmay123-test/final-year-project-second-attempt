from datetime import datetime
from typing import List, Optional, Dict, Any
from .models import db, ExpertProfile, ExpertRequest, ExpertImage, ExpertMessage, ExpertTypingStatus

EXPERT_CATEGORIES = {
    'ENGINE_EXPERT': 'Engine Expert',
    'BRAKE_SUSPENSION_EXPERT': 'Brake & Suspension Expert',
    'ELECTRICAL_EXPERT': 'Electrical Expert',
    'BODY_INTERIOR_EXPERT': 'Body & Interior Expert',
    'GENERAL_EXPERT': 'General Expert'
}

class AskExpertService:
    
    @staticmethod
    def get_expert_categories() -> Dict[str, str]:
        """Get all expert categories"""
        return EXPERT_CATEGORIES
    
    @staticmethod
    def find_available_expert(category: str) -> Optional[ExpertProfile]:
        """Find an available expert for the given category"""
        return ExpertProfile.query.filter_by(
            category=category,
            is_approved=True,
            online_status='ONLINE',
            is_busy=False
        ).first()
    
    @staticmethod
    def create_expert_request(user_id: int, expert_category: str, description: str, image_paths: List[str] = None) -> Dict[str, Any]:
        """Create a new expert request"""
        
        # Find available expert
        expert = AskExpertService.find_available_expert(expert_category)
        
        # Create request
        request = ExpertRequest(
            user_id=user_id,
            expert_category=expert_category,
            assigned_expert_id=expert.id if expert else None,
            problem_description=description,
            status='ASSIGNED' if expert else 'WAITING_QUEUE'
        )
        
        db.session.add(request)
        db.session.flush()  # Get the request ID
        
        # Add images if provided
        if image_paths:
            for image_path in image_paths:
                image = ExpertImage(request_id=request.id, image_path=image_path)
                db.session.add(image)
        
        # Initialize typing status
        typing_status = ExpertTypingStatus(request_id=request.id)
        db.session.add(typing_status)
        
        # Mark expert as busy if assigned
        if expert:
            expert.is_busy = True
            expert.last_active = datetime.utcnow()
        
        db.session.commit()
        
        # Calculate queue position if waiting
        queue_position = None
        if request.status == 'WAITING_QUEUE':
            queue_position = ExpertRequest.query.filter_by(status='WAITING_QUEUE').count()
        
        return {
            'request_id': request.id,
            'status': request.status,
            'queue_position': queue_position,
            'expert_name': expert.name if expert else None
        }
    
    @staticmethod
    def get_user_conversations(user_id: int) -> List[Dict[str, Any]]:
        """Get all conversations for a user"""
        requests = ExpertRequest.query.filter_by(user_id=user_id).order_by(ExpertRequest.created_at.desc()).all()
        
        result = []
        for request in requests:
            expert_name = None
            if request.assigned_expert_id:
                expert = ExpertProfile.query.get(request.assigned_expert_id)
                expert_name = expert.name if expert else None
            
            result.append({
                'id': request.id,
                'expert_category': request.expert_category,
                'category_name': EXPERT_CATEGORIES.get(request.expert_category, request.expert_category),
                'status': request.status,
                'created_at': request.created_at.isoformat() if request.created_at else None,
                'expert_name': expert_name,
                'problem_description': request.problem_description
            })
        
        return result
    
    @staticmethod
    def get_request_details(request_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific request"""
        request = ExpertRequest.query.filter_by(id=request_id, user_id=user_id).first()
        
        if not request:
            return None
        
        # Get images
        images = [{'id': img.id, 'image_path': img.image_path} for img in request.images]
        
        # Get messages
        messages = []
        for msg in request.messages:
            messages.append({
                'id': msg.id,
                'sender_type': msg.sender_type,
                'sender_id': msg.sender_id,
                'message': msg.message,
                'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
            })
        
        # Get typing status
        typing_status = None
        if request.typing_status:
            typing_status = {
                'user_typing': request.typing_status[0].user_typing,
                'expert_typing': request.typing_status[0].expert_typing
            }
        
        # Get expert info if assigned
        expert_info = None
        if request.assigned_expert_id:
            expert = ExpertProfile.query.get(request.assigned_expert_id)
            if expert:
                expert_info = {
                    'id': expert.id,
                    'name': expert.name,
                    'category': expert.category,
                    'online_status': expert.online_status
                }
        
        return {
            'id': request.id,
            'expert_category': request.expert_category,
            'category_name': EXPERT_CATEGORIES.get(request.expert_category, request.expert_category),
            'status': request.status,
            'problem_description': request.problem_description,
            'created_at': request.created_at.isoformat() if request.created_at else None,
            'resolved_at': request.resolved_at.isoformat() if request.resolved_at else None,
            'call_started': request.call_started,
            'images': images,
            'messages': messages,
            'typing_status': typing_status,
            'expert': expert_info
        }
    
    @staticmethod
    def add_message(request_id: int, sender_type: str, sender_id: int, message: str) -> bool:
        """Add a message to the conversation"""
        request = ExpertRequest.query.get(request_id)
        
        if not request:
            return False
        
        msg = ExpertMessage(
            request_id=request_id,
            sender_type=sender_type,
            sender_id=sender_id,
            message=message
        )
        
        db.session.add(msg)
        db.session.commit()
        
        return True
    
    @staticmethod
    def update_typing_status(request_id: int, user_typing: bool = None, expert_typing: bool = None) -> bool:
        """Update typing status for a request"""
        request = ExpertRequest.query.get(request_id)
        
        if not request:
            return False
        
        typing_status = ExpertTypingStatus.query.filter_by(request_id=request_id).first()
        
        if not typing_status:
            typing_status = ExpertTypingStatus(request_id=request_id)
            db.session.add(typing_status)
        
        if user_typing is not None:
            typing_status.user_typing = user_typing
        
        if expert_typing is not None:
            typing_status.expert_typing = expert_typing
        
        db.session.commit()
        
        return True
    
    @staticmethod
    def start_call(request_id: int, user_id: int) -> bool:
        """Start a call session"""
        request = ExpertRequest.query.filter_by(id=request_id, user_id=user_id).first()
        
        if not request or request.status != 'ASSIGNED':
            return False
        
        request.call_started = True
        db.session.commit()
        
        return True
    
    @staticmethod
    def resolve_request(request_id: int, user_id: int) -> bool:
        """Mark a request as resolved"""
        request = ExpertRequest.query.filter_by(id=request_id, user_id=user_id).first()
        
        if not request:
            return False
        
        request.status = 'RESOLVED'
        request.resolved_at = datetime.utcnow()
        
        # Free up the expert
        if request.assigned_expert_id:
            expert = ExpertProfile.query.get(request.assigned_expert_id)
            if expert:
                expert.is_busy = False
                expert.last_active = datetime.utcnow()
        
        # Auto-assign next waiting request if any
        AskExpertService.auto_assign_waiting_requests()
        
        db.session.commit()
        
        return True
    
    @staticmethod
    def auto_assign_waiting_requests():
        """Auto-assign waiting requests to available experts"""
        waiting_requests = ExpertRequest.query.filter_by(status='WAITING_QUEUE').order_by(ExpertRequest.created_at.asc()).all()
        
        for request in waiting_requests:
            expert = AskExpertService.find_available_expert(request.expert_category)
            
            if expert:
                request.assigned_expert_id = expert.id
                request.status = 'ASSIGNED'
                expert.is_busy = True
                expert.last_active = datetime.utcnow()
                
                # Initialize typing status if not exists
                if not request.typing_status:
                    typing_status = ExpertTypingStatus(request_id=request.id)
                    db.session.add(typing_status)
                
                db.session.commit()
                break  # Assign one at a time
    
    @staticmethod
    def get_request_messages(request_id: int, user_id: int) -> List[Dict]:
        """Get all messages for a request"""
        request = ExpertRequest.query.filter_by(id=request_id, user_id=user_id).first()
        
        if not request:
            return []
        
        messages = ExpertMessage.query.filter_by(request_id=request_id).order_by(ExpertMessage.created_at.asc()).all()
        
        return [
            {
                'id': msg.id,
                'sender_type': msg.sender_type,
                'sender_id': msg.sender_id,
                'message': msg.message,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S') if msg.created_at else None
            }
            for msg in messages
        ]
