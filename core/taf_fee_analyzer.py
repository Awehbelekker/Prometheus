"""
TAF Fee Analyzer - Analyze and optimize for FINRA Trading Activity Fee changes
Effective October 4, 2025: Per-trade $8.30 cap instead of daily cumulative cap
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import json
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TAFAnalysis:
    """Results of TAF fee analysis"""
    current_structure_fees: float
    new_structure_fees: float
    fee_increase: float
    fee_increase_percentage: float
    affected_trades: int
    total_trades: int
    recommendations: List[str]
    optimization_potential: float

@dataclass
class TradeRecord:
    """Individual trade record for analysis"""
    timestamp: datetime
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: int
    price: float
    value: float

class TAFFeeAnalyzer:
    """Analyze historical trading data for TAF fee impact"""
    
    def __init__(self, db_path: str = "prometheus_trading.db"):
        self.db_path = db_path
        self.TAF_RATE = 0.000166  # $0.000166 per share
        self.MAX_TAF_PER_TRADE = 8.30  # $8.30 maximum per trade
        self.THRESHOLD_SHARES = 50000  # Shares where max fee kicks in
        
    def get_historical_trades(self, days_back: int = 30) -> List[TradeRecord]:
        """Retrieve historical trading data"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            query = """
            SELECT timestamp, symbol, side, quantity, price, (quantity * price) as value
            FROM trades 
            WHERE timestamp >= ? AND timestamp <= ? AND side = 'sell'
            ORDER BY timestamp DESC
            """
            
            cursor = conn.execute(query, (start_date.isoformat(), end_date.isoformat()))
            trades = []
            
            for row in cursor.fetchall():
                trades.append(TradeRecord(
                    timestamp=datetime.fromisoformat(row[0]),
                    symbol=row[1],
                    side=row[2],
                    quantity=int(row[3]),
                    price=float(row[4]),
                    value=float(row[5])
                ))
            
            conn.close()
            return trades
            
        except Exception as e:
            print(f"Error retrieving trades: {e}")
            # Return sample data for demonstration
            return self._generate_sample_trades(days_back)
    
    def _generate_sample_trades(self, days_back: int) -> List[TradeRecord]:
        """Generate sample trading data for analysis"""
        import random
        
        trades = []
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
        
        for i in range(100):  # Generate 100 sample trades
            timestamp = datetime.now() - timedelta(
                days=random.randint(0, days_back),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Create mix of small and large trades
            if random.random() < 0.3:  # 30% large trades
                quantity = random.randint(40000, 150000)
            else:  # 70% smaller trades
                quantity = random.randint(100, 10000)
            
            price = random.uniform(50, 500)
            
            trades.append(TradeRecord(
                timestamp=timestamp,
                symbol=random.choice(symbols),
                side='sell',
                quantity=quantity,
                price=price,
                value=quantity * price
            ))
        
        return sorted(trades, key=lambda x: x.timestamp, reverse=True)
    
    def calculate_current_taf_fees(self, trades: List[TradeRecord]) -> Dict[str, float]:
        """Calculate TAF fees under current structure (daily cumulative cap)"""
        daily_fees = {}
        
        # Group trades by day
        trades_by_day = {}
        for trade in trades:
            day_key = trade.timestamp.date().isoformat()
            if day_key not in trades_by_day:
                trades_by_day[day_key] = []
            trades_by_day[day_key].append(trade)
        
        total_fees = 0
        for day, day_trades in trades_by_day.items():
            daily_shares = sum(trade.quantity for trade in day_trades)
            daily_fee = min(daily_shares * self.TAF_RATE, self.MAX_TAF_PER_TRADE)
            daily_fees[day] = daily_fee
            total_fees += daily_fee
        
        return {
            'total_fees': total_fees,
            'daily_breakdown': daily_fees,
            'avg_daily_fee': total_fees / len(daily_fees) if daily_fees else 0
        }
    
    def calculate_new_taf_fees(self, trades: List[TradeRecord]) -> Dict[str, float]:
        """Calculate TAF fees under new structure (per-trade cap)"""
        trade_fees = []
        total_fees = 0
        
        for trade in trades:
            if trade.quantity <= self.THRESHOLD_SHARES:
                fee = trade.quantity * self.TAF_RATE
            else:
                fee = self.MAX_TAF_PER_TRADE
            
            trade_fees.append({
                'timestamp': trade.timestamp.isoformat(),
                'symbol': trade.symbol,
                'quantity': trade.quantity,
                'fee': fee
            })
            total_fees += fee
        
        return {
            'total_fees': total_fees,
            'trade_breakdown': trade_fees,
            'avg_trade_fee': total_fees / len(trades) if trades else 0,
            'max_fee_trades': len([t for t in trades if t.quantity > self.THRESHOLD_SHARES])
        }
    
    def analyze_impact(self, days_back: int = 30) -> TAFAnalysis:
        """Perform comprehensive TAF fee impact analysis"""
        trades = self.get_historical_trades(days_back)
        
        if not trades:
            return TAFAnalysis(
                current_structure_fees=0,
                new_structure_fees=0,
                fee_increase=0,
                fee_increase_percentage=0,
                affected_trades=0,
                total_trades=0,
                recommendations=[],
                optimization_potential=0
            )
        
        current_fees = self.calculate_current_taf_fees(trades)
        new_fees = self.calculate_new_taf_fees(trades)
        
        fee_increase = new_fees['total_fees'] - current_fees['total_fees']
        fee_increase_pct = (fee_increase / current_fees['total_fees'] * 100) if current_fees['total_fees'] > 0 else 0
        
        # Count affected trades (those that will pay more under new structure)
        affected_trades = len([t for t in trades if t.quantity > self.THRESHOLD_SHARES])
        
        # Generate recommendations
        recommendations = self._generate_recommendations(trades, fee_increase)
        
        # Calculate optimization potential
        optimization_potential = self._calculate_optimization_potential(trades)
        
        return TAFAnalysis(
            current_structure_fees=current_fees['total_fees'],
            new_structure_fees=new_fees['total_fees'],
            fee_increase=fee_increase,
            fee_increase_percentage=fee_increase_pct,
            affected_trades=affected_trades,
            total_trades=len(trades),
            recommendations=recommendations,
            optimization_potential=optimization_potential
        )
    
    def _generate_recommendations(self, trades: List[TradeRecord], fee_increase: float) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        large_trades = [t for t in trades if t.quantity > self.THRESHOLD_SHARES]
        
        if fee_increase > 100:  # Significant impact
            recommendations.append("[WARNING]️ HIGH IMPACT: Consider implementing order splitting for trades >50,000 shares")
        
        if large_trades:
            avg_large_trade = sum(t.quantity for t in large_trades) / len(large_trades)
            recommendations.append(f"📊 {len(large_trades)} trades >50K shares (avg: {avg_large_trade:,.0f} shares)")
            
            if avg_large_trade > 75000:
                recommendations.append("🔧 Split large orders into 50K share chunks to minimize TAF fees")
        
        if fee_increase > 0:
            recommendations.append(f"💰 Potential savings: ${fee_increase:.2f} with order optimization")
        
        recommendations.append("📈 Monitor trade sizing to stay under 50,000 share threshold when possible")
        recommendations.append("🤖 Consider implementing automated order splitting in trading algorithms")
        
        return recommendations
    
    def _calculate_optimization_potential(self, trades: List[TradeRecord]) -> float:
        """Calculate potential fee savings with optimization"""
        large_trades = [t for t in trades if t.quantity > self.THRESHOLD_SHARES]
        
        current_large_trade_fees = len(large_trades) * self.MAX_TAF_PER_TRADE
        
        # Calculate optimized fees (split into 50K chunks)
        optimized_fees = 0
        for trade in large_trades:
            chunks = (trade.quantity + self.THRESHOLD_SHARES - 1) // self.THRESHOLD_SHARES  # Ceiling division
            chunk_fees = chunks * self.MAX_TAF_PER_TRADE
            optimized_fees += chunk_fees
        
        return max(0, current_large_trade_fees - optimized_fees)
    
    def generate_report(self, days_back: int = 30) -> str:
        """Generate comprehensive TAF analysis report"""
        analysis = self.analyze_impact(days_back)
        
        report = f"""
🏛️ FINRA TAF FEE IMPACT ANALYSIS
{'='*50}
Analysis Period: {days_back} days
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 FINANCIAL IMPACT
Current Structure Fees: ${analysis.current_structure_fees:.2f}
New Structure Fees: ${analysis.new_structure_fees:.2f}
Fee Increase: ${analysis.fee_increase:.2f} ({analysis.fee_increase_percentage:.1f}%)

📈 TRADE ANALYSIS
Total Trades Analyzed: {analysis.total_trades:,}
Affected Trades (>50K shares): {analysis.affected_trades:,}
Impact Percentage: {(analysis.affected_trades/analysis.total_trades*100):.1f}%

💡 OPTIMIZATION POTENTIAL
Potential Savings: ${analysis.optimization_potential:.2f}

🎯 RECOMMENDATIONS
"""
        
        for i, rec in enumerate(analysis.recommendations, 1):
            report += f"{i}. {rec}\n"
        
        report += f"""
[LIGHTNING] NEXT STEPS
1. Implement order splitting for trades >50,000 shares
2. Update trading algorithms with TAF cost calculations
3. Add TAF fee tracking to admin dashboard
4. Test optimization strategies in paper trading
5. Monitor fee impact after October 4, 2025

📅 IMPLEMENTATION TIMELINE
- Now - Oct 4: Test and optimize under current structure
- Oct 4, 2025: New TAF structure takes effect
- Post Oct 4: Monitor and adjust strategies
"""
        
        return report

def main():
    """Run TAF fee analysis"""
    analyzer = TAFFeeAnalyzer()
    
    print("🔍 Analyzing TAF Fee Impact...")
    report = analyzer.generate_report(30)
    print(report)
    
    # Save report to file
    report_path = Path("taf_analysis_report.txt")
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {report_path}")

if __name__ == "__main__":
    main()
