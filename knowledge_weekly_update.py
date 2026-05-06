"""
PROMETHEUS Weekly Knowledge Update
Pulls the latest arXiv papers on ML trading and ingests them into ChromaDB.

Run manually:   python knowledge_weekly_update.py
Scheduled via:  setup_autostart.ps1 (Sunday 07:00, before weekly WhatsApp report)

Topics pulled:
  - quantitative finance (q-fin)
  - ML for financial time series
  - deep reinforcement learning trading
  - LLM financial applications
  - market microstructure
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-7s  %(message)s',
    handlers=[
        logging.FileHandler('knowledge_update.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger('knowledge_update')

ROOT = Path(__file__).parent
KNOWLEDGE_DIR = ROOT / 'knowledge_base'
KNOWLEDGE_DIR.mkdir(exist_ok=True)

# arXiv search queries — each pulls up to MAX_RESULTS papers
ARXIV_QUERIES = [
    ("machine learning stock trading", 8),
    ("deep reinforcement learning portfolio management", 6),
    ("LLM financial markets sentiment", 6),
    ("transformer time series prediction finance", 5),
    ("market regime detection neural network", 4),
    ("quantitative trading deep learning", 5),
]

MAX_AGE_DAYS = 90   # only fetch papers published in last 90 days


def fetch_arxiv_papers():
    """Download recent arXiv papers matching trading/ML topics."""
    try:
        import arxiv
    except ImportError:
        log.error("arxiv package not installed — run: pip install arxiv")
        return []

    all_papers = []
    seen_ids = set()

    cutoff = datetime.now() - timedelta(days=MAX_AGE_DAYS)

    for query, max_results in ARXIV_QUERIES:
        log.info(f"Searching arXiv: '{query}' (last {MAX_AGE_DAYS}d)")
        try:
            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=max_results * 2,  # over-fetch, filter by date
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )
            for paper in client.results(search):
                if paper.entry_id in seen_ids:
                    continue
                if paper.published.replace(tzinfo=None) < cutoff:
                    continue
                seen_ids.add(paper.entry_id)
                all_papers.append({
                    "id": paper.entry_id.split("/")[-1],
                    "title": paper.title,
                    "authors": [str(a) for a in paper.authors[:3]],
                    "abstract": paper.summary,
                    "published": paper.published.strftime("%Y-%m-%d"),
                    "url": paper.entry_id,
                    "categories": paper.categories,
                    "query": query,
                })
                if len([p for p in all_papers if p["query"] == query]) >= max_results:
                    break
            time.sleep(1)  # be polite to arXiv
        except Exception as e:
            log.warning(f"arXiv query failed for '{query}': {e}")

    log.info(f"Fetched {len(all_papers)} new papers from arXiv")
    return all_papers


def save_papers_as_text(papers):
    """Save each paper abstract as a .txt file for ingestion."""
    saved = []
    for p in papers:
        fname = KNOWLEDGE_DIR / f"arxiv_{p['id']}.txt"
        if fname.exists():
            continue  # already ingested
        content = (
            f"TITLE: {p['title']}\n"
            f"AUTHORS: {', '.join(p['authors'])}\n"
            f"PUBLISHED: {p['published']}\n"
            f"SOURCE: arXiv {p['url']}\n"
            f"CATEGORIES: {', '.join(p['categories'])}\n\n"
            f"ABSTRACT:\n{p['abstract']}\n"
        )
        fname.write_text(content, encoding='utf-8')
        saved.append(str(fname))
    log.info(f"Saved {len(saved)} new paper files")
    return saved


def run_ingestion(new_files):
    """Feed new files into the knowledge ingestion pipeline."""
    if not new_files:
        log.info("No new files to ingest")
        return 0

    try:
        # Import and run the pipeline
        sys.path.insert(0, str(ROOT))
        from knowledge_ingestion_pipeline import KnowledgeIngestionPipeline

        pipeline = KnowledgeIngestionPipeline(
            knowledge_dir=str(KNOWLEDGE_DIR),
            vector_db_path=str(ROOT / 'knowledge_vectors')
        )

        ingested = 0
        for fpath in new_files:
            try:
                p = Path(fpath)
                if p.suffix == '.pdf':
                    result = pipeline.ingest_pdf(fpath, title=p.stem)
                else:
                    result = pipeline.ingest_text(fpath, title=p.stem)
                if result:
                    ingested += 1
                    log.info(f"Ingested: {p.name}")
            except Exception as e:
                log.warning(f"Failed to ingest {fpath}: {e}")

        log.info(f"Ingestion complete: {ingested}/{len(new_files)} documents added")
        return ingested
    except Exception as e:
        log.error(f"Pipeline error: {e}")
        return 0


def save_summary(papers, ingested_count):
    """Save a JSON summary of this update run."""
    summary = {
        "run_date": datetime.now().isoformat(),
        "papers_fetched": len(papers),
        "papers_ingested": ingested_count,
        "papers": [{"id": p["id"], "title": p["title"], "published": p["published"]}
                   for p in papers],
    }
    out = ROOT / f"knowledge_update_{datetime.now().strftime('%Y%m%d')}.json"
    out.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    log.info(f"Summary saved: {out.name}")
    return summary


def main():
    log.info("=" * 60)
    log.info("PROMETHEUS Weekly Knowledge Update")
    log.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log.info("=" * 60)

    papers = fetch_arxiv_papers()
    if not papers:
        log.warning("No papers fetched — check network connection")
        return

    new_files = save_papers_as_text(papers)
    ingested = run_ingestion(new_files)
    summary = save_summary(papers, ingested)

    log.info("=" * 60)
    log.info(f"Update complete: {ingested} new papers added to knowledge base")
    log.info("=" * 60)

    # Send WhatsApp notification if reporter is configured
    try:
        env_path = ROOT / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding='utf-8').splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

        api_key = os.environ.get("CALLMEBOT_API_KEY", "")
        if api_key and ingested > 0:
            from prometheus_reporter import send_whatsapp
            send_whatsapp(
                f"PROMETHEUS Knowledge Update\n"
                f"{ingested} new research papers indexed\n"
                f"Topics: ML trading, DRL, LLM finance\n"
                f"Total vectors: growing"
            )
    except Exception:
        pass


if __name__ == "__main__":
    main()
