"""
PROMETHEUS Twitter/X Data Source
Real-time social sentiment analysis using Twitter API v2
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import tweepy
from textblob import TextBlob

logger = logging.getLogger(__name__)


class TwitterDataSource:
    """Real-time Twitter sentiment analysis using Twitter API v2"""
    
    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_secret = os.getenv('TWITTER_ACCESS_SECRET')

        self.client = None
        self.api = None
        self.enabled = True  # ENABLED - will lazy initialize on first use
        self._initialized = False

        # BEST PRACTICE: Don't initialize during module load - use lazy initialization
        # This prevents blocking server startup if Twitter API has rate limits
        # Will auto-initialize on first use with proper timeout handling
    
    def _initialize_client(self):
        """
        Initialize Twitter API client (lazy initialization)
        BEST PRACTICE: Only initialize when first needed, with timeout to prevent blocking
        """
        if self._initialized:
            return  # Already initialized

        self._initialized = True  # Mark as initialized even if it fails

        try:
            if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
                logger.warning("[WARNING]️ Twitter API credentials not configured - using fallback mode")
                return

            # Initialize Twitter API v1.1 (primary - works with Free tier)
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(self.access_token, self.access_secret)
            # BEST PRACTICE: Disable wait_on_rate_limit during initialization to prevent blocking
            self.api = tweepy.API(auth, wait_on_rate_limit=False)

            # Test connection with v1.1 API (with timeout)
            try:
                user = self.api.verify_credentials()
                self.enabled = True
                logger.info(f"[CHECK] Twitter API v1.1 connected successfully as @{user.screen_name}")
            except Exception as e:
                logger.warning(f"[WARNING]️ Twitter API v1.1 verification failed (will retry on first use): {e}")
                # Don't fail completely - just mark as not enabled yet
                self.enabled = False
                return

            # Try to initialize v2 client (optional, for enhanced features)
            try:
                self.client = tweepy.Client(
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_secret,
                    wait_on_rate_limit=False  # Don't block on rate limits during init
                )
                # Test v2 API (with timeout)
                try:
                    self.client.get_me()
                    logger.info("[CHECK] Twitter API v2 also available")
                except Exception as e:
                    logger.warning(f"[WARNING]️ Twitter API v2 verification failed: {e}")
                    self.client = None
            except Exception as e:
                logger.warning(f"[WARNING]️ Twitter API v2 not available (using v1.1 only): {e}")
                self.client = None

        except Exception as e:
            logger.error(f"[ERROR] Twitter API initialization failed: {e}")
            self.enabled = False
    
    def get_sentiment_data(self, symbols: List[str] = None, keywords: List[str] = None) -> Dict:
        """
        Get real-time sentiment data from Twitter

        Args:
            symbols: List of stock symbols to track (e.g., ['AAPL', 'TSLA'])
            keywords: Additional keywords to track (e.g., ['bitcoin', 'fed'])

        Returns:
            Dictionary with sentiment analysis results
        """
        # Lazy initialization on first use
        if not self._initialized:
            self._initialize_client()

        if not self.enabled:
            return self._get_fallback_data(symbols, keywords)
        
        try:
            # Build search queries
            queries = []
            
            if symbols:
                for symbol in symbols:
                    queries.append(f"${symbol}")
                    queries.append(symbol)
            
            if keywords:
                queries.extend(keywords)
            
            if not queries:
                queries = ['$SPY', '$QQQ', 'stock market', 'bitcoin', 'crypto']
            
            # Collect sentiment data
            sentiment_results = {}
            
            for query in queries[:10]:  # Limit to 10 queries to avoid rate limits
                sentiment_results[query] = self._analyze_query(query)
            
            # Aggregate results
            aggregated = self._aggregate_sentiment(sentiment_results)
            
            logger.info(f"[CHECK] Twitter sentiment analysis complete: {len(sentiment_results)} queries analyzed")
            return aggregated
            
        except Exception as e:
            logger.error(f"[ERROR] Twitter sentiment analysis error: {e}")
            return self._get_fallback_data(symbols, keywords)
    
    def _analyze_query(self, query: str, max_tweets: int = 100) -> Dict:
        """Analyze sentiment for a specific query"""
        try:
            # Check if API is initialized
            if not self.api and not self.client:
                # No Twitter API configured - return empty sentiment silently
                return self._empty_sentiment()
            
            # Try v2 API first (if available)
            if self.client:
                try:
                    tweets = self.client.search_recent_tweets(
                        query=f"{query} -is:retweet lang:en",
                        max_results=min(max_tweets, 100),
                        tweet_fields=['created_at', 'public_metrics', 'author_id']
                    )

                    if tweets.data:
                        return self._analyze_tweets_v2(query, tweets.data)
                except Exception as e:
                    logger.debug(f"v2 API failed for '{query}', falling back to v1.1: {e}")

            # Fall back to v1.1 API (works with Free tier)
            if not self.api:
                return self._empty_sentiment()
                
            tweets = self.api.search_tweets(
                q=f"{query} -filter:retweets lang:en",
                count=min(max_tweets, 100),
                result_type='recent',
                tweet_mode='extended'
            )

            if not tweets:
                return self._empty_sentiment()

            # Analyze sentiment
            sentiments = []
            total_engagement = 0

            for tweet in tweets:
                # Sentiment analysis using TextBlob
                text = tweet.full_text if hasattr(tweet, 'full_text') else tweet.text
                analysis = TextBlob(text)
                sentiment_score = analysis.sentiment.polarity  # -1 to 1

                # Weight by engagement
                engagement = (
                    tweet.favorite_count * 1 +
                    tweet.retweet_count * 2
                )

                sentiments.append({
                    'score': sentiment_score,
                    'engagement': engagement
                })
                total_engagement += engagement

            # Calculate weighted sentiment
            if total_engagement > 0:
                weighted_sentiment = sum(
                    s['score'] * s['engagement'] for s in sentiments
                ) / total_engagement
            else:
                weighted_sentiment = sum(s['score'] for s in sentiments) / len(sentiments)

            # Classify sentiment
            if weighted_sentiment > 0.2:
                sentiment_label = "bullish"
            elif weighted_sentiment < -0.2:
                sentiment_label = "bearish"
            else:
                sentiment_label = "neutral"

            return {
                'query': query,
                'sentiment_score': weighted_sentiment,
                'sentiment_label': sentiment_label,
                'tweet_count': len(tweets),
                'total_engagement': total_engagement,
                'confidence': min(len(tweets) / 100, 1.0),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"[ERROR] Error analyzing query '{query}': {e}")
            return self._empty_sentiment()

    def _analyze_tweets_v2(self, query: str, tweets: list) -> Dict:
        """Analyze tweets from v2 API"""
        sentiments = []
        total_engagement = 0

        for tweet in tweets:
            # Sentiment analysis using TextBlob
            analysis = TextBlob(tweet.text)
            sentiment_score = analysis.sentiment.polarity

            # Weight by engagement
            metrics = tweet.public_metrics
            engagement = (
                metrics['like_count'] * 1 +
                metrics['retweet_count'] * 2 +
                metrics['reply_count'] * 1.5 +
                metrics['quote_count'] * 2
            )

            sentiments.append({
                'score': sentiment_score,
                'engagement': engagement
            })
            total_engagement += engagement

        # Calculate weighted sentiment
        if total_engagement > 0:
            weighted_sentiment = sum(
                s['score'] * s['engagement'] for s in sentiments
            ) / total_engagement
        else:
            weighted_sentiment = sum(s['score'] for s in sentiments) / len(sentiments)

        # Classify sentiment
        if weighted_sentiment > 0.2:
            sentiment_label = "bullish"
        elif weighted_sentiment < -0.2:
            sentiment_label = "bearish"
        else:
            sentiment_label = "neutral"

        return {
            'query': query,
            'sentiment_score': weighted_sentiment,
            'sentiment_label': sentiment_label,
            'tweet_count': len(tweets),
            'total_engagement': total_engagement,
            'confidence': min(len(tweets) / 100, 1.0),
            'timestamp': datetime.now().isoformat()
        }
    
    def _aggregate_sentiment(self, sentiment_results: Dict) -> Dict:
        """Aggregate sentiment results across all queries"""
        if not sentiment_results:
            return self._empty_sentiment()
        
        # Calculate overall sentiment
        total_score = 0
        total_weight = 0
        total_tweets = 0
        total_engagement = 0
        
        for query, data in sentiment_results.items():
            weight = data.get('confidence', 0.5)
            total_score += data.get('sentiment_score', 0) * weight
            total_weight += weight
            total_tweets += data.get('tweet_count', 0)
            total_engagement += data.get('total_engagement', 0)
        
        overall_sentiment = total_score / total_weight if total_weight > 0 else 0
        
        # Classify overall sentiment
        if overall_sentiment > 0.2:
            overall_label = "bullish"
        elif overall_sentiment < -0.2:
            overall_label = "bearish"
        else:
            overall_label = "neutral"
        
        return {
            'source': 'twitter',
            'overall_sentiment': overall_sentiment,
            'sentiment_label': overall_label,
            'total_tweets_analyzed': total_tweets,
            'total_engagement': total_engagement,
            'confidence': min(total_tweets / 500, 1.0),  # Higher confidence with more data
            'query_results': sentiment_results,
            'timestamp': datetime.now().isoformat(),
            'enabled': True
        }
    
    def _empty_sentiment(self) -> Dict:
        """Return empty sentiment data"""
        return {
            'sentiment_score': 0,
            'sentiment_label': 'neutral',
            'tweet_count': 0,
            'total_engagement': 0,
            'confidence': 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_fallback_data(self, symbols: List[str] = None, keywords: List[str] = None) -> Dict:
        """Return fallback data when API is not available"""
        if not self.enabled:
            logger.warning("[WARNING]️ Using Twitter fallback data (API not configured)")
            note = 'Twitter API not configured - using fallback mode'
        else:
            logger.info("[INFO]️ Twitter API authenticated but search requires elevated access")
            note = 'Twitter API authenticated but search requires Free tier or higher. Apply at developer.twitter.com'

        return {
            'source': 'twitter',
            'overall_sentiment': 0,
            'sentiment_label': 'neutral',
            'total_tweets_analyzed': 0,
            'total_engagement': 0,
            'confidence': 0,
            'query_results': {},
            'timestamp': datetime.now().isoformat(),
            'enabled': self.enabled,
            'authenticated': self.enabled,
            'search_available': False,
            'note': note
        }
    
    def get_trending_topics(self, woeid: int = 1) -> List[Dict]:
        """
        Get trending topics from Twitter

        Args:
            woeid: Where On Earth ID (1 = Worldwide, 23424977 = United States)

        Returns:
            List of trending topics
        """
        # Lazy initialization on first use
        if not self._initialized:
            self._initialize_client()

        if not self.enabled or not self.api:
            return []
        
        try:
            trends = self.api.get_place_trends(woeid)
            
            if not trends:
                return []
            
            trending_topics = []
            for trend in trends[0]['trends'][:20]:  # Top 20 trends
                trending_topics.append({
                    'name': trend['name'],
                    'url': trend['url'],
                    'tweet_volume': trend.get('tweet_volume', 0),
                    'timestamp': datetime.now().isoformat()
                })
            
            logger.info(f"[CHECK] Retrieved {len(trending_topics)} trending topics")
            return trending_topics
            
        except Exception as e:
            logger.error(f"[ERROR] Error getting trending topics: {e}")
            return []

    def is_authenticated(self) -> bool:
        """Check if Twitter API is authenticated (without triggering initialization)"""
        return self.enabled

    @property
    def search_available(self) -> bool:
        """Check if Twitter search is available (without triggering initialization)"""
        return self.enabled and (self.api is not None or self.client is not None)


# Global instance (lazy initialization - won't block server startup)
twitter_source = TwitterDataSource()

