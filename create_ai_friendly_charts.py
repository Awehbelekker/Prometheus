"""
Create AI-Friendly Charts for Better Pattern Detection
======================================================
Generates cleaner, simpler charts that vision AI can analyze better.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Check for required libraries
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("matplotlib not installed. Install with: pip install matplotlib")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def create_ai_friendly_chart(symbol: str, prices: list, dates: list, output_path: str):
    """
    Create a clean, simple chart optimized for AI vision analysis.
    
    Key features:
    - White background (not dark)
    - Large, clear price labels
    - Simple candlestick/line chart
    - Moving averages visible
    - Clear trend lines
    - High contrast colors
    """
    
    if not HAS_MPL:
        return False
    
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='white')
    ax.set_facecolor('white')
    
    # Plot price line
    ax.plot(dates, prices, linewidth=2, color='#2196F3', label='Price')
    
    # Calculate and plot moving averages
    if len(prices) >= 20:
        ma20 = np.convolve(prices, np.ones(20)/20, mode='valid')
        ma20_dates = dates[19:]
        ax.plot(ma20_dates, ma20, linewidth=1.5, color='#FF9800', 
                label='20-day MA', linestyle='--')
    
    if len(prices) >= 50:
        ma50 = np.convolve(prices, np.ones(50)/50, mode='valid')
        ma50_dates = dates[49:]
        ax.plot(ma50_dates, ma50, linewidth=1.5, color='#4CAF50', 
                label='50-day MA', linestyle='-.')
    
    # Find and mark support/resistance
    price_max = max(prices)
    price_min = min(prices)
    
    # Draw horizontal lines at key levels
    ax.axhline(y=price_max, color='red', linestyle=':', alpha=0.7, 
               label=f'Resistance: ${price_max:.2f}')
    ax.axhline(y=price_min, color='green', linestyle=':', alpha=0.7,
               label=f'Support: ${price_min:.2f}')
    
    # Mark trend direction with arrow and text
    trend_direction = "UPTREND ↑" if prices[-1] > prices[0] else "DOWNTREND ↓" if prices[-1] < prices[0] else "SIDEWAYS →"
    trend_color = 'green' if 'UP' in trend_direction else 'red' if 'DOWN' in trend_direction else 'gray'
    
    ax.text(0.02, 0.98, trend_direction, transform=ax.transAxes,
            fontsize=16, fontweight='bold', color=trend_color,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Title and labels - LARGE and CLEAR
    ax.set_title(f'{symbol} Stock Chart', fontsize=20, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=14)
    ax.set_ylabel('Price ($)', fontsize=14)
    
    # Add grid for better readability
    ax.grid(True, alpha=0.3)
    
    # Legend
    ax.legend(loc='upper right', fontsize=10)
    
    # Price annotations at key points
    ax.annotate(f'${prices[0]:.2f}', xy=(dates[0], prices[0]),
                fontsize=10, color='blue')
    ax.annotate(f'${prices[-1]:.2f}', xy=(dates[-1], prices[-1]),
                fontsize=10, color='blue')
    
    # Tight layout
    plt.tight_layout()
    
    # Save with high quality
    plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    return True


def generate_sample_ai_charts():
    """Generate sample AI-friendly charts using existing data"""
    
    print("=" * 60)
    print("CREATING AI-FRIENDLY CHARTS")
    print("=" * 60)
    print()
    
    output_dir = Path("charts_ai_friendly")
    output_dir.mkdir(exist_ok=True)
    
    # Try to load existing chart data or generate sample
    symbols = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN']
    
    for symbol in symbols:
        print(f"Creating AI-friendly chart for {symbol}...")
        
        # Generate sample price data (you can replace with real data)
        np.random.seed(hash(symbol) % 2**32)
        days = 90
        dates = [datetime.now() - timedelta(days=days-i) for i in range(days)]
        
        # Random walk for realistic-ish prices
        base_price = np.random.uniform(100, 500)
        returns = np.random.normal(0.001, 0.02, days)
        prices = base_price * np.cumprod(1 + returns)
        prices = prices.tolist()
        
        output_path = output_dir / f"{symbol}_ai_friendly.png"
        
        if create_ai_friendly_chart(symbol, prices, dates, str(output_path)):
            print(f"  ✓ Created: {output_path}")
        else:
            print(f"  ✗ Failed to create chart for {symbol}")
    
    print()
    print(f"AI-friendly charts saved to: {output_dir}")
    print()
    
    return output_dir


if __name__ == "__main__":
    if not HAS_MPL:
        print("ERROR: matplotlib required!")
        print("Run: pip install matplotlib")
        sys.exit(1)
    
    generate_sample_ai_charts()
    
    print("=" * 60)
    print("CHART FORMAT COMPARISON")
    print("=" * 60)
    print()
    print("Original charts issues:")
    print("  - May have dark backgrounds")
    print("  - Small/hard to read text")
    print("  - Too many overlapping indicators")
    print("  - Complex color schemes")
    print()
    print("AI-friendly charts features:")
    print("  ✓ White background")
    print("  ✓ Large, clear labels")
    print("  ✓ Simple price line + moving averages")
    print("  ✓ Explicit trend label")
    print("  ✓ Clear support/resistance lines")
    print("  ✓ High contrast colors")
    print()
