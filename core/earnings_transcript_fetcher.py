"""
Earnings Transcript Fetcher
Fetches SEC 8-K earnings filings (item 2.02) for a symbol.
Saves plain text to knowledge_base/{symbol}/ for RAG ingestion.
Cache TTL: 60 minutes. No voting — pure knowledge pipeline.
"""
import asyncio
import logging
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import aiohttp

logger = logging.getLogger(__name__)

LEARNING_DB = Path(__file__).parent.parent / "prometheus_learning.db"
KNOWLEDGE_BASE = Path(__file__).parent.parent / "knowledge_base"
_CACHE_TTL = 60  # minutes
_CACHE: dict = {}
_CACHE_EXPIRY: dict = {}

SEC_SEARCH_URL = (
    "https://efts.sec.gov/LATEST/search-index?q=%22{symbol}%22+%228-K%22"
    "&forms=8-K&dateRange=custom&startdt={start}&enddt={end}"
)
SEC_FILING_URL = "https://www.sec.gov{path}"
REQUEST_TIMEOUT = 15


def _ensure_table():
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=5)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS earnings_transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fetched_at TEXT,
                symbol TEXT,
                filing_date TEXT,
                accession_number TEXT,
                local_path TEXT,
                item_type TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"[EarningsTranscript] Table init: {e}")


def _persist(symbol: str, filing_date: str, accession: str, local_path: str, item_type: str):
    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=5)
        conn.execute(
            """INSERT INTO earnings_transcripts
               (fetched_at, symbol, filing_date, accession_number, local_path, item_type)
               VALUES (?,?,?,?,?,?)""",
            (datetime.now().isoformat(), symbol, filing_date, accession, str(local_path), item_type),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug(f"[EarningsTranscript] Persist error: {e}")


def _strip_html(html: str) -> str:
    """Basic HTML stripping — removes tags, scripts, styles."""
    text = re.sub(r"<(script|style)[^>]*>.*?</(script|style)>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"\s{3,}", "\n\n", text)
    return text.strip()


async def fetch_earnings_transcripts(
    symbol: str, max_filings: int = 3, force_refresh: bool = False
) -> List[Path]:
    """
    Fetch SEC 8-K earnings filings for a symbol and save as .txt to knowledge_base/.
    Returns list of saved file paths.
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
        return _CACHE.get(cache_key, [])

    # Ensure output directory exists
    out_dir = KNOWLEDGE_BASE / symbol.upper().replace("/", "_")
    out_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: List[Path] = []
    start_date = (now - timedelta(days=365)).strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")

    try:
        async with aiohttp.ClientSession(
            headers={"User-Agent": "PROMETHEUS-Research research@prometheus.local"}
        ) as session:
            # Search for recent 8-K filings
            search_url = SEC_SEARCH_URL.format(
                symbol=symbol.upper(), start=start_date, end=end_date
            )
            async with session.get(
                search_url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            ) as resp:
                if resp.status != 200:
                    logger.debug(f"[EarningsTranscript] SEC search HTTP {resp.status} for {symbol}")
                    return []
                data = await resp.json()

            hits = data.get("hits", {}).get("hits", [])[:max_filings]
            if not hits:
                logger.debug(f"[EarningsTranscript] No 8-K filings found for {symbol}")
                return []

            for hit in hits:
                source = hit.get("_source", {})
                accession = source.get("accession_no", "unknown")
                filing_date = source.get("file_date", "unknown")
                file_path = source.get("file_path", "")

                if not file_path:
                    continue

                # Fetch the filing document
                filing_url = SEC_FILING_URL.format(path=file_path)
                try:
                    async with session.get(
                        filing_url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
                    ) as doc_resp:
                        if doc_resp.status != 200:
                            continue
                        raw = await doc_resp.text(errors="replace")
                except Exception as e:
                    logger.debug(f"[EarningsTranscript] Fetch error {filing_url}: {e}")
                    continue

                # Identify if this contains item 2.02 (earnings results)
                item_type = "unknown"
                lower_raw = raw.lower()
                if "2.02" in lower_raw or "results of operations" in lower_raw:
                    item_type = "2.02"
                elif "7.01" in lower_raw or "regulation fd" in lower_raw:
                    item_type = "7.01"

                # Strip HTML and save
                clean_text = _strip_html(raw)
                if len(clean_text) < 200:
                    continue

                filename = f"{symbol.upper()}_{filing_date}_{accession[:10]}.txt"
                out_path = out_dir / filename

                out_path.write_text(clean_text[:50000], encoding="utf-8")  # cap at 50KB
                saved_paths.append(out_path)
                _persist(symbol, filing_date, accession, str(out_path), item_type)
                logger.info(f"[EarningsTranscript] Saved: {out_path.name} ({item_type})")

    except asyncio.TimeoutError:
        logger.debug(f"[EarningsTranscript] Timeout for {symbol}")
    except Exception as e:
        logger.debug(f"[EarningsTranscript] Error for {symbol}: {e}")

    _CACHE[cache_key] = saved_paths
    _CACHE_EXPIRY[cache_key] = now + timedelta(minutes=_CACHE_TTL)
    return saved_paths
