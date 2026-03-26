"""
TAF-Optimized Trading Engine
Optimizes order execution to minimize FINRA TAF fees under new structure
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import math

@dataclass
class OptimizedOrder:
    """Optimized order with TAF considerations"""
    symbol: str
    side: str
    original_quantity: int
    optimized_chunks: List[int]
    estimated_taf_savings: float
    execution_strategy: str

@dataclass
class TAFCalculation:
    """TAF fee calculation results"""
    original_fee: float
    optimized_fee: float
    savings: float
    chunks_needed: int

class TAFOptimizedTradingEngine:
    """Trading engine optimized for TAF fee minimization"""
    
    def __init__(self):
        self.TAF_RATE = 0.000166  # $0.000166 per share
        self.MAX_TAF_PER_TRADE = 8.30  # $8.30 maximum per trade
        self.OPTIMAL_CHUNK_SIZE = 50000  # Shares per chunk to avoid max fee
        self.MIN_CHUNK_SIZE = 1000  # Minimum viable chunk size
        
    def calculate_taf_fee(self, shares: int) -> float:
        """Calculate TAF fee for given number of shares"""
        if shares <= 0:
            return 0.0
        
        base_fee = shares * self.TAF_RATE
        return min(base_fee, self.MAX_TAF_PER_TRADE)
    
    def optimize_order_size(self, symbol: str, side: str, quantity: int) -> OptimizedOrder:
        """Optimize order size to minimize TAF fees under NEW structure"""
        if side.lower() != 'sell' or quantity <= self.OPTIMAL_CHUNK_SIZE:
            # No optimization needed for buy orders or small sell orders
            return OptimizedOrder(
                symbol=symbol,
                side=side,
                original_quantity=quantity,
                optimized_chunks=[quantity],
                estimated_taf_savings=0.0,
                execution_strategy="single_order"
            )

        # Under NEW structure: each trade pays up to $8.30 max per trade
        # Strategy: Split large orders into chunks ≤50,000 shares to pay actual rate instead of max

        # Calculate what we'd pay without optimization (single large order)
        fee_without_optimization = self.MAX_TAF_PER_TRADE  # $8.30 for any order >50K shares

        # Calculate optimal chunking to minimize fees
        chunks = self._calculate_optimal_chunks(quantity)

        # Calculate what we'd pay with optimization (multiple smaller orders)
        fee_with_optimization = sum(self.calculate_taf_fee(chunk) for chunk in chunks)

        # Savings = difference between unoptimized and optimized fees
        savings = fee_without_optimization - fee_with_optimization

        return OptimizedOrder(
            symbol=symbol,
            side=side,
            original_quantity=quantity,
            optimized_chunks=chunks,
            estimated_taf_savings=max(0, savings),  # Ensure non-negative savings
            execution_strategy="chunked_execution" if len(chunks) > 1 else "single_order"
        )
    
    def _calculate_optimal_chunks(self, quantity: int) -> List[int]:
        """Calculate optimal order chunks to minimize TAF fees under NEW structure"""
        if quantity <= self.OPTIMAL_CHUNK_SIZE:
            return [quantity]

        # Under NEW structure, we want to minimize total fees
        # Option 1: Keep as single order (pays $8.30)
        # Option 2: Split into chunks (each chunk pays its proportional fee)

        single_order_fee = self.MAX_TAF_PER_TRADE

        # Try different chunking strategies and pick the best
        best_chunks = [quantity]
        best_fee = single_order_fee

        # Strategy 1: Split into equal chunks just under 50K
        chunk_size = self.OPTIMAL_CHUNK_SIZE - 1  # 49,999 shares
        num_chunks = math.ceil(quantity / chunk_size)

        if num_chunks > 1:
            chunks = []
            remaining = quantity
            for i in range(num_chunks - 1):
                chunks.append(chunk_size)
                remaining -= chunk_size
            if remaining > 0:
                chunks.append(remaining)

            chunked_fee = sum(self.calculate_taf_fee(chunk) for chunk in chunks)

            if chunked_fee < best_fee:
                best_chunks = chunks
                best_fee = chunked_fee

        # Strategy 2: Split into exactly 50K chunks (if beneficial)
        if quantity > self.OPTIMAL_CHUNK_SIZE:
            num_full_chunks = quantity // self.OPTIMAL_CHUNK_SIZE
            remainder = quantity % self.OPTIMAL_CHUNK_SIZE

            chunks = [self.OPTIMAL_CHUNK_SIZE] * num_full_chunks
            if remainder > 0:
                chunks.append(remainder)

            chunked_fee = sum(self.calculate_taf_fee(chunk) for chunk in chunks)

            if chunked_fee < best_fee:
                best_chunks = chunks
                best_fee = chunked_fee

        return best_chunks
    
    def calculate_execution_timeline(self, optimized_order: OptimizedOrder, 
                                   interval_minutes: int = 5) -> List[Dict]:
        """Calculate execution timeline for chunked orders"""
        if optimized_order.execution_strategy == "single_order":
            return [{
                'chunk_number': 1,
                'quantity': optimized_order.original_quantity,
                'estimated_execution_time': datetime.now(),
                'estimated_taf_fee': self.calculate_taf_fee(optimized_order.original_quantity)
            }]
        
        timeline = []
        current_time = datetime.now()
        
        for i, chunk_size in enumerate(optimized_order.optimized_chunks, 1):
            timeline.append({
                'chunk_number': i,
                'quantity': chunk_size,
                'estimated_execution_time': current_time,
                'estimated_taf_fee': self.calculate_taf_fee(chunk_size)
            })
            # Add interval between chunks
            current_time = datetime.fromtimestamp(
                current_time.timestamp() + (interval_minutes * 60)
            )
        
        return timeline
    
    def analyze_portfolio_optimization(self, pending_orders: List[Dict]) -> Dict:
        """Analyze TAF optimization for entire portfolio of pending orders"""
        total_original_fees = 0
        total_optimized_fees = 0
        total_savings = 0
        optimized_orders = []
        
        for order in pending_orders:
            symbol = order.get('symbol', 'UNKNOWN')
            side = order.get('side', 'buy')
            quantity = order.get('quantity', 0)
            
            optimized = self.optimize_order_size(symbol, side, quantity)
            optimized_orders.append(optimized)
            
            original_fee = self.calculate_taf_fee(quantity) if side.lower() == 'sell' else 0
            total_original_fees += original_fee
            total_optimized_fees += sum(self.calculate_taf_fee(chunk) for chunk in optimized.optimized_chunks) if side.lower() == 'sell' else 0
        
        total_savings = total_original_fees - total_optimized_fees
        
        return {
            'total_orders': len(pending_orders),
            'optimized_orders': optimized_orders,
            'original_taf_fees': total_original_fees,
            'optimized_taf_fees': total_optimized_fees,
            'total_savings': total_savings,
            'savings_percentage': (total_savings / total_original_fees * 100) if total_original_fees > 0 else 0,
            'orders_requiring_chunking': len([o for o in optimized_orders if len(o.optimized_chunks) > 1])
        }
    
    def generate_execution_plan(self, symbol: str, side: str, quantity: int) -> Dict:
        """Generate comprehensive execution plan with TAF optimization"""
        optimized_order = self.optimize_order_size(symbol, side, quantity)
        timeline = self.calculate_execution_timeline(optimized_order)
        
        return {
            'symbol': symbol,
            'side': side,
            'original_quantity': quantity,
            'optimization_summary': {
                'chunks_needed': len(optimized_order.optimized_chunks),
                'estimated_savings': optimized_order.estimated_taf_savings,
                'execution_strategy': optimized_order.execution_strategy
            },
            'chunk_details': [
                {
                    'chunk_size': chunk,
                    'taf_fee': self.calculate_taf_fee(chunk),
                    'percentage_of_total': (chunk / quantity * 100)
                }
                for chunk in optimized_order.optimized_chunks
            ],
            'execution_timeline': timeline,
            'risk_considerations': self._generate_risk_considerations(optimized_order),
            'implementation_notes': self._generate_implementation_notes(optimized_order)
        }
    
    def _generate_risk_considerations(self, optimized_order: OptimizedOrder) -> List[str]:
        """Generate risk considerations for optimized execution"""
        considerations = []
        
        if len(optimized_order.optimized_chunks) > 1:
            considerations.append("[WARNING]️ Market impact: Chunked execution may affect average fill price")
            considerations.append("📈 Price risk: Market movement during execution window")
            considerations.append("⏱️ Timing risk: Execution spread over multiple time periods")
            
        if optimized_order.original_quantity > 100000:
            considerations.append("🔍 Large position: Monitor market liquidity during execution")
            
        considerations.append("💰 TAF savings vs. execution risk trade-off")
        
        return considerations
    
    def _generate_implementation_notes(self, optimized_order: OptimizedOrder) -> List[str]:
        """Generate implementation notes for optimized execution"""
        notes = []
        
        if optimized_order.execution_strategy == "chunked_execution":
            notes.append(f"🔧 Split into {len(optimized_order.optimized_chunks)} chunks")
            notes.append("⏰ Recommend 5-15 minute intervals between chunks")
            notes.append("📊 Monitor market conditions between executions")
            notes.append("🎯 Adjust chunk timing based on volatility")
        else:
            notes.append("[CHECK] Single order execution - no chunking needed")
        
        if optimized_order.estimated_taf_savings > 0:
            notes.append(f"💰 Estimated TAF savings: ${optimized_order.estimated_taf_savings:.2f}")
        
        return notes

def create_sample_orders() -> List[Dict]:
    """Create sample orders for testing"""
    return [
        {'symbol': 'AAPL', 'side': 'sell', 'quantity': 75000},
        {'symbol': 'MSFT', 'side': 'sell', 'quantity': 120000},
        {'symbol': 'GOOGL', 'side': 'sell', 'quantity': 25000},
        {'symbol': 'AMZN', 'side': 'sell', 'quantity': 180000},
        {'symbol': 'TSLA', 'side': 'buy', 'quantity': 50000},  # Buy order - no TAF
    ]

def main():
    """Demonstrate TAF optimization"""
    engine = TAFOptimizedTradingEngine()
    
    print("🚀 TAF-Optimized Trading Engine")
    print("=" * 50)
    
    # Test individual order optimization
    print("\n📊 INDIVIDUAL ORDER OPTIMIZATION")
    test_order = {'symbol': 'AAPL', 'side': 'sell', 'quantity': 125000}
    
    plan = engine.generate_execution_plan(
        test_order['symbol'], 
        test_order['side'], 
        test_order['quantity']
    )
    
    print(f"Symbol: {plan['symbol']}")
    print(f"Original Quantity: {plan['original_quantity']:,} shares")
    print(f"Chunks Needed: {plan['optimization_summary']['chunks_needed']}")
    print(f"Estimated Savings: ${plan['optimization_summary']['estimated_savings']:.2f}")
    
    print("\n📈 CHUNK BREAKDOWN:")
    for i, chunk in enumerate(plan['chunk_details'], 1):
        print(f"  Chunk {i}: {chunk['chunk_size']:,} shares (${chunk['taf_fee']:.2f} TAF)")
    
    # Test portfolio optimization
    print("\n🎯 PORTFOLIO OPTIMIZATION")
    sample_orders = create_sample_orders()
    portfolio_analysis = engine.analyze_portfolio_optimization(sample_orders)
    
    print(f"Total Orders: {portfolio_analysis['total_orders']}")
    print(f"Orders Requiring Chunking: {portfolio_analysis['orders_requiring_chunking']}")
    print(f"Original TAF Fees: ${portfolio_analysis['original_taf_fees']:.2f}")
    print(f"Optimized TAF Fees: ${portfolio_analysis['optimized_taf_fees']:.2f}")
    print(f"Total Savings: ${portfolio_analysis['total_savings']:.2f}")
    print(f"Savings Percentage: {portfolio_analysis['savings_percentage']:.1f}%")

if __name__ == "__main__":
    main()
