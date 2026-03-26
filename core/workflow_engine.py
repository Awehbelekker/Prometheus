"""
MASS Framework Workflow Engine
Handles multi-agent workflow creation and execution
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import uuid
from datetime import datetime
import json
import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowStep:
    """Individual step in a workflow"""
    id: str
    name: str
    agent_id: str
    task_type: str
    task_params: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@dataclass
class Workflow:
    """Complete workflow definition and state"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class WorkflowEngine:
    """Main workflow execution engine"""
    
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
        self.workflows: Dict[str, Workflow] = {}
        self.running_workflows: Dict[str, asyncio.Task] = {}
        
    def create_workflow(self, name: str, description: str, steps_config: List[Dict[str, Any]]) -> str:
        """Create a new workflow from configuration"""
        logger.info(f"Creating workflow: {name} with {len(steps_config)} steps")
        workflow_id = str(uuid.uuid4())
        
        # Create workflow steps
        steps = []
        for i, step_config in enumerate(steps_config):
            step = WorkflowStep(
                id=f"step_{i+1}",
                name=step_config.get("name", f"Step {i+1}"),
                agent_id=step_config["agent_id"],
                task_type=step_config["task_type"],
                task_params=step_config.get("task_params", {}),
                dependencies=step_config.get("dependencies", [])
            )
            steps.append(step)
        
        # Create workflow
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            steps=steps,
            metadata={"total_steps": len(steps)}
        )
        
        self.workflows[workflow_id] = workflow
        logger.info(f"Workflow created with ID: {workflow_id}")
        return workflow_id
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow asynchronously"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        
        if workflow.status != WorkflowStatus.CREATED:
            raise ValueError(f"Workflow {workflow_id} is not in created state")
        
        # Start execution
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        
        # Create execution task
        execution_task = asyncio.create_task(self._execute_workflow_steps(workflow))
        self.running_workflows[workflow_id] = execution_task
        
        try:
            result = await execution_task
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            return result
        
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.now()
            raise e
        
        finally:
            # Clean up
            if workflow_id in self.running_workflows:
                del self.running_workflows[workflow_id]
    
    async def execute_workflow(self, workflow_config: dict, context: dict = None) -> dict:
        """Execute a workflow from config and return results."""
        # Parse workflow config
        workflow_id = workflow_config.get("id", str(uuid.uuid4()))
        name = workflow_config.get("name", "Workflow")
        description = workflow_config.get("description", "")
        steps_config = workflow_config.get("steps", [])
        # Create workflow if not already present
        if workflow_id not in self.workflows:
            self.create_workflow(name, description, [
                {
                    "name": step.get("id", step.get("name", f"Step {i+1}")),
                    "agent_id": step["agent"],
                    "task_type": step["task"],
                    "task_params": step.get("parameters", {}),
                    "dependencies": step.get("dependencies", [])
                } for i, step in enumerate(steps_config)
            ])
        # Now execute by workflow_id
        return await self.execute_workflow_by_id(workflow_id)

    async def execute_workflow_by_id(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow asynchronously by id (original signature)."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        workflow = self.workflows[workflow_id]
        if workflow.status != WorkflowStatus.CREATED:
            raise ValueError(f"Workflow {workflow_id} is not in created state")
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        execution_task = asyncio.create_task(self._execute_workflow_steps(workflow))
        self.running_workflows[workflow_id] = execution_task
        try:
            result = await execution_task
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            # Adapt result for test expectations
            return {
                "status": result["status"],
                "step_results": list(result["results"].values())
            }
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.now()
            raise e
        finally:
            if workflow_id in self.running_workflows:
                del self.running_workflows[workflow_id]
    
    async def _execute_workflow_steps(self, workflow: Workflow) -> Dict[str, Any]:
        """Execute all steps in a workflow"""
        logger.info(f"Executing workflow steps for workflow ID: {workflow.id}")
        results = {}
        completed_steps = set()
        
        while len(completed_steps) < len(workflow.steps):
            # Find steps that can be executed (dependencies met)
            ready_steps = []
            for step in workflow.steps:
                if (step.status == StepStatus.PENDING and 
                    all(dep in completed_steps for dep in step.dependencies)):
                    ready_steps.append(step)
            
            if not ready_steps:
                # Check for circular dependencies or errors
                pending_steps = [s for s in workflow.steps if s.status == StepStatus.PENDING]
                if pending_steps:
                    raise RuntimeError("Circular dependency or unresolvable dependencies detected")
                break
            
            # Execute ready steps in parallel
            tasks = []
            for step in ready_steps:
                task = asyncio.create_task(self._execute_step(step, results))
                tasks.append((step, task))
            
            # Wait for all tasks to complete
            for step, task in tasks:
                try:
                    result = await task
                    logger.info(f"Step {step.id} ({step.name}) completed successfully.")
                    step.status = StepStatus.COMPLETED
                    step.result = result
                    step.end_time = datetime.now()
                    results[step.id] = result
                    completed_steps.add(step.id)
                    
                except Exception as e:
                    logger.error(f"Step {step.id} ({step.name}) failed: {e}")
                    step.status = StepStatus.FAILED
                    step.error = str(e)
                    step.end_time = datetime.now()
                    
                    # For now, continue with other steps
                    # In the future, we might want configurable error handling
                    completed_steps.add(step.id)
        
        logger.info(f"Workflow {workflow.id} execution complete. {len(completed_steps)}/{len(workflow.steps)} steps completed.")
        return {
            "workflow_id": workflow.id,
            "status": "completed" if all(s.status == StepStatus.COMPLETED for s in workflow.steps) else "partial",
            "steps_completed": len(completed_steps),
            "total_steps": len(workflow.steps),
            "results": results,
            "execution_time": (datetime.now() - workflow.started_at).total_seconds()
        }
    
    async def _execute_step(self, step: WorkflowStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        step.status = StepStatus.RUNNING
        step.start_time = datetime.now()
        
        # Get the agent
        if step.agent_id not in self.agents:
            raise RuntimeError(f"Agent {step.agent_id} not found")
        
        agent = self.agents[step.agent_id]
        
        # Prepare task parameters with context
        task_params = step.task_params.copy()
        task_params["type"] = step.task_type
        
        # Add context from previous steps if needed
        for dep_id in step.dependencies:
            if dep_id in context:
                task_params[f"context_{dep_id}"] = context[dep_id]
        
        # Execute the task
        result = await agent.process_task(task_params)
        
        return {
            "step_id": step.id,
            "agent_id": step.agent_id,
            "task_type": step.task_type,
            "result": result,
            "execution_time": (datetime.now() - step.start_time).total_seconds()
        }
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current status of a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        
        # Calculate progress
        completed_steps = sum(1 for step in workflow.steps 
                            if step.status in [StepStatus.COMPLETED, StepStatus.FAILED])
        total_steps = len(workflow.steps)
        progress = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        
        return {
            "workflow_id": workflow.id,
            "name": workflow.name,
            "status": workflow.status.value,
            "progress": round(progress, 2),
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "agent_id": step.agent_id,
                    "status": step.status.value,
                    "dependencies": step.dependencies,
                    "error": step.error
                }
                for step in workflow.steps
            ]
        }
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows with basic info"""
        return [
            {
                "id": workflow.id,
                "name": workflow.name,
                "description": workflow.description,
                "status": workflow.status.value,
                "created_at": workflow.created_at.isoformat(),
                "total_steps": len(workflow.steps)
            }
            for workflow in self.workflows.values()
        ]
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        
        if workflow.status == WorkflowStatus.RUNNING:
            # Cancel the execution task
            if workflow_id in self.running_workflows:
                task = self.running_workflows[workflow_id]
                task.cancel()
                del self.running_workflows[workflow_id]
            
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.now()
            return True
        
        return False

    def register_workflow(self, workflow_data: Dict[str, Any]):
        workflow_id = workflow_data["id"]
        steps = [WorkflowStep(
            id=step["id"],
            name=step.get("name", step["id"]),
            agent_id=step["agent"],
            task_type=step["task"],
            task_params=step.get("parameters", {}),
            dependencies=step.get("dependencies", [])
        ) for step in workflow_data["steps"]]
        workflow = Workflow(
            id=workflow_id,
            name=workflow_data["name"],
            description=workflow_data.get("description", ""),
            steps=steps
        )
        self.workflows[workflow_id] = workflow

# Predefined workflow templates
WORKFLOW_TEMPLATES = {
    "code_review": {
        "name": "Complete Code Review",
        "description": "Comprehensive code analysis, testing, and documentation review",
        "steps": [
            {
                "name": "Analyze Code",
                "agent_id": "code_analyzer",
                "task_type": "analyze_file",
                "task_params": {"file_path": "main.py"}
            },
            {
                "name": "Generate Tests",
                "agent_id": "testing_agent", 
                "task_type": "generate_tests",
                "task_params": {"code": ""},
                "dependencies": ["step_1"]
            },
            {
                "name": "Update Documentation",
                "agent_id": "documentation_agent",
                "task_type": "generate_readme",
                "task_params": {"project_info": {}},
                "dependencies": ["step_1"]
            }
        ]
    },
    "project_setup": {
        "name": "New Project Setup",
        "description": "Complete setup for a new development project",
        "steps": [
            {
                "name": "Analyze Project Structure",
                "agent_id": "code_analyzer",
                "task_type": "detect_patterns",
                "task_params": {"project_path": "./"}
            },
            {
                "name": "Generate Documentation",
                "agent_id": "documentation_agent",
                "task_type": "generate_readme",
                "task_params": {"project_info": {"name": "New Project"}},
                "dependencies": ["step_1"]
            },
            {
                "name": "Setup Testing",
                "agent_id": "testing_agent",
                "task_type": "coverage_report",
                "task_params": {"project_path": "./"},
                "dependencies": ["step_1"]
            }
        ]
    },
    "quick_analysis": {
        "name": "Quick Code Analysis",
        "description": "Fast analysis and suggestions for code improvement",
        "steps": [
            {
                "name": "Code Analysis",
                "agent_id": "code_analyzer",
                "task_type": "suggest_improvements",
                "task_params": {"code": ""}
            }
        ]
    }
}
