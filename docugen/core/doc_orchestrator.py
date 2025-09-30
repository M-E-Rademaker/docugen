"""
Documentation orchestrator - coordinates extraction, generation, and injection.
"""

from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from docugen.core.code_extractor import CodeExtractor, CodeItem
from docugen.core.doc_generator import DocGenerator
from docugen.core.doc_validator import DocValidator
from docugen.utils.config import DetailLevel


class DocOrchestrator:
    """
    Orchestrates the complete documentation workflow.

    This class coordinates:
    1. Extraction of documentable items from files
    2. Generation of documentation for each item
    3. Injection of documentation back into the file
    """

    def __init__(self, generator: DocGenerator, validator: DocValidator):
        """
        Initialize the orchestrator.

        Parameters
        ----------
        generator : DocGenerator
            Documentation generator instance
        validator : DocValidator
            Documentation validator instance
        """
        self.extractor = CodeExtractor()
        self.generator = generator
        self.validator = validator
        self.console = Console()

    def process_file(self, file_path: Path, detail_level: DetailLevel,
                    dry_run: bool = False, verbose: bool = False) -> Dict[str, Any]:
        """
        Process a file and document all eligible items.

        Parameters
        ----------
        file_path : Path
            Path to the file to process
        detail_level : DetailLevel
            Level of documentation detail
        dry_run : bool
            If True, don't actually modify the file
        verbose : bool
            If True, show detailed progress

        Returns
        -------
        Dict[str, Any]
            Processing results with keys:
            - success: bool
            - items_processed: int
            - items_documented: int
            - items_skipped: int
            - error: str (if success=False)
        """
        try:
            # Step 1: Extract documentable items
            if verbose:
                self.console.print("  [dim]Extracting code items...[/dim]")

            items = self.extractor.extract(file_path)

            if not items:
                return {
                    'success': True,
                    'items_processed': 0,
                    'items_documented': 0,
                    'items_skipped': 0
                }

            if verbose:
                self.console.print(f"  [dim]Found {len(items)} documentable items[/dim]")

            # Step 2: Determine which items need documentation
            items_to_document = []
            items_skipped = 0

            for item in items:
                if not item.has_documentation:
                    items_to_document.append(item)
                    if verbose:
                        self.console.print(f"  [dim]→ {item.type} '{item.name}': needs documentation[/dim]")
                else:
                    # Validate existing documentation
                    # Note: For now, we'll skip validation and just check if it exists
                    # TODO: Implement proper validation here
                    items_skipped += 1
                    if verbose:
                        self.console.print(f"  [dim]→ {item.type} '{item.name}': has documentation, skipping[/dim]")

            if not items_to_document:
                self.console.print("  [green]✓ All items already documented[/green]")
                return {
                    'success': True,
                    'items_processed': len(items),
                    'items_documented': 0,
                    'items_skipped': items_skipped
                }

            if dry_run:
                self.console.print(f"  [yellow]○ Dry run - would document {len(items_to_document)} items[/yellow]")
                return {
                    'success': True,
                    'items_processed': len(items),
                    'items_documented': 0,
                    'items_skipped': items_skipped
                }

            # Step 3: Generate documentation for each item
            if verbose:
                self.console.print(f"  [dim]Generating documentation for {len(items_to_document)} items...[/dim]")

            documented_items = []
            for item in items_to_document:
                try:
                    # Generate documentation for this specific code item
                    doc = self.generator.generate(
                        file_path,
                        item.code,
                        detail_level
                    )

                    documented_items.append({
                        'item': item,
                        'documentation': doc
                    })

                    if verbose:
                        self.console.print(f"  [dim]✓ Documented {item.type} '{item.name}'[/dim]")

                except Exception as e:
                    if verbose:
                        self.console.print(f"  [yellow]⚠ Failed to document {item.type} '{item.name}': {e}[/yellow]")
                    continue

            if not documented_items:
                return {
                    'success': False,
                    'items_processed': len(items),
                    'items_documented': 0,
                    'items_skipped': items_skipped,
                    'error': 'Failed to generate documentation for any items'
                }

            # Step 4: Inject all documentation back into the file
            if verbose:
                self.console.print("  [dim]Injecting documentation into file...[/dim]")

            content = file_path.read_text(encoding='utf-8')
            modified_content = self._inject_multiple_docs(
                content,
                documented_items,
                file_path.suffix.lower()
            )

            # Validate that code wasn't corrupted
            if file_path.suffix.lower() == '.py':
                import ast
                try:
                    ast.parse(modified_content)
                except SyntaxError as e:
                    return {
                        'success': False,
                        'items_processed': len(items),
                        'items_documented': 0,
                        'items_skipped': items_skipped,
                        'error': f'Documentation injection corrupted Python syntax: {e}'
                    }

            # Write back to file
            file_path.write_text(modified_content, encoding='utf-8')

            self.console.print(f"  [green]✓ Documented {len(documented_items)} items in {file_path.name}[/green]")

            return {
                'success': True,
                'items_processed': len(items),
                'items_documented': len(documented_items),
                'items_skipped': items_skipped
            }

        except Exception as e:
            return {
                'success': False,
                'items_processed': 0,
                'items_documented': 0,
                'items_skipped': 0,
                'error': str(e)
            }

    def _inject_multiple_docs(self, content: str, documented_items: List[Dict[str, Any]],
                             file_type: str) -> str:
        """
        Inject multiple documentation blocks into content.

        Parameters
        ----------
        content : str
            Original file content
        documented_items : List[Dict[str, Any]]
            List of items with their documentation
        file_type : str
            File extension (.py, .sql, .r)

        Returns
        -------
        str
            Modified content with all documentation injected
        """
        if file_type == '.py':
            return self._inject_python_docs(content, documented_items)
        elif file_type == '.sql':
            return self._inject_sql_docs(content, documented_items)
        elif file_type == '.r':
            return self._inject_r_docs(content, documented_items)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _inject_python_docs(self, content: str, documented_items: List[Dict[str, Any]]) -> str:
        """Inject Python docstrings."""
        import ast

        lines = content.split('\n')

        # Sort items by line number (descending) to inject from bottom up
        sorted_items = sorted(documented_items,
                            key=lambda x: x['item'].line_start,
                            reverse=True)

        for doc_item in sorted_items:
            item = doc_item['item']
            documentation = doc_item['documentation']

            # Find insertion point (after def/class line)
            insert_line = item.line_start  # 1-indexed, so this becomes after the def line

            # Determine indentation (get from first line of function body)
            func_def_line = lines[item.line_start - 1]
            base_indent = len(func_def_line) - len(func_def_line.lstrip())
            doc_indent = ' ' * (base_indent + 4)

            # Create docstring lines
            docstring_lines = [
                f'{doc_indent}"""',
                *[f'{doc_indent}{line}' if line.strip() else '' for line in documentation.split('\n')],
                f'{doc_indent}"""'
            ]

            # Insert docstring
            for line in reversed(docstring_lines):
                lines.insert(insert_line, line)

        return '\n'.join(lines)

    def _inject_sql_docs(self, content: str, documented_items: List[Dict[str, Any]]) -> str:
        """Inject SQL comments."""
        if not documented_items:
            return content

        # For SQL, we typically have one item (the whole file)
        doc_item = documented_items[0]
        documentation = doc_item['documentation']

        # SQL doc goes at the top of the file
        return documentation + '\n\n' + content

    def _inject_r_docs(self, content: str, documented_items: List[Dict[str, Any]]) -> str:
        """Inject R Roxygen2 comments."""
        lines = content.split('\n')

        # Sort items by line number (descending) to inject from bottom up
        sorted_items = sorted(documented_items,
                            key=lambda x: x['item'].line_start,
                            reverse=True)

        for doc_item in sorted_items:
            item = doc_item['item']
            documentation = doc_item['documentation']

            # Insert before function definition
            insert_line = item.line_start - 1  # 0-indexed

            # Insert documentation lines
            doc_lines = documentation.split('\n')
            for line in reversed(doc_lines):
                lines.insert(insert_line, line)

        return '\n'.join(lines)