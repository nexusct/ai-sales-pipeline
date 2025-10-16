"""
Complete Comcast Fiber EDI Sales Pipeline Example

This demonstrates an end-to-end sales workflow using AI agent coordination:
1. Prospect identification and qualification
2. Business research
3. EDI use case development
4. Serviceability checking
5. Pricing proposal generation
6. Customer outreach creation

IMPORTANT REQUIREMENTS:
- Set ANTHROPIC_API_KEY environment variable
- For real serviceability checks: Install selenium, webdriver-manager
- For LinkedIn/Apollo.io: Use official APIs with proper authentication

LEGAL & ETHICAL REQUIREMENTS:
- Only use data obtained through legitimate means (APIs, authorized access)
- Comply with all platform Terms of Service
- Respect privacy regulations (GDPR, CCPA, etc.)
- Use for legitimate business purposes only
"""

import asyncio
import sys
import os
from datetime import datetime

# Add claude_agent_manager to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'claude_agent_manager'))

from agent_manager import AgentManager
from config import ConfigLoader, setup_logging
from sales_agents import SalesAgents, ProspectData
from sales_workflow import SalesWorkflowBuilder, SalesPipelineManager
from web_automation import create_serviceability_checker
from startup_wizard import run_wizard


# Example prospect data
# In production, this would come from LinkedIn API, Apollo.io API, or your CRM
EXAMPLE_PROSPECTS = [
    ProspectData(
        company_name="MedTech Healthcare Group",
        contact_name="Sarah Johnson",
        contact_title="VP of Operations",
        email="sjohnson@medtechgroup.com",
        linkedin_url="https://linkedin.com/in/sarah-johnson",
        company_size="250-500 employees",
        industry="Healthcare",
        location="Philadelphia, PA",
        address="1234 Market Street, Philadelphia, PA 19103",
        source="LinkedIn Sales Navigator (via API)"
    ),
    ProspectData(
        company_name="Northeast Distribution Partners",
        contact_name="Michael Chen",
        contact_title="Director of IT",
        email="mchen@nedistro.com",
        company_size="100-250 employees",
        industry="Wholesale Distribution",
        location="Boston, MA",
        address="567 Harbor Boulevard, Boston, MA 02110",
        source="Apollo.io (via API)"
    ),
    ProspectData(
        company_name="Precision Manufacturing Corp",
        contact_name="Jennifer Martinez",
        contact_title="CIO",
        email="jmartinez@precisionmfg.com",
        company_size="500+ employees",
        industry="Manufacturing",
        location="Newark, NJ",
        address="890 Industrial Drive, Newark, NJ 07102",
        source="Company Database"
    )
]


async def run_complete_pipeline(prospect: ProspectData, manager: AgentManager):
    """Run complete sales pipeline for a single prospect"""

    print("\n" + "="*80)
    print(f"PROCESSING: {prospect.company_name}")
    print("="*80)

    # Create pipeline manager
    pipeline = SalesPipelineManager(manager)

    # Process prospect through complete workflow
    print(f"\nStarting complete sales workflow for {prospect.company_name}...")
    print(f"Contact: {prospect.contact_name} ({prospect.contact_title})")
    print(f"Industry: {prospect.industry}")
    print(f"Location: {prospect.location}")

    opportunity = await pipeline.process_prospect(prospect)

    print(f"\n{'='*80}")
    print(f"WORKFLOW COMPLETE - {prospect.company_name}")
    print(f"{'='*80}")
    print(f"Opportunity ID: {opportunity.opportunity_id}")
    print(f"Final Stage: {opportunity.stage}")

    # Display results
    if opportunity.stage == "ready_for_outreach":
        print("\n" + "-"*80)
        print("USE CASE DOCUMENT")
        print("-"*80)
        if opportunity.use_case:
            print(opportunity.use_case[:1000])
            print("...\n")

        print("-"*80)
        print("PRICING PROPOSAL")
        print("-"*80)
        if opportunity.pricing:
            print(opportunity.pricing[:1000])
            print("...\n")

        print("-"*80)
        print("OUTREACH MATERIALS")
        print("-"*80)
        if opportunity.outreach_message:
            print(opportunity.outreach_message[:1500])
            print("...\n")

    return opportunity


async def run_batch_qualification(prospects: list[ProspectData], manager: AgentManager):
    """Quick qualification of multiple prospects"""

    print("\n" + "="*80)
    print("BATCH QUALIFICATION MODE")
    print("="*80)
    print(f"Qualifying {len(prospects)} prospects...\n")

    pipeline = SalesPipelineManager(manager)
    results = await pipeline.batch_qualify_prospects(prospects)

    print("\nQUALIFICATION RESULTS:")
    print("-"*80)

    for i, result in enumerate(results, 1):
        prospect = result['prospect']
        qualification = result['qualification']

        print(f"\n{i}. {prospect.company_name}")
        print(f"   Industry: {prospect.industry}")
        print(f"   Qualification: {qualification[:200]}...")

    return results


async def demonstrate_serviceability_checking():
    """Demonstrate serviceability checking (mock mode)"""

    print("\n" + "="*80)
    print("SERVICEABILITY CHECKING DEMO")
    print("="*80)
    print("\nNOTE: Using MOCK data. For production:")
    print("- Install: pip install selenium webdriver-manager")
    print("- Provide portal credentials")
    print("- Update web_automation.py selectors for actual portal\n")

    # Create mock checker
    checker = create_serviceability_checker(use_real_portal=False)

    addresses = [
        "1234 Market Street, Philadelphia, PA 19103",
        "567 Harbor Boulevard, Boston, MA 02110",
        "890 Industrial Drive, Newark, NJ 07102"
    ]

    for address in addresses:
        print(f"\nChecking: {address}")
        result = checker.check_serviceability(address)

        print(f"  Serviceable: {'YES' if result.serviceable else 'NO'}")
        if result.serviceable:
            print(f"  Service Types: {', '.join(result.service_types)}")
            print(f"  Max Bandwidth: {result.max_bandwidth}")
            print(f"  Install Estimate: {result.installation_estimate_days} days")
        print(f"  Notes: {result.notes}")

    checker.close()


async def main():
    """Main execution function"""

    try:
        # Run the interactive wizard to collect configuration
        wizard_config = run_wizard()

        # Set API key in environment for config loader
        os.environ['ANTHROPIC_API_KEY'] = wizard_config.api_key
        os.environ['MAX_CONCURRENT_TASKS'] = str(wizard_config.max_concurrent_tasks)
        os.environ['RATE_LIMIT_PER_MINUTE'] = str(wizard_config.rate_limit_per_minute)
        os.environ['LOG_LEVEL'] = wizard_config.log_level

        # Load configuration
        config = ConfigLoader.from_env()
        setup_logging(config)

        # Convert custom prospects to ProspectData objects if provided
        prospects = EXAMPLE_PROSPECTS
        if not wizard_config.use_example_prospects and wizard_config.custom_prospects:
            prospects = [
                ProspectData(
                    company_name=p['company_name'],
                    contact_name=p['contact_name'],
                    contact_title=p['contact_title'],
                    email=p['email'],
                    linkedin_url=p.get('linkedin_url', ''),
                    company_size=p['company_size'],
                    industry=p['industry'],
                    location=p['location'],
                    address=p['address'],
                    source=p.get('source', 'Manual Entry')
                )
                for p in wizard_config.custom_prospects
            ]

        # Map wizard mode to choice
        mode_map = {
            'complete': '1',
            'batch': '2',
            'serviceability': '3',
            'all': '4'
        }
        choice = mode_map.get(wizard_config.mode, '1')

        # Create agent manager with wizard settings
        print("\nInitializing agent manager...")
        print(f"  • Max concurrent tasks: {wizard_config.max_concurrent_tasks}")
        print(f"  • Rate limit: {wizard_config.rate_limit_per_minute} requests/minute")
        manager = AgentManager(
            api_key=config.api_key,
            max_concurrent_tasks=wizard_config.max_concurrent_tasks
        )

        # Add all sales agents
        print("Loading specialized sales agents...")
        sales_team = SalesAgents.create_sales_team()
        for agent_config in sales_team:
            manager.add_agent(agent_config)
            print(f"  [OK] {agent_config.name}")

        # Start manager
        print("\nStarting agent manager...")
        manager_task = asyncio.create_task(manager.start())

        # Execute based on choice
        if choice == "1":
            # Complete pipeline for first prospect
            await run_complete_pipeline(prospects[0], manager)

        elif choice == "2":
            # Batch qualification
            await run_batch_qualification(prospects, manager)

        elif choice == "3":
            # Serviceability demo (use portal credentials if provided)
            if wizard_config.portal_credentials:
                print("\n[WARN] Real portal mode selected.")
                print("Note: You'll need to update web_automation.py selectors for your portal")
            await demonstrate_serviceability_checking()

        elif choice == "4":
            # Run all
            print("\n" + "="*80)
            print("RUNNING ALL EXAMPLES")
            print("="*80)

            # Serviceability demo
            await demonstrate_serviceability_checking()

            # Batch qualification
            await run_batch_qualification(prospects, manager)

            # Complete pipeline for one prospect
            await run_complete_pipeline(prospects[0], manager)

        else:
            print("Invalid choice, running default (option 1)")
            await run_complete_pipeline(prospects[0], manager)

        # Display statistics
        print("\n" + "="*80)
        print("AGENT MANAGER STATISTICS")
        print("="*80)

        stats = manager.get_stats()
        print(f"\nTotal Tasks Processed: {stats['total_tasks_processed']}")
        print(f"Total Tasks Failed: {stats['total_tasks_failed']}")
        print(f"Total Tokens Consumed: {stats['total_tokens_consumed']:,}")
        print(f"Active Agents: {stats['active_agents']}")

        print("\nAgent Performance:")
        for agent_stat in stats['agent_stats']:
            if agent_stat['tasks_completed'] > 0:
                print(f"  {agent_stat['name']}: "
                      f"{agent_stat['tasks_completed']} tasks, "
                      f"{agent_stat['total_tokens_used']:,} tokens")

        # Cleanup
        await manager.stop()
        manager_task.cancel()

        print("\n" + "="*80)
        print("PIPELINE EXECUTION COMPLETE")
        print("="*80)

        print("\n[OK] SUCCESS! The sales pipeline demonstration completed.")
        print("\nNext Steps:")
        print("1. Review the generated use cases, pricing, and outreach materials")
        print("2. Customize agent prompts in sales_agents.py for your needs")
        print("3. Integrate with real data sources (LinkedIn API, Apollo.io API)")
        print("4. Set up web automation for actual serviceability portal")
        print("5. Connect to your CRM for opportunity tracking")

    except Exception as e:
        print(f"\n[FAIL] ERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure ANTHROPIC_API_KEY is set in environment")
        print("2. Install requirements: pip install -r claude_agent_manager/requirements.txt")
        print("3. Check that all modules are in the correct directory")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
