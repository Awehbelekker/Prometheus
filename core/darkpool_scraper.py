"""
Dark Pool / Institutional Volume Surge Detector
Uses yfinance intraday volume vs 20-day average volume.
High surge with directional price move = institutional/dark pool conviction.
Cache TTL: 15 minutes.
"""
import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

LEARNING_DB = Path(__file__).parent.parent / "prometheus_learning.db"
_CACHE_TTL = 15  # minutes
_CACHE: Dict[str, Dict] = {}
_CACHE_EXPIRY: Dict[str, datetime] = {}

SURGE_THRESHOLD = 2.5       # volume > 2.5x avg = institutional
PRICE_MOVE_MIN = 0.003      # 0.3% directional move to confirm direction


def _ensure_table():
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=5)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS darkpool_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                current_vol INTEGER,
                avg_vol INTEGER,
                surge_ratio REAL,
                price_change_pct REAL,
                signal TEXT,
                confidence REAL
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"[DarkPool] Table init: {e}")


def _persist(symbol: str, result: Dict):
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=5)
        conn.execute(
            """INSERT INTO darkpool_signals
               (timestamp, symbol, current_vol, avg_vol, surge_ratio, price_change_pct, signal, confidence)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                result.get("timestamp", datetime.now().isoformat()),
                symbol,
                result.get("current_vol", 0),
                result.get("avg_vol", 0),
                result.get("surge_ratio", 1.0),
                result.get("price_change_pct", 0.0),
                result.get("action", "HOLD"),
                result.get("confidence", 0.0),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"[DarkPool] Persist error: {e}")


def _analyse_sync(symbol: str) -> Dict:
    """Synchronous yfinance intraday volume analysis."""
    try:
        import yfinance as yf

        ticker = yf.Ticker(symbol.upper())
        info = ticker.info or {}
        avg_vol = int(info.get("averageVolume") or info.get("averageDailyVolume10Day") or 1)

        # Intraday 5-min bars for today
        hist = ticker.history(period="1d", interval="5m")
        if hist is None or hist.empty:
            return {"action": "HOLD", "confidence": 0.0, "surge_ratio": 1.0}

        current_vol = int(hist["Volume"].sum())
        surge_ratio = current_vol / max(avg_vol, 1)

        # Price direction from open to last bar
        price_open = float(hist["Open"].iloc[0])
        price_last = float(hist["Close"].iloc[-1])
        pct_change = (price_last - price_open) / max(price_open, 0.01)

        action = "HOLD"
        confidence = 0.0

        if surge_ratio >= SURGE_THRESHOLD:
            if pct_change > PRICE_MOVE_MIN:
                action = "BUY"
                confidence = min(0.85, 0.50 + (surge_ratio - SURGE_THRESHOLD) * 0.10)
            elif pct_change < -PRICE_MOVE_MIN:
                action = "SELL"
                confidence = min(0.85, 0.50 + (surge_ratio - SURGE_THRESHOLD) * 0.10)
            else:
                # Volume surge but no direction — accumulation, slight BUY lean
                action = "HOLD"
                confidence = 0.40

        return {
            "action": action,
            "confidence": round(confidence, 4),
            "current_vol": current_vol,
            "avg_vol": avg_vol,
            "surge_ratio": round(surge_ratio, 3),
            "price_change_pct": round(pct_change * 100, 3),
        }

    except Exception as e:
        logger.debug(f"[DarkPool] Sync analysis error for {symbol}: {e}")
        return {"action": "HOLD", "confidence": 0.0, "surge_ratio": 1.0, "error": str(e)}


async def get_darkpool_signal(symbol: str, force_refresh: bool = False) -> Dict:
    """
    Detect institutional/dark pool volume surge for a symbol.
    Returns: {'action': BUY|SELL|HOLD, 'confidence': float,
              'surge_ratio': float, 'price_change_pct': float, 'cached': bool}
    """
    # Skip crypto — no dark pool concept
    if "/" in symbol:
        return {"action": "HOLD", "confidence": 0.0, "cached": False}

    _ensure_table()
    now = datetime.now()
    cache_key = symbol.upper()

    if (
        not force_refresh
        and cache_key in _CACHE
        and cache_key in _CACHE_EXPIRY
        and now < _CACHE_EXPIRY[cache_key]
    ):
        return {**_CACHE[cache_key], "cached": True}

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _analyse_sync, symbol)
    result["timestamp"] = now.isoformat()
    result["cached"] = False

    _CACHE[cache_key] = result.copy()
    _CACHE_EXPIRY[cache_key] = now + timedelta(minutes=_CACHE_TTL)
    _persist(symbol, result)

    logger.debug(
        f"[DarkPool] {symbol}: {result['action']} ({result['confidence']:.0%}) "
        f"surge={result.get('surge_ratio', 1.0):.1f}x Δprice={result.get('price_change_pct', 0):.2f}%"
    )
    return result
