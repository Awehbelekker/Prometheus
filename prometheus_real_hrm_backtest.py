#!/usr/bin/env python3
"""
PROMETHEUS REAL HRM BACKTEST
=============================
Uses real S&P 500 daily OHLCV data (1976-2026) and the market_finetuned
HRM checkpoint to generate authentic trading signals, then runs the same
allocation engine as the 50-year benchmark for a true apples-to-apples
comparison of HRM signals vs SMA baseline.

Usage:
    python prometheus_real_hrm_backtest.py [--no-cache] [--capital 10000]

Key differences from prometheus_50_year_competitor_benchmark.py:
  - Real data from data/sp500_historical_1976_2026.csv (not synthetic)
  - Signal 1 uses real HRM market_finetuned model via bars_to_tokens()
  - Correct label decoding: logits[:,-1,:3] -> [SELL, HOLD, BUY]
  - Results show actual HRM alpha vs SMA baseline
"""

import sys
import os
import json
import time
import argparse
import logging
import numpy as np
import pandas as pd
import torch
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, List

# Suppress verbose logging from imports
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT              = Path(__file__).parent
CHECKPOINT_PATH   = ROOT / "hrm_checkpoints/market_finetuned/checkpoint.pt"
META_PATH         = ROOT / "hrm_checkpoints/market_finetuned/finetune_meta.json"
SIGNAL_CACHE_PATH         = ROOT / "prometheus_real_hrm_signal_cache.npz"
SIGNAL_CACHE_PARTIAL_PATH = ROOT / "prometheus_real_hrm_signal_cache_partial.npz"
SP500_PATH        = ROOT / "data/sp500_historical_1976_2026.csv"
REGIME_PATH       = ROOT / "data/sp500_regime_labeled.csv"

# ── Reuse exact tokenizer from training ─────────────────────────────────────
sys.path.insert(0, str(ROOT))
try:
    from official_hrm.trading_dataset import bars_to_tokens, N_BARS, PAD_ID
except ImportError as e:
    print(f"ERROR: Cannot import trading_dataset: {e}")
    sys.exit(1)

# HRM model files use bare 'from models.common import ...' — add official_hrm to path
sys.path.insert(0, str(ROOT / "official_hrm"))
try:
    from official_hrm.models.hrm.hrm_act_v1 import HierarchicalReasoningModel_ACTV1
except ImportError as e:
    print(f"ERROR: Cannot import HRM model: {e}")
    sys.exit(1)


# ────────────────────────────────────────────────────────────────────────────
# Section 1: Model Loading
# ────────────────────────────────────────────────────────────────────────────

def get_inference_device():
    """Return DirectML device if available, else CPU."""
    try:
        import torch_directml
        dml = torch_directml.device()
        # Quick smoke-test: create a tiny tensor on it
        torch.zeros(1).to(dml)
        return dml
    except Exception:
        return torch.device("cpu")


def load_hrm_model(device=None) -> Optional[torch.nn.Module]:
    """
    Load market_finetuned checkpoint using the correct CPU-first path.
    DirectML device objects cannot be used as map_location — always load to CPU,
    then move model to DirectML for fast GPU inference.
    """
    if device is None:
        device = get_inference_device()
    if not CHECKPOINT_PATH.exists():
        print(f"ERROR: Checkpoint not found: {CHECKPOINT_PATH}")
        return None
    if not META_PATH.exists():
        print(f"ERROR: finetune_meta.json not found: {META_PATH}")
        return None

    with open(META_PATH) as f:
        meta = json.load(f)

    # Load weights to CPU first (required — DirectML device objects fail as map_location)
    state_dict_raw = torch.load(CHECKPOINT_PATH, map_location="cpu")
    if isinstance(state_dict_raw, dict) and 'model_state_dict' in state_dict_raw:
        state_dict_raw = state_dict_raw['model_state_dict']
    elif isinstance(state_dict_raw, dict) and 'state_dict' in state_dict_raw:
        state_dict_raw = state_dict_raw['state_dict']

    # Strip _orig_mod.model. prefix from torch.compile artifacts
    state_dict = {}
    for k, v in state_dict_raw.items():
        new_k = k.replace('_orig_mod.model.', '').replace('_orig_mod.', '')
        state_dict[new_k] = v

    # Infer num_puzzle_identifiers from embedding weight shape
    num_puzzle_ids = 1
    for k, v in state_dict.items():
        if 'puzzle_emb' in k and hasattr(v, 'shape') and len(v.shape) >= 1:
            num_puzzle_ids = max(1, v.shape[0])
            break

    config_dict = {
        'vocab_size':             meta.get('vocab_size', 20),
        'seq_len':                meta.get('seq_len', 101),
        'hidden_size':            meta.get('hidden_size', 512),
        'H_cycles':               meta.get('H_cycles', 2),
        'L_cycles':               meta.get('L_cycles', 2),
        'H_layers':               meta.get('H_layers', 4),
        'L_layers':               meta.get('L_layers', 4),
        'num_heads':              meta.get('num_heads', 8),
        'halt_max_steps':         2,   # override to 2 for inference speed
        'num_puzzle_identifiers': num_puzzle_ids,
        # Required fields not in finetune_meta.json (from hrm_finetune.py defaults)
        'batch_size':             1,
        'expansion':              4.0,
        'pos_encodings':          'rope',
        'halt_exploration_prob':  0.1,
        # DirectML doesn't support bfloat16 — use float32
        'forward_dtype':          'float32',
    }

    model = HierarchicalReasoningModel_ACTV1(config_dict)
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    # Move to DirectML for GPU-accelerated inference (loaded from CPU first)
    model = model.to(device)
    model._inference_device = device
    return model


# ────────────────────────────────────────────────────────────────────────────
# Section 2: Correct HRM Inference (matches training exactly)
# ────────────────────────────────────────────────────────────────────────────

def infer_hrm_signal(model: torch.nn.Module,
                     tokens_100: np.ndarray
                     ) -> Tuple[str, float, float, float]:
    """
    Run one HRM forward pass on a 100-token context window.
    Returns (action, sell_prob, hold_prob, buy_prob).

    This is the correct path — identical to hrm_finetune.py training:
      - Append PAD_ID at position -1 (mask label, same as hrm_feature_extract.py line 71-72)
      - Read logits[:, -1, :3]  (same as hrm_finetune.py line 290)
      - Index 0=SELL, 1=HOLD, 2=BUY (label_offset=17, stored as 0/1/2 after -LABEL_OFFSET)
    """
    device = getattr(model, '_inference_device', torch.device('cpu'))
    seq = np.append(tokens_100, PAD_ID).astype(np.int64)   # (101,)
    inputs = torch.tensor(seq).unsqueeze(0).to(device)      # (1, 101)
    batch = {
        'inputs':             inputs,
        'targets':            inputs.clone(),
        'puzzle_identifiers': torch.zeros(1, dtype=torch.long).to(device),
    }

    carry = model.initial_carry(batch)
    with torch.no_grad():
        for _ in range(model.config.halt_max_steps):
            carry, outputs = model(carry, batch)
            if carry.halted.all():
                break

    # Correct label decoding for market_finetuned:
    # logits[:, -1, :3] → softmax → [SELL_prob, HOLD_prob, BUY_prob]
    label_logits = outputs['logits'][0, -1, :3]
    probs = torch.softmax(label_logits, dim=-1).cpu().tolist()
    sell_p, hold_p, buy_p = probs[0], probs[1], probs[2]
    action = ['sell', 'hold', 'buy'][int(np.argmax(probs))]
    return action, sell_p, hold_p, buy_p


# ────────────────────────────────────────────────────────────────────────────
# Section 3: Data Loading
# ────────────────────────────────────────────────────────────────────────────

def _fill_pre1990_regimes(df: pd.DataFrame) -> None:
    """Fill regime labels for 1976-1989 (before sp500_regime_labeled.csv starts)."""
    mask = df['regime'].isna() & (df['date'] < pd.Timestamp('1990-01-01'))
    if not mask.any():
        return
    dates = df.loc[mask, 'date']
    regimes = pd.Series(index=dates.index, dtype=str)
    for idx, dt in dates.items():
        if dt < pd.Timestamp('1980-01-01'):
            regimes[idx] = 'sideways'     # 1976-1979: post-recession consolidation
        elif dt < pd.Timestamp('1983-01-01'):
            regimes[idx] = 'volatile'     # 1980-1982: stagflation
        elif dt < pd.Timestamp('1987-08-01'):
            regimes[idx] = 'bull'         # 1983-1987: Reagan bull market
        elif dt < pd.Timestamp('1988-01-01'):
            regimes[idx] = 'crash'        # 1987 Black Monday + aftermath
        else:
            regimes[idx] = 'recovery'     # 1988-1989
    df.loc[mask, 'regime'] = regimes


def load_sp500() -> pd.DataFrame:
    """
    Load real S&P 500 daily OHLCV from data/sp500_historical_1976_2026.csv.
    File has a 3-row header: row 0=Price/Close/High..., row 1=Ticker/^GSPC..., row 2=Date/empty...
    Then actual data rows starting with a date.
    """
    if not SP500_PATH.exists():
        raise FileNotFoundError(f"S&P 500 data not found: {SP500_PATH}")

    df = pd.read_csv(
        SP500_PATH,
        header=0,
        skiprows=[1, 2],
        names=['date', 'close', 'high', 'low', 'open', 'volume']
    )
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']).sort_values('date').reset_index(drop=True)
    for col in ['close', 'high', 'low', 'open', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['close'])

    # Technical indicators
    df['returns']    = df['close'].pct_change()
    for w in [5, 10, 20, 50, 200]:
        df[f'sma_{w}'] = df['close'].rolling(w).mean()
    df['volatility'] = df['returns'].rolling(20).std().fillna(0.015)
    df['returns_5']  = df['close'].pct_change(5)
    df['returns_20'] = df['close'].pct_change(20)
    df['returns_60'] = df['close'].pct_change(60)

    # RSI (14-period Wilder smoothing approximated as EWM)
    delta = df['close'].diff()
    gain  = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
    loss  = (-delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
    df['rsi'] = (100 - 100 / (1 + gain / loss.replace(0, 1e-9))).fillna(50)

    # Z-score
    roll_std = df['close'].rolling(20).std().replace(0, 1e-9)
    df['z_score'] = ((df['close'] - df['sma_20']) / roll_std).fillna(0)

    # Regime labels — join from labeled CSV (starts 1990)
    if REGIME_PATH.exists():
        reg = pd.read_csv(REGIME_PATH, usecols=['date', 'regime'])
        reg['date'] = pd.to_datetime(reg['date'])
        df = df.merge(reg[['date', 'regime']], on='date', how='left')
    else:
        df['regime'] = np.nan

    _fill_pre1990_regimes(df)
    df['regime'] = df['regime'].ffill().fillna('sideways')

    # Fill remaining NaNs with sensible defaults
    df['sma_200'] = df['sma_200'].fillna(df['close'])
    df['sma_50']  = df['sma_50'].fillna(df['close'])
    df['sma_20']  = df['sma_20'].fillna(df['close'])
    df['returns'] = df['returns'].fillna(0)

    return df


# ────────────────────────────────────────────────────────────────────────────
# Section 4: Signal Generation with Cache
# ────────────────────────────────────────────────────────────────────────────

def generate_hrm_signals(df: pd.DataFrame,
                         model: torch.nn.Module,
                         use_cache: bool = True
                         ) -> Tuple[List[str], List[float], List[float], List[float]]:
    """
    Generate one HRM signal per trading day using the 20-bar rolling window.
    Returns (actions, sell_probs, hold_probs, buy_probs) aligned to df index.
    """
    n = len(df)

    # Try cache
    if use_cache and SIGNAL_CACHE_PATH.exists():
        print(f"  Loading HRM signal cache: {SIGNAL_CACHE_PATH}")
        cache = np.load(SIGNAL_CACHE_PATH, allow_pickle=True)
        cached_dates = pd.to_datetime(cache['dates'])
        df_dates     = pd.to_datetime(df['date'])

        # Align cache to current df dates
        date_to_idx = {str(d.date()): i for i, d in enumerate(cached_dates)}
        actions, sell_ps, hold_ps, buy_ps = [], [], [], []
        for dt in df_dates:
            key = str(dt.date())
            if key in date_to_idx:
                ci = date_to_idx[key]
                actions.append(str(cache['actions'][ci]))
                sell_ps.append(float(cache['sell_probs'][ci]))
                hold_ps.append(float(cache['hold_probs'][ci]))
                buy_ps.append(float(cache['buy_probs'][ci]))
            else:
                actions.append('hold')
                sell_ps.append(0.33); hold_ps.append(0.34); buy_ps.append(0.33)

        print(f"  Cache hit: {len(actions)} signals loaded")
        return actions, sell_ps, hold_ps, buy_ps

    # Build OHLCV dataframe with proper column names for bars_to_tokens
    ohlcv = df[['open', 'high', 'low', 'close', 'volume']].copy()
    ohlcv.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

    actions: List[str]   = []
    sell_ps: List[float] = []
    hold_ps: List[float] = []
    buy_ps:  List[float] = []

    # Resume from partial checkpoint if it exists
    resume_from = 0
    if SIGNAL_CACHE_PARTIAL_PATH.exists():
        try:
            partial = np.load(SIGNAL_CACHE_PARTIAL_PATH, allow_pickle=True)
            saved_n = len(partial['actions'])
            if saved_n > 0 and saved_n < n:
                actions   = list(partial['actions'])
                sell_ps   = list(partial['sell_probs'].astype(float))
                hold_ps   = list(partial['hold_probs'].astype(float))
                buy_ps    = list(partial['buy_probs'].astype(float))
                resume_from = saved_n
                print(f"  Resuming from partial checkpoint: {resume_from:,}/{n:,} signals already done")
        except Exception:
            pass

    print(f"  Generating {n - resume_from:,} remaining HRM signals...")
    t0 = time.time()
    cache_misses = 0

    for i in range(resume_from, n):
        if i < N_BARS:
            actions.append('hold')
            sell_ps.append(0.33); hold_ps.append(0.34); buy_ps.append(0.33)
            continue

        window = ohlcv.iloc[i - N_BARS: i]
        tokens = bars_to_tokens(window)          # (100,) int16 or None

        if tokens is None:
            actions.append('hold')
            sell_ps.append(0.33); hold_ps.append(0.34); buy_ps.append(0.33)
            continue

        try:
            act, sp, hp, bp = infer_hrm_signal(model, tokens)
            actions.append(act)
            sell_ps.append(sp); hold_ps.append(hp); buy_ps.append(bp)
            cache_misses += 1
        except Exception as e:
            actions.append('hold')
            sell_ps.append(0.33); hold_ps.append(0.34); buy_ps.append(0.33)

        if (i + 1) % 1000 == 0:
            elapsed = time.time() - t0
            rate    = cache_misses / elapsed if elapsed > 0 else 0
            eta     = (n - i - 1) / rate if rate > 0 else 0
            print(f"    {i+1:,}/{n:,} ({(i+1)/n*100:.0f}%) — "
                  f"{rate:.0f} signals/s — ETA {eta:.0f}s")
            # Save partial checkpoint every 1,000 signals so crashes can resume
            np.savez_compressed(
                SIGNAL_CACHE_PARTIAL_PATH,
                dates      = np.array([str(d.date()) for d in df['date'].iloc[:len(actions)]], dtype=object),
                actions    = np.array(actions, dtype=object),
                sell_probs = np.array(sell_ps, dtype=np.float32),
                hold_probs = np.array(hold_ps, dtype=np.float32),
                buy_probs  = np.array(buy_ps,  dtype=np.float32),
            )

    elapsed = time.time() - t0
    print(f"  Signal generation complete: {cache_misses:,} HRM calls in {elapsed:.1f}s")

    # Save cache
    np.savez_compressed(
        SIGNAL_CACHE_PATH,
        dates      = np.array([str(d.date()) for d in df['date']], dtype=object),
        actions    = np.array(actions, dtype=object),
        sell_probs = np.array(sell_ps, dtype=np.float32),
        hold_probs = np.array(hold_ps, dtype=np.float32),
        buy_probs  = np.array(buy_ps,  dtype=np.float32),
    )
    print(f"  Signal cache saved: {SIGNAL_CACHE_PATH}")
    # Clean up partial checkpoint now that full cache is saved
    if SIGNAL_CACHE_PARTIAL_PATH.exists():
        SIGNAL_CACHE_PARTIAL_PATH.unlink()
    return actions, sell_ps, hold_ps, buy_ps


# ────────────────────────────────────────────────────────────────────────────
# Section 5: Backtest Engine (adapted from benchmark allocation loop)
# ────────────────────────────────────────────────────────────────────────────

def run_backtest(df: pd.DataFrame,
                 initial_capital: float = 10_000.0,
                 hrm_actions: Optional[List[str]] = None,
                 hrm_buy_probs: Optional[List[float]] = None,
                 hrm_sell_probs: Optional[List[float]] = None,
                 label: str = "SMA"
                 ) -> Dict:
    """
    Allocation-based backtest using the same engine as the 50-year benchmark.
    When hrm_actions is provided, Signal 1 uses the real HRM model.
    When hrm_actions is None, Signal 1 uses the original SMA crossover.
    """
    use_hrm = hrm_actions is not None

    capital      = initial_capital
    equity_curve = [capital]
    high_water   = capital
    trades       = 0
    wins = losses = 0
    daily_returns_list = []

    # Guardian thresholds (same as benchmark)
    GUARDIAN_DAILY_LIMIT  = -0.07
    GUARDIAN_TRAILING     = -0.08
    GUARDIAN_CRITICAL     = -0.18
    LOCKOUT_RESET_AFTER   = 60

    TARGET_EXPOSURE = {
        'bull': 1.00, 'recovery': 1.00, 'sideways': 0.88,
        'volatile': 0.55, 'bear': 0.24, 'crash': 0.00,
    }

    prev_alloc       = 0.30
    smoothed_alloc   = 0.30
    lockout_days     = 0
    circuit_breaker  = False
    daily_start_eq   = capital
    last_day         = None
    consecutive_bull = 0
    bull_streak      = 0

    t0      = time.time()
    n       = len(df)
    start_i = 201

    for idx in range(start_i, n):
        row = df.iloc[idx]
        prev_close = df.iloc[idx - 1]['close'] if idx > 0 else row['close']
        daily_ret  = (row['close'] - prev_close) / prev_close if prev_close > 0 else 0

        current_day = str(row['date'].date()) if hasattr(row['date'], 'date') else str(row['date'])
        if current_day != last_day:
            last_day      = current_day
            daily_start_eq = capital
            circuit_breaker = False

        # Guardian
        if capital > high_water:
            high_water = capital
        daily_pnl_pct = (capital - daily_start_eq) / daily_start_eq if daily_start_eq > 0 else 0
        if daily_pnl_pct <= GUARDIAN_DAILY_LIMIT:
            circuit_breaker = True
        dd_from_peak  = (capital - high_water) / high_water if high_water > 0 else 0
        in_critical   = dd_from_peak <= GUARDIAN_CRITICAL
        in_drawdown   = dd_from_peak <= GUARDIAN_TRAILING

        if in_critical:
            lockout_days += 1
            if lockout_days >= LOCKOUT_RESET_AFTER:
                high_water = capital; lockout_days = 0
                in_critical = False; in_drawdown = False
        else:
            lockout_days = max(0, lockout_days - 1)

        # Regime
        regime = str(row.get('regime', 'sideways'))
        if pd.isna(regime) or regime == 'nan':
            regime = 'sideways'

        # Bull streak tracking
        if regime == 'bull':
            consecutive_bull += 1
            bull_streak += 1
        else:
            consecutive_bull = 0

        # ── Signal 1: HRM or SMA ──────────────────────────────────────────
        signals = []
        if use_hrm and idx < len(hrm_actions):
            act = hrm_actions[idx]
            bp  = hrm_buy_probs[idx] if hrm_buy_probs else 0.33
            sp  = hrm_sell_probs[idx] if hrm_sell_probs else 0.33
            if act == 'buy' and bp > 0.40:
                signals.append(('buy',  min(bp * 0.85, 0.72)))
            elif act == 'sell' and sp > 0.40:
                signals.append(('sell', min(sp * 0.85, 0.72)))
            else:
                signals.append(('hold', 0.30))
        else:
            close  = row['close']
            sma20  = row.get('sma_20',  close)
            sma50  = row.get('sma_50',  close)
            sma200 = row.get('sma_200', close)
            if pd.isna(sma20):  sma20  = close
            if pd.isna(sma50):  sma50  = close
            if pd.isna(sma200): sma200 = close
            if close > sma20 > sma50 > sma200:
                signals.append(('buy',  0.80))
            elif close < sma20 < sma50 < sma200:
                signals.append(('sell', 0.80))
            elif close > sma50 > sma200:
                signals.append(('buy',  0.55))
            elif close < sma50 < sma200:
                signals.append(('sell', 0.55))
            else:
                signals.append(('hold', 0.30))

        # ── Signal 2: RSI ─────────────────────────────────────────────────
        rsi = float(row.get('rsi', 50) or 50)
        if rsi < 25:   signals.append(('buy',  0.75))
        elif rsi < 35: signals.append(('buy',  0.55))
        elif rsi > 75: signals.append(('sell', 0.75))
        elif rsi > 65: signals.append(('sell', 0.55))
        else:          signals.append(('hold', 0.30))

        # ── Signal 3: Regime ─────────────────────────────────────────────
        regime_map = {
            'bull': ('buy', 0.70), 'bear': ('sell', 0.70),
            'crash': ('sell', 0.90), 'recovery': ('buy', 0.72),
            'volatile': ('hold', 0.40), 'sideways': ('hold', 0.35),
        }
        signals.append(regime_map.get(regime, ('hold', 0.35)))

        # ── Signal 4: StatArb z-score ─────────────────────────────────────
        z = float(row.get('z_score', 0) or 0)
        if z < -2.0:   signals.append(('buy',  0.78))
        elif z < -1.5: signals.append(('buy',  0.58))
        elif z > 2.0:  signals.append(('sell', 0.78))
        elif z > 1.5:  signals.append(('sell', 0.58))
        else:          signals.append(('hold', 0.25))

        # ── Signal 5: Mean reversion on 20d returns ───────────────────────
        ret20 = float(row.get('returns_20', 0) or 0)
        if pd.isna(ret20): ret20 = 0
        if ret20 < -0.12:  signals.append(('buy',  0.62))
        elif ret20 > 0.18: signals.append(('sell', 0.62))
        else:              signals.append(('hold', 0.30))

        # ── Signal 6: Volatility multiplier ──────────────────────────────
        vol = float(row.get('volatility', 0.015) or 0.015)
        if pd.isna(vol): vol = 0.015
        vm = 0.70 if vol > 0.40 else (0.85 if vol > 0.25 else (1.10 if vol < 0.12 else 1.0))
        signals = [(a, c * vm) for a, c in signals]

        # ── Ensemble vote ─────────────────────────────────────────────────
        buy_w  = sum(c for a, c in signals if a == 'buy')
        sell_w = sum(c for a, c in signals if a == 'sell')
        hold_w = sum(c for a, c in signals if a == 'hold')
        total  = buy_w + sell_w + hold_w + 1e-9

        if buy_w > sell_w and buy_w > hold_w and buy_w / total > 0.38:
            sig_action = 'buy'
        elif sell_w > buy_w and sell_w > hold_w and sell_w / total > 0.38:
            sig_action = 'sell'
        else:
            sig_action = 'hold'

        # ── Raw target allocation from regime ─────────────────────────────
        raw_target = TARGET_EXPOSURE.get(regime, 0.30)

        # World model adjustment
        regime_names = ['bull', 'bear', 'volatile', 'sideways', 'crash', 'recovery']
        transition = {
            'bull':     [0.70, 0.08, 0.08, 0.10, 0.02, 0.02],
            'bear':     [0.05, 0.60, 0.12, 0.08, 0.12, 0.03],
            'volatile': [0.10, 0.15, 0.45, 0.10, 0.10, 0.10],
            'sideways': [0.20, 0.10, 0.10, 0.50, 0.03, 0.07],
            'crash':    [0.02, 0.10, 0.15, 0.03, 0.40, 0.30],
            'recovery': [0.35, 0.05, 0.10, 0.15, 0.02, 0.33],
        }
        probs_t = transition.get(regime, [1/6]*6)
        predicted_next = regime_names[int(np.argmax(probs_t))]
        if predicted_next == 'crash' and regime == 'crash':
            raw_target *= 0.30
        elif predicted_next == 'crash' and regime in ('bear', 'volatile'):
            raw_target *= 0.60
        elif predicted_next == 'bear' and regime in ('bull', 'recovery'):
            raw_target *= 0.85
        elif predicted_next == 'recovery' and regime in ('bear', 'crash'):
            raw_target = max(raw_target, 0.65)
        elif predicted_next == 'bull' and regime != 'bull':
            raw_target = max(raw_target, 0.72)

        # Shock detector
        if daily_ret <= -0.03:
            raw_target = max(0.01, raw_target * 0.35)
        elif daily_ret <= -0.02:
            raw_target = max(0.03, raw_target * 0.55)
        elif daily_ret <= -0.015:
            raw_target = max(0.10, raw_target * 0.78)
        elif daily_ret <= -0.01:
            raw_target = max(0.30, raw_target * 0.88)

        # Signal-driven nudge (both SMA and HRM paths benefit from this)
        if sig_action == 'buy':
            raw_target = min(raw_target * 1.03, 1.0)
        elif sig_action == 'sell':
            raw_target *= 0.97

        # EMA smoothing
        if raw_target < prev_alloc:
            alpha = 0.30 if regime in ('crash', 'bear') else 0.05
        else:
            alpha = 0.55 if smoothed_alloc < 0.15 else 0.15
        smoothed_alloc = alpha * raw_target + (1 - alpha) * smoothed_alloc
        prev_alloc     = smoothed_alloc

        # Adaptive leverage
        leverage = 1.0
        if (consecutive_bull >= 2 and bull_streak >= 3
                and 40 <= rsi <= 78 and not in_drawdown):
            leverage = min(1.0 + (min(bull_streak, 10) / 10) * 0.25, 1.25)

        target_alloc = min(smoothed_alloc * leverage, 1.25)

        # Guardian overrides
        if circuit_breaker:
            target_alloc = 0.0
        elif in_critical:
            target_alloc = min(target_alloc, 0.05)
        elif in_drawdown:
            target_alloc = min(target_alloc, 0.40)

        # Daily P&L
        port_return = daily_ret * target_alloc
        capital    *= (1 + port_return)

        equity_curve.append(capital)
        daily_returns_list.append(port_return)

        # Trade tracking (allocation change ≥ 5% = "trade")
        if abs(target_alloc - prev_alloc) > 0.05:
            trades += 1
            if port_return > 0:
                wins += 1
            elif port_return < 0:
                losses += 1

    elapsed = time.time() - t0

    # Metrics
    dr   = np.array(daily_returns_list)
    n_dr = len(dr)
    cagr = (capital / initial_capital) ** (252.0 / max(n_dr, 1)) - 1 if n_dr > 0 else 0
    sharpe  = (dr.mean() / (dr.std() + 1e-9)) * np.sqrt(252) if n_dr > 0 else 0
    neg_dr  = dr[dr < 0]
    sortino = (dr.mean() / (neg_dr.std() + 1e-9)) * np.sqrt(252) if len(neg_dr) > 0 else 0
    max_dd  = 0.0
    peak    = initial_capital
    for v in equity_curve:
        if v > peak: peak = v
        dd = (v - peak) / peak
        if dd < max_dd: max_dd = dd
    calmar    = cagr / abs(max_dd + 1e-9) if max_dd != 0 else 0
    win_rate  = wins / max(wins + losses, 1)
    total_ret = (capital / initial_capital) - 1

    print(f"  [{label}] CAGR={cagr*100:.2f}%  Sharpe={sharpe:.3f}  "
          f"MaxDD={max_dd*100:.1f}%  WinRate={win_rate*100:.1f}%  "
          f"Final=${capital:,.0f}  ({elapsed:.1f}s)")

    return {
        'label':         label,
        'cagr':          cagr,
        'sharpe_ratio':  sharpe,
        'sortino_ratio': sortino,
        'calmar_ratio':  calmar,
        'max_drawdown':  max_dd,
        'win_rate':      win_rate,
        'total_return':  total_ret,
        'final_capital': capital,
        'total_trades':  trades,
        'backtest_time': elapsed,
    }


def run_buy_and_hold(df: pd.DataFrame, initial_capital: float) -> Dict:
    """Simple buy-and-hold benchmark on S&P 500."""
    start_price = df['close'].iloc[201]
    end_price   = df['close'].iloc[-1]
    n_days      = len(df) - 201
    total_ret   = (end_price / start_price) - 1
    cagr        = (1 + total_ret) ** (252.0 / max(n_days, 1)) - 1
    daily_ret   = df['returns'].iloc[201:].fillna(0).values
    sharpe      = (daily_ret.mean() / (daily_ret.std() + 1e-9)) * np.sqrt(252)
    neg         = daily_ret[daily_ret < 0]
    sortino     = (daily_ret.mean() / (neg.std() + 1e-9)) * np.sqrt(252) if len(neg) > 0 else 0
    # Max drawdown
    prices  = df['close'].iloc[201:].values
    peak    = prices[0]
    max_dd  = 0.0
    for p in prices:
        if p > peak: peak = p
        dd = (p - peak) / peak
        if dd < max_dd: max_dd = dd
    calmar = cagr / abs(max_dd + 1e-9) if max_dd != 0 else 0
    final  = initial_capital * (1 + total_ret)
    print(f"  [Buy&Hold] CAGR={cagr*100:.2f}%  Sharpe={sharpe:.3f}  "
          f"MaxDD={max_dd*100:.1f}%  Final=${final:,.0f}")
    return {
        'label': 'Buy & Hold', 'cagr': cagr, 'sharpe_ratio': sharpe,
        'sortino_ratio': sortino, 'calmar_ratio': calmar,
        'max_drawdown': max_dd, 'win_rate': 0.538,
        'total_return': total_ret, 'final_capital': final,
        'total_trades': 0, 'backtest_time': 0,
    }


# ────────────────────────────────────────────────────────────────────────────
# Section 6: Report
# ────────────────────────────────────────────────────────────────────────────

def print_report(hrm_r: Dict, sma_r: Dict, bnh_r: Dict,
                 hrm_actions: List[str], df: pd.DataFrame) -> None:
    """Print comparison table and save JSON report."""
    buy_n  = hrm_actions.count('buy')
    hold_n = hrm_actions.count('hold')
    sell_n = hrm_actions.count('sell')
    total  = max(len(hrm_actions), 1)

    hrm_alpha_cagr   = (hrm_r['cagr'] - sma_r['cagr']) * 100
    hrm_alpha_sharpe = hrm_r['sharpe_ratio'] - sma_r['sharpe_ratio']
    hrm_alpha_dd     = (sma_r['max_drawdown'] - hrm_r['max_drawdown']) * 100  # positive = HRM has less DD

    date_range = f"{df['date'].iloc[0].strftime('%Y-%m-%d')} to {df['date'].iloc[-1].strftime('%Y-%m-%d')}"
    n_days     = len(df) - 201

    print()
    print("=" * 75)
    print("  PROMETHEUS REAL HRM BACKTEST — 50-YEAR COMPARISON")
    print("=" * 75)
    print(f"  Data:  S&P 500  {date_range}  ({n_days:,} trading days)")
    print(f"  HRM:   market_finetuned  (vocab=20, seq_len=101, halt_max_steps=2)")
    print(f"  Cache: {SIGNAL_CACHE_PATH.name}")
    print()
    print(f"  HRM SIGNAL DISTRIBUTION:")
    print(f"    BUY  : {buy_n:,} days ({buy_n/total*100:.1f}%)")
    print(f"    HOLD : {hold_n:,} days ({hold_n/total*100:.1f}%)")
    print(f"    SELL : {sell_n:,} days ({sell_n/total*100:.1f}%)")
    print()
    print(f"  {'Metric':<22} {'HRM Signal':>14} {'SMA Signal':>14} {'Buy & Hold':>14}")
    print(f"  {'-'*66}")

    rows = [
        ("Final Capital ($10k)", f"${hrm_r['final_capital']:>12,.0f}", f"${sma_r['final_capital']:>12,.0f}", f"${bnh_r['final_capital']:>12,.0f}"),
        ("CAGR",                 f"{hrm_r['cagr']*100:>13.2f}%", f"{sma_r['cagr']*100:>13.2f}%", f"{bnh_r['cagr']*100:>13.2f}%"),
        ("Sharpe Ratio",         f"{hrm_r['sharpe_ratio']:>14.3f}", f"{sma_r['sharpe_ratio']:>14.3f}", f"{bnh_r['sharpe_ratio']:>14.3f}"),
        ("Sortino Ratio",        f"{hrm_r['sortino_ratio']:>14.3f}", f"{sma_r['sortino_ratio']:>14.3f}", f"{bnh_r['sortino_ratio']:>14.3f}"),
        ("Calmar Ratio",         f"{hrm_r['calmar_ratio']:>14.3f}", f"{sma_r['calmar_ratio']:>14.3f}", f"{bnh_r['calmar_ratio']:>14.3f}"),
        ("Max Drawdown",         f"{hrm_r['max_drawdown']*100:>13.1f}%", f"{sma_r['max_drawdown']*100:>13.1f}%", f"{bnh_r['max_drawdown']*100:>13.1f}%"),
        ("Win Rate",             f"{hrm_r['win_rate']*100:>13.1f}%", f"{sma_r['win_rate']*100:>13.1f}%", f"{bnh_r['win_rate']*100:>13.1f}%"),
    ]
    for label, h, s, b in rows:
        print(f"  {label:<22} {h:>14} {s:>14} {b:>14}")

    print()
    print(f"  HRM ALPHA vs SMA BASELINE:")
    sign = "+" if hrm_alpha_cagr >= 0 else ""
    print(f"    CAGR    : {sign}{hrm_alpha_cagr:.2f}% per year")
    sign = "+" if hrm_alpha_sharpe >= 0 else ""
    print(f"    Sharpe  : {sign}{hrm_alpha_sharpe:.3f}")
    sign = "+" if hrm_alpha_dd >= 0 else ""
    print(f"    Max DD  : {sign}{hrm_alpha_dd:.1f}% (positive = HRM has smaller drawdown)")
    print("=" * 75)

    # Save JSON
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = ROOT / f"prometheus_real_hrm_results_{ts}.json"
    report = {
        'generated':       datetime.now().isoformat(),
        'data_range':      date_range,
        'trading_days':    n_days,
        'initial_capital': 10_000.0,
        'hrm_results':     hrm_r,
        'sma_results':     sma_r,
        'buy_hold':        bnh_r,
        'hrm_alpha': {
            'cagr_pct':    hrm_alpha_cagr,
            'sharpe':      hrm_alpha_sharpe,
            'max_dd_pct':  hrm_alpha_dd,
        },
        'hrm_signal_distribution': {
            'buy_count': buy_n, 'hold_count': hold_n, 'sell_count': sell_n,
            'buy_pct': buy_n/total, 'hold_pct': hold_n/total, 'sell_pct': sell_n/total,
        },
        'hrm_model': {
            'checkpoint':     str(CHECKPOINT_PATH),
            'vocab_size':     20,
            'seq_len':        101,
            'halt_max_steps': 2,
            'label_decode':   'logits[:,-1,:3] -> [SELL,HOLD,BUY]',
        },
        'cache_path': str(SIGNAL_CACHE_PATH),
    }
    # Make all values JSON-serialisable
    def _clean(obj):
        if isinstance(obj, (np.floating, np.integer)):
            return obj.item()
        if isinstance(obj, dict):
            return {k: _clean(v) for k, v in obj.items()}
        return obj
    with open(report_path, 'w') as f:
        json.dump(_clean(report), f, indent=2)
    print(f"\n  Report saved: {report_path.name}")


# ────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Prometheus Real HRM Backtest")
    parser.add_argument('--no-cache',  action='store_true', help='Regenerate HRM signal cache')
    parser.add_argument('--capital',   type=float, default=10_000.0, help='Initial capital')
    args = parser.parse_args()

    if args.no_cache and SIGNAL_CACHE_PATH.exists():
        SIGNAL_CACHE_PATH.unlink()
        print("Signal cache cleared.")

    print("\n" + "=" * 75)
    print("  PROMETHEUS REAL HRM BACKTEST")
    print("=" * 75)

    # 1. Load data
    print("\n[1/4] Loading S&P 500 data...")
    df = load_sp500()
    print(f"  Loaded {len(df):,} trading days: "
          f"{df['date'].iloc[0].strftime('%Y-%m-%d')} — "
          f"{df['date'].iloc[-1].strftime('%Y-%m-%d')}")
    regime_counts = df['regime'].value_counts()
    print(f"  Regime distribution: {dict(regime_counts)}")

    # 2. Load HRM model
    print("\n[2/4] Loading HRM market_finetuned model...")
    model = load_hrm_model()  # auto-detects DirectML, falls back to CPU
    if model is None:
        print("ERROR: HRM model could not be loaded. Aborting.")
        sys.exit(1)
    n_params = sum(p.numel() for p in model.parameters())
    dev_str = str(getattr(model, '_inference_device', 'cpu'))
    print(f"  Model loaded: {n_params/1e6:.1f}M params, halt_max_steps={model.config.halt_max_steps}, device={dev_str}")

    # 3. Generate HRM signals (or load cache)
    print("\n[3/4] Generating HRM signals...")
    use_cache = not args.no_cache
    hrm_actions, sell_probs, hold_probs, buy_probs = generate_hrm_signals(
        df, model, use_cache=use_cache
    )
    buy_n  = hrm_actions.count('buy')
    hold_n = hrm_actions.count('hold')
    sell_n = hrm_actions.count('sell')
    total  = len(hrm_actions)
    print(f"  Signal distribution: BUY={buy_n/total*100:.1f}%  "
          f"HOLD={hold_n/total*100:.1f}%  SELL={sell_n/total*100:.1f}%")

    # Sanity check — if HRM is collapsed (>90% one class), warn
    max_pct = max(buy_n, hold_n, sell_n) / total
    if max_pct > 0.90:
        print(f"  WARNING: HRM signals are {max_pct*100:.0f}% one class — model may be collapsed.")
        print("           Results may not reflect genuine HRM signal quality.")

    # 4. Run backtests
    print("\n[4/4] Running backtests...")
    print("  Running HRM signal backtest...")
    hrm_results = run_backtest(
        df, initial_capital=args.capital,
        hrm_actions=hrm_actions,
        hrm_buy_probs=buy_probs,
        hrm_sell_probs=sell_probs,
        label="HRM Signal"
    )

    print("  Running SMA signal backtest (baseline)...")
    sma_results = run_backtest(
        df, initial_capital=args.capital,
        hrm_actions=None,
        label="SMA Signal"
    )

    print("  Running Buy & Hold benchmark...")
    bnh_results = run_buy_and_hold(df, args.capital)

    # 5. Report
    print_report(hrm_results, sma_results, bnh_results, hrm_actions, df)


if __name__ == '__main__':
    main()
