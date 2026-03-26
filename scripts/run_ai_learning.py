#!/usr/bin/env python3
"""
Run the background AI Learning Engine (safe, data-only)
- Starts core.ai_learning_engine.AILearningEngine and its async tasks
- Does NOT place or route any orders
- Press Ctrl+C to stop (models and patterns will be saved)
"""
import os
import sys
import asyncio
from datetime import datetime

# Ensure repo root on path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(repo_root)

try:
    from core.ai_learning_engine import AILearningEngine
except Exception as import_err:
    print(f"[ERROR] Failed to import AILearningEngine: {import_err}")
    # Surface helpful tips without crashing the interpreter immediately
    print("Hint: Ensure scikit-learn, joblib, pandas, numpy, yfinance are installed per requirements.txt")
    raise

async def main():
    print("🧠 Starting AI Learning Engine (safe, data-only)")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    eng = AILearningEngine()
    try:
        await eng.start_learning()
        print("[CHECK] AI Learning Engine started. Running... Press Ctrl+C to stop.")
        # Keep running until interrupted
        while True:
            await asyncio.sleep(5)
    except KeyboardInterrupt:
        print("\n🛑 Stopping AI Learning Engine...")
        await eng.stop_learning()
        print("[CHECK] Stopped and saved state.")
    except Exception as e:
        print(f"[ERROR] AI Learning Engine crashed: {e}")
        try:
            await eng.stop_learning()
        except Exception:
            pass
        raise

if __name__ == '__main__':
    asyncio.run(main())

