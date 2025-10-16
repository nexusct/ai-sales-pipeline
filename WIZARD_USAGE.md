# Startup Wizard - Usage Guide

## Overview

The Sales Pipeline now includes an interactive startup wizard that collects all configuration variables when you run the application. No more manual environment variable setup!

## Features

The wizard collects:

1. **API Configuration**
   - Anthropic API key (with environment detection)
   - Validation of key format

2. **Agent Settings**
   - Max concurrent tasks (1-10+ agents running simultaneously)
   - Rate limit per minute (based on your API tier)
   - Log level (DEBUG, INFO, WARNING, ERROR)

3. **Pipeline Mode**
   - Complete Pipeline - Full workflow for 1 prospect
   - Batch Qualification - Quick assessment of multiple prospects
   - Serviceability Demo - Test serviceability checking only
   - Run All Examples - Demonstrate all capabilities

4. **Prospect Data**
   - Use built-in examples (3 pre-configured prospects)
   - Enter custom prospect data (unlimited)
   - Full prospect information collection

5. **Portal Credentials** (Optional)
   - Real portal URL, username, password
   - Mock mode if credentials not provided

## How to Use

### Quick Start

Simply run the sales pipeline script:

```bash
python run_sales_pipeline.py
```

The wizard will automatically start and guide you through the configuration.

### Wizard Flow

1. **Welcome Screen** - Overview of what the wizard will configure
2. **API Key** - Enter or confirm your Anthropic API key
3. **Agent Settings** - Configure performance parameters
4. **Mode Selection** - Choose which pipeline mode to run
5. **Prospect Data** - Use examples or enter custom prospects
6. **Portal Credentials** - Optional real portal configuration
7. **Summary & Confirmation** - Review and confirm all settings

### Navigation

- Press `Enter` to accept default values (shown in brackets)
- Type your value and press `Enter` to use custom values
- Type `y` or `n` for yes/no questions
- `Ctrl+C` to cancel the wizard at any time

### Example Interaction

```
================================================================================
  STEP 1: API CONFIGURATION
================================================================================

✓ Found existing API key in environment: sk-ant-api03-abc123...

Use this existing API key? (Y/n): y

================================================================================
  STEP 2: AGENT SETTINGS
================================================================================

Configure how the AI agents will operate:

Max Concurrent Tasks: Maximum number of agents running simultaneously
  • Higher = Faster but more API usage
  • Lower = Slower but more controlled
Max concurrent tasks [5]: 3

Rate Limit: Maximum API requests per minute
  • Tier 1: 50 requests/minute
  • Tier 2: 1000 requests/minute
  • Tier 3+: 2000+ requests/minute
Rate limit per minute [50]: 50

Log Level
  1. DEBUG
  2. INFO (default)
  3. WARNING
  4. ERROR

Enter choice number [2]: 2

================================================================================
  STEP 3: PIPELINE MODE
================================================================================

Select the mode to run:
  1. Complete Pipeline - Full workflow for 1 prospect (all stages)
  2. Batch Qualification - Quick assessment of multiple prospects
  3. Serviceability Demo - Test serviceability checking only
  4. Run All Examples - Demonstrate all capabilities

Enter choice number: 1

================================================================================
  STEP 4: PROSPECT DATA
================================================================================

Use example prospect data?
(No = Enter custom prospect data) (Y/n): y

================================================================================
  STEP 5: PORTAL CREDENTIALS (OPTIONAL)
================================================================================

For real serviceability checking, you can provide portal credentials.
Leave blank to use mock/demo mode.

Configure real portal credentials? (y/N): n

================================================================================
  CONFIGURATION SUMMARY
================================================================================

Review your configuration:

API Key: sk-ant-api03-abc123...
Max Concurrent Tasks: 3
Rate Limit: 50 requests/minute
Log Level: INFO
Mode: complete
Prospects: Using example data (3 prospects)
Portal: Mock/Demo mode

================================================================================

Proceed with this configuration? (Y/n): y
```

## Custom Prospect Entry

If you choose to enter custom prospect data, you'll be prompted for:

- Company Name
- Contact Name
- Contact Title
- Email Address
- Industry
- Company Size (e.g., "100-250 employees")
- Location (City, State)
- Full Address (for serviceability checking)
- LinkedIn URL (optional)
- Data Source (defaults to "Manual Entry")

You can add multiple prospects, and the wizard will ask if you want to add more after each entry.

## Advanced Usage

### Testing the Wizard Standalone

You can test the wizard module independently:

```bash
cd claude_agent_manager
python startup_wizard.py
```

This will run the wizard and display the collected configuration without starting the pipeline.

### Bypassing the Wizard

If you prefer the old behavior (environment variables + simple menu), you can:

1. Set all environment variables manually:
   ```bash
   export ANTHROPIC_API_KEY="your-key"
   export MAX_CONCURRENT_TASKS="5"
   export RATE_LIMIT_PER_MINUTE="50"
   export LOG_LEVEL="INFO"
   ```

2. Modify `run_sales_pipeline.py` to skip the wizard (comment out the wizard call)

## Configuration Object

The wizard returns a `WizardConfig` object with these properties:

```python
@dataclass
class WizardConfig:
    api_key: str
    max_concurrent_tasks: int
    rate_limit_per_minute: int
    mode: str  # 'complete', 'batch', 'serviceability', 'all'
    use_example_prospects: bool
    custom_prospects: List[Dict[str, str]]
    portal_credentials: Optional[Dict[str, str]]
    log_level: str
```

## Tips

1. **First Time Users**: Accept all defaults on your first run to see how the system works
2. **API Key Security**: The wizard uses `getpass` for password/API key entry (hidden input)
3. **Quick Testing**: Choose "Serviceability Demo" for fastest execution
4. **Production Use**: Configure custom prospects and real portal credentials
5. **Restart**: If you make a mistake, you can decline the final confirmation to restart

## Troubleshooting

**Wizard doesn't start**
- Check that `startup_wizard.py` is in the `claude_agent_manager` directory
- Verify Python 3.9+ is installed

**Input not accepted**
- Ensure you're pressing Enter after typing
- Check for typos in yes/no responses (y/n)

**API key validation warning**
- Anthropic keys typically start with `sk-ant-`
- If your key is different, you can continue anyway
- Verify your key at https://console.anthropic.com/

**Custom prospects not working**
- Ensure all required fields are filled
- Check email format is valid
- Verify address includes city and state

## What's Next?

After the wizard completes, the pipeline will:

1. Initialize the agent manager with your settings
2. Load the specialized sales agents
3. Execute the selected mode
4. Process prospects according to your configuration
5. Display results and statistics

Enjoy the streamlined configuration experience!
