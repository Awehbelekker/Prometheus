"""
PROMETHEUS WATCHDOG
===================
Monitors the main trading process and restarts it automatically if it crashes.

Restart policy:
  - Only restarts when IB Gateway is reachable on 127.0.0.1:4002
    (i.e. you have already logged in manually — watchdog won't attempt IB login)
  - If IB is down (PC rebooted, market closed, gateway not running):
    waits in a polling loop, no restart until IB is back
  - Alpaca-only mode: if IB is unreachable but WATCHDOG_ALPACA_ONLY=true in env,
    will restart anyway (Alpaca keeps trading without IB)
  - Max 10 consecutive crash-restarts before giving up (prevents infinite crash loop)
  - Exponential backoff: 30s → 60s → 120s → ... up to 10 min between restarts
  - Writes a log to prometheus_watchdog.log

Usage:
    python prometheus_watchdog.py

Or set it as a Windows Task Scheduler task with:
    Trigger: At startup (or At log on)
    Action:  python prometheus_watchdog.py
    Start in: C:/Users/Judy/Desktop/PROMETHEUS-Trading-Platform
"""

import os
import sys
import time
import socket
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
MAIN_SCRIPT = ROOT / os.environ.get('WATCHDOG_SCRIPT', 'unified_production_server.py')
LOG_FILE = ROOT / 'prometheus_watchdog.log'

IB_HOST = os.environ.get('IB_HOST', '127.0.0.1')
IB_PORT = int(os.environ.get('IB_PORT', '4002'))

MAX_CRASHES = 10              # give up after this many consecutive crashes
IB_POLL_INTERVAL = 60         # seconds between IB reachability checks when waiting
MIN_RESTART_DELAY = 30        # seconds before first restart after crash
MAX_RESTART_DELAY = 600       # cap backoff at 10 minutes
HEALTHY_RUN_THRESHOLD = 300   # seconds — if process runs >5 min, reset crash count

ALPACA_ONLY = os.environ.get('WATCHDOG_ALPACA_ONLY', 'false').lower() == 'true'

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-7s  %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger('watchdog')


def _ib_reachable() -> bool:
    """Quick TCP probe to check IB Gateway is accepting connections."""
    try:
        s = socket.create_connection((IB_HOST, IB_PORT), timeout=3)
        s.close()
        return True
    except OSError:
        return False


def _wait_for_ib():
    """Block until IB Gateway is reachable, polling every IB_POLL_INTERVAL seconds."""
    if ALPACA_ONLY:
        return  # don't gate on IB when running Alpaca-only
    if _ib_reachable():
        return
    log.info(f"IB Gateway not reachable on {IB_HOST}:{IB_PORT}. Waiting for manual login...")
    while not _ib_reachable():
        log.info(f"  Still waiting for IB Gateway... (checking every {IB_POLL_INTERVAL}s)")
        time.sleep(IB_POLL_INTERVAL)
    log.info("IB Gateway is now reachable — proceeding with restart.")


def _python_exe() -> str:
    """Return the Python executable that should run the trading script."""
    # Prefer the venv Python if it exists
    venv_python = ROOT / '.venv_directml_test' / 'Scripts' / 'python.exe'
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def _kill_port(port: int = 8000):
    """Kill any process already bound to the server port so we can bind cleanly."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                pid = int(parts[-1])
                if pid > 0:
                    subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                                   capture_output=True)
                    log.info(f"Killed stale server process PID {pid} on port {port}")
    except Exception as e:
        log.warning(f"Could not clear port {port}: {e}")


def _launch() -> subprocess.Popen:
    """Start the main trading process and return the Popen handle."""
    _kill_port(8000)  # ensure port is free before launching
    time.sleep(2)     # brief pause for OS to release the port
    python = _python_exe()
    log.info(f"Launching: {python} {MAIN_SCRIPT}")
    proc = subprocess.Popen(
        [python, str(MAIN_SCRIPT)],
        cwd=str(ROOT),
        stdout=None,
        stderr=None,
    )
    log.info(f"Process started — PID {proc.pid}")
    return proc


def main():
    log.info("=" * 70)
    log.info("PROMETHEUS WATCHDOG STARTED")
    log.info(f"  Main script : {MAIN_SCRIPT}")
    log.info(f"  IB Gateway  : {IB_HOST}:{IB_PORT}")
    log.info(f"  Alpaca-only : {ALPACA_ONLY}")
    log.info(f"  Max crashes : {MAX_CRASHES}")
    log.info("=" * 70)

    crash_count = 0
    restart_delay = MIN_RESTART_DELAY

    while True:
        # Wait for IB to be ready before each (re)start
        _wait_for_ib()

        if crash_count >= MAX_CRASHES:
            log.error(
                f"Reached {MAX_CRASHES} consecutive crashes. "
                "Watchdog giving up. Investigate logs before restarting manually."
            )
            sys.exit(1)

        start_ts = time.monotonic()
        proc = _launch()

        try:
            proc.wait()  # blocks until process exits
        except KeyboardInterrupt:
            log.info("Watchdog interrupted by user — sending SIGTERM to child.")
            proc.terminate()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
            log.info("Child stopped. Watchdog exiting.")
            sys.exit(0)

        elapsed = time.monotonic() - start_ts
        rc = proc.returncode

        if rc == 0:
            log.info(f"Process exited cleanly (rc=0) after {elapsed:.0f}s. Watchdog stopping.")
            sys.exit(0)

        log.warning(
            f"Process exited with rc={rc} after {elapsed:.0f}s. "
            f"Crash #{crash_count + 1}/{MAX_CRASHES}."
        )

        # If it ran long enough, treat as healthy run → reset crash counter
        if elapsed >= HEALTHY_RUN_THRESHOLD:
            log.info(
                f"Run lasted {elapsed:.0f}s (>{HEALTHY_RUN_THRESHOLD}s threshold) — "
                "resetting crash counter."
            )
            crash_count = 0
            restart_delay = MIN_RESTART_DELAY
        else:
            crash_count += 1
            restart_delay = min(restart_delay * 2, MAX_RESTART_DELAY)

        log.info(f"Waiting {restart_delay}s before restart...")
        time.sleep(restart_delay)


if __name__ == '__main__':
    main()
