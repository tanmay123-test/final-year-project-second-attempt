import os
from flask import Flask
from .models import db
from dotenv import load_dotenv

load_dotenv()

def init_ask_expert_db(app: Flask):
    """Initialize the Ask Expert database using PostgreSQL"""
    load_dotenv()
    
    # Configure SQLAlchemy to use PostgreSQL (Supabase)
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        # SQLAlchemy requires postgresql:// instead of postgres://
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the app with the database
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Create sample expert profiles if none exist
        from .models import ExpertProfile
        
        try:
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
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding sample experts: {e}")

def get_db():
    """Get database instance"""
    return db
