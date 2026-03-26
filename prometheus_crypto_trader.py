#!/usr/bin/env python3
"""
PROMETHEUS Crypto Trading - 24/7 Alpaca Crypto Trader
Bypasses stock market hours - trades crypto around the clock

NOW WITH ADAPTIVE CONFIDENCE THRESHOLDS!
- Learns from wins/losses per asset
- Adjusts thresholds dynamically
- Drawdown protection
"""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add project root
sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

import yfinance as yf

try:
    import alpaca_trade_api as tradeapi
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    print("⚠️ alpaca-trade-api not installed")

# AI Brain Integration
try:
    from core.ai_trading_intelligence import AITradingIntelligence
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# ADAPTIVE RISK MANAGEMENT - Dynamic confidence thresholds
try:
    from core.adaptive_risk_manager import (
        get_risk_manager, 
        get_confidence_threshold,
        record_trade,
        should_pause_trading
    )
    ADAPTIVE_RISK_AVAILABLE = True
except ImportError:
    ADAPTIVE_RISK_AVAILABLE = False
    print("⚠️ Adaptive risk manager not available - using static thresholds")

class PrometheusCryptoTrader:
    """24/7 Crypto Trading with AI Analysis and ADAPTIVE Risk Management"""
    
    def __init__(self):
        self.api = None
        self.ai_brain = None
        self.risk_manager = None
        self.crypto_watchlist = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'DOGE/USD', 'AVAX/USD']
        self.base_confidence = 0.55  # Starting point - will be adjusted per asset
        self.max_position_pct = 0.25  # Max 25% of portfolio per position
        self.session_trades = 0
        self.session_profit = 0.0
        self.entry_prices = {}  # Track entry prices for P/L calculation
        
    async def initialize(self):
        """Initialize Alpaca connection, AI brain, and Adaptive Risk Manager"""
        print("\n" + "=" * 60)
        print("🚀 PROMETHEUS CRYPTO TRADER - 24/7 Mode")
        print("   with ADAPTIVE CONFIDENCE THRESHOLDS")
        print("=" * 60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not ALPACA_AVAILABLE:
            raise Exception("Alpaca API required for crypto trading")
        
        # Connect to Alpaca LIVE
        api_key = os.getenv('ALPACA_API_KEY')
        secret_key = os.getenv('ALPACA_SECRET_KEY')
        
        if not api_key or not secret_key:
            raise Exception("ALPACA_API_KEY and ALPACA_SECRET_KEY required in .env")
        
        self.api = tradeapi.REST(api_key, secret_key, 'https://api.alpaca.markets')
        
        # Verify connection
        account = self.api.get_account()
        print(f"\n💰 Account: {account.account_number}")
        print(f"   Equity: ${float(account.equity):,.2f}")
        print(f"   Cash: ${float(account.cash):,.2f}")
        print(f"   Buying Power: ${float(account.buying_power):,.2f}")
        
        # Initialize AI Brain
        if AI_AVAILABLE:
            try:
                self.ai_brain = AITradingIntelligence()
                print("\n🧠 AI Brain: ACTIVE ✅")
            except Exception as e:
                print(f"\n🧠 AI Brain: Fallback mode ({e})")
        else:
            print("\n🧠 AI Brain: Using technical analysis")
        
        # Initialize Adaptive Risk Manager
        if ADAPTIVE_RISK_AVAILABLE:
            self.risk_manager = get_risk_manager()
            status = self.risk_manager.get_status()
            print(f"\n🎯 Adaptive Risk Manager: ACTIVE ✅")
            print(f"   Historical trades: {status['total_trades_all_time']}")
            print(f"   Overall win rate: {status['overall_win_rate']:.0%}")
            print(f"   Assets tracked: {status['assets_tracked']}")
        else:
            print("\n🎯 Adaptive Risk: Using static thresholds")
        
        # Show adaptive thresholds per asset
        print(f"\n📊 Watching with ADAPTIVE thresholds:")
        for sym in self.crypto_watchlist:
            threshold = self._get_threshold(sym)
            print(f"   {sym}: {threshold:.0%}")
        print("=" * 60 + "\n")
    
    def _get_threshold(self, symbol: str, volatility: float = 1.0) -> float:
        """Get adaptive confidence threshold for a symbol"""
        if ADAPTIVE_RISK_AVAILABLE and self.risk_manager:
            return get_confidence_threshold(symbol, 'crypto', volatility)
        return self.base_confidence
    
    def _record_trade_result(self, symbol: str, action: str, entry: float, 
                              exit_price: float, qty: float, confidence: float):
        """Record trade result for learning"""
        if ADAPTIVE_RISK_AVAILABLE:
            record_trade(symbol, 'crypto', action, entry, exit_price, qty, confidence)
        
    async def analyze_crypto(self, symbol: str) -> dict:
        """Analyze a crypto asset using AI and technicals"""
        try:
            # Convert symbol for yfinance (BTC/USD -> BTC-USD)
            yf_symbol = symbol.replace('/', '-')
            
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period='5d', interval='15m')
            
            if hist.empty:
                return {'action': 'HOLD', 'confidence': 0, 'reason': 'No data'}
            
            current_price = float(hist['Close'].iloc[-1])
            
            # Calculate technical indicators
            closes = hist['Close'].values
            
            # RSI
            if len(closes) > 14:
                deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
                gains = [d if d > 0 else 0 for d in deltas[-14:]]
                losses = [-d if d < 0 else 0 for d in deltas[-14:]]
                avg_gain = sum(gains) / 14
                avg_loss = sum(losses) / 14
                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
            else:
                rsi = 50
            
            # Momentum (4-hour change)
            if len(closes) > 16:
                momentum = (closes[-1] - closes[-16]) / closes[-16] * 100
            else:
                momentum = 0
            
            # Volume spike
            volumes = hist['Volume'].values
            if len(volumes) > 20:
                avg_vol = volumes[-20:-1].mean()
                current_vol = volumes[-1]
                vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1
            else:
                vol_ratio = 1
            
            # AI Analysis if available
            ai_signal = None
            if self.ai_brain:
                try:
                    ai_signal = await asyncio.to_thread(
                        self.ai_brain.analyze_symbol,
                        symbol.replace('/', ''),
                        {'price': current_price, 'rsi': rsi, 'momentum': momentum}
                    )
                except Exception as e:
                    print(f"   AI analysis error: {e}")
            
            # Decision logic
            action = 'HOLD'
            confidence = 0.5
            reason = ""
            
            # Strong BUY signals
            if rsi < 30 and momentum < -5:
                action = 'BUY'
                confidence = 0.80
                reason = f"Oversold (RSI={rsi:.1f}) with negative momentum - reversal likely"
            elif rsi < 35 and vol_ratio > 1.5:
                action = 'BUY'
                confidence = 0.75
                reason = f"Near oversold (RSI={rsi:.1f}) with volume spike ({vol_ratio:.1f}x)"
            
            # Strong SELL signals
            elif rsi > 70 and momentum > 5:
                action = 'SELL'
                confidence = 0.80
                reason = f"Overbought (RSI={rsi:.1f}) with high momentum - correction likely"
            elif rsi > 65 and vol_ratio > 2.0:
                action = 'SELL'
                confidence = 0.75
                reason = f"Near overbought (RSI={rsi:.1f}) with volume spike ({vol_ratio:.1f}x)"
            
            # Trend following
            elif momentum > 3 and rsi < 60:
                action = 'BUY'
                confidence = 0.70
                reason = f"Uptrend momentum ({momentum:.1f}%) with room to run"
            elif momentum < -3 and rsi > 40:
                action = 'SELL'
                confidence = 0.70
                reason = f"Downtrend momentum ({momentum:.1f}%) - cutting losses"
            
            # Override with AI if available and confident
            if ai_signal and ai_signal.get('confidence', 0) > confidence:
                action = ai_signal.get('action', action)
                confidence = ai_signal.get('confidence', confidence)
                reason = ai_signal.get('reason', reason) + " [AI]"
            
            return {
                'symbol': symbol,
                'action': action,
                'confidence': confidence,
                'reason': reason,
                'price': current_price,
                'rsi': rsi,
                'momentum': momentum,
                'volume_ratio': vol_ratio
            }
            
        except Exception as e:
            return {'action': 'HOLD', 'confidence': 0, 'reason': f'Error: {e}'}
    
    async def execute_trade(self, signal: dict):
        """Execute a crypto trade on Alpaca"""
        try:
            symbol = signal['symbol']
            action = signal['action']
            price = signal['price']
            
            # Get current account state
            account = self.api.get_account()
            buying_power = float(account.buying_power)
            equity = float(account.equity)
            
            # Calculate position size (max 20% of equity)
            max_position = equity * self.max_position_pct
            position_size = min(max_position, buying_power * 0.95)  # Keep 5% reserve
            
            if position_size < 10:  # Minimum $10 trade
                print(f"   ⚠️ Insufficient funds for {symbol} (need $10, have ${position_size:.2f})")
                return
            
            # Check existing position
            try:
                position = self.api.get_position(symbol.replace('/', ''))
                current_qty = float(position.qty)
            except:
                current_qty = 0
            
            if action == 'BUY' and current_qty == 0:
                # Calculate quantity
                qty = position_size / price
                qty = round(qty, 6)  # Crypto allows 6 decimal places
                
                if qty * price >= 1:  # Minimum $1 order
                    print(f"\n   📈 BUYING {symbol}")
                    print(f"      Qty: {qty:.6f}")
                    print(f"      Price: ${price:,.2f}")
                    print(f"      Value: ${qty * price:,.2f}")
                    print(f"      Reason: {signal['reason']}")
                    
                    order = self.api.submit_order(
                        symbol=symbol.replace('/', ''),
                        qty=qty,
                        side='buy',
                        type='market',
                        time_in_force='gtc'
                    )
                    print(f"      ✅ Order submitted: {order.id}")
                    self.session_trades += 1
                    
            elif action == 'SELL' and current_qty > 0:
                print(f"\n   📉 SELLING {symbol}")
                print(f"      Qty: {current_qty}")
                print(f"      Price: ${price:,.2f}")
                print(f"      Reason: {signal['reason']}")
                
                order = self.api.submit_order(
                    symbol=symbol.replace('/', ''),
                    qty=current_qty,
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
                print(f"      ✅ Order submitted: {order.id}")
                self.session_trades += 1
                
        except Exception as e:
            print(f"   ❌ Trade error for {signal['symbol']}: {e}")
    
    async def show_portfolio(self):
        """Display current portfolio status"""
        try:
            positions = self.api.list_positions()
            account = self.api.get_account()
            
            print("\n" + "-" * 50)
            print(f"💼 PORTFOLIO STATUS - {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 50)
            print(f"   Equity: ${float(account.equity):,.2f}")
            print(f"   Cash: ${float(account.cash):,.2f}")
            print(f"   Day P/L: ${float(account.equity) - float(account.last_equity):,.2f}")
            
            if positions:
                print(f"\n   📊 Open Positions ({len(positions)}):")
                for p in positions:
                    pnl = float(p.unrealized_pl)
                    pnl_pct = float(p.unrealized_plpc) * 100
                    emoji = "🟢" if pnl >= 0 else "🔴"
                    print(f"      {emoji} {p.symbol}: {p.qty} @ ${float(p.avg_entry_price):,.2f} | P/L: ${pnl:,.2f} ({pnl_pct:+.2f}%)")
            else:
                print("\n   No open positions")
            
            print(f"\n   Session: {self.session_trades} trades")
            print("-" * 50)
            
        except Exception as e:
            print(f"Portfolio error: {e}")
    
    async def run(self):
        """Main trading loop - runs 24/7"""
        await self.initialize()
        
        cycle = 0
        while True:
            cycle += 1
            print(f"\n🔄 TRADING CYCLE {cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 50)
            
            # Check if we should pause trading (drawdown protection)
            if ADAPTIVE_RISK_AVAILABLE:
                should_pause, reason = should_pause_trading()
                if should_pause:
                    print(f"\n   ⚠️ TRADING PAUSED: {reason}")
                    print(f"   Waiting 30 minutes before resuming...")
                    await asyncio.sleep(1800)
                    continue
            
            # Analyze each crypto
            for symbol in self.crypto_watchlist:
                print(f"\n   Analyzing {symbol}...")
                signal = await self.analyze_crypto(symbol)
                
                # Get ADAPTIVE threshold for this specific asset
                threshold = self._get_threshold(symbol)
                
                if signal['action'] != 'HOLD' and signal['confidence'] >= threshold:
                    print(f"   🎯 Signal: {signal['action']} @ {signal['confidence']:.0%} (threshold: {threshold:.0%})")
                    await self.execute_trade(signal)
                else:
                    print(f"   ⏸️ HOLD (confidence: {signal['confidence']:.0%})")
            
            # Show portfolio status
            await self.show_portfolio()
            
            # Wait before next cycle (3 minutes for crypto)
            wait_time = 180  # 3 minutes
            print(f"\n⏳ Next analysis in {wait_time // 60} minutes...")
            await asyncio.sleep(wait_time)


async def main():
    trader = PrometheusCryptoTrader()
    try:
        await trader.run()
    except KeyboardInterrupt:
        print("\n\n🛑 PROMETHEUS Crypto Trader stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    print("🔥 Starting PROMETHEUS Crypto Trader (24/7)")
    asyncio.run(main())
