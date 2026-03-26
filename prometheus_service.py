#!/usr/bin/env python3
"""
 PROMETHEUS WINDOWS SERVICE
Runs PROMETHEUS as a Windows service with auto-restart
"""

import sys
import os

# CRITICAL: Set UTF-8 encoding BEFORE any other imports to prevent emoji encoding errors
# This must be done at the very top of the file before any logging or print statements
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

# Set environment variable for child processes
os.environ['PYTHONIOENCODING'] = 'utf-8'

import time
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
log_file = project_root / "prometheus_service.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def save_service_state(state: str):
    """Save service state for resume capability"""
    try:
        state_file = project_root / "service_state.json"
        import json
        from datetime import datetime

        state_data = {
            "state": state,
            "timestamp": datetime.now().isoformat(),
            "pid": os.getpid()
        }

        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)

    except Exception as e:
        logger.warning(f"Could not save state: {e}")

def load_service_state():
    """Load previous service state"""
    try:
        state_file = project_root / "service_state.json"
        if state_file.exists():
            import json
            with open(state_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load state: {e}")
    return None

def run_prometheus():
    """Run PROMETHEUS trading system with state persistence"""
    try:
        # UTF-8 encoding is already set at module level, but ensure it's still active
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

        logger.info("=" * 80)
        logger.info("PROMETHEUS SERVICE STARTING")
        logger.info("=" * 80)

        # Check previous state
        prev_state = load_service_state()
        if prev_state:
            logger.info(f"Previous state: {prev_state['state']}")
            logger.info(f"Last run: {prev_state['timestamp']}")
            logger.info("Resuming from previous state...")
        else:
            logger.info("Fresh start - no previous state")

        save_service_state("starting")

        # Import and run the trading system
        from launch_ultimate_prometheus_LIVE_TRADING import PrometheusLiveTradingLauncher
        import asyncio

        logger.info("Modules imported successfully")

        # Create trader instance
        trader = PrometheusLiveTradingLauncher(standalone_mode=False)
        logger.info("Trader instance created")

        save_service_state("running")

        # Run the trading system
        logger.info("Starting autonomous trading...")
        logger.info("State persistence: ENABLED")
        logger.info("Auto-resume: ENABLED")
        asyncio.run(trader.run_forever())

        save_service_state("stopped_normally")

    except KeyboardInterrupt:
        logger.info("WARNING: Service stopped by user")
        save_service_state("stopped_by_user")
    except Exception as e:
        logger.error(f"ERROR: Error in service: {e}", exc_info=True)
        save_service_state("crashed")
        raise

def main():
    """Main service loop with auto-restart and state tracking"""
    restart_count = 0
    max_restarts = 10
    restart_delay = 60  # Wait 60 seconds between restarts

    logger.info("PROMETHEUS Windows Service Started")
    logger.info(f"Working Directory: {os.getcwd()}")
    logger.info(f"Log File: {log_file}")
    logger.info(f"Auto-Restart: Enabled (max {max_restarts} attempts)")
    logger.info(f"State Persistence: Enabled")
    logger.info(f"Resume Capability: Enabled")

    # Check if this is a restart
    prev_state = load_service_state()
    if prev_state and prev_state.get('state') == 'crashed':
        logger.warning("WARNING: Detected previous crash - resuming operations")

    while restart_count < max_restarts:
        try:
            logger.info(f"Starting PROMETHEUS (Attempt {restart_count + 1}/{max_restarts})")
            run_prometheus()

            # If we get here, it means the system stopped normally
            logger.info("PROMETHEUS stopped normally")
            break

        except Exception as e:
            restart_count += 1
            logger.error(f"PROMETHEUS crashed: {e}")
            logger.error(f"Crash details logged for analysis")

            if restart_count < max_restarts:
                logger.info(f"Auto-restarting in {restart_delay} seconds...")
                logger.info(f"   Restart attempt {restart_count}/{max_restarts}")
                logger.info(f"   System will resume from last known state")
                time.sleep(restart_delay)
            else:
                logger.error(f"Max restarts ({max_restarts}) reached. Service stopping.")
                logger.error(f"WARNING: Manual intervention required - check logs")
                save_service_state("max_restarts_reached")
                break

    logger.info("PROMETHEUS Service Stopped")
    logger.info(f"Total restart attempts: {restart_count}")
    logger.info(f"Check logs for details: {log_file}")

if __name__ == "__main__":
    main()

