import asyncio
import logging
from typing import Dict, Any, List, Optional
from .conflict_resolution import ConflictResolutionEngine
from .optimization_engine import SolutionOptimizationEngine

logger = logging.getLogger(__name__)

class MASSCoordinator:
    """
    Orchestrates all agent interactions and resolves conflicts.
    """
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.active_workflows: Dict[str, Any] = {}
        self.conflict_resolver = ConflictResolutionEngine()
        self.optimizer = SolutionOptimizationEngine()
        self.message_router = None  # To be implemented
        self.workflow_engine = None  # To be implemented
        self.is_running = False
    
    def register_agent(self, agent_id: str, agent_instance: Any):
        self.agents[agent_id] = agent_instance
        agent_instance.coordinator = self

    async def route_message(self, message: 'AgentMessage') -> None:
        """Route message to appropriate agent"""
        receiver = self.agents.get(message.receiver_id)
        if receiver:
            await receiver.receive_message(message)
        else:
            print(f"Warning: No agent found with ID {message.receiver_id}")

    async def execute_app_generation_workflow(self, user_requirements: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder for workflow execution logic
        return {}

    async def detect_conflicts(self, agent_outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        return await self.conflict_resolver.detect_conflicts(agent_outputs)

    async def resolve_conflicts(self, conflicts: List[Dict[str, Any]], agent_outputs: Dict[str, Any], user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self.conflict_resolver.resolve_conflicts(conflicts, agent_outputs, user_preferences)

    def optimize_solutions(self, agent_outputs: Dict[str, Any]) -> Dict[str, Any]:
        scores = self.optimizer.score_outputs(agent_outputs)
        best_agent = self.optimizer.select_best(agent_outputs)
        return {"scores": scores, "best_agent": best_agent, "best_output": agent_outputs.get(best_agent)}

    async def start(self):
        """Start the MASS Coordinator"""
        try:
            logger.info("Starting MASS Coordinator...")
            # Initialize components
            self.is_running = True
            logger.info("MASS Coordinator started successfully")
        except Exception as e:
            logger.error(f"Failed to start MASS Coordinator: {e}")
            raise

    async def stop(self):
        """Stop the MASS Coordinator"""
        try:
            logger.info("Stopping MASS Coordinator...")
            self.is_running = False
            # Cleanup resources
            logger.info("MASS Coordinator stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping MASS Coordinator: {e}")
            raise

    async def get_enterprise_metrics(self):
        """Get enterprise-level metrics for the MASS system"""
        try:
            from core.advanced_monitoring import metrics_collector

            # Get basic metrics summary
            metrics_summary = metrics_collector.get_metrics_summary()

            # Add MASS-specific metrics
            mass_metrics = {
                "mass_coordinator": {
                    "status": "running" if self.is_running else "stopped",
                    "active_agents": len(self.agents),
                    "active_workflows": len(self.active_workflows),
                    "total_conflicts_resolved": len(getattr(self.conflict_resolver, 'resolved_conflicts', [])),
                    "optimization_runs": len(getattr(self.optimizer, 'optimization_history', []))
                },
                "system_health": {
                    "overall_status": "healthy" if self.is_running else "degraded",
                    "components": {
                        "conflict_resolver": "active" if self.conflict_resolver else "inactive",
                        "optimizer": "active" if self.optimizer else "inactive",
                        "message_router": "active" if self.message_router else "inactive",
                        "workflow_engine": "active" if self.workflow_engine else "inactive"
                    }
                }
            }

            # Combine with system metrics
            enterprise_metrics = {
                **metrics_summary,
                "mass_framework": mass_metrics,
                "timestamp": metrics_summary.get("timestamp"),
                "collection_time": "real-time"
            }

            return enterprise_metrics

        except Exception as e:
            logger.error(f"Failed to get enterprise metrics: {e}")
            # Return basic fallback metrics
            return {
                "mass_coordinator": {
                    "status": "running" if self.is_running else "stopped",
                    "active_agents": len(self.agents),
                    "active_workflows": len(self.active_workflows),
                    "error": str(e)
                },
                "timestamp": "error",
                "collection_time": "failed"
            }
