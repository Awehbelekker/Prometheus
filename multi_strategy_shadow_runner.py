#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║            PROMETHEUS Multi-Strategy Shadow Trading Runner                  ║
║                                                                            ║
║  Runs N shadow trading strategies IN PARALLEL with different parameters    ║
║  to find the BEST configuration for live deployment.                       ║
║                                                                            ║
║  Each strategy runs its own PrometheusParallelShadowTrading instance with  ║
║  unique settings: AI weights, confidence thresholds, risk parameters,      ║
║  exit strategies, and position sizing.                                     ║
║                                                                            ║
║  Usage:                                                                    ║
║    python multi_strategy_shadow_runner.py                       (all 6)    ║
║    python multi_strategy_shadow_runner.py --strategies conservative,aggressive
║    python multi_strategy_shadow_runner.py --capital 50000 --iterations 100 ║
║    python multi_strategy_shadow_runner.py --leaderboard         (view)     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import json
import logging
import os
import sqlite3
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
logger = logging.getLogger('MultiStrategy')

# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 STRATEGY CONFIGURATIONS
# Each strategy has different parameters to test which approach works best.
# The runner will execute ALL strategies on the SAME market data simultaneously.
# ═══════════════════════════════════════════════════════════════════════════════

STRATEGY_CONFIGS = {
    # ──────────────────────────────────────────────────────
    # 1. CONSERVATIVE - High confidence, small positions, tight risk
    # ──────────────────────────────────────────────────────
    "conservative": {
        "description": "High confidence, small positions, tight stops. Quality over quantity.",
        "max_position_pct": 0.05,           # 5% per position (small)
        "min_confidence": 0.78,              # Only trade >78% confidence
        "min_score": 0.30,                   # Higher score threshold
        "target_pct": 0.02,                  # 2% target (modest)
        "stop_loss_pct": 0.015,              # 1.5% stop (tight)
        "trailing_stop_enabled": True,
        "trailing_stop_trigger": 0.015,      # Trigger at +1.5%
        "trailing_stop_distance": 0.008,     # Trail by 0.8%
        "dca_enabled": False,                # No averaging down
        "time_exit_enabled": True,
        "max_hold_days_stock": 5,            # Short holds
        "max_hold_days_crypto": 2,
        "scale_out_enabled": True,
        "scale_out_first_pct": 0.012,        # First exit at +1.2%
        "scale_out_second_pct": 0.025,       # Full exit at +2.5%
        "max_trades_per_day": 20,
        "ai_weights": {
            "AI_Consciousness": 0.22,   # NEW: Fine-tuned consciousness engine (highest weight)
            "RL_Agent": 0.18,            # NEW: Reinforcement learning agent
            "Revolutionary": 0.10,       # NEW: Revolutionary engines
            "HRM": 0.18,                 # Proven HRM system
            "Universal_Reasoning": 0.12,
            "Visual_Patterns": 0.06,
            "Quantum": 0.02,             # Reduced (disabled due to poor performance)
            "Technical": 0.08,
            "Agents": 0.02,              # Reduced (disabled due to 0% win rate)
            "Fed_NLP": 0.02
        }
    },

    # ──────────────────────────────────────────────────────
    # 2. AGGRESSIVE - Lower confidence, bigger bets, wider targets
    # ──────────────────────────────────────────────────────
    "aggressive": {
        "description": "Lower threshold, larger positions, DCA on dips. More trades, bigger swings.",
        "max_position_pct": 0.15,            # 15% per position (large)
        "min_confidence": 0.58,              # Lower bar to enter
        "min_score": 0.18,
        "target_pct": 0.05,                  # 5% target (ambitious)
        "stop_loss_pct": 0.04,               # 4% stop (wide)
        "trailing_stop_enabled": True,
        "trailing_stop_trigger": 0.03,       # Trigger at +3%
        "trailing_stop_distance": 0.015,     # Trail by 1.5%
        "dca_enabled": True,                 # Average down on dips
        "dca_trigger_pct": -0.03,            # DCA at -3%
        "dca_max_adds": 3,                   # Up to 3 DCA events
        "dca_position_pct": 0.08,
        "time_exit_enabled": True,
        "max_hold_days_stock": 14,           # Hold longer
        "max_hold_days_crypto": 7,
        "scale_out_enabled": True,
        "scale_out_first_pct": 0.025,        # First exit at +2.5%
        "scale_out_second_pct": 0.05,        # Full exit at +5%
        "max_trades_per_day": 60,
        "ai_weights": {
            "AI_Consciousness": 0.15,   # NEW: AI consciousness with lower weight (aggressive risk)
            "RL_Agent": 0.18,            # NEW: RL agent with higher weight (learn fast)
            "Revolutionary": 0.15,       # NEW: Revolutionary engines (crypto/options focus)
            "HRM": 0.15,
            "Universal_Reasoning": 0.15,
            "Visual_Patterns": 0.06,
            "Quantum": 0.03,
            "Technical": 0.08,
            "Agents": 0.03,
            "Fed_NLP": 0.02
        }
    },

    # ──────────────────────────────────────────────────────
    # 3. MOMENTUM - Favors strong trends, technical-heavy
    # ──────────────────────────────────────────────────────
    "momentum": {
        "description": "Follows strong momentum. Heavy technical weight, fast exits on reversals.",
        "max_position_pct": 0.10,
        "min_confidence": 0.65,
        "min_score": 0.22,
        "target_pct": 0.04,                  # 4% target
        "stop_loss_pct": 0.02,               # 2% stop
        "trailing_stop_enabled": True,
        "trailing_stop_trigger": 0.02,       # Quick trigger
        "trailing_stop_distance": 0.01,      # Trail close
        "dca_enabled": False,                # No DCA (momentum doesn't average down)
        "time_exit_enabled": True,
        "max_hold_days_stock": 3,            # Very short holds — ride momentum only
        "max_hold_days_crypto": 1,
        "scale_out_enabled": False,          # All or nothing
        "max_trades_per_day": 40,
        "ai_weights": {
            "HRM": 0.15,
            "Universal_Reasoning": 0.15,
            "Visual_Patterns": 0.15,
            "Quantum": 0.10,
            "Technical": 0.35,               # Heavy technical emphasis
            "Agents": 0.10
        }
    },

    # ──────────────────────────────────────────────────────
    # 4. MEAN REVERSION - Buys dips, heavy DCA, patience
    # ──────────────────────────────────────────────────────
    "mean_reversion": {
        "description": "Buys oversold conditions, heavy DCA, patient exits. Contrarian approach.",
        "max_position_pct": 0.08,
        "min_confidence": 0.60,
        "min_score": 0.20,
        "target_pct": 0.03,                  # 3% target
        "stop_loss_pct": 0.05,               # 5% stop (wide — need room for mean reversion)
        "trailing_stop_enabled": True,
        "trailing_stop_trigger": 0.025,
        "trailing_stop_distance": 0.012,
        "dca_enabled": True,                 # Core of strategy — average into position
        "dca_trigger_pct": -0.015,           # DCA earlier at -1.5%
        "dca_max_adds": 4,                   # Up to 4 DCA events
        "dca_position_pct": 0.06,
        "time_exit_enabled": True,
        "max_hold_days_stock": 10,
        "max_hold_days_crypto": 5,
        "scale_out_enabled": True,
        "scale_out_first_pct": 0.015,
        "scale_out_second_pct": 0.03,
        "max_trades_per_day": 30,
        "ai_weights": {
            "HRM": 0.20,
            "Universal_Reasoning": 0.25,     # Reasoning for mean reversion detection
            "Visual_Patterns": 0.20,         # Patterns like double bottoms
            "Quantum": 0.15,
            "Technical": 0.10,               # Less technical (it's contrarian)
            "Agents": 0.10
        }
    },

    # ──────────────────────────────────────────────────────
    # 5. AI CONSENSUS - Only trades when multiple AI systems agree
    # ──────────────────────────────────────────────────────
    "ai_consensus": {
        "description": "Ultra-selective: only trades when 3+ AI systems agree. Very few trades, high conviction.",
        "max_position_pct": 0.12,            # Bigger positions (high conviction)
        "min_confidence": 0.82,              # Very high confidence required
        "min_score": 0.35,                   # High aggregate score needed
        "target_pct": 0.04,                  # 4% target
        "stop_loss_pct": 0.025,              # 2.5% stop
        "trailing_stop_enabled": True,
        "trailing_stop_trigger": 0.02,
        "trailing_stop_distance": 0.01,
        "dca_enabled": True,
        "dca_trigger_pct": -0.02,
        "dca_max_adds": 1,                   # Limited DCA
        "time_exit_enabled": True,
        "max_hold_days_stock": 7,
        "max_hold_days_crypto": 3,
        "scale_out_enabled": True,
        "scale_out_first_pct": 0.02,
        "scale_out_second_pct": 0.04,
        "max_trades_per_day": 10,            # Very few trades
        "ai_weights": {
            "HRM": 0.20,                     # Even weighting — need consensus
            "Universal_Reasoning": 0.20,
            "Visual_Patterns": 0.15,
            "Quantum": 0.15,
            "Technical": 0.15,
            "Agents": 0.15
        }
    },

    # ──────────────────────────────────────────────────────
    # 6. QUICK SCALP - Tiny targets, tight stops, many trades
    # ──────────────────────────────────────────────────────
    "quick_scalp": {
        "description": "Rapid-fire micro-trades. Small targets, tight stops, high volume.",
        "max_position_pct": 0.07,
        "min_confidence": 0.60,
        "min_score": 0.18,
        "target_pct": 0.012,                 # 1.2% target (small, frequent)
        "stop_loss_pct": 0.01,               # 1% stop (tight)
        "trailing_stop_enabled": False,      # No trailing — hard targets
        "dca_enabled": False,                # No DCA — quick in/out
        "time_exit_enabled": True,
        "max_hold_days_stock": 1,            # EXIT within 1 day
        "max_hold_days_crypto": 1,
        "scale_out_enabled": False,          # All or nothing
        "max_trades_per_day": 80,            # Many trades
        "ai_weights": {
            "HRM": 0.20,
            "Universal_Reasoning": 0.10,
            "Visual_Patterns": 0.10,
            "Quantum": 0.15,
            "Technical": 0.30,               # Heavy technical for scalping
            "Agents": 0.15
        }
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT WATCHLIST (same for all strategies — apples-to-apples comparison)
# ═══════════════════════════════════════════════════════════════════════════════
DEFAULT_MULTI_WATCHLIST = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'AMD',
    'SPY', 'QQQ', 'IWM', 'DIA',
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'DOGE-USD', 'XRP-USD',
]


class MultiStrategyShadowRunner:
    """
    Orchestrates N parallel shadow trading strategies with different configs.
    All strategies trade the SAME symbols with the SAME market data but make
    DIFFERENT decisions based on their configuration.
    
    Key Features:
    - Parallel execution via asyncio
    - Real-time leaderboard comparing strategies
    - Persistent results in database
    - Auto-promotion: best-performing strategy params can be promoted to live
    """

    def __init__(self, strategies: List[str] = None, starting_capital: float = 100000.0,
                 watchlist: List[str] = None):
        self.strategies = strategies or list(STRATEGY_CONFIGS.keys())
        self.starting_capital = starting_capital
        self.watchlist = watchlist or DEFAULT_MULTI_WATCHLIST
        self.instances: Dict[str, Any] = {}
        self.start_time = datetime.now()
        self.run_id = f"multi_{self.start_time.strftime('%Y%m%d_%H%M%S')}"
        self.db_path = "prometheus_learning.db"
        self.results_dir = Path("shadow_trading_results/multi_strategy")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database tables
        self._init_multi_strategy_db()

        logger.info("=" * 70)
        logger.info("🏆 PROMETHEUS MULTI-STRATEGY SHADOW RUNNER")
        logger.info("=" * 70)
        logger.info(f"Run ID: {self.run_id}")
        logger.info(f"Strategies: {', '.join(self.strategies)}")
        logger.info(f"Capital per strategy: ${starting_capital:,.2f}")
        logger.info(f"Watchlist: {len(self.watchlist)} symbols")
        logger.info("=" * 70)

    def _init_multi_strategy_db(self):
        """Create database tables for multi-strategy tracking"""
        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            db.execute("PRAGMA journal_mode=WAL")
            cursor = db.cursor()

            # Strategy comparison snapshots
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS multi_strategy_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    strategy_name TEXT NOT NULL,
                    iteration INTEGER,
                    capital REAL,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    losing_trades INTEGER DEFAULT 0,
                    win_rate REAL DEFAULT 0,
                    total_pnl REAL DEFAULT 0,
                    max_drawdown REAL DEFAULT 0,
                    sharpe_ratio REAL DEFAULT 0,
                    avg_trade_pnl REAL DEFAULT 0,
                    best_trade_pnl REAL DEFAULT 0,
                    worst_trade_pnl REAL DEFAULT 0,
                    open_positions INTEGER DEFAULT 0
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_multi_strat_run
                ON multi_strategy_snapshots(run_id, strategy_name)
            """)

            # Strategy leaderboard (final results)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS multi_strategy_leaderboard (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    completed_at TEXT NOT NULL,
                    strategy_name TEXT NOT NULL,
                    rank INTEGER,
                    final_capital REAL,
                    total_return_pct REAL,
                    total_trades INTEGER,
                    win_rate REAL,
                    sharpe_ratio REAL,
                    max_drawdown REAL,
                    avg_trade_pnl REAL,
                    config_json TEXT,
                    promoted_to_live INTEGER DEFAULT 0
                )
            """)

            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to init multi-strategy DB: {e}")

    def _create_strategy_instance(self, strategy_name: str):
        """Create a PrometheusParallelShadowTrading instance for a strategy"""
        from parallel_shadow_trading import PrometheusParallelShadowTrading

        config = STRATEGY_CONFIGS[strategy_name]
        session_id = f"{self.run_id}_{strategy_name}"

        instance = PrometheusParallelShadowTrading(
            starting_capital=self.starting_capital,
            max_position_pct=config.get('max_position_pct', 0.10),
            session_id=session_id,
            config_name=strategy_name,
            strategy_config=config
        )

        return instance

    def _get_strategy_metrics(self, strategy_name: str) -> Dict:
        """Extract current performance metrics from a strategy instance"""
        instance = self.instances.get(strategy_name)
        if not instance:
            return {}

        trades = instance.shadow_trades
        closed_trades = [t for t in trades if t.status == 'CLOSED']
        winning = [t for t in closed_trades if t.pnl > 0]
        losing = [t for t in closed_trades if t.pnl <= 0]

        total_pnl = sum(t.pnl for t in closed_trades)
        win_rate = len(winning) / len(closed_trades) if closed_trades else 0
        avg_pnl = total_pnl / len(closed_trades) if closed_trades else 0
        best_trade = max((t.pnl for t in closed_trades), default=0)
        worst_trade = min((t.pnl for t in closed_trades), default=0)

        # Calculate max drawdown
        peak_capital = self.starting_capital
        max_drawdown = 0
        running_capital = self.starting_capital
        for trade in closed_trades:
            running_capital += trade.pnl
            peak_capital = max(peak_capital, running_capital)
            drawdown = (peak_capital - running_capital) / peak_capital if peak_capital > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)

        # Simple Sharpe approximation
        if closed_trades:
            import statistics
            pnls = [t.pnl_pct for t in closed_trades if t.pnl_pct != 0]
            if len(pnls) > 1:
                avg_ret = statistics.mean(pnls)
                std_ret = statistics.stdev(pnls)
                sharpe = (avg_ret / std_ret) * (252 ** 0.5) if std_ret > 0 else 0
            else:
                sharpe = 0
        else:
            sharpe = 0

        open_count = sum(1 for sym, pos in instance.open_positions.items() if pos)

        return {
            'strategy': strategy_name,
            'capital': instance.current_capital,
            'total_return_pct': ((instance.current_capital - self.starting_capital) / self.starting_capital) * 100,
            'total_trades': len(closed_trades),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_trade_pnl': avg_pnl,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe,
            'open_positions': open_count,
            'description': STRATEGY_CONFIGS[strategy_name].get('description', '')
        }

    def _save_snapshot(self, strategy_name: str, iteration: int):
        """Save a snapshot of strategy performance to database"""
        metrics = self._get_strategy_metrics(strategy_name)
        if not metrics:
            return

        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO multi_strategy_snapshots
                (run_id, timestamp, strategy_name, iteration, capital, total_trades,
                 winning_trades, losing_trades, win_rate, total_pnl, max_drawdown,
                 sharpe_ratio, avg_trade_pnl, best_trade_pnl, worst_trade_pnl, open_positions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.run_id,
                datetime.now().isoformat(),
                strategy_name,
                iteration,
                metrics['capital'],
                metrics['total_trades'],
                metrics['winning_trades'],
                metrics['losing_trades'],
                metrics['win_rate'],
                metrics['total_pnl'],
                metrics['max_drawdown'],
                metrics['sharpe_ratio'],
                metrics['avg_trade_pnl'],
                metrics['best_trade'],
                metrics['worst_trade'],
                metrics['open_positions']
            ))
            db.commit()
            db.close()
        except Exception as e:
            logger.debug(f"Snapshot save failed: {e}")

    def _promote_strategy_to_live(self, strategy_name: str, metrics: dict):
        """
        🏆 AUTO-PROMOTE: Write winning strategy config to disk and mark as promoted in DB.
        
        Criteria (already verified by caller):
        - Win rate > 50%
        - Positive total return
        - Has actual trades
        
        This writes a JSON config file that the live trading system can load,
        and sets promoted_to_live = 1 in the leaderboard DB.
        """
        try:
            strategy_config = STRATEGY_CONFIGS.get(strategy_name, {})
            
            # Build promoted config with metadata
            promoted_config = {
                'promoted_at': datetime.now().isoformat(),
                'source_strategy': strategy_name,
                'run_id': self.run_id,
                'performance': {
                    'win_rate': metrics.get('win_rate', 0),
                    'total_return_pct': metrics.get('total_return_pct', 0),
                    'total_trades': metrics.get('total_trades', 0),
                    'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                    'max_drawdown': metrics.get('max_drawdown', 0),
                    'avg_trade_pnl': metrics.get('avg_trade_pnl', 0),
                },
                'live_config': {
                    'min_confidence': strategy_config.get('min_confidence', 0.65),
                    'position_size_pct': strategy_config.get('position_size_pct', 0.10),
                    'stop_loss_pct': strategy_config.get('stop_loss_pct', 0.03),
                    'take_profit_pct': strategy_config.get('take_profit_pct', 0.05),
                    'max_positions': strategy_config.get('max_positions', 10),
                    'description': strategy_config.get('description', ''),
                    'ai_weights': strategy_config.get('ai_weights', {}),
                }
            }
            
            # Write promoted config to file
            config_path = os.path.join(os.path.dirname(self.db_path) or '.', 'live_trading_config_promoted.json')
            with open(config_path, 'w') as f:
                json.dump(promoted_config, f, indent=2)
            
            logger.info(f"AUTO-PROMOTED: '{strategy_name}' config written to {config_path}")
            logger.info(f"   Promoted config saved to: {config_path}")
            
            # Update DB: mark this strategy as promoted
            try:
                db = sqlite3.connect(self.db_path, timeout=30.0)
                cursor = db.cursor()
                cursor.execute("""
                    UPDATE multi_strategy_leaderboard 
                    SET promoted_to_live = 1
                    WHERE run_id = ? AND strategy_name = ?
                """, (self.run_id, strategy_name))
                db.commit()
                db.close()
                logger.info(f"🏆 DB updated: {strategy_name} marked as promoted_to_live=1")
            except Exception as db_err:
                logger.warning(f"Could not update promotion in DB: {db_err}")
            
            logger.info(f"   Strategy '{strategy_name}' has been AUTO-PROMOTED to live trading!")
            logger.info(f"   Performance: {metrics['win_rate']*100:.1f}% WR, {metrics['total_return_pct']:+.2f}% return, {metrics['total_trades']} trades")
            
        except Exception as e:
            logger.error(f"Auto-promotion failed: {e}")

    def _save_leaderboard(self):
        """Save final leaderboard to database"""
        all_metrics = []
        for name in self.strategies:
            m = self._get_strategy_metrics(name)
            if m:
                all_metrics.append(m)

        # Rank by total return
        all_metrics.sort(key=lambda x: x['total_return_pct'], reverse=True)

        try:
            db = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = db.cursor()
            for rank, m in enumerate(all_metrics, 1):
                cursor.execute("""
                    INSERT INTO multi_strategy_leaderboard
                    (run_id, completed_at, strategy_name, rank, final_capital, total_return_pct,
                     total_trades, win_rate, sharpe_ratio, max_drawdown, avg_trade_pnl, config_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.run_id,
                    datetime.now().isoformat(),
                    m['strategy'],
                    rank,
                    m['capital'],
                    m['total_return_pct'],
                    m['total_trades'],
                    m['win_rate'],
                    m['sharpe_ratio'],
                    m['max_drawdown'],
                    m['avg_trade_pnl'],
                    json.dumps(STRATEGY_CONFIGS.get(m['strategy'], {}))
                ))
            db.commit()
            db.close()
            logger.info(f"🏆 Leaderboard saved to database ({len(all_metrics)} strategies)")
        except Exception as e:
            logger.error(f"Leaderboard save failed: {e}")

    def print_leaderboard(self):
        """Print current strategy leaderboard"""
        all_metrics = []
        for name in self.strategies:
            m = self._get_strategy_metrics(name)
            if m:
                all_metrics.append(m)

        if not all_metrics:
            logger.info("No strategy data available yet.")
            return

        # Sort by total return
        all_metrics.sort(key=lambda x: x['total_return_pct'], reverse=True)

        logger.info("\n" + "=" * 95)
        logger.info("MULTI-STRATEGY SHADOW TRADING LEADERBOARD")
        logger.info("=" * 95)
        logger.info(f"{'Rank':<5} {'Strategy':<16} {'Capital':>12} {'Return':>8} {'Trades':>7} {'WR':>6} {'Sharpe':>7} {'MaxDD':>7} {'PnL':>10}")
        logger.info("-" * 95)

        for rank, m in enumerate(all_metrics, 1):
            medal = f"#{rank}" if rank <= 3 else f" {rank}"
            ret_color = "+" if m['total_return_pct'] >= 0 else ""
            logger.info(f"{medal:<4} {m['strategy']:<16} "
                  f"${m['capital']:>10,.2f} "
                  f"{ret_color}{m['total_return_pct']:>6.2f}% "
                  f"{m['total_trades']:>6} "
                  f"{m['win_rate']*100:>5.1f}% "
                  f"{m['sharpe_ratio']:>6.2f} "
                  f"{m['max_drawdown']*100:>5.2f}% "
                  f"${m['total_pnl']:>9,.2f}")

        logger.info("-" * 95)

        # Show best strategy details
        best = all_metrics[0]
        logger.info(f"\nLEADER: {best['strategy'].upper()}")
        logger.info(f"   {best['description']}")
        logger.info(f"   Capital: ${best['capital']:,.2f} | Return: {best['total_return_pct']:+.2f}%")
        logger.info(f"   Win Rate: {best['win_rate']*100:.1f}% | Sharpe: {best['sharpe_ratio']:.2f}")
        logger.info(f"   Trades: {best['total_trades']} (W:{best['winning_trades']} L:{best['losing_trades']})")
        logger.info(f"   Best Trade: ${best['best_trade']:+.2f} | Worst: ${best['worst_trade']:+.2f}")
        logger.info("=" * 95 + "\n")

    def save_report(self):
        """Save comprehensive comparison report to JSON"""
        all_metrics = []
        for name in self.strategies:
            m = self._get_strategy_metrics(name)
            if m:
                m['config'] = STRATEGY_CONFIGS.get(name, {})
                all_metrics.append(m)

        all_metrics.sort(key=lambda x: x['total_return_pct'], reverse=True)

        report = {
            'run_id': self.run_id,
            'generated_at': datetime.now().isoformat(),
            'starting_capital': self.starting_capital,
            'watchlist': self.watchlist,
            'strategies_tested': len(self.strategies),
            'leaderboard': all_metrics,
            'best_strategy': all_metrics[0]['strategy'] if all_metrics else None,
            'worst_strategy': all_metrics[-1]['strategy'] if all_metrics else None,
        }

        filepath = self.results_dir / f"comparison_{self.run_id}.json"
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Report saved: {filepath}")
        return filepath

    async def _run_single_strategy(self, strategy_name: str, interval_seconds: int,
                                     max_iterations: int, report_interval: int):
        """Run a single strategy (called as asyncio task)"""
        try:
            instance = self._create_strategy_instance(strategy_name)
            self.instances[strategy_name] = instance

            logger.info(f"🚀 Starting strategy: {strategy_name}")
            logger.info(f"   {STRATEGY_CONFIGS[strategy_name].get('description', '')}")

            # Initialize AI systems once
            await instance.initialize_all_ai_systems()

            iteration = 0
            instance.running = True

            while instance.running:
                iteration += 1

                if max_iterations and iteration > max_iterations:
                    break

                if instance.trades_today >= STRATEGY_CONFIGS[strategy_name].get('max_trades_per_day', 50):
                    await asyncio.sleep(interval_seconds)
                    continue

                # Fetch market data
                market_data = await instance.get_market_data(self.watchlist)
                if not market_data:
                    await asyncio.sleep(interval_seconds)
                    continue

                # Monitor existing positions
                await instance.monitor_positions()

                # Make decisions and trade
                for symbol, data in market_data.items():
                    if symbol in instance.open_positions and instance.open_positions[symbol]:
                        continue
                    decision = await instance.make_ai_decision(symbol, data)
                    if decision['action'] != 'HOLD':
                        await instance.execute_shadow_trade(symbol, decision, data)

                # Save snapshot periodically
                if iteration % report_interval == 0:
                    self._save_snapshot(strategy_name, iteration)
                    instance.save_session()

                # Feed learning data periodically
                if iteration % (report_interval * 5) == 0:
                    await instance.feed_to_learning_engine()

                await asyncio.sleep(interval_seconds)

        except asyncio.CancelledError:
            logger.info(f"⏹️ Strategy {strategy_name} cancelled")
        except Exception as e:
            logger.error(f"❌ Strategy {strategy_name} error: {e}", exc_info=True)
        finally:
            if strategy_name in self.instances:
                self.instances[strategy_name].save_session()

    async def run_all_strategies(self, interval_seconds: int = 60, max_iterations: int = None,
                                   report_interval: int = 10, leaderboard_interval: int = 30):
        """
        Run ALL strategies simultaneously and compare.

        Args:
            interval_seconds: Trading interval per iteration
            max_iterations: Stop after N iterations (None = run forever)
            report_interval: Save snapshots every N iterations
            leaderboard_interval: Print leaderboard every N iterations
        """
        logger.info("\n" + "=" * 70)
        logger.info("🏁 STARTING ALL STRATEGIES IN PARALLEL")
        logger.info("=" * 70)

        # Create tasks for each strategy
        tasks = {}
        for name in self.strategies:
            task = asyncio.create_task(
                self._run_single_strategy(name, interval_seconds, max_iterations, report_interval),
                name=f"strategy_{name}"
            )
            tasks[name] = task

        # Monitor task to periodically print leaderboard
        async def leaderboard_printer():
            iteration = 0
            while True:
                await asyncio.sleep(leaderboard_interval * interval_seconds)
                iteration += leaderboard_interval
                self.print_leaderboard()

                # Check if all tasks are done
                if all(t.done() for t in tasks.values()):
                    break

        leaderboard_task = asyncio.create_task(leaderboard_printer())

        try:
            # Wait for all strategy tasks to complete
            await asyncio.gather(*tasks.values(), return_exceptions=True)
        except KeyboardInterrupt:
            logger.info("\n⚠️ Multi-strategy run interrupted by user")
            for task in tasks.values():
                task.cancel()
        finally:
            leaderboard_task.cancel()

            # Final leaderboard and report
            logger.info("\n" + "=" * 70)
            logger.info("MULTI-STRATEGY RUN COMPLETE")
            logger.info("=" * 70)

            self.print_leaderboard()
            self._save_leaderboard()
            report_path = self.save_report()

            # Show promotion recommendation and auto-promote if criteria met
            all_metrics = []
            for name in self.strategies:
                m = self._get_strategy_metrics(name)
                if m and m['total_trades'] > 0:
                    all_metrics.append(m)

            if all_metrics:
                all_metrics.sort(key=lambda x: x['total_return_pct'], reverse=True)
                best = all_metrics[0]
                if best['win_rate'] > 0.5 and best['total_return_pct'] > 0:
                    logger.info(f"RECOMMENDATION: Promote '{best['strategy']}' strategy to live trading")
                    logger.info(f"   Config: {json.dumps(STRATEGY_CONFIGS[best['strategy']], indent=2)}")
                    # AUTO-PROMOTE: Actually write the promoted config and update DB
                    self._promote_strategy_to_live(best['strategy'], best)
                elif all_metrics:
                    logger.info(f"No strategy achieved >50% win rate AND positive returns")
                    logger.info(f"   Best: {best['strategy']} ({best['win_rate']*100:.1f}% WR, {best['total_return_pct']:+.2f}% return)")

            logger.info(f"Full report: {report_path}")
            logger.info("=" * 70)


def view_leaderboard():
    """View historical leaderboard from database"""
    try:
        db = sqlite3.connect('prometheus_learning.db', timeout=30.0)
        cursor = db.cursor()

        cursor.execute("""
            SELECT run_id, completed_at, strategy_name, rank, final_capital,
                   total_return_pct, total_trades, win_rate, sharpe_ratio, max_drawdown
            FROM multi_strategy_leaderboard
            ORDER BY run_id DESC, rank ASC
            LIMIT 50
        """)
        rows = cursor.fetchall()
        db.close()

        if not rows:
            print("No multi-strategy results found yet. Run a comparison first.")
            return

        current_run = None
        for row in rows:
            run_id, completed, name, rank, capital, ret_pct, trades, wr, sharpe, dd = row
            if run_id != current_run:
                current_run = run_id
                print(f"\n{'='*80}")
                print(f"Run: {run_id} | Completed: {completed}")
                print(f"{'Rank':<5} {'Strategy':<16} {'Capital':>12} {'Return':>8} {'Trades':>7} {'WR':>6} {'Sharpe':>7}")
                print("-" * 80)

            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            print(f"{medal}{rank:<3} {name:<16} ${capital:>10,.2f} {ret_pct:>+7.2f}% {trades:>6} {wr*100:>5.1f}% {sharpe:>6.2f}")

        print("=" * 80)

    except Exception as e:
        print(f"Error reading leaderboard: {e}")


def main():
    """CLI entry point for multi-strategy shadow trading"""
    import argparse

    parser = argparse.ArgumentParser(
        description='PROMETHEUS Multi-Strategy Shadow Trading — Run N strategies in parallel and compare',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available strategies:
{chr(10).join(f'  {name:<16} {cfg["description"]}' for name, cfg in STRATEGY_CONFIGS.items())}

Examples:
  python multi_strategy_shadow_runner.py                          # Run all 6 strategies
  python multi_strategy_shadow_runner.py --strategies conservative,aggressive
  python multi_strategy_shadow_runner.py --capital 50000 --iterations 200
  python multi_strategy_shadow_runner.py --leaderboard            # View past results
""")

    parser.add_argument('--strategies', type=str, default=None,
                        help='Comma-separated strategy names (default: ALL)')
    parser.add_argument('--capital', type=float, default=100000.0,
                        help='Starting capital per strategy (default: 100000, matches paper account)')
    parser.add_argument('--interval', type=int, default=60,
                        help='Trading interval in seconds (default: 60)')
    parser.add_argument('--iterations', type=int, default=None,
                        help='Max iterations per strategy (default: unlimited)')
    parser.add_argument('--report-interval', type=int, default=10,
                        help='Snapshot frequency in iterations (default: 10)')
    parser.add_argument('--leaderboard', action='store_true',
                        help='View historical multi-strategy leaderboard')
    parser.add_argument('--watchlist', type=str, default=None,
                        help='Comma-separated symbols (default: multi-asset)')

    args = parser.parse_args()

    if args.leaderboard:
        view_leaderboard()
        return

    # Parse strategies
    strategies = None
    if args.strategies:
        strategies = [s.strip().lower() for s in args.strategies.split(',')]
        invalid = [s for s in strategies if s not in STRATEGY_CONFIGS]
        if invalid:
            logger.error(f"Unknown strategies: {', '.join(invalid)}")
            print(f"Available: {', '.join(STRATEGY_CONFIGS.keys())}")
            return

    # Parse watchlist
    watchlist = None
    if args.watchlist:
        watchlist = [s.strip().upper() for s in args.watchlist.split(',')]

    runner = MultiStrategyShadowRunner(
        strategies=strategies,
        starting_capital=args.capital,
        watchlist=watchlist
    )

    # Run with asyncio
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(runner.run_all_strategies(
            interval_seconds=args.interval,
            max_iterations=args.iterations,
            report_interval=args.report_interval
        ))
    except KeyboardInterrupt:
        logger.info("⚠️ Multi-strategy runner interrupted")
    finally:
        try:
            loop.close()
        except:
            pass


if __name__ == '__main__':
    main()
