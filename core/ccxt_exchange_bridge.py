"""
CCXT Multi-Exchange Integration for PROMETHEUS
Unified access to 107+ cryptocurrency exchanges via ccxt.

Replaces the custom per-exchange configs in brokers/multi_exchange_manager.py
with a battle-tested, community-maintained library (41K+ GitHub stars).

Supported exchanges include: Binance, Coinbase, Kraken, KuCoin, OKX,
Bybit, Gate.io, Bitfinex, Huobi, and 100+ more.

Usage:
    from core.ccxt_exchange_bridge import CCXTExchangeBridge
    bridge = CCXTExchangeBridge()
    bridge.add_exchange('binance', api_key='...', secret='...')
    ticker = await bridge.get_ticker('binance', 'BTC/USDT')
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ExchangeStatus:
    """Status of a connected exchange."""
    name: str
    connected: bool = False
    sandbox: bool = False
    markets_loaded: int = 0
    last_error: Optional[str] = None
    connected_at: Optional[datetime] = None
    capabilities: List[str] = field(default_factory=list)


class CCXTExchangeBridge:
    """
    Bridge between PROMETHEUS and 107+ crypto exchanges via ccxt.

    This complements (does not replace) Alpaca and IB integrations.
    It adds broad crypto exchange coverage that Alpaca alone cannot provide.
    """

    # Exchanges we have first-class config for
    RECOMMENDED_EXCHANGES = {
        'binance': {
            'class': 'binance',
            'name': 'Binance',
            'env_key': 'BINANCE_API_KEY',
            'env_secret': 'BINANCE_SECRET',
            'sandbox': True,
        },
        'coinbase': {
            'class': 'coinbase',
            'name': 'Coinbase Advanced',
            'env_key': 'COINBASE_API_KEY',
            'env_secret': 'COINBASE_SECRET',
            'sandbox': True,
        },
        'kraken': {
            'class': 'kraken',
            'name': 'Kraken',
            'env_key': 'KRAKEN_API_KEY',
            'env_secret': 'KRAKEN_SECRET',
            'sandbox': False,
        },
        'kucoin': {
            'class': 'kucoin',
            'name': 'KuCoin',
            'env_key': 'KUCOIN_API_KEY',
            'env_secret': 'KUCOIN_SECRET',
            'sandbox': True,
        },
        'okx': {
            'class': 'okx',
            'name': 'OKX',
            'env_key': 'OKX_API_KEY',
            'env_secret': 'OKX_SECRET',
            'sandbox': True,
        },
        'bybit': {
            'class': 'bybit',
            'name': 'Bybit',
            'env_key': 'BYBIT_API_KEY',
            'env_secret': 'BYBIT_SECRET',
            'sandbox': True,
        },
    }

    def __init__(self, sandbox_mode: bool = True):
        """
        Args:
            sandbox_mode: If True, connect in testnet/sandbox mode where available.
        """
        self.sandbox_mode = sandbox_mode
        self.exchanges: Dict[str, Any] = {}  # exchange_id -> ccxt instance
        self.statuses: Dict[str, ExchangeStatus] = {}
        self._ccxt = None
        self._ccxt_async = None
        self._load_ccxt()
        self._auto_connect()

    def _load_ccxt(self):
        """Lazy-load ccxt to avoid hard dependency."""
        try:
            import ccxt
            import ccxt.async_support as ccxt_async
            self._ccxt = ccxt
            self._ccxt_async = ccxt_async
            logger.info(f"ccxt loaded: v{ccxt.__version__} — {len(ccxt.exchanges)} exchanges available")
        except ImportError:
            logger.warning(
                "ccxt not installed. Run: pip install ccxt\n"
                "This is required for multi-exchange crypto trading."
            )

    def _auto_connect(self):
        """Auto-connect exchanges that have credentials in env, or public-only mode."""
        if not self._ccxt:
            return
        if not os.getenv('CCXT_AUTO_CONNECT', 'false').lower() in ('true', '1', 'yes'):
            return

        connected = 0
        for exch_id, config in self.RECOMMENDED_EXCHANGES.items():
            api_key = os.getenv(config.get('env_key', ''), '')
            secret = os.getenv(config.get('env_secret', ''), '')
            try:
                exchange_class = getattr(self._ccxt, exch_id, None)
                if exchange_class is None:
                    continue
                opts = {'enableRateLimit': True, 'options': {'defaultType': 'spot'}}
                if api_key and secret:
                    opts['apiKey'] = api_key
                    opts['secret'] = secret
                exchange = exchange_class(opts)
                # Don't load_markets for public-only (slow) — lazy load on first use
                self.exchanges[exch_id] = exchange
                self.statuses[exch_id] = ExchangeStatus(
                    name=config.get('name', exch_id),
                    connected=True,
                    sandbox=self.sandbox_mode,
                    connected_at=datetime.now(),
                )
                connected += 1
            except Exception as exc:
                logger.debug(f"Auto-connect skipped {exch_id}: {exc}")

        if connected:
            logger.info(f"CCXT auto-connected {connected} exchanges (public mode)")


    # ------------------------------------------------------------------
    # Exchange management
    # ------------------------------------------------------------------

    def add_exchange(
        self,
        exchange_id: str,
        api_key: Optional[str] = None,
        secret: Optional[str] = None,
        password: Optional[str] = None,
        sandbox: Optional[bool] = None,
    ) -> bool:
        """
        Connect to a crypto exchange.

        Args:
            exchange_id: ccxt exchange id (e.g. 'binance', 'kraken')
            api_key: API key (falls back to env var)
            secret: API secret (falls back to env var)
            password: Passphrase if required (e.g. KuCoin)
            sandbox: Override sandbox mode for this exchange

        Returns:
            True if connection succeeded.
        """
        if not self._ccxt:
            logger.error("ccxt not available — cannot add exchange")
            return False

        # Resolve credentials from env if not provided
        config = self.RECOMMENDED_EXCHANGES.get(exchange_id, {})
        api_key = api_key or os.getenv(config.get('env_key', ''), '')
        secret = secret or os.getenv(config.get('env_secret', ''), '')

        if not api_key or not secret:
            logger.warning(f"No credentials for {exchange_id} — connecting in public-only mode")

        use_sandbox = sandbox if sandbox is not None else self.sandbox_mode

        try:
            exchange_class = getattr(self._ccxt, exchange_id, None)
            if exchange_class is None:
                logger.error(f"Unknown exchange: {exchange_id}")
                return False

            exchange = exchange_class({
                'apiKey': api_key or None,
                'secret': secret or None,
                'password': password or os.getenv(f"{exchange_id.upper()}_PASSWORD", '') or None,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'},
            })

            if use_sandbox and hasattr(exchange, 'set_sandbox_mode'):
                exchange.set_sandbox_mode(True)

            # Load markets
            exchange.load_markets()

            self.exchanges[exchange_id] = exchange
            self.statuses[exchange_id] = ExchangeStatus(
                name=config.get('name', exchange_id),
                connected=True,
                sandbox=use_sandbox,
                markets_loaded=len(exchange.markets),
                connected_at=datetime.now(),
                capabilities=list(set(
                    t for m in exchange.markets.values()
                    for t in ([m.get('type', 'spot')] if isinstance(m.get('type'), str) else [])
                )),
            )

            logger.info(
                f"Connected to {exchange_id}: {len(exchange.markets)} markets, "
                f"sandbox={use_sandbox}"
            )
            return True

        except Exception as exc:
            logger.error(f"Failed to connect to {exchange_id}: {exc}")
            self.statuses[exchange_id] = ExchangeStatus(
                name=config.get('name', exchange_id),
                connected=False,
                last_error=str(exc),
            )
            return False

    def auto_connect(self) -> Dict[str, bool]:
        """
        Auto-connect to all exchanges that have credentials in env vars.
        Returns dict of exchange_id -> success.
        """
        results = {}
        for eid, config in self.RECOMMENDED_EXCHANGES.items():
            key = os.getenv(config['env_key'], '')
            if key:
                results[eid] = self.add_exchange(eid)
            else:
                results[eid] = False
        return results

    # ------------------------------------------------------------------
    # Market data
    # ------------------------------------------------------------------

    def get_ticker(self, exchange_id: str, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current ticker for a symbol on an exchange."""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            logger.warning(f"Exchange {exchange_id} not connected")
            return None
        try:
            return exchange.fetch_ticker(symbol)
        except Exception as exc:
            logger.error(f"Ticker fetch failed ({exchange_id}/{symbol}): {exc}")
            return None

    def get_ohlcv(
        self,
        exchange_id: str,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 100,
    ) -> Optional[List]:
        """Fetch OHLCV candles."""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            return None
        try:
            return exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        except Exception as exc:
            logger.error(f"OHLCV fetch failed ({exchange_id}/{symbol}): {exc}")
            return None

    def get_order_book(self, exchange_id: str, symbol: str, limit: int = 20) -> Optional[Dict]:
        """Fetch order book."""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            return None
        try:
            return exchange.fetch_order_book(symbol, limit)
        except Exception as exc:
            logger.error(f"Order book fetch failed ({exchange_id}/{symbol}): {exc}")
            return None

    # ------------------------------------------------------------------
    # Trading
    # ------------------------------------------------------------------

    def create_order(
        self,
        exchange_id: str,
        symbol: str,
        side: str,  # 'buy' or 'sell'
        order_type: str = 'limit',  # 'market', 'limit'
        amount: float = 0.0,
        price: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """Place an order on an exchange."""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            logger.error(f"Exchange {exchange_id} not connected")
            return None
        try:
            order = exchange.create_order(symbol, order_type, side, amount, price)
            logger.info(f"Order placed on {exchange_id}: {side} {amount} {symbol} @ {price or 'market'}")
            return order
        except Exception as exc:
            logger.error(f"Order failed ({exchange_id}/{symbol}): {exc}")
            return None

    def get_balance(self, exchange_id: str) -> Optional[Dict[str, Any]]:
        """Fetch account balance."""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            return None
        try:
            return exchange.fetch_balance()
        except Exception as exc:
            logger.error(f"Balance fetch failed ({exchange_id}): {exc}")
            return None

    def get_open_orders(self, exchange_id: str, symbol: Optional[str] = None) -> List[Dict]:
        """Fetch open orders."""
        exchange = self.exchanges.get(exchange_id)
        if not exchange:
            return []
        try:
            return exchange.fetch_open_orders(symbol)
        except Exception as exc:
            logger.error(f"Open orders fetch failed ({exchange_id}): {exc}")
            return []

    # ------------------------------------------------------------------
    # Cross-exchange utilities
    # ------------------------------------------------------------------

    def find_best_price(self, symbol: str, side: str = 'buy') -> Optional[Dict[str, Any]]:
        """
        Find the best price for a symbol across all connected exchanges.
        Useful for cross-exchange arbitrage detection.
        """
        best = None
        for eid, exchange in self.exchanges.items():
            try:
                if symbol not in exchange.markets:
                    continue
                ticker = exchange.fetch_ticker(symbol)
                price = ticker.get('ask' if side == 'buy' else 'bid', 0)
                if price and (best is None or
                    (side == 'buy' and price < best['price']) or
                    (side == 'sell' and price > best['price'])):
                    best = {
                        'exchange': eid,
                        'symbol': symbol,
                        'price': price,
                        'volume': ticker.get('baseVolume', 0),
                    }
            except Exception:
                continue
        return best

    def detect_arbitrage(self, symbol: str = 'BTC/USDT', min_spread_pct: float = 0.2) -> List[Dict]:
        """
        Detect arbitrage opportunities across connected exchanges.
        Returns list of opportunities where spread > min_spread_pct.
        """
        prices = {}
        for eid, exchange in self.exchanges.items():
            try:
                if symbol not in exchange.markets:
                    continue
                ticker = exchange.fetch_ticker(symbol)
                prices[eid] = {
                    'bid': ticker.get('bid', 0),
                    'ask': ticker.get('ask', 0),
                }
            except Exception:
                continue

        opportunities = []
        exchange_ids = list(prices.keys())
        for i, buy_ex in enumerate(exchange_ids):
            for sell_ex in exchange_ids[i + 1:]:
                buy_ask = prices[buy_ex]['ask']
                sell_bid = prices[sell_ex]['bid']
                if buy_ask and sell_bid:
                    spread_pct = ((sell_bid - buy_ask) / buy_ask) * 100
                    if spread_pct > min_spread_pct:
                        opportunities.append({
                            'symbol': symbol,
                            'buy_exchange': buy_ex,
                            'buy_price': buy_ask,
                            'sell_exchange': sell_ex,
                            'sell_price': sell_bid,
                            'spread_pct': round(spread_pct, 4),
                        })
                # Check reverse direction
                buy_ask_r = prices[sell_ex]['ask']
                sell_bid_r = prices[buy_ex]['bid']
                if buy_ask_r and sell_bid_r:
                    spread_pct_r = ((sell_bid_r - buy_ask_r) / buy_ask_r) * 100
                    if spread_pct_r > min_spread_pct:
                        opportunities.append({
                            'symbol': symbol,
                            'buy_exchange': sell_ex,
                            'buy_price': buy_ask_r,
                            'sell_exchange': buy_ex,
                            'sell_price': sell_bid_r,
                            'spread_pct': round(spread_pct_r, 4),
                        })

        return sorted(opportunities, key=lambda x: x['spread_pct'], reverse=True)

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        """Return status of all exchanges."""
        return {
            'ccxt_available': self._ccxt is not None,
            'ccxt_version': getattr(self._ccxt, '__version__', 'N/A') if self._ccxt else 'N/A',
            'total_exchanges_available': len(self._ccxt.exchanges) if self._ccxt else 0,
            'connected_exchanges': len(self.exchanges),
            'sandbox_mode': self.sandbox_mode,
            'exchanges': {
                eid: {
                    'name': s.name,
                    'connected': s.connected,
                    'sandbox': s.sandbox,
                    'markets': s.markets_loaded,
                    'capabilities': s.capabilities,
                    'last_error': s.last_error,
                }
                for eid, s in self.statuses.items()
            },
        }

    def list_available_exchanges(self) -> List[str]:
        """List all 107+ exchanges available through ccxt."""
        if self._ccxt:
            return self._ccxt.exchanges
        return []
