"""
Yahoo Finance Data Source - Free Market Data Fallback
Provides real-time and historical market data for stocks and crypto
"""

import yfinance as yf
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class YahooFinanceDataSource:
    """Yahoo Finance data source for free market data"""
    
    def __init__(self):
        self.logger = logger
        self.logger.info("📊 Yahoo Finance Data Source initialized")
    
    def get_real_time_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time market data from Yahoo Finance"""
        try:
            # Convert symbol format
            yahoo_symbol = self._convert_symbol(symbol)
            
            # Get ticker
            ticker = yf.Ticker(yahoo_symbol)
            
            # Get current data
            info = ticker.info
            
            # Get latest price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
            
            if not current_price:
                # Try fast_info
                try:
                    current_price = ticker.fast_info.get('lastPrice')
                except:
                    pass
            
            if current_price and current_price > 0:
                return {
                    'symbol': symbol,
                    'price': float(current_price),
                    'volume': info.get('volume', 0),
                    'bid': info.get('bid', current_price),
                    'ask': info.get('ask', current_price),
                    'timestamp': datetime.now()
                }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Yahoo Finance failed for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, timeframe: str = '1Min', limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical market data from Yahoo Finance"""
        try:
            # Convert symbol format
            yahoo_symbol = self._convert_symbol(symbol)
            
            # Convert timeframe
            interval_map = {
                '1Min': '1m',
                '5Min': '5m',
                '15Min': '15m',
                '30Min': '30m',
                '1Hour': '1h',
                '1Day': '1d'
            }
            interval = interval_map.get(timeframe, '1m')
            
            # Determine period based on interval
            if interval in ['1m', '5m']:
                period = '1d'  # 1 minute data only available for last 7 days
            elif interval in ['15m', '30m']:
                period = '5d'
            elif interval == '1h':
                period = '1mo'
            else:
                period = '3mo'
            
            # Get ticker
            ticker = yf.Ticker(yahoo_symbol)
            
            # Get historical data
            hist = ticker.history(period=period, interval=interval)
            
            # Convert to list
            result = []
            for index, row in hist.iterrows():
                result.append({
                    'timestamp': index,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            
            # Return last 'limit' bars
            return result[-limit:] if len(result) > limit else result
            
        except Exception as e:
            self.logger.debug(f"Yahoo Finance historical data failed for {symbol}: {e}")
            return []
    
    def _convert_symbol(self, symbol: str) -> str:
        """Convert PROMETHEUS symbol format to Yahoo Finance format"""
        # Crypto conversions
        crypto_map = {
            'BTC/USD': 'BTC-USD',
            'ETH/USD': 'ETH-USD',
            'SOL/USD': 'SOL-USD',
            'DOGE/USD': 'DOGE-USD',
            'ADA/USD': 'ADA-USD'
        }
        
        if symbol in crypto_map:
            return crypto_map[symbol]
        
        # Stock symbols stay the same
        return symbol
    
    async def get_real_time_data_async(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Async wrapper for get_real_time_data"""
        return self.get_real_time_data(symbol)
    
    async def get_historical_data_async(self, symbol: str, timeframe: str = '1Min', limit: int = 100) -> List[Dict[str, Any]]:
        """Async wrapper for get_historical_data"""
        return self.get_historical_data(symbol, timeframe, limit)

