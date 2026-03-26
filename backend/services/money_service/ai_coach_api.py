"""
AI Coach API
Endpoints for AI Financial Assistant chat functionality
"""

from flask import Blueprint, request, jsonify
from ai.ai_chat_service import ai_chat_service
import sqlite3
from datetime import datetime

ai_coach_bp = Blueprint('ai_coach', __name__)

def create_ai_coach_api(app):
    """Register AI Coach API endpoints"""
    
    @ai_coach_bp.route('/api/ai-coach/chat', methods=['POST'])
    def chat():
        """Handle chat messages with AI"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            message = data.get('message')
            
            if not user_id or not message:
                return jsonify({
                    'success': False,
                    'error': 'Missing user_id or message'
                }), 400
            
            # Use existing AI chat service
            result = ai_chat_service.handle_user_chat(user_id, message)
            
            if result.get('success'):
                # Store message in history
                store_message(user_id, message, 'user')
                store_message(user_id, result['ai_response'], 'ai', result.get('message_type', 'general_query'))
                
                return jsonify({
                    'success': True,
                    'ai_response': result['ai_response'],
                    'message_type': result.get('message_type', 'general_query'),
                    'timestamp': datetime.utcnow().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Chat error: {str(e)}'
            }), 500
    
    @ai_coach_bp.route('/api/ai-coach/greeting', methods=['GET'])
    def greeting():
        """Get personalized greeting message"""
        try:
            user_id = request.args.get('user_id')
            
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'Missing user_id parameter'
                }), 400
            
            # Generate personalized greeting
            greeting = generate_greeting(user_id)
            
            return jsonify({
                'success': True,
                'greeting': greeting,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Greeting error: {str(e)}'
            }), 500
    
    @ai_coach_bp.route('/api/ai-coach/history', methods=['GET'])
    def history():
        """Get chat history for user"""
        try:
            user_id = request.args.get('user_id')
            limit = request.args.get('limit', 20)
            
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'Missing user_id parameter'
                }), 400
            
            history_messages = get_chat_history(user_id, limit)
            
            return jsonify({
                'success': True,
                'history': history_messages
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'History error: {str(e)}'
            }), 500
    
    # Register blueprint
    app.register_blueprint(ai_coach_bp)

def generate_greeting(user_id):
    """Generate personalized greeting message"""
    greetings = [
        "Hello! I'm your AI Financial Assistant. How can I help you with your financial goals today?",
        "Hi there! I'm here to help with stocks, investments, and financial planning. What would you like to know?",
        "Welcome! I can assist you with portfolio analysis, market news, and financial education. What's on your mind?",
        "Good day! I'm your financial coach powered by Gemini AI. Let's work on your financial goals together!"
    ]
    
    # For now, return a random greeting. Could be enhanced with user-specific data
    import random
    return random.choice(greetings)

def store_message(user_id, text, sender, message_type=None):
    """Store chat message in database"""
    try:
        conn = sqlite3.connect('expertease.db')
        cursor = conn.cursor()
        
        # Create chat_history table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                sender TEXT NOT NULL,
                text TEXT NOT NULL,
                message_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO ai_chat_history (user_id, sender, text, message_type)
            VALUES (?, ?, ?, ?)
        """, (user_id, sender, text, message_type))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error storing message: {e}")

def get_chat_history(user_id, limit=20):
    """Get chat history for user"""
    try:
        conn = sqlite3.connect('expertease.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, sender, text, message_type, timestamp
            FROM ai_chat_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        history = []
        for row in results:
            history.append({
                'id': row[0],
                'sender': row[1],
                'text': row[2],
                'type': row[3] or 'general_query',
                'timestamp': row[4]
            })
        
        return history
        
    except Exception as e:
        print(f"Error getting history: {e}")
        return []
