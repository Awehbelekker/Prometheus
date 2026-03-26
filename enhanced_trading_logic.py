"""
Enhanced Trading Logic with SHORT SELLING Support
This module provides the logic to integrate with the launcher
"""

from position_manager import PositionManager
from brokers.universal_broker_interface import OrderSide

class EnhancedTradingLogic:
    """Enhanced trading logic with SHORT selling capability"""
    
    def __init__(self):
        self.position_manager = PositionManager()
    
    def determine_order_details(self, symbol: str, action: str, current_price: float, 
                                equity: float, position_size_pct: float, 
                                broker_name: str = 'Alpaca'):
        """
        Determine order side, quantity, and position intent
        
        Returns:
            dict with keys: order_side, quantity, position_action, position_side, should_trade
        """
        # Get trade intent
        position_action, position_side = self.position_manager.determine_trade_intent(
            symbol, action, broker_name
        )
        
        # Get current position if exists
        current_position = self.position_manager.get_position(symbol, broker_name)
        
        # Determine if we should trade
        should_trade = True
        order_side = None
        quantity = 0
        
        if position_action == 'OPEN_LONG':
            # Open new LONG position
            order_side = OrderSide.BUY
            trade_amount = equity * position_size_pct
            quantity = trade_amount / current_price
            
        elif position_action == 'CLOSE_LONG':
            # Close existing LONG position
            order_side = OrderSide.SELL
            quantity = current_position['quantity']
            
        elif position_action == 'OPEN_SHORT':
            # Open new SHORT position
            order_side = OrderSide.SELL
            trade_amount = equity * position_size_pct
            quantity = trade_amount / current_price
            
        elif position_action == 'CLOSE_SHORT':
            # Close existing SHORT position (cover)
            order_side = OrderSide.BUY
            quantity = abs(current_position['quantity'])
            
        elif position_action in ['ADD_LONG', 'ADD_SHORT']:
            # Don't add to existing positions for now (can be enabled later)
            should_trade = False
            
        else:  # HOLD
            should_trade = False
        
        return {
            'order_side': order_side,
            'quantity': quantity,
            'position_action': position_action,
            'position_side': position_side,
            'should_trade': should_trade,
            'current_position': current_position
        }
    
    def record_trade_execution(self, symbol: str, position_action: str, position_side: str,
                              quantity: float, price: float, broker_name: str = 'Alpaca'):
        """Record trade execution and update positions"""
        
        if position_action == 'OPEN_LONG':
            self.position_manager.open_position(symbol, 'LONG', quantity, price, broker_name)
            
        elif position_action == 'OPEN_SHORT':
            self.position_manager.open_position(symbol, 'SHORT', quantity, price, broker_name)
            
        elif position_action == 'CLOSE_LONG':
            self.position_manager.close_position(symbol, broker_name)
            
        elif position_action == 'CLOSE_SHORT':
            self.position_manager.close_position(symbol, broker_name)
        
        # Update price for any remaining positions
        self.position_manager.update_position_price(symbol, price, broker_name)
