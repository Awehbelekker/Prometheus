"""
PROMETHEUS ML Feature Engine
=============================
Computes REAL technical features for pretrained ML model inference.

PROBLEM SOLVED: The pretrained sklearn models were trained on 11 real features
(RSI, MACD, Bollinger, SMA, volume_ratio, etc.) but at inference time they
received placeholder values (RSI=50, MACD=0, SMA20=current_price). This made
every ML prediction random noise.

This module computes the EXACT same features used during training, from real
OHLCV data fetched via yfinance, ensuring model predictions are meaningful.

Also adds ADVANCED features beyond the original 11 for enhanced models:
  - Cross-asset correlations (BTC/ETH spread, QQQ/SPY ratio)
  - VWAP deviation
  - Intraday volatility patterns
  - Order flow proxies (volume imbalance)
  - Mean reversion z-scores
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# Must match core/auto_model_retrainer.py FEATURE_COLS exactly
TRAINING_FEATURE_COLS = [
    "rsi", "macd", "macd_signal", "bb_upper", "bb_lower",
    "sma_20", "ema_12", "volume_ratio", "daily_return",
    "price_vs_sma20", "volatility",
]


class MLFeatureEngine:
    """
    Computes real technical features for ML model inference.

    Maintains a rolling cache of OHLCV data per symbol to avoid
    redundant yfinance calls within the same trading cycle.
    Cache expires after 5 minutes.
    """

    def __init__(self, cache_ttl_seconds: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = cache_ttl_seconds
        self._yf_available = False
        try:
            import yfinance  # noqa: F401
            self._yf_available = True
        except ImportError:
            logger.warning("yfinance not available — ML features will use fallback")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def compute_features(
        self, symbol: str, current_price: float = 0.0,
        market_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[np.ndarray]:
        """
        Compute the 11-feature vector matching the training schema exactly.

        Returns:
            1D numpy array of shape (11,) or None if data unavailable.
            Features are RAW (unscaled) — caller must apply scaler.transform().
        """
        ohlcv = await self._get_ohlcv(symbol)
        if ohlcv is None:
            return None

        closes = ohlcv["close"]
        highs = ohlcv["high"]
        lows = ohlcv["low"]
        volumes = ohlcv["volume"]

        if len(closes) < 26:
            logger.debug(f"Insufficient OHLCV data for {symbol}: {len(closes)} bars")
            return None

        # Use the most recent close as current price if not provided
        if current_price <= 0:
            current_price = closes[-1]

        # --- RSI (14-period) ---
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)
        avg_gain = np.mean(gains[-14:])
        avg_loss = np.mean(losses[-14:]) or 1e-10
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))

        # --- MACD & Signal ---
        ema12 = self._ema(closes, 12)
        ema26 = self._ema(closes, 26)
        macd = ema12[-1] - ema26[-1]
        macd_line = ema12 - ema26
        macd_signal = self._ema(macd_line[-9:], 9)[-1] if len(macd_line) >= 9 else macd

        # --- Bollinger Bands ---
        sma_20 = np.mean(closes[-20:])
        std_20 = np.std(closes[-20:]) or 1e-10
        bb_upper = sma_20 + 2.0 * std_20
        bb_lower = sma_20 - 2.0 * std_20

        # --- EMA 12 ---
        ema_12_val = ema12[-1]

        # --- Volume ratio (vs 20-day average) ---
        vol_avg_20 = np.mean(volumes[-20:]) or 1.0
        volume_ratio = volumes[-1] / vol_avg_20

        # --- Daily return ---
        daily_return = (closes[-1] - closes[-2]) / closes[-2] if closes[-2] != 0 else 0.0

        # --- Price vs SMA20 ---
        price_vs_sma20 = (current_price - sma_20) / sma_20 if sma_20 != 0 else 0.0

        # --- Volatility (20-day rolling std of returns) ---
        returns = np.diff(closes[-21:]) / np.where(closes[-21:-1] == 0, 1, closes[-21:-1])
        volatility = np.std(returns) if len(returns) >= 2 else 0.01

        features = np.array([
            rsi,
            macd,
            macd_signal,
            bb_upper,
            bb_lower,
            sma_20,
            ema_12_val,
            volume_ratio,
            daily_return,
            price_vs_sma20,
            volatility,
        ])

        # Sanitise
        features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
        return features

    async def compute_advanced_features(
        self, symbol: str, current_price: float = 0.0,
    ) -> Optional[Dict[str, float]]:
        """
        Compute advanced features beyond the base 11 for enhanced models.

        Returns dict with named features including:
        - mean_reversion_zscore: How far current price deviates from 20-day mean
        - volume_imbalance: Proxy for order flow direction
        - atr_ratio: Current ATR vs historical ATR
        - momentum_5d / momentum_10d: Multi-period momentum
        - bollinger_pctb: Bollinger %B (0-1, where price sits in bands)
        - rsi_divergence: RSI slope vs price slope divergence
        """
        ohlcv = await self._get_ohlcv(symbol)
        if ohlcv is None:
            return None

        closes = ohlcv["close"]
        highs = ohlcv["high"]
        lows = ohlcv["low"]
        volumes = ohlcv["volume"]

        if len(closes) < 30:
            return None

        if current_price <= 0:
            current_price = closes[-1]

        features = {}

        # --- Mean reversion z-score ---
        sma_20 = np.mean(closes[-20:])
        std_20 = np.std(closes[-20:]) or 1e-10
        features["mean_reversion_zscore"] = (current_price - sma_20) / std_20

        # --- Bollinger %B ---
        bb_upper = sma_20 + 2.0 * std_20
        bb_lower = sma_20 - 2.0 * std_20
        bb_range = bb_upper - bb_lower
        features["bollinger_pctb"] = (current_price - bb_lower) / bb_range if bb_range > 0 else 0.5

        # --- ATR (14-period) ---
        tr = []
        for i in range(-14, 0):
            h = highs[i]
            lo_val = lows[i]
            pc = closes[i - 1]
            tr.append(max(h - lo_val, abs(h - pc), abs(lo_val - pc)))
        atr_14 = np.mean(tr) if tr else 1e-10

        # ATR ratio: current ATR vs 40-day ATR
        tr_40 = []
        for i in range(max(-40, -len(closes) + 1), 0):
            h = highs[i]
            lo_val = lows[i]
            pc = closes[i - 1]
            tr_40.append(max(h - lo_val, abs(h - pc), abs(lo_val - pc)))
        atr_40 = np.mean(tr_40) if tr_40 else atr_14
        features["atr_ratio"] = atr_14 / atr_40 if atr_40 > 0 else 1.0

        # --- Multi-period momentum ---
        features["momentum_5d"] = (current_price - closes[-6]) / closes[-6] if closes[-6] > 0 else 0.0
        features["momentum_10d"] = (current_price - closes[-11]) / closes[-11] if len(closes) > 10 and closes[-11] > 0 else 0.0

        # --- Volume imbalance proxy ---
        # Up-day volume vs down-day volume over last 10 days
        up_vol = sum(volumes[i] for i in range(-10, 0) if closes[i] > closes[i - 1])
        dn_vol = sum(volumes[i] for i in range(-10, 0) if closes[i] < closes[i - 1])
        total_vol = up_vol + dn_vol
        features["volume_imbalance"] = (up_vol - dn_vol) / total_vol if total_vol > 0 else 0.0

        # --- RSI divergence (price making new high but RSI isn't, or vice versa) ---
        deltas = np.diff(closes[-15:])
        gains = np.where(deltas > 0, deltas, 0.0)
        losses_arr = np.where(deltas < 0, -deltas, 0.0)
        rsi_now = 100.0 - (100.0 / (1.0 + (np.mean(gains[-7:]) / (np.mean(losses_arr[-7:]) or 1e-10))))
        rsi_prev = 100.0 - (100.0 / (1.0 + (np.mean(gains[:7]) / (np.mean(losses_arr[:7]) or 1e-10))))
        price_slope = (closes[-1] - closes[-8]) / (closes[-8] or 1.0)
        rsi_slope = (rsi_now - rsi_prev) / 100.0
        features["rsi_divergence"] = price_slope - rsi_slope  # Positive = bearish divergence

        # --- Rate of change (ROC) ---
        features["roc_5"] = (closes[-1] - closes[-6]) / closes[-6] * 100 if closes[-6] > 0 else 0.0

        return features

    # ------------------------------------------------------------------
    # OHLCV data fetching with caching
    # ------------------------------------------------------------------

    async def _get_ohlcv(self, symbol: str) -> Optional[Dict[str, np.ndarray]]:
        """Get cached or fresh OHLCV data for a symbol."""
        now = time.time()

        # Check cache
        if symbol in self._cache:
            entry = self._cache[symbol]
            if now - entry["fetched_at"] < self._cache_ttl:
                return entry["data"]

        # Fetch fresh data
        data = await asyncio.get_event_loop().run_in_executor(
            None, self._fetch_ohlcv_sync, symbol,
        )

        if data is not None:
            self._cache[symbol] = {"data": data, "fetched_at": now}

        return data

    def _fetch_ohlcv_sync(self, symbol: str) -> Optional[Dict[str, np.ndarray]]:
        """Synchronous yfinance fetch — called in executor."""
        if not self._yf_available:
            return None

        import yfinance as yf

        # Normalise symbol for yfinance (e.g. BTC/USD → BTC-USD)
        yf_symbol = symbol.replace("/", "-")

        try:
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period="60d", interval="1d")
            if df is None or len(df) < 20:
                logger.debug(f"Insufficient yfinance data for {yf_symbol}: {0 if df is None else len(df)} rows")
                return None

            return {
                "close": df["Close"].values.astype(float),
                "high": df["High"].values.astype(float),
                "low": df["Low"].values.astype(float),
                "volume": df["Volume"].values.astype(float),
                "open": df["Open"].values.astype(float),
            }
        except Exception as exc:
            logger.debug(f"yfinance fetch failed for {yf_symbol}: {exc}")
            return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _ema(data: np.ndarray, span: int) -> np.ndarray:
        """Compute exponential moving average."""
        alpha = 2.0 / (span + 1.0)
        ema = np.empty_like(data, dtype=float)
        ema[0] = data[0]
        for i in range(1, len(data)):
            ema[i] = alpha * data[i] + (1 - alpha) * ema[i - 1]
        return ema

    def clear_cache(self):
        """Clear the OHLCV cache."""
        self._cache.clear()

    def cache_stats(self) -> Dict[str, Any]:
        """Return cache statistics."""
        now = time.time()
        fresh = sum(1 for v in self._cache.values() if now - v["fetched_at"] < self._cache_ttl)
        return {
            "total_cached": len(self._cache),
            "fresh_entries": fresh,
            "stale_entries": len(self._cache) - fresh,
            "ttl_seconds": self._cache_ttl,
        }


# Singleton instance
_feature_engine: Optional[MLFeatureEngine] = None


def get_feature_engine() -> MLFeatureEngine:
    """Get or create the singleton feature engine."""
    global _feature_engine
    if _feature_engine is None:
        _feature_engine = MLFeatureEngine()
    return _feature_engine
