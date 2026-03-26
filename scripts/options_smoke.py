import os, sys
from dotenv import load_dotenv

# Ensure repo root on path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(repo_root)

load_dotenv(os.path.join(repo_root, '.env'))

from core.alpaca_trading_service import AlpacaTradingService, get_alpaca_service

def main():
    print("OPTIONS API SMOKE (read-only)")
    # Force safety message (we do not place orders here)
    os.environ['ALLOW_LIVE_TRADING'] = 'false'

    svc = get_alpaca_service(use_paper=True)
    print("Service available:", svc.is_available())

    samples = [
        'AAPL 2025-01-17 C 200',
        'TSLA 2025-03-21 P 412.5',
        'AAPL250117C00200000'
    ]
    for s in samples:
        try:
            occ = AlpacaTradingService.normalize_option_symbol(s)
            print(f"  {s} -> {occ}")
        except Exception as e:
            print(f"  {s} -> ERROR: {e}")

    try:
        orders = svc.get_options_orders(limit=3)
        print("Options orders count:", len(orders))
    except Exception as e:
        print("List options orders failed:", e)

if __name__ == '__main__':
    main()

