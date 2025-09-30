"""
Command-line interface for DocuGen.
"""

import os
import sys
import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from docugen.core.file_discovery import FileDiscovery
from docugen.core.doc_parser import DocParser
from docugen.core.doc_validator import DocValidator
from docugen.core.doc_generator import DocGenerator, APIKeyMissingError, DocGeneratorError
from docugen.core.file_writer import FileWriter
from docugen.core.doc_orchestrator import DocOrchestrator
from docugen.utils.config import DetailLevel
from docugen.utils.config_manager import ConfigManager

console = Console()

# Global instances (initialized in main)
parser = None
validator = None
generator = None
writer = None
orchestrator = None


@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--detail-level', '-d',
              type=click.Choice(['minimal', 'concise', 'verbose'], case_sensitive=False),
              default='concise',
              help='Documentation detail level (minimal/concise/verbose)')
@click.option('--dry-run', is_flag=True,
              help='Show what would be done without making changes')
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output')
@click.option('--api-key',
              help='Anthropic API key (overrides config and environment)')
def main(path: str, detail_level: str, dry_run: bool, verbose: bool, api_key: str):
    """
    Document SQL, Python, and R code files using AI.

    Documentation is injected directly into the source files.

    PATH: File or directory to document

    \b
    Examples:
      docugen script.py
      docugen src/ --verbose
      docugen query.sql --dry-run
      docugen code.py --detail-level verbose
      docugen analysis.r -d minimal

    \b
    Requirements:
      Set ANTHROPIC_API_KEY environment variable:
        export ANTHROPIC_API_KEY='your-api-key-here'
    """
    global parser, validator, generator, writer, orchestrator

    # Convert detail_level string to enum
    detail_level_enum = DetailLevel(detail_level.lower())

    # Header
    console.print(Panel.fit(
        "[bold blue]DocuGen CLI v0.1.0[/bold blue]\n"
        "AI-Powered Code Documentation",
        border_style="blue"
    ))
    console.print(f"[dim]Detail Level: {detail_level.capitalize()}[/dim]")
    console.print()

    try:
        # Initialize config manager
        config_mgr = ConfigManager()

        # Get API key from: CLI arg > config file > environment > interactive prompt
        if not api_key:
            api_key = config_mgr.get_api_key()

        if not api_key:
            # First-run interactive setup
            if not config_mgr.setup_interactive():
                sys.exit(1)
            api_key = config_mgr.get_api_key()

        # Initialize components
        if verbose:
            console.print("[dim]Initializing components...[/dim]")

        parser = DocParser()
        validator = DocValidator()
        writer = FileWriter()

        # Initialize generator with API key check
        try:
            generator = DocGenerator(api_key=api_key)
            if verbose:
                console.print("[dim]✓ Claude API connected[/dim]")
        except APIKeyMissingError as e:
            console.print(f"\n[bold red]API Key Error[/bold red]")
            console.print(f"\n{str(e)}")
            sys.exit(1)

        # Initialize orchestrator
        orchestrator = DocOrchestrator(generator, validator)

        # Phase 1: Discover files
        discovery = FileDiscovery()
        files = discovery.discover(Path(path))

        if len(files) == 0:
            console.print("[yellow]No supported files found (.sql, .py, .r)[/yellow]")
            sys.exit(0)

        console.print(f"[bold]Found {len(files)} file(s) to process[/bold]\n")

        # Phase 2: Process each file using orchestrator
        success_count = 0
        error_count = 0
        total_documented = 0

        for file_path in files:
            console.print(f"[cyan]→ {file_path.name}[/cyan]")
            try:
                result = orchestrator.process_file(file_path, detail_level_enum, dry_run, verbose)

                if result['success']:
                    success_count += 1
                    total_documented += result['items_documented']
                else:
                    error_count += 1
                    console.print(f"  [red]✗ Error: {result.get('error', 'Unknown error')}[/red]")

            except Exception as e:
                error_count += 1
                console.print(f"  [red]✗ Error: {e}[/red]")
                if verbose:
                    import traceback
                    console.print(f"[dim]{traceback.format_exc()}[/dim]")

        # Summary
        console.print()
        console.print("[bold]Summary:[/bold]")
        console.print(f"  Files processed: {success_count}")
        console.print(f"  Items documented: {total_documented}")
        if error_count > 0:
            console.print(f"  ✗ Errors: {error_count}")

        if success_count > 0:
            console.print(f"\n[bold green]✓ Processing complete![/bold green]")
        elif error_count > 0:
            console.print(f"\n[bold red]✗ Processing completed with errors[/bold red]")
            sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]Fatal Error: {e}[/bold red]")
        if verbose:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == '__main__':
    main()