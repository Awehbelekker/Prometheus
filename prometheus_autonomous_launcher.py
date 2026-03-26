#!/usr/bin/env python3
"""
🚀 PROMETHEUS FULLY AUTONOMOUS LAUNCHER
=======================================
Runs LIVE TRADING + SHADOW TRADING in parallel with all AI systems enabled.

Features:
- Live Trading: Real trades with Alpaca (uses prometheus_active_trading_session.py)
- Shadow Trading: Paper trading comparison (uses parallel_shadow_trading.py)
- All 20+ AI Systems: HRM, Universal Reasoning, Visual Patterns, Quantum, etc.
- Full Learning: Continuous Learning, AI Attribution, Pattern Recognition
- DeepSeek Cloud API: Fast AI decisions when credits available

Usage:
    python prometheus_autonomous_launcher.py
    
Stop: Press Ctrl+C for graceful shutdown
"""

import sys
import os

# Fix Windows encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import asyncio
import subprocess
import signal
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/prometheus_autonomous_{timestamp}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global processes for cleanup
processes = []

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("\n⏹️ Shutdown signal received. Stopping all processes...")
    for proc in processes:
        if proc and proc.poll() is None:
            proc.terminate()
    logger.info("✅ All processes stopped. Goodbye!")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def print_banner():
    """Print startup banner"""
    print("\n" + "="*70)
    print("🔥 PROMETHEUS FULLY AUTONOMOUS TRADING SYSTEM")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    print("📊 Systems Enabled:")
    print("   ✅ Live Trading (Alpaca Paper Mode)")
    print("   ✅ Shadow Trading (AI Comparison)")
    print("   ✅ DeepSeek Cloud API (if credits available)")
    print("   ✅ All 20+ AI Systems")
    print("   ✅ Full Learning Systems")
    print("")
    print("📁 Logs: logs/prometheus_autonomous_*.log")
    print("⏹️ Stop: Press Ctrl+C")
    print("="*70 + "\n")


def main():
    """Main launcher - runs live and shadow trading in parallel"""
    print_banner()
    
    project_dir = Path(__file__).parent
    
    # Define the scripts to run
    scripts = [
        ("🟢 LIVE TRADING", "prometheus_active_trading_session.py"),
        ("🔵 SHADOW TRADING", "parallel_shadow_trading.py --capital 100000 --interval 60"),
    ]
    
    logger.info("🚀 Starting PROMETHEUS in parallel mode...")
    
    for name, script in scripts:
        script_path = project_dir / script.split()[0]
        if not script_path.exists():
            logger.error(f"❌ Script not found: {script_path}")
            continue
        
        logger.info(f"   Starting {name}: {script}")
        
        # Launch in separate process
        cmd = f'python {script}'
        proc = subprocess.Popen(
            cmd,
            shell=True,
            cwd=str(project_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        processes.append(proc)
        logger.info(f"   ✅ {name} started (PID: {proc.pid})")
    
    logger.info("\n🎯 All systems running. Monitoring output...\n")
    
    # Monitor processes and print their output
    try:
        while True:
            all_done = True
            for i, proc in enumerate(processes):
                if proc.poll() is None:
                    all_done = False
                    # Read output if available
                    if proc.stdout:
                        line = proc.stdout.readline()
                        if line:
                            prefix = "🟢" if i == 0 else "🔵"
                            print(f"{prefix} {line.rstrip()}")
            
            if all_done:
                logger.info("⚠️ All processes have exited.")
                break
            
            # Small sleep to prevent CPU spinning
            import time
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()

