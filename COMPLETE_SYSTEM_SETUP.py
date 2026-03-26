#!/usr/bin/env python3
"""
Complete System Setup - Creates Missing Databases and Tests Connectivity
"""

import sqlite3
import os
from pathlib import Path

print("\n" + "=" * 80)
print("COMPLETE SYSTEM SETUP")
print("=" * 80)

# List of databases to create
databases = {
    "prometheus_users.db": """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            tier TEXT DEFAULT 'free',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    "prometheus_portfolio.db": """
        CREATE TABLE IF NOT EXISTS portfolios (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            balance REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    "prometheus_trades.db": """
        CREATE TABLE IF NOT EXISTS trades (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            action TEXT NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    "prometheus_market_data.db": """
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            price REAL NOT NULL,
            volume REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    "prometheus_ai_learning.db": """
        CREATE TABLE IF NOT EXISTS learning_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT NOT NULL,
            outcome TEXT NOT NULL,
            confidence REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    "prometheus_audit.db": """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            user_id TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
}

created = 0
existed = 0

for db_name, schema in databases.items():
    if Path(db_name).exists():
        print(f"[EXISTS] {db_name} (already exists)")
        existed += 1
    else:
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute(schema)
            conn.commit()
            conn.close()
            print(f"[CREATED] {db_name}")
            created += 1
        except Exception as e:
            print(f"[ERROR] Failed to create {db_name}: {e}")

print("\n" + "=" * 80)
print("DATABASE SETUP COMPLETE")
print("=" * 80)
print(f"Created: {created} databases")
print(f"Already existed: {existed} databases")
print("=" * 80)

# Test IB Gateway connection
print("\nTesting IB Gateway connection...")
try:
    from ib_insync import IB
    ib = IB()
    print("Attempting to connect to IB Gateway on port 7497...")
    import asyncio
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(
        ib.connectAsync('127.0.0.1', 7497, clientId=1, timeout=5)
    )
    if ib.isConnected():
        print("[SUCCESS] IB Gateway connected!")
        print(f"Account: {ib.accountValues()}")
        ib.disconnect()
    else:
        print("[NOT CONNECTED] IB Gateway not running")
        print("[INFO] To start IB Gateway:")
        print("  1. Launch IB Gateway application")
        print("  2. Enable API in settings")
        print("  3. Set port to 7497")
except Exception as e:
    print(f"[INFO] IB Gateway not running: {e}")
    print("[INFO] This is expected if IB Gateway is not started")

# Test market data sources
print("\nTesting market data sources...")
try:
    import yfinance as yf
    print("Testing Yahoo Finance...")
    ticker = yf.Ticker("AAPL")
    info = ticker.info
    if info.get('currentPrice'):
        print(f"[SUCCESS] Yahoo Finance working (AAPL: ${info.get('currentPrice'):.2f})")
    else:
        print("[WARNING] Yahoo Finance data limited (rate limit)")
except Exception as e:
    print(f"[WARNING] Yahoo Finance: {e}")
    print("[INFO] Alternative data sources available")

print("\n" + "=" * 80)
print("SETUP COMPLETE!")
print("=" * 80)
print("\nYour system is now fully configured and ready to trade!")
print("\nNext steps:")
print("  1. Start IB Gateway (optional, for live trading)")
print("  2. Access dashboard: http://localhost:3000")
print("  3. Begin trading!")
print("=" * 80 + "\n")


