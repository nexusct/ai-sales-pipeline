"""
Configuration Management System
Handles configuration loading, validation, and environment setup.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ManagerConfig:
    """Configuration for the Agent Manager"""
    api_key: str
    max_concurrent_tasks: int = 5
    rate_limit_per_minute: int = 50
    default_model: str = "claude-sonnet-4-5-20250929"
    default_max_tokens: int = 4096
    default_temperature: float = 1.0
    log_level: str = "INFO"
    log_file: Optional[str] = None


class ConfigLoader:
    """Loads and manages configuration from various sources"""

    @staticmethod
    def from_env() -> ManagerConfig:
        """Load configuration from environment variables"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        return ManagerConfig(
            api_key=api_key,
            max_concurrent_tasks=int(os.getenv("MAX_CONCURRENT_TASKS", "5")),
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "50")),
            default_model=os.getenv("DEFAULT_MODEL", "claude-sonnet-4-5-20250929"),
            default_max_tokens=int(os.getenv("DEFAULT_MAX_TOKENS", "4096")),
            default_temperature=float(os.getenv("DEFAULT_TEMPERATURE", "1.0")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE")
        )

    @staticmethod
    def from_json(file_path: str) -> ManagerConfig:
        """Load configuration from JSON file"""
        with open(file_path, 'r') as f:
            config_dict = json.load(f)
        return ManagerConfig(**config_dict)

    @staticmethod
    def from_yaml(file_path: str) -> ManagerConfig:
        """Load configuration from YAML file"""
        with open(file_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return ManagerConfig(**config_dict)

    @staticmethod
    def from_dict(config_dict: Dict[str, Any]) -> ManagerConfig:
        """Load configuration from dictionary"""
        return ManagerConfig(**config_dict)

    @staticmethod
    def save_to_json(config: ManagerConfig, file_path: str):
        """Save configuration to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(asdict(config), f, indent=2)

    @staticmethod
    def save_to_yaml(config: ManagerConfig, file_path: str):
        """Save configuration to YAML file"""
        with open(file_path, 'w') as f:
            yaml.dump(asdict(config), f, default_flow_style=False)


class ConfigManager:
    """Manages configuration with validation and updates"""

    def __init__(self, config: ManagerConfig):
        self.config = config
        self._validate_config()

    def _validate_config(self):
        """Validate configuration values"""
        if not self.config.api_key:
            raise ValueError("API key is required")

        if self.config.max_concurrent_tasks < 1:
            raise ValueError("max_concurrent_tasks must be at least 1")

        if self.config.rate_limit_per_minute < 1:
            raise ValueError("rate_limit_per_minute must be at least 1")

        if self.config.default_max_tokens < 1:
            raise ValueError("default_max_tokens must be at least 1")

        if not 0 <= self.config.default_temperature <= 2:
            raise ValueError("default_temperature must be between 0 and 2")

        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.config.log_level.upper() not in valid_log_levels:
            raise ValueError(f"log_level must be one of {valid_log_levels}")

    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with validation"""
        for key, value in updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                raise ValueError(f"Invalid configuration key: {key}")

        self._validate_config()

    def get_config(self) -> ManagerConfig:
        """Get current configuration"""
        return self.config

    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return asdict(self.config)


def create_example_config(output_path: str = "agent_config.yaml"):
    """Create an example configuration file"""
    example_config = ManagerConfig(
        api_key="your-api-key-here",
        max_concurrent_tasks=5,
        rate_limit_per_minute=50,
        default_model="claude-sonnet-4-5-20250929",
        default_max_tokens=4096,
        default_temperature=1.0,
        log_level="INFO",
        log_file="agent_manager.log"
    )

    ConfigLoader.save_to_yaml(example_config, output_path)
    print(f"Example configuration saved to {output_path}")


def setup_logging(config: ManagerConfig):
    """Setup logging based on configuration"""
    import logging

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.log_level.upper()))
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if config.log_file:
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setLevel(getattr(logging, config.log_level.upper()))
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger
