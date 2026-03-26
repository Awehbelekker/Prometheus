"""
Enhanced Agent Base - Foundation for All AI Agents

This module provides the base class for all AI agents in the MASS Framework,
including trust validation, security controls, and enterprise features.
"""

import asyncio
import uuid
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib

logger = logging.getLogger(__name__)


class TrustLevel(Enum):
    """Trust levels for agents and operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ENTERPRISE = "enterprise"


class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
    LEARNING = "learning"


@dataclass
class AgentCapability:
    """Agent capability definition"""
    name: str
    description: str
    trust_required: TrustLevel
    max_execution_time: int  # seconds
    requires_approval: bool = False
    data_sensitivity: str = "public"


@dataclass
class AgentMessage:
    """Message between agents"""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    trust_level: TrustLevel
    priority: int = 1
    requires_response: bool = True
    correlation_id: Optional[str] = None


@dataclass
class AgentTask:
    """Task definition for agents"""
    task_id: str
    task_type: str
    parameters: Dict[str, Any]
    requirements: Dict[str, Any]
    trust_level: TrustLevel
    created_at: datetime
    deadline: Optional[datetime] = None
    priority: int = 1
    estimated_duration: Optional[int] = None


class EnhancedAgentBase:
    """
    Enhanced Agent Base Class
    
    Provides foundation for all AI agents with:
    - Trust validation and security controls
    - Performance monitoring and metrics
    - Enterprise-grade error handling
    - Learning and adaptation capabilities
    - Multi-tenant support
    """
    
    def __init__(
        self,
        agent_id: str,
        specialization: str,
        capabilities: List[AgentCapability],
        trust_level: TrustLevel = TrustLevel.MEDIUM,
        max_concurrent_tasks: int = 5
    ):
        self.agent_id = agent_id
        self.specialization = specialization
        self.capabilities = {cap.name: cap for cap in capabilities}
        self.trust_level = trust_level
        self.max_concurrent_tasks = max_concurrent_tasks
        
        # State management
        self.status = AgentStatus.IDLE
        self.active_tasks: Dict[str, AgentTask] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.coordinator = None
        
        # Performance metrics
        self.metrics = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_execution_time": 0,
            "total_execution_time": 0,
            "trust_violations": 0,
            "learning_cycles": 0
        }
        
        # Learning and adaptation
        self.learning_data = []
        self.performance_history = []
        self.adaptation_rules = []
        
        # Security and trust
        self.security_context = {}
        self.trust_validation_history = []
        
        # Enterprise features
        self.tenant_id = None
        self.user_id = None
        self.audit_log = []
        
        logger.info(f"Initialized agent: {agent_id} ({specialization})")
    
    async def initialize(self) -> None:
        """Initialize the agent"""
        try:
            self.status = AgentStatus.IDLE
            await self._load_learning_data()
            await self._validate_capabilities()
            logger.info(f"Agent {self.agent_id} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agent {self.agent_id}: {e}")
            self.status = AgentStatus.ERROR
            raise
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute a task with trust validation and monitoring
        
        Args:
            task: Task to execute
            
        Returns:
            Task execution result
        """
        try:
            # Validate task and trust level
            await self._validate_task(task)
            
            # Update status
            self.status = AgentStatus.BUSY
            self.active_tasks[task.task_id] = task
            
            # Record start time
            start_time = datetime.utcnow()
            
            # Execute the task
            result = await self._execute_task_internal(task)
            
            # Record metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            await self._record_task_completion(task, result, execution_time)
            
            # Update status
            del self.active_tasks[task.task_id]
            self.status = AgentStatus.IDLE
            
            return result
            
        except Exception as e:
            logger.error(f"Task execution failed for agent {self.agent_id}: {e}")
            await self._record_task_failure(task, str(e))
            self.status = AgentStatus.ERROR
            raise
    
    async def receive_message(self, message: AgentMessage) -> None:
        """Receive and process a message"""
        try:
            # Validate message trust level
            if message.trust_level.value > self.trust_level.value:
                await self._record_trust_violation(message)
                raise ValueError(f"Insufficient trust level for message: {message.trust_level}")
            
            # Process message
            await self._process_message(message)
            
            # Send response if required
            if message.requires_response:
                response = await self._generate_response(message)
                await self._send_response(message, response)
                
        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            await self._record_message_failure(message, str(e))
    
    async def learn_from_experience(self, experience_data: Dict[str, Any]) -> None:
        """Learn from experience and adapt behavior"""
        try:
            self.learning_data.append(experience_data)
            await self._update_adaptation_rules(experience_data)
            self.metrics["learning_cycles"] += 1
            logger.info(f"Agent {self.agent_id} learned from experience")
        except Exception as e:
            logger.error(f"Learning failed for agent {self.agent_id}: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics"""
        return {
            "agent_id": self.agent_id,
            "specialization": self.specialization,
            "status": self.status.value,
            "trust_level": self.trust_level.value,
            "active_tasks": len(self.active_tasks),
            "metrics": self.metrics.copy(),
            "capabilities": list(self.capabilities.keys()),
            "learning_cycles": self.metrics["learning_cycles"]
        }
    
    async def _execute_task_internal(self, task: AgentTask) -> Dict[str, Any]:
        """
        Internal task execution - to be implemented by subclasses
        
        Args:
            task: Task to execute
            
        Returns:
            Task result
        """
        raise NotImplementedError("Subclasses must implement _execute_task_internal")
    
    async def _validate_task(self, task: AgentTask) -> None:
        """Validate task before execution"""
        # Check if agent can handle this task type
        if task.task_type not in self.capabilities:
            raise ValueError(f"Agent {self.agent_id} cannot handle task type: {task.task_type}")
        
        # Check trust level
        required_trust = self.capabilities[task.task_type].trust_required
        if task.trust_level.value < required_trust.value:
            raise ValueError(f"Insufficient trust level for task: {task.trust_level} < {required_trust}")
        
        # Check concurrent task limit
        if len(self.active_tasks) >= self.max_concurrent_tasks:
            raise ValueError(f"Agent {self.agent_id} has reached maximum concurrent tasks")
    
    async def _record_task_completion(self, task: AgentTask, result: Dict[str, Any], execution_time: float) -> None:
        """Record successful task completion"""
        self.metrics["total_tasks"] += 1
        self.metrics["successful_tasks"] += 1
        self.metrics["total_execution_time"] += execution_time
        self.metrics["average_execution_time"] = (
            self.metrics["total_execution_time"] / self.metrics["total_tasks"]
        )
        
        # Record performance data
        self.performance_history.append({
            "task_id": task.task_id,
            "task_type": task.task_type,
            "execution_time": execution_time,
            "success": True,
            "timestamp": datetime.utcnow()
        })
    
    async def _record_task_failure(self, task: AgentTask, error: str) -> None:
        """Record task failure"""
        self.metrics["total_tasks"] += 1
        self.metrics["failed_tasks"] += 1
        
        self.performance_history.append({
            "task_id": task.task_id,
            "task_type": task.task_type,
            "execution_time": 0,
            "success": False,
            "error": error,
            "timestamp": datetime.utcnow()
        })
    
    async def _record_trust_violation(self, message: AgentMessage) -> None:
        """Record trust violation"""
        self.metrics["trust_violations"] += 1
        self.trust_validation_history.append({
            "message_id": message.message_id,
            "violation_type": "insufficient_trust",
            "timestamp": datetime.utcnow()
        })
    
    async def _load_learning_data(self) -> None:
        """Load learning data from persistent storage"""
        # Implementation depends on storage backend
        pass
    
    async def _validate_capabilities(self) -> None:
        """Validate agent capabilities"""
        for capability in self.capabilities.values():
            if capability.trust_required.value > self.trust_level.value:
                logger.warning(f"Agent {self.agent_id} trust level may be insufficient for capability: {capability.name}")
    
    async def _process_message(self, message: AgentMessage) -> None:
        """Process received message"""
        # Default implementation - subclasses can override
        logger.info(f"Agent {self.agent_id} processed message: {message.message_type}")
    
    async def _generate_response(self, message: AgentMessage) -> Dict[str, Any]:
        """Generate response to message"""
        return {
            "response_id": str(uuid.uuid4()),
            "sender_id": self.agent_id,
            "receiver_id": message.sender_id,
            "correlation_id": message.correlation_id,
            "content": {"status": "received"},
            "timestamp": datetime.utcnow()
        }
    
    async def _send_response(self, original_message: AgentMessage, response: Dict[str, Any]) -> None:
        """Send response to original message sender"""
        if self.coordinator:
            response_message = AgentMessage(
                message_id=str(uuid.uuid4()),
                sender_id=self.agent_id,
                receiver_id=original_message.sender_id,
                message_type="response",
                content=response,
                timestamp=datetime.utcnow(),
                trust_level=original_message.trust_level,
                correlation_id=original_message.correlation_id
            )
            await self.coordinator.route_message(response_message)
    
    async def _update_adaptation_rules(self, experience_data: Dict[str, Any]) -> None:
        """Update adaptation rules based on experience"""
        # Implementation depends on learning strategy
        pass
    
    async def _record_message_failure(self, message: AgentMessage, error: str) -> None:
        """Record message processing failure"""
        self.audit_log.append({
            "event": "message_failure",
            "message_id": message.message_id,
            "error": error,
            "timestamp": datetime.utcnow()
        })


class AgentFactory:
    """Factory for creating agents"""
    
    @staticmethod
    def create_agent(
        agent_type: str,
        agent_id: str,
        specialization: str,
        trust_level: TrustLevel = TrustLevel.MEDIUM,
        **kwargs
    ) -> EnhancedAgentBase:
        """Create an agent of the specified type"""
        # This would be implemented to create specific agent types
        # For now, return a base agent
        capabilities = [
            AgentCapability(
                name="basic_task",
                description="Basic task execution",
                trust_required=TrustLevel.LOW,
                max_execution_time=60
            )
        ]
        
        return EnhancedAgentBase(
            agent_id=agent_id,
            specialization=specialization,
            capabilities=capabilities,
            trust_level=trust_level
        )
