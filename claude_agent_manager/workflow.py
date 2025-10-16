"""
Workflow Orchestration System
Allows chaining multiple agents together in complex workflows.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from agent_manager import Task, TaskResult, TaskPriority, AgentManager


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepType(Enum):
    """Types of workflow steps"""
    SEQUENTIAL = "sequential"  # Execute steps one after another
    PARALLEL = "parallel"      # Execute steps concurrently
    CONDITIONAL = "conditional"  # Execute based on condition
    LOOP = "loop"              # Repeat steps


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    step_id: str
    name: str
    agent_type: Optional[str]
    prompt_template: str
    priority: TaskPriority = TaskPriority.NORMAL
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    transform_input: Optional[Callable[[Dict[str, Any]], str]] = None
    transform_output: Optional[Callable[[str, Dict[str, Any]], Dict[str, Any]]] = None
    max_retries: int = 3
    timeout: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """Result of a workflow execution"""
    workflow_id: str
    status: WorkflowStatus
    steps_completed: int
    steps_failed: int
    results: Dict[str, TaskResult]
    context: Dict[str, Any]
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @property
    def execution_time(self) -> float:
        """Calculate total execution time"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0.0


class Workflow:
    """Represents a workflow of connected agent tasks"""

    def __init__(self, workflow_id: str, name: str, description: str = ""):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.steps: List[WorkflowStep] = []
        self.context: Dict[str, Any] = {}
        self.status = WorkflowStatus.PENDING
        self.logger = logging.getLogger(__name__)

    def add_step(self, step: WorkflowStep) -> 'Workflow':
        """Add a step to the workflow (builder pattern)"""
        self.steps.append(step)
        return self

    def set_context(self, context: Dict[str, Any]) -> 'Workflow':
        """Set initial workflow context"""
        self.context.update(context)
        return self

    async def execute(self, manager: AgentManager) -> WorkflowResult:
        """Execute the workflow"""
        self.status = WorkflowStatus.RUNNING
        started_at = datetime.now()
        results: Dict[str, TaskResult] = {}
        steps_completed = 0
        steps_failed = 0

        self.logger.info(f"Starting workflow: {self.name} ({self.workflow_id})")

        try:
            for step in self.steps:
                # Check condition if present
                if step.condition and not step.condition(self.context):
                    self.logger.info(f"Skipping step {step.step_id} - condition not met")
                    continue

                # Transform input if needed
                if step.transform_input:
                    prompt = step.transform_input(self.context)
                else:
                    # Use template with context
                    prompt = step.prompt_template.format(**self.context)

                # Create task
                task = Task(
                    task_id=f"{self.workflow_id}_{step.step_id}",
                    prompt=prompt,
                    priority=step.priority,
                    agent_type=step.agent_type,
                    context=self.context.copy(),
                    max_retries=step.max_retries
                )

                # Submit and wait for result
                await manager.submit_task(task)

                # Wait for completion with timeout
                wait_time = 0
                timeout = step.timeout or 300  # Default 5 minutes
                while task.task_id not in manager.results and wait_time < timeout:
                    await asyncio.sleep(0.5)
                    wait_time += 0.5

                if task.task_id not in manager.results:
                    raise TimeoutError(f"Step {step.step_id} timed out after {timeout}s")

                result = manager.get_result(task.task_id)
                results[step.step_id] = result

                if not result.success:
                    steps_failed += 1
                    error_msg = f"Step {step.step_id} failed: {result.error}"
                    self.logger.error(error_msg)

                    self.status = WorkflowStatus.FAILED
                    return WorkflowResult(
                        workflow_id=self.workflow_id,
                        status=WorkflowStatus.FAILED,
                        steps_completed=steps_completed,
                        steps_failed=steps_failed,
                        results=results,
                        context=self.context,
                        error=error_msg,
                        started_at=started_at,
                        completed_at=datetime.now()
                    )

                steps_completed += 1

                # Transform output and update context
                if step.transform_output:
                    updates = step.transform_output(result.response, self.context)
                    self.context.update(updates)
                else:
                    # Default: store result in context
                    self.context[f"{step.step_id}_result"] = result.response

                self.logger.info(f"Completed step {step.step_id}")

            self.status = WorkflowStatus.COMPLETED
            self.logger.info(f"Workflow completed: {self.name}")

            return WorkflowResult(
                workflow_id=self.workflow_id,
                status=WorkflowStatus.COMPLETED,
                steps_completed=steps_completed,
                steps_failed=steps_failed,
                results=results,
                context=self.context,
                started_at=started_at,
                completed_at=datetime.now()
            )

        except Exception as e:
            self.status = WorkflowStatus.FAILED
            self.logger.error(f"Workflow failed: {str(e)}")

            return WorkflowResult(
                workflow_id=self.workflow_id,
                status=WorkflowStatus.FAILED,
                steps_completed=steps_completed,
                steps_failed=steps_failed,
                results=results,
                context=self.context,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.now()
            )


class WorkflowBuilder:
    """Helper class for building complex workflows"""

    @staticmethod
    def code_development_workflow(feature_description: str) -> Workflow:
        """Create a workflow for developing a new feature"""
        workflow = Workflow(
            workflow_id="code_dev_" + str(datetime.now().timestamp()),
            name="Code Development Workflow",
            description="Complete workflow from design to testing"
        )

        workflow.set_context({"feature_description": feature_description})

        # Step 1: Architecture design
        workflow.add_step(WorkflowStep(
            step_id="architecture",
            name="Design Architecture",
            agent_type="architecture",
            prompt_template="Design the architecture for this feature:\n{feature_description}",
            transform_output=lambda resp, ctx: {"architecture_design": resp}
        ))

        # Step 2: Generate code
        workflow.add_step(WorkflowStep(
            step_id="code_generation",
            name="Generate Code",
            agent_type="code_generation",
            prompt_template="Implement this feature based on the architecture:\n\nFeature: {feature_description}\n\nArchitecture:\n{architecture_design}",
            transform_output=lambda resp, ctx: {"generated_code": resp}
        ))

        # Step 3: Code review
        workflow.add_step(WorkflowStep(
            step_id="code_review",
            name="Review Code",
            agent_type="code_review",
            prompt_template="Review this code:\n\n{generated_code}",
            transform_output=lambda resp, ctx: {"review_feedback": resp}
        ))

        # Step 4: Generate tests
        workflow.add_step(WorkflowStep(
            step_id="test_generation",
            name="Generate Tests",
            agent_type="testing",
            prompt_template="Create comprehensive tests for this code:\n\n{generated_code}",
            transform_output=lambda resp, ctx: {"test_code": resp}
        ))

        # Step 5: Documentation
        workflow.add_step(WorkflowStep(
            step_id="documentation",
            name="Generate Documentation",
            agent_type="documentation",
            prompt_template="Create documentation for:\n\nCode:\n{generated_code}\n\nTests:\n{test_code}",
            transform_output=lambda resp, ctx: {"documentation": resp}
        ))

        return workflow

    @staticmethod
    def security_audit_workflow(codebase_description: str) -> Workflow:
        """Create a workflow for security auditing"""
        workflow = Workflow(
            workflow_id="security_audit_" + str(datetime.now().timestamp()),
            name="Security Audit Workflow",
            description="Comprehensive security analysis"
        )

        workflow.set_context({"codebase": codebase_description})

        # Step 1: Security analysis
        workflow.add_step(WorkflowStep(
            step_id="security_scan",
            name="Security Scan",
            agent_type="security",
            prompt_template="Perform a security analysis on:\n{codebase}",
            transform_output=lambda resp, ctx: {"vulnerabilities": resp}
        ))

        # Step 2: Code review for security
        workflow.add_step(WorkflowStep(
            step_id="security_review",
            name="Security Code Review",
            agent_type="code_review",
            prompt_template="Review for security issues:\n{codebase}\n\nKnown vulnerabilities:\n{vulnerabilities}",
            transform_output=lambda resp, ctx: {"review_findings": resp}
        ))

        # Step 3: Generate security report
        workflow.add_step(WorkflowStep(
            step_id="security_report",
            name="Generate Report",
            agent_type="documentation",
            prompt_template="Create a security audit report:\n\nVulnerabilities:\n{vulnerabilities}\n\nReview:\n{review_findings}",
            transform_output=lambda resp, ctx: {"security_report": resp}
        ))

        return workflow

    @staticmethod
    def data_analysis_workflow(dataset_description: str, analysis_goals: str) -> Workflow:
        """Create a workflow for data analysis"""
        workflow = Workflow(
            workflow_id="data_analysis_" + str(datetime.now().timestamp()),
            name="Data Analysis Workflow",
            description="End-to-end data analysis"
        )

        workflow.set_context({
            "dataset": dataset_description,
            "goals": analysis_goals
        })

        # Step 1: Data analysis
        workflow.add_step(WorkflowStep(
            step_id="analyze_data",
            name="Analyze Data",
            agent_type="data_analysis",
            prompt_template="Analyze this dataset:\n{dataset}\n\nGoals:\n{goals}",
            transform_output=lambda resp, ctx: {"analysis_results": resp}
        ))

        # Step 2: Generate code for analysis
        workflow.add_step(WorkflowStep(
            step_id="generate_analysis_code",
            name="Generate Analysis Code",
            agent_type="code_generation",
            prompt_template="Create Python code for this analysis:\n{analysis_results}",
            transform_output=lambda resp, ctx: {"analysis_code": resp}
        ))

        # Step 3: Create report
        workflow.add_step(WorkflowStep(
            step_id="create_report",
            name="Create Report",
            agent_type="documentation",
            prompt_template="Create an analysis report:\n\nAnalysis:\n{analysis_results}\n\nCode:\n{analysis_code}",
            transform_output=lambda resp, ctx: {"final_report": resp}
        ))

        return workflow

    @staticmethod
    def api_development_workflow(api_requirements: str) -> Workflow:
        """Create a workflow for API development"""
        workflow = Workflow(
            workflow_id="api_dev_" + str(datetime.now().timestamp()),
            name="API Development Workflow",
            description="Complete API development lifecycle"
        )

        workflow.set_context({"requirements": api_requirements})

        # Step 1: API design
        workflow.add_step(WorkflowStep(
            step_id="api_design",
            name="Design API",
            agent_type="api_design",
            prompt_template="Design an API based on:\n{requirements}",
            transform_output=lambda resp, ctx: {"api_design": resp}
        ))

        # Step 2: Database schema
        workflow.add_step(WorkflowStep(
            step_id="database_design",
            name="Design Database",
            agent_type="database",
            prompt_template="Design database schema for:\n{api_design}",
            transform_output=lambda resp, ctx: {"database_schema": resp}
        ))

        # Step 3: Implementation
        workflow.add_step(WorkflowStep(
            step_id="implementation",
            name="Implement API",
            agent_type="code_generation",
            prompt_template="Implement API:\n\nDesign:\n{api_design}\n\nDatabase:\n{database_schema}",
            transform_output=lambda resp, ctx: {"api_code": resp}
        ))

        # Step 4: Tests
        workflow.add_step(WorkflowStep(
            step_id="tests",
            name="Generate Tests",
            agent_type="testing",
            prompt_template="Create API tests for:\n{api_code}",
            transform_output=lambda resp, ctx: {"test_code": resp}
        ))

        # Step 5: Documentation
        workflow.add_step(WorkflowStep(
            step_id="api_docs",
            name="Create API Documentation",
            agent_type="documentation",
            prompt_template="Create API documentation:\n\nAPI:\n{api_code}\n\nDesign:\n{api_design}",
            transform_output=lambda resp, ctx: {"api_documentation": resp}
        ))

        return workflow


class WorkflowOrchestrator:
    """Manages and executes multiple workflows"""

    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.workflows: Dict[str, Workflow] = {}
        self.results: Dict[str, WorkflowResult] = {}
        self.logger = logging.getLogger(__name__)

    def register_workflow(self, workflow: Workflow):
        """Register a workflow for execution"""
        self.workflows[workflow.workflow_id] = workflow
        self.logger.info(f"Registered workflow: {workflow.name}")

    async def execute_workflow(self, workflow_id: str) -> WorkflowResult:
        """Execute a registered workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]
        result = await workflow.execute(self.agent_manager)
        self.results[workflow_id] = result
        return result

    async def execute_workflows_parallel(self, workflow_ids: List[str]) -> List[WorkflowResult]:
        """Execute multiple workflows in parallel"""
        tasks = [self.execute_workflow(wf_id) for wf_id in workflow_ids]
        return await asyncio.gather(*tasks)

    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowStatus]:
        """Get status of a workflow"""
        if workflow_id in self.workflows:
            return self.workflows[workflow_id].status
        return None

    def get_workflow_result(self, workflow_id: str) -> Optional[WorkflowResult]:
        """Get result of a completed workflow"""
        return self.results.get(workflow_id)
