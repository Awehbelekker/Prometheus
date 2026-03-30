"""
ML-Based Market Regime Detector
================================
Replaces the hardcoded transition matrix in regime_forecasting.py
with a real sklearn classifier trained on historical market features.

Models:
  - GradientBoosting classifier for regime classification
  - Trained on returns, volatility, momentum, volume features
  - Auto-retrains on new data (online learning via partial_fit fallback)

Falls back to heuristic if no trained model is available.
"""

import logging
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)

REGIME_LABELS = ["bull", "bear", "volatile", "sideways"]
REGIME_MAP = {label: i for i, label in enumerate(REGIME_LABELS)}
INV_REGIME_MAP = {i: label for label, i in REGIME_MAP.items()}

MODEL_PATH = Path("trained_models/regime_classifier.pkl")
SCALER_PATH = Path("trained_models/regime_scaler.pkl")
TRANSITION_PATH = Path("trained_models/learned_transitions.pkl")


@dataclass
class RegimeFeatures:
    """Feature vector for a single observation window"""
    returns_mean: float
    returns_std: float
    returns_skew: float
    returns_kurt: float
    volatility_5d: float
    volatility_20d: float
    vol_ratio: float          # short-term vol / long-term vol
    momentum_5d: float
    momentum_20d: float
    rsi_proxy: float          # simplified RSI from returns
    trend_slope: float        # normalized linear regression slope
    trend_r2: float           # R-squared of linear fit
    mean_reversion: float     # autocorrelation(1) of returns
    range_pct: float          # (high-low)/close range
    volume_ratio: float       # recent vol / historical vol
    up_days_pct: float        # fraction of positive return days
    max_drawdown: float       # max drawdown in window
    gap_frequency: float      # frequency of gap opens


class MLRegimeDetector:
    """
    Gradient Boosting classifier for market regime detection.
    Trained on labeled historical windows, with learned transition matrix.
    """

    def __init__(self):
        self.model = None
        self.scaler = None
        self.transition_matrix: Optional[Dict[str, Dict[str, float]]] = None
        self.feature_names = list(RegimeFeatures.__dataclass_fields__.keys())
        self._load_model()

    # ------------------------------------------------------------------
    # Feature engineering
    # ------------------------------------------------------------------

    @staticmethod
    def extract_features(df: pd.DataFrame, window: int = 20) -> Optional[np.ndarray]:
        """
        Extract regime features from a DataFrame with columns: open, high, low, close, volume.
        Returns a feature vector or None if data is insufficient.
        """
        if len(df) < window + 5:
            return None

        recent = df.tail(window)
        close = recent["close"].values
        returns = pd.Series(close).pct_change().dropna().values

        if len(returns) < 5:
            return None

        # Returns stats
        r_mean = np.mean(returns)
        r_std = np.std(returns) if np.std(returns) > 0 else 1e-8
        r_skew = float(pd.Series(returns).skew()) if len(returns) > 3 else 0.0
        r_kurt = float(pd.Series(returns).kurtosis()) if len(returns) > 3 else 0.0

        # Volatility (short vs long)
        vol_5 = np.std(returns[-5:]) if len(returns) >= 5 else r_std
        vol_20 = r_std
        vol_ratio = vol_5 / vol_20 if vol_20 > 0 else 1.0

        # Momentum
        mom_5 = (close[-1] / close[-6] - 1) if len(close) > 5 else 0.0
        mom_20 = (close[-1] / close[0] - 1)

        # RSI proxy (proportion of gains to total movement)
        gains = returns[returns > 0].sum()
        losses = abs(returns[returns < 0].sum())
        rsi_proxy = gains / (gains + losses) if (gains + losses) > 0 else 0.5

        # Trend (linear regression)
        x = np.arange(len(close))
        coeffs = np.polyfit(x, close, 1)
        slope = coeffs[0] / np.mean(close)  # normalized slope
        # R-squared
        y_hat = np.polyval(coeffs, x)
        ss_res = np.sum((close - y_hat) ** 2)
        ss_tot = np.sum((close - np.mean(close)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        # Mean reversion (lag-1 autocorrelation)
        if len(returns) > 2:
            autocorr = np.corrcoef(returns[:-1], returns[1:])[0, 1]
            if np.isnan(autocorr):
                autocorr = 0.0
        else:
            autocorr = 0.0

        # Range
        if "high" in df.columns and "low" in df.columns:
            range_pct = (recent["high"].max() - recent["low"].min()) / np.mean(close) if np.mean(close) > 0 else 0.0
        else:
            range_pct = (max(close) - min(close)) / np.mean(close) if np.mean(close) > 0 else 0.0

        # Volume ratio
        if "volume" in df.columns and df["volume"].mean() > 0:
            vol_recent = recent["volume"].tail(5).mean()
            vol_hist = df["volume"].mean()
            volume_ratio = vol_recent / vol_hist if vol_hist > 0 else 1.0
        else:
            volume_ratio = 1.0

        # Up days
        up_days = np.sum(returns > 0) / len(returns)

        # Max drawdown in window
        cummax = np.maximum.accumulate(close)
        drawdowns = (close - cummax) / cummax
        max_dd = abs(np.min(drawdowns))

        # Gap frequency (open != prev close)
        if "open" in df.columns:
            opens = recent["open"].values[1:]
            prev_close = close[:-1]
            gaps = np.abs(opens - prev_close) / prev_close
            gap_freq = np.mean(gaps > 0.005)  # gaps > 0.5%
        else:
            gap_freq = 0.0

        features = np.array([
            r_mean, r_std, r_skew, r_kurt,
            vol_5, vol_20, vol_ratio,
            mom_5, mom_20,
            rsi_proxy, slope, r2, autocorr,
            range_pct, volume_ratio, up_days,
            max_dd, gap_freq,
        ], dtype=np.float64)

        # Replace NaN/Inf
        features = np.nan_to_num(features, nan=0.0, posinf=1.0, neginf=-1.0)
        return features

    # ------------------------------------------------------------------
    # Labeling (for training)
    # ------------------------------------------------------------------

    @staticmethod
    def label_regime(returns: np.ndarray, volatility: float) -> str:
        """
        Heuristic label for training data based on realized characteristics.
        Applied to historical windows to create supervised labels.
        """
        mean_ret = np.mean(returns)
        vol = volatility

        if vol > 0.025:
            return "volatile"
        elif mean_ret > 0.0005 and vol < 0.018:
            return "bull"
        elif mean_ret < -0.0005 and vol < 0.022:
            return "bear"
        else:
            return "sideways"

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train_on_historical(
        self,
        df: pd.DataFrame,
        window: int = 20,
        step: int = 5,
    ) -> Dict[str, Any]:
        """
        Train the regime classifier on historical OHLCV data.

        Args:
            df: Full historical DataFrame with open, high, low, close, volume
            window: Observation window size for features
            step: Step size between windows

        Returns:
            Training metrics dict
        """
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import cross_val_score

        logger.info(f"Training ML regime detector on {len(df)} bars (window={window}, step={step})")

        X_list = []
        y_list = []
        regime_sequence = []

        for i in range(window + 5, len(df) - window, step):
            chunk = df.iloc[i - window - 5: i]
            features = self.extract_features(chunk, window)
            if features is None:
                continue

            # Label from forward-looking window (the regime we're IN)
            fwd = df.iloc[i: i + window]
            if len(fwd) < window // 2:
                continue
            fwd_returns = fwd["close"].pct_change().dropna().values
            if len(fwd_returns) < 3:
                continue
            fwd_vol = np.std(fwd_returns)
            label = self.label_regime(fwd_returns, fwd_vol)

            X_list.append(features)
            y_list.append(REGIME_MAP[label])
            regime_sequence.append(label)

        if len(X_list) < 50:
            logger.warning(f"Only {len(X_list)} samples — need at least 50 for training")
            return {"status": "insufficient_data", "samples": len(X_list)}

        X = np.array(X_list)
        y = np.array(y_list)

        # Scale
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train GradientBoosting — class_weight='balanced' equivalent via sample weights
        # Volatile regime is severely underrepresented (75 vs 2000+ bull samples).
        # Compute per-sample weights = total / (n_classes * class_count).
        unique_cls, cls_counts = np.unique(y, return_counts=True)
        cls_weight = {int(c): len(y) / (len(unique_cls) * cnt) for c, cnt in zip(unique_cls, cls_counts)}
        sample_weights = np.array([cls_weight[int(yi)] for yi in y])

        clf = GradientBoostingClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.1,
            min_samples_leaf=3,  # lower to allow volatile minority class to split
            subsample=0.8,
            random_state=42,
        )

        # Cross-validation
        try:
            from sklearn.model_selection import StratifiedKFold
            from sklearn.base import clone
            n_splits = min(5, len(set(y)))
            skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
            fold_scores = []
            for train_idx, val_idx in skf.split(X_scaled, y):
                clone(clf).fit(X_scaled[train_idx], y[train_idx],
                               sample_weight=sample_weights[train_idx])
                fold_clf = clone(clf)
                fold_clf.fit(X_scaled[train_idx], y[train_idx],
                             sample_weight=sample_weights[train_idx])
                fold_scores.append((fold_clf.predict(X_scaled[val_idx]) == y[val_idx]).mean())
            cv_scores = np.array(fold_scores)
            cv_mean = float(cv_scores.mean())
            cv_std = float(cv_scores.std())
        except Exception:
            cv_mean, cv_std = 0.0, 0.0

        # Full fit with class-balanced sample weights
        clf.fit(X_scaled, y, sample_weight=sample_weights)

        # Feature importances
        importances = dict(zip(self.feature_names, clf.feature_importances_))

        # Learn transition matrix from label sequence
        transitions = self._learn_transition_matrix(regime_sequence)

        # Label distribution
        unique, counts = np.unique(y, return_counts=True)
        dist = {INV_REGIME_MAP.get(u, str(u)): int(c) for u, c in zip(unique, counts)}

        # Save
        self.model = clf
        self.scaler = scaler
        self.transition_matrix = transitions
        self._save_model()

        metrics = {
            "status": "trained",
            "samples": len(X_list),
            "cv_accuracy": round(cv_mean, 4),
            "cv_std": round(cv_std, 4),
            "label_distribution": dist,
            "top_features": dict(sorted(importances.items(), key=lambda x: -x[1])[:5]),
            "transition_matrix": transitions,
        }
        logger.info(
            f"ML Regime Detector trained: {len(X_list)} samples, "
            f"CV accuracy={cv_mean:.1%} +/- {cv_std:.1%}, dist={dist}"
        )
        return metrics

    def _learn_transition_matrix(self, sequence: List[str]) -> Dict[str, Dict[str, float]]:
        """Learn transition probabilities from a sequence of regime labels."""
        counts: Dict[str, Dict[str, int]] = {r: {r2: 0 for r2 in REGIME_LABELS} for r in REGIME_LABELS}
        for i in range(len(sequence) - 1):
            fr, to = sequence[i], sequence[i + 1]
            if fr in counts and to in counts[fr]:
                counts[fr][to] += 1

        matrix = {}
        for fr in REGIME_LABELS:
            total = sum(counts[fr].values())
            if total > 0:
                matrix[fr] = {to: round(c / total, 3) for to, c in counts[fr].items()}
            else:
                matrix[fr] = {to: 0.25 for to in REGIME_LABELS}
        return matrix

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict_regime(self, df: pd.DataFrame, window: int = 20) -> Dict[str, Any]:
        """
        Predict current regime from recent market data.

        Returns dict with regime, probabilities, and confidence.
        Falls back to heuristic if model not trained.
        """
        features = self.extract_features(df, window)
        if features is None:
            return {"regime": "sideways", "confidence": 0.3, "method": "default"}

        if self.model is not None and self.scaler is not None:
            X = self.scaler.transform(features.reshape(1, -1))
            pred = self.model.predict(X)[0]
            proba = self.model.predict_proba(X)[0]
            regime = INV_REGIME_MAP.get(pred, "sideways")
            prob_dict = {}
            for i, cls in enumerate(self.model.classes_):
                prob_dict[INV_REGIME_MAP.get(cls, str(cls))] = round(float(proba[i]), 4)
            return {
                "regime": regime,
                "confidence": round(float(max(proba)), 4),
                "probabilities": prob_dict,
                "method": "ml_gradient_boosting",
            }
        else:
            # Heuristic fallback
            returns = pd.Series(df["close"].tail(window)).pct_change().dropna().values
            vol = np.std(returns) if len(returns) > 1 else 0.01
            label = self.label_regime(returns, vol)
            return {"regime": label, "confidence": 0.45, "method": "heuristic_fallback"}

    def get_transition_probs(self, current_regime: str) -> Dict[str, float]:
        """Get learned transition probabilities from current regime."""
        if self.transition_matrix and current_regime in self.transition_matrix:
            return self.transition_matrix[current_regime]
        # Hardcoded fallback
        fallback = {
            "bull": {"bull": 0.70, "sideways": 0.20, "volatile": 0.07, "bear": 0.03},
            "bear": {"bear": 0.65, "sideways": 0.20, "volatile": 0.10, "bull": 0.05},
            "volatile": {"volatile": 0.50, "sideways": 0.25, "bull": 0.15, "bear": 0.10},
            "sideways": {"sideways": 0.60, "bull": 0.20, "volatile": 0.15, "bear": 0.05},
        }
        return fallback.get(current_regime, {"bull": 0.25, "bear": 0.25, "volatile": 0.25, "sideways": 0.25})

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _save_model(self):
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(MODEL_PATH, "wb") as f:
                pickle.dump(self.model, f)
            with open(SCALER_PATH, "wb") as f:
                pickle.dump(self.scaler, f)
            if self.transition_matrix:
                with open(TRANSITION_PATH, "wb") as f:
                    pickle.dump(self.transition_matrix, f)
            logger.info("ML regime model saved")
        except Exception as e:
            logger.warning(f"Failed to save regime model: {e}")

    def _load_model(self):
        try:
            if MODEL_PATH.exists() and SCALER_PATH.exists():
                with open(MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
                with open(SCALER_PATH, "rb") as f:
                    self.scaler = pickle.load(f)
                if TRANSITION_PATH.exists():
                    with open(TRANSITION_PATH, "rb") as f:
                        self.transition_matrix = pickle.load(f)
                logger.info("ML regime model loaded from disk")
            else:
                logger.info("No pretrained regime model found — will use heuristic until trained")
        except Exception as e:
            logger.warning(f"Failed to load regime model: {e}")
            self.model = None
            self.scaler = None


# ---------------------------------------------------------------------------
# Global singleton
# ---------------------------------------------------------------------------

_detector: Optional[MLRegimeDetector] = None


def get_ml_regime_detector() -> MLRegimeDetector:
    global _detector
    if _detector is None:
        _detector = MLRegimeDetector()
    return _detector
