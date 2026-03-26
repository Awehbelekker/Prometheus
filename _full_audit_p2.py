"""
PROMETHEUS FULL AUDIT — PART 2
Deep dive into every system with correct schemas
"""
import os, sys, json, sqlite3, re, socket
from pathlib import Path
from datetime import datetime
from collections import Counter

BASE = Path(r"C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform")
os.chdir(BASE)

def section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")

def sub(title):
    print(f"\n  --- {title} ---")

# ============================================================================
# SIGNAL PREDICTIONS DEEP DIVE
# ============================================================================
section("SIGNAL PREDICTIONS DEEP DIVE")

conn = sqlite3.connect('prometheus_learning.db', timeout=10)
cur = conn.cursor()

# Signal predictions by action
cur.execute("SELECT action, COUNT(*) FROM signal_predictions GROUP BY action ORDER BY COUNT(*) DESC")
print("  By action:")
for action, cnt in cur.fetchall():
    print(f"    {action}: {cnt:,}")

# Signal confidence distribution
cur.execute("SELECT ROUND(confidence, 1) as conf_bucket, COUNT(*) FROM signal_predictions GROUP BY conf_bucket ORDER BY conf_bucket")
print("\n  Confidence distribution:")
for bucket, cnt in cur.fetchall():
    bar = '#' * min(int(cnt/2000), 40)
    print(f"    {bucket:.1f}: {cnt:>6,} {bar}")

# Signals per month
cur.execute("""SELECT strftime('%Y-%m', timestamp) as month, COUNT(*) 
               FROM signal_predictions GROUP BY month ORDER BY month""")
print("\n  Signals per month:")
for month, cnt in cur.fetchall():
    print(f"    {month}: {cnt:,}")

# Top symbols by signals
cur.execute("SELECT symbol, COUNT(*) FROM signal_predictions GROUP BY symbol ORDER BY COUNT(*) DESC LIMIT 20")
print("\n  Top symbols by signal count:")
for sym, cnt in cur.fetchall():
    print(f"    {sym}: {cnt:,}")

# OUTCOME analysis — what percent of signals got outcome recorded?
cur.execute("SELECT COUNT(*) FROM signal_predictions WHERE outcome_recorded = 1")
recorded = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM signal_predictions")
total_sig = cur.fetchone()[0]
print(f"\n  Outcome recorded: {recorded:,} / {total_sig:,} ({recorded/total_sig*100:.1f}%)")

# ============================================================================
# AI ATTRIBUTION — WHO'S MAKING THE CALLS
# ============================================================================
section("AI ATTRIBUTION — SYSTEM PERFORMANCE")

cur.execute("""SELECT ai_system, COUNT(*) as total,
               SUM(CASE WHEN eventual_pnl > 0 THEN 1 ELSE 0 END) as wins,
               SUM(CASE WHEN eventual_pnl <= 0 AND outcome_recorded = 1 THEN 1 ELSE 0 END) as losses,
               COALESCE(AVG(CASE WHEN outcome_recorded = 1 THEN eventual_pnl END), 0) as avg_pnl,
               COALESCE(SUM(CASE WHEN outcome_recorded = 1 THEN eventual_pnl END), 0) as total_pnl,
               AVG(confidence) as avg_conf,
               SUM(CASE WHEN outcome_recorded = 1 THEN 1 ELSE 0 END) as outcomes
               FROM ai_attribution 
               GROUP BY ai_system ORDER BY total DESC""")

print(f"  {'System':<25} {'Signals':>8} {'Outcomes':>8} {'Wins':>6} {'WinRate':>8} {'AvgPnL':>10} {'TotalPnL':>12} {'AvgConf':>8}")
print(f"  {'-'*95}")
for row in cur.fetchall():
    sys_name, total, wins, losses, avg_pnl, total_pnl, avg_conf, outcomes = row
    wr = round(wins/(wins+losses)*100,1) if (wins+losses) > 0 else 0
    print(f"  {sys_name or 'NULL':<25} {total:>8,} {outcomes:>8,} {wins or 0:>6,} {wr:>7.1f}% ${avg_pnl:>9.4f} ${total_pnl:>11.2f} {avg_conf:>7.3f}")

# AI system metrics
sub("AI System Performance Metrics (ai_system_metrics)")
cur.execute("SELECT * FROM ai_system_metrics ORDER BY date DESC, ai_system")
rows = cur.fetchall()
if rows:
    print(f"  {'Date':<12} {'System':<25} {'Signals':>8} {'Exec':>6} {'Wins':>5} {'Loss':>5} {'WinRate':>8} {'PnL':>10} {'Sharpe':>8}")
    print(f"  {'-'*95}")
    for row in rows[:30]:
        _id, date, sys_name, total_sig, executed, wins, losses, pnl, wr, avg_pnl, sharpe = row
        print(f"  {date:<12} {sys_name:<25} {total_sig:>8,} {executed:>6,} {wins:>5} {losses:>5} {wr:>7.1f}% ${pnl:>9.2f} {sharpe:>7.3f}")

# ============================================================================
# GUARDIAN / RISK MANAGEMENT
# ============================================================================
section("GUARDIAN RISK MANAGEMENT")

sub("Guardian Blocks (last 20)")
cur.execute("""SELECT timestamp, symbol, proposed_action, block_reason, protection_layer 
               FROM guardian_blocks ORDER BY id DESC LIMIT 20""")
for row in cur.fetchall():
    ts, sym, action, reason, layer = row
    print(f"  {ts[:19]} {sym:<12} {action:<6} {layer:<20} {reason[:60]}")

sub("Guardian Adjustments (last 20)")
cur.execute("""SELECT timestamp, symbol, original_size, adjusted_size, adjustment_reason 
               FROM guardian_adjustments ORDER BY id DESC LIMIT 20""")
for row in cur.fetchall():
    ts, sym, orig, adj, reason = row
    print(f"  {ts[:19]} {sym:<12} ${orig:.2f} -> ${adj:.2f}  {reason[:50]}")

sub("Guardian State (latest)")
cur.execute("""SELECT timestamp, high_water_mark, current_equity, daily_pnl, weekly_pnl, 
               monthly_pnl, drawdown_pct, circuit_breaker_active, regime 
               FROM guardian_state ORDER BY id DESC LIMIT 5""")
for row in cur.fetchall():
    ts, hwm, eq, dpnl, wpnl, mpnl, dd, cb, regime = row
    print(f"  {ts[:19]} equity=${eq:.2f} HWM=${hwm:.2f} DD={dd:.2f}% CB={cb} regime={regime}")

# ============================================================================
# SHADOW TRADING DEEP DIVE
# ============================================================================
section("SHADOW TRADING DEEP DIVE")

sub("Shadow Sessions")
cur.execute("""SELECT session_id, config_name, starting_capital, current_capital, 
               total_trades, winning_trades, total_pnl, win_rate, status, started_at, last_active
               FROM shadow_sessions ORDER BY last_active DESC LIMIT 15""")
for row in cur.fetchall():
    sid, cfg, start_cap, cur_cap, trades, wins, pnl, wr, status, started, active = row
    ret = ((cur_cap or 0) - (start_cap or 0)) / (start_cap or 1) * 100
    print(f"  {cfg or 'unknown':<30} cap=${cur_cap or 0:.2f} trades={trades or 0} wr={wr or 0:.1f}% pnl=${pnl or 0:.2f} ret={ret:+.2f}% [{status}]")
    print(f"    started={started} active={active}")

sub("Shadow Trade History (last 20)")
cur.execute("""SELECT timestamp, symbol, action, entry_price, exit_price, pnl, pnl_pct, 
               confidence, status, exit_reason
               FROM shadow_trade_history ORDER BY id DESC LIMIT 20""")
for row in cur.fetchall():
    ts, sym, action, ep, xp, pnl, pnl_pct, conf, status, reason = row
    pnl_str = f"${pnl:.2f}" if pnl else "open"
    print(f"  {ts[:19]} {sym:<12} {action:<5} entry=${ep or 0:.2f} exit=${xp or 0:.2f} {pnl_str:>8} conf={conf or 0:.2f} [{status}] {reason or ''}")

# ============================================================================
# LEARNING OUTCOMES
# ============================================================================
section("LEARNING OUTCOMES")

cur.execute("""SELECT symbol, predicted_action, predicted_confidence, entry_price, exit_price,
               profit_loss, profit_pct, was_correct, timestamp
               FROM learning_outcomes ORDER BY id DESC LIMIT 30""")
rows = cur.fetchall()
print(f"  Total learning outcomes: {len(rows)} (showing last 30)")
if rows:
    print(f"  {'Time':<20} {'Symbol':<10} {'Action':<5} {'Conf':>6} {'Entry':>10} {'Exit':>10} {'P/L':>8} {'Correct':>8}")
    print(f"  {'-'*85}")
    for row in rows:
        sym, action, conf, ep, xp, pnl, pct, correct, ts = row
        print(f"  {(ts or '')[:19]:<20} {sym or '':<10} {action or '':<5} {conf or 0:>5.2f} ${ep or 0:>9.2f} ${xp or 0:>9.2f} ${pnl or 0:>7.2f} {'YES' if correct else 'NO':>8}")

# Learning stats
cur.execute("SELECT COUNT(*), SUM(CASE WHEN was_correct=1 THEN 1 ELSE 0 END) FROM learning_outcomes")
total, correct = cur.fetchone()
if total:
    print(f"\n  Learning accuracy: {correct}/{total} = {correct/total*100:.1f}%")

# ============================================================================
# MODEL RETRAIN LOG
# ============================================================================
section("MODEL RETRAINING HISTORY")

cur.execute("""SELECT timestamp, symbol, model_type, success, old_metric, new_metric, samples, duration_s
               FROM model_retrain_log ORDER BY id DESC LIMIT 20""")
rows = cur.fetchall()
print(f"  Recent retrains:")
for row in rows:
    ts, sym, model, ok, old_m, new_m, samples, dur = row
    improved = "IMPROVED" if (new_m or 0) > (old_m or 0) else "WORSE" if new_m is not None else "n/a"
    print(f"  {(ts or '')[:19]} {sym or '':<10} {model or '':<20} {improved:<10} old={old_m or 0:.4f} new={new_m or 0:.4f} samples={samples} {dur or 0:.1f}s")

# ============================================================================
# MULTI-STRATEGY LEADERBOARD
# ============================================================================
section("MULTI-STRATEGY LEADERBOARD")

cur.execute("""SELECT strategy_name, rank, total_return_pct, total_trades, win_rate, 
               sharpe_ratio, max_drawdown, promoted_to_live, completed_at
               FROM multi_strategy_leaderboard ORDER BY rank ASC""")
rows = cur.fetchall()
if rows:
    print(f"  {'Strategy':<30} {'Rank':>4} {'Return%':>8} {'Trades':>7} {'WinRate':>8} {'Sharpe':>7} {'MaxDD':>7} {'Live':>5}")
    print(f"  {'-'*85}")
    for row in rows:
        name, rank, ret, trades, wr, sharpe, dd, live, completed = row
        print(f"  {name or '':<30} {rank:>4} {ret or 0:>7.1f}% {trades or 0:>7} {wr or 0:>7.1f}% {sharpe or 0:>6.2f} {dd or 0:>6.2f}% {'YES' if live else 'no':>5}")

# ============================================================================
# PERFORMANCE METRICS TIMELINE
# ============================================================================
section("PERFORMANCE METRICS TIMELINE")

cur.execute("""SELECT strftime('%Y-%m-%d', timestamp) as day, 
               MAX(total_trades) as trades, MAX(winning_trades) as wins,
               MAX(total_profit_loss) as pnl, MAX(win_rate) as wr, 
               MAX(sharpe_ratio) as sharpe, MAX(max_drawdown) as dd,
               MAX(current_balance) as bal
               FROM performance_metrics 
               GROUP BY day ORDER BY day DESC LIMIT 30""")
rows = cur.fetchall()
if rows:
    print(f"  {'Date':<12} {'Trades':>7} {'Wins':>6} {'WinRate':>8} {'P/L':>10} {'Sharpe':>8} {'MaxDD':>8} {'Balance':>12}")
    print(f"  {'-'*75}")
    for row in rows:
        day, trades, wins, pnl, wr, sharpe, dd, bal = row
        print(f"  {day:<12} {trades or 0:>7} {wins or 0:>6} {wr or 0:>7.1f}% ${pnl or 0:>9.2f} {sharpe or 0:>7.3f} {dd or 0:>7.2f}% ${bal or 0:>11.2f}")

# ============================================================================
# TRADE OPTIMIZATION
# ============================================================================
section("TRADE OPTIMIZATION — MISSED OPPORTUNITIES")

cur.execute("""SELECT symbol, entry_price, actual_exit_price, actual_profit_pct,
               optimal_exit_price, optimal_profit_pct, missed_opportunity_pct, exit_timing
               FROM trade_optimization ORDER BY id DESC""")
rows = cur.fetchall()
if rows:
    avg_missed = sum(r[6] or 0 for r in rows) / len(rows)
    print(f"  Total optimized trades: {len(rows)}")
    print(f"  Avg missed opportunity: {avg_missed:.2f}%")
    print(f"\n  {'Symbol':<10} {'ActualPnL':>10} {'OptimalPnL':>10} {'Missed':>8} {'Timing':<15}")
    print(f"  {'-'*55}")
    for row in rows:
        sym, ep, actual_xp, actual_pct, opt_xp, opt_pct, missed, timing = row
        print(f"  {sym or '':<10} {actual_pct or 0:>9.2f}% {opt_pct or 0:>9.2f}% {missed or 0:>7.2f}% {timing or '':<15}")

# ============================================================================
# WORLD MODEL STATE
# ============================================================================
section("WORLD MODEL STATE")

cur.execute("SELECT timestamp, cycle_count FROM world_model_state ORDER BY id DESC LIMIT 5")
rows = cur.fetchall()
for ts, cycles in rows:
    print(f"  {ts[:19]} - {cycles} cycles")

cur.execute("SELECT state_json FROM world_model_state ORDER BY id DESC LIMIT 1")
latest = cur.fetchone()
if latest and latest[0]:
    try:
        state = json.loads(latest[0])
        if isinstance(state, dict):
            print(f"  Latest state keys: {list(state.keys())[:15]}")
            for k, v in list(state.items())[:5]:
                if isinstance(v, (str, int, float, bool)):
                    print(f"    {k}: {v}")
                elif isinstance(v, dict):
                    print(f"    {k}: {list(v.keys())[:5]}...")
    except:
        print(f"  State: {str(latest[0])[:200]}")

conn.close()

# ============================================================================
# OPEN POSITIONS IN DB vs ALPACA
# ============================================================================
section("OPEN POSITIONS (DB)")

conn = sqlite3.connect('prometheus_learning.db', timeout=10)
cur = conn.cursor()
cur.execute("SELECT symbol, side, quantity, entry_price, current_price, unrealized_pl, broker, opened_at FROM open_positions")
rows = cur.fetchall()
if rows:
    print(f"  {'Symbol':<12} {'Side':<5} {'Qty':>10} {'Entry':>10} {'Current':>10} {'UPL':>10} {'Broker':<10}")
    print(f"  {'-'*70}")
    for row in rows:
        sym, side, qty, ep, cp, upl, broker, opened = row
        print(f"  {sym or '':<12} {side or '':<5} {qty or 0:>10.4f} ${ep or 0:>9.2f} ${cp or 0:>9.2f} ${upl or 0:>9.2f} {broker or '':<10}")
conn.close()

# ============================================================================
# .ENV FULL DUMP (MASKED)
# ============================================================================
section(".ENV FULL CONFIGURATION")

env_path = BASE / ".env"
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                if line:
                    print(f"  {line}")
                continue
            if '=' in line:
                key = line.split('=', 1)[0].strip()
                val = line.split('=', 1)[1].strip()
                if any(s in key.upper() for s in ['KEY', 'SECRET', 'PASSWORD', 'TOKEN', 'PASS']):
                    display = f"{'*'*4}...{val[-4:]}" if len(val) > 8 else ('SET' if val else 'EMPTY')
                else:
                    display = val
                print(f"  {key} = {display}")

# ============================================================================
# CORE MODULE ANALYSIS
# ============================================================================
section("CORE MODULE ANALYSIS")

core_dir = BASE / "core"
if core_dir.exists():
    modules = sorted(core_dir.glob("*.py"))
    total_lines = 0
    total_size = 0
    ai_modules = []
    for m in modules:
        size = m.stat().st_size
        total_size += size
        with open(m, 'r', encoding='utf-8', errors='replace') as f:
            lines = sum(1 for _ in f)
        total_lines += lines
        if any(k in m.name for k in ['ai', 'learn', 'signal', 'intel', 'think', 'reason', 'gpt', 'rl', 'regime', 'predict', 'model', 'mercury', 'hrm', 'mesh']):
            ai_modules.append((m.name, lines, size))
    
    print(f"  core/ total: {len(modules)} modules, {total_lines:,} lines, {total_size/(1024*1024):.1f} MB")
    print(f"\n  AI-specific modules ({len(ai_modules)}):")
    for name, lines, size in sorted(ai_modules, key=lambda x: -x[1]):
        print(f"    {name:<45} {lines:>6} lines  {size:>8,} bytes")

# ============================================================================
# SERVER INTERNAL STATE
# ============================================================================
section("SERVER INTERNAL STATE (via API)")

import urllib.request

# Full status
try:
    req = urllib.request.urlopen("http://localhost:8000/api/admin/full-status", timeout=15)
    data = json.loads(req.read())
    
    sub("Account Info")
    acct = data.get('account', {})
    for k, v in acct.items():
        print(f"  {k}: {v}")
    
    sub("Autonomous Trading")
    at = data.get('autonomous_trading', {})
    for k, v in at.items():
        if isinstance(v, list):
            print(f"  {k}: {v}")
        else:
            print(f"  {k}: {v}")
    
    sub("AI Learning")
    ai = data.get('ai_learning', {})
    for k, v in ai.items():
        if isinstance(v, list):
            print(f"  {k}:")
            for item in v:
                print(f"    - {item}")
        else:
            print(f"  {k}: {v}")
    
    sub("Shadow Trading")
    shadow = data.get('shadow_trading', {})
    for k, v in shadow.items():
        print(f"  {k}: {v}")
    
    sub("Trading Stats")
    stats = data.get('trading_stats', {})
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    sub("Resources")
    res = data.get('resources', {})
    for k, v in res.items():
        print(f"  {k}: {v}")
    
    sub("Positions")
    positions = data.get('positions', [])
    print(f"  Total: {len(positions)}")
    for p in positions:
        if isinstance(p, dict):
            print(f"    {p.get('symbol','?')}: qty={p.get('qty')} mv=${p.get('market_value',0)} upl=${p.get('unrealized_pl',0)}")
        else:
            print(f"    {p}")
    
    sub("Other Flags")
    for k in ['live_execution_enabled', 'always_live_mode', 'uptime_seconds']:
        if k in data:
            print(f"  {k}: {data[k]}")
    
except Exception as e:
    print(f"  ERROR: {e}")

# ============================================================================
# HEALTH CHECK
# ============================================================================
section("SERVER HEALTH CHECK")
try:
    req = urllib.request.urlopen("http://localhost:8000/health", timeout=5)
    health = json.loads(req.read())
    print(f"  {json.dumps(health, indent=2)}")
except Exception as e:
    print(f"  {e}")

# ============================================================================
# KEY TRADING PARAMETERS IN SERVER CODE
# ============================================================================
section("KEY TRADING PARAMETERS (from server code)")

server_file = BASE / "unified_production_server.py"
with open(server_file, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Find key parameter definitions
patterns = [
    (r'confidence_threshold\s*[:=]\s*([0-9.]+)', 'confidence_threshold'),
    (r'min_confidence\s*[:=]\s*([0-9.]+)', 'min_confidence'),
    (r'CONFIDENCE_THRESHOLD\s*[:=]\s*([0-9.]+)', 'CONFIDENCE_THRESHOLD'),
    (r'stop_loss_pct\s*[:=]\s*([0-9.]+)', 'stop_loss_pct'),
    (r'take_profit_pct\s*[:=]\s*([0-9.]+)', 'take_profit_pct'),
    (r'max_position_size\s*[:=]\s*([0-9.]+)', 'max_position_size'),
    (r'risk_per_trade\s*[:=]\s*([0-9.]+)', 'risk_per_trade'),
    (r'MAX_TRADES_PER_DAY\s*[:=]\s*([0-9]+)', 'MAX_TRADES_PER_DAY'),
    (r'DAILY_LOSS_LIMIT\s*[:=]\s*([0-9.]+)', 'DAILY_LOSS_LIMIT'),
    (r'position_size\s*[:=]\s*([0-9.]+)', 'position_size'),
]

for pattern, name in patterns:
    matches = re.findall(pattern, content)
    if matches:
        unique = sorted(set(matches))
        print(f"  {name}: {unique}")

# Find _get_enhanced_intelligence bug
sub("Enhanced Intelligence Bug Check")
idx = content.find('_get_enhanced_intelligence')
if idx > 0:
    # Find all calls
    call_matches = list(re.finditer(r'_get_enhanced_intelligence\s*\(([^)]*)\)', content))
    print(f"  Found {len(call_matches)} call(s) to _get_enhanced_intelligence:")
    for m in call_matches[:5]:
        line_num = content[:m.start()].count('\n') + 1
        args = m.group(1).strip()
        print(f"    Line {line_num}: _get_enhanced_intelligence({args[:80]})")
    
    # Find the definition
    def_match = re.search(r'def _get_enhanced_intelligence\s*\(([^)]*)\)', content)
    if def_match:
        line_num = content[:def_match.start()].count('\n') + 1
        params = def_match.group(1).strip()
        print(f"  Definition at line {line_num}: def _get_enhanced_intelligence({params[:80]})")

# ============================================================================
# CONFIGURATION FILES DEEP DIVE
# ============================================================================
section("CONFIGURATION FILES — FULL CONTENTS")

config_files = [
    "advanced_paper_trading_config_optimized.json",
    "ai_signal_weights_config.json",
    "advanced_features_config.json",
]

for cf in config_files:
    fp = BASE / cf
    if fp.exists():
        try:
            data = json.load(open(fp))
            print(f"\n  {cf}:")
            print(f"  {json.dumps(data, indent=2)[:2000]}")
        except Exception as e:
            print(f"  {cf}: ERROR - {e}")

# ============================================================================
# BENCHMARK RESULTS IN DETAIL
# ============================================================================
section("LATEST BENCHMARK RESULTS")

# Find the latest master results
master_files = sorted(BASE.glob("MASTER_BENCHMARK_RESULTS_*.json"), reverse=True)
if master_files:
    latest = master_files[0]
    data = json.load(open(latest))
    print(f"  File: {latest.name}")
    print(f"  Date: {data.get('timestamp', 'unknown')}")
    print(f"  Pass Rate: {data.get('pass_rate')}%")
    print(f"  Passed: {data.get('passed')}")
    print(f"  Failed: {data.get('failed')}")
    print(f"  Timeout: {data.get('timeout')}")
    print(f"  Total: {data.get('total_scripts')}")
    
    sub("Individual Script Results")
    for result in data.get('results', []):
        status = result.get('status', 'unknown')
        name = result.get('script', 'unknown')
        duration = result.get('duration_seconds', 0)
        marker = "PASS" if status == 'passed' else "FAIL" if status == 'failed' else "TIMEOUT"
        print(f"    [{marker:>7}] {name:<50} {duration:.1f}s")

# ============================================================================
# KEY FINDINGS SUMMARY
# ============================================================================
section("KEY FINDINGS SUMMARY")
print("""
  REVIEW EACH SECTION ABOVE FOR COMPLETE DETAILS.
  This audit was generated from live database queries, 
  live API calls, and actual file contents.
""")
print(f"  Audit timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
