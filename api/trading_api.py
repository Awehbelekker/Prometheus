#!/usr/bin/env python3
"""
TRADING API ENDPOINTS
Provides trading operations and position management
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import sqlite3
import os

router = APIRouter(prefix="/api/trading", tags=["trading"])

# Database path
DB_PATH = "prometheus_trading.db"

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

@router.get("/positions")
async def get_trading_positions():
    """Get current trading positions"""
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
        raise HTTPException(status_code=500, detail=f"Error getting trading positions: {str(e)}")

@router.get("/active")
async def get_active_trades():
    """Get active trades"""
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
        
        # Get active trades (last 24 hours)
        cursor.execute("""
            SELECT * FROM trades 
            WHERE timestamp > datetime('now', '-1 day')
            ORDER BY timestamp DESC
        """)
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
            "active_trades": formatted_trades,
            "count": len(formatted_trades),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting active trades: {str(e)}")

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
        
        # Get all trades
        cursor.execute("SELECT * FROM trades ORDER BY timestamp DESC")
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

@router.get("/recent")
async def get_recent_trades():
    """Get recent trades"""
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
        
        # Get recent trades (last 10)
        cursor.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10")
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
            "recent_trades": formatted_trades,
            "count": len(formatted_trades),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recent trades: {str(e)}")

@router.get("/trades")
async def get_all_trades():
    """Get all trades"""
    return await get_trading_history()

@router.post("/execute")
async def execute_trade(request: Dict[str, Any]):
    """Execute a trade"""
    try:
        # Extract parameters from request body
        symbol = request.get("symbol")
        side = request.get("side")
        quantity = request.get("quantity")
        price = request.get("price")
        
        if not all([symbol, side, quantity, price]):
            raise HTTPException(status_code=400, detail="Missing required parameters: symbol, side, quantity, price")
        
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
        
        if side.lower() == 'buy':
            # Add or update position
            cursor.execute("""
                INSERT INTO positions (symbol, quantity, entry_price, current_price, side, status)
                VALUES (?, ?, ?, ?, 'long', 'open')
            """, (symbol, quantity, price, price))
        else:
            # Check if we have enough shares to sell
            cursor.execute("SELECT quantity FROM positions WHERE symbol = ? AND status = 'open'")
            result = cursor.fetchone()
            
            if not result or result[0] < quantity:
                raise HTTPException(status_code=400, detail="Insufficient shares to sell")
            
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
            VALUES (?, ?, ?, ?, ?)
        """, (symbol, side, quantity, price, total_value))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Executed {side} order for {quantity} shares of {symbol} at ${price}",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "total_value": total_value,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing trade: {str(e)}")

@router.get("/status")
async def get_trading_status():
    """Get trading system status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get position count
        cursor.execute("SELECT COUNT(*) FROM positions WHERE status = 'open'")
        position_count = cursor.fetchone()[0]
        
        # Get recent trade count
        cursor.execute("""
            SELECT COUNT(*) FROM trades 
            WHERE timestamp > datetime('now', '-1 day')
        """)
        recent_trades = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "success": True,
            "trading_active": True,
            "position_count": position_count,
            "recent_trades": recent_trades,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": True,
            "trading_active": True,
            "position_count": 0,
            "recent_trades": 0,
            "timestamp": datetime.now().isoformat()
        }
