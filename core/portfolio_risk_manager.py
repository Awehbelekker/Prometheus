"""
Portfolio Risk Manager for PROMETHEUS Trading Platform
======================================================
Real risk analytics: Value-at-Risk (VaR), Conditional VaR (CVaR/ES),
Maximum Drawdown, Position Sizing, Correlation Risk, and Concentration Risk.

Uses actual portfolio data and historical returns — no mock numbers.
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from collections import deque
import math

logger = logging.getLogger(__name__)


@dataclass
class RiskMetrics:
    """Complete risk metrics for a portfolio or position"""
    timestamp: str
    # Value-at-Risk
    var_95: float = 0.0         # 95% VaR (dollar loss)
    var_99: float = 0.0         # 99% VaR (dollar loss)
    var_95_pct: float = 0.0     # 95% VaR as % of portfolio
    var_99_pct: float = 0.0     # 99% VaR as % of portfolio
    # Conditional VaR (Expected Shortfall)
    cvar_95: float = 0.0        # 95% CVaR
    cvar_99: float = 0.0        # 99% CVaR
    # Drawdown
    max_drawdown: float = 0.0   # Maximum drawdown as fraction
    max_drawdown_dollar: float = 0.0
    current_drawdown: float = 0.0
    # Volatility
    daily_volatility: float = 0.0
    annualized_volatility: float = 0.0
    # Ratios
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    # Concentration
    herfindahl_index: float = 0.0   # 0-1, higher = more concentrated
    largest_position_pct: float = 0.0
    # Position sizing
    kelly_fraction: float = 0.0
    optimal_position_size: float = 0.0
    # Summary
    risk_level: str = "unknown"     # low, moderate, elevated, high, extreme
    warnings: List[str] = field(default_factory=list)


@dataclass
class PositionRisk:
    """Risk metrics for a single position"""
    symbol: str
    weight: float               # fraction of portfolio
    market_value: float
    unrealized_pnl: float
    var_95: float
    contribution_to_risk: float # how much this position contributes to portfolio risk
    beta: float = 1.0
    correlation_to_portfolio: float = 0.0


class PortfolioRiskManager:
    """
    PROMETHEUS Portfolio Risk Manager

    Computes real risk metrics from actual return series.
    Supports parametric (normal), historical simulation, and
    Cornish-Fisher VaR approaches.
    """

    TRADING_DAYS_PER_YEAR = 252
    RISK_FREE_RATE = 0.05       # 5% annual (T-bill proxy)

    def __init__(self):
        # Return history per symbol and portfolio-level
        self._portfolio_returns: deque = deque(maxlen=756)  # ~3 years daily
        self._symbol_returns: Dict[str, deque] = {}
        self._portfolio_values: deque = deque(maxlen=756)
        self._peak_value: float = 0.0
        self._available = True
        self._calculations_run = 0

        logger.info("Portfolio Risk Manager initialized")

    def is_available(self) -> bool:
        return self._available

    # ------------------------------------------------------------------
    # Data ingestion
    # ------------------------------------------------------------------

    def record_portfolio_value(self, total_value: float):
        """Record a portfolio value snapshot (call daily or per-trade)."""
        if total_value <= 0:
            return
        self._portfolio_values.append(total_value)
        if total_value > self._peak_value:
            self._peak_value = total_value

        if len(self._portfolio_values) >= 2:
            prev = self._portfolio_values[-2]
            if prev > 0:
                ret = (total_value - prev) / prev
                self._portfolio_returns.append(ret)

    def record_symbol_return(self, symbol: str, daily_return: float):
        """Record a single-day return for a symbol."""
        if symbol not in self._symbol_returns:
            self._symbol_returns[symbol] = deque(maxlen=756)
        self._symbol_returns[symbol].append(daily_return)

    def ingest_price_series(self, symbol: str, prices: List[float]):
        """Ingest a price series and compute returns from it."""
        if len(prices) < 2:
            return
        if symbol not in self._symbol_returns:
            self._symbol_returns[symbol] = deque(maxlen=756)
        for i in range(1, len(prices)):
            if prices[i - 1] > 0:
                ret = (prices[i] - prices[i - 1]) / prices[i - 1]
                self._symbol_returns[symbol].append(ret)

    # ------------------------------------------------------------------
    # Core VaR / CVaR
    # ------------------------------------------------------------------

    def _compute_var(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """Historical simulation VaR (returns are fractional, result is fractional loss)."""
        if len(returns) < 5:
            return 0.0
        # VaR is the negative percentile of the return distribution
        alpha = 1.0 - confidence
        var = -np.percentile(returns, alpha * 100)
        return max(var, 0.0)

    def _compute_cvar(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """Conditional VaR (Expected Shortfall) — average loss beyond VaR threshold."""
        if len(returns) < 5:
            return 0.0
        alpha = 1.0 - confidence
        threshold = np.percentile(returns, alpha * 100)
        tail_losses = returns[returns <= threshold]
        if len(tail_losses) == 0:
            return self._compute_var(returns, confidence)
        return -np.mean(tail_losses)

    def _compute_parametric_var(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """Parametric (normal) VaR using Cornish-Fisher expansion for skew/kurtosis."""
        if len(returns) < 10:
            return 0.0
        mu = np.mean(returns)
        sigma = np.std(returns, ddof=1)
        if sigma == 0:
            return 0.0

        from scipy.stats import norm
        z = norm.ppf(1 - confidence)

        # Cornish-Fisher adjustment
        skew = float(np.mean(((returns - mu) / sigma) ** 3))
        kurt = float(np.mean(((returns - mu) / sigma) ** 4)) - 3.0  # excess kurtosis

        z_cf = (z +
                (z ** 2 - 1) * skew / 6 +
                (z ** 3 - 3 * z) * kurt / 24 -
                (2 * z ** 3 - 5 * z) * (skew ** 2) / 36)

        var = -(mu + z_cf * sigma)
        return max(var, 0.0)

    # ------------------------------------------------------------------
    # Drawdown
    # ------------------------------------------------------------------

    def _compute_max_drawdown(self, values: List[float]) -> Tuple[float, float]:
        """Compute max drawdown from a value series. Returns (fraction, dollar_amount)."""
        if len(values) < 2:
            return 0.0, 0.0
        peak = values[0]
        max_dd_frac = 0.0
        max_dd_dollar = 0.0
        for v in values:
            if v > peak:
                peak = v
            dd = (peak - v) / peak if peak > 0 else 0.0
            dd_dollar = peak - v
            if dd > max_dd_frac:
                max_dd_frac = dd
                max_dd_dollar = dd_dollar
        return max_dd_frac, max_dd_dollar

    def _current_drawdown(self) -> float:
        """Current drawdown from peak."""
        if not self._portfolio_values or self._peak_value <= 0:
            return 0.0
        current = self._portfolio_values[-1]
        return (self._peak_value - current) / self._peak_value

    # ------------------------------------------------------------------
    # Risk ratios
    # ------------------------------------------------------------------

    def _sharpe_ratio(self, returns: np.ndarray) -> float:
        """Annualized Sharpe ratio."""
        if len(returns) < 10:
            return 0.0
        daily_rf = self.RISK_FREE_RATE / self.TRADING_DAYS_PER_YEAR
        excess = returns - daily_rf
        mu = np.mean(excess)
        sigma = np.std(excess, ddof=1)
        if sigma == 0:
            return 0.0
        return float(mu / sigma * np.sqrt(self.TRADING_DAYS_PER_YEAR))

    def _sortino_ratio(self, returns: np.ndarray) -> float:
        """Annualized Sortino ratio (downside deviation only)."""
        if len(returns) < 10:
            return 0.0
        daily_rf = self.RISK_FREE_RATE / self.TRADING_DAYS_PER_YEAR
        excess = returns - daily_rf
        mu = np.mean(excess)
        downside = excess[excess < 0]
        if len(downside) == 0:
            return float('inf') if mu > 0 else 0.0
        down_std = np.std(downside, ddof=1)
        if down_std == 0:
            return 0.0
        return float(mu / down_std * np.sqrt(self.TRADING_DAYS_PER_YEAR))

    def _calmar_ratio(self, returns: np.ndarray, max_dd: float) -> float:
        """Calmar ratio = annualized return / max drawdown."""
        if max_dd == 0 or len(returns) < 10:
            return 0.0
        annual_return = float(np.mean(returns) * self.TRADING_DAYS_PER_YEAR)
        return annual_return / max_dd

    # ------------------------------------------------------------------
    # Position sizing (Kelly Criterion)
    # ------------------------------------------------------------------

    def _kelly_fraction(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Kelly criterion for optimal position sizing.
        f* = (p * b - q) / b
        where p = win_rate, q = 1-p, b = avg_win/avg_loss
        """
        if avg_loss == 0 or win_rate <= 0 or win_rate >= 1:
            return 0.0
        b = abs(avg_win / avg_loss)
        q = 1.0 - win_rate
        kelly = (win_rate * b - q) / b
        # Half-Kelly is safer in practice
        return max(0.0, min(kelly * 0.5, 0.25))  # cap at 25%

    def _compute_kelly_from_returns(self, returns: np.ndarray) -> float:
        """Derive Kelly fraction from a return series."""
        if len(returns) < 20:
            return 0.0
        wins = returns[returns > 0]
        losses = returns[returns < 0]
        if len(wins) == 0 or len(losses) == 0:
            return 0.0
        win_rate = len(wins) / len(returns)
        avg_win = float(np.mean(wins))
        avg_loss = float(np.mean(np.abs(losses)))
        return self._kelly_fraction(win_rate, avg_win, avg_loss)

    # ------------------------------------------------------------------
    # Concentration risk
    # ------------------------------------------------------------------

    def _herfindahl_index(self, weights: List[float]) -> float:
        """Herfindahl-Hirschman Index of portfolio concentration. 1/n = perfectly diversified."""
        if not weights:
            return 0.0
        total = sum(abs(w) for w in weights)
        if total == 0:
            return 0.0
        normalized = [abs(w) / total for w in weights]
        return sum(w ** 2 for w in normalized)

    # ------------------------------------------------------------------
    # Main computation
    # ------------------------------------------------------------------

    def compute_portfolio_risk(
        self,
        portfolio_value: float,
        positions: Optional[List[Dict[str, Any]]] = None,
    ) -> RiskMetrics:
        """
        Compute comprehensive risk metrics for the portfolio.

        positions: list of dicts with keys: symbol, market_value, unrealized_pnl
        """
        self._calculations_run += 1
        now = datetime.now().isoformat()
        returns = np.array(list(self._portfolio_returns)) if self._portfolio_returns else np.array([])
        values = list(self._portfolio_values) if self._portfolio_values else []

        metrics = RiskMetrics(timestamp=now)
        warnings = []

        if len(returns) < 5:
            warnings.append(f"Insufficient return history ({len(returns)} days). Need >=5 for VaR. Metrics are estimates.")

        # ---- VaR / CVaR ----
        if len(returns) >= 5:
            metrics.var_95_pct = round(self._compute_var(returns, 0.95), 6)
            metrics.var_99_pct = round(self._compute_var(returns, 0.99), 6)
            metrics.var_95 = round(metrics.var_95_pct * portfolio_value, 2)
            metrics.var_99 = round(metrics.var_99_pct * portfolio_value, 2)

            metrics.cvar_95 = round(self._compute_cvar(returns, 0.95) * portfolio_value, 2)
            metrics.cvar_99 = round(self._compute_cvar(returns, 0.99) * portfolio_value, 2)

        # ---- Volatility ----
        if len(returns) >= 5:
            metrics.daily_volatility = round(float(np.std(returns, ddof=1)), 6)
            metrics.annualized_volatility = round(metrics.daily_volatility * np.sqrt(self.TRADING_DAYS_PER_YEAR), 4)

        # ---- Drawdown ----
        if values:
            metrics.max_drawdown, metrics.max_drawdown_dollar = self._compute_max_drawdown(values)
            metrics.max_drawdown = round(metrics.max_drawdown, 4)
            metrics.max_drawdown_dollar = round(metrics.max_drawdown_dollar, 2)
            metrics.current_drawdown = round(self._current_drawdown(), 4)

        # ---- Risk ratios ----
        if len(returns) >= 10:
            metrics.sharpe_ratio = round(self._sharpe_ratio(returns), 3)
            metrics.sortino_ratio = round(self._sortino_ratio(returns), 3)
            metrics.calmar_ratio = round(self._calmar_ratio(returns, metrics.max_drawdown), 3)

        # ---- Kelly ----
        if len(returns) >= 20:
            metrics.kelly_fraction = round(self._compute_kelly_from_returns(returns), 4)
            metrics.optimal_position_size = round(metrics.kelly_fraction * portfolio_value, 2)

        # ---- Concentration ----
        if positions:
            weights = [p.get('market_value', 0) for p in positions]
            total_val = sum(abs(w) for w in weights)
            metrics.herfindahl_index = round(self._herfindahl_index(weights), 4)
            if total_val > 0:
                metrics.largest_position_pct = round(max(abs(w) for w in weights) / total_val, 4)
            else:
                metrics.largest_position_pct = 0.0

            # Concentration warnings
            if metrics.herfindahl_index > 0.5:
                warnings.append(f"High concentration risk: HHI={metrics.herfindahl_index:.2f}. Consider diversifying.")
            if metrics.largest_position_pct > 0.3:
                warnings.append(f"Single position is {metrics.largest_position_pct*100:.0f}% of portfolio. Max recommended: 20%.")

        # ---- Risk level classification ----
        if metrics.annualized_volatility > 0.6 or metrics.max_drawdown > 0.3 or metrics.var_95_pct > 0.05:
            metrics.risk_level = "extreme"
            warnings.append("EXTREME risk level. Consider reducing exposure immediately.")
        elif metrics.annualized_volatility > 0.4 or metrics.max_drawdown > 0.2 or metrics.var_95_pct > 0.03:
            metrics.risk_level = "high"
            warnings.append("High risk level. Review position sizes.")
        elif metrics.annualized_volatility > 0.25 or metrics.max_drawdown > 0.1:
            metrics.risk_level = "elevated"
        elif metrics.annualized_volatility > 0.12:
            metrics.risk_level = "moderate"
        else:
            metrics.risk_level = "low"

        # Additional warnings
        if metrics.sharpe_ratio < 0 and len(returns) >= 20:
            warnings.append(f"Negative Sharpe ratio ({metrics.sharpe_ratio:.2f}). Strategy is underperforming risk-free rate.")
        if metrics.current_drawdown > 0.15:
            warnings.append(f"Current drawdown is {metrics.current_drawdown*100:.1f}%. Consider risk reduction.")

        metrics.warnings = warnings
        return metrics

    def compute_position_risk(
        self,
        symbol: str,
        market_value: float,
        portfolio_value: float,
        unrealized_pnl: float = 0.0,
    ) -> PositionRisk:
        """Compute risk metrics for a single position."""
        weight = market_value / portfolio_value if portfolio_value > 0 else 0.0

        returns = np.array(list(self._symbol_returns.get(symbol, [])))
        var_95 = 0.0
        if len(returns) >= 5:
            var_95_pct = self._compute_var(returns, 0.95)
            var_95 = var_95_pct * abs(market_value)

        # Contribution to risk = weight * individual volatility * correlation
        port_returns = np.array(list(self._portfolio_returns))
        correlation = 0.0
        beta = 1.0
        if len(returns) >= 10 and len(port_returns) >= 10:
            min_len = min(len(returns), len(port_returns))
            r_sym = returns[-min_len:]
            r_port = port_returns[-min_len:]
            if np.std(r_sym) > 0 and np.std(r_port) > 0:
                correlation = float(np.corrcoef(r_sym, r_port)[0, 1])
                var_port = np.var(r_port)
                if var_port > 0:
                    beta = float(np.cov(r_sym, r_port)[0, 1] / var_port)

        contrib = weight * float(np.std(returns)) * abs(correlation) if len(returns) >= 5 else 0.0

        return PositionRisk(
            symbol=symbol,
            weight=round(weight, 4),
            market_value=round(market_value, 2),
            unrealized_pnl=round(unrealized_pnl, 2),
            var_95=round(var_95, 2),
            contribution_to_risk=round(contrib, 6),
            beta=round(beta, 3),
            correlation_to_portfolio=round(correlation, 3),
        )

    def suggest_position_size(
        self,
        symbol: str,
        portfolio_value: float,
        max_risk_per_trade: float = 0.02,  # 2% of portfolio
    ) -> Dict[str, Any]:
        """Suggest position size based on volatility and risk budget."""
        returns = np.array(list(self._symbol_returns.get(symbol, [])))
        if len(returns) < 10:
            # Fallback: assume 2% daily vol
            daily_vol = 0.02
        else:
            daily_vol = float(np.std(returns, ddof=1))

        if daily_vol == 0:
            daily_vol = 0.01

        # Risk budget approach: max_loss = position_size * daily_vol * z_score
        z_95 = 1.645
        max_position = (max_risk_per_trade * portfolio_value) / (daily_vol * z_95)

        # Kelly-based suggestion
        kelly = self._compute_kelly_from_returns(returns) if len(returns) >= 20 else 0.05
        kelly_position = kelly * portfolio_value

        suggested = min(max_position, kelly_position) if kelly_position > 0 else max_position

        return {
            "symbol": symbol,
            "portfolio_value": portfolio_value,
            "max_risk_per_trade": f"{max_risk_per_trade*100:.1f}%",
            "daily_volatility": round(daily_vol, 4),
            "risk_budget_position": round(max_position, 2),
            "kelly_position": round(kelly_position, 2),
            "suggested_position": round(suggested, 2),
            "suggested_pct_of_portfolio": round(suggested / portfolio_value * 100, 1) if portfolio_value > 0 else 0,
        }

    def get_status(self) -> Dict[str, Any]:
        """Get risk manager status."""
        return {
            "name": "Portfolio Risk Manager",
            "available": self._available,
            "calculations_run": self._calculations_run,
            "portfolio_return_history": len(self._portfolio_returns),
            "symbols_tracked": len(self._symbol_returns),
            "symbol_history_lengths": {s: len(d) for s, d in self._symbol_returns.items()},
            "peak_portfolio_value": round(self._peak_value, 2),
            "current_drawdown": round(self._current_drawdown(), 4),
        }


# Singleton
_risk_manager: Optional[PortfolioRiskManager] = None

def get_risk_manager() -> PortfolioRiskManager:
    """Get or create the risk manager singleton."""
    global _risk_manager
    if _risk_manager is None:
        _risk_manager = PortfolioRiskManager()
    return _risk_manager
