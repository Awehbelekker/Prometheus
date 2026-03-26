#!/usr/bin/env python3
"""
PROMETHEUS REALISTIC BENCHMARK - WITH REAL TRADING COSTS
Includes: Fees, Slippage, Spread, Failed Orders
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

# REALISTIC TRADING COSTS
COSTS = {
    'crypto': {'fee': 0.001, 'slippage': 0.002, 'spread': 0.003},  # 0.6% total
    'stock': {'fee': 0.0, 'slippage': 0.0005, 'spread': 0.0002},   # 0.07% total
    'etf': {'fee': 0.0, 'slippage': 0.0003, 'spread': 0.0001},     # 0.04% total
}
EXECUTION_FAILURE_RATE = 0.05

@dataclass
class Asset:
    symbol: str
    name: str
    asset_type: str

class ModelLoader:
    def __init__(self, models_dir: str = "models_pretrained"):
        self.models_dir = Path(models_dir)
        self.models: Dict[str, Any] = {}
        
    def load_models(self, symbols: List[str]) -> Dict[str, bool]:
        status = {}
        for symbol in symbols:
            model_key = symbol.replace('/', '-')
            path = self.models_dir / f"{model_key}_direction_model.pkl"
            loaded = False
            if JOBLIB_AVAILABLE and path.exists():
                try:
                    self.models[f"{symbol}_direction"] = joblib.load(path)
                    loaded = True
                except:
                    pass
            status[symbol] = loaded
        return status
    
    def predict(self, symbol: str, features: np.ndarray) -> Tuple[str, float]:
        if features is None:
            return 'hold', 0.5
        key = f"{symbol}_direction"
        if key in self.models:
            try:
                model = self.models[key]
                if len(features.shape) == 1:
                    features = features.reshape(1, -1)
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(features)[0]
                    up_prob = float(proba[1]) if len(proba) > 1 else float(proba[0])
                    return ('long', up_prob) if up_prob > 0.5 else ('short', 1 - up_prob)
            except:
                pass
        return 'hold', 0.5

class FeatureEngineer:
    @staticmethod
    def calculate_features(df: pd.DataFrame) -> Optional[np.ndarray]:
        if len(df) < 200:
            return None
        close = df['Close'].values.flatten()
        high = df['High'].values.flatten()
        low = df['Low'].values.flatten()
        volume = df['Volume'].values.flatten() if 'Volume' in df.columns else np.ones(len(close))
        
        sma_20 = float(np.mean(close[-20:]))
        sma_50 = float(np.mean(close[-50:]))
        sma_200 = float(np.mean(close[-200:]))
        
        def ema(data, period):
            if len(data) < period:
                return float(np.mean(data))
            mult = 2 / (period + 1)
            e = float(np.mean(data[:period]))
            for p in data[period:]:
                e = (float(p) - e) * mult + e
            return e
        
        ema_12, ema_26 = ema(close, 12), ema(close, 26)
        macd = ema_12 - ema_26
        macd_signal = macd * 0.9
        
        returns = np.diff(close[-15:])
        gains, losses = np.maximum(returns, 0), np.maximum(-returns, 0)
        rs = float(np.mean(gains)) / max(float(np.mean(losses)), 0.0001)
        rsi = 100 - (100 / (1 + rs))
        
        bb_std = float(np.std(close[-20:]))
        bb_upper, bb_lower = sma_20 + 2 * bb_std, sma_20 - 2 * bb_std
        
        vol_sma = float(np.mean(volume[-20:])) if len(volume) >= 20 else float(volume[-1])
        volume_ratio = float(volume[-1]) / max(vol_sma, 1)
        momentum = (float(close[-1]) / float(close[-10]) - 1) * 100 if len(close) >= 10 else 0
        
        tr_values = []
        for i in range(-14, 0):
            if abs(i) < len(close):
                tr = max(float(high[i]) - float(low[i]), 
                        abs(float(high[i]) - float(close[i-1])), 
                        abs(float(low[i]) - float(close[i-1])))
                tr_values.append(tr)
        atr = float(np.mean(tr_values)) if tr_values else 0
        
        return np.array([sma_20, sma_50, sma_200, ema_12, ema_26, macd, macd_signal,
                        rsi, bb_upper, bb_lower, volume_ratio, momentum, atr])

class RealisticBacktest:
    ASSETS = [
        Asset("BTC-USD", "Bitcoin", "crypto"), Asset("ETH-USD", "Ethereum", "crypto"),
        Asset("SOL-USD", "Solana", "crypto"), Asset("ADA-USD", "Cardano", "crypto"),
        Asset("AVAX-USD", "Avalanche", "crypto"), Asset("DOT-USD", "Polkadot", "crypto"),
        Asset("AAPL", "Apple", "stock"), Asset("MSFT", "Microsoft", "stock"),
        Asset("NVDA", "Nvidia", "stock"), Asset("AMD", "AMD", "stock"),
        Asset("GOOGL", "Google", "stock"), Asset("AMZN", "Amazon", "stock"),
        Asset("META", "Meta", "stock"), Asset("NFLX", "Netflix", "stock"),
        Asset("SPY", "S&P 500", "etf"), Asset("QQQ", "Nasdaq", "etf"),
    ]
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.model_loader = ModelLoader()
        self.position_size = 0.15
        self.confidence_threshold = 0.55
        self.stop_loss = 0.05
        self.take_profit = 0.10
        self.max_holding_days = 7
        self.max_positions = 6
        
    def get_costs(self, asset_type: str, value: float) -> float:
        c = COSTS.get(asset_type, COSTS['stock'])
        return value * (c['fee'] + c['slippage'] + c['spread'])
    
    def run(self, start_date: str = "2020-01-01") -> Dict:
        print("="*70)
        print(" PROMETHEUS REALISTIC BENCHMARK (WITH FEES & SLIPPAGE)")
        print("="*70)
        
        symbols = [a.symbol for a in self.ASSETS]
        status = self.model_loader.load_models(symbols)
        loaded = sum(1 for v in status.values() if v)
        print(f"\n[MODELS] Loaded {loaded}/{len(symbols)}")
        
        active = [a for a in self.ASSETS if status.get(a.symbol, False)]
        asset_types = {a.symbol: a.asset_type for a in self.ASSETS}
        
        print(f"[DATA] Loading from {start_date}...")
        data = {}
        for a in active:
            try:
                df = yf.download(a.symbol, start=start_date, progress=False)
                if len(df) > 200:
                    data[a.symbol] = df
            except:
                pass
        print(f"[DATA] {len(data)} assets loaded")
        
        if len(data) < 3:
            return {}
        
        capital = self.initial_capital
        equity_curve = [capital]
        trades = []
        positions = {}
        total_costs = 0
        failed = 0
        
        all_dates = set()
        for df in data.values():
            all_dates.update(df.index.tolist())
        days = sorted(list(all_dates))
        
        for i, date in enumerate(days[200:], 200):
            daily_pnl = 0.0
            closed = []
            
            for sym, pos in positions.items():
                if sym not in data or date not in data[sym].index:
                    continue
                price = float(data[sym].loc[date, 'Close'])
                pnl_pct = (price / pos['entry'] - 1) * (1 if pos['dir'] == 'long' else -1)
                pos['days'] += 1
                
                if pnl_pct <= -self.stop_loss or pnl_pct >= self.take_profit or pos['days'] >= self.max_holding_days:
                    exit_val = pos['size'] * (1 + pnl_pct)
                    exit_cost = self.get_costs(asset_types.get(sym, 'stock'), exit_val)
                    total_costs += exit_cost
                    net_pnl = pos['size'] * pnl_pct - exit_cost - pos['cost']
                    daily_pnl += net_pnl
                    trades.append({'symbol': sym, 'pnl_pct': pnl_pct, 'pnl_net': net_pnl, 
                                  'costs': pos['cost'] + exit_cost, 'won': net_pnl > 0})
                    closed.append(sym)
            
            for s in closed:
                del positions[s]
            
            if len(positions) < self.max_positions:
                opps = []
                for sym, df in data.items():
                    if sym in positions or date not in df.index:
                        continue
                    idx = df.index.get_loc(date)
                    if idx < 200:
                        continue
                    features = FeatureEngineer.calculate_features(df.iloc[:idx+1])
                    if features is not None:
                        direction, conf = self.model_loader.predict(sym, features)
                        if conf >= self.confidence_threshold and direction != 'hold':
                            opps.append({'sym': sym, 'dir': direction, 'conf': conf,
                                        'price': float(df.loc[date, 'Close']),
                                        'type': asset_types.get(sym, 'stock')})
                
                opps.sort(key=lambda x: x['conf'], reverse=True)
                for o in opps[:self.max_positions - len(positions)]:
                    if np.random.random() < EXECUTION_FAILURE_RATE:
                        failed += 1
                        continue
                    val = capital * self.position_size
                    cost = self.get_costs(o['type'], val)
                    total_costs += cost
                    positions[o['sym']] = {'dir': o['dir'], 'entry': o['price'],
                                          'size': val, 'days': 0, 'cost': cost}
            
            capital += daily_pnl
            capital = max(capital, 1)
            equity_curve.append(capital)
        
        years = len(days) / 252
        cagr = (capital / self.initial_capital) ** (1 / years) - 1 if years > 0 else 0
        returns = np.diff(equity_curve) / np.array(equity_curve[:-1])
        returns = returns[~np.isnan(returns) & ~np.isinf(returns)]
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 0 and np.std(returns) > 0 else 0
        peak = np.maximum.accumulate(equity_curve)
        max_dd = np.min((np.array(equity_curve) - peak) / peak)
        win_rate = sum(1 for t in trades if t['won']) / len(trades) if trades else 0
        
        gross_pnl = sum(t['pnl_pct'] * self.initial_capital * self.position_size for t in trades)
        net_pnl = capital - self.initial_capital
        
        print("\n" + "="*70)
        print(" RESULTS (WITH REALISTIC COSTS)")
        print("="*70)
        print(f"\n   Initial:      ${self.initial_capital:,.2f}")
        print(f"   Final:        ${capital:,.2f}")
        print(f"   NET CAGR:     {cagr*100:.2f}%")
        print(f"   Sharpe:       {sharpe:.2f}")
        print(f"   Max DD:       {max_dd*100:.2f}%")
        print(f"   Win Rate:     {win_rate*100:.1f}%")
        print(f"   Trades:       {len(trades)}")
        print(f"   Failed:       {failed}")
        print(f"\n   TOTAL COSTS:  ${total_costs:,.2f}")
        print(f"   Cost Impact:  {total_costs/max(abs(net_pnl+total_costs),1)*100:.1f}% of gross P&L")
        
        gap = 0.66 - cagr
        if gap <= 0:
            print(f"\n   [VICTORY] BEATS RENAISSANCE by {abs(gap)*100:.2f}%!")
        else:
            print(f"\n   Gap to Renaissance (66%): {gap*100:.2f}%")
        
        return {'cagr': cagr, 'sharpe': sharpe, 'max_dd': max_dd, 'trades': len(trades),
                'win_rate': win_rate, 'costs': total_costs, 'final': capital}

if __name__ == "__main__":
    RealisticBacktest(10000).run("2020-01-01")
