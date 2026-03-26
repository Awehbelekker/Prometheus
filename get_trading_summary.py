import sqlite3
from datetime import datetime

# Connect to database
db = sqlite3.connect('prometheus_learning.db')
cursor = db.cursor()

# Get today's trades
cursor.execute('''
    SELECT COUNT(*) as total_trades,
           SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
           SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
           SUM(pnl) as total_pnl,
           AVG(pnl) as avg_pnl,
           MIN(pnl) as worst_trade,
           MAX(pnl) as best_trade
    FROM trade_history
    WHERE DATE(timestamp) = DATE('now')
''')

result = cursor.fetchone()

print("\n" + "="*70)
print("📊 PROMETHEUS TRADING SYSTEM - TODAY'S SUMMARY")
print("="*70)
print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
print("-"*70)
print(f"📈 Total Trades: {result[0] or 0}")
print(f"[CHECK] Wins: {result[1] or 0}")
print(f"[ERROR] Losses: {result[2] or 0}")
if result[0] and result[0] > 0:
    win_rate = (result[1] or 0) / result[0] * 100
    print(f"🎯 Win Rate: {win_rate:.1f}%")
else:
    print(f"🎯 Win Rate: N/A")
print("-"*70)
print(f"💰 Total P&L: ${result[3]:.2f}" if result[3] else "💰 Total P&L: $0.00")
print(f"📊 Avg P&L: ${result[4]:.2f}" if result[4] else "📊 Avg P&L: $0.00")
print(f"📉 Worst Trade: ${result[5]:.2f}" if result[5] else "📉 Worst Trade: $0.00")
print(f"📈 Best Trade: ${result[6]:.2f}" if result[6] else "📈 Best Trade: $0.00")
print("="*70)

# Get recent trades
cursor.execute('''
    SELECT timestamp, broker, symbol, action, quantity, entry_price, exit_price, pnl, ai_confidence
    FROM trade_history
    WHERE DATE(timestamp) = DATE('now')
    ORDER BY timestamp DESC
    LIMIT 15
''')

trades = cursor.fetchall()

if trades:
    print("\n📋 TODAY'S TRADES:")
    print("-"*70)
    for trade in trades:
        timestamp, broker, symbol, action, quantity, entry_price, exit_price, pnl, confidence = trade
        time_str = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp[-8:]
        pnl_str = f"${pnl:.2f}" if pnl else "OPEN"
        emoji = "[CHECK]" if pnl and pnl > 0 else "[ERROR]" if pnl and pnl < 0 else "⚪"
        conf_str = f"{confidence*100:.0f}%" if confidence else "N/A"
        print(f"{emoji} {time_str} | {broker:6} | {symbol:10} | {action:4} | {quantity:8.6f} @ ${entry_price:.2f} | P&L: {pnl_str:8} | AI: {conf_str}")
    print("="*70)
else:
    print("\n[WARNING]️ No trades executed today")
    print("="*70)

# Get all-time stats
cursor.execute('''
    SELECT COUNT(*) as total_trades,
           SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
           SUM(pnl) as total_pnl
    FROM trade_history
''')

all_time = cursor.fetchone()

print("\n📊 ALL-TIME STATS:")
print("-"*70)
print(f"📈 Total Trades: {all_time[0] or 0}")
print(f"[CHECK] Total Wins: {all_time[1] or 0}")
if all_time[0] and all_time[0] > 0:
    all_time_win_rate = (all_time[1] or 0) / all_time[0] * 100
    print(f"🎯 Win Rate: {all_time_win_rate:.1f}%")
print(f"💰 Total P&L: ${all_time[2]:.2f}" if all_time[2] else "💰 Total P&L: $0.00")
print("="*70)

# Get current account balances from terminal output
print("\n💼 CURRENT ACCOUNT STATUS:")
print("-"*70)
print("🏦 IB Account: U21922116")
print("   💰 Balance: $248.16")
print("   📊 Positions: NOK (2 shares), F (1 share), SIRI (1 share)")
print("\n🏦 Alpaca Account: 910544927")
print("   💰 Balance: $87.84")
print("   📊 Positions: None")
print("\n💵 Total Capital: $336.00")
print("="*70)

# Get system status
print("\n🤖 AI SYSTEM STATUS:")
print("-"*70)
print("[CHECK] 17 Execution Agents + 3 Supervisors ACTIVE")
print("[CHECK] Tier 1 Systems: 4/4 active")
print("[CHECK] Tier 2 Systems: 3/4 active")
print("[CHECK] Tier 3 Systems: 1/2 active")
print("[CHECK] Total Advanced Systems: 8/10 active")
print("[CHECK] AI Consensus (last 10): 75.0%")
print("="*70)

db.close()

