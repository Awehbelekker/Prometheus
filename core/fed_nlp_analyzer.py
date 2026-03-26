"""
Fed / Central Bank NLP Analyzer
================================
Parses FOMC statements, meeting minutes, and Fed speeches through Ollama
to detect policy shifts, hawkish/dovish tone, and rate expectations.

Uses llama3.1:8b-trading (or any available Ollama model) for inference.
No external API keys needed — runs entirely on local Ollama.

Data sources:
  - Federal Reserve RSS feeds (public, no auth)
  - FRED API (optional, for rate data)
  - Fed calendar (embedded schedule)
"""

import logging
import asyncio
import aiohttp
import json
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

# FOMC meeting schedule 2026 (publicly known)
FOMC_DATES_2026 = [
    "2026-01-27", "2026-01-28",  # Jan
    "2026-03-17", "2026-03-18",  # Mar
    "2026-05-05", "2026-05-06",  # May
    "2026-06-16", "2026-06-17",  # Jun
    "2026-07-28", "2026-07-29",  # Jul
    "2026-09-15", "2026-09-16",  # Sep
    "2026-10-27", "2026-10-28",  # Oct
    "2026-12-15", "2026-12-16",  # Dec
]

FED_RSS_FEEDS = {
    "press_releases": "https://www.federalreserve.gov/feeds/press_all.xml",
    "speeches": "https://www.federalreserve.gov/feeds/speeches.xml",
    "testimony": "https://www.federalreserve.gov/feeds/testimony.xml",
}

# Key phrases that signal policy direction
HAWKISH_KEYWORDS = [
    "tightening", "restrictive", "inflation remains elevated",
    "further increases", "above target", "labor market remains tight",
    "reduce the size of", "quantitative tightening", "price stability",
    "upside risks to inflation", "insufficiently restrictive",
    "data dependent", "not yet convinced",
]

DOVISH_KEYWORDS = [
    "accommodative", "easing", "rate cuts", "below target",
    "downside risks", "slowing economy", "labor market softening",
    "growth concerns", "financial conditions have tightened sufficiently",
    "inflation has made progress", "disinflation", "neutral rate",
    "gradual normalization", "appropriate to reduce",
]


@dataclass
class FedAnalysis:
    """Result of analyzing a Fed communication"""
    source: str                     # 'fomc_statement', 'speech', 'minutes'
    title: str
    date: str
    tone: str                       # 'hawkish', 'dovish', 'neutral'
    tone_score: float               # -1.0 (very dovish) to +1.0 (very hawkish)
    confidence: float               # 0-1
    key_phrases: List[str]
    rate_direction: str             # 'higher', 'lower', 'unchanged'
    summary: str
    policy_shifts: List[str]        # detected changes from previous stance
    market_implications: Dict[str, str]  # asset class -> expected impact
    raw_text_snippet: str           # first 500 chars of source


@dataclass
class FedIntelligence:
    """Aggregated Fed intelligence for trading decisions"""
    timestamp: str
    overall_tone: str               # hawkish / dovish / neutral
    overall_score: float            # -1 to +1
    rate_expectation: str           # higher / lower / unchanged
    next_fomc_date: str
    days_to_fomc: int
    recent_analyses: List[FedAnalysis]
    trading_signal: str             # 'risk_on', 'risk_off', 'neutral'
    signal_confidence: float
    recommended_positioning: Dict[str, str]


class FedNLPAnalyzer:
    """
    Analyzes Federal Reserve communications using local Ollama LLM.
    Detects hawkish/dovish shifts and generates trading signals.
    """

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "llama3.1:8b-trading",
        cache_dir: str = "fed_analysis_cache",
    ):
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.analyses: List[FedAnalysis] = []
        self._session: Optional[aiohttp.ClientSession] = None
        logger.info(f"Fed NLP Analyzer initialized (model={model})")

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60)
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    # ------------------------------------------------------------------
    # Data Fetching
    # ------------------------------------------------------------------

    async def fetch_fed_rss(self, feed_key: str = "press_releases", max_items: int = 5) -> List[Dict[str, str]]:
        """Fetch recent items from Fed RSS feeds."""
        url = FED_RSS_FEEDS.get(feed_key)
        if not url:
            return []
        try:
            session = await self._get_session()
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.warning(f"Fed RSS {feed_key} returned {resp.status}")
                    return []
                text = await resp.text()
            root = ET.fromstring(text)
            items = []
            # RSS 2.0 structure
            for item in root.findall(".//item")[:max_items]:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                pub_date = item.findtext("pubDate", "")
                description = item.findtext("description", "")
                items.append({
                    "title": title,
                    "link": link,
                    "date": pub_date,
                    "description": description,
                    "source": feed_key,
                })
            logger.info(f"Fetched {len(items)} items from Fed {feed_key}")
            return items
        except Exception as e:
            logger.warning(f"Failed to fetch Fed RSS {feed_key}: {e}")
            return []

    async def fetch_page_text(self, url: str, max_chars: int = 4000) -> str:
        """Fetch text content from a Fed webpage."""
        try:
            session = await self._get_session()
            async with session.get(url) as resp:
                if resp.status != 200:
                    return ""
                html = await resp.text()
            # Simple HTML stripping (no BeautifulSoup dependency)
            text = re.sub(r"<[^>]+>", " ", html)
            text = re.sub(r"\s+", " ", text).strip()
            return text[:max_chars]
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return ""

    # ------------------------------------------------------------------
    # NLP Analysis via Ollama
    # ------------------------------------------------------------------

    async def _query_ollama(self, prompt: str) -> str:
        """Send prompt to Ollama and return the response text."""
        try:
            import psutil
            if psutil.cpu_percent(interval=0) > 85:
                logger.debug("CPU overloaded, skipping Fed NLP Ollama call")
                return ""
            session = await self._get_session()
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": 400},
            }
            async with session.post(f"{self.ollama_url}/api/generate", json=payload) as resp:
                if resp.status != 200:
                    # Try fallback model
                    payload["model"] = "llama3.1:latest"
                    async with session.post(f"{self.ollama_url}/api/generate", json=payload) as resp2:
                        if resp2.status != 200:
                            return ""
                        data = await resp2.json()
                        return data.get("response", "")
                data = await resp.json()
                return data.get("response", "")
        except Exception as e:
            logger.warning(f"Ollama query failed: {e}")
            return ""

    async def analyze_text(self, text: str, title: str = "", source: str = "unknown", date: str = "") -> FedAnalysis:
        """Analyze a Fed communication text using Ollama LLM."""

        # Quick keyword pre-scan (always works even without Ollama)
        text_lower = text.lower()
        hawk_hits = [kw for kw in HAWKISH_KEYWORDS if kw in text_lower]
        dove_hits = [kw for kw in DOVISH_KEYWORDS if kw in text_lower]
        keyword_score = (len(hawk_hits) - len(dove_hits)) / max(len(hawk_hits) + len(dove_hits), 1)

        # LLM analysis
        prompt = f"""You are an expert Federal Reserve policy analyst. Analyze this Fed communication and respond in JSON only.

TEXT: {text[:2000]}

Respond with ONLY this JSON (no other text):
{{
  "tone": "hawkish" or "dovish" or "neutral",
  "tone_score": float from -1.0 (very dovish) to 1.0 (very hawkish),
  "rate_direction": "higher" or "lower" or "unchanged",
  "key_phrases": ["phrase1", "phrase2", "phrase3"],
  "policy_shifts": ["shift1 if any"],
  "summary": "One sentence summary of policy stance",
  "market_impact": {{
    "equities": "bullish" or "bearish" or "neutral",
    "bonds": "bullish" or "bearish" or "neutral",
    "dollar": "bullish" or "bearish" or "neutral"
  }}
}}"""

        llm_response = await self._query_ollama(prompt)

        # Parse LLM JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r"\{[\s\S]*\}", llm_response)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found")

            tone = parsed.get("tone", "neutral")
            tone_score = float(parsed.get("tone_score", 0))
            rate_direction = parsed.get("rate_direction", "unchanged")
            key_phrases = parsed.get("key_phrases", hawk_hits + dove_hits)
            policy_shifts = parsed.get("policy_shifts", [])
            summary = parsed.get("summary", "Analysis unavailable")
            market_impact = parsed.get("market_impact", {})
            confidence = 0.8  # LLM-based
        except (json.JSONDecodeError, ValueError):
            # Fallback to keyword-only analysis
            tone = "hawkish" if keyword_score > 0.2 else "dovish" if keyword_score < -0.2 else "neutral"
            tone_score = keyword_score
            rate_direction = "higher" if keyword_score > 0.3 else "lower" if keyword_score < -0.3 else "unchanged"
            key_phrases = hawk_hits + dove_hits
            policy_shifts = []
            summary = f"Keyword analysis: {len(hawk_hits)} hawkish, {len(dove_hits)} dovish signals"
            market_impact = {}
            confidence = 0.4  # keyword-only

        analysis = FedAnalysis(
            source=source,
            title=title,
            date=date,
            tone=tone,
            tone_score=max(-1.0, min(1.0, tone_score)),
            confidence=confidence,
            key_phrases=key_phrases[:10],
            rate_direction=rate_direction,
            summary=summary,
            policy_shifts=policy_shifts,
            market_implications=market_impact,
            raw_text_snippet=text[:500],
        )

        self.analyses.append(analysis)
        # Keep last 50
        if len(self.analyses) > 50:
            self.analyses = self.analyses[-50:]

        logger.info(f"Fed analysis: {title[:60]} -> {tone} (score={tone_score:.2f}, conf={confidence:.0%})")
        return analysis

    # ------------------------------------------------------------------
    # High-Level Intelligence
    # ------------------------------------------------------------------

    async def get_fed_intelligence(self) -> FedIntelligence:
        """
        Full pipeline: fetch latest Fed communications, analyze them,
        and produce a trading-actionable intelligence summary.
        """
        # 1. Fetch from all RSS feeds
        all_items = []
        for feed_key in FED_RSS_FEEDS:
            items = await self.fetch_fed_rss(feed_key, max_items=3)
            all_items.extend(items)

        # 2. Analyze each item
        new_analyses = []
        for item in all_items[:6]:  # Limit to prevent Ollama overload
            # Fetch full text if we have a link
            text = item.get("description", "")
            if item.get("link") and len(text) < 200:
                full_text = await self.fetch_page_text(item["link"])
                if full_text:
                    text = full_text

            if len(text) < 50:
                continue

            analysis = await self.analyze_text(
                text=text,
                title=item.get("title", "Unknown"),
                source=item.get("source", "unknown"),
                date=item.get("date", ""),
            )
            new_analyses.append(analysis)

        # 3. Aggregate
        all_analyses = new_analyses if new_analyses else self.analyses[-5:]
        if not all_analyses:
            return self._empty_intelligence()

        avg_score = sum(a.tone_score for a in all_analyses) / len(all_analyses)
        avg_confidence = sum(a.confidence for a in all_analyses) / len(all_analyses)

        overall_tone = "hawkish" if avg_score > 0.15 else "dovish" if avg_score < -0.15 else "neutral"

        # Rate expectation from most recent analysis
        rate_exp = all_analyses[-1].rate_direction if all_analyses else "unchanged"

        # Next FOMC date
        today = datetime.utcnow().strftime("%Y-%m-%d")
        next_fomc = "unknown"
        days_to_fomc = 999
        for d in FOMC_DATES_2026:
            if d >= today:
                next_fomc = d
                days_to_fomc = (datetime.strptime(d, "%Y-%m-%d") - datetime.utcnow()).days
                break

        # Trading signal
        if avg_score > 0.3 and avg_confidence > 0.5:
            trading_signal = "risk_off"  # Hawkish = tightening = risk off
            positioning = {"equities": "reduce", "bonds": "short_duration", "cash": "increase"}
        elif avg_score < -0.3 and avg_confidence > 0.5:
            trading_signal = "risk_on"  # Dovish = easing = risk on
            positioning = {"equities": "increase", "bonds": "long_duration", "cash": "deploy"}
        else:
            trading_signal = "neutral"
            positioning = {"equities": "hold", "bonds": "neutral", "cash": "maintain"}

        intel = FedIntelligence(
            timestamp=datetime.utcnow().isoformat(),
            overall_tone=overall_tone,
            overall_score=round(avg_score, 3),
            rate_expectation=rate_exp,
            next_fomc_date=next_fomc,
            days_to_fomc=days_to_fomc,
            recent_analyses=all_analyses[-5:],
            trading_signal=trading_signal,
            signal_confidence=round(avg_confidence, 3),
            recommended_positioning=positioning,
        )

        # Cache to disk
        try:
            cache_path = self.cache_dir / f"fed_intel_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.json"
            with open(cache_path, "w") as f:
                json.dump(asdict(intel), f, indent=2, default=str)
        except Exception:
            pass

        logger.info(
            f"Fed Intelligence: {overall_tone} (score={avg_score:.2f}) "
            f"| signal={trading_signal} | next FOMC in {days_to_fomc}d"
        )
        return intel

    def _empty_intelligence(self) -> FedIntelligence:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        next_fomc = "unknown"
        days_to_fomc = 999
        for d in FOMC_DATES_2026:
            if d >= today:
                next_fomc = d
                days_to_fomc = (datetime.strptime(d, "%Y-%m-%d") - datetime.utcnow()).days
                break
        return FedIntelligence(
            timestamp=datetime.utcnow().isoformat(),
            overall_tone="neutral",
            overall_score=0.0,
            rate_expectation="unchanged",
            next_fomc_date=next_fomc,
            days_to_fomc=days_to_fomc,
            recent_analyses=[],
            trading_signal="neutral",
            signal_confidence=0.0,
            recommended_positioning={"equities": "hold", "bonds": "neutral", "cash": "maintain"},
        )

    # ------------------------------------------------------------------
    # Query interface for trading signals
    # ------------------------------------------------------------------

    def get_latest_signal(self) -> Dict[str, Any]:
        """Return the latest Fed signal for use in trading decisions."""
        if not self.analyses:
            return {"tone": "neutral", "score": 0.0, "confidence": 0.0, "signal": "neutral"}
        latest = self.analyses[-1]
        return {
            "tone": latest.tone,
            "score": latest.tone_score,
            "confidence": latest.confidence,
            "rate_direction": latest.rate_direction,
            "signal": "risk_off" if latest.tone_score > 0.3 else "risk_on" if latest.tone_score < -0.3 else "neutral",
            "source": latest.source,
            "date": latest.date,
        }
