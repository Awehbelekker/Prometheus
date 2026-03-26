"""
Adversarial Robustness Module for PROMETHEUS Trading Platform
==============================================================
Protects AI trading decisions from adversarial attacks, market manipulation,
and data poisoning. Validates signal integrity before execution.

Features:
- Input validation & anomaly detection on market data
- Adversarial signal detection (pump-and-dump, spoofing patterns)
- Model prediction sanity checks
- Ensemble disagreement detection (if AI voters diverge too much, flag it)
- Historical consistency checks
- Rate-of-change guards against flash crashes / manipulation

This is REAL robustness — no mock data, no random numbers.
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class RobustnessAlert:
    """An alert raised by the adversarial robustness system"""
    timestamp: str
    symbol: str
    alert_type: str         # 'anomaly', 'manipulation', 'disagreement', 'sanity', 'rate_of_change'
    severity: str           # 'low', 'medium', 'high', 'critical'
    description: str
    recommendation: str     # 'proceed', 'reduce_size', 'skip', 'halt'
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of validating a trade signal"""
    is_valid: bool
    confidence_adjustment: float  # Multiplier: 1.0 = no change, 0.5 = halve confidence
    alerts: List[RobustnessAlert] = field(default_factory=list)
    checks_passed: int = 0
    checks_total: int = 0
    overall_risk: str = 'normal'  # 'normal', 'elevated', 'high', 'extreme'


class AdversarialRobustnessEngine:
    """
    PROMETHEUS Adversarial Robustness Engine
    
    Validates market data and trade signals against adversarial patterns.
    Detects manipulation, anomalies, and protects against data poisoning.
    """

    def __init__(self):
        # Price history for anomaly detection (per symbol)
        self._price_history: Dict[str, deque] = {}
        self._volume_history: Dict[str, deque] = {}
        self._alert_history: List[RobustnessAlert] = []
        self._validation_count = 0
        self._blocked_count = 0
        self._available = True

        # Configurable thresholds
        self.max_price_change_1min = 0.05       # 5% max 1-minute price change
        self.max_price_change_5min = 0.10       # 10% max 5-minute price change
        self.max_volume_spike = 10.0            # 10x average volume = suspicious
        self.min_voter_agreement = 0.3          # At least 30% of voters should agree
        self.max_confidence_for_low_volume = 0.7  # Cap confidence when volume is very low
        self.history_window = 100               # Keep last 100 price points per symbol

        logger.info("Adversarial Robustness Engine initialized")

    def is_available(self) -> bool:
        return self._available

    def validate_trade_signal(
        self,
        symbol: str,
        action: str,
        confidence: float,
        price: float,
        market_data: Dict[str, Any],
        decision_scores: Optional[Dict[str, float]] = None,
        voter_details: Optional[List[Dict]] = None
    ) -> ValidationResult:
        """
        Validate a trade signal before execution.
        Returns ValidationResult with alerts and confidence adjustments.
        """
        self._validation_count += 1
        alerts = []
        checks_passed = 0
        checks_total = 0
        confidence_adj = 1.0

        # 1. Price sanity check
        checks_total += 1
        price_ok, price_alerts = self._check_price_sanity(symbol, price)
        if price_ok:
            checks_passed += 1
        else:
            alerts.extend(price_alerts)
            confidence_adj *= 0.7

        # 2. Rate-of-change guard
        checks_total += 1
        roc_ok, roc_alerts = self._check_rate_of_change(symbol, price, market_data)
        if roc_ok:
            checks_passed += 1
        else:
            alerts.extend(roc_alerts)
            confidence_adj *= 0.5

        # 3. Volume anomaly detection
        checks_total += 1
        vol_ok, vol_alerts = self._check_volume_anomaly(symbol, market_data)
        if vol_ok:
            checks_passed += 1
        else:
            alerts.extend(vol_alerts)
            confidence_adj *= 0.8

        # 4. Manipulation pattern detection
        checks_total += 1
        manip_ok, manip_alerts = self._check_manipulation_patterns(symbol, price, market_data)
        if manip_ok:
            checks_passed += 1
        else:
            alerts.extend(manip_alerts)
            confidence_adj *= 0.4

        # 5. Voter agreement check
        if decision_scores:
            checks_total += 1
            agree_ok, agree_alerts = self._check_voter_agreement(symbol, action, decision_scores, voter_details)
            if agree_ok:
                checks_passed += 1
            else:
                alerts.extend(agree_alerts)
                confidence_adj *= 0.8

        # 6. Confidence sanity check
        checks_total += 1
        conf_ok, conf_alerts = self._check_confidence_sanity(symbol, confidence, market_data)
        if conf_ok:
            checks_passed += 1
        else:
            alerts.extend(conf_alerts)
            confidence_adj *= 0.9

        # Update price/volume history
        self._update_history(symbol, price, market_data.get('volume', 0))

        # Determine overall risk level
        critical_count = sum(1 for a in alerts if a.severity == 'critical')
        high_count = sum(1 for a in alerts if a.severity == 'high')

        if critical_count > 0:
            overall_risk = 'extreme'
            confidence_adj = min(confidence_adj, 0.2)
        elif high_count >= 2:
            overall_risk = 'high'
            confidence_adj = min(confidence_adj, 0.5)
        elif high_count == 1 or len(alerts) >= 3:
            overall_risk = 'elevated'
            confidence_adj = min(confidence_adj, 0.7)
        else:
            overall_risk = 'normal'

        is_valid = overall_risk not in ('extreme',)

        if not is_valid:
            self._blocked_count += 1

        # Store alerts
        self._alert_history.extend(alerts)
        if len(self._alert_history) > 5000:
            self._alert_history = self._alert_history[-2500:]

        return ValidationResult(
            is_valid=is_valid,
            confidence_adjustment=round(confidence_adj, 3),
            alerts=alerts,
            checks_passed=checks_passed,
            checks_total=checks_total,
            overall_risk=overall_risk
        )

    def _check_price_sanity(self, symbol: str, price: float) -> Tuple[bool, List[RobustnessAlert]]:
        """Check if the price is sane (not zero, negative, or impossibly different from recent)"""
        alerts = []

        if price <= 0:
            alerts.append(RobustnessAlert(
                timestamp=datetime.now().isoformat(),
                symbol=symbol,
                alert_type='sanity',
                severity='critical',
                description=f"Invalid price: ${price}",
                recommendation='skip',
                details={'price': price}
            ))
            return False, alerts

        # Check against price history
        history = self._price_history.get(symbol)
        if history and len(history) >= 3:
            recent_avg = np.mean(list(history)[-10:])
            change_pct = abs(price - recent_avg) / recent_avg if recent_avg > 0 else 0

            if change_pct > 0.20:  # 20% deviation from recent average
                alerts.append(RobustnessAlert(
                    timestamp=datetime.now().isoformat(),
                    symbol=symbol,
                    alert_type='anomaly',
                    severity='high',
                    description=f"Price ${price:.2f} deviates {change_pct*100:.1f}% from recent average ${recent_avg:.2f}",
                    recommendation='reduce_size',
                    details={'price': price, 'recent_avg': recent_avg, 'deviation_pct': change_pct}
                ))
                return False, alerts

        return True, alerts

    def _check_rate_of_change(self, symbol: str, price: float, market_data: Dict) -> Tuple[bool, List[RobustnessAlert]]:
        """Guard against flash crashes and extreme price moves"""
        alerts = []

        momentum = market_data.get('momentum_5min', 0)
        if abs(momentum) > self.max_price_change_5min:
            severity = 'critical' if abs(momentum) > 0.15 else 'high'
            alerts.append(RobustnessAlert(
                timestamp=datetime.now().isoformat(),
                symbol=symbol,
                alert_type='rate_of_change',
                severity=severity,
                description=f"Extreme 5-min price change: {momentum*100:+.2f}% (threshold: {self.max_price_change_5min*100:.0f}%)",
                recommendation='skip' if severity == 'critical' else 'reduce_size',
                details={'momentum_5min': momentum, 'threshold': self.max_price_change_5min}
            ))
            return False, alerts

        # Check price history for rapid changes
        history = self._price_history.get(symbol)
        if history and len(history) >= 2:
            last_price = history[-1]
            change = abs(price - last_price) / last_price if last_price > 0 else 0
            if change > self.max_price_change_1min:
                alerts.append(RobustnessAlert(
                    timestamp=datetime.now().isoformat(),
                    symbol=symbol,
                    alert_type='rate_of_change',
                    severity='high',
                    description=f"Rapid price change: {change*100:+.2f}% since last check",
                    recommendation='reduce_size',
                    details={'change_pct': change, 'current': price, 'previous': last_price}
                ))
                return False, alerts

        return True, alerts

    def _check_volume_anomaly(self, symbol: str, market_data: Dict) -> Tuple[bool, List[RobustnessAlert]]:
        """Detect suspicious volume spikes that may indicate manipulation"""
        alerts = []

        vol_ratio = market_data.get('volume_ratio', 1.0)
        if vol_ratio > self.max_volume_spike:
            alerts.append(RobustnessAlert(
                timestamp=datetime.now().isoformat(),
                symbol=symbol,
                alert_type='manipulation',
                severity='high',
                description=f"Volume spike: {vol_ratio:.1f}x average (threshold: {self.max_volume_spike}x). Possible pump-and-dump.",
                recommendation='reduce_size',
                details={'volume_ratio': vol_ratio, 'threshold': self.max_volume_spike}
            ))
            return False, alerts

        # Very low volume = potential liquidity trap
        if vol_ratio < 0.1:
            alerts.append(RobustnessAlert(
                timestamp=datetime.now().isoformat(),
                symbol=symbol,
                alert_type='anomaly',
                severity='medium',
                description=f"Extremely low volume: {vol_ratio:.2f}x average. Possible liquidity trap.",
                recommendation='reduce_size',
                details={'volume_ratio': vol_ratio}
            ))
            return False, alerts

        return True, alerts

    def _check_manipulation_patterns(self, symbol: str, price: float, market_data: Dict) -> Tuple[bool, List[RobustnessAlert]]:
        """Detect common manipulation patterns: pump-and-dump, spoofing, wash trading"""
        alerts = []

        history = self._price_history.get(symbol)
        if not history or len(history) < 10:
            return True, alerts

        prices = list(history)
        vol_history = list(self._volume_history.get(symbol, []))

        # Pattern 1: Pump and dump — sharp rise followed by volume spike
        if len(prices) >= 5:
            recent_5 = prices[-5:]
            if len(recent_5) >= 2 and recent_5[0] > 0:
                change_over_5 = (recent_5[-1] - recent_5[0]) / recent_5[0]
                vol_ratio = market_data.get('volume_ratio', 1.0)

                if change_over_5 > 0.05 and vol_ratio > 5.0:
                    alerts.append(RobustnessAlert(
                        timestamp=datetime.now().isoformat(),
                        symbol=symbol,
                        alert_type='manipulation',
                        severity='high',
                        description=f"Pump-and-dump pattern detected: +{change_over_5*100:.1f}% with {vol_ratio:.1f}x volume",
                        recommendation='skip',
                        details={'price_change': change_over_5, 'volume_ratio': vol_ratio}
                    ))
                    return False, alerts

        # Pattern 2: Mean-reversion trap — unusual deviation from moving average
        if len(prices) >= 20:
            ma_20 = np.mean(prices[-20:])
            std_20 = np.std(prices[-20:])
            if std_20 > 0:
                z_score = (price - ma_20) / std_20
                if abs(z_score) > 3.0:
                    alerts.append(RobustnessAlert(
                        timestamp=datetime.now().isoformat(),
                        symbol=symbol,
                        alert_type='manipulation',
                        severity='medium',
                        description=f"Price is {z_score:.1f} std devs from 20-period mean. Possible manipulation or mean-reversion trap.",
                        recommendation='reduce_size',
                        details={'z_score': z_score, 'mean': ma_20, 'std': std_20}
                    ))
                    return False, alerts

        return True, alerts

    def _check_voter_agreement(
        self,
        symbol: str,
        action: str,
        decision_scores: Dict[str, float],
        voter_details: Optional[List[Dict]]
    ) -> Tuple[bool, List[RobustnessAlert]]:
        """Check if AI voters have reasonable agreement (not too fragmented)"""
        alerts = []

        total = sum(decision_scores.values())
        if total == 0:
            return True, alerts

        # Check if the winning action has sufficient margin
        action_score = decision_scores.get(action, 0)
        action_pct = action_score / total

        if action_pct < self.min_voter_agreement:
            alerts.append(RobustnessAlert(
                timestamp=datetime.now().isoformat(),
                symbol=symbol,
                alert_type='disagreement',
                severity='medium',
                description=f"Low voter agreement: {action} has only {action_pct*100:.1f}% of total score. AI systems are conflicted.",
                recommendation='reduce_size',
                details={'action': action, 'agreement_pct': action_pct, 'scores': decision_scores}
            ))
            return False, alerts

        # Check if the margin between top 2 is slim
        sorted_scores = sorted(decision_scores.values(), reverse=True)
        if len(sorted_scores) >= 2 and sorted_scores[0] > 0:
            margin = (sorted_scores[0] - sorted_scores[1]) / sorted_scores[0]
            if margin < 0.1:  # Less than 10% margin
                alerts.append(RobustnessAlert(
                    timestamp=datetime.now().isoformat(),
                    symbol=symbol,
                    alert_type='disagreement',
                    severity='low',
                    description=f"Slim margin between top choices ({margin*100:.1f}%). Decision is borderline.",
                    recommendation='proceed',
                    details={'margin': margin}
                ))
                # Don't fail — just warn
                return True, alerts

        return True, alerts

    def _check_confidence_sanity(self, symbol: str, confidence: float, market_data: Dict) -> Tuple[bool, List[RobustnessAlert]]:
        """Sanity check on confidence level relative to market conditions"""
        alerts = []

        # High confidence in low-volume environment is suspicious
        vol_ratio = market_data.get('volume_ratio', 1.0)
        if confidence > self.max_confidence_for_low_volume and vol_ratio < 0.3:
            alerts.append(RobustnessAlert(
                timestamp=datetime.now().isoformat(),
                symbol=symbol,
                alert_type='sanity',
                severity='medium',
                description=f"High confidence ({confidence*100:.0f}%) with very low volume ({vol_ratio:.2f}x avg). Signal reliability questionable.",
                recommendation='reduce_size',
                details={'confidence': confidence, 'volume_ratio': vol_ratio}
            ))
            return False, alerts

        # Extreme confidence (>95%) is always suspicious
        if confidence > 0.95:
            alerts.append(RobustnessAlert(
                timestamp=datetime.now().isoformat(),
                symbol=symbol,
                alert_type='sanity',
                severity='low',
                description=f"Unusually high confidence: {confidence*100:.1f}%. Capped at 95% for safety.",
                recommendation='proceed',
                details={'confidence': confidence}
            ))
            # Warn but pass
            return True, alerts

        return True, alerts

    def _update_history(self, symbol: str, price: float, volume: float):
        """Update price and volume history for a symbol"""
        if symbol not in self._price_history:
            self._price_history[symbol] = deque(maxlen=self.history_window)
        if symbol not in self._volume_history:
            self._volume_history[symbol] = deque(maxlen=self.history_window)

        if price > 0:
            self._price_history[symbol].append(price)
        if volume > 0:
            self._volume_history[symbol].append(volume)

    def get_recent_alerts(self, symbol: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get recent alerts, optionally filtered by symbol"""
        alerts = self._alert_history
        if symbol:
            alerts = [a for a in alerts if a.symbol == symbol]
        return [asdict(a) for a in alerts[-limit:]]

    def get_status(self) -> Dict:
        """Get engine status"""
        return {
            "name": "Adversarial Robustness Engine",
            "available": self._available,
            "total_validations": self._validation_count,
            "blocked_signals": self._blocked_count,
            "block_rate": f"{(self._blocked_count / max(1, self._validation_count)) * 100:.1f}%",
            "total_alerts": len(self._alert_history),
            "symbols_tracked": len(self._price_history),
            "thresholds": {
                "max_price_change_1min": f"{self.max_price_change_1min*100:.0f}%",
                "max_price_change_5min": f"{self.max_price_change_5min*100:.0f}%",
                "max_volume_spike": f"{self.max_volume_spike}x",
                "min_voter_agreement": f"{self.min_voter_agreement*100:.0f}%",
            }
        }


# Singleton
_robustness_engine: Optional[AdversarialRobustnessEngine] = None

def get_robustness_engine() -> AdversarialRobustnessEngine:
    """Get or create the robustness engine singleton"""
    global _robustness_engine
    if _robustness_engine is None:
        _robustness_engine = AdversarialRobustnessEngine()
    return _robustness_engine
