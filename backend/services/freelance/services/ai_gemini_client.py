import os
import httpx
from typing import Optional
import json
from ..gemini_config import GEMINI_API_KEY

class FreelanceGeminiClient:
    """
    Dedicated Gemini AI Client for the Freelance Service
    """
    
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-2.0-flash"

    async def generate_ai_response(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate AI response
        
        Args:
            message: User message/question
            system_prompt: Optional custom system prompt
            
        Returns:
            AI response text
        """
        try:
            # Prepare the prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nUser Question:\n{message}"
            else:
                full_prompt = message
            
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
                }
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
                            return candidate["content"]["parts"][0]["text"].strip()
                    
                    return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
                
                return f"Technical difficulties (Status: {response.status_code}). Please try again later."
                    
        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            return "I encountered an unexpected error. Please try again later."
    
    def generate_response(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        Synchronous wrapper for generate_ai_response
        """
        try:
            import asyncio
            # Check if there's already an event loop running
            try:
                loop = asyncio.get_running_loop()
                # If there's already a loop running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_async, message, system_prompt)
                    return future.result()
            except RuntimeError:
                # No loop running, create a new one
                return asyncio.run(self.generate_ai_response(message, system_prompt))
        except Exception as e:
            print(f"Sync error: {str(e)}")
            return "I apologize, but I couldn't process that request right now."
    
    def _run_async(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Helper method to run async function in thread"""
        import asyncio
        return asyncio.run(self.generate_ai_response(message, system_prompt))

# Singleton instance for freelance use
freelance_ai_client = FreelanceGeminiClient()
