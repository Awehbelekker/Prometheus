#!/usr/bin/env python3
"""Deep analysis of AI attribution, learning outcomes, and training."""
import sqlite3

DB = 'prometheus_learning.db'

def main():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    print("=== AI ATTRIBUTION TABLE ===")
    c.execute("PRAGMA table_info(ai_attribution)")
    cols = [ci[1] for ci in c.fetchall()]
    print(f"Columns: {cols}")

    c.execute("SELECT COUNT(*) FROM ai_attribution")
    print(f"Total rows: {c.fetchone()[0]}")

    c.execute("SELECT COUNT(*) FROM ai_attribution WHERE outcome_recorded = 1")
    print(f"With outcomes: {c.fetchone()[0]}")

    c.execute("SELECT COUNT(*) FROM ai_attribution WHERE eventual_pnl IS NOT NULL AND eventual_pnl != 0")
    print(f"With non-zero PnL: {c.fetchone()[0]}")

    print("\n=== AI SYSTEM PERFORMANCE FROM ATTRIBUTION ===")
    c.execute("""SELECT ai_system, COUNT(*) as total,
        SUM(CASE WHEN outcome_recorded=1 THEN 1 ELSE 0 END) as with_outcome,
        SUM(CASE WHEN eventual_pnl > 0 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN eventual_pnl <= 0 AND outcome_recorded=1 THEN 1 ELSE 0 END) as losses,
        AVG(CASE WHEN outcome_recorded=1 THEN eventual_pnl END) as avg_pnl,
        SUM(eventual_pnl) as total_pnl
        FROM ai_attribution GROUP BY ai_system ORDER BY total DESC""")
    for row in c.fetchall():
        sys_name, total, outcomes, wins, losses, avg_pnl, total_pnl = row
        wins = wins or 0
        losses = losses or 0
        wr = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        print(f"  {sys_name}: {total} signals, {outcomes} outcomes, "
              f"{wins}W/{losses}L, WR={wr:.0f}%, "
              f"avg_pnl=${avg_pnl or 0:.4f}, total=${total_pnl or 0:.4f}")

    print("\n=== SIGNAL PREDICTIONS SUMMARY ===")
    c.execute("PRAGMA table_info(signal_predictions)")
    cols = [ci[1] for ci in c.fetchall()]
    print(f"Columns: {cols}")
    c.execute("SELECT action, COUNT(*) FROM signal_predictions GROUP BY action ORDER BY COUNT(*) DESC")
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1]}")

    print("\n=== LEARNING OUTCOMES STATS ===")
    c.execute("""SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN was_correct=1 THEN 1 ELSE 0 END) as correct,
        AVG(predicted_confidence) as avg_conf,
        AVG(profit_pct) as avg_pnl_pct
        FROM learning_outcomes""")
    row = c.fetchone()
    total = row[0]
    correct = row[1] or 0
    print(f"  Total outcomes: {total}")
    print(f"  Correct predictions: {correct}")
    if total > 0:
        print(f"  Accuracy: {correct/total*100:.1f}%")
    if row[2]:
        print(f"  Avg confidence: {row[2]:.3f}")
    if row[3]:
        print(f"  Avg PnL%: {row[3]*100:.2f}%")

    print("\n=== LEARNING IMPROVEMENT TREND (by month) ===")
    c.execute("""SELECT 
        strftime('%Y-%m', timestamp) as month,
        COUNT(*) as total,
        SUM(CASE WHEN was_correct=1 THEN 1 ELSE 0 END) as correct,
        AVG(profit_pct)*100 as avg_pnl_pct,
        AVG(predicted_confidence) as avg_conf
        FROM learning_outcomes
        GROUP BY month ORDER BY month""")
    for row in c.fetchall():
        month, total, correct, avg_pnl, avg_conf = row
        correct = correct or 0
        acc = (correct / total * 100) if total > 0 else 0
        print(f"  {month}: {total} outcomes, {acc:.0f}% accuracy, "
              f"avg_pnl={avg_pnl or 0:.2f}%, conf={avg_conf or 0:.3f}")

    print("\n=== RECENT AI ATTRIBUTIONS (last 20 with outcomes) ===")
    c.execute("""SELECT ai_system, symbol, action, confidence, weight, 
        eventual_pnl, outcome_recorded, timestamp
        FROM ai_attribution WHERE outcome_recorded=1
        ORDER BY rowid DESC LIMIT 20""")
    for row in c.fetchall():
        print(f"  {row[7][:16]} | {row[0]:20s} | {row[1]:8s} | {row[2]:4s} | "
              f"conf={row[3]:.3f} | w={row[4]:.3f} | pnl=${row[5] or 0:.4f}")

    print("\n=== UNDERPERFORMER TRACKING ===")
    c.execute("""SELECT symbol, 
        COUNT(*) as trades,
        SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
        AVG(profit_loss) as avg_pnl
        FROM trade_history
        GROUP BY symbol ORDER BY avg_pnl ASC LIMIT 15""")
    for row in c.fetchall():
        sym, trades, wins, avg_pnl = row
        wins = wins or 0
        wr = (wins / trades * 100) if trades > 0 else 0
        print(f"  {sym}: {trades} trades, {wins}W, WR={wr:.0f}%, avg_pnl=${avg_pnl or 0:.4f}")

    conn.close()

if __name__ == '__main__':
    main()
