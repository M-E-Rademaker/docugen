"""
Documentation validator module - checks compliance with standards.
"""

from pathlib import Path
from typing import Dict, Any, List
from docugen.standards.sql_standard import SQLStandard
from docugen.standards.python_standard import PythonStandard
from docugen.standards.r_standard import RStandard


class ValidationResult:
    """Result of documentation validation."""

    def __init__(self, is_valid: bool, issues: List[str]):
        """
        Initialize validation result.

        Parameters
        ----------
        is_valid : bool
            Whether the documentation is valid
        issues : List[str]
            List of validation issues found
        """
        self.is_valid = is_valid
        self.issues = issues

    def __repr__(self):
        """String representation of validation result."""
        status = "VALID" if self.is_valid else "INVALID"
        return f"ValidationResult({status}, {len(self.issues)} issues)"


class DocValidator:
    """Validates documentation against language standards."""

    def validate(self, file_path: Path, documentation: Dict[str, Any]) -> ValidationResult:
        """
        Validate documentation against language-specific standards.

        Parameters
        ----------
        file_path : Path
            Path to the file being validated
        documentation : Dict[str, Any]
            Parsed documentation structure

        Returns
        -------
        ValidationResult
            Validation result with any issues found
        """
        if documentation is None:
            return ValidationResult(False, ["No documentation found"])

        # Detect file type and route to appropriate validator
        suffix = file_path.suffix.lower()
        if suffix == '.sql':
            return self._validate_sql(documentation)
        elif suffix == '.py':
            return self._validate_python(documentation)
        elif suffix == '.r':
            return self._validate_r(documentation)
        else:
            return ValidationResult(False, [f"Unsupported file type: {suffix}"])

    def _validate_sql(self, doc: Dict[str, Any]) -> ValidationResult:
        """
        Validate SQL markdown-style documentation.

        Parameters
        ----------
        doc : Dict[str, Any]
            Parsed SQL documentation

        Returns
        -------
        ValidationResult
            Validation result with specific issues
        """
        issues = []

        # Check raw documentation structure
        raw_doc = doc.get('raw_doc', '')
        if not SQLStandard.validate_structure(raw_doc):
            issues.append("Documentation does not follow SQL markdown standard structure")

        # Check required fields
        if not doc.get('name'):
            issues.append("Missing function/query name (-- # Header)")

        if not doc.get('description'):
            issues.append("Missing description section (-- ## Description)")
        elif len(doc.get('description', '').strip()) < 10:
            issues.append("Description is too short (minimum 10 characters)")

        if not doc.get('parameters'):
            issues.append("Missing parameters section (-- ## Parameters)")

        if not doc.get('returns'):
            issues.append("Missing returns section (-- ## Returns)")

        if not doc.get('examples'):
            issues.append("Missing example section (-- ## Example)")

        # Check for empty sections
        for field in ['description', 'parameters', 'returns', 'examples']:
            if doc.get(field) is not None and not doc.get(field).strip():
                issues.append(f"Empty {field} section")

        return ValidationResult(len(issues) == 0, issues)

    def _validate_python(self, doc: Dict[str, Any]) -> ValidationResult:
        """
        Validate Python NumPy-style docstrings.

        Parameters
        ----------
        doc : Dict[str, Any]
            Parsed Python documentation

        Returns
        -------
        ValidationResult
            Validation result with specific issues
        """
        issues = []

        # Check raw documentation structure
        raw_doc = doc.get('raw_doc', '')
        if not PythonStandard.validate_structure(raw_doc):
            issues.append("Documentation does not follow NumPy docstring standard structure")

        # Check required fields
        if not doc.get('name'):
            issues.append("Missing function/class name")

        if not doc.get('description'):
            issues.append("Missing description section")
        elif len(doc.get('description', '').strip()) < 10:
            issues.append("Description is too short (minimum 10 characters)")

        # Check for Parameters section structure
        if not doc.get('parameters'):
            issues.append("Missing Parameters section")
        else:
            params = doc.get('parameters', '')
            # Check if it has proper structure (parameter name : type format)
            if ':' not in params and 'None' not in params:
                issues.append("Parameters section should follow 'param_name : type' format")

        # Check for Returns section
        if not doc.get('returns'):
            issues.append("Missing Returns section")
        else:
            returns = doc.get('returns', '')
            if not returns.strip():
                issues.append("Empty Returns section")

        # Check for Examples section (recommended but not required)
        if not doc.get('examples'):
            # This is a warning, not a hard error
            pass

        # Check that Parameters and Returns sections have proper underlines in raw doc
        if 'Parameters' in raw_doc and '----------' not in raw_doc:
            issues.append("Parameters section missing dashed underline (----------)")
        if 'Returns' in raw_doc and '-------' not in raw_doc:
            issues.append("Returns section missing dashed underline (-------)")

        return ValidationResult(len(issues) == 0, issues)

    def _validate_r(self, doc: Dict[str, Any]) -> ValidationResult:
        """
        Validate R Roxygen2 documentation.

        Parameters
        ----------
        doc : Dict[str, Any]
            Parsed R documentation

        Returns
        -------
        ValidationResult
            Validation result with specific issues
        """
        issues = []

        # Check raw documentation structure
        raw_doc = doc.get('raw_doc', '')
        if not RStandard.validate_structure(raw_doc):
            issues.append("Documentation does not follow Roxygen2 standard structure")

        # Check required fields
        if not doc.get('name'):
            issues.append("Missing function name (could not extract from code)")

        if not doc.get('description'):
            issues.append("Missing description section")
        elif len(doc.get('description', '').strip()) < 10:
            issues.append("Description is too short (minimum 10 characters)")

        # Check for @param tags
        if not doc.get('parameters'):
            issues.append("Missing @param tags")
        else:
            params = doc.get('parameters', '')
            if '@param' not in params:
                issues.append("Parameters should use @param tag format")

        # Check for @return tag
        if not doc.get('returns'):
            issues.append("Missing @return tag")
        else:
            returns = doc.get('returns', '')
            if not returns.strip():
                issues.append("Empty @return section")

        # Check that all lines start with #'
        lines = raw_doc.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and not stripped.startswith("#'"):
                issues.append(f"Line {i} does not start with #' marker")
                break

        return ValidationResult(len(issues) == 0, issues)