# PROMETHEUS Trading Platform

An autonomous, self-improving AI trading system combining multi-source market intelligence, adaptive machine learning, and dual-broker live execution across equities, ETFs, and crypto.

---

## Architecture

```
Market Data (13+ sources)
        │
        ▼
Real-World Data Orchestrator  ─────►  Intelligence Signals (persisted)
        │
        ▼
Signal Voting Engine
  ├── HRM Transformer (fine-tuned, 85 epochs)
  ├── Local LLM  (prometheus-trader, Ollama)
  ├── LLaVA Vision (chart pattern analysis)
  ├── Technical Analysis (RSI/MACD/Bollinger/ATR)
  ├── Finviz Fundamentals (insider %, short float)
  ├── Fear & Greed Index (contrarian signal)
  ├── Put/Call Ratio (CBOE options flow)
  ├── RSS News Sentiment (9 live feeds)
  ├── Earnings Calendar (pre-event risk guard)
  ├── FOMC Calendar (macro event guard)
  └── Market Regime Detector (bull/bear/sideways/volatile)
        │
        ▼
Trade Decision → Dual-Broker Execution
  ├── Alpaca (equities, crypto, after-hours)
  └── Interactive Brokers (institutional execution, options)
        │
        ▼
Adaptive Learning Engine (5 continuous background loops)
  ├── Outcome Capture    — every 60s
  ├── Weight Updates     — every 5 min
  ├── Model Retrain      — every 1 hr
  ├── Insight Generation — every 15 min
  └── Risk Adaptation    — every 10 min
        │
        ▼
prometheus_learning.db  (all trade history, weights, signals)
```

---

## Self-Improvement

PROMETHEUS learns from every trade automatically:

- **AI voter weights** update based on which signals predicted correctly
- **HRM checkpoint** retrains on new labeled trade outcomes
- **Ollama fine-tune** triggers after 50+ winning trades — builds `prometheus-trader` model from actual market wins
- **Risk parameters** (position sizing, stop loss) adapt to recent win/loss streaks
- **Intelligence signals** from all 13+ sources are persisted to DB for ML correlation

No human intervention required. The system compounds its own edge over time.

---

## Key Files

| File | Purpose |
|------|---------|
| `launch_ultimate_prometheus_LIVE_TRADING.py` | Main live trading launcher |
| `unified_production_server.py` | FastAPI dashboard + REST API (port 8000) |
| `prometheus_watchdog.py` | Auto-restart on crash, port cleanup |
| `core/hrm_official_integration.py` | HRM transformer — BUY/SELL/HOLD classifier |
| `core/adaptive_learning_engine.py` | 5 background self-improvement loops |
| `core/real_world_data_orchestrator.py` | Aggregates all 13+ intelligence sources |
| `core/ollama_finetuner.py` | Auto fine-tunes local LLM from winning trades |
| `core/market_sentiment_scraper.py` | CNN Fear & Greed + CBOE Put/Call ratio |
| `core/market_calendar_scraper.py` | Earnings calendar + FOMC event dates |
| `core/web_scraper_integration.py` | Finviz fundamental data scraper |
| `brokers/alpaca_broker.py` | Alpaca Markets broker |
| `brokers/interactive_brokers_broker.py` | Interactive Brokers TWS/Gateway |
| `hrm_checkpoints/market_finetuned/` | Trained HRM model (85 epochs, 100% test acc) |

---

## Databases

| Database | Contents |
|----------|----------|
| `prometheus_learning.db` | Trades, attribution records, AI weights, news, intelligence signals |
| `performance_metrics.db` | Full historical performance data |
| `prometheus_trading.db` | Live trading state |
| `portfolio_persistence.db` | Open positions |
| `paper_trading.db` | Shadow/paper trading |

All SQLite with WAL mode. Do not delete — retraining from scratch takes hours.

---

## LLM Stack (Ollama)

Recommended models for GTX 1080 Ti (11GB VRAM):

| Model | Role | VRAM |
|-------|------|------|
| `prometheus-trader` | Auto fine-tuned from winning trades | ~5GB |
| `llama3.1:8b` | Primary reasoning | ~4.9GB |
| `deepseek-r1:8b` | Complex analysis | ~4.0GB |
| `llava:7b` | Chart vision | ~4.5GB |

Fine-tuning happens automatically — triggered by `adaptive_learning_engine.py` every hour when 50+ new winning trades exist.

---

## Setup

### Existing Server (DirectML / current)

```bash
# Activate existing venv
.venv_directml_test\Scripts\activate

# Launch
python launch_ultimate_prometheus_LIVE_TRADING.py
```

### New Server (CUDA / GTX 1080 Ti)

```bash
# 1. Clone
git clone https://github.com/Awehbelekker/Prometheus.git
cd Prometheus

# 2. Create venv (keep this exact name — scripts reference it)
python -m venv .venv_directml_test
.venv_directml_test\Scripts\activate

# 3. PyTorch with CUDA 12.1 (GTX 1080 Ti = CUDA 6.1, cu121 works)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 4. All dependencies
pip install -r requirements.txt

# 5. Verify GPU
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
# → True  NVIDIA GeForce GTX 1080 Ti

# 6. Restore migration bundle (copy databases, HRM checkpoint, models)
# See migration_bundle/ folder

# 7. Set environment
cp .env.example .env  # add your API keys

# 8. Install Ollama + models
# Download: https://ollama.com
ollama pull llama3.1:8b
ollama pull llava:7b

# 9. Launch
python launch_ultimate_prometheus_LIVE_TRADING.py
```

### Auto-start (Watchdog)

```powershell
# Run as Administrator:
.\SETUP_WATCHDOG_TASK.ps1
```

Or manually: `python prometheus_watchdog.py`

---

## Environment Variables

```bash
# Brokers
ALPACA_API_KEY=...
ALPACA_SECRET_KEY=...
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # switch to live when ready

# Local AI
AI_PROVIDER=ollama
USE_LOCAL_AI=true
OLLAMA_BASE_URL=http://localhost:11434
USE_LLAVA_VISION=true

# Optional
FRED_API_KEY=...          # economic calendar (FOMC, CPI, NFP dates)
WATCHDOG_SCRIPT=launch_ultimate_prometheus_LIVE_TRADING.py
```

---

## Interactive Brokers Setup

1. Download IB Gateway (not TWS — lighter)
2. Login with account `U21922116`
3. Enable API: port `4002` (live), `4001` (paper)
4. "Allow connections from localhost only" — ON

---

## Migration Bundle

The `migration_bundle/` folder contains everything that cannot be re-cloned:

```
migration_bundle/
├── databases/                    # All .db files (~500MB)
├── hrm_checkpoints_market_finetuned/  # Trained HRM (~270MB)
├── models_pretrained/            # Huggingface transformers (~252MB)
├── trained_models/               # sklearn regime classifier
├── .env                          # API keys
└── *.json                        # Config files
```

Transfer to new server via USB or network share. Do not regenerate — HRM training takes ~3-4 hours on CUDA.

---

## Backtesting

```bash
# HRM signal generation backtest
python prometheus_real_hrm_backtest.py

# 50-year competitor benchmark
python prometheus_50_year_competitor_benchmark.py
```

---

## Dashboard

`http://localhost:8000` — live P&L, positions, signal votes, system health

`admin_command_center.html` — full admin panel

---

## Disclaimer

This is a private trading system. Trading involves substantial risk of loss. Past performance does not guarantee future results. Use paper trading mode to validate before committing real capital.
