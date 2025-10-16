"""
Example Usage of Claude Agent Manager
Demonstrates various use cases and patterns.
"""

import asyncio
import uuid
from agent_manager import AgentManager, Task, TaskPriority
from specialized_agents import SpecializedAgents
from workflow import WorkflowBuilder, WorkflowOrchestrator, Workflow, WorkflowStep
from config import ConfigLoader, setup_logging


async def example_1_basic_usage():
    """Example 1: Basic agent manager usage"""
    print("\n=== Example 1: Basic Usage ===\n")

    # Load configuration from environment
    config = ConfigLoader.from_env()
    setup_logging(config)

    # Create agent manager
    manager = AgentManager(api_key=config.api_key, max_concurrent_tasks=3)

    # Add some general agents
    for i in range(3):
        manager.add_agent(SpecializedAgents.general_assistant())

    # Start manager in background
    manager_task = asyncio.create_task(manager.start())

    # Submit some tasks
    task1 = Task(
        task_id=str(uuid.uuid4()),
        prompt="Explain what a REST API is in simple terms.",
        priority=TaskPriority.NORMAL
    )

    task2 = Task(
        task_id=str(uuid.uuid4()),
        prompt="What are the benefits of using Docker?",
        priority=TaskPriority.HIGH
    )

    await manager.submit_task(task1)
    await manager.submit_task(task2)

    # Wait for completion
    await manager.wait_for_completion()

    # Get results
    result1 = manager.get_result(task1.task_id)
    result2 = manager.get_result(task2.task_id)

    print(f"Task 1 Result:\n{result1.response}\n")
    print(f"Task 2 Result:\n{result2.response}\n")

    # Print stats
    stats = manager.get_stats()
    print(f"Manager Stats: {stats}")

    # Stop manager
    await manager.stop()
    manager_task.cancel()


async def example_2_specialized_agents():
    """Example 2: Using specialized agents"""
    print("\n=== Example 2: Specialized Agents ===\n")

    config = ConfigLoader.from_env()
    manager = AgentManager(api_key=config.api_key, max_concurrent_tasks=5)

    # Add specialized agents
    manager.add_agent(SpecializedAgents.code_reviewer())
    manager.add_agent(SpecializedAgents.code_generator())
    manager.add_agent(SpecializedAgents.security_analyst())

    # Start manager
    manager_task = asyncio.create_task(manager.start())

    # Generate code with code_generator
    code_task = Task(
        task_id=str(uuid.uuid4()),
        prompt="Write a Python function to validate email addresses using regex.",
        priority=TaskPriority.NORMAL,
        agent_type="code_generation"
    )
    await manager.submit_task(code_task)
    await manager.wait_for_completion()

    code_result = manager.get_result(code_task.task_id)
    print(f"Generated Code:\n{code_result.response}\n")

    # Review the code with code_reviewer
    review_task = Task(
        task_id=str(uuid.uuid4()),
        prompt=f"Review this code:\n\n{code_result.response}",
        priority=TaskPriority.HIGH,
        agent_type="code_review"
    )
    await manager.submit_task(review_task)
    await manager.wait_for_completion()

    review_result = manager.get_result(review_task.task_id)
    print(f"Code Review:\n{review_result.response}\n")

    # Security check
    security_task = Task(
        task_id=str(uuid.uuid4()),
        prompt=f"Check for security issues:\n\n{code_result.response}",
        priority=TaskPriority.CRITICAL,
        agent_type="security"
    )
    await manager.submit_task(security_task)
    await manager.wait_for_completion()

    security_result = manager.get_result(security_task.task_id)
    print(f"Security Analysis:\n{security_result.response}\n")

    await manager.stop()
    manager_task.cancel()


async def example_3_workflow_execution():
    """Example 3: Using workflow orchestration"""
    print("\n=== Example 3: Workflow Orchestration ===\n")

    config = ConfigLoader.from_env()
    manager = AgentManager(api_key=config.api_key, max_concurrent_tasks=5)

    # Add all necessary specialized agents
    agent_types = ["architecture", "code_generation", "code_review", "testing", "documentation"]
    for agent_type in agent_types:
        agents_pool = SpecializedAgents.create_agent_pool([agent_type])
        for agent_config in agents_pool:
            manager.add_agent(agent_config)

    # Start manager
    manager_task = asyncio.create_task(manager.start())

    # Create workflow orchestrator
    orchestrator = WorkflowOrchestrator(manager)

    # Create a code development workflow
    workflow = WorkflowBuilder.code_development_workflow(
        "A user authentication system with JWT tokens"
    )

    # Register and execute workflow
    orchestrator.register_workflow(workflow)
    result = await orchestrator.execute_workflow(workflow.workflow_id)

    # Print results
    print(f"Workflow Status: {result.status.value}")
    print(f"Steps Completed: {result.steps_completed}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    print(f"\nFinal Context:")
    for key, value in result.context.items():
        print(f"\n{key}:")
        print(f"{str(value)[:200]}...")

    await manager.stop()
    manager_task.cancel()


async def example_4_custom_workflow():
    """Example 4: Creating a custom workflow"""
    print("\n=== Example 4: Custom Workflow ===\n")

    config = ConfigLoader.from_env()
    manager = AgentManager(api_key=config.api_key, max_concurrent_tasks=3)

    # Add agents
    manager.add_agent(SpecializedAgents.code_generator())
    manager.add_agent(SpecializedAgents.qa_tester())
    manager.add_agent(SpecializedAgents.technical_writer())

    manager_task = asyncio.create_task(manager.start())

    # Create custom workflow
    workflow = Workflow(
        workflow_id="custom_" + str(uuid.uuid4()),
        name="Custom Feature Workflow",
        description="Build, test, and document a feature"
    )

    workflow.set_context({"feature": "password strength checker"})

    # Step 1: Generate implementation
    workflow.add_step(WorkflowStep(
        step_id="implement",
        name="Implement Feature",
        agent_type="code_generation",
        prompt_template="Implement a {feature} in Python with proper validation.",
        transform_output=lambda resp, ctx: {"implementation": resp}
    ))

    # Step 2: Generate tests
    workflow.add_step(WorkflowStep(
        step_id="test",
        name="Create Tests",
        agent_type="testing",
        prompt_template="Create unit tests for:\n{implementation}",
        transform_output=lambda resp, ctx: {"tests": resp}
    ))

    # Step 3: Write documentation
    workflow.add_step(WorkflowStep(
        step_id="document",
        name="Write Docs",
        agent_type="documentation",
        prompt_template="Write user documentation for:\n{implementation}",
        transform_output=lambda resp, ctx: {"documentation": resp}
    ))

    # Execute workflow
    result = await workflow.execute(manager)

    print(f"Workflow completed: {result.status.value}")
    print(f"\nImplementation:\n{result.context['implementation'][:300]}...")
    print(f"\nTests:\n{result.context['tests'][:300]}...")
    print(f"\nDocumentation:\n{result.context['documentation'][:300]}...")

    await manager.stop()
    manager_task.cancel()


async def example_5_parallel_tasks():
    """Example 5: Parallel task execution"""
    print("\n=== Example 5: Parallel Task Execution ===\n")

    config = ConfigLoader.from_env()
    manager = AgentManager(api_key=config.api_key, max_concurrent_tasks=5)

    # Add multiple general agents
    for i in range(5):
        manager.add_agent(SpecializedAgents.general_assistant())

    manager_task = asyncio.create_task(manager.start())

    # Submit multiple tasks in parallel
    tasks = []
    questions = [
        "What is machine learning?",
        "Explain microservices architecture.",
        "What are the SOLID principles?",
        "Describe the benefits of TDD.",
        "What is continuous integration?"
    ]

    for question in questions:
        task = Task(
            task_id=str(uuid.uuid4()),
            prompt=question,
            priority=TaskPriority.NORMAL
        )
        tasks.append(task)
        await manager.submit_task(task)

    # Wait for all tasks to complete
    await manager.wait_for_completion()

    # Print results
    for i, task in enumerate(tasks):
        result = manager.get_result(task.task_id)
        print(f"\nQuestion {i+1}: {questions[i]}")
        print(f"Answer: {result.response[:200]}...")

    # Print stats
    stats = manager.get_stats()
    print(f"\nTotal tokens consumed: {stats['total_tokens_consumed']}")
    print(f"Total tasks processed: {stats['total_tasks_processed']}")

    await manager.stop()
    manager_task.cancel()


async def example_6_callback_handling():
    """Example 6: Task callbacks"""
    print("\n=== Example 6: Task Callbacks ===\n")

    config = ConfigLoader.from_env()
    manager = AgentManager(api_key=config.api_key, max_concurrent_tasks=2)

    manager.add_agent(SpecializedAgents.general_assistant())
    manager.add_agent(SpecializedAgents.general_assistant())

    manager_task = asyncio.create_task(manager.start())

    # Define callback function
    async def task_completed_callback(result):
        print(f"\n[CALLBACK] Task {result.task_id} completed!")
        print(f"[CALLBACK] Success: {result.success}")
        print(f"[CALLBACK] Processing time: {result.processing_time:.2f}s")
        print(f"[CALLBACK] Tokens used: {result.tokens_used}")

    # Create tasks with callbacks
    task1 = Task(
        task_id=str(uuid.uuid4()),
        prompt="Explain what async/await is in Python.",
        callback=task_completed_callback
    )

    task2 = Task(
        task_id=str(uuid.uuid4()),
        prompt="What are Python decorators?",
        callback=task_completed_callback
    )

    await manager.submit_task(task1)
    await manager.submit_task(task2)

    await manager.wait_for_completion()

    await manager.stop()
    manager_task.cancel()


async def main():
    """Run all examples"""
    print("Claude Agent Manager - Examples\n")
    print("=" * 50)

    try:
        # Run examples (uncomment the ones you want to run)
        await example_1_basic_usage()
        # await example_2_specialized_agents()
        # await example_3_workflow_execution()
        # await example_4_custom_workflow()
        # await example_5_parallel_tasks()
        # await example_6_callback_handling()

    except Exception as e:
        print(f"\nError running examples: {str(e)}")
        print("Make sure ANTHROPIC_API_KEY environment variable is set.")


if __name__ == "__main__":
    asyncio.run(main())
