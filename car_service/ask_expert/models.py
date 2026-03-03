from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ExpertProfile(db.Model):
    __tablename__ = 'expert_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    online_status = db.Column(db.Text, default='OFFLINE')
    is_busy = db.Column(db.Boolean, default=False)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'is_approved': self.is_approved,
            'online_status': self.online_status,
            'is_busy': self.is_busy,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }

class ExpertRequest(db.Model):
    __tablename__ = 'expert_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    expert_category = db.Column(db.Text, nullable=False)
    assigned_expert_id = db.Column(db.Integer, db.ForeignKey('expert_profiles.id'), nullable=True)
    problem_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, default='WAITING_QUEUE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    call_started = db.Column(db.Boolean, default=False)
    
    expert = db.relationship('ExpertProfile', backref='requests')
    images = db.relationship('ExpertImage', backref='request', cascade='all, delete-orphan')
    messages = db.relationship('ExpertMessage', backref='request', cascade='all, delete-orphan')
    typing_status = db.relationship('ExpertTypingStatus', backref='request', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'expert_category': self.expert_category,
            'assigned_expert_id': self.assigned_expert_id,
            'problem_description': self.problem_description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'call_started': self.call_started
        }

class ExpertImage(db.Model):
    __tablename__ = 'expert_images'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('expert_requests.id'), nullable=False)
    image_path = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'image_path': self.image_path
        }

class ExpertMessage(db.Model):
    __tablename__ = 'expert_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('expert_requests.id'), nullable=False)
    sender_type = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'sender_type': self.sender_type,
            'sender_id': self.sender_id,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class ExpertTypingStatus(db.Model):
    __tablename__ = 'expert_typing_status'
    
    request_id = db.Column(db.Integer, db.ForeignKey('expert_requests.id'), primary_key=True)
    user_typing = db.Column(db.Boolean, default=False)
    expert_typing = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'request_id': self.request_id,
            'user_typing': self.user_typing,
            'expert_typing': self.expert_typing
        }
