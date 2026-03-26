#!/usr/bin/env python3
"""
===============================================================================
 PROMETHEUS HEADLESS LIVE TRADING LAUNCHER
===============================================================================
Runs the full live trading engine + shadow learning WITHOUT the heavy
unified_production_server.py frontend. No web UI, no dashboard — just
pure trading with all cylinders firing.

Launch from any terminal (CMD, PowerShell, outside VS Code):
    python prometheus_headless.py

What runs:
  - All 6 tiers of AI systems (80+ systems)
  - Live Alpaca broker (crypto 24/7 + equities market hours)
  - Live IB Gateway connection (port 4002)
  - 30-second trading cycles with full AI consensus
  - Multi-strategy shadow trading (3 strategies, learning engine)
  - AI attribution tracking + continuous learning
  - Lightweight health API on port 8001 (optional, for monitoring)

What does NOT run:
  - unified_production_server.py (13K-line FastAPI app)
  - Frontend dashboard / web UI
  - Advanced monitoring dashboards
  - Heavy API endpoint layer
===============================================================================
"""

import sys
import os
import signal
import asyncio
import logging
import threading
from datetime import datetime
from pathlib import Path

# ─── UTF-8 encoding setup ───────────────────────────────────────────────────
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if sys.stderr:
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
os.environ['PYTHONIOENCODING'] = 'utf-8'

# ─── Ensure we're in the right directory ─────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)
sys.path.insert(0, str(SCRIPT_DIR))

# ─── Load environment variables ──────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

# ─── Logging setup ───────────────────────────────────────────────────────────
LOG_FILE = SCRIPT_DIR / "prometheus_headless.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("prometheus.headless")


# ═════════════════════════════════════════════════════════════════════════════
# SHADOW TRADING (LEARNING ENGINE) — runs in a background thread
# ═════════════════════════════════════════════════════════════════════════════
def start_shadow_trading():
    """Start multi-strategy shadow trading in a daemon thread for continuous learning."""
    shadow_thread = None

    # Attempt 1: Multi-strategy runner (3 strategies in parallel)
    try:
        from multi_strategy_shadow_runner import MultiStrategyShadowRunner
        watchlist = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META',
            'SPY', 'QQQ', 'BTC-USD', 'ETH-USD', 'SOL-USD',
        ]
        runner = MultiStrategyShadowRunner(
            strategies=['conservative', 'momentum', 'ai_consensus'],
            starting_capital=100000.0,
            watchlist=watchlist,
        )

        def _run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(runner.run_all_strategies(
                    interval_seconds=120,
                    max_iterations=None,
                    report_interval=10,
                    leaderboard_interval=30,
                ))
            except BaseException as exc:
                logger.error(f"Shadow trading thread ended: {type(exc).__name__}: {exc}")
            finally:
                loop.close()

        shadow_thread = threading.Thread(target=_run, daemon=True, name="shadow-multi")
        shadow_thread.start()
        logger.info("Shadow trading STARTED (multi-strategy: conservative + momentum + ai_consensus)")
        return shadow_thread

    except Exception as exc:
        logger.warning(f"Multi-strategy shadow init failed, falling back to single: {exc}")

    # Attempt 2: Single-strategy fallback
    try:
        from parallel_shadow_trading import PrometheusParallelShadowTrading
        shadow = PrometheusParallelShadowTrading(starting_capital=100000.0)
        watchlist = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META',
            'SPY', 'QQQ', 'BTC-USD', 'ETH-USD', 'SOL-USD',
        ]

        def _run_single():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    shadow.run_shadow_trading(watchlist=watchlist, interval_seconds=120)
                )
            except BaseException as exc:
                logger.error(f"Single shadow trading ended: {type(exc).__name__}: {exc}")
            finally:
                loop.close()

        shadow_thread = threading.Thread(target=_run_single, daemon=True, name="shadow-single")
        shadow_thread.start()
        logger.info("Shadow trading STARTED (single-strategy fallback)")
        return shadow_thread

    except Exception as exc:
        logger.error(f"Shadow trading unavailable: {exc}")
        return None


# ═════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════
async def run_headless():
    """Launch Prometheus in headless mode — trading engine only, no frontend."""

    print()
    print("=" * 80)
    print("  PROMETHEUS HEADLESS LIVE TRADING")
    print("  No frontend. No dashboard. Pure trading.")
    print("=" * 80)
    print(f"  Started:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Log file: {LOG_FILE}")
    print(f"  PID:      {os.getpid()}")
    print("=" * 80)
    print()

    # ── Verify critical environment ──────────────────────────────────────────
    live_enabled = os.getenv('LIVE_TRADING_ENABLED', 'false').lower() == 'true'
    paper_mode = os.getenv('ALPACA_PAPER_TRADING', 'true').lower() == 'true'
    ib_enabled = os.getenv('IB_LIVE_ENABLED', 'false').lower() == 'true'
    alpaca_key = os.getenv('ALPACA_LIVE_KEY') or os.getenv('ALPACA_API_KEY') or os.getenv('APCA_API_KEY_ID')

    print("  CONFIGURATION:")
    print(f"    LIVE_TRADING_ENABLED:  {live_enabled}")
    print(f"    ALPACA_PAPER_TRADING:  {paper_mode}")
    print(f"    IB_LIVE_ENABLED:       {ib_enabled}")
    print(f"    Alpaca API Key:        {'SET' if alpaca_key else 'MISSING'}")
    print(f"    OpenAI Key:            {'SET' if os.getenv('OPENAI_API_KEY') else 'MISSING'}")
    print(f"    Polygon Key:           {'SET' if os.getenv('POLYGON_API_KEY') else 'MISSING'}")
    
    mode_str = "LIVE" if (live_enabled and not paper_mode) else "PAPER"
    print(f"\n    >>> MODE: {mode_str} TRADING <<<")
    print()

    if not alpaca_key:
        logger.error("FATAL: No Alpaca API key found. Cannot trade.")
        return

    # ── Step 1: Start shadow trading (learning engine) in background ─────────
    print("[1/4] Starting shadow trading (learning engine)...")
    shadow_thread = start_shadow_trading()
    if shadow_thread:
        print("      Shadow trading: RUNNING")
    else:
        print("      Shadow trading: UNAVAILABLE (non-critical)")

    # ── Step 2: Initialize the main trading engine ───────────────────────────
    print("[2/4] Initializing live trading engine (all 6 tiers)...")
    from launch_ultimate_prometheus_LIVE_TRADING import main as init_trading

    # standalone_mode=True gives us a lightweight API on 8001 for health checks
    # standalone_mode=False runs purely headless with zero API
    launcher = await init_trading(standalone_mode=True)

    if not launcher:
        logger.error("FATAL: Trading engine initialization returned None")
        return

    if not launcher.systems.get('alpaca_broker'):
        logger.error("FATAL: No broker connections available")
        return

    active_count = len([s for s in launcher.system_health.values() if s in ('ACTIVE', 'AVAILABLE')])
    total_count = len(launcher.system_health)
    failed_count = len(launcher.failed_systems)

    print(f"      Systems: {active_count}/{total_count} active, {failed_count} failed")
    print(f"      Brokers: Alpaca={'CONNECTED' if launcher.systems.get('alpaca_broker') else 'MISSING'}")
    print(f"               IB={'CONNECTED' if launcher.systems.get('ib_broker') else 'NOT CONNECTED'}")

    # ── Step 3: Start Adaptive Learning Engine in background ─────────────────
    print("[3/4] Starting Adaptive Learning Engine (5 background loops)...")
    try:
        from core.adaptive_learning_engine import AdaptiveLearningEngine

        adaptive_engine = AdaptiveLearningEngine()

        def _run_adaptive():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(adaptive_engine.start())
            except BaseException as exc:
                logger.error(f"Adaptive learning engine ended: {type(exc).__name__}: {exc}")
            finally:
                loop.close()

        ale_thread = threading.Thread(target=_run_adaptive, daemon=True, name="adaptive-learning")
        ale_thread.start()
        logger.info("Adaptive Learning Engine STARTED — outcome capture, weight update, "
                     "model retrain, risk adaptation, insight generation")
        print("      Adaptive Learning: RUNNING (5 loops)")
    except Exception as exc:
        logger.warning(f"Adaptive Learning Engine failed to start: {exc}")
        print(f"      Adaptive Learning: UNAVAILABLE ({exc})")

    # ── Step 4: Run the trading loop forever ─────────────────────────────────
    print("[4/4] Entering live trading loop (30-second cycles)...")
    print()
    print("=" * 80)
    print("  ALL CYLINDERS FIRING — Press Ctrl+C to stop")
    print("=" * 80)
    print()

    await launcher.run_forever()


def main():
    """Entry point with proper signal handling for Windows."""
    # Graceful shutdown on Ctrl+C
    def handle_signal(sig, frame):
        print("\n\n  Shutdown signal received. Stopping Prometheus...")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        asyncio.run(run_headless())
    except KeyboardInterrupt:
        print("\n\n  Goodbye!")
    except SystemExit:
        pass
    except Exception as exc:
        logger.error(f"Fatal error: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
