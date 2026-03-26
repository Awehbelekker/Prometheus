"""
📚 Embedded Knowledge Base for PROMETHEUS Trading Platform
Provides RAGFlow-like knowledge retrieval without Docker dependency.
Falls back to this when RAGFlow is unavailable.
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import sqlite3

logger = logging.getLogger(__name__)

class EmbeddedKnowledgeBase:
    """Local knowledge base for market intelligence without Docker/RAGFlow"""
    
    def __init__(self, db_path: str = "market_knowledge.db"):
        self.db_path = db_path
        self._initialize_database()
        self._populate_trading_knowledge()
        logger.info("📚 Embedded Knowledge Base initialized")
    
    def _initialize_database(self):
        """Create SQLite database for knowledge storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                keywords TEXT,
                relevance_weight REAL DEFAULT 1.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                description TEXT NOT NULL,
                bullish_signal BOOLEAN,
                confidence_boost REAL DEFAULT 0.05,
                conditions TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_regimes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                regime_name TEXT NOT NULL,
                characteristics TEXT,
                recommended_strategy TEXT,
                risk_adjustment REAL DEFAULT 1.0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _populate_trading_knowledge(self):
        """Populate knowledge base with trading intelligence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if already populated
        cursor.execute("SELECT COUNT(*) FROM market_knowledge")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Market Knowledge
        market_knowledge = [
            ("technical_analysis", "Support and Resistance", 
             "Support levels are price points where buying pressure exceeds selling pressure. Resistance levels are where selling pressure exceeds buying. Breakouts above resistance or below support often lead to significant price movements.",
             "support,resistance,breakout,price_levels", 1.2),
            ("technical_analysis", "Volume Analysis",
             "Volume confirms price movements. High volume on breakouts indicates strong conviction. Low volume rallies are often unsustainable. Volume precedes price in many cases.",
             "volume,breakout,conviction,price_action", 1.1),
            ("technical_analysis", "Momentum Indicators",
             "RSI above 70 indicates overbought, below 30 oversold. MACD crossovers signal trend changes. Divergence between price and momentum often precedes reversals.",
             "RSI,MACD,overbought,oversold,momentum,divergence", 1.15),
            ("market_psychology", "Fear and Greed",
             "Extreme fear often presents buying opportunities. Extreme greed signals potential tops. Contrarian strategies work best at sentiment extremes.",
             "fear,greed,sentiment,contrarian,psychology", 1.1),
            ("risk_management", "Position Sizing",
             "Never risk more than 1-2% of capital per trade. Scale position size based on conviction and volatility. Larger positions for higher-probability setups.",
             "position_size,risk,capital,volatility", 1.3),
            ("risk_management", "Stop Loss Strategy",
             "Place stops at technical levels, not arbitrary percentages. Trailing stops protect profits in trending markets. Never move stops against your position.",
             "stop_loss,trailing_stop,risk_management", 1.25),
        ]
        
        cursor.executemany("""
            INSERT INTO market_knowledge (category, title, content, keywords, relevance_weight)
            VALUES (?, ?, ?, ?, ?)
        """, market_knowledge)
        
        # Trading Patterns
        patterns = [
            ("Double Bottom", "reversal", "Price forms two lows at similar levels with a peak between them. Bullish reversal pattern.", True, 0.08, "two_lows,reversal,support"),
            ("Double Top", "reversal", "Price forms two highs at similar levels with a trough between them. Bearish reversal pattern.", False, 0.08, "two_highs,reversal,resistance"),
            ("Bull Flag", "continuation", "Sharp rise followed by consolidation in a downward channel. Bullish continuation pattern.", True, 0.10, "consolidation,channel,continuation"),
            ("Bear Flag", "continuation", "Sharp decline followed by consolidation in an upward channel. Bearish continuation pattern.", False, 0.10, "consolidation,channel,continuation"),
            ("Gap Up", "momentum", "Price opens significantly above previous close. Often indicates strong buying pressure.", True, 0.12, "gap,momentum,buying_pressure"),
            ("Gap Down", "momentum", "Price opens significantly below previous close. Often indicates strong selling pressure.", False, 0.12, "gap,momentum,selling_pressure"),
            ("High Volume Breakout", "breakout", "Price breaks through key level with significantly higher than average volume.", True, 0.15, "breakout,volume,conviction"),
        ]
        
        cursor.executemany("""
            INSERT INTO trading_patterns (pattern_name, pattern_type, description, bullish_signal, confidence_boost, conditions)
            VALUES (?, ?, ?, ?, ?, ?)
        """, patterns)
        
        # Market Regimes
        regimes = [
            ("Bull Market", "Sustained uptrend with higher highs and higher lows. Dips are buying opportunities.", "Buy breakouts, hold winners, tight stops", 1.0),
            ("Bear Market", "Sustained downtrend with lower highs and lower lows. Rallies are selling opportunities.", "Short rallies, quick profits, wider stops", 0.7),
            ("Sideways/Range", "Price bounded between support and resistance. Mean reversion strategies work best.", "Buy support, sell resistance, tight ranges", 0.8),
            ("High Volatility", "Large price swings in both directions. Reduce position sizes, widen stops.", "Reduce size, widen stops, quick profits", 0.6),
        ]
        
        cursor.executemany("""
            INSERT INTO market_regimes (regime_name, characteristics, recommended_strategy, risk_adjustment)
            VALUES (?, ?, ?, ?)
        """, regimes)
        
        conn.commit()
        conn.close()
        logger.info("📚 Trading knowledge populated with patterns and strategies")

    def query_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Query knowledge base for relevant insights"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Simple keyword matching (can be enhanced with embeddings)
        keywords = query.lower().split()
        results = []

        for keyword in keywords[:5]:  # Top 5 keywords
            cursor.execute("""
                SELECT title, content, category, relevance_weight
                FROM market_knowledge
                WHERE keywords LIKE ? OR title LIKE ? OR content LIKE ?
                ORDER BY relevance_weight DESC
                LIMIT ?
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit))

            for row in cursor.fetchall():
                results.append({
                    'title': row[0],
                    'content': row[1],
                    'category': row[2],
                    'relevance_score': row[3],
                    'source': 'embedded_kb'
                })

        conn.close()

        # Deduplicate and sort by relevance
        seen = set()
        unique_results = []
        for r in results:
            if r['title'] not in seen:
                seen.add(r['title'])
                unique_results.append(r)

        return unique_results[:limit]

    def get_pattern_insights(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get trading pattern insights based on market data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        insights = []

        # Check for gap patterns
        if market_data.get('gap_pct', 0) > 2:
            cursor.execute("SELECT * FROM trading_patterns WHERE pattern_name = 'Gap Up'")
            row = cursor.fetchone()
            if row:
                insights.append({
                    'pattern': row[1],
                    'description': row[3],
                    'bullish': bool(row[4]),
                    'confidence_boost': row[5]
                })
        elif market_data.get('gap_pct', 0) < -2:
            cursor.execute("SELECT * FROM trading_patterns WHERE pattern_name = 'Gap Down'")
            row = cursor.fetchone()
            if row:
                insights.append({
                    'pattern': row[1],
                    'description': row[3],
                    'bullish': bool(row[4]),
                    'confidence_boost': row[5]
                })

        # Check for high volume breakout
        if market_data.get('volume_ratio', 1) > 2 and market_data.get('price_change_pct', 0) > 1:
            cursor.execute("SELECT * FROM trading_patterns WHERE pattern_name = 'High Volume Breakout'")
            row = cursor.fetchone()
            if row:
                insights.append({
                    'pattern': row[1],
                    'description': row[3],
                    'bullish': bool(row[4]),
                    'confidence_boost': row[5]
                })

        conn.close()
        return insights

    def get_regime_recommendation(self, regime: str) -> Dict[str, Any]:
        """Get trading recommendations for current market regime"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT regime_name, characteristics, recommended_strategy, risk_adjustment
            FROM market_regimes
            WHERE regime_name LIKE ?
        """, (f"%{regime}%",))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'regime': row[0],
                'characteristics': row[1],
                'strategy': row[2],
                'risk_adjustment': row[3]
            }
        return {'regime': 'Unknown', 'risk_adjustment': 1.0}


# Global instance
_knowledge_base = None

def get_embedded_knowledge_base() -> EmbeddedKnowledgeBase:
    """Get or create the embedded knowledge base singleton"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = EmbeddedKnowledgeBase()
    return _knowledge_base

