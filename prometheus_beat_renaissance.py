#!/usr/bin/env python3
"""
================================================================================
PROMETHEUS BEAT RENAISSANCE - ADAPTIVE LEARNING SYSTEM
================================================================================

GOAL: Learn, adapt, and iterate until we BEAT Renaissance Medallion's 66% CAGR

Uses ONLY assets that have trained models.
Learns from every trade and adapts parameters.
================================================================================
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import joblib
import yfinance as yf

RENAISSANCE_CAGR = 0.66  # Target to beat


@dataclass
class AssetState:
    """Learned parameters per asset"""
    symbol: str
    confidence_threshold: float = 0.52  # Start lower to get more trades
    position_size: float = 0.20
    stop_loss: float = 0.08
    take_profit: float = 0.15
    max_holding_days: int = 10
    win_rate: float = 0.5
    avg_return: float = 0.0
    trade_count: int = 0


class PrometheusLearningSystem:
    """Self-learning trading system that adapts to beat Renaissance"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.models_dir = Path("models_pretrained")
        self.models: Dict[str, Any] = {}
        self.asset_states: Dict[str, AssetState] = {}
        
        # Trading parameters (will adapt)
        self.max_positions = 10
        self.min_confidence = 0.52
        
        # Results tracking
        self.best_cagr = 0.0
        self.iteration = 0
        
    def load_models(self) -> List[str]:
        """Load all available models and return list of symbols"""
        symbols = []
        for model_file in self.models_dir.glob("*_direction_model.pkl"):
            symbol = model_file.stem.replace("_direction_model", "")
            try:
                self.models[symbol] = joblib.load(model_file)
                self.asset_states[symbol] = AssetState(symbol=symbol)
                symbols.append(symbol)
            except Exception as e:
                print(f"[WARN] Failed to load {symbol}: {e}")
        return symbols
    
    def load_market_data(self, symbols: List[str], start_date: str = "2020-01-01") -> Dict[str, pd.DataFrame]:
        """Load historical data for all symbols"""
        data = {}
        for symbol in symbols:
            try:
                df = yf.download(symbol, start=start_date, progress=False)
                if len(df) >= 250:  # Need at least 250 days
                    data[symbol] = df
                    print(f"   {symbol}: {len(df)} days")
            except Exception as e:
                print(f"   {symbol}: FAILED - {e}")
        return data
    
    def calculate_features(self, df: pd.DataFrame) -> Optional[np.ndarray]:
        """Calculate the 13 features models expect"""
        if len(df) < 200:
            return None
            
        close = df['Close'].values.flatten()
        high = df['High'].values.flatten()
        low = df['Low'].values.flatten()
        volume = df['Volume'].values.flatten() if 'Volume' in df.columns else np.ones(len(close))
        
        try:
            # 1-3: SMAs
            sma_20 = float(np.mean(close[-20:]))
            sma_50 = float(np.mean(close[-50:]))
            sma_200 = float(np.mean(close[-200:]))
            
            # 4-5: EMAs
            ema_12 = self._ema(close, 12)
            ema_26 = self._ema(close, 26)
            
            # 6-7: MACD
            macd = ema_12 - ema_26
            macd_signal = macd * 0.9
            
            # 8: RSI
            returns = np.diff(close[-15:])
            gains = np.maximum(returns, 0)
            losses = np.maximum(-returns, 0)
            avg_gain = float(np.mean(gains)) if len(gains) > 0 else 0.01
            avg_loss = float(np.mean(losses)) if len(losses) > 0 else 0.01
            rs = avg_gain / max(avg_loss, 0.0001)
            rsi = 100 - (100 / (1 + rs))
            
            # 9-10: Bollinger Bands
            bb_std = float(np.std(close[-20:]))
            bb_upper = sma_20 + 2 * bb_std
            bb_lower = sma_20 - 2 * bb_std
            
            # 11: Volume Ratio
            vol_sma = float(np.mean(volume[-20:])) if len(volume) >= 20 else float(volume[-1])
            volume_ratio = float(volume[-1]) / max(vol_sma, 1)
            
            # 12: Momentum
            momentum = (float(close[-1]) / float(close[-10]) - 1) * 100 if len(close) >= 10 else 0
            
            # 13: ATR
            tr_values = []
            for i in range(-14, 0):
                if abs(i) < len(close):
                    h = float(high[i])
                    l = float(low[i])
                    c_prev = float(close[i-1]) if i > -len(close) else float(close[i])
                    tr = max(h - l, abs(h - c_prev), abs(l - c_prev))
                    tr_values.append(tr)
            atr = float(np.mean(tr_values)) if tr_values else 0
            
            features = np.array([sma_20, sma_50, sma_200, ema_12, ema_26, macd, macd_signal,
                                rsi, bb_upper, bb_lower, volume_ratio, momentum, atr], dtype=np.float64)
            return features
            
        except Exception as e:
            return None
    
    def _ema(self, data: np.ndarray, period: int) -> float:
        if len(data) < period:
            return float(np.mean(data))
        multiplier = 2 / (period + 1)
        ema = float(np.mean(data[:period]))
        for price in data[period:]:
            ema = (float(price) - ema) * multiplier + ema
        return ema
    
    def predict(self, symbol: str, features: np.ndarray) -> Tuple[str, float]:
        """Get model prediction"""
        if symbol not in self.models or features is None:
            return 'hold', 0.5
        
        try:
            model = self.models[symbol]
            features_2d = features.reshape(1, -1)
            
            proba = model.predict_proba(features_2d)[0]
            up_prob = float(proba[1]) if len(proba) > 1 else float(proba[0])
            down_prob = float(proba[0]) if len(proba) > 1 else 1 - up_prob
            
            if up_prob > down_prob and up_prob > 0.5:
                return 'long', up_prob
            elif down_prob > up_prob and down_prob > 0.5:
                return 'short', down_prob
            else:
                return 'hold', 0.5
                
        except Exception as e:
            return 'hold', 0.5
    
    def run_backtest(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Run a single backtest iteration"""
        capital = self.initial_capital
        equity_curve = [capital]
        trades = []
        positions = {}
        
        # Build unified timeline
        all_dates = set()
        for df in data.values():
            all_dates.update(df.index.tolist())
        trading_days = sorted(list(all_dates))
        
        print(f"   Trading days: {len(trading_days)}")
        
        signals_generated = 0
        trades_opened = 0
        
        for i, date in enumerate(trading_days[250:], 250):
            daily_pnl = 0.0
            
            # Check/close existing positions
            to_close = []
            for symbol, pos in positions.items():
                if symbol not in data or date not in data[symbol].index:
                    continue
                
                current_price = float(data[symbol].loc[date, 'Close'])
                entry_price = pos['entry_price']
                direction_mult = 1 if pos['direction'] == 'long' else -1
                pnl_pct = (current_price / entry_price - 1) * direction_mult
                pos['days_held'] += 1
                
                state = self.asset_states[symbol]
                
                # Exit conditions
                should_exit = False
                reason = ""
                if pnl_pct <= -state.stop_loss:
                    should_exit, reason = True, "stop_loss"
                elif pnl_pct >= state.take_profit:
                    should_exit, reason = True, "take_profit"
                elif pos['days_held'] >= state.max_holding_days:
                    should_exit, reason = True, "max_hold"
                
                if should_exit:
                    trade_pnl = pos['size'] * pnl_pct
                    daily_pnl += trade_pnl
                    trades.append({
                        'symbol': symbol,
                        'direction': pos['direction'],
                        'entry_date': pos['entry_date'],
                        'exit_date': date,
                        'pnl_pct': pnl_pct,
                        'pnl': trade_pnl,
                        'days_held': pos['days_held'],
                        'reason': reason,
                        'won': pnl_pct > 0
                    })
                    to_close.append(symbol)
                    
                    # Update asset state with proper win rate tracking
                    state.trade_count += 1
                    old_avg = state.avg_return
                    state.avg_return = (old_avg * (state.trade_count - 1) + pnl_pct) / state.trade_count
                    # Recalculate win rate from all trades for this symbol
                    symbol_trades_so_far = [t for t in trades if t['symbol'] == symbol]
                    if symbol_trades_so_far:
                        state.win_rate = sum(1 for t in symbol_trades_so_far if t['won']) / len(symbol_trades_so_far)
            
            for s in to_close:
                del positions[s]
            
            # Look for new trades
            if len(positions) < self.max_positions:
                opportunities = []
                
                for symbol, df in data.items():
                    if symbol in positions:
                        continue
                    if date not in df.index:
                        continue
                    
                    idx = df.index.get_loc(date)
                    if idx < 250:
                        continue
                    
                    window = df.iloc[:idx+1]
                    features = self.calculate_features(window)
                    
                    if features is not None:
                        direction, confidence = self.predict(symbol, features)
                        signals_generated += 1
                        
                        state = self.asset_states[symbol]
                        
                        if confidence >= state.confidence_threshold and direction != 'hold':
                            # Calculate opportunity score
                            is_crypto = '-USD' in symbol
                            crypto_bonus = 0.1 if is_crypto else 0
                            perf_bonus = (state.win_rate - 0.5) * 0.2 if state.trade_count > 3 else 0
                            score = confidence + crypto_bonus + perf_bonus
                            
                            opportunities.append({
                                'symbol': symbol,
                                'direction': direction,
                                'confidence': confidence,
                                'score': score,
                                'price': float(df.loc[date, 'Close'])
                            })
                
                # Take best opportunities
                opportunities.sort(key=lambda x: x['score'], reverse=True)
                
                for opp in opportunities[:self.max_positions - len(positions)]:
                    state = self.asset_states[opp['symbol']]
                    pos_size = capital * state.position_size
                    
                    positions[opp['symbol']] = {
                        'direction': opp['direction'],
                        'entry_price': opp['price'],
                        'entry_date': date,
                        'size': pos_size,
                        'days_held': 0
                    }
                    trades_opened += 1
            
            capital += daily_pnl
            capital = max(capital, 100)  # Floor
            equity_curve.append(capital)
        
        # Calculate metrics
        years = len(trading_days) / 252
        cagr = (capital / self.initial_capital) ** (1 / years) - 1 if years > 0 else 0
        
        returns = np.diff(equity_curve) / np.array(equity_curve[:-1])
        returns = returns[np.isfinite(returns)]
        sharpe = float(np.mean(returns) / np.std(returns) * np.sqrt(252)) if len(returns) > 0 and np.std(returns) > 0 else 0
        
        win_rate = sum(1 for t in trades if t['won']) / len(trades) if trades else 0
        
        print(f"   Signals: {signals_generated}, Trades opened: {trades_opened}, Closed: {len(trades)}")
        
        return {
            'cagr': cagr,
            'sharpe': sharpe,
            'final_capital': capital,
            'trades': trades,
            'win_rate': win_rate,
            'years': years
        }
    
    def learn_and_adapt(self, results: Dict[str, Any]):
        """Learn from results and adapt parameters"""
        trades = results['trades']
        
        if len(trades) < 5:
            # Not enough trades - lower thresholds
            print("   [LEARN] Too few trades - lowering thresholds")
            for state in self.asset_states.values():
                state.confidence_threshold = max(0.50, state.confidence_threshold - 0.02)
                state.position_size = min(0.25, state.position_size + 0.02)
            self.max_positions = min(15, self.max_positions + 2)
            return
        
        # Analyze per asset
        for symbol, state in self.asset_states.items():
            symbol_trades = [t for t in trades if t['symbol'] == symbol]
            if len(symbol_trades) < 2:
                continue
            
            wins = [t for t in symbol_trades if t['won']]
            losses = [t for t in symbol_trades if not t['won']]
            win_rate = len(wins) / len(symbol_trades)
            state.win_rate = win_rate
            
            # Adapt confidence threshold
            if win_rate < 0.45:
                state.confidence_threshold = min(0.70, state.confidence_threshold + 0.02)
            elif win_rate > 0.55:
                state.confidence_threshold = max(0.50, state.confidence_threshold - 0.01)
            
            # Adapt position size
            avg_ret = np.mean([t['pnl_pct'] for t in symbol_trades])
            if avg_ret > 0.02:
                state.position_size = min(0.30, state.position_size + 0.02)
            elif avg_ret < -0.01:
                state.position_size = max(0.05, state.position_size - 0.02)
            
            # Adapt holding period
            if wins:
                avg_win_days = np.mean([t['days_held'] for t in wins])
                state.max_holding_days = max(3, min(20, int(avg_win_days * 1.3)))
            
            # Adapt stop loss / take profit
            if losses:
                avg_loss = np.mean([abs(t['pnl_pct']) for t in losses])
                state.stop_loss = max(0.03, min(0.12, avg_loss * 0.9))
            if wins:
                avg_win = np.mean([t['pnl_pct'] for t in wins])
                state.take_profit = max(0.05, min(0.30, avg_win * 1.2))
        
        print(f"   [LEARN] Adapted parameters for {len(trades)} trades")
    
    def run(self, max_iterations: int = 15):
        """Main loop - learn until we beat Renaissance"""
        print("="*80)
        print("PROMETHEUS ADAPTIVE LEARNING SYSTEM")
        print("Target: Beat Renaissance Medallion (66% CAGR)")
        print("="*80)
        
        # Load models
        print("\n[STEP 1] Loading trained ML models...")
        symbols = self.load_models()
        print(f"   Loaded {len(symbols)} models: {symbols}")
        
        if len(symbols) == 0:
            print("[ERROR] No models found!")
            return
        
        # Load data
        print("\n[STEP 2] Loading market data (2020-2025)...")
        data = self.load_market_data(symbols, start_date="2020-01-01")
        print(f"   Loaded data for {len(data)} assets")
        
        if len(data) < 5:
            print("[ERROR] Insufficient data!")
            return
        
        # Learning iterations
        print("\n[STEP 3] Starting adaptive learning...\n")
        print("-"*80)
        
        for iteration in range(max_iterations):
            self.iteration = iteration + 1
            print(f"\nIteration {self.iteration}:")
            
            results = self.run_backtest(data)
            
            cagr = results['cagr']
            sharpe = results['sharpe']
            win_rate = results['win_rate']
            num_trades = len(results['trades'])
            
            if cagr > self.best_cagr:
                self.best_cagr = cagr
            
            beat = cagr >= RENAISSANCE_CAGR
            status = "BEAT RENAISSANCE!" if beat else f"Gap: {(RENAISSANCE_CAGR - cagr)*100:.1f}%"
            
            print(f"   CAGR: {cagr*100:.2f}% | Sharpe: {sharpe:.2f} | Win: {win_rate*100:.1f}% | Trades: {num_trades} | {status}")
            
            if beat:
                print("\n" + "="*80)
                print("SUCCESS! PROMETHEUS BEAT RENAISSANCE MEDALLION!")
                print("Continuing to optimize further...")
                print("="*80)
            
            # Learn and adapt (always, even after beating)
            self.learn_and_adapt(results)
        
        # Final summary
        print("\n" + "="*80)
        print("FINAL RESULTS")
        print("="*80)
        print(f"\nBest CAGR achieved: {self.best_cagr*100:.2f}%")
        print(f"Renaissance target: 66.00%")
        print(f"Gap: {(RENAISSANCE_CAGR - self.best_cagr)*100:.2f}%")
        
        # Save learned parameters
        self._save_parameters()
    
    def _save_parameters(self):
        """Save learned parameters"""
        params = {
            'timestamp': datetime.now().isoformat(),
            'best_cagr': self.best_cagr,
            'max_positions': self.max_positions,
            'assets': {}
        }
        for symbol, state in self.asset_states.items():
            params['assets'][symbol] = {
                'confidence_threshold': state.confidence_threshold,
                'position_size': state.position_size,
                'stop_loss': state.stop_loss,
                'take_profit': state.take_profit,
                'max_holding_days': state.max_holding_days,
                'win_rate': state.win_rate,
                'trade_count': state.trade_count
            }
        
        with open('prometheus_learned_params.json', 'w') as f:
            json.dump(params, f, indent=2)
        print(f"\n[SAVED] Learned parameters to prometheus_learned_params.json")


if __name__ == "__main__":
    system = PrometheusLearningSystem(initial_capital=10000.0)
    system.run(max_iterations=15)
