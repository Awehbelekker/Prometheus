#!/usr/bin/env python3
"""
🚀 PROMETHEUS INTRADAY BACKTESTING SYSTEM
Uses hourly data for more accurate simulation of intraday stop-loss/take-profit triggers.

Features:
- Downloads hourly data (1h interval) from Yahoo Finance
- More accurate simulation of entry/exit timing
- Comparison with actual trading performance
- Detailed report generation
"""

import asyncio
import argparse
import logging
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json
import sqlite3
import warnings
warnings.filterwarnings('ignore')

# Configure logging
import sys
log_file = f'backtest_intraday_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])
logger = logging.getLogger(__name__)

@dataclass
class IntradayBacktestResult:
    """Results from intraday backtest"""
    total_return: float = 0
    win_rate: float = 0
    sharpe_ratio: float = 0
    max_drawdown: float = 0
    profit_factor: float = 0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    avg_trade_duration_hours: float = 0
    benchmark_return: float = 0  # SPY return for comparison

class PrometheusIntradayBacktester:
    """Intraday backtester using hourly data"""
    
    def __init__(self, initial_capital: float = 100000, stop_loss_pct: float = 0.03,
                 take_profit_pct: float = 0.08, position_size_pct: float = 0.10):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.position_size_pct = position_size_pct
        
        self.positions = {}
        self.trades = []
        self.portfolio_history = [initial_capital]
        self.hourly_returns = []
        
        logger.info(f"Intraday Backtester initialized")
        logger.info(f"  Capital: ${initial_capital:,.2f}, SL: {stop_loss_pct*100}%, TP: {take_profit_pct*100}%")

    async def download_hourly_data(self, symbols: List[str], days: int = 30) -> Dict[str, pd.DataFrame]:
        """Download hourly data from Yahoo Finance"""
        logger.info(f"Downloading {days} days of hourly data for {len(symbols)} symbols...")
        
        # Yahoo Finance limits: 1h data available for max 730 days
        period = f"{min(days, 60)}d"  # 1h data has limited history
        data = {}
        
        for symbol in symbols:
            try:
                yf_symbol = symbol
                if symbol.endswith('USD') and not symbol.endswith('-USD'):
                    yf_symbol = f"{symbol[:-3]}-USD"
                
                ticker = yf.Ticker(yf_symbol)
                df = ticker.history(period=period, interval='1h')
                
                if not df.empty:
                    df = self._add_indicators(df)
                    data[symbol] = df
                    logger.info(f"  {symbol}: {len(df)} hourly bars")
                else:
                    logger.warning(f"  {symbol}: No hourly data")
            except Exception as e:
                logger.error(f"  {symbol}: Download failed - {e}")
        
        return data
    
    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators"""
        try:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['EMA_12'] = df['Close'].ewm(span=12).mean()
            df['EMA_26'] = df['Close'].ewm(span=26).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Volatility'] = df['Close'].pct_change().rolling(window=20).std()
        except Exception as e:
            logger.warning(f"Indicator calculation failed: {e}")
        return df

    def _get_signal(self, row: pd.Series) -> tuple:
        """Simple signal based on technical indicators"""
        rsi = row.get('RSI', 50)
        macd = row.get('MACD', 0)
        price = row['Close']
        sma = row.get('SMA_20', price)

        # Signal logic
        if rsi < 35 and price > sma and macd > 0:
            return 'BUY', min(0.8, 0.5 + (35 - rsi) / 50)
        elif rsi > 65 and price < sma and macd < 0:
            return 'SELL', min(0.8, 0.5 + (rsi - 65) / 50)
        return 'HOLD', 0.5

    async def run_backtest(self, data: Dict[str, pd.DataFrame]) -> IntradayBacktestResult:
        """Run the intraday backtest"""
        logger.info("Running intraday backtest...")

        # Get the shortest common timeframe
        min_len = min(len(df) for df in data.values()) if data else 0
        if min_len < 50:
            logger.error("Insufficient data for backtest")
            return IntradayBacktestResult()

        # Track benchmark
        spy_data = data.get('SPY')
        if spy_data is not None and len(spy_data) > 0:
            benchmark_start = float(spy_data['Close'].iloc[0])
            benchmark_end = float(spy_data['Close'].iloc[-1])
            benchmark_return = (benchmark_end - benchmark_start) / benchmark_start * 100
        else:
            benchmark_return = 0

        all_trades = []
        for symbol, df in data.items():
            if symbol == 'SPY':
                continue  # Skip benchmark

            for i in range(50, len(df)):
                row = df.iloc[i]
                price = float(row['Close'])
                timestamp = df.index[i]

                # Check existing position
                if symbol in self.positions:
                    pos = self.positions[symbol]
                    pnl_pct = (price - pos['entry_price']) / pos['entry_price']

                    # Check exit conditions
                    if pnl_pct >= self.take_profit_pct:
                        # Take profit
                        pnl = pos['quantity'] * pos['entry_price'] * pnl_pct
                        self.current_capital += pos['quantity'] * price
                        all_trades.append({'pnl': pnl, 'pnl_pct': pnl_pct, 'duration': (timestamp - pos['entry_time']).total_seconds() / 3600})
                        del self.positions[symbol]
                    elif pnl_pct <= -self.stop_loss_pct:
                        # Stop loss
                        pnl = pos['quantity'] * pos['entry_price'] * pnl_pct
                        self.current_capital += pos['quantity'] * price
                        all_trades.append({'pnl': pnl, 'pnl_pct': pnl_pct, 'duration': (timestamp - pos['entry_time']).total_seconds() / 3600})
                        del self.positions[symbol]
                else:
                    # Check for entry
                    signal, confidence = self._get_signal(row)
                    if signal == 'BUY' and confidence > 0.55:
                        position_value = self.current_capital * self.position_size_pct
                        quantity = position_value / price
                        self.current_capital -= position_value
                        self.positions[symbol] = {
                            'entry_price': price,
                            'quantity': quantity,
                            'entry_time': timestamp
                        }

                self.portfolio_history.append(self.current_capital + sum(
                    pos['quantity'] * price for pos in self.positions.values()
                ))

        # Close remaining positions
        for symbol, pos in list(self.positions.items()):
            if symbol in data:
                final_price = float(data[symbol]['Close'].iloc[-1])
                pnl_pct = (final_price - pos['entry_price']) / pos['entry_price']
                pnl = pos['quantity'] * pos['entry_price'] * pnl_pct
                all_trades.append({'pnl': pnl, 'pnl_pct': pnl_pct, 'duration': 24})
                self.current_capital += pos['quantity'] * final_price
        self.positions.clear()

        # Calculate metrics
        total_return = (self.current_capital - self.initial_capital) / self.initial_capital * 100
        winning = [t for t in all_trades if t['pnl'] > 0]
        losing = [t for t in all_trades if t['pnl'] < 0]

        gross_profit = sum(t['pnl'] for t in winning)
        gross_loss = abs(sum(t['pnl'] for t in losing))

        # Calculate drawdown
        peak = self.initial_capital
        max_dd = 0
        for val in self.portfolio_history:
            if val > peak:
                peak = val
            dd = (peak - val) / peak
            max_dd = max(max_dd, dd)

        # Sharpe ratio
        returns = pd.Series(self.portfolio_history).pct_change().dropna()
        sharpe = (returns.mean() / returns.std() * np.sqrt(252 * 6.5)) if returns.std() > 0 else 0

        result = IntradayBacktestResult(
            total_return=total_return,
            win_rate=len(winning) / len(all_trades) * 100 if all_trades else 0,
            sharpe_ratio=float(sharpe),
            max_drawdown=max_dd * 100,
            profit_factor=gross_profit / gross_loss if gross_loss > 0 else float('inf'),
            total_trades=len(all_trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
            avg_trade_duration_hours=sum(t['duration'] for t in all_trades) / len(all_trades) if all_trades else 0,
            benchmark_return=benchmark_return
        )

        return result


def get_actual_trading_performance() -> Dict[str, Any]:
    """Get actual trading performance from database"""
    try:
        conn = sqlite3.connect('prometheus_learning.db')
        c = conn.cursor()

        c.execute('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losses,
                SUM(profit_loss) as total_pnl,
                AVG(profit_loss) as avg_pnl
            FROM trade_history
            WHERE profit_loss IS NOT NULL AND profit_loss != 0
        ''')
        row = c.fetchone()

        if row and row[0] and row[0] > 0:
            return {
                'total_trades': row[0],
                'winning_trades': row[1] or 0,
                'losing_trades': row[2] or 0,
                'win_rate': (row[1] or 0) / row[0] * 100,
                'total_pnl': row[3] or 0,
                'avg_pnl': row[4] or 0,
                'has_data': True
            }
        conn.close()
    except Exception as e:
        logger.warning(f"Could not get trading history: {e}")

    return {'has_data': False, 'total_trades': 0}


def generate_comparison_report(backtest: IntradayBacktestResult, actual: Dict) -> str:
    """Generate a comparison report"""
    report = []
    report.append("=" * 70)
    report.append("PROMETHEUS BACKTEST VS ACTUAL TRADING COMPARISON REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 70)

    report.append("\n--- INTRADAY BACKTEST RESULTS (Hourly Data) ---")
    report.append(f"Total Return:        {backtest.total_return:>10.2f}%")
    report.append(f"Benchmark (SPY):     {backtest.benchmark_return:>10.2f}%")
    report.append(f"Alpha vs Benchmark:  {backtest.total_return - backtest.benchmark_return:>10.2f}%")
    report.append(f"Win Rate:            {backtest.win_rate:>10.1f}%")
    report.append(f"Sharpe Ratio:        {backtest.sharpe_ratio:>10.2f}")
    report.append(f"Max Drawdown:        {backtest.max_drawdown:>10.1f}%")
    report.append(f"Profit Factor:       {backtest.profit_factor:>10.2f}")
    report.append(f"Total Trades:        {backtest.total_trades:>10}")
    report.append(f"Winning Trades:      {backtest.winning_trades:>10}")
    report.append(f"Losing Trades:       {backtest.losing_trades:>10}")
    report.append(f"Avg Duration (hrs):  {backtest.avg_trade_duration_hours:>10.1f}")

    if actual.get('has_data'):
        report.append("\n--- ACTUAL TRADING PERFORMANCE ---")
        report.append(f"Total Trades:        {actual['total_trades']:>10}")
        report.append(f"Winning Trades:      {actual['winning_trades']:>10}")
        report.append(f"Losing Trades:       {actual['losing_trades']:>10}")
        report.append(f"Win Rate:            {actual['win_rate']:>10.1f}%")
        report.append(f"Total P/L:           ${actual['total_pnl']:>9.2f}")
        report.append(f"Avg P/L per Trade:   ${actual['avg_pnl']:>9.2f}")
    else:
        report.append("\n--- ACTUAL TRADING PERFORMANCE ---")
        report.append("No completed trades with P/L data recorded yet.")
        report.append("P/L will be recorded when positions are closed.")

    report.append("\n--- TARGETS ---")
    report.append(f"Win Rate Target:     {'PASS' if backtest.win_rate >= 55 else 'FAIL'} (55%+ required, got {backtest.win_rate:.1f}%)")
    report.append(f"Sharpe Target:       {'PASS' if backtest.sharpe_ratio >= 2.0 else 'FAIL'} (2.0+ required, got {backtest.sharpe_ratio:.2f})")
    report.append(f"Max Drawdown Target: {'PASS' if backtest.max_drawdown <= 15 else 'FAIL'} (<15% required, got {backtest.max_drawdown:.1f}%)")
    report.append(f"Profit Factor Target:{'PASS' if backtest.profit_factor >= 1.5 else 'FAIL'} (1.5+ required, got {backtest.profit_factor:.2f})")

    report.append("=" * 70)
    return "\n".join(report)


async def main():
    parser = argparse.ArgumentParser(description='PROMETHEUS Intraday Backtest')
    parser.add_argument('--days', type=int, default=30, help='Days of hourly data')
    parser.add_argument('--symbols', type=str, default='SPY,QQQ,AAPL,MSFT,NVDA,GOOGL,AMZN,META',
                       help='Comma-separated symbols')
    parser.add_argument('--capital', type=float, default=100000, help='Initial capital')
    parser.add_argument('--sl', type=float, default=0.03, help='Stop loss percentage')
    parser.add_argument('--tp', type=float, default=0.08, help='Take profit percentage')
    args = parser.parse_args()

    symbols = [s.strip() for s in args.symbols.split(',')]

    backtester = PrometheusIntradayBacktester(
        initial_capital=args.capital,
        stop_loss_pct=args.sl,
        take_profit_pct=args.tp
    )

    # Download hourly data
    data = await backtester.download_hourly_data(symbols, args.days)

    if not data:
        logger.error("No data downloaded. Exiting.")
        return

    # Run backtest
    result = await backtester.run_backtest(data)

    # Get actual performance
    actual = get_actual_trading_performance()

    # Generate report
    report = generate_comparison_report(result, actual)
    print(report)

    # Save report
    report_file = f'comparison_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    logger.info(f"Report saved to: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())

