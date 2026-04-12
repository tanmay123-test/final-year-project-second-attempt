"""
Stock Data Service
Handles fetching stock market data from Finnhub API
"""

import os
import httpx
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
from functools import lru_cache

class StockService:
    """
    Service for fetching stock market data using Finnhub API
    """
    
    def __init__(self):
        self.api_key = os.getenv("FINNHUB_API_KEY", "your_finnhub_api_key_here")
        self.base_url = "https://finnhub.io/api/v1"
        self.cache_timeout = 300  # 5 minutes cache
        self._cache = {}
        
    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch comprehensive stock data for a given symbol
        
        Args:
            symbol: Stock ticker symbol (e.g., "AAPL", "TSLA")
            
        Returns:
            Dictionary containing stock data
        """
        try:
            # Check cache first
            cache_key = symbol.upper()
            if self._is_cached(cache_key):
                return self._cache[cache_key]["data"]
            
            # Normalize symbol
            symbol = symbol.upper().strip()
            
            # Fetch data concurrently
            tasks = [
                self._get_quote_data(symbol),
                self._get_profile_data(symbol),
                self._get_metrics_data(symbol),
                self._get_financial_data(symbol)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            quote_data = results[0] if not isinstance(results[0], Exception) else {}
            profile_data = results[1] if not isinstance(results[1], Exception) else {}
            metrics_data = results[2] if not isinstance(results[2], Exception) else {}
            financial_data = results[3] if not isinstance(results[3], Exception) else {}
            
            # Build comprehensive stock data
            stock_data = {
                "symbol": symbol,
                "company_name": profile_data.get("name", ""),
                "price": quote_data.get("c", 0),  # Current price
                "change": quote_data.get("d", 0),  # Change
                "change_percent": quote_data.get("dp", 0),  # Change percentage
                "previous_close": quote_data.get("pc", 0),  # Previous close
                "market_cap": profile_data.get("marketCapitalization", 0),
                "sector": profile_data.get("sector", "Unknown"),
                "industry": profile_data.get("industry", "Unknown"),
                "country": profile_data.get("country", ""),
                "currency": profile_data.get("currency", "USD"),
                "description": profile_data.get("description", ""),
                "pe_ratio": metrics_data.get("peBasicExclExtraTTM", {}).get("raw", 0),
                "pb_ratio": metrics_data.get("pbQuarterly", {}).get("raw", 0),
                "roe": metrics_data.get("roeTTM", {}).get("raw", 0),
                "revenue_growth": financial_data.get("revenueGrowth", {}).get("raw", 0),
                "net_margin": financial_data.get("netMargin", {}).get("raw", 0),
                "debt_to_equity": financial_data.get("debtToEquity", {}).get("raw", 0),
                "dividend_yield": metrics_data.get("dividendYieldTTM", {}).get("raw", 0),
                "beta": metrics_data.get("beta", {}).get("raw", 0),
                "volume": quote_data.get("v", 0),  # Volume
                "avg_volume": quote_data.get("avgVolume", 0),  # Average volume
                "high_52w": quote_data.get("h", 0),  # 52 week high
                "low_52w": quote_data.get("l", 0),  # 52 week low
                "timestamp": datetime.utcnow().isoformat(),
                "data_source": "Finnhub API"
            }
            
            # Check if the data is valid (price should be > 0)
            if stock_data.get("price", 0) <= 0:
                print(f"Invalid stock data (price=0) for {symbol}")
                return self._get_error_response(symbol, "Invalid stock data received")
            
            # Cache the result
            self._cache[cache_key] = {
                "data": stock_data,
                "timestamp": datetime.utcnow()
            }
            
            return stock_data
            
        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {str(e)}")
            return self._get_error_response(symbol, str(e))
    
    async def _get_quote_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch real-time quote data"""
        try:
            url = f"{self.base_url}/quote"
            params = {"symbol": symbol, "token": self.api_key}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {}
                    
        except Exception as e:
            print(f"Error fetching quote data: {str(e)}")
            return {}
    
    async def _get_profile_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch company profile data"""
        try:
            url = f"{self.base_url}/stock/profile2"
            params = {"symbol": symbol, "token": self.api_key}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {}
                    
        except Exception as e:
            print(f"Error fetching profile data: {str(e)}")
            return {}
    
    async def _get_metrics_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch financial metrics data"""
        try:
            url = f"{self.base_url}/stock/metric"
            params = {"symbol": symbol, "token": self.api_key, "metric": "all"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {}
                    
        except Exception as e:
            print(f"Error fetching metrics data: {str(e)}")
            return {}
    
    async def _get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch financial statements data"""
        try:
            url = f"{self.base_url}/stock/financials"
            params = {
                "symbol": symbol, 
                "token": self.api_key,
                "statement": "IS",  # Income Statement
                "period": "annual"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    # Extract growth metrics from financial data
                    if data and "financials" in data and data["financials"]:
                        latest = data["financials"][0]
                        return {
                            "revenueGrowth": latest.get("revenueGrowth", {"raw": 0}),
                            "netMargin": latest.get("netMargin", {"raw": 0}),
                            "debtToEquity": latest.get("debtToEquity", {"raw": 0})
                        }
                    return {}
                else:
                    return {}
                    
        except Exception as e:
            print(f"Error fetching financial data: {str(e)}")
            return {}
    
    def _is_cached(self, symbol: str) -> bool:
        """Check if data is cached and not expired"""
        if symbol not in self._cache:
            return False
        
        cache_time = self._cache[symbol]["timestamp"]
        return (datetime.utcnow() - cache_time).seconds < self.cache_timeout
    
    def _get_error_response(self, symbol: str, error: str) -> Dict[str, Any]:
        """Return error response for stock data"""
        return {
            "symbol": symbol,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": "Finnhub API",
            "note": "Unable to fetch stock data. Please verify the symbol or try again later."
        }
    
    async def search_stocks(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for stocks by company name or symbol
        
        Args:
            query: Search query (company name or symbol)
            
        Returns:
            List of matching stocks
        """
        try:
            url = f"{self.base_url}/search"
            params = {"q": query, "token": self.api_key}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("result", [])
                    
                    # Format results
                    formatted_results = []
                    for result in results[:10]:  # Limit to 10 results
                        formatted_results.append({
                            "symbol": result.get("symbol", ""),
                            "name": result.get("description", ""),
                            "type": result.get("type", ""),
                            "primary": result.get("primary", False)
                        })
                    
                    return formatted_results
                else:
                    return []
                    
        except Exception as e:
            print(f"Error searching stocks: {str(e)}")
            return []
    
    async def get_market_indices(self) -> Dict[str, Any]:
        """
        Get major market indices data
        
        Returns:
            Dictionary containing major indices data
        """
        try:
            indices = {
                "^GSPC": "S&P 500",
                "^DJI": "Dow Jones",
                "^IXIC": "NASDAQ"
            }
            
            tasks = [self._get_quote_data(symbol) for symbol in indices.keys()]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            indices_data = {}
            for i, (symbol, name) in enumerate(indices.items()):
                quote_data = results[i] if not isinstance(results[i], Exception) else {}
                indices_data[symbol] = {
                    "name": name,
                    "price": quote_data.get("c", 0),
                    "change": quote_data.get("d", 0),
                    "change_percent": quote_data.get("dp", 0)
                }
            
            return indices_data
            
        except Exception as e:
            print(f"Error fetching market indices: {str(e)}")
            return {}
    
    def extract_stock_symbols(self, text: str) -> List[str]:
        """
        Extract potential stock symbols from text
        
        Args:
            text: Input text
            
        Returns:
            List of potential stock symbols
        """
        import re
        
        # Common stock symbol patterns
        patterns = [
            r'\$([A-Z]{1,5})\b',  # $AAPL, $TSLA
            r'\b([A-Z]{1,5})\s+(?:stock|shares|inc|corp|ltd)\b',  # AAPL stock
            r'\b(NYSE|NASDAQ):\s*([A-Z]{1,5})\b',  # NASDAQ: AAPL
        ]
        
        symbols = set()
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    symbols.add(match[-1].upper())  # Get the symbol part
                else:
                    symbols.add(match.upper())
        
        # Filter out common words that might match patterns
        exclude_words = {"THE", "AND", "FOR", "INC", "CORP", "LTD", "A", "I", "AN", "IN", "ON", "AT", "TO", "OF"}
        symbols = [s for s in symbols if s not in exclude_words and len(s) >= 1]
        
        return list(symbols)[:5]  # Limit to 5 symbols
    
    def is_stock_query(self, message: str) -> bool:
        """
        Check if message is asking about stocks
        
        Args:
            message: User message
            
        Returns:
            True if message is stock-related
        """
        message_lower = message.lower()
        
        stock_keywords = [
            "stock", "stocks", "share", "shares", "equity", "equities",
            "ticker", "symbol", "market cap", "pe ratio", "dividend",
            "analyze", "analysis", "fundamentals", "valuation",
            "price", "trading", "investing", "investment", "portfolio"
        ]
        
        # Check for stock keywords
        if any(keyword in message_lower for keyword in stock_keywords):
            return True
        
        # Check for stock symbols
        symbols = self.extract_stock_symbols(message)
        if symbols:
            return True
        
        # Check for company names with stock context
        company_patterns = [
            r'\b(apple|tesla|microsoft|amazon|google|facebook|meta|nvidia|intel|amd|jpmorgan|bank of america|wells fargo|goldman sachs|morgan stanley|berkshire hathaway|johnson & johnson|procter & gamble|coca cola|pepsi|walmart|costco|home depot|lowes|disney|netflix|uber|lyft|airbnb|spotify|zoom|salesforce|oracle|intuit|adobe|microsoft|alphabet)\b.*\b(stock|shares|equity|ticker|symbol|price|analysis|invest|trade)\b',
            r'\b(stock|shares|equity|ticker|symbol|price|analysis|invest|trade)\b.*\b(apple|tesla|microsoft|amazon|google|facebook|meta|nvidia|intel|amd|jpmorgan|bank of america|wells fargo|goldman sachs|morgan stanley|berkshire hathaway|johnson & johnson|procter & gamble|coca cola|pepsi|walmart|costco|home depot|lowes|disney|netflix|uber|lyft|airbnb|spotify|zoom|salesforce|oracle|intuit|adobe|microsoft|alphabet)\b'
        ]
        
        for pattern in company_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    async def test_connection(self) -> bool:
        """
        Test connection to Finnhub API
        
        Returns:
            True if connection is successful
        """
        try:
            # Test with a common stock
            test_data = await self.get_stock_data("AAPL")
            return "error" not in test_data and test_data.get("price", 0) > 0
        except:
            return False
    
    def clear_cache(self):
        """Clear the stock data cache"""
        self._cache.clear()

# Singleton instance for reuse
stock_service = StockService()
