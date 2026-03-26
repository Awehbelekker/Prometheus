#!/usr/bin/env python3
"""
PROMETHEUS Advanced Visualizations System
Real-time performance charts, P&L tracking, and trade analytics
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import os
from dotenv import load_dotenv
import requests

load_dotenv()

class TradingVisualizer:
    """Real-time trading visualization system"""
    
    def __init__(self):
        self.fig = None
        self.axes = None
        self.performance_data = []
        self.trade_history = []
        
        # Alpaca API
        self.alpaca_api_key = os.getenv('ALPACA_API_KEY')
        self.alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
        self.alpaca_base_url = "https://api.alpaca.markets"
        self.alpaca_headers = {
            'APCA-API-KEY-ID': self.alpaca_api_key,
            'APCA-API-SECRET-KEY': self.alpaca_secret
        }
    
    def get_alpaca_portfolio_history(self, period='1D', timeframe='5Min'):
        """Get portfolio history from Alpaca"""
        try:
            response = requests.get(
                f"{self.alpaca_base_url}/v2/account/portfolio/history",
                headers=self.alpaca_headers,
                params={'period': period, 'timeframe': timeframe},
                timeout=10
            )
            return response.json()
        except Exception as e:
            print(f"Error getting portfolio history: {e}")
            return None
    
    def get_alpaca_positions(self):
        """Get current positions"""
        try:
            response = requests.get(
                f"{self.alpaca_base_url}/v2/positions",
                headers=self.alpaca_headers,
                timeout=10
            )
            return response.json()
        except Exception as e:
            print(f"Error getting positions: {e}")
            return []
    
    def create_performance_dashboard(self):
        """Create comprehensive performance dashboard"""
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('🚀 PROMETHEUS Trading Dashboard', fontsize=16, fontweight='bold')
        
        # Create grid
        gs = self.fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Main equity curve (large)
        self.ax_equity = self.fig.add_subplot(gs[0, :])
        self.ax_equity.set_title('Portfolio Equity Curve', fontweight='bold')
        self.ax_equity.set_xlabel('Time')
        self.ax_equity.set_ylabel('Equity ($)')
        self.ax_equity.grid(True, alpha=0.3)
        
        # P&L distribution
        self.ax_pnl = self.fig.add_subplot(gs[1, 0])
        self.ax_pnl.set_title('P&L Distribution', fontweight='bold')
        self.ax_pnl.set_xlabel('P&L ($)')
        self.ax_pnl.set_ylabel('Frequency')
        
        # Win rate pie chart
        self.ax_winrate = self.fig.add_subplot(gs[1, 1])
        self.ax_winrate.set_title('Win/Loss Ratio', fontweight='bold')
        
        # Drawdown
        self.ax_drawdown = self.fig.add_subplot(gs[1, 2])
        self.ax_drawdown.set_title('Drawdown %', fontweight='bold')
        self.ax_drawdown.set_xlabel('Time')
        self.ax_drawdown.set_ylabel('Drawdown %')
        self.ax_drawdown.grid(True, alpha=0.3)
        
        # Position heatmap
        self.ax_positions = self.fig.add_subplot(gs[2, :2])
        self.ax_positions.set_title('Current Positions', fontweight='bold')
        
        # Stats table
        self.ax_stats = self.fig.add_subplot(gs[2, 2])
        self.ax_stats.axis('off')
        self.ax_stats.set_title('Statistics', fontweight='bold')
        
        return self.fig
    
    def update_dashboard(self):
        """Update all dashboard elements"""
        
        # Get latest data
        portfolio_history = self.get_alpaca_portfolio_history()
        positions = self.get_alpaca_positions()
        
        if not portfolio_history:
            print("No portfolio history available")
            return
        
        # Parse equity curve
        timestamps = portfolio_history.get('timestamp', [])
        equity = portfolio_history.get('equity', [])
        
        if not timestamps or not equity:
            print("No data in portfolio history")
            return
        
        # Convert timestamps
        dates = [datetime.fromtimestamp(ts) for ts in timestamps]
        equity_values = equity
        
        # Clear all axes
        self.ax_equity.clear()
        self.ax_pnl.clear()
        self.ax_winrate.clear()
        self.ax_drawdown.clear()
        self.ax_positions.clear()
        self.ax_stats.clear()
        
        # 1. Equity curve
        self.ax_equity.plot(dates, equity_values, linewidth=2, color='#2E7D32', label='Equity')
        self.ax_equity.fill_between(dates, equity_values, alpha=0.3, color='#2E7D32')
        self.ax_equity.set_title('Portfolio Equity Curve', fontweight='bold')
        self.ax_equity.set_xlabel('Time')
        self.ax_equity.set_ylabel('Equity ($)')
        self.ax_equity.grid(True, alpha=0.3)
        self.ax_equity.legend()
        self.ax_equity.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
        # 2. Calculate returns for P&L distribution
        returns = np.diff(equity_values)
        if len(returns) > 0:
            self.ax_pnl.hist(returns, bins=20, color='#1976D2', alpha=0.7, edgecolor='black')
            self.ax_pnl.axvline(x=0, color='red', linestyle='--', linewidth=2)
            self.ax_pnl.set_title('P&L Distribution', fontweight='bold')
            self.ax_pnl.set_xlabel('Return ($)')
            self.ax_pnl.set_ylabel('Frequency')
        
        # 3. Win/Loss ratio
        wins = np.sum(returns > 0)
        losses = np.sum(returns < 0)
        if wins + losses > 0:
            colors = ['#4CAF50', '#F44336']
            labels = [f'Wins ({wins})', f'Losses ({losses})']
            self.ax_winrate.pie([wins, losses], labels=labels, colors=colors, autopct='%1.1f%%',
                               startangle=90)
            self.ax_winrate.set_title('Win/Loss Ratio', fontweight='bold')
        
        # 4. Drawdown
        peak = np.maximum.accumulate(equity_values)
        drawdown = ((equity_values - peak) / peak) * 100
        self.ax_drawdown.plot(dates, drawdown, linewidth=2, color='#D32F2F')
        self.ax_drawdown.fill_between(dates, drawdown, alpha=0.3, color='#D32F2F')
        self.ax_drawdown.set_title('Drawdown %', fontweight='bold')
        self.ax_drawdown.set_xlabel('Time')
        self.ax_drawdown.set_ylabel('Drawdown %')
        self.ax_drawdown.grid(True, alpha=0.3)
        self.ax_drawdown.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
        # 5. Current positions
        if positions:
            symbols = [p.get('symbol', 'N/A') for p in positions]
            pnl = [float(p.get('unrealized_pl', 0)) for p in positions]
            colors_pos = ['#4CAF50' if p >= 0 else '#F44336' for p in pnl]
            
            y_pos = np.arange(len(symbols))
            self.ax_positions.barh(y_pos, pnl, color=colors_pos, alpha=0.7)
            self.ax_positions.set_yticks(y_pos)
            self.ax_positions.set_yticklabels(symbols)
            self.ax_positions.set_xlabel('Unrealized P&L ($)')
            self.ax_positions.set_title('Current Positions P&L', fontweight='bold')
            self.ax_positions.axvline(x=0, color='black', linestyle='-', linewidth=1)
            self.ax_positions.grid(True, alpha=0.3, axis='x')
        else:
            self.ax_positions.text(0.5, 0.5, 'No Open Positions', 
                                  ha='center', va='center', fontsize=12)
        
        # 6. Statistics table
        total_return = equity_values[-1] - equity_values[0]
        total_return_pct = (total_return / equity_values[0]) * 100
        max_dd = np.min(drawdown)
        
        stats_text = [
            f"Starting Equity: ${equity_values[0]:.2f}",
            f"Current Equity:  ${equity_values[-1]:.2f}",
            f"",
            f"Total Return:    ${total_return:.2f}",
            f"Return %:        {total_return_pct:.2f}%",
            f"",
            f"Max Drawdown:    {max_dd:.2f}%",
            f"Win Rate:        {(wins/(wins+losses)*100):.1f}%" if wins+losses > 0 else "Win Rate: N/A",
            f"",
            f"Total Changes:   {len(returns)}",
            f"Wins:            {wins}",
            f"Losses:          {losses}",
        ]
        
        self.ax_stats.text(0.05, 0.95, '\n'.join(stats_text), 
                          transform=self.ax_stats.transAxes,
                          fontsize=10, verticalalignment='top',
                          fontfamily='monospace',
                          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        plt.tight_layout()
    
    def run_live_dashboard(self, update_interval=30):
        """Run live updating dashboard"""
        print("\n" + "="*70)
        print("🚀 PROMETHEUS Live Trading Dashboard")
        print("="*70)
        print(f"Updating every {update_interval} seconds")
        print("Close the window to stop\n")
        
        self.create_performance_dashboard()
        
        def update(frame):
            self.update_dashboard()
            return self.fig,
        
        # Update initially
        self.update_dashboard()
        
        # Animate
        ani = FuncAnimation(self.fig, update, interval=update_interval*1000, blit=False)
        
        plt.show()


def main():
    print("\n" + "="*70)
    print("📈 PROMETHEUS Advanced Visualizations")
    print("="*70)
    print()
    print("Options:")
    print("  1. Live Dashboard (auto-updating)")
    print("  2. Static Performance Report")
    print("  3. Trade Analysis Charts")
    print()
    
    choice = input("Select option (1-3) [1]: ").strip() or "1"
    
    visualizer = TradingVisualizer()
    
    if choice == "1":
        visualizer.run_live_dashboard(update_interval=30)
    elif choice == "2":
        visualizer.create_performance_dashboard()
        visualizer.update_dashboard()
        plt.savefig('trading_performance_report.png', dpi=300, bbox_inches='tight')
        print("✅ Report saved to: trading_performance_report.png")
        plt.show()
    elif choice == "3":
        print("Trade analysis coming soon...")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nVisualization stopped")
