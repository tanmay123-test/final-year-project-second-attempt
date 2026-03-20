"""
Stock AI Service
Handles AI analysis of stock data using Gemini API
"""

import os
import httpx
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from .gemini_client import gemini_client
from services.stock_service import stock_service

class StockAIService:
    """
    Service for AI-powered stock analysis using Gemini API
    """
    
    def __init__(self):
        self.gemini_client = gemini_client
        self.stock_service = stock_service
        
        # Stock-specific prompt template
        self.stock_analysis_prompt = """You are a financial education assistant specializing in stock analysis.

Use the following stock data to provide educational insights about the company fundamentals and market position.

Stock Data:
Symbol: {symbol}
Company Name: {company_name}
Current Price: ${price}
Change: {change} ({change_percent}%)
Previous Close: ${previous_close}
Market Cap: {market_cap}
Sector: {sector}
Industry: {industry}
PE Ratio: {pe_ratio}
PB Ratio: {pb_ratio}
ROE: {roe}%
Revenue Growth: {revenue_growth}%
Net Margin: {net_margin}%
Debt to Equity: {debt_to_equity}
Beta: {beta}
52-Week Range: ${low_52w} - ${high_52w}

Company Description:
{description}

IMPORTANT RULES:
* DO NOT give financial advice or recommendations
* DO NOT say "buy", "sell", "hold", "invest", or "recommend"
* DO NOT predict future price movements
* ONLY provide educational analysis and insights
* Explain what the metrics mean in simple terms
* Discuss both strengths and potential risks
* If data is incomplete or outdated, mention this limitation
* Focus on helping the user understand the business, not making investment decisions

User Question:
{user_message}

Provide an educational analysis that helps the user understand the company's fundamentals, market position, and key metrics."""

        # Stock search prompt template
        self.stock_search_prompt = """You are a financial education assistant helping users identify companies.

Based on the search results below, help the user understand which companies match their query and provide brief educational insights about each.

Search Results:
{search_results}

IMPORTANT RULES:
* DO NOT give financial advice or recommendations
* DO NOT say "buy", "sell", "hold", "invest", or "recommend"
* ONLY provide educational information about the companies
* Explain what each company does in simple terms
* If multiple results, help the user understand the differences
* If no clear matches, suggest refining the search

User Query:
{user_message}

Help the user understand the search results and learn about the relevant companies."""
    
    async def generate_stock_analysis(self, user_message: str) -> Dict[str, Any]:
        """
        Generate AI analysis for stock-related query
        
        Args:
            user_message: User's message about stocks
            
        Returns:
            Dictionary containing AI analysis response
        """
        try:
            # Extract company name or ticker symbol
            company_info = self._extract_company_info(user_message)
            
            if not company_info:
                return {
                    "success": False,
                    "error": "Could not identify a specific company or stock symbol in your message. Please provide a company name or stock symbol.",
                    "suggestions": [
                        "Try: 'Analyze Apple stock'",
                        "Try: 'What is Tesla's PE ratio?'",
                        "Try: 'Explain Microsoft fundamentals'"
                    ]
                }
            
            # Get stock data
            stock_data = await self._get_stock_data_with_fallback(company_info)
            
            if "error" in stock_data:
                return {
                    "success": False,
                    "error": f"I could not find market data for '{company_info}'. Please verify the company name or stock symbol.",
                    "suggestions": [
                        "Check the spelling of the company name",
                        "Use the exact stock ticker symbol (e.g., AAPL for Apple)",
                        "Try searching for the company first"
                    ]
                }
            
            # Generate AI analysis
            analysis = await self._generate_analysis_with_data(user_message, stock_data)
            
            return {
                "success": True,
                "analysis": analysis,
                "stock_data": stock_data,
                "company_info": company_info,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error generating stock analysis: {str(e)}")
            return {
                "success": False,
                "error": "I encountered an error while analyzing the stock. Please try again later.",
                "suggestions": [
                    "Check your internet connection",
                    "Try again with a different company",
                    "Contact support if the issue persists"
                ]
            }
    
    async def compare_stocks(self, user_message: str) -> Dict[str, Any]:
        """
        Compare multiple stocks based on user query
        
        Args:
            user_message: User's comparison query
            
        Returns:
            Dictionary containing stock comparison analysis
        """
        try:
            # Extract company names/symbols from comparison query
            companies = self._extract_comparison_companies(user_message)
            
            if len(companies) < 2:
                return {
                    "success": False,
                    "error": "Please provide at least two companies to compare.",
                    "suggestions": [
                        "Try: 'Compare Apple vs Microsoft'",
                        "Try: 'HDFC vs ICICI comparison'",
                        "Try: 'Compare Tesla, Ford, and GM'"
                    ]
                }
            
            # Get stock data for all companies
            stock_data_list = []
            for company in companies:
                stock_data = await self._get_stock_data_with_fallback(company)
                if "error" not in stock_data:
                    stock_data_list.append(stock_data)
            
            if len(stock_data_list) < 2:
                return {
                    "success": False,
                    "error": "Could not find data for sufficient companies to compare.",
                    "suggestions": [
                        "Check company names spelling",
                        "Use exact stock symbols",
                        "Try with well-known companies"
                    ]
                }
            
            # Generate AI comparison analysis
            comparison_analysis = await self._generate_comparison_analysis(user_message, stock_data_list)
            
            return {
                "success": True,
                "analysis": comparison_analysis,
                "companies": stock_data_list,
                "comparison_count": len(stock_data_list),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error comparing stocks: {str(e)}")
            return {
                "success": False,
                "error": "I encountered an error while comparing stocks. Please try again later.",
                "suggestions": [
                    "Check your internet connection",
                    "Try again with different companies",
                    "Contact support if issue persists"
                ]
            }
    
    def _extract_comparison_companies(self, message: str) -> List[str]:
        """
        Extract company names from comparison query
        
        Args:
            message: User message
            
        Returns:
            List of company names/symbols
        """
        message = message.lower()
        
        # Look for comparison patterns
        comparison_patterns = [
            r'compare\s+(.+?)\s+vs\s+(.+)',
            r'(.+?)\s+vs\s+(.+)',
            r'compare\s+(.+?),\s+(.+?),\s+and\s+(.+?)',
            r'(.+?),\s+(.+?),\s+and\s+(.+?)',
            r'(.+?)\s+and\s+(.+?)\s+comparison',
        ]
        
        for pattern in comparison_patterns:
            match = re.search(pattern, message)
            if match:
                companies = [group.strip() for group in match.groups() if group.strip()]
                return companies
        
        # Fallback: look for multiple capitalized words or symbols
        words = message.split()
        potential_companies = []
        for word in words:
            word = word.strip('.,!?')
            if len(word) > 1 and (word.isupper() or '.' in word):
                potential_companies.append(word)
        
        return potential_companies[:5]  # Limit to 5 companies
    
    async def _generate_comparison_analysis(self, user_message: str, stock_data_list: List[Dict[str, Any]]) -> str:
        """
        Generate AI comparison analysis
        
        Args:
            user_message: Original user message
            stock_data_list: List of stock data dictionaries
            
        Returns:
            AI comparison analysis text
        """
        # Format stock data for comparison prompt
        formatted_data = ""
        for i, stock_data in enumerate(stock_data_list, 1):
            formatted_data += f"""
Stock {i}:
Symbol: {stock_data.get('symbol', 'N/A')}
Company: {stock_data.get('company_name', 'N/A')}
Price: ${stock_data.get('current_price', 'N/A')}
Market Cap: ${stock_data.get('market_cap', 'N/A')}
PE Ratio: {stock_data.get('pe_ratio', 'N/A')}
Sector: {stock_data.get('sector', 'N/A')}
"""
        
        # Comparison prompt
        comparison_prompt = f"""You are a financial education assistant specializing in stock comparisons.

Compare the following stocks based on their fundamentals and market position:

{formatted_data}

User Question:
{user_message}

IMPORTANT RULES:
* DO NOT give financial advice or recommendations
* DO NOT say "buy", "sell", "hold", "invest", or "recommend"
* DO NOT suggest which stock is "better"
* ONLY provide educational comparison and insights
* Explain what the metrics mean in simple terms
* Discuss relative strengths and weaknesses of each company
* Focus on helping the user understand the differences
* If data is incomplete or outdated, mention this limitation

Provide an educational comparison that helps the user understand the differences between these companies."""
        
        # Generate AI response
        return await self.gemini_client.generate_ai_response(comparison_prompt)
    
    async def search_and_analyze(self, user_message: str) -> Dict[str, Any]:
        """
        Search for stocks and provide analysis
        
        Args:
            user_message: User's search query
            
        Returns:
            Dictionary containing search results and analysis
        """
        try:
            # Extract search terms
            search_terms = self._extract_search_terms(user_message)
            
            if not search_terms:
                return {
                    "success": False,
                    "error": "Please provide a company name or search term.",
                    "suggestions": [
                        "Try: 'Search for technology companies'",
                        "Try: 'Find automotive stocks'",
                        "Try: 'Look up Apple'"
                    ]
                }
            
            # Search for stocks
            search_results = await self.stock_service.search_stocks(search_terms)
            
            if not search_results:
                return {
                    "success": False,
                    "error": f"No companies found matching '{search_terms}'.",
                    "suggestions": [
                        "Try different search terms",
                        "Check the spelling of company names",
                        "Use more general terms"
                    ]
                }
            
            # Generate AI analysis of search results
            analysis = await self._generate_search_analysis(user_message, search_results)
            
            return {
                "success": True,
                "analysis": analysis,
                "search_results": search_results,
                "search_terms": search_terms,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error in search and analyze: {str(e)}")
            return {
                "success": False,
                "error": "I encountered an error while searching for stocks. Please try again later."
            }
    
    def _extract_company_info(self, message: str) -> Optional[str]:
        """
        Extract company name or ticker symbol from message
        
        Args:
            message: User message
            
        Returns:
            Company name or ticker symbol
        """
        message = message.strip()
        
        # Extract stock symbols first (highest priority)
        symbols = self.stock_service.extract_stock_symbols(message)
        if symbols:
            return symbols[0]  # Return the first symbol found
        
        # Dynamic company name extraction - look for any capitalized words that might be company names
        words = message.split()
        for word in words:
            # Check if word might be a company name (capitalized and longer than 2 chars)
            if len(word) > 2 and word[0].isupper():
                # For now, just return the word - the actual stock data fetching will validate it
                # This avoids async calls in this extraction method
                return word
        
        # Extract from common stock-related patterns
        stock_patterns = [
            r'\b(.+?)\s+(?:stock|shares|equity|ticker|symbol|price|analysis|invest|trade)\b',
            r'\b(?:analyze|explain|what\s+is|tell\s+me\s+about|show\s+me)\s+(.+?)\b',
            r'\b(.+?)(?:\s+(?:stock|shares|equity|ticker|symbol|price|analysis|invest|trade))\b'
        ]
        
        for pattern in stock_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                company = match.group(1) if match.groups() else match.group(0)
                return company.strip()
        
        return None
    
    def _extract_search_terms(self, message: str) -> Optional[str]:
        """
        Extract search terms from message
        
        Args:
            message: User message
            
        Returns:
            Search terms
        """
        # Remove common search keywords
        search_keywords = ["search", "find", "look up", "show me", "what are", "tell me about"]
        
        for keyword in search_keywords:
            if keyword in message.lower():
                # Extract the part after the keyword
                parts = message.lower().split(keyword, 1)
                if len(parts) > 1:
                    return parts[1].strip()
        
        # If no keyword found, use the whole message
        return message.strip()
    
    async def _get_stock_data_with_fallback(self, company_info: str) -> Dict[str, Any]:
        """
        Get stock data with fallback mechanisms
        
        Args:
            company_info: Company name or symbol
            
        Returns:
            Stock data dictionary
        """
        # First try as symbol
        stock_data = await self.stock_service.get_stock_data(company_info)
        
        # If failed and it's a company name, try searching
        if "error" in stock_data and len(company_info) > 5:
            search_results = await self.stock_service.search_stocks(company_info)
            if search_results:
                # Use the first result's symbol
                first_symbol = search_results[0]["symbol"]
                stock_data = await self.stock_service.get_stock_data(first_symbol)
        
        return stock_data
    
    async def _generate_analysis_with_data(self, user_message: str, stock_data: Dict[str, Any]) -> str:
        """
        Generate AI analysis using stock data
        
        Args:
            user_message: Original user message
            stock_data: Stock data dictionary
            
        Returns:
            AI analysis text
        """
        # Format stock data for prompt
        formatted_data = self._format_stock_data_for_prompt(stock_data)
        
        # Create the full prompt
        full_prompt = self.stock_analysis_prompt.format(
            user_message=user_message,
            **formatted_data
        )
        
        # Generate AI response
        response = await self.gemini_client.generate_ai_response(full_prompt)
        
        return response
    
    async def _generate_search_analysis(self, user_message: str, search_results: List[Dict[str, Any]]) -> str:
        """
        Generate AI analysis for search results
        
        Args:
            user_message: Original user message
            search_results: List of search results
            
        Returns:
            AI analysis text
        """
        # Format search results for prompt
        formatted_results = self._format_search_results_for_prompt(search_results)
        
        # Create the full prompt
        full_prompt = self.stock_search_prompt.format(
            user_message=user_message,
            search_results=formatted_results
        )
        
        # Generate AI response
        response = await self.gemini_client.generate_ai_response(full_prompt)
        
        return response
    
    def _format_stock_data_for_prompt(self, stock_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Format stock data for AI prompt
        
        Args:
            stock_data: Raw stock data
            
        Returns:
            Formatted stock data dictionary
        """
        def format_number(value, default="N/A"):
            if value is None or value == 0:
                return default
            try:
                if isinstance(value, (int, float)):
                    if abs(value) >= 1e9:
                        return f"${value/1e9:.1f}B"
                    elif abs(value) >= 1e6:
                        return f"${value/1e6:.1f}M"
                    elif abs(value) >= 1e3:
                        return f"${value/1e3:.1f}K"
                    else:
                        return f"{value:.2f}"
                return str(value)
            except:
                return default
        
        def format_percentage(value, default="N/A"):
            if value is None or value == 0:
                return default
            try:
                return f"{value:.2f}%"
            except:
                return default
        
        return {
            "symbol": stock_data.get("symbol", "N/A"),
            "company_name": stock_data.get("company_name", "N/A"),
            "price": format_number(stock_data.get("price", 0)),
            "change": format_number(stock_data.get("change", 0)),
            "change_percent": format_percentage(stock_data.get("change_percent", 0)),
            "previous_close": format_number(stock_data.get("previous_close", 0)),
            "market_cap": format_number(stock_data.get("market_cap", 0)),
            "sector": stock_data.get("sector", "N/A"),
            "industry": stock_data.get("industry", "N/A"),
            "pe_ratio": format_number(stock_data.get("pe_ratio", 0)),
            "pb_ratio": format_number(stock_data.get("pb_ratio", 0)),
            "roe": format_percentage(stock_data.get("roe", 0)),
            "revenue_growth": format_percentage(stock_data.get("revenue_growth", 0)),
            "net_margin": format_percentage(stock_data.get("net_margin", 0)),
            "debt_to_equity": format_number(stock_data.get("debt_to_equity", 0)),
            "beta": format_number(stock_data.get("beta", 0)),
            "low_52w": format_number(stock_data.get("low_52w", 0)),
            "high_52w": format_number(stock_data.get("high_52w", 0)),
            "description": stock_data.get("description", "No description available.")[:500] + "..." if len(stock_data.get("description", "")) > 500 else stock_data.get("description", "No description available.")
        }
    
    def _format_search_results_for_prompt(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Format search results for AI prompt
        
        Args:
            search_results: List of search results
            
        Returns:
            Formatted search results string
        """
        if not search_results:
            return "No search results found."
        
        formatted_results = []
        for i, result in enumerate(search_results[:5], 1):
            formatted_results.append(
                f"{i}. {result.get('name', 'Unknown')} ({result.get('symbol', 'N/A')}) - {result.get('type', 'Unknown')}"
            )
        
        return "\n".join(formatted_results)
    
    async def test_stock_analysis(self) -> bool:
        """
        Test stock analysis functionality
        
        Returns:
            True if test is successful
        """
        try:
            # Test with a known stock
            result = await self.generate_stock_analysis("Analyze Apple stock fundamentals")
            return result.get("success", False)
        except:
            return False
    
    def get_supported_companies(self) -> List[str]:
        """
        Get list of commonly supported companies for testing
        
        Returns:
            List of company names and symbols
        """
        return [
            "Apple (AAPL)",
            "Tesla (TSLA)",
            "Microsoft (MSFT)",
            "Amazon (AMZN)",
            "Google/Alphabet (GOOGL)",
            "Meta/Facebook (META)",
            "NVIDIA (NVDA)",
            "Intel (INTC)",
            "AMD (AMD)",
            "JPMorgan (JPM)"
        ]
    
    def get_sample_queries(self) -> List[str]:
        """
        Get sample stock analysis queries
        
        Returns:
            List of sample queries
        """
        return [
            "Analyze Apple stock fundamentals",
            "What is Tesla's PE ratio?",
            "Explain Microsoft's business model",
            "How does Amazon make money?",
            "Compare Google vs Meta",
            "Search for technology companies",
            "Find automotive stocks"
        ]

# Singleton instance for reuse
stock_ai_service = StockAIService()
