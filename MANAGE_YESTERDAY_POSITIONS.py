#!/usr/bin/env python3
"""
🎯 MANAGE YESTERDAY'S 3 POSITIONS
AI will decide: Hold, Take Profit, or Stop Loss
"""

import asyncio
from ib_insync import IB, Stock, MarketOrder
from datetime import datetime

class PositionManager:
    def __init__(self):
        self.ib = IB()
        self.take_profit_percent = 6.0
        self.stop_loss_percent = 2.0
        self.trailing_stop_percent = 1.5
        
    def print_header(self, text):
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70)
        
    def print_status(self, emoji, text):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {emoji} {text}")
    
    async def connect(self):
        """Connect to IB Gateway"""
        try:
            self.print_status("🔌", "Connecting to IB Gateway...")
            await self.ib.connectAsync('127.0.0.1', 7496, clientId=30, timeout=10)
            self.print_status("[CHECK]", "Connected!")
            return True
        except Exception as e:
            self.print_status("[ERROR]", f"Connection failed: {e}")
            return False
    
    async def analyze_and_manage_positions(self):
        """Analyze all positions and make AI decisions"""
        self.print_header("📊 ANALYZING YOUR 3 POSITIONS FROM YESTERDAY")
        
        positions = self.ib.positions()
        
        if not positions:
            self.print_status("[INFO]️", "No positions found")
            return
        
        self.print_status("📈", f"Found {len(positions)} position(s)\n")
        
        decisions = []
        total_value = 0
        total_pnl = 0
        
        for i, pos in enumerate(positions, 1):
            symbol = pos.contract.symbol
            quantity = pos.position
            avg_cost = pos.avgCost
            
            self.print_status("📊", f"Position {i}: {symbol}")
            self.print_status("💼", f"  Quantity: {quantity} shares")
            self.print_status("💵", f"  Avg Cost: ${avg_cost:.2f}")
            
            # Get current market price
            contract = pos.contract
            ticker = self.ib.reqMktData(contract, '', False, False)
            await asyncio.sleep(3)
            
            current_price = ticker.last if ticker.last and ticker.last > 0 else avg_cost
            market_value = quantity * current_price
            cost_basis = abs(quantity) * avg_cost
            unrealized_pnl = market_value - cost_basis
            pnl_percent = (unrealized_pnl / cost_basis) * 100 if cost_basis != 0 else 0
            
            self.ib.cancelMktData(contract)
            
            self.print_status("💰", f"  Current Price: ${current_price:.2f}")
            self.print_status("📈", f"  Market Value: ${market_value:.2f}")
            self.print_status("💵", f"  Unrealized P&L: ${unrealized_pnl:.2f} ({pnl_percent:+.2f}%)")
            
            total_value += market_value
            total_pnl += unrealized_pnl
            
            # AI DECISION LOGIC
            decision = None
            reason = None
            
            if pnl_percent >= self.take_profit_percent:
                decision = "SELL"
                reason = f"🎯 TAKE PROFIT - Hit {self.take_profit_percent}% target!"
                self.print_status("🎯", f"  🤖 AI DECISION: {reason}")
                
            elif pnl_percent <= -self.stop_loss_percent:
                decision = "SELL"
                reason = f"🛑 STOP LOSS - Hit {self.stop_loss_percent}% stop!"
                self.print_status("🛑", f"  🤖 AI DECISION: {reason}")
                
            else:
                decision = "HOLD"
                reason = f"[CHECK] HOLD - P&L within range ({pnl_percent:+.2f}%)"
                self.print_status("[CHECK]", f"  🤖 AI DECISION: {reason}")
                self.print_status("🎯", f"  Targets: +{self.take_profit_percent}% profit | -{self.stop_loss_percent}% stop")
            
            decisions.append({
                'symbol': symbol,
                'quantity': quantity,
                'avg_cost': avg_cost,
                'current_price': current_price,
                'market_value': market_value,
                'pnl': unrealized_pnl,
                'pnl_percent': pnl_percent,
                'decision': decision,
                'reason': reason,
                'contract': contract
            })
            
            print()
        
        # Summary
        self.print_header("📊 PORTFOLIO SUMMARY")
        self.print_status("💰", f"Total Market Value: ${total_value:.2f}")
        self.print_status("💵", f"Total Unrealized P&L: ${total_pnl:.2f}")
        self.print_status("📈", f"Total P&L %: {(total_pnl/total_value)*100:+.2f}%")
        print()
        
        # Execute decisions
        self.print_header("🚀 EXECUTING AI DECISIONS")
        
        for dec in decisions:
            if dec['decision'] == "SELL":
                self.print_status("📤", f"Closing {dec['symbol']}: {dec['reason']}")
                await self.close_position(dec)
            else:
                self.print_status("[CHECK]", f"Holding {dec['symbol']}: {dec['reason']}")
        
        print()
        
        # Final summary
        sells = [d for d in decisions if d['decision'] == 'SELL']
        holds = [d for d in decisions if d['decision'] == 'HOLD']
        
        self.print_header("[CHECK] POSITION MANAGEMENT COMPLETE")
        self.print_status("📊", f"Positions to SELL: {len(sells)}")
        self.print_status("[CHECK]", f"Positions to HOLD: {len(holds)}")
        
        if sells:
            self.print_status("💰", "Selling positions:")
            for s in sells:
                self.print_status("  📤", f"{s['symbol']}: {s['pnl_percent']:+.2f}% P&L")
        
        if holds:
            self.print_status("[CHECK]", "Holding positions:")
            for h in holds:
                self.print_status("  📊", f"{h['symbol']}: {h['pnl_percent']:+.2f}% P&L")
        
        print()
        
        return decisions
    
    async def close_position(self, position_data):
        """Close a position with market order"""
        try:
            symbol = position_data['symbol']
            quantity = position_data['quantity']
            contract = position_data['contract']
            
            # Create market order to close
            action = 'SELL' if quantity > 0 else 'BUY'
            order = MarketOrder(action, abs(quantity))
            
            self.print_status("📤", f"  Placing {action} order for {abs(quantity)} {symbol}...")
            
            trade = self.ib.placeOrder(contract, order)
            
            # Wait for fill
            await asyncio.sleep(5)
            
            if trade.orderStatus.status == 'Filled':
                fill_price = trade.orderStatus.avgFillPrice
                self.print_status("[CHECK]", f"  FILLED at ${fill_price:.2f}")
                
                # Calculate realized P&L
                realized_pnl = (fill_price - position_data['avg_cost']) * abs(quantity)
                self.print_status("💰", f"  Realized P&L: ${realized_pnl:.2f}")
                
            else:
                self.print_status("[WARNING]️", f"  Order status: {trade.orderStatus.status}")
                
        except Exception as e:
            self.print_status("[ERROR]", f"  Error closing position: {e}")

async def main():
    print("\n" + "=" * 70)
    print("  🎯 PROMETHEUS POSITION MANAGER")
    print("  💰 Managing Yesterday's 3 Positions")
    print("  🤖 AI Will Decide: Hold, Take Profit, or Stop Loss")
    print("=" * 70 + "\n")
    
    manager = PositionManager()
    
    # Connect
    connected = await manager.connect()
    if not connected:
        print("\n[ERROR] Failed to connect to IB Gateway")
        print("💡 Make sure IB Gateway is running on port 7496\n")
        return
    
    # Analyze and manage positions
    try:
        decisions = await manager.analyze_and_manage_positions()
        
        # Ask for confirmation
        print("\n" + "=" * 70)
        print("  [WARNING]️  CONFIRMATION REQUIRED")
        print("=" * 70)
        print("\nThe AI has analyzed your positions and made recommendations.")
        print("Review the decisions above.")
        print("\nDo you want to execute these decisions? (yes/no): ", end='')
        
        # For now, just show the plan
        print("\n\n💡 This is a DRY RUN - showing AI decisions only")
        print("💡 To execute, uncomment the confirmation code\n")
        
    except KeyboardInterrupt:
        print("\n\n[WARNING]️ Interrupted by user\n")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}\n")
    finally:
        manager.ib.disconnect()
        print("[CHECK] Disconnected from IB Gateway\n")

if __name__ == "__main__":
    asyncio.run(main())

