#!/usr/bin/env python3
"""Quick DB audit."""
import sqlite3, os, glob
from pathlib import Path

dbs = ["prometheus_trading.db", "prometheus_learning.db", "prometheus_replay_training.db", "trading_data.db"]

for db in dbs:
    if not os.path.exists(db):
        print(f"{db}: NOT FOUND")
        continue
    conn = sqlite3.connect(db)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"\n{db}: {len(tables)} tables")
    for t in tables:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
            if count > 0:
                print(f"  {t}: {count} rows")
        except:
            pass
    conn.close()

# Model counts
daily = list(Path("models_pretrained").glob("*_direction_model.pkl"))
intra = list(Path("models_pretrained").glob("*_intraday_5m_model.pkl"))
meta = list(Path("models_pretrained").glob("META_*"))
print(f"\nMODELS: {len(daily)} daily, {len(intra)} intraday, {len(meta)} meta = {len(daily)+len(intra)+len(meta)} total")

# Check ai_attribution table
for db in ["prometheus_trading.db", "prometheus_learning.db"]:
    if os.path.exists(db):
        conn = sqlite3.connect(db)
        try:
            cnt = conn.execute("SELECT COUNT(*) FROM ai_attribution").fetchone()[0]
            print(f"\nai_attribution in {db}: {cnt} rows")
        except:
            print(f"\nai_attribution in {db}: TABLE NOT FOUND")
        conn.close()

# Check broker balances from env
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if "ALPACA" in line or "IB_" in line or "BROKER" in line:
                key = line.split("=")[0].strip()
                if "KEY" in key or "SECRET" in key or "PASSWORD" in key:
                    print(f"  {key}=***")
                else:
                    print(f"  {line.strip()}")
