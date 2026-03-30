"""
PROMETHEUS Market Calendar Scraper
=====================================
Fetches two critical forward-looking data sources:

1. Earnings Calendar  — which stocks report earnings in the next 7 days
                        (from Finviz free screener + Yahoo Finance)
2. Economic Calendar  — upcoming macro events: FOMC, CPI, NFP, PPI, GDP
                        (from FRED release calendar + Investing.com fallback)

Why this matters:
  - Trading INTO an earnings event without knowing = gambling
  - Big macro events cause regime shifts — knowing they're coming lets
    PROMETHEUS reduce size or flip contrarian

Results cached 6 hours (calendars don't change intraday).
Persisted to prometheus_learning.db for correlation analysis.

Usage:
    from core.market_calendar_scraper import (
        get_earnings_this_week, get_economic_events, is_earnings_risk
    )
    await get_earnings_this_week()     # {symbol: {date, est_eps, ...}}
    await get_economic_events()        # [{name, date, impact, ...}]
    await is_earnings_risk('AAPL')     # True/False — reports within 3 days
"""

import asyncio
import json
import logging
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

LEARNING_DB = Path("prometheus_learning.db")

_EARNINGS_CACHE: Dict = {}
_EARNINGS_EXPIRY: Optional[datetime] = None
_ECON_CACHE: List = []
_ECON_EXPIRY: Optional[datetime] = None
_CACHE_TTL_HOURS = 6


# ─────────────────────────────────────────────────────────────
# Earnings Calendar via Yahoo Finance (free, no key required)
# ─────────────────────────────────────────────────────────────

YAHOO_EARNINGS_URL = "https://finance.yahoo.com/calendar/earnings"

async def _fetch_yahoo_earnings(session) -> Dict[str, Dict]:
    """Scrape Yahoo Finance earnings calendar for the next 7 days."""
    earnings = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
    }
    try:
        async with session.get(YAHOO_EARNINGS_URL, headers=headers, timeout=15) as resp:
            if resp.status != 200:
                logger.debug(f"Yahoo earnings calendar status: {resp.status}")
                return earnings
            html = await resp.text()

            # Extract JSON payload embedded in page
            match = re.search(r'"earningsCalendar":(\[.*?\])', html, re.DOTALL)
            if match:
                try:
                    items = json.loads(match.group(1))
                    for item in items:
                        sym = item.get('ticker', '')
                        if sym:
                            earnings[sym] = {
                                'date': item.get('startdatetime', '')[:10],
                                'company': item.get('companyshortname', ''),
                                'est_eps': item.get('epsestimate'),
                                'timing': item.get('startdatetimetype', ''),  # BMO/AMC
                            }
                except Exception as parse_err:
                    logger.debug(f"Yahoo earnings JSON parse error: {parse_err}")

            # Fallback: look for symbol mentions in table rows
            if not earnings:
                syms = re.findall(r'"symbol":"([A-Z]{1,5})"', html)
                dates = re.findall(r'"reportDate":"(\d{4}-\d{2}-\d{2})"', html)
                for sym, dt in zip(syms, dates):
                    earnings[sym] = {'date': dt, 'company': sym, 'est_eps': None}

    except Exception as e:
        logger.debug(f"Yahoo earnings calendar error: {e}")

    # Also try yfinance as a more reliable fallback
    if not earnings:
        earnings = await _fetch_yfinance_earnings()

    return earnings


async def _fetch_yfinance_earnings() -> Dict[str, Dict]:
    """Use yfinance to get earnings for a basket of major symbols."""
    earnings = {}
    try:
        import yfinance as yf
        watchlist = [
            'AAPL','MSFT','NVDA','GOOGL','AMZN','META','TSLA','JPM','V','UNH',
            'AMD','INTC','COIN','NFLX','DIS','BAC','WMT','COST','HD','CRM',
            'SPY','QQQ','IWM','GLD','SLV','BTC-USD','ETH-USD',
        ]
        for sym in watchlist:
            try:
                ticker = yf.Ticker(sym)
                cal = ticker.calendar
                if cal is not None and not cal.empty:
                    earn_date = cal.columns[0] if hasattr(cal, 'columns') else None
                    if earn_date:
                        earnings[sym] = {
                            'date': str(earn_date.date()) if hasattr(earn_date, 'date') else str(earn_date),
                            'company': sym,
                            'est_eps': None,
                            'timing': 'unknown',
                        }
            except Exception:
                pass
    except ImportError:
        pass
    return earnings


# ─────────────────────────────────────────────────────────────
# Economic Calendar via FRED release schedule
# ─────────────────────────────────────────────────────────────

FRED_RELEASES_URL = "https://api.stlouisfed.org/fred/releases/dates"

# Key release IDs and their market impact level
FRED_KEY_RELEASES = {
    10:  ('CPI',                 'HIGH'),
    18:  ('Industrial Production','MEDIUM'),
    19:  ('PPI',                 'HIGH'),
    21:  ('GDP',                 'HIGH'),
    50:  ('Unemployment Rate',   'HIGH'),
    113: ('NFP',                 'HIGH'),
    118: ('Retail Sales',        'MEDIUM'),
    53:  ('PCE',                 'HIGH'),
    10007: ('FOMC Meeting',      'VERY_HIGH'),
}

async def _fetch_fred_releases(session, fred_api_key: str = '') -> List[Dict]:
    """Fetch upcoming FRED economic release dates."""
    events = []
    if not fred_api_key:
        # Try environment
        import os
        fred_api_key = os.environ.get('FRED_API_KEY', '')
    if not fred_api_key:
        return events

    try:
        today = datetime.now().strftime('%Y-%m-%d')
        next_month = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        url = (
            f"https://api.stlouisfed.org/fred/releases/dates"
            f"?api_key={fred_api_key}&file_type=json"
            f"&realtime_start={today}&realtime_end={next_month}"
            f"&include_release_dates_with_no_data=true"
        )
        async with session.get(url, timeout=10) as resp:
            if resp.status == 200:
                data = await resp.json(content_type=None)
                for item in data.get('release_dates', []):
                    rid = item.get('release_id')
                    if rid in FRED_KEY_RELEASES:
                        name, impact = FRED_KEY_RELEASES[rid]
                        events.append({
                            'name': name,
                            'date': item.get('date', ''),
                            'impact': impact,
                            'source': 'FRED',
                        })
    except Exception as e:
        logger.debug(f"FRED releases error: {e}")
    return events


async def _fetch_hardcoded_fomc_dates() -> List[Dict]:
    """
    Return known FOMC meeting dates for 2026 as fallback when FRED key absent.
    Update this list annually.
    """
    fomc_2026 = [
        '2026-01-28', '2026-03-18', '2026-05-06',
        '2026-06-17', '2026-07-29', '2026-09-16',
        '2026-11-04', '2026-12-16',
    ]
    today = datetime.now().date()
    events = []
    for dt_str in fomc_2026:
        dt = datetime.strptime(dt_str, '%Y-%m-%d').date()
        if dt >= today:
            events.append({
                'name': 'FOMC Meeting',
                'date': dt_str,
                'impact': 'VERY_HIGH',
                'source': 'hardcoded',
            })
    return events


# ─────────────────────────────────────────────────────────────
# Persistence
# ─────────────────────────────────────────────────────────────

def _persist_earnings(earnings: Dict):
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=5)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS earnings_calendar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fetched_at TEXT,
                symbol TEXT,
                earnings_date TEXT,
                company TEXT,
                est_eps REAL,
                timing TEXT
            )
        """)
        fetched = datetime.now().isoformat()
        for sym, info in earnings.items():
            conn.execute(
                "INSERT INTO earnings_calendar "
                "(fetched_at,symbol,earnings_date,company,est_eps,timing) VALUES (?,?,?,?,?,?)",
                (fetched, sym, info.get('date',''), info.get('company',''),
                 info.get('est_eps'), info.get('timing',''))
            )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"earnings persist error: {e}")


def _persist_econ_events(events: List):
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=5)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS economic_calendar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fetched_at TEXT,
                event_name TEXT,
                event_date TEXT,
                impact TEXT,
                source TEXT
            )
        """)
        fetched = datetime.now().isoformat()
        for ev in events:
            conn.execute(
                "INSERT INTO economic_calendar "
                "(fetched_at,event_name,event_date,impact,source) VALUES (?,?,?,?,?)",
                (fetched, ev.get('name',''), ev.get('date',''),
                 ev.get('impact',''), ev.get('source',''))
            )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"econ calendar persist error: {e}")


# ─────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────

async def get_earnings_this_week(force_refresh: bool = False) -> Dict[str, Dict]:
    """Return dict of {symbol → earnings_info} for upcoming earnings."""
    global _EARNINGS_CACHE, _EARNINGS_EXPIRY
    now = datetime.now()
    if not force_refresh and _EARNINGS_EXPIRY and now < _EARNINGS_EXPIRY and _EARNINGS_CACHE:
        return _EARNINGS_CACHE

    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            earnings = await _fetch_yahoo_earnings(session)
    except Exception as e:
        logger.warning(f"get_earnings_this_week error: {e}")
        earnings = {}

    _EARNINGS_CACHE = earnings
    _EARNINGS_EXPIRY = now + timedelta(hours=_CACHE_TTL_HOURS)
    if earnings:
        _persist_earnings(earnings)
        logger.info(f"[Calendar] Fetched {len(earnings)} upcoming earnings reports")
    return earnings


async def get_economic_events(force_refresh: bool = False) -> List[Dict]:
    """Return list of upcoming high-impact economic events."""
    global _ECON_CACHE, _ECON_EXPIRY
    now = datetime.now()
    if not force_refresh and _ECON_EXPIRY and now < _ECON_EXPIRY and _ECON_CACHE:
        return _ECON_CACHE

    events: List[Dict] = []
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            fred_events = await _fetch_fred_releases(session)
            events.extend(fred_events)
    except Exception as e:
        logger.debug(f"FRED calendar error: {e}")

    # Always add FOMC dates (doesn't need API key)
    fomc = await _fetch_hardcoded_fomc_dates()
    existing_dates = {e['date'] for e in events if e.get('name') == 'FOMC Meeting'}
    for ev in fomc:
        if ev['date'] not in existing_dates:
            events.append(ev)

    # Sort by date
    events.sort(key=lambda x: x.get('date', ''))

    _ECON_CACHE = events
    _ECON_EXPIRY = now + timedelta(hours=_CACHE_TTL_HOURS)
    if events:
        _persist_econ_events(events)
        logger.info(f"[Calendar] Fetched {len(events)} upcoming economic events")
    return events


async def is_earnings_risk(symbol: str, days_ahead: int = 3) -> bool:
    """
    Returns True if symbol reports earnings within `days_ahead` calendar days.
    Use to reduce position size or skip trading before earnings.
    """
    try:
        earnings = await get_earnings_this_week()
        if symbol not in earnings:
            return False
        earn_date_str = earnings[symbol].get('date', '')
        if not earn_date_str:
            return False
        earn_date = datetime.strptime(earn_date_str[:10], '%Y-%m-%d').date()
        today = datetime.now().date()
        return 0 <= (earn_date - today).days <= days_ahead
    except Exception:
        return False


async def days_to_next_fomc() -> Optional[int]:
    """Return number of days until next FOMC meeting, or None if unknown."""
    try:
        events = await get_economic_events()
        today = datetime.now().date()
        for ev in events:
            if 'FOMC' in ev.get('name', ''):
                dt = datetime.strptime(ev['date'][:10], '%Y-%m-%d').date()
                if dt >= today:
                    return (dt - today).days
    except Exception:
        pass
    return None
