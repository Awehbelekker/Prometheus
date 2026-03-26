"""
PROMETHEUS ENHANCED DATA INGESTION SYSTEM
Scrapes and integrates multiple data sources for superior learning
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialNewsScaper:
    """Scrape financial news and sentiment from multiple sources"""
    
    def __init__(self):
        self.sources = {
            'finviz': 'https://finviz.com/quote.ashx?t={}',
            'yahoo_news': 'https://finance.yahoo.com/quote/{}/news',
            'seekingalpha': 'https://seekingalpha.com/symbol/{}'
        }
        self.sentiment_cache = {}
    
    async def get_news_sentiment(self, symbol: str) -> Dict:
        """Get aggregated news sentiment for a symbol"""
        try:
            # Use finviz for free sentiment data
            url = f"https://finviz.com/quote.ashx?t={symbol}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        
                        # Extract news headlines (simple parsing)
                        headlines = re.findall(r'<a[^>]*class="tab-link-news"[^>]*>([^<]+)</a>', html)
                        
                        # Simple sentiment scoring
                        positive_words = ['surge', 'jump', 'gain', 'profit', 'beat', 'upgrade', 'buy', 'bull']
                        negative_words = ['drop', 'fall', 'loss', 'miss', 'downgrade', 'sell', 'bear', 'crash']
                        
                        sentiment_score = 0
                        for headline in headlines[:10]:  # Top 10 headlines
                            headline_lower = headline.lower()
                            sentiment_score += sum(1 for word in positive_words if word in headline_lower)
                            sentiment_score -= sum(1 for word in negative_words if word in headline_lower)
                        
                        # Normalize to -1 to 1
                        sentiment = max(-1, min(1, sentiment_score / 10))
                        
                        return {
                            'symbol': symbol,
                            'sentiment': sentiment,
                            'news_count': len(headlines),
                            'headlines': headlines[:5],
                            'timestamp': datetime.now().isoformat()
                        }
        except Exception as e:
            logger.warning(f"Error fetching sentiment for {symbol}: {e}")
        
        return {'symbol': symbol, 'sentiment': 0, 'news_count': 0}


class SECFilingsParser:
    """Parse SEC filings for insider trading and institutional changes"""
    
    def __init__(self):
        self.sec_base = "https://www.sec.gov"
    
    async def get_insider_activity(self, symbol: str) -> Dict:
        """Get recent insider trading activity"""
        try:
            # SEC EDGAR API (free)
            url = f"https://data.sec.gov/submissions/CIK{symbol}.json"
            
            async with aiohttp.ClientSession() as session:
                headers = {'User-Agent': 'PROMETHEUS prometheus@trading.com'}
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        # Look for Form 4 (insider trading)
                        filings = data.get('filings', {}).get('recent', {})
                        form4_count = sum(1 for f in filings.get('form', []) if f == '4')
                        
                        return {
                            'symbol': symbol,
                            'insider_buys': form4_count,
                            'signal': 'bullish' if form4_count > 3 else 'neutral'
                        }
        except Exception as e:
            logger.debug(f"SEC data not available for {symbol}: {e}")
        
        return {'symbol': symbol, 'insider_buys': 0, 'signal': 'neutral'}


class EarningsCalendar:
    """Track earnings dates and surprises"""
    
    def __init__(self):
        self.earnings_cache = {}
    
    async def get_earnings_info(self, symbol: str) -> Dict:
        """Get upcoming earnings date and historical surprises"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            calendar = ticker.calendar
            
            if calendar is not None and not calendar.empty:
                earnings_date = calendar.get('Earnings Date')
                
                return {
                    'symbol': symbol,
                    'next_earnings': str(earnings_date) if earnings_date is not None else None,
                    'has_earnings_soon': self._is_earnings_soon(earnings_date)
                }
        except Exception as e:
            logger.debug(f"Earnings data not available for {symbol}: {e}")
        
        return {'symbol': symbol, 'next_earnings': None, 'has_earnings_soon': False}
    
    def _is_earnings_soon(self, earnings_date) -> bool:
        """Check if earnings is within 2 weeks"""
        try:
            if earnings_date is None:
                return False
            
            # Convert to datetime if needed
            if hasattr(earnings_date, 'iloc'):
                earnings_date = earnings_date.iloc[0]
            
            days_until = (earnings_date - datetime.now()).days
            return 0 <= days_until <= 14
        except:
            return False


class RedditSentiment:
    """Scrape Reddit WSB and investing subreddits"""
    
    def __init__(self):
        self.subreddits = ['wallstreetbets', 'stocks', 'investing']
    
    async def get_reddit_mentions(self, symbol: str) -> Dict:
        """Count mentions and sentiment on Reddit"""
        try:
            # Using pushshift.io API (free Reddit archive)
            url = f"https://api.pushshift.io/reddit/search/submission/"
            params = {
                'q': symbol,
                'subreddit': ','.join(self.subreddits),
                'size': 100,
                'after': '7d'  # Last 7 days
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        mentions = len(data.get('data', []))
                        
                        # Calculate sentiment from upvote ratio
                        avg_score = sum(p.get('score', 0) for p in data.get('data', [])) / max(mentions, 1)
                        
                        return {
                            'symbol': symbol,
                            'reddit_mentions': mentions,
                            'avg_score': avg_score,
                            'signal': 'bullish' if mentions > 10 and avg_score > 100 else 'neutral'
                        }
        except Exception as e:
            logger.debug(f"Reddit data not available for {symbol}: {e}")
        
        return {'symbol': symbol, 'reddit_mentions': 0, 'signal': 'neutral'}


class TechnicalIndicatorEnhancer:
    """Add advanced technical indicators not in basic yfinance"""
    
    def calculate_advanced_indicators(self, bars: List[Dict]) -> Dict:
        """Calculate advanced technical indicators"""
        if len(bars) < 50:
            return {}
        
        closes = [b['close'] for b in bars]
        highs = [b['high'] for b in bars]
        lows = [b['low'] for b in bars]
        volumes = [b['volume'] for b in bars]
        
        # On-Balance Volume (OBV)
        obv = self._calculate_obv(closes, volumes)
        
        # Money Flow Index (MFI)
        mfi = self._calculate_mfi(highs, lows, closes, volumes)
        
        # Average True Range (ATR)
        atr = self._calculate_atr(highs, lows, closes)
        
        # Ichimoku Cloud
        ichimoku = self._calculate_ichimoku(highs, lows, closes)
        
        return {
            'obv_trend': 'bullish' if obv[-1] > obv[-10] else 'bearish',
            'mfi': mfi[-1] if mfi else 50,
            'mfi_signal': 'oversold' if mfi and mfi[-1] < 20 else 'overbought' if mfi and mfi[-1] > 80 else 'neutral',
            'atr': atr[-1] if atr else 0,
            'volatility': 'high' if atr and atr[-1] > atr[-20] else 'normal',
            'ichimoku_signal': ichimoku
        }
    
    def _calculate_obv(self, closes, volumes):
        """On-Balance Volume"""
        obv = [volumes[0]]
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv.append(obv[-1] + volumes[i])
            elif closes[i] < closes[i-1]:
                obv.append(obv[-1] - volumes[i])
            else:
                obv.append(obv[-1])
        return obv
    
    def _calculate_mfi(self, highs, lows, closes, volumes, period=14):
        """Money Flow Index"""
        if len(closes) < period + 1:
            return []
        
        typical_prices = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
        money_flows = [tp * v for tp, v in zip(typical_prices, volumes)]
        
        mfi = []
        for i in range(period, len(typical_prices)):
            positive_flow = sum(money_flows[j] for j in range(i-period+1, i+1) 
                              if typical_prices[j] > typical_prices[j-1])
            negative_flow = sum(money_flows[j] for j in range(i-period+1, i+1) 
                              if typical_prices[j] < typical_prices[j-1])
            
            if negative_flow == 0:
                mfi.append(100)
            else:
                mfi_val = 100 - (100 / (1 + positive_flow / negative_flow))
                mfi.append(mfi_val)
        
        return mfi
    
    def _calculate_atr(self, highs, lows, closes, period=14):
        """Average True Range"""
        if len(closes) < period + 1:
            return []
        
        tr = []
        for i in range(1, len(closes)):
            tr.append(max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            ))
        
        atr = []
        for i in range(period-1, len(tr)):
            atr.append(sum(tr[i-period+1:i+1]) / period)
        
        return atr
    
    def _calculate_ichimoku(self, highs, lows, closes):
        """Ichimoku Cloud signal"""
        if len(closes) < 52:
            return 'neutral'
        
        # Tenkan-sen (9-period)
        tenkan = (max(highs[-9:]) + min(lows[-9:])) / 2
        
        # Kijun-sen (26-period)
        kijun = (max(highs[-26:]) + min(lows[-26:])) / 2
        
        # Simple signal
        if closes[-1] > tenkan and closes[-1] > kijun and tenkan > kijun:
            return 'strong_bullish'
        elif closes[-1] > tenkan and closes[-1] > kijun:
            return 'bullish'
        elif closes[-1] < tenkan and closes[-1] < kijun:
            return 'bearish'
        
        return 'neutral'


class EnhancedDataAggregator:
    """Aggregate all enhanced data sources"""
    
    def __init__(self):
        self.news_scraper = FinancialNewsScaper()
        self.sec_parser = SECFilingsParser()
        self.earnings = EarningsCalendar()
        self.reddit = RedditSentiment()
        self.technical = TechnicalIndicatorEnhancer()
        self.data_file = Path("enhanced_market_data.json")
    
    async def gather_enhanced_data(self, symbol: str, bars: List[Dict]) -> Dict:
        """Gather all enhanced data for a symbol"""
        logger.info(f"📡 Gathering enhanced data for {symbol}...")
        
        # Parallel data gathering
        results = await asyncio.gather(
            self.news_scraper.get_news_sentiment(symbol),
            self.sec_parser.get_insider_activity(symbol),
            self.earnings.get_earnings_info(symbol),
            self.reddit.get_reddit_mentions(symbol),
            return_exceptions=True
        )
        
        # Technical indicators
        technical_data = self.technical.calculate_advanced_indicators(bars)
        
        # Combine all data
        enhanced_data = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'news_sentiment': results[0] if not isinstance(results[0], Exception) else {},
            'insider_activity': results[1] if not isinstance(results[1], Exception) else {},
            'earnings': results[2] if not isinstance(results[2], Exception) else {},
            'social_sentiment': results[3] if not isinstance(results[3], Exception) else {},
            'advanced_technical': technical_data
        }
        
        # Calculate composite score
        enhanced_data['composite_score'] = self._calculate_composite_score(enhanced_data)
        
        return enhanced_data
    
    def _calculate_composite_score(self, data: Dict) -> float:
        """Calculate composite bullish/bearish score from all data"""
        score = 0
        
        # News sentiment (-1 to 1)
        score += data.get('news_sentiment', {}).get('sentiment', 0) * 0.3
        
        # Insider activity
        if data.get('insider_activity', {}).get('signal') == 'bullish':
            score += 0.2
        
        # Social sentiment
        if data.get('social_sentiment', {}).get('signal') == 'bullish':
            score += 0.15
        
        # Technical indicators
        tech = data.get('advanced_technical', {})
        if tech.get('obv_trend') == 'bullish':
            score += 0.1
        if tech.get('mfi_signal') == 'oversold':
            score += 0.15
        elif tech.get('mfi_signal') == 'overbought':
            score -= 0.15
        if tech.get('ichimoku_signal') == 'strong_bullish':
            score += 0.2
        elif tech.get('ichimoku_signal') == 'bullish':
            score += 0.1
        
        return max(-1, min(1, score))
    
    def save_to_cache(self, symbol: str, data: Dict):
        """Save enhanced data to cache"""
        try:
            cache = {}
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    cache = json.load(f)
            
            cache[symbol] = data
            
            with open(self.data_file, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Error saving cache: {e}")
    
    def load_from_cache(self, symbol: str) -> Optional[Dict]:
        """Load enhanced data from cache"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    cache = json.load(f)
                
                data = cache.get(symbol)
                if data:
                    # Check if data is fresh (< 1 hour old)
                    timestamp = datetime.fromisoformat(data.get('timestamp', '2000-01-01'))
                    if (datetime.now() - timestamp).seconds < 3600:
                        return data
        except Exception as e:
            logger.debug(f"Cache miss for {symbol}: {e}")
        
        return None


async def demo_enhanced_data():
    """Demo: Gather enhanced data for testing"""
    aggregator = EnhancedDataAggregator()
    
    symbols = ['AAPL', 'TSLA', 'NVDA', 'SPY']
    
    print("\n" + "="*70)
    print("PROMETHEUS ENHANCED DATA INGESTION - DEMO")
    print("="*70 + "\n")
    
    for symbol in symbols:
        print(f"📊 {symbol}:")
        
        # Simulate some bars
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='60d')
        
        bars = []
        for idx, row in hist.iterrows():
            bars.append({
                'close': row['Close'],
                'high': row['High'],
                'low': row['Low'],
                'volume': row['Volume']
            })
        
        # Gather enhanced data
        enhanced = await aggregator.gather_enhanced_data(symbol, bars)
        
        # Display results
        print(f"  News Sentiment: {enhanced.get('news_sentiment', {}).get('sentiment', 0):.2f}")
        print(f"  Composite Score: {enhanced.get('composite_score', 0):.2f}")
        print(f"  Technical: {enhanced.get('advanced_technical', {}).get('ichimoku_signal', 'N/A')}")
        print()
        
        # Save to cache
        aggregator.save_to_cache(symbol, enhanced)
    
    print("✅ Enhanced data cached for learning engine integration")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(demo_enhanced_data())
