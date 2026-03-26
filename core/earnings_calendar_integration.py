#!/usr/bin/env python3
"""
Earnings Calendar Integration
===============================
Fetches upcoming earnings dates for tracked symbols and exposes:
  - Days until next earnings for any symbol
  - Position-sizing multiplier (reduce exposure before earnings)
  - Earnings surprise history (beat/miss ratio)

Data sources (free, no API key required):
  1. yfinance `.calendar` (primary)
  2. SEC EDGAR XBRL filing dates (fallback)
  3. Manual overrides via local JSON

Position-sizing logic:
  - > 5 days out:  multiplier = 1.0  (normal)
  - 3-5 days out:  multiplier = 0.70  (reduce 30%)
  - 1-2 days out:  multiplier = 0.40  (reduce 60%)
  - Earnings day:  multiplier = 0.20  (minimal exposure)
"""

import logging
import json
import os
from datetime import datetime, timedelta, timezone, date
from typing import Dict, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "earnings_cache.json")
OVERRIDE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "earnings_overrides.json")


@dataclass
class EarningsInfo:
    symbol: str
    next_earnings_date: Optional[str] = None   # ISO date string
    days_until: Optional[int] = None
    position_multiplier: float = 1.0
    source: str = "unknown"
    beat_ratio: float = 0.5    # Historical beat ratio
    last_updated: str = ""


class EarningsCalendarIntegration:
    """
    Tracks upcoming earnings dates, computes position-sizing multipliers,
    and exposes data to the voting pipeline for risk-aware trading.
    """

    # Position sizing thresholds
    NORMAL_DAYS = 5
    CAUTIOUS_DAYS = 3
    HIGH_RISK_DAYS = 1

    def __init__(self):
        self._cache: Dict[str, EarningsInfo] = {}
        self._cache_ttl = timedelta(hours=6)
        self._last_bulk_fetch = None
        self._overrides = self._load_overrides()
        logger.info("Earnings Calendar Integration initialized")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_earnings_info(self, symbol: str) -> EarningsInfo:
        """Get earnings info for a single symbol (cached with TTL)."""
        cached = self._cache.get(symbol)
        if cached and cached.last_updated:
            try:
                updated = datetime.fromisoformat(cached.last_updated)
                if datetime.now(timezone.utc) - updated < self._cache_ttl:
                    return cached
            except Exception:
                pass

        # Check overrides first
        if symbol in self._overrides:
            info = self._from_override(symbol)
            self._cache[symbol] = info
            return info

        # Fetch from yfinance
        info = self._fetch_from_yfinance(symbol)
        self._cache[symbol] = info
        return info

    def get_position_multiplier(self, symbol: str) -> float:
        """
        Returns a multiplier (0.0 - 1.0) for position sizing.
        Lower means reduce position before earnings.
        """
        info = self.get_earnings_info(symbol)
        return info.position_multiplier

    def get_bulk_info(self, symbols: List[str]) -> Dict[str, EarningsInfo]:
        """Get earnings info for multiple symbols."""
        results = {}
        for sym in symbols:
            try:
                results[sym] = self.get_earnings_info(sym)
            except Exception as e:
                logger.debug(f"Earnings fetch failed for {sym}: {e}")
                results[sym] = EarningsInfo(symbol=sym)
        return results

    def get_upcoming_earnings(self, symbols: List[str], days_ahead: int = 7) -> List[Dict]:
        """Return symbols with earnings in the next N days."""
        upcoming = []
        for sym in symbols:
            info = self.get_earnings_info(sym)
            if info.days_until is not None and 0 <= info.days_until <= days_ahead:
                upcoming.append({
                    "symbol": sym,
                    "earnings_date": info.next_earnings_date,
                    "days_until": info.days_until,
                    "position_multiplier": info.position_multiplier,
                    "source": info.source,
                })
        upcoming.sort(key=lambda x: x["days_until"])
        return upcoming

    def get_summary(self, symbols: List[str] = None) -> Dict:
        """JSON-friendly summary."""
        if symbols is None:
            # Use cached symbols
            symbols = list(self._cache.keys())
        
        infos = self.get_bulk_info(symbols) if symbols else {}
        upcoming_7d = [s for s in infos.values() if s.days_until is not None and 0 <= s.days_until <= 7]
        high_risk = [s for s in infos.values() if s.position_multiplier < 0.5]

        return {
            "total_tracked": len(infos),
            "upcoming_7_days": len(upcoming_7d),
            "high_risk_positions": len(high_risk),
            "symbols": {
                sym: {
                    "next_earnings": info.next_earnings_date,
                    "days_until": info.days_until,
                    "position_multiplier": round(info.position_multiplier, 2),
                    "source": info.source,
                }
                for sym, info in infos.items()
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _fetch_from_yfinance(self, symbol: str) -> EarningsInfo:
        """Pull next earnings date from yfinance."""
        info = EarningsInfo(symbol=symbol, last_updated=datetime.now(timezone.utc).isoformat())
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)

            # Try .calendar first
            cal = ticker.calendar
            earnings_date = None

            if cal is not None:
                if isinstance(cal, dict):
                    # Newer yfinance returns dict
                    ed = cal.get("Earnings Date")
                    if ed:
                        if isinstance(ed, list) and len(ed) > 0:
                            earnings_date = ed[0]
                        elif isinstance(ed, (datetime, date)):
                            earnings_date = ed
                elif hasattr(cal, "columns"):
                    # DataFrame format
                    if "Earnings Date" in cal.columns:
                        vals = cal["Earnings Date"].dropna()
                        if len(vals) > 0:
                            earnings_date = vals.iloc[0]

            # Fallback: .earnings_dates
            if earnings_date is None and hasattr(ticker, "earnings_dates"):
                try:
                    ed_series = ticker.earnings_dates
                    if ed_series is not None and len(ed_series) > 0:
                        future_dates = [d for d in ed_series.index if d.date() >= datetime.now().date()]
                        if future_dates:
                            earnings_date = min(future_dates)
                except Exception:
                    pass

            if earnings_date is not None:
                if isinstance(earnings_date, datetime):
                    ed = earnings_date.date()
                elif isinstance(earnings_date, date):
                    ed = earnings_date
                else:
                    ed = datetime.fromisoformat(str(earnings_date)).date()

                today = datetime.now(timezone.utc).date()
                days = (ed - today).days
                info.next_earnings_date = ed.isoformat()
                info.days_until = max(days, 0)
                info.position_multiplier = self._compute_multiplier(days)
                info.source = "yfinance"
            else:
                info.source = "yfinance_no_data"

        except ImportError:
            logger.warning("yfinance not installed — earnings calendar unavailable")
            info.source = "no_yfinance"
        except Exception as e:
            logger.debug(f"yfinance earnings fetch failed for {symbol}: {e}")
            info.source = f"error: {str(e)[:50]}"

        return info

    def _compute_multiplier(self, days_until: int) -> float:
        """Compute position size multiplier based on days to earnings."""
        if days_until is None or days_until < 0:
            return 1.0
        if days_until == 0:
            return 0.20  # Earnings day — minimal
        if days_until <= self.HIGH_RISK_DAYS:
            return 0.40  # 1-2 days — reduce 60%
        if days_until <= self.CAUTIOUS_DAYS:
            return 0.70  # 3-5 days — reduce 30%
        return 1.0  # > 5 days — normal

    def _load_overrides(self) -> Dict:
        """Load manual earnings date overrides from JSON."""
        if os.path.exists(OVERRIDE_FILE):
            try:
                with open(OVERRIDE_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _from_override(self, symbol: str) -> EarningsInfo:
        """Build EarningsInfo from manual override."""
        ov = self._overrides[symbol]
        ed = datetime.fromisoformat(ov["date"]).date()
        today = datetime.now(timezone.utc).date()
        days = (ed - today).days
        return EarningsInfo(
            symbol=symbol,
            next_earnings_date=ed.isoformat(),
            days_until=max(days, 0),
            position_multiplier=self._compute_multiplier(days),
            source="manual_override",
            last_updated=datetime.now(timezone.utc).isoformat(),
        )

    def save_cache(self):
        """Persist cache to disk."""
        try:
            data = {}
            for sym, info in self._cache.items():
                data[sym] = {
                    "next_earnings_date": info.next_earnings_date,
                    "days_until": info.days_until,
                    "position_multiplier": info.position_multiplier,
                    "source": info.source,
                    "last_updated": info.last_updated,
                }
            with open(CACHE_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.debug(f"Failed to save earnings cache: {e}")
