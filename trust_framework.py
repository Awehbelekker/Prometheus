"""
Trust Framework Fallback Module
Provides basic trust framework functionality for MASS coordinator
"""

from enum import Enum
from typing import Dict, Any

class TrustLevel(Enum):
    """Trust levels for agents"""
    UNTRUSTED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERIFIED = 4

class TrustFramework:
    """Basic trust framework for agent coordination"""
    
    def __init__(self):
        self.trust_scores = {}
    
    def get_trust_level(self, agent_id: str) -> TrustLevel:
        """Get trust level for an agent"""
        return self.trust_scores.get(agent_id, TrustLevel.MEDIUM)
    
    def update_trust(self, agent_id: str, success: bool):
        """Update trust based on agent performance"""
        current = self.trust_scores.get(agent_id, TrustLevel.MEDIUM)
        if success:
            # Increase trust
            if current.value < TrustLevel.VERIFIED.value:
                self.trust_scores[agent_id] = TrustLevel(current.value + 1)
        else:
            # Decrease trust
            if current.value > TrustLevel.UNTRUSTED.value:
                self.trust_scores[agent_id] = TrustLevel(current.value - 1)
    
    def is_trusted(self, agent_id: str) -> bool:
        """Check if agent is trusted"""
        level = self.get_trust_level(agent_id)
        return level.value >= TrustLevel.MEDIUM.value

# Global instance
trust_framework = TrustFramework()
