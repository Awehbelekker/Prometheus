"""
Unusual Options Activity Detector
Uses yfinance options chains — free, no auth required.
Detects: volume > 3x open interest (sweep), put/call skew extremes.
Cache TTL: 15 minutes.
Weight: 1.3x (highest — direct institutional footprint).
"""
import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

LEARNING_DB = Path(__file__).parent.parent / "prometheus_learning.db"
_CACHE_TTL = 15  # minutes
_CACHE: Dict[str, Dict] = {}
_CACHE_EXPIRY: Dict[str, datetime] = {}

# Thresholds
VOL_OI_SPIKE = 3.0      # volume > 3x open interest = sweep
MIN_VOL = 1000          # minimum volume to matter
PC_BULLISH = 0.55       # put/call < 0.55 = calls dominating = bullish
PC_BEARISH = 1.80       # put/call > 1.80 = puts dominating = bearish
MAX_EXPIRY_DAYS = 21    # only look at near-term options


def _ensure_table():
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=5)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS unusual_options_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                total_call_vol INTEGER,
                total_put_vol INTEGER,
                pc_ratio REAL,
                surge_flag INTEGER,
                signal TEXT,
                confidence REAL
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"[UnusualOptions] Table init: {e}")


def _persist(symbol: str, result: Dict):
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=5)
        conn.execute(
            """INSERT INTO unusual_options_signals
               (timestamp, symbol, total_call_vol, total_put_vol, pc_ratio, surge_flag, signal, confidence)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                result.get("timestamp", datetime.now().isoformat()),
                symbol,
                result.get("call_vol", 0),
                result.get("put_vol", 0),
                result.get("pc_ratio", 1.0),
                1 if result.get("surge_detected") else 0,
                result.get("action", "HOLD"),
                result.get("confidence", 0.0),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"[UnusualOptions] Persist error: {e}")


def _analyse_chain(ticker_obj) -> Dict:
    """Synchronous yfinance options analysis."""
    from datetime import date, timedelta as td
    import pandas as pd

    expirations = ticker_obj.options
    if not expirations:
        return {"action": "HOLD", "confidence": 0.0, "call_vol": 0, "put_vol": 0, "pc_ratio": 1.0}

    today = date.today()
    cutoff = today + td(days=MAX_EXPIRY_DAYS)

    total_call_vol = 0
    total_put_vol = 0
    total_call_oi = 0
    total_put_oi = 0
    surge_detected = False

    for exp_str in expirations:
        try:
            exp_date = date.fromisoformat(exp_str)
        except ValueError:
            continue
        if exp_date > cutoff:
            continue

        try:
            chain = ticker_obj.option_chain(exp_str)
        except Exception:
            continue

        calls = chain.calls
        puts = chain.puts

        if calls is not None and not calls.empty:
            cv = int(calls["volume"].fillna(0).sum())
            coi = int(calls["openInterest"].fillna(0).sum())
            total_call_vol += cv
            total_call_oi += coi
            if coi > 0 and cv > VOL_OI_SPIKE * coi and cv > MIN_VOL:
                surge_detected = True

        if puts is not None and not puts.empty:
            pv = int(puts["volume"].fillna(0).sum())
            poi = int(puts["openInterest"].fillna(0).sum())
            total_put_vol += pv
            total_put_oi += poi
            if poi > 0 and pv > VOL_OI_SPIKE * poi and pv > MIN_VOL:
                surge_detected = True

    pc_ratio = total_put_vol / max(total_call_vol, 1)
    total_vol = total_call_vol + total_put_vol

    if total_vol < MIN_VOL:
        return {"action": "HOLD", "confidence": 0.0, "call_vol": total_call_vol,
                "put_vol": total_put_vol, "pc_ratio": round(pc_ratio, 3), "surge_detected": False}

    action = "HOLD"
    confidence = 0.0

    # Sweep detection — volume far exceeds open interest (urgent institutional order)
    if surge_detected:
        if total_call_vol > total_put_vol:
            action = "BUY"
            ratio = total_call_vol / max(total_call_oi, 1)
            confidence = min(0.90, 0.60 + ratio / 20.0)
        else:
            action = "SELL"
            ratio = total_put_vol / max(total_put_oi, 1)
            confidence = min(0.90, 0.60 + ratio / 20.0)
    # Pure put/call skew signal
    elif pc_ratio < PC_BULLISH:
        action = "BUY"
        confidence = min(0.75, (PC_BULLISH - pc_ratio) * 1.5 + 0.50)
    elif pc_ratio > PC_BEARISH:
        action = "SELL"
        confidence = min(0.75, (pc_ratio - PC_BEARISH) * 0.3 + 0.50)

    return {
        "action": action,
        "confidence": round(confidence, 4),
        "call_vol": total_call_vol,
        "put_vol": total_put_vol,
        "pc_ratio": round(pc_ratio, 3),
        "surge_detected": surge_detected,
    }


async def get_unusual_options_signal(symbol: str, force_refresh: bool = False) -> Dict:
    """
    Detect unusual options activity for a symbol.
    Returns: {'action': BUY|SELL|HOLD, 'confidence': float,
              'call_vol': int, 'put_vol': int, 'pc_ratio': float,
              'surge_detected': bool, 'cached': bool}
    """
    # Options data only makes sense for equities & ETFs
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

    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol.upper())
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _analyse_chain, ticker)
    except Exception as e:
        logger.debug(f"[UnusualOptions] Error for {symbol}: {e}")
        return {"action": "HOLD", "confidence": 0.0, "cached": False, "error": str(e)}

    result["timestamp"] = now.isoformat()
    result["cached"] = False

    _CACHE[cache_key] = result.copy()
    _CACHE_EXPIRY[cache_key] = now + timedelta(minutes=_CACHE_TTL)
    _persist(symbol, result)

    logger.debug(
        f"[UnusualOptions] {symbol}: {result['action']} ({result['confidence']:.0%}) "
        f"P/C={result['pc_ratio']} surge={result.get('surge_detected', False)}"
    )
    return result
