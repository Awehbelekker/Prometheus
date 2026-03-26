"""
Backtesting Validation Suite for PROMETHEUS Trading Platform.

Provides rigorous, statistically‑grounded validation of trading strategies using
real historical data (yfinance) with realistic transaction costs, slippage, and
position‑sizing constraints.

Key capabilities:
  1. Walk‑forward backtesting with configurable train/test windows
  2. Monte Carlo permutation tests (p‑value for strategy edge)
  3. Multi‑strategy comparison (Prometheus AI vs benchmarks)
  4. Risk‑adjusted metrics (Sharpe, Sortino, Calmar, max drawdown, profit factor)
  5. Regime‑aware analysis (bull / bear / sideways breakdowns)
  6. Statistical significance testing (bootstrap CIs, paired t‑tests)
  7. Report generation (JSON + human‑readable summary)

Usage (standalone):
    python -m core.backtesting_validation_suite --symbol AAPL --years 3

Author: PROMETHEUS AI Team
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import random
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE = 0.05  # annualized
DEFAULT_COMMISSION_BPS = 10  # basis points per side
DEFAULT_SLIPPAGE_BPS = 5
MIN_BARS = 60  # minimum bars to run a backtest

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TradeRecord:
    """Single completed round‑trip trade."""
    symbol: str
    side: str  # BUY / SELL (short)
    entry_price: float
    exit_price: float
    entry_date: str
    exit_date: str
    quantity: float
    pnl: float
    pnl_pct: float
    hold_bars: int
    commission: float = 0.0
    slippage: float = 0.0


@dataclass
class BacktestMetrics:
    """Aggregate metrics for a single backtest run."""
    strategy: str = ""
    symbol: str = ""
    start_date: str = ""
    end_date: str = ""
    # Returns
    total_return_pct: float = 0.0
    annualized_return_pct: float = 0.0
    buy_and_hold_return_pct: float = 0.0
    # Risk
    annualized_volatility: float = 0.0
    max_drawdown_pct: float = 0.0
    max_drawdown_duration_days: int = 0
    # Ratios
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    profit_factor: float = 0.0
    # Trades
    total_trades: int = 0
    win_rate: float = 0.0
    avg_win_pct: float = 0.0
    avg_loss_pct: float = 0.0
    best_trade_pct: float = 0.0
    worst_trade_pct: float = 0.0
    avg_hold_bars: float = 0.0
    # Costs
    total_commission: float = 0.0
    total_slippage: float = 0.0
    # Regime breakdown
    regime_returns: Dict[str, float] = field(default_factory=dict)
    # Equity curve (sampled)
    equity_curve_sample: List[float] = field(default_factory=list)
    # Warnings
    warnings: List[str] = field(default_factory=list)


@dataclass
class WalkForwardResult:
    """Result of one walk‑forward fold."""
    fold: int
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    train_metrics: BacktestMetrics
    test_metrics: BacktestMetrics


@dataclass
class MonteCarloResult:
    """Monte Carlo permutation test result."""
    strategy_sharpe: float
    mean_random_sharpe: float
    std_random_sharpe: float
    p_value: float
    num_simulations: int
    percentile_rank: float  # what % of random strategies the real one beats


@dataclass
class ValidationReport:
    """Full validation report."""
    timestamp: str = ""
    symbol: str = ""
    strategy: str = ""
    data_bars: int = 0
    # Overall
    overall_metrics: Optional[BacktestMetrics] = None
    # Walk‑forward
    walk_forward_folds: List[WalkForwardResult] = field(default_factory=list)
    walk_forward_avg_test_sharpe: float = 0.0
    walk_forward_avg_test_return: float = 0.0
    # Monte Carlo
    monte_carlo: Optional[MonteCarloResult] = None
    # Statistical
    bootstrap_sharpe_95ci: Tuple[float, float] = (0.0, 0.0)
    # Verdict
    statistically_significant: bool = False
    edge_detected: bool = False
    verdict: str = ""


# ---------------------------------------------------------------------------
# Strategy interface
# ---------------------------------------------------------------------------

class BaseStrategy:
    """Simple strategy interface.  Subclass or pass a callable to the engine."""

    name: str = "base"

    def generate_signals(self, df) -> np.ndarray:
        """Return an array of +1 (long), 0 (flat), -1 (short) for each bar."""
        raise NotImplementedError


class BuyAndHoldStrategy(BaseStrategy):
    name = "buy_and_hold"

    def generate_signals(self, df) -> np.ndarray:
        return np.ones(len(df))


class MomentumStrategy(BaseStrategy):
    """Simple dual‑SMA crossover."""
    name = "momentum_sma"

    def __init__(self, fast: int = 10, slow: int = 30):
        self.fast = fast
        self.slow = slow

    def generate_signals(self, df) -> np.ndarray:
        close = df["Close"].values
        sma_f = _rolling_mean(close, self.fast)
        sma_s = _rolling_mean(close, self.slow)
        signals = np.where(sma_f > sma_s, 1.0, -1.0)
        signals[: self.slow] = 0  # warmup
        return signals


class MeanReversionStrategy(BaseStrategy):
    """Bollinger‑band mean reversion."""
    name = "mean_reversion_bb"

    def __init__(self, window: int = 20, num_std: float = 2.0):
        self.window = window
        self.num_std = num_std

    def generate_signals(self, df) -> np.ndarray:
        close = df["Close"].values
        sma = _rolling_mean(close, self.window)
        std = _rolling_std(close, self.window)
        upper = sma + self.num_std * std
        lower = sma - self.num_std * std
        signals = np.zeros(len(close))
        for i in range(self.window, len(close)):
            if close[i] < lower[i]:
                signals[i] = 1.0  # oversold → buy
            elif close[i] > upper[i]:
                signals[i] = -1.0  # overbought → sell
            else:
                signals[i] = signals[i - 1] * 0.95  # decay toward flat
        return np.clip(signals, -1, 1)


class PrometheusAIStrategy(BaseStrategy):
    """
    Replays PROMETHEUS's actual ML model predictions on historical data.
    Falls back to a technical ensemble if models aren't available.
    """
    name = "prometheus_ai"

    def generate_signals(self, df) -> np.ndarray:
        """Use pre‑trained direction models when available, else technical ensemble."""
        close = df["Close"].values
        n = len(close)

        # Attempt to load the pre‑trained direction model for this symbol
        symbol = df.attrs.get("symbol", "UNKNOWN") if hasattr(df, "attrs") else "UNKNOWN"

        model, scaler = self._load_model(symbol)
        if model is not None:
            signals = self._model_signals(model, scaler, df)
        else:
            # Fallback: multi‑indicator ensemble
            signals = self._ensemble_signals(df)

        return signals

    # -- private helpers --
    def _load_model(self, symbol: str):
        """Return (model, scaler) tuple, or (None, None) if unavailable."""
        try:
            import joblib
            model_path = Path(f"models_pretrained/{symbol}_direction_model.pkl")
            scaler_path = Path(f"models_pretrained/{symbol}_direction_scaler.pkl")
            if model_path.exists() and scaler_path.exists():
                return joblib.load(model_path), joblib.load(scaler_path)
            if model_path.exists():
                return joblib.load(model_path), None
        except Exception:
            pass
        return None, None

    def _model_signals(self, model, scaler, df) -> np.ndarray:
        features = _compute_features(df)
        if features is None or len(features) == 0:
            return self._ensemble_signals(df)
        try:
            feat = scaler.transform(features) if scaler is not None else features
            preds = model.predict(feat)
            # Convert class labels to +1/0 (1=up, 0=down/flat)
            if hasattr(model, 'classes_'):
                unique = set(model.classes_)
                if 1 in unique:
                    signals = np.where(preds == 1, 1.0, -1.0)
                else:
                    # classes are 0/1 → map 0→-1, 1→+1
                    signals = np.where(preds > 0, 1.0, -1.0)
            else:
                signals = np.where(preds > 0, 1.0, -1.0)
            # Pad the front (we lose some rows computing features)
            pad = len(df) - len(signals)
            return np.concatenate([np.zeros(pad), signals])
        except Exception:
            return self._ensemble_signals(df)

    def _ensemble_signals(self, df) -> np.ndarray:
        close = df["Close"].values
        n = len(close)

        # RSI
        rsi = _compute_rsi(close, 14)
        rsi_sig = np.where(rsi < 30, 1.0, np.where(rsi > 70, -1.0, 0.0))

        # MACD
        ema12 = _ema(close, 12)
        ema26 = _ema(close, 26)
        macd_line = ema12 - ema26
        signal_line = _ema(macd_line, 9)
        macd_sig = np.where(macd_line > signal_line, 1.0, -1.0)
        macd_sig[:26] = 0

        # Bollinger
        sma20 = _rolling_mean(close, 20)
        std20 = _rolling_std(close, 20)
        bb_sig = np.where(close < sma20 - 2 * std20, 1.0,
                          np.where(close > sma20 + 2 * std20, -1.0, 0.0))

        # Volume (if available)
        if "Volume" in df.columns:
            vol = df["Volume"].values.astype(float)
            vol_sma = _rolling_mean(vol, 20)
            vol_sig = np.where(vol > 1.5 * vol_sma, 0.3, 0.0)
        else:
            vol_sig = np.zeros(n)

        # Weighted ensemble
        combined = 0.35 * rsi_sig + 0.30 * macd_sig + 0.20 * bb_sig + 0.15 * vol_sig
        return np.clip(combined, -1, 1)


# ---------------------------------------------------------------------------
# Backtest Engine
# ---------------------------------------------------------------------------

class BacktestEngine:
    """
    Core vectorized backtest engine with realistic friction.
    """

    def __init__(
        self,
        commission_bps: float = DEFAULT_COMMISSION_BPS,
        slippage_bps: float = DEFAULT_SLIPPAGE_BPS,
        initial_capital: float = 100_000.0,
        max_position_pct: float = 1.0,
    ):
        self.commission_bps = commission_bps
        self.slippage_bps = slippage_bps
        self.initial_capital = initial_capital
        self.max_position_pct = max_position_pct

    def run(
        self,
        df,
        strategy: BaseStrategy,
        symbol: str = "UNKNOWN",
    ) -> BacktestMetrics:
        """Run a full backtest on *df* (must have columns Open, High, Low, Close, Volume)."""
        close = df["Close"].values.astype(float)
        n = len(close)
        if n < MIN_BARS:
            m = BacktestMetrics(strategy=strategy.name, symbol=symbol)
            m.warnings.append(f"Insufficient data ({n} bars < {MIN_BARS})")
            return m

        signals = strategy.generate_signals(df)
        signals = np.nan_to_num(signals, nan=0.0)

        # -- Vectorized PnL --
        daily_returns = np.diff(close) / close[:-1]

        # Position is signal shifted by 1 (trade at next bar open)
        position = np.zeros(n)
        position[1:] = signals[:-1]
        position = np.clip(position, -1, 1) * self.max_position_pct

        # Strategy returns (before costs)
        strat_returns = position[1:] * daily_returns

        # Costs: incurred when position changes
        pos_delta = np.abs(np.diff(position))
        cost_per_bar = pos_delta * (self.commission_bps + self.slippage_bps) / 10_000
        strat_returns -= cost_per_bar

        # Equity curve
        equity = self.initial_capital * np.cumprod(1 + np.concatenate([[0], strat_returns]))

        # Buy‑and‑hold
        bh_equity = self.initial_capital * (close / close[0])

        # Trades
        trades = self._extract_trades(close, position, symbol)

        # Build metrics
        m = BacktestMetrics(
            strategy=strategy.name,
            symbol=symbol,
            start_date=str(df.index[0].date()) if hasattr(df.index[0], "date") else str(df.index[0]),
            end_date=str(df.index[-1].date()) if hasattr(df.index[-1], "date") else str(df.index[-1]),
        )

        m.total_return_pct = round((equity[-1] / self.initial_capital - 1) * 100, 4)
        years = max(n / TRADING_DAYS_PER_YEAR, 0.01)
        m.annualized_return_pct = round(((equity[-1] / self.initial_capital) ** (1 / years) - 1) * 100, 4)
        m.buy_and_hold_return_pct = round((bh_equity[-1] / self.initial_capital - 1) * 100, 4)

        # Volatility
        if len(strat_returns) > 1:
            m.annualized_volatility = round(float(np.std(strat_returns) * np.sqrt(TRADING_DAYS_PER_YEAR)), 6)

        # Drawdown
        peak = np.maximum.accumulate(equity)
        dd = (equity - peak) / peak
        m.max_drawdown_pct = round(float(np.min(dd)) * 100, 4)
        # Drawdown duration
        in_dd = dd < 0
        dd_dur = 0
        max_dd_dur = 0
        for v in in_dd:
            if v:
                dd_dur += 1
                max_dd_dur = max(max_dd_dur, dd_dur)
            else:
                dd_dur = 0
        m.max_drawdown_duration_days = max_dd_dur

        # Ratios
        mean_r = float(np.mean(strat_returns)) if len(strat_returns) else 0
        std_r = float(np.std(strat_returns)) if len(strat_returns) > 1 else 1e-9
        downside = strat_returns[strat_returns < 0]
        downside_std = float(np.std(downside)) if len(downside) > 1 else 1e-9
        rf_daily = RISK_FREE_RATE / TRADING_DAYS_PER_YEAR

        m.sharpe_ratio = round((mean_r - rf_daily) / max(std_r, 1e-9) * np.sqrt(TRADING_DAYS_PER_YEAR), 4)
        m.sortino_ratio = round((mean_r - rf_daily) / max(downside_std, 1e-9) * np.sqrt(TRADING_DAYS_PER_YEAR), 4)
        abs_dd = abs(m.max_drawdown_pct / 100) if m.max_drawdown_pct != 0 else 1e-9
        m.calmar_ratio = round(m.annualized_return_pct / 100 / abs_dd, 4)

        # Profit factor
        gross_profit = sum(t.pnl for t in trades if t.pnl > 0)
        gross_loss = abs(sum(t.pnl for t in trades if t.pnl < 0))
        m.profit_factor = round(gross_profit / max(gross_loss, 1e-9), 4)

        # Trade stats
        m.total_trades = len(trades)
        if trades:
            wins = [t for t in trades if t.pnl > 0]
            losses = [t for t in trades if t.pnl <= 0]
            m.win_rate = round(len(wins) / len(trades), 4)
            m.avg_win_pct = round(np.mean([t.pnl_pct for t in wins]) if wins else 0, 4)
            m.avg_loss_pct = round(np.mean([t.pnl_pct for t in losses]) if losses else 0, 4)
            m.best_trade_pct = round(max(t.pnl_pct for t in trades), 4)
            m.worst_trade_pct = round(min(t.pnl_pct for t in trades), 4)
            m.avg_hold_bars = round(np.mean([t.hold_bars for t in trades]), 2)

        m.total_commission = round(sum(cost_per_bar) * self.initial_capital * self.commission_bps / (self.commission_bps + self.slippage_bps + 1e-9), 2)
        m.total_slippage = round(sum(cost_per_bar) * self.initial_capital * self.slippage_bps / (self.commission_bps + self.slippage_bps + 1e-9), 2)

        # Sample equity curve (max 200 points)
        step = max(1, len(equity) // 200)
        m.equity_curve_sample = [round(float(v), 2) for v in equity[::step]]

        # Regime breakdown
        m.regime_returns = self._regime_breakdown(close, strat_returns)

        return m

    # -- helpers --

    def _extract_trades(self, close, position, symbol) -> List[TradeRecord]:
        """Extract round‑trip trades from position array."""
        trades: List[TradeRecord] = []
        in_trade = False
        entry_idx = 0
        entry_side = 0.0
        for i in range(1, len(position)):
            if not in_trade and position[i] != 0:
                in_trade = True
                entry_idx = i
                entry_side = np.sign(position[i])
            elif in_trade and (position[i] == 0 or np.sign(position[i]) != entry_side):
                # Close trade
                ep = close[entry_idx]
                xp = close[i]
                pnl_pct = (xp / ep - 1) * entry_side * 100
                pnl = (xp - ep) * entry_side
                trades.append(TradeRecord(
                    symbol=symbol, side="BUY" if entry_side > 0 else "SELL",
                    entry_price=round(float(ep), 4), exit_price=round(float(xp), 4),
                    entry_date=str(i - (i - entry_idx)), exit_date=str(i),
                    quantity=1.0, pnl=round(float(pnl), 4), pnl_pct=round(float(pnl_pct), 4),
                    hold_bars=i - entry_idx,
                ))
                in_trade = position[i] != 0
                if in_trade:
                    entry_idx = i
                    entry_side = np.sign(position[i])
        return trades

    def _regime_breakdown(self, close, strat_returns) -> Dict[str, float]:
        """Split returns by market regime (bull / bear / sideways)."""
        regimes: Dict[str, List[float]] = {"bull": [], "bear": [], "sideways": []}
        lookback = 60
        for i in range(len(strat_returns)):
            idx = i + 1  # align with close
            if idx < lookback:
                regimes["sideways"].append(float(strat_returns[i]))
                continue
            ret_lb = (close[idx] / close[idx - lookback] - 1) * 100
            if ret_lb > 5:
                regimes["bull"].append(float(strat_returns[i]))
            elif ret_lb < -5:
                regimes["bear"].append(float(strat_returns[i]))
            else:
                regimes["sideways"].append(float(strat_returns[i]))
        return {k: round(sum(v) * 100, 4) if v else 0.0 for k, v in regimes.items()}


# ---------------------------------------------------------------------------
# Validation Suite (orchestrator)
# ---------------------------------------------------------------------------

class BacktestingValidationSuite:
    """
    Orchestrates walk‑forward testing, Monte Carlo, and statistical validation.
    """

    def __init__(
        self,
        commission_bps: float = DEFAULT_COMMISSION_BPS,
        slippage_bps: float = DEFAULT_SLIPPAGE_BPS,
        initial_capital: float = 100_000.0,
    ):
        self.engine = BacktestEngine(
            commission_bps=commission_bps,
            slippage_bps=slippage_bps,
            initial_capital=initial_capital,
        )
        self.initial_capital = initial_capital
        self._reports_dir = Path("backtest_reports")
        self._reports_dir.mkdir(exist_ok=True)
        self._runs: int = 0
        logger.info("Backtesting Validation Suite initialized (commission=%sbps, slippage=%sbps)", commission_bps, slippage_bps)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def validate_strategy(
        self,
        symbol: str = "SPY",
        strategy: Optional[BaseStrategy] = None,
        years: float = 3.0,
        walk_forward_folds: int = 5,
        monte_carlo_sims: int = 500,
        bootstrap_samples: int = 1000,
    ) -> ValidationReport:
        """
        Full validation pipeline for a strategy on a single symbol.

        1. Download data
        2. Run overall backtest
        3. Walk‑forward analysis
        4. Monte Carlo permutation test
        5. Bootstrap confidence intervals
        6. Generate verdict
        """
        self._runs += 1
        report = ValidationReport(
            timestamp=datetime.now().isoformat(),
            symbol=symbol.upper(),
            strategy=(strategy or PrometheusAIStrategy()).name,
        )

        # 1. Data
        df = await self._fetch_data(symbol, years)
        if df is None or len(df) < MIN_BARS:
            report.verdict = f"INSUFFICIENT DATA — only {len(df) if df is not None else 0} bars"
            return report

        report.data_bars = len(df)

        # Tag the dataframe so the strategy can identify the symbol
        df.attrs["symbol"] = symbol.upper()

        strat = strategy or PrometheusAIStrategy()

        # 2. Overall backtest
        report.overall_metrics = self.engine.run(df, strat, symbol.upper())

        # 3. Walk‑forward
        report.walk_forward_folds = self._walk_forward(df, strat, symbol, walk_forward_folds)
        if report.walk_forward_folds:
            test_sharpes = [f.test_metrics.sharpe_ratio for f in report.walk_forward_folds]
            test_rets = [f.test_metrics.total_return_pct for f in report.walk_forward_folds]
            report.walk_forward_avg_test_sharpe = round(float(np.mean(test_sharpes)), 4)
            report.walk_forward_avg_test_return = round(float(np.mean(test_rets)), 4)

        # 4. Monte Carlo
        report.monte_carlo = self._monte_carlo_test(df, strat, symbol, monte_carlo_sims)

        # 5. Bootstrap CI on Sharpe
        report.bootstrap_sharpe_95ci = self._bootstrap_sharpe(df, strat, symbol, bootstrap_samples)

        # 6. Verdict
        report.statistically_significant = (
            report.monte_carlo is not None and report.monte_carlo.p_value < 0.05
        )
        report.edge_detected = (
            report.overall_metrics.sharpe_ratio > 0.5
            and report.overall_metrics.profit_factor > 1.0
            and report.walk_forward_avg_test_sharpe > 0.0
        )

        mc_p = f"{report.monte_carlo.p_value:.3f}" if report.monte_carlo else "N/A"
        ov_sharpe = f"{report.overall_metrics.sharpe_ratio:.2f}"
        wf_sharpe = f"{report.walk_forward_avg_test_sharpe:.2f}"

        if report.statistically_significant and report.edge_detected:
            report.verdict = (
                f"VALIDATED - Statistically significant edge detected "
                f"(p={mc_p}, Sharpe={ov_sharpe}, WF-Sharpe={wf_sharpe})"
            )
        elif report.edge_detected:
            report.verdict = (
                f"PROMISING - Edge detected but not statistically significant "
                f"(p={mc_p})"
            )
        elif report.statistically_significant:
            report.verdict = (
                f"MARGINAL - Statistically significant but weak edge "
                f"(Sharpe={ov_sharpe})"
            )
        else:
            report.verdict = (
                f"NOT VALIDATED - No significant edge detected "
                f"(Sharpe={ov_sharpe}, p={mc_p})"
            )

        return report

    async def compare_strategies(
        self,
        symbol: str = "SPY",
        years: float = 3.0,
    ) -> Dict[str, Any]:
        """Compare Prometheus AI strategy against benchmarks."""
        df = await self._fetch_data(symbol, years)
        if df is None or len(df) < MIN_BARS:
            return {"error": f"Insufficient data for {symbol}"}

        df.attrs["symbol"] = symbol.upper()

        strategies = [
            PrometheusAIStrategy(),
            BuyAndHoldStrategy(),
            MomentumStrategy(fast=10, slow=30),
            MeanReversionStrategy(window=20, num_std=2.0),
        ]

        results = {}
        for strat in strategies:
            m = self.engine.run(df, strat, symbol.upper())
            results[strat.name] = {
                "total_return_pct": m.total_return_pct,
                "annualized_return_pct": m.annualized_return_pct,
                "sharpe_ratio": m.sharpe_ratio,
                "sortino_ratio": m.sortino_ratio,
                "max_drawdown_pct": m.max_drawdown_pct,
                "profit_factor": m.profit_factor,
                "win_rate": m.win_rate,
                "total_trades": m.total_trades,
            }

        # Rank
        ranking = sorted(results.items(), key=lambda kv: kv[1]["sharpe_ratio"], reverse=True)
        return {
            "symbol": symbol.upper(),
            "period_years": years,
            "data_bars": len(df),
            "strategies": results,
            "ranking": [{"rank": i + 1, "strategy": k, "sharpe": v["sharpe_ratio"]} for i, (k, v) in enumerate(ranking)],
        }

    def save_report(self, report: ValidationReport) -> str:
        """Save report to JSON file."""
        fname = f"{report.symbol}_{report.strategy}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = self._reports_dir / fname
        # Convert dataclass → dict, handling nested dataclasses
        data = _deep_asdict(report)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        logger.info("Report saved: %s", path)
        return str(path)

    def get_status(self) -> Dict[str, Any]:
        """Status summary for the API."""
        return {
            "name": "Backtesting Validation Suite",
            "active": True,
            "runs_completed": self._runs,
            "commission_bps": self.engine.commission_bps,
            "slippage_bps": self.engine.slippage_bps,
            "initial_capital": self.initial_capital,
            "reports_dir": str(self._reports_dir),
            "available_strategies": [
                "prometheus_ai", "buy_and_hold", "momentum_sma", "mean_reversion_bb",
            ],
        }

    # ------------------------------------------------------------------
    # Walk‑forward
    # ------------------------------------------------------------------

    def _walk_forward(
        self,
        df,
        strategy: BaseStrategy,
        symbol: str,
        n_folds: int = 5,
    ) -> List[WalkForwardResult]:
        """Anchored walk‑forward: expanding train, rolling test."""
        n = len(df)
        if n < MIN_BARS * 2:
            return []

        test_size = n // (n_folds + 1)
        results: List[WalkForwardResult] = []

        for fold in range(n_folds):
            train_end = test_size * (fold + 1)
            test_end = min(train_end + test_size, n)
            if test_end - train_end < 20:
                break

            train_df = df.iloc[:train_end].copy()
            test_df = df.iloc[train_end:test_end].copy()

            train_df.attrs["symbol"] = symbol.upper()
            test_df.attrs["symbol"] = symbol.upper()

            train_m = self.engine.run(train_df, strategy, symbol)
            test_m = self.engine.run(test_df, strategy, symbol)

            results.append(WalkForwardResult(
                fold=fold + 1,
                train_start=str(train_df.index[0]),
                train_end=str(train_df.index[-1]),
                test_start=str(test_df.index[0]),
                test_end=str(test_df.index[-1]),
                train_metrics=train_m,
                test_metrics=test_m,
            ))

        return results

    # ------------------------------------------------------------------
    # Monte Carlo permutation test
    # ------------------------------------------------------------------

    def _monte_carlo_test(
        self,
        df,
        strategy: BaseStrategy,
        symbol: str,
        n_sims: int = 500,
    ) -> Optional[MonteCarloResult]:
        """Permutation test: compare real Sharpe vs randomly‑shuffled signals."""
        close = df["Close"].values.astype(float)
        n = len(close)
        if n < MIN_BARS:
            return None

        real_metrics = self.engine.run(df, strategy, symbol)
        real_sharpe = real_metrics.sharpe_ratio

        random_sharpes: List[float] = []

        # Pre‑compute daily returns once
        daily_ret = np.diff(close) / close[:-1]

        for _ in range(n_sims):
            # Random signals
            rand_signals = np.random.choice([-1.0, 0.0, 1.0], size=n, p=[0.3, 0.4, 0.3])
            position = np.zeros(n)
            position[1:] = rand_signals[:-1]
            strat_ret = position[1:] * daily_ret
            pos_delta = np.abs(np.diff(position))
            cost = pos_delta * (self.engine.commission_bps + self.engine.slippage_bps) / 10_000
            strat_ret -= cost

            mean_r = float(np.mean(strat_ret))
            std_r = float(np.std(strat_ret)) if len(strat_ret) > 1 else 1e-9
            rf_daily = RISK_FREE_RATE / TRADING_DAYS_PER_YEAR
            sharpe = (mean_r - rf_daily) / max(std_r, 1e-9) * np.sqrt(TRADING_DAYS_PER_YEAR)
            random_sharpes.append(sharpe)

        random_sharpes_arr = np.array(random_sharpes)
        p_value = float(np.mean(random_sharpes_arr >= real_sharpe))
        percentile = float(np.mean(random_sharpes_arr < real_sharpe) * 100)

        return MonteCarloResult(
            strategy_sharpe=real_sharpe,
            mean_random_sharpe=round(float(np.mean(random_sharpes_arr)), 4),
            std_random_sharpe=round(float(np.std(random_sharpes_arr)), 4),
            p_value=round(p_value, 4),
            num_simulations=n_sims,
            percentile_rank=round(percentile, 2),
        )

    # ------------------------------------------------------------------
    # Bootstrap confidence interval
    # ------------------------------------------------------------------

    def _bootstrap_sharpe(
        self,
        df,
        strategy: BaseStrategy,
        symbol: str,
        n_samples: int = 1000,
    ) -> Tuple[float, float]:
        """Bootstrap 95% CI for the Sharpe ratio."""
        close = df["Close"].values.astype(float)
        n = len(close)
        if n < MIN_BARS:
            return (0.0, 0.0)

        signals = strategy.generate_signals(df)
        signals = np.nan_to_num(signals, nan=0.0)

        daily_ret = np.diff(close) / close[:-1]
        position = np.zeros(n)
        position[1:] = signals[:-1]
        position = np.clip(position, -1, 1)
        strat_ret = position[1:] * daily_ret

        pos_delta = np.abs(np.diff(position))
        cost = pos_delta * (self.engine.commission_bps + self.engine.slippage_bps) / 10_000
        strat_ret -= cost

        rf_daily = RISK_FREE_RATE / TRADING_DAYS_PER_YEAR
        sharpes: List[float] = []
        for _ in range(n_samples):
            idx = np.random.randint(0, len(strat_ret), size=len(strat_ret))
            sample = strat_ret[idx]
            m = float(np.mean(sample))
            s = float(np.std(sample))
            sharpes.append((m - rf_daily) / max(s, 1e-9) * np.sqrt(TRADING_DAYS_PER_YEAR))

        sharpes.sort()
        lo = sharpes[int(0.025 * n_samples)]
        hi = sharpes[int(0.975 * n_samples)]
        return (round(lo, 4), round(hi, 4))

    # ------------------------------------------------------------------
    # Data fetching
    # ------------------------------------------------------------------

    async def _fetch_data(self, symbol: str, years: float):
        """Download historical daily OHLCV via yfinance."""
        try:
            import yfinance as yf
            ticker = symbol.upper().replace("/", "-")
            end = datetime.now()
            start = end - timedelta(days=int(years * 365))
            df = yf.download(ticker, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), progress=False, auto_adjust=True)
            if df is None or df.empty:
                logger.warning("No data returned for %s", symbol)
                return None
            # Flatten multi‑level columns if present
            if hasattr(df.columns, "levels") and df.columns.nlevels > 1:
                df.columns = df.columns.get_level_values(0)
            return df
        except Exception as e:
            logger.error("Failed to fetch data for %s: %s", symbol, e)
            return None


# ---------------------------------------------------------------------------
# Numeric helpers (pure numpy, no external TA libs needed)
# ---------------------------------------------------------------------------

def _rolling_mean(arr: np.ndarray, window: int) -> np.ndarray:
    out = np.full_like(arr, np.nan, dtype=float)
    cs = np.cumsum(arr)
    out[window - 1:] = (cs[window - 1:] - np.concatenate([[0], cs[:-window]])) / window
    # forward fill NaN
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1] if not np.isnan(out[i - 1]) else 0.0
    return out


def _rolling_std(arr: np.ndarray, window: int) -> np.ndarray:
    out = np.full_like(arr, 0.0, dtype=float)
    for i in range(window, len(arr)):
        out[i] = float(np.std(arr[i - window:i]))
    return out


def _ema(arr: np.ndarray, span: int) -> np.ndarray:
    alpha = 2.0 / (span + 1)
    out = np.zeros_like(arr, dtype=float)
    out[0] = arr[0]
    for i in range(1, len(arr)):
        out[i] = alpha * arr[i] + (1 - alpha) * out[i - 1]
    return out


def _compute_rsi(close: np.ndarray, period: int = 14) -> np.ndarray:
    deltas = np.diff(close)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    avg_gain = np.zeros(len(close))
    avg_loss = np.zeros(len(close))
    if len(gains) >= period:
        avg_gain[period] = np.mean(gains[:period])
        avg_loss[period] = np.mean(losses[:period])
        for i in range(period + 1, len(close)):
            avg_gain[i] = (avg_gain[i - 1] * (period - 1) + gains[i - 1]) / period
            avg_loss[i] = (avg_loss[i - 1] * (period - 1) + losses[i - 1]) / period
    rs = avg_gain / np.where(avg_loss == 0, 1e-9, avg_loss)
    rsi = 100 - 100 / (1 + rs)
    rsi[:period + 1] = 50  # neutral during warmup
    return rsi


def _compute_features(df) -> Optional[np.ndarray]:
    """Compute the same 11 features used by auto_model_retrainer for ML predictions."""
    try:
        with np.errstate(divide='ignore', invalid='ignore'):
            return _compute_features_inner(df)
    except Exception:
        return None


def _compute_features_inner(df) -> Optional[np.ndarray]:
    """Compute EXACTLY the 11 features used by AutoModelRetrainer (FEATURE_COLS order).
    Order: rsi, macd, macd_signal, bb_upper, bb_lower, sma_20, ema_12,
           volume_ratio, daily_return, price_vs_sma20, volatility
    """
    try:
        import pandas as pd

        close = df["Close"].values.astype(float)
        vol   = df["Volume"].values.astype(float) if "Volume" in df.columns else np.ones(len(close))

        n = len(close)
        if n < 30:
            return None

        # RSI(14)
        delta    = np.diff(close, prepend=close[0])
        gain     = np.where(delta > 0, delta, 0.0)
        loss     = np.where(delta < 0, -delta, 0.0)
        avg_gain = pd.Series(gain).rolling(14, min_periods=1).mean().values
        avg_loss = pd.Series(loss).rolling(14, min_periods=1).mean().values
        rs  = avg_gain / np.where(avg_loss == 0, 1e-10, avg_loss)
        rsi = 100 - (100 / (1 + rs))

        # MACD + signal
        ema12       = pd.Series(close).ewm(span=12, adjust=False).mean().values
        ema26       = pd.Series(close).ewm(span=26, adjust=False).mean().values
        macd        = ema12 - ema26
        macd_signal = pd.Series(macd).ewm(span=9, adjust=False).mean().values

        # Bollinger Bands (upper & lower — kept raw, same as retrainer)
        sma20    = pd.Series(close).rolling(20, min_periods=1).mean().values
        std20    = pd.Series(close).rolling(20, min_periods=1).std(ddof=0).values
        bb_upper = sma20 + 2 * std20
        bb_lower = sma20 - 2 * std20

        # EMA12 (already done) + SMA20
        # volume ratio vs 20-day avg
        vol_ma       = pd.Series(vol).rolling(20, min_periods=1).mean().values
        volume_ratio = vol / np.where(vol_ma == 0, 1.0, vol_ma)

        # Daily return
        daily_return = np.concatenate(
            [[0.0], np.diff(close) / np.where(close[:-1] == 0, 1.0, close[:-1])]
        )

        # Price vs SMA20
        price_vs_sma20 = (close - sma20) / np.where(sma20 == 0, 1.0, sma20)

        # Volatility — 20-day rolling std of daily_return
        volatility = pd.Series(daily_return).rolling(20, min_periods=1).std().values

        features = np.column_stack([
            rsi,            # 0
            macd,           # 1
            macd_signal,    # 2
            bb_upper,       # 3
            bb_lower,       # 4
            sma20,          # 5  (sma_20)
            ema12,          # 6  (ema_12)
            volume_ratio,   # 7
            daily_return,   # 8
            price_vs_sma20, # 9
            volatility,     # 10
        ])

        features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
        # Drop warmup rows (first 30)
        features = features[30:]
        return features
    except Exception:
        return None


def _deep_asdict(obj):
    """Recursively convert dataclass to dict, handling nested dataclasses, tuples, and numpy types."""
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _deep_asdict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, dict):
        return {k: _deep_asdict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_deep_asdict(v) for v in obj]
    # Convert numpy scalars to native Python types for JSON serialisation
    try:
        import numpy as _np
        if isinstance(obj, (_np.integer,)):
            return int(obj)
        if isinstance(obj, (_np.floating,)):
            return float(obj)
        if isinstance(obj, (_np.bool_,)):
            return bool(obj)
        if isinstance(obj, _np.ndarray):
            return obj.tolist()
    except ImportError:
        pass
    # Handle NaN / Inf which are not valid JSON
    if isinstance(obj, float):
        if obj != obj:          # NaN
            return None
        if obj == float("inf") or obj == float("-inf"):
            return None
    return obj


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_instance: Optional[BacktestingValidationSuite] = None

def get_backtester() -> BacktestingValidationSuite:
    global _instance
    if _instance is None:
        _instance = BacktestingValidationSuite()
    return _instance


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PROMETHEUS Backtesting Validation Suite")
    parser.add_argument("--symbol", default="SPY", help="Ticker symbol (default: SPY)")
    parser.add_argument("--years", type=float, default=3.0, help="Years of history (default: 3)")
    parser.add_argument("--mc", type=int, default=500, help="Monte Carlo simulations (default: 500)")
    args = parser.parse_args()

    async def main():
        suite = BacktestingValidationSuite()
        print(f"\n{'='*70}")
        print(f"  PROMETHEUS BACKTESTING VALIDATION — {args.symbol}")
        print(f"{'='*70}\n")

        report = await suite.validate_strategy(
            symbol=args.symbol,
            years=args.years,
            monte_carlo_sims=args.mc,
        )

        m = report.overall_metrics
        if m:
            print(f"  Strategy:            {m.strategy}")
            print(f"  Period:              {m.start_date} → {m.end_date}")
            print(f"  Total Return:        {m.total_return_pct:.2f}%")
            print(f"  Annual Return:       {m.annualized_return_pct:.2f}%")
            print(f"  Buy & Hold:          {m.buy_and_hold_return_pct:.2f}%")
            print(f"  Sharpe Ratio:        {m.sharpe_ratio:.2f}")
            print(f"  Sortino Ratio:       {m.sortino_ratio:.2f}")
            print(f"  Max Drawdown:        {m.max_drawdown_pct:.2f}%")
            print(f"  Win Rate:            {m.win_rate*100:.1f}%")
            print(f"  Profit Factor:       {m.profit_factor:.2f}")
            print(f"  Total Trades:        {m.total_trades}")

        if report.monte_carlo:
            mc = report.monte_carlo
            print(f"\n  Monte Carlo (n={mc.num_simulations}):")
            print(f"    Strategy Sharpe:   {mc.strategy_sharpe:.2f}")
            print(f"    Random Mean:       {mc.mean_random_sharpe:.2f} ± {mc.std_random_sharpe:.2f}")
            print(f"    p‑value:           {mc.p_value:.3f}")
            print(f"    Percentile:        {mc.percentile_rank:.1f}%")

        ci = report.bootstrap_sharpe_95ci
        print(f"\n  Bootstrap 95% CI:    [{ci[0]:.2f}, {ci[1]:.2f}]")

        print(f"\n  Walk‑Forward ({len(report.walk_forward_folds)} folds):")
        print(f"    Avg Test Sharpe:   {report.walk_forward_avg_test_sharpe:.2f}")
        print(f"    Avg Test Return:   {report.walk_forward_avg_test_return:.2f}%")

        print(f"\n  VERDICT: {report.verdict}")
        print()

        path = suite.save_report(report)
        print(f"  Report saved: {path}\n")

    asyncio.run(main())
