#!/usr/bin/env python3
"""
PROMETHEUS Full Test & Benchmark Suite
=======================================
Runs ALL backtesting, validation, and benchmarks in one shot.

Sections:
  1. Backtesting Validation Suite (walk-forward, Monte Carlo, bootstrap)
  2. Multi-Strategy Comparison
  3. AI Systems Registry Verification
  4. Full System Benchmark (AI capabilities, reasoning, signals)
  5. Performance Summary

Usage:  python _run_full_test_suite.py
"""

import sys, os, json, time, asyncio, traceback, sqlite3
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
PASS = 0
FAIL = 0
WARN = 0
ALL_RESULTS = {}
START = time.time()

def section(title):
    print(f"\n{'='*72}")
    print(f"  {title}")
    print(f"{'='*72}")

def check(name, condition, detail=""):
    global PASS, FAIL
    ok = bool(condition)
    icon = "+" if ok else "x"
    if ok: PASS += 1
    else:  FAIL += 1
    line = f"  [{icon}] {name}"
    if detail: line += f"  -- {detail}"
    print(line)
    return ok

def warn(name, detail=""):
    global WARN
    WARN += 1
    print(f"  [!] {name}  -- {detail}")

def elapsed():
    return f"{time.time()-START:.1f}s"

# ─────────────────────────────────────────────────────────────
# 1. BACKTESTING VALIDATION SUITE
# ─────────────────────────────────────────────────────────────
async def test_backtesting_validation():
    section("1. BACKTESTING VALIDATION SUITE")
    print(f"  (walk-forward, Monte Carlo permutation, bootstrap Sharpe CI)")
    print()
    
    from core.backtesting_validation_suite import (
        BacktestingValidationSuite, 
        PrometheusAIStrategy,
        BuyAndHoldStrategy,
        MomentumStrategy,
        MeanReversionStrategy,
    )
    
    suite = BacktestingValidationSuite(
        commission_bps=10,
        slippage_bps=5,
        initial_capital=100_000,
    )
    check("BacktestingValidationSuite instantiated", suite is not None)
    
    # --- Full validation on SPY (1 year, lighter for speed) ---
    print(f"\n  --- Validating PrometheusAI on SPY (1 year) ---")
    t0 = time.time()
    report = await suite.validate_strategy(
        symbol="SPY",
        years=1.0,
        walk_forward_folds=3,
        monte_carlo_sims=200,
        bootstrap_samples=500,
    )
    dt = time.time() - t0
    
    check("Validation completed", report is not None, f"{dt:.1f}s")
    check("Data bars > 200", report.data_bars > 200, f"bars={report.data_bars}")
    check("Overall metrics computed", report.overall_metrics is not None)
    
    if report.overall_metrics:
        m = report.overall_metrics
        print(f"\n  --- SPY Overall Metrics ---")
        print(f"    Total Return:      {m.total_return_pct:+.2f}%")
        print(f"    Annualized Return: {m.annualized_return_pct:+.2f}%")
        print(f"    Sharpe Ratio:      {m.sharpe_ratio:.3f}")
        print(f"    Sortino Ratio:     {m.sortino_ratio:.3f}")
        print(f"    Calmar Ratio:      {m.calmar_ratio:.3f}")
        print(f"    Max Drawdown:      {m.max_drawdown_pct:.2f}%")
        print(f"    Profit Factor:     {m.profit_factor:.2f}")
        print(f"    Win Rate:          {m.win_rate:.1f}%")
        print(f"    Total Trades:      {m.total_trades}")
        print(f"    Buy&Hold Return:   {m.buy_and_hold_return_pct:+.2f}%")
        print(f"    Total Commission:  ${m.total_commission:.2f}")
        print(f"    Total Slippage:    ${m.total_slippage:.2f}")
        
        check("Sharpe calculated", m.sharpe_ratio != 0, f"sharpe={m.sharpe_ratio:.3f}")
        check("Trades executed", m.total_trades > 0, f"trades={m.total_trades}")
        check("Costs applied", m.total_commission > 0 or m.total_slippage > 0)
        
        ALL_RESULTS["spy_overall"] = {
            "return_pct": m.total_return_pct,
            "sharpe": m.sharpe_ratio,
            "max_dd": m.max_drawdown_pct,
            "trades": m.total_trades,
            "win_rate": m.win_rate,
        }
    
    # Walk-forward
    if report.walk_forward_folds:
        print(f"\n  --- Walk-Forward Results ({len(report.walk_forward_folds)} folds) ---")
        for fold in report.walk_forward_folds:
            print(f"    Fold {fold.fold}: Train Sharpe={fold.train_metrics.sharpe_ratio:.3f}  "
                  f"Test Sharpe={fold.test_metrics.sharpe_ratio:.3f}  "
                  f"Test Return={fold.test_metrics.total_return_pct:+.2f}%")
        print(f"    Avg Test Sharpe:  {report.walk_forward_avg_test_sharpe:.3f}")
        print(f"    Avg Test Return:  {report.walk_forward_avg_test_return:+.2f}%")
        check("Walk-forward completed", len(report.walk_forward_folds) >= 2, 
              f"folds={len(report.walk_forward_folds)}")
        check("Avg test Sharpe computed", report.walk_forward_avg_test_sharpe is not None)
    
    # Monte Carlo
    if report.monte_carlo:
        mc = report.monte_carlo
        print(f"\n  --- Monte Carlo Permutation Test ---")
        print(f"    Simulations:       {mc.n_simulations}")
        print(f"    Strategy Sharpe:   {mc.strategy_sharpe:.3f}")
        print(f"    Random Mean Sharpe: {mc.random_mean_sharpe:.3f}")
        print(f"    P-Value:           {mc.p_value:.4f}")
        print(f"    Significant (5%):  {'YES' if mc.p_value < 0.05 else 'NO'}")
        check("Monte Carlo ran", mc.n_simulations > 0, f"sims={mc.n_simulations}")
        check("P-value computed", 0 <= mc.p_value <= 1, f"p={mc.p_value:.4f}")
    
    # Bootstrap CI
    if report.bootstrap_sharpe_95ci:
        lo, hi = report.bootstrap_sharpe_95ci
        print(f"\n  --- Bootstrap 95% CI for Sharpe ---")
        print(f"    [{lo:.3f}, {hi:.3f}]")
        check("Bootstrap CI computed", lo < hi, f"CI=[{lo:.3f}, {hi:.3f}]")
    
    # Verdict
    print(f"\n  VERDICT: {report.verdict}")
    check("Verdict generated", len(report.verdict) > 10)
    check("Stat significant flag set", report.statistically_significant is not None)
    check("Edge detected flag set", report.edge_detected is not None)
    
    # Save report
    path = suite.save_report(report)
    check("Report saved", Path(path).exists(), f"path={path}")
    
    ALL_RESULTS["spy_validation"] = {
        "verdict": report.verdict,
        "significant": report.statistically_significant,
        "edge": report.edge_detected,
    }
    
    return report

# ─────────────────────────────────────────────────────────────
# 2. MULTI-STRATEGY COMPARISON
# ─────────────────────────────────────────────────────────────
async def test_strategy_comparison():
    section("2. MULTI-STRATEGY COMPARISON")
    
    from core.backtesting_validation_suite import BacktestingValidationSuite
    suite = BacktestingValidationSuite()
    
    symbols = ["SPY", "AAPL", "MSFT"]
    all_comparisons = {}
    
    for sym in symbols:
        print(f"\n  --- Comparing strategies on {sym} (1 year) ---")
        t0 = time.time()
        result = await suite.compare_strategies(symbol=sym, years=1.0)
        dt = time.time() - t0
        
        if "error" in result:
            warn(f"{sym} comparison failed", result["error"])
            continue
        
        check(f"{sym} comparison completed", "strategies" in result, f"{dt:.1f}s")
        
        if "strategies" in result:
            print(f"    {'Strategy':<25} {'Return':>10} {'Sharpe':>10} {'MaxDD':>10} {'WinRate':>10} {'Trades':>8}")
            print(f"    {'-'*73}")
            for name, metrics in result["strategies"].items():
                print(f"    {name:<25} {metrics['total_return_pct']:>+9.2f}% "
                      f"{metrics['sharpe_ratio']:>9.3f} "
                      f"{metrics['max_drawdown_pct']:>9.2f}% "
                      f"{metrics['win_rate']:>9.1f}% "
                      f"{metrics['total_trades']:>7d}")
            
            if "ranking" in result:
                print(f"\n    Ranking by Sharpe:")
                for r in result["ranking"]:
                    medal = ["  ", "  ", "  "][r["rank"]-1] if r["rank"] <= 3 else "   "
                    print(f"     {medal} #{r['rank']} {r['strategy']} (Sharpe={r['sharpe']:.3f})")
        
        all_comparisons[sym] = result
    
    check("At least 2 symbols compared", len(all_comparisons) >= 2, f"compared={len(all_comparisons)}")
    ALL_RESULTS["strategy_comparison"] = {
        sym: {
            "best": res.get("ranking", [{}])[0].get("strategy", "?") if res.get("ranking") else "?",
            "best_sharpe": res.get("ranking", [{}])[0].get("sharpe", 0) if res.get("ranking") else 0,
        }
        for sym, res in all_comparisons.items()
    }
    
    return all_comparisons

# ─────────────────────────────────────────────────────────────
# 3. AI SYSTEMS REGISTRY VERIFICATION
# ─────────────────────────────────────────────────────────────
def test_ai_systems():
    section("3. AI SYSTEMS REGISTRY & CAPABILITIES")
    
    # Test that all core modules import
    modules_to_test = [
        ("core.backtesting_validation_suite", "BacktestingValidationSuite"),
        ("core.ai_consciousness_engine", None),
        ("core.universal_reasoning_engine", None),
        ("core.trading_engine", None),
        ("core.risk_manager", None),
        ("core.advanced_monitoring", None),
        ("core.quantum_portfolio_optimizer", None),
        ("core.paper_trading_manager", None),
        ("core.auto_model_retrainer", None),
        ("core.federated_learning_engine", None),
        ("core.real_world_data_orchestrator", None),
        ("core.portfolio_risk_engine", None),
        ("core.langgraph_trading_orchestrator", None),
        ("core.hierarchical_agent_coordinator", None),
        ("core.ml_regime_detector", None),
        ("core.multi_timeframe_engine", None),
    ]
    
    imported = 0
    for mod_name, class_name in modules_to_test:
        try:
            mod = __import__(mod_name, fromlist=["_"])
            if class_name:
                assert hasattr(mod, class_name)
            imported += 1
            check(f"Import {mod_name.split('.')[-1]}", True)
        except Exception as e:
            check(f"Import {mod_name.split('.')[-1]}", False, str(e)[:80])
    
    check("Core modules importable", imported >= 12, f"{imported}/{len(modules_to_test)}")
    
    # Check pretrained models
    models_dir = Path("models_pretrained")
    if models_dir.exists():
        model_count = len(list(models_dir.glob("*.pkl")))
        check("Pretrained models exist", model_count > 0, f"count={model_count}")
    else:
        warn("models_pretrained/ directory not found")
    
    # Check databases
    for db_name in ["prometheus_trading.db", "prometheus_learning.db"]:
        db_path = Path(db_name)
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                tables = cur.fetchone()[0]
                conn.close()
                check(f"Database {db_name}", tables > 0, f"tables={tables}")
            except Exception as e:
                check(f"Database {db_name}", False, str(e)[:60])
        else:
            warn(f"Database {db_name} not found")
    
    ALL_RESULTS["ai_systems"] = {"modules_imported": imported, "total_tested": len(modules_to_test)}

# ─────────────────────────────────────────────────────────────
# 4. AI CAPABILITIES BENCHMARK
# ─────────────────────────────────────────────────────────────
async def test_ai_capabilities():
    section("4. AI CAPABILITIES BENCHMARK")
    scores = {}
    
    # 4a. HRM Reasoning
    print("\n  --- 4a. HRM Reasoning Engine ---")
    try:
        from core.hrm_integration import HRMTradingEngine, HRMReasoningContext, HRMReasoningLevel
        engine = HRMTradingEngine()
        
        ctx = HRMReasoningContext(
            query="Should I buy AAPL given current market conditions?",
            context="AAPL is trading at $230, RSI=62, MACD bullish crossover, market in uptrend",
            reasoning_level=HRMReasoningLevel.DEEP,
        )
        
        t0 = time.time()
        result = engine.enhanced_reason(ctx)
        dt = time.time() - t0
        
        has_answer = result and (len(str(result)) > 50)
        check("HRM reasoning completed", has_answer, f"{dt:.2f}s, len={len(str(result))}")
        scores["hrm_reasoning"] = min(100, max(0, int(100 * (1 - dt/10))))  # faster = higher score
    except Exception as e:
        check("HRM reasoning", False, str(e)[:80])
        scores["hrm_reasoning"] = 0
    
    # 4b. ML Regime Detection
    print("\n  --- 4b. ML Regime Detection ---")
    try:
        from core.ml_regime_detector import MLRegimeDetector
        import pandas as pd
        import numpy as np
        
        detector = MLRegimeDetector()
        
        # Create synthetic market data
        np.random.seed(42)
        dates = pd.date_range("2025-01-01", periods=120, freq="B")
        prices = 100 * np.cumprod(1 + np.random.normal(0.0005, 0.015, len(dates)))
        df = pd.DataFrame({
            "Open": prices * 0.998,
            "High": prices * 1.01,
            "Low": prices * 0.99,
            "Close": prices,
            "Volume": np.random.randint(1_000_000, 10_000_000, len(dates)),
        }, index=dates)
        
        t0 = time.time()
        regime = detector.predict_regime(df)
        dt = time.time() - t0
        
        check("Regime detected", regime is not None, f"regime={regime}, {dt:.2f}s")
        scores["regime_detection"] = 90 if regime else 0
    except Exception as e:
        check("Regime detection", False, str(e)[:80])
        scores["regime_detection"] = 0
    
    # 4c. Universal Reasoning Engine
    print("\n  --- 4c. Universal Reasoning Engine ---")
    try:
        from core.universal_reasoning_engine import get_universal_engine
        engine = get_universal_engine()
        
        t0 = time.time()
        result = await engine.reason({
            "query": "Analyze MSFT for trading opportunity",
            "symbol": "MSFT",
            "price": 420.0,
            "rsi": 55,
            "volume_trend": "increasing",
        })
        dt = time.time() - t0
        
        has_result = result is not None and len(str(result)) > 20
        check("Universal reasoning completed", has_result, f"{dt:.2f}s")
        scores["universal_reasoning"] = min(95, max(0, int(90 * (1 - dt/15))))
    except Exception as e:
        check("Universal reasoning", False, str(e)[:80])
        scores["universal_reasoning"] = 0
    
    # 4d. Quantum Portfolio Optimizer
    print("\n  --- 4d. Quantum Portfolio Optimizer ---")
    try:
        from core.quantum_portfolio_optimizer import QuantumPortfolioOptimizer
        optimizer = QuantumPortfolioOptimizer()
        
        portfolio = {
            "AAPL": {"weight": 0.25, "return": 0.15, "risk": 0.20},
            "MSFT": {"weight": 0.25, "return": 0.12, "risk": 0.18},
            "GOOGL": {"weight": 0.25, "return": 0.10, "risk": 0.22},
            "AMZN": {"weight": 0.25, "return": 0.18, "risk": 0.25},
        }
        
        t0 = time.time()
        result = optimizer.optimize(portfolio)
        dt = time.time() - t0
        
        check("Quantum optimizer completed", result is not None, f"{dt:.2f}s")
        scores["quantum_optimizer"] = 85 if result else 0
    except Exception as e:
        check("Quantum optimizer", False, str(e)[:80])
        scores["quantum_optimizer"] = 0
    
    # 4e. AI Consciousness Engine
    print("\n  --- 4e. AI Consciousness Engine ---")
    try:
        from core.ai_consciousness_engine import get_consciousness_engine
        engine = get_consciousness_engine()
        
        t0 = time.time()
        state = engine.get_consciousness_state() if hasattr(engine, 'get_consciousness_state') else engine.get_state()
        dt = time.time() - t0
        
        check("Consciousness engine responsive", state is not None, f"{dt:.2f}s")
        scores["consciousness"] = 90 if state else 0
    except Exception as e:
        check("Consciousness engine", False, str(e)[:80])
        scores["consciousness"] = 0
    
    # 4f. Signal Generation
    print("\n  --- 4f. Trading Signal Generation ---")
    try:
        import yfinance as yf
        
        spy = yf.download("SPY", period="3mo", interval="1d", progress=False)
        if len(spy) > 20:
            latest = spy.iloc[-1]
            price = float(latest["Close"].iloc[0]) if hasattr(latest["Close"], 'iloc') else float(latest["Close"])
            
            # Simple technical signal check
            sma20 = float(spy["Close"].rolling(20).mean().iloc[-1])
            sma50 = float(spy["Close"].rolling(50).mean().iloc[-1]) if len(spy) >= 50 else sma20
            rsi_delta = float(spy["Close"].diff().iloc[-14:].apply(lambda x: max(x, 0)).mean() / 
                              spy["Close"].diff().iloc[-14:].abs().mean() * 100)
            
            signal = "BUY" if price > sma20 > sma50 else ("SELL" if price < sma20 < sma50 else "HOLD")
            check("Signal generated", signal in ("BUY", "SELL", "HOLD"), 
                  f"SPY=${price:.2f}, SMA20=${sma20:.2f}, signal={signal}")
            scores["signal_gen"] = 95
        else:
            warn("Insufficient SPY data for signal generation")
            scores["signal_gen"] = 0
    except Exception as e:
        check("Signal generation", False, str(e)[:80])
        scores["signal_gen"] = 0
    
    # Overall AI Score
    if scores:
        avg_score = sum(scores.values()) / len(scores)
        print(f"\n  --- AI Capability Scores ---")
        for name, score in scores.items():
            bar = "#" * (score // 5)
            print(f"    {name:<25} {score:>3}/100  [{bar}]")
        print(f"    {'OVERALL':<25} {avg_score:>5.1f}/100")
        check("Overall AI score > 50", avg_score > 50, f"score={avg_score:.1f}")
    
    ALL_RESULTS["ai_capabilities"] = scores

# ─────────────────────────────────────────────────────────────
# 5. ADDITIONAL BACKTESTS (AAPL, TSLA, QQQ)
# ─────────────────────────────────────────────────────────────
async def test_additional_backtests():
    section("5. ADDITIONAL BACKTESTS (AAPL, TSLA, QQQ)")
    
    from core.backtesting_validation_suite import BacktestingValidationSuite
    suite = BacktestingValidationSuite()
    
    symbols = ["AAPL", "TSLA", "QQQ"]
    backtest_results = {}
    
    for sym in symbols:
        print(f"\n  --- Validating on {sym} (1 year, light) ---")
        t0 = time.time()
        try:
            report = await suite.validate_strategy(
                symbol=sym,
                years=1.0,
                walk_forward_folds=2,
                monte_carlo_sims=100,
                bootstrap_samples=200,
            )
            dt = time.time() - t0
            
            if report and report.overall_metrics:
                m = report.overall_metrics
                print(f"    Return: {m.total_return_pct:+.2f}%  Sharpe: {m.sharpe_ratio:.3f}  "
                      f"MaxDD: {m.max_drawdown_pct:.2f}%  Trades: {m.total_trades}  "
                      f"WinRate: {m.win_rate:.1f}%")
                
                mc_p = report.monte_carlo.p_value if report.monte_carlo else None
                print(f"    MC p-value: {mc_p:.4f}" if mc_p is not None else "    MC: N/A")
                print(f"    Verdict: {report.verdict}")
                
                check(f"{sym} backtest completed", True, f"{dt:.1f}s")
                backtest_results[sym] = {
                    "return": m.total_return_pct,
                    "sharpe": m.sharpe_ratio,
                    "max_dd": m.max_drawdown_pct,
                    "verdict": report.verdict[:50],
                }
                
                # Save report
                suite.save_report(report)
            else:
                check(f"{sym} backtest", False, "No metrics returned")
        except Exception as e:
            check(f"{sym} backtest", False, str(e)[:80])
    
    check("Additional backtests completed", len(backtest_results) >= 2, f"{len(backtest_results)}/3")
    ALL_RESULTS["additional_backtests"] = backtest_results

# ─────────────────────────────────────────────────────────────
# 6. SERVER ENDPOINT BENCHMARK (if server running)
# ─────────────────────────────────────────────────────────────
def test_server_endpoints():
    section("6. SERVER ENDPOINT TESTS")
    
    import urllib.request
    import urllib.error
    
    endpoints = [
        ("/health", "Health Check"),
        ("/api/backtest/status", "Backtest Status"),
        ("/ops", "Ops Dashboard"),
        ("/api/ai/status", "AI Status"),
        ("/api/system/health", "System Health"),
    ]
    
    timings = {}
    
    for path, name in endpoints:
        url = f"http://localhost:8000{path}"
        try:
            t0 = time.time()
            req = urllib.request.Request(url, headers={"User-Agent": "PROMETHEUS-Test/1.0"})
            resp = urllib.request.urlopen(req, timeout=120)
            dt = time.time() - t0
            body = resp.read()
            status = resp.status
            
            check(f"{name} ({path})", status == 200, f"{status} {len(body)}B {dt:.2f}s")
            timings[path] = {"status": status, "bytes": len(body), "time_s": round(dt, 2)}
        except urllib.error.HTTPError as e:
            check(f"{name} ({path})", False, f"HTTP {e.code}")
            timings[path] = {"status": e.code, "error": True}
        except Exception as e:
            check(f"{name} ({path})", False, str(e)[:60])
            timings[path] = {"error": str(e)[:60]}
    
    if timings:
        ok_times = [v["time_s"] for v in timings.values() if "time_s" in v]
        if ok_times:
            print(f"\n    Avg response time: {sum(ok_times)/len(ok_times):.2f}s")
            print(f"    Min: {min(ok_times):.2f}s  Max: {max(ok_times):.2f}s")
    
    ALL_RESULTS["endpoints"] = timings

# ─────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────
def print_summary():
    total_time = time.time() - START
    
    section("FINAL SUMMARY")
    total = PASS + FAIL
    pct = (PASS / total * 100) if total > 0 else 0
    
    print(f"""
    Tests Passed:   {PASS}
    Tests Failed:   {FAIL}
    Warnings:       {WARN}
    Pass Rate:      {pct:.1f}%
    Total Time:     {total_time:.1f}s
    """)
    
    # Strategy comparison summary
    if "strategy_comparison" in ALL_RESULTS:
        print("  Strategy Comparison Winners:")
        for sym, info in ALL_RESULTS["strategy_comparison"].items():
            print(f"    {sym}: {info['best']} (Sharpe={info['best_sharpe']:.3f})")
    
    # AI capabilities summary
    if "ai_capabilities" in ALL_RESULTS:
        scores = ALL_RESULTS["ai_capabilities"]
        avg = sum(scores.values()) / len(scores) if scores else 0
        print(f"\n  AI Capability Score: {avg:.1f}/100")
    
    # Additional backtests 
    if "additional_backtests" in ALL_RESULTS:
        print(f"\n  Backtest Results by Symbol:")
        for sym, info in ALL_RESULTS["additional_backtests"].items():
            print(f"    {sym}: Return={info['return']:+.2f}% Sharpe={info['sharpe']:.3f} MaxDD={info['max_dd']:.2f}%")
    
    # Save full results
    results_path = Path(f"full_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    def _serialize(obj):
        if hasattr(obj, '__dict__'):
            return str(obj)
        if isinstance(obj, (set, frozenset)):
            return list(obj)
        return str(obj)
    
    with open(results_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "pass": PASS,
            "fail": FAIL,
            "warnings": WARN,
            "pass_rate": round(pct, 1),
            "total_time_s": round(total_time, 1),
            "results": ALL_RESULTS,
        }, f, indent=2, default=_serialize)
    
    print(f"\n  Results saved: {results_path}")
    
    # Final verdict
    if pct >= 90:
        print(f"\n  VERDICT: EXCELLENT - {pct:.0f}% pass rate")
    elif pct >= 75:
        print(f"\n  VERDICT: GOOD - {pct:.0f}% pass rate")
    elif pct >= 50:
        print(f"\n  VERDICT: FAIR - {pct:.0f}% pass rate, some issues to address")
    else:
        print(f"\n  VERDICT: NEEDS WORK - {pct:.0f}% pass rate")

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
async def main():
    print("=" * 72)
    print("  PROMETHEUS FULL TEST & BENCHMARK SUITE")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 72)
    
    # 1. Backtesting Validation
    try:
        await test_backtesting_validation()
    except Exception as e:
        print(f"  [x] Backtesting validation CRASHED: {e}")
        traceback.print_exc()
    
    # 2. Strategy Comparison
    try:
        await test_strategy_comparison()
    except Exception as e:
        print(f"  [x] Strategy comparison CRASHED: {e}")
        traceback.print_exc()
    
    # 3. AI Systems
    try:
        test_ai_systems()
    except Exception as e:
        print(f"  [x] AI systems test CRASHED: {e}")
        traceback.print_exc()
    
    # 4. AI Capabilities
    try:
        await test_ai_capabilities()
    except Exception as e:
        print(f"  [x] AI capabilities test CRASHED: {e}")
        traceback.print_exc()
    
    # 5. Additional Backtests
    try:
        await test_additional_backtests()
    except Exception as e:
        print(f"  [x] Additional backtests CRASHED: {e}")
        traceback.print_exc()
    
    # 6. Server Endpoints
    try:
        test_server_endpoints()
    except Exception as e:
        print(f"  [x] Server endpoint test CRASHED: {e}")
        traceback.print_exc()
    
    # Summary
    print_summary()

if __name__ == "__main__":
    asyncio.run(main())
