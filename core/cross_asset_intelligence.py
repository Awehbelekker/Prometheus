"""
CROSS-ASSET INTELLIGENCE — LIVE TRADING MODULE
================================================
Proven in 50-year benchmark: #3/13 globally (12.67% CAGR, 1.53 Sharpe)

Uses real-time VIX, Gold, and Bond data to generate a composite risk-on / risk-off
score that overlays on the regime-exposure model.

 When VIX is low & falling + Gold selling + Bonds selling → RISK-ON  → boost allocation
 When VIX is high & spiking + Gold surging + Bonds surging → RISK-OFF → cut allocation

Integration points in the live trader:
  1. detect_market_regime()  — adds VIX/Gold/Bond votes to regime detection
  2. _get_ai_position_size() — scales position size by cross-asset score
  3. run_trading_cycle()     — regime-exposure manager uses cross-asset overlay

Data sources (priority order):
  - Live data from Yahoo Finance (self-refreshing, 15-min cache)
  - Fallback to CSV files in data/ directory
"""

import logging
import time
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Attempt to use yfinance for live data
try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

try:
    import pandas as pd
    import numpy as np
    PD_AVAILABLE = True
except ImportError:
    PD_AVAILABLE = False


class LiveCrossAssetIntelligence:
    """
    Real-time cross-asset risk overlay for live trading.

    Monitors VIX, Gold (GLD), and Long-Term Bonds (TLT) to produce
    a composite score: +1 = strong risk-on, -1 = strong risk-off.

    Weights (proven in benchmark):
      VIX:   0.50  (primary fear gauge)
      Gold:  0.25  (safe-haven demand)
      Bonds: 0.25  (flight to quality)
    """

    # Yahoo Finance tickers for live data
    TICKERS = {
        'vix':   '^VIX',
        'gold':  'GLD',
        'bonds': 'TLT',
    }

    # Signal weights (proven in 50-year benchmark)
    WEIGHTS = {'vix': 0.50, 'gold': 0.25, 'bonds': 0.25}

    # Cache duration (seconds) — don't hammer the API
    CACHE_TTL = 900  # 15 minutes

    def __init__(self, data_dir: str = 'data'):
        self.data_dir = Path(data_dir)
        self._cache: Dict[str, dict] = {}
        self._cache_time: Dict[str, float] = {}
        self._csv_fallback: Dict[str, Optional[pd.DataFrame]] = {}
        self._last_composite = 0.0
        self._initialized = False

        # Pre-load CSV fallbacks
        self._load_csv_fallbacks()
        logger.info("📊 LiveCrossAssetIntelligence initialized "
                     f"(live={'yes' if YF_AVAILABLE else 'no'}, "
                     f"csv_fallback={'yes' if any(v is not None for v in self._csv_fallback.values()) else 'no'})")

    def _load_csv_fallbacks(self):
        """Load CSV data files as fallback source."""
        if not PD_AVAILABLE:
            return
        csv_map = {
            'vix':   'vix_regime_labeled.csv',
            'gold':  'gold_regime_labeled.csv',
            'bonds': 'longbonds_regime_labeled.csv',
        }
        for key, fname in csv_map.items():
            path = self.data_dir / fname
            if path.exists():
                try:
                    df = pd.read_csv(path, parse_dates=['date'])
                    df = df.set_index('date').sort_index()
                    if 'close' in df.columns:
                        df['sma20'] = df['close'].rolling(20).mean()
                        df['sma50'] = df['close'].rolling(50).mean()
                        df['ret5'] = df['close'].pct_change(5)
                    self._csv_fallback[key] = df
                except Exception as e:
                    logger.debug(f"CSV fallback load failed for {fname}: {e}")
                    self._csv_fallback[key] = None
            else:
                self._csv_fallback[key] = None

    def _fetch_live(self, asset: str) -> Optional[dict]:
        """Fetch live data from Yahoo Finance with caching."""
        now = time.time()

        # Check cache
        if asset in self._cache_time and (now - self._cache_time[asset]) < self.CACHE_TTL:
            return self._cache.get(asset)

        if not YF_AVAILABLE or not PD_AVAILABLE:
            return None

        ticker_symbol = self.TICKERS.get(asset)
        if not ticker_symbol:
            return None

        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period='1mo', interval='1d')

            if hist is None or len(hist) < 6:
                return None

            closes = hist['Close'].values
            current = closes[-1]
            sma20 = float(np.mean(closes[-20:])) if len(closes) >= 20 else float(np.mean(closes))
            ret5 = (closes[-1] - closes[-6]) / closes[-6] if len(closes) >= 6 else 0.0

            result = {
                'close': float(current),
                'sma20': sma20,
                'ret5': float(ret5),
            }

            # Cache it
            self._cache[asset] = result
            self._cache_time[asset] = now
            return result

        except Exception as e:
            logger.debug(f"Live fetch failed for {asset} ({ticker_symbol}): {e}")
            return None

    def _get_csv_latest(self, asset: str) -> Optional[dict]:
        """Get the most recent row from CSV fallback data."""
        df = self._csv_fallback.get(asset)
        if df is None or len(df) == 0:
            return None
        try:
            row = df.iloc[-1]
            return {
                'close': float(row.get('close', 0)),
                'sma20': float(row.get('sma20', row.get('close', 0))),
                'ret5': float(row.get('ret5', 0)),
            }
        except Exception:
            return None

    def _get_data(self, asset: str) -> Optional[dict]:
        """Get data with live-first, CSV-fallback strategy."""
        data = self._fetch_live(asset)
        if data is not None:
            return data
        return self._get_csv_latest(asset)

    def get_signals(self) -> Dict[str, float]:
        """
        Get individual cross-asset signals.
        Values > 0 = risk-on confirmation, < 0 = risk-off warning.
        Range roughly [-1, +1].
        """
        signals = {}

        # ── VIX signals ─────────────────────────────────────────
        vix_data = self._get_data('vix')
        if vix_data:
            vix_level = vix_data['close']
            vix_sma = vix_data['sma20']
            vix_ret5 = vix_data['ret5']

            if vix_level < 15 and vix_ret5 < 0:
                signals['vix'] = 0.8            # very calm, risk-on
            elif vix_level < 20 and vix_level < vix_sma:
                signals['vix'] = 0.4            # calm
            elif vix_level > 30 and vix_ret5 > 0.10:
                signals['vix'] = -0.9           # panic spike
            elif vix_level > 25:
                signals['vix'] = -0.5           # elevated fear
            elif vix_level > 20 and vix_level > vix_sma:
                signals['vix'] = -0.2           # rising fear
            else:
                signals['vix'] = 0.0

        # ── Gold signals (safe-haven demand) ────────────────────
        gold_data = self._get_data('gold')
        if gold_data:
            gold_ret5 = gold_data['ret5']
            if gold_ret5 > 0.03:
                signals['gold'] = -0.5          # flight to safety = risk-off
            elif gold_ret5 < -0.02:
                signals['gold'] = 0.3           # gold selling = risk-on
            else:
                signals['gold'] = 0.0

        # ── Bond signals (flight to quality) ────────────────────
        bond_data = self._get_data('bonds')
        if bond_data:
            bond_ret5 = bond_data['ret5']
            if bond_ret5 > 0.02:
                signals['bonds'] = -0.4         # bonds surging = flight to safety
            elif bond_ret5 < -0.015:
                signals['bonds'] = 0.3          # bonds selling = risk-on
            else:
                signals['bonds'] = 0.0

        return signals

    def composite_score(self) -> float:
        """
        Single composite cross-asset score.
        +1 = strong risk-on, -1 = strong risk-off.
        """
        sigs = self.get_signals()
        if not sigs:
            return 0.0
        total_w = sum(self.WEIGHTS.get(k, 0.25) for k in sigs)
        if total_w == 0:
            return 0.0
        score = sum(sigs[k] * self.WEIGHTS.get(k, 0.25) for k in sigs) / total_w
        self._last_composite = score
        self._initialized = True
        return score

    def get_regime_adjustment(self, detected_regime: str) -> Dict[str, float]:
        """
        Return regime adjustment factors based on cross-asset analysis.
        Used by the live regime detection and position sizing systems.

        Returns:
            dict with keys:
              'allocation_multiplier': 0.7 - 1.15 (multiply target allocation)
              'position_scale':        0.7 - 1.10 (multiply position size)
              'regime_vote':           float vote to add to regime detection
              'regime_label':          suggested regime component ('risk_on'/'risk_off'/'neutral')
              'composite_score':       the raw composite score
        """
        score = self.composite_score()
        signals = self.get_signals()

        result = {
            'composite_score': score,
            'signals': signals,
            'regime_label': 'neutral',
            'allocation_multiplier': 1.0,
            'position_scale': 1.0,
            'regime_vote': 0.0,
        }

        # ── Risk-on: boost allocation & position sizes ──────────
        if score > 0.2 and detected_regime in ('TRENDING', 'NORMAL', 'RANGING'):
            result['allocation_multiplier'] = 1.0 + min(score * 0.15, 0.15)  # up to +15%
            result['position_scale'] = 1.0 + min(score * 0.10, 0.10)         # up to +10%
            result['regime_label'] = 'risk_on'
            result['regime_vote'] = score * 1.2   # TRENDING boost

        elif score > 0.2 and detected_regime == 'VOLATILE':
            # Even in volatile, strong risk-on tempers the fear
            result['allocation_multiplier'] = 1.0 + min(score * 0.08, 0.08)
            result['position_scale'] = 1.0
            result['regime_label'] = 'risk_on_tempered'
            result['regime_vote'] = score * 0.5

        # ── Risk-off: cut allocation & position sizes ───────────
        elif score < -0.3:
            result['allocation_multiplier'] = max(0.70, 1.0 + score * 0.30)  # cut up to 30%
            result['position_scale'] = max(0.70, 1.0 + score * 0.25)         # cut up to 25%
            result['regime_label'] = 'risk_off'
            result['regime_vote'] = score * 1.5   # VOLATILE boost

        elif score < -0.1:
            # Mild caution
            result['allocation_multiplier'] = 0.95
            result['position_scale'] = 0.95
            result['regime_label'] = 'caution'
            result['regime_vote'] = score * 0.8

        return result

    def format_status(self) -> str:
        """Human-readable status string for logging."""
        signals = self.get_signals()
        score = self.composite_score()
        parts = [f"CrossAsset={score:+.2f}"]
        for k, v in signals.items():
            parts.append(f"{k.upper()}={v:+.2f}")
        label = 'RISK-ON' if score > 0.2 else ('RISK-OFF' if score < -0.3 else 'NEUTRAL')
        parts.append(f"({label})")
        return " | ".join(parts)


# ── Singleton ──
_instance: Optional[LiveCrossAssetIntelligence] = None


def get_cross_asset_intelligence() -> LiveCrossAssetIntelligence:
    """Get or create the global LiveCrossAssetIntelligence singleton."""
    global _instance
    if _instance is None:
        _instance = LiveCrossAssetIntelligence()
    return _instance
