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

console = Console()

# Global instances (initialized in main)
parser = None
validator = None
generator = None
writer = None


@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--suffix', default='__cli_dcreate_modified',
              help='Suffix for modified files')
@click.option('--dry-run', is_flag=True,
              help='Show what would be done without making changes')
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output')
@click.option('--api-key', envvar='ANTHROPIC_API_KEY',
              help='Anthropic API key (or set ANTHROPIC_API_KEY env var)')
def main(path: str, suffix: str, dry_run: bool, verbose: bool, api_key: str):
    """
    Document SQL, Python, and R code files using AI.

    PATH: File or directory to document

    \b
    Examples:
      docugen script.py
      docugen src/ --verbose
      docugen query.sql --dry-run
      docugen code.r --suffix "_documented"

    \b
    Requirements:
      Set ANTHROPIC_API_KEY environment variable:
        export ANTHROPIC_API_KEY='your-api-key-here'
    """
    global parser, validator, generator, writer

    # Header
    console.print(Panel.fit(
        "[bold blue]DocuGen CLI v0.1.0[/bold blue]\n"
        "AI-Powered Code Documentation",
        border_style="blue"
    ))
    console.print()

    try:
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
            console.print(f"\n[bold red]API Key Required[/bold red]")
            console.print(f"\n{str(e)}")
            console.print("\n[yellow]Set your API key:[/yellow]")
            console.print("  export ANTHROPIC_API_KEY='your-api-key-here'")
            console.print("\n[dim]Get your API key at: https://console.anthropic.com/[/dim]")
            sys.exit(1)

        # Phase 1: Discover files
        discovery = FileDiscovery()
        files = discovery.discover(Path(path))

        if len(files) == 0:
            console.print("[yellow]No supported files found (.sql, .py, .r)[/yellow]")
            sys.exit(0)

        console.print(f"[bold]Found {len(files)} file(s) to process[/bold]\n")

        # Phase 2: Process each file
        success_count = 0
        error_count = 0

        for file_path in files:
            try:
                process_file(file_path, suffix, dry_run, verbose)
                success_count += 1
            except Exception as e:
                error_count += 1
                console.print(f"  [red]✗ Error: {e}[/red]")
                if verbose:
                    import traceback
                    console.print(f"[dim]{traceback.format_exc()}[/dim]")

        # Summary
        console.print()
        console.print("[bold]Summary:[/bold]")
        console.print(f"  ✓ Success: {success_count}")
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


def process_file(file_path: Path, suffix: str, dry_run: bool, verbose: bool):
    """
    Process a single file through the documentation pipeline.

    Parameters
    ----------
    file_path : Path
        Path to the file to process
    suffix : str
        Suffix to add to output filename
    dry_run : bool
        If True, show what would be done without making changes
    verbose : bool
        If True, show detailed progress information
    """
    console.print(f"[cyan]→ {file_path.name}[/cyan]")

    # Read file content
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        raise Exception(f"Failed to read file: {e}")

    # Step 1: Parse existing documentation
    if verbose:
        console.print("  [dim]Parsing existing documentation...[/dim]")

    existing_doc = parser.parse(file_path)

    if existing_doc and verbose:
        console.print(f"  [dim]Found existing documentation for: {existing_doc.get('name', 'unknown')}[/dim]")

    # Step 2: Validate documentation
    if verbose:
        console.print("  [dim]Validating against standards...[/dim]")

    needs_generation = True
    if existing_doc:
        validation_result = validator.validate(file_path, existing_doc)
        if validation_result.is_valid:
            console.print("  [green]✓ Documentation is compliant[/green]")
            if verbose:
                console.print("  [dim]No changes needed[/dim]")
            needs_generation = False
        else:
            console.print(f"  [yellow]⚠ Documentation needs improvement ({len(validation_result.issues)} issues)[/yellow]")
            if verbose:
                for issue in validation_result.issues[:3]:  # Show first 3 issues
                    console.print(f"    [dim]- {issue}[/dim]")
                if len(validation_result.issues) > 3:
                    console.print(f"    [dim]... and {len(validation_result.issues) - 3} more[/dim]")
    else:
        console.print("  [yellow]⚠ No documentation found[/yellow]")

    if not needs_generation:
        return

    # Step 3: Generate/update documentation
    if dry_run:
        console.print("  [yellow]○ Dry run - would generate documentation[/yellow]")
        return

    if verbose:
        console.print("  [dim]Generating documentation with Claude...[/dim]")

    try:
        if existing_doc and not validator.validate(file_path, existing_doc).is_valid:
            # Update existing documentation
            new_doc = generator.update(file_path, existing_doc, content)
        else:
            # Generate new documentation
            new_doc = generator.generate(file_path, content)

        # Step 4: Write modified file
        if verbose:
            console.print("  [dim]Writing documented file...[/dim]")

        output_path = writer.write(file_path, new_doc, suffix)
        console.print(f"  [green]✓ Documentation generated → {output_path.name}[/green]")

    except DocGeneratorError as e:
        raise Exception(f"Generation failed: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")


if __name__ == '__main__':
    main()