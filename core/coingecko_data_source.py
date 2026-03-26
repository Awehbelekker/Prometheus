"""
COINGECKO DATA SOURCE
=====================

CoinGecko cryptocurrency data source for enhanced crypto trading intelligence.

Features:
- Real-time crypto prices
- Market cap and volume data
- Social metrics (Twitter, Reddit, Telegram)
- Developer activity
- Community stats
- Price change percentages

Author: PROMETHEUS AI Team
Date: October 10, 2025
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
import random

logger = logging.getLogger(__name__)

class CoinGeckoDataSource:
    """
    CoinGecko data source for cryptocurrency market intelligence
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.coingecko.com/api/v3"
        
        # Symbol to CoinGecko ID mapping
        self.symbol_to_id = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'SOL': 'solana',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'MATIC': 'matic-network',
            'AVAX': 'avalanche-2',
            'LINK': 'chainlink',
            'UNI': 'uniswap',
            'ATOM': 'cosmos'
        }
        
        logger.info("🪙 CoinGecko Data Source initialized")
    
    async def get_coin_data(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive coin data from CoinGecko"""
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'true',
                'developer_data': 'true',
                'sparkline': 'false'
            }
            
            if self.api_key:
                params['x_cg_pro_api_key'] = self.api_key
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        logger.warning("[WARNING]️ CoinGecko rate limit - using mock data")
                        return self._generate_mock_coin_data(coin_id)
                    else:
                        logger.warning(f"[WARNING]️ CoinGecko API error: {response.status}")
                        return self._generate_mock_coin_data(coin_id)
                        
        except Exception as e:
            logger.error(f"Error fetching CoinGecko data: {e}")
            return self._generate_mock_coin_data(coin_id)
    
    def _generate_mock_coin_data(self, coin_id: str) -> Dict[str, Any]:
        """Generate mock coin data"""
        return {
            'id': coin_id,
            'symbol': coin_id[:3].upper(),
            'name': coin_id.capitalize(),
            'market_data': {
                'current_price': {'usd': random.uniform(100, 50000)},
                'market_cap': {'usd': random.uniform(1e9, 1e12)},
                'total_volume': {'usd': random.uniform(1e8, 1e11)},
                'price_change_percentage_24h': random.uniform(-10, 10),
                'price_change_percentage_7d': random.uniform(-20, 20),
                'price_change_percentage_30d': random.uniform(-30, 30),
                'market_cap_rank': random.randint(1, 100)
            },
            'community_data': {
                'twitter_followers': random.randint(10000, 5000000),
                'reddit_subscribers': random.randint(5000, 2000000),
                'telegram_channel_user_count': random.randint(1000, 500000)
            },
            'developer_data': {
                'forks': random.randint(100, 10000),
                'stars': random.randint(500, 50000),
                'subscribers': random.randint(100, 5000),
                'total_issues': random.randint(50, 5000),
                'closed_issues': random.randint(40, 4500),
                'pull_requests_merged': random.randint(100, 10000),
                'commit_count_4_weeks': random.randint(10, 500)
            },
            'sentiment_votes_up_percentage': random.uniform(50, 90),
            'sentiment_votes_down_percentage': random.uniform(10, 50)
        }
    
    async def get_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Get market data for multiple symbols"""
        try:
            results = {}
            
            for symbol in symbols:
                # Convert symbol to CoinGecko ID
                coin_id = self.symbol_to_id.get(symbol.replace('/USD', '').replace('USD', ''))
                
                if not coin_id:
                    continue
                
                data = await self.get_coin_data(coin_id)
                
                if data:
                    market_data = data.get('market_data', {})
                    community_data = data.get('community_data', {})
                    developer_data = data.get('developer_data', {})
                    
                    results[symbol] = {
                        'price': market_data.get('current_price', {}).get('usd', 0),
                        'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                        'volume_24h': market_data.get('total_volume', {}).get('usd', 0),
                        'price_change_24h': market_data.get('price_change_percentage_24h', 0),
                        'price_change_7d': market_data.get('price_change_percentage_7d', 0),
                        'price_change_30d': market_data.get('price_change_percentage_30d', 0),
                        'market_cap_rank': market_data.get('market_cap_rank', 0),
                        'twitter_followers': community_data.get('twitter_followers', 0),
                        'reddit_subscribers': community_data.get('reddit_subscribers', 0),
                        'telegram_users': community_data.get('telegram_channel_user_count', 0),
                        'github_stars': developer_data.get('stars', 0),
                        'github_commits_4w': developer_data.get('commit_count_4_weeks', 0),
                        'sentiment_up': data.get('sentiment_votes_up_percentage', 50),
                        'sentiment_down': data.get('sentiment_votes_down_percentage', 50)
                    }
                
                # Rate limiting
                await asyncio.sleep(0.5)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting CoinGecko market data: {e}")
            return {}
    
    async def get_trading_signals(self, symbols: List[str]) -> Dict[str, Any]:
        """Get trading signals from CoinGecko data"""
        try:
            market_data = await self.get_market_data(symbols)

            signals = {}
            for symbol, data in market_data.items():
                # Calculate signal strength based on multiple factors
                price_momentum = abs(data.get('price_change_24h', 0)) / 10  # Normalize to 0-1

                # FIX: Handle None values in social metrics
                twitter_score = (data.get('twitter_followers') or 0) / 1000000
                reddit_score = (data.get('reddit_subscribers') or 0) / 500000
                telegram_score = (data.get('telegram_users') or 0) / 100000
                social_score = min(1.0, (twitter_score + reddit_score + telegram_score) / 3)

                # FIX: Handle None values in developer metrics
                stars_score = (data.get('github_stars') or 0) / 10000
                commits_score = (data.get('github_commits_4w') or 0) / 100
                developer_score = min(1.0, (stars_score + commits_score) / 2)

                sentiment_score = (data.get('sentiment_up', 50) - 50) / 50  # -1 to 1
                
                # Combined signal strength
                signal_strength = (
                    price_momentum * 0.3 +
                    social_score * 0.3 +
                    developer_score * 0.2 +
                    abs(sentiment_score) * 0.2
                )
                
                # Determine direction
                direction = 'bullish' if data['price_change_24h'] > 0 and sentiment_score > 0 else 'bearish'
                
                signals[symbol] = {
                    'signal_strength': min(1.0, signal_strength),
                    'direction': direction,
                    'price_momentum': data['price_change_24h'],
                    'social_score': social_score,
                    'developer_score': developer_score,
                    'sentiment_score': sentiment_score,
                    'market_cap_rank': data['market_cap_rank'],
                    'confidence': min(1.0, (social_score + developer_score) / 2),
                    'interpretation': self._interpret_signal(data, direction)
                }
            
            return signals
            
        except Exception as e:
            logger.error(f"Error getting CoinGecko trading signals: {e}")
            return {}
    
    def _interpret_signal(self, data: Dict[str, Any], direction: str) -> str:
        """Interpret CoinGecko signal"""
        price_change = data['price_change_24h']
        social_score = min(1.0, (data['twitter_followers'] / 1000000 + data['reddit_subscribers'] / 500000) / 2)
        
        if direction == 'bullish':
            if price_change > 5 and social_score > 0.7:
                return "Strong bullish momentum with high social engagement"
            elif price_change > 2:
                return "Positive price action with growing interest"
            else:
                return "Mild bullish sentiment"
        else:
            if price_change < -5 and social_score > 0.7:
                return "Strong bearish pressure despite social engagement"
            elif price_change < -2:
                return "Negative price action with declining interest"
            else:
                return "Mild bearish sentiment"
    
    async def get_trending_coins(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending coins from CoinGecko"""
        try:
            url = f"{self.base_url}/search/trending"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        coins = data.get('coins', [])
                        
                        trending = []
                        for coin in coins[:limit]:
                            item = coin.get('item', {})
                            trending.append({
                                'symbol': item.get('symbol', ''),
                                'name': item.get('name', ''),
                                'market_cap_rank': item.get('market_cap_rank', 0),
                                'price_btc': item.get('price_btc', 0),
                                'score': item.get('score', 0)
                            })
                        
                        return trending
                    else:
                        return self._generate_mock_trending()
                        
        except Exception as e:
            logger.error(f"Error getting trending coins: {e}")
            return self._generate_mock_trending()
    
    def _generate_mock_trending(self) -> List[Dict[str, Any]]:
        """Generate mock trending coins"""
        mock_coins = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'MATIC', 'AVAX', 'LINK', 'UNI', 'ATOM']
        return [
            {
                'symbol': symbol,
                'name': f'{symbol} Coin',
                'market_cap_rank': i + 1,
                'price_btc': random.uniform(0.0001, 1.0),
                'score': random.randint(0, 10)
            }
            for i, symbol in enumerate(mock_coins)
        ]

