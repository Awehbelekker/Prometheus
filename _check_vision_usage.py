import sqlite3

c = sqlite3.connect('prometheus_learning.db')

# Vision in trade reasoning
r1 = c.execute("SELECT COUNT(*) FROM trade_history WHERE reasoning LIKE '%ChartVision%' OR reasoning LIKE '%vision%' OR reasoning LIKE '%Visual%'").fetchone()[0]
r2 = c.execute("SELECT COUNT(*) FROM trade_history").fetchone()[0]
print(f"Trades with Vision in reasoning: {r1}/{r2}")

# Vision in signal_predictions ai_components
r3 = c.execute("SELECT COUNT(*) FROM signal_predictions WHERE ai_components LIKE '%ChartVision%' OR ai_components LIKE '%Vision%' OR ai_components LIKE '%Visual%'").fetchone()[0]
r4 = c.execute("SELECT COUNT(*) FROM signal_predictions").fetchone()[0]
print(f"Signals with Vision component: {r3}/{r4}")

# Sample reasoning with vision
rows = c.execute("SELECT reasoning FROM trade_history WHERE reasoning LIKE '%ChartVision%' OR reasoning LIKE '%Vision%' LIMIT 5").fetchall()
if rows:
    print("\nSample vision reasoning:")
    for r in rows:
        print(f"  {r[0][:150]}")
else:
    print("\nNo trades have ChartVision in reasoning.")

# Check ai_components distribution
rows2 = c.execute("SELECT ai_components FROM signal_predictions WHERE ai_components IS NOT NULL AND ai_components != '' LIMIT 10").fetchall()
print("\nSample ai_components:")
for r in rows2[:5]:
    print(f"  {r[0][:200]}")

# Check if llava was used recently (look in reasoning for pattern names)
rows3 = c.execute("SELECT reasoning FROM signal_predictions WHERE reasoning LIKE '%pattern%' OR reasoning LIKE '%candlestick%' OR reasoning LIKE '%trend%' ORDER BY timestamp DESC LIMIT 5").fetchall()
if rows3:
    print("\nRecent pattern-related signals:")
    for r in rows3:
        print(f"  {r[0][:150]}")

# Check chart_vision system_health from any log tables
try:
    tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"\nAll tables: {[t[0] for t in tables]}")
except:
    pass

c.close()
