"""
Knowledge AI Service
AI-powered financial education using vector search and Gemini API
"""

import os
import httpx
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from .gemini_client import gemini_client
from .vector_store_simple import vector_store
from .knowledge_loader_simple import knowledge_loader

class KnowledgeAIService:
    """
    AI service for financial education using vector search
    """
    
    def __init__(self):
        self.gemini_client = gemini_client
        self.vector_store = vector_store
        self.knowledge_loader = knowledge_loader
        
        # Knowledge-based prompt template
        self.knowledge_prompt = """You are a financial education assistant.

Use the provided financial knowledge to answer the question comprehensively.

Knowledge Context:
{retrieved_documents}

User Question:
{user_message}

IMPORTANT RULES:
* ONLY provide educational explanations based on the provided knowledge
* DO NOT give financial advice or recommendations
* DO NOT say "buy", "sell", "hold", "invest", or "recommend"
* Explain concepts clearly and simply
* Include relevant examples when helpful
* Mention risks and considerations when appropriate
* If the knowledge doesn't fully answer the question, acknowledge limitations

Provide a helpful educational response:"""
    
    async def generate_knowledge_response(self, query: str) -> Dict[str, Any]:
        """
        Generate AI response using vector search and Gemini API
        """
        try:
            # Search for relevant knowledge documents
            search_results = await self.vector_store.search_knowledge(query, limit=5)
            
            if not search_results:
                return {
                    "success": False,
                    "error": "I couldn't find relevant financial education content for your question.",
                    "suggestions": [
                        "Try asking about investing basics",
                        "Ask about diversification",
                        "Inquire about risk management",
                        "Learn about mutual funds or ETFs"
                    ]
                }
            
            # Retrieve full document content
            retrieved_documents = []
            for result in search_results:
                content = self.vector_store.get_document_content(result["id"])
                if content:
                    retrieved_documents.append({
                        "title": result["title"],
                        "content": content,
                        "score": result["score"]
                    })
            
            if not retrieved_documents:
                return {
                    "success": False,
                    "error": "I found some references but couldn't retrieve the full content.",
                    "suggestions": [
                        "Try rephrasing your question",
                        "Ask about a more general financial topic",
                        "Contact support if the issue persists"
                    ]
                }
            
            # Format retrieved documents for prompt
            formatted_documents = self._format_documents_for_prompt(retrieved_documents)
            
            # Build the full prompt
            full_prompt = self.knowledge_prompt.format(
                retrieved_documents=formatted_documents,
                user_message=query
            )
            
            # Generate AI response
            response = await self.gemini_client.generate_ai_response(full_prompt)
            
            return {
                "success": True,
                "response": response,
                "sources": [
                    {
                        "title": doc["title"],
                        "score": doc["score"]
                    }
                    for doc in retrieved_documents
                ],
                "query": query,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error generating knowledge response: {str(e)}")
            return {
                "success": False,
                "error": "I encountered an error while processing your question. Please try again later.",
                "suggestions": [
                    "Check your internet connection",
                    "Try rephrasing your question",
                    "Contact support if the issue persists"
                ]
            }
    
    def _format_documents_for_prompt(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents for AI prompt
        """
        if not documents:
            return "No relevant documents found."
        
        formatted_docs = []
        for i, doc in enumerate(documents, 1):
            formatted_docs.append(
                f"Document {i}:\n"
                f"Title: {doc['title']}\n"
                f"Content: {doc['content'][:1000]}...\n"
                f"Relevance Score: {doc['score']:.2f}\n"
            )
        
        return "\n".join(formatted_docs)
    
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
    
    def get_financial_knowledge(self, query: str) -> Dict[str, Any]:
    
    async def initialize_knowledge_base(self) -> bool:
        """
        Initialize the knowledge base with financial education content
        """
        try:
            # Initialize vector store
            store_initialized = await self.vector_store.initialize_vector_store()
            if not store_initialized:
                return False
            
            # Load financial education content
            print("📚 Loading financial education content...")
            education_content = self.knowledge_loader.load_financial_education_content()
            
            if not education_content:
                print("⚠️ No education content loaded, using sample content")
                education_content = self._get_sample_knowledge_content()
            
            # Add documents to vector store
            documents_added = await self.vector_store.add_documents_to_vector_store(education_content)
            
            if documents_added:
                print(f"✅ Added {len(education_content)} documents to knowledge base")
                return True
            else:
                print("❌ Failed to add documents to knowledge base")
                return False
                
        except Exception as e:
            print(f"❌ Error initializing knowledge base: {str(e)}")
            return False
    
    def _get_sample_knowledge_content(self) -> List[Dict[str, Any]]:
        """
        Get sample financial education content for testing
        """
        return [
            {
                "id": "diversification_101",
                "title": "What is Diversification?",
                "content": "Diversification is a risk management strategy that involves spreading investments across various financial instruments, industries, and other categories. The goal is to maximize returns by investing in different areas that would each react differently to the same event. Most investment professionals agree that, although it does not guarantee against loss, diversification is the most important component of reaching long-range financial goals while minimizing risk.",
                "metadata": {"category": "investing_basics", "difficulty": "beginner"},
                "url": "https://www.investopedia.com/terms/d/diversification.asp"
            },
            {
                "id": "mutual_funds_guide",
                "title": "Understanding Mutual Funds",
                "content": "A mutual fund is a professionally managed investment fund that pools money from many investors to purchase securities. These funds may invest in stocks, bonds, money market instruments, or other assets. Mutual funds offer small investors access to professionally managed, diversified portfolios of equities, bonds and other securities, which would be quite difficult to create with a small amount of capital.",
                "metadata": {"category": "investment_products", "difficulty": "intermediate"},
                "url": "https://www.investopedia.com/terms/m/mutualfund.asp"
            },
            {
                "id": "etf_basics",
                "title": "Exchange-Traded Funds (ETFs) Explained",
                "content": "An exchange-traded fund (ETF) is a type of investment fund and exchange-traded product, with assets that are traded on a stock exchange. ETFs are similar in many ways to mutual funds, except that ETFs are bought and sold throughout the day on stock exchanges while mutual funds are bought and sold based on their price at day's end. An ETF is a marketable security that tracks an index, a commodity, bonds, or a basket of assets like an index fund.",
                "metadata": {"category": "investment_products", "difficulty": "intermediate"},
                "url": "https://www.investopedia.com/terms/e/etf.asp"
            },
            {
                "id": "risk_management",
                "title": "Investment Risk Management",
                "content": "Risk management is the process of identification, analysis and acceptance or mitigation of uncertainty in investment decisions. Risk is inherent in all investing, but the degree of risk varies between different types of investments. Risk management in finance involves identifying, analyzing, and addressing potential risks to minimize their negative impact on investment returns.",
                "metadata": {"category": "risk_management", "difficulty": "advanced"},
                "url": "https://www.investopedia.com/terms/r/riskmanagement.asp"
            },
            {
                "id": "portfolio_allocation",
                "title": "Portfolio Allocation Strategies",
                "content": "Portfolio allocation is the process of deciding how to distribute an investment portfolio across different asset classes, such as stocks, bonds, and cash. The allocation should be based on the investor's goals, risk tolerance, and investment horizon. Common allocation strategies include strategic allocation, tactical allocation, and dynamic allocation.",
                "metadata": {"category": "portfolio_management", "difficulty": "intermediate"},
                "url": "https://www.investopedia.com/terms/p/portfolioallocation.asp"
            }
        ]
    
    async def search_knowledge_base(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for relevant documents
        """
        try:
            results = await self.vector_store.search_knowledge(query, limit)
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result["id"],
                    "title": result["title"],
                    "content": result["content"],
                    "score": result["score"],
                    "metadata": result.get("metadata", {})
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching knowledge base: {str(e)}")
            return []
    
    def get_knowledge_categories(self) -> List[str]:
        """
        Get available knowledge categories
        """
        return [
            "investing_basics",
            "investment_products", 
            "risk_management",
            "portfolio_management",
            "market_analysis",
            "financial_planning",
            "tax_planning",
            "retirement_planning"
        ]
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics
        """
        try:
            vector_count = self.vector_store.get_vector_count()
            cache_status = self.vector_store.get_cache_status()
            
            return {
                "total_documents": vector_count,
                "cache_size": cache_status["cache_size"],
                "is_connected": cache_status["is_connected"],
                "categories": self.get_knowledge_categories(),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting knowledge stats: {str(e)}")
            return {
                "total_documents": 0,
                "cache_size": 0,
                "is_connected": False,
                "categories": self.get_knowledge_categories(),
                "last_updated": datetime.utcnow().isoformat()
            }
    
    async def test_knowledge_service(self) -> bool:
        """
        Test the knowledge service functionality
        """
        try:
            # Test vector store connection
            if not self.vector_store.is_connected():
                return False
            
            # Test knowledge search
            results = await self.search_knowledge_base("diversification", limit=3)
            if not results:
                return False
            
            # Test AI response generation
            response = await self.generate_knowledge_response("What is diversification?")
            return response.get("success", False)
            
        except Exception as e:
            print(f"Error testing knowledge service: {str(e)}")
            return False
    
    def get_sample_queries(self) -> List[str]:
        """
        Get sample knowledge queries for testing
        """
        return [
            "What is diversification?",
            "How do mutual funds work?",
            "What are ETFs?",
            "How can I manage investment risk?",
            "What is portfolio allocation?",
            "What are the basics of investing?",
            "How do I start investing?",
            "What is a stock?",
            "What is a bond?",
            "How does compound interest work?"
        ]

# Singleton instance for reuse
knowledge_ai_service = KnowledgeAIService()
