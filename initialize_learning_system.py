#!/usr/bin/env python3
"""
Initialize AI Learning System
Creates all necessary tables for session learning and continuous improvement
"""

import sqlite3
from datetime import datetime
from pathlib import Path

def initialize_learning_system():
    """Initialize all AI learning tables and directories"""
    
    print("🚀 INITIALIZING AI LEARNING SYSTEM")
    print("=" * 60)
    
    db_path = "prometheus_trading.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. AI Learning Events Table
        print("\n📊 Creating AI learning events table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_learning_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                event_type TEXT NOT NULL,
                event_data TEXT,
                confidence REAL,
                applied_to_trading BOOLEAN DEFAULT FALSE,
                outcome TEXT,
                profit_impact REAL
            )
        """)
        print("[CHECK] ai_learning_events table created")
        
        # 2. Market Patterns Table
        print("\n📈 Creating market patterns table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT UNIQUE NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                timeframe TEXT,
                indicators TEXT,
                success_rate REAL,
                avg_profit REAL,
                occurrences INTEGER DEFAULT 1,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[CHECK] market_patterns table created")
        
        # 3. Trade Outcomes Table
        print("\n💰 Creating trade outcomes table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                trade_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                quantity REAL NOT NULL,
                pnl REAL,
                pnl_percent REAL,
                duration_seconds INTEGER,
                strategy_used TEXT,
                ai_confidence REAL,
                market_conditions TEXT,
                success BOOLEAN,
                learning_applied BOOLEAN DEFAULT FALSE
            )
        """)
        print("[CHECK] trade_outcomes table created")
        
        # 4. AI Coordination Log
        print("\n🤖 Creating AI coordination log...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_coordination_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                coordination_type TEXT NOT NULL,
                engines_involved TEXT NOT NULL,
                decision_made TEXT,
                confidence_score REAL,
                outcome TEXT,
                profit_impact REAL
            )
        """)
        print("[CHECK] ai_coordination_log table created")
        
        # 5. Oracle Predictions Table
        print("\n🔮 Creating oracle predictions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS oracle_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                prediction_type TEXT NOT NULL,
                predicted_direction TEXT,
                confidence_level REAL,
                predicted_price REAL,
                actual_price REAL,
                accuracy_score REAL,
                profit_generated REAL,
                verified BOOLEAN DEFAULT FALSE,
                verification_time DATETIME
            )
        """)
        print("[CHECK] oracle_predictions table created")
        
        # 6. User Behavior Patterns
        print("\n👤 Creating user behavior patterns table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_behavior_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                behavior_data TEXT,
                frequency INTEGER DEFAULT 1,
                success_rate REAL,
                risk_profile TEXT,
                preferred_strategies TEXT,
                avg_hold_time INTEGER,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[CHECK] user_behavior_patterns table created")
        
        # 7. Strategy Performance Tracking
        print("\n📊 Creating strategy performance table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                strategy_name TEXT NOT NULL,
                symbol TEXT,
                market_regime TEXT,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                avg_pnl_per_trade REAL,
                win_rate REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[CHECK] strategy_performance table created")
        
        # 8. Model Training History
        print("\n🧠 Creating model training history table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_training_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                model_name TEXT NOT NULL,
                model_type TEXT NOT NULL,
                training_samples INTEGER,
                validation_accuracy REAL,
                test_accuracy REAL,
                features_used TEXT,
                hyperparameters TEXT,
                performance_metrics TEXT,
                model_path TEXT,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        print("[CHECK] model_training_history table created")
        
        # 9. Session Learning Summary
        print("\n📝 Creating session learning summary table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_learning_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date DATE NOT NULL,
                session_start DATETIME,
                session_end DATETIME,
                total_trades INTEGER DEFAULT 0,
                successful_trades INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                patterns_discovered INTEGER DEFAULT 0,
                strategies_improved INTEGER DEFAULT 0,
                ai_accuracy REAL,
                key_learnings TEXT,
                improvements_for_next_session TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[CHECK] session_learning_summary table created")
        
        # 10. Continuous Improvement Metrics
        print("\n📈 Creating continuous improvement metrics table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS continuous_improvement_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                previous_value REAL,
                improvement_percent REAL,
                trend TEXT,
                category TEXT,
                notes TEXT
            )
        """)
        print("[CHECK] continuous_improvement_metrics table created")
        
        conn.commit()
        
        # Create AI models directory
        print("\n📁 Creating AI models directory...")
        models_dir = Path("ai_models")
        models_dir.mkdir(exist_ok=True)
        print(f"[CHECK] AI models directory created: {models_dir}")
        
        # Create learning data directory
        print("\n📁 Creating learning data directory...")
        learning_dir = Path("learning_data")
        learning_dir.mkdir(exist_ok=True)
        print(f"[CHECK] Learning data directory created: {learning_dir}")
        
        # Insert initial session summary for today
        print("\n📝 Creating today's session summary...")
        cursor.execute("""
            INSERT INTO session_learning_summary 
            (session_date, session_start, improvements_for_next_session)
            VALUES (?, ?, ?)
        """, (
            datetime.now().date(),
            datetime.now(),
            "System initialized - ready to learn from first trading session"
        ))
        conn.commit()
        print("[CHECK] Today's session summary created")
        
        # Verify all tables
        print("\n" + "=" * 60)
        print("🔍 VERIFYING LEARNING SYSTEM")
        print("-" * 60)
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND (
                name LIKE '%learning%' OR 
                name LIKE '%ai_%' OR 
                name LIKE '%pattern%' OR
                name LIKE '%prediction%' OR
                name LIKE '%coordination%' OR
                name LIKE '%oracle%' OR
                name LIKE '%strategy%' OR
                name LIKE '%session%' OR
                name LIKE '%improvement%' OR
                name LIKE '%behavior%' OR
                name LIKE '%model%'
            )
            ORDER BY name
        """)
        
        tables = cursor.fetchall()
        print(f"\n[CHECK] Learning tables created: {len(tables)}")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   - {table[0]}: {count} records")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 AI LEARNING SYSTEM INITIALIZED SUCCESSFULLY!")
        print("=" * 60)
        print("\n[CHECK] The system will now:")
        print("   1. Learn from every trade executed")
        print("   2. Identify and remember successful patterns")
        print("   3. Track AI prediction accuracy")
        print("   4. Improve strategies based on outcomes")
        print("   5. Adapt to market conditions")
        print("   6. Optimize performance continuously")
        print("   7. Carry learnings to tomorrow's session")
        print("\n🚀 Ready for intelligent, adaptive trading!")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error initializing learning system: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = initialize_learning_system()
    
    if success:
        print("\n" + "=" * 60)
        print("[CHECK] LEARNING SYSTEM: FULLY OPERATIONAL")
        print("🧠 AI will learn and improve with each session")
        print("📈 Tomorrow's performance will benefit from today's learnings")
        print("=" * 60)
    else:
        print("\n[ERROR] Failed to initialize learning system")

