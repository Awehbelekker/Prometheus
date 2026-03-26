#!/usr/bin/env python3
"""
Position Management and Exit Strategy Implementation
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)

class PositionManager:
    """Manages open positions and exit strategies"""
    
    def __init__(self, config_path: str = "config/position_management.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.open_positions = {}
        self.exit_orders = {}
        
    async def monitor_positions(self):
        """Monitor all open positions for exit conditions"""
        while True:
            try:
                for position_id, position in self.open_positions.items():
                    await self.check_exit_conditions(position_id, position)
                
                await asyncio.sleep(self.config['position_management']['monitoring']['position_check_interval_seconds'])
            except Exception as e:
                logger.error(f"Position monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def check_exit_conditions(self, position_id: str, position: Dict):
        """Check if position should be exited"""
        current_price = await self.get_current_price(position['symbol'])
        if not current_price:
            return
        
        entry_price = position['entry_price']
        current_pnl = (current_price - entry_price) / entry_price * 100
        
        # Check take profit
        if current_pnl >= self.get_take_profit_threshold(position):
            await self.exit_position(position_id, "TAKE_PROFIT", current_price)
            return
        
        # Check stop loss
        if current_pnl <= -self.get_stop_loss_threshold(position):
            await self.exit_position(position_id, "STOP_LOSS", current_price)
            return
        
        # Check time-based exit
        if self.should_exit_by_time(position):
            await self.exit_position(position_id, "TIME_EXIT", current_price)
            return
    
    async def exit_position(self, position_id: str, reason: str, exit_price: float):
        """Exit a position"""
        position = self.open_positions[position_id]
        
        # Execute exit order
        success = await self.execute_exit_order(position, exit_price)
        
        if success:
            # Record exit
            await self.record_exit(position_id, reason, exit_price)
            
            # Remove from open positions
            del self.open_positions[position_id]
            
            logger.info(f"Position {position_id} exited: {reason} @ ${exit_price:.2f}")
    
    def get_take_profit_threshold(self, position: Dict) -> float:
        """Get take profit threshold based on confidence"""
        base_threshold = self.config['position_management']['exit_strategies']['take_profit']['default_percentage']
        confidence = position.get('confidence', 0.5)
        
        if confidence > 0.8:
            return self.config['position_management']['exit_strategies']['take_profit']['scaling']['high_confidence']
        elif confidence > 0.6:
            return self.config['position_management']['exit_strategies']['take_profit']['scaling']['medium_confidence']
        else:
            return self.config['position_management']['exit_strategies']['take_profit']['scaling']['low_confidence']
    
    def get_stop_loss_threshold(self, position: Dict) -> float:
        """Get stop loss threshold"""
        return self.config['position_management']['exit_strategies']['stop_loss']['default_percentage']
    
    def should_exit_by_time(self, position: Dict) -> bool:
        """Check if position should be exited by time"""
        entry_time = datetime.fromisoformat(position['entry_time'])
        max_hold_hours = self.config['position_management']['exit_strategies']['time_based']['max_hold_hours']
        
        return datetime.now() - entry_time > timedelta(hours=max_hold_hours)
