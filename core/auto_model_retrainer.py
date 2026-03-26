"""
PROMETHEUS Auto Model Retraining Pipeline
==========================================
Automated, scheduled retraining of all 130 pretrained models with:
  - Staleness detection (retrain only when models are older than threshold)
  - Fresh market data fetching via yfinance
  - Walk-forward validation (train on history, validate on holdout)
  - Model backup before overwrite
  - Accuracy / MSE gate — new model must beat old model or a minimum bar
  - Logging results to prometheus_learning.db
  - Supports manual trigger and scheduled (AsyncIO loop) execution
"""

import asyncio
import logging
import shutil
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MODELS_DIR = Path("models_pretrained")
BACKUP_DIR = MODELS_DIR / "backups"
LEARNING_DB = Path("prometheus_learning.db")

DIRECTION_SYMBOLS: List[str] = [
    "AAPL", "AMD", "AMZN", "AVAX-USD", "ADA-USD", "BAC", "BNB-USD",
    "BTC-USD", "COIN", "COST", "CRM", "DIA", "DIS", "DOT-USD",
    "ETH-USD", "GOOGL", "HD", "INTC", "IWM", "JPM", "MATIC-USD",
    "META", "MSFT", "NFLX", "NVDA", "ORCL", "PYPL", "QQQ",
    "SOL-USD", "SPY", "TSLA", "UNH", "V", "WMT",
]

# Feature columns used by historically trained models
FEATURE_COLS = [
    "rsi", "macd", "macd_signal", "bb_upper", "bb_lower",
    "sma_20", "ema_12", "volume_ratio", "daily_return",
    "price_vs_sma20", "volatility",
]

# Staleness threshold  (retrain if older than N days)
DEFAULT_STALE_DAYS = 7
# Minimum accuracy a new direction model must achieve to replace old one
MIN_DIRECTION_ACCURACY = 0.45
# Minimum R² for price model to replace old one
MIN_PRICE_R2 = 0.0
# Minimum number of data rows needed
MIN_TRAINING_ROWS = 120


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------
@dataclass
class RetrainResult:
    symbol: str
    model_type: str          # "direction" | "price" | "intraday"
    success: bool
    old_metric: Optional[float] = None
    new_metric: Optional[float] = None
    samples: int = 0
    backed_up: bool = False
    reason: str = ""
    duration_s: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class PipelineReport:
    started: str
    finished: str
    duration_s: float
    symbols_attempted: int
    models_retrained: int
    models_skipped: int
    models_failed: int
    results: List[RetrainResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helper: compute technical features from OHLCV DataFrame
# ---------------------------------------------------------------------------
def _compute_features(df):
    """Add technical indicator columns to an OHLCV DataFrame (from yfinance)."""
    import pandas as pd

    c = df["Close"].values.astype(float)
    h = df["High"].values.astype(float)
    lo = df["Low"].values.astype(float)
    v = df["Volume"].values.astype(float)

    # RSI (14)
    delta = np.diff(c, prepend=c[0])
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = pd.Series(gain).rolling(14, min_periods=1).mean().values
    avg_loss = pd.Series(loss).rolling(14, min_periods=1).mean().values
    rs = avg_gain / np.where(avg_loss == 0, 1e-10, avg_loss)
    df["rsi"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = pd.Series(c).ewm(span=12, adjust=False).mean().values
    ema26 = pd.Series(c).ewm(span=26, adjust=False).mean().values
    df["macd"] = ema12 - ema26
    df["macd_signal"] = pd.Series(df["macd"]).ewm(span=9, adjust=False).mean().values

    # Bollinger Bands
    sma20 = pd.Series(c).rolling(20, min_periods=1).mean().values
    std20 = pd.Series(c).rolling(20, min_periods=1).std().values
    df["bb_upper"] = sma20 + 2 * std20
    df["bb_lower"] = sma20 - 2 * std20
    df["sma_20"] = sma20

    # EMA 12  (already computed)
    df["ema_12"] = ema12

    # Volume ratio (vs 20-day avg)
    vol_ma = pd.Series(v).rolling(20, min_periods=1).mean().values
    df["volume_ratio"] = v / np.where(vol_ma == 0, 1, vol_ma)

    # Daily return
    df["daily_return"] = np.concatenate([[0], np.diff(c) / np.where(c[:-1] == 0, 1, c[:-1])])

    # Price vs SMA-20
    df["price_vs_sma20"] = (c - sma20) / np.where(sma20 == 0, 1, sma20)

    # Volatility (20-day rolling std of returns)
    df["volatility"] = pd.Series(df["daily_return"]).rolling(20, min_periods=1).std().values

    return df


# ---------------------------------------------------------------------------
# Core retraining class
# ---------------------------------------------------------------------------
class AutoModelRetrainer:
    """Orchestrates automated model retraining."""

    def __init__(
        self,
        stale_days: int = DEFAULT_STALE_DAYS,
        min_direction_accuracy: float = MIN_DIRECTION_ACCURACY,
        min_price_r2: float = MIN_PRICE_R2,
        symbols: Optional[List[str]] = None,
    ):
        self.stale_days = stale_days
        self.min_direction_accuracy = min_direction_accuracy
        self.min_price_r2 = min_price_r2
        self.symbols = symbols or DIRECTION_SYMBOLS
        self._running = False
        self._schedule_task: Optional[asyncio.Task] = None
        logger.info(
            f"AutoModelRetrainer initialised — {len(self.symbols)} symbols, "
            f"stale_days={stale_days}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def retrain_all(self, force: bool = False) -> PipelineReport:
        """Run a full retraining sweep across all symbols."""
        t0 = time.time()
        started = datetime.utcnow().isoformat()
        results: List[RetrainResult] = []
        retrained = skipped = failed = 0

        for symbol in self.symbols:
            for mtype in ("direction", "price"):
                res = await self._retrain_one(symbol, mtype, force=force)
                results.append(res)
                if res.success:
                    retrained += 1
                elif res.reason.startswith("skip"):
                    skipped += 1
                else:
                    failed += 1

        duration = time.time() - t0
        report = PipelineReport(
            started=started,
            finished=datetime.utcnow().isoformat(),
            duration_s=round(duration, 1),
            symbols_attempted=len(self.symbols),
            models_retrained=retrained,
            models_skipped=skipped,
            models_failed=failed,
            results=results,
        )
        self._log_report(report)
        logger.info(
            f"Retraining complete — {retrained} retrained, "
            f"{skipped} skipped, {failed} failed  ({duration:.0f}s)"
        )
        return report

    async def retrain_symbol(self, symbol: str, force: bool = False) -> List[RetrainResult]:
        """Retrain all model types for a single symbol."""
        results = []
        for mtype in ("direction", "price"):
            results.append(await self._retrain_one(symbol, mtype, force=force))
        return results

    def start_schedule(self, interval_hours: float = 168):
        """Start a background retraining loop (default: weekly = 168 h)."""
        if self._schedule_task and not self._schedule_task.done():
            logger.warning("Schedule already running")
            return
        self._running = True
        self._schedule_task = asyncio.ensure_future(self._schedule_loop(interval_hours))
        logger.info(f"Retraining schedule started — every {interval_hours}h")

    def stop_schedule(self):
        self._running = False
        if self._schedule_task:
            self._schedule_task.cancel()
        logger.info("Retraining schedule stopped")

    def get_status(self) -> Dict[str, Any]:
        stale = self._count_stale()
        return {
            "name": "Auto Model Retrainer",
            "active": True,
            "schedule_running": self._running,
            "symbols": len(self.symbols),
            "stale_threshold_days": self.stale_days,
            "stale_models": stale,
            "total_models": self._count_models(),
            "backup_dir": str(BACKUP_DIR),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _schedule_loop(self, interval_hours: float):
        """Periodic retraining loop."""
        while self._running:
            try:
                logger.info("Scheduled retraining triggered")
                await self.retrain_all(force=False)
            except Exception as exc:
                logger.error(f"Scheduled retrain error: {exc}")
            await asyncio.sleep(interval_hours * 3600)

    async def _retrain_one(
        self, symbol: str, model_type: str, force: bool = False
    ) -> RetrainResult:
        """Retrain a single model (direction or price) for one symbol."""
        t0 = time.time()

        model_path = MODELS_DIR / f"{symbol}_{model_type}_model.pkl"
        scaler_path = MODELS_DIR / f"{symbol}_{model_type}_scaler.pkl"

        # --- staleness check ---
        if not force and model_path.exists():
            age_days = (time.time() - model_path.stat().st_mtime) / 86400
            if age_days < self.stale_days:
                return RetrainResult(
                    symbol=symbol,
                    model_type=model_type,
                    success=False,
                    reason=f"skip:fresh ({age_days:.1f}d < {self.stale_days}d)",
                    duration_s=0,
                )

        # --- fetch data ---
        try:
            df = await asyncio.get_event_loop().run_in_executor(
                None, self._fetch_data, symbol
            )
        except Exception as exc:
            return RetrainResult(
                symbol=symbol,
                model_type=model_type,
                success=False,
                reason=f"data_fetch_error: {exc}",
                duration_s=time.time() - t0,
            )

        if df is None or len(df) < MIN_TRAINING_ROWS:
            return RetrainResult(
                symbol=symbol,
                model_type=model_type,
                success=False,
                reason=f"insufficient_data ({0 if df is None else len(df)} rows)",
                duration_s=time.time() - t0,
            )

        # --- compute features ---
        df = _compute_features(df)
        feature_matrix = df[FEATURE_COLS].values.astype(np.float64)
        feature_matrix = np.nan_to_num(feature_matrix, nan=0.0, posinf=0.0, neginf=0.0)

        if model_type == "direction":
            result = self._train_direction(symbol, feature_matrix, df, model_path, scaler_path)
        else:
            result = self._train_price(symbol, feature_matrix, df, model_path, scaler_path)

        result.duration_s = round(time.time() - t0, 2)
        return result

    # ------------------------------------------------------------------
    # Data fetch
    # ------------------------------------------------------------------

    @staticmethod
    def _fetch_data(symbol: str):
        """Fetch ~2 years of daily OHLCV via yfinance."""
        import yfinance as yf

        ticker = yf.Ticker(symbol)
        df = ticker.history(period="2y", interval="1d")
        if df is None or df.empty:
            return None
        return df

    # ------------------------------------------------------------------
    # Direction model training
    # ------------------------------------------------------------------

    def _train_direction(
        self,
        symbol: str,
        X: np.ndarray,
        df,
        model_path: Path,
        scaler_path: Path,
    ) -> RetrainResult:
        from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler

        # Label: next day up (1) or down (0)
        close = df["Close"].values.astype(float)
        y = (np.roll(close, -1) > close).astype(int)
        # Drop last row (no future label)
        X = X[:-1]
        y = y[:-1]

        if len(X) < MIN_TRAINING_ROWS:
            return RetrainResult(symbol=symbol, model_type="direction", success=False,
                                 reason="insufficient_rows_after_label", samples=len(X))

        # Walk-forward split: last 20 % for validation
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]

        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_val_s = scaler.transform(X_val)

        # Train two candidates
        gb = GradientBoostingClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.05,
            min_samples_split=10, min_samples_leaf=5, subsample=0.8, random_state=42,
        )
        gb.fit(X_train_s, y_train)
        gb_acc = gb.score(X_val_s, y_val)

        rf = RandomForestClassifier(
            n_estimators=200, max_depth=8, min_samples_split=10,
            min_samples_leaf=5, random_state=42, n_jobs=-1,
        )
        rf.fit(X_train_s, y_train)
        rf_acc = rf.score(X_val_s, y_val)

        best_model = gb if gb_acc >= rf_acc else rf
        best_acc = max(gb_acc, rf_acc)
        best_tag = "GB" if gb_acc >= rf_acc else "RF"

        # --- evaluate old model on same validation set ---
        old_acc = self._evaluate_old_model(model_path, scaler_path, X_val, y_val)

        # Gate: new must beat old (or old absent) AND meet minimum bar
        if best_acc < self.min_direction_accuracy:
            # Augmented training fallback before giving up
            aug_result = self._augmented_training(symbol, X_train_s, y_train, X_val_s, y_val, scaler, model_path, scaler_path, old_acc)
            if aug_result is not None:
                return aug_result
            return RetrainResult(
                symbol=symbol, model_type="direction", success=False,
                old_metric=old_acc, new_metric=best_acc,
                samples=len(X), reason=f"below_min_accuracy ({best_acc:.3f} < {self.min_direction_accuracy})",
            )
        if old_acc is not None and best_acc < old_acc - 0.02:
            # Allow 2% degradation tolerance
            return RetrainResult(
                symbol=symbol, model_type="direction", success=False,
                old_metric=old_acc, new_metric=best_acc,
                samples=len(X), reason=f"worse_than_old ({best_acc:.3f} < {old_acc:.3f})",
            )

        # --- backup & save ---
        backed_up = self._backup(model_path, scaler_path)
        MODELS_DIR.mkdir(exist_ok=True)
        joblib.dump(best_model, model_path)
        joblib.dump(scaler, scaler_path)

        logger.info(
            f"  {symbol} direction: {best_tag} acc={best_acc:.3f} "
            f"(old={old_acc or 'N/A'}) — saved"
        )
        return RetrainResult(
            symbol=symbol, model_type="direction", success=True,
            old_metric=old_acc, new_metric=best_acc,
            samples=len(X), backed_up=backed_up,
        )

    # ------------------------------------------------------------------
    # Augmented training fallback (SMOTE + noise + ensemble)
    # ------------------------------------------------------------------

    def _augmented_training(
        self,
        symbol: str,
        X_train_s: np.ndarray,
        y_train: np.ndarray,
        X_val_s: np.ndarray,
        y_val: np.ndarray,
        scaler,
        model_path: Path,
        scaler_path: Path,
        old_acc,
    ):
        """
        Augmented training fallback when standard training fails the accuracy gate.
        Uses SMOTE-like oversampling, noise injection, and a 3-model voting ensemble.
        Returns a successful RetrainResult if it beats the threshold, else None.
        """
        try:
            from sklearn.ensemble import (
                GradientBoostingClassifier,
                RandomForestClassifier,
                ExtraTreesClassifier,
                VotingClassifier,
            )

            # --- 1. SMOTE-like minority oversampling ---
            classes, counts = np.unique(y_train, return_counts=True)
            if len(classes) == 2:
                minority_cls = classes[np.argmin(counts)]
                majority_cls = classes[np.argmax(counts)]
                minority_idx = np.where(y_train == minority_cls)[0]
                majority_idx = np.where(y_train == majority_cls)[0]
                deficit = len(majority_idx) - len(minority_idx)
                if deficit > 0 and len(minority_idx) >= 2:
                    # Synthetic oversampling: interpolate between minority neighbours
                    rng = np.random.default_rng(42)
                    synth = []
                    for _ in range(deficit):
                        i, j = rng.choice(len(minority_idx), size=2, replace=False)
                        lam = rng.uniform(0.1, 0.9)
                        new_sample = X_train_s[minority_idx[i]] * lam + X_train_s[minority_idx[j]] * (1 - lam)
                        synth.append(new_sample)
                    X_aug = np.vstack([X_train_s, np.array(synth)])
                    y_aug = np.concatenate([y_train, np.full(deficit, minority_cls)])
                else:
                    X_aug, y_aug = X_train_s, y_train
            else:
                X_aug, y_aug = X_train_s, y_train

            # --- 2. Noise injection (2x training data) ---
            rng = np.random.default_rng(123)
            noise = rng.normal(0, 0.05, X_aug.shape)
            X_noisy = np.vstack([X_aug, X_aug + noise])
            y_noisy = np.concatenate([y_aug, y_aug])

            # --- 3. Three-model soft voting ensemble ---
            gb = GradientBoostingClassifier(
                n_estimators=300, max_depth=4, learning_rate=0.03,
                min_samples_split=15, min_samples_leaf=8, subsample=0.7, random_state=42,
            )
            rf = RandomForestClassifier(
                n_estimators=300, max_depth=6, min_samples_split=12,
                min_samples_leaf=6, class_weight='balanced', random_state=42, n_jobs=-1,
            )
            et = ExtraTreesClassifier(
                n_estimators=300, max_depth=6, min_samples_split=12,
                min_samples_leaf=6, class_weight='balanced', random_state=42, n_jobs=-1,
            )
            ensemble = VotingClassifier(
                estimators=[('gb', gb), ('rf', rf), ('et', et)],
                voting='soft',
            )
            ensemble.fit(X_noisy, y_noisy)
            ens_acc = ensemble.score(X_val_s, y_val)

            logger.info(
                f"  {symbol} augmented training: ensemble acc={ens_acc:.3f} "
                f"(threshold={self.min_direction_accuracy})"
            )

            if ens_acc >= self.min_direction_accuracy:
                # Passes the gate — save the ensemble
                backed_up = self._backup(model_path, scaler_path)
                MODELS_DIR.mkdir(exist_ok=True)
                joblib.dump(ensemble, model_path)
                joblib.dump(scaler, scaler_path)
                logger.info(f"  {symbol} direction (augmented): ensemble acc={ens_acc:.3f} — saved")
                return RetrainResult(
                    symbol=symbol, model_type="direction", success=True,
                    old_metric=old_acc, new_metric=ens_acc,
                    samples=len(X_noisy), backed_up=backed_up,
                    reason="augmented_ensemble",
                )
            return None  # Augmented training also failed
        except Exception as exc:
            logger.warning(f"Augmented training failed for {symbol}: {exc}")
            return None

    # ------------------------------------------------------------------
    # Price model training
    # ------------------------------------------------------------------

    def _train_price(
        self,
        symbol: str,
        X: np.ndarray,
        df,
        model_path: Path,
        scaler_path: Path,
    ) -> RetrainResult:
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler

        close = df["Close"].values.astype(float)
        # Target: next day close
        y = np.roll(close, -1)
        X = X[:-1]
        y = y[:-1]

        if len(X) < MIN_TRAINING_ROWS:
            return RetrainResult(symbol=symbol, model_type="price", success=False,
                                 reason="insufficient_rows_after_label", samples=len(X))

        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]

        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_val_s = scaler.transform(X_val)

        model = RandomForestRegressor(
            n_estimators=200, max_depth=10, random_state=42, n_jobs=-1,
        )
        model.fit(X_train_s, y_train)

        preds = model.predict(X_val_s)
        # R² score
        ss_res = np.sum((y_val - preds) ** 2)
        ss_tot = np.sum((y_val - np.mean(y_val)) ** 2)
        r2 = 1 - ss_res / max(ss_tot, 1e-10)

        # Evaluate old model on same set
        old_r2 = self._evaluate_old_price_model(model_path, scaler_path, X_val, y_val)

        if r2 < self.min_price_r2:
            return RetrainResult(
                symbol=symbol, model_type="price", success=False,
                old_metric=old_r2, new_metric=r2, samples=len(X),
                reason=f"below_min_r2 ({r2:.3f})",
            )
        if old_r2 is not None and r2 < old_r2 - 0.05:
            return RetrainResult(
                symbol=symbol, model_type="price", success=False,
                old_metric=old_r2, new_metric=r2, samples=len(X),
                reason=f"worse_than_old ({r2:.3f} < {old_r2:.3f})",
            )

        backed_up = self._backup(model_path, scaler_path)
        MODELS_DIR.mkdir(exist_ok=True)
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)

        logger.info(f"  {symbol} price: R²={r2:.3f} (old={old_r2 or 'N/A'}) — saved")
        return RetrainResult(
            symbol=symbol, model_type="price", success=True,
            old_metric=old_r2, new_metric=r2,
            samples=len(X), backed_up=backed_up,
        )

    # ------------------------------------------------------------------
    # Evaluation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _evaluate_old_model(model_path: Path, scaler_path: Path,
                            X_val: np.ndarray, y_val: np.ndarray) -> Optional[float]:
        """Evaluate existing model on the validation set."""
        if not model_path.exists() or not scaler_path.exists():
            return None
        try:
            old_model = joblib.load(model_path)
            old_scaler = joblib.load(scaler_path)
            X_val_s = old_scaler.transform(X_val)
            return float(old_model.score(X_val_s, y_val))
        except Exception:
            return None

    @staticmethod
    def _evaluate_old_price_model(model_path: Path, scaler_path: Path,
                                  X_val: np.ndarray, y_val: np.ndarray) -> Optional[float]:
        if not model_path.exists() or not scaler_path.exists():
            return None
        try:
            old_model = joblib.load(model_path)
            old_scaler = joblib.load(scaler_path)
            X_val_s = old_scaler.transform(X_val)
            preds = old_model.predict(X_val_s)
            ss_res = np.sum((y_val - preds) ** 2)
            ss_tot = np.sum((y_val - np.mean(y_val)) ** 2)
            return float(1 - ss_res / max(ss_tot, 1e-10))
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Backup
    # ------------------------------------------------------------------

    @staticmethod
    def _backup(model_path: Path, scaler_path: Path) -> bool:
        """Copy current model + scaler to backups/ with timestamp."""
        try:
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            for p in (model_path, scaler_path):
                if p.exists():
                    dest = BACKUP_DIR / f"{p.stem}_{ts}{p.suffix}"
                    shutil.copy2(p, dest)
            return True
        except Exception as exc:
            logger.warning(f"Backup failed for {model_path.name}: {exc}")
            return False

    # ------------------------------------------------------------------
    # Staleness helpers
    # ------------------------------------------------------------------

    def _count_stale(self) -> int:
        count = 0
        for sym in self.symbols:
            for mt in ("direction", "price"):
                p = MODELS_DIR / f"{sym}_{mt}_model.pkl"
                if p.exists():
                    age = (time.time() - p.stat().st_mtime) / 86400
                    if age > self.stale_days:
                        count += 1
                else:
                    count += 1
        return count

    @staticmethod
    def _count_models() -> int:
        if MODELS_DIR.exists():
            return len(list(MODELS_DIR.glob("*.pkl")))
        return 0

    # ------------------------------------------------------------------
    # Persistence — log results to learning DB
    # ------------------------------------------------------------------

    def _log_report(self, report: PipelineReport):
        """Write retraining results to prometheus_learning.db."""
        try:
            conn = sqlite3.connect(str(LEARNING_DB))
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_retrain_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    symbol TEXT,
                    model_type TEXT,
                    success INTEGER,
                    old_metric REAL,
                    new_metric REAL,
                    samples INTEGER,
                    backed_up INTEGER,
                    reason TEXT,
                    duration_s REAL
                )
            """)
            for r in report.results:
                conn.execute(
                    """INSERT INTO model_retrain_log
                       (timestamp, symbol, model_type, success,
                        old_metric, new_metric, samples, backed_up, reason, duration_s)
                       VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (
                        r.timestamp, r.symbol, r.model_type, int(r.success),
                        r.old_metric, r.new_metric, r.samples,
                        int(r.backed_up), r.reason, r.duration_s,
                    ),
                )
            conn.commit()
            conn.close()
            logger.info(f"Logged {len(report.results)} retrain results to {LEARNING_DB}")
        except Exception as exc:
            logger.warning(f"Failed to log retrain report: {exc}")


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------
_instance: Optional[AutoModelRetrainer] = None

def get_retrainer() -> AutoModelRetrainer:
    global _instance
    if _instance is None:
        _instance = AutoModelRetrainer()
    return _instance
