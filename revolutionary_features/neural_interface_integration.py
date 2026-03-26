"""Stub NeuralInterfaceIntegration for legacy tests.

UTC timestamp generation migrated to utc_iso utility.
"""
from core.utils.time_utils import utc_iso

class NeuralInterfaceIntegration:
    def __init__(self):
        self.connected = True

    def status(self):
        return {
            'success': True,
            'capabilities': ['BCI','Signal Processing','Thought Control'],
            'timestamp': utc_iso()
        }
