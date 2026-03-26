"""
Hybrid Broker Router - Intelligent broker selection for 24/7 trading
Routes trades to optimal broker based on asset type, time, and broker health
"""

import json
import logging
from datetime import datetime, time
from typing import Dict, Optional, Tuple
from pathlib import Path
import pytz

logger = logging.getLogger(__name__)


class HybridBrokerRouter:
    """
    Intelligent broker routing system for dual-broker 24/7 trading
    
    Features:
    - Time-based routing (market hours, extended hours, after hours)
    - Asset-based routing (stocks vs crypto)
    - Health-based failover
    - Duplicate position prevention
    - Cross-broker position tracking
    """
    
    def __init__(self, config_path: str = "config/hybrid_broker_strategy.json"):
        """Initialize the hybrid broker router"""
        self.config = self._load_config(config_path)
        self.broker_health = {
            'ib': {'healthy': True, 'consecutive_failures': 0, 'last_check': None},
            'alpaca': {'healthy': True, 'consecutive_failures': 0, 'last_check': None}
        }
        self.broker_positions = {
            'ib': {},      # {symbol: quantity}
            'alpaca': {}   # {symbol: quantity}
        }
        self.failover_active = {
            'ib': False,
            'alpaca': False
        }
        
        logger.info("🔀 Hybrid Broker Router initialized")
        logger.info(f"   Strategy: {self.config['strategy_name']}")
        logger.info(f"   Failover: {'Enabled' if self.config['failover']['enabled'] else 'Disabled'}")
        logger.info(f"   24/7 Crypto: {'Enabled' if self.config['crypto_config']['trade_24_7'] else 'Disabled'}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            # Return default config
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration if file not found"""
        return {
            "strategy_name": "Hybrid Dual-Broker 24/7 Trading",
            "broker_routing": {
                "stocks": {
                    "market_hours": {"primary": "ib", "backup": "alpaca"},
                    "extended_hours": {"primary": "alpaca", "backup": "ib"},
                    "after_hours": {"primary": "alpaca", "backup": None}
                },
                "crypto": {
                    "24_7": {"primary": "alpaca", "backup": "ib"}
                }
            },
            "market_hours": {
                "regular": {"start": "09:30", "end": "16:00", "timezone": "America/New_York"},
                "extended": {
                    "pre_market_start": "04:00",
                    "pre_market_end": "09:30",
                    "after_market_start": "16:00",
                    "after_market_end": "20:00",
                    "timezone": "America/New_York"
                }
            },
            "failover": {"enabled": True, "max_consecutive_failures": 3},
            "crypto_config": {"enabled": True, "trade_24_7": True, "preferred_broker": "alpaca"},
            "stock_config": {"enabled": True, "trade_extended_hours": True}
        }
    
    def get_market_session(self) -> str:
        """
        Determine current market session
        Returns: 'market_hours', 'extended_hours', 'after_hours', or 'closed'
        """
        try:
            tz = pytz.timezone(self.config['market_hours']['regular']['timezone'])
            now = datetime.now(tz)
            current_time = now.time()
            
            # Check if weekend
            if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
                return 'closed'
            
            # Parse times
            market_start = time.fromisoformat(self.config['market_hours']['regular']['start'])
            market_end = time.fromisoformat(self.config['market_hours']['regular']['end'])
            pre_start = time.fromisoformat(self.config['market_hours']['extended']['pre_market_start'])
            after_end = time.fromisoformat(self.config['market_hours']['extended']['after_market_end'])
            
            # Determine session
            if market_start <= current_time < market_end:
                return 'market_hours'
            elif pre_start <= current_time < market_start:
                return 'extended_hours'  # Pre-market
            elif market_end <= current_time < after_end:
                return 'extended_hours'  # After-market
            else:
                return 'after_hours'  # Overnight
                
        except Exception as e:
            logger.error(f"Error determining market session: {e}")
            return 'market_hours'  # Default to market hours
    
    def is_crypto(self, symbol: str) -> bool:
        """Check if symbol is cryptocurrency"""
        return '/' in symbol or symbol.endswith('USD') and symbol[:-3] in ['BTC', 'ETH', 'SOL', 'AVAX', 'DOGE']
    
    def select_broker(self, symbol: str, action: str = 'BUY') -> Tuple[str, str]:
        """
        Select optimal broker for trade
        
        Args:
            symbol: Trading symbol
            action: 'BUY' or 'SELL'
        
        Returns:
            Tuple of (broker_name, reason)
        """
        is_crypto = self.is_crypto(symbol)
        
        # CRYPTO ROUTING (24/7)
        if is_crypto:
            if not self.config['crypto_config']['enabled']:
                return None, "Crypto trading disabled"
            
            routing = self.config['broker_routing']['crypto']['24_7']
            primary = routing['primary']
            backup = routing.get('backup')
            
            # Check if primary is healthy
            if self.broker_health[primary]['healthy'] and not self.failover_active[primary]:
                return primary, f"Crypto 24/7 on {primary.upper()} (primary)"
            
            # Failover to backup
            if backup and self.broker_health[backup]['healthy']:
                logger.warning(f"[WARNING]️ Crypto failover: {primary.upper()} → {backup.upper()}")
                self.failover_active[primary] = True
                return backup, f"Crypto 24/7 on {backup.upper()} (failover)"
            
            return None, f"No healthy broker available for crypto"
        
        # STOCK ROUTING (time-based)
        else:
            if not self.config['stock_config']['enabled']:
                return None, "Stock trading disabled"
            
            session = self.get_market_session()
            
            # Market closed (weekends/overnight)
            if session == 'closed':
                return None, "Market closed (weekend/overnight)"
            
            # After hours (overnight 8 PM - 4 AM)
            if session == 'after_hours':
                if not self.config['stock_config'].get('trade_extended_hours', False):
                    return None, "After-hours trading disabled"
                routing = self.config['broker_routing']['stocks']['after_hours']
            
            # Extended hours (pre-market 4-9:30 AM, after-market 4-8 PM)
            elif session == 'extended_hours':
                if not self.config['stock_config'].get('trade_extended_hours', False):
                    return None, "Extended hours trading disabled"
                routing = self.config['broker_routing']['stocks']['extended_hours']
            
            # Regular market hours (9:30 AM - 4 PM)
            else:
                routing = self.config['broker_routing']['stocks']['market_hours']
            
            primary = routing['primary']
            backup = routing.get('backup')
            
            # Check if primary is healthy
            if self.broker_health[primary]['healthy'] and not self.failover_active[primary]:
                return primary, f"Stock {session} on {primary.upper()} (primary)"
            
            # Failover to backup
            if backup and self.broker_health[backup]['healthy']:
                logger.warning(f"[WARNING]️ Stock failover: {primary.upper()} → {backup.upper()}")
                self.failover_active[primary] = True
                return backup, f"Stock {session} on {backup.upper()} (failover)"
            
            return None, f"No healthy broker available for stocks during {session}"
    
    def check_duplicate_position(self, symbol: str, broker: str) -> bool:
        """
        Check if position already exists on another broker
        
        Returns:
            True if duplicate would be created, False otherwise
        """
        if not self.config['position_management']['prevent_duplicates']:
            return False
        
        # Check all other brokers
        for other_broker, positions in self.broker_positions.items():
            if other_broker != broker and symbol in positions:
                logger.warning(f"[WARNING]️ Duplicate position prevented: {symbol} already on {other_broker.upper()}")
                return True
        
        return False
    
    def update_position(self, broker: str, symbol: str, quantity: float):
        """Update position tracking"""
        if quantity == 0:
            # Remove position
            if symbol in self.broker_positions[broker]:
                del self.broker_positions[broker][symbol]
        else:
            # Add/update position
            self.broker_positions[broker][symbol] = quantity
    
    def mark_broker_failure(self, broker: str):
        """Mark broker as failed (for health tracking)"""
        self.broker_health[broker]['consecutive_failures'] += 1
        self.broker_health[broker]['last_check'] = datetime.now()
        
        max_failures = self.config['failover']['max_consecutive_failures']
        if self.broker_health[broker]['consecutive_failures'] >= max_failures:
            self.broker_health[broker]['healthy'] = False
            logger.error(f"[ERROR] Broker {broker.upper()} marked as UNHEALTHY after {max_failures} failures")
    
    def mark_broker_success(self, broker: str):
        """Mark broker as successful (for health tracking)"""
        self.broker_health[broker]['consecutive_failures'] = 0
        self.broker_health[broker]['healthy'] = True
        self.broker_health[broker]['last_check'] = datetime.now()
        
        # Clear failover if broker recovered
        if self.failover_active[broker]:
            self.failover_active[broker] = False
            logger.info(f"[CHECK] Broker {broker.upper()} recovered - failover cleared")
    
    def get_status(self) -> Dict:
        """Get current router status"""
        session = self.get_market_session()
        
        return {
            'market_session': session,
            'broker_health': self.broker_health,
            'failover_active': self.failover_active,
            'positions': {
                'ib': len(self.broker_positions['ib']),
                'alpaca': len(self.broker_positions['alpaca'])
            },
            'crypto_enabled': self.config['crypto_config']['enabled'],
            'stock_enabled': self.config['stock_config']['enabled']
        }
    
    def get_routing_summary(self) -> str:
        """Get human-readable routing summary"""
        session = self.get_market_session()
        status = self.get_status()
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║           HYBRID BROKER ROUTING STATUS                       ║
╚══════════════════════════════════════════════════════════════╝

📊 Market Session: {session.upper().replace('_', ' ')}

🏦 Broker Health:
   IB.......... {'[CHECK] HEALTHY' if status['broker_health']['ib']['healthy'] else '[ERROR] UNHEALTHY'}
   Alpaca...... {'[CHECK] HEALTHY' if status['broker_health']['alpaca']['healthy'] else '[ERROR] UNHEALTHY'}

📈 Current Routing:
   Stocks...... {self._get_stock_routing(session)}
   Crypto...... Alpaca (24/7)

📊 Open Positions:
   IB.......... {status['positions']['ib']} positions
   Alpaca...... {status['positions']['alpaca']} positions

[LIGHTNING] Failover Status:
   IB.......... {'🔄 ACTIVE' if status['failover_active']['ib'] else '[CHECK] Normal'}
   Alpaca...... {'🔄 ACTIVE' if status['failover_active']['alpaca'] else '[CHECK] Normal'}
"""
        return summary
    
    def _get_stock_routing(self, session: str) -> str:
        """Get current stock routing description"""
        if session == 'closed':
            return "Market Closed"
        elif session == 'after_hours':
            return "Alpaca (after-hours)" if self.config['stock_config'].get('trade_extended_hours') else "Disabled"
        elif session == 'extended_hours':
            return "Alpaca (extended)"
        else:
            return "IB (market hours)"

