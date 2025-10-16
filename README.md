# AI Sales Pipeline with Interactive Startup Wizard

A comprehensive AI-powered sales automation system that coordinates multiple specialized agents to manage the entire sales pipeline from prospect identification through customer outreach.

## Features

- **Interactive Startup Wizard** - User-friendly configuration collection on startup
- **API Key Validation** - Real-time validation of Anthropic API keys
- **Multi-Agent System** - 7 specialized AI agents working in coordination
- **Complete Sales Workflow** - From prospect qualification to personalized outreach
- **Flexible Modes** - Complete pipeline, batch qualification, serviceability demo, or all
- **Custom Prospect Entry** - Use examples or enter unlimited custom prospects
- **Portal Integration** - Optional real portal credentials for serviceability checking

## Quick Start

### Prerequisites

```bash
# Python 3.9 or higher
python --version

# Install dependencies
pip install anthropic
pip install -r claude_agent_manager/requirements.txt
```

### Running the Pipeline

```bash
# Run the interactive wizard
python run_sales_pipeline.py
```

The wizard will guide you through:
1. API key configuration and validation
2. Agent performance settings
3. Pipeline mode selection
4. Prospect data configuration
5. Optional portal credentials

## Project Structure

```
.
├── claude_agent_manager/
│   ├── agent_manager.py        # Core agent coordination system
│   ├── startup_wizard.py       # Interactive configuration wizard
│   ├── sales_agents.py         # Specialized sales agent definitions
│   ├── sales_workflow.py       # Sales pipeline workflows
│   ├── web_automation.py       # Serviceability checking automation
│   ├── workflow.py             # Workflow engine
│   └── config.py               # Configuration management
├── run_sales_pipeline.py       # Main entry point with wizard
├── SALES_PIPELINE_README.md    # Detailed pipeline documentation
├── WIZARD_USAGE.md             # Wizard usage guide
└── README.md                   # This file
```

## Agent Cluster

The system uses 7 specialized AI agents:

| Agent | Role |
|-------|------|
| **Prospect Finder** | Identifies and qualifies leads |
| **Business Researcher** | Analyzes business requirements |
| **Use Case Builder** | Creates EDI solutions |
| **Serviceability Analyst** | Interprets serviceability results |
| **Pricing Analyst** | Develops proposals |
| **Outreach Specialist** | Crafts communications |
| **Sales Coordinator** | Orchestrates pipeline |

## Pipeline Modes

1. **Complete Pipeline** - Full workflow for 1 prospect (all stages)
2. **Batch Qualification** - Quick assessment of multiple prospects
3. **Serviceability Demo** - Test serviceability checking only
4. **Run All Examples** - Demonstrate all capabilities

## Startup Wizard Features

### API Configuration
- Automatic detection of existing API keys
- Format validation (sk-ant-* prefix)
- Real-time API validation with error handling
- Secure input using `getpass`

### Agent Settings
- Max concurrent tasks (1-10+ agents)
- Rate limit configuration (50-2000+ req/min)
- Log level selection (DEBUG, INFO, WARNING, ERROR)

### Prospect Management
- Use built-in example prospects (3 pre-configured)
- Enter unlimited custom prospects
- Full data collection per prospect

### Portal Integration
- Optional real portal credentials
- Mock mode for testing
- Secure password handling

## Configuration

The wizard collects all configuration automatically. For advanced users, you can also set environment variables:

```bash
export ANTHROPIC_API_KEY="your-api-key"
export MAX_CONCURRENT_TASKS="5"
export RATE_LIMIT_PER_MINUTE="50"
export LOG_LEVEL="INFO"
```

## Documentation

- [SALES_PIPELINE_README.md](SALES_PIPELINE_README.md) - Complete pipeline documentation
- [WIZARD_USAGE.md](WIZARD_USAGE.md) - Detailed wizard usage guide

## Example Usage

### With Wizard (Recommended)

```bash
python run_sales_pipeline.py
```

Follow the interactive prompts to configure and run.

### Programmatic Usage

```python
from sales_agents import ProspectData
from sales_workflow import SalesPipelineManager
from agent_manager import AgentManager
from config import ConfigLoader

# Create prospect
prospect = ProspectData(
    company_name="Healthcare Corp",
    contact_name="John Smith",
    contact_title="VP of IT",
    email="jsmith@example.com",
    company_size="500+ employees",
    industry="Healthcare",
    location="Philadelphia, PA",
    address="123 Main St, Philadelphia, PA 19103",
    source="LinkedIn API"
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

## Security & Compliance

**Important Legal & Ethical Requirements:**

- ✅ **ALLOWED**: Official APIs (LinkedIn Sales Navigator API, Apollo.io API, CRM)
- ✅ **ALLOWED**: Data you own or have legitimate access to
- ✅ **ALLOWED**: Publicly available business information
- ❌ **NOT ALLOWED**: Web scraping without permission
- ❌ **NOT ALLOWED**: Violating platform Terms of Service
- ❌ **NOT ALLOWED**: Bulk harvesting without authorization

### Portal Access
- Use only authorized credentials
- Automate with proper business authorization
- No unauthorized access or credential sharing

### Outreach Compliance
- Comply with CAN-SPAM Act
- Respect GDPR, CCPA privacy regulations
- Honor opt-outs and unsubscribe requests
- Use legitimate business contact information

## API Validation

The wizard includes real-time API validation:

```
[INFO] Testing API key...
[OK] API key validated successfully!
```

Handles:
- Authentication errors
- Permission issues
- Rate limiting
- API errors
- Network issues

## Troubleshooting

**"ANTHROPIC_API_KEY not set"**
```bash
export ANTHROPIC_API_KEY="your-key"
```

**API validation fails**
- Verify key at https://console.anthropic.com/
- Check internet connection
- Verify API tier and rate limits

**Module import errors**
```bash
pip install -r claude_agent_manager/requirements.txt
```

## Contributing

This is a specialized sales pipeline system. Contributions should focus on:
- Agent prompt improvements
- New workflow patterns
- Enhanced validation
- Better error handling
- Documentation improvements

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Review documentation in SALES_PIPELINE_README.md
- Check wizard guide in WIZARD_USAGE.md
- Examine example code in run_sales_pipeline.py

---

**Remember**: This system is a powerful tool. Use it responsibly, ethically, and in compliance with all applicable laws and regulations.
