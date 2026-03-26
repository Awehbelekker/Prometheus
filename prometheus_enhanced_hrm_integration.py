#!/usr/bin/env python3
"""
PROMETHEUS Enhanced HRM Integration
Integrates the enhanced HRM system with the main PROMETHEUS trading platform
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Add paths for imports
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "core"))

try:
    from enhanced_hrm_working import EnhancedHRMTradingEngine
    from core.hrm_integration import HRMReasoningContext
    ENHANCED_HRM_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced HRM not available: {e}")
    ENHANCED_HRM_AVAILABLE = False

logger = logging.getLogger(__name__)

class PROMETHEUSEnhancedHRMIntegration:
    """Integration layer between Enhanced HRM and PROMETHEUS trading system"""
    
    def __init__(self, prometheus_config: Dict[str, Any] = None):
        self.config = prometheus_config or {}
        self.enhanced_hrm = None
        self.integration_active = False
        
        # Performance tracking
        self.integration_metrics = {
            'total_integrations': 0,
            'successful_integrations': 0,
            'failed_integrations': 0,
            'average_integration_time': 0.0,
            'last_integration_time': None
        }
        
        # Initialize enhanced HRM if available
        if ENHANCED_HRM_AVAILABLE:
            try:
                self.enhanced_hrm = EnhancedHRMTradingEngine()
                logger.info("✅ Enhanced HRM integration initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Enhanced HRM: {e}")
        else:
            logger.warning("⚠️ Enhanced HRM not available for integration")
    
    async def integrate_with_trading_loop(self, trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate enhanced HRM with main trading loop"""
        try:
            start_time = datetime.now()
            self.integration_metrics['total_integrations'] += 1
            
            if not self.enhanced_hrm:
                logger.warning("⚠️ Enhanced HRM not available, skipping integration")
                return self._fallback_trading_decision(trading_data)
            
            # Convert trading data to HRM context
            context = self._convert_to_hrm_context(trading_data)
            
            # Get enhanced HRM decision
            enhanced_decision = self.enhanced_hrm.make_enhanced_decision(context)
            
            # Integrate with PROMETHEUS trading logic
            integrated_decision = await self._integrate_with_prometheus_logic(
                enhanced_decision, trading_data
            )
            
            # Update metrics
            integration_time = (datetime.now() - start_time).total_seconds()
            self._update_integration_metrics(integration_time, True)
            
            logger.info(f"✅ Enhanced HRM integration completed in {integration_time:.3f}s")
            return integrated_decision
            
        except Exception as e:
            logger.error(f"❌ Enhanced HRM integration failed: {e}")
            self._update_integration_metrics(0, False)
            return self._fallback_trading_decision(trading_data)
    
    def _convert_to_hrm_context(self, trading_data: Dict[str, Any]) -> HRMReasoningContext:
        """Convert PROMETHEUS trading data to HRM context"""
        try:
            # Extract market data
            market_data = {
                'price': trading_data.get('current_price', 100.0),
                'volume': trading_data.get('volume', 1000000),
                'symbol': trading_data.get('symbol', 'SPY'),
                'indicators': trading_data.get('technical_indicators', {})
            }
            
            # Extract user profile
            user_profile = {
                'risk_tolerance': trading_data.get('risk_tolerance', 'medium'),
                'experience': trading_data.get('experience_level', 'intermediate'),
                'account_size': trading_data.get('account_size', 10000)
            }
            
            # Extract trading history
            trading_history = trading_data.get('recent_trades', [])
            
            # Extract current portfolio
            current_portfolio = {
                'cash': trading_data.get('available_cash', 10000),
                'positions': trading_data.get('current_positions', {})
            }
            
            # Extract risk preferences
            risk_preferences = {
                'max_position_size': trading_data.get('max_position_size', 0.1),
                'stop_loss': trading_data.get('stop_loss_percentage', 0.05),
                'take_profit': trading_data.get('take_profit_percentage', 0.1)
            }
            
            # Create HRM context
            context = HRMReasoningContext(
                market_data=market_data,
                user_profile=user_profile,
                trading_history=trading_history,
                current_portfolio=current_portfolio,
                risk_preferences=risk_preferences,
                reasoning_level='HIGH_LEVEL'
            )
            
            return context
            
        except Exception as e:
            logger.error(f"❌ Context conversion failed: {e}")
            # Return minimal context
            return HRMReasoningContext(
                market_data={'price': 100.0, 'volume': 1000000, 'symbol': 'SPY'},
                user_profile={'risk_tolerance': 'medium'},
                trading_history=[],
                current_portfolio={'cash': 10000, 'positions': {}},
                risk_preferences={'max_position_size': 0.1},
                reasoning_level='HIGH_LEVEL'
            )
    
    async def _integrate_with_prometheus_logic(self, enhanced_decision: Dict[str, Any], 
                                            trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate enhanced HRM decision with PROMETHEUS trading logic"""
        try:
            # Start with enhanced HRM decision
            integrated_decision = enhanced_decision.copy()
            
            # Add PROMETHEUS-specific enhancements
            integrated_decision['prometheus_enhancements'] = {
                'market_conditions': self._assess_market_conditions(trading_data),
                'risk_adjustments': self._calculate_risk_adjustments(enhanced_decision, trading_data),
                'position_management': self._calculate_position_management(enhanced_decision, trading_data),
                'execution_strategy': self._determine_execution_strategy(enhanced_decision, trading_data)
            }
            
            # Apply PROMETHEUS risk management
            integrated_decision = self._apply_prometheus_risk_management(integrated_decision, trading_data)
            
            # Add execution metadata
            integrated_decision['execution_metadata'] = {
                'integration_timestamp': datetime.now().isoformat(),
                'prometheus_version': self.config.get('version', '1.0.0'),
                'enhanced_hrm_version': '1.0.0',
                'integration_id': f"prometheus_hrm_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            return integrated_decision
            
        except Exception as e:
            logger.error(f"❌ PROMETHEUS integration failed: {e}")
            return enhanced_decision
    
    def _assess_market_conditions(self, trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess current market conditions for PROMETHEUS"""
        try:
            conditions = {
                'volatility': 'normal',
                'trend': 'neutral',
                'liquidity': 'good',
                'market_hours': True
            }
            
            # Assess volatility
            price = trading_data.get('current_price', 100)
            indicators = trading_data.get('technical_indicators', {})
            
            if 'bollinger_upper' in indicators and 'bollinger_lower' in indicators:
                upper = float(indicators['bollinger_upper'])
                lower = float(indicators['bollinger_lower'])
                volatility = (upper - lower) / price
                
                if volatility > 0.05:
                    conditions['volatility'] = 'high'
                elif volatility < 0.02:
                    conditions['volatility'] = 'low'
            
            # Assess trend
            if 'macd' in indicators:
                macd = float(indicators['macd'])
                if macd > 0.1:
                    conditions['trend'] = 'bullish'
                elif macd < -0.1:
                    conditions['trend'] = 'bearish'
            
            # Assess liquidity
            volume = trading_data.get('volume', 1000000)
            if volume > 2000000:
                conditions['liquidity'] = 'excellent'
            elif volume < 500000:
                conditions['liquidity'] = 'poor'
            
            return conditions
            
        except Exception as e:
            logger.warning(f"⚠️ Market conditions assessment failed: {e}")
            return {'volatility': 'normal', 'trend': 'neutral', 'liquidity': 'good', 'market_hours': True}
    
    def _calculate_risk_adjustments(self, enhanced_decision: Dict[str, Any], 
                                  trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk adjustments based on PROMETHEUS logic"""
        try:
            adjustments = {
                'position_size_multiplier': 1.0,
                'stop_loss_adjustment': 0.0,
                'take_profit_adjustment': 0.0,
                'confidence_threshold': 0.6
            }
            
            # Adjust based on market conditions
            market_conditions = self._assess_market_conditions(trading_data)
            
            if market_conditions['volatility'] == 'high':
                adjustments['position_size_multiplier'] = 0.7
                adjustments['stop_loss_adjustment'] = 0.02  # Tighter stop loss
            elif market_conditions['volatility'] == 'low':
                adjustments['position_size_multiplier'] = 1.2
                adjustments['stop_loss_adjustment'] = -0.01  # Wider stop loss
            
            # Adjust based on confidence
            confidence = enhanced_decision.get('confidence', 0.5)
            if confidence > 0.8:
                adjustments['position_size_multiplier'] *= 1.1
            elif confidence < 0.4:
                adjustments['position_size_multiplier'] *= 0.8
            
            return adjustments
            
        except Exception as e:
            logger.warning(f"⚠️ Risk adjustments calculation failed: {e}")
            return {'position_size_multiplier': 1.0, 'stop_loss_adjustment': 0.0, 
                   'take_profit_adjustment': 0.0, 'confidence_threshold': 0.6}
    
    def _calculate_position_management(self, enhanced_decision: Dict[str, Any], 
                                     trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate position management parameters"""
        try:
            position_management = {
                'max_position_size': enhanced_decision.get('position_size', 0.1),
                'entry_strategy': 'market',
                'exit_strategy': 'trailing_stop',
                'rebalance_frequency': 'daily'
            }
            
            # Adjust based on account size
            account_size = trading_data.get('account_size', 10000)
            if account_size > 100000:
                position_management['max_position_size'] *= 1.2
            elif account_size < 5000:
                position_management['max_position_size'] *= 0.8
            
            # Adjust based on market regime
            market_regime = enhanced_decision.get('market_regime', 'sideways')
            if market_regime == 'volatile':
                position_management['exit_strategy'] = 'immediate_stop'
            elif market_regime in ['bullish', 'bearish']:
                position_management['exit_strategy'] = 'trailing_stop'
            
            return position_management
            
        except Exception as e:
            logger.warning(f"⚠️ Position management calculation failed: {e}")
            return {'max_position_size': 0.1, 'entry_strategy': 'market', 
                   'exit_strategy': 'trailing_stop', 'rebalance_frequency': 'daily'}
    
    def _determine_execution_strategy(self, enhanced_decision: Dict[str, Any], 
                                    trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine execution strategy"""
        try:
            strategy = {
                'order_type': 'market',
                'time_in_force': 'day',
                'execution_priority': 'normal',
                'slippage_tolerance': 0.001
            }
            
            # Adjust based on action
            action = enhanced_decision.get('action', 'HOLD')
            if action == 'BUY':
                strategy['order_type'] = 'limit'  # Use limit orders for buys
                strategy['execution_priority'] = 'high'
            elif action == 'SELL':
                strategy['order_type'] = 'market'  # Use market orders for sells
                strategy['execution_priority'] = 'high'
            
            # Adjust based on market conditions
            market_conditions = self._assess_market_conditions(trading_data)
            if market_conditions['liquidity'] == 'poor':
                strategy['slippage_tolerance'] = 0.005
                strategy['time_in_force'] = 'gtc'  # Good till cancelled
            
            return strategy
            
        except Exception as e:
            logger.warning(f"⚠️ Execution strategy determination failed: {e}")
            return {'order_type': 'market', 'time_in_force': 'day', 
                   'execution_priority': 'normal', 'slippage_tolerance': 0.001}
    
    def _apply_prometheus_risk_management(self, decision: Dict[str, Any], 
                                        trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply PROMETHEUS risk management rules"""
        try:
            # Get risk adjustments
            risk_adjustments = decision.get('prometheus_enhancements', {}).get('risk_adjustments', {})
            
            # Apply position size adjustments
            base_position_size = decision.get('position_size', 0.1)
            multiplier = risk_adjustments.get('position_size_multiplier', 1.0)
            adjusted_position_size = base_position_size * multiplier
            
            # Ensure position size is within limits
            max_position = trading_data.get('max_position_size', 0.2)
            adjusted_position_size = min(adjusted_position_size, max_position)
            
            decision['position_size'] = adjusted_position_size
            
            # Apply confidence threshold
            confidence_threshold = risk_adjustments.get('confidence_threshold', 0.6)
            if decision.get('confidence', 0) < confidence_threshold:
                decision['action'] = 'HOLD'
                decision['risk_override'] = 'Low confidence threshold'
            
            # Add risk management metadata
            decision['risk_management'] = {
                'position_size_adjusted': True,
                'confidence_threshold_applied': True,
                'risk_multiplier': multiplier,
                'final_position_size': adjusted_position_size
            }
            
            return decision
            
        except Exception as e:
            logger.warning(f"⚠️ Risk management application failed: {e}")
            return decision
    
    def _fallback_trading_decision(self, trading_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback trading decision when enhanced HRM is not available"""
        return {
            'action': 'HOLD',
            'confidence': 0.1,
            'position_size': 0.0,
            'reasoning': 'Enhanced HRM not available',
            'fallback': True,
            'timestamp': datetime.now().isoformat(),
            'prometheus_enhancements': {
                'market_conditions': {'volatility': 'unknown', 'trend': 'unknown'},
                'risk_adjustments': {'position_size_multiplier': 0.0},
                'position_management': {'max_position_size': 0.0},
                'execution_strategy': {'order_type': 'none'}
            }
        }
    
    def _update_integration_metrics(self, integration_time: float, success: bool):
        """Update integration performance metrics"""
        try:
            if success:
                self.integration_metrics['successful_integrations'] += 1
            else:
                self.integration_metrics['failed_integrations'] += 1
            
            # Update average integration time
            total = self.integration_metrics['total_integrations']
            current_avg = self.integration_metrics['average_integration_time']
            self.integration_metrics['average_integration_time'] = (
                (current_avg * (total - 1) + integration_time) / total
            )
            
            self.integration_metrics['last_integration_time'] = datetime.now().isoformat()
            
        except Exception as e:
            logger.warning(f"⚠️ Metrics update failed: {e}")
    
    def get_integration_metrics(self) -> Dict[str, Any]:
        """Get integration performance metrics"""
        try:
            metrics = self.integration_metrics.copy()
            
            # Calculate success rate
            total = metrics['total_integrations']
            if total > 0:
                metrics['success_rate'] = metrics['successful_integrations'] / total
                metrics['failure_rate'] = metrics['failed_integrations'] / total
            else:
                metrics['success_rate'] = 0.0
                metrics['failure_rate'] = 0.0
            
            # Add enhanced HRM metrics if available
            if self.enhanced_hrm:
                metrics['enhanced_hrm_metrics'] = self.enhanced_hrm.get_enhancement_metrics()
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Integration metrics failed: {e}")
            return {'error': str(e)}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get integration health status"""
        try:
            health = {
                'integration_status': 'active' if self.integration_active else 'inactive',
                'enhanced_hrm_available': ENHANCED_HRM_AVAILABLE,
                'enhanced_hrm_initialized': self.enhanced_hrm is not None,
                'last_integration': self.integration_metrics.get('last_integration_time'),
                'total_integrations': self.integration_metrics['total_integrations']
            }
            
            # Add enhanced HRM health if available
            if self.enhanced_hrm:
                health['enhanced_hrm_health'] = self.enhanced_hrm.get_health_status()
            
            return health
            
        except Exception as e:
            logger.error(f"❌ Health status failed: {e}")
            return {'error': str(e)}

# Example usage and testing
async def test_prometheus_integration():
    """Test PROMETHEUS enhanced HRM integration"""
    print("[TEST] Testing PROMETHEUS Enhanced HRM Integration...")
    
    # Initialize integration
    integration = PROMETHEUSEnhancedHRMIntegration()
    
    # Test trading data
    trading_data = {
        'current_price': 150.0,
        'volume': 2000000,
        'symbol': 'SPY',
        'technical_indicators': {
            'rsi': 65,
            'macd': 0.5,
            'bollinger_upper': 155,
            'bollinger_lower': 145
        },
        'risk_tolerance': 'medium',
        'experience_level': 'intermediate',
        'account_size': 50000,
        'available_cash': 25000,
        'current_positions': {'SPY': 100},
        'max_position_size': 0.15,
        'stop_loss_percentage': 0.05,
        'take_profit_percentage': 0.1
    }
    
    # Test integration
    result = await integration.integrate_with_trading_loop(trading_data)
    
    print(f"Integration Result: {result}")
    
    # Test metrics
    metrics = integration.get_integration_metrics()
    print(f"Integration Metrics: {metrics}")
    
    # Test health
    health = integration.get_health_status()
    print(f"Health Status: {health}")
    
    print("[SUCCESS] PROMETHEUS integration test completed!")
    return True

if __name__ == "__main__":
    asyncio.run(test_prometheus_integration())
