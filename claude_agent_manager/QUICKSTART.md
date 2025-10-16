# Quick Start Guide

Get up and running with Claude Agent Manager in 5 minutes!

## 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## 2. Set Up API Key

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
# ANTHROPIC_API_KEY=your-actual-api-key-here

# On Windows:
set ANTHROPIC_API_KEY=your-api-key

# On Mac/Linux:
export ANTHROPIC_API_KEY=your-api-key
```

## 3. Run Your First Example

```python
# Create a file: my_first_agent.py

import asyncio
from agent_manager import AgentManager, Task, TaskPriority
from specialized_agents import SpecializedAgents
from config import ConfigLoader, setup_logging

async def main():
    # Load configuration from environment
    config = ConfigLoader.from_env()
    setup_logging(config)

    # Create agent manager with 2 concurrent tasks
    manager = AgentManager(api_key=config.api_key, max_concurrent_tasks=2)

    # Add a general purpose agent
    manager.add_agent(SpecializedAgents.general_assistant())

    # Start the manager in background
    manager_task = asyncio.create_task(manager.start())

    # Create and submit a task
    task = Task(
        task_id="my_first_task",
        prompt="Explain what Claude AI is in 3 sentences.",
        priority=TaskPriority.NORMAL
    )

    print("Submitting task...")
    await manager.submit_task(task)

    # Wait for task to complete
    print("Waiting for result...")
    await manager.wait_for_completion()

    # Get and print the result
    result = manager.get_result(task.task_id)

    if result.success:
        print(f"\nResponse from Claude:\n{result.response}")
        print(f"\nTokens used: {result.tokens_used}")
        print(f"Processing time: {result.processing_time:.2f}s")
    else:
        print(f"Error: {result.error}")

    # Cleanup
    await manager.stop()
    manager_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python my_first_agent.py
```

## 4. Try Specialized Agents

```python
# Create a file: specialized_example.py

import asyncio
from agent_manager import AgentManager, Task
from specialized_agents import SpecializedAgents
from config import ConfigLoader

async def main():
    config = ConfigLoader.from_env()
    manager = AgentManager(api_key=config.api_key, max_concurrent_tasks=3)

    # Add different specialized agents
    manager.add_agent(SpecializedAgents.code_generator())
    manager.add_agent(SpecializedAgents.code_reviewer())
    manager.add_agent(SpecializedAgents.technical_writer())

    manager_task = asyncio.create_task(manager.start())

    # Generate code
    code_task = Task(
        task_id="generate",
        prompt="Write a Python function to calculate fibonacci numbers.",
        agent_type="code_generation"
    )
    await manager.submit_task(code_task)
    await manager.wait_for_completion()

    code = manager.get_result("generate").response
    print(f"Generated Code:\n{code}\n")

    # Review the code
    review_task = Task(
        task_id="review",
        prompt=f"Review this code:\n{code}",
        agent_type="code_review"
    )
    await manager.submit_task(review_task)
    await manager.wait_for_completion()

    review = manager.get_result("review").response
    print(f"Code Review:\n{review}\n")

    await manager.stop()
    manager_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
```

## 5. Use Workflows

```python
# Create a file: workflow_example.py

import asyncio
from agent_manager import AgentManager
from specialized_agents import SpecializedAgents
from workflow import WorkflowBuilder, WorkflowOrchestrator
from config import ConfigLoader

async def main():
    config = ConfigLoader.from_env()
    manager = AgentManager(api_key=config.api_key, max_concurrent_tasks=5)

    # Add agents needed for the workflow
    agent_types = ["architecture", "code_generation", "code_review", "testing", "documentation"]
    for agent_type in agent_types:
        agents = SpecializedAgents.create_agent_pool([agent_type])
        for agent_config in agents:
            manager.add_agent(agent_config)

    manager_task = asyncio.create_task(manager.start())

    # Create workflow orchestrator
    orchestrator = WorkflowOrchestrator(manager)

    # Create and execute a code development workflow
    workflow = WorkflowBuilder.code_development_workflow(
        "A simple todo list API with CRUD operations"
    )

    orchestrator.register_workflow(workflow)
    print("Executing workflow...")

    result = await orchestrator.execute_workflow(workflow.workflow_id)

    print(f"\nWorkflow Status: {result.status.value}")
    print(f"Steps Completed: {result.steps_completed}")
    print(f"Execution Time: {result.execution_time:.2f}s")

    # Print final outputs
    print("\n=== Architecture Design ===")
    print(result.context.get('architecture_design', 'N/A')[:500])

    print("\n=== Generated Code ===")
    print(result.context.get('generated_code', 'N/A')[:500])

    print("\n=== Documentation ===")
    print(result.context.get('documentation', 'N/A')[:500])

    await manager.stop()
    manager_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
```

## Common Patterns

### Pattern 1: Single Task Processing

```python
manager = AgentManager(api_key=api_key, max_concurrent_tasks=1)
manager.add_agent(SpecializedAgents.general_assistant())

manager_task = asyncio.create_task(manager.start())
await manager.submit_task(task)
await manager.wait_for_completion()
result = manager.get_result(task.task_id)
await manager.stop()
```

### Pattern 2: Parallel Task Processing

```python
manager = AgentManager(api_key=api_key, max_concurrent_tasks=5)

# Add multiple agents
for i in range(5):
    manager.add_agent(SpecializedAgents.general_assistant())

manager_task = asyncio.create_task(manager.start())

# Submit multiple tasks
for task in tasks:
    await manager.submit_task(task)

# All tasks process in parallel
await manager.wait_for_completion()
```

### Pattern 3: Agent Specialization

```python
# Use specific agents for specific tasks
manager.add_agent(SpecializedAgents.code_generator())
manager.add_agent(SpecializedAgents.code_reviewer())

# Route tasks to specific agents
code_task = Task(task_id="gen", prompt="...", agent_type="code_generation")
review_task = Task(task_id="rev", prompt="...", agent_type="code_review")
```

## Next Steps

1. Check out `examples.py` for more comprehensive examples
2. Read the full `README.md` for detailed documentation
3. Explore the `workflow.py` module for advanced workflow patterns
4. Create your own specialized agents
5. Build custom workflows for your use cases

## Troubleshooting

**Problem**: "ANTHROPIC_API_KEY environment variable not set"
- **Solution**: Make sure you've set the environment variable correctly

**Problem**: Rate limit errors
- **Solution**: Reduce `max_concurrent_tasks` or `RATE_LIMIT_PER_MINUTE`

**Problem**: Tasks timing out
- **Solution**: Increase the timeout value in WorkflowStep or use simpler prompts

## Getting Help

- Check the examples in `examples.py`
- Read the full documentation in `README.md`
- Review the code comments in each module

Happy coding with Claude Agent Manager!
