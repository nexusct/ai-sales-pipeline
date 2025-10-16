"""
Sales Workflow Orchestration for Comcast Fiber EDI
Complete pipeline from prospect identification to customer outreach
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from workflow import Workflow, WorkflowStep, WorkflowBuilder
from sales_agents import (
    ProspectData, ResearchData, ServiceabilityResult,
    PricingProposal, SalesAgents
)
from agent_manager import AgentManager, TaskPriority


@dataclass
class SalesOpportunity:
    """Complete sales opportunity data"""
    opportunity_id: str
    prospect: ProspectData
    research: Optional[ResearchData] = None
    use_case: Optional[str] = None
    serviceability: Optional[ServiceabilityResult] = None
    pricing: Optional[PricingProposal] = None
    outreach_message: Optional[str] = None
    stage: str = "prospecting"
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


class SalesWorkflowBuilder:
    """Builder for sales workflow pipelines"""

    @staticmethod
    def complete_sales_pipeline(prospect_data: ProspectData) -> Workflow:
        """
        Create a complete end-to-end sales workflow

        Steps:
        1. Qualify prospect
        2. Research business
        3. Build EDI use case
        4. Check serviceability (simulated)
        5. Create pricing proposal
        6. Generate outreach message
        """

        opportunity_id = f"OPP_{int(datetime.now().timestamp())}"

        workflow = Workflow(
            workflow_id=opportunity_id,
            name="Complete Fiber EDI Sales Pipeline",
            description=f"End-to-end sales process for {prospect_data.company_name}"
        )

        # Set initial context with prospect data
        workflow.set_context({
            "opportunity_id": opportunity_id,
            "company_name": prospect_data.company_name,
            "contact_name": prospect_data.contact_name,
            "contact_title": prospect_data.contact_title,
            "location": prospect_data.location,
            "address": prospect_data.address,
            "industry": prospect_data.industry or "Unknown",
            "company_size": prospect_data.company_size or "Unknown",
            "prospect_data": asdict(prospect_data)
        })

        # Step 1: Qualify Prospect
        workflow.add_step(WorkflowStep(
            step_id="qualify",
            name="Qualify Prospect",
            agent_type="prospecting",
            prompt_template="""Analyze this prospect for Comcast Fiber EDI services:

Company: {company_name}
Contact: {contact_name} - {contact_title}
Industry: {industry}
Company Size: {company_size}
Location: {location}

Tasks:
1. Assess if this company is a good fit for Fiber EDI services
2. Identify the key business drivers that make them a prospect
3. Rate the opportunity (A, B, C, or D)
4. Suggest qualification questions to ask
5. Identify potential objections or challenges

Provide your analysis in JSON format:
{{
  "qualification_score": "A/B/C/D",
  "is_qualified": true/false,
  "key_drivers": ["driver1", "driver2"],
  "potential_objections": ["objection1"],
  "recommended_questions": ["question1"],
  "reasoning": "explanation"
}}""",
            priority=TaskPriority.HIGH,
            transform_output=lambda resp, ctx: {
                "qualification_result": resp,
                "stage": "qualified" if "true" in resp.lower() else "disqualified"
            }
        ))

        # Step 2: Research Business
        workflow.add_step(WorkflowStep(
            step_id="research",
            name="Research Business",
            agent_type="research",
            prompt_template="""Conduct detailed business research for this prospect:

Company: {company_name}
Industry: {industry}
Location: {location}
Size: {company_size}

Qualification Results:
{qualification_result}

Research Tasks:
1. Identify business type and industry vertical
2. Determine likely technology infrastructure
3. Identify business processes that would benefit from EDI
4. List potential pain points with current B2B data exchange
5. Research regulatory requirements (HIPAA, PCI-DSS, SOX, etc.)
6. Identify likely trading partners and ecosystem

Provide comprehensive research in structured format covering:
- Business operations overview
- Technology maturity assessment
- EDI-relevant business processes
- Pain points and challenges
- Regulatory compliance needs
- Integration requirements""",
            priority=TaskPriority.NORMAL,
            transform_output=lambda resp, ctx: {
                "research_results": resp,
                "stage": "researched"
            }
        ))

        # Step 3: Build Use Case
        workflow.add_step(WorkflowStep(
            step_id="use_case",
            name="Build EDI Use Case",
            agent_type="use_case",
            prompt_template="""Create a compelling, customized EDI use case for this prospect:

Company: {company_name}
Industry: {industry}
Contact: {contact_name} ({contact_title})

Business Research:
{research_results}

Create a detailed use case that includes:
1. Executive Summary (2-3 sentences)
2. Current State Challenges
3. Proposed EDI Solution
4. Specific Use Cases (with transaction types)
5. Business Benefits (quantified where possible)
   - Time savings
   - Cost reduction
   - Error reduction
   - Compliance improvements
6. Implementation Approach
7. Expected ROI and Payback Period

Make it specific to their industry and business. Use real EDI transaction sets relevant to their sector.
Format it as a professional document ready to present.""",
            priority=TaskPriority.NORMAL,
            transform_output=lambda resp, ctx: {
                "use_case_document": resp,
                "stage": "use_case_built"
            }
        ))

        # Step 4: Simulate Serviceability Check
        # In production, this would call actual web automation
        workflow.add_step(WorkflowStep(
            step_id="serviceability",
            name="Check Fiber Serviceability",
            agent_type="serviceability",
            prompt_template="""Analyze the serviceability scenario for this location:

Company: {company_name}
Address: {address}
Location: {location}

SIMULATED SERVICEABILITY CHECK RESULT:
(In production, this would be real data from Comcast portal)

Address: {address}
Fiber Available: Yes
Service Types: Fiber DIA (Dedicated Internet Access), Ethernet Private Line
Max Bandwidth: Up to 10 Gbps
Installation Timeframe: 45-90 days
Special Notes: Standard commercial installation, no special construction required

Based on this serviceability result:
1. Confirm fiber availability and service options
2. Recommend optimal bandwidth tier based on business research
3. Note any installation considerations
4. Suggest service configuration (redundancy, SLA level, etc.)
5. Provide next steps for the sales process

Format as a serviceability summary for the sales team.""",
            priority=TaskPriority.HIGH,
            transform_output=lambda resp, ctx: {
                "serviceability_summary": resp,
                "serviceable": True,
                "stage": "serviceability_confirmed"
            }
        ))

        # Step 5: Create Pricing Proposal
        workflow.add_step(WorkflowStep(
            step_id="pricing",
            name="Create Pricing Proposal",
            agent_type="pricing",
            prompt_template="""Create a detailed pricing proposal for this opportunity:

Company: {company_name}
Industry: {industry}

Use Case:
{use_case_document}

Serviceability:
{serviceability_summary}

Create a pricing proposal that includes:

1. Recommended Service Configuration
   - Bandwidth tier
   - Service type (DIA, EPL, etc.)
   - SLA level (99.9% or 99.99%)
   - Redundancy options

2. Pricing Structure (create realistic estimates)
   - Monthly Recurring Cost (MRC)
   - Installation/Setup Cost (NRC)
   - Equipment costs
   - Contract term options (1-year, 3-year, 5-year)

3. Total Cost Analysis
   - Year 1 total cost
   - 3-year total cost of ownership
   - Cost per Mbps analysis

4. Value Justification
   - ROI calculation based on use case benefits
   - Comparison to alternatives
   - TCO advantages

5. Service Inclusions
   - 24/7 support
   - SLA guarantees
   - Monitoring and reporting
   - Professional installation

Format as a professional pricing proposal ready to present to customer.""",
            priority=TaskPriority.NORMAL,
            transform_output=lambda resp, ctx: {
                "pricing_proposal": resp,
                "stage": "pricing_complete"
            }
        ))

        # Step 6: Generate Outreach Message
        workflow.add_step(WorkflowStep(
            step_id="outreach",
            name="Generate Customer Outreach",
            agent_type="outreach",
            prompt_template="""Create a personalized outreach message for this prospect:

Contact: {contact_name}
Title: {contact_title}
Company: {company_name}

Use Case Summary:
{use_case_document}

Pricing Highlights:
{pricing_proposal}

Create THREE outreach assets:

1. INITIAL EMAIL
   - Subject line (compelling, personalized)
   - Email body (150-200 words max)
   - Clear call-to-action
   - Professional signature

2. LINKEDIN MESSAGE
   - Brief introduction (75-100 words)
   - Value proposition
   - Connection or meeting request

3. EXECUTIVE SUMMARY (for attachment)
   - One-page overview
   - Problem, solution, value
   - Key metrics and pricing
   - Next steps

Guidelines:
- Personalize to {contact_name} and their role
- Lead with value, not product features
- Reference industry-specific pain points
- Professional, consultative tone
- Respect their time (brief and focused)
- Include social proof if relevant
- Clear, low-friction next step

Make it compelling enough to get a response.""",
            priority=TaskPriority.HIGH,
            transform_output=lambda resp, ctx: {
                "outreach_materials": resp,
                "stage": "ready_for_outreach"
            }
        ))

        return workflow

    @staticmethod
    def quick_qualification_workflow(prospect_data: ProspectData) -> Workflow:
        """Quick qualification workflow for high-volume prospecting"""

        workflow = Workflow(
            workflow_id=f"QUICK_{int(datetime.now().timestamp())}",
            name="Quick Prospect Qualification",
            description=f"Fast qualification for {prospect_data.company_name}"
        )

        workflow.set_context({
            "company_name": prospect_data.company_name,
            "industry": prospect_data.industry or "Unknown",
            "company_size": prospect_data.company_size or "Unknown",
            "location": prospect_data.location
        })

        workflow.add_step(WorkflowStep(
            step_id="quick_qualify",
            name="Quick Qualification",
            agent_type="prospecting",
            prompt_template="""Quick qualification assessment:

Company: {company_name}
Industry: {industry}
Size: {company_size}

Provide fast assessment:
1. Good fit for Fiber EDI? (Yes/No/Maybe)
2. Priority level (High/Medium/Low)
3. One-sentence reasoning
4. Recommended next action

Keep it brief.""",
            transform_output=lambda resp, ctx: {"quick_qualification": resp}
        ))

        return workflow


class SalesPipelineManager:
    """Manages multiple sales opportunities through the pipeline"""

    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.opportunities: Dict[str, SalesOpportunity] = {}

    async def process_prospect(self, prospect: ProspectData) -> SalesOpportunity:
        """Process a single prospect through the complete pipeline"""

        # Create workflow
        workflow = SalesWorkflowBuilder.complete_sales_pipeline(prospect)

        # Execute workflow
        result = await workflow.execute(self.agent_manager)

        # Create sales opportunity from results
        opportunity = SalesOpportunity(
            opportunity_id=workflow.workflow_id,
            prospect=prospect,
            stage=result.context.get("stage", "unknown")
        )

        # Store results
        if result.success:
            opportunity.research = result.context.get("research_results")
            opportunity.use_case = result.context.get("use_case_document")
            opportunity.pricing = result.context.get("pricing_proposal")
            opportunity.outreach_message = result.context.get("outreach_materials")

        self.opportunities[opportunity.opportunity_id] = opportunity
        return opportunity

    async def batch_qualify_prospects(self, prospects: List[ProspectData]) -> List[Dict[str, Any]]:
        """Quickly qualify multiple prospects"""

        results = []
        for prospect in prospects:
            workflow = SalesWorkflowBuilder.quick_qualification_workflow(prospect)
            result = await workflow.execute(self.agent_manager)

            results.append({
                "prospect": prospect,
                "qualification": result.context.get("quick_qualification"),
                "status": result.status.value
            })

        return results

    def get_opportunity(self, opportunity_id: str) -> Optional[SalesOpportunity]:
        """Retrieve an opportunity by ID"""
        return self.opportunities.get(opportunity_id)

    def get_opportunities_by_stage(self, stage: str) -> List[SalesOpportunity]:
        """Get all opportunities in a specific stage"""
        return [opp for opp in self.opportunities.values() if opp.stage == stage]

    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get summary of current pipeline"""
        stages = {}
        for opp in self.opportunities.values():
            stages[opp.stage] = stages.get(opp.stage, 0) + 1

        return {
            "total_opportunities": len(self.opportunities),
            "by_stage": stages,
            "opportunities": [
                {
                    "id": opp.opportunity_id,
                    "company": opp.prospect.company_name,
                    "stage": opp.stage,
                    "created": opp.created_at.isoformat()
                }
                for opp in self.opportunities.values()
            ]
        }
