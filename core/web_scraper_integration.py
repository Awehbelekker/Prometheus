#!/usr/bin/env python3
"""
🌐 WEB SCRAPER INTEGRATION FOR PROMETHEUS
Real-world market data aggregation from multiple sources

Sources:
1. Yahoo Finance (prices, volumes)
2. TradingView (charts, indicators)
3. Finviz (screener data, sentiment)
4. Investing.com (economic calendar)
5. Reddit/Twitter (social sentiment)

Goal: Reduce API costs + get more realistic market data
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WebScraperIntegration:
    """
    🌐 Aggregates real-world market data from web sources
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        self.scraped_data_dir = Path("scraped_market_data")
        self.scraped_data_dir.mkdir(exist_ok=True)
        
        # User-Agent to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def get_finviz_data(self, symbol: str) -> Dict[str, Any]:
        """
        📊 Scrape Finviz for technical data and sentiment
        
        Returns: price, change%, volume, float, sentiment, etc.
        """
        cache_key = f"finviz_{symbol}"
        if self._check_cache(cache_key):
            return self.cache[cache_key]
        
        url = f"https://finviz.com/quote.ashx?t={symbol}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=10) as response:
                    if response.status != 200:
                        logger.warning(f"Finviz returned {response.status} for {symbol}")
                        return {}
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract data from table
                    data = {}
                    tables = soup.find_all('table', class_='snapshot-table2')
                    
                    for table in tables:
                        rows = table.find_all('tr')
                        for row in rows:
                            cols = row.find_all('td')
                            for i in range(0, len(cols), 2):
                                if i + 1 < len(cols):
                                    key = cols[i].text.strip()
                                    value = cols[i + 1].text.strip()
                                    data[key] = value
                    
                    # Parse useful fields
                    scraped = {
                        'source': 'finviz',
                        'symbol': symbol,
                        'timestamp': datetime.now().isoformat(),
                        'market_cap': data.get('Market Cap', 'N/A'),
                        'pe_ratio': data.get('P/E', 'N/A'),
                        'forward_pe': data.get('Forward P/E', 'N/A'),
                        'peg_ratio': data.get('PEG', 'N/A'),
                        'div_yield': data.get('Dividend %', 'N/A'),
                        'eps': data.get('EPS (ttm)', 'N/A'),
                        'insider_own': data.get('Insider Own', 'N/A'),
                        'short_float': data.get('Short Float', 'N/A'),
                        'target_price': data.get('Target Price', 'N/A'),
                        'rsi': data.get('RSI (14)', 'N/A'),
                        'volatility': data.get('Volatility', 'N/A'),
                        'recommendation': data.get('Recom', 'N/A')
                    }
                    
                    # Determine sentiment from recommendation
                    recom = scraped.get('recommendation', 'N/A')
                    if recom != 'N/A':
                        try:
                            recom_float = float(recom)
                            if recom_float < 2.0:
                                scraped['sentiment'] = 'bullish'
                                scraped['sentiment_score'] = 0.8
                            elif recom_float < 2.5:
                                scraped['sentiment'] = 'neutral_bullish'
                                scraped['sentiment_score'] = 0.6
                            elif recom_float < 3.0:
                                scraped['sentiment'] = 'neutral'
                                scraped['sentiment_score'] = 0.5
                            else:
                                scraped['sentiment'] = 'bearish'
                                scraped['sentiment_score'] = 0.3
                        except:
                            scraped['sentiment'] = 'neutral'
                            scraped['sentiment_score'] = 0.5
                    
                    self._update_cache(cache_key, scraped)
                    logger.info(f"✅ Scraped Finviz: {symbol} - Sentiment: {scraped.get('sentiment', 'N/A')}")
                    
                    return scraped
                    
        except Exception as e:
            logger.error(f"Finviz scrape error for {symbol}: {e}")
            return {}
    
    async def get_yahoo_finance_data(self, symbol: str) -> Dict[str, Any]:
        """
        📈 Scrape Yahoo Finance for real-time quotes
        
        Note: Better to use yfinance library, but this shows web scraping
        """
        cache_key = f"yahoo_{symbol}"
        if self._check_cache(cache_key):
            return self.cache[cache_key]
        
        url = f"https://finance.yahoo.com/quote/{symbol}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=10) as response:
                    if response.status != 200:
                        return {}
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Try to find price (Yahoo's structure changes often)
                    price_elem = soup.find('fin-streamer', {'data-symbol': symbol, 'data-field': 'regularMarketPrice'})
                    change_elem = soup.find('fin-streamer', {'data-symbol': symbol, 'data-field': 'regularMarketChange'})
                    
                    scraped = {
                        'source': 'yahoo',
                        'symbol': symbol,
                        'timestamp': datetime.now().isoformat(),
                        'price': price_elem.get('value', 'N/A') if price_elem else 'N/A',
                        'change': change_elem.get('value', 'N/A') if change_elem else 'N/A'
                    }
                    
                    self._update_cache(cache_key, scraped)
                    logger.info(f"✅ Scraped Yahoo Finance: {symbol}")
                    
                    return scraped
                    
        except Exception as e:
            logger.error(f"Yahoo scrape error for {symbol}: {e}")
            return {}
    
    async def get_reddit_sentiment(self, symbol: str, subreddits: List[str] = None) -> Dict[str, Any]:
        """
        💬 Scrape Reddit for social sentiment
        
        Subreddits: wallstreetbets, stocks, investing, etc.
        """
        if subreddits is None:
            subreddits = ['wallstreetbets', 'stocks', 'investing']
        
        cache_key = f"reddit_{symbol}"
        if self._check_cache(cache_key):
            return self.cache[cache_key]
        
        mentions = 0
        positive = 0
        negative = 0
        
        try:
            for subreddit in subreddits:
                url = f"https://www.reddit.com/r/{subreddit}/search.json?q={symbol}&sort=new&limit=25"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers, timeout=10) as response:
                        if response.status != 200:
                            continue
                        
                        data = await response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post in posts:
                            post_data = post.get('data', {})
                            title = post_data.get('title', '').lower()
                            
                            if symbol.lower() in title:
                                mentions += 1
                                
                                # Simple sentiment analysis
                                positive_words = ['buy', 'bull', 'moon', 'calls', 'long', 'up', 'gain']
                                negative_words = ['sell', 'bear', 'puts', 'short', 'down', 'loss', 'dump']
                                
                                for word in positive_words:
                                    if word in title:
                                        positive += 1
                                        break
                                
                                for word in negative_words:
                                    if word in title:
                                        negative += 1
                                        break
            
            # Calculate sentiment
            total_sentiment = positive + negative
            sentiment_score = 0.5  # neutral
            
            if total_sentiment > 0:
                sentiment_score = positive / total_sentiment
            
            scraped = {
                'source': 'reddit',
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'mentions': mentions,
                'positive_mentions': positive,
                'negative_mentions': negative,
                'sentiment_score': sentiment_score,
                'sentiment': 'bullish' if sentiment_score > 0.6 else 'bearish' if sentiment_score < 0.4 else 'neutral'
            }
            
            self._update_cache(cache_key, scraped)
            logger.info(f"✅ Scraped Reddit: {symbol} - {mentions} mentions, sentiment: {sentiment_score:.2f}")
            
            return scraped
            
        except Exception as e:
            logger.error(f"Reddit scrape error for {symbol}: {e}")
            return {}
    
    async def get_investing_com_calendar(self) -> Dict[str, Any]:
        """
        📅 Scrape economic calendar from Investing.com
        
        Returns upcoming events that could impact markets
        """
        cache_key = "economic_calendar"
        if self._check_cache(cache_key, duration=3600):  # Cache for 1 hour
            return self.cache[cache_key]
        
        url = "https://www.investing.com/economic-calendar/"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=10) as response:
                    if response.status != 200:
                        return {}
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find economic events
                    events = []
                    rows = soup.find_all('tr', {'class': 'js-event-item'})
                    
                    for row in rows[:20]:  # Top 20 events
                        time_elem = row.find('td', {'class': 'time'})
                        country_elem = row.find('td', {'class': 'flagCur'})
                        event_elem = row.find('td', {'class': 'event'})
                        impact_elem = row.find('td', {'class': 'sentiment'})
                        
                        if event_elem:
                            events.append({
                                'time': time_elem.text.strip() if time_elem else 'N/A',
                                'country': country_elem.get('title', 'N/A') if country_elem else 'N/A',
                                'event': event_elem.text.strip(),
                                'impact': impact_elem.get('data-img_key', 'low') if impact_elem else 'low'
                            })
                    
                    scraped = {
                        'source': 'investing.com',
                        'timestamp': datetime.now().isoformat(),
                        'events': events,
                        'high_impact_count': sum(1 for e in events if e['impact'] == 'high')
                    }
                    
                    self._update_cache(cache_key, scraped, duration=3600)
                    logger.info(f"✅ Scraped economic calendar: {len(events)} events")
                    
                    return scraped
                    
        except Exception as e:
            logger.error(f"Economic calendar scrape error: {e}")
            return {}
    
    async def aggregate_all_data(self, symbol: str) -> Dict[str, Any]:
        """
        🌐 Aggregate all scraped data for a symbol
        
        Returns comprehensive market intelligence
        """
        logger.info(f"🌐 Aggregating web data for {symbol}...")
        
        # Run all scrapers in parallel
        results = await asyncio.gather(
            self.get_finviz_data(symbol),
            self.get_yahoo_finance_data(symbol),
            self.get_reddit_sentiment(symbol),
            return_exceptions=True
        )
        
        finviz_data, yahoo_data, reddit_data = results
        
        # Combine data
        aggregated = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'sources': []
        }
        
        if isinstance(finviz_data, dict) and finviz_data:
            aggregated['finviz'] = finviz_data
            aggregated['sources'].append('finviz')
        
        if isinstance(yahoo_data, dict) and yahoo_data:
            aggregated['yahoo'] = yahoo_data
            aggregated['sources'].append('yahoo')
        
        if isinstance(reddit_data, dict) and reddit_data:
            aggregated['reddit'] = reddit_data
            aggregated['sources'].append('reddit')
        
        # Calculate combined sentiment
        sentiments = []
        if finviz_data and 'sentiment_score' in finviz_data:
            sentiments.append(finviz_data['sentiment_score'])
        if reddit_data and 'sentiment_score' in reddit_data:
            sentiments.append(reddit_data['sentiment_score'])
        
        if sentiments:
            aggregated['combined_sentiment'] = sum(sentiments) / len(sentiments)
            aggregated['sentiment_confidence'] = len(sentiments) / 2.0  # Max 2 sources
        else:
            aggregated['combined_sentiment'] = 0.5
            aggregated['sentiment_confidence'] = 0.0
        
        # Save to file
        output_file = self.scraped_data_dir / f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(aggregated, f, indent=2)
        
        logger.info(f"✅ Aggregated data for {symbol} from {len(aggregated['sources'])} sources")
        logger.info(f"   Combined sentiment: {aggregated['combined_sentiment']:.2f}")
        
        return aggregated
    
    def _check_cache(self, key: str, duration: int = None) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        
        cached_time = self.cache[key].get('_cached_at', 0)
        duration = duration or self.cache_duration
        
        return (time.time() - cached_time) < duration
    
    def _update_cache(self, key: str, data: Dict, duration: int = None):
        """Update cache with timestamp"""
        import time
        data['_cached_at'] = time.time()
        self.cache[key] = data
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'cached_items': len(self.cache),
            'cache_keys': list(self.cache.keys())
        }


async def demo_web_scraper():
    """
    🎯 Demo: Scrape data for multiple symbols
    """
    logger.info("🚀 Starting Web Scraper Integration Demo")
    
    scraper = WebScraperIntegration()
    
    symbols = ['AAPL', 'MSFT', 'TSLA', 'NVDA']
    
    for symbol in symbols:
        logger.info(f"\n📊 Scraping {symbol}...")
        
        aggregated = await scraper.aggregate_all_data(symbol)
        
        print(f"\n{'='*60}")
        print(f"📊 {symbol} - Aggregated Data")
        print(f"{'='*60}")
        print(f"Sources: {', '.join(aggregated.get('sources', []))}")
        print(f"Combined Sentiment: {aggregated.get('combined_sentiment', 0.5):.2f}")
        print(f"Sentiment Confidence: {aggregated.get('sentiment_confidence', 0.0):.2f}")
        
        if 'finviz' in aggregated:
            finviz = aggregated['finviz']
            print(f"\nFinviz:")
            print(f"  RSI: {finviz.get('rsi', 'N/A')}")
            print(f"  Recommendation: {finviz.get('recommendation', 'N/A')}")
            print(f"  Sentiment: {finviz.get('sentiment', 'N/A')}")
        
        if 'reddit' in aggregated:
            reddit = aggregated['reddit']
            print(f"\nReddit:")
            print(f"  Mentions: {reddit.get('mentions', 0)}")
            print(f"  Sentiment: {reddit.get('sentiment', 'N/A')} ({reddit.get('sentiment_score', 0.5):.2f})")
        
        # Small delay between symbols
        await asyncio.sleep(2)
    
    # Get economic calendar
    logger.info(f"\n📅 Fetching economic calendar...")
    calendar = await scraper.get_investing_com_calendar()
    
    if calendar and 'events' in calendar:
        print(f"\n{'='*60}")
        print(f"📅 Economic Calendar - Next Events")
        print(f"{'='*60}")
        for event in calendar['events'][:5]:
            print(f"  {event['time']:<10} | {event['country']:<15} | {event['event']}")
    
    logger.info(f"\n✅ Web scraping demo complete!")
    logger.info(f"📁 Data saved to: {scraper.scraped_data_dir}")


if __name__ == "__main__":
    asyncio.run(demo_web_scraper())
