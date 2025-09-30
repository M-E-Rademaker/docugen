"""
Configuration management.
"""

import os
from pathlib import Path
from typing import Optional
from enum import Enum
import yaml


class DetailLevel(Enum):
    """
    Documentation detail level.

    Attributes
    ----------
    MINIMAL : str
        Brief documentation with essential information only.
    CONCISE : str
        Balanced documentation with key details (default).
    VERBOSE : str
        Comprehensive documentation with examples and detailed explanations.
    """
    MINIMAL = "minimal"
    CONCISE = "concise"
    VERBOSE = "verbose"


class Config:
    """
    Application configuration.

    Manages configuration settings including API keys, file suffixes,
    and other runtime options. Can load from environment variables
    or configuration files.

    Parameters
    ----------
    api_key : str, optional
        Anthropic API key. If not provided, reads from ANTHROPIC_API_KEY
        environment variable.
    default_suffix : str, optional
        Default suffix for modified files. Defaults to '__cli_dcreate_modified'.

    Attributes
    ----------
    api_key : str or None
        The Anthropic API key for Claude API access.
    default_suffix : str
        Suffix to append to modified file names.

    Examples
    --------
    >>> config = Config()
    >>> print(config.default_suffix)
    '__cli_dcreate_modified'
    """

    def __init__(self, api_key: Optional[str] = None,
                 default_suffix: str = '__cli_dcreate_modified'):
        """
        Initialize configuration.

        Parameters
        ----------
        api_key : str, optional
            Anthropic API key. If None, reads from environment.
        default_suffix : str, optional
            Suffix for modified files.
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.default_suffix = default_suffix

    @classmethod
    def from_file(cls, config_path: Path) -> 'Config':
        """
        Load configuration from YAML file.

        Parameters
        ----------
        config_path : Path
            Path to YAML configuration file.

        Returns
        -------
        Config
            Configuration instance with loaded settings.

        Raises
        ------
        FileNotFoundError
            If config file does not exist.
        yaml.YAMLError
            If config file is not valid YAML.

        Notes
        -----
        Expected YAML structure:
            api_key: "your-api-key"
            default_suffix: "__custom_suffix"

        Examples
        --------
        >>> config = Config.from_file(Path("config.yaml"))
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

        config = cls()

        # Load API key from file if present
        if 'api_key' in data:
            config.api_key = data['api_key']

        # Load default suffix if present
        if 'default_suffix' in data:
            config.default_suffix = data['default_suffix']

        return config

    def validate(self) -> bool:
        """
        Validate configuration settings.

        Returns
        -------
        bool
            True if configuration is valid, False otherwise.

        Notes
        -----
        Currently checks if API key is present. Additional validation
        can be added as needed.

        Examples
        --------
        >>> config = Config()
        >>> if config.validate():
        ...     print("Config is valid")
        """
        return self.api_key is not None and len(self.api_key) > 0

    def get_api_key_status(self) -> str:
        """
        Get human-readable status of API key configuration.

        Returns
        -------
        str
            Status message about API key availability.

        Examples
        --------
        >>> config = Config()
        >>> print(config.get_api_key_status())
        'API key: Not configured'
        """
        if self.api_key:
            masked_key = f"{self.api_key[:8]}...{self.api_key[-4:]}"
            return f"API key: Configured ({masked_key})"
        return "API key: Not configured"