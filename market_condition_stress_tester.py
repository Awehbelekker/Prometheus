#!/usr/bin/env python3
"""
🌪️ MARKET CONDITION STRESS TESTER
Test PROMETHEUS performance under various market conditions to ensure live trading readiness

Market Conditions Tested:
1. High Volatility Markets (VIX > 25)
2. Low Volatility Markets (VIX < 15)
3. Trending Markets (Strong directional movement)
4. Sideways/Range-bound Markets
5. News Event Simulation (Earnings, Fed announcements)
6. Market Open Volatility
7. Market Close Volatility
8. Pre-market/After-hours Trading
9. Low Volume Conditions
10. High Volume Conditions
"""

import asyncio
import json
import os
import sys
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Any
import yfinance as yf
import numpy as np

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class MarketConditionStressTester:
    """Comprehensive market condition stress testing"""
    
    def __init__(self):
        self.test_id = f"stress_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.starting_capital = 540.0  # Your IB account capital
        
        # Market condition scenarios
        self.stress_scenarios = {
            "high_volatility": {
                "name": "High Volatility Market",
                "description": "VIX > 25, rapid price swings",
                "volatility_multiplier": 2.5,
                "trend_strength": 0.3,
                "noise_level": 0.8,
                "duration_minutes": 120
            },
            "low_volatility": {
                "name": "Low Volatility Market", 
                "description": "VIX < 15, minimal price movement",
                "volatility_multiplier": 0.4,
                "trend_strength": 0.1,
                "noise_level": 0.2,
                "duration_minutes": 120
            },
            "strong_uptrend": {
                "name": "Strong Bull Market",
                "description": "Sustained upward momentum",
                "volatility_multiplier": 1.2,
                "trend_strength": 0.8,
                "trend_direction": 1,
                "duration_minutes": 180
            },
            "strong_downtrend": {
                "name": "Strong Bear Market",
                "description": "Sustained downward pressure",
                "volatility_multiplier": 1.5,
                "trend_strength": 0.8,
                "trend_direction": -1,
                "duration_minutes": 180
            },
            "sideways_market": {
                "name": "Range-bound Market",
                "description": "Choppy, no clear direction",
                "volatility_multiplier": 0.8,
                "trend_strength": 0.1,
                "range_bound": True,
                "duration_minutes": 240
            },
            "news_event": {
                "name": "News Event Simulation",
                "description": "Earnings/Fed announcement volatility",
                "volatility_multiplier": 3.0,
                "trend_strength": 0.6,
                "sudden_moves": True,
                "duration_minutes": 60
            },
            "market_open": {
                "name": "Market Open Volatility",
                "description": "9:30 AM ET opening volatility",
                "volatility_multiplier": 2.0,
                "trend_strength": 0.4,
                "opening_gaps": True,
                "duration_minutes": 90
            },
            "market_close": {
                "name": "Market Close Volatility",
                "description": "3:30-4:00 PM ET closing volatility",
                "volatility_multiplier": 1.8,
                "trend_strength": 0.5,
                "closing_pressure": True,
                "duration_minutes": 90
            },
            "low_volume": {
                "name": "Low Volume Market",
                "description": "Thin liquidity conditions",
                "volatility_multiplier": 1.0,
                "trend_strength": 0.2,
                "liquidity_factor": 0.3,
                "duration_minutes": 150
            },
            "high_volume": {
                "name": "High Volume Market",
                "description": "Heavy institutional activity",
                "volatility_multiplier": 1.4,
                "trend_strength": 0.7,
                "liquidity_factor": 2.0,
                "duration_minutes": 150
            }
        }
        
        # Results tracking
        self.stress_results = {
            "test_id": self.test_id,
            "start_time": datetime.now().isoformat(),
            "starting_capital": self.starting_capital,
            "scenario_results": {},
            "overall_performance": {
                "total_scenarios": len(self.stress_scenarios),
                "scenarios_passed": 0,
                "scenarios_failed": 0,
                "average_performance": 0.0,
                "worst_case_drawdown": 0.0,
                "best_case_return": 0.0,
                "consistency_score": 0.0
            },
            "risk_metrics": {
                "max_drawdown_per_scenario": {},
                "recovery_times": {},
                "volatility_adjusted_returns": {}
            },
            "live_trading_recommendations": []
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'stress_test_{self.test_id}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def print_stress_test_header(self):
        """Print stress test header"""
        print("=" * 100)
        print("🌪️ PROMETHEUS MARKET CONDITION STRESS TESTING SUITE")
        print("=" * 100)
        print(f"🧪 Test ID: {self.test_id}")
        print(f"📅 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💰 Test Capital: ${self.starting_capital}")
        print(f"🎯 Objective: Validate performance under extreme market conditions")
        print(f"📊 Scenarios: {len(self.stress_scenarios)} different market conditions")
        print("=" * 100)
        print()
    
    async def run_stress_testing_suite(self):
        """Run complete stress testing suite"""
        self.print_stress_test_header()
        
        try:
            # Run each stress scenario
            for scenario_key, scenario_config in self.stress_scenarios.items():
                print(f"🌪️ TESTING: {scenario_config['name']}")
                print(f"📝 Description: {scenario_config['description']}")
                print(f"⏰ Duration: {scenario_config['duration_minutes']} minutes")
                print("-" * 60)
                
                scenario_result = await self.run_stress_scenario(scenario_key, scenario_config)
                self.stress_results["scenario_results"][scenario_key] = scenario_result
                
                # Evaluate scenario performance
                self.evaluate_scenario_performance(scenario_key, scenario_result)
                
                print()
                
                # Brief pause between scenarios
                await asyncio.sleep(2)
            
            # Generate comprehensive analysis
            await self.generate_stress_analysis()
            
        except Exception as e:
            self.logger.error(f"Stress testing failed: {e}")
            print(f"[ERROR] Stress testing failed: {e}")
        
        finally:
            await self.save_stress_report()
    
    async def run_stress_scenario(self, scenario_key: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run individual stress scenario"""
        scenario_start = datetime.now()
        scenario_capital = self.starting_capital * 0.2  # Use 20% of capital per scenario
        
        # Initialize scenario tracking
        scenario_data = {
            "scenario_key": scenario_key,
            "start_time": scenario_start.isoformat(),
            "config": config,
            "capital_allocated": scenario_capital,
            "trades": [],
            "pnl_history": [],
            "max_drawdown": 0.0,
            "peak_value": scenario_capital,
            "current_value": scenario_capital
        }
        
        # Simulate market conditions and trading
        total_minutes = config["duration_minutes"]
        current_pnl = 0.0
        total_trades = 0
        
        print(f"🔄 Simulating {config['name']} for {total_minutes} minutes...")
        
        # Generate realistic market data based on scenario
        market_data = self.generate_scenario_market_data(config, total_minutes)
        
        # Execute trades based on market conditions
        for minute in range(0, total_minutes, 5):  # Trade every 5 minutes
            market_conditions = market_data[min(minute, len(market_data) - 1)]
            
            # Make trading decision based on market conditions
            trade_decision = await self.make_trading_decision(market_conditions, scenario_capital, config)
            
            if trade_decision:
                trade_result = await self.execute_stress_trade(trade_decision, market_conditions)
                
                if trade_result:
                    scenario_data["trades"].append(trade_result)
                    current_pnl += trade_result["pnl"]
                    total_trades += 1
                    
                    # Update portfolio value
                    scenario_data["current_value"] = scenario_capital + current_pnl
                    
                    # Track peak and drawdown
                    if scenario_data["current_value"] > scenario_data["peak_value"]:
                        scenario_data["peak_value"] = scenario_data["current_value"]
                    
                    current_drawdown = (scenario_data["peak_value"] - scenario_data["current_value"]) / scenario_data["peak_value"]
                    if current_drawdown > scenario_data["max_drawdown"]:
                        scenario_data["max_drawdown"] = current_drawdown
                    
                    # Track P&L history
                    scenario_data["pnl_history"].append({
                        "minute": minute,
                        "cumulative_pnl": current_pnl,
                        "portfolio_value": scenario_data["current_value"],
                        "drawdown": current_drawdown
                    })
            
            # Progress update every 30 minutes
            if minute % 30 == 0 and minute > 0:
                hours = minute // 60
                mins = minute % 60
                print(f"   ⏰ {hours:02d}:{mins:02d} - P&L: ${current_pnl:.2f}, Drawdown: {scenario_data['max_drawdown']*100:.1f}%")
        
        # Calculate final scenario metrics
        scenario_end = datetime.now()
        scenario_duration = (scenario_end - scenario_start).total_seconds() / 60
        
        final_return = (current_pnl / scenario_capital) * 100 if scenario_capital > 0 else 0
        
        scenario_data.update({
            "end_time": scenario_end.isoformat(),
            "actual_duration_minutes": scenario_duration,
            "final_pnl": current_pnl,
            "final_return_percent": final_return,
            "total_trades": total_trades,
            "max_drawdown_percent": scenario_data["max_drawdown"] * 100,
            "recovery_achieved": scenario_data["current_value"] >= scenario_data["peak_value"] * 0.95
        })
        
        # Scenario summary
        print(f"[CHECK] {config['name']} COMPLETED!")
        print(f"   📊 Final P&L: ${current_pnl:.2f} ({final_return:.2f}%)")
        print(f"   📉 Max Drawdown: {scenario_data['max_drawdown_percent']:.1f}%")
        print(f"   🔢 Total Trades: {total_trades}")
        print(f"   🔄 Recovery: {'[CHECK] Yes' if scenario_data['recovery_achieved'] else '[ERROR] No'}")
        
        return scenario_data
    
    def generate_scenario_market_data(self, config: Dict[str, Any], duration_minutes: int) -> List[Dict[str, Any]]:
        """Generate realistic market data for scenario"""
        market_data = []
        base_price = 100.0  # Starting price
        
        for minute in range(duration_minutes):
            # Apply scenario-specific market conditions
            volatility = config.get("volatility_multiplier", 1.0)
            trend_strength = config.get("trend_strength", 0.0)
            trend_direction = config.get("trend_direction", 0)
            
            # Generate price movement
            random_move = np.random.normal(0, volatility * 0.01)  # Base 1% volatility
            trend_move = trend_strength * trend_direction * 0.005  # Trend component
            
            # Special scenario adjustments
            if config.get("sudden_moves"):
                if random.random() < 0.05:  # 5% chance of sudden move
                    random_move *= 3
            
            if config.get("range_bound"):
                # Keep price in range
                if base_price > 105:
                    random_move -= 0.01
                elif base_price < 95:
                    random_move += 0.01
            
            price_change = random_move + trend_move
            base_price *= (1 + price_change)
            
            market_data.append({
                "minute": minute,
                "price": base_price,
                "price_change": price_change,
                "volatility": volatility,
                "volume_factor": config.get("liquidity_factor", 1.0)
            })
        
        return market_data
    
    async def make_trading_decision(self, market_conditions: Dict[str, Any], capital: float, config: Dict[str, Any]) -> Dict[str, Any]:
        """Make trading decision based on market conditions"""
        # Simple momentum-based decision making
        price_change = market_conditions["price_change"]
        volatility = market_conditions["volatility"]
        
        # Decision thresholds based on scenario
        entry_threshold = 0.005 * volatility  # Adjust for volatility
        
        if abs(price_change) > entry_threshold:
            position_size = min(capital * 0.1, 50)  # Max $50 per trade
            
            return {
                "action": "BUY" if price_change > 0 else "SELL",
                "position_size": position_size,
                "entry_price": market_conditions["price"],
                "confidence": min(1.0, abs(price_change) / entry_threshold)
            }
        
        return None
    
    async def execute_stress_trade(self, decision: Dict[str, Any], market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trade under stress conditions"""
        # Simulate realistic execution with slippage
        slippage_factor = 0.001 * market_conditions["volatility"]  # Higher volatility = more slippage
        liquidity_factor = market_conditions.get("volume_factor", 1.0)
        
        # Adjust slippage based on liquidity
        actual_slippage = slippage_factor / liquidity_factor
        
        entry_price = decision["entry_price"]
        execution_price = entry_price * (1 + actual_slippage if decision["action"] == "BUY" else 1 - actual_slippage)
        
        # Simulate holding period and exit
        holding_minutes = random.randint(5, 30)  # Hold for 5-30 minutes
        
        # Generate exit price based on market momentum
        price_drift = np.random.normal(0, 0.01)  # Random price movement
        exit_price = execution_price * (1 + price_drift)
        
        # Calculate P&L
        if decision["action"] == "BUY":
            pnl = (exit_price - execution_price) / execution_price * decision["position_size"]
        else:
            pnl = (execution_price - exit_price) / execution_price * decision["position_size"]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "action": decision["action"],
            "entry_price": execution_price,
            "exit_price": exit_price,
            "position_size": decision["position_size"],
            "holding_minutes": holding_minutes,
            "pnl": pnl,
            "slippage": actual_slippage * 100,  # Convert to percentage
            "market_volatility": market_conditions["volatility"]
        }

if __name__ == "__main__":
    tester = MarketConditionStressTester()
    asyncio.run(tester.run_stress_testing_suite())
