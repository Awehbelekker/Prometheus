#!/usr/bin/env python3
"""
================================================================================
PROMETHEUS LIVE TRADING PATTERN FEEDBACK LOOP
================================================================================

Automatically learns from live trading outcomes:
- Captures charts before/after trades
- Records trade outcomes
- Updates pattern recognition based on actual results
- Continuous improvement through real trading feedback

================================================================================
"""

import os
import sys
import json
import time
import base64
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
import queue

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_trading_feedback.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add project root
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class TradeFeedback:
    """Represents feedback from a completed trade"""
    trade_id: str
    symbol: str
    direction: str  # long, short
    entry_time: str
    exit_time: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_pct: float
    holding_period_minutes: int
    
    # Pre-trade conditions
    entry_signals: Dict[str, Any]
    entry_patterns: List[str]
    entry_chart_path: str
    
    # Post-trade analysis
    exit_reason: str  # target, stop_loss, manual, time
    exit_patterns: List[str]
    exit_chart_path: str
    
    # Learning metadata
    pattern_success: bool
    feedback_processed: bool = False


class LiveTradingFeedbackLoop:
    """
    Continuous learning from live trading outcomes.
    
    Features:
    - Real-time trade monitoring
    - Chart capture at entry/exit
    - Pattern success tracking
    - Model fine-tuning data generation
    - Performance analytics
    """
    
    def __init__(self, 
                 feedback_dir: str = "trading_feedback",
                 pattern_file: str = "visual_ai_patterns.json",
                 auto_capture: bool = True):
        
        self.feedback_dir = Path(feedback_dir)
        self.feedback_dir.mkdir(exist_ok=True)
        
        self.charts_dir = self.feedback_dir / "charts"
        self.charts_dir.mkdir(exist_ok=True)
        
        self.pattern_file = Path(pattern_file)
        
        # Feedback storage
        self.feedback_file = self.feedback_dir / "trade_feedback.json"
        self.feedback: Dict[str, TradeFeedback] = {}
        
        # Pattern success tracking
        self.pattern_stats_file = self.feedback_dir / "pattern_stats.json"
        self.pattern_stats: Dict[str, Dict[str, Any]] = {}
        
        # Active trades being monitored
        self.active_trades: Dict[str, Dict[str, Any]] = {}
        
        # Background processing
        self.processing_queue = queue.Queue()
        self.auto_capture = auto_capture
        self._running = False
        
        self._load_data()
        
        logger.info(f"Live Trading Feedback Loop initialized")
        logger.info(f"  Stored feedback: {len(self.feedback)} trades")
        logger.info(f"  Tracked patterns: {len(self.pattern_stats)}")
    
    def _load_data(self):
        """Load existing feedback data"""
        # Load feedback
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r') as f:
                    data = json.load(f)
                    for trade_id, fb_data in data.items():
                        self.feedback[trade_id] = TradeFeedback(**fb_data)
            except Exception as e:
                logger.error(f"Failed to load feedback: {e}")
        
        # Load pattern stats
        if self.pattern_stats_file.exists():
            try:
                with open(self.pattern_stats_file, 'r') as f:
                    self.pattern_stats = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load pattern stats: {e}")
    
    def _save_data(self):
        """Save feedback data"""
        # Save feedback
        data = {tid: asdict(fb) for tid, fb in self.feedback.items()}
        with open(self.feedback_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Save pattern stats
        with open(self.pattern_stats_file, 'w') as f:
            json.dump(self.pattern_stats, f, indent=2)
    
    def _generate_trade_id(self, symbol: str, entry_time: str) -> str:
        """Generate unique trade ID"""
        hash_input = f"{symbol}:{entry_time}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    def _capture_chart(self, symbol: str, label: str) -> Optional[str]:
        """Capture chart for a symbol"""
        try:
            import yfinance as yf
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            # Get recent data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="5d", interval="15m")
            
            if df.empty:
                logger.warning(f"No data for chart capture: {symbol}")
                return None
            
            # Create chart
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(df.index, df['Close'], 'b-', linewidth=1.5)
            ax.fill_between(df.index, df['Low'], df['High'], alpha=0.3)
            
            ax.set_title(f"{symbol} - {label}")
            ax.set_xlabel("Time")
            ax.set_ylabel("Price")
            ax.grid(True, alpha=0.3)
            
            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_path = self.charts_dir / f"{symbol}_{label}_{timestamp}.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"Chart captured: {chart_path.name}")
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"Chart capture failed: {e}")
            return None
    
    def on_trade_entry(self, symbol: str, direction: str, 
                       entry_price: float, quantity: float,
                       signals: Dict[str, Any] = None,
                       patterns: List[str] = None) -> str:
        """Called when a trade is entered"""
        
        entry_time = datetime.now().isoformat()
        trade_id = self._generate_trade_id(symbol, entry_time)
        
        logger.info(f"Trade entry recorded: {trade_id} - {direction} {quantity} {symbol} @ ${entry_price:.2f}")
        
        # Capture entry chart
        entry_chart = None
        if self.auto_capture:
            entry_chart = self._capture_chart(symbol, f"entry_{direction}")
        
        # Store active trade
        self.active_trades[trade_id] = {
            "symbol": symbol,
            "direction": direction,
            "entry_time": entry_time,
            "entry_price": entry_price,
            "quantity": quantity,
            "signals": signals or {},
            "patterns": patterns or [],
            "entry_chart": entry_chart
        }
        
        return trade_id
    
    def on_trade_exit(self, trade_id: str, exit_price: float,
                      exit_reason: str = "manual",
                      exit_patterns: List[str] = None) -> Optional[TradeFeedback]:
        """Called when a trade is exited"""
        
        if trade_id not in self.active_trades:
            logger.error(f"Trade not found: {trade_id}")
            return None
        
        trade = self.active_trades[trade_id]
        exit_time = datetime.now()
        
        # Calculate P&L
        entry_price = trade['entry_price']
        quantity = trade['quantity']
        direction = trade['direction']
        
        if direction == "long":
            pnl = (exit_price - entry_price) * quantity
        else:
            pnl = (entry_price - exit_price) * quantity
        
        pnl_pct = (pnl / (entry_price * quantity)) * 100
        
        # Calculate holding period
        entry_time = datetime.fromisoformat(trade['entry_time'])
        holding_minutes = int((exit_time - entry_time).total_seconds() / 60)
        
        # Capture exit chart
        exit_chart = None
        if self.auto_capture:
            exit_chart = self._capture_chart(trade['symbol'], f"exit_{exit_reason}")
        
        # Determine pattern success
        pattern_success = pnl > 0
        
        # Create feedback record
        feedback = TradeFeedback(
            trade_id=trade_id,
            symbol=trade['symbol'],
            direction=direction,
            entry_time=trade['entry_time'],
            exit_time=exit_time.isoformat(),
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=quantity,
            pnl=round(pnl, 2),
            pnl_pct=round(pnl_pct, 2),
            holding_period_minutes=holding_minutes,
            entry_signals=trade['signals'],
            entry_patterns=trade['patterns'],
            entry_chart_path=trade.get('entry_chart', ''),
            exit_reason=exit_reason,
            exit_patterns=exit_patterns or [],
            exit_chart_path=exit_chart or '',
            pattern_success=pattern_success,
            feedback_processed=False
        )
        
        # Store feedback
        self.feedback[trade_id] = feedback
        
        # Update pattern statistics
        self._update_pattern_stats(feedback)
        
        # Remove from active trades
        del self.active_trades[trade_id]
        
        # Save data
        self._save_data()
        
        logger.info(f"Trade exit recorded: {trade_id}")
        logger.info(f"  P&L: ${pnl:.2f} ({pnl_pct:.2f}%)")
        logger.info(f"  Patterns successful: {pattern_success}")
        
        return feedback
    
    def _update_pattern_stats(self, feedback: TradeFeedback):
        """Update pattern success statistics"""
        
        for pattern in feedback.entry_patterns:
            if pattern not in self.pattern_stats:
                self.pattern_stats[pattern] = {
                    "total_trades": 0,
                    "successful_trades": 0,
                    "total_pnl": 0,
                    "avg_pnl_pct": 0,
                    "win_rate": 0,
                    "last_updated": None
                }
            
            stats = self.pattern_stats[pattern]
            stats["total_trades"] += 1
            stats["total_pnl"] += feedback.pnl
            
            if feedback.pattern_success:
                stats["successful_trades"] += 1
            
            stats["win_rate"] = (stats["successful_trades"] / stats["total_trades"]) * 100
            stats["avg_pnl_pct"] = stats["total_pnl"] / stats["total_trades"]
            stats["last_updated"] = datetime.now().isoformat()
    
    def get_pattern_performance(self, min_trades: int = 5) -> List[Dict[str, Any]]:
        """Get pattern performance statistics"""
        
        results = []
        for pattern, stats in self.pattern_stats.items():
            if stats["total_trades"] >= min_trades:
                results.append({
                    "pattern": pattern,
                    **stats
                })
        
        # Sort by win rate
        results.sort(key=lambda x: x["win_rate"], reverse=True)
        return results
    
    def get_learning_data(self) -> List[Dict[str, Any]]:
        """Generate learning data for model fine-tuning"""
        
        learning_data = []
        
        for trade_id, feedback in self.feedback.items():
            if not feedback.feedback_processed:
                # Create training example
                example = {
                    "input": {
                        "symbol": feedback.symbol,
                        "direction": feedback.direction,
                        "entry_signals": feedback.entry_signals,
                        "entry_patterns": feedback.entry_patterns
                    },
                    "output": {
                        "success": feedback.pattern_success,
                        "pnl_pct": feedback.pnl_pct,
                        "exit_reason": feedback.exit_reason,
                        "holding_period": feedback.holding_period_minutes
                    },
                    "label": "positive" if feedback.pattern_success else "negative"
                }
                
                learning_data.append(example)
        
        return learning_data
    
    def export_for_training(self, output_file: str = "training_feedback.json"):
        """Export feedback for model training"""
        
        learning_data = self.get_learning_data()
        
        output_path = self.feedback_dir / output_file
        with open(output_path, 'w') as f:
            json.dump(learning_data, f, indent=2)
        
        logger.info(f"Exported {len(learning_data)} examples to {output_path}")
        return str(output_path)
    
    def update_visual_patterns(self):
        """Update visual AI patterns based on feedback"""
        
        if not self.pattern_file.exists():
            logger.warning("Visual patterns file not found")
            return
        
        try:
            with open(self.pattern_file, 'r') as f:
                patterns = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")
            return
        
        updates = 0
        
        for pattern_name, stats in self.pattern_stats.items():
            if stats["total_trades"] >= 3:  # Minimum trades for update
                # Find matching patterns
                for entry in patterns.get('successful', []):
                    if 'patterns' in entry:
                        for p in entry['patterns']:
                            if pattern_name.lower() in p.get('type', '').lower():
                                # Add feedback data
                                p['live_win_rate'] = stats['win_rate']
                                p['live_trades'] = stats['total_trades']
                                p['live_updated'] = datetime.now().isoformat()
                                updates += 1
        
        if updates > 0:
            with open(self.pattern_file, 'w') as f:
                json.dump(patterns, f, indent=2)
            logger.info(f"Updated {updates} patterns with live feedback")
        
        return updates
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics"""
        
        if not self.feedback:
            return {"message": "No trade feedback yet"}
        
        total_trades = len(self.feedback)
        successful = sum(1 for fb in self.feedback.values() if fb.pattern_success)
        total_pnl = sum(fb.pnl for fb in self.feedback.values())
        
        # By direction
        long_trades = [fb for fb in self.feedback.values() if fb.direction == "long"]
        short_trades = [fb for fb in self.feedback.values() if fb.direction == "short"]
        
        # By exit reason
        exit_reasons = {}
        for fb in self.feedback.values():
            reason = fb.exit_reason
            if reason not in exit_reasons:
                exit_reasons[reason] = {"count": 0, "pnl": 0}
            exit_reasons[reason]["count"] += 1
            exit_reasons[reason]["pnl"] += fb.pnl
        
        return {
            "total_trades": total_trades,
            "successful_trades": successful,
            "win_rate": (successful / total_trades) * 100 if total_trades > 0 else 0,
            "total_pnl": round(total_pnl, 2),
            "avg_pnl": round(total_pnl / total_trades, 2) if total_trades > 0 else 0,
            "long_trades": len(long_trades),
            "long_win_rate": (sum(1 for t in long_trades if t.pattern_success) / len(long_trades) * 100) if long_trades else 0,
            "short_trades": len(short_trades),
            "short_win_rate": (sum(1 for t in short_trades if t.pattern_success) / len(short_trades) * 100) if short_trades else 0,
            "exit_reasons": exit_reasons,
            "top_patterns": self.get_pattern_performance()[:10],
            "tracked_patterns": len(self.pattern_stats)
        }


class AutoTradeMonitor:
    """
    Monitors live trading and automatically captures feedback.
    
    Integrates with:
    - Alpaca
    - Interactive Brokers
    - Paper trading systems
    """
    
    def __init__(self, feedback_loop: LiveTradingFeedbackLoop, 
                 broker: str = "alpaca"):
        self.feedback = feedback_loop
        self.broker = broker
        self.monitored_positions: Dict[str, str] = {}  # symbol -> trade_id
        self._running = False
        self._thread = None
    
    def start(self, poll_interval: int = 60):
        """Start monitoring"""
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, args=(poll_interval,))
        self._thread.daemon = True
        self._thread.start()
        logger.info(f"Auto trade monitor started (polling every {poll_interval}s)")
    
    def stop(self):
        """Stop monitoring"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Auto trade monitor stopped")
    
    def _monitor_loop(self, poll_interval: int):
        """Main monitoring loop"""
        while self._running:
            try:
                self._check_positions()
            except Exception as e:
                logger.error(f"Monitor error: {e}")
            time.sleep(poll_interval)
    
    def _check_positions(self):
        """Check current positions for changes"""
        if self.broker == "alpaca":
            self._check_alpaca_positions()
        elif self.broker == "ib":
            self._check_ib_positions()
    
    def _check_alpaca_positions(self):
        """Check Alpaca positions"""
        try:
            from alpaca.trading.client import TradingClient
            from dotenv import load_dotenv
            load_dotenv()
            
            client = TradingClient(
                os.getenv("ALPACA_API_KEY"),
                os.getenv("ALPACA_SECRET_KEY"),
                paper=True
            )
            
            # Get current positions
            positions = client.get_all_positions()
            current_symbols = {p.symbol: p for p in positions}
            
            # Check for new positions
            for symbol, position in current_symbols.items():
                if symbol not in self.monitored_positions:
                    # New position opened
                    direction = "long" if float(position.qty) > 0 else "short"
                    trade_id = self.feedback.on_trade_entry(
                        symbol=symbol,
                        direction=direction,
                        entry_price=float(position.avg_entry_price),
                        quantity=abs(float(position.qty))
                    )
                    self.monitored_positions[symbol] = trade_id
                    logger.info(f"New position detected: {symbol}")
            
            # Check for closed positions
            closed_symbols = set(self.monitored_positions.keys()) - set(current_symbols.keys())
            for symbol in closed_symbols:
                trade_id = self.monitored_positions[symbol]
                # Get last trade to determine exit price
                # This is simplified - in production you'd get actual exit price
                self.feedback.on_trade_exit(
                    trade_id=trade_id,
                    exit_price=0,  # Would need to get from orders
                    exit_reason="unknown"
                )
                del self.monitored_positions[symbol]
                logger.info(f"Position closed: {symbol}")
                
        except Exception as e:
            logger.error(f"Alpaca check failed: {e}")
    
    def _check_ib_positions(self):
        """Check Interactive Brokers positions"""
        # Placeholder for IB integration
        pass


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("PROMETHEUS LIVE TRADING FEEDBACK LOOP")
    print("="*70)
    
    # Initialize feedback loop
    feedback_loop = LiveTradingFeedbackLoop()
    
    # Show current analytics
    print("\n[1] Current Analytics:")
    analytics = feedback_loop.get_analytics()
    if "message" in analytics:
        print(f"    {analytics['message']}")
    else:
        print(f"    Total Trades: {analytics['total_trades']}")
        print(f"    Win Rate: {analytics['win_rate']:.1f}%")
        print(f"    Total P&L: ${analytics['total_pnl']:.2f}")
        print(f"    Tracked Patterns: {analytics['tracked_patterns']}")
    
    # Show top patterns
    print("\n[2] Top Performing Patterns:")
    patterns = feedback_loop.get_pattern_performance()
    if patterns:
        for p in patterns[:5]:
            print(f"    • {p['pattern']}")
            print(f"      Win Rate: {p['win_rate']:.1f}% ({p['total_trades']} trades)")
    else:
        print("    No patterns tracked yet")
    
    # Demo trade entry/exit
    print("\n[3] Demo Trade:")
    trade_id = feedback_loop.on_trade_entry(
        symbol="AAPL",
        direction="long",
        entry_price=185.50,
        quantity=10,
        signals={"rsi": 35, "macd": "bullish_crossover"},
        patterns=["hammer", "support_bounce", "volume_spike"]
    )
    print(f"    Trade entered: {trade_id}")
    
    # Simulate exit
    time.sleep(1)
    feedback = feedback_loop.on_trade_exit(
        trade_id=trade_id,
        exit_price=187.25,
        exit_reason="target",
        exit_patterns=["resistance_hit"]
    )
    if feedback:
        print(f"    Trade exited: P&L ${feedback.pnl:.2f} ({feedback.pnl_pct:.2f}%)")
    
    # Export learning data
    print("\n[4] Exporting learning data...")
    export_path = feedback_loop.export_for_training()
    print(f"    Exported to: {export_path}")
    
    # Update visual patterns
    print("\n[5] Updating visual patterns...")
    updates = feedback_loop.update_visual_patterns()
    print(f"    Updated {updates} patterns with feedback")
    
    print("\n" + "="*70)
    print("LIVE TRADING FEEDBACK READY")
    print("="*70)
    print("\nUsage:")
    print("  from live_trading_feedback import LiveTradingFeedbackLoop")
    print("  feedback = LiveTradingFeedbackLoop()")
    print("  trade_id = feedback.on_trade_entry(symbol, direction, price, qty)")
    print("  feedback.on_trade_exit(trade_id, exit_price, 'target')")
    print("\nAuto-monitoring:")
    print("  from live_trading_feedback import AutoTradeMonitor")
    print("  monitor = AutoTradeMonitor(feedback, broker='alpaca')")
    print("  monitor.start(poll_interval=60)")
    print("="*70)


if __name__ == "__main__":
    main()
