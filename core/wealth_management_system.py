"""
💰 PROMETHEUS Wealth Management System
Advanced wealth tracking and compound growth calculation system
"""

import sqlite3
import json
import logging
import math
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class WealthMetricType(Enum):
    TOTAL_VALUE = "total_value"
    REALIZED_GAINS = "realized_gains"
    UNREALIZED_GAINS = "unrealized_gains"
    DIVIDENDS = "dividends"
    FEES_PAID = "fees_paid"
    DEPOSITS = "deposits"
    WITHDRAWALS = "withdrawals"

@dataclass
class WealthSnapshot:
    user_id: str
    portfolio_type: str
    snapshot_date: date
    total_value: float
    allocated_capital: float
    cash_balance: float
    positions_value: float
    realized_pnl: float
    unrealized_pnl: float
    total_return: float
    total_return_percent: float
    daily_return: float
    daily_return_percent: float
    compound_growth_rate: float
    sharpe_ratio: float
    max_drawdown: float
    volatility: float

@dataclass
class AllocationHistory:
    allocation_id: str
    user_id: str
    amount: float
    allocation_type: str  # 'initial', 'additional', 'withdrawal'
    allocated_by: str
    allocation_date: datetime
    notes: str
    is_active: bool

@dataclass
class PerformanceMetrics:
    user_id: str
    portfolio_type: str
    period_start: date
    period_end: date
    starting_value: float
    ending_value: float
    total_return: float
    total_return_percent: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    calmar_ratio: float

class WealthManagementSystem:
    """
    Comprehensive wealth management and performance tracking system
    """
    
    def __init__(self, db_path: str = "wealth_management.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize wealth management database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Daily wealth snapshots
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wealth_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    portfolio_type TEXT NOT NULL,
                    snapshot_date DATE NOT NULL,
                    total_value REAL NOT NULL,
                    allocated_capital REAL NOT NULL,
                    cash_balance REAL NOT NULL,
                    positions_value REAL NOT NULL,
                    realized_pnl REAL DEFAULT 0,
                    unrealized_pnl REAL DEFAULT 0,
                    total_return REAL DEFAULT 0,
                    total_return_percent REAL DEFAULT 0,
                    daily_return REAL DEFAULT 0,
                    daily_return_percent REAL DEFAULT 0,
                    compound_growth_rate REAL DEFAULT 0,
                    sharpe_ratio REAL DEFAULT 0,
                    max_drawdown REAL DEFAULT 0,
                    volatility REAL DEFAULT 0,
                    UNIQUE(user_id, portfolio_type, snapshot_date)
                )
            """)
            
            # Allocation history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS allocation_history (
                    allocation_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    allocation_type TEXT NOT NULL,
                    allocated_by TEXT NOT NULL,
                    allocation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Performance benchmarks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_benchmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    portfolio_type TEXT NOT NULL,
                    benchmark_name TEXT NOT NULL,
                    benchmark_value REAL NOT NULL,
                    benchmark_date DATE NOT NULL,
                    UNIQUE(user_id, portfolio_type, benchmark_name, benchmark_date)
                )
            """)
            
            # Wealth milestones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wealth_milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    milestone_type TEXT NOT NULL,
                    milestone_value REAL NOT NULL,
                    achieved_date TIMESTAMP,
                    portfolio_type TEXT NOT NULL,
                    notes TEXT
                )
            """)
            
            # Risk metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    portfolio_type TEXT NOT NULL,
                    calculation_date DATE NOT NULL,
                    var_95 REAL,  -- Value at Risk 95%
                    var_99 REAL,  -- Value at Risk 99%
                    expected_shortfall REAL,
                    beta REAL,
                    alpha REAL,
                    correlation_market REAL,
                    UNIQUE(user_id, portfolio_type, calculation_date)
                )
            """)
            
            conn.commit()
            logger.info("Wealth management database initialized")

    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def record_allocation(self, user_id: str, amount: float, allocation_type: str, 
                         allocated_by: str, notes: str = "") -> str:
        """Record a new capital allocation"""
        allocation_id = str(uuid.uuid4())
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO allocation_history
                (allocation_id, user_id, amount, allocation_type, allocated_by, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (allocation_id, user_id, amount, allocation_type, allocated_by, notes))
            conn.commit()
        
        logger.info(f"Recorded ${amount:,.2f} {allocation_type} allocation for user {user_id}")
        return allocation_id

    def create_wealth_snapshot(self, user_id: str, portfolio_type: str, 
                              total_value: float, allocated_capital: float,
                              cash_balance: float, positions_value: float) -> bool:
        """Create daily wealth snapshot with performance calculations"""
        try:
            snapshot_date = date.today()
            
            # Get previous snapshot for calculations
            prev_snapshot = self.get_previous_snapshot(user_id, portfolio_type, snapshot_date)
            
            # Calculate daily returns
            daily_return = 0.0
            daily_return_percent = 0.0
            if prev_snapshot:
                daily_return = total_value - prev_snapshot['total_value']
                if prev_snapshot['total_value'] > 0:
                    daily_return_percent = (daily_return / prev_snapshot['total_value']) * 100
            
            # Calculate total returns
            total_return = total_value - allocated_capital
            total_return_percent = (total_return / allocated_capital) * 100 if allocated_capital > 0 else 0
            
            # Calculate compound growth rate (CAGR)
            compound_growth_rate = self.calculate_compound_growth_rate(user_id, portfolio_type, total_value)
            
            # Calculate risk metrics
            volatility = self.calculate_volatility(user_id, portfolio_type, 30)  # 30-day volatility
            sharpe_ratio = self.calculate_sharpe_ratio(user_id, portfolio_type, 30)
            max_drawdown = self.calculate_max_drawdown(user_id, portfolio_type, 90)  # 90-day max drawdown
            
            # Create snapshot
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO wealth_snapshots
                    (user_id, portfolio_type, snapshot_date, total_value, allocated_capital,
                     cash_balance, positions_value, total_return, total_return_percent,
                     daily_return, daily_return_percent, compound_growth_rate,
                     sharpe_ratio, max_drawdown, volatility)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, portfolio_type, snapshot_date.isoformat(), total_value, allocated_capital,
                    cash_balance, positions_value, total_return, total_return_percent,
                    daily_return, daily_return_percent, compound_growth_rate,
                    sharpe_ratio, max_drawdown, volatility
                ))
                conn.commit()
            
            # Check for wealth milestones
            self.check_wealth_milestones(user_id, portfolio_type, total_value)
            
            logger.info(f"Created wealth snapshot for {user_id}: ${total_value:,.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create wealth snapshot: {e}")
            return False

    def get_previous_snapshot(self, user_id: str, portfolio_type: str, current_date: date) -> Optional[Dict]:
        """Get the most recent snapshot before the current date"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM wealth_snapshots
                WHERE user_id = ? AND portfolio_type = ? AND snapshot_date < ?
                ORDER BY snapshot_date DESC
                LIMIT 1
            """, (user_id, portfolio_type, current_date.isoformat()))
            
            row = cursor.fetchone()
            return dict(row) if row else None

    def calculate_compound_growth_rate(self, user_id: str, portfolio_type: str, current_value: float) -> float:
        """Calculate compound annual growth rate (CAGR)"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT total_value, snapshot_date FROM wealth_snapshots
                    WHERE user_id = ? AND portfolio_type = ?
                    ORDER BY snapshot_date ASC
                    LIMIT 1
                """, (user_id, portfolio_type))
                
                first_snapshot = cursor.fetchone()
                if not first_snapshot:
                    return 0.0
                
                initial_value = first_snapshot['total_value']
                start_date = datetime.fromisoformat(first_snapshot['snapshot_date']).date()
                current_date = date.today()
                
                days_elapsed = (current_date - start_date).days
                if days_elapsed < 1 or initial_value <= 0:
                    return 0.0
                
                years_elapsed = days_elapsed / 365.25
                cagr = (pow(current_value / initial_value, 1 / years_elapsed) - 1) * 100
                
                return cagr
                
        except Exception as e:
            logger.error(f"Failed to calculate CAGR: {e}")
            return 0.0

    def calculate_volatility(self, user_id: str, portfolio_type: str, days: int = 30) -> float:
        """Calculate portfolio volatility (standard deviation of daily returns)"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT daily_return_percent FROM wealth_snapshots
                    WHERE user_id = ? AND portfolio_type = ?
                    AND snapshot_date >= date('now', '-{} days')
                    ORDER BY snapshot_date ASC
                """.format(days), (user_id, portfolio_type))
                
                returns = [row['daily_return_percent'] for row in cursor.fetchall()]
                
                if len(returns) < 2:
                    return 0.0
                
                mean_return = sum(returns) / len(returns)
                variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
                volatility = math.sqrt(variance) * math.sqrt(252)  # Annualized volatility
                
                return volatility
                
        except Exception as e:
            logger.error(f"Failed to calculate volatility: {e}")
            return 0.0

    def calculate_sharpe_ratio(self, user_id: str, portfolio_type: str, days: int = 30) -> float:
        """Calculate Sharpe ratio (risk-adjusted return)"""
        try:
            volatility = self.calculate_volatility(user_id, portfolio_type, days)
            if volatility == 0:
                return 0.0
            
            # Get average daily return
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT AVG(daily_return_percent) as avg_return FROM wealth_snapshots
                    WHERE user_id = ? AND portfolio_type = ?
                    AND snapshot_date >= date('now', '-{} days')
                """.format(days), (user_id, portfolio_type))
                
                result = cursor.fetchone()
                avg_daily_return = result['avg_return'] if result['avg_return'] else 0.0
                
                # Annualize the return
                annualized_return = avg_daily_return * 252
                
                # Assume risk-free rate of 2%
                risk_free_rate = 2.0
                
                sharpe_ratio = (annualized_return - risk_free_rate) / volatility
                return sharpe_ratio
                
        except Exception as e:
            logger.error(f"Failed to calculate Sharpe ratio: {e}")
            return 0.0

    def calculate_max_drawdown(self, user_id: str, portfolio_type: str, days: int = 90) -> float:
        """Calculate maximum drawdown over specified period"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT total_value FROM wealth_snapshots
                    WHERE user_id = ? AND portfolio_type = ?
                    AND snapshot_date >= date('now', '-{} days')
                    ORDER BY snapshot_date ASC
                """.format(days), (user_id, portfolio_type))
                
                values = [row['total_value'] for row in cursor.fetchall()]
                
                if len(values) < 2:
                    return 0.0
                
                max_drawdown = 0.0
                peak = values[0]
                
                for value in values:
                    if value > peak:
                        peak = value
                    
                    drawdown = (peak - value) / peak * 100
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
                
                return max_drawdown
                
        except Exception as e:
            logger.error(f"Failed to calculate max drawdown: {e}")
            return 0.0

    def check_wealth_milestones(self, user_id: str, portfolio_type: str, current_value: float):
        """Check and record wealth milestones"""
        milestones = [10000, 25000, 50000, 100000, 250000, 500000, 1000000, 2500000, 5000000]
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get achieved milestones
            cursor.execute("""
                SELECT milestone_value FROM wealth_milestones
                WHERE user_id = ? AND portfolio_type = ? AND achieved_date IS NOT NULL
            """, (user_id, portfolio_type))
            
            achieved = {row['milestone_value'] for row in cursor.fetchall()}
            
            # Check for new milestones
            for milestone in milestones:
                if milestone not in achieved and current_value >= milestone:
                    cursor.execute("""
                        INSERT INTO wealth_milestones
                        (user_id, milestone_type, milestone_value, achieved_date, portfolio_type)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_id, "wealth_milestone", milestone, datetime.now().isoformat(), portfolio_type))
                    
                    logger.info(f"User {user_id} achieved ${milestone:,.2f} milestone!")
            
            conn.commit()

    def get_wealth_summary(self, user_id: str, portfolio_type: str) -> Dict:
        """Get comprehensive wealth summary for user"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get latest snapshot
            cursor.execute("""
                SELECT * FROM wealth_snapshots
                WHERE user_id = ? AND portfolio_type = ?
                ORDER BY snapshot_date DESC
                LIMIT 1
            """, (user_id, portfolio_type))
            
            latest = cursor.fetchone()
            if not latest:
                return {'error': 'No wealth data available'}
            
            # Get total allocations
            cursor.execute("""
                SELECT SUM(CASE WHEN allocation_type IN ('initial', 'additional') THEN amount ELSE -amount END) as total_allocated
                FROM allocation_history
                WHERE user_id = ? AND is_active = 1
            """, (user_id,))
            
            total_allocated = cursor.fetchone()['total_allocated'] or 0.0
            
            # Get milestones
            cursor.execute("""
                SELECT milestone_value, achieved_date FROM wealth_milestones
                WHERE user_id = ? AND portfolio_type = ? AND achieved_date IS NOT NULL
                ORDER BY milestone_value DESC
            """, (user_id, portfolio_type))
            
            milestones = [{'value': row['milestone_value'], 'date': row['achieved_date']} 
                         for row in cursor.fetchall()]
            
            return {
                'user_id': user_id,
                'portfolio_type': portfolio_type,
                'current_value': latest['total_value'],
                'allocated_capital': total_allocated,
                'total_return': latest['total_return'],
                'total_return_percent': latest['total_return_percent'],
                'compound_growth_rate': latest['compound_growth_rate'],
                'sharpe_ratio': latest['sharpe_ratio'],
                'max_drawdown': latest['max_drawdown'],
                'volatility': latest['volatility'],
                'cash_balance': latest['cash_balance'],
                'positions_value': latest['positions_value'],
                'milestones_achieved': milestones,
                'last_updated': latest['snapshot_date']
            }

    def get_performance_comparison(self, user_id: str, portfolio_type: str, 
                                 benchmark: str = "SPY") -> Dict:
        """Compare user performance against benchmark"""
        # Implementation for benchmark comparison
        # This would integrate with market data to compare against S&P 500, etc.
        pass

# Global instance
wealth_management_system = WealthManagementSystem()
