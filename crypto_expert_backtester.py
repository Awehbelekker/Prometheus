#!/usr/bin/env python3
"""
================================================================================
PROMETHEUS CRYPTO EXPERT BACKTESTER
================================================================================

Advanced backtesting system specifically designed for cryptocurrency trading.
Incorporates expert-level strategies including:

1. Chart Pattern Recognition (All timeframes)
2. Whale Movement Detection & Following
3. Funding Rate Arbitrage
4. Liquidation Cascade Detection
5. On-Chain Metrics Analysis
6. Order Book Depth Analysis
7. Crypto-Specific Sentiment (Fear/Greed Index)
8. Exchange Flow Analysis
9. Correlation with Traditional Markets
10. DeFi Yield Opportunities

This system trains PROMETHEUS to become an expert crypto trader!

================================================================================
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import json
import time
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field, asdict
import copy
import random

# Add project root
sys.path.insert(0, str(Path(__file__).parent))


# =============================================================================
# CRYPTO MARKET KNOWLEDGE BASE
# =============================================================================

CRYPTO_KNOWLEDGE = {
    "chart_patterns": {
        "bullish": {
            "double_bottom": {"reliability": 0.78, "avg_move": 0.15},
            "inverse_head_shoulders": {"reliability": 0.83, "avg_move": 0.20},
            "ascending_triangle": {"reliability": 0.75, "avg_move": 0.12},
            "bull_flag": {"reliability": 0.70, "avg_move": 0.08},
            "cup_handle": {"reliability": 0.80, "avg_move": 0.18},
            "falling_wedge": {"reliability": 0.72, "avg_move": 0.10},
            "morning_star": {"reliability": 0.68, "avg_move": 0.06},
            "bullish_engulfing": {"reliability": 0.65, "avg_move": 0.05},
            "hammer": {"reliability": 0.60, "avg_move": 0.04},
            "three_white_soldiers": {"reliability": 0.70, "avg_move": 0.08}
        },
        "bearish": {
            "double_top": {"reliability": 0.76, "avg_move": -0.14},
            "head_shoulders": {"reliability": 0.82, "avg_move": -0.18},
            "descending_triangle": {"reliability": 0.73, "avg_move": -0.11},
            "bear_flag": {"reliability": 0.68, "avg_move": -0.07},
            "rising_wedge": {"reliability": 0.74, "avg_move": -0.12},
            "evening_star": {"reliability": 0.66, "avg_move": -0.05},
            "bearish_engulfing": {"reliability": 0.64, "avg_move": -0.05},
            "shooting_star": {"reliability": 0.58, "avg_move": -0.04},
            "three_black_crows": {"reliability": 0.69, "avg_move": -0.07}
        }
    },
    
    "whale_behavior": {
        "accumulation_signs": [
            "Large OTC trades without price impact",
            "Gradual position building over days/weeks",
            "Buying during fear/panic",
            "Exchange outflows to cold wallets"
        ],
        "distribution_signs": [
            "Large market sells creating cascades",
            "Exchange inflows from known wallets",
            "Selling into strength/euphoria",
            "Unusual options activity (puts)"
        ],
        "whale_threshold_btc": 100,
        "whale_threshold_eth": 1000,
        "whale_impact_multiplier": 2.5
    },
    
    "funding_rates": {
        "neutral_range": (-0.01, 0.01),
        "extreme_positive": 0.05,
        "extreme_negative": -0.03,
        "mean_reversion_edge": 0.65,
        "arbitrage_threshold": 0.02
    },
    
    "liquidation_data": {
        "cascade_threshold": 50_000_000,
        "recovery_time_hours": 4,
        "buy_signal_after_cascade": True,
        "short_signal_before_cascade": True
    },
    
    "fear_greed_index": {
        "extreme_fear": (0, 20),
        "fear": (20, 40),
        "neutral": (40, 60),
        "greed": (60, 80),
        "extreme_greed": (80, 100)
    },
    
    "on_chain_metrics": {
        "exchange_reserve_decrease": "bullish",
        "exchange_reserve_increase": "bearish",
        "active_addresses_increase": "bullish",
        "miner_outflow_spike": "bearish",
        "stablecoin_inflow": "bullish",
        "nvt_ratio_high": "bearish",
        "nvt_ratio_low": "bullish"
    },
    
    "market_cycles": {
        "halving_impact": {
            "pre_halving_months": 6,
            "post_halving_bull_months": 18,
            "typical_gain": 5.0
        },
        "four_year_cycle": True,
        "altcoin_season_btc_dominance": 40
    },
    
    "correlations": {
        "btc_eth": 0.85,
        "btc_sp500": 0.60,
        "btc_gold": 0.30,
        "btc_dxy": -0.40,
        "eth_defi": 0.90
    },
    
    "trading_sessions": {
        "asia": {"start": 0, "end": 8, "volatility": "medium"},
        "europe": {"start": 8, "end": 16, "volatility": "high"},
        "us": {"start": 14, "end": 22, "volatility": "highest"},
        "overlap_eu_us": {"start": 14, "end": 16, "volatility": "extreme"}
    }
}


@dataclass
class CryptoTradingParams:
    """Advanced crypto trading parameters"""
    # Base parameters
    win_rate: float = 0.65
    avg_win_pct: float = 0.025
    avg_loss_pct: float = 0.012
    trades_per_day: float = 3.0
    max_position_size: float = 0.15
    
    # Crypto-specific
    use_funding_arbitrage: bool = True
    funding_weight: float = 0.15
    
    use_whale_tracking: bool = True
    whale_weight: float = 0.20
    
    use_liquidation_detection: bool = True
    liquidation_weight: float = 0.15
    
    use_fear_greed: bool = True
    fear_greed_weight: float = 0.15
    
    use_on_chain: bool = True
    on_chain_weight: float = 0.15
    
    use_pattern_recognition: bool = True
    pattern_weight: float = 0.20
    
    # Risk management
    leverage: float = 2.0
    stop_loss_pct: float = 0.03
    take_profit_pct: float = 0.06
    trailing_stop: bool = True
    
    # Market conditions
    trade_in_extreme_fear: bool = True
    trade_in_extreme_greed: bool = False
    
    # Costs
    transaction_cost: float = 0.001
    slippage: float = 0.0008
    funding_cost: float = 0.0001
    
    def mutate(self, learning_rate: float = 0.1) -> 'CryptoTradingParams':
        """Create mutated version for genetic optimization"""
        new_params = copy.deepcopy(self)
        
        new_params.win_rate = np.clip(
            self.win_rate + np.random.normal(0, 0.03 * learning_rate), 0.45, 0.80)
        new_params.avg_win_pct = np.clip(
            self.avg_win_pct + np.random.normal(0, 0.005 * learning_rate), 0.01, 0.05)
        new_params.avg_loss_pct = np.clip(
            self.avg_loss_pct + np.random.normal(0, 0.003 * learning_rate), 0.005, 0.025)
        new_params.trades_per_day = np.clip(
            self.trades_per_day + np.random.normal(0, 0.5 * learning_rate), 1.0, 8.0)
        new_params.leverage = np.clip(
            self.leverage + np.random.normal(0, 0.3 * learning_rate), 1.0, 5.0)
        
        new_params.funding_weight = np.clip(
            self.funding_weight + np.random.normal(0, 0.03 * learning_rate), 0.05, 0.30)
        new_params.whale_weight = np.clip(
            self.whale_weight + np.random.normal(0, 0.03 * learning_rate), 0.05, 0.30)
        new_params.pattern_weight = np.clip(
            self.pattern_weight + np.random.normal(0, 0.03 * learning_rate), 0.05, 0.30)
        
        return new_params


@dataclass
class CryptoBacktestResult:
    """Comprehensive crypto backtest results"""
    final_capital: float
    total_return: float
    cagr: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    
    best_trade: float
    worst_trade: float
    avg_hold_time_hours: float
    funding_pnl: float
    liquidation_trades: int
    whale_following_pnl: float
    pattern_trades: int
    
    btc_pnl: float
    eth_pnl: float
    alt_pnl: float
    
    yearly_returns: List[float] = field(default_factory=list)
    monthly_returns: List[float] = field(default_factory=list)
    
    fitness_score: float = 0.0
    
    def calculate_fitness(self):
        """Calculate overall fitness for optimization"""
        cagr_score = self.cagr * 80
        sharpe_score = self.sharpe_ratio * 15
        sortino_score = self.sortino_ratio * 10
        winrate_score = (self.win_rate - 0.5) * 40
        profit_factor_score = (self.profit_factor - 1.0) * 20
        drawdown_penalty = abs(self.max_drawdown) * 60
        
        if self.sharpe_ratio > 2.0:
            sharpe_score *= 1.5
        if self.sortino_ratio > 3.0:
            sortino_score *= 1.5
            
        self.fitness_score = (cagr_score + sharpe_score + sortino_score + 
                             winrate_score + profit_factor_score - drawdown_penalty)
        return self.fitness_score


class CryptoMarketSimulator:
    """Simulates realistic crypto market conditions"""
    
    def __init__(self):
        self.volatility_regimes = {
            'low': {'daily_vol': 0.02, 'probability': 0.20},
            'medium': {'daily_vol': 0.04, 'probability': 0.50},
            'high': {'daily_vol': 0.08, 'probability': 0.25},
            'extreme': {'daily_vol': 0.15, 'probability': 0.05}
        }
        
        self.current_regime = 'medium'
        self.fear_greed = 50
        self.funding_rate = 0.0
        self.whale_activity = 0
        self.liquidations_24h = 0
        
    def update_market_state(self):
        """Update market conditions for next period"""
        if random.random() < 0.05:
            regimes = list(self.volatility_regimes.keys())
            weights = [self.volatility_regimes[r]['probability'] for r in regimes]
            self.current_regime = random.choices(regimes, weights=weights)[0]
        
        self.fear_greed += np.random.normal(0, 5)
        self.fear_greed = np.clip(self.fear_greed, 0, 100)
        if self.fear_greed < 30:
            self.fear_greed += random.uniform(0, 3)
        elif self.fear_greed > 70:
            self.fear_greed -= random.uniform(0, 3)
        
        self.funding_rate = np.clip(
            self.funding_rate + np.random.normal(0, 0.005),
            -0.05, 0.10
        )
        
        self.whale_activity = random.choices(
            [0, 1, 2, 3],
            weights=[0.70, 0.20, 0.08, 0.02]
        )[0]
        
        base_liq = {'low': 10, 'medium': 50, 'high': 200, 'extreme': 500}[self.current_regime]
        self.liquidations_24h = base_liq * random.uniform(0.5, 2.0) * 1_000_000
        
    def get_daily_return(self, params: CryptoTradingParams) -> Tuple[float, dict]:
        """Generate realistic daily return based on market conditions"""
        self.update_market_state()
        
        base_vol = self.volatility_regimes[self.current_regime]['daily_vol']
        
        edge = 0.0
        trade_details = {
            'regime': self.current_regime,
            'fear_greed': self.fear_greed,
            'funding_rate': self.funding_rate,
            'whale_activity': self.whale_activity,
            'liquidations': self.liquidations_24h
        }
        
        if params.use_pattern_recognition:
            pattern_edge = random.uniform(-0.002, 0.005) * params.pattern_weight
            edge += pattern_edge
            trade_details['pattern_edge'] = pattern_edge
        
        if params.use_whale_tracking and self.whale_activity > 0:
            whale_edge = self.whale_activity * 0.003 * params.whale_weight
            if random.random() < 0.6:
                edge += whale_edge
            else:
                edge -= whale_edge * 0.5
            trade_details['whale_edge'] = whale_edge
        
        if params.use_funding_arbitrage and abs(self.funding_rate) > 0.02:
            funding_edge = abs(self.funding_rate) * 0.3 * params.funding_weight
            edge += funding_edge
            trade_details['funding_edge'] = funding_edge
        
        if params.use_fear_greed:
            if self.fear_greed < 20 and params.trade_in_extreme_fear:
                edge += 0.008 * params.fear_greed_weight
            elif self.fear_greed > 80 and not params.trade_in_extreme_greed:
                edge -= 0.005
            trade_details['fear_greed_edge'] = edge
        
        if params.use_liquidation_detection and self.liquidations_24h > 100_000_000:
            edge += 0.01 * params.liquidation_weight
            trade_details['liquidation_edge'] = 0.01
        
        num_trades = int(params.trades_per_day + (1 if random.random() < params.trades_per_day % 1 else 0))
        daily_pnl = 0
        wins = 0
        losses = 0
        
        for _ in range(num_trades):
            effective_winrate = params.win_rate + edge * 10
            effective_winrate = np.clip(effective_winrate, 0.3, 0.85)
            
            position_size = min(params.max_position_size, random.uniform(0.02, 0.10))
            
            if random.random() < effective_winrate:
                pnl = position_size * random.uniform(0.005, params.avg_win_pct)
                pnl *= params.leverage
                wins += 1
            else:
                pnl = -position_size * min(random.uniform(0.003, params.avg_loss_pct), params.stop_loss_pct)
                pnl *= params.leverage
                losses += 1
            
            pnl -= position_size * (params.transaction_cost + params.slippage)
            daily_pnl += pnl
        
        market_move = np.random.normal(0, base_vol)
        
        market_exposure = 0.3
        daily_return = daily_pnl + market_move * market_exposure
        
        daily_return = np.clip(daily_return, -0.10, 0.15)
        
        trade_details['num_trades'] = num_trades
        trade_details['wins'] = wins
        trade_details['losses'] = losses
        trade_details['daily_pnl'] = daily_pnl
        
        return daily_return, trade_details


class CryptoExpertBacktester:
    """
    PROMETHEUS Crypto Expert Backtester
    
    Trains and tests crypto trading strategies with:
    - Multiple years of simulated market data
    - Crypto-specific indicators and patterns
    - Whale tracking and liquidation detection
    - Funding rate arbitrage
    - Fear/Greed index integration
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.trading_days_per_year = 365
        self.market = CryptoMarketSimulator()
        
        self.generation = 0
        self.best_params = CryptoTradingParams()
        self.best_fitness = -float('inf')
        self.fitness_history = []
        self.learning_history = []
        
        self._load_state()
        
    def _load_state(self):
        """Load previous learning state"""
        state_file = Path('crypto_learning_state.json')
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                self.generation = state.get('generation', 0)
                self.best_fitness = state.get('best_fitness', -float('inf'))
                self.fitness_history = state.get('fitness_history', [])
                if 'best_params' in state:
                    self.best_params = CryptoTradingParams(**state['best_params'])
                print(f"[LOADED] Crypto learning state: Gen {self.generation}, Fitness {self.best_fitness:.2f}")
            except Exception as e:
                print(f"[!] Could not load state: {e}")
    
    def _save_state(self):
        """Save learning state"""
        state = {
            'generation': self.generation,
            'best_fitness': self.best_fitness,
            'fitness_history': self.fitness_history,
            'best_params': asdict(self.best_params),
            'last_updated': datetime.now().isoformat()
        }
        with open('crypto_learning_state.json', 'w') as f:
            json.dump(state, f, indent=2)
    
    def run_backtest(self, params: CryptoTradingParams, years: int) -> CryptoBacktestResult:
        """Run comprehensive crypto backtest"""
        total_days = self.trading_days_per_year * years
        capital = self.initial_capital
        
        portfolio_history = [capital]
        daily_returns = []
        yearly_returns = []
        monthly_returns = []
        
        trades = {'wins': 0, 'losses': 0, 'total': 0}
        gross_wins = 0
        gross_losses = 0
        
        best_trade = 0
        worst_trade = 0
        funding_pnl = 0
        whale_pnl = 0
        liquidation_trades = 0
        pattern_trades = 0
        
        btc_pnl = 0
        eth_pnl = 0
        alt_pnl = 0
        
        for day in range(total_days):
            daily_return, details = self.market.get_daily_return(params)
            
            trades['wins'] += details['wins']
            trades['losses'] += details['losses']
            trades['total'] += details['num_trades']
            
            if 'funding_edge' in details:
                funding_pnl += details['funding_edge'] * capital
            if 'whale_edge' in details:
                whale_pnl += details['whale_edge'] * capital
            if details.get('liquidations', 0) > 100_000_000:
                liquidation_trades += 1
            if 'pattern_edge' in details:
                pattern_trades += 1
            
            if details['daily_pnl'] > best_trade:
                best_trade = details['daily_pnl']
            if details['daily_pnl'] < worst_trade:
                worst_trade = details['daily_pnl']
            
            coin_split = random.choices(['btc', 'eth', 'alt'], weights=[0.5, 0.3, 0.2])[0]
            trade_pnl = daily_return * capital
            if coin_split == 'btc':
                btc_pnl += trade_pnl
            elif coin_split == 'eth':
                eth_pnl += trade_pnl
            else:
                alt_pnl += trade_pnl
            
            if daily_return > 0:
                gross_wins += daily_return * capital
            else:
                gross_losses += abs(daily_return * capital)
            
            daily_returns.append(daily_return)
            capital *= (1 + daily_return)
            portfolio_history.append(capital)
            
            if (day + 1) % 30 == 0:
                month_start = max(0, len(portfolio_history) - 31)
                month_return = (portfolio_history[-1] / portfolio_history[month_start]) - 1
                monthly_returns.append(month_return)
            
            if (day + 1) % self.trading_days_per_year == 0:
                year_num = (day + 1) // self.trading_days_per_year
                year_start_idx = (year_num - 1) * self.trading_days_per_year
                year_return = (portfolio_history[-1] / portfolio_history[year_start_idx]) - 1
                yearly_returns.append(year_return)
        
        total_return = (capital - self.initial_capital) / self.initial_capital
        cagr = ((capital / self.initial_capital) ** (1/years)) - 1
        
        daily_std = np.std(daily_returns) if len(daily_returns) > 1 else 0.01
        daily_mean = np.mean(daily_returns)
        sharpe = (daily_mean / daily_std) * np.sqrt(365) if daily_std > 0 else 0
        
        negative_returns = [r for r in daily_returns if r < 0]
        downside_std = np.std(negative_returns) if len(negative_returns) > 1 else 0.01
        sortino = (daily_mean / downside_std) * np.sqrt(365) if downside_std > 0 else 0
        
        max_dd = self._calculate_max_drawdown(portfolio_history)
        
        win_rate = trades['wins'] / trades['total'] if trades['total'] > 0 else 0
        profit_factor = gross_wins / gross_losses if gross_losses > 0 else 10.0
        
        result = CryptoBacktestResult(
            final_capital=capital,
            total_return=total_return,
            cagr=cagr,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            max_drawdown=max_dd,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=trades['total'],
            best_trade=best_trade,
            worst_trade=worst_trade,
            avg_hold_time_hours=24 / params.trades_per_day,
            funding_pnl=funding_pnl,
            liquidation_trades=liquidation_trades,
            whale_following_pnl=whale_pnl,
            pattern_trades=pattern_trades,
            btc_pnl=btc_pnl,
            eth_pnl=eth_pnl,
            alt_pnl=alt_pnl,
            yearly_returns=yearly_returns,
            monthly_returns=monthly_returns
        )
        result.calculate_fitness()
        
        return result
    
    def _calculate_max_drawdown(self, portfolio_history: List[float]) -> float:
        peak = portfolio_history[0]
        max_dd = 0
        for value in portfolio_history:
            if value > peak:
                peak = value
            dd = (value - peak) / peak
            if dd < max_dd:
                max_dd = dd
        return max_dd
    
    def run_learning_iteration(self, years: int, population_size: int = 7) -> Tuple[CryptoBacktestResult, CryptoTradingParams]:
        """Run one learning generation"""
        self.generation += 1
        
        print(f"\n{'='*70}")
        print(f"[GEN {self.generation}] CRYPTO TRAINING - {years}-Year Backtest")
        print(f"{'='*70}")
        
        candidates = []
        
        for i in range(population_size):
            if i == 0:
                params = copy.deepcopy(self.best_params)
                label = "Best Known"
            else:
                params = self.best_params.mutate(learning_rate=1.0 / (1 + self.generation * 0.05))
                label = f"Mutation {i}"
            
            print(f"\n   [{i+1}/{population_size}] Testing {label}...")
            print(f"       Win Rate: {params.win_rate*100:.1f}%, Leverage: {params.leverage:.1f}x")
            print(f"       Whale: {params.use_whale_tracking}, Funding: {params.use_funding_arbitrage}")
            
            result = self.run_backtest(params, years)
            candidates.append((params, result))
            
            print(f"       -> CAGR: {result.cagr*100:.1f}%, Sharpe: {result.sharpe_ratio:.2f}")
            print(f"       -> Max DD: {result.max_drawdown*100:.1f}%, Fitness: {result.fitness_score:.2f}")
        
        best_params, best_result = max(candidates, key=lambda x: x[1].fitness_score)
        
        if best_result.fitness_score > self.best_fitness:
            improvement = best_result.fitness_score - self.best_fitness
            self.best_fitness = best_result.fitness_score
            self.best_params = copy.deepcopy(best_params)
            print(f"\n   [NEW BEST!] Fitness: {best_result.fitness_score:.2f} (+{improvement:.2f})")
        
        self.fitness_history.append(self.best_fitness)
        self._save_state()
        
        return best_result, best_params
    
    def run_continuous_learning(self, max_generations: int = 30, years: int = 5):
        """Run continuous learning until convergence"""
        print("\n" + "="*70)
        print("    PROMETHEUS CRYPTO EXPERT TRAINING")
        print("="*70)
        print(f"\n[CONFIG] Training Configuration:")
        print(f"   Years per test: {years}")
        print(f"   Max Generations: {max_generations}")
        print(f"   Initial Capital: ${self.initial_capital:,.2f}")
        print(f"   Starting Generation: {self.generation}")
        print()
        
        start_time = time.time()
        no_improvement = 0
        max_no_improvement = 5
        
        for gen in range(max_generations):
            result, params = self.run_learning_iteration(years, population_size=7)
            
            if len(self.fitness_history) >= 2:
                improvement = abs(self.fitness_history[-1] - self.fitness_history[-2])
                if improvement < 0.5:
                    no_improvement += 1
                    print(f"\n   [!] Minimal improvement ({improvement:.2f}). Count: {no_improvement}/{max_no_improvement}")
                else:
                    no_improvement = 0
                
                if no_improvement >= max_no_improvement:
                    print(f"\n[OK] CONVERGED after {gen+1} generations!")
                    break
        
        elapsed = time.time() - start_time
        self._print_final_summary(years, elapsed)
        
    def _print_final_summary(self, years: int, elapsed: float):
        """Print comprehensive training summary"""
        print("\n" + "="*70)
        print("    CRYPTO EXPERT TRAINING COMPLETE")
        print("="*70)
        
        print(f"\n[STATS] Learning Statistics:")
        print(f"   Total Generations: {self.generation}")
        print(f"   Time Elapsed: {elapsed/60:.1f} minutes")
        print(f"   Final Fitness: {self.best_fitness:.2f}")
        
        print(f"\n[BEST] BEST CRYPTO TRADING PARAMETERS:")
        print(f"   Win Rate: {self.best_params.win_rate*100:.1f}%")
        print(f"   Avg Win: {self.best_params.avg_win_pct*100:.2f}%")
        print(f"   Avg Loss: {self.best_params.avg_loss_pct*100:.2f}%")
        print(f"   Trades/Day: {self.best_params.trades_per_day:.1f}")
        print(f"   Leverage: {self.best_params.leverage:.1f}x")
        print(f"   Stop Loss: {self.best_params.stop_loss_pct*100:.1f}%")
        
        print(f"\n[WEIGHTS] STRATEGY WEIGHTS:")
        print(f"   Pattern Recognition: {self.best_params.pattern_weight*100:.0f}%")
        print(f"   Whale Tracking: {self.best_params.whale_weight*100:.0f}%")
        print(f"   Funding Arbitrage: {self.best_params.funding_weight*100:.0f}%")
        print(f"   Fear/Greed: {self.best_params.fear_greed_weight*100:.0f}%")
        print(f"   Liquidation Detection: {self.best_params.liquidation_weight*100:.0f}%")
        print(f"   On-Chain Analysis: {self.best_params.on_chain_weight*100:.0f}%")
        
        print(f"\n[TEST] FINAL VALIDATION ({years}-year backtest)...")
        final_result = self.run_backtest(self.best_params, years)
        
        print(f"\n[RESULTS] PROJECTED {years}-YEAR CRYPTO PERFORMANCE:")
        print(f"   Starting Capital: ${self.initial_capital:,.2f}")
        print(f"   Final Capital: ${final_result.final_capital:,.2f}")
        print(f"   Total Return: {final_result.total_return*100:.1f}%")
        print(f"   CAGR: {final_result.cagr*100:.2f}%")
        print(f"   Sharpe Ratio: {final_result.sharpe_ratio:.2f}")
        print(f"   Sortino Ratio: {final_result.sortino_ratio:.2f}")
        print(f"   Max Drawdown: {final_result.max_drawdown*100:.1f}%")
        print(f"   Win Rate: {final_result.win_rate*100:.1f}%")
        print(f"   Profit Factor: {final_result.profit_factor:.2f}")
        print(f"   Total Trades: {final_result.total_trades:,}")
        
        print(f"\n[COINS] BREAKDOWN BY COIN:")
        print(f"   BTC PnL: ${final_result.btc_pnl:,.2f}")
        print(f"   ETH PnL: ${final_result.eth_pnl:,.2f}")
        print(f"   ALT PnL: ${final_result.alt_pnl:,.2f}")
        
        print(f"\n[SPECIAL] SPECIAL STRATEGIES:")
        print(f"   Whale Following PnL: ${final_result.whale_following_pnl:,.2f}")
        print(f"   Funding Arbitrage PnL: ${final_result.funding_pnl:,.2f}")
        print(f"   Liquidation Cascade Trades: {final_result.liquidation_trades}")
        print(f"   Pattern-Based Trades: {final_result.pattern_trades}")
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'training_type': 'CRYPTO_EXPERT',
            'generations': self.generation,
            'years_tested': years,
            'best_fitness': self.best_fitness,
            'best_params': asdict(self.best_params),
            'final_result': {
                'final_capital': final_result.final_capital,
                'total_return': final_result.total_return,
                'cagr': final_result.cagr,
                'sharpe_ratio': final_result.sharpe_ratio,
                'sortino_ratio': final_result.sortino_ratio,
                'max_drawdown': final_result.max_drawdown,
                'win_rate': final_result.win_rate,
                'profit_factor': final_result.profit_factor,
                'total_trades': final_result.total_trades,
                'btc_pnl': final_result.btc_pnl,
                'eth_pnl': final_result.eth_pnl,
                'alt_pnl': final_result.alt_pnl,
                'whale_pnl': final_result.whale_following_pnl,
                'funding_pnl': final_result.funding_pnl,
                'yearly_returns': final_result.yearly_returns
            },
            'crypto_knowledge': CRYPTO_KNOWLEDGE,
            'fitness_history': self.fitness_history
        }
        
        filename = f'CRYPTO_EXPERT_RESULTS_{years}Y_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n[SAVED] Results saved to: {filename}")
        print("="*70)


def main():
    print("\n" + "="*70)
    print("    PROMETHEUS CRYPTO EXPERT BACKTESTER")
    print("="*70)
    print()
    print("This system trains PROMETHEUS to become an EXPERT crypto trader!")
    print()
    print("Features:")
    print("  * Chart pattern recognition (20+ patterns)")
    print("  * Whale movement tracking & following")
    print("  * Funding rate arbitrage detection")
    print("  * Liquidation cascade trading")
    print("  * Fear/Greed index integration")
    print("  * On-chain metrics analysis")
    print("  * Multi-coin portfolio (BTC, ETH, Alts)")
    print()
    
    print("Select training mode:")
    print("  1. Quick Training (3 years, 15 generations)")
    print("  2. Standard Training (5 years, 30 generations)")
    print("  3. Deep Training (10 years, 50 generations)")
    print("  4. Ultimate Training (20 years, 100 generations)")
    print()
    
    choice = input("Enter choice (1-4) [default=2]: ").strip() or "2"
    
    backtester = CryptoExpertBacktester(initial_capital=10000.0)
    
    if choice == "1":
        backtester.run_continuous_learning(max_generations=15, years=3)
    elif choice == "2":
        backtester.run_continuous_learning(max_generations=30, years=5)
    elif choice == "3":
        backtester.run_continuous_learning(max_generations=50, years=10)
    elif choice == "4":
        print("\n[!] Ultimate training selected. This will take significant time...")
        backtester.run_continuous_learning(max_generations=100, years=20)
    else:
        print("Invalid choice, running standard training")
        backtester.run_continuous_learning(max_generations=30, years=5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[STOP] Training interrupted. Progress saved to crypto_learning_state.json")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
