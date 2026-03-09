"""
News Service
Financial news fetching and AI summarization
"""

import os
import httpx
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio

class NewsService:
    """
    Service for fetching and summarizing financial news
    """
    
    def __init__(self):
        self.api_key = os.getenv("FINNHUB_API_KEY", "your_finnhub_api_key_here")
        self.base_url = "https://finnhub.io/api/v1"
        self.cache = {}
        self.cache_timeout = 1800  # 30 minutes cache
        
        # Initialize HTTP client
        self.httpx = httpx.Client(timeout=30.0)
    
    async def fetch_market_news(self, category: str = "general", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch market news from Finnhub API
        """
        try:
            # Check cache first
            cache_key = f"news_{category}_{limit}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            url = f"{self.base_url}/news"
            params = {
                "category": category,
                "token": self.api_key
            }
            
            response = self.httpx.get(url, params=params)
            
            if response.status_code == 200:
                news_data = response.json()
                
                # Format news articles
                formatted_news = []
                for article in news_data:
                    formatted_news.append({
                        "id": article.get("id", ""),
                        "headline": article.get("headline", ""),
                        "source": article.get("source", ""),
                        "url": article.get("url", ""),
                        "summary": article.get("summary", ""),
                        "datetime": article.get("datetime", ""),
                        "related": article.get("related", []),
                        "image": article.get("image", ""),
                        "category": category
                    })
                
                # Cache the results
                self.cache[cache_key] = {
                    "data": formatted_news,
                    "timestamp": datetime.utcnow()
                }
                
                return formatted_news
            else:
                print(f"❌ Failed to fetch news: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching market news: {str(e)}")
            return []
    
    async def get_company_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get news for a specific company
        """
        try:
            # Check cache first
            cache_key = f"company_news_{symbol}_{limit}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            url = f"{self.base_url}/news"
            params = {
                "id": symbol,
                "token": self.api_key
            }
            
            response = await self.httpx.get(url, params=params)
            
            if response.status_code == 200:
                news_data = response.json()
                
                # Format news articles
                formatted_news = []
                for article in news_data:
                    formatted_news.append({
                        "id": article.get("id", ""),
                        "headline": article.get("headline", ""),
                        "source": article.get("source", ""),
                        "url": article.get("url", ""),
                        "summary": article.get("summary", ""),
                        "datetime": article.get("datetime", ""),
                        "related": article.get("related", []),
                        "image": article.get("image", ""),
                        "category": "company",
                        "symbol": symbol
                    })
                
                # Cache the results
                self.cache[cache_key] = {
                    "data": formatted_news,
                    "timestamp": datetime.utcnow()
                }
                
                return formatted_news
            else:
                print(f"❌ Failed to fetch company news: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching company news: {str(e)}")
            return []
    
    async def get_crypto_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get cryptocurrency news
        """
        try:
            # Check cache first
            cache_key = f"crypto_news_{limit}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            url = f"{self.base_url}/news"
            params = {
                "category": "crypto",
                "token": self.api_key
            }
            
            response = await self.httpx.get(url, params=params)
            
            if response.status_code == 200:
                news_data = response.json()
                
                # Format news articles
                formatted_news = []
                for article in news_data:
                    formatted_news.append({
                        "id": article.get("id", ""),
                        "headline": article.get("headline", ""),
                        "source": article.get("source", ""),
                        "url": article.get("url", ""),
                        "summary": article.get("summary", ""),
                        "datetime": article.get("datetime", ""),
                        "related": article.get("related", []),
                        "image": article.get("image", ""),
                        "category": "crypto"
                    })
                
                # Cache the results
                self.cache[cache_key] = {
                    "data": formatted_news,
                    "timestamp": datetime.utcnow()
                }
                
                return formatted_news
            else:
                print(f"❌ Failed to fetch crypto news: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching crypto news: {str(e)}")
            return []
    
    async def get_forex_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get forex news
        """
        try:
            # Check cache first
            cache_key = f"forex_news_{limit}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            url = f"{self.base_url}/news"
            params = {
                "category": "forex",
                "token": self.api_key
            }
            
            response = await self.httpx.get(url, params=params)
            
            if response.status_code == 200:
                news_data = response.json()
                
                # Format news articles
                formatted_news = []
                for article in news_data:
                    formatted_news.append({
                        "id": article.get("id", ""),
                        "headline": article.get("headline", ""),
                        "source": article.get("source", ""),
                        "url": article.get("url", ""),
                        "summary": article.get("summary", ""),
                        "datetime": article.get("datetime", ""),
                        "related": article.get("related", []),
                        "image": article.get("image", ""),
                        "category": "forex"
                    })
                
                # Cache the results
                self.cache[cache_key] = {
                    "data": formatted_news,
                    "timestamp": datetime.utcnow()
                }
                
                return formatted_news
            else:
                print(f"❌ Failed to fetch forex news: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching forex news: {str(e)}")
            return []
    
    async def get_merger_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get merger and acquisition news
        """
        try:
            # Check cache first
            cache_key = f"merger_news_{limit}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]["data"]
            
            url = f"{self.base_url}/news"
            params = {
                "category": "merger",
                "token": self.api_key
            }
            
            response = await self.httpx.get(url, params=params)
            
            if response.status_code == 200:
                news_data = response.json()
                
                # Format news articles
                formatted_news = []
                for article in news_data:
                    formatted_news.append({
                        "id": article.get("id", ""),
                        "headline": article.get("headline", ""),
                        "source": article.get("source", ""),
                        "url": article.get("url", ""),
                        "summary": article.get("summary", ""),
                        "datetime": article.get("datetime", ""),
                        "related": article.get("related", []),
                        "image": article.get("image", ""),
                        "category": "merger"
                    })
                
                # Cache the results
                self.cache[cache_key] = {
                    "data": formatted_news,
                    "timestamp": datetime.utcnow()
                }
                
                return formatted_news
            else:
                print(f"❌ Failed to fetch merger news: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching merger news: {str(e)}")
            return []
    
    async def summarize_news(self, news_articles: List[Dict[str, Any]], user_query: str = "") -> Dict[str, Any]:
        """
        Summarize news articles using AI
        """
        try:
            from ..ai.gemini_client import gemini_client
            
            if not news_articles:
                return {
                    "success": False,
                    "error": "No news articles to summarize.",
                    "suggestions": [
                        "Try fetching market news first",
                        "Check your API connection",
                        "Try a different news category"
                    ]
                }
            
            # Prepare news content for summarization
            news_content = self._format_news_for_prompt(news_articles)
            
            # Build prompt
            if user_query:
                prompt = f"""You are a financial news analyst.

Summarize the following news articles and answer the user's question.

News Articles:
{news_content}

User Question: {user_query}

IMPORTANT RULES:
* DO NOT give financial advice or investment recommendations
* DO NOT suggest buying or selling securities
* Focus on factual information and market analysis
* Explain market trends and implications clearly
* Include relevant context and background

Provide a helpful news summary and analysis:"""
            else:
                prompt = f"""You are a financial news analyst.

Summarize the following news articles and provide key insights.

News Articles:
{news_content}

IMPORTANT RULES:
* DO NOT give financial advice or investment recommendations
* DO NOT suggest buying or selling securities
* Focus on factual information and market analysis
* Explain market trends and implications clearly
* Include relevant context and background

Provide a helpful news summary and analysis:"""
            
            # Generate AI response
            gemini_client_instance = gemini_client
            response = await gemini_client.generate_ai_response(prompt)
            
            return {
                "success": True,
                "summary": response,
                "articles_count": len(news_articles),
                "categories": list(set(article.get("category", "general") for article in news_articles)),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error summarizing news: {str(e)}")
            return {
                "success": False,
                "error": "I encountered an error while summarizing the news. Please try again later.",
                "suggestions": [
                    "Check your internet connection",
                    "Try again with fewer articles",
                    "Contact support if the issue persists"
                ]
            }
    
    def _format_news_for_prompt(self, news_articles: List[Dict[str, Any]]) -> str:
        """
        Format news articles for AI prompt
        """
        if not news_articles:
            return "No news articles available."
        
        formatted_news = []
        for i, article in enumerate(news_articles, 1):
            formatted_news.append(
                f"Article {i}:\n"
                f"Headline: {article['headline']}\n"
                f"Source: {article['source']}\n"
                f"Summary: {article['summary']}\n"
                f"Category: {article['category']}\n"
                f"Date: {article['datetime']}\n"
            )
        
        return "\n".join(formatted_news)
    
    def _is_cached(self, cache_key: str) -> bool:
        """
        Check if data is cached and not expired
        """
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]["timestamp"]
        return (datetime.utcnow() - cache_time).seconds < self.cache_timeout
    
    def clear_cache(self):
        """Clear the news cache"""
        self.cache.clear()
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get cache status"""
        return {
            "cache_size": len(self.cache),
            "cache_timeout": self.cache_timeout,
            "cached_keys": list(self.cache.keys())
        }
    
    def get_news_categories(self) -> List[str]:
        """Get available news categories"""
        return [
            "general",
            "forex",
            "crypto",
            "merger",
            "company"
        ]
    
    def get_sample_queries(self) -> List[str]:
        """Get sample news queries"""
        return [
            "What's happening in the tech market today?",
            "Summarize the latest financial news",
            "What are the major market trends?",
            "Any news about Apple stock?",
            "What's happening in the crypto market?",
            "Any merger and acquisition news?",
            "How is the forex market performing?"
        ]
    
    def get_market_news(self) -> Dict[str, Any]:
        """
        Get market news (synchronous version with fallback)
        
        Returns:
            Dictionary with news data
        """
        try:
            import asyncio
            # Try to fetch real news
            try:
                news_data = asyncio.run(self.fetch_market_news("general", 5))
                if news_data:
                    return {
                        'success': True,
                        'articles': news_data,
                        'timestamp': datetime.utcnow().isoformat()
                    }
            except Exception as e:
                print(f"Failed to fetch real news: {e}")
            
            # Fallback to mock news
            return self._get_mock_news()
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error fetching market news: {str(e)}"
            }
    
    def _get_mock_news(self) -> Dict[str, Any]:
        """Get mock market news when API fails"""
        mock_articles = [
            {
                "title": "Indian Markets End Higher on IT Sector Gains",
                "source": "Financial Express",
                "url": "https://www.financialexpress.com",
                "summary": "Indian equity markets closed higher today led by gains in the IT sector, with Nifty IT index rising over 2%.",
                "datetime": datetime.utcnow().isoformat()
            },
            {
                "title": "HDFC Bank Reports Q3 Profit Growth",
                "source": "Economic Times",
                "url": "https://economictimes.indiatimes.com",
                "summary": "HDFC Bank reported a 15% year-on-year growth in net profit for the third quarter, driven by strong loan growth.",
                "datetime": datetime.utcnow().isoformat()
            },
            {
                "title": "Reliance Industries Announces Green Energy Investment",
                "source": "Business Standard",
                "url": "https://www.business-standard.com",
                "summary": "Reliance Industries announced a ₹75,000 crore investment in green energy projects over the next three years.",
                "datetime": datetime.utcnow().isoformat()
            },
            {
                "title": "IT Sector Shows Strong Performance in Q4",
                "source": "Mint",
                "url": "https://www.livemint.com",
                "summary": "Indian IT companies reported strong Q4 results, with TCS and Infosys beating analyst expectations.",
                "datetime": datetime.utcnow().isoformat()
            },
            {
                "title": "Rupee Strengthens Against US Dollar",
                "source": "Reuters",
                "url": "https://www.reuters.com",
                "summary": "The Indian rupee strengthened against the US dollar, supported by foreign fund inflows and positive market sentiment.",
                "datetime": datetime.utcnow().isoformat()
            }
        ]
        
        return {
            'success': True,
            'articles': mock_articles,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'Mock Data (Educational)'
        }
    
    async def test_news_service(self) -> bool:
        """Test the news service functionality"""
        try:
            # Test market news
            market_news = await self.fetch_market_news(limit=3)
            if not market_news:
                return False
            
            # Test news summarization
            summary_result = await self.summarize_news(market_news[:2], "What are the key trends?")
            return summary_result.get("success", False)
            
        except Exception as e:
            print(f"Error testing news service: {str(e)}")
            return False

# Singleton instance for reuse
news_service = NewsService()
