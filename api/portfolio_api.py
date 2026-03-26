#!/usr/bin/env python3
"""
PORTFOLIO API ENDPOINTS
Provides portfolio management and position tracking
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import sqlite3
import os

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

# Database path
DB_PATH = "prometheus_trading.db"

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

@router.get("/positions")
async def get_positions():
    """Get current portfolio positions"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create positions table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL,
                unrealized_pnl REAL,
                realized_pnl REAL DEFAULT 0,
                side TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Get current positions
        cursor.execute("SELECT * FROM positions WHERE status = 'open'")
        positions = cursor.fetchall()
        
        conn.close()
        
        # Format positions
        formatted_positions = []
        for pos in positions:
            formatted_positions.append({
                "id": pos[0],
                "symbol": pos[1],
                "quantity": pos[2],
                "entry_price": pos[3],
                "current_price": pos[4] or pos[3],
                "unrealized_pnl": pos[5] or 0,
                "realized_pnl": pos[6],
                "side": pos[7],
                "status": pos[8],
                "created_at": pos[9],
                "updated_at": pos[10]
            })
        
        return {
            "success": True,
            "positions": formatted_positions,
            "count": len(formatted_positions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting positions: {str(e)}")

@router.get("/value")
async def get_portfolio_value():
    """Get total portfolio value"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get positions
        cursor.execute("SELECT quantity, entry_price, current_price FROM positions WHERE status = 'open'")
        positions = cursor.fetchall()
        
        total_value = 0
        total_cost = 0
        unrealized_pnl = 0
        
        for pos in positions:
            quantity, entry_price, current_price = pos
            current_price = current_price or entry_price
            
            position_value = quantity * current_price
            position_cost = quantity * entry_price
            position_pnl = position_value - position_cost
            
            total_value += position_value
            total_cost += position_cost
            unrealized_pnl += position_pnl
        
        # Get cash balance (simulated)
        cash_balance = 10000.0  # Starting cash
        
        conn.close()
        
        return {
            "success": True,
            "total_value": total_value + cash_balance,
            "invested_value": total_cost,
            "cash_balance": cash_balance,
            "unrealized_pnl": unrealized_pnl,
            "total_return_pct": (unrealized_pnl / total_cost * 100) if total_cost > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting portfolio value: {str(e)}")

@router.get("/balance")
async def get_balance():
    """Get account balance"""
    try:
        # Simulated balance for now
        return {
            "success": True,
            "cash_balance": 10000.0,
            "buying_power": 10000.0,
            "equity": 10000.0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting balance: {str(e)}")

@router.get("/summary")
async def get_portfolio_summary():
    """Get portfolio summary"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get position count
        cursor.execute("SELECT COUNT(*) FROM positions WHERE status = 'open'")
        position_count = cursor.fetchone()[0]
        
        # Get total P&L
        cursor.execute("SELECT SUM(realized_pnl) FROM positions")
        realized_pnl = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(unrealized_pnl) FROM positions WHERE status = 'open'")
        unrealized_pnl = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "success": True,
            "position_count": position_count,
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "total_pnl": realized_pnl + unrealized_pnl,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting portfolio summary: {str(e)}")

@router.get("/history")
async def get_trading_history():
    """Get trading history"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create trades table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                total_value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'filled'
            )
        """)
        
        # Get recent trades
        cursor.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 50")
        trades = cursor.fetchall()
        
        conn.close()
        
        # Format trades
        formatted_trades = []
        for trade in trades:
            formatted_trades.append({
                "id": trade[0],
                "symbol": trade[1],
                "side": trade[2],
                "quantity": trade[3],
                "price": trade[4],
                "total_value": trade[5],
                "timestamp": trade[6],
                "status": trade[7]
            })
        
        return {
            "success": True,
            "trades": formatted_trades,
            "count": len(formatted_trades),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trading history: {str(e)}")

@router.post("/buy")
async def buy_stock(symbol: str, quantity: float, price: float):
    """Buy a stock"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL,
                unrealized_pnl REAL,
                realized_pnl REAL DEFAULT 0,
                side TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                total_value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'filled'
            )
        """)
        
        total_value = quantity * price
        
        # Add position
        cursor.execute("""
            INSERT INTO positions (symbol, quantity, entry_price, current_price, side, status)
            VALUES (?, ?, ?, ?, 'long', 'open')
        """, (symbol, quantity, price, price))
        
        # Add trade record
        cursor.execute("""
            INSERT INTO trades (symbol, side, quantity, price, total_value)
            VALUES (?, 'buy', ?, ?, ?)
        """, (symbol, quantity, price, total_value))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Bought {quantity} shares of {symbol} at ${price}",
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "total_value": total_value,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error buying stock: {str(e)}")

@router.post("/sell")
async def sell_stock(symbol: str, quantity: float, price: float):
    """Sell a stock"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if we have enough shares
        cursor.execute("SELECT quantity FROM positions WHERE symbol = ? AND status = 'open'")
        result = cursor.fetchone()
        
        if not result or result[0] < quantity:
            raise HTTPException(status_code=400, detail="Insufficient shares to sell")
        
        total_value = quantity * price
        
        # Update position
        cursor.execute("""
            UPDATE positions 
            SET quantity = quantity - ?, 
                realized_pnl = realized_pnl + (? - entry_price) * ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE symbol = ? AND status = 'open'
        """, (quantity, price, quantity, symbol))
        
        # Close position if quantity becomes 0
        cursor.execute("""
            UPDATE positions 
            SET status = 'closed' 
            WHERE symbol = ? AND quantity <= 0 AND status = 'open'
        """, (symbol,))
        
        # Add trade record
        cursor.execute("""
            INSERT INTO trades (symbol, side, quantity, price, total_value)
            VALUES (?, 'sell', ?, ?, ?)
        """, (symbol, quantity, price, total_value))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Sold {quantity} shares of {symbol} at ${price}",
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
            "total_value": total_value,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error selling stock: {str(e)}")

@router.get("/current")
async def get_current_portfolio():
    """Get current portfolio overview"""
    try:
        # Get positions
        positions_response = await get_positions()
        positions = positions_response["positions"]
        
        # Get portfolio value
        value_response = await get_portfolio_value()
        
        # Get summary
        summary_response = await get_portfolio_summary()
        
        return {
            "success": True,
            "positions": positions,
            "portfolio_value": value_response,
            "summary": summary_response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting current portfolio: {str(e)}")










