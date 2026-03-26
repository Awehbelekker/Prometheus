#!/usr/bin/env python3
"""
Real-time Performance Monitoring for Prometheus Trading Platform
Tracks actual user profits, losses, and trading performance
"""

import asyncio
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserPerformanceSnapshot:
    user_id: str
    timestamp: str
    account_balance: float
    portfolio_value: float
    total_pnl: float
    daily_pnl: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_profit_per_trade: float
    max_drawdown: float
    sharpe_ratio: float
    is_live_trading: bool

@dataclass
class PlatformPerformance:
    timestamp: str
    total_users: int
    active_traders: int
    live_trading_users: int
    total_platform_pnl: float
    total_trades_today: int
    avg_user_return: float
    top_performer_pnl: float
    platform_success_rate: float
    total_assets_under_management: float

class RealTimePerformanceMonitor:
    def __init__(self):
        self.db_path = "performance_monitoring.db"
        self.is_running = False
        self.monitoring_thread = None
        
        # Performance tracking intervals
        self.snapshot_interval = 60  # Take snapshots every minute
        self.cleanup_interval = 3600  # Cleanup old data every hour
        
        # Initialize database
        self._init_database()
        
        logger.info("Real-time Performance Monitor initialized")

    def _init_database(self):
        """Initialize database for performance monitoring"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # User performance snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_performance_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    timestamp TEXT,
                    account_balance REAL,
                    portfolio_value REAL,
                    total_pnl REAL,
                    daily_pnl REAL,
                    total_trades INTEGER,
                    winning_trades INTEGER,
                    losing_trades INTEGER,
                    win_rate REAL,
                    avg_profit_per_trade REAL,
                    max_drawdown REAL,
                    sharpe_ratio REAL,
                    is_live_trading BOOLEAN,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Platform performance snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS platform_performance_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    total_users INTEGER,
                    active_traders INTEGER,
                    live_trading_users INTEGER,
                    total_platform_pnl REAL,
                    total_trades_today INTEGER,
                    avg_user_return REAL,
                    top_performer_pnl REAL,
                    platform_success_rate REAL,
                    total_assets_under_management REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Real-time alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    alert_type TEXT,
                    message TEXT,
                    severity TEXT,
                    timestamp TEXT,
                    acknowledged BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing performance monitoring database: {e}")

    async def start_monitoring(self):
        """Start real-time performance monitoring"""
        if self.is_running:
            return
        
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("Real-time performance monitoring started")

    def stop_monitoring(self):
        """Stop real-time performance monitoring"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Real-time performance monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Take performance snapshots
                asyncio.run(self._take_performance_snapshots())
                
                # Check for alerts
                asyncio.run(self._check_performance_alerts())
                
                # Sleep for snapshot interval
                time.sleep(self.snapshot_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error

    async def _take_performance_snapshots(self):
        """Take performance snapshots for all users and platform"""
        try:
            # Get all active users from live trading engine
            from services.live_trading_engine import live_trading_engine
            
            # Take user snapshots
            await self._take_user_snapshots()
            
            # Take platform snapshot
            await self._take_platform_snapshot()
            
        except Exception as e:
            logger.error(f"Error taking performance snapshots: {e}")

    async def _take_user_snapshots(self):
        """Take performance snapshots for all users"""
        try:
            # Get all users with trading accounts
            live_trading_conn = sqlite3.connect("live_trading.db")
            cursor = live_trading_conn.cursor()
            
            cursor.execute('SELECT user_id FROM user_accounts WHERE is_live_enabled = 1')
            user_ids = [row[0] for row in cursor.fetchall()]
            live_trading_conn.close()
            
            # Take snapshot for each user
            for user_id in user_ids:
                await self._take_user_snapshot(user_id)
                
        except Exception as e:
            logger.error(f"Error taking user snapshots: {e}")

    async def _take_user_snapshot(self, user_id: str):
        """Take performance snapshot for a specific user"""
        try:
            from services.live_trading_engine import live_trading_engine
            
            # Get user performance data
            performance = await live_trading_engine.get_user_performance(user_id)
            
            if not performance:
                return
            
            # Calculate additional metrics
            win_rate = performance.get('win_rate', 0)
            total_trades = performance.get('total_trades', 0)
            winning_trades = performance.get('winning_trades', 0)
            losing_trades = total_trades - winning_trades
            
            avg_profit_per_trade = (performance.get('total_pnl', 0) / total_trades) if total_trades > 0 else 0
            
            # Calculate daily P&L
            daily_pnl = await self._calculate_daily_pnl(user_id)
            
            # Calculate max drawdown and Sharpe ratio (simplified)
            max_drawdown = await self._calculate_max_drawdown(user_id)
            sharpe_ratio = await self._calculate_sharpe_ratio(user_id)
            
            # Create snapshot
            snapshot = UserPerformanceSnapshot(
                user_id=user_id,
                timestamp=datetime.now().isoformat(),
                account_balance=performance.get('account_balance', 0),
                portfolio_value=performance.get('portfolio_value', 0),
                total_pnl=performance.get('total_pnl', 0),
                daily_pnl=daily_pnl,
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                avg_profit_per_trade=avg_profit_per_trade,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                is_live_trading=performance.get('is_live_enabled', False)
            )
            
            # Store snapshot
            await self._store_user_snapshot(snapshot)
            
        except Exception as e:
            logger.error(f"Error taking user snapshot for {user_id}: {e}")

    async def _take_platform_snapshot(self):
        """Take platform-wide performance snapshot"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get latest user snapshots
            cursor.execute('''
                SELECT * FROM user_performance_snapshots 
                WHERE timestamp > datetime('now', '-5 minutes')
            ''')
            recent_snapshots = cursor.fetchall()
            
            if not recent_snapshots:
                conn.close()
                return
            
            # Calculate platform metrics
            total_users = len(recent_snapshots)
            active_traders = len([s for s in recent_snapshots if s[7] > 0])  # total_trades > 0
            live_trading_users = len([s for s in recent_snapshots if s[14] == 1])  # is_live_trading
            
            total_platform_pnl = sum([s[5] for s in recent_snapshots])  # total_pnl
            total_trades_today = sum([s[7] for s in recent_snapshots])  # total_trades
            
            avg_user_return = total_platform_pnl / total_users if total_users > 0 else 0
            top_performer_pnl = max([s[5] for s in recent_snapshots]) if recent_snapshots else 0
            
            # Calculate platform success rate
            winning_users = len([s for s in recent_snapshots if s[5] > 0])  # total_pnl > 0
            platform_success_rate = (winning_users / total_users * 100) if total_users > 0 else 0
            
            # Calculate total assets under management
            total_aum = sum([s[4] for s in recent_snapshots])  # portfolio_value
            
            # Create platform snapshot
            platform_snapshot = PlatformPerformance(
                timestamp=datetime.now().isoformat(),
                total_users=total_users,
                active_traders=active_traders,
                live_trading_users=live_trading_users,
                total_platform_pnl=total_platform_pnl,
                total_trades_today=total_trades_today,
                avg_user_return=avg_user_return,
                top_performer_pnl=top_performer_pnl,
                platform_success_rate=platform_success_rate,
                total_assets_under_management=total_aum
            )
            
            # Store platform snapshot
            await self._store_platform_snapshot(platform_snapshot)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error taking platform snapshot: {e}")

    async def _store_user_snapshot(self, snapshot: UserPerformanceSnapshot):
        """Store user performance snapshot"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_performance_snapshots 
                (user_id, timestamp, account_balance, portfolio_value, total_pnl, 
                 daily_pnl, total_trades, winning_trades, losing_trades, win_rate,
                 avg_profit_per_trade, max_drawdown, sharpe_ratio, is_live_trading)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                snapshot.user_id, snapshot.timestamp, snapshot.account_balance,
                snapshot.portfolio_value, snapshot.total_pnl, snapshot.daily_pnl,
                snapshot.total_trades, snapshot.winning_trades, snapshot.losing_trades,
                snapshot.win_rate, snapshot.avg_profit_per_trade, snapshot.max_drawdown,
                snapshot.sharpe_ratio, snapshot.is_live_trading
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing user snapshot: {e}")

    async def _store_platform_snapshot(self, snapshot: PlatformPerformance):
        """Store platform performance snapshot"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO platform_performance_snapshots 
                (timestamp, total_users, active_traders, live_trading_users,
                 total_platform_pnl, total_trades_today, avg_user_return,
                 top_performer_pnl, platform_success_rate, total_assets_under_management)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                snapshot.timestamp, snapshot.total_users, snapshot.active_traders,
                snapshot.live_trading_users, snapshot.total_platform_pnl,
                snapshot.total_trades_today, snapshot.avg_user_return,
                snapshot.top_performer_pnl, snapshot.platform_success_rate,
                snapshot.total_assets_under_management
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing platform snapshot: {e}")

    async def get_real_time_performance(self) -> Dict[str, Any]:
        """Get current real-time performance data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get latest platform snapshot
            cursor.execute('''
                SELECT * FROM platform_performance_snapshots 
                ORDER BY created_at DESC LIMIT 1
            ''')
            platform_row = cursor.fetchone()
            
            # Get top performing users
            cursor.execute('''
                SELECT user_id, total_pnl, win_rate, total_trades 
                FROM user_performance_snapshots 
                WHERE timestamp > datetime('now', '-1 hour')
                ORDER BY total_pnl DESC LIMIT 10
            ''')
            top_performers = cursor.fetchall()
            
            # Get recent performance trend
            cursor.execute('''
                SELECT timestamp, total_platform_pnl, platform_success_rate 
                FROM platform_performance_snapshots 
                WHERE timestamp > datetime('now', '-24 hours')
                ORDER BY timestamp DESC
            ''')
            performance_trend = cursor.fetchall()
            
            conn.close()
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "platform_performance": {},
                "top_performers": [],
                "performance_trend": [],
                "is_live": True
            }
            
            if platform_row:
                result["platform_performance"] = {
                    "total_users": platform_row[2],
                    "active_traders": platform_row[3],
                    "live_trading_users": platform_row[4],
                    "total_platform_pnl": platform_row[5],
                    "total_trades_today": platform_row[6],
                    "avg_user_return": platform_row[7],
                    "top_performer_pnl": platform_row[8],
                    "platform_success_rate": platform_row[9],
                    "total_assets_under_management": platform_row[10]
                }
            
            result["top_performers"] = [
                {
                    "user_id": row[0],
                    "total_pnl": row[1],
                    "win_rate": row[2],
                    "total_trades": row[3]
                }
                for row in top_performers
            ]
            
            result["performance_trend"] = [
                {
                    "timestamp": row[0],
                    "total_pnl": row[1],
                    "success_rate": row[2]
                }
                for row in performance_trend
            ]
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting real-time performance: {e}")
            return {"error": str(e)}

    async def _calculate_daily_pnl(self, user_id: str) -> float:
        """Calculate daily P&L for user"""
        try:
            live_trading_conn = sqlite3.connect("live_trading.db")
            cursor = live_trading_conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT SUM(profit_loss) FROM live_trades 
                WHERE user_id = ? AND DATE(filled_at) = ? AND status = 'filled'
            ''', (user_id, today))
            
            result = cursor.fetchone()[0]
            live_trading_conn.close()
            
            return result or 0.0
            
        except Exception as e:
            logger.error(f"Error calculating daily P&L: {e}")
            return 0.0

    async def _calculate_max_drawdown(self, user_id: str) -> float:
        """Calculate maximum drawdown for user (simplified)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT portfolio_value FROM user_performance_snapshots 
                WHERE user_id = ? AND timestamp > datetime('now', '-30 days')
                ORDER BY timestamp ASC
            ''', (user_id,))
            
            values = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if len(values) < 2:
                return 0.0
            
            # Calculate maximum drawdown
            peak = values[0]
            max_drawdown = 0.0
            
            for value in values:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak if peak > 0 else 0
                max_drawdown = max(max_drawdown, drawdown)
            
            return max_drawdown * 100  # Return as percentage
            
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {e}")
            return 0.0

    async def _calculate_sharpe_ratio(self, user_id: str) -> float:
        """Calculate Sharpe ratio for user (simplified)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT daily_pnl FROM user_performance_snapshots 
                WHERE user_id = ? AND timestamp > datetime('now', '-30 days')
                ORDER BY timestamp ASC
            ''', (user_id,))
            
            daily_returns = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if len(daily_returns) < 2:
                return 0.0
            
            # Calculate Sharpe ratio (simplified)
            avg_return = sum(daily_returns) / len(daily_returns)
            
            # Calculate standard deviation
            variance = sum([(r - avg_return) ** 2 for r in daily_returns]) / len(daily_returns)
            std_dev = variance ** 0.5
            
            # Sharpe ratio (assuming risk-free rate of 0)
            sharpe = avg_return / std_dev if std_dev > 0 else 0
            
            return sharpe
            
        except Exception as e:
            logger.error(f"Error calculating Sharpe ratio: {e}")
            return 0.0

    async def _check_performance_alerts(self):
        """Check for performance alerts and notifications"""
        try:
            # This would implement alert logic for:
            # - Large losses
            # - Unusual trading patterns
            # - System performance issues
            # - User milestone achievements
            pass
            
        except Exception as e:
            logger.error(f"Error checking performance alerts: {e}")

# Global instance
real_time_performance_monitor = RealTimePerformanceMonitor()
