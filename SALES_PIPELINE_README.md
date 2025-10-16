# Comcast Fiber EDI Sales Pipeline - AI Agent Cluster

A comprehensive AI-powered sales automation system that coordinates multiple specialized agents to manage the entire sales pipeline from prospect identification through customer outreach.

## 🎯 What This System Does

This agent cluster automates and assists with the complete sales workflow for Comcast Fiber EDI services:

1. **Prospect Identification & Qualification** - Identifies ideal prospects from your data sources
2. **Business Research** - Analyzes business type, industry, and technology needs
3. **EDI Use Case Development** - Creates customized, compelling use cases
4. **Fiber Serviceability Checking** - Automates portal checks (with web automation)
5. **Pricing Proposal Generation** - Creates competitive, value-based pricing
6. **Customer Outreach** - Generates personalized emails, messages, and presentations

## ⚠️ IMPORTANT LEGAL & ETHICAL REQUIREMENTS

**READ THIS BEFORE USING:**

### Data Sources
- ✅ **ALLOWED**: Official APIs (LinkedIn Sales Navigator API, Apollo.io API, your CRM)
- ✅ **ALLOWED**: Data you own or have legitimate access to
- ✅ **ALLOWED**: Publicly available business information
- ❌ **NOT ALLOWED**: Web scraping without permission
- ❌ **NOT ALLOWED**: Violating platform Terms of Service
- ❌ **NOT ALLOWED**: Bulk harvesting of contact data without authorization

### Portal Access
- ✅ **ALLOWED**: Using authorized Comcast partner/employee portal credentials
- ✅ **ALLOWED**: Automating with proper business authorization
- ❌ **NOT ALLOWED**: Unauthorized portal access
- ❌ **NOT ALLOWED**: Credential sharing or misuse

### Outreach Compliance
- ✅ **MUST**: Comply with CAN-SPAM Act
- ✅ **MUST**: Respect GDPR, CCPA privacy regulations
- ✅ **MUST**: Honor opt-outs and unsubscribe requests
- ✅ **MUST**: Use legitimate business contact information
- ❌ **NOT ALLOWED**: Unsolicited spam
- ❌ **NOT ALLOWED**: Purchased email lists without consent

## 🏗️ Architecture

### Agent Cluster

The system uses 7 specialized AI agents:

| Agent | Role | Specialization |
|-------|------|----------------|
| **Prospect Finder** | Identifies and qualifies leads | Lead scoring, qualification criteria |
| **Business Researcher** | Analyzes business requirements | Industry analysis, pain points, tech stack |
| **Use Case Builder** | Creates EDI solutions | ROI calculation, industry-specific use cases |
| **Serviceability Analyst** | Interprets serviceability results | Network planning, alternatives |
| **Pricing Analyst** | Develops proposals | TCO analysis, competitive pricing |
| **Outreach Specialist** | Crafts communications | Email sequences, presentations |
| **Sales Coordinator** | Orchestrates pipeline | Process management, quality gates |

### Workflow Pipeline

```
Prospect Data (LinkedIn/Apollo/CRM)
    ↓
[1. Qualification] → Prospect Finder Agent
    ↓
[2. Research] → Business Research Agent
    ↓
[3. Use Case] → Use Case Builder Agent
    ↓
[4. Serviceability] → Web Automation + Serviceability Analyst
    ↓
[5. Pricing] → Pricing Analyst Agent
    ↓
[6. Outreach] → Outreach Specialist Agent
    ↓
Complete Sales Package Ready
```

## 📋 Prerequisites

### Required
```bash
# Python 3.9+
python --version

# Anthropic API Key
export ANTHROPIC_API_KEY="your-api-key"

# Install base requirements
pip install -r claude_agent_manager/requirements.txt
```

### For Web Automation (Serviceability Checking)
```bash
# Install Selenium and WebDriver
pip install selenium webdriver-manager
```

### For Data Integration
- LinkedIn Sales Navigator API credentials (for LinkedIn data)
- Apollo.io API key (for Apollo.io data)
- CRM API access (Salesforce, HubSpot, etc.)

## 🚀 Quick Start

### 1. Basic Setup

```bash
# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Run the sales pipeline example
python run_sales_pipeline.py
```

### 2. Choose Mode

The system offers 4 modes:

1. **Complete Pipeline** - Full workflow for one prospect
2. **Batch Qualification** - Quick assessment of multiple prospects
3. **Serviceability Demo** - Test serviceability checking
4. **Run All** - Demonstrate all capabilities

### 3. Review Output

The system generates:
- Qualification assessment
- Business research report
- Custom EDI use case document
- Serviceability analysis
- Pricing proposal
- Email templates and outreach materials

## 📖 Usage Examples

### Example 1: Process Single Prospect

```python
from sales_agents import ProspectData
from sales_workflow import SalesPipelineManager
from agent_manager import AgentManager
from config import ConfigLoader

# Create prospect (from your data source)
prospect = ProspectData(
    company_name="Healthcare Corp",
    contact_name="John Smith",
    contact_title="VP of IT",
    email="jsmith@healthcarecorp.com",
    company_size="500+ employees",
    industry="Healthcare",
    location="Philadelphia, PA",
    address="123 Main St, Philadelphia, PA 19103",
    source="LinkedIn Sales Navigator API"
)

# Initialize
config = ConfigLoader.from_env()
manager = AgentManager(api_key=config.api_key)

# Add sales agents
from sales_agents import SalesAgents
for agent in SalesAgents.create_sales_team():
    manager.add_agent(agent)

# Process prospect
pipeline = SalesPipelineManager(manager)
opportunity = await pipeline.process_prospect(prospect)

# Access results
print(opportunity.use_case)
print(opportunity.pricing)
print(opportunity.outreach_message)
```

### Example 2: Batch Qualification

```python
# Multiple prospects from your data source
prospects = [
    prospect1,
    prospect2,
    prospect3,
    # ... more prospects
]

# Quick qualification
results = await pipeline.batch_qualify_prospects(prospects)

# Filter qualified prospects
qualified = [r for r in results if "qualified: true" in r['qualification'].lower()]
```

### Example 3: Serviceability Checking

```python
from web_automation import create_serviceability_checker

# Mock mode (for testing)
checker = create_serviceability_checker(use_real_portal=False)
result = checker.check_serviceability("123 Main St, Philadelphia, PA")

# Real portal mode (requires credentials)
checker = create_serviceability_checker(
    use_real_portal=True,
    username="your_portal_username",
    password="your_portal_password"
)
result = checker.check_serviceability("123 Main St, Philadelphia, PA")

print(f"Serviceable: {result.serviceable}")
print(f"Services: {result.service_types}")
print(f"Max Bandwidth: {result.max_bandwidth}")
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Optional
export MAX_CONCURRENT_TASKS="5"
export RATE_LIMIT_PER_MINUTE="50"
export LOG_LEVEL="INFO"
```

### Agent Customization

Edit `claude_agent_manager/sales_agents.py` to customize agent behavior:

```python
# Modify system prompts for your business
@staticmethod
def use_case_builder() -> AgentConfig:
    return AgentConfig(
        name="use_case_builder",
        system_prompt="""Your custom prompt here..."""
    )
```

### Web Automation Setup

For real serviceability checking:

1. **Update selectors** in `claude_agent_manager/web_automation.py`:
```python
# Update these based on actual Comcast portal
username_field = wait.until(
    EC.presence_of_element_located((By.ID, "actual-username-id"))
)
```

2. **Configure authentication**:
```python
checker = ComcastPortalAutomation(
    username="your_authorized_username",
    password="your_password"
)
checker.authenticate(portal_url="https://actual-portal-url.com")
```

3. **Test manually** to identify correct selectors

## 📊 Data Integration

### LinkedIn Sales Navigator API

```python
# Example: Fetch prospects from LinkedIn
import requests

headers = {
    "Authorization": f"Bearer {linkedin_token}",
    "X-Restli-Protocol-Version": "2.0.0"
}

response = requests.get(
    "https://api.linkedin.com/v2/salesNavigatorLeads",
    headers=headers,
    params={"q": "search", "keywords": "healthcare CIO"}
)

# Convert to ProspectData
for lead in response.json()['elements']:
    prospect = ProspectData(
        company_name=lead['company']['name'],
        contact_name=lead['firstName'] + " " + lead['lastName'],
        # ... map other fields
    )
```

### Apollo.io API

```python
import requests

response = requests.post(
    "https://api.apollo.io/v1/mixed_people/search",
    headers={"X-Api-Key": apollo_api_key},
    json={
        "q_keywords": "VP Operations",
        "person_titles": ["VP of Operations", "Director of Operations"],
        "organization_num_employees_ranges": ["51-200", "201-500"]
    }
)

# Convert to ProspectData objects
```

### CRM Integration (Salesforce Example)

```python
from simple_salesforce import Salesforce

sf = Salesforce(username='user', password='pass', security_token='token')

# Query opportunities
opportunities = sf.query("SELECT Id, Name, Account.Name FROM Opportunity WHERE Stage = 'Prospecting'")

# Convert to ProspectData
for opp in opportunities['records']:
    prospect = ProspectData(
        company_name=opp['Account']['Name'],
        # ... map fields
    )
```

## 📈 Pipeline Stages

The system tracks opportunities through these stages:

1. **prospecting** - Initial identification
2. **qualified** - Passed qualification criteria
3. **researched** - Business research complete
4. **use_case_built** - Custom use case created
5. **serviceability_confirmed** - Fiber availability confirmed
6. **pricing_complete** - Proposal generated
7. **ready_for_outreach** - All materials ready
8. **contacted** - Outreach sent
9. **engaged** - Prospect responded
10. **opportunity** - Active sales opportunity

## 🎛️ Advanced Features

### Custom Workflows

Create specialized workflows for different scenarios:

```python
from workflow import Workflow, WorkflowStep

# Quick qualification for high-volume
quick_workflow = Workflow(
    workflow_id="quick_qual",
    name="Quick Qualification"
)

quick_workflow.add_step(WorkflowStep(
    step_id="qualify",
    agent_type="prospecting",
    prompt_template="Quick assess: {company_name} in {industry}"
))

# Deep dive for enterprise prospects
enterprise_workflow = Workflow(
    workflow_id="enterprise",
    name="Enterprise Sales Process"
)
# Add more detailed steps...
```

### Callback Integration

Integrate with your systems via callbacks:

```python
async def send_to_crm(result):
    # Send opportunity to Salesforce
    await salesforce_api.create_opportunity({
        "name": result.context['company_name'],
        "stage": "Qualification",
        "amount": extract_pricing(result.context['pricing_proposal'])
    })

task.callback = send_to_crm
```

### A/B Testing

Test different approaches:

```python
# Version A: Value-focused outreach
agent_a = SalesAgents.customer_outreach_specialist()
agent_a.system_prompt += "\nFocus heavily on ROI and cost savings."

# Version B: Feature-focused outreach
agent_b = SalesAgents.customer_outreach_specialist()
agent_b.system_prompt += "\nHighlight technical features and capabilities."

# Track performance
```

## 🐛 Troubleshooting

### Common Issues

**"ANTHROPIC_API_KEY not set"**
```bash
export ANTHROPIC_API_KEY="your-key"
```

**Selenium/WebDriver errors**
```bash
pip install --upgrade selenium webdriver-manager
```

**Rate limiting**
- Reduce `MAX_CONCURRENT_TASKS`
- Increase delays between requests
- Upgrade API plan if needed

**Portal authentication fails**
- Verify credentials are correct
- Check if portal URL changed
- Update selectors in web_automation.py
- Take screenshots to debug: `checker.take_screenshot()`

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Best Practices

### 1. Data Quality
- Verify prospect data before processing
- Clean and deduplicate inputs
- Enrich with multiple data sources

### 2. Personalization
- Use all available prospect data
- Reference specific business challenges
- Tailor by industry vertical

### 3. Follow-up
- Track outreach responses
- Schedule automated follow-ups
- Update CRM with interactions

### 4. Compliance
- Maintain consent records
- Honor opt-outs immediately
- Document data sources
- Regular privacy audits

### 5. Performance Monitoring
- Track conversion rates by stage
- Monitor agent token usage
- A/B test messaging
- Optimize based on results

## 🔐 Security Considerations

- **Credential Storage**: Use environment variables or secret managers (never hardcode)
- **Data Encryption**: Encrypt sensitive prospect data at rest
- **Access Control**: Limit portal credentials to authorized users only
- **Audit Logging**: Log all serviceability checks and outreach
- **Data Retention**: Follow company data retention policies

## 📚 File Structure

```
C:\Users\eitechs\
├── claude_agent_manager/
│   ├── agent_manager.py           # Core agent system
│   ├── sales_agents.py            # Sales-specific agents
│   ├── sales_workflow.py          # Sales workflows
│   ├── web_automation.py          # Serviceability automation
│   ├── workflow.py                # Workflow engine
│   ├── config.py                  # Configuration
│   └── requirements.txt           # Dependencies
├── run_sales_pipeline.py          # Main demo script
└── SALES_PIPELINE_README.md       # This file
```

## 🚦 Getting Started Checklist

- [ ] Set ANTHROPIC_API_KEY
- [ ] Install requirements
- [ ] Test with mock data
- [ ] Configure data sources (LinkedIn, Apollo, CRM)
- [ ] Set up portal credentials (if using real serviceability)
- [ ] Customize agent prompts for your needs
- [ ] Test batch qualification
- [ ] Run complete pipeline on test prospect
- [ ] Integrate with your CRM
- [ ] Set up monitoring and logging
- [ ] Train team on system usage

## 💡 Next Steps

1. **Start Small**: Test with 5-10 prospects
2. **Measure Results**: Track conversion rates and ROI
3. **Iterate**: Refine prompts based on performance
4. **Scale Up**: Process larger volumes as system proves effective
5. **Automate**: Build scheduled runs for continuous prospecting

## 📄 License & Support

- Framework: MIT License
- Anthropic Claude: Subject to Anthropic's Terms of Service
- Data Sources: Subject to respective platform Terms of Service

For issues or questions:
- Review this documentation
- Check example code in `run_sales_pipeline.py`
- Examine agent configurations in `sales_agents.py`

---

**Remember**: This system is a powerful tool. Use it responsibly, ethically, and in compliance with all applicable laws and regulations.
