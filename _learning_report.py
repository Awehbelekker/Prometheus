"""Deep Learning Pipeline Report - March 3, 2026"""
import sqlite3, os, json
from datetime import datetime, timedelta
from collections import Counter

BASE = r'c:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform'

def section(title):
    print(f"\n{'='*65}")
    print(f"  {title}")
    print(f"{'='*65}")

db = sqlite3.connect(os.path.join(BASE, 'prometheus_learning.db'))
db.row_factory = sqlite3.Row

# ═══════════════════════════════════════════════════════
section("1. LEARNING OUTCOMES - FULL ANALYSIS (106 total)")
# ═══════════════════════════════════════════════════════
outcomes = db.execute("""
    SELECT * FROM learning_outcomes ORDER BY timestamp DESC
""").fetchall()
print(f"Total outcomes recorded: {len(outcomes)}")

# Accuracy
correct = sum(1 for o in outcomes if o['was_correct'] == 1)
incorrect = sum(1 for o in outcomes if o['was_correct'] == 0)
print(f"Correct: {correct}  Incorrect: {incorrect}  Accuracy: {correct/len(outcomes)*100:.1f}%")

# P/L stats
pls = [o['profit_loss'] for o in outcomes if o['profit_loss'] is not None]
wins = [p for p in pls if p > 0]
losses = [p for p in pls if p < 0]
print(f"\nP/L Distribution:")
print(f"  Total P/L: ${sum(pls):.2f}")
print(f"  Winning trades: {len(wins)} (avg ${sum(wins)/len(wins):.2f})" if wins else "  No wins")
print(f"  Losing trades: {len(losses)} (avg ${sum(losses)/len(losses):.2f})" if losses else "  No losses")
print(f"  Win rate: {len(wins)/len(pls)*100:.1f}%" if pls else "  N/A")

# By symbol
print(f"\nOutcomes by Symbol:")
sym_data = {}
for o in outcomes:
    s = o['symbol']
    if s not in sym_data:
        sym_data[s] = {'correct': 0, 'incorrect': 0, 'total_pl': 0, 'count': 0}
    sym_data[s]['count'] += 1
    sym_data[s]['total_pl'] += o['profit_loss'] or 0
    if o['was_correct'] == 1:
        sym_data[s]['correct'] += 1
    else:
        sym_data[s]['incorrect'] += 1

print(f"  {'Symbol':<12} {'Count':<7} {'Correct':<9} {'Accuracy':<10} {'Net P/L'}")
print(f"  {'-'*50}")
for s, d in sorted(sym_data.items(), key=lambda x: -x[1]['count']):
    acc = d['correct']/d['count']*100 if d['count'] > 0 else 0
    print(f"  {s:<12} {d['count']:<7} {d['correct']:<9} {acc:.0f}%       ${d['total_pl']:.2f}")

# By action
print(f"\nOutcomes by Predicted Action:")
for action in ['BUY', 'SELL', 'HOLD']:
    subset = [o for o in outcomes if o['predicted_action'] == action]
    if subset:
        c = sum(1 for o in subset if o['was_correct'] == 1)
        pl = sum(o['profit_loss'] or 0 for o in subset)
        print(f"  {action}: {len(subset)} predictions, {c} correct ({c/len(subset)*100:.0f}%), P/L=${pl:.2f}")

# By confidence buckets
print(f"\nAccuracy by Confidence Level:")
buckets = {'Low (<60%)': [], 'Medium (60-75%)': [], 'High (>75%)': []}
for o in outcomes:
    c = o['predicted_confidence'] or 0
    if c < 0.6:
        buckets['Low (<60%)'].append(o)
    elif c < 0.75:
        buckets['Medium (60-75%)'].append(o)
    else:
        buckets['High (>75%)'].append(o)
for bname, items in buckets.items():
    if items:
        correct_b = sum(1 for i in items if i['was_correct'] == 1)
        print(f"  {bname}: {len(items)} predictions, {correct_b} correct ({correct_b/len(items)*100:.0f}%)")

# Last 10 outcomes
print(f"\nLast 10 Learning Outcomes:")
for o in outcomes[:10]:
    ts = str(o['timestamp'])[:19]
    action = o['predicted_action']
    conf = o['predicted_confidence'] or 0
    correct_str = "CORRECT" if o['was_correct'] == 1 else "WRONG"
    pl = o['profit_loss'] or 0
    pct = o['profit_pct'] or 0
    print(f"  {ts}  {o['symbol']:<8}  {action:<5}  conf={conf:.1%}  {correct_str:<7}  P/L=${pl:.2f} ({pct*100:.1f}%)")

# ═══════════════════════════════════════════════════════
section("2. AI ATTRIBUTION DEEP DIVE (198K votes)")
# ═══════════════════════════════════════════════════════

# Outcome recording rate
total_attr = db.execute("SELECT COUNT(*) FROM ai_attribution").fetchone()[0]
recorded = db.execute("SELECT COUNT(*) FROM ai_attribution WHERE outcome_recorded=1").fetchone()[0]
print(f"Total attributions: {total_attr:,}")
print(f"Outcomes recorded: {recorded:,}  ({recorded/total_attr*100:.2f}%)")

# Attribution by system with P/L
print(f"\nAI System Performance (where P/L recorded):")
sys_perf = db.execute("""
    SELECT ai_system, 
           COUNT(*) as votes,
           AVG(confidence) as avg_conf,
           SUM(CASE WHEN outcome_recorded=1 THEN 1 ELSE 0 END) as outcomes,
           AVG(CASE WHEN eventual_pnl IS NOT NULL THEN eventual_pnl END) as avg_pnl,
           SUM(CASE WHEN eventual_pnl > 0 THEN 1 ELSE 0 END) as wins,
           SUM(CASE WHEN eventual_pnl < 0 THEN 1 ELSE 0 END) as losses
    FROM ai_attribution 
    GROUP BY ai_system 
    ORDER BY votes DESC
""").fetchall()
print(f"  {'System':<35} {'Votes':<8} {'AvgConf':<8} {'Outcomes':<10} {'AvgP/L':<10} {'W/L'}")
print(f"  {'-'*80}")
for r in sys_perf:
    avg_pnl = f"${r['avg_pnl']:.4f}" if r['avg_pnl'] is not None else "N/A"
    wl = f"{r['wins'] or 0}/{r['losses'] or 0}" if r['outcomes'] > 0 else "N/A"
    print(f"  {r['ai_system']:<35} {r['votes']:<8} {r['avg_conf']:.3f}   {r['outcomes']:<10} {avg_pnl:<10} {wl}")

# Attribution over time (by week)
print(f"\nWeekly Attribution Volume:")
weekly = db.execute("""
    SELECT strftime('%Y-W%W', timestamp) as week, COUNT(*) as cnt,
           SUM(CASE WHEN outcome_recorded=1 THEN 1 ELSE 0 END) as recorded
    FROM ai_attribution 
    GROUP BY week ORDER BY week DESC LIMIT 8
""").fetchall()
for w in weekly:
    rec_pct = w['recorded']/w['cnt']*100 if w['cnt'] > 0 else 0
    print(f"  {w['week']}: {w['cnt']:,} votes, {w['recorded']:,} outcomes ({rec_pct:.1f}%)")

# ═══════════════════════════════════════════════════════
section("3. SIGNAL PREDICTIONS ANALYSIS (161K)")
# ═══════════════════════════════════════════════════════
total_sigs = db.execute("SELECT COUNT(*) FROM signal_predictions").fetchone()[0]
recorded_sigs = db.execute("SELECT COUNT(*) FROM signal_predictions WHERE outcome_recorded=1").fetchone()[0]
print(f"Total signals: {total_sigs:,}")
print(f"Outcomes recorded: {recorded_sigs:,} ({recorded_sigs/total_sigs*100:.2f}%)")

# Signal breakdown by action
print(f"\nSignal Distribution:")
actions = db.execute("SELECT action, COUNT(*) as cnt, AVG(confidence) as avg_conf FROM signal_predictions GROUP BY action ORDER BY cnt DESC").fetchall()
for a in actions:
    print(f"  {a['action']}: {a['cnt']:,} signals (avg conf: {a['avg_conf']:.1%})")

# Signals by symbol (top 15)
print(f"\nTop 15 Symbols by Signal Count:")
sym_sigs = db.execute("""
    SELECT symbol, COUNT(*) as cnt, 
           AVG(confidence) as avg_conf,
           SUM(CASE WHEN action='BUY' THEN 1 ELSE 0 END) as buys,
           SUM(CASE WHEN action='SELL' THEN 1 ELSE 0 END) as sells,
           SUM(CASE WHEN action='HOLD' THEN 1 ELSE 0 END) as holds
    FROM signal_predictions GROUP BY symbol ORDER BY cnt DESC LIMIT 15
""").fetchall()
print(f"  {'Symbol':<12} {'Total':<8} {'AvgConf':<9} {'BUY':<8} {'SELL':<8} {'HOLD'}")
print(f"  {'-'*55}")
for r in sym_sigs:
    print(f"  {r['symbol']:<12} {r['cnt']:<8} {r['avg_conf']:.1%}    {r['buys']:<8} {r['sells']:<8} {r['holds']}")

# Today's signals
print(f"\nToday's Signals (Mar 3):")
today_sigs = db.execute("""
    SELECT timestamp, symbol, action, confidence, ai_components 
    FROM signal_predictions WHERE timestamp >= '2026-03-03'
    ORDER BY timestamp DESC LIMIT 20
""").fetchall()
today_count = db.execute("SELECT COUNT(*) FROM signal_predictions WHERE timestamp LIKE '2026-03-03%'").fetchone()[0]
print(f"  Signals generated today: {today_count}")
for s in today_sigs[:15]:
    ts = str(s['timestamp'])[:19]
    components = s['ai_components'] or ''
    print(f"  {ts}  {s['symbol']:<8}  {s['action']:<5}  conf={s['confidence']:.1%}  {components[:60]}")

# ═══════════════════════════════════════════════════════
section("4. MODEL RETRAIN LOG - FULL ANALYSIS (68 retrains)")
# ═══════════════════════════════════════════════════════
retrains = db.execute("SELECT * FROM model_retrain_log ORDER BY id DESC").fetchall()
print(f"Total retrains: {len(retrains)}")

success = sum(1 for r in retrains if r['success'] == 1)
fail = sum(1 for r in retrains if r['success'] == 0)
print(f"Successful: {success} ({success/len(retrains)*100:.0f}%)")
print(f"Failed: {fail} ({fail/len(retrains)*100:.0f}%)")

# By model type
print(f"\nBy Model Type:")
for mtype in ['direction', 'price']:
    subset = [r for r in retrains if r['model_type'] == mtype]
    s = sum(1 for r in subset if r['success'] == 1)
    f = sum(1 for r in subset if r['success'] == 0)
    metrics = [r['new_metric'] for r in subset if r['new_metric'] is not None and r['success'] == 1]
    avg_m = sum(metrics)/len(metrics) if metrics else 0
    print(f"  {mtype}: {len(subset)} attempts, {s} success, {f} fail")
    if mtype == 'direction':
        print(f"    Avg accuracy: {avg_m:.3f}")
    else:
        print(f"    Avg R²: {avg_m:.3f}")

# By symbol
print(f"\nRetrain Results by Symbol:")
sym_retrains = {}
for r in retrains:
    s = r['symbol']
    if s not in sym_retrains:
        sym_retrains[s] = {'success': 0, 'fail': 0, 'dir_metric': None, 'price_metric': None}
    if r['success'] == 1:
        sym_retrains[s]['success'] += 1
        if r['model_type'] == 'direction' and r['new_metric']:
            sym_retrains[s]['dir_metric'] = r['new_metric']
        elif r['model_type'] == 'price' and r['new_metric']:
            sym_retrains[s]['price_metric'] = r['new_metric']
    else:
        sym_retrains[s]['fail'] += 1

print(f"  {'Symbol':<10} {'OK':<5} {'Fail':<6} {'Dir Acc':<10} {'Price R²'}")
print(f"  {'-'*45}")
for s, d in sorted(sym_retrains.items()):
    dir_m = f"{d['dir_metric']:.3f}" if d['dir_metric'] else "N/A"
    price_m = f"{d['price_metric']:.3f}" if d['price_metric'] else "N/A"
    print(f"  {s:<10} {d['success']:<5} {d['fail']:<6} {dir_m:<10} {price_m}")

# Failure reasons
print(f"\nFailure Reasons:")
reasons = Counter()
for r in retrains:
    if r['success'] == 0 and r['reason']:
        reason_cat = r['reason'].split('(')[0].strip() if '(' in r['reason'] else r['reason']
        reasons[reason_cat] += 1
for reason, cnt in reasons.most_common():
    print(f"  {reason}: {cnt}")

# ═══════════════════════════════════════════════════════
section("5. SHADOW TRADING ANALYSIS")
# ═══════════════════════════════════════════════════════
shadows = db.execute("SELECT * FROM shadow_trade_history ORDER BY timestamp DESC").fetchall()
print(f"Total shadow trades: {len(shadows)}")

open_shadows = [s for s in shadows if s['status'] == 'OPEN']
closed_shadows = [s for s in shadows if s['status'] == 'CLOSED']
print(f"Open: {len(open_shadows)}  Closed: {len(closed_shadows)}")

if closed_shadows:
    pnls = [s['pnl'] for s in closed_shadows if s['pnl'] is not None]
    wins_s = [p for p in pnls if p > 0]
    losses_s = [p for p in pnls if p < 0]
    print(f"\nClosed Shadow Trade Performance:")
    print(f"  Total P/L: ${sum(pnls):.2f}")
    print(f"  Winners: {len(wins_s)} (avg ${sum(wins_s)/len(wins_s):.2f})" if wins_s else "  Winners: 0")
    print(f"  Losers: {len(losses_s)} (avg ${sum(losses_s)/len(losses_s):.2f})" if losses_s else "  Losers: 0")
    print(f"  Win rate: {len(wins_s)/len(pnls)*100:.1f}%" if pnls else "  N/A")
    print(f"  Best: ${max(pnls):.2f}" if pnls else "")
    print(f"  Worst: ${min(pnls):.2f}" if pnls else "")

    # By symbol
    print(f"\n  Shadow P/L by Symbol:")
    sym_shadow = {}
    for s in closed_shadows:
        sym = s['symbol']
        if sym not in sym_shadow:
            sym_shadow[sym] = {'trades': 0, 'pnl': 0, 'wins': 0, 'losses': 0}
        sym_shadow[sym]['trades'] += 1
        sym_shadow[sym]['pnl'] += s['pnl'] or 0
        if (s['pnl'] or 0) > 0:
            sym_shadow[sym]['wins'] += 1
        elif (s['pnl'] or 0) < 0:
            sym_shadow[sym]['losses'] += 1
    
    for sym, d in sorted(sym_shadow.items(), key=lambda x: -x[1]['pnl']):
        wr = d['wins']/(d['wins']+d['losses'])*100 if (d['wins']+d['losses']) > 0 else 0
        print(f"    {sym:<10} trades={d['trades']}  P/L=${d['pnl']:.2f}  W/L={d['wins']}/{d['losses']}  WR={wr:.0f}%")

# Shadow sessions
print(f"\nShadow Session Configs:")
configs = db.execute("""
    SELECT config_name, COUNT(*) as sessions, 
           SUM(total_trades) as total_trades,
           SUM(winning_trades) as total_wins,
           SUM(total_pnl) as total_pnl
    FROM shadow_sessions
    GROUP BY config_name
""").fetchall()
for c in configs:
    wr = c['total_wins']/c['total_trades']*100 if c['total_trades'] and c['total_trades'] > 0 else 0
    print(f"  {c['config_name']:<20} sessions={c['sessions']:<5} trades={c['total_trades'] or 0:<5} wins={c['total_wins'] or 0}  P/L=${c['total_pnl'] or 0:.2f}")

# ═══════════════════════════════════════════════════════
section("6. ADAPTIVE LEARNING ENGINE (ALE) STATUS")
# ═══════════════════════════════════════════════════════
print("ALE Database Tables Status:")
ale_tables = {
    'live_trade_outcomes': 'Captures real trade outcomes for learning',
    'ai_weight_history': 'Tracks AI system weight adjustments', 
    'model_retrain_log': 'Records automatic model retraining',
    'risk_adaptation_log': 'Performance-triggered risk changes',
    'learning_insights': 'Generated learning insights',
    'live_position_tracking': 'Tracks live positions for outcome matching',
    'live_shadow_comparison': 'Compares live vs shadow performance',
    'pattern_insights': 'Discovered trading patterns'
}
for table, desc in ale_tables.items():
    try:
        cnt = db.execute(f"SELECT COUNT(*) FROM [{table}]").fetchone()[0]
        status = "ACTIVE" if cnt > 0 else "EMPTY (waiting for data)"
        print(f"  {table:<30} {cnt:>6} rows  {status}")
    except:
        print(f"  {table:<30}  TABLE NOT FOUND")

# ═══════════════════════════════════════════════════════
section("7. AI SYSTEM METRICS")
# ═══════════════════════════════════════════════════════
try:
    metrics = db.execute("SELECT * FROM ai_system_metrics ORDER BY rowid DESC").fetchall()
    print(f"AI system metric entries: {len(metrics)}")
    for m in metrics:
        print(f"  {dict(m)}")
except Exception as e:
    print(f"Error: {e}")

# ═══════════════════════════════════════════════════════
section("8. TRADE OPTIMIZATION LOG")
# ═══════════════════════════════════════════════════════
try:
    opts = db.execute("SELECT * FROM trade_optimization ORDER BY rowid DESC LIMIT 10").fetchall()
    print(f"Optimization entries: {db.execute('SELECT COUNT(*) FROM trade_optimization').fetchone()[0]}")
    for o in opts:
        print(f"  {dict(o)}")
except Exception as e:
    print(f"Error: {e}")

# ═══════════════════════════════════════════════════════
section("9. LEARNING PIPELINE HEALTH CHECK")
# ═══════════════════════════════════════════════════════
print("Checking feedback loop completeness...\n")

# Check: How many live trades have outcomes?
total_trades = db.execute("SELECT COUNT(*) FROM trade_history").fetchone()[0]
total_outcomes = db.execute("SELECT COUNT(*) FROM learning_outcomes").fetchone()[0]
print(f"  Trade History:     {total_trades:,} trades")
print(f"  Learning Outcomes: {total_outcomes:,} recorded")
print(f"  Feedback Rate:     {total_outcomes/total_trades*100:.1f}%" if total_trades > 0 else "  N/A")

# Check: How many signals have been validated?
sigs_total = db.execute("SELECT COUNT(*) FROM signal_predictions").fetchone()[0]
sigs_recorded = db.execute("SELECT COUNT(*) FROM signal_predictions WHERE outcome_recorded=1").fetchone()[0]
print(f"\n  Signal Predictions: {sigs_total:,}")
print(f"  Outcomes Recorded:  {sigs_recorded:,}")
print(f"  Validation Rate:    {sigs_recorded/sigs_total*100:.2f}%" if sigs_total > 0 else "  N/A")

# Check: Attribution feedback
attr_total = db.execute("SELECT COUNT(*) FROM ai_attribution").fetchone()[0]
attr_recorded = db.execute("SELECT COUNT(*) FROM ai_attribution WHERE outcome_recorded=1").fetchone()[0]
print(f"\n  AI Attributions:    {attr_total:,}")
print(f"  Outcomes Recorded:  {attr_recorded:,}")
print(f"  Feedback Rate:      {attr_recorded/attr_total*100:.2f}%" if attr_total > 0 else "  N/A")

# Check: Model freshness
print(f"\n  Model Retrain Success Rate: {success}/{len(retrains)} ({success/len(retrains)*100:.0f}%)")

# Check: ALE producing data
ale_live = db.execute("SELECT COUNT(*) FROM live_trade_outcomes").fetchone()[0]
ale_weights = db.execute("SELECT COUNT(*) FROM ai_weight_history").fetchone()[0]
ale_risk = db.execute("SELECT COUNT(*) FROM risk_adaptation_log").fetchone()[0]
ale_insights = db.execute("SELECT COUNT(*) FROM learning_insights").fetchone()[0]
print(f"\n  ALE Live Outcomes:  {ale_live}")
print(f"  ALE Weight Updates: {ale_weights}")
print(f"  ALE Risk Adapts:    {ale_risk}")
print(f"  ALE Insights:       {ale_insights}")

total_ale = ale_live + ale_weights + ale_risk + ale_insights
if total_ale == 0:
    print(f"\n  STATUS: ALE loops running but NO data produced yet")
    print(f"  REASON: ALE needs closed positions with P/L to trigger learning")
    print(f"          The 5 loops check every 60s/5m/1h/10m/15m respectively")
else:
    print(f"\n  STATUS: ALE actively producing learning data")

# ═══════════════════════════════════════════════════════
section("10. CONFIDENCE CALIBRATION")
# ═══════════════════════════════════════════════════════
print("How well calibrated are confidence scores?\n")
# For each confidence bucket, what % of predictions were correct?
cal_data = db.execute("""
    SELECT 
        CASE 
            WHEN predicted_confidence < 0.5 THEN '0-50%'
            WHEN predicted_confidence < 0.6 THEN '50-60%'
            WHEN predicted_confidence < 0.7 THEN '60-70%'
            WHEN predicted_confidence < 0.8 THEN '70-80%'
            ELSE '80%+'
        END as bucket,
        COUNT(*) as total,
        SUM(CASE WHEN was_correct=1 THEN 1 ELSE 0 END) as correct,
        AVG(profit_loss) as avg_pl,
        AVG(profit_pct) as avg_pct
    FROM learning_outcomes 
    GROUP BY bucket
    ORDER BY bucket
""").fetchall()
print(f"  {'Confidence':<12} {'Predictions':<13} {'Correct':<9} {'Accuracy':<10} {'Avg P/L':<10} {'Avg %'}")
print(f"  {'-'*60}")
for r in cal_data:
    acc = r['correct']/r['total']*100 if r['total'] > 0 else 0
    avg_pl = f"${r['avg_pl']:.4f}" if r['avg_pl'] is not None else "N/A"
    avg_pct = f"{r['avg_pct']*100:.2f}%" if r['avg_pct'] is not None else "N/A"
    print(f"  {r['bucket']:<12} {r['total']:<13} {r['correct']:<9} {acc:.0f}%       {avg_pl:<10} {avg_pct}")

db.close()

# ═══════════════════════════════════════════════════════
section("11. ALE LOG ACTIVITY")
# ═══════════════════════════════════════════════════════
print("Checking prometheus_headless.log for ALE activity...\n")
log_file = os.path.join(BASE, 'prometheus_headless.log')
if os.path.exists(log_file):
    ale_lines = []
    learning_lines = []
    retrain_lines = []
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if 'adaptive_learning' in line.lower() or 'AdaptiveLearning' in line:
                ale_lines.append(line.strip())
            if 'learning' in line.lower() and '2026-03-03' in line:
                learning_lines.append(line.strip())
            if 'retrain' in line.lower() and '2026-03-03' in line:
                retrain_lines.append(line.strip())
    
    print(f"  ALE log entries (all time): {len(ale_lines)}")
    print(f"  Learning-related entries today: {len(learning_lines)}")
    print(f"  Retrain entries today: {len(retrain_lines)}")
    
    if ale_lines:
        print(f"\n  Last 15 ALE log entries:")
        for l in ale_lines[-15:]:
            print(f"    {l[:120]}")
    
    if retrain_lines:
        print(f"\n  Last 10 retrain log entries today:")
        for l in retrain_lines[-10:]:
            print(f"    {l[:120]}")

# ═══════════════════════════════════════════════════════
section("12. MODEL FILES - FRESHNESS AUDIT")
# ═══════════════════════════════════════════════════════
model_dir = os.path.join(BASE, 'models_pretrained')
if os.path.exists(model_dir):
    now = datetime.now()
    models = {}
    for f in os.listdir(model_dir):
        if f.endswith(('.pkl', '.joblib')):
            fp = os.path.join(model_dir, f)
            age_h = (now - datetime.fromtimestamp(os.path.getmtime(fp))).total_seconds() / 3600
            # Extract symbol and type
            parts = f.replace('_model.pkl', '').replace('_scaler.pkl', '')
            if '_direction_' in f:
                mtype = 'direction'
                sym = f.split('_direction_')[0]
            elif '_price_' in f:
                mtype = 'price'
                sym = f.split('_price_')[0]
            else:
                continue
            
            if sym not in models:
                models[sym] = {}
            if 'scaler' in f:
                continue
            models[sym][mtype] = age_h
    
    print(f"{'Symbol':<12} {'Direction Age':<16} {'Price Age':<16} {'Status'}")
    print(f"{'-'*55}")
    for sym in sorted(models):
        d = models[sym]
        dir_age = f"{d.get('direction', 999):.1f}h" if 'direction' in d else "MISSING"
        price_age = f"{d.get('price', 999):.1f}h" if 'price' in d else "MISSING"
        
        max_age = max(d.get('direction', 0), d.get('price', 0))
        if max_age < 24:
            status = "FRESH"
        elif max_age < 72:
            status = "OK"
        elif max_age < 168:
            status = "STALE"
        else:
            status = "VERY STALE"
        print(f"  {sym:<12} {dir_age:<16} {price_age:<16} {status}")

print(f"\n{'='*65}")
print(f"  LEARNING REPORT COMPLETE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*65}")
