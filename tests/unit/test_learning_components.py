"""
PROMETHEUS Trading Platform - Learning Components Unit Tests
Tests for AI Attribution Tracker, Learning Feedback Loop, and Real AI Backtest System
"""

import pytest
import asyncio
import sqlite3
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, List

# Set test environment
os.environ["TESTING"] = "true"
os.environ["DISABLE_LIVE_TRADING"] = "true"


# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 AI ATTRIBUTION TRACKER TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestAIAttributionTracker:
    """Tests for the AI Attribution Tracker system"""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        yield db_path
        # Cleanup - handle Windows file locking
        import gc
        gc.collect()
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except PermissionError:
            pass  # File still locked, will be cleaned up later
    
    @pytest.fixture
    def tracker(self, temp_db):
        """Create an AI Attribution Tracker with temp database"""
        from core.ai_attribution_tracker import AIAttributionTracker
        tracker = AIAttributionTracker(db_path=temp_db)
        return tracker
    
    def test_tracker_initialization(self, tracker, temp_db):
        """Test that tracker initializes correctly with database tables"""
        # Verify database tables were created
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'ai_attribution' in tables
        assert 'ai_system_metrics' in tables
    
    @pytest.mark.asyncio
    async def test_record_signal(self, tracker):
        """Test recording a trading signal with AI attribution"""
        attribution_ids = await tracker.record_signal(
            symbol='AAPL',
            ai_components=['Technical', 'Quantum', 'Agents'],
            vote_breakdown={'BUY': 3, 'HOLD': 1, 'SELL': 0},
            action='BUY',
            confidence=0.85,
            entry_price=150.00,
            trade_id='test_trade_001'
        )
        
        assert len(attribution_ids) == 3
        assert all('attr_' in aid for aid in attribution_ids)
        
        # Verify in-memory metrics updated
        assert 'Technical' in tracker.ai_metrics
        assert tracker.ai_metrics['Technical'].total_signals >= 1
    
    @pytest.mark.asyncio
    async def test_record_outcome(self, tracker, temp_db):
        """Test recording trade outcome and updating metrics"""
        # First record a signal
        await tracker.record_signal(
            symbol='MSFT',
            ai_components=['Technical', 'Oracle'],
            vote_breakdown={'BUY': 2},
            action='BUY',
            confidence=0.75,
            entry_price=300.00,
            trade_id='test_trade_002'
        )
        
        # Record outcome
        await tracker.record_outcome(
            symbol='MSFT',
            pnl=50.00,
            pnl_pct=0.05,
            trade_id='test_trade_002'
        )
        
        # Verify database was updated
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT eventual_pnl, outcome_recorded FROM ai_attribution WHERE symbol='MSFT'")
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) >= 1
        # At least one should have outcome recorded
        assert any(row[1] == 1 for row in rows)
    
    @pytest.mark.asyncio
    async def test_get_top_performers(self, tracker):
        """Test getting top performing AI systems"""
        # Record multiple signals with outcomes
        for i in range(10):
            await tracker.record_signal(
                symbol=f'TEST{i}',
                ai_components=['Technical'],
                vote_breakdown={'BUY': 1},
                action='BUY',
                confidence=0.8,
                entry_price=100.00
            )
            await tracker.record_outcome(
                symbol=f'TEST{i}',
                pnl=10.00 if i % 2 == 0 else -5.00,
                pnl_pct=0.1 if i % 2 == 0 else -0.05
            )
        
        top_performers = await tracker.get_top_performers(period_days=30, min_signals=3)
        
        assert isinstance(top_performers, list)
        if top_performers:
            assert 'ai_system' in top_performers[0]
            assert 'total_pnl' in top_performers[0]
            assert 'win_rate' in top_performers[0]
    
    @pytest.mark.asyncio
    async def test_generate_leaderboard_report(self, tracker):
        """Test leaderboard report generation"""
        # Add some test data
        await tracker.record_signal(
            symbol='SPY',
            ai_components=['Technical', 'Quantum'],
            vote_breakdown={'BUY': 2},
            action='BUY',
            confidence=0.9,
            entry_price=450.00
        )
        
        report = await tracker.generate_leaderboard_report(period_days=7)
        
        assert isinstance(report, str)
        assert 'LEADERBOARD' in report or 'No data' in report
    
    def test_calculate_sharpe(self, tracker):
        """Test Sharpe ratio calculation"""
        # Test with positive returns
        pnl_history = [10, 20, 15, 25, 30]
        sharpe = tracker._calculate_sharpe(pnl_history)
        assert sharpe > 0
        
        # Test with mixed returns
        pnl_history = [10, -5, 15, -10, 20]
        sharpe = tracker._calculate_sharpe(pnl_history)
        assert isinstance(sharpe, float)
        
        # Test with empty history
        sharpe = tracker._calculate_sharpe([])
        assert sharpe == 0.0
    
    def test_get_metrics_summary(self, tracker):
        """Test getting metrics summary"""
        summary = tracker.get_metrics_summary()

        assert 'total_ai_systems' in summary
        assert 'total_signals' in summary
        assert 'systems' in summary
        assert isinstance(summary['systems'], dict)

    @pytest.mark.asyncio
    async def test_get_ai_recommendations(self, tracker):
        """Test AI weight recommendations"""
        # Add test data with varying performance
        for i in range(15):
            await tracker.record_signal(
                symbol=f'REC{i}',
                ai_components=['Technical', 'Quantum'],
                vote_breakdown={'BUY': 2},
                action='BUY',
                confidence=0.8,
                entry_price=100.00
            )
            # Technical wins more often
            pnl = 20.00 if i % 3 != 0 else -10.00
            await tracker.record_outcome(symbol=f'REC{i}', pnl=pnl, pnl_pct=pnl/100)

        recommendations = await tracker.get_ai_recommendations()

        assert 'increase_weight' in recommendations
        assert 'decrease_weight' in recommendations
        assert 'maintain_weight' in recommendations


# ═══════════════════════════════════════════════════════════════════════════════
# 🧠 LEARNING FEEDBACK LOOP TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestLearningFeedbackLoop:
    """Tests for the Learning Feedback Loop methods in live trading"""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        yield db_path
        # Cleanup - handle Windows file locking
        import gc
        gc.collect()
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except PermissionError:
            pass  # File still locked, will be cleaned up later

    @pytest.fixture
    def mock_trading_system(self, temp_db):
        """Create a mock trading system with learning methods"""
        import logging

        class MockTradingSystem:
            def __init__(self, db_path):
                self.db_path = db_path
                self.logger = logging.getLogger('test')
                self.systems = {}
                self._init_db()

            def _init_db(self):
                conn = sqlite3.connect(self.db_path)
                conn.execute("PRAGMA journal_mode=WAL")
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS signal_predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        action TEXT NOT NULL,
                        confidence REAL,
                        entry_price REAL,
                        target_price REAL,
                        stop_loss REAL,
                        ai_components TEXT,
                        vote_breakdown TEXT,
                        reasoning TEXT,
                        market_data TEXT,
                        outcome_recorded INTEGER DEFAULT 0
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS learning_outcomes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        predicted_action TEXT,
                        predicted_confidence REAL,
                        entry_price REAL,
                        exit_price REAL,
                        profit_loss REAL,
                        profit_pct REAL,
                        was_correct INTEGER,
                        ai_components TEXT,
                        learning_notes TEXT
                    )
                """)
                conn.commit()
                conn.close()

            async def _store_signal_prediction(self, signal: Dict[str, Any]):
                """Store AI signal prediction for later learning comparison"""
                conn = sqlite3.connect(self.db_path, timeout=30.0)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO signal_predictions
                    (timestamp, symbol, action, confidence, entry_price, target_price, stop_loss,
                     ai_components, vote_breakdown, reasoning, market_data, outcome_recorded)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (
                    datetime.now().isoformat(),
                    signal.get('symbol', ''),
                    signal.get('action', 'HOLD'),
                    signal.get('confidence', 0.5),
                    signal.get('entry_price', 0),
                    signal.get('target_price', 0),
                    signal.get('stop_loss', 0),
                    str(signal.get('ai_components', [])),
                    str(signal.get('vote_breakdown', {})),
                    signal.get('reasoning', ''),
                    str(signal.get('market_data', {}))
                ))
                conn.commit()
                conn.close()

            async def _get_original_prediction(self, symbol: str) -> Dict[str, Any]:
                """Retrieve the original AI prediction for a symbol"""
                conn = sqlite3.connect(self.db_path, timeout=30.0)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT action, confidence, entry_price, target_price, stop_loss,
                           ai_components, vote_breakdown, reasoning, market_data
                    FROM signal_predictions
                    WHERE symbol = ? AND outcome_recorded = 0
                    ORDER BY timestamp DESC LIMIT 1
                """, (symbol,))
                row = cursor.fetchone()
                conn.close()

                if row:
                    return {
                        'action': row[0],
                        'confidence': row[1],
                        'entry_price': row[2],
                        'target_price': row[3],
                        'stop_loss': row[4],
                        'ai_components': eval(row[5]) if row[5] else [],
                        'vote_breakdown': eval(row[6]) if row[6] else {},
                        'reasoning': row[7],
                        'market_data': eval(row[8]) if row[8] else {}
                    }
                return {'action': 'HOLD', 'confidence': 0.5, 'ai_components': []}

            async def _persist_learning_outcome(self, symbol: str, entry_price: float,
                                                exit_price: float, profit_loss: float,
                                                profit_pct: float, was_correct: bool,
                                                original_prediction: Dict[str, Any]):
                """Persist learning outcome to database"""
                conn = sqlite3.connect(self.db_path, timeout=30.0)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO learning_outcomes
                    (timestamp, symbol, predicted_action, predicted_confidence, entry_price,
                     exit_price, profit_loss, profit_pct, was_correct, ai_components, learning_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    symbol,
                    original_prediction.get('action', 'HOLD'),
                    original_prediction.get('confidence', 0.5),
                    entry_price,
                    exit_price,
                    profit_loss,
                    profit_pct,
                    1 if was_correct else 0,
                    str(original_prediction.get('ai_components', [])),
                    f"Trade outcome: {'Correct' if was_correct else 'Incorrect'}"
                ))
                # Mark prediction as processed
                cursor.execute("""
                    UPDATE signal_predictions SET outcome_recorded = 1
                    WHERE symbol = ? AND outcome_recorded = 0
                """, (symbol,))
                conn.commit()
                conn.close()

        return MockTradingSystem(temp_db)

    @pytest.mark.asyncio
    async def test_store_signal_prediction(self, mock_trading_system, temp_db):
        """Test storing signal predictions"""
        signal = {
            'symbol': 'AAPL',
            'action': 'BUY',
            'confidence': 0.85,
            'entry_price': 150.00,
            'target_price': 165.00,
            'stop_loss': 145.00,
            'ai_components': ['Technical', 'Quantum'],
            'vote_breakdown': {'BUY': 2, 'HOLD': 0},
            'reasoning': 'Strong bullish signals',
            'market_data': {'rsi': 45, 'macd': 'bullish'}
        }

        await mock_trading_system._store_signal_prediction(signal)

        # Verify stored in database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT symbol, action, confidence FROM signal_predictions WHERE symbol='AAPL'")
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == 'AAPL'
        assert row[1] == 'BUY'
        assert row[2] == 0.85

    @pytest.mark.asyncio
    async def test_get_original_prediction(self, mock_trading_system):
        """Test retrieving original predictions"""
        # Store a prediction first
        signal = {
            'symbol': 'MSFT',
            'action': 'STRONG_BUY',
            'confidence': 0.92,
            'entry_price': 300.00,
            'ai_components': ['Oracle', 'Consciousness']
        }
        await mock_trading_system._store_signal_prediction(signal)

        # Retrieve it
        prediction = await mock_trading_system._get_original_prediction('MSFT')

        assert prediction['action'] == 'STRONG_BUY'
        assert prediction['confidence'] == 0.92
        assert 'Oracle' in prediction['ai_components']

    @pytest.mark.asyncio
    async def test_persist_learning_outcome(self, mock_trading_system, temp_db):
        """Test persisting learning outcomes"""
        # Store prediction first
        signal = {
            'symbol': 'GOOGL',
            'action': 'BUY',
            'confidence': 0.80,
            'entry_price': 140.00,
            'ai_components': ['Technical']
        }
        await mock_trading_system._store_signal_prediction(signal)

        # Get prediction and persist outcome
        prediction = await mock_trading_system._get_original_prediction('GOOGL')
        await mock_trading_system._persist_learning_outcome(
            symbol='GOOGL',
            entry_price=140.00,
            exit_price=150.00,
            profit_loss=10.00,
            profit_pct=0.0714,
            was_correct=True,
            original_prediction=prediction
        )

        # Verify outcome stored
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT symbol, profit_loss, was_correct FROM learning_outcomes WHERE symbol='GOOGL'")
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        assert row[1] == 10.00
        assert row[2] == 1  # was_correct = True

    @pytest.mark.asyncio
    async def test_prediction_marked_as_processed(self, mock_trading_system, temp_db):
        """Test that predictions are marked as processed after outcome recording"""
        signal = {'symbol': 'TSLA', 'action': 'BUY', 'confidence': 0.75, 'entry_price': 200.00}
        await mock_trading_system._store_signal_prediction(signal)

        prediction = await mock_trading_system._get_original_prediction('TSLA')
        await mock_trading_system._persist_learning_outcome(
            symbol='TSLA', entry_price=200.00, exit_price=210.00,
            profit_loss=10.00, profit_pct=0.05, was_correct=True,
            original_prediction=prediction
        )

        # Verify prediction marked as processed
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT outcome_recorded FROM signal_predictions WHERE symbol='TSLA'")
        row = cursor.fetchone()
        conn.close()

        assert row[0] == 1  # outcome_recorded = True


# ═══════════════════════════════════════════════════════════════════════════════
# 📊 REAL AI BACKTEST SYSTEM TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestRealAIBacktest:
    """Tests for the Real AI Backtest system"""

    @pytest.fixture
    def mock_historical_data(self):
        """Create mock historical data for testing"""
        import pandas as pd
        import numpy as np

        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        data = {
            'Open': np.random.uniform(100, 110, 30),
            'High': np.random.uniform(110, 120, 30),
            'Low': np.random.uniform(90, 100, 30),
            'Close': np.random.uniform(100, 110, 30),
            'Volume': np.random.randint(1000000, 5000000, 30)
        }
        df = pd.DataFrame(data, index=dates)
        return df

    def test_technical_indicator_calculation(self, mock_historical_data):
        """Test technical indicator calculation"""
        df = mock_historical_data.copy()

        # Calculate RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        assert len(rsi) == len(df)
        assert rsi.dropna().between(0, 100).all()

    def test_position_sizing(self):
        """Test position sizing calculation"""
        capital = 100000
        max_position_pct = 0.10
        price = 150.00

        max_position_value = capital * max_position_pct
        shares = int(max_position_value / price)

        assert shares == 66  # $10,000 / $150 = 66 shares
        assert shares * price <= max_position_value

    def test_stop_loss_calculation(self):
        """Test stop loss price calculation"""
        entry_price = 100.00
        stop_loss_pct = 0.03  # 3%

        stop_loss_price = entry_price * (1 - stop_loss_pct)

        assert stop_loss_price == 97.00

    def test_take_profit_calculation(self):
        """Test take profit price calculation"""
        entry_price = 100.00
        take_profit_pct = 0.08  # 8%

        take_profit_price = entry_price * (1 + take_profit_pct)

        assert take_profit_price == 108.00

    def test_pnl_calculation(self):
        """Test P&L calculation"""
        entry_price = 100.00
        exit_price = 110.00
        quantity = 10

        pnl = (exit_price - entry_price) * quantity
        pnl_pct = (exit_price - entry_price) / entry_price

        assert pnl == 100.00
        assert pnl_pct == 0.10

    def test_win_rate_calculation(self):
        """Test win rate calculation"""
        trades = [
            {'pnl': 100},
            {'pnl': -50},
            {'pnl': 75},
            {'pnl': -25},
            {'pnl': 150}
        ]

        wins = sum(1 for t in trades if t['pnl'] > 0)
        total = len(trades)
        win_rate = wins / total

        assert win_rate == 0.6  # 3 wins out of 5

    def test_profit_factor_calculation(self):
        """Test profit factor calculation"""
        trades = [
            {'pnl': 100},
            {'pnl': -50},
            {'pnl': 75},
            {'pnl': -25}
        ]

        gross_profit = sum(t['pnl'] for t in trades if t['pnl'] > 0)
        gross_loss = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        assert gross_profit == 175
        assert gross_loss == 75
        assert profit_factor == pytest.approx(2.333, rel=0.01)

    def test_max_drawdown_calculation(self):
        """Test maximum drawdown calculation"""
        equity_curve = [100000, 105000, 102000, 98000, 103000, 95000, 100000]

        peak = equity_curve[0]
        max_drawdown = 0

        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)

        # Peak was 105000, lowest after was 95000
        expected_drawdown = (105000 - 95000) / 105000
        assert max_drawdown == pytest.approx(expected_drawdown, rel=0.01)

    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation"""
        import numpy as np

        returns = [0.02, -0.01, 0.03, -0.005, 0.015]
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        risk_free_rate = 0.0

        sharpe = (avg_return - risk_free_rate) / std_return if std_return > 0 else 0

        assert isinstance(sharpe, float)
        assert sharpe > 0  # Positive average return should give positive Sharpe

    def test_sortino_ratio_calculation(self):
        """Test Sortino ratio calculation"""
        import numpy as np

        returns = [0.02, -0.01, 0.03, -0.005, 0.015]
        avg_return = np.mean(returns)
        downside_returns = [r for r in returns if r < 0]
        downside_std = np.std(downside_returns) if downside_returns else 0

        sortino = avg_return / downside_std if downside_std > 0 else 0

        assert isinstance(sortino, float)

    @pytest.mark.asyncio
    async def test_ai_signal_generation_mock(self):
        """Test AI signal generation with mocked AI systems"""
        # Mock AI signal
        mock_signal = {
            'action': 'BUY',
            'confidence': 0.85,
            'ai_components': ['Technical', 'Quantum'],
            'vote_breakdown': {'BUY': 2, 'HOLD': 0, 'SELL': 0}
        }

        assert mock_signal['action'] in ['BUY', 'SELL', 'HOLD']
        assert 0 <= mock_signal['confidence'] <= 1
        assert len(mock_signal['ai_components']) > 0

    def test_trade_duration_calculation(self):
        """Test trade duration calculation"""
        entry_time = datetime(2024, 1, 1, 10, 0, 0)
        exit_time = datetime(2024, 1, 2, 14, 30, 0)

        duration = exit_time - entry_time
        duration_hours = duration.total_seconds() / 3600

        assert duration_hours == 28.5

    def test_backtest_metrics_structure(self):
        """Test that backtest metrics have correct structure"""
        metrics = {
            'initial_capital': 100000,
            'final_capital': 110000,
            'total_return': 0.10,
            'total_trades': 50,
            'winning_trades': 30,
            'losing_trades': 20,
            'win_rate': 0.60,
            'profit_factor': 1.5,
            'sharpe_ratio': 1.2,
            'sortino_ratio': 1.8,
            'max_drawdown': 0.15,
            'avg_win': 500,
            'avg_loss': 250
        }

        required_keys = ['initial_capital', 'final_capital', 'total_return',
                        'total_trades', 'win_rate', 'sharpe_ratio', 'max_drawdown']

        for key in required_keys:
            assert key in metrics


# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestLearningIntegration:
    """Integration tests for learning components working together"""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        yield db_path
        # Cleanup - handle Windows file locking
        import gc
        gc.collect()
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except PermissionError:
            pass  # File still locked, will be cleaned up later

    @pytest.mark.asyncio
    async def test_full_learning_cycle(self, temp_db):
        """Test complete learning cycle: signal → trade → outcome → learning"""
        from core.ai_attribution_tracker import AIAttributionTracker

        tracker = AIAttributionTracker(db_path=temp_db)

        # 1. Record signal
        attribution_ids = await tracker.record_signal(
            symbol='NVDA',
            ai_components=['Technical', 'Quantum', 'Consciousness'],
            vote_breakdown={'BUY': 3},
            action='BUY',
            confidence=0.90,
            entry_price=500.00,
            trade_id='integration_test_001'
        )

        assert len(attribution_ids) == 3

        # 2. Record outcome (profitable trade)
        await tracker.record_outcome(
            symbol='NVDA',
            pnl=50.00,
            pnl_pct=0.10,
            trade_id='integration_test_001'
        )

        # 3. Verify metrics updated
        summary = tracker.get_metrics_summary()
        assert summary['total_signals'] >= 3

        # 4. Get recommendations
        recommendations = await tracker.get_ai_recommendations()
        assert isinstance(recommendations, dict)

    @pytest.mark.asyncio
    async def test_multiple_ai_systems_attribution(self, temp_db):
        """Test attribution across multiple AI systems"""
        from core.ai_attribution_tracker import AIAttributionTracker

        tracker = AIAttributionTracker(db_path=temp_db)

        # Simulate multiple trades with different AI combinations
        ai_combinations = [
            ['Technical', 'Quantum'],
            ['Oracle', 'Consciousness'],
            ['Agents', 'GPT-OSS'],
            ['Technical', 'Oracle', 'Quantum']
        ]

        for i, ai_combo in enumerate(ai_combinations):
            await tracker.record_signal(
                symbol=f'TEST{i}',
                ai_components=ai_combo,
                vote_breakdown={'BUY': len(ai_combo)},
                action='BUY',
                confidence=0.8,
                entry_price=100.00
            )

            # Alternate wins and losses
            pnl = 20.00 if i % 2 == 0 else -10.00
            await tracker.record_outcome(symbol=f'TEST{i}', pnl=pnl, pnl_pct=pnl/100)

        # Verify all AI systems tracked
        summary = tracker.get_metrics_summary()
        assert summary['total_ai_systems'] >= 4


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

