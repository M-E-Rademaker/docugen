"""
Code extractor module - identifies documentable items in code files.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class CodeItem:
    """Represents a documentable code item (function, class, etc.)."""
    type: str  # 'function', 'class', 'async_function', 'query'
    name: str
    code: str  # The actual code snippet
    line_start: int  # Starting line number (1-indexed)
    line_end: int  # Ending line number (1-indexed)
    has_documentation: bool
    existing_doc: str = ""  # Existing documentation if any


class CodeExtractor:
    """Extracts documentable items from code files."""

    def extract(self, file_path: Path) -> List[CodeItem]:
        """
        Extract all documentable items from a file.

        Parameters
        ----------
        file_path : Path
            Path to the code file

        Returns
        -------
        List[CodeItem]
            List of documentable code items found in the file

        Raises
        ------
        ValueError
            If file type is not supported
        """
        content = file_path.read_text(encoding='utf-8')
        suffix = file_path.suffix.lower()

        if suffix == '.py':
            return self._extract_python(content)
        elif suffix == '.sql':
            return self._extract_sql(content)
        elif suffix == '.r':
            return self._extract_r(content)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def _extract_python(self, content: str) -> List[CodeItem]:
        """
        Extract Python functions and classes.

        Parameters
        ----------
        content : str
            Python file content

        Returns
        -------
        List[CodeItem]
            List of Python functions and classes
        """
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        lines = content.split('\n')
        items = []

        # Extract module-level functions and classes
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                item_type = 'class' if isinstance(node, ast.ClassDef) else \
                           'async_function' if isinstance(node, ast.AsyncFunctionDef) else \
                           'function'

                # Get the code for this item
                start_line = node.lineno - 1  # 0-indexed
                end_line = node.end_lineno  # Already points to last line + 1

                code_lines = lines[start_line:end_line]
                code = '\n'.join(code_lines)

                # Check for existing documentation
                existing_doc = ast.get_docstring(node) or ""

                items.append(CodeItem(
                    type=item_type,
                    name=node.name,
                    code=code,
                    line_start=node.lineno,
                    line_end=node.end_lineno,
                    has_documentation=bool(existing_doc),
                    existing_doc=existing_doc
                ))

        return items

    def _extract_sql(self, content: str) -> List[CodeItem]:
        """
        Extract SQL functions/procedures.

        For SQL, we treat the entire file as one documentable unit
        since SQL files typically contain one main query or function.

        Parameters
        ----------
        content : str
            SQL file content

        Returns
        -------
        List[CodeItem]
            List containing the SQL query/function
        """
        lines = content.split('\n')

        # Check if there's existing documentation
        has_doc = False
        doc_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('-- #'):
                has_doc = True
                doc_lines.append(line)
            elif has_doc and stripped.startswith('--'):
                doc_lines.append(line)
            elif has_doc:
                break

        existing_doc = '\n'.join(doc_lines) if doc_lines else ""

        # For SQL, treat the whole file as one item
        # Try to extract function/procedure name
        name = "SQL Query"
        for line in lines:
            # Look for CREATE FUNCTION, CREATE PROCEDURE, etc.
            match = re.search(r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:FUNCTION|PROCEDURE)\s+(\w+)',
                            line, re.IGNORECASE)
            if match:
                name = match.group(1)
                break

        return [CodeItem(
            type='query',
            name=name,
            code=content,
            line_start=1,
            line_end=len(lines),
            has_documentation=has_doc,
            existing_doc=existing_doc
        )]

    def _extract_r(self, content: str) -> List[CodeItem]:
        """
        Extract R functions.

        Parameters
        ----------
        content : str
            R file content

        Returns
        -------
        List[CodeItem]
            List of R functions
        """
        lines = content.split('\n')
        items = []

        # Find R function definitions: name <- function(...)
        i = 0
        while i < len(lines):
            line = lines[i]

            # Check for function definition
            match = re.match(r'^\s*([a-zA-Z_][\w.]*)\s*<-\s*function\s*\(', line)
            if match:
                func_name = match.group(1)
                start_line = i + 1  # 1-indexed

                # Find the end of the function (closing brace)
                brace_count = 0
                in_function = False
                end_line = i

                for j in range(i, len(lines)):
                    for char in lines[j]:
                        if char == '{':
                            brace_count += 1
                            in_function = True
                        elif char == '}':
                            brace_count -= 1
                            if in_function and brace_count == 0:
                                end_line = j + 1
                                break
                    if in_function and brace_count == 0:
                        break

                # Check for existing Roxygen documentation
                doc_start = None
                for k in range(i - 1, -1, -1):
                    if lines[k].strip().startswith("#'"):
                        doc_start = k
                    else:
                        break

                has_doc = doc_start is not None
                existing_doc = '\n'.join(lines[doc_start:i]) if has_doc else ""

                # Extract the function code
                func_lines = lines[i:end_line]
                code = '\n'.join(func_lines)

                items.append(CodeItem(
                    type='function',
                    name=func_name,
                    code=code,
                    line_start=start_line,
                    line_end=end_line,
                    has_documentation=has_doc,
                    existing_doc=existing_doc
                ))

                i = end_line
            else:
                i += 1

        return items