import os
import sys
import asyncio
import argparse
import json
from datetime import datetime

sys.path.append(os.getcwd())

from core.hierarchical_reasoning import HierarchicalReasoningModel, Objective
from core.internal_paper_trading import paper_trading_engine

SYMBOLS = ["AAPL", "SPY", "MSFT", "NVDA", "AMZN", "TSLA"]
SESSIONS_DIR = os.path.join(os.getcwd(), "session_runs")

async def fetch_bars(symbol: str):
    """Fetch minute bars for today using yfinance via orchestrator provider.
    Returns dict with 'close' list. If unavailable, returns None.
    """
    try:
        # We'll use the same orchestrator fetch as market data update, but pull history via yfinance directly
        import yfinance as yf
        hist = yf.Ticker(symbol).history(period="1d", interval="1m")
        if hist is None or hist.empty:
            return None
        closes = [float(x) for x in hist['Close'].tolist()]
        return {"close": closes}
    except Exception:
        return None

async def resolve_position_size(portfolio, price: float, max_position_pct: float) -> float:
    # Size at half of max position pct for caution
    target_value = portfolio.intended_investment * (max_position_pct / 100.0) * 0.5
    if price <= 0:
        return 0.0
    qty = max(0.0, round(target_value / price, 2))
    return qty

async def ensure_portfolio(user_id: str, invest: float = 100000.0):
    if user_id not in paper_trading_engine.user_portfolios:
        await paper_trading_engine.create_user_portfolio(user_id, invest)
    return paper_trading_engine.user_portfolios[user_id]

async def run_once(dry_run: bool, execute: bool, session_dir: str):
    obj = Objective(name="baseline", target_return_daily_pct=1.0, max_drawdown_pct=3.0, max_position_pct=2.0)
    trace_path = os.path.join(session_dir, "hrm_traces.jsonl")
    hrm = HierarchicalReasoningModel(obj, trace_path=trace_path)

    plan = await hrm.reason_once(SYMBOLS, paper_trading_engine._is_market_open, fetch_bars)

    # Optionally execute small trades
    actions = []
    if execute and plan.market_open and not dry_run:
        user_id = "hrm_bot"
        portfolio = await ensure_portfolio(user_id)
        for d in plan.decisions:
            # Translate decision to quantity using simple sizing and current market ask/bid
            if d.action == 'hold':
                continue
            md = paper_trading_engine.market_data.get(d.symbol)
            price = None
            if md:
                price = md.ask if d.action == 'buy' else md.bid
            else:
                # Try updating once
                await paper_trading_engine._update_real_market_data(d.symbol)
                md = paper_trading_engine.market_data.get(d.symbol)
                if md:
                    price = md.ask if d.action == 'buy' else md.bid

            if not price or price <= 0:
                continue

            qty = await resolve_position_size(portfolio, price, obj.max_position_pct)
            if qty <= 0:
                continue

            try:
                res = await paper_trading_engine.place_paper_trade(user_id, d.symbol, d.action, qty, trade_type='market')
                actions.append({"symbol": d.symbol, "action": d.action, "qty": qty, "price": price, "ok": res.get("success", False)})
            except Exception as e:
                actions.append({"symbol": d.symbol, "action": d.action, "error": str(e)})

    # Persist a run record
    with open(os.path.join(session_dir, "hrm_runs.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "market_open": plan.market_open,
            "decisions": [d.__dict__ for d in plan.decisions],
            "executed": actions
        }) + "\n")

    print("HRM single run complete. market_open=", plan.market_open, "decisions=", len(plan.decisions), "executed=", len(actions))

async def run_loop(dry_run: bool, execute: bool, minutes: int, session_dir: str):
    await paper_trading_engine.start_market_data_feed()
    for _ in range(max(1, minutes)):
        await run_once(dry_run, execute, session_dir)
        await asyncio.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run one HRM iteration and exit")
    parser.add_argument("--execute", action="store_true", help="Place small paper trades when market is open")
    parser.add_argument("--minutes", type=int, default=30, help="How many minutes to run in loop mode")
    parser.add_argument("--dry-run", action="store_true", help="Do not place trades (log only)")
    args = parser.parse_args()

    # Prepare session dir (use latest session from run_paper_session if present; else make one)
    sessions_root = SESSIONS_DIR
    if not os.path.isdir(sessions_root):
        os.makedirs(sessions_root, exist_ok=True)
    existing = [d for d in os.listdir(sessions_root) if d.startswith("session_")]
    if existing:
        existing.sort()
        session_dir = os.path.join(sessions_root, existing[-1])
    else:
        sid = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join(sessions_root, f"session_{sid}")
        os.makedirs(session_dir, exist_ok=True)

    if args.once:
        asyncio.run(run_once(dry_run=args.dry_run, execute=args.execute, session_dir=session_dir))
    else:
        asyncio.run(run_loop(dry_run=args.dry_run, execute=args.execute, minutes=args.minutes, session_dir=session_dir))

