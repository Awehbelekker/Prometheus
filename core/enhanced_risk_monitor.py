"""
Enhanced Risk Monitoring Module
Real-time risk tracking and enforcement
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RiskMetrics:
    """Risk metrics tracking"""
    position_size: float
    portfolio_heat: float
    daily_loss: float
    correlated_positions: int
    max_beta: float
    timestamp: datetime

class EnhancedRiskMonitor:
    """Enhanced risk monitoring with real-time tracking"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.current_metrics = RiskMetrics(
            position_size=0.0,
            portfolio_heat=0.0,
            daily_loss=0.0,
            correlated_positions=0,
            max_beta=0.0,
            timestamp=datetime.utcnow()
        )
        self.alerts = []
    
    def check_position_size(self, position_size: float) -> tuple[bool, str]:
        """Check if position size is within limits"""
        max_size = self.config['position_sizing']['max_per_trade']
        
        if position_size > max_size:
            return False, f"Position size {position_size:.1%} exceeds limit {max_size:.1%}"
        
        # Check warning threshold
        warning_threshold = self.config['risk_monitoring']['alert_thresholds']['position_size_warning']
        if position_size > warning_threshold:
            self.alerts.append(f"Position size {position_size:.1%} approaching limit")
        
        return True, "Position size OK"
    
    def check_portfolio_heat(self, portfolio_heat: float) -> tuple[bool, str]:
        """Check if portfolio heat is within limits"""
        max_heat = self.config['portfolio_heat']['max_total_risk']
        
        if portfolio_heat > max_heat:
            return False, f"Portfolio heat {portfolio_heat:.1%} exceeds limit {max_heat:.1%}"
        
        # Check warning threshold
        warning_threshold = self.config['risk_monitoring']['alert_thresholds']['portfolio_heat_warning']
        if portfolio_heat > warning_threshold:
            self.alerts.append(f"Portfolio heat {portfolio_heat:.1%} approaching limit")
        
        return True, "Portfolio heat OK"
    
    def check_correlation(self, correlated_count: int) -> tuple[bool, str]:
        """Check if correlation is within limits"""
        max_correlated = self.config['correlation']['max_correlated_positions']
        
        if correlated_count > max_correlated:
            return False, f"Correlated positions {correlated_count} exceeds limit {max_correlated}"
        
        return True, "Correlation OK"
    
    def check_daily_loss(self, daily_loss: float) -> tuple[bool, str]:
        """Check if daily loss is within limits"""
        max_loss = self.config['circuit_breaker']['daily_loss_limit']
        
        if daily_loss > max_loss:
            return False, f"Daily loss {daily_loss:.1%} exceeds limit {max_loss:.1%}"
        
        # Check warning threshold
        warning_threshold = self.config['risk_monitoring']['alert_thresholds']['daily_loss_warning']
        if daily_loss > warning_threshold:
            self.alerts.append(f"Daily loss {daily_loss:.1%} approaching limit")
        
        return True, "Daily loss OK"
    
    def get_alerts(self) -> List[str]:
        """Get current risk alerts"""
        return self.alerts.copy()
    
    def clear_alerts(self):
        """Clear risk alerts"""
        self.alerts = []
