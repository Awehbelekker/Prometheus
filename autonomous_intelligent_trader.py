#!/usr/bin/env python
"""
PROMETHEUS Autonomous Intelligent Trader
==========================================
Smart trading system that analyzes market conditions to maximize profits.

Features:
- Real-time market data analysis
- Technical indicators (RSI, MACD, Moving Averages)
- Smart entry/exit decisions based on momentum
- Dynamic profit targets based on trend strength
- Volatility-adjusted stop-losses
"""
import time
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv

load_dotenv()

# Try to import yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("[WARNING] yfinance not available - using Alpaca data only")

# Configuration
CHECK_INTERVAL = 60  # Check every 60 seconds
WATCHLIST = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'SPY', 'QQQ']

# Trading Parameters
BASE_PROFIT_TARGET = 0.5  # Base 0.5% profit target
MAX_PROFIT_TARGET = 8.0   # Max 8% for strong trends
STOP_LOSS = -3.0          # -3% stop loss
MIN_POSITION_SIZE = 5.0   # Minimum $5 position
MAX_POSITION_PCT = 0.15   # Max 15% of portfolio per position

class IntelligentTrader:
    """Intelligent autonomous trading engine"""
    
    def __init__(self):
        self.client = TradingClient(
            os.getenv('ALPACA_API_KEY'),
            os.getenv('ALPACA_SECRET_KEY'),
            paper=False
        )
        self.trade_log = []
        
    def get_market_data(self, symbol: str, period: str = "5d") -> Optional[pd.DataFrame]:
        """Get historical market data for analysis"""
        if not YFINANCE_AVAILABLE:
            return None
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval="1h")
            if df.empty:
                df = ticker.history(period=period, interval="1d")
            return df if not df.empty else None
        except Exception as e:
            print(f"[ERROR] Failed to get data for {symbol}: {e}")
            return None
    
    def calculate_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate technical indicators"""
        if df is None or len(df) < 20:
            return {}
        
        indicators = {}
        close = df['Close']
        
        # RSI (14-period)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['rsi'] = float(100 - (100 / (1 + rs.iloc[-1]))) if not pd.isna(rs.iloc[-1]) else 50
        
        # Moving Averages
        indicators['sma_20'] = float(close.rolling(20).mean().iloc[-1])
        indicators['sma_50'] = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else indicators['sma_20']
        indicators['ema_12'] = float(close.ewm(span=12).mean().iloc[-1])
        indicators['ema_26'] = float(close.ewm(span=26).mean().iloc[-1])
        
        # MACD
        indicators['macd'] = indicators['ema_12'] - indicators['ema_26']
        indicators['macd_signal'] = float(close.ewm(span=12).mean().ewm(span=9).mean().iloc[-1])
        
        # Trend strength (price vs SMAs)
        current_price = float(close.iloc[-1])
        indicators['price'] = current_price
        indicators['above_sma20'] = current_price > indicators['sma_20']
        indicators['above_sma50'] = current_price > indicators['sma_50']
        
        # Momentum (price change %)
        if len(close) >= 5:
            indicators['momentum_5d'] = float((current_price / close.iloc[-5] - 1) * 100)
        else:
            indicators['momentum_5d'] = 0
            
        # Volatility (ATR-like)
        high_low = df['High'] - df['Low']
        indicators['volatility'] = float(high_low.rolling(14).mean().iloc[-1] / current_price * 100)
        
        return indicators
    
    def analyze_opportunity(self, symbol: str, indicators: Dict) -> Dict:
        """Analyze if symbol presents a trading opportunity"""
        if not indicators:
            return {'action': 'HOLD', 'score': 0, 'reason': 'No data'}
        
        score = 0
        reasons = []
        
        # RSI analysis
        rsi = indicators.get('rsi', 50)
        if rsi < 30:
            score += 2
            reasons.append(f"RSI oversold ({rsi:.1f})")
        elif rsi < 40:
            score += 1
            reasons.append(f"RSI low ({rsi:.1f})")
        elif rsi > 70:
            score -= 2
            reasons.append(f"RSI overbought ({rsi:.1f})")
        
        # Trend analysis
        if indicators.get('above_sma20') and indicators.get('above_sma50'):
            score += 2
            reasons.append("Strong uptrend (above SMAs)")
        elif indicators.get('above_sma20'):
            score += 1
            reasons.append("Moderate uptrend")
        
        # MACD
        if indicators.get('macd', 0) > indicators.get('macd_signal', 0):
            score += 1
            reasons.append("MACD bullish")
        
        # Momentum
        momentum = indicators.get('momentum_5d', 0)
        if momentum > 3:
            score += 1
            reasons.append(f"Strong momentum (+{momentum:.1f}%)")
        elif momentum < -3:
            score -= 1
            reasons.append(f"Weak momentum ({momentum:.1f}%)")
        
        # Determine action
        if score >= 3:
            return {'action': 'BUY', 'score': score, 'reason': ', '.join(reasons), 'indicators': indicators}
        elif score <= -2:
            return {'action': 'SELL', 'score': score, 'reason': ', '.join(reasons), 'indicators': indicators}
        return {'action': 'HOLD', 'score': score, 'reason': ', '.join(reasons) or 'Neutral', 'indicators': indicators}

    def get_dynamic_profit_target(self, indicators: Dict) -> float:
        """Calculate dynamic profit target based on trend strength"""
        base = BASE_PROFIT_TARGET

        # Increase target for strong trends
        if indicators.get('above_sma20') and indicators.get('above_sma50'):
            base += 1.5  # +1.5% for strong uptrend

        momentum = indicators.get('momentum_5d', 0)
        if momentum > 5:
            base += 2.0  # +2% for strong momentum
        elif momentum > 2:
            base += 1.0  # +1% for moderate momentum

        rsi = indicators.get('rsi', 50)
        if 40 < rsi < 60:
            base += 0.5  # +0.5% for neutral RSI (room to run)

        return min(base, MAX_PROFIT_TARGET)

    def should_sell_position(self, symbol: str, entry_price: float, current_price: float,
                            indicators: Dict) -> Tuple[bool, str]:
        """Smart exit decision based on market conditions"""
        pnl_pct = (current_price / entry_price - 1) * 100

        # Dynamic profit target
        profit_target = self.get_dynamic_profit_target(indicators)

        # Check stop-loss (always honor this)
        if pnl_pct <= STOP_LOSS:
            return True, f"STOP-LOSS ({pnl_pct:.2f}% <= {STOP_LOSS}%)"

        # Check profit target
        if pnl_pct >= profit_target:
            # But wait - is momentum still strong?
            momentum = indicators.get('momentum_5d', 0)
            rsi = indicators.get('rsi', 50)

            # Let winners run if momentum is very strong and RSI not overbought
            if momentum > 5 and rsi < 65 and pnl_pct < MAX_PROFIT_TARGET:
                return False, f"Letting profits run (momentum={momentum:.1f}%, RSI={rsi:.0f})"

            return True, f"TAKE-PROFIT ({pnl_pct:.2f}% >= {profit_target:.1f}% target)"

        # Trailing stop check (if in profit and momentum weakening)
        if pnl_pct > 2.0:  # If we have 2%+ profit
            momentum = indicators.get('momentum_5d', 0)
            if momentum < -1:  # Momentum turning negative
                return True, f"TRAILING-STOP (momentum weakening: {momentum:.1f}%)"

        return False, f"HOLD ({pnl_pct:.2f}%, target={profit_target:.1f}%)"

    def get_account_info(self) -> Dict:
        """Get current account status"""
        account = self.client.get_account()
        return {
            'cash': float(account.cash),
            'buying_power': float(account.buying_power),
            'portfolio_value': float(account.portfolio_value),
            'daytrade_count': account.daytrade_count
        }

    def get_positions(self) -> List[Dict]:
        """Get all current positions"""
        positions = self.client.get_all_positions()
        return [{
            'symbol': p.symbol,
            'qty': float(p.qty),
            'entry_price': float(p.avg_entry_price),
            'current_price': float(p.current_price),
            'market_value': float(p.market_value),
            'pnl_pct': float(p.unrealized_plpc) * 100,
            'pnl_usd': float(p.unrealized_pl)
        } for p in positions]

    def execute_buy(self, symbol: str, amount_usd: float) -> bool:
        """Execute a buy order"""
        try:
            # Get current price
            df = self.get_market_data(symbol, "1d")
            if df is None or df.empty:
                return False

            current_price = float(df['Close'].iloc[-1])
            qty = round(amount_usd / current_price, 4)

            if qty * current_price < MIN_POSITION_SIZE:
                print(f"[SKIP] {symbol}: Position too small (${qty * current_price:.2f})")
                return False

            order = self.client.submit_order(MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC
            ))
            print(f"[BUY] {symbol}: {qty} shares @ ~${current_price:.2f} = ${qty*current_price:.2f}")
            self.trade_log.append({'time': datetime.now(), 'action': 'BUY', 'symbol': symbol, 'qty': qty})
            return True
        except Exception as e:
            print(f"[ERROR] Buy failed for {symbol}: {e}")
            return False

    def execute_sell(self, symbol: str, qty: float) -> bool:
        """Execute a sell order"""
        try:
            order = self.client.submit_order(MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.GTC
            ))
            print(f"[SELL] {symbol}: {qty} shares")
            self.trade_log.append({'time': datetime.now(), 'action': 'SELL', 'symbol': symbol, 'qty': qty})
            return True
        except Exception as e:
            print(f"[ERROR] Sell failed for {symbol}: {e}")
            return False

    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        print(f"\n{'='*70}")
        print(f"PROMETHEUS INTELLIGENT TRADER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")

        # Get account info
        account = self.get_account_info()
        print(f"Cash: ${account['cash']:.2f} | Buying Power: ${account['buying_power']:.2f}")
        print(f"Portfolio: ${account['portfolio_value']:.2f} | Day Trades: {account['daytrade_count']}/3")

        # STEP 1: Check existing positions for exit opportunities
        print(f"\n--- POSITION ANALYSIS ---")
        positions = self.get_positions()

        for pos in positions:
            symbol = pos['symbol']

            # Skip stablecoins
            if symbol in ['USDCUSD', 'USDTUSD']:
                continue

            # Get fresh market data and indicators
            df = self.get_market_data(symbol)
            indicators = self.calculate_indicators(df) if df is not None else {}

            # Smart exit decision
            should_sell, reason = self.should_sell_position(
                symbol, pos['entry_price'], pos['current_price'], indicators
            )

            status = "SELL!" if should_sell else "HOLD"
            pnl_emoji = "+" if pos['pnl_pct'] >= 0 else ""
            print(f"  {symbol}: {pnl_emoji}{pos['pnl_pct']:.2f}% (${pos['pnl_usd']:.2f}) -> {status} | {reason}")

            if should_sell and pos['qty'] > 0:
                self.execute_sell(symbol, pos['qty'])

        # STEP 2: Look for buy opportunities (if we have buying power)
        if account['buying_power'] > MIN_POSITION_SIZE * 2:
            print(f"\n--- OPPORTUNITY SCAN ---")
            opportunities = []

            for symbol in WATCHLIST:
                # Skip if already holding
                if any(p['symbol'] == symbol for p in positions):
                    continue

                df = self.get_market_data(symbol)
                indicators = self.calculate_indicators(df)
                analysis = self.analyze_opportunity(symbol, indicators)

                if analysis['action'] == 'BUY':
                    opportunities.append((symbol, analysis))
                    print(f"  🎯 {symbol}: BUY (score={analysis['score']}) - {analysis['reason']}")
                else:
                    print(f"  · {symbol}: {analysis['action']} (score={analysis['score']})")

            # Execute best opportunity
            if opportunities:
                opportunities.sort(key=lambda x: x[1]['score'], reverse=True)
                best_symbol, best_analysis = opportunities[0]

                # Calculate position size (max 15% of portfolio or available cash)
                position_size = min(
                    account['buying_power'] * 0.5,  # Use 50% of available
                    account['portfolio_value'] * MAX_POSITION_PCT
                )

                if position_size >= MIN_POSITION_SIZE:
                    print(f"\n>>> EXECUTING: BUY {best_symbol} for ${position_size:.2f}")
                    self.execute_buy(best_symbol, position_size)
        else:
            print(f"\n[INFO] Low buying power (${account['buying_power']:.2f}) - waiting for exits")

        print(f"\n{'='*70}")


def main():
    print("\n" + "="*70)
    print("  PROMETHEUS AUTONOMOUS INTELLIGENT TRADER")
    print("  Smart trading with technical analysis")
    print("="*70)
    print(f"  Watchlist: {', '.join(WATCHLIST)}")
    print(f"  Base Profit Target: {BASE_PROFIT_TARGET}% (dynamic up to {MAX_PROFIT_TARGET}%)")
    print(f"  Stop Loss: {STOP_LOSS}%")
    print(f"  Check Interval: {CHECK_INTERVAL} seconds")
    print("="*70)

    trader = IntelligentTrader()

    while True:
        try:
            trader.run_trading_cycle()
            print(f"\nNext cycle in {CHECK_INTERVAL} seconds... (Ctrl+C to stop)")
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\n\nTrader stopped by user.")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")
            print(f"Retrying in {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()

