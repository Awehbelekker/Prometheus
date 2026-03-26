#!/usr/bin/env python3
"""Test the exact same shadow thread that runs in the server."""
import asyncio
import sys
import traceback
import threading
import logging
import time

# Force verbose logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    stream=sys.stdout
)
# Suppress noisy loggers
for name in ['urllib3', 'filelock', 'torch', 'tensorflow']:
    logging.getLogger(name).setLevel(logging.WARNING)

print("=" * 60)
print("FULL SHADOW THREAD TEST (mirrors server exactly)")
print("=" * 60)

from multi_strategy_shadow_runner import MultiStrategyShadowRunner

watchlist = ['AAPL', 'MSFT', 'SPY']
runner = MultiStrategyShadowRunner(
    strategies=['conservative', 'momentum', 'ai_consensus'],
    starting_capital=100000.0,
    watchlist=watchlist
)

# This is EXACTLY what the server does:
def _run_shadow():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        print(f"[THREAD] Starting run_all_strategies at {time.strftime('%H:%M:%S')}")
        loop.run_until_complete(runner.run_all_strategies(
            interval_seconds=10,    # short for testing
            max_iterations=2,       # just 2 iterations
            report_interval=1,
            leaderboard_interval=1
        ))
        print(f"[THREAD] run_all_strategies completed normally at {time.strftime('%H:%M:%S')}")
    except BaseException as _e:
        print(f"[THREAD] Shadow trading thread ended with {type(_e).__name__}: {_e}")
        traceback.print_exc()
    finally:
        try:
            loop.close()
            print("[THREAD] Event loop closed successfully")
        except Exception as close_err:
            print(f"[THREAD] Error closing event loop: {close_err}")

thread = threading.Thread(target=_run_shadow, daemon=True, name="shadow-trading")
print(f"\n[MAIN] Starting shadow thread...")
thread.start()

# Wait for thread to finish (max 5 minutes)
for i in range(300):
    if not thread.is_alive():
        print(f"\n[MAIN] Thread died after {i} seconds")
        break
    if i % 15 == 0 and i > 0:
        print(f"[MAIN] Thread still alive after {i}s...")
    time.sleep(1)
else:
    print(f"\n[MAIN] Thread still running after 300s (expected)")

print(f"\n[MAIN] Final thread status: alive={thread.is_alive()}")
print("[MAIN] Test complete")
