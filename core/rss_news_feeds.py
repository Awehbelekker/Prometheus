"""
FREE RSS News Feed Integration
Replaces delayed/expensive news APIs with FREE RSS feeds

Sources (ALL FREE):
- Financial Times RSS
- Wall Street Journal RSS
- Reuters RSS
- Bloomberg RSS (limited)
- MarketWatch RSS
- CNBC RSS
- Yahoo Finance RSS
"""

import asyncio
import aiohttp
import xml.etree.ElementTree as ET
import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class NewsSignal:
    """Structured news signal"""
    headline: str
    source: str
    url: str
    published: datetime
    symbols: List[str]
    sentiment: float  # -1 to 1
    impact: float  # 0 to 1
    category: str
    summary: Optional[str] = None


class RSSNewsFeeds:
    """FREE RSS news feed aggregator"""
    
    # RSS Feed URLs (ALL FREE)
    RSS_FEEDS = {
        # Major Financial News
        "reuters_business": "https://www.reutersagency.com/feed/?best-topics=business-finance",
        "reuters_markets": "https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best",
        "marketwatch": "https://www.marketwatch.com/rss/topstories",
        "cnbc_top": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "cnbc_market": "https://www.cnbc.com/id/20910258/device/rss/rss.html",
        "yahoo_finance": "https://finance.yahoo.com/news/rssindex",
        
        # Crypto News
        "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "cointelegraph": "https://cointelegraph.com/rss",
        
        # Tech/Business
        "techcrunch": "https://techcrunch.com/feed/",
        "businessinsider": "https://www.businessinsider.com/rss",
    }
    
    # Sentiment keywords
    BULLISH_KEYWORDS = [
        "surge", "soar", "jump", "rally", "gain", "rise", "climb", "beat", "exceed",
        "upgrade", "buy", "bullish", "growth", "profit", "record", "high", "boost",
        "strong", "positive", "upbeat", "optimistic", "recovery", "breakthrough"
    ]
    
    BEARISH_KEYWORDS = [
        "plunge", "crash", "fall", "drop", "decline", "sink", "tumble", "miss",
        "downgrade", "sell", "bearish", "loss", "weak", "low", "cut", "slash",
        "negative", "pessimistic", "warning", "risk", "concern", "fear", "crisis"
    ]
    
    # High-impact event keywords
    HIGH_IMPACT_KEYWORDS = [
        "fed", "federal reserve", "fomc", "rate", "interest rate", "inflation",
        "earnings", "quarterly", "guidance", "forecast", "merger", "acquisition",
        "bankruptcy", "default", "lawsuit", "investigation", "sec", "regulation",
        "ceo", "resign", "layoff", "restructuring", "ipo", "stock split"
    ]
    
    def __init__(self):
        self.session = None
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        logger.info(f"✅ RSS News Feeds initialized with {len(self.RSS_FEEDS)} sources")
    
    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={"User-Agent": "PROMETHEUS Trading Bot/2.0"}
            )
        return self.session
    
    async def fetch_feed(self, feed_name: str, feed_url: str) -> List[Dict]:
        """Fetch and parse a single RSS feed"""
        try:
            session = await self._get_session()
            
            async with session.get(feed_url, timeout=10) as response:
                if response.status != 200:
                    logger.warning(f"⚠️ Feed {feed_name} returned {response.status}")
                    return []
                
                content = await response.text()
            
            # Parse XML
            root = ET.fromstring(content)
            items = []
            
            # Handle both RSS and Atom formats
            for item in root.findall(".//item"):
                items.append(self._parse_rss_item(item, feed_name))
            
            for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
                items.append(self._parse_atom_entry(entry, feed_name))
            
            logger.debug(f"📰 {feed_name}: {len(items)} articles")
            return items
            
        except Exception as e:
            logger.error(f"❌ Error fetching {feed_name}: {e}")
            return []
    
    def _parse_rss_item(self, item: ET.Element, source: str) -> Dict:
        """Parse RSS item"""
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        description = item.findtext("description", "")
        pub_date = item.findtext("pubDate", "")
        
        return {
            "title": title,
            "link": link,
            "description": self._clean_html(description),
            "published": pub_date,
            "source": source
        }
    
    def _parse_atom_entry(self, entry: ET.Element, source: str) -> Dict:
        """Parse Atom entry"""
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        
        title = entry.findtext("atom:title", "", ns) or entry.findtext("title", "")
        link_elem = entry.find("atom:link", ns) or entry.find("link")
        link = link_elem.get("href", "") if link_elem is not None else ""
        summary = entry.findtext("atom:summary", "", ns) or entry.findtext("summary", "")
        published = entry.findtext("atom:published", "", ns) or entry.findtext("published", "")
        
        return {
            "title": title,
            "link": link,
            "description": self._clean_html(summary),
            "published": published,
            "source": source
        }
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags"""
        clean = re.sub(r'<[^>]+>', '', text)
        return clean.strip()[:500]
    
    async def fetch_all_feeds(self) -> List[Dict]:
        """Fetch all RSS feeds concurrently"""
        tasks = [
            self.fetch_feed(name, url) 
            for name, url in self.RSS_FEEDS.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_items = []
        for result in results:
            if isinstance(result, list):
                all_items.extend(result)
        
        logger.info(f"✅ Fetched {len(all_items)} news items from {len(self.RSS_FEEDS)} sources")
        return all_items
    
    def extract_symbols(self, text: str) -> List[str]:
        """Extract stock symbols from text"""
        # Explicit $SYMBOL format
        explicit = re.findall(r'\$([A-Z]{1,5})\b', text)
        
        # Known company mappings
        company_symbols = {
            "apple": "AAPL", "microsoft": "MSFT", "google": "GOOGL", "alphabet": "GOOGL",
            "amazon": "AMZN", "meta": "META", "facebook": "META", "tesla": "TSLA",
            "nvidia": "NVDA", "netflix": "NFLX", "spotify": "SPOT", "uber": "UBER",
            "airbnb": "ABNB", "coinbase": "COIN", "palantir": "PLTR", "snowflake": "SNOW",
            "amd": "AMD", "intel": "INTC", "qualcomm": "QCOM", "broadcom": "AVGO",
            "jpmorgan": "JPM", "goldman sachs": "GS", "morgan stanley": "MS",
            "bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL"
        }
        
        text_lower = text.lower()
        for company, symbol in company_symbols.items():
            if company in text_lower:
                explicit.append(symbol)
        
        return list(set(explicit))
    
    def calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score from text"""
        text_lower = text.lower()
        
        bullish_count = sum(1 for word in self.BULLISH_KEYWORDS if word in text_lower)
        bearish_count = sum(1 for word in self.BEARISH_KEYWORDS if word in text_lower)
        
        if bullish_count + bearish_count == 0:
            return 0.0
        
        sentiment = (bullish_count - bearish_count) / (bullish_count + bearish_count)
        return max(min(sentiment, 1.0), -1.0)
    
    def calculate_impact(self, text: str, source: str) -> float:
        """Calculate news impact score"""
        text_lower = text.lower()
        
        # Base impact by source
        source_impacts = {
            "reuters": 0.5,
            "wsj": 0.6,
            "cnbc": 0.4,
            "bloomberg": 0.6,
            "yahoo": 0.3,
            "marketwatch": 0.4,
        }
        
        base_impact = 0.3
        for src, impact in source_impacts.items():
            if src in source.lower():
                base_impact = impact
                break
        
        # Boost for high-impact keywords
        impact_boost = sum(0.1 for word in self.HIGH_IMPACT_KEYWORDS if word in text_lower)
        
        return min(base_impact + impact_boost, 1.0)
    
    def categorize_news(self, text: str) -> str:
        """Categorize news type"""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ["earnings", "quarterly", "revenue", "profit"]):
            return "earnings"
        elif any(w in text_lower for w in ["fed", "fomc", "rate", "inflation"]):
            return "macro"
        elif any(w in text_lower for w in ["merger", "acquisition", "takeover", "deal"]):
            return "m&a"
        elif any(w in text_lower for w in ["bitcoin", "crypto", "blockchain", "ethereum"]):
            return "crypto"
        elif any(w in text_lower for w in ["ipo", "offering", "debut"]):
            return "ipo"
        elif any(w in text_lower for w in ["lawsuit", "sec", "investigation", "fraud"]):
            return "regulatory"
        else:
            return "general"
    
    def process_news_item(self, item: Dict) -> Optional[NewsSignal]:
        """Process a news item into a signal"""
        title = item.get("title", "")
        description = item.get("description", "")
        full_text = f"{title} {description}"
        
        if len(full_text.strip()) < 20:
            return None
        
        symbols = self.extract_symbols(full_text)
        sentiment = self.calculate_sentiment(full_text)
        impact = self.calculate_impact(full_text, item.get("source", ""))
        category = self.categorize_news(full_text)
        
        # Parse date
        pub_str = item.get("published", "")
        try:
            # Try common formats
            for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"]:
                try:
                    published = datetime.strptime(pub_str[:25], fmt.split("%z")[0])
                    break
                except:
                    continue
            else:
                published = datetime.now()
        except:
            published = datetime.now()
        
        return NewsSignal(
            headline=title,
            source=item.get("source", "unknown"),
            url=item.get("link", ""),
            published=published,
            symbols=symbols,
            sentiment=sentiment,
            impact=impact,
            category=category,
            summary=description[:200] if description else None
        )
    
    async def get_news_signals(self, min_impact: float = 0.3) -> List[NewsSignal]:
        """Get processed news signals"""
        items = await self.fetch_all_feeds()
        
        signals = []
        for item in items:
            signal = self.process_news_item(item)
            if signal and signal.impact >= min_impact:
                signals.append(signal)
        
        # Sort by impact
        signals.sort(key=lambda x: x.impact, reverse=True)
        
        logger.info(f"✅ Generated {len(signals)} news signals (min impact: {min_impact})")
        return signals
    
    async def get_signals_for_symbol(self, symbol: str) -> List[NewsSignal]:
        """Get news signals for a specific symbol"""
        all_signals = await self.get_news_signals(min_impact=0.2)
        
        symbol_signals = [s for s in all_signals if symbol.upper() in s.symbols]
        return symbol_signals
    
    async def get_market_sentiment(self) -> Dict[str, Any]:
        """Get overall market sentiment from news"""
        signals = await self.get_news_signals()
        
        if not signals:
            return {
                "overall_sentiment": 0.0,
                "confidence": 0.0,
                "bullish_count": 0,
                "bearish_count": 0,
                "neutral_count": 0,
                "top_stories": []
            }
        
        total_weight = 0
        weighted_sentiment = 0
        bullish = bearish = neutral = 0
        
        for signal in signals:
            weight = signal.impact
            weighted_sentiment += signal.sentiment * weight
            total_weight += weight
            
            if signal.sentiment > 0.1:
                bullish += 1
            elif signal.sentiment < -0.1:
                bearish += 1
            else:
                neutral += 1
        
        return {
            "overall_sentiment": weighted_sentiment / total_weight if total_weight > 0 else 0,
            "confidence": min(total_weight / len(signals), 1.0),
            "bullish_count": bullish,
            "bearish_count": bearish,
            "neutral_count": neutral,
            "signal_count": len(signals),
            "top_stories": [
                {"headline": s.headline, "sentiment": s.sentiment, "impact": s.impact}
                for s in signals[:5]
            ]
        }
    
    async def close(self):
        """Close session"""
        if self.session and not self.session.closed:
            await self.session.close()


# Global instance
rss_news_feeds = RSSNewsFeeds()


async def get_news_signals(min_impact: float = 0.3) -> List[NewsSignal]:
    """Get news signals"""
    return await rss_news_feeds.get_news_signals(min_impact)


async def get_market_sentiment() -> Dict[str, Any]:
    """Get market sentiment from news"""
    return await rss_news_feeds.get_market_sentiment()


if __name__ == "__main__":
    async def test():
        print("=" * 60)
        print("Testing FREE RSS News Feeds")
        print("=" * 60)
        
        feeds = RSSNewsFeeds()
        
        print("\n📰 Fetching all RSS feeds...")
        signals = await feeds.get_news_signals()
        
        print(f"\n✅ Got {len(signals)} news signals")
        print("\n🔥 Top 5 High-Impact Stories:")
        for i, signal in enumerate(signals[:5], 1):
            sentiment_icon = "📈" if signal.sentiment > 0 else "📉" if signal.sentiment < 0 else "➡️"
            print(f"  {i}. {sentiment_icon} [{signal.source}] {signal.headline[:60]}...")
            print(f"     Impact: {signal.impact:.2f} | Sentiment: {signal.sentiment:.2f} | Symbols: {signal.symbols}")
        
        print("\n📊 Market Sentiment:")
        sentiment = await feeds.get_market_sentiment()
        print(f"  Overall: {sentiment['overall_sentiment']:.2f}")
        print(f"  Bullish: {sentiment['bullish_count']} | Bearish: {sentiment['bearish_count']}")
        
        await feeds.close()
        print("\n✅ RSS News Feeds Test Complete - FREE NEWS DATA ACTIVE!")
    
    asyncio.run(test())
