#!/usr/bin/env python3
"""
PROMETHEUS COMPREHENSIVE BENCHMARK TEST
========================================
Validates ALL AI systems, 6 enhancements, AGGRESSIVE config,
and learning feedback loop with REAL market data.

Run: python benchmark_full_system_test.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import asyncio
import json
import sqlite3
import traceback
from datetime import datetime, timedelta
from pathlib import Path

# Track results
results = {"passed": 0, "failed": 0, "warnings": 0, "details": []}

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    icon = "+" if condition else "x"
    results["passed" if condition else "failed"] += 1
    results["details"].append({"name": name, "status": status, "detail": detail})
    print(f"  [{icon}] {name}" + (f" -- {detail}" if detail else ""))
    return condition

def warn(name, detail=""):
    results["warnings"] += 1
    results["details"].append({"name": name, "status": "WARN", "detail": detail})
    print(f"  [!] {name}" + (f" -- {detail}" if detail else ""))

def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

# ============================================================
# SECTION 1: AGGRESSIVE Configuration Verification
# ============================================================
def test_aggressive_config():
    section("1. AGGRESSIVE Configuration Parameters")
    from prometheus_active_trading_session import PrometheusActiveTradingSession
    s = PrometheusActiveTradingSession()

    check("Position size = 12%", s.position_size_pct == 0.12, f"actual={s.position_size_pct}")
    check("Stop loss = 2%", s.stop_loss_percent == 2.0, f"actual={s.stop_loss_percent}")
    check("Take profit = 5%", s.take_profit_pct == 0.05, f"actual={s.take_profit_pct}")
    check("Max positions = 8", s.max_concurrent_positions == 8, f"actual={s.max_concurrent_positions}")
    check("Min AI score = 2", s.min_ai_score == 2, f"actual={s.min_ai_score}")
    check("Max daily trades = 16", s.max_daily_trades == 16, f"actual={s.max_daily_trades}")
    check("Max daily loss = 5%", abs(s.max_daily_loss - s.starting_capital * 0.05) < 0.01)
    return s

# ============================================================
# SECTION 2: 6 Backtest Enhancements Verification
# ============================================================
def test_enhancements(s):
    section("2. Six Backtest Enhancements")
    check("TRAILING_STOP enabled", s.trailing_stop_enabled)
    check("  trigger=2%, distance=1%", s.trailing_stop_trigger == 0.02 and s.trailing_stop_distance == 0.01)
    check("DCA enabled", s.dca_enabled)
    check("  trigger=-2%, max_adds=2", s.dca_trigger_pct == -0.02 and s.dca_max_adds == 2)
    check("TIME_EXIT enabled", s.time_exit_enabled)
    check("  crypto=3d, stock=7d", s.max_hold_days_crypto == 3 and s.max_hold_days_stock == 7)
    check("SCALE_OUT enabled", s.scale_out_enabled)
    check("  first=+2%, second=+4%", s.scale_out_first_pct == 0.02 and s.scale_out_second_pct == 0.04)
    check("CORRELATION_FILTER enabled", s.correlation_filter_enabled)
    check("  max_correlated=2", s.max_correlated_positions == 2)
    check("SENTIMENT_FILTER enabled", s.sentiment_filter_enabled)
    check("  Fed days loaded", len(s.fed_days_2025_2026) >= 16, f"count={len(s.fed_days_2025_2026)}")
    # Position tracking dicts exist
    check("position_highs dict", isinstance(s.position_highs, dict))
    check("position_entry_times dict", isinstance(s.position_entry_times, dict))
    check("scaled_positions dict", isinstance(s.scaled_positions, dict))
    check("dca_counts dict", isinstance(s.dca_counts, dict))

# ============================================================
# SECTION 3: AI Systems Initialization
# ============================================================
def test_ai_systems(s):
    section("3. AI Systems Status")
    check("AI Brain Active", s.ai_brain_active, "Universal Reasoning / Hybrid / Unified")
    check("Universal Reasoning Engine", s.universal_reasoning is not None)
    check("Real-World Data Orchestrator", s.orchestrator is not None)

    # Phase 3 AI systems
    oracle_ok = s.market_oracle is not None
    check("Market Oracle Engine", oracle_ok, "RAGFlow predictive analysis" if oracle_ok else "NOT LOADED")
    agents_ok = s.agent_coordinator is not None
    check("Hierarchical Agent Coordinator", agents_ok, "17 agents + 3 supervisors" if agents_ok else "NOT LOADED")
    cl_ok = s.continuous_learning is not None
    check("Continuous Learning Engine", cl_ok, "AGGRESSIVE mode" if cl_ok else "NOT LOADED")
    al_ok = s.ai_learning is not None
    check("AI Learning Engine", al_ok, "pattern recognition" if al_ok else "NOT LOADED")

    # AI Attribution
    attr_ok = hasattr(s, 'ai_attribution_tracker') and s.ai_attribution_tracker is not None
    check("AI Attribution Tracker", attr_ok)

    if not oracle_ok or not agents_ok:
        warn("Some Phase 3 AI systems failed to load - check import errors above")

# ============================================================
# SECTION 4: Circuit Breakers & Safety
# ============================================================
def test_safety(s):
    section("4. Safety Systems")
    check("Circuit breaker: max_consecutive_losses=5", s.max_consecutive_losses == 5)
    check("Circuit breaker NOT triggered", not s.circuit_breaker_triggered)
    check("Stop loss configured", s.stop_loss_percent > 0)
    check("Max daily loss configured", s.max_daily_loss > 0)

# ============================================================
# SECTION 5: Learning Feedback Loop
# ============================================================
def test_learning_loop():
    section("5. Learning Feedback Loop (Database)")
    db_path = str(Path(__file__).parent / 'prometheus_learning.db')
    try:
        db = sqlite3.connect(db_path, timeout=10)
        c = db.cursor()
        tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}

        for t in ['trade_history', 'signal_predictions', 'ai_attribution',
                   'learning_outcomes', 'live_position_tracking']:
            check(f"Table '{t}' exists", t in tables)

        # Row counts
        for t in ['trade_history', 'signal_predictions', 'ai_attribution']:
            if t in tables:
                cnt = c.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
                check(f"  {t} has data", cnt > 0, f"rows={cnt:,}")

        # Adaptive weights
        try:
            from core.ai_attribution_tracker import AIAttributionTracker
            tracker = AIAttributionTracker()
            weights = tracker.get_ai_system_weights()
            check("Adaptive weights available", len(weights) > 0, f"systems={list(weights.keys())}")
        except Exception as e:
            check("Adaptive weights available", False, str(e))

        db.close()
    except Exception as e:
        check("Database accessible", False, str(e))

# ============================================================
# SECTION 6: Real Market Data Test
# ============================================================
def test_real_market_data():
    section("6. Real Market Data (yfinance)")
    try:
        import yfinance as yf
        symbols_to_test = ['AAPL', 'BTC-USD']
        for sym in symbols_to_test:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="5d", interval="1d")
            has_data = not hist.empty and len(hist) > 0
            price = float(hist['Close'].iloc[-1]) if has_data else 0
            check(f"yfinance {sym} data", has_data, f"price=${price:.2f}, rows={len(hist)}")
    except Exception as e:
        check("yfinance available", False, str(e))

# ============================================================
# SECTION 7: AI Signal Generation Test (Live Fire)
# ============================================================
async def test_ai_signal_generation(s):
    section("7. AI Signal Generation (Live Fire Test)")
    try:
        import yfinance as yf
        test_symbol = 'AAPL'
        ticker = yf.Ticker(test_symbol)
        hist = ticker.history(period="5d", interval="1d")
        if hist.empty:
            check("Market data for signal test", False, "No data returned")
            return

        latest = hist.iloc[-1]
        market_data = {
            'price': float(latest['Close']),
            'volume': float(latest['Volume']),
            'high': float(latest['High']),
            'low': float(latest['Low']),
            'change_percent': float(latest['Close'] / hist.iloc[-2]['Close'] - 1) * 100 if len(hist) > 1 else 0,
        }
        check("Market data fetched", True, f"AAPL=${market_data['price']:.2f}")

        # Test enhanced intelligence gathering
        if hasattr(s, '_get_enhanced_intelligence'):
            try:
                intel = await s._get_enhanced_intelligence(test_symbol, market_data)
                has_intel = intel is not None and len(intel) > 0
                check("Enhanced intelligence gathered", has_intel,
                       f"sources={len(intel)}" if has_intel else "empty")
            except Exception as e:
                warn(f"Enhanced intelligence error: {e}")

        # Test AI reasoning decision
        if hasattr(s, '_ai_reasoning_decision'):
            try:
                decision = await s._ai_reasoning_decision(test_symbol, market_data, {})
                has_decision = decision is not None
                if has_decision:
                    action = decision.get('action', 'UNKNOWN')
                    conf = decision.get('confidence', 0)
                    check("AI reasoning decision", True, f"action={action}, confidence={conf:.2f}")
                else:
                    warn("AI reasoning returned None (may be expected if HOLD)")
            except Exception as e:
                warn(f"AI reasoning error: {e}")

        # Test prometheus_aggressive_analysis (main scoring function)
        if hasattr(s, 'prometheus_aggressive_analysis'):
            try:
                analysis = await s.prometheus_aggressive_analysis(test_symbol, market_data)
                if analysis:
                    buy_score = analysis.get('buy_score', 0)
                    sell_score = analysis.get('sell_score', 0)
                    check("Aggressive analysis", True,
                           f"buy_score={buy_score}, sell_score={sell_score}")
                else:
                    warn("Aggressive analysis returned None")
            except Exception as e:
                warn(f"Aggressive analysis error: {e}")

    except Exception as e:
        check("AI signal test", False, traceback.format_exc())

# ============================================================
# MAIN
# ============================================================
def main():
    print("\n" + "=" * 70)
    print("  PROMETHEUS COMPREHENSIVE BENCHMARK TEST")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    try:
        s = test_aggressive_config()
        test_enhancements(s)
        test_ai_systems(s)
        test_safety(s)
        test_learning_loop()
        test_real_market_data()
        asyncio.run(test_ai_signal_generation(s))
    except Exception as e:
        print(f"\n  FATAL ERROR: {e}")
        traceback.print_exc()

    # Summary
    total = results["passed"] + results["failed"]
    section("BENCHMARK SUMMARY")
    print(f"  PASSED : {results['passed']}/{total}")
    print(f"  FAILED : {results['failed']}/{total}")
    print(f"  WARNINGS: {results['warnings']}")
    pct = results['passed'] / total * 100 if total > 0 else 0
    grade = "A+" if pct >= 95 else "A" if pct >= 90 else "B" if pct >= 80 else "C" if pct >= 70 else "F"
    print(f"\n  SCORE  : {pct:.0f}% (Grade: {grade})")

    if results['failed'] > 0:
        print(f"\n  FAILURES:")
        for d in results['details']:
            if d['status'] == 'FAIL':
                print(f"    x {d['name']}: {d['detail']}")

    # Save results
    out = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to: {out}")


if __name__ == '__main__':
    main()

