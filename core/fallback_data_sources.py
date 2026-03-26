"""
Fallback Data Sources and Broker Failover System
Provides alternative data sources when primary brokers fail
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from core.error_handling import (
    MarketDataError, ConnectionError, TradingError, ErrorSeverity,
    error_logger, create_market_data_error
)

logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    """Standardized market data structure"""
    symbol: str
    price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: Optional[int] = None
    timestamp: datetime = None
    source: str = "unknown"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class FallbackDataProvider:
    """Base class for fallback data providers"""
    
    def __init__(self, name: str, priority: int = 1):
        self.name = name
        self.priority = priority  # Lower number = higher priority
        self.last_success = None
        self.failure_count = 0
        self.max_failures = 5
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get market data - to be implemented by subclasses"""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.failure_count < self.max_failures
    
    def record_success(self):
        """Record successful data fetch"""
        self.last_success = datetime.now()
        self.failure_count = 0
    
    def record_failure(self):
        """Record failed data fetch"""
        self.failure_count += 1

class AlphaVantageProvider(FallbackDataProvider):
    """Alpha Vantage fallback data provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Alpha Vantage", priority=1)
        self.api_key = api_key or "demo"  # Use demo key if none provided
        self.base_url = "https://www.alphavantage.co/query"
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get market data from Alpha Vantage"""
        try:
            session = await self._get_session()
            
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'Global Quote' in data:
                        quote = data['Global Quote']
                        market_data = MarketData(
                            symbol=symbol,
                            price=float(quote.get('05. price', 0)),
                            bid=float(quote.get('03. high', 0)),  # Using high as bid approximation
                            ask=float(quote.get('04. low', 0)),   # Using low as ask approximation
                            volume=int(quote.get('06. volume', 0)),
                            source=self.name
                        )
                        
                        self.record_success()
                        logger.info(f"✅ Alpha Vantage data for {symbol}: ${market_data.price}")
                        return market_data
                    else:
                        raise MarketDataError(f"No quote data for {symbol}")
                else:
                    raise ConnectionError(f"Alpha Vantage HTTP {response.status}")
                    
        except Exception as e:
            self.record_failure()
            logger.warning(f"Alpha Vantage failed for {symbol}: {e}")
            return None
        finally:
            if self.session and not self.session.closed:
                await self.session.close()

class YahooFinanceProvider(FallbackDataProvider):
    """Yahoo Finance fallback data provider"""
    
    def __init__(self):
        super().__init__("Yahoo Finance", priority=2)
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get market data from Yahoo Finance"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/{symbol}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'chart' in data and 'result' in data['chart']:
                        result = data['chart']['result'][0]
                        meta = result.get('meta', {})
                        
                        market_data = MarketData(
                            symbol=symbol,
                            price=float(meta.get('regularMarketPrice', 0)),
                            bid=float(meta.get('bid', 0)),
                            ask=float(meta.get('ask', 0)),
                            volume=int(meta.get('regularMarketVolume', 0)),
                            source=self.name
                        )
                        
                        self.record_success()
                        logger.info(f"✅ Yahoo Finance data for {symbol}: ${market_data.price}")
                        return market_data
                    else:
                        raise MarketDataError(f"No chart data for {symbol}")
                else:
                    raise ConnectionError(f"Yahoo Finance HTTP {response.status}")
                    
        except Exception as e:
            self.record_failure()
            logger.warning(f"Yahoo Finance failed for {symbol}: {e}")
            return None
        finally:
            if self.session and not self.session.closed:
                await self.session.close()

class PolygonProvider(FallbackDataProvider):
    """Polygon.io fallback data provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Polygon.io", priority=3)
        self.api_key = api_key
        self.base_url = "https://api.polygon.io/v2"
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get market data from Polygon.io"""
        if not self.api_key:
            logger.debug("Polygon.io API key not provided, skipping")
            return None
            
        try:
            session = await self._get_session()
            url = f"{self.base_url}/snapshot/locale/us/markets/stocks/tickers/{symbol}"
            
            params = {'apikey': self.api_key}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'ticker' in data:
                        ticker = data['ticker']
                        market_data = MarketData(
                            symbol=symbol,
                            price=float(ticker.get('lastQuote', {}).get('P', 0)),
                            bid=float(ticker.get('lastQuote', {}).get('p', 0)),
                            ask=float(ticker.get('lastQuote', {}).get('P', 0)),
                            volume=int(ticker.get('lastTrade', {}).get('s', 0)),
                            source=self.name
                        )
                        
                        self.record_success()
                        logger.info(f"✅ Polygon.io data for {symbol}: ${market_data.price}")
                        return market_data
                    else:
                        raise MarketDataError(f"No ticker data for {symbol}")
                else:
                    raise ConnectionError(f"Polygon.io HTTP {response.status}")
                    
        except Exception as e:
            self.record_failure()
            logger.warning(f"Polygon.io failed for {symbol}: {e}")
            return None
        finally:
            if self.session and not self.session.closed:
                await self.session.close()

class FallbackDataManager:
    """Manages multiple fallback data sources"""
    
    def __init__(self):
        self.providers: List[FallbackDataProvider] = []
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available fallback providers"""
        # Add providers in order of preference
        self.providers.append(AlphaVantageProvider())
        self.providers.append(YahooFinanceProvider())
        self.providers.append(PolygonProvider())
        
        # Sort by priority
        self.providers.sort(key=lambda p: p.priority)
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get market data from fallback sources"""
        for provider in self.providers:
            if not provider.is_available():
                logger.debug(f"Skipping {provider.name} - too many failures")
                continue
            
            try:
                data = await provider.get_market_data(symbol)
                if data and data.price > 0:
                    logger.info(f"✅ Fallback data from {provider.name} for {symbol}")
                    return data
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                provider.record_failure()
                continue
        
        logger.error(f"❌ All fallback providers failed for {symbol}")
        return None
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        for provider in self.providers:
            status[provider.name] = {
                'available': provider.is_available(),
                'priority': provider.priority,
                'failure_count': provider.failure_count,
                'last_success': provider.last_success.isoformat() if provider.last_success else None
            }
        return status

class BrokerFailoverManager:
    """Manages failover between brokers"""
    
    def __init__(self):
        self.primary_broker = None
        self.fallback_broker = None
        self.fallback_data_manager = FallbackDataManager()
        self.current_broker = None
        self.failover_active = False
    
    def set_brokers(self, primary_broker, fallback_broker):
        """Set primary and fallback brokers"""
        self.primary_broker = primary_broker
        self.fallback_broker = fallback_broker
        self.current_broker = primary_broker
    
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get market data with automatic failover"""
        # Try current broker first
        if self.current_broker:
            try:
                data = await self.current_broker.get_market_data(symbol)
                if data and data.get('price', 0) > 0:
                    return data
            except Exception as e:
                logger.warning(f"Current broker failed for {symbol}: {e}")
                await self._handle_broker_failure()
        
        # Try fallback broker
        if self.fallback_broker and not self.failover_active:
            try:
                data = await self.fallback_broker.get_market_data(symbol)
                if data and data.get('price', 0) > 0:
                    logger.info(f"✅ Using fallback broker for {symbol}")
                    return data
            except Exception as e:
                logger.warning(f"Fallback broker failed for {symbol}: {e}")
        
        # Try fallback data sources
        try:
            fallback_data = await self.fallback_data_manager.get_market_data(symbol)
            if fallback_data:
                return {
                    'symbol': fallback_data.symbol,
                    'price': fallback_data.price,
                    'bid': fallback_data.bid,
                    'ask': fallback_data.ask,
                    'volume': fallback_data.volume,
                    'timestamp': fallback_data.timestamp,
                    'source': f"fallback_{fallback_data.source}"
                }
        except Exception as e:
            logger.error(f"All fallback sources failed for {symbol}: {e}")
        
        # All sources failed
        raise MarketDataError(
            message=f"All data sources failed for {symbol}",
            broker="all",
            symbol=symbol
        )
    
    async def _handle_broker_failure(self):
        """Handle broker failure and switch to fallback"""
        if not self.failover_active:
            self.failover_active = True
            logger.warning("🚨 Broker failover activated")
            
            # Switch to fallback broker
            if self.fallback_broker:
                self.current_broker = self.fallback_broker
                logger.info("🔄 Switched to fallback broker")
            
            # Log the failure
            from core.error_handling import TradingError, ErrorSeverity, ErrorCategory, ErrorContext
            failure_error = TradingError(
                message="Primary broker failed, switched to fallback",
                category=ErrorCategory.CONNECTION,
                severity=ErrorSeverity.HIGH,
                context=ErrorContext(
                    broker=self.primary_broker.__class__.__name__ if self.primary_broker else "unknown",
                    operation="failover"
                )
            )
            await error_logger.log_error(failure_error)
    
    async def restore_primary_broker(self):
        """Restore primary broker when it becomes available"""
        if self.failover_active and self.primary_broker:
            try:
                # Test primary broker connection
                if hasattr(self.primary_broker, 'check_connection'):
                    is_connected = await self.primary_broker.check_connection()
                    if is_connected:
                        self.current_broker = self.primary_broker
                        self.failover_active = False
                        logger.info("✅ Primary broker restored")
                        return True
            except Exception as e:
                logger.debug(f"Primary broker still unavailable: {e}")
        
        return False
    
    def get_failover_status(self) -> Dict[str, Any]:
        """Get current failover status"""
        return {
            'failover_active': self.failover_active,
            'current_broker': self.current_broker.__class__.__name__ if self.current_broker else None,
            'primary_broker': self.primary_broker.__class__.__name__ if self.primary_broker else None,
            'fallback_broker': self.fallback_broker.__class__.__name__ if self.fallback_broker else None,
            'fallback_providers': self.fallback_data_manager.get_provider_status()
        }

# Global instances
fallback_data_manager = FallbackDataManager()
broker_failover_manager = BrokerFailoverManager()

# Utility functions
async def get_market_data_with_fallback(symbol: str, primary_broker=None, fallback_broker=None) -> Dict[str, Any]:
    """Get market data with automatic failover"""
    if primary_broker and fallback_broker:
        broker_failover_manager.set_brokers(primary_broker, fallback_broker)
        return await broker_failover_manager.get_market_data(symbol)
    else:
        # Use fallback data sources only
        fallback_data = await fallback_data_manager.get_market_data(symbol)
        if fallback_data:
            return {
                'symbol': fallback_data.symbol,
                'price': fallback_data.price,
                'bid': fallback_data.bid,
                'ask': fallback_data.ask,
                'volume': fallback_data.volume,
                'timestamp': fallback_data.timestamp,
                'source': f"fallback_{fallback_data.source}"
            }
        else:
            raise MarketDataError(
                message=f"No data available for {symbol} from any source",
                broker="all",
                symbol=symbol
            )
