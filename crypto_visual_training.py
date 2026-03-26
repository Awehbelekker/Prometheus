#!/usr/bin/env python3
"""
================================================================================
PROMETHEUS CRYPTO VISUAL TRAINING
================================================================================

Generates and trains on crypto chart patterns using local LLaVA model.
Downloads real crypto charts from exchanges and learns patterns.

Features:
- Downloads BTC, ETH, SOL, DOGE, AVAX charts
- Multiple timeframes (1m, 5m, 15m, 1h, 4h, 1d)
- Pattern recognition via LLaVA
- Saves learned patterns for live trading

================================================================================
"""

import os
import sys
import json
import time
import base64
import requests
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_visual_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to import chart generation libraries
try:
    import yfinance as yf
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    import mplfinance as mpf
    CHART_GEN_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Chart generation libs not available: {e}")
    CHART_GEN_AVAILABLE = False

OLLAMA_URL = "http://localhost:11434"
LLAVA_MODEL = "llava:7b"

# Crypto symbols to train on
CRYPTO_SYMBOLS = {
    'BTC-USD': {'name': 'Bitcoin', 'type': 'major'},
    'ETH-USD': {'name': 'Ethereum', 'type': 'major'},
    'SOL-USD': {'name': 'Solana', 'type': 'altcoin'},
    'DOGE-USD': {'name': 'Dogecoin', 'type': 'meme'},
    'AVAX-USD': {'name': 'Avalanche', 'type': 'altcoin'},
    'LINK-USD': {'name': 'Chainlink', 'type': 'defi'},
    'MATIC-USD': {'name': 'Polygon', 'type': 'layer2'},
    'ADA-USD': {'name': 'Cardano', 'type': 'altcoin'},
    'XRP-USD': {'name': 'Ripple', 'type': 'major'},
    'DOT-USD': {'name': 'Polkadot', 'type': 'altcoin'},
}

# Timeframes to analyze
TIMEFRAMES = {
    '5m': {'interval': '5m', 'period': '5d', 'bars': 100},
    '15m': {'interval': '15m', 'period': '7d', 'bars': 100},
    '1h': {'interval': '1h', 'period': '30d', 'bars': 100},
    '4h': {'interval': '1h', 'period': '60d', 'bars': 100},  # 4h approximation
    '1d': {'interval': '1d', 'period': '1y', 'bars': 250},
}

# Chart patterns knowledge base
CRYPTO_PATTERNS = {
    'bullish': [
        'double_bottom', 'inverse_head_shoulders', 'ascending_triangle',
        'bull_flag', 'cup_handle', 'falling_wedge', 'morning_star',
        'bullish_engulfing', 'hammer', 'three_white_soldiers', 'rounding_bottom'
    ],
    'bearish': [
        'double_top', 'head_shoulders', 'descending_triangle',
        'bear_flag', 'rising_wedge', 'evening_star', 'bearish_engulfing',
        'shooting_star', 'three_black_crows', 'rounding_top'
    ],
    'continuation': [
        'flag', 'pennant', 'rectangle', 'symmetrical_triangle', 'channel'
    ]
}


def check_llava():
    """Check if LLaVA is available in Ollama"""
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            for m in models:
                if 'llava' in m.get('name', '').lower():
                    logger.info(f"[OK] Found LLaVA model: {m['name']}")
                    return True
            logger.warning("LLaVA not found - will use pattern detection only")
            return False
    except Exception as e:
        logger.error(f"Ollama not available: {e}")
        return False


def download_crypto_data(symbol: str, interval: str, period: str) -> dict:
    """Download crypto OHLCV data from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            return None
        
        return {
            'symbol': symbol,
            'interval': interval,
            'data': df,
            'start': df.index[0],
            'end': df.index[-1]
        }
    except Exception as e:
        logger.warning(f"Could not download {symbol} {interval}: {e}")
        return None


def generate_candlestick_chart(data: dict, output_path: str) -> bool:
    """Generate candlestick chart for visual analysis"""
    try:
        df = data['data'].copy()
        symbol = data['symbol']
        interval = data['interval']
        
        # Style for crypto charts
        mc = mpf.make_marketcolors(
            up='#00ff00', down='#ff0000',
            edge='inherit',
            wick={'up': '#00ff00', 'down': '#ff0000'},
            volume='in'
        )
        style = mpf.make_mpf_style(
            marketcolors=mc,
            gridstyle='-',
            gridcolor='#333333',
            facecolor='#1a1a2e',
            figcolor='#1a1a2e',
            edgecolor='#ffffff'
        )
        
        # Add moving averages
        df['SMA20'] = df['Close'].rolling(20).mean()
        df['SMA50'] = df['Close'].rolling(50).mean()
        
        # Generate chart
        fig, axes = mpf.plot(
            df,
            type='candle',
            style=style,
            volume=True,
            title=f'{symbol} - {interval}',
            figsize=(12, 8),
            returnfig=True,
            addplot=[
                mpf.make_addplot(df['SMA20'], color='yellow', width=1),
                mpf.make_addplot(df['SMA50'], color='cyan', width=1)
            ]
        )
        
        fig.savefig(output_path, dpi=100, bbox_inches='tight', facecolor='#1a1a2e')
        plt.close(fig)
        
        logger.info(f"Generated chart: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Chart generation error: {e}")
        return False


def analyze_chart_with_llava(image_path: str, symbol: str) -> dict:
    """Analyze crypto chart using LLaVA vision model"""
    
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    prompt = f"""Analyze this {symbol} cryptocurrency chart for trading patterns.

You are an expert crypto trader. Identify:
1. Chart patterns (double top/bottom, head & shoulders, triangles, flags, wedges, cup & handle, etc.)
2. Trend direction: bullish, bearish, or sideways
3. Trend strength: strong, moderate, or weak
4. Key support levels (price points where buying occurs)
5. Key resistance levels (price points where selling occurs)
6. Volume pattern: increasing, decreasing, or neutral
7. Signal quality: strong, moderate, weak, or avoid
8. Confidence level: 0.0 to 1.0

Consider crypto-specific factors:
- Higher volatility than stocks
- 24/7 trading
- Whale movement patterns
- Volume spikes indicating accumulation/distribution

Respond ONLY with valid JSON:
{{"patterns": ["pattern1", "pattern2"], "trend": "bullish", "trend_strength": "moderate", "support": [95000, 92000], "resistance": [100000, 105000], "volume_pattern": "increasing", "signal": "moderate", "confidence": 0.75, "recommendation": "BUY" or "SELL" or "HOLD"}}"""

    payload = {
        "model": LLAVA_MODEL,
        "prompt": prompt,
        "images": [image_data],
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 1024
        }
    }
    
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=300
        )
        
        if resp.status_code == 200:
            result = resp.json()
            text = result.get('response', '')
            return parse_llava_response(text, symbol)
        else:
            return {'success': False, 'error': f"Status {resp.status_code}"}
            
    except requests.Timeout:
        return {'success': False, 'error': 'Timeout'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def parse_llava_response(text: str, symbol: str) -> dict:
    """Parse LLaVA JSON response"""
    try:
        # Extract JSON from response
        import re
        json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            result['success'] = True
            result['symbol'] = symbol
            result['timestamp'] = datetime.now().isoformat()
            return result
        else:
            return {
                'success': False,
                'error': 'No JSON in response',
                'raw': text[:500]
            }
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'JSON parse error: {e}',
            'raw': text[:500]
        }


def detect_patterns_technical(data: dict) -> dict:
    """Detect patterns using technical analysis (no LLaVA needed)"""
    try:
        df = data['data'].copy()
        symbol = data['symbol']
        
        patterns_found = []
        signals = []
        
        closes = df['Close'].values
        highs = df['High'].values
        lows = df['Low'].values
        volumes = df['Volume'].values
        
        # Calculate indicators
        sma20 = df['Close'].rolling(20).mean().values
        sma50 = df['Close'].rolling(50).mean().values
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        current_price = closes[-1]
        
        # Trend detection
        if len(closes) >= 50:
            trend = 'bullish' if current_price > sma50[-1] else 'bearish'
            trend_strength = 'strong' if abs(current_price - sma50[-1]) / sma50[-1] > 0.05 else 'moderate'
        else:
            trend = 'neutral'
            trend_strength = 'weak'
        
        # Double bottom detection
        if len(lows) >= 20:
            recent_lows = lows[-20:]
            min1_idx = recent_lows.argmin()
            min1 = recent_lows[min1_idx]
            
            # Check for second low
            if min1_idx < 15:
                remaining = recent_lows[min1_idx + 3:]
                if len(remaining) > 0:
                    min2_idx = remaining.argmin()
                    min2 = remaining[min2_idx]
                    
                    if abs(min1 - min2) / min1 < 0.02:  # Within 2%
                        patterns_found.append('double_bottom')
                        signals.append({'pattern': 'double_bottom', 'signal': 'bullish', 'confidence': 0.75})
        
        # Double top detection
        if len(highs) >= 20:
            recent_highs = highs[-20:]
            max1_idx = recent_highs.argmax()
            max1 = recent_highs[max1_idx]
            
            if max1_idx < 15:
                remaining = recent_highs[max1_idx + 3:]
                if len(remaining) > 0:
                    max2_idx = remaining.argmax()
                    max2 = remaining[max2_idx]
                    
                    if abs(max1 - max2) / max1 < 0.02:
                        patterns_found.append('double_top')
                        signals.append({'pattern': 'double_top', 'signal': 'bearish', 'confidence': 0.75})
        
        # RSI signals
        if current_rsi < 30:
            patterns_found.append('oversold')
            signals.append({'pattern': 'oversold', 'signal': 'bullish', 'confidence': 0.70})
        elif current_rsi > 70:
            patterns_found.append('overbought')
            signals.append({'pattern': 'overbought', 'signal': 'bearish', 'confidence': 0.70})
        
        # Volume spike
        avg_volume = volumes[-20:].mean()
        if volumes[-1] > avg_volume * 2:
            patterns_found.append('volume_spike')
            signals.append({'pattern': 'volume_spike', 'signal': trend, 'confidence': 0.65})
        
        # Support/Resistance
        support = round(lows[-20:].min(), 2)
        resistance = round(highs[-20:].max(), 2)
        
        # Overall recommendation
        bullish_signals = sum(1 for s in signals if s['signal'] == 'bullish')
        bearish_signals = sum(1 for s in signals if s['signal'] == 'bearish')
        
        if bullish_signals > bearish_signals:
            recommendation = 'BUY'
            confidence = min(0.85, 0.5 + bullish_signals * 0.1)
        elif bearish_signals > bullish_signals:
            recommendation = 'SELL'
            confidence = min(0.85, 0.5 + bearish_signals * 0.1)
        else:
            recommendation = 'HOLD'
            confidence = 0.5
        
        return {
            'success': True,
            'symbol': symbol,
            'patterns': patterns_found,
            'trend': trend,
            'trend_strength': trend_strength,
            'support': [support],
            'resistance': [resistance],
            'rsi': round(current_rsi, 2),
            'volume_pattern': 'high' if volumes[-1] > avg_volume * 1.5 else 'normal',
            'signal': 'moderate' if len(patterns_found) > 0 else 'weak',
            'confidence': confidence,
            'recommendation': recommendation,
            'signals': signals,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'symbol': data.get('symbol', 'UNKNOWN')
        }


def run_crypto_visual_training():
    """Main training loop"""
    print("\n" + "="*70)
    print("    PROMETHEUS CRYPTO VISUAL TRAINING")
    print("="*70)
    print()
    
    # Check if LLaVA is available
    use_llava = check_llava()
    
    # Create output directories
    charts_dir = Path("crypto_charts")
    charts_dir.mkdir(exist_ok=True)
    
    patterns_dir = Path("crypto_patterns")
    patterns_dir.mkdir(exist_ok=True)
    
    all_results = []
    trained_count = 0
    
    print(f"\n[CONFIG]")
    print(f"  Symbols: {len(CRYPTO_SYMBOLS)}")
    print(f"  Timeframes: {len(TIMEFRAMES)}")
    print(f"  LLaVA Vision: {'ENABLED' if use_llava else 'DISABLED (technical only)'}")
    print(f"  Charts will generate in: {charts_dir}")
    print()
    
    for symbol, info in CRYPTO_SYMBOLS.items():
        print(f"\n{'='*60}")
        print(f"[{symbol}] {info['name']} ({info['type']})")
        print(f"{'='*60}")
        
        for tf_name, tf_config in TIMEFRAMES.items():
            print(f"\n  [{tf_name}] Downloading data...")
            
            # Download data
            data = download_crypto_data(
                symbol, 
                tf_config['interval'], 
                tf_config['period']
            )
            
            if data is None:
                print(f"    [!] No data available")
                continue
            
            print(f"    [OK] Got {len(data['data'])} bars")
            
            # Generate chart if possible
            chart_path = charts_dir / f"{symbol.replace('-', '_')}_{tf_name}.png"
            
            if CHART_GEN_AVAILABLE:
                print(f"    Generating chart...")
                if generate_candlestick_chart(data, str(chart_path)):
                    
                    # Analyze with LLaVA if available
                    if use_llava:
                        print(f"    Analyzing with LLaVA...")
                        result = analyze_chart_with_llava(str(chart_path), symbol)
                    else:
                        result = detect_patterns_technical(data)
                else:
                    result = detect_patterns_technical(data)
            else:
                # Technical analysis only
                result = detect_patterns_technical(data)
            
            if result.get('success'):
                result['timeframe'] = tf_name
                result['crypto_type'] = info['type']
                all_results.append(result)
                trained_count += 1
                
                # Display results
                patterns = result.get('patterns', [])
                trend = result.get('trend', 'unknown')
                rec = result.get('recommendation', 'HOLD')
                conf = result.get('confidence', 0)
                
                print(f"    [RESULT] Trend: {trend} | Patterns: {patterns}")
                print(f"    [SIGNAL] {rec} (confidence: {conf:.0%})")
            else:
                print(f"    [!] Analysis failed: {result.get('error', 'unknown')}")
    
    # Save results
    print("\n" + "="*70)
    print("    SAVING TRAINING RESULTS")
    print("="*70)
    
    output = {
        'timestamp': datetime.now().isoformat(),
        'training_type': 'CRYPTO_VISUAL',
        'use_llava': use_llava,
        'symbols_trained': len(CRYPTO_SYMBOLS),
        'timeframes': list(TIMEFRAMES.keys()),
        'total_analyses': trained_count,
        'results': all_results,
        'pattern_knowledge': CRYPTO_PATTERNS
    }
    
    output_file = patterns_dir / f"crypto_visual_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n[SAVED] Results to: {output_file}")
    
    # Also save as latest
    latest_file = patterns_dir / "crypto_visual_training_latest.json"
    with open(latest_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    # Summary
    print("\n" + "="*70)
    print("    CRYPTO VISUAL TRAINING COMPLETE")
    print("="*70)
    print(f"\n  Total Analyses: {trained_count}")
    print(f"  Symbols: {', '.join(CRYPTO_SYMBOLS.keys())}")
    print(f"  Vision Model: {'LLaVA' if use_llava else 'Technical Only'}")
    
    # Pattern summary
    all_patterns = []
    for r in all_results:
        all_patterns.extend(r.get('patterns', []))
    
    if all_patterns:
        from collections import Counter
        pattern_counts = Counter(all_patterns)
        print(f"\n  [PATTERNS FOUND]")
        for pattern, count in pattern_counts.most_common(10):
            print(f"    {pattern}: {count}")
    
    # Recommendations summary
    recs = [r.get('recommendation', 'HOLD') for r in all_results if r.get('success')]
    if recs:
        from collections import Counter
        rec_counts = Counter(recs)
        print(f"\n  [RECOMMENDATIONS]")
        for rec, count in rec_counts.items():
            print(f"    {rec}: {count}")
    
    print("\n  [NEXT STEPS]")
    print("    1. Review crypto_charts/ for generated images")
    print("    2. Results saved to crypto_patterns/")
    print("    3. Run live trading to use these patterns")
    print("="*70)
    
    return output


if __name__ == "__main__":
    try:
        run_crypto_visual_training()
    except KeyboardInterrupt:
        print("\n\n[STOP] Training interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
