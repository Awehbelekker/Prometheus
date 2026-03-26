#!/usr/bin/env python3
"""
HRM Trading Integration
Connects trading system to HRM training for learning from trades
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import HRM trainer
try:
    from core.hrm_trading_trainer import (
        get_hrm_trainer,
        record_trade_outcome,
        train_hrm_on_trading,
        HRMTradingTrainer
    )
    HRM_TRAINER_AVAILABLE = True
    logger.info("✅ HRM Trading Trainer available")
except ImportError as e:
    logger.warning(f"HRM Trading Trainer not available: {e}")
    HRM_TRAINER_AVAILABLE = False


class HRMTradingIntegration:
    """
    Integrates HRM training with the trading system
    Automatically records trade outcomes for learning
    """
    
    def __init__(self, auto_train_interval: int = 50):
        """
        Initialize HRM trading integration
        
        Args:
            auto_train_interval: Train after this many new samples
        """
        self.auto_train_interval = auto_train_interval
        self.samples_since_training = 0
        self.total_samples = 0
        self.enabled = HRM_TRAINER_AVAILABLE
        
        if self.enabled:
            try:
                self.trainer = get_hrm_trainer()
                status = self.trainer.get_training_status()
                self.total_samples = status['total_samples']
                logger.info(f"🧠 HRM Integration ready - {self.total_samples} samples loaded")
            except Exception as e:
                logger.error(f"Failed to initialize HRM trainer: {e}")
                self.enabled = False
                self.trainer = None
        else:
            self.trainer = None
    
    def record_entry(
        self,
        symbol: str,
        action: str,
        price: float,
        quantity: float,
        market_data: Dict[str, Any],
        technical_indicators: Dict[str, float],
        confidence: float,
        ai_reasoning: Optional[str] = None
    ) -> Optional[str]:
        """
        Record trade entry for tracking
        Returns entry_id for later matching with exit
        """
        if not self.enabled:
            return None
        
        entry_id = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store entry for later matching
        if not hasattr(self, '_pending_trades'):
            self._pending_trades = {}
        
        self._pending_trades[entry_id] = {
            'symbol': symbol,
            'action': action,
            'entry_price': price,
            'quantity': quantity,
            'market_data': market_data.copy(),
            'technical_indicators': technical_indicators.copy(),
            'confidence': confidence,
            'ai_reasoning': ai_reasoning,
            'entry_time': datetime.now()
        }
        
        logger.debug(f"📝 Recorded entry: {entry_id}")
        return entry_id
    
    def record_exit(
        self,
        entry_id: str,
        exit_price: float,
        exit_reason: str = "take_profit"
    ) -> Dict[str, Any]:
        """
        Record trade exit and calculate P&L for training
        """
        if not self.enabled or not hasattr(self, '_pending_trades'):
            return {'status': 'not_enabled'}
        
        if entry_id not in self._pending_trades:
            logger.warning(f"Entry not found: {entry_id}")
            return {'status': 'entry_not_found'}
        
        entry = self._pending_trades.pop(entry_id)
        
        # Calculate profit/loss
        if entry['action'].upper() == 'BUY':
            profit_pct = (exit_price - entry['entry_price']) / entry['entry_price'] * 100
        else:  # SELL (short)
            profit_pct = (entry['entry_price'] - exit_price) / entry['entry_price'] * 100
        
        profit_usd = profit_pct / 100 * entry['entry_price'] * entry['quantity']
        
        # Determine if this was a good decision
        is_profitable = profit_usd > 0
        
        # Record for HRM training
        try:
            sample_count = record_trade_outcome(
                symbol=entry['symbol'],
                action=entry['action'],
                market_data=entry['market_data'],
                technical_indicators=entry['technical_indicators'],
                profit_loss=profit_usd,
                confidence=entry['confidence']
            )
            
            self.total_samples = sample_count
            self.samples_since_training += 1
            
            logger.info(f"🧠 HRM recorded: {entry['symbol']} {entry['action']} "
                       f"P&L: ${profit_usd:.2f} ({profit_pct:.1f}%)")
            
            # Auto-train if we have enough new samples
            if self.samples_since_training >= self.auto_train_interval:
                self._trigger_auto_train()
            
            return {
                'status': 'recorded',
                'entry_id': entry_id,
                'symbol': entry['symbol'],
                'profit_usd': profit_usd,
                'profit_pct': profit_pct,
                'is_profitable': is_profitable,
                'total_samples': self.total_samples
            }
            
        except Exception as e:
            logger.error(f"Failed to record trade outcome: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def record_completed_trade(
        self,
        symbol: str,
        action: str,
        entry_price: float,
        exit_price: float,
        quantity: float,
        market_data: Dict[str, Any],
        technical_indicators: Dict[str, float],
        confidence: float
    ) -> Dict[str, Any]:
        """
        Record a completed trade in one call (entry + exit)
        For when you don't track entries/exits separately
        """
        if not self.enabled:
            return {'status': 'not_enabled'}
        
        # Calculate profit/loss
        if action.upper() == 'BUY':
            profit_pct = (exit_price - entry_price) / entry_price * 100
        else:
            profit_pct = (entry_price - exit_price) / entry_price * 100
        
        profit_usd = profit_pct / 100 * entry_price * quantity
        
        try:
            sample_count = record_trade_outcome(
                symbol=symbol,
                action=action,
                market_data=market_data,
                technical_indicators=technical_indicators,
                profit_loss=profit_usd,
                confidence=confidence
            )
            
            self.total_samples = sample_count
            self.samples_since_training += 1
            
            logger.info(f"🧠 HRM: {symbol} {action} → ${profit_usd:.2f} ({profit_pct:.1f}%)")
            
            if self.samples_since_training >= self.auto_train_interval:
                self._trigger_auto_train()
            
            return {
                'status': 'recorded',
                'profit_usd': profit_usd,
                'profit_pct': profit_pct,
                'total_samples': self.total_samples
            }
            
        except Exception as e:
            logger.error(f"Failed to record trade: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _trigger_auto_train(self):
        """Trigger automatic training when enough samples collected"""
        logger.info(f"🎓 Auto-training HRM with {self.total_samples} samples...")
        
        try:
            result = train_hrm_on_trading(epochs=5, batch_size=16)
            self.samples_since_training = 0
            
            if result['status'] == 'complete':
                logger.info(f"✅ HRM Training complete - "
                           f"Accuracy: {result.get('final_accuracy', 0):.1%}")
            else:
                logger.warning(f"HRM Training: {result}")
                
        except Exception as e:
            logger.error(f"Auto-training failed: {e}")
    
    def get_prediction(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        technical_indicators: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Get HRM prediction for a trading decision
        """
        if not self.enabled or self.trainer is None:
            return {
                'status': 'not_available',
                'action': 'HOLD',
                'confidence': 0.5
            }
        
        try:
            prediction = self.trainer.predict(market_data, technical_indicators)
            prediction['status'] = 'success'
            prediction['symbol'] = symbol
            return prediction
            
        except Exception as e:
            logger.error(f"HRM prediction failed: {e}")
            return {
                'status': 'error',
                'action': 'HOLD',
                'confidence': 0.5,
                'error': str(e)
            }
    
    def get_training_status(self) -> Dict[str, Any]:
        """Get HRM training status"""
        if not self.enabled or self.trainer is None:
            return {
                'enabled': False,
                'total_samples': 0,
                'ready_to_train': False
            }
        
        status = self.trainer.get_training_status()
        status['enabled'] = True
        status['samples_since_training'] = self.samples_since_training
        status['auto_train_interval'] = self.auto_train_interval
        return status
    
    def manual_train(self, epochs: int = 10) -> Dict[str, Any]:
        """Manually trigger training"""
        if not self.enabled:
            return {'status': 'not_enabled'}
        
        logger.info(f"🎓 Manual HRM training with {epochs} epochs...")
        result = train_hrm_on_trading(epochs=epochs, batch_size=32)
        self.samples_since_training = 0
        return result


# Global instance
_hrm_integration: Optional[HRMTradingIntegration] = None


def get_hrm_integration() -> HRMTradingIntegration:
    """Get or create global HRM integration instance"""
    global _hrm_integration
    
    if _hrm_integration is None:
        _hrm_integration = HRMTradingIntegration()
    
    return _hrm_integration


# Convenience functions for trading system integration
def hrm_record_trade(
    symbol: str,
    action: str,
    entry_price: float,
    exit_price: float,
    quantity: float,
    market_data: Dict[str, Any],
    technical_indicators: Optional[Dict[str, float]] = None,
    confidence: float = 0.7
) -> Dict[str, Any]:
    """
    Record a completed trade for HRM learning
    Call this after each trade completes
    """
    integration = get_hrm_integration()
    
    # Default technical indicators if not provided
    if technical_indicators is None:
        technical_indicators = {
            'rsi': 50,
            'macd': 0,
            'macd_signal': 0
        }
    
    return integration.record_completed_trade(
        symbol=symbol,
        action=action,
        entry_price=entry_price,
        exit_price=exit_price,
        quantity=quantity,
        market_data=market_data,
        technical_indicators=technical_indicators,
        confidence=confidence
    )


def hrm_get_prediction(
    symbol: str,
    market_data: Dict[str, Any],
    technical_indicators: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Get HRM trading prediction
    """
    integration = get_hrm_integration()
    
    if technical_indicators is None:
        technical_indicators = {'rsi': 50, 'macd': 0}
    
    return integration.get_prediction(symbol, market_data, technical_indicators)


def hrm_train_now(epochs: int = 10) -> Dict[str, Any]:
    """Manually trigger HRM training"""
    integration = get_hrm_integration()
    return integration.manual_train(epochs)


def hrm_status() -> Dict[str, Any]:
    """Get HRM training status"""
    integration = get_hrm_integration()
    return integration.get_training_status()


if __name__ == "__main__":
    # Test the integration
    logging.basicConfig(level=logging.INFO)
    
    integration = HRMTradingIntegration(auto_train_interval=20)
    
    print(f"\nHRM Status: {integration.get_training_status()}")
    
    # Simulate some trades
    import numpy as np
    
    for i in range(25):
        result = integration.record_completed_trade(
            symbol=['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA'][i % 5],
            action=['BUY', 'SELL'][i % 2],
            entry_price=100 + np.random.uniform(-10, 10),
            exit_price=100 + np.random.uniform(-15, 20),
            quantity=10,
            market_data={
                'price': 100,
                'volume': 1000000,
                'change_percent': np.random.uniform(-5, 5)
            },
            technical_indicators={
                'rsi': 50 + np.random.uniform(-30, 30),
                'macd': np.random.uniform(-2, 2)
            },
            confidence=0.7
        )
        print(f"Trade {i+1}: {result}")
    
    print(f"\nFinal Status: {integration.get_training_status()}")
