"""
REDDIT DATA SOURCE
==================

Reddit social sentiment data source for trading intelligence.

Monitors:
- r/wallstreetbets - Retail trading sentiment
- r/stocks - General stock discussion
- r/cryptocurrency - Crypto sentiment
- r/investing - Investment discussion

Features:
- Real-time post monitoring
- Sentiment analysis
- Mention tracking
- Trending stock detection
- Upvote/comment scoring

Author: PROMETHEUS AI Team
Date: October 10, 2025
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
import re
from enum import Enum

logger = logging.getLogger(__name__)

class RedditSentiment(Enum):
    VERY_BULLISH = "very_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    VERY_BEARISH = "very_bearish"

@dataclass
class RedditPost:
    """Reddit post data"""
    post_id: str
    subreddit: str
    title: str
    body: str
    author: str
    score: int
    num_comments: int
    created_utc: datetime
    url: str
    symbols_mentioned: List[str]
    sentiment: RedditSentiment
    sentiment_score: float  # -1 to 1

class RedditDataSource:
    """
    Reddit data source for social sentiment analysis
    """
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        import os
        # Load from environment if not provided
        self.client_id = client_id or os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = os.getenv('REDDIT_USER_AGENT', 'PROMETHEUS Trading Bot 1.0')
        self.access_token = None
        self._credentials_logged = False
        
        # Log credential status once
        if self.client_id and self.client_secret:
            logger.info("✅ Reddit API credentials loaded from environment")
        else:
            logger.warning("⚠️ Reddit API credentials not found - using mock data")
        
        # Subreddits to monitor
        self.subreddits = [
            'wallstreetbets',
            'stocks',
            'cryptocurrency',
            'investing',
            'StockMarket',
            'CryptoCurrency',
            'Bitcoin',
            'ethereum'
        ]
        
        # Sentiment keywords
        self.bullish_keywords = [
            'moon', 'rocket', 'bullish', 'buy', 'calls', 'long', 'pump',
            'breakout', 'rally', 'surge', 'gains', 'profit', 'tendies',
            'diamond hands', 'hold', 'hodl', 'to the moon', '🚀', '📈'
        ]
        
        self.bearish_keywords = [
            'crash', 'dump', 'bearish', 'sell', 'puts', 'short', 'drop',
            'collapse', 'tank', 'plunge', 'loss', 'rekt', 'paper hands',
            'sell off', 'correction', '📉', '💩'
        ]
        
        # Stock symbol pattern
        self.symbol_pattern = re.compile(r'\$([A-Z]{1,5})\b|\b([A-Z]{2,5})\b')
        
        logger.info("📱 Reddit Data Source initialized")
    
    async def get_access_token(self) -> bool:
        """Get Reddit API access token"""
        try:
            if not self.client_id or not self.client_secret:
                logger.warning("[WARNING]️ Reddit API credentials not provided - using mock data")
                return False
            
            # Reddit OAuth2 token endpoint
            auth_url = "https://www.reddit.com/api/v1/access_token"
            
            async with aiohttp.ClientSession() as session:
                auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
                data = {'grant_type': 'client_credentials'}
                headers = {'User-Agent': self.user_agent}
                
                async with session.post(auth_url, auth=auth, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.access_token = result.get('access_token')
                        logger.info("[CHECK] Reddit API access token obtained")
                        return True
                    else:
                        logger.error(f"[ERROR] Failed to get Reddit access token: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error getting Reddit access token: {e}")
            return False
    
    async def fetch_subreddit_posts(self, subreddit: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Fetch recent posts from a subreddit"""
        try:
            if not self.access_token:
                # Use mock data if no API access
                return self._generate_mock_posts(subreddit, limit)
            
            url = f"https://oauth.reddit.com/r/{subreddit}/hot"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'User-Agent': 'PROMETHEUS Trading Bot 1.0'
            }
            params = {'limit': limit}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = data.get('data', {}).get('children', [])
                        return [post['data'] for post in posts]
                    else:
                        logger.warning(f"[WARNING]️ Reddit API error: {response.status}")
                        return self._generate_mock_posts(subreddit, limit)
                        
        except Exception as e:
            logger.error(f"Error fetching Reddit posts: {e}")
            return self._generate_mock_posts(subreddit, limit)
    
    def _generate_mock_posts(self, subreddit: str, limit: int) -> List[Dict[str, Any]]:
        """Generate mock Reddit posts for testing"""
        import random
        
        mock_titles = [
            "AAPL to the moon! 🚀 Earnings beat expectations",
            "TSLA calls printing! Diamond hands 💎",
            "BTC breaking out! New ATH incoming",
            "NVDA looking bullish, buying more calls",
            "Market crash incoming? SPY puts loaded",
            "ETH merge successful, price surging",
            "MSFT strong buy, AI revolution",
            "GME short squeeze 2.0?",
            "Crypto winter is over, time to buy",
            "Tech stocks oversold, time to load up",
            "AMD crushing it with new chips! 🔥",
            "META metaverse play looking good",
            "NFLX subscriber growth strong",
            "CRM cloud dominance continues",
            "ADBE creative suite AI upgrade",
            "PLTR government contracts booming",
            "RBLX virtual economy growing",
            "COIN crypto exchange volume up",
            "SOL Solana ecosystem expanding",
            "AVAX avalanche momentum",
            "ADA Cardano smart contracts live",
            "DOGE to the moon! Much wow 🐕",
            "GOOGL AI search dominance",
            "AMZN AWS growth continues"
        ]
        
        posts = []
        for i in range(min(limit, len(mock_titles))):
            posts.append({
                'id': f'mock_{i}',
                'subreddit': subreddit,
                'title': mock_titles[i],
                'selftext': f'Mock post body for {mock_titles[i]}',
                'author': f'user_{i}',
                'score': random.randint(10, 5000),
                'num_comments': random.randint(5, 500),
                'created_utc': (datetime.now() - timedelta(hours=random.randint(1, 24))).timestamp(),
                'url': f'https://reddit.com/r/{subreddit}/comments/mock_{i}'
            })
        
        return posts
    
    def extract_symbols(self, text: str) -> List[str]:
        """Extract stock symbols from text"""
        symbols = set()
        
        # Find all potential symbols
        matches = self.symbol_pattern.findall(text.upper())
        for match in matches:
            symbol = match[0] if match[0] else match[1]
            # Filter out common words that look like symbols
            if symbol and len(symbol) >= 2 and symbol not in ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE']:
                symbols.add(symbol)
        
        return list(symbols)
    
    def analyze_sentiment(self, text: str) -> tuple[RedditSentiment, float]:
        """Analyze sentiment of text"""
        text_lower = text.lower()
        
        # Count bullish and bearish keywords
        bullish_count = sum(1 for keyword in self.bullish_keywords if keyword.lower() in text_lower)
        bearish_count = sum(1 for keyword in self.bearish_keywords if keyword.lower() in text_lower)
        
        # Calculate sentiment score
        total_keywords = bullish_count + bearish_count
        if total_keywords == 0:
            return RedditSentiment.NEUTRAL, 0.0
        
        sentiment_score = (bullish_count - bearish_count) / total_keywords
        
        # Classify sentiment
        if sentiment_score > 0.5:
            sentiment = RedditSentiment.VERY_BULLISH
        elif sentiment_score > 0.2:
            sentiment = RedditSentiment.BULLISH
        elif sentiment_score < -0.5:
            sentiment = RedditSentiment.VERY_BEARISH
        elif sentiment_score < -0.2:
            sentiment = RedditSentiment.BEARISH
        else:
            sentiment = RedditSentiment.NEUTRAL
        
        return sentiment, sentiment_score
    
    async def get_trading_signals(self, symbols: List[str]) -> Dict[str, Any]:
        """Get trading signals from Reddit for specific symbols"""
        try:
            all_posts = []
            
            # Fetch posts from all subreddits
            for subreddit in self.subreddits[:3]:  # Limit to top 3 for performance
                posts = await self.fetch_subreddit_posts(subreddit, limit=10)
                all_posts.extend(posts)
            
            # Analyze posts for each symbol
            symbol_signals = {}
            
            for symbol in symbols:
                mentions = []
                total_sentiment = 0.0
                total_score = 0
                
                for post in all_posts:
                    text = f"{post.get('title', '')} {post.get('selftext', '')}"
                    post_symbols = self.extract_symbols(text)
                    
                    if symbol in post_symbols:
                        sentiment, sentiment_score = self.analyze_sentiment(text)
                        mentions.append({
                            'title': post.get('title'),
                            'score': post.get('score', 0),
                            'sentiment': sentiment.value,
                            'sentiment_score': sentiment_score,
                            'subreddit': post.get('subreddit'),
                            'url': post.get('url')
                        })
                        total_sentiment += sentiment_score * post.get('score', 1)
                        total_score += post.get('score', 1)
                
                if mentions:
                    avg_sentiment = total_sentiment / total_score if total_score > 0 else 0.0
                    
                    symbol_signals[symbol] = {
                        'mention_count': len(mentions),
                        'avg_sentiment': avg_sentiment,
                        'total_engagement': total_score,
                        'top_mentions': sorted(mentions, key=lambda x: x['score'], reverse=True)[:3],
                        'signal_strength': min(1.0, len(mentions) / 10),  # Normalize to 0-1
                        'confidence': min(1.0, total_score / 1000)  # Normalize to 0-1
                    }
            
            return symbol_signals
            
        except Exception as e:
            logger.error(f"Error getting Reddit trading signals: {e}")
            return {}
    
    async def get_trending_symbols(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending symbols from Reddit"""
        try:
            all_posts = []
            
            # Fetch posts from all subreddits
            for subreddit in self.subreddits[:3]:
                posts = await self.fetch_subreddit_posts(subreddit, limit=25)
                all_posts.extend(posts)
            
            # Count symbol mentions
            symbol_mentions = {}
            
            for post in all_posts:
                text = f"{post.get('title', '')} {post.get('selftext', '')}"
                symbols = self.extract_symbols(text)
                sentiment, sentiment_score = self.analyze_sentiment(text)
                score = post.get('score', 0)
                
                for symbol in symbols:
                    if symbol not in symbol_mentions:
                        symbol_mentions[symbol] = {
                            'symbol': symbol,
                            'mention_count': 0,
                            'total_score': 0,
                            'total_sentiment': 0.0,
                            'posts': []
                        }
                    
                    symbol_mentions[symbol]['mention_count'] += 1
                    symbol_mentions[symbol]['total_score'] += score
                    symbol_mentions[symbol]['total_sentiment'] += sentiment_score * score
                    symbol_mentions[symbol]['posts'].append({
                        'title': post.get('title'),
                        'score': score,
                        'subreddit': post.get('subreddit')
                    })
            
            # Calculate trending score and sort
            trending = []
            for symbol, data in symbol_mentions.items():
                avg_sentiment = data['total_sentiment'] / data['total_score'] if data['total_score'] > 0 else 0.0
                trending_score = data['mention_count'] * data['total_score'] * (1 + abs(avg_sentiment))
                
                trending.append({
                    'symbol': symbol,
                    'mention_count': data['mention_count'],
                    'avg_sentiment': avg_sentiment,
                    'total_engagement': data['total_score'],
                    'trending_score': trending_score,
                    'top_posts': sorted(data['posts'], key=lambda x: x['score'], reverse=True)[:3]
                })
            
            # Sort by trending score and return top N
            trending.sort(key=lambda x: x['trending_score'], reverse=True)
            return trending[:limit]
            
        except Exception as e:
            logger.error(f"Error getting trending symbols: {e}")
            return []

