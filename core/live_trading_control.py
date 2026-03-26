#!/usr/bin/env python3
"""
🎯 PROMETHEUS LIVE TRADING CONTROL SYSTEM
Admin-controlled live trading with real money - strict safety controls
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import json
import sqlite3
import os
from decimal import Decimal

logger = logging.getLogger(__name__)

class TradingMode(Enum):
    """Trading modes"""
    PAPER_ONLY = "paper_only"
    LIVE_AUTHORIZED = "live_authorized"
    EMERGENCY_STOP = "emergency_stop"

class AdminAction(Enum):
    """Admin actions for live trading"""
    AUTHORIZE_LIVE = "authorize_live"
    FORCE_STOP = "force_stop"
    EMERGENCY_HALT = "emergency_halt"
    RESUME_TRADING = "resume_trading"

@dataclass
class LiveTradingSession:
    """Live trading session with real money"""
    session_id: str
    admin_id: str
    authorized_capital: Decimal
    max_daily_loss: Decimal
    max_position_size: Decimal
    authorized_symbols: List[str]
    start_time: datetime
    end_time: Optional[datetime]
    status: TradingMode
    current_pnl: Decimal = Decimal('0')
    trades_executed: int = 0
    last_heartbeat: Optional[datetime] = None

@dataclass
class AdminControl:
    """Admin control record"""
    control_id: str
    admin_id: str
    action: AdminAction
    session_id: Optional[str]
    reason: str
    timestamp: datetime
    parameters: Dict[str, Any]

class LiveTradingControlSystem:
    """
    🎯 LIVE TRADING CONTROL SYSTEM
    Strict admin controls for live trading with real money
    """
    
    def __init__(self, db_path: str = "live_trading_control.db"):
        self.db_path = db_path
        self.active_sessions: Dict[str, LiveTradingSession] = {}
        self.authorized_admins = set()
        self.emergency_stop_active = False
        self.max_concurrent_sessions = 1  # Only one live session at a time
        
        # Initialize database
        self._init_database()
        
        # Load authorized admins from environment
        self._load_authorized_admins()
        
        logger.info("🎯 Live Trading Control System initialized")
    
    def _init_database(self):
        """Initialize control database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Live trading sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS live_sessions (
                session_id TEXT PRIMARY KEY,
                admin_id TEXT NOT NULL,
                authorized_capital REAL NOT NULL,
                max_daily_loss REAL NOT NULL,
                max_position_size REAL NOT NULL,
                authorized_symbols TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT NOT NULL,
                current_pnl REAL DEFAULT 0,
                trades_executed INTEGER DEFAULT 0,
                last_heartbeat TEXT
            )
        ''')
        
        # Admin controls table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_controls (
                control_id TEXT PRIMARY KEY,
                admin_id TEXT NOT NULL,
                action TEXT NOT NULL,
                session_id TEXT,
                reason TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                parameters TEXT NOT NULL
            )
        ''')
        
        # Emergency stops table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emergency_stops (
                stop_id TEXT PRIMARY KEY,
                admin_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_authorized_admins(self):
        """Load authorized admin IDs from environment"""
        admin_list = os.getenv('AUTHORIZED_LIVE_TRADING_ADMINS', '')
        if admin_list:
            self.authorized_admins = set(admin_list.split(','))
            logger.info(f"[CHECK] Loaded {len(self.authorized_admins)} authorized admins")
        else:
            logger.warning("[WARNING]️ No authorized admins configured - live trading disabled")
    
    async def authorize_live_trading(self, admin_id: str, capital: Decimal, 
                                   max_daily_loss: Decimal, max_position_size: Decimal,
                                   authorized_symbols: List[str], reason: str) -> Dict[str, Any]:
        """Authorize live trading session with real money"""
        
        # Verify admin authorization
        if admin_id not in self.authorized_admins:
            return {
                "success": False,
                "error": f"Admin {admin_id} not authorized for live trading",
                "requires": "AUTHORIZED_LIVE_TRADING_ADMINS environment variable"
            }
        
        # Check for emergency stop
        if self.emergency_stop_active:
            return {
                "success": False,
                "error": "Emergency stop active - live trading disabled",
                "action_required": "Clear emergency stop first"
            }
        
        # Check concurrent sessions
        active_count = len([s for s in self.active_sessions.values() 
                           if s.status == TradingMode.LIVE_AUTHORIZED])
        if active_count >= self.max_concurrent_sessions:
            return {
                "success": False,
                "error": f"Maximum {self.max_concurrent_sessions} live sessions allowed",
                "active_sessions": active_count
            }
        
        # Validate parameters
        if capital <= 0 or max_daily_loss <= 0 or max_position_size <= 0:
            return {
                "success": False,
                "error": "Invalid trading parameters - all values must be positive"
            }
        
        if max_daily_loss > capital * Decimal('0.1'):  # Max 10% daily loss
            return {
                "success": False,
                "error": "Daily loss limit cannot exceed 10% of capital"
            }
        
        # Create live trading session
        session_id = f"live_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = LiveTradingSession(
            session_id=session_id,
            admin_id=admin_id,
            authorized_capital=capital,
            max_daily_loss=max_daily_loss,
            max_position_size=max_position_size,
            authorized_symbols=authorized_symbols,
            start_time=datetime.now(),
            end_time=None,
            status=TradingMode.LIVE_AUTHORIZED,
            last_heartbeat=datetime.now()
        )
        
        # Store session
        self.active_sessions[session_id] = session
        await self._save_session(session)
        
        # Log admin control
        await self._log_admin_action(
            admin_id=admin_id,
            action=AdminAction.AUTHORIZE_LIVE,
            session_id=session_id,
            reason=reason,
            parameters={
                "capital": float(capital),
                "max_daily_loss": float(max_daily_loss),
                "max_position_size": float(max_position_size),
                "symbols": authorized_symbols
            }
        )
        
        logger.warning(f"🚨 LIVE TRADING AUTHORIZED by {admin_id}: ${capital} capital")
        
        return {
            "success": True,
            "session_id": session_id,
            "message": f"Live trading authorized with ${capital} capital",
            "parameters": {
                "capital": float(capital),
                "max_daily_loss": float(max_daily_loss),
                "max_position_size": float(max_position_size),
                "authorized_symbols": authorized_symbols
            },
            "warning": "REAL MONEY TRADING ACTIVE - Monitor closely"
        }
    
    async def force_stop_live_trading(self, admin_id: str, session_id: str, 
                                    reason: str) -> Dict[str, Any]:
        """Force stop a live trading session"""
        
        if admin_id not in self.authorized_admins:
            return {"success": False, "error": "Admin not authorized"}
        
        if session_id not in self.active_sessions:
            return {"success": False, "error": "Session not found"}
        
        session = self.active_sessions[session_id]
        session.status = TradingMode.EMERGENCY_STOP
        session.end_time = datetime.now()
        
        await self._save_session(session)
        
        # Log admin action
        await self._log_admin_action(
            admin_id=admin_id,
            action=AdminAction.FORCE_STOP,
            session_id=session_id,
            reason=reason,
            parameters={"final_pnl": float(session.current_pnl)}
        )
        
        logger.warning(f"🛑 LIVE TRADING FORCE STOPPED by {admin_id}: {reason}")
        
        return {
            "success": True,
            "message": f"Live trading session {session_id} force stopped",
            "reason": reason,
            "final_pnl": float(session.current_pnl)
        }
    
    async def emergency_halt_all(self, admin_id: str, reason: str) -> Dict[str, Any]:
        """Emergency halt all live trading"""
        
        if admin_id not in self.authorized_admins:
            return {"success": False, "error": "Admin not authorized"}
        
        self.emergency_stop_active = True
        stopped_sessions = []
        
        # Stop all active sessions
        for session_id, session in self.active_sessions.items():
            if session.status == TradingMode.LIVE_AUTHORIZED:
                session.status = TradingMode.EMERGENCY_STOP
                session.end_time = datetime.now()
                await self._save_session(session)
                stopped_sessions.append(session_id)
        
        # Log emergency stop
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO emergency_stops (stop_id, admin_id, reason, timestamp, active)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            f"emergency_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            admin_id, reason, datetime.now().isoformat(), True
        ))
        conn.commit()
        conn.close()
        
        logger.critical(f"🚨 EMERGENCY HALT ACTIVATED by {admin_id}: {reason}")
        
        return {
            "success": True,
            "message": "EMERGENCY HALT ACTIVATED - All live trading stopped",
            "reason": reason,
            "stopped_sessions": stopped_sessions,
            "warning": "Manual intervention required to resume"
        }
    
    async def _save_session(self, session: LiveTradingSession):
        """Save session to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO live_sessions 
            (session_id, admin_id, authorized_capital, max_daily_loss, max_position_size,
             authorized_symbols, start_time, end_time, status, current_pnl, trades_executed, last_heartbeat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session.session_id, session.admin_id, float(session.authorized_capital),
            float(session.max_daily_loss), float(session.max_position_size),
            json.dumps(session.authorized_symbols), session.start_time.isoformat(),
            session.end_time.isoformat() if session.end_time else None,
            session.status.value, float(session.current_pnl), session.trades_executed,
            session.last_heartbeat.isoformat() if session.last_heartbeat else None
        ))
        conn.commit()
        conn.close()
    
    async def _log_admin_action(self, admin_id: str, action: AdminAction, 
                              session_id: Optional[str], reason: str, 
                              parameters: Dict[str, Any]):
        """Log admin action"""
        control_id = f"ctrl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO admin_controls (control_id, admin_id, action, session_id, reason, timestamp, parameters)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            control_id, admin_id, action.value, session_id, reason,
            datetime.now().isoformat(), json.dumps(parameters)
        ))
        conn.commit()
        conn.close()

# Global instance
live_trading_control = LiveTradingControlSystem()
