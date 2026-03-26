"""Stub HolographicUIIntegration for legacy tests.

Updated to use utc_iso utility for timestamps.
"""
from core.utils.time_utils import utc_iso

class HolographicUIIntegration:
    def __init__(self):
        self.mode = '3d'

    def status(self):
        return {
            'success': True,
            'features': ['3D Interface','Gesture Recognition','Immersive Experience'],
            'timestamp': utc_iso()
        }
