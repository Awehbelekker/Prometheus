"""
PROMETHEUS Knowledge Books Downloader
Downloads large ML/trading books that are too big for git.
Run once after cloning on a new server.

Usage: python download_knowledge_books.py
"""

import urllib.request
import time
from pathlib import Path

kb = Path("knowledge_base")
kb.mkdir(exist_ok=True)

BOOKS = [
    # Large books (excluded from git due to size — downloaded here)
    (
        "https://raw.githubusercontent.com/meerilahi/Books-Collection/main/"
        "Reinforcement%20Learning%20An%20Introduction%20Richard%20S.%20Sutton%20and%20Andrew%20G%20Barto.pdf",
        "reinforcement_learning_sutton_barto.pdf",
        "Reinforcement Learning: An Introduction (Sutton & Barto) — 85MB",
    ),
    (
        "https://raw.githubusercontent.com/meerilahi/Books-Collection/main/"
        "Probabalistic%20Machine%20Learning%20Advance%20Topics%20Kevin%20P%20Murphy.pdf",
        "probabilistic_ml_advanced_murphy.pdf",
        "Probabilistic ML Advanced Topics (Murphy) — 65MB",
    ),
    # Lopez de Prado full book (in git, but re-download if missing)
    (
        "https://raw.githubusercontent.com/meerilahi/Books-Collection/main/"
        "Advances%20in%20Financial%20Machine%20Learning%20Marcos%20Lopez%20de%20Prado.pdf",
        "advances_in_financial_machine_learning_lopez_de_prado.pdf",
        "Advances in Financial Machine Learning (Lopez de Prado) — 8MB",
    ),
]

headers = {"User-Agent": "Mozilla/5.0"}

print("PROMETHEUS Knowledge Books Downloader")
print("=" * 50)

for url, fname, desc in BOOKS:
    dest = kb / fname
    if dest.exists():
        print(f"[SKIP] Already exists: {fname}")
        continue
    print(f"[DOWN] {desc}")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=180) as r:
            data = r.read()
        if data[:4] == b"%PDF":
            dest.write_bytes(data)
            print(f"  OK  {len(data)//1024//1024:.0f}MB saved")
        else:
            print(f"  ERR not a valid PDF")
        time.sleep(2)
    except Exception as e:
        print(f"  ERR {e}")

print()
print("Done. Now run: python knowledge_ingestion_pipeline.py")
