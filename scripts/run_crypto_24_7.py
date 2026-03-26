#!/usr/bin/env python3
"""
Run PROMETHEUS Crypto Trading 24/7 (safe, paper trading)
- Starts revolutionary_crypto_engine.py for continuous crypto trading
- Uses internal paper trading engine with real crypto market data
- Crypto markets never close, so this can run continuously
- Press Ctrl+C to stop safely
"""
import os
import sys
import asyncio
from datetime import datetime

# Ensure repo root on path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(repo_root)

try:
    from revolutionary_crypto_engine import PrometheusRevolutionaryCryptoEngine
    from core.internal_paper_trading import paper_trading_engine
except Exception as import_err:
    print(f"[ERROR] Failed to import crypto engine: {import_err}")
    print("Hint: Ensure all dependencies are installed and crypto engine is available")
    raise

async def main():
    print("🚀 Starting PROMETHEUS Crypto Trading 24/7 (paper trading)")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("💰 Crypto markets never close - continuous trading opportunity!")
    
    # Initialize paper trading engine first
    await paper_trading_engine.start_market_data_feed()
    print("[CHECK] Paper trading engine started with real market data")
    
    # Initialize crypto engine (will use paper trading internally)
    crypto_engine = PrometheusRevolutionaryCryptoEngine(
        alpaca_key=os.getenv('ALPACA_PAPER_KEY', ''),
        alpaca_secret=os.getenv('ALPACA_PAPER_SECRET', '')
    )
    
    try:
        print("🔥 Starting revolutionary crypto strategies...")
        
        # Start all crypto strategies concurrently
        tasks = [
            crypto_engine.revolutionary_arbitrage_strategy(),
            crypto_engine.revolutionary_momentum_strategy(),
            crypto_engine.revolutionary_24_7_monitoring(),
        ]
        
        # Add grid trading for top crypto pairs
        for symbol in ["BTC/USD", "ETH/USD", "SOL/USD"]:
            tasks.append(crypto_engine.revolutionary_grid_trading(symbol))
        
        print("[CHECK] All crypto strategies started. Running 24/7... Press Ctrl+C to stop.")
        
        # Run all strategies concurrently
        await asyncio.gather(*tasks)
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping crypto trading engine...")
        print("[CHECK] Crypto trading stopped safely.")
    except Exception as e:
        print(f"[ERROR] Crypto trading engine crashed: {e}")
        raise

if __name__ == '__main__':
    asyncio.run(main())
