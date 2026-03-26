from alpaca.trading.client import TradingClient
import os

api_key = os.getenv('ALPACA_API_KEY')
api_secret = os.getenv('ALPACA_SECRET_KEY')

with open('alpaca_status_report.txt', 'w') as f:
    if not api_key or not api_secret:
        f.write('Alpaca API key/secret not found in environment.\n')
    else:
        client = TradingClient(api_key, api_secret, paper=False)
        account = client.get_account()
        positions = client.get_all_positions()
        f.write(f'Account Value: ${float(account.equity):,.2f}\n')
        f.write(f'Cash: ${float(account.cash):,.2f}\n')
        f.write(f'Buying Power: ${float(account.buying_power):,.2f}\n')
        if hasattr(account, 'unrealized_pl') and account.unrealized_pl:
            pl = float(account.unrealized_pl)
            plpc = (float(account.unrealized_plpc) * 100) if hasattr(account, 'unrealized_plpc') else 0
            f.write(f'Unrealized P&L: ${pl:.2f} ({plpc:+.2f}%)\n')
        else:
            f.write('Unrealized P&L: $0.00\n')
        f.write(f'\nPositions: {len(positions)}\n')
        if positions:
            for pos in positions:
                qty = float(pos.qty)
                avg_price = float(pos.avg_entry_price)
                current_price = float(pos.current_price)
                current_value = qty * current_price
                pnl = float(pos.unrealized_pl)
                pnl_pct = float(pos.unrealized_plpc) * 100
                f.write(f'{pos.symbol}: {qty} @ ${avg_price:.2f} (now: ${current_price:.2f}) = ${current_value:.2f}, P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)\n')
        else:
            f.write('No open positions\n')
