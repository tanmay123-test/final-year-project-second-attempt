import os
from flask import Flask
from .models import db

def init_ask_expert_db(app: Flask):
    """Initialize the Ask Expert database"""
    db_path = os.path.join(os.path.dirname(__file__), 'ask_expert.db')
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the app with the database
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Create sample expert profiles if none exist
        from .models import ExpertProfile
        
        if ExpertProfile.query.count() == 0:
            sample_experts = [
                ExpertProfile(
                    name='John Smith',
                    category='ENGINE_EXPERT',
                    is_approved=True,
                    online_status='ONLINE',
                    is_busy=False
                ),
                ExpertProfile(
                    name='Mike Johnson',
                    category='BRAKE_SUSPENSION_EXPERT',
                    is_approved=True,
                    online_status='ONLINE',
                    is_busy=False
                ),
                ExpertProfile(
                    name='Sarah Davis',
                    category='ELECTRICAL_EXPERT',
                    is_approved=True,
                    online_status='ONLINE',
                    is_busy=False
                ),
                ExpertProfile(
                    name='Tom Wilson',
                    category='BODY_INTERIOR_EXPERT',
                    is_approved=True,
                    online_status='ONLINE',
                    is_busy=False
                ),
                ExpertProfile(
                    name='Lisa Brown',
                    category='GENERAL_EXPERT',
                    is_approved=True,
                    online_status='ONLINE',
                    is_busy=False
                )
            ]
            
            for expert in sample_experts:
                db.session.add(expert)
            
            db.session.commit()

def get_db():
    """Get database instance"""
    return db
