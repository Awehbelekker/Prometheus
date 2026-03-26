"""
OPTIMAL TAKE PROFIT ANALYSIS
Analyzes historical trades to determine the optimal take profit level.
"""
import sqlite3

def analyze_optimal_take_profit():
    db = sqlite3.connect('prometheus_learning.db')
    c = db.cursor()

    print('=' * 80)
    print('OPTIMAL TAKE PROFIT ANALYSIS')
    print('=' * 80)

    # Get all closed trades with P/L
    c.execute('''
        SELECT 
            symbol, 
            price, 
            exit_price, 
            quantity,
            profit_loss,
            (exit_price - price) / price * 100 as profit_pct
        FROM trade_history
        WHERE exit_price IS NOT NULL AND exit_price > 0 AND price > 0
        AND profit_loss IS NOT NULL
        ORDER BY profit_pct DESC
    ''')

    trades = c.fetchall()
    print(f'Total Closed Trades with P/L: {len(trades)}')

    if not trades:
        print("No trades found!")
        return

    profit_pcts = [t[5] for t in trades if t[5] is not None]
    
    # Calculate what % of trades reached various profit levels
    levels = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0]
    
    print()
    print("Profit Level    Trades Reached    % of Total")
    print('-' * 50)
    
    for level in levels:
        reached = len([p for p in profit_pcts if p >= level])
        pct = reached / len(profit_pcts) * 100 if profit_pcts else 0
        print(f'+{level:.1f}%           {reached:<18} {pct:>8.1f}%')
    
    # Statistics
    print()
    print('=' * 50)
    print('PROFIT STATISTICS')
    print('=' * 50)
    
    wins = [p for p in profit_pcts if p > 0]
    losses = [p for p in profit_pcts if p < 0]
    
    print(f'Win Rate: {len(wins)/len(profit_pcts)*100:.1f}%')
    print(f'Max Win: {max(profit_pcts):.2f}%')
    print(f'Max Loss: {min(profit_pcts):.2f}%')
    print(f'Avg P/L: {sum(profit_pcts)/len(profit_pcts):.3f}%')
    
    if wins:
        print(f'Avg Win: +{sum(wins)/len(wins):.3f}%')
    if losses:
        print(f'Avg Loss: {sum(losses)/len(losses):.3f}%')
    
    # OPTIMAL TAKE PROFIT CALCULATION
    print()
    print('=' * 50)
    print('OPTIMAL TAKE PROFIT RECOMMENDATION')
    print('=' * 50)
    
    best_tp = 0
    best_ev = -999
    
    for tp in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        # If we had this take profit, how many would have been wins?
        simulated_wins = len([p for p in profit_pcts if p >= tp])
        simulated_losses = len(profit_pcts) - simulated_wins
        
        win_rate = simulated_wins / len(profit_pcts)
        loss_rate = simulated_losses / len(profit_pcts)
        
        # Assume stop loss at 1.5%
        stop_loss = 1.5
        
        # Costs: ~0.6% for crypto, ~0.1% for stocks, average ~0.35%
        avg_cost = 0.35
        
        # Expected value per trade
        ev = (win_rate * tp) - (loss_rate * stop_loss) - avg_cost
        
        print(f'TP {tp}%: Win Rate={win_rate*100:.1f}%, EV={ev:.3f}%')
        
        if ev > best_ev:
            best_ev = ev
            best_tp = tp
    
    print()
    print(f'>>> RECOMMENDED TAKE PROFIT: {best_tp}%')
    print(f'>>> Expected Value per Trade: {best_ev:.3f}%')
    print()
    print('Justification:')
    print(f'- Based on {len(trades)} historical trades')
    print(f'- Current max win achieved: {max(profit_pcts):.2f}%')
    reached = len([p for p in profit_pcts if p >= best_tp])
    pct = reached / len(profit_pcts) * 100
    print(f'- Trades reaching {best_tp}%: {reached} ({pct:.1f}%)')

    db.close()
    return best_tp, best_ev


if __name__ == '__main__':
    analyze_optimal_take_profit()

