"""
Gemini AI Client
Handles communication with Google Gemini API for financial education assistant
"""

import os
import json
import logging
import httpx
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MODEL_NAME = "gemini-2.0-flash"


class GeminiClient:
    """
    Client for interacting with Google Gemini API
    Acts as a financial education assistant
    """
    
    def __init__(self):
        # Use the provided Gemini API key for housekeeping AI chat
        self.api_key = "AIzaSyCzZoEMgFTLvyF1A5HfePnriU3IPcUQHQk"
        
        # Fallback to environment variable if needed
        if not self.api_key or len(self.api_key) < 20:
            try:
                from services.freelance.gemini_config import GEMINI_API_KEY
                self.api_key = GEMINI_API_KEY
            except ImportError:
                self.api_key = os.getenv("GEMINI_API_KEY", "your_gemini_api_key_here")
            
        # Connectivity check on startup
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("⚠️ GEMINI_API_KEY not found in environment variables")
            print("📝 Please set GEMINI_API_KEY in your .env file")
        else:
            print("✅ Gemini API key loaded successfully")
            
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = MODEL_NAME
        logging.info(f"Gemini client initialized with model: {MODEL_NAME}")
        
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
        Synchronous Gemini call using httpx directly (no asyncio wrapping).
        Safe to call from Flask request threads.
        """
        try:
            # Build payload directly — do NOT use system_prompt.format() here
            # because `message` may already be a fully-formed prompt containing { } chars
            if '{user_message}' in self.system_prompt and len(message) < 500:
                # Short conversational message — wrap in system prompt
                full_prompt = self.system_prompt.format(user_message=message)
            else:
                # Already a full prompt (e.g. stock analysis prompt) — use as-is
                full_prompt = message

            url = f"{self.base_url}/models/{self.model}:generateContent"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            }
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                },
            }
            with httpx.Client(timeout=45.0) as client:
                response = client.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                candidates = result.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return self._clean_response(parts[0].get("text", ""))
                print(f"Gemini empty candidates: {result}")
                return "I apologize, but I couldn't generate a response. Please try rephrasing your question."

            elif response.status_code == 400:
                print(f"Gemini 400 error: {response.text[:300]}")
                return "I apologize, but I couldn't process that request. Please try asking in a different way."

            elif response.status_code == 429:
                print(f"Gemini 429 error: {response.text[:300]}")
                return "I'm receiving too many requests right now. Please wait a moment and try again."

            elif response.status_code == 404:
                raise ValueError(
                    f"Gemini model not found. Check model name. Error: {response.text}"
                )

            else:
                print(f"Gemini error {response.status_code}: {response.text[:300]}")
                return "I'm experiencing technical difficulties. Please try again later."

        except httpx.TimeoutException:
            print("Gemini timeout")
            return "The request timed out. Please try again."
        except httpx.RequestError as e:
            print(f"Gemini connection error: {e}")
            return "I'm having trouble connecting to my services. Please try again later."
        except ValueError:
            raise
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                raise ValueError(
                    f"Gemini model not found. Check model name. Error: {error_msg}"
                )
            raise

    def _run_async(self, message: str) -> str:
        """Helper method to run async function in thread (kept for backward compat)"""
        import asyncio
        return asyncio.run(self.generate_ai_response(message))

# Singleton instance for reuse
gemini_client = GeminiClient()
