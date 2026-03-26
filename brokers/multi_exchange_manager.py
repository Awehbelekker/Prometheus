"""
Multi-Exchange Support System
Integrates Binance, Coinbase, Kraken alongside Alpaca and Interactive Brokers
Enables cross-exchange arbitrage and global market access
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import time

logger = logging.getLogger(__name__)

class ExchangeType(Enum):
    """Supported exchange types"""
    ALPACA = "alpaca"
    INTERACTIVE_BROKERS = "ib"
    BINANCE = "binance"
    COINBASE = "coinbase"
    KRAKEN = "kraken"

@dataclass
class ExchangeConnection:
    """Exchange connection details"""
    exchange: ExchangeType
    status: str  # 'connected', 'disconnected', 'error'
    api_key: str
    capabilities: List[str]
    supported_assets: List[str]
    fees: Dict[str, float]
    connected_at: Optional[datetime] = None
    last_error: Optional[str] = None

class MultiExchangeManager:
    """
    Unified interface for multiple exchanges
    Handles connections, orders, and cross-exchange operations
    """
    
    def __init__(self):
        # Exchange connections
        self.connections = {}
        
        # Exchange configurations
        self.exchange_configs = {
            ExchangeType.BINANCE: {
                'name': 'Binance',
                'api_url': 'https://api.binance.com',
                'ws_url': 'wss://stream.binance.com:9443',
                'capabilities': ['spot', 'futures', 'margin', 'crypto'],
                'supported_assets': ['BTC', 'ETH', 'USDT', 'BNB', 'ADA', 'SOL'],
                'fees': {'maker': 0.001, 'taker': 0.001},  # 0.1%
                'rate_limits': {'requests_per_minute': 1200}
            },
            ExchangeType.COINBASE: {
                'name': 'Coinbase Pro',
                'api_url': 'https://api.pro.coinbase.com',
                'ws_url': 'wss://ws-feed.pro.coinbase.com',
                'capabilities': ['spot', 'crypto'],
                'supported_assets': ['BTC', 'ETH', 'USDC', 'LTC', 'BCH', 'LINK'],
                'fees': {'maker': 0.005, 'taker': 0.005},  # 0.5%
                'rate_limits': {'requests_per_second': 10}
            },
            ExchangeType.KRAKEN: {
                'name': 'Kraken',
                'api_url': 'https://api.kraken.com',
                'ws_url': 'wss://ws.kraken.com',
                'capabilities': ['spot', 'futures', 'margin', 'crypto'],
                'supported_assets': ['BTC', 'ETH', 'USDT', 'XRP', 'DOT', 'ADA'],
                'fees': {'maker': 0.0016, 'taker': 0.0026},  # 0.16%/0.26%
                'rate_limits': {'requests_per_second': 15}
            },
            ExchangeType.ALPACA: {
                'name': 'Alpaca Markets',
                'api_url': 'https://api.alpaca.markets',
                'capabilities': ['spot', 'crypto', 'stocks'],
                'supported_assets': ['BTC', 'ETH', 'AAPL', 'TSLA', 'SPY'],
                'fees': {'maker': 0.0, 'taker': 0.0},  # Commission-free
                'rate_limits': {'requests_per_minute': 200}
            },
            ExchangeType.INTERACTIVE_BROKERS: {
                'name': 'Interactive Brokers',
                'api_url': 'localhost:7497',
                'capabilities': ['stocks', 'options', 'futures', 'forex'],
                'supported_assets': ['AAPL', 'TSLA', 'SPY', 'QQQ', 'ES', 'NQ'],
                'fees': {'per_share': 0.0005},  # $0.0005/share
                'rate_limits': {'requests_per_second': 50}
            }
        }
        
        # Cross-exchange arbitrage tracking
        self.arbitrage_opportunities = []
        
        # Order routing preferences
        self.routing_preferences = {
            'crypto': [ExchangeType.BINANCE, ExchangeType.COINBASE, ExchangeType.KRAKEN],
            'stocks': [ExchangeType.INTERACTIVE_BROKERS, ExchangeType.ALPACA],
            'futures': [ExchangeType.INTERACTIVE_BROKERS, ExchangeType.BINANCE]
        }
        
        logger.info("✅ Multi-Exchange Manager initialized")
    
    async def connect_exchange(
        self,
        exchange: ExchangeType,
        api_key: str,
        api_secret: str,
        **kwargs
    ) -> bool:
        """
        Connect to an exchange
        
        Args:
            exchange: Exchange type
            api_key: API key
            api_secret: API secret
            **kwargs: Additional connection parameters
            
        Returns:
            Success status
        """
        try:
            logger.info(f"🔌 Connecting to {exchange.value}...")
            
            config = self.exchange_configs.get(exchange)
            if not config:
                logger.error(f"Unknown exchange: {exchange}")
                return False
            
            # Create connection (simplified - in production use actual exchange APIs)
            connection = ExchangeConnection(
                exchange=exchange,
                status='connected',
                api_key=api_key[:10] + '...',  # Masked
                capabilities=config['capabilities'],
                supported_assets=config['supported_assets'],
                fees=config['fees'],
                connected_at=datetime.utcnow()
            )
            
            # Test connection
            test_result = await self._test_connection(exchange, api_key, api_secret)
            
            if test_result:
                self.connections[exchange] = connection
                logger.info(f"✅ Connected to {config['name']}")
                logger.info(f"   Capabilities: {', '.join(config['capabilities'])}")
                logger.info(f"   Supported assets: {len(config['supported_assets'])}")
                return True
            else:
                logger.error(f"❌ Connection test failed for {exchange.value}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error connecting to {exchange.value}: {e}")
            return False
    
    async def _test_connection(
        self,
        exchange: ExchangeType,
        api_key: str,
        api_secret: str
    ) -> bool:
        """Test exchange connection"""
        try:
            # Simulate connection test
            await asyncio.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def get_market_data(
        self,
        exchange: ExchangeType,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get market data from specific exchange
        
        Args:
            exchange: Exchange to query
            symbol: Trading symbol
            
        Returns:
            Market data dict
        """
        try:
            if exchange not in self.connections:
                logger.warning(f"Not connected to {exchange.value}")
                return None
            
            # Get market data (simplified)
            if exchange == ExchangeType.BINANCE:
                data = await self._binance_get_ticker(symbol)
            elif exchange == ExchangeType.COINBASE:
                data = await self._coinbase_get_ticker(symbol)
            elif exchange == ExchangeType.KRAKEN:
                data = await self._kraken_get_ticker(symbol)
            elif exchange == ExchangeType.ALPACA:
                data = await self._alpaca_get_quote(symbol)
            elif exchange == ExchangeType.INTERACTIVE_BROKERS:
                data = await self._ib_get_quote(symbol)
            else:
                data = None
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting market data from {exchange.value}: {e}")
            return None
    
    async def place_order(
        self,
        exchange: ExchangeType,
        symbol: str,
        side: str,  # 'buy' or 'sell'
        quantity: float,
        order_type: str = 'market',
        limit_price: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Place order on specific exchange
        
        Args:
            exchange: Exchange to use
            symbol: Trading symbol
            side: 'buy' or 'sell'
            quantity: Order quantity
            order_type: 'market', 'limit', etc.
            limit_price: Limit price (for limit orders)
            
        Returns:
            Order confirmation
        """
        try:
            if exchange not in self.connections:
                logger.error(f"Not connected to {exchange.value}")
                return None
            
            logger.info(f"📤 Placing {side} order on {exchange.value}: {quantity} {symbol}")
            
            # Place order (simplified)
            order = {
                'order_id': self._generate_order_id(),
                'exchange': exchange.value,
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'order_type': order_type,
                'limit_price': limit_price,
                'status': 'submitted',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Exchange-specific order placement
            if exchange == ExchangeType.BINANCE:
                result = await self._binance_place_order(order)
            elif exchange == ExchangeType.COINBASE:
                result = await self._coinbase_place_order(order)
            elif exchange == ExchangeType.KRAKEN:
                result = await self._kraken_place_order(order)
            elif exchange == ExchangeType.ALPACA:
                result = await self._alpaca_place_order(order)
            elif exchange == ExchangeType.INTERACTIVE_BROKERS:
                result = await self._ib_place_order(order)
            else:
                result = order
            
            logger.info(f"✅ Order placed: {result['order_id']}")
            return result
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    async def find_best_execution_venue(
        self,
        symbol: str,
        side: str,
        quantity: float
    ) -> Optional[ExchangeType]:
        """
        Find best exchange for order execution
        Considers price, fees, liquidity
        
        Args:
            symbol: Trading symbol
            side: 'buy' or 'sell'
            quantity: Order quantity
            
        Returns:
            Best exchange
        """
        try:
            # Determine asset type
            asset_type = 'crypto' if symbol in ['BTC', 'ETH', 'USDT'] else 'stocks'
            
            # Get candidate exchanges
            candidates = self.routing_preferences.get(asset_type, [])
            connected_candidates = [ex for ex in candidates if ex in self.connections]
            
            if not connected_candidates:
                logger.warning(f"No connected exchanges for {asset_type}")
                return None
            
            # Get quotes from all candidates
            best_exchange = None
            best_price = float('inf') if side == 'buy' else 0.0
            
            for exchange in connected_candidates:
                market_data = await self.get_market_data(exchange, symbol)
                if not market_data:
                    continue
                
                price = market_data.get('ask' if side == 'buy' else 'bid', 0.0)
                fees = self.exchange_configs[exchange]['fees'].get('taker', 0.001)
                
                # Calculate total cost
                if side == 'buy':
                    total_cost = price * (1 + fees)
                    if total_cost < best_price:
                        best_price = total_cost
                        best_exchange = exchange
                else:
                    net_proceeds = price * (1 - fees)
                    if net_proceeds > best_price:
                        best_price = net_proceeds
                        best_exchange = exchange
            
            if best_exchange:
                logger.info(f"🎯 Best execution venue: {best_exchange.value} @ {best_price:.2f}")
            
            return best_exchange
            
        except Exception as e:
            logger.error(f"Error finding best venue: {e}")
            return None
    
    async def scan_cross_exchange_arbitrage(
        self,
        symbols: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Scan for arbitrage opportunities across exchanges
        
        Args:
            symbols: Symbols to scan
            
        Returns:
            List of arbitrage opportunities
        """
        opportunities = []
        
        try:
            for symbol in symbols:
                # Get prices from all connected exchanges
                prices = {}
                
                for exchange in self.connections.keys():
                    market_data = await self.get_market_data(exchange, symbol)
                    if market_data:
                        prices[exchange] = {
                            'bid': market_data.get('bid', 0.0),
                            'ask': market_data.get('ask', 0.0)
                        }
                
                # Find arbitrage opportunities
                for buy_exchange, buy_data in prices.items():
                    for sell_exchange, sell_data in prices.items():
                        if buy_exchange == sell_exchange:
                            continue
                        
                        # Calculate profit
                        buy_price = buy_data['ask']
                        sell_price = sell_data['bid']
                        
                        buy_fee = self.exchange_configs[buy_exchange]['fees'].get('taker', 0.001)
                        sell_fee = self.exchange_configs[sell_exchange]['fees'].get('taker', 0.001)
                        
                        gross_profit = (sell_price - buy_price) / buy_price
                        net_profit = gross_profit - buy_fee - sell_fee
                        
                        # Opportunity threshold: 0.5% net profit
                        if net_profit > 0.005:
                            opportunity = {
                                'symbol': symbol,
                                'buy_exchange': buy_exchange.value,
                                'sell_exchange': sell_exchange.value,
                                'buy_price': buy_price,
                                'sell_price': sell_price,
                                'net_profit_pct': net_profit,
                                'timestamp': datetime.utcnow().isoformat()
                            }
                            opportunities.append(opportunity)
                            logger.info(f"💰 Arbitrage opportunity: {symbol} - "
                                       f"{net_profit:.3%} profit "
                                       f"({buy_exchange.value} → {sell_exchange.value})")
            
            self.arbitrage_opportunities = opportunities
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scanning arbitrage: {e}")
            return []
    
    # Exchange-specific implementations (simplified)
    
    async def _binance_get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get Binance ticker"""
        # Simulated - in production use actual Binance API
        return {
            'symbol': symbol,
            'bid': 50000.0,
            'ask': 50050.0,
            'last': 50025.0,
            'volume': 1000.0,
            'exchange': 'binance'
        }
    
    async def _coinbase_get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get Coinbase ticker"""
        return {
            'symbol': symbol,
            'bid': 50020.0,
            'ask': 50070.0,
            'last': 50045.0,
            'volume': 800.0,
            'exchange': 'coinbase'
        }
    
    async def _kraken_get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get Kraken ticker"""
        return {
            'symbol': symbol,
            'bid': 50010.0,
            'ask': 50060.0,
            'last': 50035.0,
            'volume': 900.0,
            'exchange': 'kraken'
        }
    
    async def _alpaca_get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get Alpaca quote"""
        return {
            'symbol': symbol,
            'bid': 150.0,
            'ask': 150.10,
            'last': 150.05,
            'volume': 10000.0,
            'exchange': 'alpaca'
        }
    
    async def _ib_get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get Interactive Brokers quote"""
        return {
            'symbol': symbol,
            'bid': 149.98,
            'ask': 150.08,
            'last': 150.03,
            'volume': 15000.0,
            'exchange': 'ib'
        }
    
    async def _binance_place_order(self, order: Dict) -> Dict:
        """Place Binance order"""
        await asyncio.sleep(0.05)  # Simulate network delay
        order['status'] = 'filled'
        order['filled_at'] = datetime.utcnow().isoformat()
        return order
    
    async def _coinbase_place_order(self, order: Dict) -> Dict:
        """Place Coinbase order"""
        await asyncio.sleep(0.05)
        order['status'] = 'filled'
        order['filled_at'] = datetime.utcnow().isoformat()
        return order
    
    async def _kraken_place_order(self, order: Dict) -> Dict:
        """Place Kraken order"""
        await asyncio.sleep(0.05)
        order['status'] = 'filled'
        order['filled_at'] = datetime.utcnow().isoformat()
        return order
    
    async def _alpaca_place_order(self, order: Dict) -> Dict:
        """Place Alpaca order"""
        await asyncio.sleep(0.05)
        order['status'] = 'filled'
        order['filled_at'] = datetime.utcnow().isoformat()
        return order
    
    async def _ib_place_order(self, order: Dict) -> Dict:
        """Place IB order"""
        await asyncio.sleep(0.05)
        order['status'] = 'filled'
        order['filled_at'] = datetime.utcnow().isoformat()
        return order
    
    def _generate_order_id(self) -> str:
        """Generate unique order ID"""
        return f"ORD_{int(time.time() * 1000)}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get multi-exchange manager status"""
        return {
            'connected_exchanges': [ex.value for ex in self.connections.keys()],
            'exchange_count': len(self.connections),
            'arbitrage_opportunities': len(self.arbitrage_opportunities),
            'supported_exchanges': [ex.value for ex in ExchangeType],
            'connections': {
                ex.value: {
                    'status': conn.status,
                    'capabilities': conn.capabilities,
                    'connected_at': conn.connected_at.isoformat() if conn.connected_at else None
                }
                for ex, conn in self.connections.items()
            }
        }


# Global instance
_multi_exchange_manager = None

def get_multi_exchange_manager() -> MultiExchangeManager:
    """Get or create global multi-exchange manager"""
    global _multi_exchange_manager
    if _multi_exchange_manager is None:
        _multi_exchange_manager = MultiExchangeManager()
    return _multi_exchange_manager
