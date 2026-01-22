"""Configuration management for EC2 TUI."""

import sys
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from pydantic import BaseModel, Field
from platformdirs import user_config_dir

from .defaults import DEFAULT_CONFIG
from ..utils.exceptions import ConfigurationError


class UIConfig(BaseModel):
    """UI configuration."""

    default_region: str = Field(default="eu-west-1")
    refresh_interval_seconds: int = Field(default=30, ge=0)
    theme: str = Field(default="omarchy")


class RetryConfig(BaseModel):
    """Retry mechanism configuration."""

    enabled: bool = Field(default=True)
    interval_seconds: int = Field(default=60, ge=1)
    max_attempts: int = Field(default=60, ge=1)


class NotificationConfig(BaseModel):
    """Notification configuration."""

    enabled: bool = Field(default=True)
    urgency: str = Field(default="normal")


class SavedInstanceTypesConfig(BaseModel):
    """Saved instance types configuration."""

    types: list[str] = Field(default_factory=list)


class AWSConfig(BaseModel):
    """AWS configuration."""

    use_cli_credentials: bool = Field(default=True)
    profile: Optional[str] = Field(default=None)


class Config(BaseModel):
    """Main configuration model."""

    ui: UIConfig = Field(default_factory=UIConfig)
    retry: RetryConfig = Field(default_factory=RetryConfig)
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)
    saved_instance_types: SavedInstanceTypesConfig = Field(
        default_factory=SavedInstanceTypesConfig
    )
    aws: AWSConfig = Field(default_factory=AWSConfig)

    def save_instance_type(self, instance_type: str) -> None:
        """Add an instance type to saved types if not already present."""
        if instance_type not in self.saved_instance_types.types:
            self.saved_instance_types.types.append(instance_type)

    def to_dict(self) -> dict:
        """Convert config to dictionary for saving."""
        return self.model_dump(exclude_none=True)


def get_config_path() -> Path:
    """Get the configuration file path."""
    config_dir = Path(user_config_dir("ec2-tui"))
    config_file = config_dir / "config.toml"

    # Also check for config.toml in current directory
    local_config = Path("config.toml")
    if local_config.exists():
        return local_config

    return config_file


def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load configuration from TOML file.

    Args:
        config_path: Optional path to config file. If None, uses default locations.

    Returns:
        Config object with merged configuration.

    Raises:
        ConfigurationError: If config file is invalid.
    """
    # Start with default config
    config_data = DEFAULT_CONFIG.copy()

    # Determine config file path
    if config_path is None:
        config_path = get_config_path()

    # Load user config if it exists
    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                user_config = tomllib.load(f)
                # Deep merge user config with defaults
                _deep_merge(config_data, user_config)
        except Exception as e:
            raise ConfigurationError(f"Failed to load config from {config_path}: {e}")

    # Validate and create Config object
    try:
        return Config(**config_data)
    except Exception as e:
        raise ConfigurationError(f"Invalid configuration: {e}")


def save_config(config: Config, config_path: Optional[Path] = None) -> None:
    """
    Save configuration to TOML file.

    Args:
        config: Config object to save.
        config_path: Optional path to save to. If None, uses default location.
    """
    if config_path is None:
        config_path = get_config_path()

    # Ensure config directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert config to TOML
    import tomli_w

    with open(config_path, "wb") as f:
        tomli_w.dump(config.to_dict(), f)


def _deep_merge(base: dict, update: dict) -> None:
    """
    Deep merge update dict into base dict.

    Args:
        base: Base dictionary to merge into (modified in place).
        update: Dictionary with updates.
    """
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
