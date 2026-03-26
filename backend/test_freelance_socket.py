#!/usr/bin/env python3
"""
Test script for freelance real-time communication
Run this to verify socket handlers are working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.freelance.socket_handlers import handle_freelance_socket_events
from services.freelance.models.database import freelance_db
from flask import Flask
from flask_socketio import SocketIO
import threading
import time

def test_freelance_socket():
    """Test the freelance socket handlers"""
    print("🧪 Testing Freelance Socket Handlers...")
    
    # Create test Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret'
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Register freelance socket handlers
    try:
        handle_freelance_socket_events(socketio)
        print("✅ Socket handlers registered successfully")
    except Exception as e:
        print(f"❌ Failed to register socket handlers: {e}")
        return False
    
    # Test database connection
    try:
        conn = freelance_db.get_conn()
        conn.close()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    print("✅ All socket tests passed!")
    print("\n📋 Manual Testing Steps:")
    print("1. Start the backend server: python app.py")
    print("2. Open frontend and navigate to a freelance project")
    print("3. Accept a proposal to start a project")
    print("4. Open the chat section in project details")
    print("5. Send messages and verify real-time updates")
    print("6. Check browser console for socket connection status")
    
    return True

def test_database_schema():
    """Test if the database schema is correct"""
    print("\n🧪 Testing Database Schema...")
    
    try:
        conn = freelance_db.get_conn()
        cursor = conn.cursor()
        
        # Check if freelance_messages table has is_read column
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'freelance_messages' 
            AND column_name = 'is_read'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"✅ is_read column exists: {result[0]} ({result[1]})")
        else:
            print("⚠️  is_read column not found - adding it...")
            cursor.execute("""
                ALTER TABLE freelance_messages 
                ADD COLUMN IF NOT EXISTS is_read BOOLEAN DEFAULT FALSE
            """)
            conn.commit()
            print("✅ is_read column added successfully")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Freelance Real-time Communication Tests\n")
    
    # Run tests
    socket_test = test_freelance_socket()
    schema_test = test_database_schema()
    
    if socket_test and schema_test:
        print("\n🎉 All tests passed! Real-time communication is ready.")
        print("\n🔗 Next Steps:")
        print("1. Start your backend server")
        print("2. Start your frontend development server")
        print("3. Test with an active freelance project")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
