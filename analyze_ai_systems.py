"""
PROMETHEUS AI System Performance Analysis
"""
import sqlite3

db = sqlite3.connect('prometheus_learning.db')
c = db.cursor()

print("=" * 70)
print("AI SYSTEM PERFORMANCE ANALYSIS")
print("=" * 70)

# 1. AI Attribution Performance
print("\n🤖 AI SYSTEM PERFORMANCE (from ai_attribution table)")
print("-" * 60)
c.execute('''
    SELECT ai_system, 
           COUNT(*) as signals, 
           SUM(CASE WHEN eventual_pnl > 0 THEN 1 ELSE 0 END) as wins,
           SUM(eventual_pnl) as total_pnl
    FROM ai_attribution 
    WHERE eventual_pnl IS NOT NULL 
    GROUP BY ai_system 
    ORDER BY total_pnl DESC
''')
rows = c.fetchall()
if rows:
    print(f"{'System':<30} {'Signals':>8} {'Wins':>6} {'Win%':>8} {'Total P/L':>12}")
    print("-" * 70)
    for r in rows:
        win_pct = (r[2]/r[1]*100) if r[1] > 0 else 0
        print(f"{r[0]:<30} {r[1]:>8} {r[2]:>6} {win_pct:>7.1f}% ${r[3]:>11.4f}")
else:
    print("No AI attribution data with P/L recorded")

# 2. Check ai_system_metrics table
print("\n📊 AI SYSTEM METRICS TABLE")
print("-" * 60)
c.execute('SELECT * FROM ai_system_metrics ORDER BY timestamp DESC LIMIT 5')
rows = c.fetchall()
c.execute('PRAGMA table_info(ai_system_metrics)')
cols = [r[1] for r in c.fetchall()]
print(f"Columns: {cols}")
print(f"Records: {len(rows)}")
if rows:
    for r in rows[:3]:
        print(r)

# 3. Check if learning is actually being applied
print("\n🔄 LEARNING APPLICATION CHECK")
print("-" * 60)

# Check trade_optimization table
c.execute('SELECT COUNT(*) FROM trade_optimization')
opt_count = c.fetchone()[0]
print(f"Trade optimization records: {opt_count}")

# Check pattern_insights table
c.execute('SELECT COUNT(*) FROM pattern_insights')
pattern_count = c.fetchone()[0]
print(f"Pattern insights records: {pattern_count}")

# 4. Check if any weights are being adjusted
print("\n⚖️ WEIGHT ADJUSTMENT CHECK")
print("-" * 60)
c.execute('''
    SELECT ai_system, AVG(vote_weight) as avg_weight, COUNT(*) as count
    FROM ai_attribution
    GROUP BY ai_system
    ORDER BY avg_weight DESC
''')
weights = c.fetchall()
if weights:
    print(f"{'System':<30} {'Avg Weight':>12} {'Count':>8}")
    print("-" * 55)
    for w in weights:
        print(f"{w[0]:<30} {w[1]:>12.4f} {w[2]:>8}")
    
    # Check if weights vary over time (sign of learning)
    unique_weights = set(w[1] for w in weights)
    if len(unique_weights) == 1:
        print("\n⚠️ WARNING: All AI systems have SAME weight - no adaptive weighting!")
    else:
        print(f"\n✅ Weights vary: {len(unique_weights)} unique values")

# 5. Critical: Are learning outputs being used?
print("\n❓ CRITICAL: ARE LEARNING OUTPUTS BEING USED IN DECISIONS?")
print("-" * 60)
print("Checking if learning systems influence trading decisions...")

# This would require code analysis - summarize findings
print("""
Based on code analysis:
- Learning systems RECORD data ✅
- Learning systems ANALYZE patterns ✅  
- Learning systems DO NOT feed back into decision weights ❌
- No get_recommendation() calls in live trading ❌
- No adaptive weight adjustment based on performance ❌

CONCLUSION: Learning systems are PASSIVE OBSERVERS, not ACTIVE PARTICIPANTS
""")

db.close()

