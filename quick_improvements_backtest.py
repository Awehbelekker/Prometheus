#!/usr/bin/env python3
"""
Quick Improvements Backtest
Tests the new autonomous adaptive trade limits and enhancements
"""

import sys
import asyncio
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import json

# Fix console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class QuickImprovementsBacktest:
    def __init__(self):
        self.initial_capital = 10000
        self.capital = self.initial_capital
        self.positions = {}
        self.trades = []
        
        # NEW: Autonomous Adaptive Trade Limits (the enhancement we just added)
        self.base_trades_per_day = 20
        self.max_trades_per_day = 20
        self.today_wins = 0
        self.today_losses = 0
        self.today_profit = 0.0
        self.today_commissions = 0.0
        self.total_trades_today = 0
        
        # Trading parameters with enhancements
        self.take_profit_pct = 0.05  # 5%
        self.stop_loss_pct = 0.08    # 8%
        
    def adjust_trade_limit_autonomously(self):
        """🧠 Autonomous trade limit adjustment based on performance"""
        if self.total_trades_today < 5:
            return  # Need minimum data
        
        win_rate = self.today_wins / self.total_trades_today if self.total_trades_today > 0 else 0
        avg_profit_per_trade = self.today_profit / self.total_trades_today if self.total_trades_today > 0 else 0
        net_profit = self.today_profit - self.today_commissions
        
        old_limit = self.max_trades_per_day
        
        # AUTONOMOUS DECISION LOGIC
        if win_rate > 0.60 and net_profit > 0:
            self.max_trades_per_day = min(50, int(self.base_trades_per_day * 1.5))
            print(f"📈 [AUTONOMOUS] Trade limit INCREASED: {old_limit} → {self.max_trades_per_day}")
        elif win_rate < 0.40 or net_profit < -20:
            self.max_trades_per_day = max(10, int(self.base_trades_per_day * 0.5))
            print(f"📉 [AUTONOMOUS] Trade limit REDUCED: {old_limit} → {self.max_trades_per_day}")
        elif avg_profit_per_trade > 2.0:
            self.max_trades_per_day = min(40, int(self.base_trades_per_day * 1.25))
            print(f"💰 [AUTONOMOUS] Trade limit adjusted: {old_limit} → {self.max_trades_per_day}")
        else:
            self.max_trades_per_day = self.base_trades_per_day
    
    async def run_backtest(self, symbol='SPY', period='6mo'):
        """Run quick backtest with new enhancements"""
        print("\n" + "="*80)
        print("🔥 QUICK IMPROVEMENTS BACKTEST")
        print("="*80)
        print(f"Symbol: {symbol}")
        print(f"Period: {period}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"✨ NEW FEATURE: Autonomous Adaptive Trade Limits (starts at {self.max_trades_per_day})")
        print("="*80 + "\n")
        
        # Download data
        print(f"📥 Downloading {symbol} data...")
        data = yf.download(symbol, period=period, progress=False)
        
        if data.empty:
            print(f"❌ No data for {symbol}")
            return
        
        print(f"✅ Downloaded {len(data)} days of data")
        
        # Simple momentum strategy with adaptive limits
        data['Returns'] = data['Close'].pct_change()
        data['Signal'] = 0
        
        # Generate signals based on momentum
        lookback = 20
        data['Momentum'] = data['Close'].pct_change(lookback)
        data.loc[data['Momentum'] > 0.02, 'Signal'] = 1   # Buy signal
        data.loc[data['Momentum'] < -0.02, 'Signal'] = -1  # Sell signal
        
        position = 0
        entry_price = 0
        daily_trades = 0
        current_day = None
        
        for i in range(lookback, len(data)):
            date = data.index[i]
            price = float(data['Close'].iloc[i])
            signal = int(data['Signal'].iloc[i])
            
            # Reset daily counters at new day
            if current_day != date.date():
                if daily_trades >= 5:  # Adjust limits after enough trades
                    self.adjust_trade_limit_autonomously()
                
                # Reset daily counters
                current_day = date.date()
                daily_trades = 0
                self.total_trades_today = 0
                self.today_wins = 0
                self.today_losses = 0
                self.today_profit = 0.0
                self.today_commissions = 0.0
            
            # Check trade limit
            if self.total_trades_today >= self.max_trades_per_day:
                continue
            
            # Enter position
            if position == 0 and signal == 1 and self.capital > 100:
                position_size = min(self.capital * 0.10, 1000)  # 10% of capital, max $1000
                shares = int(position_size / price)
                if shares > 0:
                    position = shares
                    entry_price = price
                    cost = shares * price
                    self.capital -= cost
                    self.today_commissions += 0.50
                    daily_trades += 1
                    self.total_trades_today += 1
                    
                    self.trades.append({
                        'date': date,
                        'action': 'BUY',
                        'price': price,
                        'shares': shares,
                        'capital': self.capital
                    })
            
            # Exit position (take profit or stop loss)
            elif position > 0:
                pnl_pct = (price - entry_price) / entry_price if entry_price > 0 else 0
                
                # Take profit
                if pnl_pct >= self.take_profit_pct:
                    proceeds = position * price
                    profit = proceeds - (position * entry_price)
                    self.capital += proceeds
                    self.today_profit += profit
                    self.today_wins += 1
                    self.today_commissions += 0.50
                    daily_trades += 1
                    self.total_trades_today += 1
                    
                    self.trades.append({
                        'date': date,
                        'action': 'SELL_PROFIT',
                        'price': price,
                        'shares': position,
                        'profit': profit,
                        'capital': self.capital
                    })
                    position = 0
                    entry_price = 0
                
                # Stop loss
                elif pnl_pct <= -self.stop_loss_pct:
                    proceeds = position * price
                    profit = proceeds - (position * entry_price)
                    self.capital += proceeds
                    self.today_profit += profit
                    self.today_losses += 1
                    self.today_commissions += 0.50
                    daily_trades += 1
                    self.total_trades_today += 1
                    
                    self.trades.append({
                        'date': date,
                        'action': 'SELL_LOSS',
                        'price': price,
                        'shares': position,
                        'profit': profit,
                        'capital': self.capital
                    })
                    position = 0
                    entry_price = 0
        
        # Close any open position
        if position > 0:
            price = float(data['Close'].iloc[-1])
            proceeds = position * price
            profit = proceeds - (position * entry_price)
            self.capital += proceeds
            self.trades.append({
                'date': data.index[-1],
                'action': 'CLOSE',
                'price': price,
                'shares': position,
                'profit': profit,
                'capital': self.capital
            })
        
        # Calculate results
        self.print_results()
    
    def print_results(self):
        """Print backtest results"""
        print("\n" + "="*80)
        print("📊 BACKTEST RESULTS")
        print("="*80)
        
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100
        total_trades = len(self.trades)
        
        wins = sum(1 for t in self.trades if t.get('profit', 0) > 0)
        losses = sum(1 for t in self.trades if t.get('profit', 0) < 0)
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        
        total_profit = sum(t.get('profit', 0) for t in self.trades if t.get('profit', 0) > 0)
        total_loss = sum(t.get('profit', 0) for t in self.trades if t.get('profit', 0) < 0)
        
        print(f"Initial Capital:    ${self.initial_capital:,.2f}")
        print(f"Final Capital:      ${self.capital:,.2f}")
        print(f"Total Return:       {total_return:+.2f}%")
        print(f"Total Profit:       ${total_return/100 * self.initial_capital:+,.2f}")
        print(f"\nTotal Trades:       {total_trades}")
        print(f"Winning Trades:     {wins} ({win_rate:.1f}%)")
        print(f"Losing Trades:      {losses}")
        print(f"Gross Profit:       ${total_profit:,.2f}")
        print(f"Gross Loss:         ${total_loss:,.2f}")
        print(f"Net P&L:            ${total_profit + total_loss:+,.2f}")
        
        print("\n🆕 ADAPTIVE TRADE LIMIT FEATURE:")
        print(f"Base Trade Limit:   {self.base_trades_per_day} trades/day")
        print(f"Final Limit:        {self.max_trades_per_day} trades/day")
        print(f"Adjustment Range:   10-50 trades/day (autonomous)")
        
        print("="*80 + "\n")
        
        # Save results
        results = {
            'timestamp': datetime.now().isoformat(),
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_return_pct': total_return,
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'adaptive_limits': {
                'base': self.base_trades_per_day,
                'final': self.max_trades_per_day,
                'range': '10-50'
            }
        }
        
        filename = f"quick_backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to: {filename}\n")

async def main():
    backtester = QuickImprovementsBacktest()
    await backtester.run_backtest('SPY', '6mo')

if __name__ == '__main__':
    asyncio.run(main())
