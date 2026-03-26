import os
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional

# Lightweight, pluggable hierarchical reasoning model for paper trading

@dataclass
class Objective:
    name: str
    target_return_daily_pct: float = 1.0
    max_drawdown_pct: float = 3.0
    max_position_pct: float = 2.0

@dataclass
class StrategyDecision:
    symbol: str
    strategy: str  # 'momentum' | 'mean_reversion'
    signal: float  # positive = buy bias, negative = sell bias
    confidence: float
    action: str  # 'hold' | 'buy' | 'sell'
    quantity: float

@dataclass
class HRMPlan:
    timestamp: str
    market_open: bool
    objectives: List[Objective]
    universe: List[str]
    decisions: List[StrategyDecision]
    notes: List[str]


class HierarchicalReasoningModel:
    def __init__(self, objective: Objective, trace_path: Optional[str] = None):
        self.objective = objective
        self.trace_path = trace_path or os.path.join(os.getcwd(), "reports", "hrm_traces.jsonl")
        os.makedirs(os.path.dirname(self.trace_path), exist_ok=True)

    async def reason_once(self, symbols: List[str], is_market_open_fn, fetch_bars_fn) -> HRMPlan:
        market_open = await is_market_open_fn()
        notes = []
        decisions: List[StrategyDecision] = []

        # Top-level: adhere to risk bounds
        max_pos_pct = self.objective.max_position_pct

        # Mid-level: choose strategy per symbol based on short vs long MA
        for sym in symbols:
            try:
                bars = await fetch_bars_fn(sym)
                if not bars or len(bars["close"]) < 20:
                    notes.append(f"{sym}: insufficient bars")
                    continue

                closes = bars["close"]
                # simple moving averages
                ma5 = sum(closes[-5:]) / 5
                ma20 = sum(closes[-20:]) / 20
                last = closes[-1]
                # signal strength on normalized scale
                signal = (ma5 - ma20) / ma20 if ma20 else 0.0

                # Strategy selection
                if abs(signal) > 0.003:  # 0.3% threshold
                    strategy = 'momentum'
                else:
                    strategy = 'mean_reversion'

                # Low-level: action decision
                if strategy == 'momentum':
                    action = 'buy' if signal > 0 else 'sell'
                    confidence = min(1.0, abs(signal) * 300)  # scale
                else:
                    # mean reversion: fade small moves
                    action = 'sell' if signal > 0 else 'buy'
                    confidence = min(0.6, 0.3 + abs(signal) * 200)

                qty = 0.0
                if market_open:
                    # Placeholder position sizing: 0.5% of portfolio at price ~ last
                    # Actual trade sizing will be resolved by the runner with real portfolio info
                    qty = 0.0  # runner will translate percentage to shares

                decisions.append(StrategyDecision(
                    symbol=sym,
                    strategy=strategy,
                    signal=signal,
                    confidence=confidence,
                    action=action,
                    quantity=qty
                ))
            except Exception as e:
                notes.append(f"{sym}: error {e}")

        plan = HRMPlan(
            timestamp=datetime.now().isoformat(),
            market_open=market_open,
            objectives=[self.objective],
            universe=symbols,
            decisions=decisions,
            notes=notes,
        )

        # Trace persist
        try:
            with open(self.trace_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    "timestamp": plan.timestamp,
                    "market_open": plan.market_open,
                    "objective": asdict(self.objective),
                    "universe": plan.universe,
                    "decisions": [asdict(d) for d in plan.decisions],
                    "notes": plan.notes,
                }) + "\n")
        except Exception:
            pass

        return plan

