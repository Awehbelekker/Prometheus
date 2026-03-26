"""
🚀 PROMETHEUS TRADING - Polygon.io Premium Market Data Provider
==============================================================
Enhanced market data provider using Polygon.io premium S3 access
for high-frequency, real-time market data with minimal latency.

Features:
- Direct S3 access to Polygon.io flatfiles
- Real-time tick data and aggregates
- Historical data with microsecond precision
- Options, forex, and crypto data
- Unlimited API calls (S3 access)
"""

import asyncio
import aiohttp
import boto3
import logging
import json
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import pandas as pd
from decimal import Decimal
from core.utils.time_utils import utc_now

logger = logging.getLogger(__name__)

@dataclass
class PolygonPremiumDataPoint:
    """Enhanced data point from Polygon.io premium service"""
    symbol: str
    price: float
    volume: int
    change: float
    change_percent: float
    timestamp: datetime
    source: str = 'polygon_premium'
    
    # Enhanced fields from premium service
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None
    high: Optional[float] = None
    low: Optional[float] = None
    open: Optional[float] = None
    close: Optional[float] = None
    vwap: Optional[float] = None
    
    # Market microstructure
    trade_count: Optional[int] = None
    spread: Optional[float] = None
    market_cap: Optional[int] = None
    
    # Options data (if applicable)
    implied_volatility: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None

class PolygonPremiumProvider:
    """
    🎯 Polygon.io Premium Market Data Provider
    Uses S3 direct access for ultra-low latency data
    """
    
    def __init__(self):
        # Load .env for credentials if present
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except Exception:
            pass
        self.access_key_id = os.getenv('POLYGON_ACCESS_KEY_ID')
        self.secret_access_key = os.getenv('POLYGON_SECRET_ACCESS_KEY')
        self.api_key = os.getenv('POLYGON_API_KEY')
        self.s3_endpoint = os.getenv('POLYGON_S3_ENDPOINT', 'https://files.polygon.io')
        self.bucket = os.getenv('POLYGON_S3_BUCKET', 'flatfiles')
        
        # Initialize S3 client for direct flatfile access
        self.s3_client = None
        if self.access_key_id and self.secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                endpoint_url=self.s3_endpoint
            )
            logger.info("[CHECK] Polygon.io Premium S3 client initialized")
        else:
            logger.warning("[WARNING]️ Polygon.io Premium S3 credentials not found")

        # Check API key availability
        if self.api_key:
            logger.info("[CHECK] Polygon.io API key configured")
        else:
            logger.warning("[WARNING]️ Polygon.io API key not found")
    
    async def get_real_time_quote(self, symbol: str) -> Optional[PolygonPremiumDataPoint]:
        """Get real-time quote using premium S3 access"""
        try:
            if not self.s3_client:
                # Allow REST API usage if an API key is configured even when S3 is not
                if self.api_key:
                    logger.info("[WARNING]️ Polygon Premium S3 not configured; falling back to REST API")
                    return await self._get_rest_api_quote(symbol)
                logger.warning("[ERROR] Polygon.io Premium not configured (no S3 or API key)")
                return None

            # S3 may be configured; for now still use REST API while flatfile access is implemented
            return await self._get_rest_api_quote(symbol)

        except Exception as e:
            logger.error(f"[ERROR] Polygon Premium error for {symbol}: {e}")
            return None
    
    async def _get_rest_api_quote(self, symbol: str) -> Optional[PolygonPremiumDataPoint]:
        """Fallback to REST API for real-time quotes"""
        try:
            # Use the premium API endpoint
            url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}"
            params = {
                'apikey': self.api_key  # Using the proper API key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        ticker_data = data.get('results', {})
                        
                        if ticker_data:
                            last_quote = ticker_data.get('lastQuote', {})
                            last_trade = ticker_data.get('lastTrade', {})
                            day_data = ticker_data.get('day', {})
                            prev_day = ticker_data.get('prevDay', {})
                            
                            current_price = last_trade.get('p', 0)
                            prev_close = prev_day.get('c', current_price)
                            change = current_price - prev_close
                            change_percent = (change / prev_close * 100) if prev_close else 0
                            
                            return PolygonPremiumDataPoint(
                                symbol=symbol,
                                price=float(current_price),
                                volume=int(day_data.get('v', 0)),
                                change=float(change),
                                change_percent=float(change_percent),
                                timestamp=utc_now(),
                                source='polygon_premium',
                                bid=float(last_quote.get('b', 0)) if last_quote.get('b') else None,
                                ask=float(last_quote.get('a', 0)) if last_quote.get('a') else None,
                                bid_size=int(last_quote.get('s', 0)) if last_quote.get('s') else None,
                                ask_size=int(last_quote.get('S', 0)) if last_quote.get('S') else None,
                                high=float(day_data.get('h', 0)) if day_data.get('h') else None,
                                low=float(day_data.get('l', 0)) if day_data.get('l') else None,
                                open=float(day_data.get('o', 0)) if day_data.get('o') else None,
                                close=float(day_data.get('c', 0)) if day_data.get('c') else None,
                                vwap=float(day_data.get('vw', 0)) if day_data.get('vw') else None,
                                trade_count=int(last_trade.get('s', 0)) if last_trade.get('s') else None,
                                spread=float(last_quote.get('a', 0) - last_quote.get('b', 0)) if last_quote.get('a') and last_quote.get('b') else None
                            )
                            
        except Exception as e:
            logger.debug(f"Polygon REST unavailable for {symbol}: {e}")
            return None
    
    async def get_s3_flatfile_data(self, symbol: str, date: str = None) -> Optional[pd.DataFrame]:
        """
        Access Polygon.io S3 flatfiles directly for historical data
        Format: s3://flatfiles/us_stocks_sip/day_aggs_v1/2023/01/01.parquet
        """
        try:
            if not self.s3_client:
                return None
            
            if not date:
                date = datetime.now().strftime('%Y/%m/%d')
            else:
                # Convert date format if needed
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                date = date_obj.strftime('%Y/%m/%d')
            
            # Construct S3 key for daily aggregates
            s3_key = f"us_stocks_sip/day_aggs_v1/{date}.parquet"
            
            logger.info(f"📊 Fetching S3 flatfile: {s3_key}")
            
            # Download the parquet file
            response = self.s3_client.get_object(Bucket=self.bucket, Key=s3_key)
            
            # Read parquet data
            df = pd.read_parquet(response['Body'])
            
            # Filter for specific symbol if provided
            if symbol:
                df = df[df['ticker'] == symbol.upper()]
            
            logger.info(f"[CHECK] Retrieved {len(df)} records from S3 flatfile")
            return df
            
        except Exception as e:
            logger.error(f"[ERROR] S3 flatfile error for {symbol} on {date}: {e}")
            return None
    
    async def get_tick_data(self, symbol: str, date: str = None) -> Optional[pd.DataFrame]:
        """
        Get tick-level data from S3 flatfiles
        Ultra-high frequency data with microsecond precision
        """
        try:
            if not self.s3_client:
                return None
            
            if not date:
                date = datetime.now().strftime('%Y/%m/%d')
            
            # Construct S3 key for tick data
            s3_key = f"us_stocks_sip/trades_v1/{date}/{symbol.upper()}.parquet"
            
            logger.info(f"📈 Fetching tick data: {s3_key}")
            
            response = self.s3_client.get_object(Bucket=self.bucket, Key=s3_key)
            df = pd.read_parquet(response['Body'])
            
            logger.info(f"[CHECK] Retrieved {len(df)} tick records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"[ERROR] Tick data error for {symbol}: {e}")
            return None
    
    async def get_options_data(self, underlying: str) -> Optional[List[Dict[str, Any]]]:
        """Get options chain data from Polygon.io premium"""
        try:
            url = f"https://api.polygon.io/v3/snapshot/options/{underlying}"
            params = {
                'apikey': self.api_key,
                'limit': 250
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('results', [])
                        
        except Exception as e:
            logger.error(f"[ERROR] Options data error for {underlying}: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if Polygon.io Premium is properly configured"""
        return bool(self.api_key or (self.access_key_id and self.secret_access_key and self.s3_client))
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the Polygon.io Premium connection"""
        try:
            if not self.s3_client:
                return {
                    'status': 'error',
                    'message': 'S3 client not configured',
                    'configured': False
                }
            
            # Test S3 access by listing bucket contents
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix='us_stocks_sip/',
                MaxKeys=1
            )
            
            if 'Contents' in response:
                return {
                    'status': 'success',
                    'message': 'Polygon.io Premium S3 access verified',
                    'configured': True,
                    'bucket': self.bucket,
                    'files_available': len(response.get('Contents', []))
                }
            else:
                return {
                    'status': 'warning',
                    'message': 'S3 access configured but no files found',
                    'configured': True
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Connection test failed: {str(e)}',
                'configured': False
            }

# Global instance
polygon_premium_provider = PolygonPremiumProvider()

async def get_polygon_premium_data(symbol: str) -> Optional[Dict[str, Any]]:
    """
    🎯 Main function to get Polygon.io premium market data
    """
    try:
        data = await polygon_premium_provider.get_real_time_quote(symbol)
        
        if data:
            return {
                'symbol': data.symbol,
                'price': data.price,
                'volume': data.volume,
                'change': data.change,
                'change_percent': data.change_percent,
                'bid': data.bid,
                'ask': data.ask,
                'spread': data.spread,
                'high': data.high,
                'low': data.low,
                'open': data.open,
                'vwap': data.vwap,
                'timestamp': data.timestamp.isoformat(),
                'source': data.source,
                'type': 'stock_premium'
            }
        
        return None
        
    except Exception as e:
        logger.error(f"[ERROR] Error getting Polygon premium data for {symbol}: {e}")
        return None
