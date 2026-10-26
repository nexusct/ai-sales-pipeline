"""
Interactive Startup Wizard for Sales Pipeline Configuration

This wizard collects all necessary configuration variables on startup,
providing a user-friendly interface for setting up the sales pipeline.
"""

import os
import sys
import subprocess
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from getpass import getpass
import anthropic


@dataclass
class WizardConfig:
    """Configuration collected from the wizard"""
    api_key: str
    max_concurrent_tasks: int
    rate_limit_per_minute: int
    mode: str
    use_example_prospects: bool
    custom_prospects: List[Dict[str, str]]
    portal_credentials: Optional[Dict[str, str]]
    log_level: str


class StartupWizard:
    """Interactive wizard for collecting startup configuration"""

    def __init__(self):
        self.config = None

    def clear_screen(self):
        """Clear the console screen safely"""
        # Use platform-specific clear command safely without shell injection risk
        if os.name == 'nt':
            # Windows
            subprocess.run(['cls'], shell=True, check=False)
        else:
            # Unix-like systems
            subprocess.run(['clear'], check=False)

    def print_header(self, title: str):
        """Print a formatted header"""
        print("\n" + "="*80)
        print(f"  {title}")
        print("="*80 + "\n")

    def print_section(self, title: str):
        """Print a section divider"""
        print("\n" + "-"*80)
        print(f"  {title}")
        print("-"*80 + "\n")

    def get_input(self, prompt: str, default: Optional[str] = None,
                  required: bool = True, secret: bool = False) -> str:
        """Get user input with optional default value"""
        if default:
            prompt_text = f"{prompt} [{default}]: "
        else:
            prompt_text = f"{prompt}: "

        while True:
            try:
                if secret:
                    value = getpass(prompt_text)
                else:
                    value = input(prompt_text).strip()

                if not value and default:
                    return default

                if not value and required:
                    print("  [WARN] This field is required. Please enter a value.")
                    continue

                return value
            except (KeyboardInterrupt, EOFError):
                print("\n\nWizard cancelled by user.")
                sys.exit(0)

    def get_choice(self, prompt: str, choices: List[str], default: Optional[str] = None) -> str:
        """Get user choice from a list of options"""
        print(f"\n{prompt}")
        for i, choice in enumerate(choices, 1):
            default_marker = " (default)" if default and choice == default else ""
            print(f"  {i}. {choice}{default_marker}")

        while True:
            choice_input = self.get_input("\nEnter choice number",
                                         default=str(choices.index(default) + 1) if default else None,
                                         required=True)
            try:
                choice_num = int(choice_input)
                if 1 <= choice_num <= len(choices):
                    return choices[choice_num - 1]
                else:
                    print(f"  [WARN] Please enter a number between 1 and {len(choices)}")
            except ValueError:
                print(f"  [WARN] Please enter a valid number")

    def get_yes_no(self, prompt: str, default: bool = True) -> bool:
        """Get yes/no input from user"""
        default_text = "Y/n" if default else "y/N"
        while True:
            response = self.get_input(f"{prompt} ({default_text})",
                                     default="y" if default else "n",
                                     required=False).lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            elif not response:
                return default
            else:
                print("  [WARN] Please enter 'y' for yes or 'n' for no")

    def welcome_screen(self):
        """Display welcome screen"""
        self.clear_screen()
        self.print_header("COMCAST FIBER EDI SALES PIPELINE - SETUP WIZARD")

        print("Welcome! This wizard will help you configure the AI-powered sales pipeline.")
        print("\nThe system will guide you through:")
        print("  [OK] API Configuration")
        print("  [OK] Agent Settings")
        print("  [OK] Pipeline Mode Selection")
        print("  [OK] Prospect Data Configuration")
        print("  [OK] Optional Portal Credentials")
        print("\nPress Enter to continue...")
        input()

    def validate_api_key(self, api_key: str) -> bool:
        """
        Test the API key by making a simple API call.
        Returns True if valid, False otherwise.
        """
        print("\n[INFO] Testing API key...")
        try:
            client = anthropic.Anthropic(api_key=api_key)

            # Make a minimal request to test the key
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )

            print("[OK] API key validated successfully!")
            return True

        except anthropic.AuthenticationError:
            print("[ERROR] Authentication failed - Invalid API key")
            return False
        except anthropic.PermissionDeniedError:
            print("[ERROR] Permission denied - Check your API key permissions")
            return False
        except anthropic.RateLimitError:
            print("[WARN] Rate limit reached, but API key appears valid")
            return True  # Key is valid, just rate limited
        except anthropic.APIError as e:
            print(f"[ERROR] API error: {str(e)}")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error during validation: {str(e)}")
            return False

    def configure_api_key(self) -> str:
        """Configure Anthropic API key"""
        self.clear_screen()
        self.print_header("STEP 1: API CONFIGURATION")

        # Check if API key exists in environment
        existing_key = os.getenv('ANTHROPIC_API_KEY')

        if existing_key:
            print(f"[OK] Found existing API key in environment: {existing_key[:20]}...")

            validate_existing = self.get_yes_no(
                "\nValidate this API key before using?",
                default=True
            )

            if validate_existing:
                if self.validate_api_key(existing_key):
                    use_existing = self.get_yes_no("\nUse this existing API key?", default=True)
                    if use_existing:
                        return existing_key
                else:
                    print("\n[WARN] Existing API key validation failed.")
                    use_anyway = self.get_yes_no("Use it anyway?", default=False)
                    if use_anyway:
                        return existing_key
            else:
                use_existing = self.get_yes_no("\nUse this existing API key?", default=True)
                if use_existing:
                    return existing_key

        print("\nEnter your Anthropic API key:")
        print("(You can find this at https://console.anthropic.com/)")

        while True:
            api_key = self.get_input("API Key", secret=True, required=True)

            # Validate key format (basic check)
            if not api_key.startswith('sk-ant-'):
                print("\n[WARN] Warning: API key doesn't match expected format (should start with 'sk-ant-')")
                if not self.get_yes_no("Continue anyway?", default=False):
                    continue

            # Validate key with API
            validate = self.get_yes_no("\nValidate API key now?", default=True)

            if validate:
                if self.validate_api_key(api_key):
                    return api_key
                else:
                    print("\n[ERROR] API key validation failed.")
                    retry = self.get_yes_no("Enter a different key?", default=True)
                    if retry:
                        continue
                    else:
                        use_anyway = self.get_yes_no("Use this key anyway?", default=False)
                        if use_anyway:
                            return api_key
                        else:
                            sys.exit(1)
            else:
                return api_key

    def configure_agent_settings(self) -> Dict[str, Any]:
        """Configure agent performance settings"""
        self.clear_screen()
        self.print_header("STEP 2: AGENT SETTINGS")

        print("Configure how the AI agents will operate:\n")

        # Max concurrent tasks
        print("Max Concurrent Tasks: Maximum number of agents running simultaneously")
        print("  • Higher = Faster but more API usage")
        print("  • Lower = Slower but more controlled")
        max_tasks = self.get_input("Max concurrent tasks", default="5")

        # Rate limit
        print("\nRate Limit: Maximum API requests per minute")
        print("  • Tier 1: 50 requests/minute")
        print("  • Tier 2: 1000 requests/minute")
        print("  • Tier 3+: 2000+ requests/minute")
        rate_limit = self.get_input("Rate limit per minute", default="50")

        # Log level
        log_level = self.get_choice("Log Level",
                                    ["DEBUG", "INFO", "WARNING", "ERROR"],
                                    default="INFO")

        try:
            return {
                'max_concurrent_tasks': int(max_tasks),
                'rate_limit_per_minute': int(rate_limit),
                'log_level': log_level
            }
        except ValueError:
            print("\n[WARN] Invalid number entered. Using defaults.")
            return {
                'max_concurrent_tasks': 5,
                'rate_limit_per_minute': 50,
                'log_level': 'INFO'
            }

    def select_mode(self) -> str:
        """Select pipeline execution mode"""
        self.clear_screen()
        self.print_header("STEP 3: PIPELINE MODE")

        modes = [
            "Complete Pipeline - Full workflow for 1 prospect (all stages)",
            "Batch Qualification - Quick assessment of multiple prospects",
            "Serviceability Demo - Test serviceability checking only",
            "Run All Examples - Demonstrate all capabilities"
        ]

        mode_choice = self.get_choice("Select the mode to run:", modes)

        # Map choice to mode code
        mode_map = {
            modes[0]: "complete",
            modes[1]: "batch",
            modes[2]: "serviceability",
            modes[3]: "all"
        }

        return mode_map[mode_choice]

    def configure_prospects(self) -> Dict[str, Any]:
        """Configure prospect data source"""
        self.clear_screen()
        self.print_header("STEP 4: PROSPECT DATA")

        use_examples = self.get_yes_no(
            "Use example prospect data?\n(No = Enter custom prospect data)",
            default=True
        )

        custom_prospects = []

        if not use_examples:
            print("\n" + "-"*80)
            print("Enter custom prospect information")
            print("-"*80)

            add_more = True
            prospect_num = 1

            while add_more:
                print(f"\n--- Prospect #{prospect_num} ---")

                prospect = {
                    'company_name': self.get_input("Company Name", required=True),
                    'contact_name': self.get_input("Contact Name", required=True),
                    'contact_title': self.get_input("Contact Title", required=True),
                    'email': self.get_input("Email Address", required=True),
                    'industry': self.get_input("Industry", required=True),
                    'company_size': self.get_input("Company Size (e.g., 100-250 employees)", required=True),
                    'location': self.get_input("Location (City, State)", required=True),
                    'address': self.get_input("Full Address (for serviceability)", required=True),
                    'linkedin_url': self.get_input("LinkedIn URL", required=False),
                    'source': self.get_input("Data Source", default="Manual Entry")
                }

                custom_prospects.append(prospect)
                prospect_num += 1

                add_more = self.get_yes_no("\nAdd another prospect?", default=False)

        return {
            'use_examples': use_examples,
            'custom_prospects': custom_prospects
        }

    def configure_portal_credentials(self) -> Optional[Dict[str, str]]:
        """Configure optional portal credentials for serviceability checking"""
        self.clear_screen()
        self.print_header("STEP 5: PORTAL CREDENTIALS (OPTIONAL)")

        print("For real serviceability checking, you can provide portal credentials.")
        print("Leave blank to use mock/demo mode.\n")

        use_portal = self.get_yes_no(
            "Configure real portal credentials?",
            default=False
        )

        if not use_portal:
            return None

        print("\nEnter portal credentials:")
        print("[WARN] Ensure you have authorization to use these credentials\n")

        credentials = {
            'portal_url': self.get_input("Portal URL", required=True),
            'username': self.get_input("Username", required=True),
            'password': self.get_input("Password", secret=True, required=True)
        }

        return credentials

    def show_summary(self, config: WizardConfig):
        """Display configuration summary"""
        self.clear_screen()
        self.print_header("CONFIGURATION SUMMARY")

        print("Review your configuration:\n")

        print(f"API Key: {config.api_key[:20]}..." if config.api_key else "API Key: Not set")
        print(f"Max Concurrent Tasks: {config.max_concurrent_tasks}")
        print(f"Rate Limit: {config.rate_limit_per_minute} requests/minute")
        print(f"Log Level: {config.log_level}")
        print(f"Mode: {config.mode}")

        if config.use_example_prospects:
            print("Prospects: Using example data (3 prospects)")
        else:
            print(f"Prospects: Custom data ({len(config.custom_prospects)} prospects)")

        if config.portal_credentials:
            print(f"Portal: Real portal ({config.portal_credentials['portal_url']})")
        else:
            print("Portal: Mock/Demo mode")

        print("\n" + "="*80)

        confirmed = self.get_yes_no("\nProceed with this configuration?", default=True)

        if not confirmed:
            restart = self.get_yes_no("Restart wizard?", default=True)
            if restart:
                return self.run()
            else:
                print("\nConfiguration cancelled.")
                sys.exit(0)

        return config

    def run(self) -> WizardConfig:
        """Run the complete wizard workflow"""

        # Welcome
        self.welcome_screen()

        # Step 1: API Key
        api_key = self.configure_api_key()

        # Step 2: Agent Settings
        agent_settings = self.configure_agent_settings()

        # Step 3: Mode Selection
        mode = self.select_mode()

        # Step 4: Prospect Data
        prospect_config = self.configure_prospects()

        # Step 5: Portal Credentials
        portal_creds = self.configure_portal_credentials()

        # Create configuration object
        config = WizardConfig(
            api_key=api_key,
            max_concurrent_tasks=agent_settings['max_concurrent_tasks'],
            rate_limit_per_minute=agent_settings['rate_limit_per_minute'],
            log_level=agent_settings['log_level'],
            mode=mode,
            use_example_prospects=prospect_config['use_examples'],
            custom_prospects=prospect_config['custom_prospects'],
            portal_credentials=portal_creds
        )

        # Show summary and confirm
        config = self.show_summary(config)

        return config


def run_wizard() -> WizardConfig:
    """
    Main entry point for the wizard.
    Returns a WizardConfig object with all collected settings.
    """
    wizard = StartupWizard()
    return wizard.run()


if __name__ == "__main__":
    # Test the wizard standalone
    config = run_wizard()
    print("\n[OK] Wizard completed successfully!")
    print(f"Configuration: {config}")
