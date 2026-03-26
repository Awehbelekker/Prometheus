#!/usr/bin/env python3
"""Quick audit analysis script for PROMETHEUS system"""
import sqlite3
from datetime import datetime, timedelta
import os

def main():
    print("="*70)
    print("PROMETHEUS TRADING PLATFORM - COMPREHENSIVE AUDIT")
    print("="*70)
    
    # Database Analysis
    db = sqlite3.connect('prometheus_learning.db')
    c = db.cursor()
    
    # Get all tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in c.fetchall()]
    print(f"\n📊 DATABASE TABLES ({len(tables)}):")
    for t in tables:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        count = c.fetchone()[0]
        print(f"  - {t}: {count:,} records")
    
    # Trading Performance
    print("\n" + "="*70)
    print("📈 TRADING PERFORMANCE METRICS")
    print("="*70)
    # Check column names first
    c.execute("PRAGMA table_info(trade_history)")
    columns = [col[1] for col in c.fetchall()]
    print(f"Columns: {columns}")

    # Find P/L column
    pnl_col = 'pnl' if 'pnl' in columns else ('profit_loss' if 'profit_loss' in columns else ('pl' if 'pl' in columns else None))
    if pnl_col:
        c.execute(f"SELECT COUNT(*), SUM(CASE WHEN {pnl_col} > 0 THEN 1 ELSE 0 END), SUM({pnl_col}), AVG({pnl_col}), MIN({pnl_col}), MAX({pnl_col}) FROM trade_history")
        row = c.fetchone()
        total, wins, total_pnl, avg_pnl, min_pnl, max_pnl = row
        wins = wins or 0
        total_pnl = total_pnl or 0
        avg_pnl = avg_pnl or 0
        min_pnl = min_pnl or 0
        max_pnl = max_pnl or 0
        win_rate = (wins/total*100) if total > 0 else 0
        print(f"Total Trades: {total}")
        print(f"Win Rate: {win_rate:.1f}% ({wins} wins)")
        print(f"Total P/L: ${total_pnl:.2f}")
        print(f"Avg P/L: ${avg_pnl:.4f}")
        print(f"Best Trade: ${max_pnl:.4f}")
        print(f"Worst Trade: ${min_pnl:.4f}")
    else:
        c.execute("SELECT COUNT(*) FROM trade_history")
        total = c.fetchone()[0]
        print(f"Total Trades: {total}")
        print("P/L column not found in standard names")
    
    # Last 24 hours
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    c.execute("SELECT COUNT(*), SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END), SUM(pnl) FROM trade_history WHERE timestamp > ?", (yesterday,))
    row = c.fetchone()
    recent_total, recent_wins, recent_pnl = row[0] or 0, row[1] or 0, row[2] or 0
    print(f"\nLast 24 Hours: {recent_total} trades, {recent_wins} wins, ${recent_pnl:.2f} P/L")
    
    # AI Attribution
    print("\n" + "="*70)
    print("🤖 AI ATTRIBUTION ANALYSIS")
    print("="*70)
    c.execute("SELECT COUNT(*), SUM(CASE WHEN pnl IS NOT NULL THEN 1 ELSE 0 END) FROM ai_attribution")
    total_signals, signals_with_pnl = c.fetchone()
    signals_with_pnl = signals_with_pnl or 0
    coverage = (signals_with_pnl/total_signals*100) if total_signals > 0 else 0
    print(f"Total AI Signals: {total_signals:,}")
    print(f"Signals with P/L: {signals_with_pnl:,} ({coverage:.1f}%)")
    
    # Top AI systems
    c.execute("""
        SELECT ai_system, COUNT(*) as signals,
               SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
               SUM(pnl) as total_pnl
        FROM ai_attribution WHERE pnl IS NOT NULL
        GROUP BY ai_system ORDER BY total_pnl DESC LIMIT 10
    """)
    print("\nTop AI Systems (by total P/L):")
    for row in c.fetchall():
        system, signals, wins, pnl = row
        wins = wins or 0
        pnl = pnl or 0
        wr = (wins/signals*100) if signals > 0 else 0
        print(f"  {system}: {signals} signals, {wr:.1f}% win rate, ${pnl:.2f} P/L")
    
    # Shadow trading
    print("\n" + "="*70)
    print("👥 SHADOW TRADING STATUS")
    print("="*70)
    try:
        c.execute("SELECT COUNT(*) FROM shadow_sessions")
        sessions = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM shadow_trade_history")
        shadow_trades = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM shadow_position_tracking")
        shadow_positions = c.fetchone()[0]
        print(f"Shadow Sessions: {sessions}")
        print(f"Shadow Trades: {shadow_trades}")
        print(f"Shadow Positions: {shadow_positions}")
    except Exception as e:
        print(f"Shadow tables not found: {e}")
    
    db.close()
    
    # Check broker status
    print("\n" + "="*70)
    print("🔌 BROKER CONNECTION STATUS")
    print("="*70)
    
    # Alpaca
    api_key = os.getenv('ALPACA_API_KEY', os.getenv('APCA_API_KEY_ID', ''))
    api_secret = os.getenv('ALPACA_SECRET_KEY', os.getenv('APCA_API_SECRET_KEY', ''))
    if api_key:
        print(f"✅ ALPACA: Credentials found (key: {api_key[:8]}...)")
    else:
        print("❌ ALPACA: No credentials in environment")
    
    # IB
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 4002))
        sock.close()
        if result == 0:
            print("✅ IB GATEWAY: Port 4002 is OPEN")
        else:
            print("❌ IB GATEWAY: Port 4002 is CLOSED")
    except Exception as e:
        print(f"❌ IB GATEWAY: Error checking - {e}")

if __name__ == "__main__":
    main()

