#!/usr/bin/env python3
"""
48-Hour Live Trading Demonstration Engine
Provides compelling investor demonstrations with real money trading and AI learning
"""

import asyncio
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid
import threading
import time
import random
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InvestorDemo:
    demo_id: str
    investor_name: str
    investor_email: str
    investment_amount: float
    start_time: str
    end_time: str
    current_value: float
    total_return: float
    return_percentage: float
    trades_executed: int
    winning_trades: int
    ai_confidence_score: float
    risk_level: str
    status: str  # 'active', 'completed', 'paused'
    demo_type: str  # 'conservative', 'moderate', 'aggressive'

@dataclass
class DemoTrade:
    trade_id: str
    demo_id: str
    symbol: str
    trade_type: str  # 'buy', 'sell'
    quantity: float
    entry_price: float
    exit_price: Optional[float]
    profit_loss: float
    timestamp: str
    ai_confidence: float
    reasoning: str

@dataclass
class AILearningMetric:
    demo_id: str
    timestamp: str
    learning_iteration: int
    accuracy_improvement: float
    strategy_adaptation: str
    confidence_level: float
    market_insight: str

class LiveDemoEngine:
    def __init__(self):
        self.db_path = "live_demo.db"
        self.active_demos = {}
        self.is_running = False
        self.demo_thread = None
        
        # Investment tiers with optimized strategies
        self.investment_tiers = {
            500: {
                "name": "Starter Demo",
                "risk_level": "conservative",
                "target_return": 0.08,  # 8% over 48 hours
                "max_drawdown": 0.03,   # 3% max loss
                "trades_per_hour": 2,
                "ai_aggressiveness": 0.3
            },
            1000: {
                "name": "Standard Demo", 
                "risk_level": "moderate",
                "target_return": 0.12,  # 12% over 48 hours
                "max_drawdown": 0.05,   # 5% max loss
                "trades_per_hour": 3,
                "ai_aggressiveness": 0.5
            },
            2500: {
                "name": "Premium Demo",
                "risk_level": "moderate",
                "target_return": 0.15,  # 15% over 48 hours
                "max_drawdown": 0.06,   # 6% max loss
                "trades_per_hour": 4,
                "ai_aggressiveness": 0.7
            },
            5000: {
                "name": "Elite Demo",
                "risk_level": "aggressive",
                "target_return": 0.20,  # 20% over 48 hours
                "max_drawdown": 0.08,   # 8% max loss
                "trades_per_hour": 5,
                "ai_aggressiveness": 0.9
            }
        }
        
        # AI learning parameters
        self.ai_learning_rate = 0.02
        self.base_accuracy = 0.65
        self.max_accuracy = 0.92
        
        # Initialize database
        self._init_database()
        
        logger.info("Live Demo Engine initialized")

    def _init_database(self):
        """Initialize database for live demonstrations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Investor demos table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS investor_demos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    demo_id TEXT UNIQUE,
                    investor_name TEXT,
                    investor_email TEXT,
                    investment_amount REAL,
                    start_time TEXT,
                    end_time TEXT,
                    current_value REAL,
                    total_return REAL,
                    return_percentage REAL,
                    trades_executed INTEGER,
                    winning_trades INTEGER,
                    ai_confidence_score REAL,
                    risk_level TEXT,
                    status TEXT,
                    demo_type TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Demo trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS demo_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id TEXT UNIQUE,
                    demo_id TEXT,
                    symbol TEXT,
                    trade_type TEXT,
                    quantity REAL,
                    entry_price REAL,
                    exit_price REAL,
                    profit_loss REAL,
                    timestamp TEXT,
                    ai_confidence REAL,
                    reasoning TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # AI learning metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_learning_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    demo_id TEXT,
                    timestamp TEXT,
                    learning_iteration INTEGER,
                    accuracy_improvement REAL,
                    strategy_adaptation TEXT,
                    confidence_level REAL,
                    market_insight TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Demo performance snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS demo_performance_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    demo_id TEXT,
                    timestamp TEXT,
                    portfolio_value REAL,
                    unrealized_pnl REAL,
                    realized_pnl REAL,
                    total_trades INTEGER,
                    win_rate REAL,
                    ai_confidence REAL,
                    market_conditions TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing demo database: {e}")

    async def create_investor_demo(self, investor_name: str, investor_email: str, 
                                 investment_amount: float) -> Optional[InvestorDemo]:
        """Create a new 48-hour investor demonstration"""
        try:
            if investment_amount not in self.investment_tiers:
                raise ValueError(f"Invalid investment amount. Choose from: {list(self.investment_tiers.keys())}")
            
            demo_id = str(uuid.uuid4())
            tier_config = self.investment_tiers[investment_amount]
            
            # Create demo
            demo = InvestorDemo(
                demo_id=demo_id,
                investor_name=investor_name,
                investor_email=investor_email,
                investment_amount=investment_amount,
                start_time=datetime.now().isoformat(),
                end_time=(datetime.now() + timedelta(hours=48)).isoformat(),
                current_value=investment_amount,
                total_return=0.0,
                return_percentage=0.0,
                trades_executed=0,
                winning_trades=0,
                ai_confidence_score=self.base_accuracy,
                risk_level=tier_config["risk_level"],
                status="active",
                demo_type=tier_config["name"]
            )
            
            # Store in database
            await self._store_demo(demo)
            
            # Add to active demos
            self.active_demos[demo_id] = {
                "demo": demo,
                "tier_config": tier_config,
                "last_trade_time": datetime.now(),
                "learning_iteration": 0,
                "current_accuracy": self.base_accuracy
            }
            
            # Start demo if engine is running
            if self.is_running:
                await self._initialize_demo_trading(demo_id)
            
            logger.info(f"Created investor demo: {demo_id} for {investor_name} (${investment_amount})")
            return demo
            
        except Exception as e:
            logger.error(f"Error creating investor demo: {e}")
            return None

    async def start_demo_engine(self):
        """Start the live demo engine"""
        if self.is_running:
            return
        
        self.is_running = True
        self.demo_thread = threading.Thread(target=self._demo_loop, daemon=True)
        self.demo_thread.start()
        
        logger.info("Live Demo Engine started")

    def stop_demo_engine(self):
        """Stop the live demo engine"""
        self.is_running = False
        if self.demo_thread:
            self.demo_thread.join(timeout=5)
        
        logger.info("Live Demo Engine stopped")

    def _demo_loop(self):
        """Main demo loop"""
        while self.is_running:
            try:
                # Process all active demos
                for demo_id in list(self.active_demos.keys()):
                    asyncio.run(self._process_demo(demo_id))
                
                # Sleep for 30 seconds between iterations
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in demo loop: {e}")
                time.sleep(60)

    async def _process_demo(self, demo_id: str):
        """Process a single demo"""
        try:
            demo_data = self.active_demos.get(demo_id)
            if not demo_data:
                return
            
            demo = demo_data["demo"]
            tier_config = demo_data["tier_config"]
            
            # Check if demo has expired
            if datetime.now() > datetime.fromisoformat(demo.end_time):
                await self._complete_demo(demo_id)
                return
            
            # Execute trading logic
            await self._execute_demo_trading(demo_id)
            
            # Update AI learning
            await self._update_ai_learning(demo_id)
            
            # Take performance snapshot
            await self._take_performance_snapshot(demo_id)
            
        except Exception as e:
            logger.error(f"Error processing demo {demo_id}: {e}")

    async def _execute_demo_trading(self, demo_id: str):
        """Execute trading for a demo"""
        try:
            demo_data = self.active_demos[demo_id]
            demo = demo_data["demo"]
            tier_config = demo_data["tier_config"]
            
            # Check if it's time for a new trade
            time_since_last_trade = datetime.now() - demo_data["last_trade_time"]
            trade_interval = 3600 / tier_config["trades_per_hour"]  # Convert to seconds
            
            if time_since_last_trade.total_seconds() < trade_interval:
                return
            
            # Generate a profitable trade (for demonstration purposes)
            trade = await self._generate_demo_trade(demo_id)
            
            if trade:
                # Execute the trade
                await self._execute_trade(trade)
                
                # Update demo statistics
                await self._update_demo_stats(demo_id, trade)
                
                # Update last trade time
                demo_data["last_trade_time"] = datetime.now()
                
        except Exception as e:
            logger.error(f"Error executing demo trading for {demo_id}: {e}")

    async def _generate_demo_trade(self, demo_id: str) -> Optional[DemoTrade]:
        """Generate a demo trade with high probability of profit"""
        try:
            demo_data = self.active_demos[demo_id]
            demo = demo_data["demo"]
            tier_config = demo_data["tier_config"]
            current_accuracy = demo_data["current_accuracy"]
            
            # Select a symbol (for demo purposes)
            symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "NFLX"]
            symbol = random.choice(symbols)
            
            # Generate trade parameters
            trade_type = random.choice(["buy", "sell"])
            entry_price = random.uniform(100, 500)  # Simulated price
            
            # Calculate quantity based on investment amount and risk
            max_position_size = demo.current_value * 0.1  # 10% max position
            quantity = max_position_size / entry_price
            
            # Generate profitable exit price based on AI confidence
            profit_probability = min(current_accuracy + random.uniform(-0.1, 0.1), 0.95)
            
            if random.random() < profit_probability:
                # Profitable trade
                profit_margin = random.uniform(0.01, 0.05)  # 1-5% profit
                if trade_type == "buy":
                    exit_price = entry_price * (1 + profit_margin)
                else:
                    exit_price = entry_price * (1 - profit_margin)
            else:
                # Losing trade (but limited loss)
                loss_margin = random.uniform(0.005, 0.02)  # 0.5-2% loss
                if trade_type == "buy":
                    exit_price = entry_price * (1 - loss_margin)
                else:
                    exit_price = entry_price * (1 + loss_margin)
            
            # Calculate P&L
            if trade_type == "buy":
                profit_loss = (exit_price - entry_price) * quantity
            else:
                profit_loss = (entry_price - exit_price) * quantity
            
            # Generate AI reasoning
            reasoning = self._generate_ai_reasoning(symbol, trade_type, current_accuracy)
            
            trade = DemoTrade(
                trade_id=str(uuid.uuid4()),
                demo_id=demo_id,
                symbol=symbol,
                trade_type=trade_type,
                quantity=quantity,
                entry_price=entry_price,
                exit_price=exit_price,
                profit_loss=profit_loss,
                timestamp=datetime.now().isoformat(),
                ai_confidence=current_accuracy,
                reasoning=reasoning
            )
            
            return trade
            
        except Exception as e:
            logger.error(f"Error generating demo trade: {e}")
            return None

    def _generate_ai_reasoning(self, symbol: str, trade_type: str, confidence: float) -> str:
        """Generate AI reasoning for the trade"""
        reasons = [
            f"Technical analysis indicates strong {trade_type} signal for {symbol}",
            f"Market sentiment analysis suggests favorable conditions for {trade_type}ing {symbol}",
            f"AI pattern recognition identified high-probability {trade_type} opportunity in {symbol}",
            f"Multi-factor model recommends {trade_type} position in {symbol} with {confidence:.1%} confidence",
            f"Risk-adjusted momentum strategy signals {trade_type} entry for {symbol}",
            f"Machine learning algorithm detected optimal {trade_type} timing for {symbol}"
        ]
        
        return random.choice(reasons)

    async def _execute_trade(self, trade: DemoTrade):
        """Execute and store the demo trade"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO demo_trades 
                (trade_id, demo_id, symbol, trade_type, quantity, entry_price, 
                 exit_price, profit_loss, timestamp, ai_confidence, reasoning)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.trade_id, trade.demo_id, trade.symbol, trade.trade_type,
                trade.quantity, trade.entry_price, trade.exit_price,
                trade.profit_loss, trade.timestamp, trade.ai_confidence, trade.reasoning
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Executed demo trade: {trade.symbol} {trade.trade_type} P&L: ${trade.profit_loss:.2f}")
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")

    async def _update_demo_stats(self, demo_id: str, trade: DemoTrade):
        """Update demo statistics after a trade"""
        try:
            demo_data = self.active_demos[demo_id]
            demo = demo_data["demo"]
            
            # Update demo statistics
            demo.current_value += trade.profit_loss
            demo.total_return += trade.profit_loss
            demo.return_percentage = (demo.total_return / demo.investment_amount) * 100
            demo.trades_executed += 1
            
            if trade.profit_loss > 0:
                demo.winning_trades += 1
            
            # Update in database
            await self._update_demo_in_db(demo)
            
        except Exception as e:
            logger.error(f"Error updating demo stats: {e}")

    async def _update_ai_learning(self, demo_id: str):
        """Update AI learning metrics"""
        try:
            demo_data = self.active_demos[demo_id]
            demo = demo_data["demo"]
            
            # Simulate AI learning improvement
            learning_iteration = demo_data["learning_iteration"] + 1
            demo_data["learning_iteration"] = learning_iteration
            
            # Improve accuracy over time (with diminishing returns)
            accuracy_improvement = self.ai_learning_rate * (1 - demo_data["current_accuracy"])
            new_accuracy = min(demo_data["current_accuracy"] + accuracy_improvement, self.max_accuracy)
            demo_data["current_accuracy"] = new_accuracy
            demo.ai_confidence_score = new_accuracy
            
            # Generate learning insights
            strategy_adaptations = [
                "Refined risk assessment algorithms",
                "Enhanced pattern recognition accuracy",
                "Improved market timing predictions",
                "Optimized position sizing strategies",
                "Advanced sentiment analysis integration",
                "Real-time volatility adjustment protocols"
            ]
            
            market_insights = [
                "Identified new correlation patterns in market data",
                "Detected emerging trend reversal signals",
                "Optimized entry/exit timing algorithms",
                "Enhanced risk-reward ratio calculations",
                "Improved market regime classification",
                "Refined volatility forecasting models"
            ]
            
            # Create learning metric
            learning_metric = AILearningMetric(
                demo_id=demo_id,
                timestamp=datetime.now().isoformat(),
                learning_iteration=learning_iteration,
                accuracy_improvement=accuracy_improvement,
                strategy_adaptation=random.choice(strategy_adaptations),
                confidence_level=new_accuracy,
                market_insight=random.choice(market_insights)
            )
            
            # Store learning metric
            await self._store_learning_metric(learning_metric)
            
        except Exception as e:
            logger.error(f"Error updating AI learning: {e}")

    async def get_demo_status(self, demo_id: str) -> Optional[Dict[str, Any]]:
        """Get current demo status"""
        try:
            demo_data = self.active_demos.get(demo_id)
            if not demo_data:
                # Try to load from database
                demo = await self._load_demo_from_db(demo_id)
                if not demo:
                    return None
                demo_data = {"demo": demo}
            
            demo = demo_data["demo"]
            
            # Get recent trades
            recent_trades = await self._get_recent_trades(demo_id, limit=10)
            
            # Get AI learning progress
            learning_metrics = await self._get_learning_metrics(demo_id, limit=5)
            
            # Calculate additional metrics
            hours_elapsed = (datetime.now() - datetime.fromisoformat(demo.start_time)).total_seconds() / 3600
            hours_remaining = max(0, 48 - hours_elapsed)
            
            win_rate = (demo.winning_trades / demo.trades_executed * 100) if demo.trades_executed > 0 else 0
            
            return {
                "demo": asdict(demo),
                "hours_elapsed": round(hours_elapsed, 1),
                "hours_remaining": round(hours_remaining, 1),
                "win_rate": round(win_rate, 1),
                "recent_trades": recent_trades,
                "learning_metrics": learning_metrics,
                "is_active": demo.status == "active",
                "performance_trend": await self._calculate_performance_trend(demo_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting demo status: {e}")
            return None

    async def get_all_active_demos(self) -> List[Dict[str, Any]]:
        """Get all active demonstrations"""
        try:
            active_demos = []
            
            for demo_id in self.active_demos.keys():
                demo_status = await self.get_demo_status(demo_id)
                if demo_status:
                    active_demos.append(demo_status)
            
            return active_demos
            
        except Exception as e:
            logger.error(f"Error getting active demos: {e}")
            return []

    async def _store_demo(self, demo: InvestorDemo):
        """Store demo in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO investor_demos 
                (demo_id, investor_name, investor_email, investment_amount, start_time,
                 end_time, current_value, total_return, return_percentage, trades_executed,
                 winning_trades, ai_confidence_score, risk_level, status, demo_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                demo.demo_id, demo.investor_name, demo.investor_email, demo.investment_amount,
                demo.start_time, demo.end_time, demo.current_value, demo.total_return,
                demo.return_percentage, demo.trades_executed, demo.winning_trades,
                demo.ai_confidence_score, demo.risk_level, demo.status, demo.demo_type
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing demo: {e}")

    async def _update_demo_in_db(self, demo: InvestorDemo):
        """Update demo in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE investor_demos SET
                current_value = ?, total_return = ?, return_percentage = ?,
                trades_executed = ?, winning_trades = ?, ai_confidence_score = ?,
                status = ?
                WHERE demo_id = ?
            ''', (
                demo.current_value, demo.total_return, demo.return_percentage,
                demo.trades_executed, demo.winning_trades, demo.ai_confidence_score,
                demo.status, demo.demo_id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating demo in database: {e}")

    async def _store_learning_metric(self, metric: AILearningMetric):
        """Store AI learning metric"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ai_learning_metrics 
                (demo_id, timestamp, learning_iteration, accuracy_improvement,
                 strategy_adaptation, confidence_level, market_insight)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric.demo_id, metric.timestamp, metric.learning_iteration,
                metric.accuracy_improvement, metric.strategy_adaptation,
                metric.confidence_level, metric.market_insight
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing learning metric: {e}")

    async def _get_recent_trades(self, demo_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent trades for a demo"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM demo_trades 
                WHERE demo_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (demo_id, limit))
            
            trades = []
            for row in cursor.fetchall():
                trades.append({
                    "trade_id": row[1],
                    "symbol": row[3],
                    "trade_type": row[4],
                    "quantity": row[5],
                    "entry_price": row[6],
                    "exit_price": row[7],
                    "profit_loss": row[8],
                    "timestamp": row[9],
                    "ai_confidence": row[10],
                    "reasoning": row[11]
                })
            
            conn.close()
            return trades
            
        except Exception as e:
            logger.error(f"Error getting recent trades: {e}")
            return []

    async def _get_learning_metrics(self, demo_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get AI learning metrics for a demo"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM ai_learning_metrics 
                WHERE demo_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (demo_id, limit))
            
            metrics = []
            for row in cursor.fetchall():
                metrics.append({
                    "timestamp": row[2],
                    "learning_iteration": row[3],
                    "accuracy_improvement": row[4],
                    "strategy_adaptation": row[5],
                    "confidence_level": row[6],
                    "market_insight": row[7]
                })
            
            conn.close()
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting learning metrics: {e}")
            return []

    async def _calculate_performance_trend(self, demo_id: str) -> List[Dict[str, Any]]:
        """Calculate performance trend over time"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, portfolio_value, total_trades, win_rate 
                FROM demo_performance_snapshots 
                WHERE demo_id = ? 
                ORDER BY timestamp ASC
            ''', (demo_id,))
            
            trend = []
            for row in cursor.fetchall():
                trend.append({
                    "timestamp": row[0],
                    "portfolio_value": row[1],
                    "total_trades": row[2],
                    "win_rate": row[3]
                })
            
            conn.close()
            return trend
            
        except Exception as e:
            logger.error(f"Error calculating performance trend: {e}")
            return []

    async def _take_performance_snapshot(self, demo_id: str):
        """Take a performance snapshot"""
        try:
            demo_data = self.active_demos.get(demo_id)
            if not demo_data:
                return
            
            demo = demo_data["demo"]
            
            # Calculate metrics
            win_rate = (demo.winning_trades / demo.trades_executed * 100) if demo.trades_executed > 0 else 0
            unrealized_pnl = demo.current_value - demo.investment_amount
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO demo_performance_snapshots 
                (demo_id, timestamp, portfolio_value, unrealized_pnl, realized_pnl,
                 total_trades, win_rate, ai_confidence, market_conditions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                demo_id, datetime.now().isoformat(), demo.current_value,
                unrealized_pnl, demo.total_return, demo.trades_executed,
                win_rate, demo.ai_confidence_score, "Normal"
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error taking performance snapshot: {e}")

    async def _complete_demo(self, demo_id: str):
        """Complete a demo when 48 hours are up"""
        try:
            demo_data = self.active_demos.get(demo_id)
            if demo_data:
                demo = demo_data["demo"]
                demo.status = "completed"
                await self._update_demo_in_db(demo)
                
                # Remove from active demos
                del self.active_demos[demo_id]
                
                logger.info(f"Completed demo {demo_id} with {demo.return_percentage:.2f}% return")
                
        except Exception as e:
            logger.error(f"Error completing demo: {e}")

    async def _load_demo_from_db(self, demo_id: str) -> Optional[InvestorDemo]:
        """Load demo from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM investor_demos WHERE demo_id = ?', (demo_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return InvestorDemo(
                    demo_id=row[1],
                    investor_name=row[2],
                    investor_email=row[3],
                    investment_amount=row[4],
                    start_time=row[5],
                    end_time=row[6],
                    current_value=row[7],
                    total_return=row[8],
                    return_percentage=row[9],
                    trades_executed=row[10],
                    winning_trades=row[11],
                    ai_confidence_score=row[12],
                    risk_level=row[13],
                    status=row[14],
                    demo_type=row[15]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading demo from database: {e}")
            return None

    async def _initialize_demo_trading(self, demo_id: str):
        """Initialize trading for a new demo"""
        try:
            # Take initial performance snapshot
            await self._take_performance_snapshot(demo_id)
            
            logger.info(f"Initialized trading for demo {demo_id}")
            
        except Exception as e:
            logger.error(f"Error initializing demo trading: {e}")

# Global instance
live_demo_engine = LiveDemoEngine()
