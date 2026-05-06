#!/usr/bin/env python3
"""
================================================================================
PROMETHEUS KNOWLEDGE AUTO-DISCOVERY & AUTONOMOUS INGESTION
================================================================================

Feeds everything available into ChromaDB immediately, then pulls new research
autonomously on a weekly schedule.

IMMEDIATE FEED (no internet required):
  - Compiled arXiv insights (831 papers already parsed)
  - PROMETHEUS own trade history as episodic memory
  - Learned pattern files from all learning cycles
  - ai_knowledge_training_data.json
  - All PDFs in knowledge_base/ (28 papers + books; dedup is chunk-level)

AUTONOMOUS WEEKLY PULL (internet, all free / no API key):
  - arXiv RSS  — q-fin, cs.LG, cs.AI new papers
  - AQR Research — free institutional papers
  - FRED — economic calendar and release notes
  - SEC EDGAR — earnings summaries for held symbols

USAGE:
  python prometheus_knowledge_autodiscovery.py          # feed now + pull now
  python prometheus_knowledge_autodiscovery.py --now    # feed local only (fast)
  python prometheus_knowledge_autodiscovery.py --daemon # run weekly in background
================================================================================
"""

import os, sys, json, time, sqlite3, logging, argparse, hashlib, threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [KNOWLEDGE] %(message)s',
    handlers=[
        logging.FileHandler('knowledge_autodiscovery.log'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

KNOWLEDGE_DIR  = Path('knowledge_base')
VECTORS_DIR    = Path('knowledge_vectors')
LEARNING_DB    = Path('prometheus_learning.db')
LAST_PULL_FILE = Path('knowledge_last_pull.json')

# Symbols PROMETHEUS actively trades — populate their dirs
TRACKED_SYMBOLS = ['AAPL', 'NVDA', 'TSLA', 'SPY', 'AMD', 'GOOGL', 'MSFT', 'QQQ',
                   'AMZN', 'META', 'BTC/USD', 'ETH/USD']

# arXiv categories for autonomous pull
ARXIV_CATS = ['q-fin.TR', 'q-fin.PM', 'q-fin.ST', 'cs.LG', 'cs.AI', 'stat.ML']


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline bootstrap
# ─────────────────────────────────────────────────────────────────────────────

def get_pipeline():
    """Return an initialised KnowledgeIngestionPipeline."""
    from knowledge_ingestion_pipeline import KnowledgeIngestionPipeline
    return KnowledgeIngestionPipeline(
        knowledge_dir=str(KNOWLEDGE_DIR),
        vector_db_path=str(VECTORS_DIR)
    )


# ─────────────────────────────────────────────────────────────────────────────
# FEED 1 — arXiv compiled insights (831 papers, zero network calls)
# ─────────────────────────────────────────────────────────────────────────────

def feed_arxiv_compiled(pipeline) -> int:
    """Ingest the pre-compiled arXiv research knowledge module."""
    log.info("FEED 1/5 — arXiv compiled insights (831 papers)...")
    try:
        from arxiv_research_knowledge import ARXIV_RESEARCH_KNOWLEDGE as ARK
    except ImportError:
        log.warning("arxiv_research_knowledge.py not found — skipping")
        return 0

    ingested = 0
    meta = ARK.get('metadata', {})
    base_meta = {
        'source': 'arxiv_compiled',
        'papers_analyzed': meta.get('total_papers_analyzed', 831),
        'compiled_date': meta.get('date_compiled', '2026-01'),
    }

    # Ingest each top-level section as a separate document
    for section_key, section_data in ARK.items():
        if section_key == 'metadata' or not isinstance(section_data, dict):
            continue
        title = f"arXiv Research: {section_key.replace('_', ' ').title()}"
        content = f"Section: {title}\n\nSource: arXiv ({meta.get('total_papers_analyzed', 831)} papers)\n\n"

        for technique, details in section_data.items():
            content += f"\n### {technique.replace('_', ' ').title()}\n"
            if isinstance(details, dict):
                for k, v in details.items():
                    content += f"  {k}: {v}\n"
            elif isinstance(details, list):
                for item in details:
                    content += f"  - {item}\n"
            else:
                content += f"  {details}\n"

        doc_id = pipeline.ingest_raw_text(
            content=content,
            title=title,
            source_type='paper',
            metadata={**base_meta, 'section': section_key}
        )
        if doc_id:
            ingested += 1

    log.info(f"  [OK] Ingested {ingested} arXiv sections")
    return ingested


# ─────────────────────────────────────────────────────────────────────────────
# FEED 2 — PROMETHEUS own trade history (episodic memory — most unique dataset)
# ─────────────────────────────────────────────────────────────────────────────

def feed_own_trade_history(pipeline) -> int:
    """Convert live trade outcomes into episodic knowledge chunks."""
    log.info("FEED 2/5 — Own trade history (episodic memory)...")
    if not LEARNING_DB.exists():
        log.warning(f"  {LEARNING_DB} not found — skipping")
        return 0

    try:
        conn = sqlite3.connect(str(LEARNING_DB), timeout=30)
        conn.row_factory = sqlite3.Row

        # Pull closed trades with full context
        rows = conn.execute("""
            SELECT ai_system, action as signal_action, symbol, entry_price,
                   eventual_pnl as pnl, was_correct as win, confidence,
                   'unknown' as regime, timestamp
            FROM ai_attribution
            WHERE outcome_recorded = 1
            ORDER BY timestamp DESC
            LIMIT 5000
        """).fetchall()
        conn.close()
    except Exception as e:
        log.warning(f"  Could not query trade history: {e}")
        return 0

    if not rows:
        log.warning("  No closed trade rows found — skipping")
        return 0

    # Group into batches of 50 trades per knowledge chunk
    batch_size = 50
    ingested = 0
    for batch_start in range(0, len(rows), batch_size):
        batch = rows[batch_start:batch_start + batch_size]
        wins = [r for r in batch if r['win']]
        losses = [r for r in batch if not r['win']]

        content = f"PROMETHEUS Episodic Trade Memory — Batch {batch_start // batch_size + 1}\n"
        content += f"Period: {batch[-1]['timestamp'][:10]} to {batch[0]['timestamp'][:10]}\n"
        content += f"Trades: {len(batch)} | Wins: {len(wins)} | Losses: {len(losses)}\n"
        content += f"Win Rate: {len(wins)/len(batch):.1%}\n\n"

        content += "=== WINNING PATTERNS ===\n"
        for r in wins[:15]:
            pnl_str = f"+${r['pnl']:.2f}" if r['pnl'] else "n/a"
            content += (f"WIN | {r['symbol']} | {r['signal_action']} | "
                        f"AI={r['ai_system']} | regime={r['regime']} | "
                        f"conf={r['confidence']:.2f} | pnl={pnl_str}\n")

        content += "\n=== LOSING PATTERNS ===\n"
        for r in losses[:10]:
            pnl_str = f"-${abs(r['pnl']):.2f}" if r['pnl'] else "n/a"
            content += (f"LOSS | {r['symbol']} | {r['signal_action']} | "
                        f"AI={r['ai_system']} | regime={r['regime']} | "
                        f"conf={r['confidence']:.2f} | pnl={pnl_str}\n")

        title = f"Trade History Batch {batch_start // batch_size + 1} ({batch[0]['timestamp'][:10]})"
        doc_id = pipeline.ingest_raw_text(
            content=content, title=title, source_type='episodic',
            metadata={'category': 'own_trades', 'batch': batch_start // batch_size}
        )
        if doc_id:
            ingested += 1

    log.info(f"  [OK] Ingested {ingested} episodic memory batches ({len(rows)} trades)")
    return ingested


# ─────────────────────────────────────────────────────────────────────────────
# AUTONOMOUS PULL — arXiv RSS (free, no API key, q-fin + ML papers)
# ─────────────────────────────────────────────────────────────────────────────

def pull_arxiv_rss(pipeline) -> int:
    """Pull latest papers from arXiv RSS feeds. Free, no auth required."""
    log.info("PULL — arXiv RSS new papers...")
    try:
        import urllib.request
        import xml.etree.ElementTree as ET
    except ImportError:
        log.warning("  urllib/xml not available")
        return 0

    ingested = 0
    for cat in ARXIV_CATS:
        url = f"https://rss.arxiv.org/rss/{cat}"
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                xml_data = resp.read()
            root = ET.fromstring(xml_data)
            ns = {'dc': 'http://purl.org/dc/elements/1.1/'}

            for item in root.findall('.//item')[:20]:  # 20 newest per category
                title_el = item.find('title')
                desc_el  = item.find('description')
                link_el  = item.find('link')
                if title_el is None or desc_el is None:
                    continue

                title   = title_el.text or 'Unknown'
                abstract = desc_el.text or ''
                link    = link_el.text if link_el is not None else ''

                # Filter for trading-relevant content
                keywords = ['trading', 'portfolio', 'stock', 'market', 'finance',
                           'prediction', 'forecasting', 'deep learning', 'reinforcement',
                           'regime', 'momentum', 'volatility', 'risk', 'lstm', 'transformer']
                combined = (title + abstract).lower()
                if not any(kw in combined for kw in keywords):
                    continue

                content = (f"arXiv Paper: {title}\n"
                          f"Category: {cat}\n"
                          f"URL: {link}\n\n"
                          f"Abstract:\n{abstract}")

                doc_id = pipeline.ingest_raw_text(
                    content=content,
                    title=f"arXiv [{cat}]: {title[:80]}",
                    source_type='paper',
                    metadata={'source': 'arxiv_rss', 'category': cat,
                             'url': link, 'fetched': datetime.now().isoformat()}
                )
                if doc_id:
                    ingested += 1

        except Exception as e:
            log.warning(f"  arXiv {cat} feed failed: {e}")

    log.info(f"  [OK] Ingested {ingested} new arXiv papers")
    return ingested


# ─────────────────────────────────────────────────────────────────────────────
# AUTONOMOUS PULL — FRED Economic Releases (free, no key for basic access)
# ─────────────────────────────────────────────────────────────────────────────

def pull_fred_releases(pipeline) -> int:
    """Pull recent FRED economic release descriptions. Builds macro context."""
    log.info("PULL — FRED economic releases...")
    # Key FRED series that affect trading decisions
    FRED_SERIES = {
        'FEDFUNDS':   'Federal Funds Rate — impacts risk assets and bond yields',
        'CPIAUCSL':   'Consumer Price Index — inflation indicator, drives Fed policy',
        'UNRATE':     'Unemployment Rate — labor market health, risk-on/off signal',
        'DGS10':      '10-Year Treasury Yield — risk-free rate, equity valuation anchor',
        'VIXCLS':     'CBOE Volatility Index — market fear gauge, regime indicator',
        'SP500':      'S&P 500 Index — broad market benchmark',
        'DCOILWTICO': 'WTI Crude Oil — commodity regime, inflation proxy',
        'DTWEXBGS':   'US Dollar Index — currency strength, international capital flows',
    }

    try:
        import urllib.request, urllib.parse
        fred_key = os.getenv('FRED_API_KEY', '')
        ingested = 0

        for series_id, description in FRED_SERIES.items():
            try:
                if fred_key:
                    url = (f"https://api.stlouisfed.org/fred/series/observations"
                           f"?series_id={series_id}&api_key={fred_key}"
                           f"&file_type=json&limit=12&sort_order=desc")
                    with urllib.request.urlopen(url, timeout=10) as resp:
                        data = json.loads(resp.read())
                    obs = data.get('observations', [])
                    content = (f"FRED Series: {series_id}\n"
                              f"Description: {description}\n\n"
                              f"Recent Values (newest first):\n")
                    for o in obs[:12]:
                        content += f"  {o['date']}: {o['value']}\n"
                else:
                    # No API key — ingest the description and series context only
                    content = (f"FRED Economic Indicator: {series_id}\n"
                              f"Description: {description}\n\n"
                              f"This indicator is tracked by PROMETHEUS for macro regime context. "
                              f"Add FRED_API_KEY to .env for live values.\n"
                              f"Access at: https://fred.stlouisfed.org/series/{series_id}")

                doc_id = pipeline.ingest_raw_text(
                    content=content,
                    title=f"FRED: {series_id} — {description[:50]}",
                    source_type='study',
                    metadata={'source': 'fred', 'series': series_id,
                             'fetched': datetime.now().isoformat()}
                )
                if doc_id:
                    ingested += 1
            except Exception as e:
                log.warning(f"  FRED {series_id}: {e}")

        log.info(f"  [OK] Ingested {ingested} FRED series")
        return ingested
    except Exception as e:
        log.warning(f"  FRED pull failed: {e}")
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# AUTONOMOUS PULL — AQR Free Research Abstracts
# ─────────────────────────────────────────────────────────────────────────────

def pull_aqr_insights(pipeline) -> int:
    """
    Ingest AQR's key published research findings as structured knowledge.
    AQR publishes free papers at aqr.com/insights/research — these are
    the canonical institutional findings on momentum, value, carry, quality.
    Pre-compiled here to avoid scraping; add URL fetch if desired.
    """
    log.info("PULL — AQR Research insights (pre-compiled)...")

    AQR_PAPERS = [
        {
            "title": "Value and Momentum Everywhere (Asness et al., AQR)",
            "content": (
                "AQR Key Finding: Value and momentum premia exist across 8 asset classes "
                "and 4 geographic regions. Neither factor explains the other — they are "
                "negatively correlated, providing diversification. Combined value+momentum "
                "portfolios have significantly higher Sharpe ratios than either alone.\n\n"
                "Implementation: Rank assets by 12-month return minus 1-month (momentum) "
                "and book-to-market ratio (value). Go long top quartile, short bottom quartile. "
                "Rebalance monthly. Works in equities, fixed income, FX, commodities.\n\n"
                "Risk: Momentum crashes during sharp market reversals (2009 March). "
                "Value underperforms during momentum-driven bubbles. "
                "Drawdowns are correlated across asset classes during crises."
            ),
        },
        {
            "title": "Betting Against Beta (Frazzini & Pedersen, AQR)",
            "content": (
                "AQR Key Finding: Low-beta assets generate higher risk-adjusted returns than "
                "high-beta assets — the Security Market Line is too flat. The BAB factor "
                "(long low-beta, short high-beta) has produced positive returns in 20 of 23 "
                "developed equity markets.\n\n"
                "Mechanism: Leverage-constrained investors bid up high-beta assets, causing "
                "overpricing relative to CAPM predictions. Low-beta stocks are underowned.\n\n"
                "PROMETHEUS application: Prefer lower-beta signals in high-VIX regimes. "
                "Reduce exposure to high-beta names when HMM detects Crisis/Risk-Off state."
            ),
        },
        {
            "title": "Quality Minus Junk (Asness et al., AQR)",
            "content": (
                "AQR Key Finding: High-quality companies (profitable, growing, safe, high payout) "
                "are systematically underpriced. A long-quality short-junk factor (QMJ) earns "
                "positive returns globally.\n\n"
                "Quality metrics: Profitability (gross profit/assets), growth (5yr avg change), "
                "safety (low beta, low leverage, low earnings volatility), payout (dividend+buyback).\n\n"
                "PROMETHEUS application: When MarketResearcher AI scores fundamentals, "
                "weight quality metrics higher than growth in uncertain regimes. "
                "Quality outperforms during bear markets and recessions."
            ),
        },
        {
            "title": "Time Series Momentum (Moskowitz et al., AQR)",
            "content": (
                "AQR Key Finding: Each of 58 liquid futures contracts shows significant "
                "time series momentum — positive (negative) past 12-month returns predict "
                "positive (negative) future returns. Sharpe ratio ~1.28 before costs.\n\n"
                "Best lookback: 12 months (1-month excluded). Signal: sign of past 12-month return. "
                "Consistent across equities, bonds, currencies, commodities.\n\n"
                "PROMETHEUS application: Use 12-month price trend as a prior when LangGraph "
                "and Technical_Analysis systems generate conflicting signals. "
                "Time series momentum is the strongest single predictor across asset classes."
            ),
        },
        {
            "title": "Carry (Koijen et al., AQR)",
            "content": (
                "AQR Key Finding: Carry — the expected return of holding an asset if prices "
                "remain unchanged — predicts returns across asset classes. High-carry assets "
                "outperform low-carry assets.\n\n"
                "Asset class specifics:\n"
                "- FX: High-yield currencies outperform low-yield (carry trade)\n"
                "- Equities: High dividend yield stocks outperform\n"
                "- Fixed Income: Steeper yield curve segments outperform\n"
                "- Commodities: Backwardated contracts outperform contangoed\n\n"
                "PROMETHEUS crypto application: In BTC/ETH, funding rates signal carry. "
                "Positive funding = crowd is long = potential contrarian short signal."
            ),
        },
    ]

    ingested = 0
    for paper in AQR_PAPERS:
        doc_id = pipeline.ingest_raw_text(
            content=paper['content'],
            title=paper['title'],
            source_type='paper',
            metadata={'source': 'aqr_research', 'institution': 'AQR Capital Management',
                     'ingested': datetime.now().isoformat()}
        )
        if doc_id:
            ingested += 1

    log.info(f"  [OK] Ingested {ingested} AQR research papers")
    return ingested


# ─────────────────────────────────────────────────────────────────────────────
# FEED 3 — Learned pattern files
# ─────────────────────────────────────────────────────────────────────────────

def feed_learned_patterns(pipeline) -> int:
    """Ingest all learned_patterns_*.json files."""
    log.info("FEED 3/5 — Learned pattern files...")
    pattern_files = sorted(Path('.').glob('learned_patterns*.json'))
    ingested = 0
    for fp in pattern_files:
        try:
            data = json.loads(fp.read_text(encoding='utf-8'))
            content = f"Learned Patterns — {fp.name}\n\n{json.dumps(data, indent=2)[:8000]}"
            doc_id = pipeline.ingest_raw_text(
                content=content, title=f"Patterns: {fp.stem}",
                source_type='study',
                metadata={'source_file': fp.name, 'category': 'learned_patterns'}
            )
            if doc_id:
                ingested += 1
        except Exception as e:
            log.warning(f"  Could not ingest {fp.name}: {e}")

    log.info(f"  [OK] Ingested {ingested} pattern files")
    return ingested


# ─────────────────────────────────────────────────────────────────────────────
# FEED 4 — Missing PDFs in knowledge_base/
# ─────────────────────────────────────────────────────────────────────────────

def feed_missing_pdfs(pipeline) -> int:
    """Ingest all PDFs in knowledge_base/ — let _ingest_content handle deduplication.

    Previously this skipped PDFs whose path was in the metadata index, which caused
    documents indexed under the old ChromaDB backend to never be embedded in the
    numpy fallback store.  Passing every PDF through ingest_pdf() is safe because
    _ingest_content checks whether the doc's first chunk already exists in the
    *vector* store before embedding; already-embedded docs are skipped in <1ms.
    """
    log.info("FEED 4/5 — All PDFs in knowledge_base/...")
    ingested = 0
    pdfs = sorted(KNOWLEDGE_DIR.glob('*.pdf'))
    for pdf in pdfs:
        log.info(f"  Checking: {pdf.name}")
        doc_id = pipeline.ingest_pdf(str(pdf), source_type='paper')
        if doc_id:
            ingested += 1

    log.info(f"  [OK] Processed {len(pdfs)} PDFs, {ingested} newly embedded")
    return ingested


# ─────────────────────────────────────────────────────────────────────────────
# FEED 5 — ai_knowledge_training_data.json
# ─────────────────────────────────────────────────────────────────────────────

def feed_ai_knowledge_training(pipeline) -> int:
    """Ingest the compiled ai_knowledge_training_data.json."""
    log.info("FEED 5/5 — ai_knowledge_training_data.json...")
    fp = Path('ai_knowledge_training_data.json')
    if not fp.exists():
        log.warning("  Not found — skipping")
        return 0
    try:
        data = json.loads(fp.read_text(encoding='utf-8'))
        kb = data.get('knowledge_base', {})
        ingested = 0
        for category, items in kb.items():
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict):
                    title = item.get('title', category)
                    content = f"{title}\n\n{json.dumps(item, indent=2)[:6000]}"
                    doc_id = pipeline.ingest_raw_text(
                        content=content, title=title,
                        source_type='book',
                        metadata={'category': category, 'source': 'ai_knowledge_training'}
                    )
                    if doc_id:
                        ingested += 1
        log.info(f"  [OK] Ingested {ingested} training knowledge items")
        return ingested
    except Exception as e:
        log.warning(f"  Error: {e}")
        return 0



# ─────────────────────────────────────────────────────────────────────────────
# ORCHESTRATOR — run all feeds + pulls
# ─────────────────────────────────────────────────────────────────────────────

def run_local_feeds(pipeline) -> int:
    """Run all local (no-internet) feeds. Fast, safe to run anytime."""
    total = 0
    total += feed_arxiv_compiled(pipeline)
    total += feed_own_trade_history(pipeline)
    total += feed_learned_patterns(pipeline)
    total += feed_missing_pdfs(pipeline)
    total += feed_ai_knowledge_training(pipeline)
    return total


def run_autonomous_pulls(pipeline) -> int:
    """Run internet pulls. Requires connectivity."""
    total = 0
    total += pull_arxiv_rss(pipeline)
    total += pull_fred_releases(pipeline)
    total += pull_aqr_insights(pipeline)
    return total


def save_pull_timestamp():
    LAST_PULL_FILE.write_text(
        json.dumps({'last_pull': datetime.now().isoformat()}), encoding='utf-8'
    )


def should_pull_now(interval_days: int = 7) -> bool:
    if not LAST_PULL_FILE.exists():
        return True
    try:
        data = json.loads(LAST_PULL_FILE.read_text(encoding='utf-8'))
        last = datetime.fromisoformat(data['last_pull'])
        return (datetime.now() - last).days >= interval_days
    except Exception:
        return True


def run_once(local_only: bool = False):
    """Execute one full knowledge ingestion cycle."""
    log.info("=" * 70)
    log.info("PROMETHEUS KNOWLEDGE AUTO-DISCOVERY  — starting")
    log.info("=" * 70)

    pipeline = get_pipeline()

    local_count = run_local_feeds(pipeline)
    log.info(f"Local feeds complete: {local_count} new documents ingested")

    if not local_only:
        if should_pull_now():
            pull_count = run_autonomous_pulls(pipeline)
            save_pull_timestamp()
            log.info(f"Autonomous pulls complete: {pull_count} new documents ingested")
        else:
            log.info("Autonomous pull skipped — ran within last 7 days")

    total = pipeline.get_total_embeddings() if hasattr(pipeline, 'get_total_embeddings') else '?'
    log.info(f"Knowledge base now contains ~{total} embeddings")
    log.info("AUTO-DISCOVERY COMPLETE [OK]")


def run_daemon(interval_hours: int = 168):
    """Run as a background daemon, pulling new knowledge weekly."""
    log.info(f"Starting knowledge daemon (interval: {interval_hours}h)")
    while True:
        try:
            run_once()
        except Exception as e:
            log.error(f"Daemon cycle error: {e}", exc_info=True)
        log.info(f"Next pull in {interval_hours} hours — sleeping...")
        time.sleep(interval_hours * 3600)


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='PROMETHEUS Knowledge Auto-Discovery & Autonomous Ingestion'
    )
    parser.add_argument('--now',    action='store_true', help='Local feeds only (fast, no internet)')
    parser.add_argument('--daemon', action='store_true', help='Run as weekly background daemon')
    parser.add_argument('--hours',  type=int, default=168, help='Daemon interval in hours (default: 168 = weekly)')
    args = parser.parse_args()

    if args.daemon:
        run_daemon(interval_hours=args.hours)
    else:
        run_once(local_only=args.now)
