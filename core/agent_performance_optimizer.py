#!/usr/bin/env python3
"""
PROMETHEUS Agent Performance Optimizer
=======================================
Tracks and optimizes agent performance over time.
Integrates with existing hierarchical_agent_coordinator.py.

Features:
- Track agent decisions and outcomes
- Calculate performance metrics per agent
- Optimize agent selection based on performance
- Adapt agent weights dynamically
- Store performance history in database
"""

import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
import pandas as pd

# Import existing systems
from core.hierarchical_agent_coordinator import (
    AgentType,
    AgentPerformance,
    TradingDecision
)

logger = logging.getLogger(__name__)


@dataclass
class AgentDecisionRecord:
    """Record of an agent's decision and outcome"""
    record_id: str
    agent_id: str
    agent_type: str
    symbol: str
    action: str
    quantity: int
    entry_price: float
    exit_price: Optional[float]
    confidence: float
    expected_return: float
    actual_return: Optional[float]
    risk_score: float
    decision_time: datetime
    exit_time: Optional[datetime]
    outcome: Optional[str]  # 'success', 'failure', 'pending'
    reasoning: str


class AgentPerformanceOptimizer:
    """
    Tracks and optimizes agent performance
    """
    
    def __init__(self, db_path: str = "agent_performance.db"):
        self.db_path = Path(db_path)
        self.agent_weights = {}
        self.agent_metrics = {}
        
        # Initialize database
        self._init_database()
        
        # Load historical performance
        self._load_agent_metrics()
        
        logger.info(f"📈 Agent Performance Optimizer initialized: {self.db_path}")
    
    def _init_database(self):
        """Initialize SQLite database for agent performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Agent decisions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_decisions (
                record_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                quantity INTEGER,
                entry_price REAL,
                exit_price REAL,
                confidence REAL,
                expected_return REAL,
                actual_return REAL,
                risk_score REAL,
                decision_time TEXT NOT NULL,
                exit_time TEXT,
                outcome TEXT,
                reasoning TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Agent performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_metrics (
                agent_id TEXT PRIMARY KEY,
                agent_type TEXT NOT NULL,
                total_decisions INTEGER DEFAULT 0,
                successful_decisions INTEGER DEFAULT 0,
                failed_decisions INTEGER DEFAULT 0,
                pending_decisions INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0.0,
                average_return REAL DEFAULT 0.0,
                risk_adjusted_return REAL DEFAULT 0.0,
                confidence_accuracy REAL DEFAULT 0.0,
                total_profit REAL DEFAULT 0.0,
                total_loss REAL DEFAULT 0.0,
                sharpe_ratio REAL DEFAULT 0.0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indices
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_agent_decisions 
            ON agent_decisions(agent_id, decision_time)
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("[CHECK] Agent performance database initialized")
    
    async def record_decision(
        self,
        decision: TradingDecision
    ) -> str:
        """
        Record an agent's trading decision
        
        Args:
            decision: Trading decision from agent
        
        Returns:
            Record ID
        """
        record_id = f"{decision.agent_id}_{decision.symbol}_{datetime.now().timestamp()}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO agent_decisions
            (record_id, agent_id, agent_type, symbol, action, quantity, 
             entry_price, confidence, expected_return, risk_score, 
             decision_time, outcome, reasoning)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record_id,
            decision.agent_id,
            decision.agent_type.value,
            decision.symbol,
            decision.action,
            decision.quantity,
            decision.price,
            decision.confidence,
            decision.expected_return,
            decision.risk_score,
            datetime.now().isoformat(),
            'pending',
            decision.reasoning
        ))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"📝 Recorded decision: {record_id}")
        
        return record_id
    
    async def update_decision_outcome(
        self,
        record_id: str,
        exit_price: float,
        actual_return: float,
        outcome: str
    ):
        """
        Update decision outcome after trade completion
        
        Args:
            record_id: Decision record ID
            exit_price: Exit price
            actual_return: Actual return achieved
            outcome: 'success' or 'failure'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE agent_decisions
            SET exit_price = ?,
                actual_return = ?,
                exit_time = ?,
                outcome = ?
            WHERE record_id = ?
        ''', (
            exit_price,
            actual_return,
            datetime.now().isoformat(),
            outcome,
            record_id
        ))
        
        conn.commit()
        conn.close()
        
        # Update agent metrics
        await self._update_agent_metrics(record_id)
        
        logger.debug(f"[CHECK] Updated decision outcome: {record_id} -> {outcome}")
    
    async def _update_agent_metrics(self, record_id: str):
        """Update agent performance metrics after decision outcome"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get decision details
        cursor.execute('''
            SELECT agent_id, agent_type, outcome, actual_return
            FROM agent_decisions
            WHERE record_id = ?
        ''', (record_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return
        
        agent_id, agent_type, outcome, actual_return = result
        
        # Calculate metrics for this agent
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN outcome = 'failure' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN outcome = 'pending' THEN 1 ELSE 0 END) as pending,
                AVG(CASE WHEN outcome != 'pending' THEN actual_return ELSE NULL END) as avg_return,
                SUM(CASE WHEN actual_return > 0 THEN actual_return ELSE 0 END) as total_profit,
                SUM(CASE WHEN actual_return < 0 THEN actual_return ELSE 0 END) as total_loss
            FROM agent_decisions
            WHERE agent_id = ?
        ''', (agent_id,))
        
        metrics = cursor.fetchone()
        total, successful, failed, pending, avg_return, total_profit, total_loss = metrics
        
        # Calculate derived metrics
        win_rate = successful / (successful + failed) if (successful + failed) > 0 else 0.0
        avg_return = avg_return or 0.0
        
        # Update or insert metrics
        cursor.execute('''
            INSERT OR REPLACE INTO agent_metrics
            (agent_id, agent_type, total_decisions, successful_decisions, 
             failed_decisions, pending_decisions, win_rate, average_return,
             total_profit, total_loss, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            agent_id,
            agent_type,
            total,
            successful,
            failed,
            pending,
            win_rate,
            avg_return,
            total_profit or 0.0,
            total_loss or 0.0,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"📊 Updated metrics for agent: {agent_id}")
    
    def _load_agent_metrics(self):
        """Load agent metrics from database"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT agent_id, agent_type, total_decisions, successful_decisions,
                   win_rate, average_return, risk_adjusted_return
            FROM agent_metrics
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            for _, row in df.iterrows():
                self.agent_metrics[row['agent_id']] = {
                    'agent_type': row['agent_type'],
                    'total_decisions': row['total_decisions'],
                    'successful_decisions': row['successful_decisions'],
                    'win_rate': row['win_rate'],
                    'average_return': row['average_return'],
                    'risk_adjusted_return': row['risk_adjusted_return']
                }
            
            logger.info(f"📊 Loaded metrics for {len(self.agent_metrics)} agents")
    
    async def get_agent_performance(
        self,
        agent_id: str
    ) -> Optional[AgentPerformance]:
        """Get performance metrics for specific agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM agent_metrics WHERE agent_id = ?
        ''', (agent_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        # Convert to AgentPerformance dataclass
        return AgentPerformance(
            agent_id=result[0],
            agent_type=AgentType(result[1]),
            total_decisions=result[2],
            successful_decisions=result[3],
            average_return=result[6],
            risk_adjusted_return=result[7],
            confidence_accuracy=result[8],
            last_updated=datetime.fromisoformat(result[12])
        )
    
    async def get_top_agents(
        self,
        n: int = 5,
        metric: str = 'win_rate'
    ) -> List[Dict[str, Any]]:
        """Get top performing agents"""
        conn = sqlite3.connect(self.db_path)
        
        query = f'''
            SELECT agent_id, agent_type, total_decisions, win_rate, 
                   average_return, risk_adjusted_return
            FROM agent_metrics
            WHERE total_decisions >= 10
            ORDER BY {metric} DESC
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(n,))
        conn.close()
        
        return df.to_dict('records')
    
    async def optimize_agent_weights(self) -> Dict[str, float]:
        """
        Optimize agent weights based on performance
        
        Returns:
            Dictionary of agent_id -> weight
        """
        logger.info("🎯 Optimizing agent weights...")
        
        # Get all agent metrics
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT agent_id, win_rate, average_return, total_decisions
            FROM agent_metrics
            WHERE total_decisions >= 5
        ''', conn)
        conn.close()
        
        if df.empty:
            logger.warning("[WARNING]️ No agent performance data available")
            return {}
        
        # Calculate weights based on win rate and average return
        df['score'] = df['win_rate'] * 0.6 + (df['average_return'] * 10) * 0.4
        df['weight'] = df['score'] / df['score'].sum()
        
        # Convert to dictionary
        weights = dict(zip(df['agent_id'], df['weight']))
        
        self.agent_weights = weights
        
        logger.info(f"[CHECK] Optimized weights for {len(weights)} agents")
        
        return weights


# Global instance
_performance_optimizer = None

def get_performance_optimizer() -> AgentPerformanceOptimizer:
    """Get global performance optimizer instance"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = AgentPerformanceOptimizer()
    return _performance_optimizer

