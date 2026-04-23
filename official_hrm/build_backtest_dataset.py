"""
build_backtest_dataset.py — Generate HRM training data from Prometheus backtests.

Runs a fast historical backtest on multiple symbols over a configurable date range,
captures every individual trade (entry + exit + P&L), then encodes each as an HRM
token sequence using the same pipeline as trading_dataset.py.

This is the primary way to scale the HRM training set beyond the ~200 live/paper
trade examples.  A 2-year backtest on 20 symbols typically generates 1,000-3,000
labeled trade examples.

Usage (from official_hrm/ directory):
    python build_backtest_dataset.py

Options:
    --years      Years of history to backtest (default: 2)
    --symbols    Comma-separated tickers (default: curated 20-symbol list)
    --db         Path to prometheus_learning.db (default: ../prometheus_learning.db)
    --out        Output dataset directory (default: ../hrm_trading_dataset)
    --combine    If set, merge backtest trades with live DB trades (default: True)
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import yfinance as yf
import pandas as pd

# ── Path setup ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_ROOT))

from official_hrm.trading_dataset import (
    build_dataset,
    _load_backtest_trades,
    bars_to_tokens,
    _pnl_to_label,
    _write_split,
    VOCAB_SIZE, SEQ_LEN, N_BARS, LABEL_OFFSET,
    LABEL_SELL, LABEL_HOLD, LABEL_BUY,
)

# ── Default symbols — mix of equity, crypto, ETF ──────────────────────────────
DEFAULT_SYMBOLS = [
    "AAPL", "MSFT", "NVDA", "TSLA", "AMZN",
    "GOOGL", "META", "AMD", "SPY", "QQQ",
    "BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD",
    "JPM", "GS", "XOM", "BA", "NFLX", "CRM",
]

# ── Simple signal engine (mirrors Prometheus core logic) ─────────────────────

def _compute_signal(df_window: pd.DataFrame) -> tuple:
    """
    Compute a BUY/SELL/HOLD signal from the last N_BARS of price data.
    Uses RSI + momentum + volume surge — deterministic, no randomness.

    Returns (action: str, confidence: float)
    """
    if len(df_window) < 14:
        return "HOLD", 0.5

    close = df_window["Close"].values.astype(float)
    volume = df_window["Volume"].values.astype(float)

    # RSI-14
    deltas = np.diff(close)
    gain = np.where(deltas > 0, deltas, 0.0)
    loss = np.where(deltas < 0, -deltas, 0.0)
    avg_gain = gain[-14:].mean() if len(gain) >= 14 else gain.mean()
    avg_loss = loss[-14:].mean() if len(loss) >= 14 else loss.mean()
    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))

    # Short vs long momentum
    mom_short = (close[-1] - close[-5]) / (close[-5] + 1e-9) if len(close) >= 5 else 0.0
    mom_long = (close[-1] - close[-20]) / (close[-20] + 1e-9) if len(close) >= 20 else 0.0

    # Volume surge (last bar vs 10-bar avg)
    vol_surge = (volume[-1] / (volume[-10:].mean() + 1e-9)) if len(volume) >= 10 else 1.0

    score = 0.0

    # RSI signals
    if rsi < 30:
        score += 0.4  # oversold → buy
    elif rsi > 70:
        score -= 0.4  # overbought → sell
    elif rsi < 45:
        score += 0.15
    elif rsi > 55:
        score -= 0.15

    # Momentum
    score += np.clip(mom_short * 3, -0.3, 0.3)
    score += np.clip(mom_long * 1.5, -0.2, 0.2)

    # Volume confirms direction
    if vol_surge > 1.5:
        score *= 1.2

    if score > 0.25:
        return "BUY", min(0.9, 0.5 + abs(score))
    elif score < -0.25:
        return "SELL", min(0.9, 0.5 + abs(score))
    else:
        return "HOLD", 0.5


# ── Backtest engine ───────────────────────────────────────────────────────────

def run_backtest(
    symbols: list,
    years: float,
    stop_loss_pct: float = 0.05,
    take_profit_pct: float = 0.09,
    max_positions: int = 5,
    verbose: bool = True,
) -> list:
    """
    Run a simple vectorised backtest on daily bars.

    Returns list of raw trade dicts {symbol, action, price, date, pnl, entry_price}
    suitable for _load_backtest_trades().
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=int(years * 365) + 30)  # buffer

    if verbose:
        print(f"Fetching {years}yr daily data for {len(symbols)} symbols "
              f"({start_date.date()} to {end_date.date()})...")

    # Download all symbols
    all_data = {}
    for sym in symbols:
        try:
            df = yf.download(
                sym,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                interval="1d",
                progress=False,
                auto_adjust=True,
            )
            # Flatten MultiIndex columns
            if hasattr(df.columns, "levels"):
                df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            if len(df) > 30:
                all_data[sym] = df
        except Exception as e:
            if verbose:
                print(f"  Warning: could not fetch {sym}: {e}")

    if not all_data:
        raise RuntimeError("No data fetched — check internet connection or symbols")

    if verbose:
        print(f"  Got data for {len(all_data)}/{len(symbols)} symbols")

    # Get aligned dates
    all_dates = sorted(set.intersection(*[set(df.index) for df in all_data.values()]))
    if verbose:
        print(f"  {len(all_dates)} common trading days")

    positions = {}   # symbol → {entry_price, entry_date, quantity}
    trades = []      # collected trade records

    for i, date in enumerate(all_dates):
        if i < N_BARS:
            continue  # need lookback window

        # --- Manage open positions ---
        for sym in list(positions.keys()):
            if sym not in all_data or date not in all_data[sym].index:
                continue
            pos = positions[sym]
            current_price = float(all_data[sym].loc[date, "Close"])
            pnl_pct = (current_price - pos["entry_price"]) / pos["entry_price"]

            exit_reason = None
            if pnl_pct <= -stop_loss_pct:
                exit_reason = "stop_loss"
            elif pnl_pct >= take_profit_pct:
                exit_reason = "take_profit"
            else:
                # Re-evaluate signal
                window = all_data[sym].iloc[max(0, i - N_BARS):i + 1]
                action, _ = _compute_signal(window)
                if action == "SELL":
                    exit_reason = "signal_exit"

            if exit_reason:
                pnl_dollars = (current_price - pos["entry_price"]) * pos["quantity"]
                trades.append({
                    "symbol": sym,
                    "action": "SELL",
                    "price": current_price,
                    "date": date,
                    "pnl": pnl_dollars,
                    "entry_price": pos["entry_price"],
                    "exit_reason": exit_reason,
                })
                del positions[sym]

        # --- Look for new entries ---
        if len(positions) < max_positions:
            for sym, df in all_data.items():
                if sym in positions:
                    continue
                if date not in df.index:
                    continue
                window = df.iloc[max(0, i - N_BARS):i + 1]
                action, confidence = _compute_signal(window)
                if action == "BUY" and confidence >= 0.6:
                    entry_price = float(df.loc[date, "Close"])
                    quantity = 1000.0 / entry_price  # $1000 notional per trade
                    positions[sym] = {
                        "entry_price": entry_price,
                        "entry_date": date,
                        "quantity": quantity,
                    }
                    trades.append({
                        "symbol": sym,
                        "action": "BUY",
                        "price": entry_price,
                        "date": date,
                        "pnl": 0.0,
                        "entry_price": entry_price,
                    })

    # Close remaining positions at last date
    if all_dates:
        last_date = all_dates[-1]
        for sym, pos in positions.items():
            if sym in all_data and last_date in all_data[sym].index:
                final_price = float(all_data[sym].loc[last_date, "Close"])
                pnl_dollars = (final_price - pos["entry_price"]) * pos["quantity"]
                trades.append({
                    "symbol": sym,
                    "action": "SELL",
                    "price": final_price,
                    "date": last_date,
                    "pnl": pnl_dollars,
                    "entry_price": pos["entry_price"],
                    "exit_reason": "end_of_backtest",
                })

    if verbose:
        buy_count = sum(1 for t in trades if t["action"] == "BUY")
        sell_count = sum(1 for t in trades if t["action"] == "SELL")
        print(f"  Backtest complete: {buy_count} entries, {sell_count} exits")

    return trades


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Build HRM dataset from backtests")
    parser.add_argument("--years", type=float, default=2.0,
                        help="Years of history to backtest (default: 2)")
    parser.add_argument("--symbols", type=str, default=None,
                        help="Comma-separated tickers (default: built-in 20-symbol list)")
    parser.add_argument("--db", default=str(_ROOT / "prometheus_learning.db"),
                        help="Path to prometheus_learning.db")
    parser.add_argument("--out", default=str(_ROOT / "hrm_trading_dataset"),
                        help="Output dataset directory")
    parser.add_argument("--no-combine", action="store_true",
                        help="Use only backtest trades, skip DB trades")
    parser.add_argument("--test-fraction", type=float, default=0.2)
    args = parser.parse_args()

    symbols = args.symbols.split(",") if args.symbols else DEFAULT_SYMBOLS
    symbols = [s.strip() for s in symbols]

    print(f"\n{'='*60}")
    print(f"HRM Backtest Dataset Builder")
    print(f"  symbols : {len(symbols)}")
    print(f"  years   : {args.years}")
    print(f"  combine : {not args.no_combine}")
    print(f"  output  : {args.out}")
    print(f"{'='*60}\n")

    # Run backtest
    raw_trades = run_backtest(symbols, years=args.years, verbose=True)

    # Convert to standard trade format
    bt_trades = _load_backtest_trades(raw_trades)
    print(f"\nPaired {len(bt_trades)} complete BUY→SELL trades from backtest")

    if args.no_combine:
        # Backtest-only mode: write directly without DB
        _build_from_trades_only(bt_trades, args.out, args.test_fraction)
    else:
        # Combine with live DB trades
        build_dataset(
            db_path=args.db,
            output_dir=args.out,
            test_fraction=args.test_fraction,
            verbose=True,
            extra_backtest_trades=bt_trades,
        )

    print(f"\nDone. Next steps:")
    print(f"  1. cd official_hrm && python hrm_finetune.py")
    print(f"  2. python hrm_finetune_watcher.py")


def _build_from_trades_only(trades: list, output_dir: str, test_fraction: float):
    """Build dataset from trades only (no DB), for backtest-only mode."""
    from official_hrm.trading_dataset import (
        _fetch_bars, _pnl_to_label, _write_split, SEQ_LEN,
        LABEL_SELL, LABEL_HOLD, LABEL_BUY, VOCAB_SIZE
    )
    import numpy as np

    examples = []
    for i, t in enumerate(trades):
        context_tokens = _fetch_bars(t["symbol"], t["timestamp"])
        if context_tokens is None:
            continue
        label = _pnl_to_label(t["pnl_pct"], t["action"])
        seq = np.concatenate([context_tokens, np.array([label], dtype=np.int16)])
        examples.append((seq, label, t["symbol"]))
        if (i + 1) % 100 == 0:
            print(f"  encoded {i+1}/{len(trades)}, {len(examples)} usable")

    print(f"\nUsable examples: {len(examples)}")
    labels = [e[1] for e in examples]
    print(f"  SELL={labels.count(LABEL_SELL)} HOLD={labels.count(LABEL_HOLD)} BUY={labels.count(LABEL_BUY)}")

    rng = np.random.default_rng(42)
    idx = rng.permutation(len(examples))
    n_test = max(1, int(len(examples) * test_fraction))
    test_idx = idx[:n_test]
    train_idx = idx[n_test:]

    symbols = sorted(set(e[2] for e in examples))
    symbol_to_group = {s: i for i, s in enumerate(symbols)}

    for split_name, split_idx in [("train", train_idx), ("test", test_idx)]:
        _write_split(
            split_name=split_name,
            split_idx=split_idx,
            examples=examples,
            symbol_to_group=symbol_to_group,
            output_dir=output_dir,
            verbose=True,
        )

    print(f"\nDataset written to: {output_dir}")
    print(f"  train={len(train_idx)}  test={len(test_idx)}  vocab_size={VOCAB_SIZE}  seq_len={SEQ_LEN}")


if __name__ == "__main__":
    main()
