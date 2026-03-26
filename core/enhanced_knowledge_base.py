#!/usr/bin/env python3
"""
PROMETHEUS Enhanced Knowledge Base
===================================
Advanced knowledge storage and retrieval system.
Extends existing persistent_memory.py with comprehensive knowledge management.

Features:
- Pattern storage and retrieval
- Strategy performance history
- Market condition memory
- Cross-session learning
- Knowledge transfer between sessions
- Intelligent knowledge retrieval
"""

import asyncio
import logging
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np

# Import existing persistent memory
from core.persistent_memory import PersistentMemory

logger = logging.getLogger(__name__)


@dataclass
class TradingPattern:
    """Stored trading pattern"""
    pattern_id: str
    pattern_type: str
    description: str
    conditions: Dict[str, Any]
    success_rate: float
    average_return: float
    occurrences: int
    last_seen: datetime
    confidence: float


@dataclass
class StrategyPerformance:
    """Strategy performance history"""
    strategy_id: str
    strategy_name: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    average_return: float
    total_profit: float
    sharpe_ratio: float
    max_drawdown: float
    best_market_conditions: List[str]
    last_updated: datetime


@dataclass
class MarketConditionMemory:
    """Memory of market conditions and outcomes"""
    memory_id: str
    market_regime: str
    volatility_level: float
    sentiment: float
    successful_strategies: List[str]
    failed_strategies: List[str]
    key_indicators: Dict[str, float]
    timestamp: datetime


class EnhancedKnowledgeBase:
    """
    Enhanced knowledge base for cross-session learning
    Extends existing PersistentMemory
    """
    
    def __init__(self, db_path: str = "knowledge_base.db"):
        self.db_path = Path(db_path)
        
        # Use existing persistent memory for simple key-value storage
        self.persistent_memory = PersistentMemory("knowledge_memory.json")
        
        # Initialize database for structured knowledge
        self._init_database()
        
        # In-memory caches
        self.pattern_cache = {}
        self.strategy_cache = {}
        
        logger.info(f"📚 Enhanced Knowledge Base initialized: {self.db_path}")
    
    def _init_database(self):
        """Initialize SQLite database for knowledge storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trading patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                description TEXT,
                conditions TEXT,
                success_rate REAL,
                average_return REAL,
                occurrences INTEGER,
                last_seen TEXT,
                confidence REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Strategy performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                strategy_id TEXT PRIMARY KEY,
                strategy_name TEXT NOT NULL,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                win_rate REAL,
                average_return REAL,
                total_profit REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                best_market_conditions TEXT,
                last_updated TEXT
            )
        ''')
        
        # Market condition memory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_conditions (
                memory_id TEXT PRIMARY KEY,
                market_regime TEXT,
                volatility_level REAL,
                sentiment REAL,
                successful_strategies TEXT,
                failed_strategies TEXT,
                key_indicators TEXT,
                timestamp TEXT
            )
        ''')
        
        # Session knowledge table (for cross-session learning)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_knowledge (
                session_id TEXT PRIMARY KEY,
                start_time TEXT,
                end_time TEXT,
                total_trades INTEGER,
                profitable_trades INTEGER,
                total_return REAL,
                key_learnings TEXT,
                market_conditions TEXT,
                successful_patterns TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("[CHECK] Knowledge base database initialized")
    
    async def store_pattern(self, pattern: TradingPattern):
        """Store or update a trading pattern"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO trading_patterns
            (pattern_id, pattern_type, description, conditions, success_rate,
             average_return, occurrences, last_seen, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern.pattern_id,
            pattern.pattern_type,
            pattern.description,
            json.dumps(pattern.conditions),
            pattern.success_rate,
            pattern.average_return,
            pattern.occurrences,
            pattern.last_seen.isoformat(),
            pattern.confidence
        ))
        
        conn.commit()
        conn.close()
        
        # Update cache
        self.pattern_cache[pattern.pattern_id] = pattern
        
        logger.debug(f"📝 Stored pattern: {pattern.pattern_id}")
    
    async def retrieve_patterns(
        self,
        pattern_type: Optional[str] = None,
        min_success_rate: float = 0.0,
        min_occurrences: int = 0
    ) -> List[TradingPattern]:
        """Retrieve trading patterns matching criteria"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM trading_patterns
            WHERE success_rate >= ? AND occurrences >= ?
        '''
        params = [min_success_rate, min_occurrences]
        
        if pattern_type:
            query += ' AND pattern_type = ?'
            params.append(pattern_type)
        
        query += ' ORDER BY success_rate DESC, occurrences DESC'
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        patterns = []
        for row in results:
            pattern = TradingPattern(
                pattern_id=row[0],
                pattern_type=row[1],
                description=row[2],
                conditions=json.loads(row[3]),
                success_rate=row[4],
                average_return=row[5],
                occurrences=row[6],
                last_seen=datetime.fromisoformat(row[7]),
                confidence=row[8]
            )
            patterns.append(pattern)
        
        logger.debug(f"📖 Retrieved {len(patterns)} patterns")
        
        return patterns
    
    async def store_strategy_performance(self, performance: StrategyPerformance):
        """Store or update strategy performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO strategy_performance
            (strategy_id, strategy_name, total_trades, winning_trades, losing_trades,
             win_rate, average_return, total_profit, sharpe_ratio, max_drawdown,
             best_market_conditions, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            performance.strategy_id,
            performance.strategy_name,
            performance.total_trades,
            performance.winning_trades,
            performance.losing_trades,
            performance.win_rate,
            performance.average_return,
            performance.total_profit,
            performance.sharpe_ratio,
            performance.max_drawdown,
            json.dumps(performance.best_market_conditions),
            performance.last_updated.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Update cache
        self.strategy_cache[performance.strategy_id] = performance
        
        logger.debug(f"📝 Stored strategy performance: {performance.strategy_id}")
    
    async def retrieve_strategy_performance(
        self,
        strategy_id: Optional[str] = None,
        min_win_rate: float = 0.0
    ) -> List[StrategyPerformance]:
        """Retrieve strategy performance history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if strategy_id:
            query = 'SELECT * FROM strategy_performance WHERE strategy_id = ?'
            cursor.execute(query, (strategy_id,))
        else:
            query = '''
                SELECT * FROM strategy_performance
                WHERE win_rate >= ?
                ORDER BY win_rate DESC, total_profit DESC
            '''
            cursor.execute(query, (min_win_rate,))
        
        results = cursor.fetchall()
        conn.close()
        
        performances = []
        for row in results:
            perf = StrategyPerformance(
                strategy_id=row[0],
                strategy_name=row[1],
                total_trades=row[2],
                winning_trades=row[3],
                losing_trades=row[4],
                win_rate=row[5],
                average_return=row[6],
                total_profit=row[7],
                sharpe_ratio=row[8],
                max_drawdown=row[9],
                best_market_conditions=json.loads(row[10]),
                last_updated=datetime.fromisoformat(row[11])
            )
            performances.append(perf)
        
        logger.debug(f"📖 Retrieved {len(performances)} strategy performances")
        
        return performances
    
    async def store_market_condition(self, memory: MarketConditionMemory):
        """Store market condition memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO market_conditions
            (memory_id, market_regime, volatility_level, sentiment,
             successful_strategies, failed_strategies, key_indicators, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory.memory_id,
            memory.market_regime,
            memory.volatility_level,
            memory.sentiment,
            json.dumps(memory.successful_strategies),
            json.dumps(memory.failed_strategies),
            json.dumps(memory.key_indicators),
            memory.timestamp.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"📝 Stored market condition memory: {memory.memory_id}")
    
    async def retrieve_similar_market_conditions(
        self,
        current_regime: str,
        current_volatility: float,
        tolerance: float = 0.2
    ) -> List[MarketConditionMemory]:
        """Retrieve similar past market conditions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find similar conditions
        query = '''
            SELECT * FROM market_conditions
            WHERE market_regime = ?
            AND ABS(volatility_level - ?) <= ?
            ORDER BY timestamp DESC
            LIMIT 10
        '''
        
        cursor.execute(query, (current_regime, current_volatility, tolerance))
        results = cursor.fetchall()
        conn.close()
        
        memories = []
        for row in results:
            memory = MarketConditionMemory(
                memory_id=row[0],
                market_regime=row[1],
                volatility_level=row[2],
                sentiment=row[3],
                successful_strategies=json.loads(row[4]),
                failed_strategies=json.loads(row[5]),
                key_indicators=json.loads(row[6]),
                timestamp=datetime.fromisoformat(row[7])
            )
            memories.append(memory)
        
        logger.debug(f"📖 Retrieved {len(memories)} similar market conditions")
        
        return memories
    
    async def save_session_knowledge(
        self,
        session_id: str,
        session_data: Dict[str, Any]
    ):
        """Save knowledge from completed trading session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO session_knowledge
            (session_id, start_time, end_time, total_trades, profitable_trades,
             total_return, key_learnings, market_conditions, successful_patterns)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            session_data.get('start_time', datetime.now().isoformat()),
            session_data.get('end_time', datetime.now().isoformat()),
            session_data.get('total_trades', 0),
            session_data.get('profitable_trades', 0),
            session_data.get('total_return', 0.0),
            json.dumps(session_data.get('key_learnings', [])),
            json.dumps(session_data.get('market_conditions', {})),
            json.dumps(session_data.get('successful_patterns', []))
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"💾 Saved session knowledge: {session_id}")
    
    async def load_session_knowledge(
        self,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Load knowledge from previous sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM session_knowledge
            ORDER BY created_at DESC
            LIMIT ?
        '''
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in results:
            session = {
                'session_id': row[0],
                'start_time': row[1],
                'end_time': row[2],
                'total_trades': row[3],
                'profitable_trades': row[4],
                'total_return': row[5],
                'key_learnings': json.loads(row[6]),
                'market_conditions': json.loads(row[7]),
                'successful_patterns': json.loads(row[8])
            }
            sessions.append(session)
        
        logger.info(f"📖 Loaded knowledge from {len(sessions)} previous sessions")
        
        return sessions


# Global instance
_knowledge_base = None

def get_knowledge_base() -> EnhancedKnowledgeBase:
    """Get global knowledge base instance"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = EnhancedKnowledgeBase()
    return _knowledge_base

