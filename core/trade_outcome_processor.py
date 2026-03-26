"""
Trade Outcome Processor — Central Hub for Post-Trade Learning
=============================================================
Wires together:
  1. RL Agent feedback (learn_from_outcome)
  2. Continuous Learning Engine (record_trading_outcome)
  3. Regime-aware context for future signals

Called after every completed trade so all AI subsystems learn from real outcomes.
"""

import logging
import asyncio
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy singletons — avoid importing heavy libs at module level
# ---------------------------------------------------------------------------

_rl_system = None
_continuous_learner = None
_regime_forecaster = None


def _get_rl_system():
    """Lazy-load the full ReinforcementLearningTrading wrapper (not just the raw agent)."""
    global _rl_system
    if _rl_system is None:
        try:
            from core.reinforcement_learning_trading import ReinforcementLearningTrading
            rl = ReinforcementLearningTrading(state_dim=50)
            model_path = "trained_models/rl_trading_agent.pt"
            if Path(model_path).exists():
                rl.load_model(model_path)
                logger.info("RL Trading System loaded with pretrained checkpoint")
            else:
                logger.info("RL Trading System initialized (no checkpoint — will learn from scratch)")
            _rl_system = rl
        except Exception as e:
            logger.warning(f"RL system unavailable: {e}")
    return _rl_system


def _get_continuous_learner():
    """Lazy-load ContinuousLearningEngine."""
    global _continuous_learner
    if _continuous_learner is None:
        try:
            from core.continuous_learning_engine import ContinuousLearningEngine, LearningMode
            _continuous_learner = ContinuousLearningEngine(learning_mode=LearningMode.BALANCED)
            logger.info("Continuous Learning Engine wired into trade outcome processor")
        except Exception as e:
            logger.warning(f"Continuous learning engine unavailable: {e}")
    return _continuous_learner


def _get_regime_forecaster():
    """Lazy-load MarketRegimeForecaster."""
    global _regime_forecaster
    if _regime_forecaster is None:
        try:
            from core.regime_forecasting import MarketRegimeForecaster
            _regime_forecaster = MarketRegimeForecaster()
            logger.info("Regime Forecaster wired into trade outcome processor")
        except Exception as e:
            logger.warning(f"Regime forecaster unavailable: {e}")
    return _regime_forecaster


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_rl_save_counter = 0


async def process_trade_outcome(
    symbol: str,
    side: str,            # 'buy' or 'sell'
    quantity: float,
    entry_price: float,
    exit_price: Optional[float],
    realized_pnl: float,
    unrealized_pnl: float,
    execution_mode: str,  # 'paper' or 'live'
    user_id: str = "",
    extra_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Central post-trade learning hook.
    Called after every trade execution to feed ALL learning subsystems.

    Returns a summary dict of what each subsystem did.
    """
    global _rl_save_counter
    results: Dict[str, Any] = {}
    extra_context = extra_context or {}

    # ------------------------------------------------------------------
    # 1. Feed RL Agent
    # ------------------------------------------------------------------
    try:
        rl = _get_rl_system()
        if rl is not None:
            # Build market_data dict from what we know
            market_data = {
                "price": exit_price or entry_price,
                "volume": extra_context.get("volume", 0),
                "indicators": extra_context.get("indicators", {
                    "rsi": extra_context.get("rsi", 50),
                    "macd": extra_context.get("macd", 0),
                    "volatility": extra_context.get("volatility", 0.02),
                }),
            }
            portfolio = {
                "total_value": extra_context.get("portfolio_value", 100000),
                "positions": extra_context.get("positions_count", 1),
            }
            context = {"symbol": symbol, "execution_mode": execution_mode}

            # Encode current state
            state = rl.encode_state(market_data, portfolio, context)

            # Build outcome
            action = "BUY" if side.lower() == "buy" else "SELL"
            outcome = {
                "profit": max(realized_pnl, 0),
                "loss": abs(min(realized_pnl, 0)),
                "success": realized_pnl > 0,
            }

            # Next state = same state (single-step, not episodic)
            next_state = state.copy()

            # Learn
            rl.learn_from_outcome(state, action, outcome, next_state, done=False)
            results["rl_agent"] = {
                "status": "learned",
                "buffer_size": len(rl.replay_buffer),
                "reward": rl.calculate_reward(action, outcome),
            }

            # Auto-save every 20 learning steps
            _rl_save_counter += 1
            if _rl_save_counter % 20 == 0:
                try:
                    rl.save_model("trained_models/rl_trading_agent.pt")
                    results["rl_agent"]["saved"] = True
                except Exception as save_err:
                    logger.warning(f"RL checkpoint save failed: {save_err}")
    except Exception as e:
        logger.warning(f"RL feedback failed (non-critical): {e}")
        results["rl_agent"] = {"status": "error", "error": str(e)}

    # ------------------------------------------------------------------
    # 2. Feed Continuous Learning Engine
    # ------------------------------------------------------------------
    try:
        cl = _get_continuous_learner()
        if cl is not None:
            from core.continuous_learning_engine import TradingOutcome
            duration = extra_context.get("hold_duration_seconds", 0)
            outcome_obj = TradingOutcome(
                trade_id=extra_context.get("trade_id", f"trade_{datetime.now().strftime('%Y%m%d%H%M%S')}"),
                timestamp=datetime.utcnow(),
                symbol=symbol,
                action=side,
                entry_price=entry_price,
                exit_price=exit_price,
                quantity=quantity,
                profit_loss=realized_pnl,
                duration=timedelta(seconds=duration),
                market_conditions=extra_context.get("market_conditions", {}),
                model_confidence=extra_context.get("confidence", 0.5),
                model_version=extra_context.get("model_version", "v1"),
                features_used=extra_context.get("features_used", {}),
                risk_metrics=extra_context.get("risk_metrics", {"risk_factor": 1.0, "max_risk": 1000.0}),
            )
            await cl.record_trading_outcome(outcome_obj)
            results["continuous_learning"] = {
                "status": "recorded",
                "total_outcomes": len(cl.trading_outcomes),
                "learning_rate": cl.current_learning_rate,
            }
    except Exception as e:
        logger.warning(f"Continuous learning feedback failed (non-critical): {e}")
        results["continuous_learning"] = {"status": "error", "error": str(e)}

    # ------------------------------------------------------------------
    # 3. Regime context enrichment (non-blocking best-effort)
    # ------------------------------------------------------------------
    try:
        rf = _get_regime_forecaster()
        if rf is not None and rf.current_regime is not None:
            results["current_regime"] = {
                "regime": rf.current_regime.current_regime,
                "confidence": rf.current_regime.confidence,
                "duration_days": rf.current_regime.duration_days,
            }
    except Exception:
        pass

    logger.info(
        f"Trade outcome processed: {symbol} {side} pnl=${realized_pnl:.2f} "
        f"| RL={'ok' if results.get('rl_agent', {}).get('status') == 'learned' else 'skip'} "
        f"| CL={'ok' if results.get('continuous_learning', {}).get('status') == 'recorded' else 'skip'}"
    )
    return results
