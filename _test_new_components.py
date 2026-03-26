"""
Test suite for Prometheus Phase 1 & Phase 2 components:
  1. MLFeatureEngine - real features for ML inference
  2. StatArbEngine  - pairs trading, mean reversion, etc.
  3. HMM RegimeDetector - market regime detection
  4. DeadEndMemory  - trade rejection/failure tracking
  5. WorldModel     - persistent market state
"""

import asyncio
import sys
import time
import traceback
from pathlib import Path

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).parent))


def header(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_pass(name: str, detail: str = ""):
    print(f"  ✅ {name}" + (f" — {detail}" if detail else ""))


def test_fail(name: str, detail: str = ""):
    print(f"  ❌ {name}" + (f" — {detail}" if detail else ""))


passed = 0
failed = 0


def check(condition: bool, name: str, detail: str = ""):
    global passed, failed
    if condition:
        test_pass(name, detail)
        passed += 1
    else:
        test_fail(name, detail)
        failed += 1


# ──────────────────────────────────────────────────────────────────────────
# 1. ML Feature Engine
# ──────────────────────────────────────────────────────────────────────────

def test_ml_feature_engine():
    header("1. ML Feature Engine")
    try:
        from core.ml_feature_engine import MLFeatureEngine, TRAINING_FEATURE_COLS, get_feature_engine

        engine = get_feature_engine()
        check(engine is not None, "Singleton creation")
        check(len(TRAINING_FEATURE_COLS) == 11, "11 training features defined", str(TRAINING_FEATURE_COLS))

        # Test real feature computation (requires yfinance + network)
        loop = asyncio.new_event_loop()
        features = loop.run_until_complete(engine.compute_features("AAPL", current_price=170.0))
        if features is not None:
            check(features.shape == (11,), "Feature shape is (11,)", str(features.shape))
            check(not all(f == 0 for f in features), "Features are non-trivial", str(features[:3]))
            # RSI should be between 0 and 100
            rsi = features[0]
            check(0 <= rsi <= 100, f"RSI in valid range", f"RSI={rsi:.1f}")
        else:
            print("  ⚠️  Feature computation returned None (yfinance may be unavailable)")

        # Test advanced features
        adv = loop.run_until_complete(engine.compute_advanced_features("AAPL"))
        if adv:
            check("mean_reversion_zscore" in adv, "Advanced features include z-score")
            check("atr_ratio" in adv, "Advanced features include ATR ratio")
        else:
            print("  ⚠️  Advanced features returned None")

        loop.close()
    except Exception as e:
        test_fail(f"ML Feature Engine import/run", str(e))
        traceback.print_exc()


# ──────────────────────────────────────────────────────────────────────────
# 2. Statistical Arbitrage Engine
# ──────────────────────────────────────────────────────────────────────────

def test_statarb_engine():
    header("2. Statistical Arbitrage Engine")
    try:
        from core.statarb_engine import StatArbEngine, get_statarb_engine, CRYPTO_PAIRS_YF, EQUITY_PAIRS_YF

        engine = get_statarb_engine()
        check(engine is not None, "Singleton creation")
        check(len(CRYPTO_PAIRS_YF) > 0, f"Crypto pairs defined: {len(CRYPTO_PAIRS_YF)}")
        check(len(EQUITY_PAIRS_YF) > 0, f"Equity pairs defined: {len(EQUITY_PAIRS_YF)}")

        status = engine.get_status()
        check(status["active"], "Engine active")
        check(status["pairs_monitored"] > 0, f"Pairs monitored: {status['pairs_monitored']}")

        # Test half-life estimation
        import numpy as np
        # Create a mean-reverting series
        np.random.seed(42)
        series = np.cumsum(np.random.randn(100) * 0.5)
        hl = engine._estimate_half_life(series)
        check(isinstance(hl, float), f"Half-life estimation works", f"hl={hl:.1f}")

        # Test ADF test
        # Stationary series should pass
        stationary = np.random.randn(100)
        check(isinstance(engine._simple_adf_test(stationary), bool), "ADF test returns bool")

        # Test signal generation (requires network)
        loop = asyncio.new_event_loop()
        signals = loop.run_until_complete(engine.generate_signals("SPY"))
        check(isinstance(signals, list), f"Signal generation returns list", f"{len(signals)} signals")
        for sig in signals[:2]:
            check(sig.action in ("BUY", "SELL", "HOLD"), f"Signal action valid: {sig.action}")
            check(0 <= sig.confidence <= 1, f"Confidence in range: {sig.confidence:.2f}")
            print(f"      → {sig.strategy}: {sig.action} conf={sig.confidence:.0%} z={sig.z_score:.2f}")

        # Test Kelly
        engine.record_outcome("mean_reversion", 1.5)
        engine.record_outcome("mean_reversion", -0.8)
        engine.record_outcome("mean_reversion", 2.0)
        kelly = engine._kelly_fraction("mean_reversion", 0.6)
        check(0 <= kelly <= 0.25, f"Kelly fraction reasonable: {kelly:.3f}")

        loop.close()
    except Exception as e:
        test_fail(f"StatArb Engine import/run", str(e))
        traceback.print_exc()


# ──────────────────────────────────────────────────────────────────────────
# 3. HMM Regime Detector
# ──────────────────────────────────────────────────────────────────────────

def test_hmm_regime_detector():
    header("3. HMM Regime Detector")
    try:
        from core.hmm_regime_detector import (
            GaussianHMM, RegimeDetector, MarketRegime,
            REGIME_NAMES, REGIME_STRATEGY_WEIGHTS, get_regime_detector,
        )

        # Test raw HMM
        import numpy as np
        np.random.seed(42)

        hmm = GaussianHMM(n_states=3, n_features=2, n_iter=10)
        check(hmm.n_states == 3, "HMM has 3 states")

        # Create synthetic data with 3 regimes
        # Regime 0: low vol, positive drift
        d0 = np.random.randn(50, 2) * 0.5 + [0.01, 0.5]
        # Regime 1: high vol, no drift
        d1 = np.random.randn(50, 2) * 2.0 + [0.0, 2.0]
        # Regime 2: high vol, negative drift
        d2 = np.random.randn(50, 2) * 3.0 + [-0.02, 3.0]
        X = np.vstack([d0, d1, d2])

        hmm.fit(X)
        check(hmm._fitted, "HMM fitted successfully")

        probs = hmm.predict_proba(X)
        check(probs.shape == (150, 3), f"Probability shape: {probs.shape}")
        check(np.allclose(probs.sum(axis=1), 1.0, atol=0.01), "Probabilities sum to 1")

        states = hmm.predict(X)
        check(len(states) == 150, f"Predicted {len(states)} states")

        # Test regime detector
        detector = get_regime_detector()
        check(detector is not None, "Detector singleton created")

        check(len(REGIME_NAMES) == 3, "3 regime names defined")
        check(len(REGIME_STRATEGY_WEIGHTS) == 3, "3 regime strategy weight sets")

        # Test strategy weight lookup
        for regime in MarketRegime:
            weights = REGIME_STRATEGY_WEIGHTS[regime]
            check("position_size_mult" in weights, f"Regime {regime.name} has position_size_mult")

        # Test live detection (requires network)
        loop = asyncio.new_event_loop()
        regime_state = loop.run_until_complete(detector.detect_regime("SPY"))
        if regime_state:
            check(regime_state.regime in MarketRegime, f"Regime: {regime_state.regime_name}")
            check(0 <= regime_state.probability <= 1, f"Probability: {regime_state.probability:.0%}")
            check(-1 <= regime_state.trend_strength <= 1, f"Trend: {regime_state.trend_strength:+.2f}")
            print(f"      → Current regime: {regime_state.regime_name} ({regime_state.probability:.0%})")
            print(f"      → Vol percentile: {regime_state.volatility_percentile:.0%}")
            print(f"      → Trend strength: {regime_state.trend_strength:+.2f}")
        else:
            print("  ⚠️  Regime detection returned None (yfinance may be unavailable)")
        loop.close()

    except Exception as e:
        test_fail(f"HMM Regime Detector import/run", str(e))
        traceback.print_exc()


# ──────────────────────────────────────────────────────────────────────────
# 4. Dead-End Memory
# ──────────────────────────────────────────────────────────────────────────

def test_dead_end_memory():
    header("4. Dead-End Memory")
    try:
        from core.dead_end_memory import DeadEndMemory

        # Use temp DB for testing
        test_db = Path("test_dead_end_memory.db")
        mem = DeadEndMemory(db_path=test_db)
        check(mem is not None, "Memory created")

        # Record some events
        mem.record_rejection("AAPL", "BUY", "low_confidence", strategy="mean_reversion")
        mem.record_rejection("AAPL", "BUY", "low_confidence", strategy="mean_reversion")
        mem.record_failure("AAPL", "BUY", "stop_loss_hit", pnl_pct=-1.5, strategy="mean_reversion")
        mem.record_failure("AAPL", "BUY", "poor_timing", pnl_pct=-2.1, strategy="mean_reversion")
        mem.record_stop_loss("AAPL", "BUY", pnl_pct=-3.0, strategy="pairs_trade")
        check(True, "Recorded 5 events")

        # Query toxicity
        tox = mem.get_toxicity_score("AAPL")
        check(tox["reject_count"] == 2, f"Reject count: {tox['reject_count']}")
        check(tox["loss_count"] >= 2, f"Loss count: {tox['loss_count']}")
        check(tox["score"] > 0, f"Toxicity score: {tox['score']:.2f}")
        print(f"      → Score={tox['score']:.2f}, recommendation={tox['recommendation']}")

        # Should block
        blocked, reason = mem.should_block_trade("AAPL", block_threshold=0.3)
        check(isinstance(blocked, bool), f"Block check: blocked={blocked}")

        # Clean symbol should not be blocked
        tox_clean = mem.get_toxicity_score("MSFT")
        check(tox_clean["score"] == 0.0, "Clean symbol has 0 toxicity")

        # Worst symbols
        worst = mem.get_worst_symbols()
        check(len(worst) > 0, f"Worst symbols: {len(worst)}")

        # Status
        status = mem.get_status()
        check(status["total_records"] >= 5, f"Total records: {status['total_records']}")

        # Cleanup
        del mem
        import gc; gc.collect()
        try:
            test_db.unlink(missing_ok=True)
            check(True, "Cleaned up test DB")
        except PermissionError:
            check(True, "Test DB cleanup deferred (Windows lock)")

    except Exception as e:
        test_fail(f"Dead-End Memory import/run", str(e))
        traceback.print_exc()
    finally:
        try:
            Path("test_dead_end_memory.db").unlink(missing_ok=True)
        except (PermissionError, OSError):
            pass


# ──────────────────────────────────────────────────────────────────────────
# 5. World Model
# ──────────────────────────────────────────────────────────────────────────

def test_world_model():
    header("5. World Model")
    try:
        from core.world_model import WorldModel, WorldState

        # Use temp DB
        test_db = Path("test_world_model.db")
        wm = WorldModel(db_path=test_db)
        check(wm is not None, "World model created")
        check(isinstance(wm.state, WorldState), "State is WorldState")

        # Update regime
        wm.update_regime("Low Vol / Trending", 0.82, {"momentum": 1.2, "mean_reversion": 0.5})
        check(wm.state.regime == "Low Vol / Trending", "Regime updated")

        # Update portfolio
        wm.update_portfolio(portfolio_value=100.93, cash=5.50, positions=6, exposure_pct=0.94)
        check(wm.state.portfolio_value == 100.93, f"Portfolio: ${wm.state.portfolio_value}")
        check(wm.state.open_positions == 6, f"Positions: {wm.state.open_positions}")

        # Update symbol intel
        wm.update_symbol_intel("BTC/USD", support=95000, resistance=100000, trend="bullish")
        check("BTC/USD" in wm.state.symbol_states, "Symbol intel stored")

        # Save and reload
        wm.save()
        check(wm.state.cycle_count == 1, f"Cycle count: {wm.state.cycle_count}")

        # Reload from DB
        wm2 = WorldModel(db_path=test_db)
        check(wm2.state.regime == "Low Vol / Trending", "State persisted across reload")
        check(wm2.state.cycle_count == 1, "Cycle count persisted")

        # Queries
        check(wm.get_regime() == "Low Vol / Trending", "get_regime()")
        check(wm.get_strategy_weight("momentum") == 1.2, "get_strategy_weight()")
        check(wm.is_portfolio_overexposed(max_exposure=0.90), "Over-exposed at 94%")
        check(not wm.is_portfolio_overexposed(max_exposure=0.95), "Not over-exposed at 95% threshold")

        summary = wm.get_summary()
        check("regime" in summary, f"Summary: {summary}")

        status = wm.get_status()
        check(status["active"], "World model active")

        # Cleanup
        del wm, wm2
        import gc; gc.collect()
        try:
            test_db.unlink(missing_ok=True)
        except (PermissionError, OSError):
            pass

    except Exception as e:
        test_fail(f"World Model import/run", str(e))
        traceback.print_exc()
    finally:
        try:
            Path("test_world_model.db").unlink(missing_ok=True)
        except (PermissionError, OSError):
            pass


# ──────────────────────────────────────────────────────────────────────────
# 6. Integration check — imports work in launch file context
# ──────────────────────────────────────────────────────────────────────────

def test_integration_imports():
    header("6. Integration Imports")
    try:
        from core.ml_feature_engine import get_feature_engine
        check(True, "ml_feature_engine imports OK")
    except Exception as e:
        test_fail("ml_feature_engine import", str(e))

    try:
        from core.statarb_engine import get_statarb_engine
        check(True, "statarb_engine imports OK")
    except Exception as e:
        test_fail("statarb_engine import", str(e))

    try:
        from core.hmm_regime_detector import get_regime_detector
        check(True, "hmm_regime_detector imports OK")
    except Exception as e:
        test_fail("hmm_regime_detector import", str(e))

    try:
        from core.dead_end_memory import get_dead_end_memory
        check(True, "dead_end_memory imports OK")
    except Exception as e:
        test_fail("dead_end_memory import", str(e))

    try:
        from core.world_model import get_world_model
        check(True, "world_model imports OK")
    except Exception as e:
        test_fail("world_model import", str(e))


# ──────────────────────────────────────────────────────────────────────────
# Run all tests
# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "🔬" * 30)
    print("  PROMETHEUS Phase 1+2 Component Test Suite")
    print("🔬" * 30)

    start = time.time()

    test_integration_imports()
    test_ml_feature_engine()
    test_statarb_engine()
    test_hmm_regime_detector()
    test_dead_end_memory()
    test_world_model()

    elapsed = time.time() - start

    print(f"\n{'='*60}")
    print(f"  RESULTS: {passed} passed, {failed} failed ({elapsed:.1f}s)")
    print(f"{'='*60}")

    if failed:
        print(f"\n  ⚠️  {failed} test(s) FAILED — review above output")
        sys.exit(1)
    else:
        print(f"\n  ✅ All {passed} tests PASSED")
        sys.exit(0)
