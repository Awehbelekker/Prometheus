#!/usr/bin/env python3
"""Quick test of DrawdownGuardian — all 10 protection layers"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from core.drawdown_guardian import DrawdownGuardian

g = DrawdownGuardian({"db_path": ":memory:"})
PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; icon = "+"
    else:
        FAIL += 1; icon = "x"
    print(f"  [{icon}] {name}  {detail}")

print("=" * 60)
print("  DRAWDOWN GUARDIAN — 10-Layer Protection Test")
print("=" * 60)

# L1: Circuit breaker (no loss yet, should pass)
ok, sz, r = g.gate("AAPL", "BUY", 10, 230, confidence=0.8, portfolio_value=10000, open_positions={}, regime="bull")
check("L1 Circuit breaker pass (no loss)", ok, r[:50])

# L1b: Trip circuit breaker with daily loss
g.current_equity = 10000
g.daily_pnl = -350  # -3.5% daily loss
ok, sz, r = g.gate("AAPL", "BUY", 10, 230, confidence=0.8, portfolio_value=10000, open_positions={}, regime="bull")
check("L1b Circuit breaker trips on daily -3.5%", not ok, r[:60])
# Reset
g.circuit_breaker_tripped = False
g.circuit_breaker_until = None
g.daily_pnl = 0

# L2: Trailing stop — simulate 10% drawdown
g.high_water_mark = 10000
g.current_equity = 9000  # -10% drawdown
ok, sz, r = g.gate("AAPL", "BUY", 10, 230, confidence=0.8, portfolio_value=9000, open_positions={}, regime="bull")
check("L2 Trailing stop reduces size at -10% DD", ok and sz < 10, f"size={sz:.1f} {r[:50]}")

# L2b: Critical drawdown (simulate -16% DD)
g.current_equity = 8400  # -16%
ok, sz, r = g.gate("AAPL", "BUY", 10, 230, confidence=0.8, portfolio_value=8400, open_positions={}, regime="bull")
check("L2b Critical DD blocks trade at -16%", not ok, r[:60])
# Reset HWM for subsequent tests
g.high_water_mark = 0
g.current_equity = 0

# L3: Regime gate
ok, sz, r = g.gate("AAPL", "BUY", 10, 230, confidence=0.8, portfolio_value=10000, open_positions={}, regime="crisis")
check("L3 Crisis regime blocks BUY", not ok, r[:60])

ok, sz, r = g.gate("AAPL", "SELL", 10, 230, confidence=0.8, portfolio_value=10000, open_positions={}, regime="crisis")
check("L3b Crisis allows SELL", ok, r[:50])

# L4: Max positions
full = {f"SYM{i}": {"market_value": 1000} for i in range(10)}
ok, sz, r = g.gate("NEW", "BUY", 10, 50, confidence=0.8, portfolio_value=10000, open_positions=full, regime="bull")
check("L4 Max positions blocks at 10", not ok, r[:60])

# L4b: Drawdown reduces max positions
five_pos = {f"S{i}": {"market_value": 1000} for i in range(5)}
ok, sz, r = g.gate("NEW", "BUY", 10, 50, confidence=0.8, portfolio_value=10000, open_positions=five_pos, regime="high_vol_choppy")
check("L4b High vol caps at 5 positions", not ok, r[:60])

# L5: Correlation guard
corr = {"AAPL": {"market_value": 2000}, "MSFT": {"market_value": 2000}, "GOOGL": {"market_value": 2000}}
ok, sz, r = g.gate("META", "BUY", 5, 500, confidence=0.8, portfolio_value=10000, open_positions=corr, regime="bull")
check("L5 Correlation blocks 4th mega-cap tech", not ok, r[:60])

# L5b: Correlation allows first in group
ok, sz, r = g.gate("NVDA", "BUY", 5, 700, confidence=0.8, portfolio_value=100000, open_positions={}, regime="bull")
check("L5b Correlation allows first in group", ok, r[:50])

# Reset HWM so next tests with $10K portfolio aren't blocked by trailing stop
g.high_water_mark = 0
g.current_equity = 0

# L6: Single position cap (15%)
ok, sz, r = g.gate("AAPL", "BUY", 100, 230, confidence=0.8, portfolio_value=10000, open_positions={}, regime="bull")
check("L6 Position >15% gets capped", ok and sz < 100, f"size={sz:.2f} (was 100)")

# L7: Sector exposure
sector_heavy = {"BTC/USD": {"market_value": 3000}, "ETH/USD": {"market_value": 2000}}
ok, sz, r = g.gate("SOL/USD", "BUY", 100, 20, confidence=0.8, portfolio_value=10000, open_positions=sector_heavy, regime="bull")
check("L7 Sector blocks crypto at 40%", not ok, r[:60])

# L7b: Sector allows when under limit
ok, sz, r = g.gate("SOL/USD", "BUY", 5, 20, confidence=0.8, portfolio_value=100000, open_positions={}, regime="bull")
check("L7b Sector allows when under limit", ok, r[:60])
# Reset HWM for next tests with smaller portfolios
g.high_water_mark = 0
g.current_equity = 0

# L8: Volatility scaling
ok, sz, r = g.gate("TSLA", "BUY", 10, 300, confidence=0.8, portfolio_value=100000, open_positions={}, regime="bull", volatility_ratio=2.5)
check("L8 High vol reduces size", ok and sz < 10, f"size={sz:.1f}")

# L8b: Normal vol no reduction
ok, sz, r = g.gate("TSLA", "BUY", 10, 300, confidence=0.8, portfolio_value=100000, open_positions={}, regime="bull", volatility_ratio=1.0)
check("L8b Normal vol no reduction", ok and sz == 10, f"size={sz:.1f}")

# Reset HWM for confidence tests with smaller portfolio
g.high_water_mark = 0
g.current_equity = 0

# L9: Confidence filter
ok, sz, r = g.gate("AAPL", "BUY", 10, 230, confidence=0.40, portfolio_value=10000, open_positions={}, regime="bull")
check("L9 Low confidence blocked", not ok, r[:50])

ok, sz, r = g.gate("AAPL", "BUY", 10, 230, confidence=0.60, portfolio_value=10000, open_positions={}, regime="bull")
check("L9b Medium conf reduces size", ok and sz < 10, f"size={sz:.1f}")

# L10: Stop-loss registration + trigger
stop = g.set_stop_loss("AAPL", 230.0, 10.0)
check("L10 Stop-loss registered", stop["stop_price"] < 230 and stop["stop_pct"] == 2.0,
      f"stop=${stop['stop_price']:.2f}")

stop_c = g.set_stop_loss("BTC/USD", 68000.0, 0.01)
check("L10b Crypto stop (wider)", stop_c["stop_pct"] == 4.0, f"stop_pct={stop_c['stop_pct']}%")

# Stop trigger check
triggered = g.check_stops({"AAPL": 220.0})  # below 225.40 stop
check("L10c Stop-loss triggers on price drop", len(triggered) > 0,
      f"triggered={len(triggered)}")

# Status
status = g.get_status()
check("Status report works", all(k in status for k in ["drawdown_pct", "limits", "blocks_today"]),
      f"blocks={status.get('blocks_today', 0)}")

# P/L tracking
g.update_pnl(-50.0, 9950.0)
check("P/L tracking works", g.daily_pnl == -50.0 and g.current_equity == 9950.0, 
      f"daily_pnl={g.daily_pnl}")

# Reset functions
g.reset_daily_pnl()
check("Daily reset works", g.daily_pnl == 0.0, "daily_pnl=0")

print(f"\n{'='*60}")
print(f"  Results: {PASS} passed, {FAIL} failed out of {PASS+FAIL}")
pct = PASS / (PASS + FAIL) * 100 if (PASS + FAIL) > 0 else 0
grade = "A+ PERFECT" if FAIL == 0 else "NEEDS FIXES" if FAIL > 3 else "GOOD"
print(f"  Score: {pct:.0f}%  Grade: {grade}")
print(f"{'='*60}")
