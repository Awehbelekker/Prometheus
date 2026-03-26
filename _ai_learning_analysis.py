#!/usr/bin/env python3
"""Analyze AI learning, adaptation, and training effectiveness."""
import sqlite3
import json
import os
import glob
from datetime import datetime

DB = 'prometheus_learning.db'

def main():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # 1. All tables
    print("=" * 70)
    print("PROMETHEUS AI LEARNING & TRAINING ANALYSIS")
    print("=" * 70)
    
    print("\n--- DATABASE TABLES ---")
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in c.fetchall()]
    for t in tables:
        c.execute(f'SELECT COUNT(*) FROM [{t}]')
        cnt = c.fetchone()[0]
        print(f"  {t}: {cnt} rows")
    
    # 2. AI System Performance (weight evolution)
    print("\n--- AI SYSTEM PERFORMANCE (Weight Evolution) ---")
    if 'ai_system_performance' in tables:
        c.execute("PRAGMA table_info(ai_system_performance)")
        cols_info = c.fetchall()
        col_names = [ci[1] for ci in cols_info]
        print(f"  Columns: {col_names}")
        c.execute("SELECT * FROM ai_system_performance ORDER BY rowid DESC LIMIT 20")
        cols = [d[0] for d in c.description]
        rows = c.fetchall()
        for row in rows:
            d = dict(zip(cols, row))
            print(f"  {d}")
    
    # 3. AI Trade Attribution Summary
    print("\n--- AI TRADE ATTRIBUTION (Per System) ---")
    if 'ai_trade_attribution' in tables:
        c.execute("PRAGMA table_info(ai_trade_attribution)")
        cols_info = c.fetchall()
        print(f"  Columns: {[ci[1] for ci in cols_info]}")
        
        c.execute("""SELECT ai_system, COUNT(*) as cnt, 
            AVG(CAST(confidence as FLOAT)) as avg_conf,
            AVG(CAST(weight as FLOAT)) as avg_weight,
            MIN(CAST(weight as FLOAT)) as min_weight,
            MAX(CAST(weight as FLOAT)) as max_weight,
            COUNT(DISTINCT ROUND(CAST(weight as FLOAT), 4)) as unique_weights
            FROM ai_trade_attribution 
            GROUP BY ai_system ORDER BY cnt DESC""")
        for row in c.fetchall():
            print(f"  {row[0]}: {row[1]} records | avg_conf={row[2]:.3f} | "
                  f"weight: avg={row[3]:.4f} min={row[4]:.4f} max={row[5]:.4f} unique={row[6]}")
    
    # 4. Weight changes over time (first vs last)
    print("\n--- WEIGHT EVOLUTION (First vs Last Attribution) ---")
    if 'ai_trade_attribution' in tables:
        c.execute("SELECT DISTINCT ai_system FROM ai_trade_attribution")
        systems = [r[0] for r in c.fetchall()]
        for sys_name in systems:
            c.execute(f"""SELECT weight FROM ai_trade_attribution 
                WHERE ai_system = ? ORDER BY rowid ASC LIMIT 1""", (sys_name,))
            first = c.fetchone()
            c.execute(f"""SELECT weight FROM ai_trade_attribution
                WHERE ai_system = ? ORDER BY rowid DESC LIMIT 1""", (sys_name,))
            last = c.fetchone()
            if first and last:
                f_w = float(first[0]) if first[0] else 0
                l_w = float(last[0]) if last[0] else 0
                change = l_w - f_w
                pct = (change / f_w * 100) if f_w != 0 else 0
                arrow = "^" if change > 0 else ("v" if change < 0 else "=")
                print(f"  {sys_name}: {f_w:.4f} -> {l_w:.4f} ({arrow} {change:+.4f}, {pct:+.1f}%)")
    
    # 5. Continuous Learning
    print("\n--- CONTINUOUS LEARNING DATA ---")
    if 'continuous_learning' in tables:
        c.execute("PRAGMA table_info(continuous_learning)")
        print(f"  Columns: {[ci[1] for ci in c.fetchall()]}")
        c.execute("SELECT * FROM continuous_learning ORDER BY rowid DESC LIMIT 10")
        cols = [d[0] for d in c.description]
        for row in c.fetchall():
            print(f"  {dict(zip(cols, row))}")
    
    # 6. Trade History Performance
    print("\n--- TRADE PERFORMANCE BY DATE ---")
    if 'trade_history' in tables:
        c.execute("""SELECT date(timestamp) as dt, COUNT(*) as trades,
            SUM(CASE WHEN CAST(profit_loss AS FLOAT) > 0 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN CAST(profit_loss AS FLOAT) <= 0 THEN 1 ELSE 0 END) as losses,
            ROUND(AVG(CAST(profit_loss AS FLOAT)), 4) as avg_pnl,
            ROUND(SUM(CAST(profit_loss AS FLOAT)), 4) as total_pnl
            FROM trade_history WHERE timestamp IS NOT NULL
            GROUP BY date(timestamp) ORDER BY dt DESC LIMIT 30""")
        total_trades = 0
        total_wins = 0
        for row in c.fetchall():
            dt, trades, wins, losses, avg_pnl, total_pnl = row
            wr = (wins / trades * 100) if trades > 0 else 0
            total_trades += trades
            total_wins += wins
            print(f"  {dt}: {trades} trades, {wins}W/{losses}L, WR={wr:.0f}%, "
                  f"avg_pnl=${avg_pnl}, total_pnl=${total_pnl}")
        if total_trades > 0:
            print(f"  OVERALL: {total_trades} trades, {total_wins}W, "
                  f"WR={total_wins/total_trades*100:.1f}%")
    
    # 7. Market regime adaptation
    print("\n--- MARKET REGIME ADAPTATION ---")
    if 'market_regimes' in tables:
        c.execute("SELECT * FROM market_regimes ORDER BY rowid DESC LIMIT 10")
        cols = [d[0] for d in c.description]
        for row in c.fetchall():
            print(f"  {dict(zip(cols, row))}")
    else:
        # Check if regime data is in other tables
        for t in tables:
            if 'regime' in t.lower() or 'market' in t.lower():
                c.execute(f"SELECT * FROM [{t}] LIMIT 3")
                cols = [d[0] for d in c.description]
                print(f"  Table [{t}]:")
                for row in c.fetchall():
                    print(f"    {dict(zip(cols, row))}")
    
    # 8. Learning/training model files
    print("\n--- TRAINING & MODEL FILES ---")
    patterns = ['*model*.json', '*model*.pkl', '*model*.h5', '*weights*.json',
                '*learning*.json', '*training*.json', '*ai_signal_weights*']
    found = set()
    for p in patterns:
        for f in glob.glob(p):
            found.add(f)
    for f in sorted(found):
        size = os.path.getsize(f)
        mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M')
        print(f"  {f} ({size:,} bytes, modified: {mtime})")
        if f.endswith('.json') and size < 10000:
            try:
                with open(f) as fh:
                    data = json.load(fh)
                if isinstance(data, dict):
                    for k, v in list(data.items())[:10]:
                        print(f"    {k}: {v}")
            except:
                pass
    
    # 9. Shadow trading results
    print("\n--- SHADOW TRADING ANALYSIS ---")
    shadow_files = glob.glob('shadow_trading_results/*.json')
    print(f"  Total shadow result files: {len(shadow_files)}")
    if shadow_files:
        total_trades = 0
        total_profitable = 0
        for sf in shadow_files[-5:]:
            try:
                with open(sf) as fh:
                    data = json.load(fh)
                trades = data.get('total_trades', 0)
                capital = data.get('current_capital', 0)
                total_trades += trades
                print(f"  {os.path.basename(sf)}: trades={trades}, capital={capital}")
            except:
                pass
        print(f"  Recent shadow trades total: {total_trades}")
    
    # 10. Open positions and their AI signals
    print("\n--- CURRENT OPEN POSITIONS ---")
    if 'open_positions' in tables:
        c.execute("SELECT * FROM open_positions")
        cols = [d[0] for d in c.description]
        print(f"  Columns: {cols}")
        for row in c.fetchall():
            print(f"  {dict(zip(cols, row))}")
    
    # 11. Recent trade details
    print("\n--- LAST 10 TRADES (Full Detail) ---")
    if 'trade_history' in tables:
        c.execute("SELECT * FROM trade_history ORDER BY rowid DESC LIMIT 10")
        cols = [d[0] for d in c.description]
        for row in c.fetchall():
            d = dict(zip(cols, row))
            print(f"  {d.get('symbol','?')} | {d.get('action','?')} | "
                  f"qty={d.get('quantity','?')} | price={d.get('price','?')} | "
                  f"pnl={d.get('profit_loss','?')} | {d.get('timestamp','?')}")
    
    # 12. Underperformer removal log
    print("\n--- UNDERPERFORMER REMOVALS ---")
    if 'underperformers' in tables:
        c.execute("SELECT * FROM underperformers ORDER BY rowid DESC LIMIT 20")
        cols = [d[0] for d in c.description]
        for row in c.fetchall():
            print(f"  {dict(zip(cols, row))}")
    
    # 13. Check all learning-related tables
    print("\n--- ALL LEARNING-RELATED TABLES ---")
    for t in tables:
        if any(k in t.lower() for k in ['learn', 'train', 'model', 'adapt', 'optim', 'weight', 'regime', 'perf']):
            c.execute(f"PRAGMA table_info([{t}])")
            info = c.fetchall()
            c.execute(f"SELECT COUNT(*) FROM [{t}]")
            cnt = c.fetchone()[0]
            print(f"\n  [{t}] ({cnt} rows)")
            print(f"    Columns: {[i[1] for i in info]}")
            if cnt > 0 and cnt <= 20:
                c.execute(f"SELECT * FROM [{t}]")
                cols = [d[0] for d in c.description]
                for row in c.fetchall():
                    print(f"    {dict(zip(cols, row))}")
            elif cnt > 20:
                c.execute(f"SELECT * FROM [{t}] ORDER BY rowid DESC LIMIT 5")
                cols = [d[0] for d in c.description]
                for row in c.fetchall():
                    print(f"    {dict(zip(cols, row))}")

    conn.close()
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")

if __name__ == '__main__':
    main()
