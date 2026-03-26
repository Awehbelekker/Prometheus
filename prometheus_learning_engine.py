"""
🧠 PROMETHEUS LEARNING ENGINE
Advanced pattern recognition and trade optimization system

Features:
1. Pattern Recognition - Identifies successful trade patterns
2. Trade Optimization - Analyzes optimal vs actual exit points
3. Historical Fetching - Gets price data for optimization analysis
4. Learning Insights - Generates actionable insights
5. Performance Attribution - Tracks which strategies work best
"""

import sqlite3
import json
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class TradeOptimization:
    """Analysis of actual vs optimal trade execution"""
    symbol: str
    entry_date: str
    exit_date: str
    entry_price: float
    actual_exit_price: float
    actual_profit_pct: float
    optimal_exit_price: float
    optimal_profit_pct: float
    missed_opportunity_pct: float
    exit_timing: str  # 'early', 'optimal', 'late'
    max_price_after_entry: float
    min_price_after_entry: float
    max_potential_profit_pct: float
    max_potential_loss_pct: float
    hold_duration_hours: float


@dataclass
class PatternInsight:
    """Successful trading pattern identified"""
    pattern_type: str  # 'RSI_OVERSOLD', 'MACD_CROSSOVER', 'VOLUME_SPIKE', etc.
    success_rate: float
    avg_profit_pct: float
    trade_count: int
    avg_hold_duration_hours: float
    best_symbols: List[str]
    conditions: Dict[str, any]
    created_at: str


class PrometheusLearningEngine:
    """
    Advanced learning system that analyzes trading history to improve future decisions
    """
    
    def __init__(self, db_path='prometheus_learning.db'):
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create learning tables if they don't exist"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Trade optimization analysis table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_optimization (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER,
                symbol TEXT,
                entry_date TEXT,
                exit_date TEXT,
                entry_price REAL,
                actual_exit_price REAL,
                actual_profit_pct REAL,
                optimal_exit_price REAL,
                optimal_profit_pct REAL,
                missed_opportunity_pct REAL,
                exit_timing TEXT,
                max_price_after_entry REAL,
                min_price_after_entry REAL,
                max_potential_profit_pct REAL,
                max_potential_loss_pct REAL,
                hold_duration_hours REAL,
                analysis_date TEXT,
                FOREIGN KEY(trade_id) REFERENCES trade_history(id)
            )
        """)
        
        # Pattern insights table - Create new one with proper schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                success_rate REAL,
                avg_profit_pct REAL,
                trade_count INTEGER,
                avg_hold_duration_hours REAL,
                best_symbols TEXT,
                conditions TEXT,
                created_at TEXT
            )
        """)
        
        db.commit()
        db.close()
    
    def fetch_historical_prices(self, symbol: str, start_date: datetime, 
                                end_date: datetime, interval='1h') -> Optional[pd.DataFrame]:
        """
        Fetch historical price data for optimization analysis
        
        Args:
            symbol: Trading symbol (e.g., 'BTC-USD', 'AAPL')
            start_date: Start date for historical data
            end_date: End date for historical data
            interval: Data interval ('1m', '5m', '1h', '1d')
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Convert crypto symbols for yfinance
            yf_symbol = symbol.replace('/', '-')
            
            # Fetch data
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if df.empty:
                logger.warning(f"No historical data found for {symbol}")
                return None
            
            return df
        
        except Exception as e:
            logger.error(f"Error fetching historical prices for {symbol}: {e}")
            return None
    
    def analyze_trade_optimization(self, trade_id: int) -> Optional[TradeOptimization]:
        """
        Analyze a closed trade to find optimal vs actual exit points
        
        Args:
            trade_id: ID from trade_history table
        
        Returns:
            TradeOptimization object with analysis results
        """
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Get trade details
        cursor.execute("""
            SELECT symbol, timestamp, exit_timestamp, price, exit_price,
                   profit_loss, quantity, hold_duration_seconds
            FROM trade_history
            WHERE id = ? AND status = 'closed' AND exit_price IS NOT NULL
        """, (trade_id,))
        
        trade = cursor.fetchone()
        db.close()
        
        if not trade:
            logger.warning(f"Trade {trade_id} not found or not closed")
            return None
        
        symbol, entry_ts, exit_ts, entry_price, exit_price, profit_loss, quantity, duration = trade
        
        # Parse dates
        entry_date = datetime.fromisoformat(entry_ts)
        exit_date = datetime.fromisoformat(exit_ts) if exit_ts else datetime.now()
        
        # Fetch historical prices
        # Add buffer to see what happened after exit
        end_date = exit_date + timedelta(hours=24)
        prices = self.fetch_historical_prices(symbol, entry_date, end_date, interval='1h')
        
        if prices is None or prices.empty:
            logger.warning(f"No price data available for {symbol}")
            return None
        
        # Calculate actual profit
        actual_profit_pct = ((exit_price - entry_price) / entry_price) * 100
        
        # Find optimal exit (highest price after entry)
        optimal_exit_price = prices['High'].max()
        optimal_profit_pct = ((optimal_exit_price - entry_price) / entry_price) * 100
        
        # Find worst case (lowest price after entry)
        min_price = prices['Low'].min()
        max_potential_loss_pct = ((min_price - entry_price) / entry_price) * 100
        
        # Determine exit timing
        missed_opportunity = optimal_profit_pct - actual_profit_pct
        
        if actual_profit_pct >= optimal_profit_pct * 0.95:  # Within 5% of optimal
            exit_timing = 'optimal'
        elif actual_profit_pct >= optimal_profit_pct * 0.70:  # Within 70%
            exit_timing = 'good'
        elif exit_price < entry_price and optimal_profit_pct > 5:
            exit_timing = 'too_early'
        elif actual_profit_pct < optimal_profit_pct * 0.50:
            exit_timing = 'early'
        else:
            exit_timing = 'acceptable'
        
        # Calculate hold duration
        hold_hours = duration / 3600 if duration else 0
        
        optimization = TradeOptimization(
            symbol=symbol,
            entry_date=entry_ts,
            exit_date=exit_ts,
            entry_price=entry_price,
            actual_exit_price=exit_price,
            actual_profit_pct=actual_profit_pct,
            optimal_exit_price=optimal_exit_price,
            optimal_profit_pct=optimal_profit_pct,
            missed_opportunity_pct=missed_opportunity,
            exit_timing=exit_timing,
            max_price_after_entry=optimal_exit_price,
            min_price_after_entry=min_price,
            max_potential_profit_pct=optimal_profit_pct,
            max_potential_loss_pct=max_potential_loss_pct,
            hold_duration_hours=hold_hours
        )
        
        # Save to database
        self._save_optimization(trade_id, optimization)
        
        return optimization
    
    def _save_optimization(self, trade_id: int, opt: TradeOptimization):
        """Save optimization analysis to database"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO trade_optimization
            (trade_id, symbol, entry_date, exit_date, entry_price, actual_exit_price,
             actual_profit_pct, optimal_exit_price, optimal_profit_pct, missed_opportunity_pct,
             exit_timing, max_price_after_entry, min_price_after_entry, 
             max_potential_profit_pct, max_potential_loss_pct, hold_duration_hours, analysis_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (trade_id, opt.symbol, opt.entry_date, opt.exit_date, opt.entry_price,
              opt.actual_exit_price, opt.actual_profit_pct, opt.optimal_exit_price,
              opt.optimal_profit_pct, opt.missed_opportunity_pct, opt.exit_timing,
              opt.max_price_after_entry, opt.min_price_after_entry, 
              opt.max_potential_profit_pct, opt.max_potential_loss_pct,
              opt.hold_duration_hours, datetime.now().isoformat()))
        
        db.commit()
        db.close()
    
    def analyze_all_closed_trades(self, limit: int = None) -> Dict[str, any]:
        """
        Analyze all closed trades for optimization insights
        
        Returns:
            Summary statistics and insights
        """
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        query = """
            SELECT id FROM trade_history 
            WHERE status = 'closed' AND exit_price IS NOT NULL
            ORDER BY exit_timestamp DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        trade_ids = [row[0] for row in cursor.fetchall()]
        db.close()
        
        logger.info(f"Analyzing {len(trade_ids)} closed trades...")
        
        results = []
        for trade_id in trade_ids:
            opt = self.analyze_trade_optimization(trade_id)
            if opt:
                results.append(opt)
        
        if not results:
            return {'error': 'No trades analyzed'}
        
        # Calculate summary statistics
        avg_missed_opportunity = np.mean([r.missed_opportunity_pct for r in results])
        optimal_exits = len([r for r in results if r.exit_timing == 'optimal'])
        early_exits = len([r for r in results if 'early' in r.exit_timing])
        
        summary = {
            'total_analyzed': len(results),
            'optimal_exits': optimal_exits,
            'early_exits': early_exits,
            'optimal_exit_rate': optimal_exits / len(results) * 100,
            'avg_missed_opportunity_pct': avg_missed_opportunity,
            'total_missed_profit': sum([r.missed_opportunity_pct for r in results]),
            'best_exit_timing': max(results, key=lambda r: r.actual_profit_pct).symbol if results else None,
            'worst_exit_timing': min(results, key=lambda r: r.actual_profit_pct).symbol if results else None
        }
        
        logger.info(f"✅ Analysis complete: {optimal_exits}/{len(results)} optimal exits ({summary['optimal_exit_rate']:.1f}%)")
        logger.info(f"📊 Avg missed opportunity: {avg_missed_opportunity:.2f}%")
        
        return summary
    
    def identify_successful_patterns(self, min_profit_pct: float = 5.0) -> List[PatternInsight]:
        """
        Identify patterns in successful trades
        
        Args:
            min_profit_pct: Minimum profit percentage to consider trade successful
        
        Returns:
            List of identified patterns
        """
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Get successful trades
        cursor.execute("""
            SELECT symbol, confidence, reasoning, profit_loss, price, 
                   hold_duration_seconds, timestamp
            FROM trade_history
            WHERE status = 'closed' 
              AND profit_loss > 0
              AND ((exit_price - price) / price * 100) >= ?
        """, (min_profit_pct,))
        
        successful_trades = cursor.fetchall()
        db.close()
        
        if not successful_trades:
            logger.warning("No successful trades found")
            return []
        
        # Group by confidence ranges
        high_confidence_trades = [t for t in successful_trades if t[1] > 0.75]
        medium_confidence_trades = [t for t in successful_trades if 0.50 < t[1] <= 0.75]
        
        patterns = []
        
        # Pattern 1: High confidence pattern
        if high_confidence_trades:
            avg_profit = np.mean([t[3] for t in high_confidence_trades])
            avg_hold = np.mean([t[5]/3600 if t[5] else 0 for t in high_confidence_trades])
            symbols = list(set([t[0] for t in high_confidence_trades]))
            
            pattern = PatternInsight(
                pattern_type='HIGH_CONFIDENCE',
                success_rate=len(high_confidence_trades) / len(successful_trades) * 100,
                avg_profit_pct=avg_profit / np.mean([t[4] for t in high_confidence_trades]) * 100,
                trade_count=len(high_confidence_trades),
                avg_hold_duration_hours=avg_hold,
                best_symbols=symbols[:5],
                conditions={'min_confidence': 0.75},
                created_at=datetime.now().isoformat()
            )
            patterns.append(pattern)
            self._save_pattern(pattern)
        
        # Pattern 2: Quick profit pattern (hold < 24 hours)
        quick_trades = [t for t in successful_trades if t[5] and t[5] < 86400]
        if quick_trades:
            avg_profit = np.mean([t[3] for t in quick_trades])
            avg_hold = np.mean([t[5]/3600 for t in quick_trades])
            
            pattern = PatternInsight(
                pattern_type='QUICK_PROFIT',
                success_rate=len(quick_trades) / len(successful_trades) * 100,
                avg_profit_pct=avg_profit / np.mean([t[4] for t in quick_trades]) * 100,
                trade_count=len(quick_trades),
                avg_hold_duration_hours=avg_hold,
                best_symbols=list(set([t[0] for t in quick_trades]))[:5],
                conditions={'max_hold_hours': 24},
                created_at=datetime.now().isoformat()
            )
            patterns.append(pattern)
            self._save_pattern(pattern)
        
        # Pattern 3: Symbol-specific success
        symbol_profits = {}
        for trade in successful_trades:
            symbol = trade[0]
            profit_pct = (trade[3] / trade[4]) * 100
            if symbol not in symbol_profits:
                symbol_profits[symbol] = []
            symbol_profits[symbol].append(profit_pct)
        
        # Find symbols with consistent success
        for symbol, profits in symbol_profits.items():
            if len(profits) >= 3:  # At least 3 successful trades
                avg_profit = np.mean(profits)
                if avg_profit >= min_profit_pct:
                    pattern = PatternInsight(
                        pattern_type=f'SYMBOL_SUCCESS_{symbol}',
                        success_rate=100.0,  # All analyzed are successful
                        avg_profit_pct=avg_profit,
                        trade_count=len(profits),
                        avg_hold_duration_hours=0,
                        best_symbols=[symbol],
                        conditions={'symbol': symbol, 'min_trades': 3},
                        created_at=datetime.now().isoformat()
                    )
                    patterns.append(pattern)
                    self._save_pattern(pattern)
        
        logger.info(f"🧠 Identified {len(patterns)} successful patterns")
        return patterns
    
    def _save_pattern(self, pattern: PatternInsight):
        """Save pattern insight to database"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO pattern_insights
            (pattern_type, success_rate, avg_profit_pct, trade_count, 
             avg_hold_duration_hours, best_symbols, conditions, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (pattern.pattern_type, pattern.success_rate, pattern.avg_profit_pct,
              pattern.trade_count, pattern.avg_hold_duration_hours,
              json.dumps(pattern.best_symbols), json.dumps(pattern.conditions),
              pattern.created_at))
        
        db.commit()
        db.close()
    
    def get_top_trades_analysis(self, limit: int = 20) -> List[Dict]:
        """
        Get top performing trades with optimization analysis
        
        Returns:
            List of trade analyses sorted by profit
        """
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT th.id, th.symbol, th.price, th.exit_price, 
                   ((th.exit_price - th.price) / th.price * 100) as profit_pct,
                   th.timestamp, th.exit_timestamp, th.hold_duration_seconds,
                   topt.optimal_profit_pct, topt.missed_opportunity_pct, topt.exit_timing
            FROM trade_history th
            LEFT JOIN trade_optimization topt ON th.id = topt.trade_id
            WHERE th.status = 'closed' AND th.exit_price IS NOT NULL
            ORDER BY profit_pct DESC
            LIMIT ?
        """, (limit,))
        
        trades = []
        for row in cursor.fetchall():
            trades.append({
                'id': row[0],
                'symbol': row[1],
                'entry_price': row[2],
                'exit_price': row[3],
                'actual_profit_pct': row[4],
                'entry_date': row[5],
                'exit_date': row[6],
                'hold_hours': row[7] / 3600 if row[7] else 0,
                'optimal_profit_pct': row[8] or 0,
                'missed_opportunity_pct': row[9] or 0,
                'exit_timing': row[10] or 'unknown'
            })
        
        db.close()
        return trades
    
    def get_learning_recommendations(self) -> Dict[str, any]:
        """
        Generate actionable recommendations based on learning insights
        
        Returns:
            Dictionary with recommendations for improving trading
        """
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        recommendations = {
            'generated_at': datetime.now().isoformat(),
            'insights': [],
            'action_items': []
        }
        
        # Get recent patterns
        cursor.execute("""
            SELECT pattern_type, success_rate, avg_profit_pct, trade_count, best_symbols
            FROM pattern_insights
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        patterns = cursor.fetchall()
        
        for pattern in patterns:
            pattern_type, success_rate, avg_profit, count, symbols_json = pattern
            symbols = json.loads(symbols_json)
            
            recommendations['insights'].append({
                'pattern': pattern_type,
                'success_rate': f"{success_rate:.1f}%",
                'avg_profit': f"{avg_profit:.2f}%",
                'trades': count,
                'best_symbols': symbols
            })
            
            # Generate action items
            if success_rate > 70 and count >= 5:
                recommendations['action_items'].append(
                    f"✅ Continue using {pattern_type} strategy - {success_rate:.0f}% success rate"
                )
            
            if 'HIGH_CONFIDENCE' in pattern_type and avg_profit > 5:
                recommendations['action_items'].append(
                    f"💰 High confidence trades averaging {avg_profit:.1f}% profit - prioritize these"
                )
            
            if 'SYMBOL_SUCCESS' in pattern_type:
                symbol = pattern_type.split('_')[-1]
                recommendations['action_items'].append(
                    f"🎯 {symbol} shows consistent profitability - consider increasing position size"
                )
        
        # Get exit timing insights
        cursor.execute("""
            SELECT AVG(missed_opportunity_pct), 
                   COUNT(CASE WHEN exit_timing LIKE '%early%' THEN 1 END) * 100.0 / COUNT(*) as early_pct
            FROM trade_optimization
        """)
        
        result = cursor.fetchone()
        if result and result[0]:
            avg_missed, early_pct = result
            
            if avg_missed > 5:
                recommendations['action_items'].append(
                    f"⚠️ Average missed opportunity: {avg_missed:.1f}% - consider adjusting exit strategy"
                )
            
            if early_pct > 40:
                recommendations['action_items'].append(
                    f"⏰ {early_pct:.0f}% of trades exited early - consider longer hold times or trailing stops"
                )
        
        db.close()
        return recommendations


if __name__ == '__main__':
    # Demo usage
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    logger.info("🧠 Prometheus Learning Engine - Starting Analysis")
    
    engine = PrometheusLearningEngine()
    
    # Step 1: Analyze closed trades for optimization
    logger.info("\n" + "="*60)
    logger.info("STEP 1: Analyzing closed trades for optimization")
    logger.info("="*60)
    summary = engine.analyze_all_closed_trades(limit=20)
    print(json.dumps(summary, indent=2))
    
    # Step 2: Identify successful patterns
    logger.info("\n" + "="*60)
    logger.info("STEP 2: Identifying successful patterns")
    logger.info("="*60)
    patterns = engine.identify_successful_patterns(min_profit_pct=3.0)
    for pattern in patterns:
        print(f"\n  {pattern.pattern_type}:")
        print(f"    Success Rate: {pattern.success_rate:.1f}%")
        print(f"    Avg Profit: {pattern.avg_profit_pct:.2f}%")
        print(f"    Trades: {pattern.trade_count}")
        print(f"    Best Symbols: {', '.join(pattern.best_symbols)}")
    
    # Step 3: Get recommendations
    logger.info("\n" + "="*60)
    logger.info("STEP 3: Generating recommendations")
    logger.info("="*60)
    recommendations = engine.get_learning_recommendations()
    print(json.dumps(recommendations, indent=2))
