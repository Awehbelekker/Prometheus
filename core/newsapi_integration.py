"""
NewsAPI.org Integration for PROMETHEUS Trading Platform
Provides real-time news intelligence for trading decisions
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import aiohttp
import asyncio
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class NewsCategory(Enum):
    """News categories for filtering"""
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    GENERAL = "general"


class NewsSentiment(Enum):
    """News sentiment classification"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


@dataclass
class NewsArticle:
    """Represents a news article"""
    source: str
    author: Optional[str]
    title: str
    description: Optional[str]
    url: str
    published_at: datetime
    content: Optional[str]
    sentiment: Optional[NewsSentiment] = None
    relevance_score: float = 0.0
    symbols_mentioned: List[str] = None
    
    def __post_init__(self):
        if self.symbols_mentioned is None:
            self.symbols_mentioned = []


@dataclass
class NewsSignal:
    """Trading signal derived from news"""
    symbol: str
    signal_type: str  # "bullish", "bearish", "neutral"
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    articles: List[NewsArticle]
    timestamp: datetime
    reasoning: str


class NewsAPIIntegration:
    """
    NewsAPI.org integration for real-time news intelligence
    
    Features:
    - Real-time news fetching for specific symbols
    - Sentiment analysis of news articles
    - Trading signal generation from news
    - Breaking news alerts
    - News impact scoring
    """
    
    def __init__(self):
        self.api_key = os.getenv("NEWSAPI_KEY", "")
        self.base_url = "https://newsapi.org/v2"
        self.enabled = bool(self.api_key and self.api_key != "your_newsapi_key_here")
        
        # Rate limiting (100 requests/day for free tier)
        self.max_requests_per_day = 100
        self.requests_today = 0
        self.last_reset = datetime.now().date()
        
        # Cache for recent news
        self.news_cache: Dict[str, List[NewsArticle]] = {}
        self.cache_duration = timedelta(minutes=15)
        self.last_cache_update: Dict[str, datetime] = {}
        
        if self.enabled:
            logger.info("[CHECK] NewsAPI integration enabled")
            logger.info(f"   API Key: {self.api_key[:8]}...{self.api_key[-4:]}")
            logger.info(f"   Rate Limit: {self.max_requests_per_day} requests/day")
        else:
            logger.warning("[WARNING]️ NewsAPI integration disabled (no API key)")
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        # Reset counter if it's a new day
        today = datetime.now().date()
        if today > self.last_reset:
            self.requests_today = 0
            self.last_reset = today
        
        if self.requests_today >= self.max_requests_per_day:
            logger.warning(f"[WARNING]️ NewsAPI rate limit reached ({self.requests_today}/{self.max_requests_per_day})")
            return False
        
        return True
    
    def _increment_request_count(self):
        """Increment the request counter"""
        self.requests_today += 1
        logger.debug(f"NewsAPI requests today: {self.requests_today}/{self.max_requests_per_day}")
    
    async def get_symbol_news(
        self,
        symbol: str,
        hours_back: int = 24,
        max_articles: int = 10
    ) -> List[NewsArticle]:
        """
        Get recent news for a specific symbol
        
        Args:
            symbol: Stock symbol (e.g., "AAPL", "TSLA")
            hours_back: How many hours back to search
            max_articles: Maximum number of articles to return
            
        Returns:
            List of NewsArticle objects
        """
        if not self.enabled:
            return []
        
        # Check cache first
        cache_key = f"{symbol}_{hours_back}"
        if cache_key in self.news_cache:
            last_update = self.last_cache_update.get(cache_key)
            if last_update and datetime.now() - last_update < self.cache_duration:
                logger.debug(f"📰 Using cached news for {symbol}")
                return self.news_cache[cache_key][:max_articles]
        
        # Check rate limit
        if not self._check_rate_limit():
            # Return cached data if available, even if stale
            if cache_key in self.news_cache:
                logger.warning(f"[WARNING]️ Rate limit reached, returning stale cache for {symbol}")
                return self.news_cache[cache_key][:max_articles]
            return []
        
        try:
            # Build query
            company_names = self._get_company_name(symbol)
            query = f"{symbol} OR {company_names}"
            
            # Calculate date range
            from_date = (datetime.now() - timedelta(hours=hours_back)).isoformat()
            
            # Make API request
            url = f"{self.base_url}/everything"
            params = {
                "q": query,
                "from": from_date,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": max_articles,
                "apiKey": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    self._increment_request_count()
                    
                    if response.status == 200:
                        data = await response.json()
                        articles = self._parse_articles(data.get("articles", []), symbol)
                        
                        # Update cache
                        self.news_cache[cache_key] = articles
                        self.last_cache_update[cache_key] = datetime.now()
                        
                        logger.info(f"📰 Fetched {len(articles)} news articles for {symbol}")
                        return articles[:max_articles]
                    
                    elif response.status == 429:
                        logger.error("[ERROR] NewsAPI rate limit exceeded")
                        self.requests_today = self.max_requests_per_day  # Block further requests
                        return []
                    
                    else:
                        logger.error(f"[ERROR] NewsAPI error: {response.status}")
                        return []
        
        except Exception as e:
            logger.error(f"[ERROR] Error fetching news for {symbol}: {e}")
            return []
    
    async def get_breaking_news(
        self,
        category: NewsCategory = NewsCategory.BUSINESS,
        max_articles: int = 20
    ) -> List[NewsArticle]:
        """
        Get breaking news headlines
        
        Args:
            category: News category to fetch
            max_articles: Maximum number of articles
            
        Returns:
            List of NewsArticle objects
        """
        if not self.enabled or not self._check_rate_limit():
            return []
        
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                "category": category.value,
                "language": "en",
                "country": "us",
                "pageSize": max_articles,
                "apiKey": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    self._increment_request_count()
                    
                    if response.status == 200:
                        data = await response.json()
                        articles = self._parse_articles(data.get("articles", []))
                        logger.info(f"📰 Fetched {len(articles)} breaking news articles")
                        return articles
                    else:
                        logger.error(f"[ERROR] NewsAPI error: {response.status}")
                        return []
        
        except Exception as e:
            logger.error(f"[ERROR] Error fetching breaking news: {e}")
            return []
    
    def _parse_articles(self, raw_articles: List[Dict], symbol: Optional[str] = None) -> List[NewsArticle]:
        """Parse raw API response into NewsArticle objects"""
        articles = []
        
        for raw in raw_articles:
            try:
                article = NewsArticle(
                    source=raw.get("source", {}).get("name", "Unknown"),
                    author=raw.get("author"),
                    title=raw.get("title", ""),
                    description=raw.get("description"),
                    url=raw.get("url", ""),
                    published_at=datetime.fromisoformat(raw.get("publishedAt", "").replace("Z", "+00:00")),
                    content=raw.get("content"),
                    symbols_mentioned=[symbol] if symbol else []
                )
                
                # Analyze sentiment
                article.sentiment = self._analyze_sentiment(article)
                article.relevance_score = self._calculate_relevance(article, symbol)
                
                articles.append(article)
            
            except Exception as e:
                logger.debug(f"Error parsing article: {e}")
                continue
        
        return articles
    
    def _analyze_sentiment(self, article: NewsArticle) -> NewsSentiment:
        """Simple sentiment analysis based on keywords"""
        text = f"{article.title} {article.description or ''}".lower()
        
        # Positive keywords
        positive_words = ["surge", "gain", "profit", "growth", "bullish", "upgrade", "beat", "strong", "record", "high"]
        # Negative keywords
        negative_words = ["fall", "loss", "decline", "bearish", "downgrade", "miss", "weak", "crash", "low", "concern"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count + 1:
            return NewsSentiment.POSITIVE
        elif negative_count > positive_count + 1:
            return NewsSentiment.NEGATIVE
        else:
            return NewsSentiment.NEUTRAL
    
    def _calculate_relevance(self, article: NewsArticle, symbol: Optional[str]) -> float:
        """Calculate relevance score for an article"""
        if not symbol:
            return 0.5
        
        text = f"{article.title} {article.description or ''}".lower()
        symbol_lower = symbol.lower()
        
        # Check if symbol is mentioned
        if symbol_lower in text:
            return 0.9
        
        # Check if company name is mentioned
        company_name = self._get_company_name(symbol).lower()
        if company_name in text:
            return 0.8
        
        return 0.3
    
    def _get_company_name(self, symbol: str) -> str:
        """Get company name from symbol"""
        # Simple mapping for common symbols
        company_map = {
            "AAPL": "Apple",
            "MSFT": "Microsoft",
            "GOOGL": "Google",
            "AMZN": "Amazon",
            "TSLA": "Tesla",
            "NVDA": "Nvidia",
            "META": "Meta",
            "NFLX": "Netflix",
            "SPY": "S&P 500",
            "QQQ": "Nasdaq"
        }
        return company_map.get(symbol, symbol)
    
    async def generate_trading_signal(self, symbol: str) -> Optional[NewsSignal]:
        """
        Generate a trading signal based on recent news
        
        Args:
            symbol: Stock symbol
            
        Returns:
            NewsSignal object or None
        """
        articles = await self.get_symbol_news(symbol, hours_back=6, max_articles=10)
        
        if not articles:
            return None
        
        # Analyze sentiment distribution
        sentiment_scores = {
            NewsSentiment.VERY_POSITIVE: 2.0,
            NewsSentiment.POSITIVE: 1.0,
            NewsSentiment.NEUTRAL: 0.0,
            NewsSentiment.NEGATIVE: -1.0,
            NewsSentiment.VERY_NEGATIVE: -2.0
        }
        
        total_score = sum(sentiment_scores.get(a.sentiment, 0) * a.relevance_score for a in articles)
        avg_score = total_score / len(articles) if articles else 0
        
        # Determine signal type
        if avg_score > 0.5:
            signal_type = "bullish"
            strength = min(avg_score / 2.0, 1.0)
        elif avg_score < -0.5:
            signal_type = "bearish"
            strength = min(abs(avg_score) / 2.0, 1.0)
        else:
            signal_type = "neutral"
            strength = 0.3
        
        # Calculate confidence based on article count and recency
        confidence = min(len(articles) / 10.0, 1.0) * 0.7 + 0.3
        
        reasoning = f"Analyzed {len(articles)} articles. Avg sentiment: {avg_score:.2f}"
        
        return NewsSignal(
            symbol=symbol,
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            articles=articles,
            timestamp=datetime.now(),
            reasoning=reasoning
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "enabled": self.enabled,
            "requests_today": self.requests_today,
            "max_requests": self.max_requests_per_day,
            "remaining_requests": self.max_requests_per_day - self.requests_today,
            "cache_size": len(self.news_cache),
            "last_reset": self.last_reset.isoformat()
        }


# Global instance
_newsapi_instance: Optional[NewsAPIIntegration] = None


def get_newsapi() -> NewsAPIIntegration:
    """Get or create the global NewsAPI instance"""
    global _newsapi_instance
    if _newsapi_instance is None:
        _newsapi_instance = NewsAPIIntegration()
    return _newsapi_instance


# Example usage
async def test_newsapi():
    """Test the NewsAPI integration"""
    newsapi = get_newsapi()
    
    if not newsapi.enabled:
        print("[ERROR] NewsAPI not enabled (no API key)")
        return
    
    print("[CHECK] NewsAPI enabled")
    print(f"Status: {newsapi.get_status()}")
    
    # Test symbol news
    print("\n📰 Fetching news for AAPL...")
    articles = await newsapi.get_symbol_news("AAPL", hours_back=24, max_articles=5)
    for article in articles:
        print(f"  - {article.title} ({article.sentiment.value})")
    
    # Test trading signal
    print("\n📊 Generating trading signal for TSLA...")
    signal = await newsapi.generate_trading_signal("TSLA")
    if signal:
        print(f"  Signal: {signal.signal_type}")
        print(f"  Strength: {signal.strength:.2f}")
        print(f"  Confidence: {signal.confidence:.2f}")
        print(f"  Reasoning: {signal.reasoning}")


if __name__ == "__main__":
    asyncio.run(test_newsapi())

