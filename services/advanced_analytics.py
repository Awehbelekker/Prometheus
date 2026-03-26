#!/usr/bin/env python3
"""
Advanced Analytics Engine for Prometheus Trading Platform
Deep market insights, predictive analytics, and comprehensive performance analysis
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import json
import sqlite3
from enum import Enum
import matplotlib.pyplot as plt
try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    sns = None
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types of analytics"""
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    RISK_ANALYSIS = "risk_analysis"
    MARKET_SENTIMENT = "market_sentiment"
    CORRELATION_MATRIX = "correlation_matrix"
    VOLATILITY_ANALYSIS = "volatility_analysis"
    PERFORMANCE_ATTRIBUTION = "performance_attribution"
    SECTOR_ANALYSIS = "sector_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    PREDICTIVE_MODELING = "predictive_modeling"
    BACKTESTING = "backtesting"

class RiskLevel(Enum):
    """Risk assessment levels"""
    VERY_LOW = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    VERY_HIGH = 5

@dataclass
class PortfolioMetrics:
    """Comprehensive portfolio performance metrics"""
    total_value: float
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    beta: float
    alpha: float
    information_ratio: float
    tracking_error: float
    var_95: float  # Value at Risk 95%
    cvar_95: float  # Conditional VaR 95%
    win_rate: float
    profit_factor: float
    avg_winning_trade: float
    avg_losing_trade: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int
    total_trades: int
    profitable_trades: int

@dataclass
class RiskMetrics:
    """Risk analysis metrics"""
    portfolio_risk: RiskLevel
    concentration_risk: float
    sector_exposure: Dict[str, float]
    geographic_exposure: Dict[str, float]
    currency_exposure: Dict[str, float]
    liquidity_risk: float
    counterparty_risk: float
    market_risk: float
    credit_risk: float
    operational_risk: float
    tail_risk: float
    stress_test_results: Dict[str, float]

@dataclass
class MarketInsight:
    """Individual market insight"""
    insight_id: str
    category: str
    title: str
    description: str
    confidence: float
    impact_score: float
    time_horizon: str
    symbols_affected: List[str]
    recommendations: List[str]
    supporting_data: Dict[str, Any]
    created_at: datetime

@dataclass
class PredictiveModel:
    """Predictive model results"""
    model_type: str
    symbol: str
    prediction_horizon: str
    predicted_price: float
    confidence_interval: Tuple[float, float]
    probability_up: float
    probability_down: float
    feature_importance: Dict[str, float]
    model_accuracy: float
    last_updated: datetime

class AdvancedAnalyticsEngine:
    """Main analytics engine with comprehensive market analysis"""
    
    def __init__(self):
        self.db_path = "analytics.db"
        self.models = {}
        self.cache = {}
        self.init_database()
        
    def init_database(self):
        """Initialize analytics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Portfolio analysis results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_analysis (
                analysis_id TEXT PRIMARY KEY,
                user_id TEXT,
                analysis_type TEXT,
                results TEXT,  -- JSON
                created_at TIMESTAMP,
                valid_until TIMESTAMP
            )
        ''')
        
        # Market insights
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_insights (
                insight_id TEXT PRIMARY KEY,
                category TEXT,
                title TEXT,
                description TEXT,
                confidence REAL,
                impact_score REAL,
                time_horizon TEXT,
                symbols_affected TEXT,  -- JSON
                recommendations TEXT,   -- JSON
                supporting_data TEXT,   -- JSON
                created_at TIMESTAMP
            )
        ''')
        
        # Predictive models
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictive_models (
                model_id TEXT PRIMARY KEY,
                model_type TEXT,
                symbol TEXT,
                prediction_horizon TEXT,
                predicted_price REAL,
                confidence_lower REAL,
                confidence_upper REAL,
                probability_up REAL,
                probability_down REAL,
                feature_importance TEXT,  -- JSON
                model_accuracy REAL,
                created_at TIMESTAMP,
                valid_until TIMESTAMP
            )
        ''')
        
        # Performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_tracking (
                user_id TEXT,
                date DATE,
                portfolio_value REAL,
                daily_return REAL,
                benchmark_return REAL,
                alpha REAL,
                beta REAL,
                sharpe_ratio REAL,
                PRIMARY KEY (user_id, date)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    async def analyze_portfolio(self, user_id: str, portfolio_data: Dict[str, Any],
                              benchmark_data: pd.DataFrame = None) -> PortfolioMetrics:
        """Comprehensive portfolio analysis"""
        try:
            # Extract portfolio time series
            portfolio_values = pd.Series(portfolio_data.get('values', []))
            portfolio_returns = portfolio_values.pct_change().dropna()
            
            if len(portfolio_returns) < 30:
                logger.warning("Insufficient data for comprehensive analysis")
                return self._create_basic_metrics(portfolio_data)
            
            # Calculate performance metrics
            total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) - 1
            annualized_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
            volatility = portfolio_returns.std() * np.sqrt(252)
            
            # Risk-adjusted returns
            risk_free_rate = 0.02  # Assume 2% risk-free rate
            excess_returns = portfolio_returns - (risk_free_rate / 252)
            sharpe_ratio = excess_returns.mean() / portfolio_returns.std() * np.sqrt(252)
            
            # Sortino ratio (downside deviation)
            negative_returns = portfolio_returns[portfolio_returns < 0]
            downside_std = negative_returns.std() * np.sqrt(252)
            sortino_ratio = annualized_return / downside_std if downside_std > 0 else 0
            
            # Maximum drawdown
            cumulative = (1 + portfolio_returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # Calmar ratio
            calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
            
            # Market benchmark analysis
            beta, alpha = 0.0, 0.0
            information_ratio, tracking_error = 0.0, 0.0
            
            if benchmark_data is not None and len(benchmark_data) >= len(portfolio_returns):
                benchmark_returns = benchmark_data.pct_change().dropna()
                if len(benchmark_returns) >= len(portfolio_returns):
                    # Align data
                    aligned_port = portfolio_returns[-len(benchmark_returns):]
                    covariance = np.cov(aligned_port, benchmark_returns)[0, 1]
                    market_variance = benchmark_returns.var()
                    beta = covariance / market_variance if market_variance > 0 else 0
                    
                    # Alpha calculation
                    benchmark_return = benchmark_returns.mean() * 252
                    alpha = annualized_return - (risk_free_rate + beta * (benchmark_return - risk_free_rate))
                    
                    # Information ratio and tracking error
                    active_returns = aligned_port - benchmark_returns
                    tracking_error = active_returns.std() * np.sqrt(252)
                    information_ratio = active_returns.mean() / active_returns.std() * np.sqrt(252) if active_returns.std() > 0 else 0
            
            # Value at Risk (VaR) and Conditional VaR
            var_95 = np.percentile(portfolio_returns, 5)
            cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
            
            # Trade-level analysis
            trades_data = portfolio_data.get('trades', [])
            trade_metrics = self._analyze_trades(trades_data)
            
            metrics = PortfolioMetrics(
                total_value=portfolio_values.iloc[-1],
                total_return=total_return,
                annualized_return=annualized_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                max_drawdown=max_drawdown,
                calmar_ratio=calmar_ratio,
                beta=beta,
                alpha=alpha,
                information_ratio=information_ratio,
                tracking_error=tracking_error,
                var_95=var_95,
                cvar_95=cvar_95,
                win_rate=trade_metrics.get('win_rate', 0.0),
                profit_factor=trade_metrics.get('profit_factor', 0.0),
                avg_winning_trade=trade_metrics.get('avg_winning_trade', 0.0),
                avg_losing_trade=trade_metrics.get('avg_losing_trade', 0.0),
                largest_win=trade_metrics.get('largest_win', 0.0),
                largest_loss=trade_metrics.get('largest_loss', 0.0),
                consecutive_wins=trade_metrics.get('consecutive_wins', 0),
                consecutive_losses=trade_metrics.get('consecutive_losses', 0),
                total_trades=trade_metrics.get('total_trades', 0),
                profitable_trades=trade_metrics.get('profitable_trades', 0)
            )
            
            # Store results
            await self._store_analysis_results(user_id, AnalysisType.PORTFOLIO_ANALYSIS, asdict(metrics))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Portfolio analysis error: {e}")
            return self._create_basic_metrics(portfolio_data)
    
    def _analyze_trades(self, trades_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze individual trade performance"""
        if not trades_data:
            return {}
        
        profits = [trade.get('profit', 0) for trade in trades_data]
        winning_trades = [p for p in profits if p > 0]
        losing_trades = [p for p in profits if p < 0]
        
        total_trades = len(trades_data)
        profitable_trades = len(winning_trades)
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0
        
        avg_winning_trade = np.mean(winning_trades) if winning_trades else 0
        avg_losing_trade = np.mean(losing_trades) if losing_trades else 0
        
        gross_profit = sum(winning_trades)
        gross_loss = abs(sum(losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        largest_win = max(winning_trades) if winning_trades else 0
        largest_loss = min(losing_trades) if losing_trades else 0
        
        # Consecutive wins/losses
        consecutive_wins = consecutive_losses = 0
        current_wins = current_losses = 0
        
        for profit in profits:
            if profit > 0:
                current_wins += 1
                current_losses = 0
                consecutive_wins = max(consecutive_wins, current_wins)
            elif profit < 0:
                current_losses += 1
                current_wins = 0
                consecutive_losses = max(consecutive_losses, current_losses)
        
        return {
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'win_rate': win_rate,
            'avg_winning_trade': avg_winning_trade,
            'avg_losing_trade': avg_losing_trade,
            'profit_factor': profit_factor,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'consecutive_wins': consecutive_wins,
            'consecutive_losses': consecutive_losses
        }
    
    async def analyze_risk(self, portfolio_data: Dict[str, Any]) -> RiskMetrics:
        """Comprehensive risk analysis"""
        try:
            positions = portfolio_data.get('positions', [])
            total_value = portfolio_data.get('total_value', 1.0)
            
            # Concentration risk
            position_weights = [pos.get('value', 0) / total_value for pos in positions]
            concentration_risk = max(position_weights) if position_weights else 0
            
            # Sector exposure
            sector_exposure = {}
            for pos in positions:
                sector = pos.get('sector', 'Unknown')
                weight = pos.get('value', 0) / total_value
                sector_exposure[sector] = sector_exposure.get(sector, 0) + weight
            
            # Geographic exposure (mock data)
            geographic_exposure = {
                'US': 0.6, 'Europe': 0.2, 'Asia': 0.15, 'Other': 0.05
            }
            
            # Currency exposure (mock data)
            currency_exposure = {
                'USD': 0.7, 'EUR': 0.15, 'JPY': 0.1, 'Other': 0.05
            }
            
            # Risk level assessment
            risk_factors = [
                concentration_risk * 10,  # High concentration = high risk
                len(positions) / 20,  # Fewer positions = higher risk
                portfolio_data.get('volatility', 0.2) * 5  # High volatility = high risk
            ]
            
            avg_risk = np.mean(risk_factors)
            if avg_risk < 1: portfolio_risk = RiskLevel.VERY_LOW
            elif avg_risk < 2: portfolio_risk = RiskLevel.LOW
            elif avg_risk < 3: portfolio_risk = RiskLevel.MODERATE
            elif avg_risk < 4: portfolio_risk = RiskLevel.HIGH
            else: portfolio_risk = RiskLevel.VERY_HIGH
            
            # Stress test scenarios
            stress_test_results = {
                'market_crash_2008': -0.37,  # 37% loss
                'covid_2020': -0.34,         # 34% loss
                'dot_com_2000': -0.49,       # 49% loss
                'interest_rate_shock': -0.15, # 15% loss
                'currency_crisis': -0.08     # 8% loss
            }
            
            risk_metrics = RiskMetrics(
                portfolio_risk=portfolio_risk,
                concentration_risk=concentration_risk,
                sector_exposure=sector_exposure,
                geographic_exposure=geographic_exposure,
                currency_exposure=currency_exposure,
                liquidity_risk=0.1,      # Mock values
                counterparty_risk=0.05,
                market_risk=0.2,
                credit_risk=0.03,
                operational_risk=0.02,
                tail_risk=0.15,
                stress_test_results=stress_test_results
            )
            
            # Store results
            await self._store_analysis_results("risk", AnalysisType.RISK_ANALYSIS, asdict(risk_metrics))
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"Risk analysis error: {e}")
            return RiskMetrics(
                portfolio_risk=RiskLevel.MODERATE,
                concentration_risk=0.0,
                sector_exposure={},
                geographic_exposure={},
                currency_exposure={},
                liquidity_risk=0.0,
                counterparty_risk=0.0,
                market_risk=0.0,
                credit_risk=0.0,
                operational_risk=0.0,
                tail_risk=0.0,
                stress_test_results={}
            )
    
    async def generate_market_insights(self, market_data: Dict[str, Any]) -> List[MarketInsight]:
        """Generate AI-powered market insights"""
        insights = []
        
        try:
            # Market sentiment analysis
            sentiment_score = market_data.get('sentiment', 0.0)
            if abs(sentiment_score) > 0.7:
                sentiment_insight = MarketInsight(
                    insight_id=f"sentiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category="Market Sentiment",
                    title="Extreme Market Sentiment Detected",
                    description=f"Market sentiment is showing extreme {'bullish' if sentiment_score > 0 else 'bearish'} conditions ({sentiment_score:.2f}). This often precedes reversals.",
                    confidence=0.8,
                    impact_score=abs(sentiment_score),
                    time_horizon="1-2 weeks",
                    symbols_affected=["SPY", "QQQ", "IWM"],
                    recommendations=[
                        "Consider contrarian positions",
                        "Reduce position sizes",
                        "Monitor for reversal signals"
                    ],
                    supporting_data={"sentiment_score": sentiment_score},
                    created_at=datetime.now()
                )
                insights.append(sentiment_insight)
            
            # Volatility analysis
            vix = market_data.get('vix', 20)
            if vix > 30:
                volatility_insight = MarketInsight(
                    insight_id=f"volatility_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category="Volatility",
                    title="High Volatility Environment",
                    description=f"VIX at {vix:.1f} indicates elevated fear and uncertainty. Markets may experience large swings.",
                    confidence=0.9,
                    impact_score=min(vix / 50, 1.0),
                    time_horizon="1-4 weeks",
                    symbols_affected=["VIX", "SPY", "UVXY"],
                    recommendations=[
                        "Reduce leverage",
                        "Consider hedging strategies",
                        "Look for volatility mean reversion"
                    ],
                    supporting_data={"vix": vix},
                    created_at=datetime.now()
                )
                insights.append(volatility_insight)
            
            # Sector rotation analysis
            sector_performance = market_data.get('sector_performance', {})
            if sector_performance:
                top_sector = max(sector_performance, key=sector_performance.get)
                bottom_sector = min(sector_performance, key=sector_performance.get)
                
                if sector_performance[top_sector] - sector_performance[bottom_sector] > 0.1:
                    rotation_insight = MarketInsight(
                        insight_id=f"rotation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        category="Sector Rotation",
                        title="Strong Sector Rotation Detected",
                        description=f"{top_sector} outperforming {bottom_sector} by {(sector_performance[top_sector] - sector_performance[bottom_sector])*100:.1f}%",
                        confidence=0.7,
                        impact_score=0.6,
                        time_horizon="2-8 weeks",
                        symbols_affected=[],
                        recommendations=[
                            f"Consider overweight {top_sector}",
                            f"Reduce exposure to {bottom_sector}",
                            "Monitor rotation sustainability"
                        ],
                        supporting_data=sector_performance,
                        created_at=datetime.now()
                    )
                    insights.append(rotation_insight)
            
            # Store insights
            for insight in insights:
                await self._store_market_insight(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Market insights generation error: {e}")
            return []
    
    async def create_predictive_model(self, symbol: str, price_data: pd.DataFrame,
                                    features_data: Dict[str, Any]) -> PredictiveModel:
        """Create and train predictive model for price forecasting"""
        try:
            if len(price_data) < 100:
                logger.warning(f"Insufficient data for {symbol} prediction model")
                return None
            
            # Prepare features
            prices = price_data['close'].values
            returns = pd.Series(prices).pct_change().dropna()
            
            # Technical indicators as features
            price_df = pd.DataFrame({'close': prices})
            
            # Moving averages
            price_df['ma_5'] = price_df['close'].rolling(5).mean()
            price_df['ma_20'] = price_df['close'].rolling(20).mean()
            price_df['ma_50'] = price_df['close'].rolling(50).mean()
            
            # RSI
            delta = price_df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            price_df['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            ema_12 = price_df['close'].ewm(span=12).mean()
            ema_26 = price_df['close'].ewm(span=26).mean()
            price_df['macd'] = ema_12 - ema_26
            
            # Bollinger Bands
            bb_ma = price_df['close'].rolling(20).mean()
            bb_std = price_df['close'].rolling(20).std()
            price_df['bb_upper'] = bb_ma + (2 * bb_std)
            price_df['bb_lower'] = bb_ma - (2 * bb_std)
            price_df['bb_position'] = (price_df['close'] - price_df['bb_lower']) / (price_df['bb_upper'] - price_df['bb_lower'])
            
            # Volume features (if available)
            if 'volume' in price_data.columns:
                price_df['volume'] = price_data['volume'].values
                price_df['volume_ma'] = price_df['volume'].rolling(20).mean()
                price_df['volume_ratio'] = price_df['volume'] / price_df['volume_ma']
            
            # Prepare training data
            feature_cols = ['ma_5', 'ma_20', 'ma_50', 'rsi', 'macd', 'bb_position']
            if 'volume_ratio' in price_df.columns:
                feature_cols.append('volume_ratio')
            
            # Create target (next day return)
            price_df['future_return'] = price_df['close'].shift(-1) / price_df['close'] - 1
            
            # Remove NaN values
            clean_data = price_df.dropna()
            
            if len(clean_data) < 50:
                logger.warning(f"Insufficient clean data for {symbol} model")
                return None
            
            X = clean_data[feature_cols].values
            y = clean_data['future_return'].values[:-1]  # Remove last value (no future return)
            X = X[:-1]  # Align with y
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            # Use 80% for training, 20% for testing
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            model.fit(X_train, y_train)
            
            # Evaluate model
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            model_accuracy = (train_score + test_score) / 2
            
            # Make prediction
            latest_features = X[-1].reshape(1, -1)
            predicted_return = model.predict(latest_features)[0]
            current_price = prices[-1]
            predicted_price = current_price * (1 + predicted_return)
            
            # Feature importance
            feature_importance = dict(zip(feature_cols, model.feature_importances_))
            
            # Confidence interval (simplified)
            prediction_std = np.std(model.predict(X_test) - y_test)
            confidence_lower = predicted_price - (1.96 * prediction_std * current_price)
            confidence_upper = predicted_price + (1.96 * prediction_std * current_price)
            
            # Probability calculations
            probability_up = 0.5 + (predicted_return * 2)  # Simplified
            probability_up = max(0, min(1, probability_up))
            probability_down = 1 - probability_up
            
            prediction_model = PredictiveModel(
                model_type="RandomForest",
                symbol=symbol,
                prediction_horizon="1 day",
                predicted_price=predicted_price,
                confidence_interval=(confidence_lower, confidence_upper),
                probability_up=probability_up,
                probability_down=probability_down,
                feature_importance=feature_importance,
                model_accuracy=model_accuracy,
                last_updated=datetime.now()
            )
            
            # Store model
            await self._store_predictive_model(prediction_model)
            
            return prediction_model
            
        except Exception as e:
            logger.error(f"Predictive model creation error for {symbol}: {e}")
            return None
    
    async def detect_anomalies(self, portfolio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in trading patterns and portfolio behavior"""
        anomalies = []
        
        try:
            returns = portfolio_data.get('returns', [])
            if len(returns) < 30:
                return anomalies
            
            returns_array = np.array(returns).reshape(-1, 1)
            
            # Use Isolation Forest for anomaly detection
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomaly_labels = iso_forest.fit_predict(returns_array)
            
            # Statistical anomalies
            returns_series = pd.Series(returns)
            mean_return = returns_series.mean()
            std_return = returns_series.std()
            
            for i, (return_val, is_anomaly) in enumerate(zip(returns, anomaly_labels)):
                if is_anomaly == -1:  # Anomaly detected
                    z_score = abs((return_val - mean_return) / std_return)
                    
                    anomaly = {
                        'type': 'statistical',
                        'date_index': i,
                        'value': return_val,
                        'z_score': z_score,
                        'severity': 'high' if z_score > 3 else 'medium' if z_score > 2 else 'low',
                        'description': f"Unusual return of {return_val:.2%} (Z-score: {z_score:.2f})"
                    }
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            return []
    
    async def correlation_analysis(self, symbols: List[str], 
                                 price_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Analyze correlations between different assets"""
        try:
            if len(symbols) < 2:
                return {}
            
            # Align all price data
            aligned_data = {}
            min_length = float('inf')
            
            for symbol in symbols:
                if symbol in price_data and len(price_data[symbol]) > 0:
                    returns = price_data[symbol]['close'].pct_change().dropna()
                    aligned_data[symbol] = returns
                    min_length = min(min_length, len(returns))
            
            if len(aligned_data) < 2 or min_length < 30:
                return {}
            
            # Align all series to same length
            for symbol in aligned_data:
                aligned_data[symbol] = aligned_data[symbol][-min_length:]
            
            # Create correlation matrix
            correlation_df = pd.DataFrame(aligned_data)
            correlation_matrix = correlation_df.corr()
            
            # Find strongest correlations
            strong_correlations = []
            for i in range(len(symbols)):
                for j in range(i + 1, len(symbols)):
                    if symbols[i] in correlation_matrix.index and symbols[j] in correlation_matrix.columns:
                        corr_value = correlation_matrix.loc[symbols[i], symbols[j]]
                        if abs(corr_value) > 0.7:
                            strong_correlations.append({
                                'pair': [symbols[i], symbols[j]],
                                'correlation': corr_value,
                                'strength': 'very_strong' if abs(corr_value) > 0.9 else 'strong'
                            })
            
            # Portfolio diversification analysis
            avg_correlation = correlation_matrix.mean().mean()
            diversification_score = 1 - avg_correlation
            
            return {
                'correlation_matrix': correlation_matrix.to_dict(),
                'strong_correlations': strong_correlations,
                'average_correlation': avg_correlation,
                'diversification_score': diversification_score,
                'recommendation': self._get_diversification_recommendation(diversification_score)
            }
            
        except Exception as e:
            logger.error(f"Correlation analysis error: {e}")
            return {}
    
    def _get_diversification_recommendation(self, score: float) -> str:
        """Get diversification recommendation based on score"""
        if score > 0.8:
            return "Excellent diversification"
        elif score > 0.6:
            return "Good diversification"
        elif score > 0.4:
            return "Moderate diversification - consider adding uncorrelated assets"
        else:
            return "Poor diversification - portfolio may be over-concentrated"
    
    async def _store_analysis_results(self, user_id: str, analysis_type: AnalysisType, results: Dict[str, Any]):
        """Store analysis results in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            analysis_id = f"{user_id}_{analysis_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            valid_until = datetime.now() + timedelta(hours=24)
            
            # Convert RiskLevel enum to string for JSON serialization
            if 'portfolio_risk' in results and hasattr(results['portfolio_risk'], 'name'):
                results['portfolio_risk'] = results['portfolio_risk'].name
            
            cursor.execute('''
                INSERT INTO portfolio_analysis 
                (analysis_id, user_id, analysis_type, results, created_at, valid_until)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (analysis_id, user_id, analysis_type.value, json.dumps(results, default=str),
                  datetime.now(), valid_until))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing analysis results: {e}")
    
    async def _store_market_insight(self, insight: MarketInsight):
        """Store market insight in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO market_insights 
                (insight_id, category, title, description, confidence, impact_score,
                 time_horizon, symbols_affected, recommendations, supporting_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (insight.insight_id, insight.category, insight.title, insight.description,
                  insight.confidence, insight.impact_score, insight.time_horizon,
                  json.dumps(insight.symbols_affected), json.dumps(insight.recommendations),
                  json.dumps(insight.supporting_data), insight.created_at))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing market insight: {e}")
    
    async def _store_predictive_model(self, model: PredictiveModel):
        """Store predictive model results in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            model_id = f"{model.symbol}_{model.model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            valid_until = datetime.now() + timedelta(hours=6)  # Models valid for 6 hours
            
            cursor.execute('''
                INSERT INTO predictive_models 
                (model_id, model_type, symbol, prediction_horizon, predicted_price,
                 confidence_lower, confidence_upper, probability_up, probability_down,
                 feature_importance, model_accuracy, created_at, valid_until)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (model_id, model.model_type, model.symbol, model.prediction_horizon,
                  model.predicted_price, model.confidence_interval[0], model.confidence_interval[1],
                  model.probability_up, model.probability_down, json.dumps(model.feature_importance),
                  model.model_accuracy, model.last_updated, valid_until))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing predictive model: {e}")
    
    def _create_basic_metrics(self, portfolio_data: Dict[str, Any]) -> PortfolioMetrics:
        """Create basic metrics when full analysis isn't possible"""
        return PortfolioMetrics(
            total_value=portfolio_data.get('total_value', 0.0),
            total_return=portfolio_data.get('total_return', 0.0),
            annualized_return=0.0,
            volatility=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            max_drawdown=0.0,
            calmar_ratio=0.0,
            beta=0.0,
            alpha=0.0,
            information_ratio=0.0,
            tracking_error=0.0,
            var_95=0.0,
            cvar_95=0.0,
            win_rate=0.0,
            profit_factor=0.0,
            avg_winning_trade=0.0,
            avg_losing_trade=0.0,
            largest_win=0.0,
            largest_loss=0.0,
            consecutive_wins=0,
            consecutive_losses=0,
            total_trades=0,
            profitable_trades=0
        )

# Global analytics engine
analytics_engine = AdvancedAnalyticsEngine()

async def demo_advanced_analytics():
    """Demo function for advanced analytics"""
    print("🚀 Prometheus Advanced Analytics Demo")
    
    # Generate mock portfolio data
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    portfolio_values = 100000 * (1 + np.cumsum(np.random.randn(len(dates)) * 0.01))
    
    portfolio_data = {
        'values': portfolio_values.tolist(),
        'total_value': portfolio_values[-1],
        'total_return': (portfolio_values[-1] / portfolio_values[0]) - 1,
        'positions': [
            {'symbol': 'AAPL', 'value': 15000, 'sector': 'Technology'},
            {'symbol': 'GOOGL', 'value': 12000, 'sector': 'Technology'},
            {'symbol': 'JPM', 'value': 10000, 'sector': 'Financial'},
            {'symbol': 'JNJ', 'value': 8000, 'sector': 'Healthcare'}
        ],
        'trades': [
            {'symbol': 'AAPL', 'profit': 150, 'return_pct': 0.02},
            {'symbol': 'GOOGL', 'profit': -75, 'return_pct': -0.01},
            {'symbol': 'MSFT', 'profit': 200, 'return_pct': 0.03}
        ]
    }
    
    # Portfolio analysis
    metrics = await analytics_engine.analyze_portfolio("demo_user", portfolio_data)
    print(f"[CHECK] Portfolio Analysis: {metrics.total_return:.2%} return, {metrics.sharpe_ratio:.2f} Sharpe")
    
    # Risk analysis
    risk_metrics = await analytics_engine.analyze_risk(portfolio_data)
    print(f"[CHECK] Risk Analysis: {risk_metrics.portfolio_risk.name} risk level")
    
    # Market insights
    market_data = {
        'sentiment': 0.8,
        'vix': 35,
        'sector_performance': {
            'Technology': 0.15,
            'Healthcare': 0.08,
            'Financial': 0.02,
            'Energy': -0.05
        }
    }
    
    insights = await analytics_engine.generate_market_insights(market_data)
    print(f"[CHECK] Generated {len(insights)} market insights")
    
    # Predictive modeling
    mock_price_data = pd.DataFrame({
        'close': np.random.randn(200).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 200)
    })
    
    model = await analytics_engine.create_predictive_model("AAPL", mock_price_data, {})
    if model:
        print(f"[CHECK] Predictive Model: {model.predicted_price:.2f} target price ({model.model_accuracy:.2%} accuracy)")
    
    # Anomaly detection
    returns = np.random.normal(0.001, 0.02, 100).tolist()
    returns[50] = 0.15  # Add anomaly
    portfolio_data['returns'] = returns
    
    anomalies = await analytics_engine.detect_anomalies(portfolio_data)
    print(f"[CHECK] Detected {len(anomalies)} anomalies")
    
    print("\n🎉 Advanced analytics demo completed!")

if __name__ == "__main__":
    asyncio.run(demo_advanced_analytics())
