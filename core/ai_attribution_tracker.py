"""
🎯 AI ATTRIBUTION TRACKER
Tracks which of the 80+ Revolutionary AI systems generate the most profitable signals.
Enables continuous optimization by identifying top-performing AI components.

Features:
- Per-AI-system performance tracking
- Win rate, average P&L, Sharpe ratio by AI system
- Daily/weekly leaderboard reports
- Historical attribution analysis
- Integration with learning engines
"""

import asyncio
import logging
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import json
import math

logger = logging.getLogger(__name__)

@dataclass
class AISignalAttribution:
    """Attribution record for a single AI signal"""
    attribution_id: str
    timestamp: datetime
    symbol: str
    ai_system: str  # e.g., 'Oracle', 'Quantum', 'Consciousness', 'Agents', 'CPT-OSS', 'Technical'
    action: str  # BUY, SELL, HOLD
    confidence: float
    vote_weight: float  # How much this AI contributed to final decision
    entry_price: float
    eventual_pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    outcome_recorded: bool = False
    trade_id: Optional[str] = None

@dataclass
class AISystemMetrics:
    """Performance metrics for a single AI system"""
    ai_system: str
    total_signals: int = 0
    signals_executed: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    win_rate: float = 0.0
    avg_pnl: float = 0.0
    avg_confidence: float = 0.0
    sharpe_ratio: float = 0.0
    max_win: float = 0.0
    max_loss: float = 0.0
    pnl_history: List[float] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)

class AIAttributionTracker:
    """
    Tracks which AI systems generate profitable signals.
    Enables optimization of AI weights based on performance.
    """
    
    def __init__(self, db_path: str = 'prometheus_learning.db'):
        self.db_path = db_path
        self.ai_metrics: Dict[str, AISystemMetrics] = {}
        self.recent_attributions: List[AISignalAttribution] = []

        # Initialize database tables
        self._init_database()

        # Load historical metrics - handle case where no event loop is running
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self._load_historical_metrics())
        except RuntimeError:
            # No running event loop - load synchronously or skip for testing
            try:
                asyncio.run(self._load_historical_metrics())
            except Exception:
                # In test environment, just skip loading historical metrics
                pass

        logger.info("🎯 AI Attribution Tracker initialized")
    
    def _init_database(self):
        """Initialize database tables for attribution tracking"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            db.execute("PRAGMA journal_mode=WAL")
            cursor = db.cursor()
            
            # Create ai_attribution table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_attribution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    attribution_id TEXT UNIQUE,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    ai_system TEXT NOT NULL,
                    system_name TEXT,
                    action TEXT NOT NULL,
                    confidence REAL,
                    vote_weight REAL,
                    entry_price REAL,
                    eventual_pnl REAL,
                    pnl_pct REAL,
                    was_correct INTEGER DEFAULT NULL,
                    outcome_recorded INTEGER DEFAULT 0,
                    trade_id TEXT
                )
            """)
            # Add columns to existing tables that predate this schema (safe on existing DBs)
            for col, typedef in [("system_name", "TEXT"), ("was_correct", "INTEGER DEFAULT NULL")]:
                try:
                    cursor.execute(f"ALTER TABLE ai_attribution ADD COLUMN {col} {typedef}")
                except Exception:
                    pass  # column already exists
            
            # Create ai_system_metrics table for daily snapshots
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    ai_system TEXT NOT NULL,
                    total_signals INTEGER,
                    signals_executed INTEGER,
                    winning_trades INTEGER,
                    losing_trades INTEGER,
                    total_pnl REAL,
                    win_rate REAL,
                    avg_pnl REAL,
                    sharpe_ratio REAL,
                    UNIQUE(date, ai_system)
                )
            """)
            
            # Create ai_system_weights table for persistent weight history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_system_weights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_time TEXT NOT NULL,
                    ai_system TEXT NOT NULL,
                    weight REAL NOT NULL,
                    win_rate REAL,
                    avg_pnl REAL,
                    total_signals INTEGER,
                    period_days INTEGER DEFAULT 30,
                    UNIQUE(snapshot_time, ai_system)
                )
            """)

            # Create index for faster queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_attribution_system ON ai_attribution(ai_system)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_attribution_symbol ON ai_attribution(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_attribution_timestamp ON ai_attribution(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_weights_time ON ai_system_weights(snapshot_time)")

            db.commit()
            db.close()

            logger.info("✅ AI Attribution database initialized (incl. ai_system_weights table)")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Attribution database: {e}")
    
    async def record_signal(self, symbol: str, ai_components: List[str], 
                           vote_breakdown: Dict[str, float], action: str,
                           confidence: float, entry_price: float,
                           trade_id: Optional[str] = None) -> List[str]:
        """
        Record a trading signal with attribution to contributing AI systems.
        Returns list of attribution IDs for later outcome recording.
        """
        attribution_ids = []
        
        try:
            timestamp = datetime.now()
            total_votes = sum(vote_breakdown.values()) or 1
            
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()
            
            for ai_system in ai_components:
                attribution_id = f"attr_{timestamp.strftime('%Y%m%d_%H%M%S')}_{ai_system}_{symbol}"
                
                # FIX: Calculate per-system vote weight
                # Old code used vote_breakdown.get(action, 0)/total_votes which gave EVERY system
                # the SAME weight (the winning action's total / grand total), making AI attribution useless.
                # New: Each contributing system gets an equal share of the winning action's votes.
                num_contributors = len(ai_components) or 1
                vote_weight = (vote_breakdown.get(action, 0) / total_votes / num_contributors) if total_votes > 0 else (1.0 / num_contributors)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO ai_attribution
                    (attribution_id, timestamp, symbol, ai_system, system_name, action, confidence,
                     vote_weight, entry_price, trade_id, outcome_recorded)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (
                    attribution_id,
                    timestamp.isoformat(),
                    symbol,
                    ai_system,
                    ai_system,   # system_name mirrors ai_system for adaptive_learning_engine queries
                    action,
                    confidence,
                    vote_weight,
                    entry_price,
                    trade_id
                ))
                
                attribution_ids.append(attribution_id)
                
                # Update in-memory metrics
                if ai_system not in self.ai_metrics:
                    self.ai_metrics[ai_system] = AISystemMetrics(ai_system=ai_system)
                self.ai_metrics[ai_system].total_signals += 1
                self.ai_metrics[ai_system].avg_confidence = (
                    (self.ai_metrics[ai_system].avg_confidence * (self.ai_metrics[ai_system].total_signals - 1) + confidence)
                    / self.ai_metrics[ai_system].total_signals
                )
            
            db.commit()
            db.close()
            
            logger.debug(f"📝 Recorded signal attribution: {symbol} → {ai_components}")

        except Exception as e:
            logger.error(f"Error recording signal attribution: {e}")

        return attribution_ids

    async def record_outcome(self, symbol: str, pnl: float, pnl_pct: float,
                            trade_id: Optional[str] = None):
        """Record trade outcome and update AI system metrics"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            was_correct = 1 if pnl_pct > 0 else 0

            # Update attributions for this symbol/trade
            if trade_id:
                cursor.execute("""
                    UPDATE ai_attribution
                    SET eventual_pnl = ?, pnl_pct = ?, outcome_recorded = 1, was_correct = ?
                    WHERE trade_id = ? AND outcome_recorded = 0
                """, (pnl, pnl_pct, was_correct, trade_id))
                # Fall back to symbol-based lookup when attributions were stored without trade_id
                if cursor.rowcount == 0:
                    cursor.execute("""
                        UPDATE ai_attribution
                        SET eventual_pnl = ?, pnl_pct = ?, outcome_recorded = 1,
                            trade_id = ?, was_correct = ?
                        WHERE id IN (
                            SELECT id FROM ai_attribution
                            WHERE symbol = ? AND outcome_recorded = 0
                            ORDER BY timestamp DESC LIMIT 10
                        )
                    """, (pnl, pnl_pct, trade_id, was_correct, symbol))
            else:
                # SQLite doesn't support ORDER BY/LIMIT in UPDATE, so use subquery
                cursor.execute("""
                    UPDATE ai_attribution
                    SET eventual_pnl = ?, pnl_pct = ?, outcome_recorded = 1, was_correct = ?
                    WHERE id IN (
                        SELECT id FROM ai_attribution
                        WHERE symbol = ? AND outcome_recorded = 0
                        ORDER BY timestamp DESC LIMIT 10
                    )
                """, (pnl, pnl_pct, was_correct, symbol))

            # Get affected AI systems and update their metrics
            cursor.execute("""
                SELECT DISTINCT ai_system FROM ai_attribution
                WHERE symbol = ? AND eventual_pnl = ?
            """, (symbol, pnl))

            affected_systems = [row[0] for row in cursor.fetchall()]

            db.commit()
            db.close()

            # Update in-memory metrics
            is_win = pnl > 0
            for ai_system in affected_systems:
                if ai_system not in self.ai_metrics:
                    self.ai_metrics[ai_system] = AISystemMetrics(ai_system=ai_system)

                metrics = self.ai_metrics[ai_system]
                metrics.signals_executed += 1
                metrics.total_pnl += pnl
                metrics.pnl_history.append(pnl)

                if is_win:
                    metrics.winning_trades += 1
                    metrics.max_win = max(metrics.max_win, pnl)
                else:
                    metrics.losing_trades += 1
                    metrics.max_loss = min(metrics.max_loss, pnl)

                # Recalculate metrics
                metrics.win_rate = metrics.winning_trades / metrics.signals_executed if metrics.signals_executed > 0 else 0
                metrics.avg_pnl = metrics.total_pnl / metrics.signals_executed if metrics.signals_executed > 0 else 0
                metrics.sharpe_ratio = self._calculate_sharpe(metrics.pnl_history)
                metrics.last_updated = datetime.now()

            # Persist ai_system_metrics to database (table was created but never written to)
            if affected_systems:
                try:
                    db2 = sqlite3.connect(self.db_path, timeout=30.0)
                    c2 = db2.cursor()
                    today = datetime.now().strftime('%Y-%m-%d')
                    for ai_system in affected_systems:
                        m = self.ai_metrics.get(ai_system)
                        if m:
                            c2.execute("""
                                INSERT INTO ai_system_metrics
                                    (date, ai_system, total_signals, signals_executed,
                                     winning_trades, losing_trades, total_pnl, win_rate, avg_pnl, sharpe_ratio)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ON CONFLICT(date, ai_system) DO UPDATE SET
                                    total_signals = excluded.total_signals,
                                    signals_executed = excluded.signals_executed,
                                    winning_trades = excluded.winning_trades,
                                    losing_trades = excluded.losing_trades,
                                    total_pnl = excluded.total_pnl,
                                    win_rate = excluded.win_rate,
                                    avg_pnl = excluded.avg_pnl,
                                    sharpe_ratio = excluded.sharpe_ratio
                            """, (today, ai_system, m.total_signals, m.signals_executed,
                                  m.winning_trades, m.losing_trades, m.total_pnl,
                                  m.win_rate, m.avg_pnl, m.sharpe_ratio))
                    db2.commit()
                    db2.close()
                except Exception as persist_err:
                    logger.debug(f"ai_system_metrics persist failed: {persist_err}")

            logger.info(f"📊 Outcome recorded for {symbol}: P/L=${pnl:+.2f} → {affected_systems}")

        except Exception as e:
            logger.error(f"Error recording outcome: {e}")

    def _calculate_sharpe(self, pnl_history: List[float], risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe ratio from P&L history"""
        if len(pnl_history) < 2:
            return 0.0

        avg_return = sum(pnl_history) / len(pnl_history)
        std_dev = math.sqrt(sum((x - avg_return) ** 2 for x in pnl_history) / len(pnl_history))

        if std_dev == 0:
            return 0.0

        return (avg_return - risk_free_rate) / std_dev

    async def get_top_performers(self, period_days: int = 30, min_signals: int = 5) -> List[Dict[str, Any]]:
        """Get top-performing AI systems over specified period"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()

            cursor.execute("""
                SELECT
                    ai_system,
                    COUNT(*) as total_signals,
                    SUM(CASE WHEN eventual_pnl > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN eventual_pnl <= 0 THEN 1 ELSE 0 END) as losses,
                    SUM(eventual_pnl) as total_pnl,
                    AVG(eventual_pnl) as avg_pnl,
                    AVG(confidence) as avg_confidence
                FROM ai_attribution
                WHERE timestamp >= ? AND outcome_recorded = 1
                GROUP BY ai_system
                HAVING total_signals >= ?
                ORDER BY total_pnl DESC
            """, (cutoff_date, min_signals))

            results = []
            for row in cursor.fetchall():
                ai_system, total_signals, wins, losses, total_pnl, avg_pnl, avg_confidence = row
                win_rate = wins / total_signals if total_signals > 0 else 0

                results.append({
                    'ai_system': ai_system,
                    'total_signals': total_signals,
                    'wins': wins,
                    'losses': losses,
                    'win_rate': win_rate,
                    'total_pnl': total_pnl or 0,
                    'avg_pnl': avg_pnl or 0,
                    'avg_confidence': avg_confidence or 0,
                    'rank': len(results) + 1
                })

            db.close()
            return results

        except Exception as e:
            logger.error(f"Error getting top performers: {e}")
            return []

    async def generate_leaderboard_report(self, period_days: int = 7) -> str:
        """Generate a formatted leaderboard report"""
        top_performers = await self.get_top_performers(period_days=period_days, min_signals=3)

        if not top_performers:
            return "📊 AI Leaderboard: No data available yet"

        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║          🏆 AI SYSTEM LEADERBOARD ({period_days}-Day Performance)         ║
╠══════════════════════════════════════════════════════════════════╣
"""

        for i, perf in enumerate(top_performers[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            pnl_emoji = "💰" if perf['total_pnl'] > 0 else "📉"

            report += f"""║ {medal} {perf['ai_system']:<15} │ Signals: {perf['total_signals']:>3} │ Win: {perf['win_rate']*100:>5.1f}% │ P/L: {pnl_emoji}${perf['total_pnl']:>8.2f} ║
"""

        report += """╚══════════════════════════════════════════════════════════════════╝"""

        return report

    async def get_ai_recommendations(self) -> Dict[str, Any]:
        """Get recommendations for AI weight adjustments based on performance"""
        top_performers = await self.get_top_performers(period_days=30, min_signals=10)

        recommendations = {
            'increase_weight': [],
            'decrease_weight': [],
            'maintain_weight': [],
            'top_performer': None,
            'worst_performer': None
        }

        if not top_performers:
            return recommendations

        avg_pnl = sum(p['avg_pnl'] for p in top_performers) / len(top_performers)
        avg_win_rate = sum(p['win_rate'] for p in top_performers) / len(top_performers)

        for perf in top_performers:
            if perf['avg_pnl'] > avg_pnl * 1.2 and perf['win_rate'] > avg_win_rate:
                recommendations['increase_weight'].append(perf['ai_system'])
            elif perf['avg_pnl'] < avg_pnl * 0.8 or perf['win_rate'] < avg_win_rate * 0.8:
                recommendations['decrease_weight'].append(perf['ai_system'])
            else:
                recommendations['maintain_weight'].append(perf['ai_system'])

        if top_performers:
            recommendations['top_performer'] = top_performers[0]['ai_system']
            recommendations['worst_performer'] = top_performers[-1]['ai_system']

        return recommendations

    async def _load_historical_metrics(self):
        """Load historical metrics from database"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            cursor.execute("""
                SELECT
                    ai_system,
                    COUNT(*) as total_signals,
                    SUM(CASE WHEN outcome_recorded = 1 THEN 1 ELSE 0 END) as executed,
                    SUM(CASE WHEN eventual_pnl > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN eventual_pnl <= 0 AND outcome_recorded = 1 THEN 1 ELSE 0 END) as losses,
                    SUM(eventual_pnl) as total_pnl,
                    AVG(confidence) as avg_confidence
                FROM ai_attribution
                GROUP BY ai_system
            """)

            for row in cursor.fetchall():
                ai_system, total_signals, executed, wins, losses, total_pnl, avg_confidence = row

                self.ai_metrics[ai_system] = AISystemMetrics(
                    ai_system=ai_system,
                    total_signals=total_signals or 0,
                    signals_executed=executed or 0,
                    winning_trades=wins or 0,
                    losing_trades=losses or 0,
                    total_pnl=total_pnl or 0,
                    win_rate=(wins / executed) if executed and executed > 0 else 0,
                    avg_pnl=(total_pnl / executed) if executed and executed > 0 else 0,
                    avg_confidence=avg_confidence or 0
                )

            db.close()
            logger.info(f"📊 Loaded historical metrics for {len(self.ai_metrics)} AI systems")

        except Exception as e:
            logger.warning(f"Could not load historical metrics: {e}")

    async def get_ai_system_weights(self, min_signals: int = 5, period_days: int = 30) -> Dict[str, float]:
        """
        🎯 LEARNING FEEDBACK LOOP - Get adaptive weights based on AI system performance

        Returns a dictionary of AI system names to weight multipliers (0.5 to 2.0)
        - Top performers get weight boost (up to 2.0x)
        - Poor performers get weight reduction (down to 0.5x)
        - Systems with insufficient data get neutral weight (1.0x)

        This is the CRITICAL missing piece that closes the learning feedback loop.
        """
        weights = {}

        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()

            cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()

            # Get performance metrics for each AI system
            cursor.execute("""
                SELECT
                    ai_system,
                    COUNT(*) as total_signals,
                    SUM(CASE WHEN eventual_pnl > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN eventual_pnl <= 0 AND outcome_recorded = 1 THEN 1 ELSE 0 END) as losses,
                    SUM(eventual_pnl) as total_pnl,
                    AVG(eventual_pnl) as avg_pnl
                FROM ai_attribution
                WHERE timestamp >= ? AND outcome_recorded = 1
                GROUP BY ai_system
            """, (cutoff_date,))

            rows = cursor.fetchall()
            db.close()

            if not rows:
                logger.warning("No AI attribution data with outcomes - using neutral weights")
                return {}

            # Calculate metrics for weight adjustment
            all_win_rates = []
            all_avg_pnls = []
            system_data = {}

            for row in rows:
                ai_system, total_signals, wins, losses, total_pnl, avg_pnl = row
                executed = wins + losses if wins and losses else 0

                if executed >= min_signals:
                    win_rate = (wins / executed) if executed > 0 else 0
                    all_win_rates.append(win_rate)
                    all_avg_pnls.append(avg_pnl or 0)
                    system_data[ai_system] = {
                        'win_rate': win_rate,
                        'avg_pnl': avg_pnl or 0,
                        'total_pnl': total_pnl or 0,
                        'signals': executed
                    }
                elif executed > 0:
                    # FIX: Systems below min_signals were silently excluded,
                    # causing _get_ai_weight() to return neutral 1.0 for them.
                    # Now assign cautious weight scaled by how much data we have.
                    # e.g. 2 out of 5 min_signals → 0.3 + (2/5)*0.4 = 0.46x
                    cautious_weight = 0.3 + (executed / min_signals) * 0.4
                    win_rate = (wins / executed) if executed > 0 else 0
                    # Further reduce if win rate is very low
                    if win_rate < 0.15:  # <15% WR = extra penalty
                        cautious_weight *= 0.5
                    weights[ai_system] = round(cautious_weight, 3)
                    logger.info(f"🎯 AI Weight (low-data): {ai_system} = {cautious_weight:.3f}x "
                              f"(only {executed}/{min_signals} signals, WR={win_rate:.0%})")

            if not all_win_rates:
                logger.warning("No AI systems with sufficient signals - using neutral weights")
                return {}

            # Calculate baseline metrics
            avg_win_rate = sum(all_win_rates) / len(all_win_rates)
            avg_pnl = sum(all_avg_pnls) / len(all_avg_pnls)

            # Calculate adaptive weights
            for ai_system, data in system_data.items():
                # Performance score: combine win rate and P/L performance
                win_rate_score = data['win_rate'] / avg_win_rate if avg_win_rate > 0 else 1.0

                # P/L score: relative performance vs peers AND absolute direction
                # Systems with negative avg_pnl are penalised even if they're the "least bad"
                if avg_pnl != 0:
                    pnl_score = 1.0 + (data['avg_pnl'] - avg_pnl) / abs(avg_pnl) * 0.3
                else:
                    pnl_score = 1.0 if data['avg_pnl'] >= 0 else 0.8

                # Absolute PnL penalty: if this system's avg trade is a loss, cap its score
                if data['avg_pnl'] < 0:
                    # Scale penalty by loss size: -$5 avg → 0.9x, -$50 avg → 0.5x, -$200+ → 0.3x
                    abs_loss = abs(data['avg_pnl'])
                    abs_penalty = max(0.3, 1.0 - min(0.7, abs_loss / 300.0))
                    pnl_score = min(pnl_score, abs_penalty)

                # Combined score (60% win rate, 40% P/L)
                combined_score = win_rate_score * 0.6 + pnl_score * 0.4

                # Clamp to reasonable range [0.3, 3.0] — widened to let learning differentiate better
                weight = max(0.3, min(3.0, combined_score))
                weights[ai_system] = weight

                logger.debug(f"🎯 AI Weight: {ai_system} = {weight:.2f}x "
                           f"(win_rate={data['win_rate']:.1%}, avg_pnl=${data['avg_pnl']:.4f})")

            # Log summary
            if weights:
                best = max(weights.items(), key=lambda x: x[1])
                worst = min(weights.items(), key=lambda x: x[1])
                logger.info(f"🎯 AI WEIGHTS LOADED: {len(weights)} systems | "
                          f"Best: {best[0]}={best[1]:.2f}x | Worst: {worst[0]}={worst[1]:.2f}x")

        except Exception as e:
            logger.error(f"Error calculating AI system weights: {e}")

        return weights

    def get_ai_system_weights_sync(self, min_signals: int = 5, period_days: int = 30) -> Dict[str, float]:
        """Synchronous version of get_ai_system_weights for use in non-async contexts"""
        try:
            loop = asyncio.get_running_loop()
            # If there's a running loop, we need to use create_task or run in executor
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.get_ai_system_weights(min_signals, period_days))
                return future.result(timeout=10)
        except RuntimeError:
            # No running loop - we can use asyncio.run
            return asyncio.run(self.get_ai_system_weights(min_signals, period_days))

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all AI system metrics"""
        summary = {
            'total_ai_systems': len(self.ai_metrics),
            'total_signals': sum(m.total_signals for m in self.ai_metrics.values()),
            'total_executed': sum(m.signals_executed for m in self.ai_metrics.values()),
            'total_pnl': sum(m.total_pnl for m in self.ai_metrics.values()),
            'best_performer': None,
            'worst_performer': None,
            'systems': {}
        }

        for name, metrics in self.ai_metrics.items():
            summary['systems'][name] = {
                'signals': metrics.total_signals,
                'executed': metrics.signals_executed,
                'win_rate': metrics.win_rate,
                'total_pnl': metrics.total_pnl,
                'avg_pnl': metrics.avg_pnl,
                'sharpe': metrics.sharpe_ratio
            }

        # Find best/worst by total P&L
        if self.ai_metrics:
            sorted_by_pnl = sorted(self.ai_metrics.items(), key=lambda x: x[1].total_pnl, reverse=True)
            if sorted_by_pnl:
                summary['best_performer'] = sorted_by_pnl[0][0]
                summary['worst_performer'] = sorted_by_pnl[-1][0]

        return summary

    def persist_weight_snapshot(self, weights: Dict[str, float], period_days: int = 30):
        """
        💾 Persist a snapshot of current AI system weights so we can track
        learning progress over time and survive restarts.
        """
        if not weights:
            return
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()
            snapshot_time = datetime.now().isoformat()

            for ai_system, weight in weights.items():
                # Also pull latest win_rate/avg_pnl from ai_attribution for context
                cursor.execute("""
                    SELECT
                        COUNT(*) as total,
                        AVG(CASE WHEN eventual_pnl > 0 THEN 1.0 ELSE 0.0 END) as wr,
                        AVG(eventual_pnl) as avg_pnl
                    FROM ai_attribution
                    WHERE ai_system = ? AND outcome_recorded = 1
                """, (ai_system,))
                row = cursor.fetchone()
                total_signals = row[0] if row else 0
                win_rate = row[1] if row and row[1] is not None else 0
                avg_pnl = row[2] if row and row[2] is not None else 0

                cursor.execute("""
                    INSERT INTO ai_system_weights
                        (snapshot_time, ai_system, weight, win_rate, avg_pnl, total_signals, period_days)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(snapshot_time, ai_system) DO UPDATE SET
                        weight = excluded.weight,
                        win_rate = excluded.win_rate,
                        avg_pnl = excluded.avg_pnl,
                        total_signals = excluded.total_signals
                """, (snapshot_time, ai_system, weight, win_rate, avg_pnl, total_signals, period_days))

            db.commit()
            db.close()
            logger.info(f"💾 Weight snapshot persisted: {len(weights)} systems at {snapshot_time[:19]}")
        except Exception as e:
            logger.error(f"Failed to persist weight snapshot: {e}")

    async def record_shadow_outcome(self, symbol: str, pnl: float, pnl_pct: float,
                                     ai_components: List[str] = None,
                                     confidence: float = 0.0,
                                     entry_price: float = 0.0,
                                     action: str = 'BUY'):
        """
        🔄 Ingest a completed shadow trade outcome into the ai_attribution table
        so shadow results feed back into the weight calculation loop.
        """
        if not ai_components:
            return
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()
            timestamp = datetime.now().isoformat()
            total_components = len(ai_components)

            for ai_system in ai_components:
                import uuid
                attribution_id = f"shadow_{uuid.uuid4().hex[:12]}"
                vote_weight = 1.0 / total_components if total_components > 0 else 1.0

                cursor.execute("""
                    INSERT OR REPLACE INTO ai_attribution
                    (attribution_id, timestamp, symbol, ai_system, action, confidence,
                     vote_weight, entry_price, eventual_pnl, pnl_pct, outcome_recorded, trade_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                """, (
                    attribution_id, timestamp, symbol, ai_system, action,
                    confidence, vote_weight, entry_price, pnl, pnl_pct,
                    f"shadow_{timestamp}"
                ))

            db.commit()
            db.close()

            # Update in-memory metrics too
            is_win = pnl > 0
            for ai_system in ai_components:
                if ai_system not in self.ai_metrics:
                    self.ai_metrics[ai_system] = AISystemMetrics(ai_system=ai_system)
                m = self.ai_metrics[ai_system]
                m.signals_executed += 1
                m.total_pnl += pnl
                m.pnl_history.append(pnl)
                if is_win:
                    m.winning_trades += 1
                    m.max_win = max(m.max_win, pnl)
                else:
                    m.losing_trades += 1
                    m.max_loss = min(m.max_loss, pnl)
                m.win_rate = m.winning_trades / m.signals_executed if m.signals_executed > 0 else 0
                m.avg_pnl = m.total_pnl / m.signals_executed if m.signals_executed > 0 else 0
                m.sharpe_ratio = self._calculate_sharpe(m.pnl_history)

            logger.info(f"🔄 Shadow outcome → attribution: {symbol} P/L=${pnl:+.2f} → {ai_components}")
        except Exception as e:
            logger.error(f"Error recording shadow outcome to attribution: {e}")


# Global singleton instance
_attribution_tracker: Optional[AIAttributionTracker] = None

def get_attribution_tracker() -> AIAttributionTracker:
    """Get the global AI Attribution Tracker instance"""
    global _attribution_tracker
    if _attribution_tracker is None:
        _attribution_tracker = AIAttributionTracker()
    return _attribution_tracker

