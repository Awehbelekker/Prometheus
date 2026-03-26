"""
TRADING COST CALCULATOR - Central Cost Analysis for PROMETHEUS
Calculates actual trading costs for all broker/asset combinations
and determines minimum profitable price moves.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class CostBreakdown:
    """Detailed breakdown of trading costs"""
    commission: float = 0.0
    spread: float = 0.0
    slippage: float = 0.0
    regulatory_fees: float = 0.0
    total: float = 0.0
    
    def __post_init__(self):
        self.total = self.commission + self.spread + self.slippage + self.regulatory_fees


@dataclass
class TradeCostResult:
    """Result of a trade cost calculation"""
    broker: str
    asset_class: str
    position_value: float
    entry_cost: CostBreakdown
    exit_cost: CostBreakdown
    round_trip_cost_dollars: float
    round_trip_cost_pct: float
    min_profitable_move_pct: float
    min_profitable_move_dollars: float
    is_viable: bool  # True if minimum move is achievable (< 5%)


class TradingCostCalculator:
    """
    Central trading cost calculator for PROMETHEUS.
    Calculates actual costs for all broker/asset combinations.
    """
    
    # Cost structures by broker and asset class (in percentages/basis points)
    COST_STRUCTURES = {
        'alpaca': {
            'stocks': {
                'commission_per_share': 0.0,
                'commission_pct': 0.0,
                'min_commission': 0.0,
                'spread_pct': 0.02,  # ~0.02% for liquid stocks
                'slippage_pct': 0.05,  # ~0.05% typical
                'regulatory_fees_pct': 0.001,  # SEC/FINRA fees
            },
            'crypto': {
                'commission_per_share': 0.0,
                'commission_pct': 0.0,
                'maker_fee_pct': 0.15,  # 0.15% maker
                'taker_fee_pct': 0.25,  # 0.25% taker (market orders)
                'spread_pct': 0.20,  # ~0.20% typical spread
                'slippage_pct': 0.10,  # ~0.10% slippage
            },
        },
        'ib': {
            'stocks': {
                'commission_per_share': 0.005,  # $0.005/share for Pro
                'min_commission': 1.0,  # $1 minimum
                'max_commission_pct': 0.5,  # 0.5% max
                'spread_pct': 0.01,  # ~0.01% for very liquid
                'slippage_pct': 0.03,  # ~0.03%
                'regulatory_fees_pct': 0.001,
            },
            'stocks_lite': {  # IBKR Lite - commission free
                'commission_per_share': 0.0,
                'min_commission': 0.0,
                'spread_pct': 0.01,
                'slippage_pct': 0.03,
                'regulatory_fees_pct': 0.001,
            },
            'options': {
                'commission_per_contract': 0.65,  # $0.65/contract
                'exchange_fees': 0.30,  # ~$0.30/contract
                'spread_pct': 2.0,  # ~2% typical spread on options
                'slippage_pct': 1.0,  # ~1% slippage
            },
            'forex': {
                'commission_pct': 0.002,  # 0.2 basis points
                'spread_pct': 0.01,  # ~1 pip
                'slippage_pct': 0.005,
            },
            'futures': {
                'commission_per_contract': 0.85,
                'exchange_fees': 1.50,
                'spread_pct': 0.02,
                'slippage_pct': 0.01,
            },
        },
    }
    
    def __init__(self):
        logger.info("TradingCostCalculator initialized")
    
    def calculate_cost(
        self,
        broker: str,
        asset_class: str,
        position_value: float,
        entry_price: float,
        quantity: float = 0,
        num_contracts: int = 0,
    ) -> TradeCostResult:
        """
        Calculate comprehensive trading costs.
        
        Args:
            broker: 'alpaca' or 'ib'
            asset_class: 'stocks', 'crypto', 'options', 'forex', 'futures'
            position_value: Total value of the position in dollars
            entry_price: Price per share/unit
            quantity: Number of shares (for per-share commissions)
            num_contracts: Number of contracts (for options/futures)
        
        Returns:
            TradeCostResult with full cost breakdown
        """
        broker = broker.lower().replace('_broker', '').replace(' ', '_')
        asset_class = asset_class.lower()
        
        # Get cost structure
        if broker not in self.COST_STRUCTURES:
            broker = 'alpaca'  # Default
        
        broker_costs = self.COST_STRUCTURES[broker]
        if asset_class not in broker_costs:
            asset_class = 'stocks'  # Default
        
        costs = broker_costs[asset_class]
        
        # Calculate entry costs
        entry_cost = self._calculate_single_leg_cost(
            costs, position_value, quantity, num_contracts, is_entry=True
        )
        
        # Calculate exit costs (similar to entry)
        exit_cost = self._calculate_single_leg_cost(
            costs, position_value, quantity, num_contracts, is_entry=False
        )
        
        # Total round-trip
        round_trip_dollars = entry_cost.total + exit_cost.total
        round_trip_pct = (round_trip_dollars / position_value * 100) if position_value > 0 else 0
        
        # Minimum profitable move (need 1.5x costs to be worthwhile)
        min_move_pct = round_trip_pct * 1.5
        min_move_dollars = position_value * (min_move_pct / 100)
        
        return TradeCostResult(
            broker=broker,
            asset_class=asset_class,
            position_value=position_value,
            entry_cost=entry_cost,
            exit_cost=exit_cost,
            round_trip_cost_dollars=round_trip_dollars,
            round_trip_cost_pct=round_trip_pct,
            min_profitable_move_pct=min_move_pct,
            min_profitable_move_dollars=min_move_dollars,
            is_viable=min_move_pct < 5.0,  # Achievable if < 5%
        )

    def _calculate_single_leg_cost(
        self,
        costs: Dict,
        position_value: float,
        quantity: float,
        num_contracts: int,
        is_entry: bool,
    ) -> CostBreakdown:
        """Calculate cost for entry or exit leg"""
        commission = 0.0
        spread = 0.0
        slippage = 0.0
        regulatory = 0.0

        # Commission calculation
        if 'commission_per_share' in costs and costs['commission_per_share'] > 0 and quantity > 0:
            commission = quantity * costs['commission_per_share']
            if 'min_commission' in costs:
                commission = max(commission, costs['min_commission'])
            if 'max_commission_pct' in costs:
                max_comm = position_value * (costs['max_commission_pct'] / 100)
                commission = min(commission, max_comm)
        elif 'taker_fee_pct' in costs:  # Crypto
            commission = position_value * (costs['taker_fee_pct'] / 100)
        elif 'commission_per_contract' in costs and num_contracts > 0:
            commission = num_contracts * costs['commission_per_contract']
            if 'exchange_fees' in costs:
                commission += num_contracts * costs['exchange_fees']
        elif 'commission_pct' in costs:
            commission = position_value * (costs['commission_pct'] / 100)

        # Spread cost (half on each leg)
        if 'spread_pct' in costs:
            spread = position_value * (costs['spread_pct'] / 100 / 2)

        # Slippage
        if 'slippage_pct' in costs:
            slippage = position_value * (costs['slippage_pct'] / 100)

        # Regulatory fees (typically only on sells for SEC/FINRA)
        if 'regulatory_fees_pct' in costs:
            if not is_entry:  # Only on exit
                regulatory = position_value * (costs['regulatory_fees_pct'] / 100)

        return CostBreakdown(
            commission=commission,
            spread=spread,
            slippage=slippage,
            regulatory_fees=regulatory,
        )

    def is_trade_profitable(
        self,
        broker: str,
        asset_class: str,
        entry_price: float,
        current_price: float,
        quantity: float,
    ) -> Tuple[bool, float, float]:
        """
        Check if a trade would be profitable after costs.

        Returns:
            Tuple of (is_profitable, gross_pnl, net_pnl)
        """
        position_value = entry_price * quantity
        gross_pnl = (current_price - entry_price) * quantity

        cost_result = self.calculate_cost(
            broker=broker,
            asset_class=asset_class,
            position_value=position_value,
            entry_price=entry_price,
            quantity=quantity,
        )

        net_pnl = gross_pnl - cost_result.round_trip_cost_dollars

        return (net_pnl > 0, gross_pnl, net_pnl)

    def get_minimum_position_size(
        self,
        broker: str,
        asset_class: str,
        target_profit: float = 1.0,  # $1 minimum profit target
    ) -> float:
        """
        Calculate minimum position size to make trading viable.

        Args:
            broker: Broker name
            asset_class: Asset class
            target_profit: Minimum acceptable profit in dollars

        Returns:
            Minimum position size in dollars
        """
        # Calculate cost for a $100 reference position
        cost_result = self.calculate_cost(
            broker=broker,
            asset_class=asset_class,
            position_value=100.0,
            entry_price=10.0,
            quantity=10,
        )

        # Scale to find position where 2% gain exceeds costs + target
        if cost_result.round_trip_cost_pct > 0:
            # Position where 2% gain = costs + target profit
            # 0.02 * position = (cost_pct/100) * position + target
            # position * (0.02 - cost_pct/100) = target
            net_gain_pct = 2.0 - cost_result.round_trip_cost_pct
            if net_gain_pct > 0:
                min_position = (target_profit / (net_gain_pct / 100))
                return max(min_position, 10.0)  # At least $10

        return 25.0  # Default minimum

    def get_cost_comparison_table(self) -> str:
        """Generate a comparison table of all costs"""
        lines = []
        lines.append("=" * 100)
        lines.append("TRADING COST COMPARISON TABLE")
        lines.append("=" * 100)
        lines.append(f"{'Broker':<12} {'Asset Class':<15} {'Entry Cost':<12} {'Exit Cost':<12} "
                    f"{'Round-Trip %':<14} {'Min Move':<12} {'Viable':<8}")
        lines.append("-" * 100)

        test_cases = [
            ('alpaca', 'stocks', 100.0, 10.0, 10),
            ('alpaca', 'crypto', 100.0, 1.0, 100),
            ('ib', 'stocks', 100.0, 10.0, 10),
            ('ib', 'stocks_lite', 100.0, 10.0, 10),
            ('ib', 'options', 500.0, 5.0, 0, 1),
            ('ib', 'forex', 1000.0, 1.0, 1000),
            ('ib', 'futures', 5000.0, 50.0, 0, 1),
        ]

        for case in test_cases:
            broker = case[0]
            asset_class = case[1]
            position_value = case[2]
            entry_price = case[3]
            quantity = case[4] if len(case) > 4 else 0
            num_contracts = case[5] if len(case) > 5 else 0

            result = self.calculate_cost(
                broker=broker,
                asset_class=asset_class,
                position_value=position_value,
                entry_price=entry_price,
                quantity=quantity,
                num_contracts=num_contracts,
            )

            viable = "YES" if result.is_viable else "NO"
            lines.append(
                f"{broker.upper():<12} {asset_class:<15} "
                f"${result.entry_cost.total:<10.4f} ${result.exit_cost.total:<10.4f} "
                f"{result.round_trip_cost_pct:<13.3f}% {result.min_profitable_move_pct:<11.3f}% "
                f"{viable:<8}"
            )

        lines.append("=" * 100)
        return "\n".join(lines)


# Singleton instance
_calculator: Optional[TradingCostCalculator] = None

def get_cost_calculator() -> TradingCostCalculator:
    """Get the global TradingCostCalculator instance"""
    global _calculator
    if _calculator is None:
        _calculator = TradingCostCalculator()
    return _calculator


if __name__ == '__main__':
    # Test the calculator
    calc = TradingCostCalculator()
    print(calc.get_cost_comparison_table())

    print("\n\nMinimum Position Sizes for $1 Target Profit:")
    print("-" * 50)
    for broker, asset_class in [('alpaca', 'stocks'), ('alpaca', 'crypto'), ('ib', 'stocks'), ('ib', 'forex')]:
        min_pos = calc.get_minimum_position_size(broker, asset_class)
        print(f"{broker.upper()} {asset_class}: ${min_pos:.2f}")

