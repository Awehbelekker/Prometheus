#!/usr/bin/env python3
"""
Broker snapshot (read-only): prints Alpaca account, positions, and recent orders.
Safe: does not place or cancel orders. Defaults to PAPER unless env flags enable live.
"""
import os
import sys

# Repo root and env loading
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
from dotenv import load_dotenv
load_dotenv(os.path.join(repo_root, '.env'))
# Ensure repo root on path
sys.path.insert(0, repo_root)


from core.alpaca_trading_service import get_alpaca_service

def _is_true(name: str) -> bool:
    return os.getenv(name, "false").strip().lower() in ("1", "true", "yes", "on")

def resolve_use_paper() -> bool:
    allow_live = _is_true('ALLOW_LIVE_TRADING') or (
        _is_true('ENABLE_LIVE_ORDER_EXECUTION') and _is_true('LIVE_TRADING_ENABLED') and not _is_true('PAPER_TRADING_ONLY')
    )
    return not allow_live

def main():
    use_paper = resolve_use_paper()
    svc = get_alpaca_service(use_paper=use_paper)
    if not svc.is_available():
        print("[ERROR] Alpaca service not available.")
        return 1

    acct = svc.get_account_info()
    pos = svc.get_positions()
    orders = svc.get_orders(limit=5) if hasattr(svc, 'get_orders') else []

    print("\n📄 Broker Snapshot")
    print(f"Environment: {'PAPER' if use_paper else 'LIVE'}")
    if isinstance(acct, dict) and acct.get('error'):
        print(f"Account error: {acct['error']}")
    else:
        print(f"Equity: {acct.get('portfolio_value')}  Cash: {acct.get('cash')}  Buying Power: {acct.get('buying_power')}")

    print("\nPositions (top 10):")
    for p in (pos or [])[:10]:
        print(f"  - {p.get('symbol')} qty={p.get('qty')} avg={p.get('avg_entry_price')} unrealized={p.get('unrealized_pl')}")

    print("\nRecent Orders (up to 5):")
    for o in (orders or [])[:5]:
        print(f"  - {o.get('symbol')} {o.get('side')} {o.get('qty')} status={o.get('status')} filled={o.get('filled_qty')} avg={o.get('filled_avg_price')} id={o.get('id')}")

    return 0

if __name__ == '__main__':
    raise SystemExit(main())

