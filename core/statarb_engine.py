"""
PROMETHEUS Statistical Arbitrage Engine
========================================
Implements mathematically-grounded trading strategies inspired by
Renaissance Technologies / Medallion Fund principles:

1. PAIRS TRADING:  Find correlated assets, trade the spread when it
   deviates >2σ from the mean.  This is Renaissance's bread and butter.

2. MEAN REVERSION Z-SCORE:  For individual assets, compute z-score of
   price relative to rolling mean.  Fade extremes.

3. CROSS-ASSET MOMENTUM DIVERGENCE:  When normally-correlated assets
   diverge (e.g. BTC up but ETH flat), trade the laggard.

4. VOLUME-WEIGHTED REVERSAL:  When price moves sharply on low volume,
   expect reversal.  When price moves on high volume, expect continuation.

All strategies produce properly-calibrated confidence scores and
risk-reward targets.  Every signal comes with a mathematical edge
estimate, not an LLM opinion.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Data Types
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class StatArbSignal:
    """A signal produced by the statistical arbitrage engine."""
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float  # 0.0 – 1.0
    strategy: str  # pairs_trade, mean_reversion, momentum_divergence, volume_reversal
    edge_estimate: float  # Expected edge in % (e.g. 1.5 = +1.5% expected move)
    z_score: float  # How many σ from mean (sign indicates direction)
    target_pct: float  # Target profit %
    stop_pct: float  # Stop loss %
    reasoning: str
    pair_symbol: Optional[str] = None  # For pairs trades, the other leg
    kelly_fraction: float = 0.0  # Optimal position fraction (Kelly Criterion)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PairRelationship:
    """Tracks the statistical relationship between two assets."""
    symbol_a: str
    symbol_b: str
    correlation: float  # Rolling Pearson correlation
    spread_mean: float  # Mean of normalised spread
    spread_std: float  # Std of normalised spread
    current_spread: float  # Current normalised spread
    z_score: float  # Current z-score of spread
    half_life: float  # Mean-reversion half-life in days
    cointegrated: bool  # Engle-Granger test result
    updated_at: datetime = field(default_factory=datetime.now)


# ═══════════════════════════════════════════════════════════════════════════════
# Predefined pairs to monitor
# ═══════════════════════════════════════════════════════════════════════════════

CRYPTO_PAIRS = [
    ("BTC/USD", "ETH/USD"),
    ("BTC/USD", "SOL/USD"),
    ("ETH/USD", "SOL/USD"),
    ("LINK/USD", "AVAX/USD"),
    ("UNI/USD", "SUSHI/USD"),
]

EQUITY_PAIRS = [
    ("SPY", "QQQ"),
    ("QQQ", "IWM"),
    ("AAPL", "MSFT"),
    ("GOOGL", "META"),
    ("NVDA", "AMD"),
    ("AMZN", "GOOGL"),
]

# Y-finance compatible versions
CRYPTO_PAIRS_YF = [
    ("BTC-USD", "ETH-USD"),
    ("BTC-USD", "SOL-USD"),
    ("ETH-USD", "SOL-USD"),
    ("LINK-USD", "AVAX-USD"),
    ("UNI-USD", "SUSHI-USD"),
]

EQUITY_PAIRS_YF = EQUITY_PAIRS[:]  # Same format


# ═══════════════════════════════════════════════════════════════════════════════
# Statistical Arbitrage Engine
# ═══════════════════════════════════════════════════════════════════════════════

class StatArbEngine:
    """
    Pure math-based trading signal generator.
    No LLMs, no opinions — only statistical relationships.
    """

    def __init__(
        self,
        lookback_days: int = 60,
        z_entry_threshold: float = 2.0,
        z_exit_threshold: float = 0.5,
        min_correlation: float = 0.65,
        min_half_life: float = 1.0,
        max_half_life: float = 30.0,
        cache_ttl: int = 300,  # 5 minutes
    ):
        self.lookback_days = lookback_days
        self.z_entry_threshold = z_entry_threshold
        self.z_exit_threshold = z_exit_threshold
        self.min_correlation = min_correlation
        self.min_half_life = min_half_life
        self.max_half_life = max_half_life
        self.cache_ttl = cache_ttl

        # Cache
        self._price_cache: Dict[str, Dict] = {}
        self._pair_cache: Dict[str, PairRelationship] = {}

        # Performance tracking for Kelly
        self._strategy_history: Dict[str, List[float]] = {
            "pairs_trade": [],
            "mean_reversion": [],
            "momentum_divergence": [],
            "volume_reversal": [],
        }

        self._yf_available = False
        try:
            import yfinance  # noqa: F401
            self._yf_available = True
        except ImportError:
            logger.warning("yfinance not available for StatArb")

        logger.info(
            f"StatArbEngine initialized: lookback={lookback_days}d, "
            f"z_entry={z_entry_threshold}, min_corr={min_correlation}"
        )

    # ──────────────────────────────────────────────────────────────────────
    # Main entry point: generate signals for a symbol
    # ──────────────────────────────────────────────────────────────────────

    async def generate_signals(self, symbol: str) -> List[StatArbSignal]:
        """
        Generate all statistical arbitrage signals for a symbol.
        Returns a list of 0-N signals, sorted by confidence descending.
        """
        signals: List[StatArbSignal] = []

        # 1. Mean reversion on the asset itself
        mr_signal = await self._mean_reversion_signal(symbol)
        if mr_signal:
            signals.append(mr_signal)

        # 2. Pairs trading against correlated assets
        pair_signals = await self._pairs_trading_signals(symbol)
        signals.extend(pair_signals)

        # 3. Volume-weighted reversal
        vr_signal = await self._volume_reversal_signal(symbol)
        if vr_signal:
            signals.append(vr_signal)

        # 4. Momentum divergence
        md_signal = await self._momentum_divergence_signal(symbol)
        if md_signal:
            signals.append(md_signal)

        # Sort by confidence
        signals.sort(key=lambda s: s.confidence, reverse=True)
        return signals

    async def get_best_signal(self, symbol: str) -> Optional[StatArbSignal]:
        """Get the single best statistical signal for a symbol."""
        signals = await self.generate_signals(symbol)
        return signals[0] if signals else None

    # ──────────────────────────────────────────────────────────────────────
    # Strategy 1: Mean Reversion Z-Score
    # ──────────────────────────────────────────────────────────────────────

    async def _mean_reversion_signal(self, symbol: str) -> Optional[StatArbSignal]:
        """
        Trade mean reversion when price deviates significantly from its
        rolling mean (z-score > threshold).
        """
        prices = await self._get_prices(symbol)
        if prices is None or len(prices) < 30:
            return None

        closes = prices["close"]
        volumes = prices["volume"]

        # 20-day rolling mean & std
        window = min(20, len(closes) - 1)
        mean = np.mean(closes[-window:])
        std = np.std(closes[-window:])
        if std < 1e-10:
            return None

        current = closes[-1]
        z_score = (current - mean) / std

        # Only signal at extremes
        if abs(z_score) < self.z_entry_threshold:
            return None

        # Direction: fade the extreme
        action = "BUY" if z_score < -self.z_entry_threshold else "SELL"

        # Half-life estimation (Ornstein-Uhlenbeck)
        half_life = self._estimate_half_life(closes[-window:])
        if half_life < self.min_half_life or half_life > self.max_half_life:
            return None  # Not mean-reverting or too slow

        # Confidence based on z-score magnitude and half-life
        z_mag = min(abs(z_score), 4.0)  # Cap at 4σ
        confidence = 0.50 + (z_mag - 2.0) * 0.15  # 50% at 2σ, 80% at 4σ
        confidence = min(0.85, max(0.50, confidence))

        # Volume confirmation: higher volume at extremes = more confidence
        vol_ratio = volumes[-1] / (np.mean(volumes[-20:]) or 1.0)
        if vol_ratio > 1.5:
            confidence = min(0.90, confidence + 0.05)

        # Edge estimate: expected reversion towards mean
        edge_pct = abs(z_score) * (std / mean) * 100 * 0.5  # 50% of full reversion
        edge_pct = min(edge_pct, 5.0)  # Cap at 5%

        # Targets
        target_pct = edge_pct / 100  # e.g. 2% → 0.02
        stop_pct = target_pct * 0.5  # 2:1 risk/reward

        # Kelly fraction
        kelly = self._kelly_fraction("mean_reversion", confidence)

        return StatArbSignal(
            symbol=symbol,
            action=action,
            confidence=confidence,
            strategy="mean_reversion",
            edge_estimate=edge_pct,
            z_score=z_score,
            target_pct=target_pct,
            stop_pct=stop_pct,
            kelly_fraction=kelly,
            reasoning=f"Mean reversion: z={z_score:.2f}, half_life={half_life:.1f}d, "
                      f"vol_ratio={vol_ratio:.1f}x, edge={edge_pct:.1f}%",
        )

    # ──────────────────────────────────────────────────────────────────────
    # Strategy 2: Pairs Trading
    # ──────────────────────────────────────────────────────────────────────

    async def _pairs_trading_signals(self, symbol: str) -> List[StatArbSignal]:
        """
        Find pairs where the spread has deviated significantly.
        Trade long the underperformer, short the outperformer.
        """
        signals: List[StatArbSignal] = []

        # Normalise symbol for pair lookup
        sym_norm = symbol.upper().replace("/", "-").replace(" ", "")

        # Find all pairs containing this symbol
        all_pairs = CRYPTO_PAIRS_YF + EQUITY_PAIRS_YF
        my_pairs = [(a, b) for a, b in all_pairs if sym_norm in (a, b)]

        if not my_pairs:
            return signals

        for sym_a, sym_b in my_pairs:
            try:
                pair_rel = await self._compute_pair_relationship(sym_a, sym_b)
                if pair_rel is None:
                    continue

                # Only trade pairs with sufficient correlation
                if pair_rel.correlation < self.min_correlation:
                    continue

                # Only trade when z-score exceeds threshold
                if abs(pair_rel.z_score) < self.z_entry_threshold:
                    continue

                # Half-life must be reasonable
                if pair_rel.half_life < self.min_half_life or pair_rel.half_life > self.max_half_life:
                    continue

                # Determine action for THIS symbol
                # If z_score > 0: spread is high → sym_a overpriced relative to sym_b
                # If z_score < 0: spread is low → sym_a underpriced relative to sym_b
                if sym_norm == sym_a:
                    action = "SELL" if pair_rel.z_score > 0 else "BUY"
                    pair_sym = sym_b
                else:
                    action = "BUY" if pair_rel.z_score > 0 else "SELL"
                    pair_sym = sym_a

                # Confidence: stronger z-score and correlation → higher confidence
                z_mag = min(abs(pair_rel.z_score), 4.0)
                conf_from_z = 0.45 + (z_mag - 2.0) * 0.15
                conf_from_corr = pair_rel.correlation  # Higher corr = more reliable
                confidence = 0.6 * conf_from_z + 0.4 * conf_from_corr
                confidence = min(0.90, max(0.45, confidence))

                # Extra confidence if cointegrated
                if pair_rel.cointegrated:
                    confidence = min(0.92, confidence + 0.05)

                # Edge: expected spread convergence
                edge_pct = abs(pair_rel.z_score) * pair_rel.spread_std / (pair_rel.spread_mean or 1.0) * 100 * 0.5
                edge_pct = min(edge_pct, 5.0)

                kelly = self._kelly_fraction("pairs_trade", confidence)

                # Convert pair symbol back to trading format
                pair_sym_trade = pair_sym.replace("-USD", "/USD")

                signals.append(StatArbSignal(
                    symbol=symbol,
                    action=action,
                    confidence=confidence,
                    strategy="pairs_trade",
                    edge_estimate=edge_pct,
                    z_score=pair_rel.z_score,
                    target_pct=edge_pct / 100,
                    stop_pct=edge_pct / 200,  # 2:1 R:R
                    pair_symbol=pair_sym_trade,
                    kelly_fraction=kelly,
                    reasoning=(
                        f"Pairs trade: {sym_a}/{sym_b} z={pair_rel.z_score:.2f}, "
                        f"corr={pair_rel.correlation:.2f}, half_life={pair_rel.half_life:.1f}d"
                        f"{', cointegrated' if pair_rel.cointegrated else ''}"
                    ),
                ))

            except Exception as exc:
                logger.debug(f"Pair analysis failed for {sym_a}/{sym_b}: {exc}")

        return signals

    async def _compute_pair_relationship(
        self, sym_a: str, sym_b: str,
    ) -> Optional[PairRelationship]:
        """Compute the statistical relationship between two assets."""
        cache_key = f"{sym_a}:{sym_b}"
        now = time.time()

        if cache_key in self._pair_cache:
            cached = self._pair_cache[cache_key]
            if (now - cached.updated_at.timestamp()) < self.cache_ttl:
                return cached

        prices_a = await self._get_prices(sym_a)
        prices_b = await self._get_prices(sym_b)

        if prices_a is None or prices_b is None:
            return None

        ca = prices_a["close"]
        cb = prices_b["close"]

        # Align lengths
        min_len = min(len(ca), len(cb))
        if min_len < 30:
            return None
        ca = ca[-min_len:]
        cb = cb[-min_len:]

        # Correlation
        correlation = float(np.corrcoef(ca, cb)[0, 1])

        # Normalised spread: log(A) - β * log(B)
        log_a = np.log(ca)
        log_b = np.log(cb)

        # OLS regression to find hedge ratio β
        beta = np.cov(log_a, log_b)[0, 1] / (np.var(log_b) or 1e-10)
        spread = log_a - beta * log_b

        spread_mean = float(np.mean(spread))
        spread_std = float(np.std(spread)) or 1e-10
        current_spread = float(spread[-1])
        z_score = (current_spread - spread_mean) / spread_std

        # Half-life (Ornstein-Uhlenbeck)
        half_life = self._estimate_half_life(spread)

        # Simple cointegration test (Augmented Dickey-Fuller approximation)
        cointegrated = self._simple_adf_test(spread)

        pair_rel = PairRelationship(
            symbol_a=sym_a,
            symbol_b=sym_b,
            correlation=correlation,
            spread_mean=spread_mean,
            spread_std=spread_std,
            current_spread=current_spread,
            z_score=z_score,
            half_life=half_life,
            cointegrated=cointegrated,
        )

        self._pair_cache[cache_key] = pair_rel
        return pair_rel

    # ──────────────────────────────────────────────────────────────────────
    # Strategy 3: Volume-Weighted Reversal
    # ──────────────────────────────────────────────────────────────────────

    async def _volume_reversal_signal(self, symbol: str) -> Optional[StatArbSignal]:
        """
        When price moves sharply on LOW volume → likely reversal.
        When price moves sharply on HIGH volume → likely continuation.
        """
        prices = await self._get_prices(symbol)
        if prices is None or len(prices) < 20:
            return None

        closes = prices["close"]
        volumes = prices["volume"]

        # Recent price change
        pct_change = (closes[-1] - closes[-2]) / closes[-2] if closes[-2] > 0 else 0
        abs_change = abs(pct_change)

        # Need meaningful move to trigger (>1%)
        if abs_change < 0.01:
            return None

        # Volume analysis
        avg_vol = np.mean(volumes[-20:]) or 1.0
        vol_ratio = volumes[-1] / avg_vol

        # Low volume + big move = reversal signal
        if vol_ratio < 0.7 and abs_change > 0.015:
            action = "SELL" if pct_change > 0 else "BUY"  # Fade the move
            z_score = pct_change / (np.std(np.diff(closes[-20:]) / closes[-20:-1]) or 0.01)

            confidence = 0.50 + min(abs_change * 10, 0.25)
            # Lower vol = more confident it's a fake move
            confidence += (1.0 - vol_ratio) * 0.1
            confidence = min(0.75, confidence)

            edge_pct = abs_change * 50  # Expect 50% reversion
            kelly = self._kelly_fraction("volume_reversal", confidence)

            return StatArbSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                strategy="volume_reversal",
                edge_estimate=edge_pct,
                z_score=z_score,
                target_pct=edge_pct / 100,
                stop_pct=edge_pct / 200,
                kelly_fraction=kelly,
                reasoning=f"Vol reversal: {pct_change*100:+.1f}% on {vol_ratio:.1f}x avg vol (fade expected)",
            )

        # High volume + big move = continuation signal
        if vol_ratio > 2.0 and abs_change > 0.015:
            action = "BUY" if pct_change > 0 else "SELL"  # Follow the move
            z_score = pct_change / (np.std(np.diff(closes[-20:]) / closes[-20:-1]) or 0.01)

            confidence = 0.50 + min(abs_change * 8, 0.20)
            confidence += min((vol_ratio - 2.0) * 0.05, 0.10)
            confidence = min(0.75, confidence)

            edge_pct = abs_change * 70  # Expect continuation
            kelly = self._kelly_fraction("volume_reversal", confidence)

            return StatArbSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                strategy="volume_reversal",
                edge_estimate=edge_pct,
                z_score=z_score,
                target_pct=edge_pct / 100,
                stop_pct=edge_pct / 200,
                kelly_fraction=kelly,
                reasoning=f"Vol continuation: {pct_change*100:+.1f}% on {vol_ratio:.1f}x avg vol (momentum)",
            )

        return None

    # ──────────────────────────────────────────────────────────────────────
    # Strategy 4: Momentum Divergence (Cross-Asset)
    # ──────────────────────────────────────────────────────────────────────

    async def _momentum_divergence_signal(self, symbol: str) -> Optional[StatArbSignal]:
        """
        When normally-correlated assets diverge in momentum,
        trade the laggard expecting convergence.
        """
        sym_norm = symbol.upper().replace("/", "-").replace(" ", "")
        all_pairs = CRYPTO_PAIRS_YF + EQUITY_PAIRS_YF
        my_pairs = [(a, b) for a, b in all_pairs if sym_norm in (a, b)]

        if not my_pairs:
            return None

        best_signal: Optional[StatArbSignal] = None
        best_divergence = 0.0

        for sym_a, sym_b in my_pairs:
            try:
                prices_a = await self._get_prices(sym_a)
                prices_b = await self._get_prices(sym_b)
                if prices_a is None or prices_b is None:
                    continue

                ca = prices_a["close"]
                cb = prices_b["close"]
                min_len = min(len(ca), len(cb))
                if min_len < 10:
                    continue

                # 5-day momentum for each
                mom_a = (ca[-1] - ca[-6]) / ca[-6] if ca[-6] > 0 else 0
                mom_b = (cb[-1] - cb[-6]) / cb[-6] if cb[-6] > 0 else 0

                divergence = mom_a - mom_b  # Positive = A outperforming B

                # Only trigger on meaningful divergence (>3%)
                if abs(divergence) < 0.03:
                    continue

                # Also check that they were correlated historically
                corr = float(np.corrcoef(ca[-min_len:], cb[-min_len:])[0, 1])
                if corr < 0.5:
                    continue

                # Trade the laggard (expect convergence)
                if sym_norm == sym_a:
                    # A is outperforming → expect A to revert down
                    if divergence > 0:
                        action = "SELL"
                    else:
                        action = "BUY"
                else:
                    # This is sym_b
                    if divergence > 0:
                        action = "BUY"  # B is lagging → expect B to catch up
                    else:
                        action = "SELL"

                if abs(divergence) > abs(best_divergence):
                    best_divergence = divergence
                    confidence = 0.45 + min(abs(divergence) * 3, 0.30)
                    confidence = min(0.80, max(0.45, confidence))

                    edge_pct = abs(divergence) * 50  # Expect 50% convergence
                    kelly = self._kelly_fraction("momentum_divergence", confidence)

                    pair_sym_trade = (sym_b if sym_norm == sym_a else sym_a).replace("-USD", "/USD")
                    best_signal = StatArbSignal(
                        symbol=symbol,
                        action=action,
                        confidence=confidence,
                        strategy="momentum_divergence",
                        edge_estimate=edge_pct,
                        z_score=divergence / 0.03,  # Normalise
                        target_pct=edge_pct / 100,
                        stop_pct=edge_pct / 200,
                        pair_symbol=pair_sym_trade,
                        kelly_fraction=kelly,
                        reasoning=(
                            f"Momentum divergence: {sym_a} {mom_a*100:+.1f}% vs "
                            f"{sym_b} {mom_b*100:+.1f}% (corr={corr:.2f})"
                        ),
                    )
            except Exception as exc:
                logger.debug(f"Momentum divergence failed for {sym_a}/{sym_b}: {exc}")

        return best_signal

    # ──────────────────────────────────────────────────────────────────────
    # Kelly Criterion Position Sizing
    # ──────────────────────────────────────────────────────────────────────

    def _kelly_fraction(self, strategy: str, confidence: float) -> float:
        """
        Compute Kelly Criterion fraction for position sizing.

        Kelly formula: f* = (bp - q) / b
        where b = win/loss ratio, p = win probability, q = 1-p

        Uses half-Kelly for safety (common in practice).
        """
        history = self._strategy_history.get(strategy, [])

        if len(history) < 10:
            # Not enough history — use confidence as proxy
            p = confidence
            b = 2.0  # Assumed 2:1 risk/reward
        else:
            wins = [h for h in history if h > 0]
            losses = [h for h in history if h < 0]
            p = len(wins) / len(history) if history else 0.5
            avg_win = np.mean(wins) if wins else 1.0
            avg_loss = abs(np.mean(losses)) if losses else 1.0
            b = avg_win / avg_loss if avg_loss > 0 else 1.0

        q = 1.0 - p
        kelly = (b * p - q) / b if b > 0 else 0.0

        # Half-Kelly for safety
        kelly = max(0.0, min(0.25, kelly * 0.5))  # Cap at 25% of capital
        return kelly

    def record_outcome(self, strategy: str, pnl_pct: float):
        """Record a trade outcome for Kelly Criterion calculation."""
        if strategy in self._strategy_history:
            self._strategy_history[strategy].append(pnl_pct)
            # Keep last 100 results
            if len(self._strategy_history[strategy]) > 100:
                self._strategy_history[strategy] = self._strategy_history[strategy][-100:]

    # ──────────────────────────────────────────────────────────────────────
    # Statistical helpers
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _estimate_half_life(series: np.ndarray) -> float:
        """
        Estimate the half-life of mean reversion using the
        Ornstein-Uhlenbeck process.

        Uses OLS on: Δy(t) = λ·y(t-1) + ε
        Half-life = -ln(2) / λ
        """
        if len(series) < 5:
            return 999.0

        y = series - np.mean(series)
        y_lag = y[:-1]
        dy = np.diff(y)

        # OLS: dy = lambda * y_lag
        if np.sum(y_lag ** 2) == 0:
            return 999.0

        lam = np.sum(dy * y_lag) / np.sum(y_lag ** 2)

        if lam >= 0:
            return 999.0  # Not mean-reverting

        half_life = -np.log(2) / lam
        return float(max(0.1, half_life))

    @staticmethod
    def _simple_adf_test(series: np.ndarray, critical_value: float = -2.86) -> bool:
        """
        Simplified Augmented Dickey-Fuller test for stationarity.
        Returns True if the series is likely stationary (cointegrated).

        Uses the t-statistic from: Δy(t) = α + β·y(t-1) + ε
        """
        if len(series) < 20:
            return False

        y = series
        y_lag = y[:-1]
        dy = np.diff(y)

        n = len(dy)
        x = np.column_stack([np.ones(n), y_lag])
        try:
            # OLS
            xtx_inv = np.linalg.inv(x.T @ x)
            beta = xtx_inv @ x.T @ dy
            residuals = dy - x @ beta
            sigma_sq = np.sum(residuals ** 2) / (n - 2)
            se_beta = np.sqrt(sigma_sq * np.diag(xtx_inv))
            t_stat = beta[1] / se_beta[1] if se_beta[1] > 0 else 0

            return bool(t_stat < critical_value)
        except (np.linalg.LinAlgError, ZeroDivisionError):
            return False

    # ──────────────────────────────────────────────────────────────────────
    # Price data management (with caching)
    # ──────────────────────────────────────────────────────────────────────

    async def _get_prices(self, symbol: str) -> Optional[Dict[str, np.ndarray]]:
        """Get cached or fresh price data."""
        now = time.time()

        # Normalise
        sym = symbol.upper().replace("/", "-").replace(" ", "")

        if sym in self._price_cache:
            entry = self._price_cache[sym]
            if now - entry["fetched_at"] < self.cache_ttl:
                return entry["data"]

        data = await asyncio.get_event_loop().run_in_executor(
            None, self._fetch_prices_sync, sym,
        )

        if data is not None:
            self._price_cache[sym] = {"data": data, "fetched_at": now}

        return data

    def _fetch_prices_sync(self, symbol: str) -> Optional[Dict[str, np.ndarray]]:
        """Sync yfinance fetch."""
        if not self._yf_available:
            return None

        import yfinance as yf

        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=f"{self.lookback_days}d", interval="1d")
            if df is None or len(df) < 20:
                return None

            return {
                "close": df["Close"].values.astype(float),
                "high": df["High"].values.astype(float),
                "low": df["Low"].values.astype(float),
                "volume": df["Volume"].values.astype(float),
                "open": df["Open"].values.astype(float),
            }
        except Exception as exc:
            logger.debug(f"yfinance fetch failed for {symbol}: {exc}")
            return None

    # ──────────────────────────────────────────────────────────────────────
    # Utility
    # ──────────────────────────────────────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        """Return engine status."""
        return {
            "name": "Statistical Arbitrage Engine",
            "active": True,
            "pairs_monitored": len(CRYPTO_PAIRS) + len(EQUITY_PAIRS),
            "price_cache_entries": len(self._price_cache),
            "pair_cache_entries": len(self._pair_cache),
            "strategy_history": {
                k: len(v) for k, v in self._strategy_history.items()
            },
        }


# Singleton
_statarb_engine: Optional[StatArbEngine] = None


def get_statarb_engine() -> StatArbEngine:
    """Get or create the singleton StatArb engine."""
    global _statarb_engine
    if _statarb_engine is None:
        _statarb_engine = StatArbEngine()
    return _statarb_engine
