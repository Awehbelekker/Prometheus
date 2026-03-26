# Broker integrations for PROMETHEUS Trading Platform
from .universal_broker_interface import BrokerManager, Order, OrderType, OrderSide
from .alpaca_broker import AlpacaBroker

try:
    from .interactive_brokers_broker import InteractiveBrokersBroker
    IB_AVAILABLE = True
except ImportError:
    IB_AVAILABLE = False

__all__ = ['BrokerManager', 'Order', 'OrderType', 'OrderSide', 'AlpacaBroker']

if IB_AVAILABLE:
    __all__.append('InteractiveBrokersBroker')
