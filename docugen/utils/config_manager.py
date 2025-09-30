"""
Configuration manager for storing API keys and settings.
"""

import os
import json
from pathlib import Path
from typing import Optional


class ConfigManager:
    """Manages DocuGen configuration and API keys."""

    def __init__(self):
        """Initialize configuration manager with default paths."""
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()

    def _get_config_dir(self) -> Path:
        """Get platform-specific configuration directory."""
        if os.name == 'nt':  # Windows
            base = os.environ.get('APPDATA', os.path.expanduser('~'))
            return Path(base) / 'DocuGen'
        else:  # macOS/Linux
            return Path.home() / '.docugen'

    def _ensure_config_dir(self):
        """Create configuration directory if it doesn't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def get_api_key(self) -> Optional[str]:
        """
        Get API key from config file or environment variable.

        Returns
        -------
        Optional[str]
            API key if found, None otherwise
        """
        # First check environment variable
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if api_key:
            return api_key

        # Then check config file
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('anthropic_api_key')
            except (json.JSONDecodeError, IOError):
                return None

        return None

    def set_api_key(self, api_key: str):
        """
        Save API key to config file.

        Parameters
        ----------
        api_key : str
            Anthropic API key to save
        """
        config = {}

        # Load existing config if it exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Update API key
        config['anthropic_api_key'] = api_key

        # Save config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

        # Set restrictive permissions (owner only)
        if os.name != 'nt':  # Unix-like systems
            os.chmod(self.config_file, 0o600)

    def has_api_key(self) -> bool:
        """
        Check if API key is configured.

        Returns
        -------
        bool
            True if API key is available, False otherwise
        """
        return self.get_api_key() is not None

    def prompt_for_api_key(self) -> str:
        """
        Prompt user to enter their API key interactively.

        Returns
        -------
        str
            API key entered by user
        """
        from rich.console import Console
        from rich.prompt import Prompt

        console = Console()

        console.print("\n[bold yellow]⚠ API Key Required[/bold yellow]")
        console.print("\nDocuGen requires an Anthropic API key to generate documentation.")
        console.print("[dim]Get your API key at: https://console.anthropic.com/[/dim]\n")

        api_key = Prompt.ask("[cyan]Enter your Anthropic API key[/cyan]", password=True)

        return api_key.strip()

    def setup_interactive(self) -> bool:
        """
        Interactive setup to configure API key on first run.

        Returns
        -------
        bool
            True if setup completed successfully, False otherwise
        """
        from rich.console import Console
        from rich.prompt import Confirm

        console = Console()

        # Check if already configured
        if self.has_api_key():
            return True

        # Prompt for API key
        api_key = self.prompt_for_api_key()

        if not api_key:
            console.print("[red]No API key provided. Cannot continue.[/red]")
            return False

        # Ask if user wants to save it
        save = Confirm.ask("\n[cyan]Save API key for future use?[/cyan]", default=True)

        if save:
            try:
                self.set_api_key(api_key)
                console.print(f"[green]✓ API key saved to {self.config_file}[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠ Could not save API key: {e}[/yellow]")
                console.print("[dim]You can set the ANTHROPIC_API_KEY environment variable instead.[/dim]")
        else:
            # Set for current session only
            os.environ['ANTHROPIC_API_KEY'] = api_key
            console.print("[yellow]API key set for this session only.[/yellow]")

        return True