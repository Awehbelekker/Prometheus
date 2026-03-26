# PROMETHEUS 50-Year Competitive Benchmark Results

**Last Updated:** March 4, 2026  
**Benchmark Script:** `prometheus_50_year_competitor_benchmark.py`

---

## Summary

| Mode | CAGR | Sharpe | Max DD | Rank | Rating |
|------|------|--------|--------|------|--------|
| **Synthetic (calibrated)** | 22.27% | 2.01 | -13.4% | #2/13 | 🏆 ELITE TIER |
| **Real S&P 500 (1976-2026)** | 12.90% | 1.45 | -16.2% | #7/13 | 📈 ADVANCED TIER |

---

## Synthetic Data Benchmark (Default)

Calibrated synthetic data matching real S&P 500 statistical properties (~10.5% buy-and-hold CAGR).

| Metric | Value |
|--------|-------|
| Final Capital | $232,618,717 (from $10,000) |
| CAGR | 22.27% |
| Sharpe Ratio | 2.01 |
| Max Drawdown | -13.4% |
| Rank | **#2 out of 13** |
| Beats | **11/12 competitors (91.7%)** |
| Loses to | 1 (Renaissance Medallion) |
| Rating | 🏆 **ELITE TIER — Top 3 globally** |

### Competitors Beaten (Synthetic)
- Citadel Wellington (22.5% historical CAGR)
- Two Sigma (18.0%)
- D.E. Shaw (16.7%)
- AQR Capital (14.2%)
- Bridgewater All Weather (10.5%)
- Betterment (8.5%)
- Wealthfront (8.0%)
- Robinhood Avg User (4.0%)
- Traditional 60/40 (7.5%)
- QuantConnect Community (12.0%)
- Interactive Brokers Avg (9.0%)

---

## Real S&P 500 Benchmark (`--real-data`)

Uses **actual ^GSPC prices** from 1976-01-02 to 2026-02-27 (12,644 trading days) downloaded via yfinance, with regime labels classified from rolling returns and volatility.

| Metric | Value |
|--------|-------|
| Final Capital | $4,321,077 (from $10,000) |
| CAGR | 12.90% |
| Sharpe Ratio | 1.45 |
| Max Drawdown | -16.2% |
| Buy-and-Hold CAGR | 9.01% |
| **Alpha over B&H** | **+3.89%/year** |
| Rank | **#7 out of 13** |
| Beats | 6/12 competitors (50%) |
| Rating | 📈 **ADVANCED TIER** |

### Key Context for Real Data
- S&P 500 buy-and-hold had a **-56% drawdown** in 2008-2009 — PROMETHEUS limited it to **-16.2%**
- The 3.89% annual alpha is generated purely through **regime-adaptive allocation** (no leverage, no derivatives)
- Competitor profiles still use their own historical returns (they trade many asset classes, not just S&P 500), so the comparison is somewhat asymmetric

### Real Data Regime Distribution
| Regime | Days | % |
|--------|------|---|
| Bull | 10,022 | 80.5% |
| Sideways | 1,457 | 11.7% |
| Volatile | 352 | 2.8% |
| Crash | 331 | 2.7% |
| Bear | 194 | 1.6% |
| Recovery | 89 | 0.7% |

---

## Architecture

The benchmark uses a **regime-exposure allocation model** — no individual positions, no stops, no entries/exits:

```
Portfolio return each day = market_return × allocation
```

### Core Components
1. **HMM Regime Detection** — 82% accuracy via 6-source ensemble + StatArb + World Model
2. **World Model** — transition-matrix-based proactive allocation shifts
3. **Asymmetric EMA Smoothing** — fast ramp-down (α=0.30 crash, 0.15 volatile), slow ramp-up (α=0.06)
4. **Two-Tier Market Shock Detector** — -2.5% daily → 60% cut, -1.5% → 25% cut
5. **DrawdownGuardian** — daily limit -3%, trailing stop -8%, critical DD -18%, lockout reset 30 days
6. **Consecutive Crash Fast Exit** — 2+ crash days → snap allocation to 0%

### Target Exposure by Regime
| Regime | Allocation |
|--------|-----------|
| Bull | 95% |
| Recovery | 85% |
| Sideways | 50% |
| Volatile | 35% |
| Bear | 12% |
| Crash | 0% |

---

## Live Trading Integration

The benchmark's regime-exposure model has been ported to live trading via `core/regime_exposure_manager.py` (`RegimeExposureManager` class). Integration points in `launch_ultimate_prometheus_LIVE_TRADING.py`:

1. **Position sizing** — uses `alloc_state.size_scale` (allocation × 1.37, capped 1.5)
2. **Trading cycle start** — full regime-exposure update with SPY daily return, equity, World Model prediction
3. **Entry gate** — skips all new entries when target allocation ≤ 2%

---

## How to Run

```bash
# Default (synthetic calibrated data)
python prometheus_50_year_competitor_benchmark.py

# Real S&P 500 data (1976-2026)
python prometheus_50_year_competitor_benchmark.py --real-data

# Rebuild real data regime labels (if needed)
python build_real_sp500_data.py
```

---

## Data Files
- `data/sp500_historical_1976_2026.csv` — Raw ^GSPC prices from yfinance (12,644 rows)
- `data/sp500_regime_labeled.csv` — Regime-classified real data
- `build_real_sp500_data.py` — Downloads and classifies S&P 500 data
- `core/regime_exposure_manager.py` — Live trading regime-exposure module
