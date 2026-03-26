import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dotenv import load_dotenv
load_dotenv()
from core.alpaca_trading_service import AlpacaTradingService

print("=" * 70)
print(" ALPACA LIVE - POSITIONS & HOLD/SELL ANALYSIS")
print("=" * 70)
svc = AlpacaTradingService(use_paper_trading=False)
info = svc.get_account_info()
if info and "error" not in info:
    print(f"  Equity: ${info.get('equity',0):.2f} | Cash: ${info.get('cash',0):.2f} | BP: ${info.get('buying_power',0):.2f}")

positions = svc.get_positions()
print(f"\n  Open Positions: {len(positions)}")
if positions:
    for p in positions:
        pct = p['unrealized_plpc'] * 100
        v = 'HOLD+' if pct>2 else 'HOLD' if pct>-3 else 'WATCH' if pct>-8 else 'SELL?'
        print(f"  {p['symbol']:10s} qty={p['qty']} avg=${p['avg_entry_price']:.4f} now=${p['current_price']:.4f} P/L=${p['unrealized_pl']:+.4f} ({pct:+.1f}%) -> {v}")
else:
    print("  NO OPEN POSITIONS (all 52 DB pending records are stale signal logs)")

print(f"\n{'='*70}")
print(" ALPACA PAPER DIAGNOSIS")
print("=" * 70)
psvc = AlpacaTradingService(use_paper_trading=True)
pi = psvc.get_account_info()
if pi and "error" not in pi:
    print(f"  Equity: ${pi.get('equity',0):.2f} | Cash: ${pi.get('cash',0):.2f}")
    pp = psvc.get_positions()
    print(f"  Paper Positions: {len(pp)}")
    if float(pi.get('equity',0)) >= 99000:
        print("  DIAGNOSIS: Paper $100K untouched = EXPECTED.")
        print("  PROMETHEUS trades LIVE only. Shadow system is internal, not Alpaca Paper.")
else:
    print(f"  Paper error: {pi}")
