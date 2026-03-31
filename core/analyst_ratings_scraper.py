"""
Analyst Ratings Scraper
Uses yfinance .info (recommendationMean/Key) + .recommendations DataFrame.
Cache TTL: 60 minutes (ratings change at most daily).
"""
import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

LEARNING_DB = Path(__file__).parent.parent / "prometheus_learning.db"
_CACHE_TTL = 60  # minutes
_CACHE: Dict[str, Dict] = {}
_CACHE_EXPIRY: Dict[str, datetime] = {}


def _ensure_table():
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=5)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyst_rating_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                rec_mean REAL,
                rec_key TEXT,
                upgrades_14d INTEGER,
                downgrades_14d INTEGER,
                signal TEXT,
                confidence REAL
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"[AnalystRatings] Table init: {e}")


def _persist(symbol: str, result: Dict):
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=5)
        conn.execute(
            """INSERT INTO analyst_rating_signals
               (timestamp, symbol, rec_mean, rec_key, upgrades_14d, downgrades_14d, signal, confidence)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                result.get("timestamp", datetime.now().isoformat()),
                symbol,
                result.get("rec_mean", 3.0),
                result.get("rec_key", "hold"),
                result.get("upgrades_14d", 0),
                result.get("downgrades_14d", 0),
                result.get("action", "HOLD"),
                result.get("confidence", 0.0),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"[AnalystRatings] Persist error: {e}")


def _fetch_sync(symbol: str) -> Dict:
    """Synchronous yfinance fetch — called via run_in_executor."""
    try:
        import yfinance as yf
        import pandas as pd

        # Strip crypto suffixes — yfinance analyst data is equities only
        clean = symbol.replace("/USD", "").replace("/", "").upper()
        ticker = yf.Ticker(clean)
        info = ticker.info or {}

        rec_mean = float(info.get("recommendationMean") or 3.0)
        rec_key = str(info.get("recommendationKey") or "hold").lower()

        # Normalize: 1=StrongBuy→+1.0 … 5=StrongSell→-1.0
        norm_score = (3.0 - rec_mean) / 2.0

        if norm_score > 0.25:
            action = "BUY"
            confidence = min(0.85, norm_score)
        elif norm_score < -0.25:
            action = "SELL"
            confidence = min(0.85, abs(norm_score))
        else:
            action = "HOLD"
            confidence = 0.40

        upgrades_14d = 0
        downgrades_14d = 0

        try:
            rec_df = ticker.recommendations
            if rec_df is not None and not rec_df.empty:
                cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=14)
                if rec_df.index.tz is None:
                    rec_df.index = rec_df.index.tz_localize("UTC")
                recent = rec_df[rec_df.index >= cutoff]
                if not recent.empty and "To Grade" in recent.columns:
                    buy_terms = ["buy", "outperform", "overweight", "strong buy", "positive"]
                    sell_terms = ["sell", "underperform", "underweight", "strong sell", "negative"]
                    grades = recent["To Grade"].str.lower()
                    upgrades_14d = int(grades.str.contains("|".join(buy_terms), na=False).sum())
                    downgrades_14d = int(grades.str.contains("|".join(sell_terms), na=False).sum())
                    if upgrades_14d > downgrades_14d and action == "BUY":
                        confidence = min(0.90, confidence + 0.05 * upgrades_14d)
                    elif downgrades_14d > upgrades_14d and action == "SELL":
                        confidence = min(0.90, confidence + 0.05 * downgrades_14d)
        except Exception:
            pass

        return {
            "action": action,
            "confidence": round(confidence, 4),
            "rec_mean": round(rec_mean, 2),
            "rec_key": rec_key,
            "upgrades_14d": upgrades_14d,
            "downgrades_14d": downgrades_14d,
        }

    except Exception as e:
        logger.debug(f"[AnalystRatings] Sync fetch error for {symbol}: {e}")
        return {"action": "HOLD", "confidence": 0.0, "rec_mean": 3.0, "rec_key": "hold",
                "upgrades_14d": 0, "downgrades_14d": 0}


async def get_analyst_signal(symbol: str, force_refresh: bool = False) -> Dict:
    """
    Fetch analyst consensus for a symbol.
    Returns: {'action': BUY|SELL|HOLD, 'confidence': float,
              'rec_mean': float, 'rec_key': str,
              'upgrades_14d': int, 'downgrades_14d': int, 'cached': bool}
    """
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
    result = await loop.run_in_executor(None, _fetch_sync, symbol)
    result["timestamp"] = now.isoformat()
    result["cached"] = False

    _CACHE[cache_key] = result.copy()
    _CACHE_EXPIRY[cache_key] = now + timedelta(minutes=_CACHE_TTL)
    _persist(symbol, result)

    logger.debug(
        f"[AnalystRatings] {symbol}: {result['action']} ({result['confidence']:.0%}) "
        f"mean={result['rec_mean']} key={result['rec_key']}"
    )
    return result
