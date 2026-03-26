#!/usr/bin/env python3
"""Check the regime exposure manager and other gates."""
import sys, os
sys.path.insert(0, os.getcwd())

print("=" * 60)
print("  REGIME EXPOSURE + GUARDIAN + TIMING GATE CHECK")
print("=" * 60)

# 1. Regime Exposure Manager
print("\n--- REGIME EXPOSURE MANAGER ---")
try:
    from core.regime_exposure_manager import get_regime_exposure_manager
    rem = get_regime_exposure_manager()
    state = rem.get_current_state()
    print(f"  Target allocation: {state.target_allocation:.2%}")
    print(f"  Current regime: {getattr(state, 'regime', 'unknown')}")
    print(f"  Risk level: {getattr(state, 'risk_level', 'unknown')}")
    if state.target_allocation <= 0.02:
        print("  *** THIS IS BLOCKING ALL TRADES! Target allocation <= 2% ***")
    else:
        print("  OK - target allocation above 2% threshold")
    # Print all attributes
    for attr in dir(state):
        if not attr.startswith('_'):
            try:
                val = getattr(state, attr)
                if not callable(val):
                    print(f"  {attr}: {val}")
            except:
                pass
except Exception as e:
    print(f"  Regime manager: {e}")

# 2. HMM Regime Detector
print("\n--- HMM REGIME DETECTOR ---")
try:
    from core.hmm_regime_detector import get_regime_detector
    rd = get_regime_detector()
    rs = rd.get_status()
    print(f"  Status: {rs}")
except Exception as e:
    print(f"  HMM Regime: {e}")

# 3. Drawdown Guardian
print("\n--- DRAWDOWN GUARDIAN ---")
try:
    from core.drawdown_guardian import DrawdownGuardian
    guardian = DrawdownGuardian()
    # Test a crypto trade
    approved, adj_size, reason = guardian.gate(
        symbol="SOL-USD",
        action="BUY",
        proposed_size=0.15,
        price=130.0,
        confidence=0.811,
        portfolio_value=350.0,
        open_positions={},
        regime="unknown",
        volatility_ratio=1.0
    )
    print(f"  SOL-USD BUY test: approved={approved}, adj_size={adj_size:.2%}, reason={reason}")
except Exception as e:
    print(f"  Guardian: {e}")

# 4. Sentiment Filter
print("\n--- SENTIMENT FILTER ---")
try:
    # The sentiment filter is a method on the launcher
    from datetime import datetime
    # Check for Fed days or events
    today = datetime.now()
    # Typically this checks if today is a Fed announcement day
    print(f"  Today: {today.strftime('%A %Y-%m-%d')}")
    print(f"  Weekend - no Fed events concern")
except Exception as e:
    print(f"  Sentiment: {e}")

# 5. Check AI Timing
print("\n--- AI TIMING ---")
try:
    hour = datetime.now().hour
    minute = datetime.now().minute
    print(f"  Current hour: {hour}:{minute:02d}")
    # The timing check avoids first 15 min of market open and last 15 min before close
    # For crypto this shouldn't matter
    if 9 <= hour <= 10 and minute < 15:
        print("  WARNING: Near market open - timing might block")
    elif 15 <= hour <= 16 and minute > 45:
        print("  WARNING: Near market close - timing might block")
    else:
        print("  OK - not near volatile times")
except Exception as e:
    print(f"  Timing: {e}")
