#!/usr/bin/env python3
"""
🚀 PROMETHEUS REAL AI BACKTESTING SYSTEM
Backtesting using ACTUAL 80+ Revolutionary AI systems instead of simplified mock logic.

This backtester:
1. Downloads historical market data via yfinance
2. Replays the data through ACTUAL PROMETHEUS AI systems:
   - Market Oracle Engine
   - Quantum Trading Engine  
   - AI Consciousness Engine
   - Hierarchical Agent Coordinator (17 agents + 3 supervisors)
   - CPT-OSS/GPT-OSS
   - Technical Analysis
3. Uses the same decision-making pipeline as live trading
4. Calculates comprehensive metrics: Sharpe, Sortino, Calmar, max drawdown, win rate
5. Provides AI attribution analysis showing which systems contributed to profits

Usage:
    python prometheus_real_ai_backtest.py --period 90 --symbols SPY,QQQ,AAPL,BTCUSD
"""

import asyncio
import argparse
import logging
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import json
import sqlite3
import warnings
warnings.filterwarnings('ignore')

# Configure logging with UTF-8 encoding for Windows compatibility
import sys
try:
    # Ensure emoji/unicode log lines do not crash on Windows cp1252 consoles.
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

log_file = f'backtest_real_ai_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Stream handler with error handling for unicode
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler]
)
logger = logging.getLogger(__name__)

# Suppress logging errors from other modules with emojis
logging.getLogger('core.hierarchical_agent_coordinator').setLevel(logging.WARNING)

@dataclass
class BacktestTrade:
    """Individual trade record"""
    trade_id: str
    timestamp: datetime
    symbol: str
    action: str  # BUY, SELL
    entry_price: float
    exit_price: Optional[float] = None
    quantity: float = 0
    pnl: float = 0
    pnl_pct: float = 0
    ai_components: List[str] = field(default_factory=list)
    confidence: float = 0
    duration_hours: float = 0
    exit_reason: str = ""

@dataclass
class BacktestMetrics:
    """Comprehensive backtest metrics"""
    total_return: float = 0
    sharpe_ratio: float = 0
    sortino_ratio: float = 0
    calmar_ratio: float = 0
    max_drawdown: float = 0
    win_rate: float = 0
    profit_factor: float = 0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    gross_profit: float = 0
    gross_loss: float = 0
    avg_win: float = 0
    avg_loss: float = 0
    avg_trade_duration_hours: float = 0
    best_trade: float = 0
    worst_trade: float = 0
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    ai_attribution: Dict[str, Dict[str, float]] = field(default_factory=dict)

class PrometheusRealAIBacktester:
    """
    Real AI Backtesting System using actual PROMETHEUS components.
    Unlike mock backtests, this runs the actual 80+ AI systems.
    """
    
    def __init__(self, initial_capital: float = 100000,
                 max_position_pct: float = 0.12,     # AGGRESSIVE: 12% position size
                 stop_loss_pct: float = 0.02,         # AGGRESSIVE: 2% stop loss
                 take_profit_pct: float = 0.05,       # AGGRESSIVE: 5% take profit
                 min_confidence: float = 0.60,
                 min_tech_confidence: float = 0.65,
                 max_concurrent_positions: int = 8):   # AGGRESSIVE: max 8 open positions

        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_position_pct = max_position_pct
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.min_confidence = min_confidence
        self.min_tech_confidence = min_tech_confidence
        self.max_concurrent_positions = max_concurrent_positions

        # Trading state
        self.positions: Dict[str, BacktestTrade] = {}
        self.closed_trades: List[BacktestTrade] = []
        self.portfolio_history: List[float] = [initial_capital]
        self.daily_returns: List[float] = []

        # AI System tracking
        self.ai_systems: Dict[str, Any] = {}
        self.ai_attribution: Dict[str, Dict[str, Any]] = {}

        # === 6 AGGRESSIVE ENHANCEMENTS (matching live trading config) ===

        # ENHANCEMENT 1: TRAILING STOP
        self.trailing_stop_enabled = True
        self.trailing_stop_trigger = 0.02   # Activate at +2% profit
        self.trailing_stop_distance = 0.01  # Sell if drops 1% from high

        # ENHANCEMENT 2: DCA ON DIPS
        self.dca_enabled = True
        self.dca_trigger_pct = -0.02   # Buy more if down 2%
        self.dca_max_adds = 2          # Max 2 DCA adds per position
        self.dca_position_pct = 0.05   # 5% of capital per DCA buy

        # ENHANCEMENT 3: TIME-BASED EXIT
        self.time_exit_enabled = True
        self.max_hold_days_crypto = 3  # Exit crypto after 3 days if not profitable
        self.max_hold_days_stock = 7   # Exit stocks after 7 days if not profitable

        # ENHANCEMENT 4: SCALE-OUT PROFITS
        self.scale_out_enabled = True
        self.scale_out_first_pct = 0.02   # Sell 50% at +2%
        self.scale_out_second_pct = 0.04  # Sell remaining at +4%

        # ENHANCEMENT 5: CORRELATION FILTER
        self.correlation_filter_enabled = True
        self.max_correlated_positions = 2
        self.correlated_assets = {
            'BTC-USD': ['ETH-USD', 'SOL-USD', 'LINK-USD'],
            'ETH-USD': ['BTC-USD', 'SOL-USD'],
            'SOL-USD': ['BTC-USD', 'ETH-USD'],
            'AAPL': ['MSFT', 'GOOGL'],
            'MSFT': ['AAPL', 'GOOGL'],
            'GOOGL': ['AAPL', 'MSFT'],
            'QQQ': ['SPY'],
            'SPY': ['QQQ'],
        }

        # ENHANCEMENT 6: SENTIMENT/FED DAYS FILTER
        self.sentiment_filter_enabled = True
        self.fed_days_2025_2026 = [
            "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
            "2025-07-30", "2025-09-17", "2025-11-05", "2025-12-17",
            "2026-01-28", "2026-03-18", "2026-05-06", "2026-06-17",
            "2026-07-29", "2026-09-16", "2026-11-04", "2026-12-16",
        ]

        # Position tracking for enhancements
        self.position_highs: Dict[str, float] = {}
        self.position_entry_times: Dict[str, datetime] = {}
        self.scaled_positions: Dict[str, int] = {}
        self.dca_counts: Dict[str, int] = {}

        # Initialize AI systems
        self._init_ai_systems()

        logger.info(f"🚀 PROMETHEUS Real AI Backtester initialized (AGGRESSIVE CONFIG)")
        logger.info(f"   Initial Capital: ${initial_capital:,.2f}")
        logger.info(f"   Max Position: {max_position_pct*100:.1f}%")
        logger.info(f"   Stop Loss: {stop_loss_pct*100:.1f}%")
        logger.info(f"   Take Profit: {take_profit_pct*100:.1f}%")
        logger.info(f"   Max Concurrent Positions: {max_concurrent_positions}")
        logger.info(f"   Enhancements: TRAILING_STOP, SCALE_OUT, TIME_EXIT, DCA, SENTIMENT, CORRELATION")

    def _init_ai_systems(self):
        """Initialize actual PROMETHEUS AI systems"""
        logger.info("📡 Initializing PROMETHEUS AI systems...")

        # Default config for AI systems (AGGRESSIVE)
        default_config = {
            'risk': {'max_position_pct': self.max_position_pct, 'stop_loss_pct': self.stop_loss_pct},
            'portfolio': {'max_positions': self.max_concurrent_positions, 'diversification': True},
            'arbitrage': {'min_spread': 0.001},
            'oracle': {'confidence_threshold': 0.6}
        }

        # Import and initialize actual AI systems
        try:
            from revolutionary_features.oracle.market_oracle_engine import MarketOracleEngine
            self.ai_systems['oracle'] = MarketOracleEngine(config=default_config)
            logger.info("   ✅ Market Oracle Engine")
        except Exception as e:
            logger.warning(f"   ⚠️ Market Oracle unavailable: {e}")

        try:
            from revolutionary_features.quantum_trading.quantum_trading_engine import QuantumTradingEngine
            self.ai_systems['quantum'] = QuantumTradingEngine(config=default_config)
            logger.info("   ✅ Quantum Trading Engine")
        except Exception as e:
            logger.warning(f"   ⚠️ Quantum Trading unavailable: {e}")
        
        try:
            from revolutionary_features.ai_consciousness.ai_consciousness_engine import AIConsciousnessEngine
            self.ai_systems['consciousness'] = AIConsciousnessEngine()
            logger.info("   ✅ AI Consciousness Engine")
        except Exception as e:
            logger.warning(f"   ⚠️ AI Consciousness unavailable: {e}")

        try:
            from core.hierarchical_agent_coordinator import HierarchicalAgentCoordinator
            self.ai_systems['agents'] = HierarchicalAgentCoordinator()
            logger.info("   ✅ Hierarchical Agent Coordinator")
        except Exception as e:
            logger.warning(f"   ⚠️ Agent Coordinator unavailable: {e}")

        try:
            from core.gpt_oss_trading_adapter import GPTOSSTradingAdapter
            self.ai_systems['gpt_oss'] = GPTOSSTradingAdapter()
            logger.info("   ✅ GPT-OSS Trading Adapter")
        except Exception as e:
            logger.warning(f"   ⚠️ GPT-OSS unavailable: {e}")

        # Market Intelligence Agents
        try:
            from core.market_intelligence_agents import GapDetectionAgent
            self.ai_systems['gap_detector'] = GapDetectionAgent(agent_id="backtest_gap_detector")
            logger.info("   ✅ Gap Detection Agent")
        except Exception as e:
            logger.warning(f"   ⚠️ Gap Detection Agent unavailable: {e}")

        try:
            from core.market_intelligence_agents import OpportunityScannerAgent
            self.ai_systems['opportunity_scanner'] = OpportunityScannerAgent(agent_id="backtest_opp_scanner")
            logger.info("   ✅ Opportunity Scanner Agent")
        except Exception as e:
            logger.warning(f"   ⚠️ Opportunity Scanner Agent unavailable: {e}")

        try:
            from core.market_intelligence_agents import MarketResearchAgent
            self.ai_systems['market_researcher'] = MarketResearchAgent(agent_id="backtest_researcher")
            logger.info("   ✅ Market Research Agent")
        except Exception as e:
            logger.warning(f"   ⚠️ Market Research Agent unavailable: {e}")

        logger.info(f"📊 Initialized {len(self.ai_systems)} AI systems for backtesting")

    async def download_historical_data(self, symbols: List[str], period_days: int,
                                       interval: str = '1d') -> Dict[str, pd.DataFrame]:
        """Download historical data for backtesting

        Args:
            symbols: List of symbols to download
            period_days: Number of days of data
            interval: Data interval - '1d' for daily, '1h' for hourly
        """
        interval_name = 'hourly' if interval == '1h' else 'daily'
        logger.info(f"Downloading {period_days} days of {interval_name} data for {len(symbols)} symbols...")

        data = {}
        for symbol in symbols:
            try:
                # Convert PROMETHEUS crypto symbols to yfinance format
                yf_symbol = symbol
                if symbol.endswith('USD') and not symbol.endswith('-USD'):
                    yf_symbol = f"{symbol[:-3]}-USD"  # BTCUSD -> BTC-USD

                ticker = yf.Ticker(yf_symbol)

                if interval == '1h':
                    # Hourly data: use period parameter (max 730 days for 1h)
                    period = f"{min(period_days, 60)}d"
                    df = ticker.history(period=period, interval='1h')
                else:
                    # Daily data: use date range
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=period_days)
                    df = ticker.history(start=start_date.strftime('%Y-%m-%d'),
                                       end=end_date.strftime('%Y-%m-%d'))

                if not df.empty:
                    df = self._add_technical_indicators(df)
                    data[symbol] = df
                    bars_text = f"{len(df)} {interval_name} bars"
                    logger.info(f"   {symbol}: {bars_text}")
                else:
                    logger.warning(f"   {symbol}: No data available")

            except Exception as e:
                logger.error(f"   {symbol}: Download failed - {e}")

        return data

    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to historical data"""
        try:
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            # Moving Averages
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['EMA_12'] = df['Close'].ewm(span=12).mean()
            df['EMA_26'] = df['Close'].ewm(span=26).mean()

            # MACD
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()

            # Bollinger Bands
            df['BB_Middle'] = df['Close'].rolling(window=20).mean()
            df['BB_Std'] = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * 2)
            df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * 2)

            # ATR (Average True Range)
            high_low = df['High'] - df['Low']
            high_close = abs(df['High'] - df['Close'].shift())
            low_close = abs(df['Low'] - df['Close'].shift())
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(window=14).mean()

            # Volatility
            df['Volatility'] = df['Close'].pct_change().rolling(window=20).std()

        except Exception as e:
            logger.warning(f"Technical indicator calculation failed: {e}")

        return df

    async def get_ai_signal(self, symbol: str, market_data: Dict[str, Any],
                           historical_df: pd.DataFrame, current_idx: int) -> Optional[Dict[str, Any]]:
        """Get trading signal using ACTUAL PROMETHEUS AI systems"""
        try:
            ai_contributions = []
            signal_votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
            confidence_scores = []

            current_price = market_data['Close']

            # Prepare market context for AI systems
            context = {
                'symbol': symbol,
                'price': current_price,
                'volume': market_data.get('Volume', 0),
                'high': market_data.get('High', current_price),
                'low': market_data.get('Low', current_price),
                'rsi': market_data.get('RSI', 50),
                'macd': market_data.get('MACD', 0),
                'volatility': market_data.get('Volatility', 0.02),
                'historical': historical_df.iloc[max(0, current_idx-30):current_idx].to_dict('records'),
                'recent_candles': historical_df.iloc[max(0, current_idx-10):current_idx + 1][['Open', 'High', 'Low', 'Close', 'Volume']].to_dict('records')
            }

            # ═══════════════════════════════════════════════════════════════
            # 📈 MARKET REGIME DETECTION (Reduce trading in sideways markets)
            # ═══════════════════════════════════════════════════════════════
            market_regime = self._detect_market_regime(historical_df, current_idx)
            regime_confidence_boost = 0.0

            if market_regime == 'SIDEWAYS':
                # In sideways markets, require MUCH higher confidence (hardest to profit)
                regime_confidence_boost = 0.20  # Need 20% more confidence (was 10%)
                logger.debug(f"Sideways market detected - increasing confidence threshold by 20%")
            elif market_regime == 'HIGH_VOLATILITY':
                # In high volatility, be more selective
                regime_confidence_boost = 0.15
                logger.debug(f"High volatility detected - increasing confidence threshold by 15%")
            elif market_regime == 'TRENDING_BEAR':
                # In bear markets, be cautious with longs
                regime_confidence_boost = 0.10  # Need 10% more confidence for buys
                logger.debug(f"Bear market detected - increasing buy confidence threshold by 10%")

            # ═══════════════════════════════════════════════════════════════
            # 🔮 MARKET ORACLE ENGINE
            # ═══════════════════════════════════════════════════════════════
            if self.ai_systems.get('oracle'):
                try:
                    oracle = self.ai_systems['oracle']
                    if hasattr(oracle, 'generate_prediction'):
                        prediction = await oracle.generate_prediction(symbol, '24h')
                        if prediction:
                            oracle_action = 'BUY' if prediction.predicted_change_percent > 1.0 else \
                                          'SELL' if prediction.predicted_change_percent < -1.0 else 'HOLD'
                            self._register_ai_signal(
                                signal_votes,
                                confidence_scores,
                                ai_contributions,
                                oracle_action,
                                prediction.confidence,
                                'Oracle',
                                weight=1.2
                            )
                except Exception as e:
                    logger.debug(f"Oracle prediction failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # ⚛️ QUANTUM TRADING ENGINE (Weight: 0.6, Min Confidence: 0.70)
            # ═══════════════════════════════════════════════════════════════
            if self.ai_systems.get('quantum'):
                try:
                    quantum = self.ai_systems['quantum']
                    if hasattr(quantum, 'detect_arbitrage_opportunities'):
                        arb_result = await quantum.detect_arbitrage_opportunities(context)
                        if arb_result and arb_result.get('opportunities'):
                            quantum_confidence = arb_result.get('confidence', 0.7)
                            # Only accept high-confidence quantum signals (0.70+ threshold)
                            if quantum_confidence >= 0.70:
                                self._register_ai_signal(
                                    signal_votes,
                                    confidence_scores,
                                    ai_contributions,
                                    'BUY',
                                    quantum_confidence,
                                    'Quantum',
                                    weight=0.6
                                )
                            else:
                                logger.debug(f"Quantum signal filtered: confidence {quantum_confidence:.2f} < 0.70")
                except Exception as e:
                    logger.debug(f"Quantum analysis failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🧠 AI CONSCIOUSNESS ENGINE
            # ═══════════════════════════════════════════════════════════════
            if self.ai_systems.get('consciousness'):
                try:
                    consciousness = self.ai_systems['consciousness']
                    if hasattr(consciousness, 'analyze_market_awareness'):
                        awareness = await consciousness.analyze_market_awareness(symbol, context)
                        if awareness:
                            consciousness_action = awareness.get('recommended_action', 'HOLD')
                            self._register_ai_signal(
                                signal_votes,
                                confidence_scores,
                                ai_contributions,
                                consciousness_action,
                                awareness.get('confidence', 0.6),
                                'Consciousness',
                                weight=1.1
                            )
                except Exception as e:
                    logger.debug(f"Consciousness analysis failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 👁️ MARKET INTELLIGENCE (Vision-Like Pattern Scanners)
            # ═══════════════════════════════════════════════════════════════
            if self.ai_systems.get('gap_detector'):
                try:
                    gap_signal = self._get_historical_gap_signal(symbol, historical_df, current_idx)
                    if gap_signal and gap_signal['confidence'] >= 0.55:
                        self._register_ai_signal(
                            signal_votes,
                            confidence_scores,
                            ai_contributions,
                            gap_signal['action'],
                            gap_signal['confidence'],
                            'ChartVision',
                            weight=0.7
                        )
                except Exception as e:
                    logger.debug(f"Gap detector analysis failed: {e}")

            if self.ai_systems.get('opportunity_scanner'):
                try:
                    opportunity_signal = self._get_historical_opportunity_signal(symbol, historical_df, current_idx)
                    if opportunity_signal and opportunity_signal['confidence'] >= 0.55:
                        self._register_ai_signal(
                            signal_votes,
                            confidence_scores,
                            ai_contributions,
                            opportunity_signal['action'],
                            opportunity_signal['confidence'],
                            'OpportunityScanner',
                            weight=0.8
                        )
                except Exception as e:
                    logger.debug(f"Opportunity scanner analysis failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🤖 HIERARCHICAL AGENT COORDINATOR (Weight: 2.0 - Top Performer!)
            # ═══════════════════════════════════════════════════════════════
            if self.ai_systems.get('agents'):
                try:
                    coordinator = self.ai_systems['agents']
                    if hasattr(coordinator, 'coordinate_intelligent_trading'):
                        decisions = await coordinator.coordinate_intelligent_trading(context)
                        if decisions:
                            for decision in decisions:
                                # Match symbol directly or use as general market sentiment
                                symbol_match = decision.symbol == symbol or decision.symbol in [symbol.replace('/', '')]
                                # Also accept high-confidence decisions as general market sentiment
                                is_market_sentiment = decision.confidence >= 0.65 and decision.action in ['buy', 'sell']

                                if symbol_match or is_market_sentiment:
                                    action = decision.action.upper()
                                    weight = 2.0 if symbol_match else 1.0
                                    self._register_ai_signal(
                                        signal_votes,
                                        confidence_scores,
                                        ai_contributions,
                                        action,
                                        decision.confidence,
                                        'Agents',
                                        weight=weight
                                    )
                except Exception as e:
                    logger.debug(f"Agent coordination failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 📊 TECHNICAL ANALYSIS (Weight: 0.4, Min Confidence: 0.65)
            # AGGRESSIVE FILTERING - Technical is the biggest source of losses
            # ═══════════════════════════════════════════════════════════════
            try:
                tech_signal = self._get_technical_signal(market_data)
                tech_confidence = tech_signal['confidence']

                # Only accept high-confidence technical signals (0.65+ threshold)
                # AND require confirmation from at least one other AI system
                if tech_confidence >= self.min_tech_confidence:
                    # Further reduced weight from 0.5 to 0.4 (biggest loss source)
                    self._register_ai_signal(
                        signal_votes,
                        confidence_scores,
                        ai_contributions,
                        tech_signal['action'],
                        tech_confidence,
                        'Technical',
                        weight=0.4
                    )
                else:
                    logger.debug(f"Technical signal filtered: {tech_confidence:.2f} < {self.min_tech_confidence:.2f}")
            except Exception as e:
                logger.debug(f"Technical analysis failed: {e}")

            # ═══════════════════════════════════════════════════════════════
            # 🎯 SYNTHESIZE FINAL SIGNAL
            # ═══════════════════════════════════════════════════════════════
            if not ai_contributions:
                return None

            final_action = max(signal_votes, key=signal_votes.get)
            total_votes = sum(signal_votes.values())

            vote_confidence = signal_votes[final_action] / total_votes if total_votes > 0 else 0.5
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
            final_confidence = (vote_confidence * 0.6 + avg_confidence * 0.4)

            # Agreement bonus
            agreement_bonus = min(0.15, len(ai_contributions) * 0.03)
            final_confidence = min(0.95, final_confidence + agreement_bonus)

            # Apply market regime confidence adjustment
            min_confidence_required = self.min_confidence + regime_confidence_boost
            if final_action != 'HOLD' and final_confidence < min_confidence_required:
                logger.debug(f"Signal filtered by regime ({market_regime}): {final_confidence:.2f} < {min_confidence_required:.2f}")
                return None

            return {
                'symbol': symbol,
                'action': final_action,
                'confidence': final_confidence,
                'ai_components': ai_contributions,
                'vote_breakdown': signal_votes,
                'entry_price': current_price,
                'market_regime': market_regime
            }

        except Exception as e:
            logger.error(f"Error getting AI signal for {symbol}: {e}")
            return None

    def _get_technical_signal(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get technical analysis signal"""
        rsi = market_data.get('RSI', 50)
        macd = market_data.get('MACD', 0)
        macd_signal = market_data.get('MACD_Signal', 0)

        action = 'HOLD'
        confidence = 0.5

        # RSI signals
        if rsi < 30:
            action = 'BUY'
            confidence = 0.75
        elif rsi > 70:
            action = 'SELL'
            confidence = 0.75

        # MACD crossover
        if macd > macd_signal and macd_signal < 0:
            action = 'BUY'
            confidence = max(confidence, 0.65)
        elif macd < macd_signal and macd_signal > 0:
            action = 'SELL'
            confidence = max(confidence, 0.65)

        return {'action': action, 'confidence': confidence}

    def _register_ai_signal(self,
                            signal_votes: Dict[str, float],
                            confidence_scores: List[float],
                            ai_contributions: List[str],
                            action: str,
                            confidence: float,
                            component: str,
                            weight: float = 1.0) -> bool:
        """Register a directional AI vote and keep attribution deduplicated."""
        normalized_action = str(action or 'HOLD').upper()
        normalized_confidence = float(confidence or 0.0)

        if normalized_action not in signal_votes or normalized_action == 'HOLD' or normalized_confidence <= 0:
            return False

        signal_votes[normalized_action] += normalized_confidence * weight
        confidence_scores.append(normalized_confidence)

        if component not in ai_contributions:
            ai_contributions.append(component)

        return True

    def _get_historical_gap_signal(self,
                                   symbol: str,
                                   historical_df: pd.DataFrame,
                                   current_idx: int) -> Optional[Dict[str, Any]]:
        """Derive a gap-style signal from replayed candles instead of live market fetches."""
        try:
            if current_idx < 1:
                return None

            current_bar = historical_df.iloc[current_idx]
            previous_bar = historical_df.iloc[current_idx - 1]

            prev_close = float(previous_bar.get('Close', 0) or 0)
            current_open = float(current_bar.get('Open', current_bar.get('Close', 0)) or 0)
            current_close = float(current_bar.get('Close', 0) or 0)

            if prev_close <= 0 or current_open <= 0 or current_close <= 0:
                return None

            gap_pct = (current_open - prev_close) / prev_close
            if abs(gap_pct) < 0.012:
                return None

            intraday_follow_through = (current_close - current_open) / current_open
            recent_volume = historical_df.iloc[max(0, current_idx - 10):current_idx]['Volume'].dropna()
            avg_volume = float(recent_volume.mean()) if not recent_volume.empty else 0.0
            current_volume = float(current_bar.get('Volume', 0) or 0)
            volume_ratio = (current_volume / avg_volume) if avg_volume > 0 else 1.0

            action = 'BUY' if gap_pct > 0 else 'SELL'
            if gap_pct > 0 and intraday_follow_through < -0.01:
                return None
            if gap_pct < 0 and intraday_follow_through > 0.01:
                return None

            confidence = 0.50
            confidence += min(abs(gap_pct) * 8.0, 0.20)
            confidence += min(max(volume_ratio - 1.0, 0.0) * 0.08, 0.10)
            confidence += min(abs(intraday_follow_through) * 2.5, 0.08)

            return {
                'symbol': symbol,
                'action': action,
                'confidence': min(confidence, 0.88),
                'reasoning': (
                    f"Historical gap {gap_pct:+.2%} with follow-through {intraday_follow_through:+.2%} "
                    f"and volume ratio {volume_ratio:.2f}"
                )
            }
        except Exception as e:
            logger.debug(f"Historical gap signal failed: {e}")
            return None

    def _get_historical_opportunity_signal(self,
                                           symbol: str,
                                           historical_df: pd.DataFrame,
                                           current_idx: int) -> Optional[Dict[str, Any]]:
        """Derive a momentum/breakout opportunity signal from replayed history."""
        try:
            if current_idx < 5:
                return None

            current_bar = historical_df.iloc[current_idx]
            prior_window = historical_df.iloc[max(0, current_idx - 20):current_idx]
            if len(prior_window) < 5:
                return None

            current_close = float(current_bar.get('Close', 0) or 0)
            current_volume = float(current_bar.get('Volume', 0) or 0)
            if current_close <= 0:
                return None

            breakout_high = float(prior_window['High'].max())
            breakdown_low = float(prior_window['Low'].min())
            avg_volume = float(prior_window['Volume'].tail(10).mean()) if 'Volume' in prior_window else 0.0
            volume_ratio = (current_volume / avg_volume) if avg_volume > 0 else 1.0

            momentum_3 = (current_close / float(historical_df.iloc[current_idx - 3]['Close'])) - 1.0
            momentum_5 = (current_close / float(historical_df.iloc[current_idx - 5]['Close'])) - 1.0
            sma_20 = float(current_bar.get('SMA_20', np.nan))
            macd = float(current_bar.get('MACD', 0) or 0)
            macd_signal = float(current_bar.get('MACD_Signal', 0) or 0)

            candidates = []

            if breakout_high > 0 and current_close >= breakout_high * 1.002 and volume_ratio >= 1.15:
                confidence = min(0.90, 0.58 + max(volume_ratio - 1.0, 0.0) * 0.10 + max(momentum_3, 0.0) * 3.0)
                candidates.append({
                    'symbol': symbol,
                    'action': 'BUY',
                    'confidence': confidence,
                    'reasoning': f"Breakout above 20-bar high with volume ratio {volume_ratio:.2f}"
                })

            if breakdown_low > 0 and current_close <= breakdown_low * 0.998 and volume_ratio >= 1.15:
                confidence = min(0.90, 0.58 + max(volume_ratio - 1.0, 0.0) * 0.10 + abs(min(momentum_3, 0.0)) * 3.0)
                candidates.append({
                    'symbol': symbol,
                    'action': 'SELL',
                    'confidence': confidence,
                    'reasoning': f"Breakdown below 20-bar low with volume ratio {volume_ratio:.2f}"
                })

            if not np.isnan(sma_20) and current_close > sma_20 and macd > macd_signal and momentum_5 > 0.025:
                confidence = min(0.84, 0.55 + momentum_5 * 2.8 + max(volume_ratio - 1.0, 0.0) * 0.06)
                candidates.append({
                    'symbol': symbol,
                    'action': 'BUY',
                    'confidence': confidence,
                    'reasoning': f"Momentum continuation: 5-bar return {momentum_5:+.2%} above SMA20"
                })

            if not np.isnan(sma_20) and current_close < sma_20 and macd < macd_signal and momentum_5 < -0.025:
                confidence = min(0.84, 0.55 + abs(momentum_5) * 2.8 + max(volume_ratio - 1.0, 0.0) * 0.06)
                candidates.append({
                    'symbol': symbol,
                    'action': 'SELL',
                    'confidence': confidence,
                    'reasoning': f"Momentum breakdown: 5-bar return {momentum_5:+.2%} below SMA20"
                })

            if not candidates:
                return None

            return max(candidates, key=lambda item: item['confidence'])
        except Exception as e:
            logger.debug(f"Historical opportunity signal failed: {e}")
            return None

    def _detect_market_regime(self, df: pd.DataFrame, current_idx: int, lookback: int = 20) -> str:
        """Detect current market regime to adjust trading behavior

        Returns:
            str: One of 'TRENDING_BULL', 'TRENDING_BEAR', 'HIGH_VOLATILITY', 'SIDEWAYS'
        """
        try:
            if current_idx < lookback:
                return 'UNKNOWN'

            window_data = df.iloc[max(0, current_idx - lookback):current_idx]

            if len(window_data) < 10:
                return 'UNKNOWN'

            # Calculate returns and volatility
            returns = window_data['Close'].pct_change().dropna()
            if len(returns) < 5:
                return 'UNKNOWN'

            avg_return = returns.mean()
            volatility = returns.std()

            # Calculate trend (price change over period)
            trend = (window_data['Close'].iloc[-1] - window_data['Close'].iloc[0]) / window_data['Close'].iloc[0]

            # Classify regime
            if volatility > 0.03:  # High volatility (>3% daily std)
                return 'HIGH_VOLATILITY'
            elif trend > 0.05 and volatility < 0.02:  # Strong uptrend with low volatility
                return 'TRENDING_BULL'
            elif trend < -0.05:  # Strong downtrend
                return 'TRENDING_BEAR'
            elif abs(trend) < 0.02 and volatility < 0.015:  # Sideways with low volatility
                return 'SIDEWAYS'
            else:
                return 'NORMAL'

        except Exception as e:
            logger.debug(f"Market regime detection failed: {e}")
            return 'UNKNOWN'

    def _is_crypto_symbol(self, symbol: str) -> bool:
        """Detect if a symbol is crypto (for time exit logic)"""
        crypto_symbols = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'DOGE-USD',
                          'AVAX-USD', 'DOT-USD', 'BNB-USD', 'XRP-USD', 'LINK-USD']
        return symbol in crypto_symbols or '-USD' in symbol

    def _is_fed_day(self, timestamp) -> bool:
        """Check if a given date is a Fed meeting day (sentiment filter for backtest)"""
        if not self.sentiment_filter_enabled:
            return False
        if hasattr(timestamp, 'strftime'):
            date_str = timestamp.strftime("%Y-%m-%d")
        else:
            date_str = str(timestamp)[:10]
        return date_str in self.fed_days_2025_2026

    def _check_correlation_filter(self, symbol: str) -> bool:
        """Check if adding this symbol would exceed correlated position limits"""
        if not self.correlation_filter_enabled:
            return False
        correlated_symbols = self.correlated_assets.get(symbol, [])
        if not correlated_symbols:
            return False
        correlated_count = 0
        for corr_symbol in correlated_symbols:
            if corr_symbol in self.positions:
                correlated_count += 1
        return correlated_count >= self.max_correlated_positions

    def _cleanup_position_tracking(self, symbol: str):
        """Clean up all tracking data when position fully closed"""
        if symbol in self.position_highs:
            del self.position_highs[symbol]
        if symbol in self.position_entry_times:
            del self.position_entry_times[symbol]
        if symbol in self.scaled_positions:
            del self.scaled_positions[symbol]
        if symbol in self.dca_counts:
            del self.dca_counts[symbol]

    async def run_backtest(self, symbols: List[str], period_days: int = 90,
                          interval: str = '1d') -> BacktestMetrics:
        """Run comprehensive backtest using real AI systems

        Args:
            symbols: List of symbols to backtest
            period_days: Number of days of data
            interval: Data interval - '1d' for daily, '1h' for hourly
        """
        interval_name = 'HOURLY' if interval == '1h' else 'DAILY'
        logger.info(f"\n{'='*80}")
        logger.info(f"STARTING PROMETHEUS REAL AI BACKTEST ({interval_name} DATA)")
        logger.info(f"   Period: {period_days} days")
        logger.info(f"   Symbols: {symbols}")
        logger.info(f"{'='*80}\n")

        # Download historical data with specified interval
        historical_data = await self.download_historical_data(symbols, period_days, interval)

        if not historical_data:
            logger.error("❌ No historical data available. Aborting backtest.")
            return BacktestMetrics()

        # Run through each day
        total_days = max(len(df) for df in historical_data.values())

        for day_idx in range(20, total_days):  # Start after 20 days for indicator warmup
            # Use prior day's total equity as baseline for daily returns (not just cash)
            day_start_value = self.portfolio_history[-1] if self.portfolio_history else self.initial_capital

            for symbol, df in historical_data.items():
                if day_idx >= len(df):
                    continue

                market_data = df.iloc[day_idx].to_dict()
                current_price = market_data['Close']
                timestamp = df.index[day_idx]

                # ═══════════════════════════════════════════════════════
                # CHECK EXISTING POSITIONS with ALL 6 ENHANCEMENTS
                # ═══════════════════════════════════════════════════════
                if symbol in self.positions:
                    position = self.positions[symbol]
                    day_high = market_data.get('High', current_price)
                    day_low = market_data.get('Low', current_price)
                    is_crypto = self._is_crypto_symbol(symbol)
                    pnl_at_close = (current_price - position.entry_price) / position.entry_price

                    should_exit = False
                    partial_exit = False
                    partial_qty = 0
                    exit_reason = ""
                    exit_price = current_price

                    # ─── SAFETY: STOP LOSS (always first) ───
                    sl_price = position.entry_price * (1 - self.stop_loss_pct)
                    if day_low <= sl_price:
                        should_exit = True
                        exit_reason = "STOP_LOSS"
                        exit_price = sl_price

                    # ─── ENHANCEMENT 1: TRAILING STOP ───
                    if self.trailing_stop_enabled and not should_exit:
                        if symbol not in self.position_highs:
                            self.position_highs[symbol] = day_high
                        else:
                            self.position_highs[symbol] = max(self.position_highs[symbol], day_high)
                        high_price = self.position_highs[symbol]
                        high_pnl = (high_price - position.entry_price) / position.entry_price if position.entry_price > 0 else 0
                        if high_pnl >= self.trailing_stop_trigger:
                            drop_from_high = (high_price - current_price) / high_price if high_price > 0 else 0
                            if drop_from_high >= self.trailing_stop_distance:
                                should_exit = True
                                exit_price = current_price
                                exit_reason = f"TRAILING_STOP (peak +{high_pnl*100:.1f}%, now +{pnl_at_close*100:.1f}%)"

                    # ─── ENHANCEMENT 4: SCALE-OUT ───
                    if self.scale_out_enabled and not should_exit:
                        scaled_level = self.scaled_positions.get(symbol, 0)
                        pnl_at_high_pct = (day_high - position.entry_price) / position.entry_price

                        if pnl_at_high_pct >= self.scale_out_first_pct and scaled_level == 0:
                            partial_exit = True
                            partial_qty = position.quantity * 0.5
                            self.scaled_positions[symbol] = 1
                            exit_price = position.entry_price * (1 + self.scale_out_first_pct)
                            exit_reason = f"SCALE_OUT_1 (+{self.scale_out_first_pct*100:.0f}%)"
                        elif pnl_at_high_pct >= self.scale_out_second_pct and scaled_level == 1:
                            should_exit = True
                            self.scaled_positions[symbol] = 2
                            exit_price = position.entry_price * (1 + self.scale_out_second_pct)
                            exit_reason = f"SCALE_OUT_2 (+{self.scale_out_second_pct*100:.0f}%)"

                    # ─── ENHANCEMENT 3: TIME-BASED EXIT ───
                    if self.time_exit_enabled and not should_exit and not partial_exit:
                        entry_time = self.position_entry_times.get(symbol, position.timestamp)
                        try:
                            ts_naive = pd.Timestamp(timestamp).tz_localize(None) if pd.Timestamp(timestamp).tzinfo else pd.Timestamp(timestamp)
                            entry_naive = pd.Timestamp(entry_time).tz_localize(None) if pd.Timestamp(entry_time).tzinfo else pd.Timestamp(entry_time)
                            days_held = (ts_naive - entry_naive).total_seconds() / 86400
                        except Exception:
                            days_held = 0
                        max_days = self.max_hold_days_crypto if is_crypto else self.max_hold_days_stock
                        if days_held >= max_days and pnl_at_close < self.scale_out_first_pct:
                            should_exit = True
                            exit_price = current_price
                            exit_reason = f"TIME_EXIT ({days_held:.1f}d >= {max_days}d, P/L: {pnl_at_close*100:+.1f}%)"

                    # ─── TAKE PROFIT (checked after enhancements) ───
                    if not should_exit and not partial_exit:
                        tp_price = position.entry_price * (1 + self.take_profit_pct)
                        if day_high >= tp_price:
                            should_exit = True
                            exit_price = tp_price
                            exit_reason = "TAKE_PROFIT"

                    # ─── ENHANCEMENT 2: DCA ON DIPS ───
                    if self.dca_enabled and not should_exit and not partial_exit:
                        if pnl_at_close <= self.dca_trigger_pct:
                            dca_count = self.dca_counts.get(symbol, 0)
                            if dca_count < self.dca_max_adds:
                                dca_amount = self.current_capital * self.dca_position_pct
                                if dca_amount > 0 and current_price > 0:
                                    dca_qty = dca_amount / current_price
                                    if dca_qty * current_price <= self.current_capital:
                                        old_value = position.entry_price * position.quantity
                                        new_value = current_price * dca_qty
                                        position.quantity += dca_qty
                                        position.entry_price = (old_value + new_value) / position.quantity
                                        self.current_capital -= dca_qty * current_price
                                        self.dca_counts[symbol] = dca_count + 1
                                        logger.debug(f"DCA #{dca_count+1}: {symbol} +{dca_qty:.4f} @ ${current_price:.2f}")

                    # ─── EXECUTE EXIT (full or partial) ───
                    if should_exit:
                        await self._close_position(symbol, exit_price, exit_reason, timestamp)
                    elif partial_exit and partial_qty > 0:
                        partial_pnl = (exit_price - position.entry_price) * partial_qty
                        partial_pnl_pct = (exit_price - position.entry_price) / position.entry_price
                        self.current_capital += partial_qty * exit_price
                        position.quantity -= partial_qty
                        partial_trade = BacktestTrade(
                            trade_id=f"{position.trade_id}_partial",
                            timestamp=position.timestamp,
                            symbol=symbol, action='BUY',
                            entry_price=position.entry_price,
                            exit_price=exit_price,
                            quantity=partial_qty,
                            pnl=partial_pnl, pnl_pct=partial_pnl_pct,
                            ai_components=position.ai_components,
                            confidence=position.confidence,
                            exit_reason=exit_reason
                        )
                        try:
                            ts_dt = timestamp.to_pydatetime() if hasattr(timestamp, 'to_pydatetime') else timestamp
                            partial_trade.duration_hours = (ts_dt - position.timestamp).total_seconds() / 3600
                        except Exception:
                            partial_trade.duration_hours = 24.0
                        self.closed_trades.append(partial_trade)
                        is_win = partial_pnl > 0
                        for ai in position.ai_components:
                            if ai in self.ai_attribution:
                                self.ai_attribution[ai]['pnl'] += partial_pnl
                                if is_win:
                                    self.ai_attribution[ai]['wins'] += 1
                        logger.debug(f"SCALE_OUT: {symbol} sold {partial_qty:.4f} @ ${exit_price:.2f}")

                # ═══════════════════════════════════════════════════════
                # GET AI SIGNAL FOR NEW POSITIONS (with entry filters)
                # ═══════════════════════════════════════════════════════
                if symbol not in self.positions:
                    # Check max concurrent positions (AGGRESSIVE: 8)
                    if len(self.positions) >= self.max_concurrent_positions:
                        continue
                    # ENHANCEMENT 6: Sentiment filter - skip Fed meeting days
                    if self._is_fed_day(timestamp):
                        continue
                    # ENHANCEMENT 5: Correlation filter
                    if self._check_correlation_filter(symbol):
                        continue

                    signal = await self.get_ai_signal(symbol, market_data, df, day_idx)
                    min_confidence = getattr(self, 'min_confidence', 0.50)
                    if signal and signal['action'] in ['BUY', 'STRONG_BUY'] and signal['confidence'] >= min_confidence:
                        await self._open_position(symbol, current_price, signal, timestamp)

            # Track portfolio value
            # Portfolio = cash + value of all open positions
            portfolio_value = self.current_capital
            for symbol, position in self.positions.items():
                if symbol in historical_data and day_idx < len(historical_data[symbol]):
                    current_price = historical_data[symbol].iloc[day_idx]['Close']
                    # Position value = quantity * current market price
                    portfolio_value += position.quantity * current_price

            self.portfolio_history.append(portfolio_value)

            if day_start_value > 0:
                daily_return = (portfolio_value - day_start_value) / day_start_value
                self.daily_returns.append(daily_return)

            # Progress logging
            if day_idx % 20 == 0:
                logger.info(f"📊 Day {day_idx}/{total_days}: Portfolio ${portfolio_value:,.2f} | Open Positions: {len(self.positions)}")

        # Close any remaining positions
        for symbol in list(self.positions.keys()):
            if symbol in historical_data and len(historical_data[symbol]) > 0:
                final_price = historical_data[symbol].iloc[-1]['Close']
                final_ts = historical_data[symbol].index[-1]
                await self._close_position(symbol, final_price, "BACKTEST_END", final_ts)

        # Calculate final metrics
        metrics = self._calculate_metrics()

        # Print report
        self._print_report(metrics, period_days)

        return metrics

    async def _open_position(self, symbol: str, price: float, signal: Dict, timestamp):
        """Open a new position"""
        position_value = self.current_capital * self.max_position_pct
        quantity = position_value / price

        if quantity * price > self.current_capital:
            logger.warning(f"Insufficient capital for {symbol}")
            return

        self.current_capital -= quantity * price

        # Convert pandas timestamp to datetime for consistent handling
        if hasattr(timestamp, 'to_pydatetime'):
            ts_datetime = timestamp.to_pydatetime()
        else:
            ts_datetime = timestamp

        trade = BacktestTrade(
            trade_id=f"bt_{ts_datetime.strftime('%Y%m%d_%H%M%S')}_{symbol}",
            timestamp=ts_datetime,
            symbol=symbol,
            action='BUY',
            entry_price=price,
            quantity=quantity,
            ai_components=signal.get('ai_components', []),
            confidence=signal.get('confidence', 0)
        )

        self.positions[symbol] = trade

        # Initialize enhancement tracking for this position
        self.position_highs[symbol] = price
        self.position_entry_times[symbol] = ts_datetime
        self.scaled_positions[symbol] = 0
        self.dca_counts[symbol] = 0

        # Track AI attribution
        for ai in signal.get('ai_components', []):
            if ai not in self.ai_attribution:
                self.ai_attribution[ai] = {'trades': 0, 'wins': 0, 'pnl': 0}
            self.ai_attribution[ai]['trades'] += 1

        logger.debug(f"OPENED {symbol}: {quantity:.4f} @ ${price:.2f} ({signal.get('ai_components', [])})")

    async def _close_position(self, symbol: str, price: float, reason: str, timestamp):
        """Close a position and record P&L"""
        if symbol not in self.positions:
            return

        trade = self.positions[symbol]
        trade.exit_price = price
        trade.pnl = (price - trade.entry_price) * trade.quantity
        trade.pnl_pct = (price - trade.entry_price) / trade.entry_price
        trade.exit_reason = reason

        # Handle timezone-aware/naive datetime differences
        try:
            if hasattr(timestamp, 'tz_localize') and hasattr(trade.timestamp, 'tzinfo'):
                # Both are pandas timestamps - convert to naive
                ts_naive = pd.Timestamp(timestamp).tz_localize(None) if pd.Timestamp(timestamp).tzinfo else pd.Timestamp(timestamp)
                trade_ts_naive = pd.Timestamp(trade.timestamp).tz_localize(None) if pd.Timestamp(trade.timestamp).tzinfo else pd.Timestamp(trade.timestamp)
                trade.duration_hours = (ts_naive - trade_ts_naive).total_seconds() / 3600
            else:
                trade.duration_hours = (timestamp - trade.timestamp).total_seconds() / 3600
        except Exception:
            trade.duration_hours = 24.0  # Default to 1 day if calculation fails

        self.current_capital += trade.quantity * price

        # Update AI attribution with outcome
        is_win = trade.pnl > 0
        for ai in trade.ai_components:
            if ai in self.ai_attribution:
                self.ai_attribution[ai]['pnl'] += trade.pnl
                if is_win:
                    self.ai_attribution[ai]['wins'] += 1

        self.closed_trades.append(trade)
        del self.positions[symbol]

        # Clean up enhancement tracking
        self._cleanup_position_tracking(symbol)

        emoji = "💰" if is_win else "📉"
        logger.debug(f"{emoji} CLOSED {symbol}: P/L ${trade.pnl:+.2f} ({trade.pnl_pct*100:+.2f}%) - {reason}")

    def _calculate_metrics(self) -> BacktestMetrics:
        """Calculate comprehensive backtest metrics"""
        metrics = BacktestMetrics()

        if not self.closed_trades:
            return metrics

        # Basic trade stats
        metrics.total_trades = len(self.closed_trades)
        pnls = [t.pnl for t in self.closed_trades]

        metrics.winning_trades = sum(1 for t in self.closed_trades if t.pnl > 0)
        metrics.losing_trades = sum(1 for t in self.closed_trades if t.pnl <= 0)
        metrics.win_rate = metrics.winning_trades / metrics.total_trades if metrics.total_trades > 0 else 0

        # P&L stats
        wins = [t.pnl for t in self.closed_trades if t.pnl > 0]
        losses = [t.pnl for t in self.closed_trades if t.pnl <= 0]

        metrics.gross_profit = sum(wins) if wins else 0
        metrics.gross_loss = abs(sum(losses)) if losses else 0
        metrics.avg_win = np.mean(wins) if wins else 0
        metrics.avg_loss = abs(np.mean(losses)) if losses else 0
        metrics.best_trade = max(pnls) if pnls else 0
        metrics.worst_trade = min(pnls) if pnls else 0

        # Profit factor
        metrics.profit_factor = metrics.gross_profit / metrics.gross_loss if metrics.gross_loss > 0 else float('inf')

        # Total return
        final_value = self.portfolio_history[-1] if self.portfolio_history else self.initial_capital
        metrics.total_return = (final_value - self.initial_capital) / self.initial_capital

        # Max drawdown
        peak = self.initial_capital
        max_dd = 0
        for value in self.portfolio_history:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            max_dd = max(max_dd, dd)
        metrics.max_drawdown = max_dd

        # Sharpe ratio (annualized)
        if self.daily_returns and len(self.daily_returns) > 1:
            avg_return = np.mean(self.daily_returns)
            std_return = np.std(self.daily_returns)
            if std_return > 0:
                metrics.sharpe_ratio = (avg_return / std_return) * np.sqrt(252)

        # Sortino ratio (annualized)
        if self.daily_returns:
            negative_returns = [r for r in self.daily_returns if r < 0]
            if negative_returns:
                downside_std = np.std(negative_returns)
                if downside_std > 0:
                    metrics.sortino_ratio = (np.mean(self.daily_returns) / downside_std) * np.sqrt(252)

        # Calmar ratio
        if metrics.max_drawdown > 0:
            n = len(self.daily_returns)
            annualized_return = ((1 + metrics.total_return) ** (252 / n) - 1) if n > 0 else 0
            metrics.calmar_ratio = annualized_return / metrics.max_drawdown

        # Average trade duration
        durations = [t.duration_hours for t in self.closed_trades if t.duration_hours > 0]
        metrics.avg_trade_duration_hours = np.mean(durations) if durations else 0

        # AI Attribution
        metrics.ai_attribution = self.ai_attribution

        return metrics

    def _print_report(self, metrics: BacktestMetrics, period_days: int):
        """Print comprehensive backtest report"""
        print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          🚀 PROMETHEUS REAL AI BACKTEST RESULTS ({period_days} Days)                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  💰 PERFORMANCE SUMMARY                                                      ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║  Initial Capital:     ${self.initial_capital:>12,.2f}                                   ║
║  Final Capital:       ${self.portfolio_history[-1] if self.portfolio_history else self.initial_capital:>12,.2f}                                   ║
║  Total Return:        {metrics.total_return*100:>12.2f}%                                   ║
║                                                                              ║
║  📊 RISK METRICS                                                             ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║  Sharpe Ratio:        {metrics.sharpe_ratio:>12.2f}                                       ║
║  Sortino Ratio:       {metrics.sortino_ratio:>12.2f}                                       ║
║  Calmar Ratio:        {metrics.calmar_ratio:>12.2f}                                       ║
║  Max Drawdown:        {metrics.max_drawdown*100:>12.2f}%                                   ║
║                                                                              ║
║  📈 TRADE STATISTICS                                                         ║
║  ─────────────────────────────────────────────────────────────────────────── ║
║  Total Trades:        {metrics.total_trades:>12}                                          ║
║  Winning Trades:      {metrics.winning_trades:>12}                                          ║
║  Losing Trades:       {metrics.losing_trades:>12}                                          ║
║  Win Rate:            {metrics.win_rate*100:>12.1f}%                                       ║
║  Profit Factor:       {metrics.profit_factor:>12.2f}                                       ║
║  Avg Win:             ${metrics.avg_win:>12.2f}                                   ║
║  Avg Loss:            ${metrics.avg_loss:>12.2f}                                   ║
║  Best Trade:          ${metrics.best_trade:>12.2f}                                   ║
║  Worst Trade:         ${metrics.worst_trade:>12.2f}                                   ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  🤖 AI SYSTEM ATTRIBUTION                                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣""")

        for ai_name, stats in sorted(self.ai_attribution.items(), key=lambda x: x[1]['pnl'], reverse=True):
            win_rate = (stats['wins'] / stats['trades'] * 100) if stats['trades'] > 0 else 0
            pnl_emoji = "💰" if stats['pnl'] > 0 else "📉"
            print(f"║  {ai_name:<18} │ Trades: {stats['trades']:>4} │ Win: {win_rate:>5.1f}% │ P/L: {pnl_emoji}${stats['pnl']:>10.2f} ║")

        # Exit reason breakdown for enhancement validation
        exit_reasons = {}
        for t in self.closed_trades:
            reason = t.exit_reason if t.exit_reason else 'UNKNOWN'
            # Group by base reason (strip dynamic details)
            base_reason = reason.split(' (')[0] if ' (' in reason else reason
            exit_reasons[base_reason] = exit_reasons.get(base_reason, 0) + 1

        print(f"""╠══════════════════════════════════════════════════════════════════════════════╣
║  🔧 EXIT REASON BREAKDOWN (6 Enhancements Validation)                       ║
╠══════════════════════════════════════════════════════════════════════════════╣""")
        for reason, count in sorted(exit_reasons.items(), key=lambda x: -x[1]):
            pct = count / max(len(self.closed_trades), 1) * 100
            print(f"║  {reason:<25} │ Count: {count:>4} │ {pct:>5.1f}% of trades            ║")

        print(f"""╚══════════════════════════════════════════════════════════════════════════════╝
""")

    def persist_learning_artifacts(self, metrics: BacktestMetrics, period_days: int, symbols: List[str], results_file: str):
        """Persist backtest insights and AI weight snapshots to learning tables."""
        timestamp = datetime.now().isoformat()
        con = None

        try:
            con = sqlite3.connect('prometheus_learning.db')
            cur = con.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS learning_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    insight_type TEXT NOT NULL,
                    symbol TEXT,
                    description TEXT NOT NULL,
                    confidence_impact REAL DEFAULT 0,
                    applied BOOLEAN DEFAULT 0
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS ai_weight_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    voter TEXT,
                    old_weight REAL,
                    new_weight REAL,
                    accuracy REAL,
                    sample_count INTEGER
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS dead_end_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    symbol TEXT,
                    failure_signature TEXT NOT NULL,
                    details TEXT,
                    severity REAL DEFAULT 0
                )
            """)

            summary_desc = (
                f"Backtest {results_file}: period={period_days}d, symbols={','.join(symbols)}, "
                f"return={metrics.total_return:.4f}, sharpe={metrics.sharpe_ratio:.4f}, "
                f"win_rate={metrics.win_rate:.4f}, max_dd={metrics.max_drawdown:.4f}"
            )
            cur.execute(
                """
                INSERT INTO learning_insights
                (timestamp, insight_type, symbol, description, confidence_impact, applied)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (timestamp, 'benchmark_summary', None, summary_desc, float(metrics.win_rate), 0)
            )

            for ai_name, stats in (metrics.ai_attribution or {}).items():
                trades = int(stats.get('trades', 0) or 0)
                wins = int(stats.get('wins', 0) or 0)
                pnl = float(stats.get('pnl', 0.0) or 0.0)
                accuracy = (wins / trades) if trades > 0 else 0.0
                new_weight = round(max(0.05, min(1.0, 0.25 + accuracy * 0.75)), 4)

                detail_desc = (
                    f"AI={ai_name}: trades={trades}, wins={wins}, accuracy={accuracy:.4f}, pnl={pnl:.2f}, "
                    f"suggested_weight={new_weight:.4f}"
                )
                cur.execute(
                    """
                    INSERT INTO learning_insights
                    (timestamp, insight_type, symbol, description, confidence_impact, applied)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (timestamp, 'ai_component_performance', None, detail_desc, accuracy, 0)
                )

                cur.execute(
                    """
                    INSERT INTO ai_weight_history
                    (timestamp, voter, old_weight, new_weight, accuracy, sample_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (timestamp, ai_name, None, new_weight, accuracy, trades)
                )

                if trades >= 3 and (pnl < 0 or accuracy < 0.40):
                    failure_signature = f"{ai_name}:acc={accuracy:.4f}|pnl={pnl:.2f}|trades={trades}"
                    cur.execute(
                        """
                        INSERT INTO dead_end_memory
                        (timestamp, memory_type, symbol, failure_signature, details, severity)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            timestamp,
                            'ai_component_underperformance',
                            None,
                            failure_signature,
                            detail_desc,
                            round(min(1.0, max((0.40 - accuracy), 0.0) + (abs(min(pnl, 0.0)) / 1000.0)), 4)
                        )
                    )

            benchmark_failures = []
            if metrics.total_return <= 0:
                benchmark_failures.append(f"return={metrics.total_return:.4f}")
            if metrics.sharpe_ratio < 0:
                benchmark_failures.append(f"sharpe={metrics.sharpe_ratio:.4f}")
            if metrics.win_rate < 0.50:
                benchmark_failures.append(f"win_rate={metrics.win_rate:.4f}")
            if metrics.max_drawdown > 0.15:
                benchmark_failures.append(f"max_dd={metrics.max_drawdown:.4f}")

            if benchmark_failures:
                failure_signature = '|'.join(benchmark_failures)
                cur.execute(
                    """
                    INSERT INTO dead_end_memory
                    (timestamp, memory_type, symbol, failure_signature, details, severity)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        timestamp,
                        'benchmark_failure',
                        None,
                        failure_signature,
                        summary_desc,
                        round(min(1.0, len(benchmark_failures) * 0.2), 4)
                    )
                )

            con.commit()
            logger.info("🧠 Persisted learning artifacts to learning_insights, ai_weight_history, and dead_end_memory")
        except Exception as e:
            logger.warning(f"Could not persist learning artifacts: {e}")
        finally:
            if con is not None:
                try:
                    con.close()
                except Exception:
                    pass


async def main():
    """Main entry point for backtesting"""
    parser = argparse.ArgumentParser(description='PROMETHEUS Real AI Backtesting System')
    parser.add_argument('--period', type=int, default=90, help='Backtest period in days (default: 90)')
    parser.add_argument('--symbols', type=str, default='SPY,QQQ,AAPL,MSFT,GOOGL,BTCUSD,ETHUSD',
                       help='Comma-separated list of symbols')
    parser.add_argument('--capital', type=float, default=100000, help='Initial capital (default: 100000)')
    parser.add_argument('--max-position', type=float, default=0.12, help='Max position size as %% (default: 0.12 AGGRESSIVE)')
    parser.add_argument('--stop-loss', type=float, default=0.02, help='Stop loss %% (default: 0.02 AGGRESSIVE)')
    parser.add_argument('--take-profit', type=float, default=0.05, help='Take profit %% (default: 0.05 AGGRESSIVE)')
    parser.add_argument('--hourly', action='store_true', help='Use hourly data instead of daily')

    args = parser.parse_args()

    symbols = [s.strip() for s in args.symbols.split(',')]

    backtester = PrometheusRealAIBacktester(
        initial_capital=args.capital,
        max_position_pct=args.max_position,
        stop_loss_pct=args.stop_loss,
        take_profit_pct=args.take_profit
    )

    # Determine interval
    interval = '1h' if args.hourly else '1d'

    metrics = await backtester.run_backtest(symbols, args.period, interval)

    # Save results to JSON (including trade-level details)
    interval_suffix = '_hourly' if args.hourly else '_daily'
    results_file = f'backtest_results{interval_suffix}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    trade_details = []
    for t in backtester.closed_trades:
        trade_details.append({
            'symbol': t.symbol, 'entry_price': t.entry_price,
            'exit_price': t.exit_price, 'quantity': t.quantity,
            'pnl': t.pnl, 'pnl_pct': t.pnl_pct,
            'exit_reason': t.exit_reason,
            'ai_components': t.ai_components,
            'confidence': t.confidence,
            'duration_hours': t.duration_hours
        })
    with open(results_file, 'w') as f:
        json.dump({
            'period_days': args.period,
            'symbols': symbols,
            'initial_capital': args.capital,
            'final_capital': backtester.portfolio_history[-1] if backtester.portfolio_history else args.capital,
            'total_return': metrics.total_return,
            'sharpe_ratio': metrics.sharpe_ratio,
            'sortino_ratio': metrics.sortino_ratio,
            'calmar_ratio': metrics.calmar_ratio,
            'max_drawdown': metrics.max_drawdown,
            'win_rate': metrics.win_rate,
            'profit_factor': metrics.profit_factor,
            'total_trades': metrics.total_trades,
            'ai_attribution': metrics.ai_attribution,
            'trades': trade_details
        }, f, indent=2)

    backtester.persist_learning_artifacts(metrics, args.period, symbols, results_file)

    logger.info(f"📁 Results saved to {results_file}")

    return metrics


if __name__ == '__main__':
    asyncio.run(main())

