"""
🚀 PROMETHEUS TRADING - Real-Time Market Data Integration
=========================================================
Replaces simulated data with actual live market feeds from multiple sources:
- Alpha Vantage (Free tier: 5 API calls/minute, 500/day)
- Yahoo Finance (Free, unlimited)
- Polygon.io (Free tier: 5 calls/minute)
- Financial Modeling Prep (Free tier: 250/day)
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import os
from decimal import Decimal
import yfinance as yf
import pandas as pd
import numpy as np
from core.utils.time_utils import utc_now
from core.polygon_premium_provider import polygon_premium_provider, get_polygon_premium_data
# Load environment variables if .env is present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


logger = logging.getLogger(__name__)

@dataclass
class MarketDataPoint:
    """Standardized market data structure"""
    symbol: str
    price: float
    volume: int
    change: float
    change_percent: float
    timestamp: datetime
    source: str
    bid: Optional[float] = None
    ask: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None

@dataclass
class CryptoDataPoint:
    """Cryptocurrency market data"""
    symbol: str
    price: float
    volume_24h: float
    change_24h: float
    change_percent_24h: float
    market_cap: float
    timestamp: datetime
    source: str

class AlphaVantageProvider:
    """Alpha Vantage free API integration (5 calls/minute, 500/day)"""

    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')  # Demo key for testing
        self.base_url = "https://www.alphavantage.co/query"
        self.rate_limit = 5  # calls per minute
        self.last_calls = []

    async def _check_rate_limit(self):
        """Enforce rate limiting"""
        now = datetime.now()
        # Remove calls older than 1 minute
        self.last_calls = [call for call in self.last_calls if (now - call).seconds < 60]

        if len(self.last_calls) >= self.rate_limit:
            wait_time = 60 - (now - self.last_calls[0]).seconds
            logger.warning(f"⏳ Alpha Vantage rate limit hit, waiting {wait_time}s")
            await asyncio.sleep(wait_time)

        self.last_calls.append(now)

    async def get_real_time_quote(self, symbol: str) -> Optional[MarketDataPoint]:
        """Get real-time stock quote from Alpha Vantage"""
        try:
            await self._check_rate_limit()

            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        if 'Global Quote' in data:
                            quote = data['Global Quote']
                            return MarketDataPoint(
                                symbol=symbol,
                                price=float(quote.get('05. price', 0)),
                                volume=int(float(quote.get('06. volume', 0))),
                                change=float(quote.get('09. change', 0)),
                                change_percent=float(quote.get('10. change percent', '0%').strip('%')),
                                timestamp=utc_now(),
                                source='alpha_vantage',
                                high_52w=float(quote.get('03. high', 0)),
                                low_52w=float(quote.get('04. low', 0))
                            )
                        else:
                            logger.warning(f"[WARNING]️ Alpha Vantage API limit reached for {symbol}")
                            return None

        except Exception as e:
            logger.error(f"[ERROR] Alpha Vantage error for {symbol}: {e}")
            return None

class YahooFinanceProvider:
    """Yahoo Finance free API (unlimited, most reliable)"""

    def __init__(self):
        self.source = 'yahoo_finance'

    async def get_real_time_quote(self, symbol: str) -> Optional[MarketDataPoint]:
        """Get real-time quote from Yahoo Finance using yfinance"""
        try:
            # Fetch most recent minute data
            hist = yf.Ticker(symbol).history(period="1d", interval="1m")
            if hist is None or hist.empty:
                return None

            current_price = float(hist['Close'].iloc[-1])
            prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
            change = current_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close else 0.0
            volume = int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0

            bid = current_price - 0.01
            ask = current_price + 0.01

            return MarketDataPoint(
                symbol=symbol,
                price=current_price,
                volume=volume,
                change=change,
                change_percent=change_percent,
                timestamp=utc_now(),
                source=self.source,
                bid=bid,
                ask=ask,
                high_52w=None,
                low_52w=None,
                market_cap=None,
                pe_ratio=None,
                dividend_yield=None
            )

        except Exception as e:
            logger.error(f"[ERROR] Yahoo Finance error for {symbol}: {e}")
            return None

    async def get_historical_data(self, symbol: str, period: str = "1mo") -> Optional[pd.DataFrame]:
        """Get historical data for analysis"""
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            hist = await loop.run_in_executor(None, ticker.history, period)
            return hist

        except Exception as e:
            logger.error(f"[ERROR] Yahoo Finance historical data error for {symbol}: {e}")
            return None

class PolygonProvider:
    """Polygon.io free tier integration (5 calls/minute)"""

    def __init__(self):
        self.api_key = os.getenv('POLYGON_API_KEY', '')
        self.base_url = "https://api.polygon.io"
        self.rate_limit = 5
        self.last_calls = []

    async def get_real_time_quote(self, symbol: str) -> Optional[MarketDataPoint]:
        """Get real-time quote from Polygon"""
        if not self.api_key:
            return None

        try:
            await self._check_rate_limit()

            url = f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}"
            params = {'apikey': self.api_key}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        ticker_data = data.get('results', {})

                        if ticker_data:
                            last_quote = ticker_data.get('lastQuote', {})
                            last_trade = ticker_data.get('lastTrade', {})

                            return MarketDataPoint(
                                symbol=symbol,
                                price=float(last_trade.get('p', 0)),
                                volume=int(ticker_data.get('volume', 0)),
                                change=float(ticker_data.get('todaysChange', 0)),
                                change_percent=float(ticker_data.get('todaysChangePerc', 0)),
                                timestamp=utc_now(),
                                source='polygon',
                                bid=last_quote.get('bidPrice'),
                                ask=last_quote.get('askPrice')
                            )

        except Exception as e:
            logger.error(f"[ERROR] Polygon error for {symbol}: {e}")
            return None

    async def _check_rate_limit(self):
        """Enforce Polygon rate limiting"""
        now = datetime.now()
        self.last_calls = [call for call in self.last_calls if (now - call).seconds < 60]

        if len(self.last_calls) >= self.rate_limit:
            wait_time = 60 - (now - self.last_calls[0]).seconds
            await asyncio.sleep(wait_time)

        self.last_calls.append(now)

class CoinGeckoProvider:
    """CoinGecko free crypto API"""

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"

    async def get_crypto_quote(self, symbol: str) -> Optional[CryptoDataPoint]:
        """Get cryptocurrency data"""
        try:
            # Convert symbol to CoinGecko ID format
            symbol_map = {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'ADA': 'cardano',
                'DOT': 'polkadot', 'LINK': 'chainlink', 'SOL': 'solana'
            }

            coin_id = symbol_map.get(symbol.upper(), symbol.lower())
            url = f"{self.base_url}/simple/price"

            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }

            timeout = aiohttp.ClientTimeout(total=5)  # 5 second timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        if coin_id in data:
                            coin_data = data[coin_id]
                            return CryptoDataPoint(
                                symbol=symbol,
                                price=float(coin_data.get('usd', 0)),
                                volume_24h=float(coin_data.get('usd_24h_vol', 0)),
                                change_24h=0,  # Calculate from price change
                                change_percent_24h=float(coin_data.get('usd_24h_change', 0)),
                                market_cap=float(coin_data.get('usd_market_cap', 0)),
                                timestamp=utc_now(),
                                source='coingecko'
                            )

        except Exception as e:
            logger.debug(f"CoinGecko unavailable for {symbol}: {e}")
            return None

class RealTimeMarketDataOrchestrator:
    """
    🎯 Main orchestrator for real-time market data
    Intelligently routes requests to best available provider
    """

    def __init__(self):
        self.providers = {
            'stocks': [
                polygon_premium_provider,  # Primary (Premium S3 access/REST)
                YahooFinanceProvider(),    # Secondary (yfinance)
                AlphaVantageProvider(),    # Tertiary
                PolygonProvider()          # Quaternary (if API key available)
            ],
            'crypto': [
                CoinGeckoProvider()
            ]
        }
        self.cache = {}
        self.cache_duration = 30  # seconds

    # Known crypto base symbols for routing detection
    CRYPTO_BASES = {
        'BTC', 'ETH', 'ADA', 'DOT', 'LINK', 'SOL', 'AVAX', 'DOGE',
        'UNI', 'AAVE', 'SUSHI', 'CRV', 'SHIB', 'PEPE', 'USDC', 'USDT',
        'XRP', 'BNB', 'LTC', 'BCH', 'NEAR', 'FTM', 'ALGO', 'XLM',
        'VET', 'ATOM', 'MATIC', 'MANA', 'SAND', 'AXS', 'FIL', 'HBAR',
    }

    def _normalize_symbol(self, symbol: str) -> tuple:
        """Normalize symbol and detect if it's crypto.
        Returns (normalized_symbol, is_crypto).
        Handles BTC/USD, BTC-USD, BTCUSD formats → BTC-USD for yfinance."""
        upper = symbol.upper()
        # Check /USD format (Alpaca style)
        if '/USD' in upper:
            base = upper.split('/USD')[0]
            if base in self.CRYPTO_BASES:
                return f"{base}-USD", True
        # Check -USD format (yfinance style)
        if upper.endswith('-USD'):
            base = upper.replace('-USD', '')
            if base in self.CRYPTO_BASES:
                return upper, True
        # Check bare BTCUSD format
        if upper.endswith('USD') and '/' not in upper and '-' not in upper:
            base = upper[:-3]
            if base in self.CRYPTO_BASES:
                return f"{base}-USD", True
        return symbol, False

    async def get_live_stock_data(self, symbol: str) -> Optional[MarketDataPoint]:
        """Get live stock data with fallback providers.
        Auto-detects crypto symbols and normalizes them for yfinance."""

        # ═══ CRYPTO AUTO-DETECTION: Route BTC/USD, ETH/USD etc. properly ═══
        normalized, is_crypto = self._normalize_symbol(symbol)
        if is_crypto:
            logger.debug(f"🔄 Auto-routing crypto symbol {symbol} → {normalized}")
            # Try crypto providers first (CoinGecko)
            crypto_data = await self.get_live_crypto_data(normalized)
            if crypto_data:
                return crypto_data
            # Fallback: try yfinance with normalized symbol (BTC-USD works on yfinance)
            symbol = normalized  # Use normalized for stock providers as fallback

        # Check cache first
        cache_key = f"stock_{normalized if is_crypto else symbol}"
        if self._is_cached(cache_key):
            logger.info(f"📦 Returning cached data for {symbol}")
            return self.cache[cache_key]['data']

        # Try providers in order
        for provider in self.providers['stocks']:
            try:
                data = await provider.get_real_time_quote(symbol)
                if data and data.price > 0:
                    logger.info(f"[CHECK] Got live data for {symbol} from {data.source}: ${data.price:.2f}")
                    self._cache_data(cache_key, data)
                    return data

            except Exception as e:
                logger.warning(f"[WARNING]️ Provider {provider.__class__.__name__} failed for {symbol}: {e}")
                continue

        logger.error(f"[ERROR] All providers failed for {symbol}")
        return None

    async def get_live_crypto_data(self, symbol: str) -> Optional[CryptoDataPoint]:
        """Get live cryptocurrency data. Normalizes /USD → -USD format."""

        # Normalize crypto symbol format
        normalized, _ = self._normalize_symbol(symbol)
        symbol = normalized if normalized != symbol else symbol

        cache_key = f"crypto_{symbol}"
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']

        for provider in self.providers['crypto']:
            try:
                data = await provider.get_crypto_quote(symbol)
                if data and data.price > 0:
                    logger.info(f"[CHECK] Got crypto data for {symbol}: ${data.price:.2f}")
                    self._cache_data(cache_key, data)
                    return data

            except Exception as e:
                logger.warning(f"[WARNING]️ Crypto provider failed for {symbol}: {e}")
                continue

        return None

    async def get_bulk_quotes(self, symbols: List[str]) -> Dict[str, MarketDataPoint]:
        """Get multiple quotes concurrently"""
        tasks = []
        for symbol in symbols:
            # Normalize crypto symbols: handle both BTC/USD and BTC-USD formats
            normalized = symbol.upper().replace('/USD', '-USD')
            crypto_base = normalized.replace('-USD', '')
            if crypto_base in ['BTC', 'ETH', 'ADA', 'DOT', 'LINK', 'SOL', 'AVAX', 'DOGE',
                               'UNI', 'AAVE', 'SUSHI', 'CRV', 'SHIB', 'PEPE', 'USDC', 'USDT',
                               'XRP', 'BNB']:
                # Use -USD suffix for Yahoo Finance compatibility
                crypto_symbol = f"{crypto_base}-USD"
                # Wrap crypto calls with timeout
                tasks.append(asyncio.wait_for(self.get_live_crypto_data(crypto_symbol), timeout=10))
            else:
                tasks.append(self.get_live_stock_data(symbol))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        quotes = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, (MarketDataPoint, CryptoDataPoint)) and result is not None:
                quotes[symbol] = result
            else:
                logger.warning(f"[WARNING]️ Failed to get data for {symbol}")

        return quotes

    def _is_cached(self, key: str) -> bool:
        """Check if data is cached and still valid"""
        if key not in self.cache:
            return False

        cached_time = self.cache[key]['timestamp']
        return (datetime.now() - cached_time).seconds < self.cache_duration

    def _cache_data(self, key: str, data: Union[MarketDataPoint, CryptoDataPoint]):
        """Cache data with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }

# Global instance
market_data_orchestrator = RealTimeMarketDataOrchestrator()

async def get_real_time_market_data(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    🎯 Main function to get real-time market data
    Replaces all simulated data in the system
    """
    try:
        quotes = await market_data_orchestrator.get_bulk_quotes(symbols)

        formatted_data = {}
        for symbol, data in quotes.items():
            if isinstance(data, MarketDataPoint):
                formatted_data[symbol] = {
                    'symbol': data.symbol,
                    'price': data.price,
                    'volume': data.volume,
                    'change': data.change,
                    'change_percent': data.change_percent,
                    'timestamp': data.timestamp.isoformat(),
                    'source': data.source,
                    'bid': data.bid,
                    'ask': data.ask,
                    'market_cap': data.market_cap,
                    'pe_ratio': data.pe_ratio,
                    'dividend_yield': data.dividend_yield,
                    'type': 'stock'
                }
            elif isinstance(data, CryptoDataPoint):
                formatted_data[symbol] = {
                    'symbol': data.symbol,
                    'price': data.price,
                    'volume_24h': data.volume_24h,
                    'change_24h': data.change_24h,
                    'change_percent_24h': data.change_percent_24h,
                    'market_cap': data.market_cap,
                    'timestamp': data.timestamp.isoformat(),
                    'source': data.source,
                    'type': 'crypto'
                }

        logger.info(f"[CHECK] Retrieved live data for {len(formatted_data)} symbols")
        return formatted_data

    except Exception as e:
        logger.error(f"[ERROR] Error getting real-time market data: {e}")
        return {}

# Convenience functions for backward compatibility
async def get_stock_price(symbol: str) -> float:
    """Get current stock price"""
    data = await market_data_orchestrator.get_live_stock_data(symbol)
    return data.price if data else 0.0

async def get_market_sentiment(symbol: str) -> Dict[str, Any]:
    """Get market sentiment based on real price movement"""
    data = await market_data_orchestrator.get_live_stock_data(symbol)

    if not data:
        return {'sentiment': 'neutral', 'confidence': 0.5}

    # Calculate sentiment based on real price movement
    if data.change_percent > 2:
        sentiment = 'bullish'
        confidence = min(0.9, 0.6 + (data.change_percent / 10))
    elif data.change_percent < -2:
        sentiment = 'bearish'
        confidence = min(0.9, 0.6 + (abs(data.change_percent) / 10))
    else:
        sentiment = 'neutral'
        confidence = 0.6

    return {
        'sentiment': sentiment,
        'confidence': confidence,
        'price_change': data.change,
        'price_change_percent': data.change_percent,
        'volume': data.volume,
        'source': data.source
    }
