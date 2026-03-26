#!/usr/bin/env python3
"""
Hierarchical Memory System for HRM
Implements episodic, semantic, and procedural memory for long-term learning
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class EpisodicMemory:
    """Short-term memory (days) - Specific trading episodes"""
    
    def __init__(self, db_path: str = "memory/episodic_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize episodic memory database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                context TEXT NOT NULL,
                decision TEXT NOT NULL,
                outcome TEXT,
                profit REAL,
                learning TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def store_episode(self, context: Dict, decision: Dict, outcome: Dict = None):
        """Store a trading episode"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO episodes (timestamp, context, decision, outcome, profit, learning)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            json.dumps(context),
            json.dumps(decision),
            json.dumps(outcome) if outcome else None,
            outcome.get('profit', 0) if outcome else None,
            outcome.get('learning', '') if outcome else None
        ))
        conn.commit()
        conn.close()
    
    def retrieve_recent(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """Retrieve recent episodes"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT * FROM episodes 
            WHERE timestamp > ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (cutoff, limit))
        
        episodes = []
        for row in cursor.fetchall():
            episodes.append({
                'id': row[0],
                'timestamp': row[1],
                'context': json.loads(row[2]),
                'decision': json.loads(row[3]),
                'outcome': json.loads(row[4]) if row[4] else None,
                'profit': row[5],
                'learning': row[6]
            })
        conn.close()
        return episodes
    
    def retrieve_similar(self, context: Dict, limit: int = 10) -> List[Dict]:
        """Retrieve similar episodes based on context"""
        # Simple similarity: match symbol and similar indicators
        symbol = context.get('market_data', {}).get('symbol', '')
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT * FROM episodes 
            WHERE context LIKE ?
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (f'%{symbol}%', limit))
        
        episodes = []
        for row in cursor.fetchall():
            episodes.append({
                'id': row[0],
                'timestamp': row[1],
                'context': json.loads(row[2]),
                'decision': json.loads(row[3]),
                'outcome': json.loads(row[4]) if row[4] else None
            })
        conn.close()
        return episodes


class SemanticMemory:
    """Medium-term memory (weeks) - Patterns and concepts"""
    
    def __init__(self, db_path: str = "memory/semantic_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize semantic memory database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                success_rate REAL,
                frequency INTEGER DEFAULT 1,
                last_seen TEXT,
                learned_from TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def store_pattern(self, pattern_type: str, pattern_data: Dict, success: bool):
        """Store or update a pattern"""
        conn = sqlite3.connect(self.db_path)
        
        # Check if pattern exists
        cursor = conn.execute("""
            SELECT id, frequency, success_rate FROM patterns 
            WHERE pattern_type = ? AND pattern_data = ?
        """, (pattern_type, json.dumps(pattern_data)))
        
        row = cursor.fetchone()
        if row:
            # Update existing pattern
            pattern_id, frequency, old_success_rate = row
            new_frequency = frequency + 1
            new_success_rate = ((old_success_rate * frequency) + (1.0 if success else 0.0)) / new_frequency
            
            conn.execute("""
                UPDATE patterns 
                SET frequency = ?, success_rate = ?, last_seen = ?
                WHERE id = ?
            """, (new_frequency, new_success_rate, datetime.now().isoformat(), pattern_id))
        else:
            # Insert new pattern
            conn.execute("""
                INSERT INTO patterns (pattern_type, pattern_data, success_rate, frequency, last_seen)
                VALUES (?, ?, ?, ?, ?)
            """, (
                pattern_type,
                json.dumps(pattern_data),
                1.0 if success else 0.0,
                1,
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def retrieve_patterns(self, pattern_type: str = None, min_success_rate: float = 0.6) -> List[Dict]:
        """Retrieve patterns"""
        conn = sqlite3.connect(self.db_path)
        
        if pattern_type:
            cursor = conn.execute("""
                SELECT * FROM patterns 
                WHERE pattern_type = ? AND success_rate >= ?
                ORDER BY frequency DESC, success_rate DESC
            """, (pattern_type, min_success_rate))
        else:
            cursor = conn.execute("""
                SELECT * FROM patterns 
                WHERE success_rate >= ?
                ORDER BY frequency DESC, success_rate DESC
            """, (min_success_rate,))
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                'id': row[0],
                'pattern_type': row[1],
                'pattern_data': json.loads(row[2]),
                'success_rate': row[3],
                'frequency': row[4],
                'last_seen': row[5]
            })
        conn.close()
        return patterns


class ProceduralMemory:
    """Long-term memory (months) - Strategies and procedures"""
    
    def __init__(self, db_path: str = "memory/procedural_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize procedural memory database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                strategy_data TEXT NOT NULL,
                total_trades INTEGER DEFAULT 0,
                successful_trades INTEGER DEFAULT 0,
                total_profit REAL DEFAULT 0,
                avg_profit_per_trade REAL DEFAULT 0,
                created_at TEXT,
                last_used TEXT,
                market_regimes TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def store_strategy(self, strategy_name: str, strategy_data: Dict, outcome: Dict):
        """Store or update a strategy"""
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute("""
            SELECT id, total_trades, successful_trades, total_profit FROM strategies 
            WHERE strategy_name = ?
        """, (strategy_name,))
        
        row = cursor.fetchone()
        if row:
            # Update existing strategy
            strategy_id, total_trades, successful_trades, total_profit = row
            new_total = total_trades + 1
            new_successful = successful_trades + (1 if outcome.get('success', False) else 0)
            new_profit = total_profit + outcome.get('profit', 0)
            new_avg = new_profit / new_total if new_total > 0 else 0
            
            conn.execute("""
                UPDATE strategies 
                SET total_trades = ?, successful_trades = ?, total_profit = ?,
                    avg_profit_per_trade = ?, last_used = ?
                WHERE id = ?
            """, (new_total, new_successful, new_profit, new_avg, datetime.now().isoformat(), strategy_id))
        else:
            # Insert new strategy
            profit = outcome.get('profit', 0)
            conn.execute("""
                INSERT INTO strategies (strategy_name, strategy_data, total_trades, 
                    successful_trades, total_profit, avg_profit_per_trade, created_at, last_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                strategy_name,
                json.dumps(strategy_data),
                1,
                1 if outcome.get('success', False) else 0,
                profit,
                profit,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def retrieve_best_strategies(self, limit: int = 10) -> List[Dict]:
        """Retrieve best performing strategies"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT * FROM strategies 
            WHERE total_trades >= 5
            ORDER BY avg_profit_per_trade DESC
            LIMIT ?
        """, (limit,))
        
        strategies = []
        for row in cursor.fetchall():
            total_trades = row[2] if len(row) > 2 else 0
            successful_trades = row[3] if len(row) > 3 else 0
            success_rate = successful_trades / total_trades if total_trades > 0 else 0
            strategies.append({
                'id': row[0],
                'strategy_name': row[1],
                'strategy_data': json.loads(row[2]) if len(row) > 2 and row[2] else {},
                'total_trades': total_trades,
                'successful_trades': successful_trades,
                'success_rate': success_rate,
                'total_profit': row[4] if len(row) > 4 else 0,
                'avg_profit_per_trade': row[5] if len(row) > 5 else 0
            })
        conn.close()
        return strategies


class HierarchicalMemorySystem:
    """
    Complete hierarchical memory system
    Combines episodic, semantic, and procedural memory
    """
    
    def __init__(self):
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.procedural = ProceduralMemory()
    
    def remember_decision(self, context: Dict, decision: Dict, outcome: Dict = None):
        """Store decision in all relevant memory systems"""
        # Clean decision for JSON serialization
        clean_decision = {
            'action': decision.get('action'),
            'confidence': decision.get('confidence'),
            'position_size': decision.get('position_size')
        }
        
        # Episodic: Store the episode
        self.episodic.store_episode(context, clean_decision, outcome)
        
        # Semantic: Extract and store patterns
        if outcome:
            pattern = self._extract_pattern(context, decision, outcome)
            if pattern:
                self.semantic.store_pattern(
                    pattern['type'],
                    pattern['data'],
                    outcome.get('success', False)
                )
        
        # Procedural: Store strategy
        if outcome:
            strategy_name = self._extract_strategy_name(clean_decision)
            self.procedural.store_strategy(strategy_name, clean_decision, outcome)
    
    def recall_for_context(self, context: Dict) -> Dict[str, Any]:
        """Recall relevant memories for current context"""
        return {
            'episodic': self.episodic.retrieve_similar(context, limit=5),
            'semantic': self.semantic.retrieve_patterns(min_success_rate=0.6),
            'procedural': self.procedural.retrieve_best_strategies(limit=5)
        }
    
    def _extract_pattern(self, context: Dict, decision: Dict, outcome: Dict) -> Optional[Dict]:
        """Extract pattern from context and decision"""
        market_data = context.get('market_data', {})
        indicators = market_data.get('indicators', {})
        
        if not indicators:
            return None
        
        # Extract key indicators
        pattern_data = {
            'rsi_range': self._categorize_rsi(indicators.get('rsi', 50)),
            'macd_direction': 'positive' if indicators.get('macd', 0) > 0 else 'negative',
            'action': decision.get('action', 'HOLD')
        }
        
        return {
            'type': 'indicator_pattern',
            'data': pattern_data
        }
    
    def _categorize_rsi(self, rsi: float) -> str:
        """Categorize RSI value"""
        if rsi > 70:
            return 'overbought'
        elif rsi < 30:
            return 'oversold'
        else:
            return 'neutral'
    
    def _extract_strategy_name(self, decision: Dict) -> str:
        """Extract strategy name from decision"""
        action = decision.get('action', 'HOLD')
        confidence = decision.get('confidence', 0.0)
        
        if confidence > 0.8:
            return f"{action}_high_confidence"
        elif confidence > 0.5:
            return f"{action}_medium_confidence"
        else:
            return f"{action}_low_confidence"

