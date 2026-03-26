#!/usr/bin/env python3
"""
Cross-Asset Correlation Tracker
=================================
Learns inter-market correlations from historical data and surfaces
signals about correlation breakdowns (divergences) that often precede
large moves.

Tracked asset pairs:
  - Equity indices: SPY / QQQ / DIA / IWM
  - Risk gauges:    SPY vs VIX  (inverse correlation)
  - Sector rotations: XLK vs XLE, XLF vs TLT
  - Crypto correlation: BTC-USD vs ETH-USD
  - Bond/equity: TLT vs SPY

Outputs:
  - Rolling 20-day and 60-day correlation matrices
  - Divergence alerts when correlation breaks >2 sigma
  - Hedging suggestions (if long SPY, check VIX, TLT)
"""

import logging
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Default universe of correlated pairs
DEFAULT_UNIVERSE = [
    "SPY", "QQQ", "DIA", "IWM",   # Equity indices
    "TLT", "HYG",                  # Bonds
    "GLD", "SLV",                  # Metals
    "XLK", "XLE", "XLF",          # Sectors
]

# Known inverse / hedge relationships
HEDGE_MAP = {
    "SPY":  ["VIX", "TLT", "GLD"],
    "QQQ":  ["VIX", "TLT"],
    "DIA":  ["VIX", "TLT"],
    "IWM":  ["VIX", "TLT"],
    "XLK":  ["XLE"],   # Growth vs value rotation
    "XLE":  ["XLK"],
    "XLF":  ["TLT"],   # Financials inversely correlated with bonds
    "TLT":  ["SPY", "HYG"],
    "BTC-USD": ["ETH-USD"],
}


@dataclass
class CorrelationAlert:
    pair: Tuple[str, str]
    window: int
    expected_corr: float
    current_corr: float
    z_score: float
    alert_type: str        # DIVERGENCE | CONVERGENCE
    timestamp: str = ""


@dataclass
class CorrelationSnapshot:
    window: int
    matrix: Dict[str, Dict[str, float]]   # symbol -> symbol -> correlation
    timestamp: str = ""


class CrossAssetCorrelationTracker:
    """
    Computes rolling correlations between assets and detects divergences.
    Uses yfinance for historical prices (free, no API key).
    """

    DIVERGENCE_Z_THRESHOLD = 2.0  # 2-sigma divergence alert
    SHORT_WINDOW = 20
    LONG_WINDOW = 60

    def __init__(self, symbols: List[str] = None):
        self.symbols = symbols or DEFAULT_UNIVERSE
        self._price_cache: Dict[str, np.ndarray] = {}
        self._corr_short: Optional[CorrelationSnapshot] = None
        self._corr_long: Optional[CorrelationSnapshot] = None
        self._alerts: List[CorrelationAlert] = []
        self._last_update = None
        self._update_interval = timedelta(hours=1)
        logger.info(f"Cross-Asset Correlation Tracker initialized: {len(self.symbols)} assets")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, force: bool = False) -> bool:
        """Refresh price data + correlation matrices. Returns True if updated."""
        if not force and self._last_update and datetime.now(timezone.utc) - self._last_update < self._update_interval:
            return False

        try:
            self._fetch_prices()
            if len(self._price_cache) < 2:
                logger.warning("Not enough price data for correlations")
                return False

            self._compute_correlations()
            self._detect_divergences()
            self._last_update = datetime.now(timezone.utc)
            return True
        except Exception as e:
            logger.error(f"Correlation update failed: {e}")
            return False

    def get_correlation(self, sym_a: str, sym_b: str, window: int = 20) -> Optional[float]:
        """Get pairwise rolling correlation."""
        self.update()
        snap = self._corr_short if window <= 30 else self._corr_long
        if not snap:
            return None
        return snap.matrix.get(sym_a, {}).get(sym_b)

    def get_correlation_matrix(self, window: int = 20) -> Optional[Dict]:
        """Get full correlation matrix for the tracked universe."""
        self.update()
        snap = self._corr_short if window <= 30 else self._corr_long
        if snap:
            return {"window": snap.window, "matrix": snap.matrix, "timestamp": snap.timestamp}
        return None

    def get_divergence_alerts(self) -> List[Dict]:
        """Get active divergence alerts."""
        self.update()
        return [
            {
                "pair": list(a.pair),
                "window": a.window,
                "expected_corr": round(a.expected_corr, 3),
                "current_corr": round(a.current_corr, 3),
                "z_score": round(a.z_score, 2),
                "alert_type": a.alert_type,
                "timestamp": a.timestamp,
            }
            for a in self._alerts
        ]

    def get_hedge_suggestions(self, symbol: str) -> Dict:
        """Suggest hedges for a given symbol based on correlation data."""
        self.update()
        hedges = HEDGE_MAP.get(symbol, [])
        suggestions = []
        for hedge_sym in hedges:
            corr = self.get_correlation(symbol, hedge_sym, window=20)
            suggestions.append({
                "symbol": hedge_sym,
                "correlation_20d": round(corr, 3) if corr is not None else None,
                "type": "inverse" if (corr is not None and corr < 0) else "diversifier",
            })
        return {
            "for_symbol": symbol,
            "hedges": suggestions,
        }

    def get_summary(self) -> Dict:
        """JSON-friendly summary."""
        self.update()
        return {
            "symbols_tracked": self.symbols,
            "short_window": self.SHORT_WINDOW,
            "long_window": self.LONG_WINDOW,
            "active_alerts": len(self._alerts),
            "alerts": self.get_divergence_alerts()[:10],
            "last_updated": self._last_update.isoformat() if self._last_update else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _fetch_prices(self):
        """Fetch last 90 days of daily close prices from yfinance."""
        try:
            import yfinance as yf
        except ImportError:
            logger.warning("yfinance not installed — correlation tracker unavailable")
            return

        try:
            # Bulk download is faster
            tickers_str = " ".join(self.symbols)
            data = yf.download(tickers_str, period="90d", interval="1d", progress=False, threads=True)

            if data is None or data.empty:
                logger.warning("No price data returned")
                return

            close = data["Close"] if "Close" in data.columns else data.get("Adj Close")
            if close is None:
                logger.warning("No Close column in yfinance data")
                return

            # Handle single-symbol edge case
            if isinstance(close, np.ndarray) or (hasattr(close, 'ndim') and close.ndim == 1):
                if len(self.symbols) == 1:
                    self._price_cache[self.symbols[0]] = close.dropna().values
                return

            for sym in self.symbols:
                if sym in close.columns:
                    series = close[sym].dropna()
                    if len(series) >= self.LONG_WINDOW:
                        self._price_cache[sym] = series.values

            logger.info(f"Fetched prices for {len(self._price_cache)}/{len(self.symbols)} symbols")

        except Exception as e:
            logger.error(f"Price fetch failed: {e}")

    def _compute_correlations(self):
        """Compute rolling correlation matrices."""
        syms = list(self._price_cache.keys())
        if len(syms) < 2:
            return

        # Compute returns
        returns = {}
        min_len = min(len(self._price_cache[s]) for s in syms)
        for sym in syms:
            prices = self._price_cache[sym][-min_len:]
            rets = np.diff(np.log(prices + 1e-10))  # log returns
            returns[sym] = rets

        now_str = datetime.now(timezone.utc).isoformat()

        for window, attr in [(self.SHORT_WINDOW, "_corr_short"), (self.LONG_WINDOW, "_corr_long")]:
            matrix = {}
            for i, sym_a in enumerate(syms):
                matrix[sym_a] = {}
                for j, sym_b in enumerate(syms):
                    if i == j:
                        matrix[sym_a][sym_b] = 1.0
                    elif j < i:
                        matrix[sym_a][sym_b] = matrix[sym_b][sym_a]
                    else:
                        ra = returns[sym_a][-window:]
                        rb = returns[sym_b][-window:]
                        if len(ra) >= window and len(rb) >= window:
                            corr = np.corrcoef(ra, rb)[0, 1]
                            matrix[sym_a][sym_b] = float(corr) if np.isfinite(corr) else 0.0
                        else:
                            matrix[sym_a][sym_b] = 0.0

            setattr(self, attr, CorrelationSnapshot(
                window=window, matrix=matrix, timestamp=now_str
            ))

    def _detect_divergences(self):
        """Detect when short-term correlation deviates significantly from long-term."""
        self._alerts.clear()

        if not self._corr_short or not self._corr_long:
            return

        now_str = datetime.now(timezone.utc).isoformat()
        syms = list(self._corr_short.matrix.keys())

        for i, sym_a in enumerate(syms):
            for j in range(i + 1, len(syms)):
                sym_b = syms[j]
                short_corr = self._corr_short.matrix.get(sym_a, {}).get(sym_b)
                long_corr = self._corr_long.matrix.get(sym_a, {}).get(sym_b)

                if short_corr is None or long_corr is None:
                    continue

                # Simple z-score: how many sigma is the short-term corr from the long-term
                diff = abs(short_corr - long_corr)
                # Approximate std of correlation ~= 1/sqrt(window)
                std_approx = 1.0 / np.sqrt(self.SHORT_WINDOW)

                z = diff / std_approx if std_approx > 0 else 0

                if z >= self.DIVERGENCE_Z_THRESHOLD:
                    alert_type = "DIVERGENCE" if abs(short_corr) < abs(long_corr) else "CONVERGENCE"
                    self._alerts.append(CorrelationAlert(
                        pair=(sym_a, sym_b),
                        window=self.SHORT_WINDOW,
                        expected_corr=long_corr,
                        current_corr=short_corr,
                        z_score=z,
                        alert_type=alert_type,
                        timestamp=now_str,
                    ))

        if self._alerts:
            logger.info(f"Correlation tracker: {len(self._alerts)} divergence alerts")
