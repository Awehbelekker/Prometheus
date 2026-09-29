"""
PROMETHEUS Knowledge Books Downloader
======================================
Downloads the two textbooks that exceed GitHub's 100MB file limit.
All other PDFs (28 research papers + books ≤ 20MB) are tracked in git.

Two-command server setup after git clone:
  python download_knowledge_books.py           # fetch Sutton (85MB) + Murphy (65MB)
  python prometheus_knowledge_autodiscovery.py --now  # embed everything → numpy store

Knowledge base after setup:
  - 28 research PDFs  (papers, books)
  - 42 trade-history batches (episodic memory)
  - 7 learned-pattern files
  - 4 arXiv compiled sections (831 papers distilled)
  Total: ~19,000 vectors  (all-MiniLM-L6-v2, 384-dim, cosine)
"""

import sys
import urllib.request
import time
from pathlib import Path

kb = Path("knowledge_base")
kb.mkdir(exist_ok=True)

# ── Books that must be downloaded (too large for git) ─────────────────────────
LARGE_BOOKS = [
    (
        "https://raw.githubusercontent.com/meerilahi/Books-Collection/main/"
        "Reinforcement%20Learning%20An%20Introduction%20Richard%20S.%20Sutton%20and%20Andrew%20G%20Barto.pdf",
        "reinforcement_learning_sutton_barto.pdf",
        "Reinforcement Learning (Sutton & Barto)",
        85,
    ),
    (
        "https://raw.githubusercontent.com/meerilahi/Books-Collection/main/"
        "Probabalistic%20Machine%20Learning%20Advance%20Topics%20Kevin%20P%20Murphy.pdf",
        "probabilistic_ml_advanced_murphy.pdf",
        "Probabilistic ML Advanced Topics (Murphy)",
        65,
    ),
]

# ── PDFs that should already be in git — warn if missing ─────────────────────
GIT_PDFS = [
    "advances_in_financial_machine_learning_lopez_de_prado.pdf",
    "book_of_why_pearl_causal_inference.pdf",
    "deep_learning_goodfellow.pdf",
    "hands_on_llm_alammar.pdf",
    "ml_in_finance_dixon_halperin.pdf",
    "rl_stochastic_optimization_powell.pdf",
    "FinBERT_Financial_Sentiment.pdf",
    "Deep_RL_Portfolio_Management.pdf",
    "Transformer_Time_Series.pdf",
    "HiPPO_Recurrent_Memory.pdf",
    "hidden_markov_market_regime.pdf",
    "Deep_Momentum_Networks.pdf",
    "deep_learning_asset_pricing.pdf",
    "almgren_chriss_optimal_execution.pdf",
    "kelly_criterion_portfolio_sizing.pdf",
    "momentum_crashes_understanding.pdf",
    "machine_learning_return_prediction.pdf",
    "earnings_surprise_ml_prediction.pdf",
    "Stock_Prediction_Deep_Learning.pdf",
    "Time_Varying_Neural_Network_Stock.pdf",
    "Qlib_AI_Quantitative_Investment.pdf",
    "DeepSeek_R1_Reasoning.pdf",
    "lopez_de_prado_triple_barrier_labeling.pdf",
    "lopez_de_prado_portfolio_construction_ml.pdf",
    "lopez_de_prado_causal_factor_investing.pdf",
    "lopez_de_prado_10_reasons_ml_funds_fail.pdf",
]

HEADERS = {"User-Agent": "Mozilla/5.0"}

print("PROMETHEUS Knowledge Books Downloader")
print("=" * 50)

# ── Download large books ───────────────────────────────────────────────────────
errors = 0
for url, fname, desc, size_mb in LARGE_BOOKS:
    dest = kb / fname
    if dest.exists() and dest.stat().st_size > 1_000_000:
        print(f"  [OK]   {fname} ({dest.stat().st_size // 1024 // 1024}MB already present)")
        continue
    print(f"  [DL]   {desc}  (~{size_mb}MB) ...")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=300) as r:
            data = r.read()
        if data[:4] == b"%PDF":
            dest.write_bytes(data)
            print(f"         saved {len(data) // 1024 // 1024}MB → {fname}")
        else:
            print(f"  [ERR]  Response was not a PDF — check URL")
            errors += 1
        time.sleep(2)
    except Exception as exc:
        print(f"  [ERR]  {exc}")
        errors += 1

# ── Verify git-tracked PDFs are present ───────────────────────────────────────
print()
missing_git = [f for f in GIT_PDFS if not (kb / f).exists()]
if missing_git:
    print(f"  [WARN] {len(missing_git)} git-tracked PDFs not found locally:")
    for f in missing_git:
        print(f"         {f}")
    print("         Run: git lfs pull   (or check your clone is complete)")
else:
    print(f"  [OK]   All {len(GIT_PDFS)} git-tracked PDFs present")

# ── Summary ───────────────────────────────────────────────────────────────────
total_pdfs = len(list(kb.glob("*.pdf")))
total_mb   = sum(f.stat().st_size for f in kb.glob("*.pdf")) // 1024 // 1024
print()
print(f"knowledge_base/: {total_pdfs} PDFs  ({total_mb}MB total)")
print()
if errors:
    print(f"  {errors} download error(s) — fix above then re-run")
    sys.exit(1)
else:
    print("Next step:")
    print("  python prometheus_knowledge_autodiscovery.py --now")
    print("  (embeds all 28 PDFs + trade history + patterns → ~19,000 vectors)")
