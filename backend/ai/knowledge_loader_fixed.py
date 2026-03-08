"""
Knowledge Loader
Financial education documents loader for FAISS vector database
"""

import os
import json
import re
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
import requests

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
                "categories": ["markets", "investing", "personal finance", "retirement"],
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
                print(f"📚 Loading from {source['name']}...")
                
                try:
                    # Fetch main content
                    response = requests.get(source['base_url'], timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        articles = soup.find_all('article')
                        
                        for article in articles:
                            title_tag = article.find('h2')
                            title = title_tag.text.strip() if title_tag else ""
                            
                            content_tag = article.find('div', class_='post-content')
                            content = content_tag.text.strip() if content_tag else ""
                            
                            # Extract main content
                            content = content if content else ""
                            
                            all_content.append({
                                'source': source['name'],
                                'title': title,
                                'content': content,
                                'url': source['base_url'],
                                'categories': source['categories'],
                                'content_type': source['content_type'],
                                'word_count': len(content.split()),
                                'published': "Unknown"
                            })
                        
                    else:
                        print(f"❌ Failed to fetch from {source['name']}: {response.status_code}")
                
                except Exception as e:
                    print(f"❌ Error loading from {source['name']}: {str(e)}")
                    continue
            
            return all_content
            
        except Exception as e:
            print(f"❌ Critical error loading financial education content: {str(e)}")
            return []
    
    def load_investing_guides(self) -> List[Dict[str, Any]]:
        """Load investing guides"""
        try:
            response = requests.get("https://www.investopedia/a-z/guides/stock-investing-guides", timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('article')
                
                guides = []
                for article in articles:
                    title_tag = article.find('h2')
                    title = title_tag.text.strip() if title_tag else ""
                    
                    content_tag = article.find('div', class_='post-content')
                    content = content_tag.text.strip() if content_tag else ""
                    
                    guides.append({
                        'title': title,
                        'content': content,
                        'url': "https://www.investopedia.com",
                        'word_count': len(content.split()),
                        'published': "Unknown",
                        'categories': self._extract_categories(article)
                    })
                
                return guides
                
        except Exception as e:
            print(f"❌ Error loading investing guides: {str(e)}")
            return []
    
    def load_mutual_fund_data(self) -> List[Dict[str, Any]]:
        """Load mutual fund data"""
        try:
            response = requests.get("https://api.mutualfunds.com/v1/mutual-funds", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error loading mutual fund data: {str(e)}")
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
    
    def load_etf_data(self) -> List[Dict[str, Any]]:
        """Load ETF data"""
        try:
            response = requests.get("https://api.ETFdb.com/v1/etf/list", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error loading ETF data: {str(e)}")
            return []
    
    def load_stock_data(self) -> List[Dict[str, Any]]:
        """Load sample stock data for testing"""
        return [
            {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "price": 190.50},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "price": 380.50},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology", "price": 2800.50},
            {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Cyclical", "price": 245.30},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial", "price": 150.00},
            {"symbol": "BRK.B", "name": "Berkshire Hathaway", "sector": "Financial Services", "price": 350000.00}
        ]
    
    def get_supported_companies(self) -> List[str]:
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
            "NFLX - Netflix (Entertainment)",
            "SP500 - S&P 500 Index",
            "DJI - Dow Jones Industrial Average"
        ]
    
    def get_sample_queries(self) -> List[str]:
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
            "What are the best performing stocks?",
            "How to optimize portfolio returns?",
            "What is sector allocation?",
            "Compare growth vs value stocks"
        ]
    
    def get_financial_keywords(self) -> List[str]:
        """Get financial keywords for query detection"""
        return [
            "portfolio", "investments", "stocks", "shares", "equity", "diversification",
            "returns", "profit", "loss", "risk", "analysis", "fundamentals", "valuation",
            "price", "trading", "investing", "investment", "market", "sector", "industry",
            "index", "etf", "nasdaq", "nyse", "dow", "sp500", "s&p500", "russell"
        ]

# Singleton instance for reuse
knowledge_loader = KnowledgeLoader()
