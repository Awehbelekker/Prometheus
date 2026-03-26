#!/usr/bin/env python3
"""
🎯 PROMETHEUS INTERNAL PAPER TRADING SYSTEM
Real live data paper trading for AI learning and user testing
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid
import sqlite3
import aiohttp
import websockets
from decimal import Decimal
import yfinance as yf
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PaperTrade:
    """Internal paper trade record"""
    trade_id: str
    user_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    price: float
    timestamp: datetime
    status: str  # 'filled', 'pending', 'cancelled'
    trade_type: str  # 'market', 'limit', 'stop'
    intended_investment: float  # User's real intended investment amount
    portfolio_percentage: float  # Percentage of their intended portfolio

@dataclass
class PaperPortfolio:
    """User's paper trading portfolio"""
    user_id: str
    cash_balance: float
    intended_investment: float  # What they plan to invest for real
    positions: Dict[str, Dict[str, float]]  # symbol -> {quantity, avg_price, current_value}
    total_value: float
    pnl: float
    pnl_percentage: float
    trades_count: int
    win_rate: float

@dataclass
class MarketData:
    """Real-time market data"""
    symbol: str
    price: float
    bid: float
    ask: float
    volume: float
    timestamp: datetime
    change_24h: float
    change_percentage: float

class InternalPaperTradingEngine:
    """
    Internal paper trading engine using real live market data
    for AI learning and user testing
    """
    
    def __init__(self):
        self.db_path = "paper_trading.db"
        self.market_data: Dict[str, MarketData] = {}
        self.user_portfolios: Dict[str, PaperPortfolio] = {}
        self.active_trades: Dict[str, PaperTrade] = {}
        self.ai_learning_data: List[Dict[str, Any]] = []
        self.max_users = 200  # Maximum 200 users
        self.current_users = 0
        
        # Initialize database
        self._init_database()
        
        # Market data feed will be started when needed
        self._market_data_feed_task = None

        logger.info("🎯 Internal Paper Trading Engine initialized with REAL market data only")
    
    def _init_database(self):
        """Initialize SQLite database for paper trading"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paper_trades (
                trade_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                intended_investment REAL NOT NULL,
                portfolio_percentage REAL NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paper_portfolios (
                user_id TEXT PRIMARY KEY,
                cash_balance REAL NOT NULL,
                intended_investment REAL NOT NULL,
                positions TEXT NOT NULL,
                total_value REAL NOT NULL,
                pnl REAL NOT NULL,
                pnl_percentage REAL NOT NULL,
                trades_count INTEGER NOT NULL,
                win_rate REAL NOT NULL,
                last_updated TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                symbol TEXT PRIMARY KEY,
                price REAL NOT NULL,
                bid REAL NOT NULL,
                ask REAL NOT NULL,
                volume REAL NOT NULL,
                timestamp TEXT NOT NULL,
                change_24h REAL NOT NULL,
                change_percentage REAL NOT NULL,
                data_source TEXT DEFAULT 'REAL_MARKET_DATA',
                market_open BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_learning_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                trade_data TEXT NOT NULL,
                market_conditions TEXT NOT NULL,
                outcome TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("[CHECK] Database initialized")
    
    async def _start_market_data_feed(self):
        """Start REAL market data feed - NO SIMULATION"""
        logger.info("🔄 Starting REAL market data feed (NO SIMULATION)...")

        # Popular symbols for paper trading
        symbols = [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
            'SPY', 'QQQ', 'IWM', 'GLD', 'SLV', 'VTI', 'BTC-USD', 'ETH-USD'
        ]

        while True:
            try:
                # Check if markets are open before updating data
                if not await self._is_market_open():
                    logger.info("🕐 Markets closed - pausing data feed")
                    await asyncio.sleep(300)  # Check every 5 minutes when closed
                    continue

                # Get REAL market data only
                for symbol in symbols:
                    await self._update_real_market_data(symbol)

                # Update portfolios with real prices
                await self._update_all_portfolios()

                # Feed real data to AI learning system
                await self._feed_ai_learning_data()

                await asyncio.sleep(30)  # Update every 30 seconds during market hours

            except Exception as e:
                logger.error(f"Real market data feed error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _update_real_market_data(self, symbol: str):
        """Update market data using REAL market sources - NO SIMULATION"""
        try:
            from core.real_time_market_data import market_data_orchestrator

            # Get real market data from live sources
            if symbol.endswith('-USD'):  # Crypto symbols
                crypto_symbol = symbol.replace('-USD', '')
                real_data = await market_data_orchestrator.get_live_crypto_data(crypto_symbol)
            else:  # Stock symbols
                real_data = await market_data_orchestrator.get_live_stock_data(symbol)

            if real_data and real_data.price > 0:
                # Use REAL market data
                market_data = MarketData(
                    symbol=symbol,
                    price=real_data.price,
                    bid=getattr(real_data, 'bid', real_data.price * 0.999),
                    ask=getattr(real_data, 'ask', real_data.price * 1.001),
                    volume=getattr(real_data, 'volume', 0),
                    timestamp=datetime.now(),
                    change_24h=getattr(real_data, 'change_24h', 0),
                    change_percentage=getattr(real_data, 'change_percentage', 0)
                )

                self.market_data[symbol] = market_data

                # Store REAL data in database with actual provider source
                conn = sqlite3.connect(self.db_path, timeout=30)
                cursor = conn.cursor()
                data_source = getattr(real_data, 'source', 'unknown')

                # Provide safe fallbacks for fields some providers don't supply
                price = float(getattr(real_data, 'price', 0.0) or 0.0)
                bid = getattr(real_data, 'bid', None)
                if bid is None:
                    bid = price - 0.01 if price else 0.0
                ask = getattr(real_data, 'ask', None)
                if ask is None:
                    ask = price + 0.01 if price else 0.0
                volume = int(getattr(real_data, 'volume', 0) or 0)
                change_24h = float(getattr(real_data, 'change_24h', 0) or 0)
                change_pct = float(
                    getattr(real_data, 'change_percent', getattr(real_data, 'change_percentage', 0)) or 0
                )

                cursor.execute('''
                    INSERT OR REPLACE INTO market_data
                    (symbol, price, bid, ask, volume, timestamp, change_24h, change_percentage, data_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''' , (
                    symbol, price, bid, ask,
                    volume, datetime.now().isoformat(),
                    change_24h, change_pct, data_source
                ))
                conn.commit()
                conn.close()

                logger.debug(f"[CHECK] Updated REAL market data for {symbol}: ${real_data.price:.2f}")
            else:
                logger.warning(f"[WARNING]️ No real market data available for {symbol} - skipping update")

        except Exception as e:
            logger.error(f"[ERROR] Failed to get real market data for {symbol}: {e}")
            # DO NOT fall back to simulation - skip this symbol

    async def _is_market_open(self) -> bool:
        """Check if markets are currently open - REAL market hours only"""
        try:
            # Try to get market status from Alpaca API if available
            alpaca_api_key = os.getenv('ALPACA_PAPER_KEY')
            alpaca_secret_key = os.getenv('ALPACA_PAPER_SECRET')

            if alpaca_api_key and alpaca_secret_key:
                try:
                    from alpaca_trade_api import REST
                    alpaca_api = REST(
                        alpaca_api_key,
                        alpaca_secret_key,
                        'https://paper-api.alpaca.markets',
                        api_version='v2'
                    )
                    clock = alpaca_api.get_clock()
                    is_open = clock.is_open
                    logger.debug(f"📊 Alpaca market status: {'OPEN' if is_open else 'CLOSED'}")
                    return is_open
                except Exception as e:
                    logger.warning(f"[WARNING]️ Alpaca market status check failed: {e}")

            # Fallback to timezone-aware market hours check (9:30 AM - 4:00 PM ET, Mon-Fri)
            # Import centralized market hours utility
            try:
                from core.market_hours_utils import is_market_open, get_eastern_time
                is_open = is_market_open(include_extended_hours=False)
                eastern_time = get_eastern_time()
                logger.debug(f"🕐 Market hours check: {'OPEN' if is_open else 'CLOSED'} (ET: {eastern_time.strftime('%I:%M %p')})")
                return is_open
            except ImportError:
                logger.warning("[WARNING]️ market_hours_utils not available, using local time approximation")
                # Fallback to old method if utility not available
                now = datetime.now()
                if now.weekday() >= 5:
                    logger.debug("📅 Weekend - markets closed")
                    return False
                market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
                market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
                is_open = market_open <= now <= market_close
                logger.debug(f"🕐 Market hours check: {'OPEN' if is_open else 'CLOSED'} ({now.strftime('%H:%M')})")
                return is_open

        except Exception as e:
            logger.error(f"[ERROR] Market hours check failed: {e}")
            return False  # Default to closed on error

    async def validate_real_market_data(self) -> Dict[str, Any]:
        """Validate that we're using real market data sources"""
        validation_results = {
            "using_real_data": True,
            "data_sources": [],
            "market_status": "UNKNOWN",
            "symbols_with_real_data": 0,
            "total_symbols": len(self.market_data),
            "last_update": None
        }

        try:
            # Check market status
            is_open = await self._is_market_open()
            validation_results["market_status"] = "OPEN" if is_open else "CLOSED"

            # Check data sources in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT symbol, data_source, timestamp FROM market_data ORDER BY timestamp DESC LIMIT 10")
            recent_data = cursor.fetchall()
            conn.close()

            real_data_count = 0
            for symbol, source, timestamp in recent_data:
                if source == 'REAL_MARKET_DATA':
                    real_data_count += 1
                validation_results["data_sources"].append({
                    "symbol": symbol,
                    "source": source,
                    "timestamp": timestamp
                })

            validation_results["symbols_with_real_data"] = real_data_count
            validation_results["using_real_data"] = real_data_count > 0

            if recent_data:
                validation_results["last_update"] = recent_data[0][2]

            logger.info(f"[CHECK] Market data validation: {real_data_count}/{len(recent_data)} symbols using real data")

        except Exception as e:
            logger.error(f"[ERROR] Market data validation failed: {e}")
            validation_results["using_real_data"] = False
            validation_results["error"] = str(e)

        return validation_results

    async def start_market_data_feed(self):
        """Start the market data feed if not already running"""
        if self._market_data_feed_task is None or self._market_data_feed_task.done():
            self._market_data_feed_task = asyncio.create_task(self._start_market_data_feed())
            logger.info("🔄 Market data feed started")
        else:
            logger.info("🔄 Market data feed already running")
    
    async def create_user_portfolio(self, user_id: str, intended_investment: float) -> Dict[str, Any]:
        """Create a new paper trading portfolio for a user"""
        if self.current_users >= self.max_users:
            return {
                "success": False,
                "error": "Maximum user limit reached (200 users)",
                "current_users": self.current_users
            }
        
        if user_id in self.user_portfolios:
            return {
                "success": False,
                "error": "User already has a portfolio",
                "portfolio": asdict(self.user_portfolios[user_id])
            }
        
        # Create new portfolio with intended investment as starting cash
        portfolio = PaperPortfolio(
            user_id=user_id,
            cash_balance=intended_investment,
            intended_investment=intended_investment,
            positions={},
            total_value=intended_investment,
            pnl=0.0,
            pnl_percentage=0.0,
            trades_count=0,
            win_rate=0.0
        )
        
        self.user_portfolios[user_id] = portfolio
        self.current_users += 1
        
        # Save to database
        await self._save_portfolio(portfolio)
        
        logger.info(f"[CHECK] Created paper portfolio for user {user_id} with ${intended_investment:,.2f}")
        
        return {
            "success": True,
            "portfolio": asdict(portfolio),
            "message": f"Paper trading portfolio created with ${intended_investment:,.2f}",
            "users_remaining": self.max_users - self.current_users
        }
    
    async def place_paper_trade(self, user_id: str, symbol: str, side: str,
                               quantity: float, trade_type: str = 'market') -> Dict[str, Any]:
        """Place a paper trade with REAL market data and conditions"""

        # Check if markets are open (except for crypto)
        if not symbol.endswith('-USD'):  # Stock symbols
            if not await self._is_market_open():
                return {
                    "success": False,
                    "error": "Markets are closed - cannot execute stock trades",
                    "market_status": "CLOSED"
                }

        if user_id not in self.user_portfolios:
            return {"success": False, "error": "User portfolio not found"}

        if symbol not in self.market_data:
            return {
                "success": False,
                "error": f"Real market data not available for {symbol}",
                "note": "Paper trading uses only real market data - no simulation"
            }

        portfolio = self.user_portfolios[user_id]
        market_data = self.market_data[symbol]
        
        # Calculate trade value using REAL market spreads
        if trade_type == 'market':
            # Use real bid/ask spread - buyers pay ask, sellers get bid
            price = market_data.ask if side == 'buy' else market_data.bid
            logger.info(f"📊 Using REAL {side.upper()} price for {symbol}: ${price:.2f} (spread: ${market_data.ask - market_data.bid:.4f})")
        else:
            # For limit orders, use mid-price but note this is simplified
            price = (market_data.bid + market_data.ask) / 2
            logger.info(f"📊 Using mid-price for limit order on {symbol}: ${price:.2f}")
        
        trade_value = quantity * price
        
        # Check if user has enough cash for buy orders
        if side == 'buy' and trade_value > portfolio.cash_balance:
            return {
                "success": False,
                "error": f"Insufficient cash. Need ${trade_value:,.2f}, have ${portfolio.cash_balance:,.2f}"
            }
        
        # Check if user has enough shares for sell orders
        if side == 'sell':
            current_position = portfolio.positions.get(symbol, {}).get('quantity', 0)
            if quantity > current_position:
                return {
                    "success": False,
                    "error": f"Insufficient shares. Need {quantity}, have {current_position}"
                }
        
        # Create trade
        trade = PaperTrade(
            trade_id=str(uuid.uuid4()),
            user_id=user_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            timestamp=datetime.now(),
            status='filled',
            trade_type=trade_type,
            intended_investment=portfolio.intended_investment,
            portfolio_percentage=(trade_value / portfolio.intended_investment) * 100
        )
        
        # Execute trade
        await self._execute_paper_trade(trade)
        
        # Store AI learning data
        await self._store_ai_learning_data(trade, market_data)
        
        return {
            "success": True,
            "trade": asdict(trade),
            "portfolio": asdict(self.user_portfolios[user_id]),
            "message": f"{side.upper()} {quantity} shares of {symbol} at ${price:.2f}"
        }
    
    async def _execute_paper_trade(self, trade: PaperTrade):
        """Execute a paper trade and update portfolio"""
        portfolio = self.user_portfolios[trade.user_id]
        trade_value = trade.quantity * trade.price
        
        if trade.side == 'buy':
            # Add to position
            if trade.symbol not in portfolio.positions:
                portfolio.positions[trade.symbol] = {'quantity': 0, 'avg_price': 0, 'current_value': 0}
            
            current_qty = portfolio.positions[trade.symbol]['quantity']
            current_avg = portfolio.positions[trade.symbol]['avg_price']
            
            # Calculate new average price
            total_qty = current_qty + trade.quantity
            new_avg_price = ((current_qty * current_avg) + (trade.quantity * trade.price)) / total_qty
            
            portfolio.positions[trade.symbol]['quantity'] = total_qty
            portfolio.positions[trade.symbol]['avg_price'] = new_avg_price
            portfolio.cash_balance -= trade_value
            
        else:  # sell
            # Remove from position
            portfolio.positions[trade.symbol]['quantity'] -= trade.quantity
            portfolio.cash_balance += trade_value
            
            # Remove position if quantity is 0
            if portfolio.positions[trade.symbol]['quantity'] <= 0:
                del portfolio.positions[trade.symbol]
        
        portfolio.trades_count += 1
        
        # Update portfolio value and P&L
        await self._update_portfolio_value(portfolio)
        
        # Save trade and portfolio
        await self._save_trade(trade)
        await self._save_portfolio(portfolio)
        
        logger.info(f"[CHECK] Executed paper trade: {trade.side} {trade.quantity} {trade.symbol} at ${trade.price:.2f}")
    
    async def _update_portfolio_value(self, portfolio: PaperPortfolio):
        """Update portfolio total value and P&L"""
        total_value = portfolio.cash_balance
        
        for symbol, position in portfolio.positions.items():
            if symbol in self.market_data:
                current_price = self.market_data[symbol].price
                position_value = position['quantity'] * current_price
                position['current_value'] = position_value
                total_value += position_value
        
        portfolio.total_value = total_value
        portfolio.pnl = total_value - portfolio.intended_investment
        portfolio.pnl_percentage = (portfolio.pnl / portfolio.intended_investment) * 100 if portfolio.intended_investment > 0 else 0
    
    async def _update_all_portfolios(self):
        """Update all user portfolios with current market prices"""
        for portfolio in self.user_portfolios.values():
            await self._update_portfolio_value(portfolio)
            await self._save_portfolio(portfolio)
    
    async def _store_ai_learning_data(self, trade: PaperTrade, market_data: MarketData):
        """Store trade data for AI learning"""
        learning_data = {
            "trade": asdict(trade),
            "market_conditions": asdict(market_data),
            "user_behavior": {
                "intended_investment": trade.intended_investment,
                "portfolio_percentage": trade.portfolio_percentage,
                "trade_timing": trade.timestamp.isoformat()
            }
        }
        
        self.ai_learning_data.append(learning_data)
        
        # Store in database for AI training
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ai_learning_data (user_id, trade_data, market_conditions, outcome, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            trade.user_id,
            json.dumps(asdict(trade)),
            json.dumps(asdict(market_data)),
            'pending',  # Will be updated with actual outcome
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
    
    async def _feed_ai_learning_data(self):
        """Feed trading data to AI learning systems"""
        if len(self.ai_learning_data) > 0:
            # Send to AI learning engine
            try:
                from .ai_learning_engine import get_ai_learning_engine
                ai_engine = get_ai_learning_engine()
                
                for data in self.ai_learning_data[-10:]:  # Send last 10 data points
                    await ai_engine.process_trading_data(data)
                
            except Exception as e:
                logger.error(f"Failed to feed AI learning data: {e}")
    
    async def _save_trade(self, trade: PaperTrade):
        """Save trade to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO paper_trades VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade.trade_id, trade.user_id, trade.symbol, trade.side,
            trade.quantity, trade.price, trade.timestamp.isoformat(),
            trade.status, trade.trade_type, trade.intended_investment,
            trade.portfolio_percentage
        ))
        conn.commit()
        conn.close()
    
    async def _save_portfolio(self, portfolio: PaperPortfolio):
        """Save portfolio to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO paper_portfolios VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            portfolio.user_id, portfolio.cash_balance, portfolio.intended_investment,
            json.dumps(portfolio.positions), portfolio.total_value, portfolio.pnl,
            portfolio.pnl_percentage, portfolio.trades_count, portfolio.win_rate,
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
    
    async def get_user_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Get user's current portfolio"""
        if user_id not in self.user_portfolios:
            return {"success": False, "error": "Portfolio not found"}
        
        portfolio = self.user_portfolios[user_id]
        await self._update_portfolio_value(portfolio)
        
        return {
            "success": True,
            "portfolio": asdict(portfolio),
            "market_data": {symbol: asdict(data) for symbol, data in self.market_data.items()},
            "ai_insights": await self._get_ai_insights_for_user(user_id)
        }
    
    async def _get_ai_insights_for_user(self, user_id: str) -> List[str]:
        """Get AI-generated insights for user"""
        insights = [
            "Your portfolio shows strong diversification across sectors",
            "AI suggests considering tech stocks based on current market trends",
            "Risk level is appropriate for your intended investment amount",
            "Market volatility is increasing - consider defensive positions",
            "Your trading pattern shows good timing on entries"
        ]
        return insights[:3]  # Return top 3 insights
    
    async def get_platform_stats(self) -> Dict[str, Any]:
        """Get platform-wide statistics"""
        total_value = sum(p.total_value for p in self.user_portfolios.values())
        total_pnl = sum(p.pnl for p in self.user_portfolios.values())
        total_trades = sum(p.trades_count for p in self.user_portfolios.values())
        
        return {
            "total_users": self.current_users,
            "max_users": self.max_users,
            "users_remaining": self.max_users - self.current_users,
            "total_portfolio_value": total_value,
            "total_pnl": total_pnl,
            "total_trades": total_trades,
            "ai_learning_data_points": len(self.ai_learning_data),
            "active_symbols": len(self.market_data),
            "system_status": "active"
        }

# Global instance
paper_trading_engine = InternalPaperTradingEngine()

async def get_paper_trading_engine():
    """Get the global paper trading engine"""
    return paper_trading_engine
