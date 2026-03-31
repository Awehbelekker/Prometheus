"""
Insider Trading Signal Scraper
Thin caching + signal-extraction layer over core/sec_edgar_api.SECEdgarAPI.
Detects cluster buying (2+ officers), CEO/CFO buys, and mass selling.
Cache TTL: 30 minutes.
"""
import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

LEARNING_DB = Path(__file__).parent.parent / "prometheus_learning.db"
_CACHE_TTL = 30  # minutes
_CACHE: Dict[str, Dict] = {}
_CACHE_EXPIRY: Dict[str, datetime] = {}

_EXEC_TITLES = {"ceo", "cfo", "president", "chairman", "chief executive", "chief financial"}


def _ensure_table():
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=5)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS insider_trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                buy_count INTEGER,
                sell_count INTEGER,
                signal_type TEXT,
                signal TEXT,
                confidence REAL
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"[InsiderTrading] Table init: {e}")


def _persist(symbol: str, result: Dict):
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=5)
        conn.execute(
            """INSERT INTO insider_trading_signals
               (timestamp, symbol, buy_count, sell_count, signal_type, signal, confidence)
               VALUES (?,?,?,?,?,?,?)""",
            (
                result.get("timestamp", datetime.now().isoformat()),
                symbol,
                result.get("buy_count", 0),
                result.get("sell_count", 0),
                result.get("signal_type", "none"),
                result.get("action", "HOLD"),
                result.get("confidence", 0.0),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"[InsiderTrading] Persist error: {e}")


def _is_executive(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in _EXEC_TITLES)


def _analyse_trades(trades) -> Dict:
    """Convert InsiderTrade list → signal dict."""
    buy_trades = [t for t in trades if getattr(t, "transaction_type", "").lower() == "buy"]
    sell_trades = [t for t in trades if getattr(t, "transaction_type", "").lower() == "sell"]
    exec_buys = [t for t in buy_trades if _is_executive(getattr(t, "insider_title", ""))]

    action = "HOLD"
    confidence = 0.0
    signal_type = "none"

    if exec_buys:
        # CEO/CFO buying own stock — very high conviction
        action = "BUY"
        confidence = min(0.85, 0.70 + len(exec_buys) * 0.05)
        signal_type = "ceo_cfo_buy"
    elif len(buy_trades) >= 2:
        # Multiple insiders buying within the window
        action = "BUY"
        confidence = min(0.85, 0.50 + len(buy_trades) * 0.08)
        signal_type = "cluster_buying"
    elif len(sell_trades) >= 3:
        # Mass insider selling — distribution warning
        action = "SELL"
        confidence = min(0.70, 0.40 + len(sell_trades) * 0.07)
        signal_type = "mass_selling"
    elif len(buy_trades) == 1:
        # Single non-exec buy — mild signal
        action = "BUY"
        confidence = 0.50
        signal_type = "single_buy"

    return {
        "action": action,
        "confidence": round(confidence, 4),
        "buy_count": len(buy_trades),
        "sell_count": len(sell_trades),
        "signal_type": signal_type,
    }


async def get_insider_signal(symbol: str, force_refresh: bool = False) -> Dict:
    """
    Fetch SEC Form 4 insider trading signal for a symbol.
    Returns: {'action': BUY|SELL|HOLD, 'confidence': float,
              'buy_count': int, 'sell_count': int, 'signal_type': str, 'cached': bool}
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

    try:
        from core.sec_edgar_api import SECEdgarAPI
        api = SECEdgarAPI()
        trades = await api.get_insider_trades_for_symbol(symbol)
        result = _analyse_trades(trades)
    except Exception as e:
        logger.debug(f"[InsiderTrading] SEC API error for {symbol}: {e}")
        result = {"action": "HOLD", "confidence": 0.0, "buy_count": 0,
                  "sell_count": 0, "signal_type": "error"}

    result["timestamp"] = now.isoformat()
    result["cached"] = False

    _CACHE[cache_key] = result.copy()
    _CACHE_EXPIRY[cache_key] = now + timedelta(minutes=_CACHE_TTL)
    _persist(symbol, result)

    logger.debug(
        f"[InsiderTrading] {symbol}: {result['action']} ({result['confidence']:.0%}) "
        f"type={result['signal_type']} buys={result['buy_count']} sells={result['sell_count']}"
    )
    return result
