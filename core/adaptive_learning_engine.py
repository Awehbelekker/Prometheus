"""
PROMETHEUS Adaptive Learning Engine
====================================
Closes the feedback loop on EVERY trade.  Five concurrent background loops:

  1. Outcome Capture   (every 60 s)  – records P&L for closed trades
  2. Weight Update     (every 5 min) – adjusts AI voter weights from accuracy
  3. Model Retrain     (every 1 hr)  – audits staleness, retrains worst models
  4. Insight Generator (every 15 min)– persists learning_insights rows to DB
  5. Risk Adaptation   (every 10 min)– shrinks/grows sizing based on performance

Designed to run as a daemon thread alongside the main trading loop.
"""

import asyncio
import json
import logging
import math
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger("prometheus.adaptive_learning")

# ──────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────
TRADING_DB = Path("prometheus_trading.db")
LEARNING_DB = Path("prometheus_learning.db")
MODELS_DIR = Path("models_pretrained")
WEIGHTS_FILE = Path("ai_signal_weights_config.json")

DEFAULT_LOOP_INTERVALS = {
    "outcome_capture": 60,        # seconds
    "weight_update": 300,         # 5 min
    "model_retrain": 3600,        # 1 hour
    "insight_generation": 900,    # 15 min
    "risk_adaptation": 600,       # 10 min
}

# The 13 AI voters whose weights we track / update
AI_VOTERS = [
    "hrm_reasoning", "gpt_oss", "quantum_optimizer",
    "consciousness_engine", "mercury2", "pattern_match",
    "ml_regime", "langgraph_orchestrator", "fed_nlp",
    "adversarial_robustness", "explainable_ai", "chart_vision",
    "universal_reasoning",
]


# ──────────────────────────────────────────────────────────────
# DB bootstrap
# ──────────────────────────────────────────────────────────────
def _ensure_tables():
    """Create tables used by the adaptive learning engine if they don't exist."""
    for db_path in (TRADING_DB, LEARNING_DB):
        if not db_path.exists():
            continue
        conn = sqlite3.connect(str(db_path))
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS live_trade_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT,
                symbol TEXT,
                side TEXT,
                entry_price REAL,
                exit_price REAL,
                pnl REAL,
                pnl_pct REAL,
                hold_seconds INTEGER,
                ai_signals TEXT,
                outcome TEXT,
                captured_at TEXT
            );
            CREATE TABLE IF NOT EXISTS ai_weight_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                voter TEXT,
                old_weight REAL,
                new_weight REAL,
                accuracy REAL,
                sample_count INTEGER
            );
            CREATE TABLE IF NOT EXISTS risk_adaptation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                metric TEXT,
                old_value REAL,
                new_value REAL,
                reason TEXT
            );
        """)
        conn.close()


# ──────────────────────────────────────────────────────────────
# AdaptiveLearningEngine
# ──────────────────────────────────────────────────────────────
class AdaptiveLearningEngine:
    """Runs 5 concurrent learning loops that make Prometheus truly adaptive."""

    def __init__(self, intervals: Optional[Dict[str, int]] = None):
        self.intervals = {**DEFAULT_LOOP_INTERVALS, **(intervals or {})}
        self._running = False
        self._stats = {
            "outcomes_captured": 0,
            "weight_updates": 0,
            "models_retrained": 0,
            "insights_generated": 0,
            "risk_adaptations": 0,
            "started_at": None,
        }
        _ensure_tables()
        logger.info("AdaptiveLearningEngine initialised")

    # ── Public API ───────────────────────────────────────────
    async def start(self):
        """Launch all 5 background loops."""
        self._running = True
        self._stats["started_at"] = datetime.now().isoformat()
        logger.info("=== Adaptive Learning Engine STARTED ===")

        tasks = [
            asyncio.create_task(self._loop_outcome_capture()),
            asyncio.create_task(self._loop_weight_update()),
            asyncio.create_task(self._loop_model_retrain()),
            asyncio.create_task(self._loop_insight_generation()),
            asyncio.create_task(self._loop_risk_adaptation()),
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    def stop(self):
        self._running = False
        logger.info("Adaptive Learning Engine STOPPED")

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": "Adaptive Learning Engine",
            "running": self._running,
            **self._stats,
        }

    # ══════════════════════════════════════════════════════════
    # Loop 1: Outcome Capture  (60 s)
    # ══════════════════════════════════════════════════════════
    async def _loop_outcome_capture(self):
        while self._running:
            try:
                n = self._capture_outcomes()
                if n > 0:
                    logger.info(f"[Outcome Capture] Recorded {n} new outcomes")
                    self._stats["outcomes_captured"] += n
            except Exception as exc:
                logger.error(f"[Outcome Capture] Error: {exc}")
            await asyncio.sleep(self.intervals["outcome_capture"])

    def _capture_outcomes(self) -> int:
        """Scan closed trades that don't yet have a learning outcome row."""
        if not TRADING_DB.exists():
            return 0
        conn_t = sqlite3.connect(str(TRADING_DB))
        conn_t.row_factory = sqlite3.Row

        # Get closed trades not yet in live_trade_outcomes
        # Use trade_history if it exists, or orders table
        rows = []
        try:
            rows = conn_t.execute("""
                SELECT * FROM trade_history
                WHERE status IN ('CLOSED', 'FILLED', 'completed')
                  AND id NOT IN (
                      SELECT CAST(trade_id AS INTEGER) FROM live_trade_outcomes
                      WHERE trade_id IS NOT NULL
                  )
                ORDER BY timestamp DESC
                LIMIT 50
            """).fetchall()
        except Exception:
            pass

        if not rows:
            # Try orders table as fallback
            try:
                rows = conn_t.execute("""
                    SELECT * FROM orders
                    WHERE status IN ('filled', 'FILLED', 'completed')
                    ORDER BY timestamp DESC
                    LIMIT 50
                """).fetchall()
            except Exception:
                pass

        conn_t.close()

        # Always capture shadow trade outcomes regardless of live trade_history rows
        shadow_count = self._capture_shadow_outcomes()

        if not rows:
            return shadow_count

        conn_l = sqlite3.connect(str(LEARNING_DB))
        inserted = 0
        for row in rows:
            rd = dict(row)
            trade_id = str(rd.get("id", rd.get("order_id", "")))
            symbol = rd.get("symbol", "")
            side = rd.get("side", rd.get("action", ""))
            entry_price = float(rd.get("entry_price", rd.get("price", 0)) or 0)
            exit_price = float(rd.get("exit_price", rd.get("filled_price", entry_price)) or entry_price)
            qty = float(rd.get("quantity", rd.get("qty", 1)) or 1)

            if entry_price <= 0:
                continue

            pnl = (exit_price - entry_price) * qty if side.upper() in ("BUY", "LONG") else (entry_price - exit_price) * qty
            pnl_pct = ((exit_price / entry_price) - 1) * 100 if entry_price else 0
            outcome = "WIN" if pnl > 0 else ("LOSS" if pnl < 0 else "BREAKEVEN")

            # Parse timestamps for hold duration
            try:
                ts_str = rd.get("timestamp", rd.get("created_at", ""))
                exit_ts = rd.get("closed_at", rd.get("filled_at", ts_str))
                if ts_str and exit_ts:
                    t1 = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00").split("+")[0])
                    t2 = datetime.fromisoformat(str(exit_ts).replace("Z", "+00:00").split("+")[0])
                    hold_s = int((t2 - t1).total_seconds())
                else:
                    hold_s = 0
            except Exception:
                hold_s = 0

            ai_signals = rd.get("ai_signals", rd.get("signal_source", ""))

            try:
                conn_l.execute(
                    """INSERT INTO live_trade_outcomes
                       (trade_id, symbol, side, entry_price, exit_price,
                        pnl, pnl_pct, hold_seconds, ai_signals, outcome, captured_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (trade_id, symbol, side, entry_price, exit_price,
                     pnl, round(pnl_pct, 4), hold_s, str(ai_signals),
                     outcome, datetime.now().isoformat()),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                pass
            except Exception as exc:
                logger.debug(f"Outcome insert error: {exc}")

        # Also record in the existing learning_outcomes table
        if inserted > 0:
            try:
                conn_l.execute("""
                    INSERT OR IGNORE INTO learning_outcomes
                    (timestamp, metric_name, metric_value, details)
                    VALUES (?, 'adaptive_capture_batch', ?, ?)
                """, (datetime.now().isoformat(), inserted,
                      f"Captured {inserted} trade outcomes"))
            except Exception:
                pass

        conn_l.commit()
        conn_l.close()
        return inserted + shadow_count

    def _capture_shadow_outcomes(self) -> int:
        """Capture outcomes from shadow (paper) trading sessions."""
        if not LEARNING_DB.exists():
            return 0
        conn = sqlite3.connect(str(LEARNING_DB))
        conn.row_factory = sqlite3.Row

        # Get recent shadow trades not yet captured (closed trades only, text-based dedup)
        try:
            rows = conn.execute("""
                SELECT * FROM shadow_trade_history
                WHERE exit_time IS NOT NULL
                  AND exit_price IS NOT NULL
                  AND exit_price > 0
                  AND ('shadow_' || CAST(id AS TEXT)) NOT IN (
                      SELECT trade_id FROM live_trade_outcomes
                      WHERE trade_id LIKE 'shadow_%'
                  )
                ORDER BY timestamp DESC
                LIMIT 100
            """).fetchall()
        except Exception:
            conn.close()
            return 0

        inserted = 0
        for row in rows:
            rd = dict(row)
            trade_id = f"shadow_{rd.get('id', '')}"
            symbol = rd.get("symbol", "")
            pnl = float(rd.get("pnl", rd.get("profit_loss", 0)) or 0)
            pnl_pct = float(rd.get("pnl_pct", rd.get("return_pct", 0)) or 0)
            outcome = "WIN" if pnl > 0 else ("LOSS" if pnl < 0 else "BREAKEVEN")

            # Calculate hold duration
            try:
                ts_str = rd.get("timestamp", "")
                exit_ts = rd.get("exit_time", "")
                if ts_str and exit_ts:
                    t1 = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00").split("+")[0])
                    t2 = datetime.fromisoformat(str(exit_ts).replace("Z", "+00:00").split("+")[0])
                    hold_s = int((t2 - t1).total_seconds())
                else:
                    hold_s = 0
            except Exception:
                hold_s = 0

            try:
                conn.execute(
                    """INSERT INTO live_trade_outcomes
                       (trade_id, symbol, side, entry_price, exit_price,
                        pnl, pnl_pct, hold_seconds, ai_signals, outcome, captured_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (trade_id, symbol,
                     rd.get("side", rd.get("action", "")),
                     float(rd.get("entry_price", 0) or 0),
                     float(rd.get("exit_price", 0) or 0),
                     pnl, round(pnl_pct, 4), hold_s,
                     rd.get("strategy", "shadow"),
                     outcome, datetime.now().isoformat()),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                pass
            except Exception:
                pass

        conn.commit()
        conn.close()
        return inserted

    # ══════════════════════════════════════════════════════════
    # Loop 2: AI Weight Update  (5 min)
    # ══════════════════════════════════════════════════════════
    async def _loop_weight_update(self):
        while self._running:
            try:
                updated = self._update_ai_weights()
                if updated:
                    logger.info(f"[Weight Update] Updated {updated} voter weights")
                    self._stats["weight_updates"] += 1
            except Exception as exc:
                logger.error(f"[Weight Update] Error: {exc}")
            await asyncio.sleep(self.intervals["weight_update"])

    def _update_ai_weights(self) -> int:
        """
        Compute per-voter accuracy from signal_predictions + outcomes,
        then update ai_signal_weights_config.json.
        """
        if not LEARNING_DB.exists():
            return 0

        conn = sqlite3.connect(str(LEARNING_DB))
        conn.row_factory = sqlite3.Row

        # Load current weights
        current_weights = {}
        if WEIGHTS_FILE.exists():
            try:
                current_weights = json.loads(WEIGHTS_FILE.read_text())
            except Exception:
                pass

        if not current_weights:
            # Initialize with equal weights
            current_weights = {v: 1.0 / len(AI_VOTERS) for v in AI_VOTERS}

        # Compute accuracy per voter from attribution records
        voter_stats: Dict[str, Dict] = {}
        try:
            rows = conn.execute("""
                SELECT system_name,
                       COUNT(*) as total,
                       SUM(CASE WHEN was_correct = 1 THEN 1 ELSE 0 END) as correct
                FROM ai_attribution
                WHERE system_name IS NOT NULL
                GROUP BY system_name
            """).fetchall()
            for r in rows:
                name = r["system_name"].lower().replace(" ", "_").replace("-", "_")
                voter_stats[name] = {
                    "total": r["total"],
                    "correct": r["correct"],
                    "accuracy": r["correct"] / max(r["total"], 1),
                }
        except Exception:
            pass

        # Also pull from live_trade_outcomes to supplement accuracy
        try:
            outcome_rows = conn.execute("""
                SELECT outcome, COUNT(*) as cnt
                FROM live_trade_outcomes
                WHERE captured_at > datetime('now', '-7 days')
                GROUP BY outcome
            """).fetchall()
            # Use win rate as a multiplier
            total_trades = sum(r["cnt"] for r in outcome_rows)
            wins = sum(r["cnt"] for r in outcome_rows if r["outcome"] == "WIN")
            recent_win_rate = wins / max(total_trades, 1)
        except Exception:
            recent_win_rate = 0.5

        conn.close()

        if not voter_stats:
            return 0

        # Compute new weights: sigmoid(accuracy) * EMA with old weight
        EMA_ALPHA = 0.3  # how fast to adapt (0=never, 1=instant)
        new_weights = {}
        updated_count = 0

        for voter in AI_VOTERS:
            old_w = current_weights.get(voter, 1.0 / len(AI_VOTERS))

            # Find matching stats (fuzzy match on name)
            stats = None
            for key, val in voter_stats.items():
                if voter in key or key in voter:
                    stats = val
                    break

            if stats and stats["total"] >= 10:
                acc = stats["accuracy"]
                # Sigmoid transform: center at 0.5, steepen
                raw = 1.0 / (1.0 + math.exp(-10 * (acc - 0.5)))
                new_w = EMA_ALPHA * raw + (1 - EMA_ALPHA) * old_w
                updated_count += 1

                # Log to DB
                self._log_weight_change(voter, old_w, new_w, acc, stats["total"])
            else:
                new_w = old_w  # not enough data yet

            new_weights[voter] = new_w

        # Normalize to sum = 1.0
        total = sum(new_weights.values())
        if total > 0:
            new_weights = {k: v / total for k, v in new_weights.items()}

        # Save updated weights
        try:
            WEIGHTS_FILE.write_text(json.dumps(new_weights, indent=2))
        except Exception as exc:
            logger.error(f"Failed to save weights: {exc}")

        return updated_count

    def _log_weight_change(self, voter: str, old_w: float, new_w: float,
                           accuracy: float, sample_count: int):
        try:
            conn = sqlite3.connect(str(LEARNING_DB))
            conn.execute(
                """INSERT INTO ai_weight_history
                   (timestamp, voter, old_weight, new_weight, accuracy, sample_count)
                   VALUES (?,?,?,?,?,?)""",
                (datetime.now().isoformat(), voter, old_w, new_w, accuracy, sample_count),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════
    # Loop 3: Model Retrain  (1 hour)
    # ══════════════════════════════════════════════════════════
    async def _loop_model_retrain(self):
        # Wait 5 minutes before first retrain check (let system stabilize)
        await asyncio.sleep(300)
        while self._running:
            try:
                retrained = await self._auto_retrain()
                if retrained > 0:
                    logger.info(f"[Model Retrain] Retrained {retrained} models")
                    self._stats["models_retrained"] += retrained
            except Exception as exc:
                logger.error(f"[Model Retrain] Error: {exc}")

            # Rebuild Ollama prometheus-trader model from live trade patterns
            try:
                from core.ollama_finetuner import maybe_finetune
                maybe_finetune()
            except Exception as exc:
                logger.warning(f"[Model Retrain] Ollama fine-tune skipped: {exc}")

            await asyncio.sleep(self.intervals["model_retrain"])

    async def _auto_retrain(self) -> int:
        """Find stale or underperforming models, retrain the worst 3."""
        try:
            from core.auto_model_retrainer import AutoModelRetrainer
            retrainer = AutoModelRetrainer(
                stale_days=5,
                min_direction_accuracy=0.45,  # lowered threshold
            )

            # Find worst-performing models
            stale_models = self._find_worst_models(limit=3)

            retrained = 0
            for symbol, model_type in stale_models:
                try:
                    results = await retrainer._retrain_one(symbol, model_type, force=True)
                    if results.success:
                        retrained += 1
                        logger.info(f"  Retrained {symbol} {model_type}: "
                                    f"{results.old_metric:.3f} -> {results.new_metric:.3f}")
                except Exception as exc:
                    logger.warning(f"  Retrain failed {symbol} {model_type}: {exc}")

            # If no specific worst models, do a general sweep
            if not stale_models:
                report = await retrainer.retrain_all(force=False)
                retrained = report.models_retrained

            return retrained
        except ImportError:
            logger.warning("auto_model_retrainer not available")
            return 0

    def _find_worst_models(self, limit: int = 3) -> List[Tuple[str, str]]:
        """Query model_retrain_log for models with lowest recent accuracy."""
        worst = []
        try:
            conn = sqlite3.connect(str(LEARNING_DB))
            rows = conn.execute("""
                SELECT symbol, model_type, new_metric
                FROM model_retrain_log
                WHERE model_type = 'direction'
                  AND new_metric IS NOT NULL
                  AND timestamp > datetime('now', '-30 days')
                ORDER BY new_metric ASC
                LIMIT ?
            """, (limit,)).fetchall()
            conn.close()
            worst = [(r[0], r[1]) for r in rows]
        except Exception:
            pass

        # Also check for stale models (not retrained in > 14 days)
        if len(worst) < limit:
            import time as _time
            for sym in ["META", "INTC", "DIS", "PYPL", "BAC"]:
                for mt in ("direction",):
                    p = MODELS_DIR / f"{sym}_{mt}_model.pkl"
                    if p.exists():
                        age_days = (_time.time() - p.stat().st_mtime) / 86400
                        if age_days > 14 and (sym, mt) not in worst:
                            worst.append((sym, mt))
                            if len(worst) >= limit:
                                break
                if len(worst) >= limit:
                    break

        return worst[:limit]

    # ══════════════════════════════════════════════════════════
    # Loop 4: Insight Generation  (15 min)
    # ══════════════════════════════════════════════════════════
    async def _loop_insight_generation(self):
        while self._running:
            try:
                n = self._generate_and_persist_insights()
                if n > 0:
                    logger.info(f"[Insights] Generated {n} new insights")
                    self._stats["insights_generated"] += n
            except Exception as exc:
                logger.error(f"[Insights] Error: {exc}")
            await asyncio.sleep(self.intervals["insight_generation"])

    def _generate_and_persist_insights(self) -> int:
        """
        Analyze recent outcomes and persist actionable insights
        to learning_insights table.
        """
        if not LEARNING_DB.exists():
            return 0

        conn = sqlite3.connect(str(LEARNING_DB))
        conn.row_factory = sqlite3.Row
        insights_added = 0
        now = datetime.now().isoformat()

        # Insight 1: Per-symbol win rate (last 7 days)
        try:
            rows = conn.execute("""
                SELECT symbol,
                       COUNT(*) as total,
                       SUM(CASE WHEN outcome = 'WIN' THEN 1 ELSE 0 END) as wins,
                       AVG(pnl) as avg_pnl
                FROM live_trade_outcomes
                WHERE captured_at > datetime('now', '-7 days')
                GROUP BY symbol
                HAVING total >= 3
            """).fetchall()
            for r in rows:
                wr = r["wins"] / max(r["total"], 1)
                detail = (f"Symbol {r['symbol']}: {r['wins']}/{r['total']} wins "
                          f"({wr*100:.0f}%), avg PnL ${r['avg_pnl']:.2f}")
                conn.execute("""
                    INSERT INTO learning_insights
                    (timestamp, insight_type, symbol, metric_value, details, source)
                    VALUES (?,?,?,?,?,?)
                """, (now, "symbol_win_rate", r["symbol"], round(wr, 4),
                      detail, "adaptive_learning_engine"))
                insights_added += 1
        except Exception as exc:
            logger.debug(f"Symbol insight error: {exc}")

        # Insight 2: AI system accuracy ranking
        try:
            rows = conn.execute("""
                SELECT system_name,
                       COUNT(*) as total,
                       SUM(CASE WHEN was_correct = 1 THEN 1 ELSE 0 END) as correct
                FROM ai_attribution
                WHERE timestamp > datetime('now', '-7 days')
                GROUP BY system_name
                HAVING total >= 20
                ORDER BY (CAST(correct AS REAL) / total) DESC
            """).fetchall()
            for r in rows:
                acc = r["correct"] / max(r["total"], 1)
                detail = (f"AI {r['system_name']}: {r['correct']}/{r['total']} correct "
                          f"({acc*100:.1f}%)")
                conn.execute("""
                    INSERT INTO learning_insights
                    (timestamp, insight_type, symbol, metric_value, details, source)
                    VALUES (?,?,?,?,?,?)
                """, (now, "ai_system_accuracy", r["system_name"], round(acc, 4),
                      detail, "adaptive_learning_engine"))
                insights_added += 1
        except Exception as exc:
            logger.debug(f"AI accuracy insight error: {exc}")

        # Insight 3: Shadow vs live comparison
        try:
            shadow_wr = conn.execute("""
                SELECT AVG(CASE WHEN outcome = 'WIN' THEN 1.0 ELSE 0.0 END) as wr
                FROM live_trade_outcomes
                WHERE trade_id LIKE 'shadow_%'
                  AND captured_at > datetime('now', '-7 days')
            """).fetchone()
            live_wr = conn.execute("""
                SELECT AVG(CASE WHEN outcome = 'WIN' THEN 1.0 ELSE 0.0 END) as wr
                FROM live_trade_outcomes
                WHERE trade_id NOT LIKE 'shadow_%'
                  AND captured_at > datetime('now', '-7 days')
            """).fetchone()

            if shadow_wr and live_wr and shadow_wr["wr"] is not None and live_wr["wr"] is not None:
                diff = (live_wr["wr"] or 0) - (shadow_wr["wr"] or 0)
                detail = (f"Live WR: {(live_wr['wr'] or 0)*100:.1f}% vs "
                          f"Shadow WR: {(shadow_wr['wr'] or 0)*100:.1f}% "
                          f"(diff: {diff*100:+.1f}%)")
                conn.execute("""
                    INSERT INTO learning_insights
                    (timestamp, insight_type, symbol, metric_value, details, source)
                    VALUES (?,?,?,?,?,?)
                """, (now, "live_vs_shadow", "ALL", round(diff, 4),
                      detail, "adaptive_learning_engine"))
                insights_added += 1
        except Exception as exc:
            logger.debug(f"Shadow comparison insight error: {exc}")

        # Insight 4: Prediction accuracy trend
        try:
            recent = conn.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN was_correct = 1 THEN 1 ELSE 0 END) as correct
                FROM signal_predictions
                WHERE timestamp > datetime('now', '-1 day')
            """).fetchone()
            older = conn.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN was_correct = 1 THEN 1 ELSE 0 END) as correct
                FROM signal_predictions
                WHERE timestamp BETWEEN datetime('now', '-8 days') AND datetime('now', '-1 day')
            """).fetchone()

            if (recent and older and recent["total"] > 10 and older["total"] > 10):
                recent_acc = recent["correct"] / max(recent["total"], 1)
                older_acc = older["correct"] / max(older["total"], 1)
                trend = recent_acc - older_acc
                detail = (f"Prediction accuracy: last 24h={recent_acc*100:.1f}% "
                          f"vs prev week={older_acc*100:.1f}% (trend: {trend*100:+.1f}%)")
                conn.execute("""
                    INSERT INTO learning_insights
                    (timestamp, insight_type, symbol, metric_value, details, source)
                    VALUES (?,?,?,?,?,?)
                """, (now, "prediction_accuracy_trend", "ALL", round(trend, 4),
                      detail, "adaptive_learning_engine"))
                insights_added += 1
        except Exception as exc:
            logger.debug(f"Prediction trend insight error: {exc}")

        conn.commit()
        conn.close()
        return insights_added

    # ══════════════════════════════════════════════════════════
    # Loop 5: Risk Adaptation  (10 min)
    # ══════════════════════════════════════════════════════════
    async def _loop_risk_adaptation(self):
        while self._running:
            try:
                adapted = self._adapt_risk()
                if adapted:
                    logger.info(f"[Risk Adaptation] Made {adapted} adjustments")
                    self._stats["risk_adaptations"] += adapted
            except Exception as exc:
                logger.error(f"[Risk Adaptation] Error: {exc}")
            await asyncio.sleep(self.intervals["risk_adaptation"])

    def _adapt_risk(self) -> int:
        """
        Adjust position sizing and max-positions based on recent performance.
        Rules:
          - If win rate < 35% over last 24h → reduce position size by 30%
          - If drawdown > 5% over last 7d  → halve max positions
          - If win rate > 60% for 3+ days  → restore full sizing
        """
        if not LEARNING_DB.exists():
            return 0

        conn = sqlite3.connect(str(LEARNING_DB))
        conn.row_factory = sqlite3.Row
        adjustments = 0

        # Load current risk config
        risk_config_path = Path("risk_config.json")
        risk_config = {}
        if risk_config_path.exists():
            try:
                risk_config = json.loads(risk_config_path.read_text())
            except Exception:
                pass

        # Symbol-level protection: detect worst performers and reduce their allocation
        try:
            bad_symbols = conn.execute("""
                SELECT symbol, COUNT(*) as cnt, ROUND(AVG(pnl), 2) as avg_pnl
                FROM live_trade_outcomes
                WHERE captured_at > datetime('now', '-7 days')
                GROUP BY symbol
                HAVING avg_pnl < -200
                ORDER BY avg_pnl
            """).fetchall()
            
            restricted = risk_config.get("symbol_restrictions", {})
            for row in bad_symbols:
                sym, cnt, avg_pnl = row
                if sym not in restricted:
                    restricted[sym] = {"max_position_size": 0.015}  # 1.5% instead of 5%
                    self._log_risk_adaptation(
                        f"symbol_restriction_{sym}", 0, 0.015,
                        f"{sym} avg loss ${avg_pnl} ({cnt} trades)"
                    )
                    adjustments += 1
            if bad_symbols:
                risk_config["symbol_restrictions"] = restricted
        except Exception:
            pass

        default_max_position_pct = risk_config.get("max_position_pct", 5.0)
        default_max_positions = risk_config.get("max_positions", 10)

        # Recent win rate
        try:
            row = conn.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN outcome = 'WIN' THEN 1 ELSE 0 END) as wins,
                       SUM(pnl) as total_pnl
                FROM live_trade_outcomes
                WHERE captured_at > datetime('now', '-1 day')
            """).fetchone()

            if row and row["total"] >= 5:
                wr = row["wins"] / max(row["total"], 1)
                total_pnl = row["total_pnl"] or 0

                if wr < 0.33:
                    # Reduce position size
                    new_pct = round(default_max_position_pct * 0.7, 4)  # 4dp to avoid rounding 0.007 -> 0.01
                    if risk_config.get("max_position_pct", default_max_position_pct) != new_pct:
                        old_val = risk_config.get("max_position_pct", default_max_position_pct)
                        risk_config["max_position_pct"] = new_pct
                        risk_config["risk_reduced_at"] = datetime.now().isoformat()
                        self._log_risk_adaptation(
                            "max_position_pct", old_val, new_pct,
                            f"Win rate {wr*100:.0f}% < 33% threshold"
                        )
                        adjustments += 1

                elif wr > 0.60:
                    # Restore sizing if it was reduced
                    if risk_config.get("max_position_pct", default_max_position_pct) < default_max_position_pct:
                        old_val = risk_config.get("max_position_pct", default_max_position_pct)
                        risk_config["max_position_pct"] = default_max_position_pct
                        risk_config.pop("risk_reduced_at", None)
                        self._log_risk_adaptation(
                            "max_position_pct", old_val, default_max_position_pct,
                            f"Win rate {wr*100:.0f}% > 60% — restored"
                        )
                        adjustments += 1
        except Exception as exc:
            logger.debug(f"Win rate check error: {exc}")

        # 7-day drawdown check
        try:
            row = conn.execute("""
                SELECT SUM(pnl) as weekly_pnl
                FROM live_trade_outcomes
                WHERE captured_at > datetime('now', '-7 days')
            """).fetchone()

            if row and row["weekly_pnl"] is not None:
                weekly_pnl = row["weekly_pnl"]
                # Approximate drawdown based on typical $100K portfolio
                portfolio_value = 100_000  # default
                drawdown_pct = abs(min(weekly_pnl, 0)) / portfolio_value * 100

                if drawdown_pct > 5.0:
                    new_max = max(3, default_max_positions // 2)
                    if risk_config.get("max_positions", default_max_positions) != new_max:
                        old_val = risk_config.get("max_positions", default_max_positions)
                        risk_config["max_positions"] = new_max
                        self._log_risk_adaptation(
                            "max_positions", old_val, new_max,
                            f"Weekly drawdown {drawdown_pct:.1f}% > 5%"
                        )
                        adjustments += 1
        except Exception as exc:
            logger.debug(f"Drawdown check error: {exc}")

        conn.close()

        # Save risk config
        if adjustments > 0:
            try:
                risk_config_path.write_text(json.dumps(risk_config, indent=2))
                logger.info(f"Risk config updated: {risk_config}")
            except Exception as exc:
                logger.error(f"Failed to save risk config: {exc}")

        return adjustments

    def _log_risk_adaptation(self, metric: str, old_val: float, new_val: float, reason: str):
        try:
            conn = sqlite3.connect(str(LEARNING_DB))
            conn.execute(
                """INSERT INTO risk_adaptation_log
                   (timestamp, metric, old_value, new_value, reason)
                   VALUES (?,?,?,?,?)""",
                (datetime.now().isoformat(), metric, old_val, new_val, reason),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass


# ──────────────────────────────────────────────────────────────
# Singleton accessor
# ──────────────────────────────────────────────────────────────
_instance: Optional[AdaptiveLearningEngine] = None


def get_adaptive_engine() -> AdaptiveLearningEngine:
    global _instance
    if _instance is None:
        _instance = AdaptiveLearningEngine()
    return _instance
