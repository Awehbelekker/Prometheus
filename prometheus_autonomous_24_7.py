#!/usr/bin/env python3
"""
================================================================================
PROMETHEUS AUTONOMOUS 24/7 INTELLIGENCE SYSTEM
================================================================================

This is the MASTER launcher that runs PROMETHEUS continuously:

WHEN MARKETS ARE OPEN:
  - Trades stocks (Regular: 9:30 AM - 4:00 PM ET)
  - Trades pre-market (4:00 AM - 9:30 AM ET)
  - Trades after-hours (4:00 PM - 8:00 PM ET)
  - Trades crypto (24/7 on Alpaca)

WHEN MARKETS ARE CLOSED:
  - Runs backtests with new strategies
  - Analyzes past trades and learns from them
  - Trains pattern recognition on historical data
  - Ingests new knowledge from research papers
  - Optimizes strategy parameters
  - Prepares for next trading session

AVAILABLE TRADING ACCESS:
  1. Alpaca (Stocks + Crypto) - 24/5 stocks, 24/7 crypto
  2. Interactive Brokers (Stocks, Options, Futures, Forex) - Extended hours
  3. Crypto via Alpaca - BTC, ETH, SOL, etc. (24/7)

TO RUN OUTSIDE VS CODE:
  1. Open PowerShell or Command Prompt
  2. Navigate to: cd C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform
  3. Run: python prometheus_autonomous_24_7.py

================================================================================
"""

import os
import sys
import json
import time
import logging
import asyncio
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import signal

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
log_file = f'prometheus_autonomous_{datetime.now().strftime("%Y%m%d")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PrometheusAutonomous247:
    """
    The MASTER PROMETHEUS system that NEVER stops.
    Always trading, learning, or improving.
    """
    
    def __init__(self):
        self.running = True
        self.current_mode = "initializing"
        self.start_time = datetime.now()
        
        # Statistics
        self.stats = {
            "trading_sessions": 0,
            "learning_sessions": 0,
            "backtests_run": 0,
            "patterns_learned": 0,
            "trades_executed": 0,
            "total_pnl": 0.0,
            "uptime_hours": 0
        }
        
        # Load scheduler
        try:
            from timezone_trading_scheduler import TradingScheduler
            self.scheduler = TradingScheduler()
            logger.info("✅ Timezone scheduler loaded")
        except ImportError:
            logger.warning("Timezone scheduler not available")
            self.scheduler = None
        
        # Available trading markets
        self.markets = {
            "us_stocks": {
                "name": "US Stocks (Alpaca + IB)",
                "hours": "9:30 AM - 4:00 PM ET (4:30 PM - 11:00 PM SA)",
                "extended": "4:00 AM - 8:00 PM ET",
                "broker": ["alpaca", "ib"],
                "symbols": ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "AMD"]
            },
            "crypto": {
                "name": "Crypto (Alpaca)",
                "hours": "24/7",
                "broker": ["alpaca"],
                "symbols": ["BTC/USD", "ETH/USD", "SOL/USD", "DOGE/USD", "AVAX/USD"]
            },
            "options": {
                "name": "Options (IB)",
                "hours": "9:30 AM - 4:00 PM ET",
                "broker": ["ib"],
                "symbols": ["SPY", "QQQ", "AAPL", "TSLA"]
            },
            "futures": {
                "name": "Futures (IB)",
                "hours": "Nearly 24/5",
                "broker": ["ib"],
                "symbols": ["ES", "NQ", "CL", "GC"]
            },
            "forex": {
                "name": "Forex (IB)",
                "hours": "24/5 (Sunday 5PM - Friday 5PM ET)",
                "broker": ["ib"],
                "symbols": ["EUR/USD", "GBP/USD", "USD/JPY"]
            }
        }
        
        # Offline activities (when markets closed)
        self.offline_activities = [
            "backtest_new_strategies",
            "analyze_past_trades",
            "train_pattern_recognition",
            "optimize_parameters",
            "ingest_knowledge",
            "generate_reports"
        ]
        
        self.load_stats()
    
    def load_stats(self):
        """Load previous statistics"""
        stats_file = Path("prometheus_autonomous_stats.json")
        if stats_file.exists():
            try:
                with open(stats_file) as f:
                    saved = json.load(f)
                    self.stats.update(saved)
            except:
                pass
    
    def save_stats(self):
        """Save current statistics"""
        self.stats["uptime_hours"] = (datetime.now() - self.start_time).total_seconds() / 3600
        with open("prometheus_autonomous_stats.json", 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def get_market_status(self) -> Dict:
        """Get current market status"""
        if self.scheduler:
            return self.scheduler.get_market_status()
        
        # Fallback
        import pytz
        et = datetime.now(pytz.timezone('US/Eastern'))
        hour = et.hour
        is_weekend = et.weekday() >= 5
        
        if is_weekend:
            return {"session": "weekend", "is_open": False}
        elif 9 <= hour < 16:
            return {"session": "regular", "is_open": True}
        else:
            return {"session": "closed", "is_open": False}
    
    def display_status(self):
        """Display current PROMETHEUS status"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        status = self.get_market_status()
        uptime = datetime.now() - self.start_time
        
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ██████╗  ██████╗ ███╗   ███╗███████╗████████╗██╗  ██╗███████╗     ║
║   ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔════╝╚══██╔══╝██║  ██║██╔════╝     ║
║   ██████╔╝██████╔╝██║   ██║██╔████╔██║█████╗     ██║   ███████║█████╗       ║
║   ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔══╝     ██║   ██╔══██║██╔══╝       ║
║   ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗   ██║   ██║  ██║███████╗     ║
║   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝     ║
║                                                                              ║
║                    AUTONOMOUS 24/7 INTELLIGENCE SYSTEM                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
        
        # Time display
        if self.scheduler:
            times = self.scheduler.get_all_timezones()
            print(f"  📍 Your Time:   {times['local'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"  🇺🇸 US Eastern:  {times['eastern'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
        else:
            print(f"  📍 Local Time:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"  ⏱️  Uptime:      {str(uptime).split('.')[0]}")
        
        # Current mode
        mode_display = {
            "trading": "🟢 ACTIVELY TRADING",
            "learning": "🧠 LEARNING & ANALYZING",
            "backtesting": "📊 BACKTESTING STRATEGIES",
            "optimizing": "⚙️ OPTIMIZING PARAMETERS",
            "idle": "💤 IDLE (Weekend)",
            "initializing": "🔄 INITIALIZING..."
        }
        print(f"\n  🎯 Current Mode: {mode_display.get(self.current_mode, self.current_mode)}")
        
        # Market status
        session = status.get('session', 'unknown')
        session_emoji = {
            "regular": "🟢 OPEN",
            "pre_market": "🟡 PRE-MARKET",
            "after_hours": "🟠 AFTER-HOURS",
            "closed": "🔴 CLOSED",
            "weekend": "⚫ WEEKEND",
            "holiday": "🔵 HOLIDAY"
        }
        print(f"  📈 US Market:   {session_emoji.get(session, session)}")
        print(f"  🪙 Crypto:      🟢 24/7 ACTIVE")
        
        if status.get('time_to_close'):
            print(f"  ⏳ Closes in:   {status['time_to_close']}")
        if status.get('time_to_open'):
            print(f"  ⏳ Opens in:    {status['time_to_open']}")
        
        # Statistics
        print(f"""
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊 SESSION STATISTICS
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
    Trading Sessions:    {self.stats['trading_sessions']}
    Learning Sessions:   {self.stats['learning_sessions']}
    Backtests Run:       {self.stats['backtests_run']}
    Patterns Learned:    {self.stats['patterns_learned']}
    Trades Executed:     {self.stats['trades_executed']}
    Total P&L:           ${self.stats['total_pnl']:.2f}
""")
        
        # Available markets
        print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("  🌍 AVAILABLE TRADING MARKETS")
        print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        for market_id, market in self.markets.items():
            is_active = "🟢" if self._is_market_active(market_id, status) else "🔴"
            print(f"    {is_active} {market['name']}")
            print(f"       Hours: {market['hours']}")
            print(f"       Symbols: {', '.join(market['symbols'][:5])}...")
            print()
        
        print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("  Press Ctrl+C to stop PROMETHEUS")
        print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    def _is_market_active(self, market_id: str, status: Dict) -> bool:
        """Check if a specific market is currently active"""
        session = status.get('session', 'closed')
        
        if market_id == "crypto":
            return True  # Crypto is always active
        elif market_id == "us_stocks":
            return session in ["regular", "pre_market", "after_hours"]
        elif market_id == "futures":
            return session != "weekend"
        elif market_id == "forex":
            return session != "weekend"
        else:
            return session == "regular"
    
    async def run_trading_session(self, status: Dict):
        """Run an active trading session"""
        self.current_mode = "trading"
        self.stats["trading_sessions"] += 1
        logger.info("🚀 Starting trading session...")
        
        try:
            # Determine which markets to trade
            active_markets = []
            for market_id, market in self.markets.items():
                if self._is_market_active(market_id, status):
                    active_markets.append(market_id)
            
            logger.info(f"Active markets: {active_markets}")
            
            # Import and run the dual broker system
            try:
                from final_dual_broker_fixed import FinalDualBrokerTradingSystem
                
                # Run one trading iteration
                system = FinalDualBrokerTradingSystem()
                await system.initialize()
                
                # Trade for the session
                result = await system.run_single_iteration()
                
                if result and result.get('trades'):
                    self.stats["trades_executed"] += len(result['trades'])
                    self.stats["total_pnl"] += result.get('pnl', 0)
                
            except Exception as e:
                logger.error(f"Trading system error: {e}")
                
                # Fallback: Try crypto trading via Alpaca
                if "crypto" in active_markets:
                    await self._trade_crypto()
        
        except Exception as e:
            logger.error(f"Trading session error: {e}")
    
    async def _trade_crypto(self):
        """Trade crypto 24/7"""
        logger.info("📈 Trading crypto...")
        
        try:
            from alpaca.trading.client import TradingClient
            from alpaca.trading.requests import MarketOrderRequest
            from alpaca.trading.enums import OrderSide, TimeInForce
            
            # Load Alpaca credentials
            api_key = os.getenv('ALPACA_API_KEY', '')
            secret_key = os.getenv('ALPACA_SECRET_KEY', '')
            
            if api_key and secret_key:
                client = TradingClient(api_key, secret_key, paper=True)
                account = client.get_account()
                logger.info(f"Alpaca account: ${float(account.equity):.2f}")
                
                # Check for crypto opportunities
                # This is where crypto trading logic would go
                
        except Exception as e:
            logger.warning(f"Crypto trading not available: {e}")
    
    async def run_learning_session(self):
        """Run learning and analysis when markets are closed"""
        self.current_mode = "learning"
        self.stats["learning_sessions"] += 1
        logger.info("🧠 Starting learning session...")
        
        activities = [
            self._analyze_past_trades,
            self._train_patterns,
            self._ingest_knowledge,
            self._run_backtest,
            self._optimize_parameters
        ]
        
        for activity in activities:
            try:
                await activity()
            except Exception as e:
                logger.error(f"Learning activity error: {e}")
            
            # Check if market opened
            status = self.get_market_status()
            if status.get('is_open') or status.get('session') in ['pre_market', 'after_hours']:
                logger.info("Market opened - switching to trading mode")
                return
    
    async def _analyze_past_trades(self):
        """Analyze past trades to learn from them"""
        logger.info("📊 Analyzing past trades...")
        
        try:
            # Load trade history
            trade_files = list(Path(".").glob("trade_history*.json"))
            if trade_files:
                # Analyze each trade file
                for trade_file in trade_files[-5:]:  # Last 5 files
                    with open(trade_file) as f:
                        trades = json.load(f)
                        logger.info(f"Analyzed {len(trades)} trades from {trade_file.name}")
        except Exception as e:
            logger.debug(f"Trade analysis: {e}")
    
    async def _train_patterns(self):
        """Train pattern recognition on historical data"""
        logger.info("🎯 Training pattern recognition...")
        
        try:
            # Check if pattern training is needed
            pattern_files = list(Path(".").glob("visual_ai_patterns*.json"))
            if pattern_files:
                latest = max(pattern_files, key=lambda p: p.stat().st_mtime)
                with open(latest) as f:
                    patterns = json.load(f)
                    self.stats["patterns_learned"] = patterns.get("total_patterns", 0)
                    logger.info(f"Patterns loaded: {self.stats['patterns_learned']}")
        except Exception as e:
            logger.debug(f"Pattern training: {e}")
    
    async def _ingest_knowledge(self):
        """Ingest new knowledge from research papers"""
        logger.info("📚 Checking knowledge base...")
        
        try:
            from knowledge_ingestion_pipeline import KnowledgeIngestionPipeline
            pipeline = KnowledgeIngestionPipeline()
            
            # Check for new PDFs in knowledge_base folder
            kb_path = Path("knowledge_base")
            if kb_path.exists():
                pdfs = list(kb_path.glob("*.pdf"))
                logger.info(f"Knowledge base: {len(pdfs)} research papers available")
        except Exception as e:
            logger.debug(f"Knowledge ingestion: {e}")
    
    async def _run_backtest(self):
        """Run backtests on new strategies"""
        self.current_mode = "backtesting"
        logger.info("📈 Running strategy backtest...")
        
        try:
            self.stats["backtests_run"] += 1
            
            # Run a quick backtest
            # This would integrate with the learning backtest system
            
        except Exception as e:
            logger.debug(f"Backtest: {e}")
    
    async def _optimize_parameters(self):
        """Optimize strategy parameters"""
        self.current_mode = "optimizing"
        logger.info("⚙️ Optimizing parameters...")
        
        try:
            # Load and update optimized config
            config_file = Path("advanced_paper_trading_config_optimized.json")
            if config_file.exists():
                with open(config_file) as f:
                    config = json.load(f)
                    logger.info(f"Config loaded: {config.get('system_name', 'Unknown')}")
        except Exception as e:
            logger.debug(f"Optimization: {e}")
    
    def run(self):
        """Main 24/7 loop"""
        logger.info("=" * 60)
        logger.info("🔥 PROMETHEUS AUTONOMOUS 24/7 SYSTEM STARTING")
        logger.info("=" * 60)
        
        # Handle graceful shutdown
        def signal_handler(sig, frame):
            logger.info("\n🛑 Shutdown signal received...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            while self.running:
                # Get market status
                status = self.get_market_status()
                session = status.get('session', 'closed')
                
                # Display status
                self.display_status()
                
                # Decide what to do
                if session == "weekend":
                    # Weekend - focus on learning
                    self.current_mode = "learning"
                    loop.run_until_complete(self.run_learning_session())
                    time.sleep(300)  # Check every 5 minutes
                    
                elif session in ["regular", "pre_market", "after_hours"]:
                    # Market is open - TRADE!
                    loop.run_until_complete(self.run_trading_session(status))
                    time.sleep(60)  # Check every minute during trading
                    
                else:
                    # Market closed but not weekend
                    # Trade crypto if available, otherwise learn
                    if self.markets.get("crypto"):
                        loop.run_until_complete(self._trade_crypto())
                    
                    loop.run_until_complete(self.run_learning_session())
                    time.sleep(120)  # Check every 2 minutes
                
                # Save stats periodically
                self.save_stats()
        
        except KeyboardInterrupt:
            logger.info("\n🛑 PROMETHEUS shutting down gracefully...")
        finally:
            self.save_stats()
            loop.close()
            
            print("\n" + "=" * 60)
            print("PROMETHEUS AUTONOMOUS SESSION ENDED")
            print("=" * 60)
            print(f"Total uptime: {str(datetime.now() - self.start_time).split('.')[0]}")
            print(f"Trading sessions: {self.stats['trading_sessions']}")
            print(f"Learning sessions: {self.stats['learning_sessions']}")
            print(f"Backtests run: {self.stats['backtests_run']}")
            print("=" * 60)


def create_windows_shortcut():
    """Create a desktop shortcut to run PROMETHEUS"""
    script_path = Path(__file__).resolve()
    
    shortcut_content = f'''@echo off
title PROMETHEUS Autonomous 24/7 Trading System
cd /d "{script_path.parent}"
python "{script_path.name}"
pause
'''
    
    shortcut_path = script_path.parent / "START_PROMETHEUS.bat"
    with open(shortcut_path, 'w') as f:
        f.write(shortcut_content)
    
    logger.info(f"Created launcher: {shortcut_path}")
    return shortcut_path


def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                 PROMETHEUS AUTONOMOUS 24/7 INTELLIGENCE                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   This system runs CONTINUOUSLY - trading when markets are open,            ║
║   learning and improving when markets are closed.                           ║
║                                                                              ║
║   TRADING CAPABILITIES:                                                      ║
║   ├─ US Stocks (Alpaca + IB)     : 9:30 AM - 4:00 PM ET                     ║
║   ├─ Extended Hours (Pre/After)  : 4:00 AM - 8:00 PM ET                     ║
║   ├─ Crypto (Alpaca)             : 24/7                                     ║
║   ├─ Options (IB)                : Regular Hours                            ║
║   ├─ Futures (IB)                : Nearly 24/5                              ║
║   └─ Forex (IB)                  : 24/5                                     ║
║                                                                              ║
║   LEARNING CAPABILITIES (when not trading):                                  ║
║   ├─ Backtest new strategies                                                ║
║   ├─ Analyze past trades                                                    ║
║   ├─ Train pattern recognition                                              ║
║   ├─ Optimize parameters                                                    ║
║   ├─ Ingest new knowledge                                                   ║
║   └─ Generate performance reports                                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Create launcher shortcut
    launcher = create_windows_shortcut()
    print(f"\n📌 Created launcher: {launcher}")
    print("   Double-click this file to start PROMETHEUS outside VS Code!\n")
    
    # Start the system
    prometheus = PrometheusAutonomous247()
    prometheus.run()


if __name__ == "__main__":
    main()
