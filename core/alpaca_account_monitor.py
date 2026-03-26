#!/usr/bin/env python3
"""
🔍 ALPACA ACCOUNT MONITOR
Enhanced account monitoring based on Alpaca implementation guide
Implements periodic account polling and force refresh patterns
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from core.alpaca_trading_service import AlpacaTradingService

logger = logging.getLogger(__name__)

@dataclass
class AccountSnapshot:
    """Account state snapshot for monitoring"""
    timestamp: datetime
    buying_power: float
    portfolio_value: float
    equity: float
    positions_count: int
    open_orders_count: int
    day_trade_count: int
    account_blocked: bool
    trading_blocked: bool

class AlpacaAccountMonitor:
    """
    Enhanced account monitoring service implementing Alpaca guide recommendations:
    - Periodic account polling (every 10-30 seconds)
    - Force refresh after trades
    - Account change detection
    - Health monitoring
    """
    
    def __init__(self, alpaca_service: AlpacaTradingService, poll_interval: int = 15):
        self.alpaca_service = alpaca_service
        self.poll_interval = poll_interval
        self.is_monitoring = False
        self.last_snapshot: Optional[AccountSnapshot] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        self.change_callbacks: List[callable] = []
        
    def add_change_callback(self, callback: callable):
        """Add callback for account changes"""
        self.change_callbacks.append(callback)
        
    async def start_monitoring(self):
        """Start periodic account monitoring"""
        if self.is_monitoring:
            logger.warning("Account monitoring already started")
            return
            
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info(f"Started account monitoring (interval: {self.poll_interval}s)")
        
    async def stop_monitoring(self):
        """Stop account monitoring"""
        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped account monitoring")
        
    async def force_refresh(self, reason: str = "manual"):
        """Force immediate account refresh - call after trades"""
        try:
            logger.info(f"Force refreshing account data (reason: {reason})")
            
            # Wait a moment for order processing if after trade
            if reason == "trade_executed":
                await asyncio.sleep(2)
                
            new_snapshot = await self._capture_account_snapshot()
            if new_snapshot:
                await self._process_snapshot(new_snapshot, force=True)
                logger.info("Force refresh completed")
            else:
                logger.error("Force refresh failed - no snapshot captured")
                
        except Exception as e:
            logger.error(f"Force refresh failed: {e}")
            
    async def get_current_snapshot(self) -> Optional[AccountSnapshot]:
        """Get current account snapshot"""
        return await self._capture_account_snapshot()
        
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Account monitoring loop started")
        
        while self.is_monitoring:
            try:
                snapshot = await self._capture_account_snapshot()
                if snapshot:
                    await self._process_snapshot(snapshot)
                else:
                    logger.warning("Failed to capture account snapshot")
                    
                await asyncio.sleep(self.poll_interval)
                
            except asyncio.CancelledError:
                logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
                
    async def _capture_account_snapshot(self) -> Optional[AccountSnapshot]:
        """Capture current account state"""
        try:
            # Get account info
            account_data = await asyncio.to_thread(self.alpaca_service.get_account_info)
            if not account_data:
                return None
                
            # Get positions (synchronous call)
            positions = self.alpaca_service.get_positions()
            positions_count = len(positions) if positions else 0

            # Get orders (synchronous call)
            orders = self.alpaca_service.get_orders()
            open_orders = [o for o in orders if o.get('status') in ['new', 'partially_filled']] if orders else []
            
            # Create snapshot
            snapshot = AccountSnapshot(
                timestamp=datetime.utcnow(),
                buying_power=float(account_data.get('buying_power', 0)),
                portfolio_value=float(account_data.get('portfolio_value', 0)),
                equity=float(account_data.get('equity', 0)),
                positions_count=positions_count,
                open_orders_count=len(open_orders),
                day_trade_count=int(account_data.get('daytrade_count', 0)),
                account_blocked=account_data.get('account_blocked', False),
                trading_blocked=account_data.get('trading_blocked', False)
            )
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to capture account snapshot: {e}")
            return None
            
    async def _process_snapshot(self, snapshot: AccountSnapshot, force: bool = False):
        """Process account snapshot and detect changes"""
        try:
            changes_detected = False
            change_details = []
            
            if self.last_snapshot and not force:
                # Check for significant changes
                if abs(snapshot.buying_power - self.last_snapshot.buying_power) > 1.0:
                    changes_detected = True
                    change_details.append(f"Buying Power: ${self.last_snapshot.buying_power:.2f} → ${snapshot.buying_power:.2f}")
                    
                if abs(snapshot.portfolio_value - self.last_snapshot.portfolio_value) > 1.0:
                    changes_detected = True
                    change_details.append(f"Portfolio Value: ${self.last_snapshot.portfolio_value:.2f} → ${snapshot.portfolio_value:.2f}")
                    
                if snapshot.positions_count != self.last_snapshot.positions_count:
                    changes_detected = True
                    change_details.append(f"Positions: {self.last_snapshot.positions_count} → {snapshot.positions_count}")
                    
                if snapshot.open_orders_count != self.last_snapshot.open_orders_count:
                    changes_detected = True
                    change_details.append(f"Open Orders: {self.last_snapshot.open_orders_count} → {snapshot.open_orders_count}")
                    
                if snapshot.trading_blocked != self.last_snapshot.trading_blocked:
                    changes_detected = True
                    status = "BLOCKED" if snapshot.trading_blocked else "UNBLOCKED"
                    change_details.append(f"Trading Status: {status}")
                    
            # Log current state
            if changes_detected or force:
                logger.info(f"Account Update - Buying Power: ${snapshot.buying_power:.2f}, "
                          f"Portfolio: ${snapshot.portfolio_value:.2f}, "
                          f"Positions: {snapshot.positions_count}, "
                          f"Orders: {snapshot.open_orders_count}")
                          
                if changes_detected:
                    logger.info(f"Changes detected: {'; '.join(change_details)}")
                    
                # Notify callbacks
                for callback in self.change_callbacks:
                    try:
                        await callback(snapshot, change_details if changes_detected else [])
                    except Exception as e:
                        logger.error(f"Error in change callback: {e}")
                        
            self.last_snapshot = snapshot
            
        except Exception as e:
            logger.error(f"Error processing snapshot: {e}")
            
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring service status"""
        return {
            "is_monitoring": self.is_monitoring,
            "poll_interval": self.poll_interval,
            "last_update": self.last_snapshot.timestamp.isoformat() if self.last_snapshot else None,
            "callbacks_registered": len(self.change_callbacks),
            "current_snapshot": {
                "buying_power": self.last_snapshot.buying_power if self.last_snapshot else 0,
                "portfolio_value": self.last_snapshot.portfolio_value if self.last_snapshot else 0,
                "positions_count": self.last_snapshot.positions_count if self.last_snapshot else 0,
                "open_orders_count": self.last_snapshot.open_orders_count if self.last_snapshot else 0,
                "trading_blocked": self.last_snapshot.trading_blocked if self.last_snapshot else False
            } if self.last_snapshot else None
        }
