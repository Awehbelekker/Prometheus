"""
Position Manager for SHORT SELLING Capability
Tracks open positions and determines trade intent
Includes automatic profit-taking and stop-loss monitoring
Integrated with Prometheus Learning Engine for continuous improvement
"""

import sqlite3
from typing import Dict, Optional, Tuple, List
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class PositionManager:
    """Manages open positions for LONG and SHORT trading"""
    
    def __init__(self, db_path='prometheus_learning.db'):
        self.db_path = db_path
    
    def get_position(self, symbol: str, broker: str = 'Alpaca') -> Optional[Dict]:
        """Get current position for a symbol"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT symbol, side, quantity, entry_price, current_price, 
                   unrealized_pl, broker, opened_at, updated_at
            FROM open_positions
            WHERE symbol = ? AND broker = ?
        """, (symbol, broker))
        
        row = cursor.fetchone()
        db.close()
        
        if row:
            return {
                'symbol': row[0],
                'side': row[1],
                'quantity': row[2],
                'entry_price': row[3],
                'current_price': row[4],
                'unrealized_pl': row[5],
                'broker': row[6],
                'opened_at': row[7],
                'updated_at': row[8]
            }
        return None
    
    def determine_trade_intent(self, symbol: str, action: str, broker: str = 'Alpaca') -> Tuple[str, str]:
        """
        Determine if trade should OPEN or CLOSE a position
        Returns: (position_action, position_side)
        
        position_action: 'OPEN_LONG', 'CLOSE_LONG', 'OPEN_SHORT', 'CLOSE_SHORT'
        position_side: 'LONG', 'SHORT'
        """
        position = self.get_position(symbol, broker)
        
        if action in ['BUY', 'STRONG_BUY']:
            if position is None:
                # No position - open LONG
                return ('OPEN_LONG', 'LONG')
            elif position['side'] == 'SHORT':
                # Have SHORT position - close it (cover)
                return ('CLOSE_SHORT', 'SHORT')
            else:
                # Have LONG position - add to it (or ignore if max position)
                return ('ADD_LONG', 'LONG')
        
        elif action in ['SELL', 'STRONG_SELL']:
            if position is None:
                # No position - open SHORT
                return ('OPEN_SHORT', 'SHORT')
            elif position['side'] == 'LONG':
                # Have LONG position - close it
                return ('CLOSE_LONG', 'LONG')
            else:
                # Have SHORT position - add to it (or ignore if max position)
                return ('ADD_SHORT', 'SHORT')
        
        return ('HOLD', 'NONE')
    
    def open_position(self, symbol: str, side: str, quantity: float, 
                     entry_price: float, broker: str = 'Alpaca'):
        """Open a new position"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO open_positions
            (symbol, side, quantity, entry_price, current_price, broker, opened_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (symbol, side, quantity, entry_price, entry_price, broker, now, now))
        
        db.commit()
        db.close()
    
    def close_position(self, symbol: str, broker: str = 'Alpaca') -> Optional[Dict]:
        """Close a position and return its details"""
        position = self.get_position(symbol, broker)
        
        if position:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            
            cursor.execute("""
                DELETE FROM open_positions
                WHERE symbol = ? AND broker = ?
            """, (symbol, broker))
            
            db.commit()
            db.close()
        
        return position
    
    def update_position_price(self, symbol: str, current_price: float, broker: str = 'Alpaca'):
        """Update current price and calculate unrealized P/L"""
        position = self.get_position(symbol, broker)
        
        if position:
            entry_price = position['entry_price']
            quantity = position['quantity']
            side = position['side']
            
            # Calculate unrealized P/L
            if side == 'LONG':
                unrealized_pl = (current_price - entry_price) * quantity
            else:  # SHORT
                unrealized_pl = (entry_price - current_price) * quantity
            
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            
            cursor.execute("""
                UPDATE open_positions
                SET current_price = ?, unrealized_pl = ?, updated_at = ?
                WHERE symbol = ? AND broker = ?
            """, (current_price, unrealized_pl, datetime.now().isoformat(), symbol, broker))
            
            db.commit()
            db.close()
    
    def get_all_positions(self, broker: str = None) -> list:
        """Get all open positions"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()

        if broker:
            cursor.execute("""
                SELECT symbol, side, quantity, entry_price, current_price,
                       unrealized_pl, broker, opened_at, updated_at
                FROM open_positions
                WHERE broker = ?
            """, (broker,))
        else:
            cursor.execute("""
                SELECT symbol, side, quantity, entry_price, current_price,
                       unrealized_pl, broker, opened_at, updated_at
                FROM open_positions
            """)

        positions = []
        for row in cursor.fetchall():
            positions.append({
                'symbol': row[0],
                'side': row[1],
                'quantity': row[2],
                'entry_price': row[3],
                'current_price': row[4],
                'unrealized_pl': row[5],
                'broker': row[6],
                'opened_at': row[7],
                'updated_at': row[8]
            })

        db.close()
        return positions

    def check_exit_conditions(self, symbol: str, current_price: float, broker: str = 'Alpaca',
                              take_profit_pct: float = 0.08, stop_loss_pct: float = 0.03,
                              trailing_stop_pct: float = 0.025) -> Dict:
        """
        Check if a position should be exited based on profit/loss conditions

        Returns:
            dict with keys: should_exit, exit_reason, profit_pct, unrealized_pl
        """
        position = self.get_position(symbol, broker)

        if not position:
            return {'should_exit': False, 'exit_reason': None, 'profit_pct': 0, 'unrealized_pl': 0}

        entry_price = position['entry_price']
        quantity = position['quantity']
        side = position['side']

        # Calculate profit percentage
        if side == 'LONG':
            profit_pct = (current_price - entry_price) / entry_price
            unrealized_pl = (current_price - entry_price) * quantity
        else:  # SHORT
            profit_pct = (entry_price - current_price) / entry_price
            unrealized_pl = (entry_price - current_price) * quantity

        # Check exit conditions
        should_exit = False
        exit_reason = None

        # Take profit check (8% default)
        if profit_pct >= take_profit_pct:
            should_exit = True
            exit_reason = f"TAKE_PROFIT ({profit_pct*100:.2f}% >= {take_profit_pct*100:.1f}%)"
            logger.info(f"💰 {symbol}: TAKE PROFIT triggered at {profit_pct*100:.2f}% gain!")

        # Stop loss check (3% default)
        elif profit_pct <= -stop_loss_pct:
            should_exit = True
            exit_reason = f"STOP_LOSS ({profit_pct*100:.2f}% <= -{stop_loss_pct*100:.1f}%)"
            logger.warning(f"🛑 {symbol}: STOP LOSS triggered at {profit_pct*100:.2f}% loss!")

        # Trailing stop check - only applies if we're in profit
        elif profit_pct > 0:
            # Get highest price since entry (we'll track this via current_price updates)
            highest_price = position.get('current_price', entry_price)

            if side == 'LONG' and current_price > highest_price:
                # Update to new high
                self.update_position_price(symbol, current_price, broker)
            elif side == 'LONG':
                # Check if we've fallen trailing_stop_pct from the high
                drawdown_from_high = (highest_price - current_price) / highest_price
                if drawdown_from_high >= trailing_stop_pct and profit_pct > 0:
                    should_exit = True
                    exit_reason = f"TRAILING_STOP ({drawdown_from_high*100:.2f}% drawdown from high)"
                    logger.info(f"📉 {symbol}: TRAILING STOP triggered - locking in {profit_pct*100:.2f}% profit")

        return {
            'should_exit': should_exit,
            'exit_reason': exit_reason,
            'profit_pct': profit_pct,
            'unrealized_pl': unrealized_pl,
            'position': position
        }

    def get_positions_to_exit(self, current_prices: Dict[str, float], broker: str = 'Alpaca',
                              take_profit_pct: float = 0.08, stop_loss_pct: float = 0.03,
                              trailing_stop_pct: float = 0.025) -> List[Dict]:
        """
        Check all positions and return list of positions that should be exited

        Args:
            current_prices: dict of {symbol: current_price}

        Returns:
            List of positions that should be exited with exit details
        """
        positions_to_exit = []
        all_positions = self.get_all_positions(broker)

        for position in all_positions:
            symbol = position['symbol']
            if symbol in current_prices:
                exit_check = self.check_exit_conditions(
                    symbol, current_prices[symbol], broker,
                    take_profit_pct, stop_loss_pct, trailing_stop_pct
                )

                if exit_check['should_exit']:
                    positions_to_exit.append({
                        'symbol': symbol,
                        'side': position['side'],
                        'quantity': position['quantity'],
                        'entry_price': position['entry_price'],
                        'current_price': current_prices[symbol],
                        'exit_reason': exit_check['exit_reason'],
                        'profit_pct': exit_check['profit_pct'],
                        'unrealized_pl': exit_check['unrealized_pl'],
                        'broker': broker
                    })

        return positions_to_exit
    
    def record_trade_outcome(self, trade_id: int, exit_price: float, exit_reason: str,
                            market_indicators: Optional[Dict] = None) -> bool:
        """
        Record detailed trade outcome for machine learning
        
        Args:
            trade_id: ID of the trade in trade_history
            exit_price: Final exit price
            exit_reason: Reason for exit (TAKE_PROFIT, STOP_LOSS, etc.)
            market_indicators: Optional dict of market conditions at exit
        
        Returns:
            True if successful
        """
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        try:
            # Get trade entry details
            cursor.execute("""
                SELECT symbol, price, quantity, timestamp, broker
                FROM trade_history
                WHERE id = ?
            """, (trade_id,))
            
            trade = cursor.fetchone()
            if not trade:
                logger.error(f"Trade {trade_id} not found")
                return False
            
            symbol, entry_price, quantity, entry_time, broker = trade
            
            # Calculate profit/loss
            profit_loss = (exit_price - entry_price) * quantity
            profit_pct = ((exit_price - entry_price) / entry_price) * 100
            
            # Calculate hold duration
            entry_dt = datetime.fromisoformat(entry_time)
            exit_dt = datetime.now()
            duration_seconds = int((exit_dt - entry_dt).total_seconds())
            
            # Update trade_history with complete outcome
            cursor.execute("""
                UPDATE trade_history
                SET exit_price = ?,
                    profit_loss = ?,
                    status = 'closed',
                    exit_timestamp = ?,
                    hold_duration_seconds = ?
                WHERE id = ?
            """, (exit_price, profit_loss, exit_dt.isoformat(), duration_seconds, trade_id))
            
            # Store market indicators if provided
            if market_indicators:
                cursor.execute("""
                    INSERT OR REPLACE INTO performance_metrics
                    (trade_id, symbol, profit_pct, exit_reason, indicators_json, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (trade_id, symbol, profit_pct, exit_reason,
                      json.dumps(market_indicators), exit_dt.isoformat()))
            
            db.commit()
            logger.info(f"✅ Recorded outcome for trade {trade_id}: {profit_pct:+.2f}%")
            return True
        
        except Exception as e:
            logger.error(f"Error recording trade outcome: {e}")
            db.rollback()
            return False
        
        finally:
            db.close()
    
    def get_learning_insights(self, symbol: Optional[str] = None, 
                             min_confidence: float = 0.0) -> Dict[str, any]:
        """
        Retrieve learning insights to inform future trading decisions
        
        Args:
            symbol: Optional symbol to get insights for
            min_confidence: Minimum confidence threshold for patterns
        
        Returns:
            Dict with patterns, success rates, and recommendations
        """
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        insights = {
            'patterns': [],
            'top_performers': [],
            'recommendations': []
        }
        
        # Get successful patterns
        if symbol:
            cursor.execute("""
                SELECT pattern_type, success_rate, avg_profit_pct, trade_count
                FROM pattern_insights
                WHERE best_symbols LIKE ? 
                ORDER BY success_rate DESC, avg_profit_pct DESC
                LIMIT 5
            """, (f'%{symbol}%',))
        else:
            cursor.execute("""
                SELECT pattern_type, success_rate, avg_profit_pct, trade_count
                FROM pattern_insights
                ORDER BY success_rate DESC, avg_profit_pct DESC
                LIMIT 10
            """)
        
        patterns = cursor.fetchall()
        for pattern in patterns:
            insights['patterns'].append({
                'type': pattern[0],
                'success_rate': pattern[1],
                'avg_profit': pattern[2],
                'trades': pattern[3]
            })
        
        # Get top performing symbols
        cursor.execute("""
            SELECT symbol, 
                   COUNT(*) as trades,
                   AVG((exit_price - price) / price * 100) as avg_profit,
                   SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
            FROM trade_history
            WHERE status = 'closed' AND exit_price IS NOT NULL
            GROUP BY symbol
            HAVING trades >= 3
            ORDER BY win_rate DESC, avg_profit DESC
            LIMIT 10
        """)
        
        top_symbols = cursor.fetchall()
        for row in top_symbols:
            insights['top_performers'].append({
                'symbol': row[0],
                'trades': row[1],
                'avg_profit_pct': row[2],
                'win_rate': row[3]
            })
        
        # Generate recommendations
        if insights['patterns']:
            best_pattern = insights['patterns'][0]
            if best_pattern['success_rate'] > 70:
                insights['recommendations'].append(
                    f"Prioritize {best_pattern['type']} trades - {best_pattern['success_rate']:.0f}% success rate"
                )
        
        if insights['top_performers']:
            best_symbol = insights['top_performers'][0]
            if best_symbol['win_rate'] > 60:
                insights['recommendations'].append(
                    f"Focus on {best_symbol['symbol']} - {best_symbol['win_rate']:.0f}% win rate"
                )
        
        db.close()
        return insights
    
    def apply_learning_to_decision(self, symbol: str, base_confidence: float,
                                   indicators: Dict) -> Tuple[float, List[str]]:
        """
        Apply learning insights to adjust trade confidence
        
        Args:
            symbol: Trading symbol
            base_confidence: Initial confidence from AI systems
            indicators: Current market indicators
        
        Returns:
            Tuple of (adjusted_confidence, reasoning_list)
        """
        insights = self.get_learning_insights(symbol=symbol)
        
        adjusted_confidence = base_confidence
        reasoning = []
        
        # Boost confidence for historically successful symbols
        for performer in insights.get('top_performers', []):
            if performer['symbol'] == symbol:
                if performer['win_rate'] > 70:
                    boost = 0.10
                    adjusted_confidence = min(1.0, adjusted_confidence + boost)
                    reasoning.append(f"📊 {symbol} has {performer['win_rate']:.0f}% win rate (+{boost*100:.0f}%)")
                elif performer['win_rate'] < 40:
                    penalty = 0.15
                    adjusted_confidence = max(0.0, adjusted_confidence - penalty)
                    reasoning.append(f"⚠️ {symbol} has low {performer['win_rate']:.0f}% win rate (-{penalty*100:.0f}%)")
        
        # Apply pattern-based adjustments
        for pattern in insights.get('patterns', [])[:3]:  # Top 3 patterns
            if pattern['success_rate'] > 75 and pattern['avg_profit'] > 5:
                boost = 0.05
                adjusted_confidence = min(1.0, adjusted_confidence + boost)
                reasoning.append(f"🧠 {pattern['type']} pattern identified (+{boost*100:.0f}%)")
        
        return adjusted_confidence, reasoning
