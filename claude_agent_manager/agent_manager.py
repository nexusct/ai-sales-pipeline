"""
Claude Agent Manager - Core Module
A comprehensive framework for managing multiple Claude agents with pooling,
task distribution, and workflow orchestration.
"""

import anthropic
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from collections import defaultdict
import time


class AgentStatus(Enum):
    """Agent status states"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentConfig:
    """Configuration for a Claude agent"""
    name: str
    model: str = "claude-sonnet-4-5-20250929"
    max_tokens: int = 4096
    temperature: float = 1.0
    specialization: Optional[str] = None
    system_prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Represents a task to be processed by an agent"""
    task_id: str
    prompt: str
    priority: TaskPriority = TaskPriority.NORMAL
    agent_type: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    callback: Optional[Callable] = None
    created_at: datetime = field(default_factory=datetime.now)
    retries: int = 0
    max_retries: int = 3


@dataclass
class TaskResult:
    """Result of a processed task"""
    task_id: str
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    agent_name: str = ""
    processing_time: float = 0.0
    tokens_used: int = 0
    completed_at: datetime = field(default_factory=datetime.now)


class ClaudeAgent:
    """Represents a single Claude agent instance"""

    def __init__(self, config: AgentConfig, api_key: str):
        self.config = config
        self.client = anthropic.Anthropic(api_key=api_key)
        self.status = AgentStatus.IDLE
        self.current_task: Optional[Task] = None
        self.tasks_completed = 0
        self.total_tokens_used = 0
        self.created_at = datetime.now()
        self.last_used = None

    async def process_task(self, task: Task) -> TaskResult:
        """Process a task using this agent"""
        self.status = AgentStatus.BUSY
        self.current_task = task
        start_time = time.time()

        try:
            # Build messages
            messages = [{"role": "user", "content": task.prompt}]

            # Add context if provided
            if task.context:
                context_str = "\n".join([f"{k}: {v}" for k, v in task.context.items()])
                messages[0]["content"] = f"Context:\n{context_str}\n\nTask:\n{task.prompt}"

            # Call Claude API
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=self.config.system_prompt or "",
                messages=messages
            )

            # Extract response
            response_text = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            # Update stats
            self.tasks_completed += 1
            self.total_tokens_used += tokens_used
            self.last_used = datetime.now()

            result = TaskResult(
                task_id=task.task_id,
                success=True,
                response=response_text,
                agent_name=self.config.name,
                processing_time=time.time() - start_time,
                tokens_used=tokens_used
            )

            # Call callback if provided
            if task.callback:
                await task.callback(result)

            return result

        except Exception as e:
            logging.error(f"Agent {self.config.name} error processing task {task.task_id}: {str(e)}")
            self.status = AgentStatus.ERROR

            return TaskResult(
                task_id=task.task_id,
                success=False,
                error=str(e),
                agent_name=self.config.name,
                processing_time=time.time() - start_time
            )

        finally:
            self.status = AgentStatus.IDLE
            self.current_task = None

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "name": self.config.name,
            "status": self.status.value,
            "specialization": self.config.specialization,
            "tasks_completed": self.tasks_completed,
            "total_tokens_used": self.total_tokens_used,
            "uptime": (datetime.now() - self.created_at).total_seconds(),
            "last_used": self.last_used.isoformat() if self.last_used else None
        }


class AgentManager:
    """Main agent manager for orchestrating multiple Claude agents"""

    def __init__(self, api_key: str, max_concurrent_tasks: int = 5):
        self.api_key = api_key
        self.max_concurrent_tasks = max_concurrent_tasks
        self.agents: Dict[str, ClaudeAgent] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.results: Dict[str, TaskResult] = {}
        self.specialized_agents: Dict[str, List[str]] = defaultdict(list)
        self.running = False
        self.logger = logging.getLogger(__name__)

        # Rate limiting
        self.rate_limit_window = 60  # seconds
        self.max_requests_per_minute = 50
        self.request_timestamps: List[float] = []

        # Metrics
        self.total_tasks_processed = 0
        self.total_tasks_failed = 0
        self.total_tokens_consumed = 0

    def add_agent(self, config: AgentConfig) -> ClaudeAgent:
        """Add a new agent to the pool"""
        agent = ClaudeAgent(config, self.api_key)
        self.agents[config.name] = agent

        if config.specialization:
            self.specialized_agents[config.specialization].append(config.name)

        self.logger.info(f"Added agent: {config.name} (specialization: {config.specialization})")
        return agent

    def remove_agent(self, agent_name: str):
        """Remove an agent from the pool"""
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            if agent.config.specialization:
                self.specialized_agents[agent.config.specialization].remove(agent_name)
            del self.agents[agent_name]
            self.logger.info(f"Removed agent: {agent_name}")

    async def submit_task(self, task: Task) -> str:
        """Submit a task to the queue"""
        # Priority queue uses tuple (priority, item)
        # Lower number = higher priority, so we negate the priority value
        await self.task_queue.put((-task.priority.value, task))
        self.logger.info(f"Task {task.task_id} submitted with priority {task.priority.value}")
        return task.task_id

    def get_available_agent(self, agent_type: Optional[str] = None) -> Optional[ClaudeAgent]:
        """Get an available agent, optionally filtered by type"""
        candidates = []

        if agent_type and agent_type in self.specialized_agents:
            # Get specialized agents
            candidates = [self.agents[name] for name in self.specialized_agents[agent_type]
                         if name in self.agents]
        else:
            # Get all agents
            candidates = list(self.agents.values())

        # Filter for idle agents
        idle_agents = [a for a in candidates if a.status == AgentStatus.IDLE]

        if not idle_agents:
            return None

        # Return least recently used agent
        return min(idle_agents, key=lambda a: a.last_used or datetime.min)

    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        current_time = time.time()

        # Remove timestamps outside the window
        self.request_timestamps = [
            ts for ts in self.request_timestamps
            if current_time - ts < self.rate_limit_window
        ]

        # Check if we're at the limit
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            wait_time = self.rate_limit_window - (current_time - self.request_timestamps[0])
            if wait_time > 0:
                self.logger.warning(f"Rate limit reached, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)

        self.request_timestamps.append(current_time)

    async def _process_queue(self):
        """Main queue processing loop"""
        while self.running:
            try:
                # Get task from queue with timeout
                try:
                    _, task = await asyncio.wait_for(
                        self.task_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Get available agent
                agent = None
                while agent is None and self.running:
                    agent = self.get_available_agent(task.agent_type)
                    if agent is None:
                        await asyncio.sleep(0.1)

                if not self.running:
                    break

                # Check rate limit
                await self._check_rate_limit()

                # Process task
                self.logger.info(f"Processing task {task.task_id} with agent {agent.config.name}")
                result = await agent.process_task(task)

                # Store result
                self.results[task.task_id] = result

                # Update metrics
                if result.success:
                    self.total_tasks_processed += 1
                    self.total_tokens_consumed += result.tokens_used
                else:
                    self.total_tasks_failed += 1

                    # Retry logic
                    if task.retries < task.max_retries:
                        task.retries += 1
                        self.logger.info(f"Retrying task {task.task_id} (attempt {task.retries}/{task.max_retries})")
                        await self.task_queue.put((-task.priority.value, task))

                self.task_queue.task_done()

            except Exception as e:
                self.logger.error(f"Error in queue processing: {str(e)}")

    async def start(self):
        """Start the agent manager"""
        if self.running:
            self.logger.warning("Agent manager is already running")
            return

        self.running = True
        self.logger.info("Agent manager started")

        # Start multiple workers
        workers = [
            asyncio.create_task(self._process_queue())
            for _ in range(self.max_concurrent_tasks)
        ]

        try:
            await asyncio.gather(*workers)
        except asyncio.CancelledError:
            self.logger.info("Agent manager workers cancelled")

    async def stop(self):
        """Stop the agent manager"""
        self.running = False
        self.logger.info("Agent manager stopped")

    async def wait_for_completion(self):
        """Wait for all queued tasks to complete"""
        await self.task_queue.join()

    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Get result for a specific task"""
        return self.results.get(task_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get overall manager statistics"""
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.status == AgentStatus.BUSY),
            "total_tasks_processed": self.total_tasks_processed,
            "total_tasks_failed": self.total_tasks_failed,
            "total_tokens_consumed": self.total_tokens_consumed,
            "queue_size": self.task_queue.qsize(),
            "specializations": dict(self.specialized_agents),
            "agent_stats": [agent.get_stats() for agent in self.agents.values()]
        }
