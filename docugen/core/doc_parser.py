"""
Documentation parser module - extracts existing documentation.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import re
import ast


class DocParser:
    """Parses existing documentation from code files."""

    def parse(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse existing documentation from file.

        Parameters
        ----------
        file_path : Path
            Path to the file to parse

        Returns
        -------
        Optional[Dict[str, Any]]
            Parsed documentation structure or None if no docs found
        """
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return None

        # Detect file type and route to appropriate parser
        suffix = file_path.suffix.lower()
        if suffix == '.sql':
            return self._parse_sql(content)
        elif suffix == '.py':
            return self._parse_python(content)
        elif suffix == '.r':
            return self._parse_r(content)
        else:
            return None

    def _parse_sql(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse SQL markdown-style documentation.

        Parameters
        ----------
        content : str
            The SQL file content

        Returns
        -------
        Optional[Dict[str, Any]]
            Parsed documentation with keys: name, description, parameters,
            returns, examples, raw_doc
        """
        # Look for markdown-style SQL comments
        # Pattern: -- # Function Name followed by sections
        lines = content.split('\n')
        doc_lines = []
        in_doc_block = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('-- #'):
                in_doc_block = True
                doc_lines.append(line)
            elif in_doc_block and stripped.startswith('--'):
                doc_lines.append(line)
            elif in_doc_block and not stripped.startswith('--'):
                # End of documentation block
                break

        if not doc_lines:
            return None

        raw_doc = '\n'.join(doc_lines)

        # Extract sections
        result = {
            'name': None,
            'description': None,
            'parameters': None,
            'returns': None,
            'examples': None,
            'raw_doc': raw_doc
        }

        current_section = None
        section_content = []

        for line in doc_lines:
            stripped = line.strip()
            if stripped.startswith('-- #') and not stripped.startswith('-- ##'):
                # Function name
                result['name'] = stripped[4:].strip()
            elif '-- ## Description' in stripped:
                if current_section:
                    result[current_section] = '\n'.join(section_content).strip()
                    section_content = []
                current_section = 'description'
            elif '-- ## Parameters' in stripped:
                if current_section:
                    result[current_section] = '\n'.join(section_content).strip()
                    section_content = []
                current_section = 'parameters'
            elif '-- ## Returns' in stripped:
                if current_section:
                    result[current_section] = '\n'.join(section_content).strip()
                    section_content = []
                current_section = 'returns'
            elif '-- ## Example' in stripped:
                if current_section:
                    result[current_section] = '\n'.join(section_content).strip()
                    section_content = []
                current_section = 'examples'
            elif current_section and stripped.startswith('--'):
                # Content line
                content_text = stripped[2:].strip()
                section_content.append(content_text)

        # Save last section
        if current_section and section_content:
            result[current_section] = '\n'.join(section_content).strip()

        return result

    def _parse_python(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse Python NumPy-style docstrings.

        Parameters
        ----------
        content : str
            The Python file content

        Returns
        -------
        Optional[Dict[str, Any]]
            Parsed documentation with keys: name, description, parameters,
            returns, examples, raw_doc
        """
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return None

        # Find the first function or class with a docstring
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)
                if docstring:
                    return self._parse_numpy_docstring(node.name, docstring)

        return None

    def _parse_numpy_docstring(self, name: str, docstring: str) -> Dict[str, Any]:
        """
        Parse NumPy-style docstring content.

        Parameters
        ----------
        name : str
            Name of the function/class
        docstring : str
            The docstring content

        Returns
        -------
        Dict[str, Any]
            Parsed documentation structure
        """
        result = {
            'name': name,
            'description': None,
            'parameters': None,
            'returns': None,
            'examples': None,
            'raw_doc': f'"""\n{docstring}\n"""'
        }

        # Split into sections
        lines = docstring.split('\n')
        current_section = 'description'
        section_content = []
        description_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Check for section headers
            if stripped == 'Parameters':
                if description_lines:
                    result['description'] = '\n'.join(description_lines).strip()
                    description_lines = []
                current_section = 'parameters'
                # Skip the dashes line
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('-'):
                    i += 1
                section_content = []
            elif stripped == 'Returns':
                if current_section == 'parameters' and section_content:
                    result['parameters'] = '\n'.join(section_content).strip()
                current_section = 'returns'
                # Skip the dashes line
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('-'):
                    i += 1
                section_content = []
            elif stripped in ['Examples', 'Example']:
                if current_section == 'returns' and section_content:
                    result['returns'] = '\n'.join(section_content).strip()
                current_section = 'examples'
                # Skip the dashes line
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('-'):
                    i += 1
                section_content = []
            else:
                # Regular content line
                if current_section == 'description':
                    description_lines.append(line)
                else:
                    section_content.append(line)

            i += 1

        # Save remaining content
        if current_section == 'description' and description_lines:
            result['description'] = '\n'.join(description_lines).strip()
        elif section_content:
            result[current_section] = '\n'.join(section_content).strip()

        return result

    def _parse_r(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse R Roxygen2 documentation.

        Parameters
        ----------
        content : str
            The R file content

        Returns
        -------
        Optional[Dict[str, Any]]
            Parsed documentation with keys: name, description, parameters,
            returns, examples, raw_doc
        """
        lines = content.split('\n')
        doc_lines = []
        in_doc_block = False
        function_name = None

        # Find Roxygen2 comment block
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#'"):
                in_doc_block = True
                doc_lines.append(line)
            elif in_doc_block and stripped.startswith("#'"):
                doc_lines.append(line)
            elif in_doc_block and not stripped.startswith("#'"):
                # Check if next non-empty line is a function definition
                if '<-' in stripped and 'function' in stripped:
                    match = re.match(r'(\w+)\s*<-\s*function', stripped)
                    if match:
                        function_name = match.group(1)
                break

        if not doc_lines:
            return None

        raw_doc = '\n'.join(doc_lines)

        result = {
            'name': function_name,
            'description': None,
            'parameters': None,
            'returns': None,
            'examples': None,
            'raw_doc': raw_doc
        }

        current_section = 'description'
        section_content = []
        description_lines = []
        param_lines = []

        for line in doc_lines:
            stripped = line.strip()
            if stripped.startswith("#'"):
                content_text = stripped[2:].strip()

                if content_text.startswith('@param'):
                    if description_lines:
                        result['description'] = '\n'.join(description_lines).strip()
                        description_lines = []
                    current_section = 'parameters'
                    param_lines.append(content_text)
                elif content_text.startswith('@return'):
                    if param_lines:
                        result['parameters'] = '\n'.join(param_lines).strip()
                        param_lines = []
                    current_section = 'returns'
                    section_content = [content_text[7:].strip()]
                elif content_text.startswith('@examples'):
                    if current_section == 'returns' and section_content:
                        result['returns'] = '\n'.join(section_content).strip()
                        section_content = []
                    current_section = 'examples'
                    section_content = []
                elif content_text.startswith('@export'):
                    # Skip export tag
                    continue
                else:
                    # Regular content
                    if current_section == 'description':
                        description_lines.append(content_text)
                    elif current_section == 'parameters':
                        if param_lines:
                            param_lines.append(content_text)
                    else:
                        section_content.append(content_text)

        # Save remaining content
        if description_lines:
            result['description'] = '\n'.join(description_lines).strip()
        if param_lines:
            result['parameters'] = '\n'.join(param_lines).strip()
        if section_content:
            result[current_section] = '\n'.join(section_content).strip()

        return result