#!/usr/bin/env python3
"""
PROMETHEUS Trading Scheduler
============================
Automatically manages trading sessions based on market hours.
- Starts stock trading at market open
- Runs crypto trading 24/7
- Handles timezone conversion (SAST to ET)
"""

import asyncio
import subprocess
import sys
import os
from datetime import datetime, time as dt_time
from pathlib import Path
import logging

# Setup
sys.path.insert(0, str(Path(__file__).parent))
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import timezone support
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

ET = ZoneInfo('America/New_York')
SAST = ZoneInfo('Africa/Johannesburg')


class PrometheusScheduler:
    """Manages PROMETHEUS trading sessions automatically"""
    
    def __init__(self):
        self.crypto_process = None
        self.stock_process = None
        self.project_dir = Path(__file__).parent
        
        # Market hours in Eastern Time
        self.market_open = dt_time(9, 30)   # 9:30 AM ET = 4:30 PM SAST
        self.market_close = dt_time(16, 0)  # 4:00 PM ET = 11:00 PM SAST
        self.pre_market_start = dt_time(4, 0)  # 4:00 AM ET = 11:00 AM SAST
        
    def get_eastern_time(self) -> datetime:
        """Get current time in US Eastern"""
        return datetime.now(ET)
    
    def get_sast_time(self) -> datetime:
        """Get current time in South Africa"""
        return datetime.now(SAST)
    
    def is_market_open(self) -> bool:
        """Check if US stock market is currently open"""
        now_et = self.get_eastern_time()
        
        # Check if weekend
        if now_et.weekday() >= 5:
            return False
        
        # Check market hours
        current_time = now_et.time()
        return self.market_open <= current_time <= self.market_close
    
    def is_pre_market(self) -> bool:
        """Check if pre-market session"""
        now_et = self.get_eastern_time()
        if now_et.weekday() >= 5:
            return False
        current_time = now_et.time()
        return self.pre_market_start <= current_time < self.market_open
    
    def time_until_market_open(self) -> float:
        """Returns seconds until market opens"""
        now_et = self.get_eastern_time()
        
        # If weekend, calculate to Monday
        days_ahead = 0
        if now_et.weekday() == 5:  # Saturday
            days_ahead = 2
        elif now_et.weekday() == 6:  # Sunday
            days_ahead = 1
        
        # Calculate next market open
        next_open = now_et.replace(
            hour=self.market_open.hour,
            minute=self.market_open.minute,
            second=0,
            microsecond=0
        )
        
        if now_et.time() >= self.market_open or days_ahead > 0:
            from datetime import timedelta
            next_open += timedelta(days=1 + days_ahead)
        
        return (next_open - now_et).total_seconds()
    
    def start_crypto_trader(self):
        """Start 24/7 crypto trading"""
        if self.crypto_process and self.crypto_process.poll() is None:
            logger.info("Crypto trader already running")
            return
        
        logger.info("🔥 Starting PROMETHEUS Crypto Trader (24/7)...")
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['OLLAMA_MODELS'] = 'D:\\Ollama\\models'
        
        self.crypto_process = subprocess.Popen(
            [sys.executable, 'prometheus_crypto_trader.py'],
            cwd=self.project_dir,
            env=env,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        logger.info(f"   PID: {self.crypto_process.pid}")
    
    def start_stock_trader(self):
        """Start stock trading (market hours only)"""
        if self.stock_process and self.stock_process.poll() is None:
            logger.info("Stock trader already running")
            return
        
        logger.info("📈 Starting PROMETHEUS Stock Trader (Market Hours)...")
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['OLLAMA_MODELS'] = 'D:\\Ollama\\models'
        
        self.stock_process = subprocess.Popen(
            [sys.executable, 'launch_prometheus_live.py', '--force'],
            cwd=self.project_dir,
            env=env,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        logger.info(f"   PID: {self.stock_process.pid}")
    
    def stop_stock_trader(self):
        """Stop stock trading after market close"""
        if self.stock_process and self.stock_process.poll() is None:
            logger.info("📉 Stopping stock trader (market closed)...")
            self.stock_process.terminate()
            self.stock_process = None
    
    async def run(self):
        """Main scheduler loop"""
        logger.info("=" * 60)
        logger.info("🚀 PROMETHEUS TRADING SCHEDULER")
        logger.info("=" * 60)
        logger.info(f"Local Time (SAST): {self.get_sast_time().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"US Eastern Time:   {self.get_eastern_time().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("")
        logger.info("Schedule:")
        logger.info("  Crypto: 24/7 (always running)")
        logger.info("  Stocks: 4:30 PM - 11:00 PM SAST (9:30 AM - 4:00 PM ET)")
        logger.info("=" * 60)
        
        # Always start crypto trading
        self.start_crypto_trader()
        
        while True:
            now_et = self.get_eastern_time()
            now_sast = self.get_sast_time()
            
            # Check market status
            if self.is_market_open():
                if not self.stock_process or self.stock_process.poll() is not None:
                    logger.info(f"\n🔔 MARKET OPEN - {now_sast.strftime('%H:%M SAST')}")
                    self.start_stock_trader()
            else:
                if self.stock_process and self.stock_process.poll() is None:
                    logger.info(f"\n🔕 MARKET CLOSED - {now_sast.strftime('%H:%M SAST')}")
                    self.stop_stock_trader()
                
                # Log time until next open
                seconds_to_open = self.time_until_market_open()
                hours = int(seconds_to_open // 3600)
                minutes = int((seconds_to_open % 3600) // 60)
                if hours > 0 or minutes > 0:
                    logger.debug(f"Market opens in: {hours}h {minutes}m")
            
            # Check if crypto trader still running
            if self.crypto_process and self.crypto_process.poll() is not None:
                logger.warning("Crypto trader stopped - restarting...")
                self.start_crypto_trader()
            
            # Sleep for 1 minute between checks
            await asyncio.sleep(60)


async def main():
    scheduler = PrometheusScheduler()
    try:
        await scheduler.run()
    except KeyboardInterrupt:
        logger.info("\n🛑 Scheduler stopped by user")
        if scheduler.crypto_process:
            scheduler.crypto_process.terminate()
        if scheduler.stock_process:
            scheduler.stock_process.terminate()


if __name__ == "__main__":
    asyncio.run(main())
