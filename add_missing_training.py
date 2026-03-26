"""Add training for missing symbols"""
import json
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

print('🔧 ADDING MISSING SYMBOL TRAINING')
print('=' * 60)

# Missing symbols
missing_symbols = ['ADBE', 'PLTR', 'RBLX', 'COIN', 'AVAX-USD', 'ADA-USD', 'DOGE-USD']

# Load existing patterns
pattern_files = list(Path('.').glob('learned_patterns_*.json'))
latest = max(pattern_files, key=lambda f: f.stat().st_mtime)
with open(latest, 'r') as f:
    patterns = json.load(f)

print(f'Loaded: {latest.name}')

# Training periods
periods = [(1, '1y'), (2, '2y'), (3, '3y'), (5, '5y')]

success_count = 0

for symbol in missing_symbols:
    print(f'\n📊 Training {symbol}...')
    
    for years, period_str in periods:
        try:
            df = yf.download(symbol, period=period_str, progress=False)
            if len(df) < 50:
                continue
            
            # Calculate indicators
            df['returns'] = df['Close'].pct_change()
            df['volatility'] = df['returns'].rolling(20).std()
            df['momentum'] = df['Close'].pct_change(20)
            df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
            df = df.dropna()
            
            if len(df) < 30:
                continue
            
            # Create key (remove -USD suffix for pattern key)
            clean_symbol = symbol.replace('-USD', '')
            key = f'{clean_symbol}_{years}'
            
            # Trend pattern
            uptrend = (df['returns'] > 0).sum()
            downtrend = (df['returns'] <= 0).sum()
            patterns['trend_patterns'][key] = [{
                'angle': 'trend_identification',
                'pattern_type': 'trend_strength',
                'characteristics': {
                    'uptrend_periods': int(uptrend),
                    'downtrend_periods': int(downtrend),
                    'trend_strength_avg': float(abs(df['momentum']).mean()),
                    'uptrend_ratio': float(uptrend / len(df))
                }
            }]
            
            # Volume pattern
            patterns['volume_patterns'][key] = [{
                'angle': 'volume_analysis',
                'pattern_type': 'volume_profile',
                'characteristics': {
                    'avg_volume_ratio': float(df['volume_ratio'].mean()),
                    'volume_std': float(df['volume_ratio'].std()),
                    'high_volume_days': int((df['volume_ratio'] > 1.5).sum())
                }
            }]
            
            # Volatility pattern
            patterns['volatility_patterns'][key] = [{
                'angle': 'volatility_analysis',
                'pattern_type': 'volatility_regime',
                'characteristics': {
                    'volatility_mean': float(df['volatility'].mean()),
                    'volatility_std': float(df['volatility'].std()),
                    'high_vol_periods': int((df['volatility'] > df['volatility'].quantile(0.75)).sum())
                }
            }]
            
            # Momentum pattern
            patterns['momentum_patterns'][key] = [{
                'angle': 'momentum_analysis',
                'pattern_type': 'momentum_profile',
                'characteristics': {
                    'avg_momentum': float(df['momentum'].mean()),
                    'momentum_std': float(df['momentum'].std()),
                    'positive_momentum_ratio': float((df['momentum'] > 0).sum() / len(df))
                }
            }]
            
            # Reversal pattern
            autocorr = df['returns'].autocorr()
            if np.isnan(autocorr):
                autocorr = 0.0
            patterns['reversal_patterns'][key] = [{
                'angle': 'reversal_detection',
                'pattern_type': 'mean_reversion',
                'characteristics': {
                    'mean_reversion_strength': float(autocorr),
                    'oversold_periods': int((df['returns'] < df['returns'].quantile(0.1)).sum()),
                    'overbought_periods': int((df['returns'] > df['returns'].quantile(0.9)).sum())
                }
            }]
            
            success_count += 1
            print(f'   ✅ {key} trained')
            
        except Exception as e:
            print(f'   ❌ {symbol}_{years}y: {e}')

# Save updated patterns
with open(latest, 'w') as f:
    json.dump(patterns, f, indent=2)

print(f'\n✅ Added {success_count} new pattern sets')
print(f'📁 Saved to: {latest.name}')

# Verify counts
total = sum(len(v) if isinstance(v, dict) else 0 for v in patterns.values())
print(f'📊 Total pattern sets: {total}')
