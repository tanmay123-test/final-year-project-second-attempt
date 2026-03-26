"""
Knowledge Loader
Financial education documents loader for FAISS vector database
"""

import os
import json
import re
from typing import List, Dict, Any
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Any

class KnowledgeLoader:
    """
    Financial education documents loader for FAISS vector database
    """
    
    def __init__(self):
        self.sources = [
            {
                "name": "Investopedia",
                "base_url": "https://www.investopedia.com",
                "categories": ["investing", "stocks", "mutual funds", "ETFs", "retirement", "risk management"],
                "content_type": "educational"
            },
            {
                "name": "SEC",
                "base_url": "https://www.sec.gov",
                "categories": ["markets", "regulations", "investing", "trading", "risk management"],
                "content_type": "official"
            },
            {
                "name": "Morning Brew",
                "base_url": "https://www.morningbrew.com",
                "categories": "markets", "investing", "personal finance", "retirement"],
                "content_type": "educational"
            },
            {
                "name": "Investopedia",
                "base_url": "https://www.investopedia.com",
                "categories": ["investing", "stocks", "mutual funds", "ETFs", "retirement"],
                "content_type": "educational"
            }
        ]
    
    def load_financial_education_content(self) -> List[Dict[str, Any]]:
        """
        Load financial education content from various sources
        """
        try:
            all_content = []
            
            for source in self.sources:
                print(f"  Loading from {source['name']}...")
                
                try:
                    # Fetch main content
                    response = requests.get(source['base_url'], timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        articles = soup.find_all('article')
                        
                        for article in articles:
                            title = article.find('h2').text.strip()
                            content = article.find('div', class_='post-content').text.strip()
                            
                            # Extract main content
                            content = content if content else ""
                            
                            all_content.append({
                                'source': source['name'],
                                'title': title,
                                'content': content,
                                'url': source['base_url'] + article.find('a', href='href'),
                                'categories': source['categories'],
                                'content_type': source['content_type'],
                                'word_count': len(content.split()),
                                'published': article.find('time').text.strip() if article.find('time') else "Unknown"
                            })
                        
                    except Exception as e:
                        print(f"  Error loading from {source['name']}: {str(e)}")
                    continue
                
                except Exception as e:
                    print(f"  Critical error loading {source['name']}: {str(e)}")
                    continue
            
            return all_content
            
        except Exception as e:
            print(f"  Critical error loading financial education content: {str(e)}")
            return []
    
    def load_investing_guides() -> List[Dict[str, Any]]:
        """Load investing guides"""
        try:
            response = requests.get("https://www.investopedia/a-z/guides/stock-investing-guides", timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('article')
                
                guides = []
                for article in articles:
                    title = article.find('h2').text.strip()
                    content = article.find('div', class_='post-content').text.strip()
                    
                    guides.append({
                        'title': title,
                        'content': content,
                        'url': response.url,
                        'word_count': len(content.split()),
                        'published': article.find('time').text.strip() if article.find('time') else "Unknown",
                        'categories': self._extract_categories(article),
                        'word_count': len(content.split())
                    })
                
                return guides
                
            except Exception as e:
                print(f"  Error loading investing guides: {str(e)}")
                return []
    
    def load_mutual_fund_data() -> List[Dict[str, Any]]:
        """Load mutual fund data"""
        try:
            response = requests.get("https://api.mutualfunds.com/v1/mutual-funds", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
                
            except Exception as e:
                print(f"  Error loading mutual fund data: {str(e)}")
                return []
    
    def _extract_categories(self, article) -> List[str]:
        """Extract categories from article"""
        try:
            categories = article.find_all('div', class_='categories')
            if categories:
                return [tag.text.strip() for tag in categories]
            return []
        except:
            return []
    
    def load_etf_data() -> List[Dict[str, Any]]:
        """Load ETF data"""
        try:
            response = requests.get("https://api.ETFdb.com/v1/etf/list", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
                
            except Exception as e:
                print(f"  Error loading ETF data: {str(e)}")
                return []
    
    def load_stock_data() -> List[Dict[str, Any]]:
        """Load sample stock data for testing"""
        return [
            {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "price": 190.50},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "price": 380.50},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology", "price": 2800.50},
            {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Cyclical", "price": 245.30"},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial", "price": 150.00},
            {"symbol": "BRK.B", "name": "Berkshire Hathaway", "sector": "Financial Services", "price": 350000.00}
        ]
    
    def get_supported_companies() -> List[str]:
        """Get list of supported companies for testing"""
        return [
            "AAPL - Apple Inc. (Technology)",
            "MSFT - Microsoft Corporation (Technology)",
            "GOOGL - Alphabet Inc. (Technology)",
            "TSLA - Tesla Inc. (Consumer Cyclical)",
            "JPM - JPMorgan Chase & Co. (Financial)",
            "BRK.B - Berkshire Hathaway (Financial Services)",
            "JNJ - Johnson & Johnson (Healthcare)",
            "PG - Procter & Gamble (Consumer Staples)",
            "KO - Coca-Cola (Beverages)", 
            "PEP - PepsiCo (Beverages)",
            "WMT - Walmart (Retail)",
            "HD - Home Depot (Retail)",
            "LOWE - Lowe's Companies (Retail)",
            "DIS - Disney (Entertainment)",
            "NFLX - NFLX (Entertainment)",
            "SP500 - S&P 500 Index)",
            "DJI - Dow Jones Industrial Average"
        ]
    
    def get_sample_queries() -> List[str]:
        """Get sample portfolio queries"""
        return [
            "Analyze my portfolio",
            "What is diversification?",
            "What is my portfolio performance?",
            "Compare Apple vs Microsoft",
            "Search for technology companies",
            "What is a good PE ratio?",
            "How does diversification work?",
            "Explain portfolio concentration risk",
            "What are the best performing stocks?"
            "How to optimize portfolio returns?"
            "What is sector allocation?"
            "Compare growth vs value stocks"
        ]
    
    def get_financial_keywords() -> List[str]:
        """Get financial keywords for query detection"""
        return [
            "portfolio", "investments", "stocks", "shares", "equity", "diversification",
            "portfolio", "returns", "profit", "loss", "risk",
            "analysis", "fundamentals", "valuation",
            "price", "trading", "investing", "investment", "portfolio",
            "market", "sector", "industry", "index", "etf", "nasdaq",
            "nyse", "dow", "sp500", "s&p500", "russell"
        ]

# Singleton instance for reuse
vector_store = VectorStore()
knowledge_loader = KnowledgeLoader()
