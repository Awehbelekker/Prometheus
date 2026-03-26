from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio

class MessageType(Enum):
    ANALYSIS_REQUEST = "analysis_request"
    ANALYSIS_RESPONSE = "analysis_response"
    COORDINATION_REQUEST = "coordination_request"
    COORDINATION_RESPONSE = "coordination_response"
    CONFLICT_ALERT = "conflict_alert"
    SOLUTION_PROPOSAL = "solution_proposal"
    APPROVAL_REQUEST = "approval_request"
    STATUS_UPDATE = "status_update"

@dataclass
class AgentMessage:
    sender_id: str
    receiver_id: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: float
    correlation_id: str
    priority: int = 1  # 1-10, 10 being highest priority

class AgentBase(ABC):
    def __init__(self, agent_id: str, specialization: str):
        self.agent_id = agent_id
        self.specialization = specialization
        self.coordinator = None
        self.message_queue = []
        self.active_tasks = {}

    @abstractmethod
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def analyze_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def coordinate_with_agents(self, other_agents: List[str], task_context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    async def send_message(self, message: AgentMessage):
        if self.coordinator:
            await self.coordinator.route_message(message)

    async def receive_message(self, message: AgentMessage):
        self.message_queue.append(message)
        await self.process_message_queue()

    async def process_message_queue(self):
        while self.message_queue:
            message = self.message_queue.pop(0)
            # Implement message handling logic here
            pass
