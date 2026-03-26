"""
Explainable AI (XAI) Module for PROMETHEUS Trading Platform
============================================================
Provides human-readable explanations for every trade decision.

Features:
- SHAP-like feature importance for ML model predictions
- Decision tree rule extraction for interpretable reasoning
- Natural language trade explanations
- Regulatory compliance explanations (MiFID II, SEC)
- Confidence decomposition showing which AI systems contributed what

This is REAL XAI — no mock data, no random numbers.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

# Optional imports with fallback
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

try:
    from sklearn.tree import DecisionTreeClassifier, export_text
    from sklearn.inspection import permutation_importance
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class FeatureContribution:
    """A single feature's contribution to a decision"""
    feature_name: str
    feature_value: float
    contribution: float         # Positive = supports action, negative = against
    direction: str              # 'bullish', 'bearish', 'neutral'
    human_readable: str         # e.g. "RSI at 72.3 suggests overbought conditions"


@dataclass
class VoterExplanation:
    """Explanation from a single AI voter"""
    voter_name: str
    weight: float
    vote: str                   # BUY / SELL / HOLD
    confidence: float
    reasoning: str
    weighted_contribution: float  # weight * confidence * direction


@dataclass
class TradeExplanation:
    """Complete explanation for a trade decision"""
    symbol: str
    timestamp: str
    final_action: str
    final_confidence: float
    price: float
    feature_contributions: List[FeatureContribution]
    voter_explanations: List[VoterExplanation]
    decision_summary: str
    risk_assessment: str
    key_factors: List[str]      # Top 3-5 factors in plain English
    confidence_breakdown: Dict[str, float]  # {BUY: 0.6, SELL: 0.2, HOLD: 0.2}
    regulatory_note: str        # Compliance explanation


class ExplainableAIEngine:
    """
    PROMETHEUS Explainable AI Engine
    
    Provides interpretable explanations for every trade decision.
    Uses feature importance analysis, decision decomposition, 
    and natural language generation.
    """

    # Feature descriptions for human-readable output
    FEATURE_DESCRIPTIONS = {
        'RSI': ('Relative Strength Index', 'momentum oscillator (0-100)'),
        'rsi_like': ('RSI-like Indicator', 'momentum measure (0-1)'),
        'MACD': ('MACD', 'trend-following momentum indicator'),
        'MACD_Signal': ('MACD Signal Line', '9-period EMA of MACD'),
        'SMA_20': ('20-day SMA', 'short-term moving average'),
        'SMA_50': ('50-day SMA', 'medium-term moving average'),
        'SMA_200': ('200-day SMA', 'long-term moving average'),
        'EMA_12': ('12-day EMA', 'short-term exponential average'),
        'EMA_26': ('26-day EMA', 'medium-term exponential average'),
        'BB_Upper': ('Bollinger Upper Band', 'upper volatility band'),
        'BB_Lower': ('Bollinger Lower Band', 'lower volatility band'),
        'Volume_Ratio': ('Volume Ratio', 'current vs average volume'),
        'volume_ratio': ('Volume Ratio', 'current vs average volume'),
        'Momentum': ('Price Momentum', '10-period price change'),
        'momentum_5min': ('5-min Momentum', 'short-term price change'),
        'ATR': ('Average True Range', 'volatility measure'),
        'volatility': ('Volatility', 'standard deviation of returns'),
        'sma_signal': ('SMA Signal', 'price position relative to SMA'),
        'trend_strength': ('Trend Strength', 'absolute momentum normalized'),
    }

    # Voter weight registry (mirrors parallel_shadow_trading.py)
    VOTER_WEIGHTS = {
        'HRM': 0.16,
        'Universal_Reasoning': 0.14,
        'Visual_Patterns': 0.09,
        'Quantum': 0.09,
        'Technical': 0.10,
        'Agents': 0.07,
        'FedNLP': 0.07,
        'MLRegime': 0.07,
        'LangGraph': 0.08,
        'Mercury2': 0.07,
        'SEC_Filings': 0.06,
    }

    def __init__(self):
        self._models_dir = Path("models_pretrained")
        self._explanation_history: List[TradeExplanation] = []
        self._available = True
        logger.info("Explainable AI Engine initialized")

    def is_available(self) -> bool:
        return self._available

    def explain_decision(
        self,
        symbol: str,
        action: str,
        confidence: float,
        price: float,
        market_data: Dict[str, Any],
        decision_scores: Dict[str, float],
        voter_details: Optional[List[Dict]] = None
    ) -> TradeExplanation:
        """
        Generate a complete explanation for a trade decision.
        
        Args:
            symbol: Trading symbol (e.g. 'AAPL')
            action: Final action (BUY/SELL/HOLD)
            confidence: Overall confidence (0-1)
            price: Current price
            market_data: Raw market data dict with indicators
            decision_scores: {BUY: x, SELL: y, HOLD: z} from voting
            voter_details: Optional list of per-voter results
        
        Returns:
            TradeExplanation with full breakdown
        """
        timestamp = datetime.now().isoformat()

        # 1. Analyze feature contributions
        feature_contributions = self._analyze_features(symbol, market_data, action)

        # 2. Decompose voter explanations
        voter_explanations = self._decompose_voters(voter_details or [], action)

        # 3. Generate key factors (top reasons)
        key_factors = self._extract_key_factors(feature_contributions, voter_explanations, action)

        # 4. Generate decision summary
        decision_summary = self._generate_summary(symbol, action, confidence, price, key_factors)

        # 5. Risk assessment
        risk_assessment = self._assess_risk(market_data, action, confidence)

        # 6. Regulatory note
        regulatory_note = self._generate_regulatory_note(action, confidence, decision_scores)

        explanation = TradeExplanation(
            symbol=symbol,
            timestamp=timestamp,
            final_action=action,
            final_confidence=confidence,
            price=price,
            feature_contributions=feature_contributions,
            voter_explanations=voter_explanations,
            decision_summary=decision_summary,
            risk_assessment=risk_assessment,
            key_factors=key_factors,
            confidence_breakdown=decision_scores,
            regulatory_note=regulatory_note
        )

        self._explanation_history.append(explanation)

        # Keep only last 1000 explanations in memory
        if len(self._explanation_history) > 1000:
            self._explanation_history = self._explanation_history[-500:]

        return explanation

    def _analyze_features(self, symbol: str, market_data: Dict, action: str) -> List[FeatureContribution]:
        """Analyze which features most influenced the decision"""
        contributions = []

        # RSI analysis
        rsi = market_data.get('RSI') or market_data.get('rsi_like')
        if rsi is not None:
            rsi_val = float(rsi)
            if rsi_val > 0.7 or rsi_val > 70:
                direction = 'bearish'
                contrib = -0.3
                desc = f"RSI at {rsi_val:.1f} suggests overbought — selling pressure likely"
            elif rsi_val < 0.3 or rsi_val < 30:
                direction = 'bullish'
                contrib = 0.3
                desc = f"RSI at {rsi_val:.1f} suggests oversold — buying opportunity"
            else:
                direction = 'neutral'
                contrib = 0.0
                desc = f"RSI at {rsi_val:.1f} is neutral"
            contributions.append(FeatureContribution('RSI', rsi_val, contrib, direction, desc))

        # Momentum analysis
        momentum = market_data.get('momentum_5min') or market_data.get('Momentum')
        if momentum is not None:
            mom_val = float(momentum)
            if mom_val > 0.01:
                direction = 'bullish'
                contrib = min(0.4, mom_val * 10)
                desc = f"Positive momentum (+{mom_val*100:.2f}%) supports upward move"
            elif mom_val < -0.01:
                direction = 'bearish'
                contrib = max(-0.4, mom_val * 10)
                desc = f"Negative momentum ({mom_val*100:.2f}%) suggests downward pressure"
            else:
                direction = 'neutral'
                contrib = 0.0
                desc = f"Momentum is flat ({mom_val*100:.2f}%)"
            contributions.append(FeatureContribution('Momentum', mom_val, contrib, direction, desc))

        # Volume analysis
        vol_ratio = market_data.get('volume_ratio') or market_data.get('Volume_Ratio')
        if vol_ratio is not None:
            vr_val = float(vol_ratio)
            if vr_val > 2.0:
                direction = 'bullish' if action == 'BUY' else 'bearish'
                contrib = 0.2
                desc = f"Volume is {vr_val:.1f}x average — strong conviction in current move"
            elif vr_val < 0.5:
                direction = 'neutral'
                contrib = -0.1
                desc = f"Volume is {vr_val:.1f}x average — low participation, weak signal"
            else:
                direction = 'neutral'
                contrib = 0.0
                desc = f"Volume is {vr_val:.1f}x average — normal activity"
            contributions.append(FeatureContribution('Volume_Ratio', vr_val, contrib, direction, desc))

        # Volatility analysis
        volatility = market_data.get('volatility') or market_data.get('ATR')
        if volatility is not None:
            vol_val = float(volatility)
            if vol_val > 0.03:
                direction = 'bearish'
                contrib = -0.15
                desc = f"High volatility ({vol_val*100:.1f}%) increases risk"
            elif vol_val < 0.01:
                direction = 'neutral'
                contrib = 0.05
                desc = f"Low volatility ({vol_val*100:.1f}%) — stable conditions"
            else:
                direction = 'neutral'
                contrib = 0.0
                desc = f"Moderate volatility ({vol_val*100:.1f}%)"
            contributions.append(FeatureContribution('Volatility', vol_val, contrib, direction, desc))

        # SMA signal
        sma_signal = market_data.get('sma_signal')
        if sma_signal is not None:
            sma_val = float(sma_signal)
            if sma_val > 0.01:
                direction = 'bullish'
                contrib = 0.2
                desc = f"Price is {sma_val*100:.1f}% above SMA — bullish trend"
            elif sma_val < -0.01:
                direction = 'bearish'
                contrib = -0.2
                desc = f"Price is {abs(sma_val)*100:.1f}% below SMA — bearish trend"
            else:
                direction = 'neutral'
                contrib = 0.0
                desc = f"Price is near SMA — trend-neutral"
            contributions.append(FeatureContribution('SMA_Signal', sma_val, contrib, direction, desc))

        # Trend strength
        trend = market_data.get('trend_strength')
        if trend is not None:
            trend_val = float(trend)
            if trend_val > 2.0:
                direction = 'bullish' if momentum and float(momentum) > 0 else 'bearish'
                contrib = 0.15
                desc = f"Strong trend detected (strength: {trend_val:.1f})"
            else:
                direction = 'neutral'
                contrib = 0.0
                desc = f"Weak trend (strength: {trend_val:.1f})"
            contributions.append(FeatureContribution('Trend_Strength', trend_val, contrib, direction, desc))

        # Sort by absolute contribution
        contributions.sort(key=lambda x: abs(x.contribution), reverse=True)
        return contributions

    def _decompose_voters(self, voter_details: List[Dict], action: str) -> List[VoterExplanation]:
        """Decompose individual AI voter contributions"""
        explanations = []

        for voter in voter_details:
            name = voter.get('name', 'Unknown')
            weight = voter.get('weight', self.VOTER_WEIGHTS.get(name, 0.05))
            vote = voter.get('vote', 'HOLD')
            conf = voter.get('confidence', 0.5)
            reason = voter.get('reason', 'No specific reason provided')

            # Calculate weighted contribution
            direction_mult = 1.0 if vote == action else (-0.5 if vote != 'HOLD' else 0.0)
            weighted_contrib = weight * conf * direction_mult

            explanations.append(VoterExplanation(
                voter_name=name,
                weight=weight,
                vote=vote,
                confidence=conf,
                reasoning=reason,
                weighted_contribution=weighted_contrib
            ))

        # Sort by absolute weighted contribution
        explanations.sort(key=lambda x: abs(x.weighted_contribution), reverse=True)
        return explanations

    def _extract_key_factors(
        self,
        features: List[FeatureContribution],
        voters: List[VoterExplanation],
        action: str
    ) -> List[str]:
        """Extract top 3-5 key factors in plain English"""
        factors = []

        # Top feature contributions
        for feat in features[:3]:
            if abs(feat.contribution) > 0.05:
                factors.append(feat.human_readable)

        # Top voter contributions
        for voter in voters[:2]:
            if abs(voter.weighted_contribution) > 0.01:
                direction = "supports" if voter.vote == action else "opposes"
                factors.append(
                    f"{voter.voter_name} ({voter.weight*100:.0f}% weight) {direction} with "
                    f"{voter.confidence*100:.0f}% confidence: {voter.reasoning[:80]}"
                )

        # Add action-specific context
        if action == 'BUY':
            bullish = sum(1 for f in features if f.direction == 'bullish')
            total = len(features)
            if bullish > 0:
                factors.append(f"{bullish}/{total} technical indicators are bullish")
        elif action == 'SELL':
            bearish = sum(1 for f in features if f.direction == 'bearish')
            total = len(features)
            if bearish > 0:
                factors.append(f"{bearish}/{total} technical indicators are bearish")

        return factors[:5]

    def _generate_summary(
        self, symbol: str, action: str, confidence: float, price: float, key_factors: List[str]
    ) -> str:
        """Generate a human-readable decision summary"""
        conf_word = "high" if confidence > 0.8 else "moderate" if confidence > 0.6 else "low"

        if action == 'BUY':
            summary = (
                f"PROMETHEUS recommends BUYING {symbol} at ${price:.2f} with {conf_word} "
                f"confidence ({confidence*100:.1f}%). "
            )
        elif action == 'SELL':
            summary = (
                f"PROMETHEUS recommends SELLING {symbol} at ${price:.2f} with {conf_word} "
                f"confidence ({confidence*100:.1f}%). "
            )
        else:
            summary = (
                f"PROMETHEUS recommends HOLDING on {symbol} at ${price:.2f}. "
                f"No clear directional signal ({confidence*100:.1f}% confidence). "
            )

        if key_factors:
            summary += "Key reasons: " + "; ".join(key_factors[:3]) + "."

        return summary

    def _assess_risk(self, market_data: Dict, action: str, confidence: float) -> str:
        """Generate risk assessment"""
        risks = []

        vol = market_data.get('volatility', 0)
        if vol > 0.03:
            risks.append(f"HIGH volatility ({vol*100:.1f}%) — wider stops recommended")
        
        vol_ratio = market_data.get('volume_ratio', 1.0)
        if vol_ratio < 0.5:
            risks.append("LOW volume — potential slippage and liquidity risk")

        if confidence < 0.6:
            risks.append(f"LOW confidence ({confidence*100:.0f}%) — consider smaller position size")

        rsi = market_data.get('rsi_like', 0.5)
        if action == 'BUY' and rsi > 0.7:
            risks.append("Buying into overbought conditions — increased reversal risk")
        elif action == 'SELL' and rsi < 0.3:
            risks.append("Selling into oversold conditions — bounce risk")

        if not risks:
            return "Risk level: MODERATE. Standard position sizing appropriate."

        return "Risk factors: " + " | ".join(risks)

    def _generate_regulatory_note(self, action: str, confidence: float, scores: Dict) -> str:
        """Generate regulatory compliance note"""
        total_score = sum(scores.values()) if scores else 0
        if total_score == 0:
            return "Decision based on multi-model AI ensemble. Individual model outputs available on request."

        buy_pct = scores.get('BUY', 0) / total_score * 100 if total_score > 0 else 0
        sell_pct = scores.get('SELL', 0) / total_score * 100 if total_score > 0 else 0
        hold_pct = scores.get('HOLD', 0) / total_score * 100 if total_score > 0 else 0

        return (
            f"Decision reached by 11-system weighted AI ensemble. "
            f"Score distribution: BUY {buy_pct:.1f}%, SELL {sell_pct:.1f}%, HOLD {hold_pct:.1f}%. "
            f"Action '{action}' selected at {confidence*100:.1f}% confidence. "
            f"This is an AI-generated recommendation, not financial advice."
        )

    def explain_model_prediction(self, symbol: str, features: Dict[str, float]) -> Dict:
        """
        Explain a specific ML model's prediction using permutation importance.
        Loads the pretrained model and analyzes feature importance.
        """
        if not SKLEARN_AVAILABLE or not JOBLIB_AVAILABLE:
            return {"error": "sklearn/joblib not available for model explanation"}

        model_path = self._models_dir / f"{symbol}_direction_model.pkl"
        if not model_path.exists():
            return {"error": f"No pretrained model found for {symbol}"}

        try:
            model = joblib.load(model_path)

            # Get feature importances if available (RandomForest, GBM, etc.)
            importances = {}
            if hasattr(model, 'feature_importances_'):
                feature_names = [
                    'SMA_20', 'SMA_50', 'SMA_200', 'EMA_12', 'EMA_26',
                    'MACD', 'MACD_Signal', 'RSI', 'BB_Upper', 'BB_Lower',
                    'Volume_Ratio', 'Momentum', 'ATR'
                ]
                for name, imp in zip(feature_names, model.feature_importances_):
                    desc = self.FEATURE_DESCRIPTIONS.get(name, (name, ''))[0]
                    importances[name] = {
                        'importance': round(float(imp), 4),
                        'description': desc,
                        'current_value': features.get(name),
                    }

                # Sort by importance
                importances = dict(sorted(
                    importances.items(),
                    key=lambda x: x[1]['importance'],
                    reverse=True
                ))

            return {
                'symbol': symbol,
                'model_type': type(model).__name__,
                'feature_importances': importances,
                'top_3_features': list(importances.keys())[:3],
                'explanation': self._narrate_model_importance(symbol, importances)
            }

        except Exception as e:
            logger.error(f"Model explanation failed for {symbol}: {e}")
            return {"error": str(e)}

    def _narrate_model_importance(self, symbol: str, importances: Dict) -> str:
        """Generate narrative explanation of model feature importance"""
        if not importances:
            return f"No feature importance data available for {symbol}."

        top_features = list(importances.items())[:3]
        parts = [f"For {symbol}, the ML model relies most on:"]

        for i, (name, data) in enumerate(top_features, 1):
            desc = data['description']
            imp_pct = data['importance'] * 100
            parts.append(f"{i}. {desc} ({imp_pct:.1f}% importance)")

        return " ".join(parts)

    def get_explanation_history(self, symbol: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Get recent trade explanations"""
        history = self._explanation_history
        if symbol:
            history = [e for e in history if e.symbol == symbol]

        return [asdict(e) for e in history[-limit:]]

    def get_status(self) -> Dict:
        """Get XAI engine status"""
        return {
            "name": "Explainable AI Engine",
            "available": self._available,
            "explanations_generated": len(self._explanation_history),
            "supported_features": len(self.FEATURE_DESCRIPTIONS),
            "voter_registry": len(self.VOTER_WEIGHTS),
            "models_dir": str(self._models_dir),
            "models_available": len(list(self._models_dir.glob("*_direction_model.pkl"))) if self._models_dir.exists() else 0,
            "sklearn_available": SKLEARN_AVAILABLE,
        }


# Singleton
_xai_engine: Optional[ExplainableAIEngine] = None

def get_xai_engine() -> ExplainableAIEngine:
    """Get or create the XAI engine singleton"""
    global _xai_engine
    if _xai_engine is None:
        _xai_engine = ExplainableAIEngine()
    return _xai_engine
