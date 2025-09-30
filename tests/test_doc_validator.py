"""
Comprehensive tests for documentation validator module.
"""

import pytest
from pathlib import Path
from docugen.core.doc_validator import DocValidator, ValidationResult
from docugen.core.doc_parser import DocParser


class TestValidationResult:
    """Test suite for ValidationResult class."""

    def test_validation_result_valid(self):
        """Test creating valid ValidationResult."""
        result = ValidationResult(True, [])
        assert result.is_valid is True
        assert len(result.issues) == 0
        assert "VALID" in repr(result)

    def test_validation_result_invalid(self):
        """Test creating invalid ValidationResult."""
        issues = ["Missing description", "No parameters"]
        result = ValidationResult(False, issues)
        assert result.is_valid is False
        assert len(result.issues) == 2
        assert "INVALID" in repr(result)
        assert "2 issues" in repr(result)

    def test_validation_result_empty_issues(self):
        """Test ValidationResult with empty issues list."""
        result = ValidationResult(True, [])
        assert result.is_valid is True
        assert result.issues == []


class TestDocValidatorPython:
    """Test suite for Python documentation validation."""

    @pytest.fixture
    def validator(self):
        """Create a DocValidator instance."""
        return DocValidator()

    @pytest.fixture
    def parser(self):
        """Create a DocParser instance."""
        return DocParser()

    @pytest.fixture
    def fixtures_dir(self):
        """Get path to fixtures directory."""
        return Path(__file__).parent / "fixtures"

    def test_validate_documented_python(self, validator, parser, fixtures_dir):
        """Test validating properly documented Python file."""
        file_path = fixtures_dir / "python_documented.py"
        doc = parser.parse(file_path)
        result = validator.validate(file_path, doc)

        assert result.is_valid is True
        assert len(result.issues) == 0

    def test_validate_incomplete_python(self, validator, parser, fixtures_dir):
        """Test validating Python file with incomplete documentation."""
        file_path = fixtures_dir / "python_incomplete.py"
        doc = parser.parse(file_path)
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert len(result.issues) > 0
        # Should have issues about missing sections
        assert any("Missing" in issue or "missing" in issue for issue in result.issues)

    def test_validate_undocumented_python(self, validator, fixtures_dir):
        """Test validating Python file with no documentation."""
        file_path = fixtures_dir / "python_undocumented.py"
        result = validator.validate(file_path, None)

        assert result.is_valid is False
        assert "No documentation found" in result.issues

    def test_validate_python_missing_name(self, validator, tmp_path):
        """Test validating Python doc without function name."""
        doc = {
            'name': None,
            'description': 'A description',
            'parameters': 'x : int',
            'returns': 'int',
            'raw_doc': '"""\nDoc\n\nParameters\n----------\nx : int\n\nReturns\n-------\nint\n"""'
        }
        file_path = tmp_path / "test.py"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("name" in issue.lower() for issue in result.issues)

    def test_validate_python_short_description(self, validator, tmp_path):
        """Test validating Python doc with too short description."""
        doc = {
            'name': 'func',
            'description': 'Short',  # Less than 10 characters
            'parameters': 'x : int',
            'returns': 'int',
            'raw_doc': '"""\nShort\n\nParameters\n----------\nx : int\n\nReturns\n-------\nint\n"""'
        }
        file_path = tmp_path / "test.py"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("too short" in issue.lower() for issue in result.issues)

    def test_validate_python_missing_parameters(self, validator, tmp_path):
        """Test validating Python doc without Parameters section."""
        doc = {
            'name': 'func',
            'description': 'A proper description here',
            'parameters': None,
            'returns': 'int',
            'raw_doc': '"""\nA proper description here\n\nReturns\n-------\nint\n"""'
        }
        file_path = tmp_path / "test.py"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("Parameters" in issue for issue in result.issues)

    def test_validate_python_missing_returns(self, validator, tmp_path):
        """Test validating Python doc without Returns section."""
        doc = {
            'name': 'func',
            'description': 'A proper description here',
            'parameters': 'x : int',
            'returns': None,
            'raw_doc': '"""\nA proper description here\n\nParameters\n----------\nx : int\n"""'
        }
        file_path = tmp_path / "test.py"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("Returns" in issue for issue in result.issues)

    def test_validate_python_empty_returns(self, validator, tmp_path):
        """Test validating Python doc with empty Returns section."""
        doc = {
            'name': 'func',
            'description': 'A proper description here',
            'parameters': 'x : int',
            'returns': '   ',
            'raw_doc': '"""\nA proper description here\n\nParameters\n----------\nx : int\n\nReturns\n-------\n\n"""'
        }
        file_path = tmp_path / "test.py"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("Empty Returns" in issue for issue in result.issues)

    def test_validate_python_bad_parameter_format(self, validator, tmp_path):
        """Test validating Python doc with improperly formatted parameters."""
        doc = {
            'name': 'func',
            'description': 'A proper description here',
            'parameters': 'x is a number',  # Missing colon format
            'returns': 'int\n    Description',
            'raw_doc': '"""\nA proper description here\n\nParameters\n----------\nx is a number\n\nReturns\n-------\nint\n    Description\n"""'
        }
        file_path = tmp_path / "test.py"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("param_name : type" in issue for issue in result.issues)

    def test_validate_python_missing_underlines(self, validator, tmp_path):
        """Test validating Python doc without proper section underlines."""
        doc = {
            'name': 'func',
            'description': 'A proper description here',
            'parameters': 'x : int',
            'returns': 'int',
            'raw_doc': '"""\nA proper description here\n\nParameters\nx : int\n\nReturns\nint\n"""'
        }
        file_path = tmp_path / "test.py"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("underline" in issue.lower() for issue in result.issues)


class TestDocValidatorSQL:
    """Test suite for SQL documentation validation."""

    @pytest.fixture
    def validator(self):
        """Create a DocValidator instance."""
        return DocValidator()

    @pytest.fixture
    def parser(self):
        """Create a DocParser instance."""
        return DocParser()

    @pytest.fixture
    def fixtures_dir(self):
        """Get path to fixtures directory."""
        return Path(__file__).parent / "fixtures"

    def test_validate_documented_sql(self, validator, parser, fixtures_dir):
        """Test validating properly documented SQL file."""
        file_path = fixtures_dir / "sql_documented.sql"
        doc = parser.parse(file_path)
        result = validator.validate(file_path, doc)

        assert result.is_valid is True
        assert len(result.issues) == 0

    def test_validate_incomplete_sql(self, validator, parser, fixtures_dir):
        """Test validating SQL file with incomplete documentation."""
        file_path = fixtures_dir / "sql_incomplete.sql"
        doc = parser.parse(file_path)
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert len(result.issues) > 0
        # Should have issues about missing sections
        assert any("Missing" in issue or "missing" in issue for issue in result.issues)

    def test_validate_undocumented_sql(self, validator, fixtures_dir):
        """Test validating SQL file with no documentation."""
        file_path = fixtures_dir / "sql_undocumented.sql"
        result = validator.validate(file_path, None)

        assert result.is_valid is False
        assert "No documentation found" in result.issues

    def test_validate_sql_missing_name(self, validator, tmp_path):
        """Test validating SQL doc without function name."""
        doc = {
            'name': None,
            'description': 'A description of the query',
            'parameters': '- param1 (INT)',
            'returns': '- result (INT)',
            'examples': 'SELECT 1',
            'raw_doc': '-- ## Description\n-- A description'
        }
        file_path = tmp_path / "test.sql"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("name" in issue.lower() for issue in result.issues)

    def test_validate_sql_short_description(self, validator, tmp_path):
        """Test validating SQL doc with too short description."""
        doc = {
            'name': 'Query',
            'description': 'Short',
            'parameters': '- param1 (INT)',
            'returns': '- result (INT)',
            'examples': 'SELECT 1',
            'raw_doc': '-- # Query\n--\n-- ## Description\n-- Short'
        }
        file_path = tmp_path / "test.sql"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("too short" in issue.lower() for issue in result.issues)

    def test_validate_sql_missing_description(self, validator, tmp_path):
        """Test validating SQL doc without Description section."""
        doc = {
            'name': 'Query',
            'description': None,
            'parameters': '- param1 (INT)',
            'returns': '- result (INT)',
            'examples': 'SELECT 1',
            'raw_doc': '-- # Query'
        }
        file_path = tmp_path / "test.sql"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("Description" in issue for issue in result.issues)

    def test_validate_sql_missing_parameters(self, validator, tmp_path):
        """Test validating SQL doc without Parameters section."""
        doc = {
            'name': 'Query',
            'description': 'A proper description of the query',
            'parameters': None,
            'returns': '- result (INT)',
            'examples': 'SELECT 1',
            'raw_doc': '-- # Query\n-- ## Description\n-- A proper description'
        }
        file_path = tmp_path / "test.sql"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("parameters" in issue.lower() for issue in result.issues)

    def test_validate_sql_missing_returns(self, validator, tmp_path):
        """Test validating SQL doc without Returns section."""
        doc = {
            'name': 'Query',
            'description': 'A proper description of the query',
            'parameters': '- param1 (INT)',
            'returns': None,
            'examples': 'SELECT 1',
            'raw_doc': '-- # Query\n-- ## Description\n-- A proper description'
        }
        file_path = tmp_path / "test.sql"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("returns" in issue.lower() for issue in result.issues)

    def test_validate_sql_missing_example(self, validator, tmp_path):
        """Test validating SQL doc without Example section."""
        doc = {
            'name': 'Query',
            'description': 'A proper description of the query',
            'parameters': '- param1 (INT)',
            'returns': '- result (INT)',
            'examples': None,
            'raw_doc': '-- # Query\n-- ## Description\n-- A proper description'
        }
        file_path = tmp_path / "test.sql"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("example" in issue.lower() for issue in result.issues)

    def test_validate_sql_empty_sections(self, validator, tmp_path):
        """Test validating SQL doc with empty sections."""
        doc = {
            'name': 'Query',
            'description': '   ',
            'parameters': '',
            'returns': '   ',
            'examples': '',
            'raw_doc': '-- # Query\n-- ## Description\n--\n-- ## Parameters\n--'
        }
        file_path = tmp_path / "test.sql"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        # Should have multiple empty section issues
        empty_issues = [i for i in result.issues if "Empty" in i]
        assert len(empty_issues) >= 2


class TestDocValidatorR:
    """Test suite for R documentation validation."""

    @pytest.fixture
    def validator(self):
        """Create a DocValidator instance."""
        return DocValidator()

    @pytest.fixture
    def parser(self):
        """Create a DocParser instance."""
        return DocParser()

    @pytest.fixture
    def fixtures_dir(self):
        """Get path to fixtures directory."""
        return Path(__file__).parent / "fixtures"

    def test_validate_documented_r(self, validator, parser, fixtures_dir):
        """Test validating properly documented R file."""
        file_path = fixtures_dir / "r_documented.r"
        doc = parser.parse(file_path)
        result = validator.validate(file_path, doc)

        assert result.is_valid is True
        assert len(result.issues) == 0

    def test_validate_incomplete_r(self, validator, parser, fixtures_dir):
        """Test validating R file with incomplete documentation."""
        file_path = fixtures_dir / "r_incomplete.r"
        doc = parser.parse(file_path)
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert len(result.issues) > 0
        # Should have issues about missing sections
        assert any("@return" in issue for issue in result.issues)

    def test_validate_undocumented_r(self, validator, fixtures_dir):
        """Test validating R file with no documentation."""
        file_path = fixtures_dir / "r_undocumented.r"
        result = validator.validate(file_path, None)

        assert result.is_valid is False
        assert "No documentation found" in result.issues

    def test_validate_r_missing_name(self, validator, tmp_path):
        """Test validating R doc without function name."""
        doc = {
            'name': None,
            'description': 'A description of the function',
            'parameters': '@param x A value',
            'returns': 'A result',
            'examples': 'func(x)',
            'raw_doc': "#' A description\n#' @param x A value\n#' @return A result"
        }
        file_path = tmp_path / "test.r"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("name" in issue.lower() for issue in result.issues)

    def test_validate_r_short_description(self, validator, tmp_path):
        """Test validating R doc with too short description."""
        doc = {
            'name': 'func',
            'description': 'Short',
            'parameters': '@param x A numeric value',
            'returns': 'A result',
            'examples': 'func(x)',
            'raw_doc': "#' Short\n#' @param x A value\n#' @return A result"
        }
        file_path = tmp_path / "test.r"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("too short" in issue.lower() for issue in result.issues)

    def test_validate_r_missing_description(self, validator, tmp_path):
        """Test validating R doc without description."""
        doc = {
            'name': 'func',
            'description': None,
            'parameters': '@param x A numeric value',
            'returns': 'A result',
            'examples': 'func(x)',
            'raw_doc': "#' @param x A value\n#' @return A result"
        }
        file_path = tmp_path / "test.r"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("description" in issue.lower() for issue in result.issues)

    def test_validate_r_missing_param_tags(self, validator, tmp_path):
        """Test validating R doc without @param tags."""
        doc = {
            'name': 'func',
            'description': 'A proper description of the function',
            'parameters': None,
            'returns': 'A result',
            'examples': 'func(x)',
            'raw_doc': "#' A proper description\n#' @return A result"
        }
        file_path = tmp_path / "test.r"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("@param" in issue for issue in result.issues)

    def test_validate_r_missing_return_tag(self, validator, tmp_path):
        """Test validating R doc without @return tag."""
        doc = {
            'name': 'func',
            'description': 'A proper description of the function',
            'parameters': '@param x A numeric value',
            'returns': None,
            'examples': 'func(x)',
            'raw_doc': "#' A proper description\n#' @param x A value"
        }
        file_path = tmp_path / "test.r"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("@return" in issue for issue in result.issues)

    def test_validate_r_empty_return(self, validator, tmp_path):
        """Test validating R doc with empty @return section."""
        doc = {
            'name': 'func',
            'description': 'A proper description of the function',
            'parameters': '@param x A numeric value',
            'returns': '   ',
            'examples': 'func(x)',
            'raw_doc': "#' A proper description\n#' @param x A value\n#' @return"
        }
        file_path = tmp_path / "test.r"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("Empty @return" in issue for issue in result.issues)

    def test_validate_r_bad_param_format(self, validator, tmp_path):
        """Test validating R doc with parameters not using @param format."""
        doc = {
            'name': 'func',
            'description': 'A proper description of the function',
            'parameters': 'x is a value',  # Missing @param tag
            'returns': 'A result',
            'examples': 'func(x)',
            'raw_doc': "#' A proper description\n#' x is a value\n#' @return A result"
        }
        file_path = tmp_path / "test.r"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("@param tag" in issue for issue in result.issues)

    def test_validate_r_line_without_marker(self, validator, tmp_path):
        """Test validating R doc with lines not starting with #'."""
        doc = {
            'name': 'func',
            'description': 'A proper description of the function',
            'parameters': '@param x A numeric value',
            'returns': 'A result',
            'examples': 'func(x)',
            'raw_doc': "#' A proper description\n@param x A value\n#' @return A result"
        }
        file_path = tmp_path / "test.r"
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("does not start with #'" in issue for issue in result.issues)


class TestDocValidatorGeneral:
    """Test suite for general validator functionality."""

    @pytest.fixture
    def validator(self):
        """Create a DocValidator instance."""
        return DocValidator()

    def test_validate_none_documentation(self, validator, tmp_path):
        """Test validating with None documentation."""
        file_path = tmp_path / "test.py"
        result = validator.validate(file_path, None)

        assert result.is_valid is False
        assert "No documentation found" in result.issues

    def test_validate_unsupported_file_type(self, validator, tmp_path):
        """Test validating file with unsupported extension."""
        file_path = tmp_path / "test.txt"
        doc = {'name': 'test'}
        result = validator.validate(file_path, doc)

        assert result.is_valid is False
        assert any("Unsupported file type" in issue for issue in result.issues)

    def test_validate_different_file_types(self, validator, tmp_path):
        """Test that validator routes to correct language validator."""
        # Valid minimal docs for each language
        sql_doc = {
            'name': 'Query',
            'description': 'A proper description of the query',
            'parameters': '- None',
            'returns': '- result (INT)',
            'examples': 'SELECT 1',
            'raw_doc': '-- # Query\n-- ## Description\n-- A proper description\n-- ## Parameters\n-- - None\n-- ## Returns\n-- - result (INT)\n-- ## Example\n-- SELECT 1'
        }

        python_doc = {
            'name': 'func',
            'description': 'A proper description here',
            'parameters': 'x : int',
            'returns': 'int\n    Result',
            'raw_doc': '"""\nA proper description here\n\nParameters\n----------\nx : int\n\nReturns\n-------\nint\n    Result\n"""'
        }

        r_doc = {
            'name': 'func',
            'description': 'A proper description of the function',
            'parameters': '@param x A numeric value',
            'returns': 'A result',
            'raw_doc': "#' A proper description of the function\n#' @param x A numeric value\n#' @return A result"
        }

        sql_result = validator.validate(tmp_path / "test.sql", sql_doc)
        py_result = validator.validate(tmp_path / "test.py", python_doc)
        r_result = validator.validate(tmp_path / "test.r", r_doc)

        # Each should be valid for its type
        assert sql_result.is_valid is True
        assert py_result.is_valid is True
        assert r_result.is_valid is True


class TestDocValidatorCrossPlatform:
    """Test suite for cross-platform compatibility."""

    @pytest.fixture
    def validator(self):
        """Create a DocValidator instance."""
        return DocValidator()

    def test_validate_windows_paths(self, validator, tmp_path):
        """Test validation with Path objects (works on all platforms)."""
        file_path = tmp_path / "test.py"
        doc = {
            'name': 'func',
            'description': 'A proper description here',
            'parameters': 'x : int',
            'returns': 'int\n    Result',
            'raw_doc': '"""\nA proper description here\n\nParameters\n----------\nx : int\n\nReturns\n-------\nint\n    Result\n"""'
        }

        result = validator.validate(file_path, doc)
        # Should work regardless of platform
        assert isinstance(result, ValidationResult)

    def test_validate_with_unicode_content(self, validator, tmp_path):
        """Test validation with unicode characters in documentation."""
        file_path = tmp_path / "test.py"
        doc = {
            'name': 'calculate_pi',
            'description': 'Calculate pi (3.14159) to specified precision',
            'parameters': 'precision : int\n    Number of decimal places',
            'returns': 'float\n    Value of pi',
            'raw_doc': '"""\nCalculate pi (3.14159) to specified precision\n\nParameters\n----------\nprecision : int\n    Number of decimal places\n\nReturns\n-------\nfloat\n    Value of pi\n"""'
        }

        result = validator.validate(file_path, doc)
        assert result.is_valid is True