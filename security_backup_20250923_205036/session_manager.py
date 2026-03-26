#!/usr/bin/env python3
"""
User Session Management System
Handles user sessions, trade resumption, and state synchronization
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
import hashlib
import hmac
from core.persistence_manager import get_persistence_manager

logger = logging.getLogger(__name__)

@dataclass
class UserSession:
    """Enhanced user session with trade state tracking"""
    user_id: str
    session_id: str
    session_token: str
    created_at: datetime
    last_activity: datetime
    is_online: bool
    device_info: Dict[str, str]
    ip_address: str
    active_trades: List[str]
    trade_notifications: List[Dict[str, Any]]
    ai_learning_state: Dict[str, Any]
    preferences: Dict[str, Any]
    session_data: Dict[str, Any]

@dataclass
class TradeResumption:
    """Information about trades that continued while user was offline"""
    trade_id: str
    symbol: str
    status_changes: List[Dict[str, Any]]
    pnl_changes: List[Dict[str, Any]]
    notifications: List[str]
    time_offline: float  # seconds

class SessionManager:
    """
    Comprehensive session management for persistent trading
    Handles login, logout, session tracking, and trade resumption
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, UserSession] = {}
        self.session_tokens: Dict[str, str] = {}  # token -> user_id
        self.persistence = get_persistence_manager()
        self.session_timeout = 3600  # 1 hour
        self.max_sessions_per_user = 3
        
        # Load existing sessions
        self._load_existing_sessions()
    
    def _load_existing_sessions(self):
        """Load existing sessions from database"""
        try:
            # This would typically load from database
            # For now, we'll start fresh each time
            logger.info("Session manager initialized")
        except Exception as e:
            logger.error(f"Failed to load existing sessions: {e}")
    
    async def create_session(self, user_id: str, device_info: Dict[str, str], ip_address: str) -> Dict[str, Any]:
        """Create a new user session and resume any active trades"""
        try:
            # Generate session identifiers
            session_id = str(uuid.uuid4())
            session_token = self._generate_session_token(user_id, session_id)
            
            # Check for existing sessions and limit them
            await self._cleanup_user_sessions(user_id)
            
            # Load user's persistent data
            user_data = self.persistence.load_user_session(user_id)
            if not user_data:
                user_data = {
                    'active_trades': [],
                    'ai_learning_state': {},
                    'preferences': {},
                    'session_data': {}
                }
            
            # Get user's active trades
            active_trades = self.persistence.load_user_trades(user_id, status='active')
            trade_ids = [trade['trade_id'] for trade in active_trades]
            
            # Calculate trade resumption info
            resumption_info = await self._calculate_trade_resumption(user_id, user_data.get('last_activity'))
            
            # Create session object
            session = UserSession(
                user_id=user_id,
                session_id=session_id,
                session_token=session_token,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                is_online=True,
                device_info=device_info,
                ip_address=ip_address,
                active_trades=trade_ids,
                trade_notifications=[],
                ai_learning_state=user_data.get('ai_learning_state', {}),
                preferences=user_data.get('preferences', {}),
                session_data=user_data.get('session_data', {})
            )
            
            # Store session
            self.active_sessions[session_id] = session
            self.session_tokens[session_token] = user_id
            
            # Update database
            await self._save_session_to_db(session)
            
            # Prepare response
            response = {
                'session_id': session_id,
                'session_token': session_token,
                'user_id': user_id,
                'active_trades': active_trades,
                'trade_resumption': resumption_info,
                'ai_learning_state': session.ai_learning_state,
                'preferences': session.preferences,
                'notifications': await self._get_user_notifications(user_id),
                'session_created': session.created_at.isoformat()
            }
            
            logger.info(f"Session created for user {user_id} with {len(active_trades)} active trades")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create session for user {user_id}: {e}")
            raise
    
    async def _calculate_trade_resumption(self, user_id: str, last_activity: Optional[str]) -> List[TradeResumption]:
        """Calculate what happened to trades while user was offline"""
        resumption_info = []
        
        if not last_activity:
            return resumption_info
        
        try:
            last_activity_dt = datetime.fromisoformat(last_activity)
            offline_duration = (datetime.now() - last_activity_dt).total_seconds()
            
            # Get user's trades
            active_trades = self.persistence.load_user_trades(user_id, status='active')
            completed_trades = self.persistence.load_user_trades(user_id, status='completed')
            
            # Check for trades that completed while offline
            for trade in completed_trades:
                trade_updated = datetime.fromisoformat(trade['last_updated'])
                if trade_updated > last_activity_dt:
                    # This trade completed while user was offline
                    history = self.persistence.get_trade_history(trade['trade_id'], limit=50)
                    
                    # Find changes since last activity
                    status_changes = []
                    pnl_changes = []
                    notifications = []
                    
                    for snapshot in history:
                        if snapshot.timestamp > last_activity_dt:
                            if snapshot.status != 'active':
                                status_changes.append({
                                    'timestamp': snapshot.timestamp.isoformat(),
                                    'status': snapshot.status,
                                    'price': snapshot.price,
                                    'pnl': snapshot.pnl
                                })
                                
                                if snapshot.status == 'completed':
                                    if snapshot.pnl > 0:
                                        notifications.append(f"[CHECK] Trade {trade['symbol']} completed with profit: ${snapshot.pnl:.2f}")
                                    else:
                                        notifications.append(f"[ERROR] Trade {trade['symbol']} completed with loss: ${snapshot.pnl:.2f}")
                    
                    if status_changes or notifications:
                        resumption = TradeResumption(
                            trade_id=trade['trade_id'],
                            symbol=trade['symbol'],
                            status_changes=status_changes,
                            pnl_changes=pnl_changes,
                            notifications=notifications,
                            time_offline=offline_duration
                        )
                        resumption_info.append(resumption)
            
            # Check for significant price changes in active trades
            for trade in active_trades:
                history = self.persistence.get_trade_history(trade['trade_id'], limit=20)
                
                price_changes = []
                for snapshot in history:
                    if snapshot.timestamp > last_activity_dt:
                        price_change_pct = abs(snapshot.price - trade['entry_price']) / trade['entry_price'] * 100
                        if price_change_pct > 5:  # Significant price change
                            price_changes.append({
                                'timestamp': snapshot.timestamp.isoformat(),
                                'price': snapshot.price,
                                'change_pct': price_change_pct,
                                'pnl': snapshot.pnl
                            })
                
                if price_changes:
                    notifications = [f"📈 {trade['symbol']} had significant price movement while you were away"]
                    
                    resumption = TradeResumption(
                        trade_id=trade['trade_id'],
                        symbol=trade['symbol'],
                        status_changes=[],
                        pnl_changes=price_changes,
                        notifications=notifications,
                        time_offline=offline_duration
                    )
                    resumption_info.append(resumption)
            
            return resumption_info
            
        except Exception as e:
            logger.error(f"Failed to calculate trade resumption: {e}")
            return []
    
    async def _get_user_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending notifications for user"""
        try:
            # Get recent AI learning events
            events = self.persistence.get_unprocessed_learning_events(limit=10)
            user_events = [e for e in events if e['user_id'] == user_id]
            
            notifications = []
            for event in user_events:
                if event['event_type'] == 'trade_completion':
                    data = event['event_data']
                    if data['pnl'] > 0:
                        notifications.append({
                            'type': 'success',
                            'message': f"Trade completed with profit: ${data['pnl']:.2f}",
                            'timestamp': event['timestamp']
                        })
                    else:
                        notifications.append({
                            'type': 'warning',
                            'message': f"Trade completed with loss: ${data['pnl']:.2f}",
                            'timestamp': event['timestamp']
                        })
            
            return notifications
            
        except Exception as e:
            logger.error(f"Failed to get user notifications: {e}")
            return []
    
    def _generate_session_token(self, user_id: str, session_id: str) -> str:
        """Generate secure session token"""
        secret_key = "prometheus_trading_secret"  # In production, use environment variable
        message = f"{user_id}:{session_id}:{int(time.time())}"
        signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
        return f"{message}:{signature}"
    
    def validate_session_token(self, token: str) -> Optional[str]:
        """Validate session token and return user_id"""
        try:
            if token in self.session_tokens:
                user_id = self.session_tokens[token]
                
                # Find session and update activity
                for session in self.active_sessions.values():
                    if session.user_id == user_id and session.session_token == token:
                        session.last_activity = datetime.now()
                        return user_id
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to validate session token: {e}")
            return None
    
    async def update_session_activity(self, session_token: str) -> bool:
        """Update session last activity"""
        try:
            user_id = self.validate_session_token(session_token)
            if user_id:
                # Session is automatically updated in validate_session_token
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update session activity: {e}")
            return False
    
    async def end_session(self, session_token: str) -> bool:
        """End user session"""
        try:
            user_id = self.session_tokens.get(session_token)
            if not user_id:
                return False
            
            # Find and remove session
            session_to_remove = None
            for session_id, session in self.active_sessions.items():
                if session.session_token == session_token:
                    session.is_online = False
                    session.last_activity = datetime.now()
                    
                    # Save final session state
                    await self._save_session_to_db(session)
                    
                    session_to_remove = session_id
                    break
            
            if session_to_remove:
                del self.active_sessions[session_to_remove]
                del self.session_tokens[session_token]
                
                logger.info(f"Session ended for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
            return False
    
    async def _cleanup_user_sessions(self, user_id: str):
        """Clean up old sessions for a user"""
        try:
            user_sessions = [s for s in self.active_sessions.values() if s.user_id == user_id]
            
            # Sort by last activity (oldest first)
            user_sessions.sort(key=lambda s: s.last_activity)
            
            # Remove excess sessions
            while len(user_sessions) >= self.max_sessions_per_user:
                old_session = user_sessions.pop(0)
                
                # Remove from active sessions
                if old_session.session_id in self.active_sessions:
                    del self.active_sessions[old_session.session_id]
                
                if old_session.session_token in self.session_tokens:
                    del self.session_tokens[old_session.session_token]
                
                logger.info(f"Cleaned up old session for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup user sessions: {e}")
    
    async def _save_session_to_db(self, session: UserSession):
        """Save session to database"""
        try:
            session_data = {
                'user_id': session.user_id,
                'session_id': session.session_id,
                'last_login': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'is_online': session.is_online,
                'active_trades': session.active_trades,
                'ai_learning_state': session.ai_learning_state,
                'preferences': session.preferences,
                'session_data': {
                    'device_info': session.device_info,
                    'ip_address': session.ip_address,
                    'session_token': session.session_token
                }
            }
            
            self.persistence.save_user_session(session_data)
            
        except Exception as e:
            logger.error(f"Failed to save session to database: {e}")
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            now = datetime.now()
            expired_sessions = []
            
            for session_id, session in self.active_sessions.items():
                if (now - session.last_activity).total_seconds() > self.session_timeout:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                session = self.active_sessions[session_id]
                await self.end_session(session.session_token)
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
    
    def get_session_info(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        try:
            user_id = self.session_tokens.get(session_token)
            if not user_id:
                return None
            
            for session in self.active_sessions.values():
                if session.session_token == session_token:
                    return {
                        'user_id': session.user_id,
                        'session_id': session.session_id,
                        'created_at': session.created_at.isoformat(),
                        'last_activity': session.last_activity.isoformat(),
                        'is_online': session.is_online,
                        'active_trades_count': len(session.active_trades),
                        'device_info': session.device_info
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session info: {e}")
            return None
    
    def get_active_users(self) -> List[Dict[str, Any]]:
        """Get list of currently active users"""
        try:
            active_users = []
            
            for session in self.active_sessions.values():
                if session.is_online:
                    active_users.append({
                        'user_id': session.user_id,
                        'session_id': session.session_id,
                        'last_activity': session.last_activity.isoformat(),
                        'active_trades': len(session.active_trades),
                        'device_info': session.device_info
                    })
            
            return active_users
            
        except Exception as e:
            logger.error(f"Failed to get active users: {e}")
            return []

# Global session manager instance
session_manager = None

def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    global session_manager
    if session_manager is None:
        session_manager = SessionManager()
    return session_manager
