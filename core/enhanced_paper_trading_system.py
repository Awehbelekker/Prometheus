"""
📊 ENHANCED INTERNAL PAPER TRADING SYSTEM
Complete paper trading system with session options, real market data, and gamification integration
"""

import sqlite3
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import yfinance as yf
from .dual_tier_permission_system import dual_tier_system, TradingPermission
from .gamification_engine import gamification_engine

logger = logging.getLogger(__name__)

class SessionType(Enum):
    """Paper trading session types"""
    QUICK_24H = "24_hour"
    EXTENDED_48H = "48_hour"
    FULL_WEEK = "168_hour"
    CUSTOM = "custom"

class SessionStatus(Enum):
    """Session status"""
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class PaperTradingSession:
    """Paper trading session"""
    session_id: str
    user_id: str
    session_type: SessionType
    starting_capital: float
    current_value: float
    duration_hours: int
    status: SessionStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    trades_count: int = 0
    profit_loss: float = 0.0
    return_percentage: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    positions: Dict[str, Any] = None
    session_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.positions is None:
            self.positions = {}
        if self.session_data is None:
            self.session_data = {}

@dataclass
class PaperTrade:
    """Individual paper trade"""
    trade_id: str
    session_id: str
    user_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    price: float
    timestamp: datetime
    trade_type: str  # 'market', 'limit', 'stop'
    status: str = 'filled'
    profit_loss: float = 0.0

@dataclass
class MarketDataPoint:
    """Real-time market data"""
    symbol: str
    price: float
    bid: float
    ask: float
    volume: int
    change: float
    change_percent: float
    timestamp: datetime

class EnhancedPaperTradingSystem:
    """
    📊 ENHANCED PAPER TRADING SYSTEM
    Complete paper trading with sessions, real market data, and gamification
    """
    
    def __init__(self, db_path: str = "enhanced_paper_trading.db"):
        self.db_path = db_path
        self.active_sessions: Dict[str, PaperTradingSession] = {}
        self.market_data_cache: Dict[str, MarketDataPoint] = {}
        self.supported_symbols = [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
            'SPY', 'QQQ', 'IWM', 'GLD', 'SLV', 'VTI', 'BTC-USD', 'ETH-USD'
        ]
        self._init_database()
        self._market_data_task = None
        logger.info("📊 Enhanced Paper Trading System initialized")

    def start_market_data_feed(self):
        """Start the market data feed if not already running"""
        try:
            if self._market_data_task is None or self._market_data_task.done():
                loop = asyncio.get_event_loop()
                self._market_data_task = loop.create_task(self._start_market_data_feed())
                logger.info("🔄 Market data feed started")
        except RuntimeError:
            # No event loop running, will start when needed
            logger.info("🔄 Market data feed will start when event loop is available")

    def _init_database(self):
        """Initialize paper trading database"""
        with sqlite3.connect(self.db_path) as conn:
            # Sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS paper_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_type TEXT NOT NULL,
                    starting_capital REAL NOT NULL,
                    current_value REAL NOT NULL,
                    duration_hours INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    trades_count INTEGER DEFAULT 0,
                    profit_loss REAL DEFAULT 0.0,
                    return_percentage REAL DEFAULT 0.0,
                    max_drawdown REAL DEFAULT 0.0,
                    win_rate REAL DEFAULT 0.0,
                    total_volume REAL DEFAULT 0.0,
                    positions TEXT,  -- JSON
                    session_data TEXT,  -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Add total_volume column if it doesn't exist (migration)
            try:
                conn.execute("ALTER TABLE paper_sessions ADD COLUMN total_volume REAL DEFAULT 0.0")
            except sqlite3.OperationalError:
                # Column already exists
                pass

            # Trades table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS paper_trades (
                    trade_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    trade_type TEXT NOT NULL,
                    status TEXT DEFAULT 'filled',
                    profit_loss REAL DEFAULT 0.0,
                    FOREIGN KEY (session_id) REFERENCES paper_sessions (session_id)
                )
            """)
            
            # Market data table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    symbol TEXT PRIMARY KEY,
                    price REAL NOT NULL,
                    bid REAL NOT NULL,
                    ask REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    change_amount REAL NOT NULL,
                    change_percent REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("[CHECK] Enhanced paper trading database initialized")

    async def _start_market_data_feed(self):
        """Start real-time market data feed"""
        logger.info("🔄 Starting real-time market data feed...")
        
        while True:
            try:
                for symbol in self.supported_symbols:
                    await self._update_market_data(symbol)
                
                # Update active sessions
                await self._update_active_sessions()
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Market data feed error: {e}")
                await asyncio.sleep(10)

    async def _update_market_data(self, symbol: str):
        """Update market data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d", interval="1m")
            
            if not hist.empty:
                latest = hist.iloc[-1]
                current_price = float(latest['Close'])
                volume = int(latest['Volume'])
                
                # Calculate change
                if len(hist) > 1:
                    prev_price = float(hist.iloc[-2]['Close'])
                    change = current_price - prev_price
                    change_percent = (change / prev_price) * 100 if prev_price > 0 else 0
                else:
                    change = 0
                    change_percent = 0
                
                # Create market data point
                market_data = MarketDataPoint(
                    symbol=symbol,
                    price=current_price,
                    bid=current_price * 0.999,  # Approximate bid
                    ask=current_price * 1.001,  # Approximate ask
                    volume=volume,
                    change=change,
                    change_percent=change_percent,
                    timestamp=datetime.now()
                )
                
                # Cache the data
                self.market_data_cache[symbol] = market_data
                
                # Store in database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO market_data (
                            symbol, price, bid, ask, volume, change_amount, change_percent
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        symbol, current_price, market_data.bid, market_data.ask,
                        volume, change, change_percent
                    ))
                    conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to update market data for {symbol}: {e}")

    async def _update_active_sessions(self):
        """Update all active trading sessions and execute trading logic"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get all active sessions
                cursor.execute("""
                    SELECT session_id, user_id, current_value, trades_count, starting_capital
                    FROM paper_sessions
                    WHERE status = 'active'
                """)

                active_sessions = cursor.fetchall()

                for session_id, user_id, current_value, trades_count, starting_capital in active_sessions:
                    logger.debug(f"Processing session {session_id[:8]}... - Value: ${current_value:,.2f}, Trades: {trades_count}")

                    # Execute trading logic for this session
                    await self._execute_trading_cycle(session_id, user_id, current_value, starting_capital)

        except Exception as e:
            logger.error(f"Failed to update active sessions: {e}")

    async def _execute_trading_cycle(self, session_id: str, user_id: str, current_value: float, starting_capital: float):
        """Execute trading cycle for a specific session"""
        try:
            # Import AI trading intelligence
            from .ai_trading_intelligence import get_ai_trading_signal

            # Analyze each supported symbol
            for symbol in self.supported_symbols[:5]:  # Limit to 5 symbols for performance
                try:
                    # Get current market data
                    market_data_point = self.market_data_cache.get(symbol)
                    if not market_data_point:
                        continue

                    # Convert to dict for AI analysis
                    market_data = {
                        'symbol': symbol,
                        'price': market_data_point.price,
                        'volume': market_data_point.volume,
                        'change': market_data_point.change_percent,
                        'timestamp': market_data_point.timestamp.isoformat()
                    }

                    # Get AI trading signal
                    ai_signal = await get_ai_trading_signal(symbol, market_data)

                    logger.info(f"🤖 AI Signal for {symbol}: {ai_signal.signal} (confidence: {ai_signal.confidence:.2f})")

                    # Execute trade if confidence is high enough and signal is not HOLD
                    if ai_signal.confidence >= 0.7 and ai_signal.signal != 'HOLD':
                        await self._execute_paper_trade(session_id, symbol, ai_signal, market_data_point.price)

                    # Small delay between symbol analysis
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error analyzing {symbol} for session {session_id}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Trading cycle error for session {session_id}: {e}")

    async def _execute_paper_trade(self, session_id: str, symbol: str, ai_signal, current_price: float):
        """Execute a paper trade based on AI signal"""
        try:
            logger.info(f"🔧 Attempting to execute trade: {symbol} {ai_signal.signal} @ ${current_price}")

            # Calculate position size (2% of current portfolio value)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT current_value FROM paper_sessions WHERE session_id = ?", (session_id,))
                result = cursor.fetchone()
                if not result:
                    logger.error(f"[ERROR] Session {session_id} not found")
                    return

                current_value = result[0]
                position_size = current_value * 0.05  # 5% position size for better execution
                quantity = max(1, int(position_size / current_price))  # Minimum 1 share

                # For expensive stocks, use fractional shares concept (round to 2 decimal places)
                if quantity == 0:
                    quantity = round(position_size / current_price, 2)
                    if quantity < 0.01:
                        quantity = 0.01  # Minimum fractional share

                logger.info(f"📊 Portfolio: ${current_value:,.2f}, Position size: ${position_size:.2f}, Quantity: {quantity}")

                if quantity <= 0:
                    logger.warning(f"[WARNING]️ Quantity too small: {quantity}")
                    return

                # Create trade record
                trade_id = str(uuid.uuid4())
                side = ai_signal.signal  # BUY or SELL

                # Get user_id for the session
                cursor.execute("SELECT user_id FROM paper_sessions WHERE session_id = ?", (session_id,))
                user_result = cursor.fetchone()
                if not user_result:
                    return
                user_id = user_result[0]

                # Insert trade
                cursor.execute("""
                    INSERT INTO paper_trades
                    (trade_id, session_id, user_id, symbol, side, quantity, price, timestamp, trade_type, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trade_id, session_id, user_id, symbol, side, quantity, current_price,
                    datetime.now(), 'ai_signal', 'filled'
                ))

                # Update session trade count
                cursor.execute("""
                    UPDATE paper_sessions
                    SET trades_count = trades_count + 1
                    WHERE session_id = ?
                """, (session_id,))

                conn.commit()

                logger.info(f"[CHECK] Executed {side} trade: {quantity} shares of {symbol} at ${current_price:.2f}")

        except Exception as e:
            logger.error(f"Failed to execute paper trade: {e}")

    async def create_paper_session(self, user_id: str, session_type: SessionType,
                                 starting_capital: float, custom_hours: Optional[int] = None) -> Optional[str]:
        """Create a new paper trading session"""
        try:
            # Check user permissions
            if not dual_tier_system.has_permission(user_id, TradingPermission.PAPER_TRADING):
                logger.warning(f"User {user_id} does not have paper trading permission")
                return None
            
            # Determine session duration
            duration_map = {
                SessionType.QUICK_24H: 24,
                SessionType.EXTENDED_48H: 48,
                SessionType.FULL_WEEK: 168,
                SessionType.CUSTOM: custom_hours or 24
            }
            duration_hours = duration_map[session_type]
            
            # Create session
            session = PaperTradingSession(
                session_id=str(uuid.uuid4()),
                user_id=user_id,
                session_type=session_type,
                starting_capital=starting_capital,
                current_value=starting_capital,
                duration_hours=duration_hours,
                status=SessionStatus.NOT_STARTED
            )
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO paper_sessions (
                        session_id, user_id, session_type, starting_capital,
                        current_value, duration_hours, status, positions, session_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    session.user_id,
                    session.session_type.value,
                    session.starting_capital,
                    session.current_value,
                    session.duration_hours,
                    session.status.value,
                    json.dumps(session.positions),
                    json.dumps(session.session_data)
                ))
                conn.commit()
            
            logger.info(f"[CHECK] Paper session created: {session.session_id} for user {user_id}")
            return session.session_id
            
        except Exception as e:
            logger.error(f"Failed to create paper session: {e}")
            return None

    async def start_session(self, session_id: str) -> bool:
        """Start a paper trading session"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            if session.status != SessionStatus.NOT_STARTED:
                logger.warning(f"Session {session_id} cannot be started - current status: {session.status}")
                return False
            
            # Update session status
            session.status = SessionStatus.ACTIVE
            session.start_time = datetime.now()
            session.end_time = session.start_time + timedelta(hours=session.duration_hours)
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE paper_sessions 
                    SET status = ?, start_time = ?, end_time = ?
                    WHERE session_id = ?
                """, (
                    session.status.value,
                    session.start_time,
                    session.end_time,
                    session_id
                ))
                conn.commit()
            
            # Add to active sessions
            self.active_sessions[session_id] = session
            
            logger.info(f"🚀 Paper session started: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            return False

    async def get_session(self, session_id: str) -> Optional[PaperTradingSession]:
        """Get paper trading session"""
        try:
            # Check active sessions first
            if session_id in self.active_sessions:
                return self.active_sessions[session_id]
            
            # Query database
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM paper_sessions WHERE session_id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                session = PaperTradingSession(
                    session_id=row['session_id'],
                    user_id=row['user_id'],
                    session_type=SessionType(row['session_type']),
                    starting_capital=row['starting_capital'],
                    current_value=row['current_value'],
                    duration_hours=row['duration_hours'],
                    status=SessionStatus(row['status']),
                    start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
                    end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                    trades_count=row['trades_count'],
                    profit_loss=row['profit_loss'],
                    return_percentage=row['return_percentage'],
                    max_drawdown=row['max_drawdown'],
                    win_rate=row['win_rate'],
                    positions=json.loads(row['positions']) if row['positions'] else {},
                    session_data=json.loads(row['session_data']) if row['session_data'] else {}
                )
                
                return session
                
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None

# Global instance
enhanced_paper_trading = EnhancedPaperTradingSystem()
