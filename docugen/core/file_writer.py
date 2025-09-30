"""
File writer module - safely writes modified files.
"""

from pathlib import Path
import ast
import re


class FileWriter:
    """Handles safe file writing operations and documentation injection."""

    def write(self, original_path: Path, content: str, suffix: str) -> Path:
        """
        Write modified file with suffix (legacy method for backward compatibility).

        Parameters
        ----------
        original_path : Path
            Original file path
        content : str
            Modified file content
        suffix : str
            Suffix to add to filename

        Returns
        -------
        Path
            Path to the written file
        """
        # Create new filename with suffix
        new_name = f"{original_path.stem}{suffix}{original_path.suffix}"
        new_path = original_path.parent / new_name

        # Write file
        new_path.write_text(content, encoding='utf-8')

        return new_path

    def inject_documentation(self, file_path: Path, documentation: str) -> Path:
        """
        Inject documentation into the original file.

        Parameters
        ----------
        file_path : Path
            Original file path
        documentation : str
            Documentation to inject

        Returns
        -------
        Path
            Path to the modified file (same as input)
        """
        # Read original file
        content = file_path.read_text(encoding='utf-8')

        # Determine file type and inject accordingly
        suffix = file_path.suffix.lower()
        if suffix == '.sql':
            modified_content = self._inject_sql_doc(content, documentation)
        elif suffix == '.py':
            modified_content = self._inject_python_doc(content, documentation)
        elif suffix == '.r':
            modified_content = self._inject_r_doc(content, documentation)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        # Write back to original file
        file_path.write_text(modified_content, encoding='utf-8')

        return file_path

    def _inject_sql_doc(self, content: str, documentation: str) -> str:
        """
        Inject SQL documentation at the beginning of the file.

        Parameters
        ----------
        content : str
            Original file content
        documentation : str
            Documentation comments to inject

        Returns
        -------
        str
            Modified content with documentation injected
        """
        lines = content.split('\n')

        # Remove existing documentation if present
        new_lines = []
        skip_doc = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('-- #'):
                skip_doc = True
            elif skip_doc and stripped.startswith('--'):
                continue
            elif skip_doc and not stripped.startswith('--'):
                skip_doc = False
                new_lines.append(line)
            else:
                new_lines.append(line)

        # Add new documentation at the beginning
        result = documentation + '\n\n' + '\n'.join(new_lines)
        return result.strip() + '\n'

    def _inject_python_doc(self, content: str, documentation: str) -> str:
        """
        Inject Python docstrings for ALL undocumented functions/classes.

        CRITICAL: This method MUST preserve all code functionality.
        It only adds/updates docstrings, never modifies actual code.

        Parameters
        ----------
        content : str
            Original file content
        documentation : str
            Docstring content to inject (WITHOUT triple quotes)

        Returns
        -------
        str
            Modified content with docstrings injected

        Raises
        ------
        ValueError
            If file cannot be parsed or injection would corrupt code
        """
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            raise ValueError(f"Cannot parse Python file: {e}")

        lines = content.split('\n')

        # Find ALL functions and classes at module level
        # Sort by line number in reverse to inject from bottom to top
        # (avoids line number shifts during injection)
        targets = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                existing_doc = ast.get_docstring(node)
                targets.append({
                    'node': node,
                    'line': node.lineno - 1,  # 0-indexed
                    'has_doc': existing_doc is not None,
                    'name': node.name
                })

        # Sort by line number descending (inject from bottom up)
        targets.sort(key=lambda x: x['line'], reverse=True)

        # Process each target
        for target in targets:
            node = target['node']
            func_line = target['line']

            # Remove existing docstring if present
            if target['has_doc']:
                # Find the docstring location
                for i in range(func_line + 1, len(lines)):
                    stripped = lines[i].strip()
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        quote_type = '"""' if stripped.startswith('"""') else "'''"

                        # Check if single-line docstring
                        if stripped.endswith(quote_type) and len(stripped) > 6:
                            del lines[i]
                            break
                        else:
                            # Multi-line docstring
                            start = i
                            for j in range(i + 1, len(lines)):
                                if quote_type in lines[j]:
                                    del lines[start:j+1]
                                    break
                            break
                    elif stripped and not stripped.startswith('#'):
                        # No docstring found (shouldn't happen if has_doc=True)
                        break

            # Insert new docstring
            indent = ' ' * (node.col_offset + 4)  # Body indent
            docstring_lines = [
                f'{indent}"""',
                *[f'{indent}{line}' if line else indent.rstrip() for line in documentation.split('\n')],
                f'{indent}"""'
            ]

            # Insert after function/class definition line
            insert_pos = func_line + 1
            for line in reversed(docstring_lines):
                lines.insert(insert_pos, line)

        result = '\n'.join(lines)

        # Validate: ensure result is still valid Python
        try:
            ast.parse(result)
        except SyntaxError as e:
            raise ValueError(f"Injection corrupted Python syntax: {e}")

        return result

    def _inject_r_doc(self, content: str, documentation: str) -> str:
        """
        Inject R Roxygen2 documentation before function definition.

        Parameters
        ----------
        content : str
            Original file content
        documentation : str
            Roxygen2 comments to inject

        Returns
        -------
        str
            Modified content with documentation injected
        """
        lines = content.split('\n')

        # Find existing Roxygen2 block and function definition
        doc_start = None
        doc_end = None
        func_line = None

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#'"):
                if doc_start is None:
                    doc_start = i
                doc_end = i
            elif doc_start is not None and '<-' in stripped and 'function' in stripped:
                func_line = i
                break
            elif stripped and not stripped.startswith("#'") and doc_start is not None:
                # Found non-Roxygen line after doc block
                break

        # Find function definition if not found yet
        if func_line is None:
            for i, line in enumerate(lines):
                if '<-' in line and 'function' in line:
                    func_line = i
                    break

        if func_line is None:
            # No function found, add at beginning
            return documentation + '\n\n' + content

        # Remove existing documentation if present
        if doc_start is not None and doc_end is not None:
            del lines[doc_start:doc_end + 1]
            func_line -= (doc_end - doc_start + 1)

        # Insert new documentation before function
        lines.insert(func_line, documentation)

        return '\n'.join(lines)

    def backup(self, file_path: Path) -> Path:
        """Create backup of original file."""
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        backup_path.write_bytes(file_path.read_bytes())
        return backup_path