# Claude Agent Manager

A comprehensive Python framework for managing multiple Claude AI agents with pooling, task distribution, and workflow orchestration. Perfect for building applications that require multiple AI agents working together on complex tasks.

## Features

- **Agent Pool Management**: Create and manage multiple Claude agents with different specializations
- **Task Queue System**: Intelligent task distribution with priority-based queuing
- **Specialized Agents**: Pre-configured agents for different domains (code review, security analysis, data analysis, etc.)
- **Workflow Orchestration**: Chain multiple agents together in complex workflows
- **Rate Limiting**: Built-in rate limiting to stay within API limits
- **Monitoring & Logging**: Comprehensive metrics and logging
- **Configuration Management**: Flexible configuration from environment variables, JSON, or YAML
- **Async/Await Support**: Fully asynchronous for high performance

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd claude_agent_manager

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Quick Start

### Basic Usage

```python
import asyncio
from agent_manager import AgentManager, Task, TaskPriority
from specialized_agents import SpecializedAgents
from config import ConfigLoader

async def main():
    # Load configuration
    config = ConfigLoader.from_env()

    # Create agent manager
    manager = AgentManager(api_key=config.api_key, max_concurrent_tasks=3)

    # Add agents
    manager.add_agent(SpecializedAgents.general_assistant())

    # Start manager
    manager_task = asyncio.create_task(manager.start())

    # Submit task
    task = Task(
        task_id="task1",
        prompt="Explain what REST APIs are.",
        priority=TaskPriority.NORMAL
    )
    await manager.submit_task(task)

    # Wait for completion
    await manager.wait_for_completion()

    # Get result
    result = manager.get_result(task.task_id)
    print(result.response)

    # Stop manager
    await manager.stop()

asyncio.run(main())
```

### Using Specialized Agents

```python
# Add specialized agents
manager.add_agent(SpecializedAgents.code_reviewer())
manager.add_agent(SpecializedAgents.security_analyst())
manager.add_agent(SpecializedAgents.data_analyst())

# Submit task to specific agent type
task = Task(
    task_id="security_check",
    prompt="Review this code for security vulnerabilities...",
    agent_type="security"  # Routes to security_analyst
)
await manager.submit_task(task)
```

### Workflow Orchestration

```python
from workflow import WorkflowBuilder, WorkflowOrchestrator

# Create orchestrator
orchestrator = WorkflowOrchestrator(manager)

# Create a code development workflow
workflow = WorkflowBuilder.code_development_workflow(
    "A user authentication system with JWT tokens"
)

# Execute workflow
result = await orchestrator.execute_workflow(workflow.workflow_id)

print(f"Workflow Status: {result.status}")
print(f"Final Documentation: {result.context['documentation']}")
```

## Available Specialized Agents

The framework includes pre-configured specialized agents:

| Agent | Specialization | Use Case |
|-------|----------------|----------|
| `code_reviewer` | Code Review | Review code for bugs, security, performance |
| `code_generator` | Code Generation | Generate high-quality, production-ready code |
| `data_analyst` | Data Analysis | Analyze datasets and provide insights |
| `technical_writer` | Documentation | Create clear, comprehensive documentation |
| `qa_tester` | Testing | Design test cases and test plans |
| `security_analyst` | Security | Identify vulnerabilities and security issues |
| `devops_engineer` | DevOps | CI/CD pipelines, infrastructure as code |
| `architect` | Software Architecture | System design and architecture patterns |
| `database_expert` | Database Design | Schema design and query optimization |
| `api_designer` | API Design | RESTful and GraphQL API design |
| `ui_ux_specialist` | UI/UX | User interface design and frontend development |
| `general_assistant` | General | General-purpose assistant |

## Pre-built Workflows

The framework includes several pre-built workflows:

### Code Development Workflow
Complete feature development from architecture to testing:
```python
workflow = WorkflowBuilder.code_development_workflow(
    "Feature description here"
)
```
Steps: Architecture Design → Code Generation → Code Review → Test Generation → Documentation

### Security Audit Workflow
Comprehensive security analysis:
```python
workflow = WorkflowBuilder.security_audit_workflow(
    "Codebase description here"
)
```
Steps: Security Scan → Security Code Review → Security Report

### Data Analysis Workflow
End-to-end data analysis:
```python
workflow = WorkflowBuilder.data_analysis_workflow(
    dataset_description="Your dataset",
    analysis_goals="Your goals"
)
```
Steps: Data Analysis → Generate Analysis Code → Create Report

### API Development Workflow
Complete API development lifecycle:
```python
workflow = WorkflowBuilder.api_development_workflow(
    "API requirements here"
)
```
Steps: API Design → Database Design → Implementation → Tests → Documentation

## Creating Custom Workflows

```python
from workflow import Workflow, WorkflowStep

# Create workflow
workflow = Workflow(
    workflow_id="custom_workflow",
    name="My Custom Workflow",
    description="Custom workflow description"
)

# Set initial context
workflow.set_context({"input_data": "some data"})

# Add steps
workflow.add_step(WorkflowStep(
    step_id="step1",
    name="First Step",
    agent_type="code_generation",
    prompt_template="Generate code for: {input_data}",
    transform_output=lambda resp, ctx: {"code": resp}
))

workflow.add_step(WorkflowStep(
    step_id="step2",
    name="Second Step",
    agent_type="code_review",
    prompt_template="Review this code: {code}",
    transform_output=lambda resp, ctx: {"review": resp}
))

# Execute
result = await workflow.execute(manager)
```

## Configuration

### Environment Variables

```bash
export ANTHROPIC_API_KEY="your-api-key"
export MAX_CONCURRENT_TASKS="5"
export RATE_LIMIT_PER_MINUTE="50"
export DEFAULT_MODEL="claude-sonnet-4-5-20250929"
export LOG_LEVEL="INFO"
```

### Configuration File (YAML)

```yaml
api_key: "your-api-key"
max_concurrent_tasks: 5
rate_limit_per_minute: 50
default_model: "claude-sonnet-4-5-20250929"
default_max_tokens: 4096
default_temperature: 1.0
log_level: "INFO"
log_file: "agent_manager.log"
```

Load from file:
```python
config = ConfigLoader.from_yaml("config.yaml")
```

## Monitoring and Metrics

```python
# Get manager statistics
stats = manager.get_stats()
print(f"Total agents: {stats['total_agents']}")
print(f"Active agents: {stats['active_agents']}")
print(f"Tasks processed: {stats['total_tasks_processed']}")
print(f"Tokens consumed: {stats['total_tokens_consumed']}")

# Get agent-specific stats
for agent_stat in stats['agent_stats']:
    print(f"{agent_stat['name']}: {agent_stat['tasks_completed']} tasks")
```

## Advanced Features

### Task Callbacks

```python
async def on_task_complete(result):
    print(f"Task completed: {result.task_id}")
    print(f"Tokens used: {result.tokens_used}")

task = Task(
    task_id="task1",
    prompt="Your prompt here",
    callback=on_task_complete
)
```

### Priority Queue

```python
# High priority task
urgent_task = Task(
    task_id="urgent",
    prompt="Critical task",
    priority=TaskPriority.CRITICAL
)

# Normal priority task
normal_task = Task(
    task_id="normal",
    prompt="Normal task",
    priority=TaskPriority.NORMAL
)

# Urgent task will be processed first
```

### Rate Limiting

Rate limiting is automatic and configurable:
```python
manager = AgentManager(
    api_key=api_key,
    max_concurrent_tasks=5
)
manager.max_requests_per_minute = 50  # Adjust as needed
```

### Retry Logic

Tasks automatically retry on failure:
```python
task = Task(
    task_id="task1",
    prompt="Your prompt",
    max_retries=3  # Will retry up to 3 times on failure
)
```

## Architecture

```
claude_agent_manager/
├── agent_manager.py      # Core agent manager and pool
├── specialized_agents.py # Pre-configured specialized agents
├── workflow.py           # Workflow orchestration system
├── config.py             # Configuration management
├── examples.py           # Usage examples
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## API Reference

### AgentManager

Main class for managing agents and tasks.

**Methods:**
- `add_agent(config: AgentConfig)` - Add an agent to the pool
- `remove_agent(agent_name: str)` - Remove an agent from the pool
- `submit_task(task: Task)` - Submit a task for processing
- `get_result(task_id: str)` - Get result for a task
- `get_stats()` - Get manager statistics
- `start()` - Start processing tasks
- `stop()` - Stop the manager
- `wait_for_completion()` - Wait for all tasks to complete

### Task

Represents a task to be processed.

**Parameters:**
- `task_id: str` - Unique task identifier
- `prompt: str` - The prompt for the agent
- `priority: TaskPriority` - Task priority (LOW, NORMAL, HIGH, CRITICAL)
- `agent_type: Optional[str]` - Specific agent type to use
- `context: Dict[str, Any]` - Additional context
- `callback: Optional[Callable]` - Callback function on completion
- `max_retries: int` - Maximum number of retries (default: 3)

### Workflow

Represents a sequence of agent tasks.

**Methods:**
- `add_step(step: WorkflowStep)` - Add a step to the workflow
- `set_context(context: Dict[str, Any])` - Set workflow context
- `execute(manager: AgentManager)` - Execute the workflow

## Examples

Run the included examples:

```bash
# Basic usage
python examples.py

# Or run specific examples by uncommenting them in examples.py
```

## Best Practices

1. **Agent Pooling**: Create multiple agents of the same type for parallel processing
2. **Task Priorities**: Use priorities to ensure critical tasks are processed first
3. **Error Handling**: Always check `result.success` before using the response
4. **Rate Limiting**: Monitor your API usage and adjust rate limits accordingly
5. **Logging**: Enable logging to debug issues and monitor performance
6. **Workflows**: Use workflows for complex multi-step processes
7. **Resource Cleanup**: Always call `manager.stop()` when done

## Troubleshooting

### API Key Not Found
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

### Rate Limit Errors
Adjust the rate limit:
```python
manager.max_requests_per_minute = 30  # Lower the rate
```

### Task Timeouts
Increase timeout for long-running tasks:
```python
step = WorkflowStep(
    step_id="long_task",
    timeout=600  # 10 minutes
    # ... other parameters
)
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

MIT License

## Support

For issues and questions:
- Open an issue on GitHub
- Check the examples in `examples.py`
- Review the API documentation above

## Credits

Built with Anthropic's Claude API.
