#!/usr/bin/env python3
"""Quick system verification script"""
import sqlite3
import sys
from pathlib import Path

print("=" * 80)
print("PROMETHEUS SYSTEM VERIFICATION")
print("=" * 80)

# Database Check
try:
    conn = sqlite3.connect('prometheus_learning.db')
    cursor = conn.cursor()
    
    # Tables
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name')
    tables = [row[0] for row in cursor.fetchall()]
    print(f"\n✅ Database: {len(tables)} tables")
    
    # Guardian State
    cursor.execute('SELECT high_water_mark, current_equity, current_drawdown_pct FROM guardian_state ORDER BY id DESC LIMIT 1')
    gstate = cursor.fetchone()
    if gstate:
        print(f"✅ Guardian: HWM=${gstate[0]:.2f}, Equity=${gstate[1]:.2f}, DD={gstate[2]:.2f}%")
    else:
        print("⚠️  Guardian: Not initialized")
    
    # Trade History
    cursor.execute('SELECT COUNT(*) FROM trade_history')
    total_trades = cursor.fetchone()[0]
    print(f"✅ Trade History: {total_trades} total trades")
    
    # Recent exits
    cursor.execute('SELECT exit_reason, COUNT(*) FROM trade_history WHERE exit_reason IS NOT NULL GROUP BY exit_reason ORDER BY COUNT(*) DESC LIMIT 5')
    exits = cursor.fetchall()
    if exits:
        print("   Exit breakdown:")
        for reason, count in exits:
            print(f"      {reason}: {count}")
    
    # Learning Data
    cursor.execute('SELECT COUNT(*) FROM ai_signal_predictions')
    predictions = cursor.fetchone()[0]
    print(f"✅ AI Learning: {predictions} signal predictions stored")
    
    cursor.execute('SELECT COUNT(*) FROM ai_learning_outcomes')
    outcomes = cursor.fetchone()[0]
    print(f"✅ Learning Outcomes: {outcomes} trades with feedback")
    
    conn.close()
except Exception as e:
    print(f"❌ Database error: {e}")

# Configuration Check
print("\n" + "=" * 80)
print("AUDIT FIX VERIFICATION")
print("=" * 80)

try:
    with open('launch_ultimate_prometheus_LIVE_TRADING.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check min_confidence
    if "'min_confidence': 0.80" in content or "'min_confidence': 0.8," in content:
        print("✅ Min Confidence: 0.80 (80%+ trades only)")
    else:
        print("⚠️  Min Confidence: NOT at 0.80")
    
    # Check for AUDIT DISABLED markers
    if "AUDIT 2026-03 — DISABLED Quantum" in content:
        print("✅ Quantum Voter: DISABLED (was 10.1% WR)")
    else:
        print("⚠️  Quantum Voter: May still be active")
    
    if "AUDIT 2026-03 — DISABLED Agent Coordinator" in content:
        print("✅ Agent Coordinator: DISABLED (was 0% WR)")
    else:
        print("⚠️  Agent Coordinator: May still be active")
    
    # Check MarketResearcher boost
    if "mr_boost = 1.4" in content:
        print("✅ MarketResearcher: 1.4x boost (best performer)")
    else:
        print("⚠️  MarketResearcher: Boost not found")
        
except Exception as e:
    print(f"❌ Config check error: {e}")

# File System Check
print("\n" + "=" * 80)
print("CRITICAL FILES")
print("=" * 80)

critical_files = [
    'unified_production_server.py',
    'launch_ultimate_prometheus_LIVE_TRADING.py',
    'core/drawdown_guardian.py',
    'brokers/alpaca_broker.py',
    'brokers/interactive_brokers_broker.py',
    'prometheus_learning.db'
]

for file in critical_files:
    path = Path(file)
    if path.exists():
        size = path.stat().st_size
        if size > 1024*1024:
            print(f"✅ {file}: {size/(1024*1024):.1f} MB")
        elif size > 1024:
            print(f"✅ {file}: {size/1024:.1f} KB")
        else:
            print(f"✅ {file}: {size} bytes")
    else:
        print(f"❌ {file}: MISSING")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
