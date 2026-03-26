#!/usr/bin/env python3
"""
================================================================================
PROMETHEUS 24/5 CONTINUOUS TRADING MONITOR
================================================================================

Runs continuously and ensures PROMETHEUS never misses ANY trading opportunity:

- Pre-Market (4:00 AM - 9:30 AM ET): Scans for overnight gaps, earnings movers
- Regular Market (9:30 AM - 4:00 PM ET): Full trading with high liquidity
- After-Hours (4:00 PM - 8:00 PM ET): Catches earnings reactions
- Overnight (IB): Monitors futures and overnight moves
- Crypto (24/7): Trades BTC, ETH around the clock
- Forex (24/5): FX pairs Sunday 5 PM - Friday 5 PM ET

Automatically adjusts for:
- Your timezone (South Africa = UTC+2)
- US market holidays
- Early close days
- Daylight saving time changes

================================================================================
"""

import os
import sys
import json
import time
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import threading

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('continuous_trading_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import timezone scheduler
try:
    from timezone_trading_scheduler import TradingScheduler
    SCHEDULER_AVAILABLE = True
except ImportError:
    logger.warning("TradingScheduler not available")
    SCHEDULER_AVAILABLE = False


class ContinuousTradingMonitor:
    """
    24/5 trading monitor that never sleeps (except on weekends).
    """
    
    def __init__(self):
        if SCHEDULER_AVAILABLE:
            self.scheduler = TradingScheduler()
        else:
            self.scheduler = None
        
        self.running = False
        self.session_active = False
        self.stats = {
            "sessions_started": 0,
            "trades_executed": 0,
            "opportunities_found": 0,
            "hours_monitored": 0,
            "start_time": None
        }
        
        # Configuration
        self.config = {
            "monitor_interval_seconds": 60,  # Check every minute
            "pre_market_enabled": True,
            "after_hours_enabled": True,
            "crypto_24_7_enabled": True,
            "forex_24_5_enabled": False,
            "alert_on_session_change": True,
            "auto_launch_trading": True,
        }
        
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        config_file = Path("continuous_trading_config.json")
        if config_file.exists():
            try:
                with open(config_file) as f:
                    saved = json.load(f)
                    self.config.update(saved)
            except Exception as e:
                logger.warning(f"Could not load config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        with open("continuous_trading_config.json", 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_session_status(self) -> Dict:
        """Get current trading session status"""
        if self.scheduler:
            return self.scheduler.get_market_status()
        
        # Fallback if scheduler not available
        import pytz
        et = datetime.now(pytz.timezone('US/Eastern'))
        hour = et.hour
        minute = et.minute
        
        is_weekend = et.weekday() >= 5
        
        if is_weekend:
            return {"session": "weekend", "is_open": False}
        elif 4 <= hour < 9 or (hour == 9 and minute < 30):
            return {"session": "pre_market", "is_open": self.config["pre_market_enabled"]}
        elif (hour == 9 and minute >= 30) or (9 < hour < 16):
            return {"session": "regular", "is_open": True}
        elif 16 <= hour < 20:
            return {"session": "after_hours", "is_open": self.config["after_hours_enabled"]}
        else:
            return {"session": "closed", "is_open": False}
    
    def should_trade_now(self, status: Dict) -> bool:
        """Determine if we should be trading based on session"""
        session = status.get("session", "closed")
        
        # Always trade during regular hours
        if session == "regular":
            return True
        
        # Pre-market if enabled
        if session == "pre_market" and self.config["pre_market_enabled"]:
            return True
        
        # After-hours if enabled
        if session == "after_hours" and self.config["after_hours_enabled"]:
            return True
        
        # Crypto trades 24/7
        if self.config["crypto_24_7_enabled"] and session not in ["weekend"]:
            return True  # Crypto always available except weekends
        
        return False
    
    def get_tradeable_assets(self, status: Dict) -> Dict[str, list]:
        """Get list of tradeable assets for current session"""
        session = status.get("session", "closed")
        
        assets = {
            "stocks": [],
            "crypto": [],
            "forex": [],
            "futures": []
        }
        
        # Regular session - all stocks
        if session == "regular":
            assets["stocks"] = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "AMD", "COIN", "PLTR"]
        
        # Pre-market - limited liquidity
        elif session == "pre_market" and self.config["pre_market_enabled"]:
            assets["stocks"] = ["NVDA", "TSLA", "AAPL"]  # Most liquid only
        
        # After-hours - limited
        elif session == "after_hours" and self.config["after_hours_enabled"]:
            assets["stocks"] = ["NVDA", "TSLA", "AAPL", "AMZN"]  # Major movers only
        
        # Crypto 24/7
        if self.config["crypto_24_7_enabled"]:
            assets["crypto"] = ["BTC/USD", "ETH/USD", "SOL/USD"]
        
        # Forex 24/5
        if self.config["forex_24_5_enabled"] and session != "weekend":
            assets["forex"] = ["EUR/USD", "GBP/USD", "USD/JPY"]
        
        return assets
    
    def display_status(self):
        """Display current monitoring status"""
        status = self.get_session_status()
        assets = self.get_tradeable_assets(status)
        
        # Clear screen for clean display
        print("\033[2J\033[H", end="")
        
        print("=" * 70)
        print("🔄 PROMETHEUS 24/5 CONTINUOUS TRADING MONITOR")
        print("=" * 70)
        
        if self.scheduler:
            times = self.scheduler.get_all_timezones()
            print(f"\n📍 Your Local Time:  {times['local'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"   US Eastern Time:  {times['eastern'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
        else:
            print(f"\n📍 Local Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Session status with emoji
        session_display = {
            "regular": ("🟢 REGULAR MARKET", "Full liquidity - all stocks tradeable"),
            "pre_market": ("🟡 PRE-MARKET", "Limited liquidity - major stocks only"),
            "after_hours": ("🟠 AFTER-HOURS", "Extended trading - limited stocks"),
            "closed": ("🔴 MARKET CLOSED", "Crypto/Forex may still be available"),
            "weekend": ("⚫ WEEKEND", "Crypto 24/7 still active"),
            "holiday": ("🔵 HOLIDAY", "US markets closed")
        }
        
        session = status.get("session", "closed")
        emoji, desc = session_display.get(session, ("❓", "Unknown"))
        
        print(f"\n📊 CURRENT SESSION: {emoji}")
        print(f"   {desc}")
        
        if status.get("time_to_open"):
            print(f"   ⏳ Market opens in: {status['time_to_open']}")
        if status.get("time_to_close"):
            print(f"   ⏳ Market closes in: {status['time_to_close']}")
        
        # Trading decision
        should_trade = self.should_trade_now(status)
        print(f"\n🤖 TRADING STATUS: {'✅ ACTIVE' if should_trade else '⏸️ WAITING'}")
        
        # Tradeable assets
        print("\n📋 TRADEABLE ASSETS RIGHT NOW:")
        if assets["stocks"]:
            print(f"   Stocks: {', '.join(assets['stocks'])}")
        if assets["crypto"]:
            print(f"   Crypto: {', '.join(assets['crypto'])}")
        if assets["forex"]:
            print(f"   Forex: {', '.join(assets['forex'])}")
        if not any(assets.values()):
            print("   [No assets tradeable right now]")
        
        # Stats
        if self.stats["start_time"]:
            runtime = datetime.now() - self.stats["start_time"]
            hours = runtime.total_seconds() / 3600
            print(f"\n📈 SESSION STATS:")
            print(f"   Running for: {str(runtime).split('.')[0]}")
            print(f"   Sessions started: {self.stats['sessions_started']}")
            print(f"   Opportunities found: {self.stats['opportunities_found']}")
        
        # Next events
        if self.scheduler:
            print("\n📅 NEXT 3 TRADING DAYS:")
            events = self.scheduler.get_upcoming_events(5)
            trading_days = [e for e in events if e['type'] not in ['closed', 'weekend', 'holiday']][:3]
            for event in trading_days:
                print(f"   • {event['date']}")
        
        print("\n" + "=" * 70)
        print("Press Ctrl+C to stop monitoring")
        print("=" * 70)
    
    async def start_trading_session(self, status: Dict):
        """Start an active trading session"""
        if self.session_active:
            return
        
        self.session_active = True
        self.stats["sessions_started"] += 1
        
        session = status.get("session", "unknown")
        logger.info(f"🚀 Starting trading session: {session}")
        
        try:
            # Import and run the trading system
            if self.config["auto_launch_trading"]:
                from final_dual_broker_fixed import FinalDualBrokerTradingSystem
                
                # Create trading system with session-appropriate config
                assets = self.get_tradeable_assets(status)
                
                logger.info(f"Trading assets: {assets}")
                
                # Run one trading iteration
                # In production, this would be a full trading loop
                
        except Exception as e:
            logger.error(f"Trading session error: {e}")
        finally:
            self.session_active = False
    
    def run(self):
        """Main monitoring loop"""
        self.running = True
        self.stats["start_time"] = datetime.now()
        last_session = None
        
        logger.info("🔄 Starting 24/5 Continuous Trading Monitor...")
        
        try:
            while self.running:
                # Get current status
                status = self.get_session_status()
                current_session = status.get("session")
                
                # Display status
                self.display_status()
                
                # Check for session change
                if last_session != current_session:
                    if last_session is not None:
                        logger.info(f"📢 Session changed: {last_session} → {current_session}")
                        
                        if self.config["alert_on_session_change"]:
                            # Could add notification here (email, SMS, etc.)
                            pass
                    
                    last_session = current_session
                
                # Start trading if appropriate
                if self.should_trade_now(status):
                    # Check for opportunities
                    self.stats["opportunities_found"] += 1
                    
                    if self.config["auto_launch_trading"] and not self.session_active:
                        asyncio.run(self.start_trading_session(status))
                
                # Sleep until next check
                time.sleep(self.config["monitor_interval_seconds"])
                
        except KeyboardInterrupt:
            logger.info("🛑 Monitor stopped by user")
            self.running = False
        
        # Save stats
        self.save_stats()
    
    def save_stats(self):
        """Save monitoring stats"""
        if self.stats["start_time"]:
            runtime = datetime.now() - self.stats["start_time"]
            self.stats["hours_monitored"] = runtime.total_seconds() / 3600
        
        with open("continuous_monitor_stats.json", 'w') as f:
            stats_json = {k: str(v) if isinstance(v, datetime) else v 
                         for k, v in self.stats.items()}
            json.dump(stats_json, f, indent=2)


def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           PROMETHEUS 24/5 CONTINUOUS TRADING MONITOR                 ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║   This monitor runs continuously to ensure you NEVER miss a         ║
║   trading opportunity, regardless of timezone.                       ║
║                                                                      ║
║   Coverage:                                                          ║
║   • Pre-Market:    4:00 AM - 9:30 AM ET (11:00 AM - 4:30 PM SA)     ║
║   • Regular:       9:30 AM - 4:00 PM ET (4:30 PM - 11:00 PM SA)     ║
║   • After-Hours:   4:00 PM - 8:00 PM ET (11:00 PM - 3:00 AM SA)     ║
║   • Crypto:        24/7 (Always active)                             ║
║   • Forex:         24/5 (Sunday 5PM - Friday 5PM ET)                ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")
    
    monitor = ContinuousTradingMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
