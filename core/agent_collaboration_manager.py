"""
SynergyCore™ Collaboration Manager for MASS Framework
Enables AI agents to work together on complex tasks
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from core.agent_base import AgentBase
from core.llm_service import llm_service, AIMessage
import json
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class CollaborationStatus(Enum):
    PLANNING = "planning"
    EXECUTING = "executing"
    AGGREGATING = "aggregating"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class SubTask:
    id: str
    description: str
    assigned_agent: str
    dependencies: List[str]
    priority: TaskPriority
    estimated_duration: int  # minutes
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class CollaborationSession:
    id: str
    main_task: str
    subtasks: List[SubTask]
    participating_agents: List[str]
    status: CollaborationStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    final_result: Optional[Dict[str, Any]] = None

class AgentCollaborationManager:
    """Manages collaboration between multiple AI agents"""
    
    def __init__(self):
        self.active_sessions: Dict[str, CollaborationSession] = {}
        self.agent_registry: Dict[str, AgentBase] = {}
        self.collaboration_templates = self._load_collaboration_templates()
    
    def register_agent(self, agent: AgentBase):
        """Register an agent for collaboration"""
        self.agent_registry[agent.agent_id] = agent
        logger.info(f"Registered agent for collaboration: {agent.agent_id}")
    
    def _load_collaboration_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load collaboration templates for common task patterns"""
        return {
            "full_development_cycle": {
                "description": "Complete development from concept to deployment",
                "stages": [
                    {"name": "planning", "agents": ["ai_code_generator"], "tasks": ["analyze_requirements"]},
                    {"name": "implementation", "agents": ["ai_code_generator"], "tasks": ["generate_code"]},
                    {"name": "testing", "agents": ["ai_testing_agent"], "tasks": ["generate_tests", "analyze_coverage"]},
                    {"name": "documentation", "agents": ["ai_documentation_agent"], "tasks": ["generate_documentation"]},
                    {"name": "optimization", "agents": ["ai_debugging_agent"], "tasks": ["analyze_performance", "optimize_code"]}
                ]
            },
            "code_review_and_improvement": {
                "description": "Comprehensive code review and improvement",
                "stages": [
                    {"name": "analysis", "agents": ["ai_code_generator", "ai_debugging_agent"], "tasks": ["review_code", "analyze_performance"]},
                    {"name": "improvement", "agents": ["ai_code_generator"], "tasks": ["refactor_code"]},
                    {"name": "validation", "agents": ["ai_testing_agent"], "tasks": ["generate_tests"]},
                    {"name": "documentation", "agents": ["ai_documentation_agent"], "tasks": ["update_documentation"]}
                ]
            },
            "debugging_and_fixing": {
                "description": "Comprehensive debugging and bug fixing",
                "stages": [
                    {"name": "diagnosis", "agents": ["ai_debugging_agent"], "tasks": ["debug_error", "analyze_performance"]},
                    {"name": "fixing", "agents": ["ai_code_generator"], "tasks": ["fix_bug"]},
                    {"name": "testing", "agents": ["ai_testing_agent"], "tasks": ["generate_tests"]},
                    {"name": "verification", "agents": ["ai_debugging_agent"], "tasks": ["verify_fix"]}
                ]
            }
        }
    
    async def orchestrate_multi_agent_task(
        self, 
        task_description: str, 
        context: Dict[str, Any] = None,
        template: str = None
    ) -> CollaborationSession:
        """Orchestrate a complex task across multiple agents"""
        
        session_id = str(uuid.uuid4())
        logger.info(f"Starting SynergyCore™ collaboration session: {session_id}")
        
        try:
            # Step 1: Analyze task and create execution plan
            execution_plan = await self._create_execution_plan(task_description, context, template)
            
            # Step 2: Create collaboration session
            session = CollaborationSession(
                id=session_id,
                main_task=task_description,
                subtasks=execution_plan["subtasks"],
                participating_agents=execution_plan["agents"],
                status=CollaborationStatus.PLANNING,
                created_at=datetime.now()
            )
            
            self.active_sessions[session_id] = session
            
            # Step 3: Execute the collaboration plan
            await self._execute_collaboration_plan(session)
            
            return session
            
        except Exception as e:
            logger.error(f"SynergyCore™ collaboration failed: {str(e)}")
            if session_id in self.active_sessions:
                self.active_sessions[session_id].status = CollaborationStatus.FAILED
            raise
    
    async def _create_execution_plan(
        self, 
        task_description: str, 
        context: Dict[str, Any] = None,
        template: str = None
    ) -> Dict[str, Any]:
        """Create detailed execution plan for SynergyCore™ collaboration"""
        
        system_prompt = """You are a project manager for AI agents. Create a detailed execution plan for SynergyCore™ collaboration.

Available Agents:
- ai_code_generator: Code generation, refactoring, review
- ai_documentation_agent: Documentation generation and analysis
- ai_testing_agent: Test generation and coverage analysis  
- ai_debugging_agent: Debugging, performance analysis, optimization

Task Decomposition Guidelines:
1. Break down complex tasks into smaller, manageable subtasks
2. Identify dependencies between subtasks
3. Assign appropriate agents based on their capabilities
4. Estimate realistic timeframes
5. Consider parallel execution opportunities
6. Plan for result aggregation

Output Format:
{
    "agents": ["agent1", "agent2"],
    "subtasks": [
        {
            "id": "task1",
            "description": "Task description",
            "assigned_agent": "agent_id",
            "dependencies": ["prerequisite_task_id"],
            "priority": "high|medium|low",
            "estimated_duration": 10
        }
    ],
    "execution_strategy": "parallel|sequential|hybrid",
    "aggregation_method": "description of how to combine results"
}"""

        user_prompt = f"""Create an execution plan for this task:

Task: {task_description}
Context: {context or {}}
Template: {template or "custom"}

Please provide a detailed execution plan that optimizes for efficiency and quality."""

        try:
            response = await llm_service.chat_completion([
                AIMessage(role="system", content=system_prompt),
                AIMessage(role="user", content=user_prompt)
            ])
            
            # Parse the response
            plan_data = json.loads(response.content)
            
            # Convert to SubTask objects
            subtasks = []
            for task_data in plan_data["subtasks"]:
                priority_map = {"high": TaskPriority.HIGH, "medium": TaskPriority.MEDIUM, "low": TaskPriority.LOW}
                subtask = SubTask(
                    id=task_data["id"],
                    description=task_data["description"],
                    assigned_agent=task_data["assigned_agent"],
                    dependencies=task_data.get("dependencies", []),
                    priority=priority_map.get(task_data.get("priority", "medium"), TaskPriority.MEDIUM),
                    estimated_duration=task_data.get("estimated_duration", 5)
                )
                subtasks.append(subtask)
            
            return {
                "agents": plan_data["agents"],
                "subtasks": subtasks,
                "execution_strategy": plan_data.get("execution_strategy", "hybrid"),
                "aggregation_method": plan_data.get("aggregation_method", "sequential")
            }
            
        except Exception as e:
            logger.error(f"Failed to create execution plan: {str(e)}")
            # Fallback to simple plan
            return self._create_fallback_plan(task_description)
    
    def _create_fallback_plan(self, task_description: str) -> Dict[str, Any]:
        """Create a simple fallback execution plan"""
        return {
            "agents": ["ai_code_generator"],
            "subtasks": [
                SubTask(
                    id="fallback_task",
                    description=task_description,
                    assigned_agent="ai_code_generator",
                    dependencies=[],
                    priority=TaskPriority.MEDIUM,
                    estimated_duration=10
                )
            ],
            "execution_strategy": "sequential",
            "aggregation_method": "direct"
        }
    
    async def _execute_collaboration_plan(self, session: CollaborationSession):
        """Execute the collaboration plan"""
        session.status = CollaborationStatus.EXECUTING
        
        try:
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(session.subtasks)
            
            # Execute tasks respecting dependencies
            completed_tasks = {}
            remaining_tasks = {task.id: task for task in session.subtasks}
            
            while remaining_tasks:
                # Find tasks ready for execution (no pending dependencies)
                ready_tasks = []
                for task_id, task in remaining_tasks.items():
                    if all(dep in completed_tasks for dep in task.dependencies):
                        ready_tasks.append(task)
                
                if not ready_tasks:
                    logger.error("Circular dependency detected in collaboration plan")
                    break
                
                # Execute ready tasks (potentially in parallel)
                task_results = await self._execute_tasks_batch(ready_tasks, completed_tasks)
                
                # Update completed tasks
                for task_id, result in task_results.items():
                    completed_tasks[task_id] = result
                    if task_id in remaining_tasks:
                        remaining_tasks[task_id].result = result
                        remaining_tasks[task_id].completed_at = datetime.now()
                        del remaining_tasks[task_id]
            
            # Aggregate results
            session.status = CollaborationStatus.AGGREGATING
            final_result = await self._aggregate_results(session.subtasks, completed_tasks)
            
            session.final_result = final_result
            session.status = CollaborationStatus.COMPLETED
            session.completed_at = datetime.now()
            
        except Exception as e:
            logger.error(f"Collaboration execution failed: {str(e)}")
            session.status = CollaborationStatus.FAILED
            raise
    
    def _build_dependency_graph(self, subtasks: List[SubTask]) -> Dict[str, List[str]]:
        """Build dependency graph for task execution"""
        graph = {}
        for task in subtasks:
            graph[task.id] = task.dependencies
        return graph
    
    async def _execute_tasks_batch(
        self, 
        tasks: List[SubTask], 
        completed_tasks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a batch of tasks in parallel"""
        
        # Prepare task execution coroutines
        task_coroutines = []
        for task in tasks:
            if task.assigned_agent in self.agent_registry:
                agent = self.agent_registry[task.assigned_agent]
                task_coroutine = self._execute_single_task(agent, task, completed_tasks)
                task_coroutines.append((task.id, task_coroutine))
        
        # Execute tasks in parallel
        results = {}
        if task_coroutines:
            task_results = await asyncio.gather(
                *[coroutine for _, coroutine in task_coroutines],
                return_exceptions=True
            )
            
            for i, (task_id, _) in enumerate(task_coroutines):
                result = task_results[i]
                if isinstance(result, Exception):
                    logger.error(f"Task {task_id} failed: {str(result)}")
                    results[task_id] = {"error": str(result)}
                else:
                    results[task_id] = result
        
        return results
    
    async def _execute_single_task(
        self, 
        agent: AgentBase, 
        task: SubTask, 
        completed_tasks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single task with an agent"""
        
        task.started_at = datetime.now()
        
        try:
            # Prepare task context with dependency results
            task_context = {
                "description": task.description,
                "priority": task.priority.name,
                "dependencies": task.dependencies,
                "dependency_results": {dep: completed_tasks.get(dep) for dep in task.dependencies}
            }
            
            # Execute the task
            result = await agent.process_task({
                "type": "collaboration_task",
                "context": task_context,
                "task_id": task.id
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Task execution failed for {task.id}: {str(e)}")
            raise
    
    async def _aggregate_results(
        self, 
        subtasks: List[SubTask], 
        completed_tasks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Aggregate results from all subtasks"""
        
        system_prompt = """You are a result aggregator for SynergyCore™ collaboration.
        Combine the results from multiple AI agents into a coherent, comprehensive final result.
        
        Guidelines:
        1. Synthesize information from all subtasks
        2. Resolve any conflicts or inconsistencies
        3. Create a unified, actionable result
        4. Highlight key achievements and insights
        5. Include next steps if applicable"""
        
        # Prepare results summary
        results_summary = []
        for task in subtasks:
            if task.result:
                results_summary.append({
                    "task": task.description,
                    "agent": task.assigned_agent,
                    "result": task.result
                })
        
        user_prompt = f"""Aggregate these subtask results into a final comprehensive result:

Subtask Results:
{json.dumps(results_summary, indent=2)}

Please provide a unified, actionable final result that combines all insights and outputs."""

        try:
            response = await llm_service.chat_completion([
                AIMessage(role="system", content=system_prompt),
                AIMessage(role="user", content=user_prompt)
            ])
            
            return {
                "status": "success",
                "aggregated_result": response.content,
                "subtask_results": completed_tasks,
                "summary": {
                    "total_tasks": len(subtasks),
                    "completed_tasks": len([t for t in subtasks if t.result]),
                    "participating_agents": list(set(t.assigned_agent for t in subtasks))
                }
            }
            
        except Exception as e:
            logger.error(f"Result aggregation failed: {str(e)}")
            return {
                "status": "partial_success",
                "error": str(e),
                "subtask_results": completed_tasks
            }
    
    async def get_collaboration_status(self, session_id: str) -> Dict[str, Any]:
        """Get the status of a collaboration session"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "status": session.status.value,
            "main_task": session.main_task,
            "total_subtasks": len(session.subtasks),
            "completed_subtasks": len([t for t in session.subtasks if t.result]),
            "participating_agents": session.participating_agents,
            "created_at": session.created_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "final_result": session.final_result
        }
    
    async def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active collaboration sessions"""
        sessions = []
        for session_id, session in self.active_sessions.items():
            sessions.append({
                "session_id": session_id,
                "status": session.status.value,
                "main_task": session.main_task,
                "created_at": session.created_at.isoformat(),
                "participating_agents": session.participating_agents
            })
        return sessions

# Global collaboration manager instance
collaboration_manager = AgentCollaborationManager()
