"""
Gemini AI Client
Handles communication with Google Gemini API for financial education assistant
"""

import os
import json
import httpx
from typing import Optional, Dict, Any
from datetime import datetime

class GeminiClient:
    """
    Client for interacting with Google Gemini API
    Acts as a financial education assistant
    """
    
    def __init__(self):
        # Try to load API key from separate config file if available
        try:
            from services.freelance.gemini_config import GEMINI_API_KEY
            self.api_key = GEMINI_API_KEY
        except ImportError:
            self.api_key = os.getenv("GEMINI_API_KEY", "your_gemini_api_key_here")
            
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-1.5-flash"  # Fast and efficient model
        
        # Financial education prompt template
        self.system_prompt = """You are a financial education assistant inside a community group.

Your role is to:
* explain financial concepts clearly
* help beginners understand investing basics
* answer finance related questions in simple terms
* provide educational information about markets and investing

Rules:
* NEVER give direct financial advice
* NEVER say "buy", "sell", "invest", or "recommend"
* NEVER suggest specific stocks, funds, or investments
* ALWAYS focus on education and analysis only
* If you're unsure about something, say "I don't have enough information"
* Keep responses educational and informative
* Use simple language that beginners can understand

User Question:
{user_message}

Provide a helpful educational response:"""
    
    async def generate_ai_response(self, message: str) -> str:
        """
        Generate AI response for financial education
        
        Args:
            message: User message/question
            
        Returns:
            AI response text
        """
        try:
            # Prepare the prompt
            full_prompt = self.system_prompt.format(user_message=message)
            
            # Prepare API request
            url = f"{self.base_url}/models/{self.model}:generateContent"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": full_prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH", 
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            # Make API call
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract the generated text
                    if "candidates" in result and len(result["candidates"]) > 0:
                        candidate = result["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            text = candidate["content"]["parts"][0]["text"]
                            return self._clean_response(text)
                    
                    return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
                
                elif response.status_code == 400:
                    return "I apologize, but I couldn't process that request. Please try asking in a different way."
                
                elif response.status_code == 429:
                    return "I'm receiving too many requests right now. Please wait a moment and try again."
                
                else:
                    return "I'm experiencing technical difficulties. Please try again later."
                    
        except httpx.TimeoutException:
            return "The request timed out. Please try again."
        
        except httpx.RequestError:
            return "I'm having trouble connecting to my services. Please try again later."
        
        except Exception as e:
            # Log error for debugging (in production, use proper logging)
            print(f"Gemini API Error: {str(e)}")
            return "I encountered an unexpected error. Please try again."
    
    def _clean_response(self, text: str) -> str:
        """
        Clean and format the AI response
        
        Args:
            text: Raw AI response
            
        Returns:
            Cleaned response text
        """
        # Remove any potential disclaimers or harmful content
        text = text.strip()
        
        # Ensure it doesn't contain financial advice keywords
        forbidden_phrases = [
            "you should buy", 
            "you should sell", 
            "I recommend",
            "you should invest",
            "buy this",
            "sell that"
        ]
        
        text_lower = text.lower()
        for phrase in forbidden_phrases:
            if phrase in text_lower:
                return "I can provide educational information but cannot give specific financial advice. Could you rephrase your question to focus on learning about financial concepts?"
        
        # Ensure response is educational
        if len(text) < 10:
            return "I'd be happy to help with financial education. Could you provide more details about what you'd like to learn?"
        
        return text
    
    async def test_connection(self) -> bool:
        """
        Test connection to Gemini API
        
        Returns:
            True if connection is successful
        """
        try:
            test_response = await self.generate_ai_response("Hello, can you explain what a stock is?")
            return len(test_response) > 10 and "error" not in test_response.lower()
        except:
            return False
    
    def get_financial_keywords(self) -> list:
        """
        Get list of financial keywords that trigger AI responses
        
        Returns:
            List of trigger keywords
        """
        return [
            "explain", "what is", "how does", "why", "stock", "investment", 
            "market", "finance", "money", "investing", "trading", "portfolio",
            "diversification", "risk", "return", "bond", "mutual fund",
            "etf", "index", "economy", "inflation", "interest", "compound",
            "dividend", "capital", "asset", "liability", "budget", "saving"
        ]
    
    def should_respond_to_message(self, message: str) -> bool:
        """
        Check if AI should respond to the message
        
        Args:
            message: User message
            
        Returns:
            True if AI should respond
        """
        message_lower = message.lower()
        keywords = self.get_financial_keywords()
        
        # Check if any financial keyword is present
        for keyword in keywords:
            if keyword in message_lower:
                return True
        
        # Check for question patterns
        question_indicators = ["?", "what", "how", "why", "explain", "tell me"]
        for indicator in question_indicators:
            if indicator in message_lower:
                return True
        
        return False
    
    def generate_response(self, message: str) -> str:
        """
        Synchronous wrapper for generate_ai_response
        
        Args:
            message: User message
            
        Returns:
            AI response string
        """
        try:
            import asyncio
            # Check if there's already an event loop running
            try:
                loop = asyncio.get_running_loop()
                # If there's already a loop running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_async, message)
                    return future.result()
            except RuntimeError:
                # No loop running, create a new one
                return asyncio.run(self.generate_ai_response(message))
        except Exception as e:
            return f"I apologize, but I couldn't process that request. Please try asking in a different way."
    
    def _run_async(self, message: str) -> str:
        """Helper method to run async function in thread"""
        import asyncio
        return asyncio.run(self.generate_ai_response(message))

# Singleton instance for reuse
gemini_client = GeminiClient()
