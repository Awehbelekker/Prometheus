"""
TAF Fee Impact Simulator
Interactive simulator to test different trading strategies against new TAF fee structure
"""

import json
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import random

@dataclass
class SimulationScenario:
    """Trading scenario for simulation"""
    name: str
    description: str
    trades_per_day: int
    avg_trade_size: int
    size_variance: float  # 0.0 to 1.0
    symbols: List[str]
    duration_days: int

@dataclass
class SimulationResult:
    """Results of TAF fee simulation"""
    scenario_name: str
    total_trades: int
    total_volume: int
    current_structure_fees: float
    new_structure_fees: float
    fee_difference: float
    fee_increase_percentage: float
    affected_trades: int
    daily_breakdown: List[Dict]
    optimization_savings: float
    recommendations: List[str]

class TAFSimulator:
    """Simulate TAF fee impact under different trading scenarios"""
    
    def __init__(self):
        self.TAF_RATE = 0.000166  # $0.000166 per share
        self.MAX_TAF_PER_TRADE = 8.30  # $8.30 maximum per trade
        self.THRESHOLD_SHARES = 50000  # Shares where max fee kicks in
        
        # Predefined scenarios
        self.scenarios = {
            'conservative': SimulationScenario(
                name='Conservative Trading',
                description='Low frequency, moderate position sizes',
                trades_per_day=5,
                avg_trade_size=25000,
                size_variance=0.3,
                symbols=['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
                duration_days=30
            ),
            'aggressive': SimulationScenario(
                name='Aggressive High-Volume',
                description='High frequency, large position sizes',
                trades_per_day=20,
                avg_trade_size=75000,
                size_variance=0.5,
                symbols=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX'],
                duration_days=30
            ),
            'day_trading': SimulationScenario(
                name='Day Trading Strategy',
                description='Very high frequency, smaller positions',
                trades_per_day=50,
                avg_trade_size=15000,
                size_variance=0.4,
                symbols=['SPY', 'QQQ', 'IWM', 'AAPL', 'TSLA'],
                duration_days=30
            ),
            'swing_trading': SimulationScenario(
                name='Swing Trading',
                description='Medium frequency, large positions',
                trades_per_day=3,
                avg_trade_size=100000,
                size_variance=0.6,
                symbols=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
                duration_days=30
            )
        }
    
    def generate_trades(self, scenario: SimulationScenario) -> List[Dict]:
        """Generate synthetic trades based on scenario parameters"""
        trades = []
        
        for day in range(scenario.duration_days):
            # Vary trades per day slightly
            daily_trades = max(1, int(scenario.trades_per_day * (0.7 + random.random() * 0.6)))
            
            for trade_num in range(daily_trades):
                # Generate trade size with variance
                size_multiplier = 1.0 + (random.random() - 0.5) * 2 * scenario.size_variance
                trade_size = max(100, int(scenario.avg_trade_size * size_multiplier))
                
                # Only simulate sell trades (TAF applies to sells only)
                trade = {
                    'day': day + 1,
                    'trade_id': f"T{day+1:02d}{trade_num+1:02d}",
                    'symbol': random.choice(scenario.symbols),
                    'side': 'sell',
                    'quantity': trade_size,
                    'price': random.uniform(50, 500),  # Random price for value calculation
                    'timestamp': datetime.now() + timedelta(days=day, hours=random.randint(9, 16))
                }
                trade['value'] = trade['quantity'] * trade['price']
                trades.append(trade)
        
        return trades
    
    def calculate_current_structure_fees(self, trades: List[Dict]) -> Tuple[float, List[Dict]]:
        """Calculate TAF fees under current structure (daily cumulative cap)"""
        daily_breakdown = {}
        
        # Group trades by day
        for trade in trades:
            day = trade['day']
            if day not in daily_breakdown:
                daily_breakdown[day] = {'trades': 0, 'volume': 0, 'fee': 0}
            
            daily_breakdown[day]['trades'] += 1
            daily_breakdown[day]['volume'] += trade['quantity']
        
        # Calculate daily fees with cumulative cap
        total_fees = 0
        breakdown_list = []
        
        for day, data in daily_breakdown.items():
            daily_fee = min(data['volume'] * self.TAF_RATE, self.MAX_TAF_PER_TRADE)
            data['fee'] = daily_fee
            total_fees += daily_fee
            
            breakdown_list.append({
                'day': day,
                'trades': data['trades'],
                'volume': data['volume'],
                'fee': daily_fee,
                'structure': 'current'
            })
        
        return total_fees, breakdown_list
    
    def calculate_new_structure_fees(self, trades: List[Dict]) -> Tuple[float, List[Dict]]:
        """Calculate TAF fees under new structure (per-trade cap)"""
        daily_breakdown = {}
        total_fees = 0
        
        # Group trades by day for breakdown
        for trade in trades:
            day = trade['day']
            if day not in daily_breakdown:
                daily_breakdown[day] = {'trades': 0, 'volume': 0, 'fee': 0}
            
            # Calculate per-trade fee
            trade_fee = min(trade['quantity'] * self.TAF_RATE, self.MAX_TAF_PER_TRADE)
            total_fees += trade_fee
            
            daily_breakdown[day]['trades'] += 1
            daily_breakdown[day]['volume'] += trade['quantity']
            daily_breakdown[day]['fee'] += trade_fee
        
        breakdown_list = []
        for day, data in daily_breakdown.items():
            breakdown_list.append({
                'day': day,
                'trades': data['trades'],
                'volume': data['volume'],
                'fee': data['fee'],
                'structure': 'new'
            })
        
        return total_fees, breakdown_list
    
    def calculate_optimization_potential(self, trades: List[Dict]) -> float:
        """Calculate potential savings with order optimization"""
        savings = 0
        
        for trade in trades:
            if trade['quantity'] > self.THRESHOLD_SHARES:
                # Current fee for large trade
                current_fee = self.MAX_TAF_PER_TRADE
                
                # Optimized fee (split into smaller chunks)
                num_chunks = (trade['quantity'] + self.THRESHOLD_SHARES - 1) // self.THRESHOLD_SHARES
                optimized_fee = num_chunks * self.MAX_TAF_PER_TRADE
                
                # In this case, keeping as single trade is better
                savings += max(0, optimized_fee - current_fee)
        
        return abs(savings)  # Return absolute value for display
    
    def generate_recommendations(self, result: SimulationResult) -> List[str]:
        """Generate optimization recommendations based on simulation results"""
        recommendations = []
        
        impact_percentage = result.fee_increase_percentage
        affected_percentage = (result.affected_trades / result.total_trades) * 100
        
        if impact_percentage > 50:
            recommendations.append("🚨 HIGH IMPACT: Fee increase >50% - immediate optimization required")
        elif impact_percentage > 20:
            recommendations.append("[WARNING]️ MODERATE IMPACT: Consider optimization strategies")
        else:
            recommendations.append("[CHECK] LOW IMPACT: Current strategy relatively unaffected")
        
        if affected_percentage > 30:
            recommendations.append(f"📊 {affected_percentage:.1f}% of trades exceed 50K shares threshold")
            recommendations.append("🔧 Consider splitting large orders to minimize fees")
        
        if result.total_volume > 10000000:  # 10M+ shares
            recommendations.append("📈 High volume detected - implement automated order sizing")
        
        recommendations.append("💡 Test optimization strategies in paper trading first")
        recommendations.append("📅 Implement changes before October 4, 2025")
        
        return recommendations
    
    def run_simulation(self, scenario_name: str) -> SimulationResult:
        """Run complete TAF fee simulation for given scenario"""
        if scenario_name not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        scenario = self.scenarios[scenario_name]
        trades = self.generate_trades(scenario)
        
        # Calculate fees under both structures
        current_fees, current_breakdown = self.calculate_current_structure_fees(trades)
        new_fees, new_breakdown = self.calculate_new_structure_fees(trades)
        
        # Calculate metrics
        fee_difference = new_fees - current_fees
        fee_increase_pct = (fee_difference / current_fees * 100) if current_fees > 0 else 0
        affected_trades = len([t for t in trades if t['quantity'] > self.THRESHOLD_SHARES])
        total_volume = sum(t['quantity'] for t in trades)
        optimization_savings = self.calculate_optimization_potential(trades)
        
        # Create result
        result = SimulationResult(
            scenario_name=scenario.name,
            total_trades=len(trades),
            total_volume=total_volume,
            current_structure_fees=current_fees,
            new_structure_fees=new_fees,
            fee_difference=fee_difference,
            fee_increase_percentage=fee_increase_pct,
            affected_trades=affected_trades,
            daily_breakdown=current_breakdown + new_breakdown,
            optimization_savings=optimization_savings,
            recommendations=[]
        )
        
        result.recommendations = self.generate_recommendations(result)
        
        return result
    
    def compare_scenarios(self, scenario_names: List[str]) -> Dict:
        """Compare multiple scenarios side by side"""
        results = {}
        
        for scenario_name in scenario_names:
            results[scenario_name] = self.run_simulation(scenario_name)
        
        # Generate comparison summary
        comparison = {
            'scenarios': results,
            'summary': {
                'highest_impact': max(results.keys(), key=lambda x: results[x].fee_increase_percentage),
                'lowest_impact': min(results.keys(), key=lambda x: results[x].fee_increase_percentage),
                'highest_fees': max(results.keys(), key=lambda x: results[x].new_structure_fees),
                'most_affected_trades': max(results.keys(), key=lambda x: results[x].affected_trades)
            }
        }
        
        return comparison
    
    def export_results(self, result: SimulationResult, filename: str = None) -> str:
        """Export simulation results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"taf_simulation_{result.scenario_name.lower().replace(' ', '_')}_{timestamp}.json"
        
        # Convert result to dictionary for JSON serialization
        result_dict = asdict(result)
        
        with open(filename, 'w') as f:
            json.dump(result_dict, f, indent=2, default=str)
        
        return filename

def main():
    """Run TAF fee simulation demonstration"""
    simulator = TAFSimulator()
    
    print("🎯 TAF Fee Impact Simulator")
    print("=" * 50)
    
    # Run individual scenario
    print("\n📊 INDIVIDUAL SCENARIO ANALYSIS")
    result = simulator.run_simulation('aggressive')
    
    print(f"Scenario: {result.scenario_name}")
    print(f"Total Trades: {result.total_trades:,}")
    print(f"Total Volume: {result.total_volume:,} shares")
    print(f"Current Structure Fees: ${result.current_structure_fees:.2f}")
    print(f"New Structure Fees: ${result.new_structure_fees:.2f}")
    print(f"Fee Increase: ${result.fee_difference:.2f} ({result.fee_increase_percentage:.1f}%)")
    print(f"Affected Trades: {result.affected_trades} ({result.affected_trades/result.total_trades*100:.1f}%)")
    
    print("\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"{i}. {rec}")
    
    # Compare all scenarios
    print("\n🔍 SCENARIO COMPARISON")
    comparison = simulator.compare_scenarios(['conservative', 'aggressive', 'day_trading', 'swing_trading'])
    
    print(f"Highest Impact: {comparison['summary']['highest_impact']}")
    print(f"Lowest Impact: {comparison['summary']['lowest_impact']}")
    print(f"Highest Fees: {comparison['summary']['highest_fees']}")
    
    # Export results
    filename = simulator.export_results(result)
    print(f"\n📄 Results exported to: {filename}")

if __name__ == "__main__":
    main()
