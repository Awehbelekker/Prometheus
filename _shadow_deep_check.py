"""Deep dive into shadow trading and learning database stats."""
import sqlite3, json
from pathlib import Path

DB = Path("prometheus_learning.db")
conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row

W = 70

def hdr(title):
    print("\n" + "="*W)
    print(f"  {title}")
    print("="*W)

def safe(val, fmt=None):
    if val is None:
        return "n/a"
    try:
        return fmt % float(val) if fmt else str(val)
    except:
        return str(val)

# ── Shadow Sessions ───────────────────────────────────────────────────────────
# Columns: id, session_id, config_name, starting_capital, current_capital,
#          max_position_pct, started_at, last_active, status, config_json,
#          total_trades, winning_trades, total_pnl, win_rate
hdr("SHADOW TRADING SESSIONS")
try:
    r = conn.execute("""
        SELECT COUNT(*) as cnt,
               MIN(started_at) as first,
               MAX(started_at) as last,
               MAX(last_active) as latest_active,
               COALESCE(SUM(total_trades),0) as trades,
               COALESCE(SUM(winning_trades),0) as winning,
               COALESCE(AVG(CASE WHEN win_rate IS NOT NULL THEN win_rate END),0) as avg_wr,
               COALESCE(SUM(total_pnl),0) as total_pnl,
               COALESCE(SUM(starting_capital),0) as sum_start,
               COALESCE(SUM(current_capital),0) as sum_curr
        FROM shadow_sessions""").fetchone()
    print(f"  Total sessions      : {r['cnt']}")
    print(f"  First started       : {r['first']}")
    print(f"  Last started        : {r['last']}")
    print(f"  Last active         : {r['latest_active']}")
    print(f"  Total trades        : {r['trades']}")
    print(f"  Winning trades      : {r['winning']}")
    total = r['trades'] or 1
    print(f"  Win rate (overall)  : {r['winning']/total*100:.1f}%")
    print(f"  Avg session win%    : {float(r['avg_wr'])*100:.1f}%")
    print(f"  Cumulative PnL      : ${float(r['total_pnl']):+.4f}")
    sc = float(r['sum_start']) or 1
    cc = float(r['sum_curr'])
    print(f"  Capital: start=${sc:.2f}  current=${cc:.2f}  change={((cc-sc)/sc*100):+.2f}%")
except Exception as e:
    print(f"  [error: {e}]")

print("\n  Status breakdown:")
try:
    rows = conn.execute("""
        SELECT status, COUNT(*) as n, COALESCE(AVG(win_rate),0) as wr,
               COALESCE(SUM(total_pnl),0) as pnl
        FROM shadow_sessions GROUP BY status ORDER BY n DESC""").fetchall()
    for r in rows:
        print(f"    {r['status']:<15}: {r['n']:>4} sessions  avg_wr={float(r['wr'])*100:.1f}%  pnl=${float(r['pnl']):+.4f}")
except Exception as e:
    print(f"  [error: {e}]")

print("\n  Recent 10 sessions:")
try:
    rows = conn.execute("""
        SELECT started_at, config_name, total_trades, winning_trades,
               win_rate, total_pnl, status, starting_capital, current_capital
        FROM shadow_sessions ORDER BY started_at DESC LIMIT 10""").fetchall()
    h = f"  {'Started':<19}  {'Config':<25}  {'T':>4}  {'W':>4}  {'WR%':>5}  {'PnL':>9}  {'Cap Chg':>8}  Status"
    print(h)
    print("  " + "-"*(len(h)-2))
    for r in rows:
        wr  = f"{float(r['win_rate'])*100:.0f}%" if r['win_rate'] is not None else " n/a"
        pnl = f"${float(r['total_pnl']):+.3f}" if r['total_pnl'] is not None else "    n/a"
        sc  = float(r['starting_capital'] or 0)
        cc  = float(r['current_capital'] or 0)
        chg = f"{(cc-sc)/sc*100:+.1f}%" if sc else "   n/a"
        cfg = str(r['config_name'] or '')[:25]
        print(f"  {str(r['started_at'])[:19]:<19}  {cfg:<25}  {r['total_trades'] or 0:>4}  {r['winning_trades'] or 0:>4}  {wr:>5}  {pnl:>9}  {chg:>8}  {r['status'] or ''}")
except Exception as e:
    print(f"  [error: {e}]")

# ── Shadow Trade History ──────────────────────────────────────────────────────
# Columns: id, session_id, trade_id, timestamp, symbol, action, quantity,
#          entry_price, target_price, stop_loss, confidence, reason,
#          ai_components, asset_class, exit_price, exit_time, pnl, pnl_pct,
#          status, exit_reason, market_conditions, live_comparison
hdr("SHADOW TRADE HISTORY")
try:
    r = conn.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN action='BUY' THEN 1 ELSE 0 END) as buys,
               SUM(CASE WHEN action='SELL' THEN 1 ELSE 0 END) as sells,
               SUM(CASE WHEN status='closed' THEN 1 ELSE 0 END) as closed,
               SUM(CASE WHEN pnl>0 THEN 1 ELSE 0 END) as winners,
               COALESCE(SUM(pnl),0) as total_pnl,
               COALESCE(AVG(pnl),0) as avg_pnl,
               COALESCE(MAX(pnl),0) as best,
               COALESCE(MIN(pnl),0) as worst,
               COALESCE(AVG(confidence),0) as avg_conf
        FROM shadow_trade_history""").fetchone()
    print(f"  Total trades        : {r['total']}")
    print(f"  BUY / SELL          : {r['buys']} / {r['sells']}")
    print(f"  Closed trades       : {r['closed']}")
    w = r['winners'] or 0
    c = r['closed'] or 1
    print(f"  Winners             : {w} ({w/c*100:.0f}% of closed)")
    print(f"  Total PnL           : ${float(r['total_pnl']):+.4f}")
    print(f"  Avg PnL/trade       : ${float(r['avg_pnl']):+.4f}")
    print(f"  Best  trade         : ${float(r['best']):+.4f}")
    print(f"  Worst trade         : ${float(r['worst']):+.4f}")
    print(f"  Avg confidence      : {float(r['avg_conf']):.3f}")
except Exception as e:
    print(f"  [error: {e}]")

print("\n  Last 15 trades:")
try:
    rows = conn.execute("""
        SELECT timestamp, symbol, action, quantity, entry_price,
               exit_price, pnl, pnl_pct, confidence, status, exit_reason
        FROM shadow_trade_history ORDER BY timestamp DESC LIMIT 15""").fetchall()
    print(f"  {'Time':<19}  {'Sym':<8}  {'Act':<4}  {'Qty':>8}  {'Entry':>8}  {'Exit':>8}  {'PnL':>9}  {'PnL%':>7}  {'Conf':>5}  Status")
    print("  " + "-"*105)
    for r in rows:
        pnl = f"${float(r['pnl']):+.3f}" if r['pnl'] is not None else "  open"
        pct = f"{float(r['pnl_pct']):+.2f}%" if r['pnl_pct'] is not None else "    n/a"
        ex  = f"${float(r['exit_price']):.2f}" if r['exit_price'] else "   open"
        print(f"  {str(r['timestamp'])[:19]:<19}  {r['symbol']:<8}  {r['action']:<4}  {r['quantity']:>8}  ${float(r['entry_price']):>7.2f}  {ex:>8}  {pnl:>9}  {pct:>7}  {float(r['confidence'] or 0):>5.2f}  {r['status'] or ''}")
except Exception as e:
    print(f"  [error: {e}]")

# ── Shadow Position Tracking ──────────────────────────────────────────────────
# Columns: id, session_id, symbol, position_high, entry_time, scaled_level,
#          dca_count, updated_at
hdr("SHADOW POSITION TRACKING")
try:
    r = conn.execute("SELECT COUNT(*) as n FROM shadow_position_tracking").fetchone()
    print(f"  Total position records: {r['n']}")
    rows = conn.execute("""
        SELECT symbol, position_high, entry_time, scaled_level, dca_count, updated_at
        FROM shadow_position_tracking ORDER BY updated_at DESC LIMIT 15""").fetchall()
    print(f"\n  {'Symbol':<10}  {'PositionHigh':>12}  {'EntryTime':<19}  {'Scale':>5}  {'DCA':>3}  Updated")
    print("  " + "-"*78)
    for r in rows:
        print(f"  {r['symbol']:<10}  ${float(r['position_high'] or 0):>11.4f}  {str(r['entry_time'] or '')[:19]:<19}  {r['scaled_level'] or 0:>5}  {r['dca_count'] or 0:>3}  {str(r['updated_at'] or '')[:19]}")
except Exception as e:
    print(f"  [error: {e}]")

# ── Learning Outcomes ─────────────────────────────────────────────────────────
# Columns: id, timestamp, symbol, predicted_action, predicted_confidence,
#          entry_price, exit_price, profit_loss, profit_pct, was_correct,
#          ai_components, learning_notes
hdr("AI LEARNING OUTCOMES (106 total)")
try:
    r = conn.execute("""
        SELECT COUNT(*) as cnt,
               SUM(CASE WHEN was_correct=1 THEN 1 ELSE 0 END) as correct,
               COALESCE(SUM(profit_loss),0) as total_pnl,
               COALESCE(AVG(profit_loss),0) as avg_pnl,
               COALESCE(MAX(profit_loss),0) as best,
               COALESCE(MIN(profit_loss),0) as worst,
               COALESCE(AVG(predicted_confidence),0) as avg_conf
        FROM learning_outcomes""").fetchone()
    correct = int(r['correct'] or 0)
    total   = int(r['cnt'] or 1)
    print(f"  Total outcomes      : {total}")
    print(f"  Correct predictions : {correct}/{total} ({correct/total*100:.1f}%)")
    print(f"  Total PnL           : ${float(r['total_pnl']):+.4f}")
    print(f"  Avg PnL/trade       : ${float(r['avg_pnl']):+.4f}")
    print(f"  Best trade          : ${float(r['best']):+.4f}")
    print(f"  Worst trade         : ${float(r['worst']):+.4f}")
    print(f"  Avg confidence      : {float(r['avg_conf']):.3f}")
except Exception as e:
    print(f"  [error: {e}]")

print("\n  Breakdown by predicted action:")
try:
    rows = conn.execute("""
        SELECT predicted_action,
               COUNT(*) as n,
               SUM(CASE WHEN was_correct=1 THEN 1 ELSE 0 END) as correct,
               AVG(profit_loss) as avg_pnl, SUM(profit_loss) as sum_pnl
        FROM learning_outcomes GROUP BY predicted_action""").fetchall()
    for r in rows:
        n = int(r['n'])
        c = int(r['correct'] or 0)
        print(f"    {r['predicted_action']:<5}: {n:>3} outcomes  acc={c/n*100:.0f}%  avg_pnl=${float(r['avg_pnl'] or 0):+.4f}  sum=${float(r['sum_pnl'] or 0):+.4f}")
except Exception as e:
    print(f"  [error: {e}]")

print("\n  Top 5 symbols by trade count:")
try:
    rows = conn.execute("""
        SELECT symbol, COUNT(*) as n,
               SUM(CASE WHEN was_correct=1 THEN 1 ELSE 0 END) as correct,
               AVG(profit_loss) as avg_pnl
        FROM learning_outcomes GROUP BY symbol ORDER BY n DESC LIMIT 10""").fetchall()
    for r in rows:
        n = int(r['n'])
        c = int(r['correct'] or 0)
        print(f"    {r['symbol']:<10}: {n:>3} trades  acc={c/n*100:.0f}%  avg_pnl=${float(r['avg_pnl'] or 0):+.4f}")
except Exception as e:
    print(f"  [error: {e}]")

# ── Signal Predictions ────────────────────────────────────────────────────────
# Columns: id, timestamp, symbol, action, confidence, entry_price, target_price,
#          stop_loss, ai_components, vote_breakdown, reasoning, market_data,
#          outcome_recorded
hdr("SIGNAL PREDICTIONS (161,299 total)")
try:
    r = conn.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN action='BUY' THEN 1 ELSE 0 END) as buys,
               SUM(CASE WHEN action='SELL' THEN 1 ELSE 0 END) as sells,
               SUM(CASE WHEN action='HOLD' THEN 1 ELSE 0 END) as holds,
               SUM(CASE WHEN outcome_recorded=1 THEN 1 ELSE 0 END) as recorded,
               AVG(confidence) as avg_conf,
               MIN(timestamp) as first_ts,
               MAX(timestamp) as last_ts
        FROM signal_predictions""").fetchone()
    total = int(r['total'])
    print(f"  Total predictions   : {total:,}")
    print(f"  BUY signals         : {int(r['buys'] or 0):,}  ({int(r['buys'] or 0)/total*100:.1f}%)")
    print(f"  SELL signals        : {int(r['sells'] or 0):,}  ({int(r['sells'] or 0)/total*100:.1f}%)")
    print(f"  HOLD signals        : {int(r['holds'] or 0):,}  ({int(r['holds'] or 0)/total*100:.1f}%)")
    print(f"  Outcomes recorded   : {int(r['recorded'] or 0):,}  ({int(r['recorded'] or 0)/total*100:.2f}%)")
    print(f"  Avg confidence      : {float(r['avg_conf']):.3f}")
    print(f"  Date range          : {r['first_ts']} → {r['last_ts']}")
except Exception as e:
    print(f"  [error: {e}]")

print("\n  Top 10 symbols by signal count:")
try:
    rows = conn.execute("""
        SELECT symbol, COUNT(*) as n,
               AVG(confidence) as avg_conf,
               SUM(CASE WHEN action='BUY' THEN 1 ELSE 0 END) as b,
               SUM(CASE WHEN action='SELL' THEN 1 ELSE 0 END) as s,
               SUM(CASE WHEN action='HOLD' THEN 1 ELSE 0 END) as h
        FROM signal_predictions GROUP BY symbol ORDER BY n DESC LIMIT 10""").fetchall()
    print(f"  {'Symbol':<12}  {'Count':>7}  {'Conf':>5}  {'Buy%':>6}  {'Sel%':>6}  {'Hld%':>6}")
    for r in rows:
        n = int(r['n'])
        print(f"  {r['symbol']:<12}  {n:>7,}  {float(r['avg_conf']):.3f}  {int(r['b'] or 0)/n*100:>5.1f}%  {int(r['s'] or 0)/n*100:>5.1f}%  {int(r['h'] or 0)/n*100:>5.1f}%")
except Exception as e:
    print(f"  [error: {e}]")

# ── AI Attribution ────────────────────────────────────────────────────────────
# Columns: id, attribution_id, timestamp, symbol, ai_system, action,
#          confidence, vote_weight, entry_price, eventual_pnl, pnl_pct,
#          outcome_recorded, trade_id
hdr("AI ATTRIBUTION LEADERBOARD (198,470 rows)")
try:
    rows = conn.execute("""
        SELECT ai_system,
               COUNT(*) as votes,
               AVG(confidence) as avg_conf,
               AVG(vote_weight) as avg_weight,
               SUM(CASE WHEN eventual_pnl IS NOT NULL THEN 1 ELSE 0 END) as with_outcome,
               AVG(CASE WHEN eventual_pnl IS NOT NULL THEN eventual_pnl END) as avg_pnl,
               SUM(CASE WHEN eventual_pnl > 0 THEN 1 ELSE 0 END) as wins
        FROM ai_attribution
        GROUP BY ai_system
        ORDER BY votes DESC LIMIT 15""").fetchall()
    print(f"  {'AI System':<35}  {'Votes':>7}  {'Conf':>5}  {'Wt':>5}  {'W/OutcomeP':>10}  {'AvgPnL':>8}  {'WinRate':>7}")
    print("  " + "-"*100)
    for r in rows:
        wout = int(r['with_outcome'] or 0)
        wins = int(r['wins'] or 0)
        wr   = f"{wins/wout*100:.0f}%" if wout else "  n/a"
        apnl = f"${float(r['avg_pnl']):+.4f}" if r['avg_pnl'] is not None else "     n/a"
        print(f"  {r['ai_system']:<35}  {int(r['votes']):>7,}  {float(r['avg_conf']):.3f}  {float(r['avg_weight'] or 0):.3f}  {wout:>10,}  {apnl:>8}  {wr:>7}")
except Exception as e:
    print(f"  [error: {e}]")

# ── Multi-Strategy Leaderboard ────────────────────────────────────────────────
# Columns: id, run_id, completed_at, strategy_name, rank, final_capital,
#          total_return_pct, total_trades, win_rate, sharpe_ratio,
#          max_drawdown, avg_trade_pnl, config_json, promoted_to_live
hdr("MULTI-STRATEGY LEADERBOARD (24 rows)")
try:
    rows = conn.execute("""
        SELECT strategy_name, rank, final_capital, total_return_pct,
               total_trades, win_rate, sharpe_ratio, max_drawdown,
               avg_trade_pnl, promoted_to_live, completed_at
        FROM multi_strategy_leaderboard ORDER BY rank ASC LIMIT 15""").fetchall()
    print(f"  {'#':>3}  {'Strategy':<30}  {'FinalCap':>10}  {'Ret%':>7}  {'Trades':>6}  {'WR%':>5}  {'Sharpe':>6}  {'DD%':>6}  {'Promoted'}")
    print("  " + "-"*100)
    for r in rows:
        fc  = f"${float(r['final_capital']):,.0f}" if r['final_capital'] else "    n/a"
        ret = f"{float(r['total_return_pct']):+.1f}%" if r['total_return_pct'] else " n/a"
        wr  = f"{float(r['win_rate'])*100:.0f}%" if r['win_rate'] else " n/a"
        sh  = f"{float(r['sharpe_ratio']):.2f}" if r['sharpe_ratio'] else " n/a"
        dd  = f"{float(r['max_drawdown'])*100:.1f}%" if r['max_drawdown'] else " n/a"
        prm = "YES" if r['promoted_to_live'] else " no"
        print(f"  {r['rank'] or 0:>3}  {str(r['strategy_name'] or '')[:30]:<30}  {fc:>10}  {ret:>7}  {r['total_trades'] or 0:>6}  {wr:>5}  {sh:>6}  {dd:>6}  {prm}")
except Exception as e:
    print(f"  [error: {e}]")

# ── Open Positions ────────────────────────────────────────────────────────────
# Columns: id, symbol, side, quantity, entry_price, current_price,
#          unrealized_pl, broker, opened_at, updated_at
hdr("CURRENT LIVE OPEN POSITIONS (5 rows)")
try:
    rows = conn.execute("""
        SELECT symbol, side, quantity, entry_price, current_price,
               unrealized_pl, broker, opened_at
        FROM open_positions ORDER BY unrealized_pl DESC""").fetchall()
    if not rows:
        print("  (no open positions)")
    else:
        print(f"  {'Symbol':<10}  {'Side':<5}  {'Qty':>10}  {'Entry':>10}  {'Current':>10}  {'Unreal PnL':>12}  Broker")
        for r in rows:
            pl = float(r['unrealized_pl'] or 0)
            print(f"  {r['symbol']:<10}  {r['side'] or 'LONG':<5}  {r['quantity']:>10}  ${float(r['entry_price']):.4f}  ${float(r['current_price'] or 0):.4f}  ${pl:>+11.4f}  {r['broker'] or ''}")
except Exception as e:
    print(f"  [error: {e}]")

# ── Performance Metrics ───────────────────────────────────────────────────────
hdr("PERFORMANCE METRICS (latest 5)")
try:
    rows = conn.execute("""
        SELECT timestamp, total_trades, winning_trades, losing_trades,
               total_profit_loss, win_rate, average_profit, average_loss,
               sharpe_ratio, max_drawdown, current_balance
        FROM performance_metrics ORDER BY timestamp DESC LIMIT 5""").fetchall()
    for r in rows:
        print(f"\n  [{r['timestamp']}]")
        print(f"    Trades  : {r['total_trades']}  (W:{r['winning_trades']} / L:{r['losing_trades']})  WR:{float(r['win_rate'] or 0)*100:.1f}%")
        print(f"    Total PnL: ${float(r['total_profit_loss'] or 0):+.4f}  avg_win=${float(r['average_profit'] or 0):+.4f}  avg_loss=${float(r['average_loss'] or 0):+.4f}")
        print(f"    Sharpe   : {safe(r['sharpe_ratio'],'%.3f')}  MaxDD: {safe(r['max_drawdown'],'%.4f')}  Balance: ${float(r['current_balance'] or 0):.2f}")
except Exception as e:
    print(f"  [error: {e}]")

# ── Trade Optimization ────────────────────────────────────────────────────────
hdr("TRADE OPTIMIZATION ANALYSIS (16 rows)")
try:
    r = conn.execute("""
        SELECT COUNT(*) as n,
               AVG(actual_profit_pct) as avg_actual,
               AVG(optimal_profit_pct) as avg_optimal,
               AVG(missed_opportunity_pct) as avg_missed,
               AVG(hold_duration_hours) as avg_hold,
               SUM(CASE WHEN exit_timing='too_early' THEN 1 ELSE 0 END) as early,
               SUM(CASE WHEN exit_timing='too_late' THEN 1 ELSE 0 END) as late,
               SUM(CASE WHEN exit_timing='optimal' THEN 1 ELSE 0 END) as optimal
        FROM trade_optimization""").fetchone()
    print(f"  Analyzed trades       : {r['n']}")
    print(f"  Avg actual return     : {float(r['avg_actual'] or 0):+.2f}%")
    print(f"  Avg optimal return    : {float(r['avg_optimal'] or 0):+.2f}%")
    print(f"  Avg missed opportunity: {float(r['avg_missed'] or 0):+.2f}%")
    print(f"  Avg hold duration     : {float(r['avg_hold'] or 0):.1f} hours")
    print(f"  Exit timing — too early: {r['early']}  too late: {r['late']}  optimal: {r['optimal']}")
except Exception as e:
    print(f"  [error: {e}]")

conn.close()
print("\n" + "="*W + "\n")

