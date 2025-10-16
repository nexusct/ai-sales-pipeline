"""
Claude Agent Manager

A comprehensive framework for managing multiple Claude AI agents with pooling,
task distribution, and workflow orchestration.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

from .agent_manager import (
    AgentManager,
    ClaudeAgent,
    AgentConfig,
    Task,
    TaskResult,
    TaskPriority,
    AgentStatus
)

from .specialized_agents import SpecializedAgents

from .workflow import (
    Workflow,
    WorkflowStep,
    WorkflowBuilder,
    WorkflowOrchestrator,
    WorkflowStatus,
    WorkflowResult
)

from .config import (
    ConfigLoader,
    ConfigManager,
    ManagerConfig,
    setup_logging
)

__all__ = [
    # Agent Manager
    "AgentManager",
    "ClaudeAgent",
    "AgentConfig",
    "Task",
    "TaskResult",
    "TaskPriority",
    "AgentStatus",

    # Specialized Agents
    "SpecializedAgents",

    # Workflow
    "Workflow",
    "WorkflowStep",
    "WorkflowBuilder",
    "WorkflowOrchestrator",
    "WorkflowStatus",
    "WorkflowResult",

    # Configuration
    "ConfigLoader",
    "ConfigManager",
    "ManagerConfig",
    "setup_logging",
]
