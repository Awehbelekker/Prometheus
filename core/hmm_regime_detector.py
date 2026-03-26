"""
PROMETHEUS HMM Regime Detector
================================
Hidden Markov Model for detecting market regimes:

  State 0: LOW VOLATILITY / TRENDING   → Favour momentum / trend-following
  State 1: HIGH VOLATILITY / CHOPPY    → Favour mean-reversion / reduce size
  State 2: CRISIS / RISK-OFF           → Go defensive / cash-heavy

This is a core Renaissance-style insight: the same strategy does NOT work
in all regimes.  Mean-reversion prints money in range-bound markets but
gets obliterated in trends.  Trend-following works in strong directional
moves but whipsaws in chop.

The regime detector tells other systems WHICH strategy to trust.

Implementation: Gaussian HMM fitted on [returns, volatility, volume_change]
using the Baum-Welch (EM) algorithm.  No external dependencies beyond numpy.

We use a streaming approach — the model fits once on historical data and
then does online inference (Viterbi / forward algorithm) in real time.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Regime definitions
# ═══════════════════════════════════════════════════════════════════════════════

class MarketRegime(IntEnum):
    LOW_VOL_TRENDING = 0
    HIGH_VOL_CHOPPY = 1
    CRISIS_RISK_OFF = 2


REGIME_NAMES = {
    MarketRegime.LOW_VOL_TRENDING: "Low Vol / Trending",
    MarketRegime.HIGH_VOL_CHOPPY: "High Vol / Choppy",
    MarketRegime.CRISIS_RISK_OFF: "Crisis / Risk-Off",
}

# Strategy weights per regime: how much to trust each strategy family
REGIME_STRATEGY_WEIGHTS = {
    MarketRegime.LOW_VOL_TRENDING: {
        "momentum": 1.2,
        "trend_following": 1.3,
        "mean_reversion": 0.5,
        "pairs_trade": 0.8,
        "volume_reversal": 0.6,
        "position_size_mult": 1.0,  # Full size
    },
    MarketRegime.HIGH_VOL_CHOPPY: {
        "momentum": 0.5,
        "trend_following": 0.4,
        "mean_reversion": 1.3,
        "pairs_trade": 1.2,
        "volume_reversal": 1.1,
        "position_size_mult": 0.6,  # Reduced size
    },
    MarketRegime.CRISIS_RISK_OFF: {
        "momentum": 0.3,
        "trend_following": 0.3,
        "mean_reversion": 0.4,
        "pairs_trade": 0.5,
        "volume_reversal": 0.3,
        "position_size_mult": 0.25,  # Minimal size — capital preservation
    },
}


@dataclass
class RegimeState:
    """Current regime assessment."""
    regime: MarketRegime
    regime_name: str
    probability: float  # How confident is the HMM in this state
    state_probs: Dict[int, float]  # Probability of each state
    strategy_weights: Dict[str, float]  # Weights to apply per strategy
    volatility_percentile: float  # 0-1, where current vol sits historically
    trend_strength: float  # -1 to +1
    updated_at: datetime = field(default_factory=datetime.now)


# ═══════════════════════════════════════════════════════════════════════════════
# Gaussian HMM (pure numpy, no hmmlearn dependency)
# ═══════════════════════════════════════════════════════════════════════════════

class GaussianHMM:
    """
    Minimal Gaussian Hidden Markov Model with:
    - Baum-Welch (EM) fitting
    - Forward algorithm for state probabilities
    - Viterbi for most-likely state sequence

    Observations are D-dimensional continuous vectors.
    Each hidden state emits from a multivariate Gaussian.
    """

    def __init__(self, n_states: int = 3, n_features: int = 3, n_iter: int = 50):
        self.n_states = n_states
        self.n_features = n_features
        self.n_iter = n_iter

        # Model parameters
        self.pi: np.ndarray = np.ones(n_states) / n_states  # Initial probs
        self.A: np.ndarray = np.full((n_states, n_states), 1.0 / n_states)  # Transition
        # Make transitions slightly sticky (prefer staying in same state)
        for i in range(n_states):
            self.A[i, i] = 0.7
            others = [j for j in range(n_states) if j != i]
            for j in others:
                self.A[i, j] = 0.3 / len(others)

        # Emission parameters (means & covariances)
        self.means: np.ndarray = np.zeros((n_states, n_features))
        self.covs: np.ndarray = np.array([np.eye(n_features) for _ in range(n_states)])
        self._fitted = False

    def fit(self, X: np.ndarray) -> 'GaussianHMM':
        """
        Fit HMM using Baum-Welch (EM) algorithm.
        X: shape (T, D) — T time steps, D features.
        """
        T, D = X.shape
        K = self.n_states

        if T < K * 5:
            logger.warning(f"HMM: Not enough data ({T} < {K*5}), skipping fit")
            return self

        # Initialise means via K-means-like clustering
        # Sort by volatility (second feature) and split into K groups
        sorted_idx = np.argsort(X[:, 1] if D > 1 else X[:, 0])
        chunk_size = T // K
        for k in range(K):
            start = k * chunk_size
            end = start + chunk_size if k < K - 1 else T
            self.means[k] = np.mean(X[sorted_idx[start:end]], axis=0)
            cov = np.cov(X[sorted_idx[start:end]].T)
            if cov.ndim == 0:
                cov = np.array([[float(cov)]])
            self.covs[k] = cov + 1e-6 * np.eye(D)

        for iteration in range(self.n_iter):
            # E-step: forward-backward
            log_B = self._compute_log_emission(X)
            alpha = self._forward(log_B)
            beta = self._backward(log_B)

            # Posterior: P(state_k | observations)
            gamma = alpha + beta
            gamma -= _logsumexp_axis(gamma, axis=1, keepdims=True)
            gamma = np.exp(gamma)

            # Xi: P(state_i at t, state_j at t+1 | observations)
            xi = np.zeros((T - 1, K, K))
            for t in range(T - 1):
                for i in range(K):
                    for j in range(K):
                        xi[t, i, j] = alpha[t, i] + np.log(self.A[i, j] + 1e-300) + log_B[t + 1, j] + beta[t + 1, j]
                xi[t] -= _logsumexp_2d(xi[t])
            xi = np.exp(xi)

            # M-step
            # Initial distribution
            self.pi = gamma[0] + 1e-10
            self.pi /= self.pi.sum()

            # Transition matrix
            for i in range(K):
                denom = gamma[:-1, i].sum() + 1e-10
                for j in range(K):
                    self.A[i, j] = xi[:, i, j].sum() / denom
                self.A[i] /= self.A[i].sum()

            # Emission parameters
            for k in range(K):
                gamma_k = gamma[:, k]
                total = gamma_k.sum() + 1e-10
                self.means[k] = (gamma_k[:, None] * X).sum(axis=0) / total
                diff = X - self.means[k]
                self.covs[k] = (gamma_k[:, None, None] * (diff[:, :, None] * diff[:, None, :])).sum(axis=0) / total
                self.covs[k] += 1e-6 * np.eye(D)  # Regularise

        self._fitted = True
        logger.info(f"HMM fitted: {self.n_iter} iterations, {T} observations, {K} states")
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Return state probabilities for each time step.
        X: shape (T, D) → returns (T, K)
        """
        log_B = self._compute_log_emission(X)
        alpha = self._forward(log_B)
        # Normalise
        probs = np.exp(alpha - _logsumexp_axis(alpha, axis=1, keepdims=True))
        return probs

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Most likely state at each time step (argmax of filtered probs)."""
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)

    def current_state_probs(self, X: np.ndarray) -> np.ndarray:
        """State probabilities at the LAST time step only."""
        probs = self.predict_proba(X)
        return probs[-1]

    # ── Internal methods ─────────────────────────────────────────────────

    def _compute_log_emission(self, X: np.ndarray) -> np.ndarray:
        """Log emission probabilities: log P(x_t | state_k)."""
        T = X.shape[0]
        K = self.n_states
        D = self.n_features
        log_B = np.zeros((T, K))

        for k in range(K):
            diff = X - self.means[k]
            try:
                cov_inv = np.linalg.inv(self.covs[k])
                log_det = np.log(np.linalg.det(self.covs[k]) + 1e-300)
            except np.linalg.LinAlgError:
                cov_inv = np.eye(D)
                log_det = 0.0

            # Multivariate Gaussian log-likelihood
            mahal = np.sum(diff @ cov_inv * diff, axis=1)
            log_B[:, k] = -0.5 * (D * np.log(2 * np.pi) + log_det + mahal)

        return log_B

    def _forward(self, log_B: np.ndarray) -> np.ndarray:
        """Forward algorithm (log-space)."""
        T, K = log_B.shape
        alpha = np.zeros((T, K))
        alpha[0] = np.log(self.pi + 1e-300) + log_B[0]

        log_A = np.log(self.A + 1e-300)
        for t in range(1, T):
            for j in range(K):
                alpha[t, j] = _logsumexp_1d(alpha[t - 1] + log_A[:, j]) + log_B[t, j]

        return alpha

    def _backward(self, log_B: np.ndarray) -> np.ndarray:
        """Backward algorithm (log-space)."""
        T, K = log_B.shape
        beta = np.zeros((T, K))

        log_A = np.log(self.A + 1e-300)
        for t in range(T - 2, -1, -1):
            for j in range(K):
                beta[t, j] = _logsumexp_1d(log_A[j, :] + log_B[t + 1, :] + beta[t + 1, :])

        return beta


# ── Log-space utilities ──────────────────────────────────────────────────

def _logsumexp_1d(x: np.ndarray) -> float:
    m = np.max(x)
    if np.isinf(m):
        return float('-inf')
    return m + np.log(np.sum(np.exp(x - m)))


def _logsumexp_axis(x: np.ndarray, axis: int, keepdims: bool = False) -> np.ndarray:
    m = np.max(x, axis=axis, keepdims=True)
    result = m + np.log(np.sum(np.exp(x - m), axis=axis, keepdims=True))
    if not keepdims:
        result = np.squeeze(result, axis=axis)
    return result


def _logsumexp_2d(x: np.ndarray) -> float:
    m = np.max(x)
    if np.isinf(m):
        return float('-inf')
    return m + np.log(np.sum(np.exp(x - m)))


# ═══════════════════════════════════════════════════════════════════════════════
# Regime Detector (wraps HMM with trading logic)
# ═══════════════════════════════════════════════════════════════════════════════

class RegimeDetector:
    """
    Detects the current market regime using an HMM on:
      Feature 0: log returns
      Feature 1: realised volatility (rolling std of returns)
      Feature 2: volume change ratio

    Fits on daily data; does online detection in real time.
    """

    def __init__(
        self,
        lookback_days: int = 120,
        vol_window: int = 20,
        refit_interval: int = 86400,  # Refit every 24h
        cache_ttl: int = 300,
    ):
        self.lookback_days = lookback_days
        self.vol_window = vol_window
        self.refit_interval = refit_interval
        self.cache_ttl = cache_ttl

        self.hmm = GaussianHMM(n_states=3, n_features=3, n_iter=30)
        self._last_fit_time = 0.0
        self._regime_cache: Dict[str, Tuple[RegimeState, float]] = {}

        self._yf_available = False
        try:
            import yfinance  # noqa: F401
            self._yf_available = True
        except ImportError:
            logger.warning("yfinance not available for RegimeDetector")

        logger.info(f"RegimeDetector initialized: lookback={lookback_days}d, vol_window={vol_window}")

    async def detect_regime(self, symbol: str = "SPY") -> Optional[RegimeState]:
        """
        Detect the current market regime for a symbol.
        Default: SPY (broad market regime).
        """
        now = time.time()

        # Check cache
        if symbol in self._regime_cache:
            cached, ts = self._regime_cache[symbol]
            if now - ts < self.cache_ttl:
                return cached

        # Fetch data
        features = await self._build_features(symbol)
        if features is None:
            return None

        # Refit if needed
        if now - self._last_fit_time > self.refit_interval or not self.hmm._fitted:
            self.hmm.fit(features)
            self._last_fit_time = now
            self._sort_states_by_volatility(features)

        # Predict current state
        state_probs = self.hmm.current_state_probs(features)
        current_regime = MarketRegime(int(np.argmax(state_probs)))

        # Compute extra metrics
        returns = features[:, 0]
        volatilities = features[:, 1]

        vol_percentile = float(
            np.sum(volatilities < volatilities[-1]) / len(volatilities)
        )

        # Trend strength: momentum of last 10 days normalised
        recent_returns = returns[-10:] if len(returns) >= 10 else returns
        trend_strength = float(np.mean(recent_returns) / (np.std(recent_returns) + 1e-10))
        trend_strength = max(-1.0, min(1.0, trend_strength))

        state = RegimeState(
            regime=current_regime,
            regime_name=REGIME_NAMES[current_regime],
            probability=float(state_probs[current_regime]),
            state_probs={int(i): float(p) for i, p in enumerate(state_probs)},
            strategy_weights=REGIME_STRATEGY_WEIGHTS[current_regime].copy(),
            volatility_percentile=vol_percentile,
            trend_strength=trend_strength,
        )

        self._regime_cache[symbol] = (state, now)

        logger.info(
            f"Regime({symbol}): {state.regime_name} "
            f"(p={state.probability:.0%}, vol_pctl={vol_percentile:.0%}, "
            f"trend={trend_strength:+.2f})"
        )

        return state

    def get_strategy_weight(self, regime_state: Optional[RegimeState], strategy: str) -> float:
        """Get the weight multiplier for a strategy given current regime."""
        if regime_state is None:
            return 1.0  # No regime info → neutral
        return regime_state.strategy_weights.get(strategy, 1.0)

    def get_position_size_mult(self, regime_state: Optional[RegimeState]) -> float:
        """Get position sizing multiplier for current regime."""
        if regime_state is None:
            return 1.0
        return regime_state.strategy_weights.get("position_size_mult", 1.0)

    def _sort_states_by_volatility(self, features: np.ndarray):
        """
        After fitting, sort states so that state 0 = lowest vol,
        state 2 = highest vol.  This ensures consistent regime mapping.
        """
        vol_by_state = []
        for k in range(self.hmm.n_states):
            # Mean of volatility feature (index 1)
            vol_by_state.append(self.hmm.means[k, 1])

        order = np.argsort(vol_by_state)

        # Rearrange model parameters
        self.hmm.pi = self.hmm.pi[order]
        self.hmm.A = self.hmm.A[order][:, order]
        self.hmm.means = self.hmm.means[order]
        self.hmm.covs = self.hmm.covs[order]

    async def _build_features(self, symbol: str) -> Optional[np.ndarray]:
        """Build the 3-feature matrix from OHLCV data."""
        data = await asyncio.get_event_loop().run_in_executor(
            None, self._fetch_data_sync, symbol,
        )
        if data is None:
            return None

        closes = data["close"]
        volumes = data["volume"]

        if len(closes) < 30:
            return None

        # Feature 0: log returns
        log_returns = np.diff(np.log(closes))

        # Feature 1: rolling realised volatility
        vol = np.array([
            np.std(log_returns[max(0, i - self.vol_window):i])
            if i >= self.vol_window else np.std(log_returns[:i + 1])
            for i in range(len(log_returns))
        ])

        # Feature 2: volume change ratio
        avg_vol = np.convolve(volumes[1:], np.ones(self.vol_window) / self.vol_window, mode='same')
        vol_ratio = volumes[1:] / (avg_vol + 1e-10)

        # Stack features (T-1 rows because of differencing)
        X = np.column_stack([log_returns, vol, vol_ratio])

        # Replace NaN/Inf
        X = np.nan_to_num(X, nan=0.0, posinf=3.0, neginf=-3.0)

        return X

    def _fetch_data_sync(self, symbol: str) -> Optional[Dict[str, np.ndarray]]:
        """Fetch OHLCV via yfinance."""
        if not self._yf_available:
            return None

        import yfinance as yf
        try:
            sym = symbol.upper().replace("/", "-").replace(" ", "")
            ticker = yf.Ticker(sym)
            df = ticker.history(period=f"{self.lookback_days}d", interval="1d")
            if df is None or len(df) < 30:
                return None
            return {
                "close": df["Close"].values.astype(float),
                "volume": df["Volume"].values.astype(float),
            }
        except Exception as exc:
            logger.debug(f"yfinance fetch failed for {symbol}: {exc}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Return detector status."""
        return {
            "name": "HMM Regime Detector",
            "active": True,
            "fitted": self.hmm._fitted,
            "n_states": self.hmm.n_states,
            "last_fit": datetime.fromtimestamp(self._last_fit_time).isoformat() if self._last_fit_time > 0 else "never",
            "cached_regimes": list(self._regime_cache.keys()),
        }


# Singleton
_regime_detector: Optional[RegimeDetector] = None


def get_regime_detector() -> RegimeDetector:
    """Get or create the singleton regime detector."""
    global _regime_detector
    if _regime_detector is None:
        _regime_detector = RegimeDetector()
    return _regime_detector
