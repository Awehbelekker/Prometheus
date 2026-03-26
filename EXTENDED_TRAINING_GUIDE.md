# Extended Historical Training Guide

## 🎯 Goal
Train PROMETHEUS on multi-year historical data to get accurate annual return metrics (CAGR) instead of short-term backtest estimates.

## 📊 What This Solves

**Before:**
- Learning engine used only 120 days (4 months) of data
- Annual returns were extrapolated/estimated
- Couldn't measure true long-term performance

**After:**
- Can train on 1, 3, 5, or 10 years of real historical data
- Calculate true CAGR (Compound Annual Growth Rate)
- Measure strategies across bull/bear/sideways markets
- Get accurate time-in-market metrics

## 🚀 Quick Start

### Option 1: 5-Year Training (Recommended)
```powershell
python extended_historical_training.py --years 5
```

This will:
- Download 5 years of data for 30+ symbols
- Test your top 20 evolved strategies
- Calculate true CAGR, Sharpe, Win Rate, Max Drawdown
- Compare against S&P 500, Renaissance, Citadel benchmarks

**Expected Results:**
- CAGR: 15-35% (vs S&P 10%, Renaissance 66%)
- Sharpe: 1.5-2.0 (vs S&P 0.5)
- Takes: ~10-20 minutes

### Option 2: 10-Year Training (Maximum Data)
```powershell
python extended_historical_training.py --years 10
```

Best for:
- Most accurate CAGR calculation
- Testing across 2020 crash, recovery, bull markets
- Maximum confidence in metrics
- Takes: ~20-30 minutes

### Option 3: 1-Year Quick Test
```powershell
python extended_historical_training.py --years 1
```

Best for:
- Quick validation
- Recent market conditions only
- Takes: ~5 minutes

### Option 4: Custom Symbols
```powershell
python extended_historical_training.py --years 5 --symbols "SPY,AAPL,TSLA,NVDA"
```

## 📈 What You'll Get

### 1. True CAGR Calculation
Instead of estimating from 4 months, calculates:
```
CAGR = (Final Value / Initial Value) ^ (1 / Years) - 1
```

Example:
- $100K → $180K over 5 years = **12.47% CAGR**
- $100K → $250K over 5 years = **20.11% CAGR**

### 2. Multi-Symbol Validation
Tests each strategy on 20-30 different stocks to ensure:
- Not overfitted to one symbol
- Works across sectors
- Robust performance

### 3. Comprehensive Metrics
- **CAGR**: True annual return rate
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Worst peak-to-trough decline
- **Win Rate**: % of profitable trades
- **Trades/Year**: Activity level
- **Average Hold Time**: Trade duration

### 4. Benchmark Comparisons
Automatically compares against:
- S&P 500 (10% CAGR benchmark)
- Renaissance Medallion (66% CAGR target)
- Citadel (20% CAGR)
- Two Sigma (15% CAGR)

## 📁 Output Files

Results saved to:
```
extended_training_5yr_20260111_123456.json
```

Contains:
- All strategy results
- Symbol-by-symbol breakdown
- Aggregate metrics
- Trade details

## 🔄 Integration with Learning Engine

The extended training results feed back into the learning engine:

1. **Identifies Best Long-Term Strategies**
   - Strategies that work over years, not just months
   
2. **Refines Strategy Selection**
   - Prioritizes strategies with proven CAGR
   
3. **Improves Position Sizing**
   - Better risk assessment from real drawdown data

## 💡 Tips for Best Results

### 1. Run After Learning Engine Has Generated Strategies
```powershell
# First: Let learning engine evolve strategies
python PROMETHEUS_ULTIMATE_LEARNING_ENGINE.py
# (Let it run for a few hours)

# Then: Test those strategies on extended data
python extended_historical_training.py --years 5
```

### 2. Start with 5 Years
- Best balance of data quantity vs quality
- Captures recent market conditions
- Fast enough to iterate

### 3. Compare Multiple Time Periods
```powershell
# Test robustness
python extended_historical_training.py --years 1
python extended_historical_training.py --years 3
python extended_historical_training.py --years 5

# If CAGR consistent across all = robust strategy
```

### 4. Focus on Sharpe Ratio
- CAGR alone isn't enough
- High CAGR + Low Sharpe = high risk
- Target: Sharpe > 1.5 for institutional-grade

## 🎯 Realistic Expectations

Based on industry standards:

### Excellent Performance (Top 10% of Funds)
- CAGR: 20-35%
- Sharpe: 1.5-2.5
- Max DD: <15%
- Win Rate: 60-70%

### Good Performance (Better than S&P)
- CAGR: 12-20%
- Sharpe: 1.0-1.5
- Max DD: 15-25%
- Win Rate: 55-65%

### Market Performance (Baseline)
- CAGR: 8-12%
- Sharpe: 0.5-1.0
- Max DD: 25-40%
- Win Rate: 50-60%

### World-Class (Renaissance Level)
- CAGR: 40-66%
- Sharpe: 2.0-3.0
- Max DD: <10%
- Win Rate: 70-80%

## 🔍 Understanding the Results

### Example Output:
```
Strategy: Evolved Gen 137
CAGR: 18.5%
Sharpe: 1.82
Win Rate: 73.2%
Max DD: 12.4%
```

**What this means:**
- **18.5% CAGR**: Turn $100K into $229K over 5 years
- **1.82 Sharpe**: Excellent risk-adjusted returns (beating most hedge funds)
- **73.2% Win Rate**: Nearly 3 out of 4 trades profitable
- **12.4% Max DD**: Worst decline was 12.4% from peak

**Comparison:**
- Beats S&P 500 (10% CAGR) by 8.5%
- Competitive with top hedge funds
- Better Sharpe than Citadel (1.5)
- Lower drawdown than industry average (30%)

## 🚀 Next Steps After Training

1. **Update Live Trading Config**
   ```powershell
   # Use strategies with proven 5-year CAGR
   python update_live_strategy_weights.py
   ```

2. **Set Realistic Targets**
   - Don't expect 66% Renaissance returns immediately
   - Target 15-25% CAGR initially
   - Scale up as system proves itself

3. **Continue Learning**
   - Learning engine keeps evolving strategies
   - Re-run extended training monthly
   - Compare results to track improvement

4. **Deploy Best Strategies**
   - Focus on strategies with:
     - CAGR > 15%
     - Sharpe > 1.5
     - Max DD < 15%
     - Win Rate > 60%

## ❓ FAQ

**Q: Why not just use the learning engine's Sharpe ratios?**
A: Learning engine uses 120 days. Extended training validates over years, catching seasonal patterns and regime changes.

**Q: How long does 10-year training take?**
A: 20-30 minutes for 20 strategies × 30 symbols = 600 backtests.

**Q: Should I run this daily?**
A: No. Run when:
- Learning engine has evolved new strategies (weekly)
- Want to validate performance (monthly)
- Major market changes occur

**Q: What if CAGR is negative?**
A: Normal! Some strategies only work in certain market conditions. The learning engine will evolve better ones.

**Q: Can I use crypto symbols?**
A: Yes! Use format: `--symbols "BTC-USD,ETH-USD,SPY"`
Note: Crypto has less historical data (typically 5-7 years max).

**Q: How does this compare to the benchmark I just ran?**
A: That benchmark used learning engine's 120-day metrics. This calculates true multi-year CAGR from actual backtests.

## 🎯 Summary

**Run this command:**
```powershell
python extended_historical_training.py --years 5
```

**You'll get:**
- True CAGR over 5 years (not extrapolated)
- Multi-symbol validation (not overfitted)
- Accurate max drawdown (real worst-case)
- Industry benchmark comparisons
- Confidence in your strategies' long-term performance

**Then you can say:**
"My best strategy has a proven 18.5% CAGR over 5 years with a 1.82 Sharpe ratio, tested across 30 symbols and 1,260 trading days. This beats the S&P 500 by 8.5% annually and is competitive with top-tier hedge funds."

🏆 **That's real bragging rights backed by data!**
