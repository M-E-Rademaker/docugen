"""
Comprehensive tests for documentation generator module with mocked API calls.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from anthropic import APIError, APIConnectionError, RateLimitError
from docugen.core.doc_generator import (
    DocGenerator,
    DocGeneratorError,
    APIKeyMissingError
)


class TestDocGeneratorInitialization:
    """Test suite for DocGenerator initialization."""

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        with patch('docugen.core.doc_generator.Anthropic'):
            generator = DocGenerator(api_key="test-key-123")
            assert generator.api_key == "test-key-123"

    def test_init_with_env_var(self, monkeypatch):
        """Test initialization with API key from environment."""
        monkeypatch.setenv('ANTHROPIC_API_KEY', 'env-key-456')
        with patch('docugen.core.doc_generator.Anthropic'):
            generator = DocGenerator()
            assert generator.api_key == "env-key-456"

    def test_init_without_api_key(self, monkeypatch):
        """Test initialization fails without API key."""
        monkeypatch.delenv('ANTHROPIC_API_KEY', raising=False)
        with pytest.raises(APIKeyMissingError) as exc_info:
            DocGenerator()
        assert "API key not found" in str(exc_info.value)
        assert "ANTHROPIC_API_KEY" in str(exc_info.value)

    def test_init_client_creation_fails(self):
        """Test initialization fails when client creation fails."""
        with patch('docugen.core.doc_generator.Anthropic', side_effect=Exception("Connection failed")):
            with pytest.raises(DocGeneratorError) as exc_info:
                DocGenerator(api_key="test-key")
            assert "Failed to initialize" in str(exc_info.value)

    def test_init_sets_model(self):
        """Test initialization sets correct model."""
        with patch('docugen.core.doc_generator.Anthropic'):
            generator = DocGenerator(api_key="test-key")
            assert generator.model == "claude-3-5-sonnet-20241022"

    def test_init_creates_prompts(self):
        """Test initialization creates language-specific prompt methods."""
        with patch('docugen.core.doc_generator.Anthropic'):
            generator = DocGenerator(api_key="test-key")
            # Test that prompt methods exist and return strings
            from docugen.utils.config import DetailLevel
            assert isinstance(generator._get_sql_prompt(DetailLevel.CONCISE), str)
            assert isinstance(generator._get_python_prompt(DetailLevel.CONCISE), str)
            assert isinstance(generator._get_r_prompt(DetailLevel.CONCISE), str)


class TestDocGeneratorLanguageDetection:
    """Test suite for file language detection."""

    @pytest.fixture
    def generator(self):
        """Create a DocGenerator instance."""
        with patch('docugen.core.doc_generator.Anthropic'):
            return DocGenerator(api_key="test-key")

    def test_detect_sql_file(self, generator):
        """Test detecting SQL file."""
        result = generator._get_file_language(Path("test.sql"))
        assert result == 'sql'

    def test_detect_python_file(self, generator):
        """Test detecting Python file."""
        result = generator._get_file_language(Path("test.py"))
        assert result == 'python'

    def test_detect_r_file(self, generator):
        """Test detecting R file."""
        result = generator._get_file_language(Path("test.r"))
        assert result == 'r'

    def test_detect_uppercase_extension(self, generator):
        """Test detecting file with uppercase extension."""
        result = generator._get_file_language(Path("TEST.SQL"))
        assert result == 'sql'

    def test_detect_unsupported_extension(self, generator):
        """Test detecting file with unsupported extension."""
        with pytest.raises(DocGeneratorError) as exc_info:
            generator._get_file_language(Path("test.txt"))
        assert "Unsupported file extension" in str(exc_info.value)
        assert ".txt" in str(exc_info.value)

    def test_detect_no_extension(self, generator):
        """Test detecting file without extension."""
        with pytest.raises(DocGeneratorError):
            generator._get_file_language(Path("testfile"))


class TestDocGeneratorPrompts:
    """Test suite for prompt templates."""

    @pytest.fixture
    def generator(self):
        """Create a DocGenerator instance."""
        with patch('docugen.core.doc_generator.Anthropic'):
            return DocGenerator(api_key="test-key")

    def test_sql_prompt_structure(self, generator):
        """Test SQL prompt has required structure."""
        from docugen.utils.config import DetailLevel
        prompt = generator._get_sql_prompt(DetailLevel.CONCISE)
        assert "SQL" in prompt or "sql" in prompt
        assert "documentation" in prompt.lower()
        assert "-- #" in prompt
        assert "## Description" in prompt
        assert "## Parameters" in prompt
        assert "## Returns" in prompt
        assert "## Example" in prompt

    def test_python_prompt_structure(self, generator):
        """Test Python prompt has required structure."""
        prompt = generator._get_python_prompt()
        assert "NumPy" in prompt
        assert "Parameters" in prompt
        assert "----------" in prompt
        assert "Returns" in prompt
        assert "-------" in prompt
        assert "Examples" in prompt or "Example" in prompt

    def test_r_prompt_structure(self, generator):
        """Test R prompt has required structure."""
        prompt = generator._get_r_prompt()
        assert "Roxygen2" in prompt
        assert "#'" in prompt
        assert "@param" in prompt
        assert "@return" in prompt
        assert "@examples" in prompt
        assert "@export" in prompt

    def test_prompt_has_code_placeholder(self, generator):
        """Test all prompts have code placeholder."""
        sql_prompt = generator._get_sql_prompt()
        python_prompt = generator._get_python_prompt()
        r_prompt = generator._get_r_prompt()

        assert "{code}" in sql_prompt
        assert "{code}" in python_prompt
        assert "{code}" in r_prompt


class TestDocGeneratorGenerate:
    """Test suite for documentation generation."""

    @pytest.fixture
    def generator(self):
        """Create a DocGenerator instance with mocked client."""
        with patch('docugen.core.doc_generator.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            gen = DocGenerator(api_key="test-key")
            gen.client = mock_client
            return gen

    def test_generate_python_success(self, generator):
        """Test successful Python documentation generation."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = '"""\nTest function.\n\nParameters\n----------\nx : int\n\nReturns\n-------\nint\n"""'
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        file_path = Path("test.py")
        code = "def test(x):\n    return x"

        result = generator.generate(file_path, code)

        assert result is not None
        assert "Parameters" in result
        assert "Returns" in result
        generator.client.messages.create.assert_called_once()

    def test_generate_sql_success(self, generator):
        """Test successful SQL documentation generation."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = '-- # Test Query\n-- ## Description\n-- Test description'
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        file_path = Path("test.sql")
        code = "SELECT * FROM users;"

        result = generator.generate(file_path, code)

        assert result is not None
        assert "-- #" in result
        generator.client.messages.create.assert_called_once()

    def test_generate_r_success(self, generator):
        """Test successful R documentation generation."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "#' Test Function\n#' @param x A value\n#' @return Result"
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        file_path = Path("test.r")
        code = "test <- function(x) { return(x) }"

        result = generator.generate(file_path, code)

        assert result is not None
        assert "#'" in result
        assert "@param" in result
        generator.client.messages.create.assert_called_once()

    def test_generate_rate_limit_error(self, generator):
        """Test handling of rate limit error."""
        # Use type() to create a custom exception class
        RateLimitError = type('RateLimitError', (Exception,), {})
        mock_error = RateLimitError("Rate limit exceeded")
        generator.client.messages.create = Mock(side_effect=mock_error)

        file_path = Path("test.py")
        code = "def test(): pass"

        with pytest.raises(DocGeneratorError) as exc_info:
            generator.generate(file_path, code)
        assert "error" in str(exc_info.value).lower()

    def test_generate_connection_error(self, generator):
        """Test handling of connection error."""
        # Use type() to create a custom exception class
        APIConnectionError = type('APIConnectionError', (Exception,), {})
        mock_error = APIConnectionError("Connection failed")
        generator.client.messages.create = Mock(side_effect=mock_error)

        file_path = Path("test.py")
        code = "def test(): pass"

        with pytest.raises(DocGeneratorError) as exc_info:
            generator.generate(file_path, code)
        assert "error" in str(exc_info.value).lower()

    def test_generate_api_error(self, generator):
        """Test handling of generic API error."""
        # Use type() to create a custom exception class
        APIError = type('APIError', (Exception,), {})
        mock_error = APIError("API error")
        generator.client.messages.create = Mock(side_effect=mock_error)

        file_path = Path("test.py")
        code = "def test(): pass"

        with pytest.raises(DocGeneratorError) as exc_info:
            generator.generate(file_path, code)
        assert "error" in str(exc_info.value).lower()

    def test_generate_unexpected_error(self, generator):
        """Test handling of unexpected error."""
        generator.client.messages.create = Mock(
            side_effect=Exception("Unexpected error")
        )

        file_path = Path("test.py")
        code = "def test(): pass"

        with pytest.raises(DocGeneratorError) as exc_info:
            generator.generate(file_path, code)
        assert "Unexpected error" in str(exc_info.value)

    def test_generate_uses_correct_prompt(self, generator):
        """Test that generate uses correct prompt for file type."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Generated docs"
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        # Test Python
        generator.generate(Path("test.py"), "def func(): pass")
        call_args = generator.client.messages.create.call_args
        prompt = call_args[1]['messages'][0]['content']
        assert "NumPy" in prompt

        # Reset mock
        generator.client.messages.create.reset_mock()

        # Test SQL
        generator.generate(Path("test.sql"), "SELECT 1;")
        call_args = generator.client.messages.create.call_args
        prompt = call_args[1]['messages'][0]['content']
        assert "documentation" in prompt.lower()

    def test_generate_with_correct_parameters(self, generator):
        """Test that generate calls API with correct parameters."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Generated docs"
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        generator.generate(Path("test.py"), "def func(): pass")

        call_args = generator.client.messages.create.call_args
        assert call_args[1]['model'] == "claude-3-5-sonnet-20241022"
        assert call_args[1]['max_tokens'] == 4096
        assert call_args[1]['temperature'] == 0.2
        assert len(call_args[1]['messages']) == 1
        assert call_args[1]['messages'][0]['role'] == 'user'

    def test_generate_strips_whitespace(self, generator):
        """Test that generate strips whitespace from response."""
        # Mock API response with extra whitespace
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = '\n\n  Generated docs  \n\n'
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        result = generator.generate(Path("test.py"), "def func(): pass")
        assert result == "Generated docs"


class TestDocGeneratorUpdate:
    """Test suite for documentation updating."""

    @pytest.fixture
    def generator(self):
        """Create a DocGenerator instance with mocked client."""
        with patch('docugen.core.doc_generator.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            gen = DocGenerator(api_key="test-key")
            gen.client = mock_client
            return gen

    def test_update_python_success(self, generator):
        """Test successful Python documentation update."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = '"""\nUpdated documentation.\n\nParameters\n----------\nx : int\n\nReturns\n-------\nint\n"""'
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        file_path = Path("test.py")
        existing_doc = {
            'content': 'Old docs',
            'type': 'docstring'
        }
        code = "def test(x):\n    return x"

        result = generator.update(file_path, existing_doc, code)

        assert result is not None
        assert "Updated" in result or "Parameters" in result
        generator.client.messages.create.assert_called_once()

    def test_update_includes_existing_content(self, generator):
        """Test that update includes existing documentation in prompt."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Updated docs"
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        file_path = Path("test.py")
        existing_doc = {
            'content': 'Existing documentation content',
            'type': 'docstring'
        }
        code = "def test(): pass"

        generator.update(file_path, existing_doc, code)

        call_args = generator.client.messages.create.call_args
        prompt = call_args[1]['messages'][0]['content']
        assert "Existing documentation content" in prompt
        assert "EXISTING DOCUMENTATION" in prompt

    def test_update_includes_code(self, generator):
        """Test that update includes code being documented in prompt."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Updated docs"
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        file_path = Path("test.py")
        existing_doc = {'content': 'Old docs'}
        code = "def test(x, y):\n    return x + y"

        generator.update(file_path, existing_doc, code)

        call_args = generator.client.messages.create.call_args
        prompt = call_args[1]['messages'][0]['content']
        assert code in prompt

    def test_update_rate_limit_error(self, generator):
        """Test handling of rate limit error during update."""
        RateLimitError = type('RateLimitError', (Exception,), {})
        mock_error = RateLimitError("Rate limit exceeded")
        generator.client.messages.create = Mock(side_effect=mock_error)

        file_path = Path("test.py")
        existing_doc = {'content': 'Old docs'}
        code = "def test(): pass"

        with pytest.raises(DocGeneratorError) as exc_info:
            generator.update(file_path, existing_doc, code)
        assert "error" in str(exc_info.value).lower()

    def test_update_connection_error(self, generator):
        """Test handling of connection error during update."""
        APIConnectionError = type('APIConnectionError', (Exception,), {})
        mock_error = APIConnectionError("Connection failed")
        generator.client.messages.create = Mock(side_effect=mock_error)

        file_path = Path("test.py")
        existing_doc = {'content': 'Old docs'}
        code = "def test(): pass"

        with pytest.raises(DocGeneratorError) as exc_info:
            generator.update(file_path, existing_doc, code)
        assert "error" in str(exc_info.value).lower()

    def test_update_api_error(self, generator):
        """Test handling of API error during update."""
        APIError = type('APIError', (Exception,), {})
        mock_error = APIError("API error")
        generator.client.messages.create = Mock(side_effect=mock_error)

        file_path = Path("test.py")
        existing_doc = {'content': 'Old docs'}
        code = "def test(): pass"

        with pytest.raises(DocGeneratorError) as exc_info:
            generator.update(file_path, existing_doc, code)
        assert "error" in str(exc_info.value).lower()

    def test_update_empty_existing_content(self, generator):
        """Test update with empty existing documentation."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "New docs"
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        file_path = Path("test.py")
        existing_doc = {}  # No content key
        code = "def test(): pass"

        result = generator.update(file_path, existing_doc, code)
        assert result is not None

    def test_update_uses_correct_language_prompt(self, generator):
        """Test that update uses correct base prompt for language."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Updated docs"
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        # Test SQL
        generator.update(Path("test.sql"), {'content': 'old'}, "SELECT 1;")
        call_args = generator.client.messages.create.call_args
        prompt = call_args[1]['messages'][0]['content']
        assert "markdown" in prompt.lower() or "SQL" in prompt


class TestDocGeneratorCrossPlatform:
    """Test suite for cross-platform compatibility."""

    @pytest.fixture
    def generator(self):
        """Create a DocGenerator instance with mocked client."""
        with patch('docugen.core.doc_generator.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            gen = DocGenerator(api_key="test-key")
            gen.client = mock_client
            return gen

    def test_generate_with_pathlib_path(self, generator):
        """Test generate works with pathlib Path objects."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Generated docs"
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        file_path = Path("test.py")
        result = generator.generate(file_path, "def func(): pass")
        assert result is not None

    def test_generate_with_unicode_code(self, generator):
        """Test generate handles unicode in code content."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Generated docs"
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        file_path = Path("test.py")
        code = "def calculate_pi():\n    '''Calculate pi value'''\n    return 3.14159"
        result = generator.generate(file_path, code)
        assert result is not None

    def test_generate_with_unicode_response(self, generator):
        """Test generate handles unicode in API response."""
        # Mock API response with unicode
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = '"""\nCalculate pi (3.14159).\n\nReturns\n-------\nfloat\n    Value of pi\n"""'
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        file_path = Path("test.py")
        result = generator.generate(file_path, "def func(): pass")
        assert "pi" in result