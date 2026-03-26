#!/usr/bin/env python3
"""
🌙 PROMETHEUS OVERNIGHT TRADING SESSION - $255.00
Autonomous overnight paper trading with intelligent strategies
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
import signal
import sys
import os

class OvernightTradingSession:
    def __init__(self, starting_capital: float = 255.00, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.starting_capital = starting_capital
        self.session_id = f"overnight_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.user_id = f"overnight_trader_{self.session_id}"
        
        # Portfolio state
        self.portfolio = {
            "cash": starting_capital,
            "positions": {},
            "total_value": starting_capital,
            "trades": [],
            "pnl": 0.0,
            "max_drawdown": 0.0,
            "peak_value": starting_capital
        }
        
        # Trading parameters
        self.max_position_size = 0.15  # Max 15% per position
        self.stop_loss_pct = 0.05      # 5% stop loss
        self.take_profit_pct = 0.08    # 8% take profit
        self.max_positions = 5         # Max 5 concurrent positions
        self.min_trade_size = 10.0     # Minimum $10 per trade
        
        # Session control
        self.running = False
        self.session_start = None
        self.session_end = None
        self.trade_count = 0
        self.last_market_check = None
        
        # Watchlist
        self.watchlist = ["AAPL", "SPY", "QQQ", "TSLA", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "NFLX"]
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_filename = f"overnight_session_{self.session_id}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Overnight Trading Session Initialized: {self.session_id}")
        self.logger.info(f"Starting Capital: ${self.starting_capital:.2f}")
    
    def get_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Get real-time market data"""
        try:
            symbols_str = ",".join(symbols)
            response = requests.get(f"{self.base_url}/api/market-data?symbols={symbols_str}", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Market data failed: {response.status_code}")
                return {}
        except Exception as e:
            self.logger.error(f"Market data error: {e}")
            return {}
    
    def calculate_position_value(self, symbol: str, shares: float, current_price: float) -> float:
        """Calculate current value of a position"""
        return shares * current_price
    
    def update_portfolio_values(self, market_data: Dict[str, Any]):
        """Update portfolio with current market prices"""
        total_value = self.portfolio["cash"]
        
        for symbol, position in self.portfolio["positions"].items():
            if symbol in market_data:
                current_price = market_data[symbol]["price"]
                position["current_price"] = current_price
                position_value = position["shares"] * current_price
                total_value += position_value
                
                # Calculate unrealized P&L
                position["unrealized_pnl"] = (current_price - position["avg_price"]) * position["shares"]
                position["unrealized_pnl_pct"] = (position["unrealized_pnl"] / (position["avg_price"] * position["shares"])) * 100
        
        self.portfolio["total_value"] = total_value
        self.portfolio["pnl"] = total_value - self.starting_capital
        
        # Track peak value and drawdown
        if total_value > self.portfolio["peak_value"]:
            self.portfolio["peak_value"] = total_value
        
        current_drawdown = (self.portfolio["peak_value"] - total_value) / self.portfolio["peak_value"]
        if current_drawdown > self.portfolio["max_drawdown"]:
            self.portfolio["max_drawdown"] = current_drawdown
    
    def can_afford_trade(self, cost: float) -> bool:
        """Check if we can afford a trade"""
        return self.portfolio["cash"] >= cost
    
    def execute_buy_order(self, symbol: str, shares: float, price: float, reason: str = "") -> Dict[str, Any]:
        """Execute a buy order"""
        cost = shares * price
        
        if not self.can_afford_trade(cost):
            return {"success": False, "error": "Insufficient funds"}
        
        if cost < self.min_trade_size:
            return {"success": False, "error": f"Trade size too small (${cost:.2f} < ${self.min_trade_size})"}
        
        # Check position size limit
        position_pct = cost / self.portfolio["total_value"]
        if position_pct > self.max_position_size:
            return {"success": False, "error": f"Position size too large ({position_pct:.1%} > {self.max_position_size:.1%})"}
        
        # Execute trade
        self.portfolio["cash"] -= cost
        
        if symbol in self.portfolio["positions"]:
            # Add to existing position
            existing = self.portfolio["positions"][symbol]
            total_shares = existing["shares"] + shares
            total_cost = (existing["shares"] * existing["avg_price"]) + cost
            new_avg_price = total_cost / total_shares
            
            self.portfolio["positions"][symbol].update({
                "shares": total_shares,
                "avg_price": new_avg_price,
                "current_price": price
            })
        else:
            # New position
            self.portfolio["positions"][symbol] = {
                "shares": shares,
                "avg_price": price,
                "current_price": price,
                "entry_time": datetime.now().isoformat(),
                "unrealized_pnl": 0.0,
                "unrealized_pnl_pct": 0.0
            }
        
        # Record trade
        trade = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "side": "buy",
            "shares": shares,
            "price": price,
            "cost": cost,
            "reason": reason,
            "portfolio_value": self.portfolio["total_value"]
        }
        self.portfolio["trades"].append(trade)
        self.trade_count += 1
        
        self.logger.info(f"🟢 BUY: {shares:.3f} {symbol} @ ${price:.2f} (${cost:.2f}) - {reason}")
        return {"success": True, "trade": trade}
    
    def execute_sell_order(self, symbol: str, shares: float, price: float, reason: str = "") -> Dict[str, Any]:
        """Execute a sell order"""
        if symbol not in self.portfolio["positions"]:
            return {"success": False, "error": f"No position in {symbol}"}
        
        position = self.portfolio["positions"][symbol]
        if position["shares"] < shares:
            return {"success": False, "error": "Insufficient shares"}
        
        # Execute trade
        proceeds = shares * price
        self.portfolio["cash"] += proceeds
        
        # Calculate realized P&L
        realized_pnl = (price - position["avg_price"]) * shares
        
        # Update position
        position["shares"] -= shares
        if position["shares"] == 0:
            del self.portfolio["positions"][symbol]
        
        # Record trade
        trade = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "side": "sell",
            "shares": shares,
            "price": price,
            "proceeds": proceeds,
            "realized_pnl": realized_pnl,
            "reason": reason,
            "portfolio_value": self.portfolio["total_value"]
        }
        self.portfolio["trades"].append(trade)
        self.trade_count += 1
        
        self.logger.info(f"🔴 SELL: {shares:.3f} {symbol} @ ${price:.2f} (${proceeds:.2f}, P&L: ${realized_pnl:.2f}) - {reason}")
        return {"success": True, "trade": trade}
    
    def analyze_symbol(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced analysis for trading opportunities with 24-hour optimizations"""
        price = data["price"]
        change_pct = data["change_percent"]
        volume = data.get("volume", 0)

        analysis = {
            "symbol": symbol,
            "price": price,
            "change_pct": change_pct,
            "volume": volume,
            "signal": "HOLD",
            "confidence": 0.0,
            "reason": ""
        }

        # Enhanced momentum strategy for 24-hour session
        if change_pct > 3.0 and volume > 1500000:
            analysis.update({
                "signal": "BUY",
                "confidence": min(0.9, change_pct / 4.0),
                "reason": f"Strong upward momentum (+{change_pct:.2f}%) with high volume ({volume:,})"
            })
        elif change_pct > 1.5 and volume > 2000000:
            analysis.update({
                "signal": "BUY",
                "confidence": min(0.7, change_pct / 3.0),
                "reason": f"Moderate momentum (+{change_pct:.2f}%) with very high volume ({volume:,})"
            })
        # Enhanced mean reversion for oversold conditions
        elif change_pct < -4.0 and volume > 1200000:
            analysis.update({
                "signal": "BUY",
                "confidence": min(0.8, abs(change_pct) / 5.0),
                "reason": f"Strong oversold bounce opportunity ({change_pct:.2f}%) with high volume ({volume:,})"
            })
        elif change_pct < -2.5 and volume > 1800000:
            analysis.update({
                "signal": "BUY",
                "confidence": min(0.6, abs(change_pct) / 4.0),
                "reason": f"Oversold bounce opportunity ({change_pct:.2f}%) with very high volume ({volume:,})"
            })
        # Breakout detection for gap moves
        elif abs(change_pct) > 6.0 and volume > 2500000:
            if change_pct > 0:
                analysis.update({
                    "signal": "BUY",
                    "confidence": min(0.8, change_pct / 8.0),
                    "reason": f"Breakout momentum (+{change_pct:.2f}%) with massive volume ({volume:,})"
                })
        # Overbought conditions - more conservative
        elif change_pct > 8.0:
            analysis.update({
                "signal": "SELL",
                "confidence": 0.7,
                "reason": f"Overbought condition (+{change_pct:.2f}%)"
            })

        return analysis
    
    def check_risk_management(self):
        """Check and execute risk management rules"""
        positions_to_close = []
        
        for symbol, position in self.portfolio["positions"].items():
            current_price = position["current_price"]
            avg_price = position["avg_price"]
            pnl_pct = position["unrealized_pnl_pct"]
            
            # Stop loss check
            if pnl_pct <= -self.stop_loss_pct * 100:
                positions_to_close.append({
                    "symbol": symbol,
                    "shares": position["shares"],
                    "price": current_price,
                    "reason": f"Stop loss triggered ({pnl_pct:.2f}%)"
                })
            
            # Take profit check
            elif pnl_pct >= self.take_profit_pct * 100:
                # Sell half the position
                sell_shares = position["shares"] * 0.5
                positions_to_close.append({
                    "symbol": symbol,
                    "shares": sell_shares,
                    "price": current_price,
                    "reason": f"Take profit ({pnl_pct:.2f}%)"
                })
        
        # Execute risk management trades
        for trade in positions_to_close:
            self.execute_sell_order(
                trade["symbol"], 
                trade["shares"], 
                trade["price"], 
                trade["reason"]
            )
    
    def trading_cycle(self):
        """Execute one trading cycle"""
        try:
            # Get market data
            market_data = self.get_market_data(self.watchlist)
            if not market_data:
                self.logger.warning("No market data received, skipping cycle")
                return
            
            # Update portfolio values
            self.update_portfolio_values(market_data)
            
            # Log portfolio status
            self.logger.info(f"💰 Portfolio: ${self.portfolio['total_value']:.2f} | P&L: ${self.portfolio['pnl']:.2f} ({(self.portfolio['pnl']/self.starting_capital)*100:.2f}%)")
            
            # Check risk management
            self.check_risk_management()
            
            # Look for new opportunities (if we have room for more positions)
            if len(self.portfolio["positions"]) < self.max_positions:
                opportunities = []
                
                for symbol, data in market_data.items():
                    if symbol not in self.portfolio["positions"]:
                        analysis = self.analyze_symbol(symbol, data)
                        if analysis["signal"] == "BUY" and analysis["confidence"] > 0.5:
                            opportunities.append(analysis)
                
                # Sort by confidence and take the best opportunity
                opportunities.sort(key=lambda x: x["confidence"], reverse=True)
                
                if opportunities:
                    best_opportunity = opportunities[0]
                    symbol = best_opportunity["symbol"]
                    price = best_opportunity["price"]
                    
                    # Calculate position size (aim for 10-15% of portfolio)
                    target_investment = self.portfolio["total_value"] * 0.12
                    shares = target_investment / price
                    
                    if target_investment >= self.min_trade_size:
                        self.execute_buy_order(symbol, shares, price, best_opportunity["reason"])
            
            self.last_market_check = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Trading cycle error: {e}")
    
    def print_status(self):
        """Print current portfolio status"""
        print("\n" + "="*80)
        print(f"🌙 PROMETHEUS OVERNIGHT TRADING SESSION - {self.session_id}")
        print("="*80)
        print(f"💰 Starting Capital: ${self.starting_capital:.2f}")
        print(f"💵 Current Cash: ${self.portfolio['cash']:.2f}")
        print(f"📈 Total Portfolio Value: ${self.portfolio['total_value']:.2f}")
        print(f"📊 P&L: ${self.portfolio['pnl']:.2f} ({(self.portfolio['pnl']/self.starting_capital)*100:.2f}%)")
        print(f"📉 Max Drawdown: {self.portfolio['max_drawdown']*100:.2f}%")
        print(f"🔢 Total Trades: {self.trade_count}")
        
        if self.portfolio["positions"]:
            print(f"\n📋 CURRENT POSITIONS ({len(self.portfolio['positions'])}):")
            for symbol, position in self.portfolio["positions"].items():
                position_value = position["shares"] * position["current_price"]
                pnl = position["unrealized_pnl"]
                pnl_pct = position["unrealized_pnl_pct"]
                
                print(f"  {symbol}: {position['shares']:.3f} shares @ ${position['current_price']:.2f}")
                print(f"    Avg Cost: ${position['avg_price']:.2f} | Value: ${position_value:.2f}")
                print(f"    P&L: ${pnl:.2f} ({pnl_pct:.2f}%)")
        
        if self.portfolio["trades"]:
            print(f"\n📝 RECENT TRADES:")
            for trade in self.portfolio["trades"][-5:]:  # Show last 5 trades
                side_emoji = "🟢" if trade["side"] == "buy" else "🔴"
                timestamp = trade["timestamp"][:19]
                print(f"  {side_emoji} {timestamp} | {trade['side'].upper()} {trade['shares']:.3f} {trade['symbol']} @ ${trade['price']:.2f}")
                if trade.get("reason"):
                    print(f"    Reason: {trade['reason']}")
        
        print("="*80)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info("🛑 Shutdown signal received, stopping trading session...")
        self.stop_session()
    
    def stop_session(self):
        """Stop the trading session"""
        self.running = False
        self.session_end = datetime.now()
        self.logger.info("🏁 Trading session stopped")
    
    def run_overnight_session(self, duration_hours: float = 8.0):
        """Run the overnight trading session"""
        self.logger.info(f"🚀 Starting overnight trading session for {duration_hours} hours")
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.running = True
        self.session_start = datetime.now()
        session_end_time = self.session_start + timedelta(hours=duration_hours)
        
        self.logger.info(f"⏰ Session will run until: {session_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        cycle_count = 0
        
        try:
            while self.running and datetime.now() < session_end_time:
                cycle_count += 1
                self.logger.info(f"🔄 Trading Cycle #{cycle_count}")
                
                # Execute trading cycle
                self.trading_cycle()
                
                # Print status every 10 cycles
                if cycle_count % 10 == 0:
                    self.print_status()
                
                # Wait before next cycle (5 minutes)
                if self.running:
                    time.sleep(300)  # 5 minutes
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Manual stop requested")
        except Exception as e:
            self.logger.error(f"Session error: {e}")
        finally:
            self.stop_session()
            self.generate_final_report()
    
    def generate_final_report(self):
        """Generate final session report"""
        duration = (self.session_end - self.session_start).total_seconds() / 3600 if self.session_end else 0
        
        report = f"""
{'='*80}
🌙 PROMETHEUS OVERNIGHT TRADING SESSION - FINAL REPORT
{'='*80}
📅 Session ID: {self.session_id}
⏰ Duration: {duration:.2f} hours
💰 Starting Capital: ${self.starting_capital:.2f}
💵 Final Portfolio Value: ${self.portfolio['total_value']:.2f}
📊 Total P&L: ${self.portfolio['pnl']:.2f} ({(self.portfolio['pnl']/self.starting_capital)*100:.2f}%)
📉 Max Drawdown: {self.portfolio['max_drawdown']*100:.2f}%
🔢 Total Trades: {self.trade_count}
📈 Win Rate: {self.calculate_win_rate():.1f}%
{'='*80}
"""
        
        print(report)
        self.logger.info("📄 Final report generated")
        
        # Save detailed report to file
        report_filename = f"overnight_report_{self.session_id}.json"
        with open(report_filename, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "duration_hours": duration,
                "starting_capital": self.starting_capital,
                "final_value": self.portfolio["total_value"],
                "pnl": self.portfolio["pnl"],
                "max_drawdown": self.portfolio["max_drawdown"],
                "trade_count": self.trade_count,
                "trades": self.portfolio["trades"],
                "final_positions": self.portfolio["positions"]
            }, f, indent=2)
        
        self.logger.info(f"📄 Detailed report saved: {report_filename}")
    
    def calculate_win_rate(self) -> float:
        """Calculate win rate from completed trades"""
        if not self.portfolio["trades"]:
            return 0.0
        
        winning_trades = sum(1 for trade in self.portfolio["trades"] 
                           if trade.get("realized_pnl", 0) > 0)
        total_trades = len([t for t in self.portfolio["trades"] if t["side"] == "sell"])
        
        return (winning_trades / total_trades * 100) if total_trades > 0 else 0.0

def main():
    """Main function to run overnight trading session"""
    print("🌙 PROMETHEUS OVERNIGHT TRADING SESSION")
    print("💰 Starting Capital: $255.00")
    print("⏰ Duration: 8 hours")
    print("🎯 Strategy: Momentum + Mean Reversion")
    
    session = OvernightTradingSession(starting_capital=255.00)
    session.run_overnight_session(duration_hours=8.0)

if __name__ == "__main__":
    main()
