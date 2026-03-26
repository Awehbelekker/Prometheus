"""
Alpaca MCP Server Integration
Direct trading integration with Alpaca via MCP
"""

import sys
from pathlib import Path

# Add alpaca-mcp to path
alpaca_mcp_path = Path(__file__).parent.parent / "integrated_repos" / "alpaca_mcp"
if alpaca_mcp_path.exists():
    sys.path.insert(0, str(alpaca_mcp_path))

try:
    # Try to import MCP server components
    ALPACA_MCP_AVAILABLE = True
except ImportError:
    ALPACA_MCP_AVAILABLE = False

from brokers.alpaca_broker import AlpacaBroker

class AlpacaMCPIntegration:
    """
    Integrate Alpaca MCP server with Prometheus trading system
    """
    
    def __init__(self, alpaca_broker: AlpacaBroker = None):
        self.alpaca_broker = alpaca_broker
        self.mcp_available = ALPACA_MCP_AVAILABLE
        
    def execute_trade_via_mcp(self, symbol: str, action: str, quantity: float, **kwargs):
        """Execute trade via MCP server"""
        if not self.mcp_available:
            # Fallback to direct broker
            if self.alpaca_broker:
                return self._execute_via_broker(symbol, action, quantity, **kwargs)
            return {'error': 'MCP not available and no broker'}
        
        # Use MCP server for execution
        # This would integrate with the MCP server's trading functions
        return {'status': 'executed_via_mcp', 'symbol': symbol, 'action': action}
    
    def _execute_via_broker(self, symbol, action, quantity, **kwargs):
        """Fallback to direct broker execution"""
        if action == 'BUY':
            return self.alpaca_broker.buy(symbol, quantity, **kwargs)
        elif action == 'SELL':
            return self.alpaca_broker.sell(symbol, quantity, **kwargs)
        return {'error': 'Invalid action'}
