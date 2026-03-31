"""
StockTwits Sentiment Scraper
Free public API — no auth required.
Returns bullish/bearish ratio per symbol, cached 15 min.
"""
import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

import aiohttp

logger = logging.getLogger(__name__)

LEARNING_DB = Path(__file__).parent.parent / "prometheus_learning.db"
_CACHE_TTL = 15  # minutes
_CACHE: Dict[str, Dict] = {}
_CACHE_EXPIRY: Dict[str, datetime] = {}

BASE_URL = "https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"
REQUEST_TIMEOUT = 10


def _ensure_table():
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=5)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stocktwits_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                bull_count INTEGER,
                bear_count INTEGER,
                bull_ratio REAL,
                total_tagged INTEGER,
                signal TEXT,
                confidence REAL
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"[StockTwits] Table init: {e}")


def _persist(symbol: str, result: Dict):
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=5)
        conn.execute(
            """INSERT INTO stocktwits_signals
               (timestamp, symbol, bull_count, bear_count, bull_ratio, total_tagged, signal, confidence)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                result.get("timestamp", datetime.now().isoformat()),
                symbol,
                result.get("bull_count", 0),
                result.get("bear_count", 0),
                result.get("bull_ratio", 0.5),
                result.get("total_tagged", 0),
                result.get("action", "HOLD"),
                result.get("confidence", 0.0),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"[StockTwits] Persist error: {e}")


def _clean_symbol(symbol: str) -> str:
    """StockTwits uses plain ticker — strip crypto suffixes."""
    return symbol.replace("/USD", "").replace("/", "").upper()


async def get_stocktwits_signal(symbol: str, force_refresh: bool = False) -> Dict:
    """
    Fetch StockTwits bullish/bearish ratio for a symbol.
    Returns: {'action': BUY|SELL|HOLD, 'confidence': float,
              'bull_count': int, 'bear_count': int, 'bull_ratio': float, 'cached': bool}
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

    clean = _clean_symbol(symbol)
    url = BASE_URL.format(symbol=clean)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
                headers={"User-Agent": "Mozilla/5.0"},
            ) as resp:
                if resp.status != 200:
                    return {"action": "HOLD", "confidence": 0.0, "cached": False, "error": f"HTTP {resp.status}"}
                data = await resp.json()

        messages = data.get("messages", [])
        if not messages:
            return {"action": "HOLD", "confidence": 0.0, "cached": False}

        bull_count = 0
        bear_count = 0
        for msg in messages:
            sentiment = msg.get("entities", {}).get("sentiment", {})
            if sentiment:
                basic = sentiment.get("basic", "")
                if basic == "Bullish":
                    bull_count += 1
                elif basic == "Bearish":
                    bear_count += 1

        total = bull_count + bear_count
        if total < 3:
            return {"action": "HOLD", "confidence": 0.0, "cached": False, "total_tagged": total}

        bull_ratio = bull_count / total

        if bull_ratio > 0.65:
            action = "BUY"
            confidence = min(0.80, bull_ratio)
        elif bull_ratio < 0.35:
            action = "SELL"
            confidence = min(0.80, 1.0 - bull_ratio)
        else:
            action = "HOLD"
            confidence = 0.40

        result = {
            "action": action,
            "confidence": confidence,
            "bull_count": bull_count,
            "bear_count": bear_count,
            "bull_ratio": round(bull_ratio, 4),
            "total_tagged": total,
            "timestamp": now.isoformat(),
            "cached": False,
        }

        _CACHE[cache_key] = result.copy()
        _CACHE_EXPIRY[cache_key] = now + timedelta(minutes=_CACHE_TTL)
        _persist(symbol, result)

        logger.debug(f"[StockTwits] {symbol}: {action} ({confidence:.0%}) bull={bull_ratio:.0%} n={total}")
        return result

    except asyncio.TimeoutError:
        logger.debug(f"[StockTwits] Timeout for {symbol}")
        return {"action": "HOLD", "confidence": 0.0, "cached": False, "error": "timeout"}
    except Exception as e:
        logger.debug(f"[StockTwits] Error for {symbol}: {e}")
        return {"action": "HOLD", "confidence": 0.0, "cached": False, "error": str(e)}
