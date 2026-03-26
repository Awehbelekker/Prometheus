"""
COMPREHENSIVE TRADING COST ANALYSIS FOR PROMETHEUS
Analyzes all trading costs, historical performance, and generates optimization recommendations
"""
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class TradingCosts:
    """Trading cost structure for a broker/asset combination"""
    broker: str
    asset_class: str
    commission_per_share: float = 0.0
    commission_pct: float = 0.0
    min_commission: float = 0.0
    maker_fee: float = 0.0
    taker_fee: float = 0.0
    spread_pct: float = 0.0
    slippage_pct: float = 0.0
    regulatory_fees: float = 0.0
    
    @property
    def total_entry_cost_pct(self) -> float:
        return self.taker_fee + self.spread_pct / 2 + self.slippage_pct
    
    @property
    def total_exit_cost_pct(self) -> float:
        return self.taker_fee + self.spread_pct / 2 + self.slippage_pct
    
    @property
    def round_trip_pct(self) -> float:
        return self.total_entry_cost_pct + self.total_exit_cost_pct
    
    @property
    def min_profitable_move_pct(self) -> float:
        return self.round_trip_pct * 1.5  # Need 1.5x costs to be worthwhile


# Define actual trading costs based on broker documentation
TRADING_COSTS = {
    'alpaca_stocks': TradingCosts(
        broker='Alpaca',
        asset_class='Stocks/ETFs',
        commission_per_share=0.0,  # Commission-free
        spread_pct=0.0002,  # ~0.02% for liquid stocks
        slippage_pct=0.0005,  # ~0.05% typical slippage
        regulatory_fees=0.000008,  # SEC fee: $8 per $1M
    ),
    'alpaca_crypto': TradingCosts(
        broker='Alpaca',
        asset_class='Crypto',
        maker_fee=0.0015,  # 0.15% maker
        taker_fee=0.0025,  # 0.25% taker (market orders)
        spread_pct=0.002,  # ~0.2% typical spread
        slippage_pct=0.001,  # ~0.1% slippage
    ),
    'ib_stocks_lite': TradingCosts(
        broker='IB Lite',
        asset_class='Stocks/ETFs',
        commission_per_share=0.0,  # Commission-free for Lite
        spread_pct=0.0001,  # ~0.01% for very liquid
        slippage_pct=0.0003,  # ~0.03% slippage
        regulatory_fees=0.000008,
    ),
    'ib_stocks_pro': TradingCosts(
        broker='IB Pro',
        asset_class='Stocks/ETFs',
        commission_per_share=0.005,  # $0.005/share
        min_commission=1.0,  # $1 minimum
        spread_pct=0.0001,
        slippage_pct=0.0003,
        regulatory_fees=0.000008,
    ),
    'ib_options': TradingCosts(
        broker='IB',
        asset_class='Options',
        commission_pct=0.0,  # Per contract
        min_commission=0.65,  # $0.65/contract
        spread_pct=0.02,  # ~2% typical spread
        slippage_pct=0.01,  # ~1% slippage
    ),
    'ib_forex': TradingCosts(
        broker='IB',
        asset_class='Forex',
        commission_pct=0.00002,  # 0.2 basis points
        spread_pct=0.0001,  # ~1 pip
        slippage_pct=0.00005,
    ),
}


def analyze_trade_history():
    """Analyze all historical trades from the database"""
    db = sqlite3.connect('prometheus_learning.db')
    c = db.cursor()
    
    print('=' * 100)
    print('COMPREHENSIVE TRADE HISTORY ANALYSIS')
    print('=' * 100)
    
    # Get all closed trades
    c.execute('''
        SELECT 
            symbol, action, price, exit_price, quantity, profit_loss,
            broker, timestamp, exit_timestamp
        FROM trade_history
        WHERE exit_price IS NOT NULL AND exit_price > 0 AND price > 0
        ORDER BY timestamp DESC
    ''')
    
    trades = c.fetchall()
    print(f'\nTotal Closed Trades: {len(trades)}')
    
    # Categorize trades
    stock_trades = []
    crypto_trades = []
    
    for t in trades:
        symbol, action, entry, exit_p, qty, pnl, broker, ts, exit_ts = t
        qty = qty or 0
        pnl = pnl or 0
        pct = ((exit_p - entry) / entry * 100) if entry > 0 else 0
        
        trade_data = {
            'symbol': symbol,
            'entry': entry,
            'exit': exit_p,
            'qty': qty,
            'pnl': pnl,
            'pct': pct,
            'broker': broker or 'Alpaca',
            'value': entry * qty
        }
        
        if '/' in symbol or symbol.endswith('USD'):
            crypto_trades.append(trade_data)
        else:
            stock_trades.append(trade_data)
    
    return stock_trades, crypto_trades, db


def print_trade_analysis(trades: List[Dict], asset_type: str):
    """Print detailed analysis for a set of trades"""
    if not trades:
        print(f'\nNo {asset_type} trades found.')
        return

    total_value = sum(t['value'] for t in trades)
    total_pnl = sum(t['pnl'] for t in trades)
    avg_pct = sum(t['pct'] for t in trades) / len(trades)
    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] <= 0]

    print(f'\n{asset_type.upper()} TRADES ANALYSIS')
    print('-' * 60)
    print(f'Total Trades: {len(trades)}')
    print(f'Wins: {len(wins)} | Losses: {len(losses)}')
    print(f'Win Rate: {len(wins)/len(trades)*100:.1f}%')
    print(f'Total P/L: ${total_pnl:.4f}')
    print(f'Avg P/L %: {avg_pct:.3f}%')
    print(f'Avg Trade Value: ${total_value/len(trades):.2f}')

    if wins:
        avg_win = sum(t['pct'] for t in wins) / len(wins)
        max_win = max(t['pct'] for t in wins)
        print(f'Avg Win: +{avg_win:.2f}% | Max Win: +{max_win:.2f}%')

    if losses:
        avg_loss = sum(t['pct'] for t in losses) / len(losses)
        max_loss = min(t['pct'] for t in losses)
        print(f'Avg Loss: {avg_loss:.2f}% | Max Loss: {max_loss:.2f}%')

    print(f'\nTop 10 {asset_type} Trades:')
    for t in trades[:10]:
        status = 'WIN' if t['pnl'] > 0 else 'LOSS'
        print(f"  {t['symbol']:12} Entry: ${t['entry']:8.2f} Exit: ${t['exit']:8.2f} "
              f"Qty: {t['qty']:.4f} P/L: ${t['pnl']:+.4f} ({t['pct']:+.2f}%) [{status}]")


def print_profit_distribution(trades: List[Dict]):
    """Print profit distribution analysis"""
    if not trades:
        return

    all_pcts = [t['pct'] for t in trades]

    print('\n' + '=' * 100)
    print('PROFIT DISTRIBUTION ANALYSIS')
    print('=' * 100)

    ranges = [
        (-100, -5, 'Heavy Loss (< -5%)'),
        (-5, -3, 'Moderate Loss (-5% to -3%)'),
        (-3, -1, 'Small Loss (-3% to -1%)'),
        (-1, 0, 'Tiny Loss (-1% to 0%)'),
        (0, 0.5, 'Tiny Win (0% to 0.5%)'),
        (0.5, 1, 'Small Win (0.5% to 1%)'),
        (1, 2, 'Moderate Win (1% to 2%)'),
        (2, 3, 'Good Win (2% to 3%)'),
        (3, 5, 'Great Win (3% to 5%)'),
        (5, 100, 'Excellent Win (> 5%)'),
    ]

    print(f'\n{"Range":<30} {"Count":>8} {"Pct":>8} {"Cumulative":>12}')
    print('-' * 60)

    cumulative = 0
    for low, high, label in ranges:
        count = len([p for p in all_pcts if low <= p < high])
        pct = count / len(all_pcts) * 100
        cumulative += pct
        bar = '#' * int(pct / 2)
        print(f'{label:<30} {count:>8} {pct:>7.1f}% {cumulative:>10.1f}% {bar}')


def print_cost_comparison_table():
    """Print the trading cost comparison table"""
    print('\n' + '=' * 100)
    print('TRADING COST COMPARISON TABLE')
    print('=' * 100)

    print(f'\n{"Broker":<12} {"Asset Class":<15} {"Entry Cost":<12} {"Exit Cost":<12} '
          f'{"Round-Trip %":<14} {"Min Profitable Move":<20}')
    print('-' * 95)

    for key, cost in TRADING_COSTS.items():
        entry = f'{cost.total_entry_cost_pct*100:.3f}%'
        exit_c = f'{cost.total_exit_cost_pct*100:.3f}%'
        rt = f'{cost.round_trip_pct*100:.3f}%'
        min_move = f'{cost.min_profitable_move_pct*100:.3f}%'

        print(f'{cost.broker:<12} {cost.asset_class:<15} {entry:<12} {exit_c:<12} '
              f'{rt:<14} {min_move:<20}')


def calculate_cost_impact(trades: List[Dict], cost_structure: TradingCosts):
    """Calculate how costs impact profitability"""
    if not trades:
        return

    print(f'\n--- Cost Impact Analysis for {cost_structure.broker} {cost_structure.asset_class} ---')

    gross_profitable = 0
    net_profitable = 0
    cost_killed = 0

    for t in trades:
        gross_pnl_pct = t['pct']
        cost_pct = cost_structure.round_trip_pct * 100
        net_pnl_pct = gross_pnl_pct - cost_pct

        if gross_pnl_pct > 0:
            gross_profitable += 1
            if net_pnl_pct > 0:
                net_profitable += 1
            else:
                cost_killed += 1

    print(f'Gross Profitable Trades: {gross_profitable} ({gross_profitable/len(trades)*100:.1f}%)')
    print(f'Net Profitable (after costs): {net_profitable} ({net_profitable/len(trades)*100:.1f}%)')
    print(f'Trades Killed by Costs: {cost_killed} ({cost_killed/len(trades)*100:.1f}%)')


if __name__ == '__main__':
    stock_trades, crypto_trades, db = analyze_trade_history()

    print_trade_analysis(stock_trades, 'Stock')
    print_trade_analysis(crypto_trades, 'Crypto')

    all_trades = stock_trades + crypto_trades
    print_profit_distribution(all_trades)

    print_cost_comparison_table()

    # Calculate cost impact
    if stock_trades:
        calculate_cost_impact(stock_trades, TRADING_COSTS['alpaca_stocks'])
    if crypto_trades:
        calculate_cost_impact(crypto_trades, TRADING_COSTS['alpaca_crypto'])

    db.close()

