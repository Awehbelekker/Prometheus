"""
PROMETHEUS Market Sentiment Scraper
=====================================
Collects two high-signal free market-wide sentiment indicators:

1. CNN Fear & Greed Index  — single 0-100 score; <25 = extreme fear (buy),
                             >75 = extreme greed (sell/caution)
2. CBOE Put/Call Ratio     — >1.2 bearish, <0.7 bullish (contrarian)

Both are FREE, no API key required.  Results cached 15 min.
Persisted to prometheus_learning.db for ML training.

Usage:
    from core.market_sentiment_scraper import get_market_sentiment
    sentiment = await get_market_sentiment()
    # {'fear_greed': 38, 'fear_greed_label': 'Fear', 'put_call_ratio': 0.95,
    #  'fg_signal': 'BUY', 'pc_signal': 'NEUTRAL', 'composite_signal': 'BUY',
    #  'composite_score': 0.42, 'cached': False}
"""

import asyncio
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

_CACHE: Dict = {}
_CACHE_EXPIRY: Optional[datetime] = None
_CACHE_TTL_MINUTES = 15

LEARNING_DB = Path("prometheus_learning.db")


# ─────────────────────────────────────────────────────────────
# CNN Fear & Greed (official API endpoint)
# ─────────────────────────────────────────────────────────────
CNN_FG_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

async def _fetch_fear_greed(session) -> Dict:
    """Fetch CNN Fear & Greed Index. Returns score 0-100 and label."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.cnn.com/markets/fear-and-greed',
        }
        async with session.get(CNN_FG_URL, headers=headers, timeout=10) as resp:
            if resp.status == 200:
                data = await resp.json(content_type=None)
                score = data.get('fear_and_greed', {}).get('score', None)
                rating = data.get('fear_and_greed', {}).get('rating', 'unknown')
                if score is not None:
                    score = float(score)
                    return {'fear_greed': round(score, 1), 'fear_greed_label': rating}
    except Exception as e:
        logger.debug(f"CNN Fear&Greed fetch failed: {e}")
    return {}


# ─────────────────────────────────────────────────────────────
# CBOE Put/Call Ratio (daily from CBOE data page)
# ─────────────────────────────────────────────────────────────
CBOE_PC_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/PUT_CALL_RATIO.json"

async def _fetch_put_call(session) -> Dict:
    """Fetch CBOE equity put/call ratio. Returns latest value."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        async with session.get(CBOE_PC_URL, headers=headers, timeout=10) as resp:
            if resp.status == 200:
                data = await resp.json(content_type=None)
                # Data: {"data": [[date, open, high, low, close], ...]}
                rows = data.get('data', [])
                if rows:
                    latest = rows[-1]
                    # close is index 4
                    ratio = float(latest[4]) if len(latest) > 4 else float(latest[-1])
                    return {'put_call_ratio': round(ratio, 3)}
    except Exception as e:
        logger.debug(f"CBOE Put/Call fetch failed: {e}")
    return {}


# ─────────────────────────────────────────────────────────────
# Signal interpretation
# ─────────────────────────────────────────────────────────────

def _interpret_fear_greed(score: float) -> str:
    """Contrarian: extreme fear = buy opportunity, extreme greed = caution."""
    if score <= 25:   return 'BUY'    # extreme fear
    if score <= 40:   return 'BUY'    # fear
    if score >= 75:   return 'SELL'   # extreme greed
    if score >= 60:   return 'HOLD'   # greed / caution
    return 'HOLD'


def _interpret_put_call(ratio: float) -> str:
    """High put/call = bearish hedging → contrarian buy. Low = complacency."""
    if ratio >= 1.2:   return 'BUY'    # lots of puts = panic hedging
    if ratio >= 1.0:   return 'HOLD'
    if ratio <= 0.65:  return 'SELL'   # too many calls = complacency
    return 'HOLD'


def _composite_signal(fg_score: float, pc_ratio: float) -> tuple:
    """
    Combine Fear/Greed + Put/Call into one directional score.
    Returns (signal: str, score: float) where score -1..+1.
    """
    # Normalize Fear & Greed: 0=extreme fear→+1, 100=extreme greed→-1
    fg_norm = (50 - fg_score) / 50  # +1 at extreme fear, -1 at extreme greed

    # Normalize Put/Call: 1.2 → +0.8, 0.65 → -0.8
    pc_clamped = max(0.5, min(1.5, pc_ratio))
    pc_norm = (pc_clamped - 0.9) / 0.6   # centred at 0.9

    composite = (fg_norm * 0.6) + (pc_norm * 0.4)
    composite = max(-1.0, min(1.0, composite))

    if composite > 0.25:   signal = 'BUY'
    elif composite < -0.25: signal = 'SELL'
    else:                   signal = 'HOLD'

    return signal, round(composite, 3)


# ─────────────────────────────────────────────────────────────
# Persistence
# ─────────────────────────────────────────────────────────────

def _persist(result: Dict):
    """Save snapshot to prometheus_learning.db for ML training."""
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=5)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS market_sentiment_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                fear_greed REAL,
                fear_greed_label TEXT,
                put_call_ratio REAL,
                fg_signal TEXT,
                pc_signal TEXT,
                composite_signal TEXT,
                composite_score REAL
            )
        """)
        conn.execute(
            "INSERT INTO market_sentiment_snapshots "
            "(timestamp,fear_greed,fear_greed_label,put_call_ratio,"
            "fg_signal,pc_signal,composite_signal,composite_score) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (
                datetime.now().isoformat(),
                result.get('fear_greed'),
                result.get('fear_greed_label', ''),
                result.get('put_call_ratio'),
                result.get('fg_signal', ''),
                result.get('pc_signal', ''),
                result.get('composite_signal', ''),
                result.get('composite_score', 0),
            )
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"market_sentiment_scraper persist error: {e}")


# ─────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────

async def get_market_sentiment(force_refresh: bool = False) -> Dict:
    """
    Return Fear & Greed + Put/Call sentiment.  Cached 15 min.

    Returns dict with keys:
        fear_greed, fear_greed_label, put_call_ratio,
        fg_signal, pc_signal, composite_signal, composite_score, cached
    """
    global _CACHE, _CACHE_EXPIRY

    now = datetime.now()
    if not force_refresh and _CACHE_EXPIRY and now < _CACHE_EXPIRY and _CACHE:
        return {**_CACHE, 'cached': True}

    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            fg_data, pc_data = await asyncio.gather(
                _fetch_fear_greed(session),
                _fetch_put_call(session),
                return_exceptions=True
            )
    except Exception as e:
        logger.warning(f"market_sentiment_scraper session error: {e}")
        fg_data, pc_data = {}, {}

    if isinstance(fg_data, Exception): fg_data = {}
    if isinstance(pc_data, Exception): pc_data = {}

    fg_score = fg_data.get('fear_greed', 50.0)
    pc_ratio = pc_data.get('put_call_ratio', 0.9)

    fg_signal = _interpret_fear_greed(fg_score)
    pc_signal = _interpret_put_call(pc_ratio)
    composite_signal, composite_score = _composite_signal(fg_score, pc_ratio)

    result = {
        'fear_greed': fg_score,
        'fear_greed_label': fg_data.get('fear_greed_label', 'Neutral'),
        'put_call_ratio': pc_ratio,
        'fg_signal': fg_signal,
        'pc_signal': pc_signal,
        'composite_signal': composite_signal,
        'composite_score': composite_score,
        'cached': False,
        'fetched_at': now.isoformat(),
    }

    _CACHE = result.copy()
    _CACHE_EXPIRY = now + timedelta(minutes=_CACHE_TTL_MINUTES)

    _persist(result)
    logger.info(
        f"[Sentiment] F&G={fg_score} ({fg_data.get('fear_greed_label','?')}) "
        f"P/C={pc_ratio} → {composite_signal} ({composite_score:+.2f})"
    )
    return result
