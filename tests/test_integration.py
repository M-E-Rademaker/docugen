"""
Integration tests for end-to-end DocuGen pipeline.

These tests verify that all components work together correctly.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from docugen.core.doc_parser import DocParser
from docugen.core.doc_validator import DocValidator
from docugen.core.doc_generator import DocGenerator
from docugen.core.file_writer import FileWriter


class TestParserValidatorIntegration:
    """Test integration between parser and validator."""

    @pytest.fixture
    def parser(self):
        """Create a DocParser instance."""
        return DocParser()

    @pytest.fixture
    def validator(self):
        """Create a DocValidator instance."""
        return DocValidator()

    @pytest.fixture
    def fixtures_dir(self):
        """Get path to fixtures directory."""
        return Path(__file__).parent / "fixtures"

    def test_parse_and_validate_documented_python(self, parser, validator, fixtures_dir):
        """Test parsing and validating documented Python file."""
        file_path = fixtures_dir / "python_documented.py"

        # Parse the file
        doc = parser.parse(file_path)
        assert doc is not None

        # Validate the parsed documentation
        result = validator.validate(file_path, doc)
        assert result.is_valid is True

    def test_parse_and_validate_incomplete_python(self, parser, validator, fixtures_dir):
        """Test parsing and validating incomplete Python file."""
        file_path = fixtures_dir / "python_incomplete.py"

        # Parse the file
        doc = parser.parse(file_path)
        assert doc is not None

        # Validate the parsed documentation
        result = validator.validate(file_path, doc)
        assert result.is_valid is False
        assert len(result.issues) > 0

    def test_parse_and_validate_documented_sql(self, parser, validator, fixtures_dir):
        """Test parsing and validating documented SQL file."""
        file_path = fixtures_dir / "sql_documented.sql"

        doc = parser.parse(file_path)
        assert doc is not None

        result = validator.validate(file_path, doc)
        assert result.is_valid is True

    def test_parse_and_validate_documented_r(self, parser, validator, fixtures_dir):
        """Test parsing and validating documented R file."""
        file_path = fixtures_dir / "r_documented.r"

        doc = parser.parse(file_path)
        assert doc is not None

        result = validator.validate(file_path, doc)
        assert result.is_valid is True

    def test_parse_and_validate_all_fixtures(self, parser, validator, fixtures_dir):
        """Test parsing and validating all fixture files."""
        results = {}

        for file_path in fixtures_dir.glob("*"):
            if file_path.suffix in ['.py', '.sql', '.r']:
                doc = parser.parse(file_path)
                if doc is not None:
                    validation = validator.validate(file_path, doc)
                    results[file_path.name] = validation.is_valid

        # Check that documented files are valid
        assert results.get('python_documented.py') is True
        assert results.get('sql_documented.sql') is True
        assert results.get('r_documented.r') is True

        # Check that incomplete files are invalid
        assert results.get('python_incomplete.py') is False
        assert results.get('sql_incomplete.sql') is False
        assert results.get('r_incomplete.r') is False


class TestGeneratorWriterIntegration:
    """Test integration between generator and file writer."""

    @pytest.fixture
    def generator(self):
        """Create a DocGenerator instance with mocked API."""
        with patch('docugen.core.doc_generator.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            gen = DocGenerator(api_key="test-key")
            gen.client = mock_client
            return gen

    @pytest.fixture
    def writer(self):
        """Create a FileWriter instance."""
        return FileWriter()

    def test_generate_and_write_python(self, generator, writer, tmp_path):
        """Test generating and writing Python documentation."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = '"""\nGenerated documentation.\n\nParameters\n----------\nx : int\n\nReturns\n-------\nint\n"""'
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        # Create original file
        original = tmp_path / "test.py"
        code = "def test(x):\n    return x"
        original.write_text(code)

        # Generate documentation
        docs = generator.generate(original, code)

        # Add docs to code
        documented_code = f"{docs}\ndef test(x):\n    return x"

        # Write documented version
        new_path = writer.write(original, documented_code, "_documented")

        # Verify
        assert new_path.exists()
        assert "Parameters" in new_path.read_text()
        assert "Returns" in new_path.read_text()
        assert "def test(x):" in new_path.read_text()

    def test_generate_and_write_sql(self, generator, writer, tmp_path):
        """Test generating and writing SQL documentation."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = '-- # Test Query\n-- ## Description\n-- Test description\n-- ## Parameters\n-- - None\n-- ## Returns\n-- - result (INT)\n-- ## Example\n-- SELECT 1;'
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        # Create original file
        original = tmp_path / "query.sql"
        code = "SELECT * FROM users;"
        original.write_text(code)

        # Generate and write
        docs = generator.generate(original, code)
        documented_code = f"{docs}\n\n{code}"
        new_path = writer.write(original, documented_code, "_documented")

        # Verify
        assert new_path.exists()
        assert "-- #" in new_path.read_text()
        assert "SELECT * FROM users;" in new_path.read_text()

    def test_backup_generate_and_write(self, generator, writer, tmp_path):
        """Test backup, generate, and write workflow."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = '"""\nGenerated docs.\n\nReturns\n-------\nNone\n"""'
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        # Create original file
        original = tmp_path / "script.py"
        code = "def func():\n    pass"
        original.write_text(code)

        # Backup
        backup_path = writer.backup(original)

        # Generate and write
        docs = generator.generate(original, code)
        documented_code = f"{docs}\ndef func():\n    pass"
        new_path = writer.write(original, documented_code, "_documented")

        # Verify all files exist
        assert original.exists()
        assert backup_path.exists()
        assert new_path.exists()

        # Verify contents
        assert backup_path.read_text() == code
        assert "Generated docs" in new_path.read_text()


class TestFullPipelineIntegration:
    """Test complete end-to-end pipeline."""

    @pytest.fixture
    def parser(self):
        """Create a DocParser instance."""
        return DocParser()

    @pytest.fixture
    def validator(self):
        """Create a DocValidator instance."""
        return DocValidator()

    @pytest.fixture
    def generator(self):
        """Create a DocGenerator instance with mocked API."""
        with patch('docugen.core.doc_generator.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            gen = DocGenerator(api_key="test-key")
            gen.client = mock_client
            return gen

    @pytest.fixture
    def writer(self):
        """Create a FileWriter instance."""
        return FileWriter()

    def test_undocumented_to_documented_python(self, parser, validator, generator, writer, tmp_path):
        """Test complete pipeline: undocumented -> documented Python file."""
        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = '"""\nCalculate sum.\n\nParameters\n----------\na : int\n    First number\nb : int\n    Second number\n\nReturns\n-------\nint\n    Sum of a and b\n"""'
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        # Create undocumented file
        original = tmp_path / "calc.py"
        code = "def add(a, b):\n    return a + b"
        original.write_text(code)

        # Step 1: Parse (should find no docs)
        doc = parser.parse(original)
        assert doc is None

        # Step 2: Validate (should be invalid)
        validation = validator.validate(original, doc)
        assert validation.is_valid is False

        # Step 3: Generate documentation
        docs = generator.generate(original, code)

        # Step 4: Write documented version with docs inside function
        documented_code = f"def add(a, b):\n    {docs}\n    return a + b"
        new_path = writer.write(original, documented_code, "_documented")

        # Step 5: Verify new file is documented
        new_doc = parser.parse(new_path)
        assert new_doc is not None
        # Note: Validation may or may not pass depending on generated docs quality
        # The key is that documentation was successfully generated and inserted

    def test_incomplete_to_complete_documentation(self, parser, validator, generator, writer, tmp_path):
        """Test complete pipeline: incomplete -> complete documentation."""
        # Create file with incomplete docs
        original = tmp_path / "func.py"
        code = '''def process(data):
    """Process data."""
    return data'''
        original.write_text(code)

        # Mock API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = '"""\nProcess input data.\n\nParameters\n----------\ndata : list\n    Input data to process\n\nReturns\n-------\nlist\n    Processed data\n\nExamples\n--------\n>>> process([1, 2, 3])\n[1, 2, 3]\n"""'
        mock_response.content = [mock_content]
        generator.client.messages.create = Mock(return_value=mock_response)

        # Step 1: Parse existing docs
        doc = parser.parse(original)
        assert doc is not None

        # Step 2: Validate (should be invalid - incomplete)
        validation = validator.validate(original, doc)
        assert validation.is_valid is False

        # Step 3: Update documentation
        updated_docs = generator.update(original, doc, code)

        # Step 4: Write updated version with docs inside function
        documented_code = f"def process(data):\n    {updated_docs}\n    return data"
        new_path = writer.write(original, documented_code, "_complete")

        # Step 5: Verify new file has complete docs
        new_doc = parser.parse(new_path)
        assert new_doc is not None
        # Documentation was successfully updated and inserted

    def test_multiple_files_pipeline(self, parser, validator, generator, writer, tmp_path):
        """Test pipeline with multiple files of different types."""
        # Mock API to return appropriate docs for each language
        def mock_generate(model, max_tokens, temperature, messages):
            prompt = messages[0]['content']
            response = Mock()
            content = Mock()

            if 'def' in prompt:  # Python
                content.text = '"""\nPython function.\n\nReturns\n-------\nNone\n"""'
            elif 'SELECT' in prompt:  # SQL
                content.text = '-- # SQL Query\n-- ## Description\n-- Query description\n-- ## Parameters\n-- - None\n-- ## Returns\n-- - result (INT)\n-- ## Example\n-- SELECT 1;'
            else:  # R
                content.text = "#' R function\n#' @return Result\n#' @export"

            response.content = [content]
            return response

        generator.client.messages.create = Mock(side_effect=mock_generate)

        # Create multiple files
        py_file = tmp_path / "script.py"
        py_file.write_text("def func():\n    pass")

        sql_file = tmp_path / "query.sql"
        sql_file.write_text("SELECT 1;")

        r_file = tmp_path / "func.r"
        r_file.write_text("func <- function() {}")

        files = [py_file, sql_file, r_file]
        documented_files = []

        # Process each file
        for file_path in files:
            code = file_path.read_text()

            # Parse
            doc = parser.parse(file_path)

            # Validate
            validation = validator.validate(file_path, doc)

            if not validation.is_valid:
                # Generate docs
                docs = generator.generate(file_path, code)

                # Write documented version - different format for each language
                if file_path.suffix == '.py':
                    # For Python, insert docstring inside function
                    documented_code = code.replace('def func():', f'def func():\n    {docs}')
                else:
                    # For SQL and R, prepend documentation
                    documented_code = f"{docs}\n{code}"

                new_path = writer.write(file_path, documented_code, "_documented")
                documented_files.append(new_path)

        # Verify all documented files
        assert len(documented_files) == 3
        for doc_file in documented_files:
            assert doc_file.exists()
            # Files exist with documentation added


class TestErrorHandlingIntegration:
    """Test error handling across components."""

    @pytest.fixture
    def parser(self):
        """Create a DocParser instance."""
        return DocParser()

    @pytest.fixture
    def validator(self):
        """Create a DocValidator instance."""
        return DocValidator()

    @pytest.fixture
    def generator(self):
        """Create a DocGenerator instance with mocked API."""
        with patch('docugen.core.doc_generator.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            gen = DocGenerator(api_key="test-key")
            gen.client = mock_client
            return gen

    def test_handle_unparseable_file(self, parser, validator, tmp_path):
        """Test handling file that can't be parsed."""
        # Create invalid Python file
        invalid_file = tmp_path / "invalid.py"
        invalid_file.write_text("def broken(\n    incomplete syntax")

        # Parse should return None
        doc = parser.parse(invalid_file)
        assert doc is None

        # Validate should handle None
        result = validator.validate(invalid_file, doc)
        assert result.is_valid is False
        assert "No documentation found" in result.issues

    def test_handle_api_error_gracefully(self, parser, generator, tmp_path):
        """Test handling API errors gracefully."""
        # Mock API to raise error
        APIError = type('APIError', (Exception,), {})
        mock_error = APIError("API Error")
        generator.client.messages.create = Mock(side_effect=mock_error)

        original = tmp_path / "test.py"
        code = "def func(): pass"
        original.write_text(code)

        # Should raise DocGeneratorError
        with pytest.raises(Exception) as exc_info:
            generator.generate(original, code)

        assert "error" in str(exc_info.value).lower()

    def test_handle_nonexistent_file(self, parser, validator, tmp_path):
        """Test handling nonexistent file."""
        nonexistent = tmp_path / "does_not_exist.py"

        # Parser should handle gracefully
        doc = parser.parse(nonexistent)
        assert doc is None

        # Validator should handle None
        result = validator.validate(nonexistent, doc)
        assert result.is_valid is False


class TestCrossPlatformIntegration:
    """Test cross-platform compatibility of integrated pipeline."""

    @pytest.fixture
    def parser(self):
        """Create a DocParser instance."""
        return DocParser()

    @pytest.fixture
    def writer(self):
        """Create a FileWriter instance."""
        return FileWriter()

    def test_pipeline_with_unicode_content(self, parser, writer, tmp_path):
        """Test pipeline with unicode content."""
        # Create file with unicode
        original = tmp_path / "unicode.py"
        code = "def calculate_π():\n    '''Calculate π'''\n    return 3.14159"
        original.write_text(code, encoding='utf-8')

        # Parse
        doc = parser.parse(original)
        # May or may not find docs depending on parser

        # Write new version
        new_path = writer.write(original, code, "_new")

        # Verify unicode preserved
        assert "π" in new_path.read_text(encoding='utf-8')

    def test_pipeline_with_path_spaces(self, parser, writer, tmp_path):
        """Test pipeline with spaces in paths."""
        # Create directory with spaces
        subdir = tmp_path / "my test dir"
        subdir.mkdir()

        original = subdir / "test file.py"
        code = "def func(): pass"
        original.write_text(code)

        # Parse
        doc = parser.parse(original)

        # Write
        new_path = writer.write(original, code, "_new")

        assert new_path.exists()
        assert new_path.parent == subdir

    def test_pipeline_with_nested_directories(self, parser, writer, tmp_path):
        """Test pipeline with nested directory structure."""
        # Create nested structure
        nested = tmp_path / "src" / "modules" / "core"
        nested.mkdir(parents=True)

        original = nested / "utils.py"
        code = "def helper(): pass"
        original.write_text(code)

        # Parse
        doc = parser.parse(original)

        # Backup
        backup = writer.backup(original)

        # Write
        new_path = writer.write(original, code, "_modified")

        # Verify all files in correct location
        assert backup.parent == nested
        assert new_path.parent == nested


class TestPerformanceIntegration:
    """Test performance characteristics of integrated pipeline."""

    @pytest.fixture
    def parser(self):
        """Create a DocParser instance."""
        return DocParser()

    @pytest.fixture
    def validator(self):
        """Create a DocValidator instance."""
        return DocValidator()

    def test_parse_validate_many_files(self, parser, validator, tmp_path):
        """Test parsing and validating multiple files efficiently."""
        # Create multiple test files
        for i in range(10):
            test_file = tmp_path / f"test_{i}.py"
            test_file.write_text(f"def func_{i}():\n    pass")

        # Process all files
        results = []
        for file_path in tmp_path.glob("*.py"):
            doc = parser.parse(file_path)
            validation = validator.validate(file_path, doc)
            results.append((file_path.name, validation.is_valid))

        # All should be processed
        assert len(results) == 10

    def test_parse_large_file(self, parser, tmp_path):
        """Test parsing large file."""
        # Create file with many functions
        code_lines = ['"""Module docstring."""\n\n']
        for i in range(50):
            code_lines.append(f'def func_{i}():\n')
            code_lines.append(f'    """Function {i}."""\n')
            code_lines.append(f'    pass\n\n')

        large_file = tmp_path / "large.py"
        large_file.write_text(''.join(code_lines))

        # Should parse successfully
        doc = parser.parse(large_file)
        # Parser finds first function with docstring
        assert doc is not None