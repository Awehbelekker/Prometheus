# PROMETHEUS Trading Platform

An autonomous, self-improving AI trading system combining multi-source market intelligence, adaptive machine learning, and dual-broker live execution across equities, ETFs, and crypto.

---

## Architecture

```
Market Data (28 sources)
        │
        ▼
Real-World Data Orchestrator  ─────►  Intelligence Signals (persisted to DB)
        │
        ▼
Signal Voting Engine
  ├── HRM Transformer (fine-tuned, 85 epochs)
  ├── Local LLM (prometheus-trader via Ollama)
  ├── LangGraph 4-node decision graph
  ├── SB3 PPO Reinforcement Learning agent
  ├── LLaVA Vision (chart pattern analysis)
  ├── Technical Analysis (RSI/MACD/Bollinger/ATR)
  ├── Unusual Options Activity (sweep detection)
  ├── Insider Trading (SEC EDGAR filings)
  ├── Analyst Ratings (yfinance consensus)
  ├── StockTwits Sentiment (bull/bear ratio)
  ├── Dark Pool Activity (volume surge detection)
  ├── Options Chain (put/call ratio)
  ├── SEC Filings RAG (earnings transcripts)
  ├── Finviz Fundamentals (insider %, short float)
  ├── Fear & Greed Index (contrarian signal)
  ├── Put/Call Ratio (CBOE options flow)
  ├── RSS News Sentiment (10 live feeds)
  ├── Earnings Calendar (pre-event risk guard)
  ├── FOMC Calendar (macro event guard)
  └── Market Regime Detector (bull/bear/sideways/volatile)
        │
        ▼
Trade Decision → Dual-Broker Execution
  ├── Alpaca (equities, crypto, 24/5)
  └── Interactive Brokers (institutional execution)
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
Parallel Shadow Trader ($100K virtual — learns alongside live trades)
        │
        ▼
prometheus_learning.db  (trade history, weights, signals, patterns)
```

---

## Self-Improvement

PROMETHEUS learns from every trade automatically:

- **AI voter weights** update hourly based on which signals predicted correctly
- **HRM checkpoint** retrains on new labeled trade outcomes
- **Ollama fine-tune** triggers after 50+ winning trades — builds `prometheus-trader` model from actual wins
- **Risk parameters** (position sizing, stop loss) adapt to recent win/loss streaks
- **Shadow trader** runs $100K virtual capital in parallel — accelerates learning without risking real money

No human intervention required. The system compounds its own edge over time.

---

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 16GB | 32GB |
| GPU | None (CPU fallback) | NVIDIA GTX 1080 Ti+ (CUDA) or AMD (DirectML) |
| Storage | 20GB free | 50GB+ |
| OS | Windows 10 | Windows 10/11 Pro |
| Python | 3.11 | 3.11 |

---

## Key Files

| File | Purpose |
|------|---------|
| `launch_ultimate_prometheus_LIVE_TRADING.py` | Main live trading launcher |
| `unified_production_server.py` | FastAPI dashboard + REST API (port 8000) |
| `prometheus_watchdog.py` | Auto-restart on crash, port cleanup |
| `run_prometheus.bat` | One-click launcher (double-click to start) |
| `core/hrm_official_integration.py` | HRM transformer — BUY/SELL/HOLD classifier |
| `core/adaptive_learning_engine.py` | 5 background self-improvement loops |
| `core/real_world_data_orchestrator.py` | Aggregates all intelligence sources |
| `core/unusual_options_activity.py` | Options sweep detection |
| `core/insider_trading_scraper.py` | SEC EDGAR insider activity |
| `core/analyst_ratings_scraper.py` | Analyst consensus via yfinance |
| `core/stocktwits_sentiment.py` | StockTwits bull/bear ratio |
| `core/darkpool_scraper.py` | Volume surge / dark pool detection |
| `core/ollama_finetuner.py` | Auto fine-tunes local LLM from winning trades |
| `trained_models/sb3_ppo_trading.zip` | Trained PPO agent (SPY 5yr, +21.5% eval) |
| `trained_models/regime_classifier.pkl` | Market regime classifier |
| `brokers/alpaca_broker.py` | Alpaca Markets integration |
| `brokers/interactive_brokers_broker.py` | Interactive Brokers Gateway integration |
| `Modelfile.prometheus` | Ollama fine-tune template |

---

## Databases

| Database | Contents |
|----------|----------|
| `prometheus_learning.db` | Trades, attribution, AI weights, signals, patterns |
| `performance_metrics.db` | Full historical performance data |
| `prometheus_trading.db` | Live trading state |
| `portfolio_persistence.db` | Open positions |
| `paper_trading.db` | Shadow/paper trading |

All SQLite with WAL mode. **Do not delete** — retraining from scratch takes hours.

> These databases are NOT included in the repo (too large). See **Migration Bundle** below.

---

## LLM Stack (Ollama — required)

| Model | Role | VRAM |
|-------|------|------|
| `llama3.1:8b` | Primary trading reasoning | ~4.9GB |
| `llava:7b` | Chart pattern vision | ~4.5GB |
| `deepseek-r1:8b` | Complex multi-step analysis | ~4.0GB |
| `prometheus-trader` | Auto-generated fine-tune (builds itself) | ~5GB |

The `prometheus-trader` model is built automatically by `core/ollama_finetuner.py` after 50+ winning trades — no manual action needed.

---

## Fresh Install (New Server)

### 1. Prerequisites

- Python 3.11 — [python.org](https://www.python.org/downloads/)
- Git — [git-scm.com](https://git-scm.com)
- Ollama — [ollama.com](https://ollama.com) (install and leave running)
- Interactive Brokers Gateway — [ibkr.com/gateway](https://www.interactivebrokers.com/en/trading/ibgateway.php)

### 2. Clone

```bash
git clone --recurse-submodules https://github.com/Awehbelekker/Prometheus.git
cd Prometheus
```

> `--recurse-submodules` is required — pulls ThinkMesh reasoning engine

### 3. Virtual Environment

```bash
# Keep this exact name — all scripts reference .venv_directml_test
python -m venv .venv_directml_test
.venv_directml_test\Scripts\activate
```

### 4. PyTorch

**NVIDIA GPU (CUDA):**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
python -c "import torch; print(torch.cuda.is_available())"  # → True
```

**AMD GPU (DirectML):**
```bash
pip install torch-directml
```

**CPU only:**
```bash
pip install torch torchvision torchaudio
```

### 5. Dependencies

```bash
pip install -r requirements.txt
pip install -e ThinkMesh/
```

### 6. Environment

```bash
copy .env.example .env
# Edit .env — fill in your API keys (see Environment Variables section below)
```

### 7. Ollama Models

```bash
ollama pull llama3.1:8b
ollama pull llava:7b
ollama pull deepseek-r1:8b
```

### 8. Restore Migration Bundle

The trained HRM model, learning database, and signal cache cannot be regenerated from code alone. Copy from an existing installation:

```
migration_bundle/
├── hrm_checkpoints/market_finetuned/   ← 270MB trained transformer (85 epochs)
├── prometheus_learning.db              ← trade history + learned weights
├── performance_metrics.db
├── trained_models/                     ← included in repo (1.7MB)
└── prometheus_real_hrm_signal_cache.npz  ← optional, saves 90min startup
```

> Without `hrm_checkpoints/market_finetuned/` the system falls back to LSTM — still functional but less accurate.

### 9. Interactive Brokers Gateway

1. Open IB Gateway and log in
2. Configure: Settings → API → Enable socket port `4002` (live) or `4001` (paper)
3. Check "Allow connections from localhost only"

### 10. Launch

```bash
# Option A — double-click
run_prometheus.bat

# Option B — manual
.venv_directml_test\Scripts\activate
python launch_ultimate_prometheus_LIVE_TRADING.py

# Option C — watchdog (auto-restarts on crash)
python prometheus_watchdog.py
```

Dashboard: `http://localhost:8000`

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
# ── Alpaca (required for stock/crypto trading) ────────────────────────────
ALPACA_LIVE_KEY=your_alpaca_live_key
ALPACA_LIVE_SECRET=your_alpaca_live_secret
ALPACA_LIVE_BASE_URL=https://api.alpaca.markets
ALPACA_PAPER_KEY=your_alpaca_paper_key
ALPACA_PAPER_SECRET=your_alpaca_paper_secret
ALPACA_PAPER_BASE_URL=https://paper-api.alpaca.markets

# Use live or paper:
ALPACA_API_KEY=your_alpaca_live_key
ALPACA_SECRET_KEY=your_alpaca_live_secret
ALPACA_BASE_URL=https://api.alpaca.markets   # or paper-api.alpaca.markets
ALPACA_PAPER_TRADING=false                   # true = paper only

# ── Interactive Brokers (optional, enhances execution) ────────────────────
IB_LIVE_ENABLED=true
IB_PORT=4002           # IB Gateway live port (NOT 7496 which is TWS)
IB_PAPER_PORT=4001
IB_HOST=127.0.0.1
IB_CLIENT_ID=1
IB_ACCOUNT=your_ib_account_number

# ── Local AI (required) ───────────────────────────────────────────────────
AI_PROVIDER=ollama
USE_LOCAL_AI=true
OLLAMA_BASE_URL=http://localhost:11434
USE_LLAVA_VISION=true

# ── Free data sources (recommended) ──────────────────────────────────────
FRED_API_KEY=your_fred_key        # free at fred.stlouisfed.org
REDDIT_CLIENT_ID=your_reddit_id   # free at reddit.com/prefs/apps
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=PROMETHEUS Trading Bot 1.0

# ── Optional / paid ───────────────────────────────────────────────────────
OPENAI_API_KEY=your_key           # fallback LLM
ANTHROPIC_API_KEY=your_key        # Claude vision
POLYGON_API_KEY=your_key          # market data
TWITTER_API_KEY=your_key          # social sentiment
```

> **Never commit your `.env` file.** It is in `.gitignore` by default.

---

## Interactive Brokers Setup

1. Download **IB Gateway** (lighter than TWS): [ibkr.com/gateway](https://www.interactivebrokers.com/en/trading/ibgateway.php)
2. Log in with your IBKR credentials
3. Go to: Configure → Settings → API → Enable ActiveX and Socket Clients
4. Set socket port to `4002` (live) or `4001` (paper)
5. Check "Allow connections from localhost only"
6. Set `IB_ACCOUNT=` in `.env` to your account number (format: `Uxxxxxxxx`)

---

## Network Transfer (Existing Install → New Server)

To copy a complete running installation over a local network:

```powershell
# On new server — receive (run first):
net share PROMETHEUS_RECV=C:\Users\NewUser\Desktop\ /GRANT:Everyone,FULL

# On existing server — send:
robocopy "C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform" \\NEW-SERVER-IP\PROMETHEUS_RECV\PROMETHEUS-Trading-Platform /E /XD .venv_directml_test .venv-gpu311 __pycache__ .git /XF *.pyc

# Then copy the venv separately (or recreate fresh — recommended):
# Recreating fresh on new server is cleaner than copying venv
```

Or use the migration bundle approach — copy only what can't be cloned:
```
hrm_checkpoints/market_finetuned/
prometheus_learning.db
performance_metrics.db
.env
```

---

## Backtesting

```bash
python prometheus_real_hrm_backtest.py
python prometheus_50_year_competitor_benchmark.py
```

---

## Dashboard

- `http://localhost:8000` — live P&L, positions, signal votes, system health
- `admin_command_center.html` — full admin panel

---

## Disclaimer

Trading involves substantial risk of loss. Past performance does not guarantee future results. Start with paper trading (`ALPACA_PAPER_TRADING=true`) to validate before committing real capital.
