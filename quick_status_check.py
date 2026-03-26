"""Quick status check for PROMETHEUS trading system"""
import sqlite3
import glob
import os
from datetime import datetime

print("\n" + "="*80)
print("🔍 PROMETHEUS TRADING SYSTEM - QUICK STATUS CHECK")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# 1. Check for recent database
print("\n📊 DATABASE STATUS:")
dbs = glob.glob('internal_paper_session_*.db')
if dbs:
    latest = max(dbs, key=os.path.getctime)
    db_time = datetime.fromtimestamp(os.path.getctime(latest))
    age_hours = (datetime.now() - db_time).total_seconds() / 3600
    print(f"Latest DB: {latest}")
    print(f"Created: {db_time.strftime('%Y-%m-%d %H:%M:%S')} ({age_hours:.1f} hours ago)")
    
    try:
        conn = sqlite3.connect(latest)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trades")
        total = cursor.fetchone()[0]
        print(f"Total Trades: {total}")
        
        cursor.execute("SELECT timestamp, symbol, action FROM trades ORDER BY timestamp DESC LIMIT 1")
        last_trade = cursor.fetchone()
        if last_trade:
            print(f"Last Trade: {last_trade[0]} - {last_trade[2]} {last_trade[1]}")
        conn.close()
    except Exception as e:
        print(f"Error reading DB: {e}")
else:
    print("[ERROR] No session databases found")

# 2. Check IB Gateway connection
print("\n🔌 IB GATEWAY STATUS:")
import subprocess
result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
if '7497' in result.stdout:
    print("[CHECK] IB Gateway port 7497 is active")
else:
    print("[ERROR] IB Gateway port 7497 not found")

if '4001' in result.stdout:
    print("[CHECK] Connection to Alpaca (port 4001) detected")

# 3. Check service status
print("\n🔧 SERVICE STATUS:")
result = subprocess.run(['sc', 'query', 'PrometheusTrading'], capture_output=True, text=True)
if 'RUNNING' in result.stdout:
    print("[CHECK] PrometheusTrading service is RUNNING")
elif 'STOPPED' in result.stdout:
    print("[ERROR] PrometheusTrading service is STOPPED")
else:
    print("[WARNING]️  Service status unknown")

# 4. Check current session
print("\n📈 CURRENT TRADING SESSION:")
try:
    from core.market_hours_utils import get_eastern_time, is_ib_trading_hours, is_overnight_session
    et = get_eastern_time()
    print(f"Eastern Time: {et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"IB Trading Available: {'YES [CHECK]' if is_ib_trading_hours() else 'NO [ERROR]'}")
    print(f"Overnight Session: {'YES 🌙' if is_overnight_session() else 'NO'}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80)

