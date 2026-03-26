"""Stub BlockchainTradingIntegration for legacy tests.
Provides minimal interface expected by comprehensive test suite.

Migrated to centralized UTC time utilities (utc_iso) replacing deprecated
datetime.utcnow direct usage for consistency and future-proofing.
"""
from core.utils.time_utils import utc_iso

class BlockchainTradingIntegration:
    def __init__(self):
        self.initialized = True
        self.backend = 'simulated'

    def status(self):
        return {
            'success': True,
            'backend': self.backend,
            'features': ['Smart Contracts','DeFi','Cross-chain'],
            'timestamp': utc_iso()
        }
