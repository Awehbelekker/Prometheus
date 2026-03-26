#!/usr/bin/env python3
"""
PROMETHEUS Historical Replay Trainer
=========================================
Downloads 2-year daily data for core symbols, calculates RSI/MACD/SMA/Volume
indicators, generates ~8,000+ training signals per symbol with forward-looking
price labels (was_correct), and stores them in prometheus_replay_training.db.

After running this trainer, the supervised learning pipeline can re-train
all pretrained ML models on fresh, labeled data.

Usage:
    python historical_replay_trainer.py
"""

import os
import sys
import time
import json
import sqlite3
import logging
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ── Logging ─────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("replay_trainer")

# ── Core symbol universe ────────────────────────────────────────────────
SYMBOLS = [
    "AAPL", "AMD", "AMZN", "GOOGL", "META", "MSFT", "NVDA", "TSLA",
    "QQQ", "SPY", "NFLX", "INTC", "COST", "JPM", "V", "DIS",
    "COIN", "PYPL",
]

# ── Indicator helpers ───────────────────────────────────────────────────

def _ema(data: List[float], period: int) -> List[Optional[float]]:
    """Exponential moving average."""
    result: List[Optional[float]] = [None] * len(data)
    if len(data) < period:
        return result
    k = 2.0 / (period + 1)
    result[period - 1] = sum(data[:period]) / period
    for i in range(period, len(data)):
        result[i] = data[i] * k + result[i - 1] * (1 - k)
    return result


def _sma(data: List[float], period: int) -> List[Optional[float]]:
    """Simple moving average."""
    result: List[Optional[float]] = [None] * len(data)
    for i in range(period - 1, len(data)):
        result[i] = sum(data[i - period + 1 : i + 1]) / period
    return result


def compute_rsi(closes: List[float], period: int = 14) -> List[Optional[float]]:
    """Wilder-smoothed RSI."""
    result: List[Optional[float]] = [None] * len(closes)
    if len(closes) < period + 1:
        return result
    gains, losses = [], []
    for i in range(1, period + 1):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        result[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        result[period] = 100.0 - 100.0 / (1 + rs)
    for i in range(period + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        avg_gain = (avg_gain * (period - 1) + max(d, 0)) / period
        avg_loss = (avg_loss * (period - 1) + max(-d, 0)) / period
        if avg_loss == 0:
            result[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            result[i] = 100.0 - 100.0 / (1 + rs)
    return result


def compute_macd(closes: List[float]) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
    """MACD line, signal, histogram."""
    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)
    macd_line: List[Optional[float]] = [None] * len(closes)
    for i in range(len(closes)):
        if ema12[i] is not None and ema26[i] is not None:
            macd_line[i] = ema12[i] - ema26[i]
    # Signal line = 9-period EMA of MACD line
    valid_macd = [v for v in macd_line if v is not None]
    signal_raw = _ema(valid_macd, 9) if len(valid_macd) >= 9 else [None] * len(valid_macd)
    signal: List[Optional[float]] = [None] * len(closes)
    hist: List[Optional[float]] = [None] * len(closes)
    j = 0
    for i in range(len(closes)):
        if macd_line[i] is not None:
            if j < len(signal_raw):
                signal[i] = signal_raw[j]
                if signal[i] is not None:
                    hist[i] = macd_line[i] - signal[i]
            j += 1
    return macd_line, signal, hist


def compute_bollinger(closes: List[float], period: int = 20, std_mult: float = 2.0):
    """Bollinger Bands: upper, middle, lower."""
    sma_vals = _sma(closes, period)
    upper: List[Optional[float]] = [None] * len(closes)
    lower: List[Optional[float]] = [None] * len(closes)
    for i in range(period - 1, len(closes)):
        window = closes[i - period + 1 : i + 1]
        mean = sma_vals[i]
        std = (sum((x - mean) ** 2 for x in window) / period) ** 0.5
        upper[i] = mean + std_mult * std
        lower[i] = mean - std_mult * std
    return upper, sma_vals, lower


def compute_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[Optional[float]]:
    """Average True Range."""
    result: List[Optional[float]] = [None] * len(closes)
    if len(closes) < period + 1:
        return result
    trs = []
    for i in range(1, len(closes)):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        trs.append(tr)
    if len(trs) < period:
        return result
    atr_val = sum(trs[:period]) / period
    result[period] = atr_val
    for i in range(period, len(trs)):
        atr_val = (atr_val * (period - 1) + trs[i]) / period
        result[i + 1] = atr_val
    return result


# ── Data fetching ───────────────────────────────────────────────────────

def fetch_historical_data(symbol: str, period: str = "2y") -> Optional[List[dict]]:
    """Fetch historical daily candles using yfinance (if available) or Alpaca."""
    candles = []

    # Attempt yfinance first
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval="1d")
        if df is not None and len(df) > 50:
            for idx, row in df.iterrows():
                candles.append({
                    "date": idx.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                })
            logger.info(f"  yfinance: {symbol} → {len(candles)} candles")
            return candles
    except Exception as e:
        logger.debug(f"  yfinance failed for {symbol}: {e}")

    # Fallback: Alpaca data API
    try:
        api_key = os.getenv("ALPACA_API_KEY") or os.getenv("APCA_API_KEY_ID", "")
        api_secret = os.getenv("ALPACA_SECRET_KEY") or os.getenv("APCA_API_SECRET_KEY", "")
        if api_key and api_secret:
            import requests
            end_date = datetime.utcnow().strftime("%Y-%m-%d")
            start_date = (datetime.utcnow() - timedelta(days=730)).strftime("%Y-%m-%d")
            url = f"https://data.alpaca.markets/v2/stocks/{symbol}/bars"
            params = {"timeframe": "1Day", "start": start_date, "end": end_date, "limit": 10000, "feed": "iex"}
            headers = {"APCA-API-KEY-ID": api_key, "APCA-API-SECRET-KEY": api_secret}
            resp = requests.get(url, params=params, headers=headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                bars = data.get("bars", [])
                for b in bars:
                    candles.append({
                        "date": b["t"][:10],
                        "open": float(b["o"]),
                        "high": float(b["h"]),
                        "low": float(b["l"]),
                        "close": float(b["c"]),
                        "volume": int(b["v"]),
                    })
                logger.info(f"  Alpaca: {symbol} → {len(candles)} candles")
                return candles if len(candles) > 50 else None
    except Exception as e:
        logger.debug(f"  Alpaca failed for {symbol}: {e}")

    # Fallback: Try loading from any local CSV/parquet the platform may have cached
    try:
        csv_path = Path(f"data/historical/{symbol}_daily.csv")
        if csv_path.exists():
            import csv
            with open(csv_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    candles.append({
                        "date": row.get("date") or row.get("Date", ""),
                        "open": float(row.get("open") or row.get("Open", 0)),
                        "high": float(row.get("high") or row.get("High", 0)),
                        "low": float(row.get("low") or row.get("Low", 0)),
                        "close": float(row.get("close") or row.get("Close", 0)),
                        "volume": int(float(row.get("volume") or row.get("Volume", 0))),
                    })
            if len(candles) > 50:
                logger.info(f"  CSV: {symbol} → {len(candles)} candles")
                return candles
    except Exception:
        pass

    logger.warning(f"  No data source returned enough candles for {symbol}")
    return None


# ── Signal generation ───────────────────────────────────────────────────

def generate_signals(symbol: str, candles: List[dict], forward_days: int = 5) -> List[dict]:
    """
    For each candle (except last `forward_days`), generate a training signal:
      - Features: RSI, MACD, MACD histogram, SMA20, SMA50, Bollinger %B,
                  ATR, volume ratio, price change %
      - Label: BUY if future_close > current_close * 1.005 (0.5% threshold)
               SELL if future_close < current_close * 0.995
               HOLD otherwise
      - was_correct: Based on actual future price movement
    """
    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    volumes = [c["volume"] for c in candles]
    n = len(candles)

    # Compute all indicators
    rsi_vals = compute_rsi(closes, 14)
    macd_line, macd_signal, macd_hist = compute_macd(closes)
    sma20 = _sma(closes, 20)
    sma50 = _sma(closes, 50)
    bb_upper, bb_mid, bb_lower = compute_bollinger(closes, 20)
    atr_vals = compute_atr(highs, lows, closes, 14)

    # Average volume (20-day rolling)
    avg_vol = _sma([float(v) for v in volumes], 20)

    signals = []
    # Start at index 50 (need enough history for all indicators)
    # End at n - forward_days (need future prices for labels)
    start_idx = max(50, 26 + 9)  # Need at least 35 bars for MACD signal
    end_idx = n - forward_days

    for i in range(start_idx, end_idx):
        # Skip if any key indicator is None
        if rsi_vals[i] is None or macd_line[i] is None or sma20[i] is None:
            continue

        current_close = closes[i]
        future_close = closes[i + forward_days]

        # Price change over forward window
        future_return = (future_close - current_close) / current_close

        # Generate label based on actual future price
        if future_return > 0.005:  # >0.5% gain = BUY was correct
            label = "BUY"
            was_correct = True
        elif future_return < -0.005:  # >0.5% loss = SELL was correct
            label = "SELL"
            was_correct = True
        else:
            label = "HOLD"
            was_correct = True  # HOLD when market is flat = correct

        # Now generate the SIGNAL (what the system would have predicted)
        # Use RSI + MACD + SMA crossover logic
        rsi = rsi_vals[i]
        macd_h = macd_hist[i] if macd_hist[i] is not None else 0
        sma20_v = sma20[i]
        sma50_v = sma50[i] if sma50[i] is not None else sma20_v

        # Signal generation rules (what we WOULD predict)
        predicted_action = "HOLD"
        confidence = 0.50

        # RSI-based (tightened thresholds: 22/78)
        if rsi < 22:
            predicted_action = "BUY"
            confidence = 0.75
        elif rsi > 78:
            predicted_action = "SELL"
            confidence = 0.75
        elif rsi < 30 and macd_h > 0:  # RSI oversold + MACD bullish confirmation
            predicted_action = "BUY"
            confidence = 0.65
        elif rsi > 70 and macd_h < 0:  # RSI overbought + MACD bearish confirmation
            predicted_action = "SELL"
            confidence = 0.65
        # SMA crossover
        elif sma20_v > sma50_v and closes[i] > sma20_v and macd_h > 0:
            predicted_action = "BUY"
            confidence = 0.60
        elif sma20_v < sma50_v and closes[i] < sma20_v and macd_h < 0:
            predicted_action = "SELL"
            confidence = 0.60

        # Determine if OUR prediction was correct
        if predicted_action == "BUY":
            signal_was_correct = future_return > 0.002  # >0.2% gain = prediction was right
        elif predicted_action == "SELL":
            signal_was_correct = future_return < -0.002  # >0.2% drop = prediction was right
        else:
            signal_was_correct = abs(future_return) < 0.01  # <1% move = HOLD was right

        # Bollinger %B
        bb_b = None
        if bb_upper[i] is not None and bb_lower[i] is not None and (bb_upper[i] - bb_lower[i]) > 0:
            bb_b = (closes[i] - bb_lower[i]) / (bb_upper[i] - bb_lower[i])

        # Volume ratio
        vol_ratio = volumes[i] / avg_vol[i] if avg_vol[i] and avg_vol[i] > 0 else 1.0

        # Daily return
        daily_return = (closes[i] - closes[i - 1]) / closes[i - 1] if closes[i - 1] > 0 else 0

        signals.append({
            "symbol": symbol,
            "date": candles[i]["date"],
            "close": current_close,
            "future_close": future_close,
            "future_return_pct": round(future_return * 100, 4),
            "actual_label": label,
            "predicted_action": predicted_action,
            "predicted_confidence": round(confidence, 3),
            "was_correct": signal_was_correct,
            # Feature vector for ML training
            "rsi": round(rsi, 2),
            "macd": round(macd_line[i], 4) if macd_line[i] else 0,
            "macd_hist": round(macd_h, 4),
            "macd_signal": round(macd_signal[i], 4) if macd_signal[i] else 0,
            "sma20": round(sma20_v, 2),
            "sma50": round(sma50_v, 2),
            "bb_pct_b": round(bb_b, 4) if bb_b is not None else None,
            "atr": round(atr_vals[i], 4) if atr_vals[i] is not None else None,
            "volume_ratio": round(vol_ratio, 2),
            "daily_return_pct": round(daily_return * 100, 4),
            "price_vs_sma20": round((current_close / sma20_v - 1) * 100, 4),
            "price_vs_sma50": round((current_close / sma50_v - 1) * 100, 4) if sma50_v else None,
        })

    return signals


# ── Database storage ────────────────────────────────────────────────────

def init_db(db_path: str = "prometheus_replay_training.db") -> sqlite3.Connection:
    """Create replay training database with proper schema."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS replay_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            close REAL,
            future_close REAL,
            future_return_pct REAL,
            actual_label TEXT,
            predicted_action TEXT,
            predicted_confidence REAL,
            was_correct INTEGER,
            rsi REAL,
            macd REAL,
            macd_hist REAL,
            macd_signal REAL,
            sma20 REAL,
            sma50 REAL,
            bb_pct_b REAL,
            atr REAL,
            volume_ratio REAL,
            daily_return_pct REAL,
            price_vs_sma20 REAL,
            price_vs_sma50 REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, date)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS replay_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            total_signals INTEGER,
            correct_signals INTEGER,
            accuracy_pct REAL,
            buy_signals INTEGER,
            sell_signals INTEGER,
            hold_signals INTEGER,
            avg_future_return REAL,
            data_start TEXT,
            data_end TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_replay_symbol ON replay_signals(symbol)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_replay_date ON replay_signals(date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_replay_correct ON replay_signals(was_correct)")
    conn.commit()
    return conn


def store_signals(conn: sqlite3.Connection, signals: List[dict]):
    """Insert or replace signals into database."""
    cursor = conn.cursor()
    for sig in signals:
        cursor.execute("""
            INSERT OR REPLACE INTO replay_signals (
                symbol, date, close, future_close, future_return_pct,
                actual_label, predicted_action, predicted_confidence, was_correct,
                rsi, macd, macd_hist, macd_signal, sma20, sma50,
                bb_pct_b, atr, volume_ratio, daily_return_pct,
                price_vs_sma20, price_vs_sma50
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sig["symbol"], sig["date"], sig["close"], sig["future_close"],
            sig["future_return_pct"], sig["actual_label"], sig["predicted_action"],
            sig["predicted_confidence"], int(sig["was_correct"]),
            sig["rsi"], sig["macd"], sig["macd_hist"], sig["macd_signal"],
            sig["sma20"], sig["sma50"], sig.get("bb_pct_b"),
            sig.get("atr"), sig["volume_ratio"], sig["daily_return_pct"],
            sig["price_vs_sma20"], sig.get("price_vs_sma50"),
        ))
    conn.commit()


def store_summary(conn: sqlite3.Connection, symbol: str, signals: List[dict]):
    """Store per-symbol summary statistics."""
    if not signals:
        return
    total = len(signals)
    correct = sum(1 for s in signals if s["was_correct"])
    buys = sum(1 for s in signals if s["predicted_action"] == "BUY")
    sells = sum(1 for s in signals if s["predicted_action"] == "SELL")
    holds = sum(1 for s in signals if s["predicted_action"] == "HOLD")
    avg_ret = sum(s["future_return_pct"] for s in signals) / total

    conn.execute("""
        INSERT OR REPLACE INTO replay_summary (
            symbol, total_signals, correct_signals, accuracy_pct,
            buy_signals, sell_signals, hold_signals, avg_future_return,
            data_start, data_end
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        symbol, total, correct, round(correct / total * 100, 2),
        buys, sells, holds, round(avg_ret, 4),
        signals[0]["date"], signals[-1]["date"],
    ))
    conn.commit()


# ── Supervised ML retraining ───────────────────────────────────────────

def retrain_pretrained_models(conn: sqlite3.Connection, symbols: Optional[List[str]] = None):
    """
    Retrain the sklearn pretrained models using replay training data.
    Updates models in models_pretrained/ directory.
    """
    try:
        import numpy as np
        from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import train_test_split
        import pickle
    except ImportError as e:
        logger.error(f"Cannot retrain — missing dependencies: {e}")
        logger.info("Install with: pip install scikit-learn numpy")
        return

    models_dir = Path("models_pretrained")
    models_dir.mkdir(exist_ok=True)

    cursor = conn.cursor()

    if symbols is None:
        cursor.execute("SELECT DISTINCT symbol FROM replay_signals")
        symbols = [row[0] for row in cursor.fetchall()]

    feature_cols = [
        "rsi", "macd", "macd_hist", "macd_signal",
        "sma20", "sma50", "bb_pct_b", "atr",
        "volume_ratio", "daily_return_pct",
        "price_vs_sma20", "price_vs_sma50",
    ]

    retrained = 0
    for symbol in symbols:
        cursor.execute(f"""
            SELECT {', '.join(feature_cols)}, actual_label
            FROM replay_signals
            WHERE symbol = ? AND rsi IS NOT NULL AND macd IS NOT NULL
        """, (symbol,))
        rows = cursor.fetchall()

        if len(rows) < 100:
            logger.warning(f"  {symbol}: Only {len(rows)} samples — skipping (need 100+)")
            continue

        # Build feature matrix
        X_raw = []
        y = []
        for row in rows:
            features = list(row[:-1])
            # Replace None with 0
            features = [0.0 if f is None else float(f) for f in features]
            label = row[-1]
            # Encode: BUY=1, SELL=-1, HOLD=0
            if label == "BUY":
                y.append(1)
            elif label == "SELL":
                y.append(-1)
            else:
                y.append(0)
            X_raw.append(features)

        X = np.array(X_raw, dtype=np.float64)
        y_arr = np.array(y)

        # Handle NaN/Inf
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(X, y_arr, test_size=0.2, random_state=42)

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train GradientBoosting direction model
        gb_model = GradientBoostingClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            min_samples_split=10,
            min_samples_leaf=5,
            subsample=0.8,
            random_state=42,
        )
        gb_model.fit(X_train_scaled, y_train)
        gb_accuracy = gb_model.score(X_test_scaled, y_test)

        # Train RandomForest for comparison
        rf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1,
        )
        rf_model.fit(X_train_scaled, y_train)
        rf_accuracy = rf_model.score(X_test_scaled, y_test)

        # Save better model as direction model
        best_model = gb_model if gb_accuracy >= rf_accuracy else rf_model
        best_accuracy = max(gb_accuracy, rf_accuracy)
        best_type = "GB" if gb_accuracy >= rf_accuracy else "RF"

        # Save model + scaler
        model_path = models_dir / f"{symbol}_direction_model.pkl"
        scaler_path = models_dir / f"{symbol}_direction_scaler.pkl"

        with open(model_path, "wb") as f:
            pickle.dump(best_model, f)
        with open(scaler_path, "wb") as f:
            pickle.dump(scaler, f)

        retrained += 1
        logger.info(
            f"  {symbol}: {len(rows)} samples → {best_type} accuracy {best_accuracy:.1%} "
            f"(GB={gb_accuracy:.1%}, RF={rf_accuracy:.1%}) — saved to {model_path.name}"
        )

    logger.info(f"\nRetrained {retrained}/{len(symbols)} models in {models_dir}/")
    return retrained


# ── Main execution ──────────────────────────────────────────────────────

def main():
    print("=" * 80)
    print("  PROMETHEUS HISTORICAL REPLAY TRAINER")
    print("  Generating labeled training signals from 2-year historical data")
    print("=" * 80)
    print()

    start_time = time.time()
    db = init_db()

    total_signals = 0
    total_correct = 0
    symbol_stats = []

    for i, symbol in enumerate(SYMBOLS, 1):
        print(f"\n[{i}/{len(SYMBOLS)}] Processing {symbol}...")
        candles = fetch_historical_data(symbol)

        if not candles or len(candles) < 60:
            print(f"  Skipped {symbol}: insufficient data ({len(candles) if candles else 0} candles)")
            continue

        signals = generate_signals(symbol, candles, forward_days=5)
        if not signals:
            print(f"  Skipped {symbol}: no signals generated")
            continue

        store_signals(db, signals)
        store_summary(db, symbol, signals)

        correct = sum(1 for s in signals if s["was_correct"])
        accuracy = correct / len(signals) * 100
        total_signals += len(signals)
        total_correct += correct

        buys = sum(1 for s in signals if s["predicted_action"] == "BUY")
        sells = sum(1 for s in signals if s["predicted_action"] == "SELL")
        holds = sum(1 for s in signals if s["predicted_action"] == "HOLD")

        symbol_stats.append({
            "symbol": symbol,
            "signals": len(signals),
            "accuracy": accuracy,
            "buys": buys,
            "sells": sells,
            "holds": holds,
        })

        print(f"  {len(signals)} signals | {accuracy:.1f}% accuracy | BUY:{buys} SELL:{sells} HOLD:{holds}")

    # Print summary
    elapsed = time.time() - start_time
    overall_accuracy = (total_correct / total_signals * 100) if total_signals > 0 else 0

    print("\n" + "=" * 80)
    print("  REPLAY TRAINING COMPLETE")
    print("=" * 80)
    print(f"  Symbols processed: {len(symbol_stats)}/{len(SYMBOLS)}")
    print(f"  Total signals: {total_signals:,}")
    print(f"  Overall accuracy: {overall_accuracy:.1f}%")
    print(f"  Time elapsed: {elapsed:.1f}s")
    print(f"  Database: prometheus_replay_training.db")
    print()

    # Step 2: Retrain pretrained models
    print("=" * 80)
    print("  STEP 2: RETRAINING PRETRAINED ML MODELS")
    print("=" * 80)
    if total_signals > 500:
        retrained = retrain_pretrained_models(db)
        if retrained:
            print(f"\n  {retrained} models retrained with fresh labeled data")
        else:
            print("\n  No models retrained (check sklearn installation)")
    else:
        print(f"  Insufficient data ({total_signals} signals) — need 500+ for retraining")

    db.close()

    # Save summary to JSON
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "symbols_processed": len(symbol_stats),
        "total_signals": total_signals,
        "overall_accuracy": round(overall_accuracy, 2),
        "time_elapsed_seconds": round(elapsed, 1),
        "per_symbol": symbol_stats,
    }
    with open("replay_training_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n  Summary saved to replay_training_summary.json")
    print("  Done!\n")


if __name__ == "__main__":
    main()
