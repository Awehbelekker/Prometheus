"""
Advanced Load Balancing and Resource Optimization System
Provides intelligent agent load balancing, dynamic scaling, and resource allocation
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import heapq
import threading
from collections import defaultdict, deque
import psutil
import json

logger = logging.getLogger(__name__)

class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    RESOURCE_BASED = "resource_based"
    ADAPTIVE = "adaptive"

class AgentStatus(Enum):
    """Agent status"""
    AVAILABLE = "available"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    MAINTENANCE = "maintenance"
    FAILED = "failed"

@dataclass
class AgentNode:
    """Represents an agent node in the load balancing system"""
    agent_id: str
    agent_type: str
    weight: float = 1.0
    max_concurrent_tasks: int = 10
    current_tasks: int = 0
    status: AgentStatus = AgentStatus.AVAILABLE
    
    # Performance metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    
    # Resource utilization
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    queue_size: int = 0
    
    # Health metrics
    health_score: float = 1.0
    consecutive_failures: int = 0
    last_health_check: Optional[datetime] = None

@dataclass
class LoadBalancingConfig:
    """Configuration for load balancing"""
    strategy: LoadBalancingStrategy = LoadBalancingStrategy.ADAPTIVE
    health_check_interval: int = 30  # seconds
    overload_threshold: float = 0.8  # 80% capacity
    failure_threshold: int = 3
    recovery_time: int = 60  # seconds
    enable_auto_scaling: bool = True
    min_agents: int = 1
    max_agents: int = 10
    scale_up_threshold: float = 0.7
    scale_down_threshold: float = 0.3

class ResourceMonitor:
    """Monitors system resources and agent performance"""
    
    def __init__(self):
        self.cpu_history = deque(maxlen=100)
        self.memory_history = deque(maxlen=100)
        self.load_history = deque(maxlen=100)
        self.monitoring_active = True
        self._monitor_thread = None
        
    def start_monitoring(self):
        """Start resource monitoring"""
        if self._monitor_thread is None or not self._monitor_thread.is_alive():
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("Resource monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                load_avg = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
                
                self.cpu_history.append(cpu_percent)
                self.memory_history.append(memory.percent)
                self.load_history.append(load_avg)
                
                time.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {str(e)}")
                time.sleep(30)
    
    def get_system_load(self) -> Dict[str, float]:
        """Get current system load metrics"""
        return {
            'cpu_percent': list(self.cpu_history)[-1] if self.cpu_history else 0,
            'memory_percent': list(self.memory_history)[-1] if self.memory_history else 0,
            'load_average': list(self.load_history)[-1] if self.load_history else 0,
            'avg_cpu': sum(self.cpu_history) / len(self.cpu_history) if self.cpu_history else 0,
            'avg_memory': sum(self.memory_history) / len(self.memory_history) if self.memory_history else 0
        }

class LoadBalancer:
    """
    Intelligent load balancer for agent requests
    """
    
    def __init__(self, config: LoadBalancingConfig = None):
        self.config = config or LoadBalancingConfig()
        self.agents: Dict[str, AgentNode] = {}
        self.agent_queues: Dict[str, asyncio.Queue] = {}
        
        # Load balancing state
        self._round_robin_index = 0
        self._request_counts = defaultdict(int)
        
        # Monitoring
        self.resource_monitor = ResourceMonitor()
        self.resource_monitor.start_monitoring()
        
        # Health checking
        self._health_check_task = None
        self._start_health_checking()
        
        logger.info(f"Load balancer initialized with strategy: {self.config.strategy.value}")
    
    def register_agent(self, 
                      agent_id: str, 
                      agent_type: str, 
                      weight: float = 1.0,
                      max_concurrent: int = 10) -> bool:
        """Register a new agent with the load balancer"""
        
        if agent_id in self.agents:
            logger.warning(f"Agent {agent_id} already registered")
            return False
        
        agent_node = AgentNode(
            agent_id=agent_id,
            agent_type=agent_type,
            weight=weight,
            max_concurrent_tasks=max_concurrent
        )
        
        self.agents[agent_id] = agent_node
        self.agent_queues[agent_id] = asyncio.Queue()
        
        logger.info(f"Registered agent: {agent_id} (type: {agent_type}, weight: {weight})")
        return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent"""
        if agent_id not in self.agents:
            return False
        
        # Mark as maintenance first
        self.agents[agent_id].status = AgentStatus.MAINTENANCE
        
        # Wait for current tasks to complete
        # In a real implementation, you'd want to gracefully drain tasks
        
        del self.agents[agent_id]
        if agent_id in self.agent_queues:
            del self.agent_queues[agent_id]
        
        logger.info(f"Unregistered agent: {agent_id}")
        return True
    
    async def get_agent(self, agent_type: str = None, requirements: Dict[str, Any] = None) -> Optional[str]:
        """Get the best available agent based on load balancing strategy"""
        
        # Filter available agents
        available_agents = [
            agent for agent in self.agents.values()
            if (agent.status == AgentStatus.AVAILABLE and
                (agent_type is None or agent.agent_type == agent_type) and
                agent.current_tasks < agent.max_concurrent_tasks)
        ]
        
        if not available_agents:
            logger.warning(f"No available agents for type: {agent_type}")
            return None
        
        # Apply load balancing strategy
        selected_agent = await self._select_agent(available_agents, requirements)
        
        if selected_agent:
            # Update agent state
            selected_agent.current_tasks += 1
            selected_agent.total_requests += 1
            selected_agent.last_request_time = datetime.now()
            
            # Update status based on load
            if selected_agent.current_tasks >= selected_agent.max_concurrent_tasks * self.config.overload_threshold:
                selected_agent.status = AgentStatus.BUSY
            
            return selected_agent.agent_id
        
        return None
    
    async def _select_agent(self, available_agents: List[AgentNode], requirements: Dict[str, Any] = None) -> Optional[AgentNode]:
        """Select agent based on configured strategy"""
        
        if not available_agents:
            return None
        
        if self.config.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_selection(available_agents)
        
        elif self.config.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(available_agents)
        
        elif self.config.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_selection(available_agents)
        
        elif self.config.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            return self._least_response_time_selection(available_agents)
        
        elif self.config.strategy == LoadBalancingStrategy.RESOURCE_BASED:
            return self._resource_based_selection(available_agents)
        
        elif self.config.strategy == LoadBalancingStrategy.ADAPTIVE:
            return await self._adaptive_selection(available_agents, requirements)
        
        else:
            # Default to round robin
            return self._round_robin_selection(available_agents)
    
    def _round_robin_selection(self, agents: List[AgentNode]) -> AgentNode:
        """Simple round-robin selection"""
        selected = agents[self._round_robin_index % len(agents)]
        self._round_robin_index += 1
        return selected
    
    def _weighted_round_robin_selection(self, agents: List[AgentNode]) -> AgentNode:
        """Weighted round-robin selection"""
        # Calculate total weight
        total_weight = sum(agent.weight for agent in agents)
        
        # Create weighted list
        weighted_agents = []
        for agent in agents:
            weight_ratio = agent.weight / total_weight
            count = max(1, int(weight_ratio * 10))  # Scale to reasonable range
            weighted_agents.extend([agent] * count)
        
        selected = weighted_agents[self._round_robin_index % len(weighted_agents)]
        self._round_robin_index += 1
        return selected
    
    def _least_connections_selection(self, agents: List[AgentNode]) -> AgentNode:
        """Select agent with least current connections"""
        return min(agents, key=lambda a: a.current_tasks)
    
    def _least_response_time_selection(self, agents: List[AgentNode]) -> AgentNode:
        """Select agent with lowest average response time"""
        return min(agents, key=lambda a: a.avg_response_time)
    
    def _resource_based_selection(self, agents: List[AgentNode]) -> AgentNode:
        """Select agent based on resource utilization"""
        def resource_score(agent):
            cpu_factor = 1.0 - (agent.cpu_usage / 100.0)
            memory_factor = 1.0 - (agent.memory_usage / 100.0)
            load_factor = 1.0 - (agent.current_tasks / agent.max_concurrent_tasks)
            return (cpu_factor + memory_factor + load_factor) / 3.0
        
        return max(agents, key=resource_score)
    
    async def _adaptive_selection(self, agents: List[AgentNode], requirements: Dict[str, Any] = None) -> AgentNode:
        """Adaptive selection considering multiple factors"""
        
        def calculate_score(agent):
            # Base score from health
            score = agent.health_score
            
            # Adjust for current load
            load_factor = 1.0 - (agent.current_tasks / agent.max_concurrent_tasks)
            score *= load_factor
            
            # Adjust for response time
            if agent.avg_response_time > 0:
                time_factor = 1.0 / (1.0 + agent.avg_response_time)
                score *= time_factor
            
            # Adjust for success rate
            if agent.total_requests > 0:
                success_rate = agent.successful_requests / agent.total_requests
                score *= success_rate
            
            # System load consideration
            system_load = self.resource_monitor.get_system_load()
            if system_load['cpu_percent'] > 80:
                # Prefer agents with better performance under high load
                score *= (1.0 - agent.cpu_usage / 100.0)
            
            return score
        
        # Select agent with highest score
        return max(agents, key=calculate_score)
    
    async def release_agent(self, agent_id: str, success: bool = True, response_time: float = 0.0):
        """Release an agent after task completion"""
        
        if agent_id not in self.agents:
            return
        
        agent = self.agents[agent_id]
        agent.current_tasks = max(0, agent.current_tasks - 1)
        
        # Update metrics
        if success:
            agent.successful_requests += 1
            agent.consecutive_failures = 0
        else:
            agent.failed_requests += 1
            agent.consecutive_failures += 1
        
        # Update average response time
        if response_time > 0:
            if agent.avg_response_time == 0:
                agent.avg_response_time = response_time
            else:
                # Exponential moving average
                alpha = 0.1
                agent.avg_response_time = alpha * response_time + (1 - alpha) * agent.avg_response_time
        
        # Update health score
        self._update_health_score(agent)
        
        # Update status
        if agent.consecutive_failures >= self.config.failure_threshold:
            agent.status = AgentStatus.FAILED
        elif agent.current_tasks < agent.max_concurrent_tasks * self.config.overload_threshold:
            agent.status = AgentStatus.AVAILABLE
    
    def _update_health_score(self, agent: AgentNode):
        """Update agent health score based on recent performance"""
        
        # Base score from success rate
        if agent.total_requests > 0:
            success_rate = agent.successful_requests / agent.total_requests
            health_score = success_rate
        else:
            health_score = 1.0
        
        # Adjust for consecutive failures
        if agent.consecutive_failures > 0:
            failure_penalty = min(0.9, agent.consecutive_failures * 0.1)
            health_score *= (1.0 - failure_penalty)
        
        # Adjust for response time
        if agent.avg_response_time > 10.0:  # 10 seconds threshold
            time_penalty = min(0.5, agent.avg_response_time / 20.0)
            health_score *= (1.0 - time_penalty)
        
        agent.health_score = max(0.1, min(1.0, health_score))
    
    def _start_health_checking(self):
        """Start periodic health checking"""
        async def health_check_loop():
            while True:
                try:
                    await self._perform_health_checks()
                    await asyncio.sleep(self.config.health_check_interval)
                except Exception as e:
                    logger.error(f"Health check error: {str(e)}")
                    await asyncio.sleep(60)
        
        self._health_check_task = asyncio.create_task(health_check_loop())
    
    async def _perform_health_checks(self):
        """Perform health checks on all agents"""
        
        for agent in self.agents.values():
            # Check if agent has been inactive too long
            if agent.last_request_time:
                time_since_last = datetime.now() - agent.last_request_time
                if time_since_last > timedelta(minutes=10):
                    # Ping agent or perform health check
                    # Implementation depends on your agent interface
                    pass
            
            # Auto-recovery for failed agents
            if agent.status == AgentStatus.FAILED:
                time_since_failure = datetime.now() - (agent.last_request_time or datetime.now())
                if time_since_failure > timedelta(seconds=self.config.recovery_time):
                    agent.status = AgentStatus.AVAILABLE
                    agent.consecutive_failures = 0
                    logger.info(f"Agent {agent.agent_id} recovered from failure")
            
            agent.last_health_check = datetime.now()
    
    def get_load_statistics(self) -> Dict[str, Any]:
        """Get comprehensive load balancing statistics"""
        
        total_agents = len(self.agents)
        available_agents = sum(1 for a in self.agents.values() if a.status == AgentStatus.AVAILABLE)
        busy_agents = sum(1 for a in self.agents.values() if a.status == AgentStatus.BUSY)
        failed_agents = sum(1 for a in self.agents.values() if a.status == AgentStatus.FAILED)
        
        total_requests = sum(a.total_requests for a in self.agents.values())
        total_successful = sum(a.successful_requests for a in self.agents.values())
        total_failed = sum(a.failed_requests for a in self.agents.values())
        
        avg_response_time = sum(a.avg_response_time for a in self.agents.values()) / total_agents if total_agents > 0 else 0
        
        system_load = self.resource_monitor.get_system_load()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'strategy': self.config.strategy.value,
            'agents': {
                'total': total_agents,
                'available': available_agents,
                'busy': busy_agents,
                'failed': failed_agents
            },
            'requests': {
                'total': total_requests,
                'successful': total_successful,
                'failed': total_failed,
                'success_rate': (total_successful / total_requests * 100) if total_requests > 0 else 0
            },
            'performance': {
                'avg_response_time': avg_response_time,
                'system_load': system_load
            },
            'agent_details': [
                {
                    'agent_id': agent.agent_id,
                    'type': agent.agent_type,
                    'status': agent.status.value,
                    'current_tasks': agent.current_tasks,
                    'max_tasks': agent.max_concurrent_tasks,
                    'health_score': agent.health_score,
                    'avg_response_time': agent.avg_response_time,
                    'success_rate': (agent.successful_requests / agent.total_requests * 100) if agent.total_requests > 0 else 0
                }
                for agent in self.agents.values()
            ]
        }
    
    async def shutdown(self):
        """Shutdown the load balancer"""
        logger.info("Shutting down load balancer...")
        
        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Stop resource monitoring
        self.resource_monitor.stop_monitoring()
        
        # Clear agents
        self.agents.clear()
        self.agent_queues.clear()
        
        logger.info("Load balancer shutdown complete")


class AutoScaler:
    """
    Automatic scaling for agent pools based on load and performance metrics
    """
    
    def __init__(self, load_balancer: LoadBalancer):
        self.load_balancer = load_balancer
        self.config = load_balancer.config
        self.scaling_history = deque(maxlen=100)
        self._scaling_task = None
        
        if self.config.enable_auto_scaling:
            self._start_auto_scaling()
    
    def _start_auto_scaling(self):
        """Start automatic scaling monitoring"""
        async def scaling_loop():
            while True:
                try:
                    await self._evaluate_scaling()
                    await asyncio.sleep(60)  # Evaluate every minute
                except Exception as e:
                    logger.error(f"Auto-scaling error: {str(e)}")
                    await asyncio.sleep(120)
        
        self._scaling_task = asyncio.create_task(scaling_loop())
        logger.info("Auto-scaling enabled")
    
    async def _evaluate_scaling(self):
        """Evaluate if scaling is needed"""
        
        stats = self.load_balancer.get_load_statistics()
        
        # Calculate current utilization
        total_agents = stats['agents']['total']
        available_agents = stats['agents']['available']
        utilization = 1.0 - (available_agents / total_agents) if total_agents > 0 else 1.0
        
        # Get system resources
        system_load = stats['performance']['system_load']
        
        # Scale up conditions
        if (utilization > self.config.scale_up_threshold and 
            total_agents < self.config.max_agents and
            system_load['cpu_percent'] < 80):
            
            await self._scale_up()
        
        # Scale down conditions
        elif (utilization < self.config.scale_down_threshold and 
              total_agents > self.config.min_agents):
            
            await self._scale_down()
    
    async def _scale_up(self):
        """Scale up agent pool"""
        # This would integrate with your agent creation system
        logger.info("Scaling up agent pool")
        
        # Record scaling action
        self.scaling_history.append({
            'timestamp': datetime.now(),
            'action': 'scale_up',
            'reason': 'high_utilization'
        })
    
    async def _scale_down(self):
        """Scale down agent pool"""
        # This would integrate with your agent management system
        logger.info("Scaling down agent pool")
        
        # Record scaling action
        self.scaling_history.append({
            'timestamp': datetime.now(),
            'action': 'scale_down',
            'reason': 'low_utilization'
        })
    
    def get_scaling_history(self) -> List[Dict[str, Any]]:
        """Get scaling history"""
        return list(self.scaling_history)


# Global load balancer instance
load_balancer = LoadBalancer()
auto_scaler = AutoScaler(load_balancer)

# Convenience functions
async def get_available_agent(agent_type: str = None, requirements: Dict[str, Any] = None) -> Optional[str]:
    """Get an available agent from the load balancer"""
    return await load_balancer.get_agent(agent_type, requirements)

async def release_agent(agent_id: str, success: bool = True, response_time: float = 0.0):
    """Release an agent back to the load balancer"""
    await load_balancer.release_agent(agent_id, success, response_time)

def register_agent(agent_id: str, agent_type: str, weight: float = 1.0, max_concurrent: int = 10) -> bool:
    """Register a new agent with the load balancer"""
    return load_balancer.register_agent(agent_id, agent_type, weight, max_concurrent)

def get_load_stats() -> Dict[str, Any]:
    """Get current load balancing statistics"""
    return load_balancer.get_load_statistics()

# Context manager for agent usage
class AgentContext:
    """Context manager for agent acquisition and release"""
    
    def __init__(self, agent_type: str = None, requirements: Dict[str, Any] = None):
        self.agent_type = agent_type
        self.requirements = requirements
        self.agent_id = None
        self.start_time = None
    
    async def __aenter__(self):
        self.agent_id = await get_available_agent(self.agent_type, self.requirements)
        if not self.agent_id:
            raise RuntimeError(f"No available agents of type: {self.agent_type}")
        
        self.start_time = time.time()
        return self.agent_id
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.agent_id and self.start_time:
            success = exc_type is None
            response_time = time.time() - self.start_time
            await release_agent(self.agent_id, success, response_time)

async def use_agent(agent_type: str = None, requirements: Dict[str, Any] = None):
    """Context manager for using an agent"""
    return AgentContext(agent_type, requirements)
