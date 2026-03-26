#!/usr/bin/env python3
"""
"🔄 PROMETHEUS Live Shadow Trade Comparison: Legacy vs Kelly vs 60/40 Blend
==========================================================================
Runs three position-sizing strategies on the same real-time market data
and compares signals, sizing, and simulated P&L side-by-side.

Usage:
    python shadow_trade_comparison.py                  # Default 20 symbols, 50 iterations
    python shadow_trade_comparison.py --iterations 100 # More iterations
    python shadow_trade_comparison.py --symbols AAPL MSFT NVDA  # Custom symbols
"""

import asyncio
import json
import logging
import math
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf

# Kelly Criterion integration
try:
    from advanced_risk_management import (
        AdvancedRiskManager,
        DrawdownProtection,
        KellyPositionSizer,
        VolatilityScaler,
    )
    KELLY_AVAILABLE = True
except ImportError:
    KELLY_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ── Symbol universe ──────────────────────────────────────────────────
DEFAULT_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "NVDA", "META", "AMZN",  # mega-cap tech
    "JPM", "GS", "BAC",                                  # financials
    "SPY", "QQQ", "XLF", "XLE",                          # ETFs
    "TSLA", "AMD", "INTC",                                # volatile tech
    "GLD", "SLV",                                         # metals
    "BTC-USD", "ETH-USD",                                 # crypto
]

# ── Data structures ──────────────────────────────────────────────────

@dataclass
class Signal:
    symbol: str
    timestamp: datetime
    action: str          # BUY / SELL / HOLD
    confidence: float
    score: float
    entry_price: float
    target_price: float
    stop_loss: float
    reasons: List[str] = field(default_factory=list)


@dataclass
class ShadowPosition:
    symbol: str
    action: str
    entry_price: float
    quantity: float
    dollars: float
    target_price: float
    stop_loss: float
    confidence: float
    entry_time: datetime
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl: float = 0.0
    pnl_pct: float = 0.0
    status: str = "open"
    exit_reason: str = ""


# ── Technical indicator helpers ──────────────────────────────────────

def compute_indicators(df: pd.DataFrame) -> Dict:
    """Compute technical indicators from OHLCV dataframe."""
    # Flatten multi-index columns from yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df = df.droplevel(1, axis=1)
    close = df["Close"].values.flatten()
    high = df["High"].values.flatten()
    low = df["Low"].values.flatten()
    volume = df["Volume"].values.flatten()
    n = len(close)
    if n < 30:
        return {}

    # Returns
    rets = np.diff(close) / close[:-1]
    ret_5 = (close[-1] / close[-6] - 1) if n >= 6 else 0
    ret_20 = (close[-1] / close[-21] - 1) if n >= 21 else 0

    # Volatility (20-day)
    vol_20 = float(np.std(rets[-20:])) if len(rets) >= 20 else float(np.std(rets))

    # Simple RSI-14
    gains = np.where(rets > 0, rets, 0)
    losses = np.where(rets < 0, -rets, 0)
    avg_gain = float(np.mean(gains[-14:])) if len(gains) >= 14 else 0.01
    avg_loss = float(np.mean(losses[-14:])) if len(losses) >= 14 else 0.01
    rs = avg_gain / max(avg_loss, 1e-9)
    rsi = 100 - 100 / (1 + rs)

    # MACD (12/26/9)
    close_s = pd.Series(close)
    ema12 = float(close_s.ewm(span=12).mean().iloc[-1])
    ema26 = float(close_s.ewm(span=26).mean().iloc[-1])
    macd_line = ema12 - ema26

    # Volume ratio
    avg_vol = float(np.mean(volume[-20:])) if n >= 20 else float(np.mean(volume))
    vol_ratio = float(volume[-1]) / max(avg_vol, 1) if avg_vol > 0 else 1.0

    # Drawdown from 60-day peak
    peak_60 = float(np.max(close[-60:])) if n >= 60 else float(np.max(close))
    dd_60 = (close[-1] - peak_60) / peak_60

    # Trend strength: slope of 20-day linear regression
    if n >= 20:
        x = np.arange(20)
        y = close[-20:]
        slope = float(np.polyfit(x, y, 1)[0])
        trend_strength = slope / close[-1]  # normalize
    else:
        trend_strength = 0.0

    # Simulated VIX from 20-day vol (annualized)
    sim_vix = vol_20 * math.sqrt(252) * 100

    return {
        "price": float(close[-1]),
        "ret_5": ret_5,
        "ret_20": ret_20,
        "vol_20": vol_20,
        "rsi": rsi,
        "macd_line": float(macd_line),
        "volume_ratio": vol_ratio,
        "dd_60": dd_60,
        "trend_strength": trend_strength,
        "sim_vix": sim_vix,
        "avg_gain": avg_gain,
        "avg_loss": avg_loss,
    }


# ── Signal generation (mirrors PROMETHEUS logic) ─────────────────────

def generate_signal(symbol: str, indicators: Dict) -> Optional[Signal]:
    """Generate a trading signal from technical indicators."""
    if not indicators:
        return None

    price = indicators["price"]
    rsi = indicators["rsi"]
    macd = indicators["macd_line"]
    vol_ratio = indicators["volume_ratio"]
    ret_5 = indicators["ret_5"]
    trend = indicators["trend_strength"]
    dd_60 = indicators["dd_60"]

    # Score components (−1 to +1 each)
    scores = []

    # RSI reversal
    if rsi < 30:
        scores.append(("RSI oversold", 0.7))
    elif rsi < 40:
        scores.append(("RSI low", 0.3))
    elif rsi > 70:
        scores.append(("RSI overbought", -0.7))
    elif rsi > 60:
        scores.append(("RSI high", -0.3))
    else:
        scores.append(("RSI neutral", 0.0))

    # MACD
    if macd > 0:
        scores.append(("MACD bullish", min(macd / price * 1000, 0.5)))
    else:
        scores.append(("MACD bearish", max(macd / price * 1000, -0.5)))

    # Momentum
    if ret_5 > 0.02:
        scores.append(("Strong momentum", 0.4))
    elif ret_5 > 0:
        scores.append(("Mild momentum", 0.2))
    elif ret_5 < -0.02:
        scores.append(("Negative momentum", -0.4))
    else:
        scores.append(("Flat momentum", -0.1))

    # Volume confirmation
    if vol_ratio > 1.5:
        scores.append(("High volume", 0.3))
    elif vol_ratio < 0.5:
        scores.append(("Low volume", -0.2))
    else:
        scores.append(("Normal volume", 0.0))

    # Trend
    if trend > 0.001:
        scores.append(("Uptrend", 0.4))
    elif trend < -0.001:
        scores.append(("Downtrend", -0.4))
    else:
        scores.append(("No trend", 0.0))

    # Drawdown recovery
    if dd_60 < -0.10:
        scores.append(("Deep drawdown recovery potential", 0.3))

    total_score = sum(s for _, s in scores)
    num = len(scores)
    avg_score = total_score / num if num else 0

    # Map score to action
    if avg_score >= 0.15:
        action = "BUY"
        confidence = min(0.5 + avg_score, 0.95)
        target = price * (1 + 0.03 + avg_score * 0.02)
        stop = price * (1 - 0.02)
    elif avg_score <= -0.15:
        action = "SELL"
        confidence = min(0.5 + abs(avg_score), 0.95)
        target = price * (1 - 0.03 - abs(avg_score) * 0.02)
        stop = price * (1 + 0.02)
    else:
        action = "HOLD"
        confidence = 0.3
        target = price
        stop = price

    return Signal(
        symbol=symbol,
        timestamp=datetime.now(),
        action=action,
        confidence=confidence,
        score=avg_score,
        entry_price=price,
        target_price=target,
        stop_loss=stop,
        reasons=[r for r, _ in scores if _ != 0],
    )


# ── Position sizing ─────────────────────────────────────────────────

def legacy_position_size(capital: float, price: float, max_pct: float = 0.10) -> Tuple[float, float]:
    """Legacy fixed-percentage position sizing. Returns (dollars, quantity)."""
    dollars = capital * max_pct
    qty = dollars / price if price > 0 else 0
    return dollars, qty


def kelly_position_size(
    capital: float,
    price: float,
    indicators: Dict,
    confidence: float,
    dd_current: float,
) -> Tuple[float, float, Dict]:
    """Kelly Criterion position sizing. Returns (dollars, quantity, info)."""
    if not KELLY_AVAILABLE:
        d, q = legacy_position_size(capital, price)
        return d, q, {"method": "fallback_legacy"}

    kelly = KellyPositionSizer(fractional_kelly=0.25)
    vol_scaler = VolatilityScaler()
    dd_protect = DrawdownProtection(warning_level=0.10, emergency_level=0.13, max_drawdown=0.15)

    win_rate = 0.50 + indicators.get("avg_gain", 0.01) * 5  # proxy
    win_rate = max(0.40, min(0.75, win_rate))
    avg_win = max(indicators.get("avg_gain", 0.01), 0.005)
    avg_loss = max(indicators.get("avg_loss", 0.01), 0.005)

    kelly_dollars, kelly_info = kelly.calculate_position_size(
        win_rate=win_rate,
        avg_win=avg_win,
        avg_loss=avg_loss,
        confidence=confidence,
        capital=capital,
    )

    # VIX scaling
    sim_vix = indicators.get("sim_vix", 20)
    vol_mult, vol_regime = vol_scaler.get_volatility_multiplier(sim_vix)
    kelly_dollars *= vol_mult

    # Drawdown protection
    dd_mult, dd_status = dd_protect.get_drawdown_multiplier(abs(dd_current))
    kelly_dollars *= dd_mult

    # Clamp to 15% of capital
    kelly_dollars = min(kelly_dollars, capital * 0.15)
    qty = kelly_dollars / price if price > 0 else 0

    info = {
        "method": "kelly",
        "raw_fraction": kelly_info.get("raw_kelly", 0),
        "final_fraction": kelly_info.get("final_fraction", 0),
        "vol_regime": vol_regime,
        "vol_mult": vol_mult,
        "dd_status": dd_status,
        "dd_mult": dd_mult,
        "win_rate_est": win_rate,
    }
    return kelly_dollars, qty, info


def blend_position_size(
    capital: float,
    price: float,
    indicators: Dict,
    confidence: float,
    dd_current: float,
) -> Tuple[float, float, Dict]:
    """60/40 Legacy-Kelly blend (benchmark-recommended). Returns (dollars, qty, info)."""
    leg_dollars, leg_qty = legacy_position_size(capital, price)
    if KELLY_AVAILABLE:
        k_dollars, k_qty, k_info = kelly_position_size(
            capital, price, indicators, confidence, dd_current
        )
    else:
        k_dollars, k_qty, k_info = leg_dollars, leg_qty, {"method": "fallback_legacy"}

    blend_dollars = 0.6 * leg_dollars + 0.4 * k_dollars
    blend_dollars = min(blend_dollars, capital * 0.15)
    blend_qty = blend_dollars / price if price > 0 else 0
    info = {
        "method": "blend_60_40",
        "legacy_dollars": round(leg_dollars, 2),
        "kelly_dollars": round(k_dollars, 2),
        "blend_dollars": round(blend_dollars, 2),
    }
    return blend_dollars, blend_qty, info


# ── Shadow Trading Engine ────────────────────────────────────────────

class ShadowEngine:
    """Runs a shadow portfolio with a given sizing method."""

    def __init__(self, name: str, capital: float, sizing: str = "legacy"):
        self.name = name
        self.sizing = sizing  # "legacy", "kelly", or "blend"
        self.starting_capital = capital
        self.capital = capital
        self.peak_capital = capital
        self.open_positions: Dict[str, ShadowPosition] = {}
        self.closed: List[ShadowPosition] = []
        self.trade_count = 0
        self.max_open = 8

    @property
    def current_drawdown(self) -> float:
        if self.peak_capital <= 0:
            return 0
        return (self.capital - self.peak_capital) / self.peak_capital

    def process_signal(self, signal: Signal, indicators: Dict):
        """Process a signal: open or close positions."""
        if signal.action == "HOLD":
            return

        symbol = signal.symbol

        # Close existing position on opposing signal
        if symbol in self.open_positions:
            pos = self.open_positions[symbol]
            if (pos.action == "BUY" and signal.action == "SELL") or \
               (pos.action == "SELL" and signal.action == "BUY"):
                self._close_position(symbol, signal.entry_price, "opposing_signal")
            return

        # Open new position
        if len(self.open_positions) >= self.max_open:
            return

        if signal.confidence < 0.55:
            return

        price = signal.entry_price
        if self.sizing == "kelly":
            dollars, qty, info = kelly_position_size(
                self.capital, price, indicators, signal.confidence, self.current_drawdown
            )
        elif self.sizing == "blend":
            dollars, qty, info = blend_position_size(
                self.capital, price, indicators, signal.confidence, self.current_drawdown
            )
        else:
            dollars, qty = legacy_position_size(self.capital, price)
            info = {"method": "legacy"}

        if dollars <= 0 or qty <= 0:
            return

        pos = ShadowPosition(
            symbol=symbol,
            action=signal.action,
            entry_price=price,
            quantity=qty,
            dollars=dollars,
            target_price=signal.target_price,
            stop_loss=signal.stop_loss,
            confidence=signal.confidence,
            entry_time=signal.timestamp,
        )
        self.open_positions[symbol] = pos
        self.trade_count += 1

    def update_prices(self, prices: Dict[str, float]):
        """Update open positions with current prices, close on stop/target."""
        to_close = []
        for sym, pos in self.open_positions.items():
            if sym not in prices:
                continue
            px = prices[sym]
            if pos.action == "BUY":
                if px >= pos.target_price:
                    to_close.append((sym, px, "target_hit"))
                elif px <= pos.stop_loss:
                    to_close.append((sym, px, "stop_loss"))
            elif pos.action == "SELL":
                if px <= pos.target_price:
                    to_close.append((sym, px, "target_hit"))
                elif px >= pos.stop_loss:
                    to_close.append((sym, px, "stop_loss"))

        for sym, px, reason in to_close:
            self._close_position(sym, px, reason)

    def _close_position(self, symbol: str, exit_price: float, reason: str):
        if symbol not in self.open_positions:
            return
        pos = self.open_positions.pop(symbol)
        pos.exit_price = exit_price
        pos.exit_time = datetime.now()
        pos.exit_reason = reason
        if pos.action == "BUY":
            pos.pnl = (exit_price - pos.entry_price) * pos.quantity
            pos.pnl_pct = (exit_price / pos.entry_price - 1) * 100
        else:
            pos.pnl = (pos.entry_price - exit_price) * pos.quantity
            pos.pnl_pct = (pos.entry_price / exit_price - 1) * 100
        pos.status = "closed"
        self.capital += pos.pnl
        self.peak_capital = max(self.peak_capital, self.capital)
        self.closed.append(pos)

    def close_all(self, prices: Dict[str, float]):
        """Force-close all open positions at current prices."""
        for sym in list(self.open_positions.keys()):
            px = prices.get(sym, self.open_positions[sym].entry_price)
            self._close_position(sym, px, "session_end")

    def summary(self) -> Dict:
        wins = [t for t in self.closed if t.pnl > 0]
        losses = [t for t in self.closed if t.pnl <= 0]
        total_pnl = sum(t.pnl for t in self.closed)
        win_rate = len(wins) / len(self.closed) * 100 if self.closed else 0
        avg_win = np.mean([t.pnl_pct for t in wins]) if wins else 0
        avg_loss = np.mean([t.pnl_pct for t in losses]) if losses else 0
        max_dd = min((t.pnl_pct for t in self.closed), default=0)

        return {
            "name": self.name,
            "sizing": self.sizing,
            "starting_capital": self.starting_capital,
            "final_capital": round(self.capital, 2),
            "total_pnl": round(total_pnl, 2),
            "return_pct": round((self.capital / self.starting_capital - 1) * 100, 2),
            "total_trades": len(self.closed),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(win_rate, 1),
            "avg_win_pct": round(float(avg_win), 2),
            "avg_loss_pct": round(float(avg_loss), 2),
            "worst_trade_pct": round(float(max_dd), 2),
            "open_positions": len(self.open_positions),
        }


# ── Main comparison runner ────────────────────────────────────────────

def fetch_data(symbols: List[str], period: str = "6mo") -> Dict[str, pd.DataFrame]:
    """Download historical data for all symbols."""
    data = {}
    for sym in symbols:
        try:
            df = yf.download(sym, period=period, progress=False)
            if df is not None and len(df) >= 30:
                data[sym] = df
        except Exception:
            pass
    return data


def run_comparison(
    symbols: List[str],
    capital: float = 100_000,
    iterations: int = 50,
) -> Dict:
    """Run the full shadow trade comparison."""

    print("\n" + "=" * 80)
    print("🔄 PROMETHEUS LIVE SHADOW TRADE COMPARISON")
    print("   Legacy (Fixed 10%) vs Kelly Criterion vs 60/40 Blend")
    print("=" * 80)

    if not KELLY_AVAILABLE:
        print("⚠️  Kelly module not found – running Legacy-only comparison")

    # Fetch data
    print(f"\n📥 Fetching 6-month data for {len(symbols)} symbols …")
    all_data = fetch_data(symbols)
    loaded = list(all_data.keys())
    print(f"   ✅ Loaded {len(loaded)} symbols: {', '.join(loaded)}")

    if not loaded:
        print("❌ No data available. Exiting.")
        return {}

    # Create three engines
    legacy = ShadowEngine("Legacy (Fixed 10%)", capital, sizing="legacy")
    kelly_eng = ShadowEngine("Kelly Criterion", capital, sizing="kelly")
    blend_eng = ShadowEngine("Blend (60/40)", capital, sizing="blend")

    # Simulate trading across the last `iterations` days
    min_len = min(len(df) for df in all_data.values())
    actual_iters = min(iterations, min_len - 30)  # need 30 days for indicators
    start_idx = min_len - actual_iters

    print(f"\n🚀 Running {actual_iters} trading days …\n")
    signal_log: List[Dict] = []

    for day_offset in range(actual_iters):
        idx = start_idx + day_offset
        prices_today = {}

        for sym, df in all_data.items():
            if idx >= len(df):
                continue
            window = df.iloc[: idx + 1]
            indicators = compute_indicators(window)
            if not indicators:
                continue

            prices_today[sym] = indicators["price"]

            # Generate signal (same for both engines)
            sig = generate_signal(sym, indicators)
            if sig is None:
                continue

            # All three engines see the same signal
            legacy.process_signal(sig, indicators)
            kelly_eng.process_signal(sig, indicators)
            blend_eng.process_signal(sig, indicators)

            if sig.action != "HOLD":
                signal_log.append({
                    "day": day_offset + 1,
                    "symbol": sym,
                    "action": sig.action,
                    "price": round(sig.entry_price, 2),
                    "confidence": round(sig.confidence, 3),
                    "score": round(sig.score, 3),
                })

        # Update all engines with current prices
        legacy.update_prices(prices_today)
        kelly_eng.update_prices(prices_today)
        blend_eng.update_prices(prices_today)

        # Progress
        if (day_offset + 1) % 10 == 0 or day_offset == actual_iters - 1:
            l_s = legacy.summary()
            k_s = kelly_eng.summary()
            b_s = blend_eng.summary()
            print(
                f"  Day {day_offset + 1:>3}/{actual_iters}  |  "
                f"Legacy: ${l_s['total_pnl']:>+10,.2f}  |  "
                f"Kelly: ${k_s['total_pnl']:>+10,.2f}  |  "
                f"Blend: ${b_s['total_pnl']:>+10,.2f}"
            )

    # Close remaining positions at last known prices
    last_prices = {}
    for sym, df in all_data.items():
        if len(df) > 0:
            col = df["Close"]
            if isinstance(col, pd.DataFrame):
                col = col.iloc[:, 0]
            last_prices[sym] = float(col.iloc[-1])
    legacy.close_all(last_prices)
    kelly_eng.close_all(last_prices)
    blend_eng.close_all(last_prices)

    # ── Results ──────────────────────────────────────────────────────
    l = legacy.summary()
    k = kelly_eng.summary()
    b = blend_eng.summary()

    print("\n" + "=" * 80)
    print("📊 SHADOW TRADE COMPARISON RESULTS (3-WAY)")
    print("=" * 80)

    header = f"{'Metric':<22} {'Legacy':<16} {'Kelly':<16} {'Blend 60/40':<16} {'Winner':<14}"
    print(header)
    print("-" * 84)

    def pick_winner_3(lv, kv, bv, higher_better=True):
        vals = {"LEGACY": lv, "KELLY": kv, "BLEND": bv}
        if higher_better:
            best = max(vals, key=vals.get)
        else:
            best = min(vals, key=vals.get)
        # Check for ties with the best
        best_val = vals[best]
        tied = [k for k, v in vals.items() if abs(v - best_val) < 0.01]
        if len(tied) == 3:
            return "TIE"
        if len(tied) == 2:
            return f"{'/'.join(tied)}"
        return f"{best} ✓"

    metrics = [
        ("Return %", l["return_pct"], k["return_pct"], b["return_pct"], True),
        ("Total P&L ($)", l["total_pnl"], k["total_pnl"], b["total_pnl"], True),
        ("Win Rate %", l["win_rate"], k["win_rate"], b["win_rate"], True),
        ("Total Trades", l["total_trades"], k["total_trades"], b["total_trades"], None),
        ("Avg Win %", l["avg_win_pct"], k["avg_win_pct"], b["avg_win_pct"], True),
        ("Avg Loss %", l["avg_loss_pct"], k["avg_loss_pct"], b["avg_loss_pct"], False),
        ("Worst Trade %", l["worst_trade_pct"], k["worst_trade_pct"], b["worst_trade_pct"], False),
    ]

    win_counts = {"LEGACY": 0, "KELLY": 0, "BLEND": 0}

    for name, lv, kv, bv, higher in metrics:
        if higher is None:
            winner = ""
        else:
            winner = pick_winner_3(lv, kv, bv, higher)
            for label in ["LEGACY", "KELLY", "BLEND"]:
                if label in winner and "✓" in winner:
                    win_counts[label] += 1

        if isinstance(lv, float) and abs(lv) > 100:
            print(f"  {name:<20} ${lv:>+12,.2f}  ${kv:>+12,.2f}  ${bv:>+12,.2f}  {winner}")
        else:
            print(f"  {name:<20} {lv:>12}  {kv:>12}  {bv:>12}  {winner}")

    print("-" * 84)
    best_label = max(win_counts, key=win_counts.get)
    best_count = win_counts[best_label]
    counts_str = f"Legacy {win_counts['LEGACY']}, Kelly {win_counts['KELLY']}, Blend {win_counts['BLEND']}"
    if list(win_counts.values()).count(best_count) > 1:
        overall = f"TIE ({counts_str})"
    else:
        overall = f"{best_label} WINS ({counts_str})"
    print(f"  OVERALL: {overall}\n")

    # ── Save report ──────────────────────────────────────────────────
    report = {
        "timestamp": datetime.now().isoformat(),
        "symbols": loaded,
        "trading_days": actual_iters,
        "starting_capital": capital,
        "kelly_available": KELLY_AVAILABLE,
        "legacy": l,
        "kelly": k,
        "blend": b,
        "overall_winner": overall,
        "win_counts": win_counts,
        "signal_count": len(signal_log),
    }

    out_path = f"shadow_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"📁 Full report saved: {out_path}")
    print("=" * 80)

    return report


# ── CLI ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    symbols = DEFAULT_SYMBOLS
    iters = 50

    args = sys.argv[1:]
    if "--symbols" in args:
        idx = args.index("--symbols") + 1
        symbols = []
        while idx < len(args) and not args[idx].startswith("--"):
            symbols.append(args[idx].upper())
            idx += 1
    if "--iterations" in args:
        idx = args.index("--iterations") + 1
        if idx < len(args):
            iters = int(args[idx])

    run_comparison(symbols=symbols, iterations=iters)
