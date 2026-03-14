"""
Knowledge AI Service
AI-powered financial education using Gemini API
"""

import os
import httpx
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from .gemini_client import gemini_client

class KnowledgeAIService:
    """
    AI service for financial education
    """
    
    def __init__(self):
        self.gemini_client = gemini_client
    
    def get_financial_knowledge(self, query: str) -> Dict[str, Any]:
        """
        Get financial knowledge using Gemini API (simplified version)
        
        Args:
            query: User query about financial concept
            
        Returns:
            Dictionary with knowledge response
        """
        try:
            # Build educational prompt
            prompt = f"""
You are a financial education assistant.

Explain the following financial concept clearly and simply:

Concept: {query}

Rules:
* Only provide educational explanations
* Do not give financial advice
* Do not say "buy", "sell", "hold", or "recommend"
* Explain concepts clearly and simply
* Include relevant examples when helpful
* Mention risks and considerations when appropriate
* Use simple, easy-to-understand language
* Acknowledge if this is educational information only

Provide a helpful educational response about this financial concept.
"""
            
            # Generate response using Gemini (simplified synchronous call)
            try:
                response = self.gemini_client.generate_response(prompt)
                if response and "couldn't process" not in response.lower():
                    return {
                        'success': True,
                        'response': response,
                        'type': 'knowledge_response',
                        'query': query,
                        'timestamp': datetime.utcnow().isoformat()
                    }
            except Exception as e:
                print(f"Gemini API failed: {e}")
            
            # Fallback to basic educational response
            return self._get_basic_knowledge_response(query)
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error retrieving financial knowledge: {str(e)}",
                'suggestions': [
                    "Try rephrasing your question",
                    "Ask about a more general financial topic",
                    "Contact support if the issue persists"
                ]
            }
    
    def _get_basic_knowledge_response(self, query: str) -> Dict[str, Any]:
        """Get basic educational response for common financial concepts"""
        query_lower = query.lower()
        
        # Basic educational responses
        educational_responses = {
            "diversification": """
**Diversification - Educational Overview**

Diversification is a risk management strategy that involves spreading investments across various assets, industries, and geographic areas.

**Key Points:**
- Reduces portfolio risk by not putting all eggs in one basket
- Different assets perform differently under various market conditions
- Helps protect against significant losses in any single investment

**Example:**
Instead of investing all money in one stock, diversify across:
- Multiple stocks from different sectors
- Bonds and fixed income
- Real estate or commodities
- International markets

**Important Note:**
This information is for educational purposes only and not financial advice.
""",
            "compound interest": """
**Compound Interest - Educational Overview**

Compound interest is the process where interest earns interest, creating exponential growth over time.

**How It Works:**
- You earn interest on your principal amount
- You also earn interest on accumulated interest
- This creates a snowball effect of growing wealth

**Example:**
If you invest ₹10,000 at 8% annual compound interest:
- Year 1: ₹10,800
- Year 2: ₹11,664 (interest on interest)
- Year 3: ₹12,597 (compounding continues)

**Key Insight:**
The earlier you start, the more powerful compound interest becomes.

**Important Note:**
This information is for educational purposes only and not financial advice.
""",
            "mutual funds": """
**Mutual Funds - Educational Overview**

Mutual funds are investment vehicles that pool money from multiple investors to purchase a diversified portfolio of stocks, bonds, or other securities.

**How They Work:**
- Professional fund managers handle investment decisions
- Investors buy shares representing ownership in the fund
- Returns depend on the fund's performance

**Types of Mutual Funds:**
- Equity funds (stocks)
- Debt funds (bonds)
- Hybrid funds (balanced approach)
- Index funds (track market indices)

**Benefits:**
- Professional management
- Diversification
- Liquidity
- Affordable entry point

**Important Note:**
This information is for educational purposes only and not financial advice.
"""
        }
        
        # Check for matching concepts
        for concept, response in educational_responses.items():
            if concept in query_lower:
                return {
                    'success': True,
                    'response': response.strip(),
                    'type': 'knowledge_response',
                    'query': query,
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        # Generic response for other concepts
        generic_response = f"""
**Financial Education - {query.title()}**

I apologize, but I'm unable to provide detailed information on "{query}" at the moment.

**What I can help with:**
- Stock analysis (e.g., "analyze HDFC stock")
- Basic concepts like diversification, compound interest, mutual funds
- Market news and updates

**Suggestions:**
- Try rephrasing your question
- Be more specific about the financial concept
- Check if the concept is spelled correctly

**Important Note:**
This information is for educational purposes only and not financial advice.
"""
        
        return {
            'success': True,
            'response': generic_response.strip(),
            'type': 'knowledge_response',
            'query': query,
            'timestamp': datetime.utcnow().isoformat()
        }

# Singleton instance for reuse
knowledge_ai_service = KnowledgeAIService()
