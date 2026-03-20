"""
Simple Knowledge Loader
Mock financial education documents loader
"""

import json
from typing import List, Dict, Any
from datetime import datetime

class KnowledgeLoader:
    """
    Simple financial education documents loader
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
        Load financial education content (mock implementation)
        """
        try:
            # Return sample financial education content
            return self._get_sample_knowledge_content()
            
        except Exception as e:
            print(f"❌ Critical error loading financial education content: {str(e)}")
            return []
    
    def load_investing_guides(self) -> List[Dict[str, Any]]:
        """Load investing guides (mock implementation)"""
        try:
            return [
                {
                    'title': 'Stock Market Basics',
                    'content': 'The stock market is where investors buy and sell shares of publicly traded companies. It provides a platform for companies to raise capital and for investors to potentially earn returns on their investments.',
                    'url': 'https://www.investopedia.com',
                    'word_count': 45,
                    'published': '2024-01-01',
                    'categories': ['investing', 'stocks', 'basics']
                },
                {
                    'title': 'Understanding Mutual Funds',
                    'content': 'Mutual funds pool money from many investors to purchase a diversified portfolio of stocks, bonds, or other securities. They offer professional management and instant diversification.',
                    'url': 'https://www.investopedia.com',
                    'word_count': 42,
                    'published': '2024-01-01',
                    'categories': ['investing', 'mutual funds', 'basics']
                }
            ]
                
        except Exception as e:
            print(f"❌ Error loading investing guides: {str(e)}")
            return []
    
    def load_mutual_fund_data(self) -> List[Dict[str, Any]]:
        """Load mutual fund data (mock implementation)"""
        try:
            return [
                {"symbol": "VFIAX", "name": "Vanguard 500 Index Admiral", "category": "Large Cap", "expense_ratio": 0.04},
                {"symbol": "FXAIX", "name": "Fidelity 500 Index", "category": "Large Cap", "expense_ratio": 0.015},
                {"symbol": "VTSAX", "name": "Vanguard Total Stock Market Admiral", "category": "Total Market", "expense_ratio": 0.05}
            ]
                
        except Exception as e:
            print(f"❌ Error loading mutual fund data: {str(e)}")
            return []
    
    def load_etf_data(self) -> List[Dict[str, Any]]:
        """Load ETF data (mock implementation)"""
        try:
            return [
                {"symbol": "SPY", "name": "SPDR S&P 500 ETF", "category": "Large Cap", "expense_ratio": 0.09},
                {"symbol": "QQQ", "name": "Invesco QQQ Trust", "category": "Technology", "expense_ratio": 0.20},
                {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF", "category": "Total Market", "expense_ratio": 0.03}
            ]
                
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
                "url": "https://www.investopedia.com/terms/d/diversification.asp",
                "category": "investing_basics"
            },
            {
                "id": "mutual_funds_guide",
                "title": "Understanding Mutual Funds",
                "content": "A mutual fund is a professionally managed investment fund that pools money from many investors to purchase securities. These funds may invest in stocks, bonds, money market instruments, or other assets. Mutual funds offer small investors access to professionally managed, diversified portfolios of equities, bonds and other securities, which would be quite difficult to create with a small amount of capital.",
                "metadata": {"category": "investment_products", "difficulty": "intermediate"},
                "url": "https://www.investopedia.com/terms/m/mutualfund.asp",
                "category": "investment_products"
            },
            {
                "id": "etf_basics",
                "title": "Exchange-Traded Funds (ETFs) Explained",
                "content": "An exchange-traded fund (ETF) is a type of investment fund and exchange-traded product, with assets that are traded on a stock exchange. ETFs are similar in many ways to mutual funds, except that ETFs are bought and sold throughout the day on stock exchanges while mutual funds are bought and sold based on their price at day's end. An ETF is a marketable security that tracks an index, a commodity, bonds, or a basket of assets like an index fund.",
                "metadata": {"category": "investment_products", "difficulty": "intermediate"},
                "url": "https://www.investopedia.com/terms/e/etf.asp",
                "category": "investment_products"
            },
            {
                "id": "risk_management",
                "title": "Investment Risk Management",
                "content": "Risk management is the process of identification, analysis and acceptance or mitigation of uncertainty in investment decisions. Risk is inherent in all investing, but the degree of risk varies between different types of investments. Risk management in finance involves identifying, analyzing, and addressing potential risks to minimize their negative impact on investment returns.",
                "metadata": {"category": "risk_management", "difficulty": "advanced"},
                "url": "https://www.investopedia.com/terms/r/riskmanagement.asp",
                "category": "risk_management"
            },
            {
                "id": "portfolio_allocation",
                "title": "Portfolio Allocation Strategies",
                "content": "Portfolio allocation is the process of deciding how to distribute an investment portfolio across different asset classes, such as stocks, bonds, and cash. The allocation should be based on the investor's goals, risk tolerance, and investment horizon. Common allocation strategies include strategic allocation, tactical allocation, and dynamic allocation.",
                "metadata": {"category": "portfolio_management", "difficulty": "intermediate"},
                "url": "https://www.investopedia.com/terms/p/portfolioallocation.asp",
                "category": "portfolio_management"
            },
            {
                "id": "stock_valuation",
                "title": "Understanding Stock Valuation",
                "content": "Stock valuation is the process of determining the intrinsic value of a company's stock. Various methods exist for stock valuation, including discounted cash flow analysis, price-to-earnings ratio analysis, and dividend discount models. Understanding stock valuation helps investors make informed decisions about buying, holding, or selling stocks.",
                "metadata": {"category": "stock_analysis", "difficulty": "intermediate"},
                "url": "https://www.investopedia.com/terms/s/stockvaluation.asp",
                "category": "stock_analysis"
            },
            {
                "id": "market_cycles",
                "title": "Understanding Market Cycles",
                "content": "Market cycles refer to the periodic fluctuations in financial markets, characterized by periods of expansion (bull markets) and contraction (bear markets). Understanding market cycles helps investors recognize patterns and make more informed investment decisions. Market cycles can be influenced by economic factors, investor sentiment, and geopolitical events.",
                "metadata": {"category": "market_analysis", "difficulty": "advanced"},
                "url": "https://www.investopedia.com/terms/m/marketcycles.asp",
                "category": "market_analysis"
            },
            {
                "id": "compound_interest",
                "title": "The Power of Compound Interest",
                "content": "Compound interest is the addition of interest to the principal sum of a loan or deposit, or in other words, interest on interest. It is the result of reinvesting interest, rather than paying it out, so that interest in the next period is then earned on the principal sum plus previously accumulated interest. Compound interest is a powerful force in wealth building over time.",
                "metadata": {"category": "investing_basics", "difficulty": "beginner"},
                "url": "https://www.investopedia.com/terms/c/compoundinterest.asp",
                "category": "investing_basics"
            }
        ]

# Singleton instance for reuse
knowledge_loader = KnowledgeLoader()
