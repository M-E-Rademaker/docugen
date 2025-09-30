"""
Comprehensive tests for file writer module.
"""

import pytest
from pathlib import Path
from docugen.core.file_writer import FileWriter


class TestFileWriterWrite:
    """Test suite for file writing functionality."""

    @pytest.fixture
    def writer(self):
        """Create a FileWriter instance."""
        return FileWriter()

    def test_write_creates_file(self, writer, tmp_path):
        """Test that write creates a new file."""
        original = tmp_path / "test.py"
        original.write_text("original content")

        content = "modified content"
        new_path = writer.write(original, content, "_modified")

        assert new_path.exists()
        assert new_path.read_text() == "modified content"

    def test_write_adds_suffix(self, writer, tmp_path):
        """Test that write adds suffix to filename."""
        original = tmp_path / "test.py"
        original.write_text("original")

        new_path = writer.write(original, "new content", "_modified")

        assert new_path.name == "test_modified.py"
        assert new_path.parent == original.parent

    def test_write_preserves_extension(self, writer, tmp_path):
        """Test that write preserves file extension."""
        original = tmp_path / "script.sql"
        original.write_text("SELECT 1;")

        new_path = writer.write(original, "SELECT 2;", "_new")

        assert new_path.suffix == ".sql"
        assert new_path.name == "script_new.sql"

    def test_write_returns_path(self, writer, tmp_path):
        """Test that write returns the path to new file."""
        original = tmp_path / "test.py"
        original.write_text("original")

        result = writer.write(original, "new", "_suffix")

        assert isinstance(result, Path)
        assert result.exists()

    def test_write_overwrites_existing(self, writer, tmp_path):
        """Test that write overwrites existing file with same name."""
        original = tmp_path / "test.py"
        original.write_text("original")

        # Create file with target name
        target = tmp_path / "test_modified.py"
        target.write_text("old modified")

        # Write should overwrite
        new_path = writer.write(original, "new modified", "_modified")

        assert new_path.read_text() == "new modified"

    def test_write_with_empty_content(self, writer, tmp_path):
        """Test writing empty content."""
        original = tmp_path / "test.py"
        original.write_text("original")

        new_path = writer.write(original, "", "_empty")

        assert new_path.exists()
        assert new_path.read_text() == ""

    def test_write_with_unicode_content(self, writer, tmp_path):
        """Test writing unicode content."""
        original = tmp_path / "test.py"
        original.write_text("original")

        content = "def calculate_pi():\n    '''Calculate pi value'''\n    return 3.14159"
        new_path = writer.write(original, content, "_unicode")

        assert new_path.exists()
        assert "pi" in new_path.read_text()

    def test_write_preserves_newlines(self, writer, tmp_path):
        """Test that write preserves newline characters."""
        original = tmp_path / "test.py"
        original.write_text("original")

        content = "line1\nline2\nline3"
        new_path = writer.write(original, content, "_newlines")

        assert new_path.read_text() == content

    def test_write_multiple_files_same_directory(self, writer, tmp_path):
        """Test writing multiple files in same directory."""
        file1 = tmp_path / "test1.py"
        file2 = tmp_path / "test2.py"
        file1.write_text("content1")
        file2.write_text("content2")

        path1 = writer.write(file1, "modified1", "_new")
        path2 = writer.write(file2, "modified2", "_new")

        assert path1.exists()
        assert path2.exists()
        assert path1.name == "test1_new.py"
        assert path2.name == "test2_new.py"

    def test_write_different_suffixes(self, writer, tmp_path):
        """Test writing same file with different suffixes."""
        original = tmp_path / "test.py"
        original.write_text("original")

        path1 = writer.write(original, "version1", "_v1")
        path2 = writer.write(original, "version2", "_v2")

        assert path1.name == "test_v1.py"
        assert path2.name == "test_v2.py"
        assert path1.read_text() == "version1"
        assert path2.read_text() == "version2"

    def test_write_with_complex_suffix(self, writer, tmp_path):
        """Test writing with complex suffix."""
        original = tmp_path / "test.py"
        original.write_text("original")

        new_path = writer.write(original, "content", "_documented_2024")

        assert new_path.name == "test_documented_2024.py"

    def test_write_sql_file(self, writer, tmp_path):
        """Test writing SQL file."""
        original = tmp_path / "query.sql"
        original.write_text("SELECT 1;")

        content = "-- Documentation\nSELECT 1;"
        new_path = writer.write(original, content, "_documented")

        assert new_path.suffix == ".sql"
        assert new_path.read_text() == content

    def test_write_r_file(self, writer, tmp_path):
        """Test writing R file."""
        original = tmp_path / "script.r"
        original.write_text("func <- function() {}")

        content = "#' Documentation\nfunc <- function() {}"
        new_path = writer.write(original, content, "_documented")

        assert new_path.suffix == ".r"
        assert new_path.read_text() == content

    def test_write_file_in_subdirectory(self, writer, tmp_path):
        """Test writing file that's in a subdirectory."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        original = subdir / "test.py"
        original.write_text("original")

        new_path = writer.write(original, "modified", "_new")

        assert new_path.parent == subdir
        assert new_path.name == "test_new.py"

    def test_write_long_content(self, writer, tmp_path):
        """Test writing long content."""
        original = tmp_path / "test.py"
        original.write_text("original")

        # Create long content
        content = "# Header\n" + ("line\n" * 1000)
        new_path = writer.write(original, content, "_long")

        assert new_path.read_text() == content


class TestFileWriterBackup:
    """Test suite for backup functionality."""

    @pytest.fixture
    def writer(self):
        """Create a FileWriter instance."""
        return FileWriter()

    def test_backup_creates_file(self, writer, tmp_path):
        """Test that backup creates a backup file."""
        original = tmp_path / "test.py"
        original.write_text("original content")

        backup_path = writer.backup(original)

        assert backup_path.exists()
        assert backup_path.read_text() == "original content"

    def test_backup_adds_extension(self, writer, tmp_path):
        """Test that backup adds .backup extension."""
        original = tmp_path / "test.py"
        original.write_text("content")

        backup_path = writer.backup(original)

        assert backup_path.name == "test.py.backup"

    def test_backup_preserves_content(self, writer, tmp_path):
        """Test that backup preserves exact content."""
        original = tmp_path / "test.py"
        content = "def func():\n    '''Docstring'''\n    pass"
        original.write_text(content)

        backup_path = writer.backup(original)

        assert backup_path.read_text() == content

    def test_backup_returns_path(self, writer, tmp_path):
        """Test that backup returns the path to backup file."""
        original = tmp_path / "test.py"
        original.write_text("content")

        result = writer.backup(original)

        assert isinstance(result, Path)
        assert result.exists()

    def test_backup_overwrites_existing(self, writer, tmp_path):
        """Test that backup overwrites existing backup."""
        original = tmp_path / "test.py"
        original.write_text("new content")

        # Create old backup
        old_backup = tmp_path / "test.py.backup"
        old_backup.write_text("old backup")

        backup_path = writer.backup(original)

        assert backup_path.read_text() == "new content"

    def test_backup_with_unicode(self, writer, tmp_path):
        """Test backup preserves unicode content."""
        original = tmp_path / "test.py"
        content = "def �():\n    return 3.14159"
        original.write_text(content)

        backup_path = writer.backup(original)

        assert "�" in backup_path.read_text()

    def test_backup_binary_content(self, writer, tmp_path):
        """Test backup preserves binary content."""
        original = tmp_path / "test.py"
        # Write some special characters
        original.write_bytes(b"content\x00\x01\x02")

        backup_path = writer.backup(original)

        assert backup_path.read_bytes() == b"content\x00\x01\x02"

    def test_backup_empty_file(self, writer, tmp_path):
        """Test backup of empty file."""
        original = tmp_path / "test.py"
        original.write_text("")

        backup_path = writer.backup(original)

        assert backup_path.exists()
        assert backup_path.read_text() == ""

    def test_backup_multiple_files(self, writer, tmp_path):
        """Test backing up multiple files."""
        file1 = tmp_path / "test1.py"
        file2 = tmp_path / "test2.py"
        file1.write_text("content1")
        file2.write_text("content2")

        backup1 = writer.backup(file1)
        backup2 = writer.backup(file2)

        assert backup1.name == "test1.py.backup"
        assert backup2.name == "test2.py.backup"
        assert backup1.read_text() == "content1"
        assert backup2.read_text() == "content2"

    def test_backup_file_in_subdirectory(self, writer, tmp_path):
        """Test backup of file in subdirectory."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        original = subdir / "test.py"
        original.write_text("content")

        backup_path = writer.backup(original)

        assert backup_path.parent == subdir
        assert backup_path.name == "test.py.backup"

    def test_backup_different_file_types(self, writer, tmp_path):
        """Test backup of different file types."""
        py_file = tmp_path / "script.py"
        sql_file = tmp_path / "query.sql"
        r_file = tmp_path / "analysis.r"

        py_file.write_text("python")
        sql_file.write_text("sql")
        r_file.write_text("r")

        py_backup = writer.backup(py_file)
        sql_backup = writer.backup(sql_file)
        r_backup = writer.backup(r_file)

        assert py_backup.name == "script.py.backup"
        assert sql_backup.name == "query.sql.backup"
        assert r_backup.name == "analysis.r.backup"


class TestFileWriterCrossPlatform:
    """Test suite for cross-platform compatibility."""

    @pytest.fixture
    def writer(self):
        """Create a FileWriter instance."""
        return FileWriter()

    def test_write_with_pathlib_path(self, writer, tmp_path):
        """Test write works with pathlib Path objects."""
        original = Path(tmp_path) / "test.py"
        original.write_text("original")

        new_path = writer.write(original, "modified", "_new")

        assert isinstance(new_path, Path)
        assert new_path.exists()

    def test_backup_with_pathlib_path(self, writer, tmp_path):
        """Test backup works with pathlib Path objects."""
        original = Path(tmp_path) / "test.py"
        original.write_text("original")

        backup_path = writer.backup(original)

        assert isinstance(backup_path, Path)
        assert backup_path.exists()

    def test_write_preserves_utf8_encoding(self, writer, tmp_path):
        """Test that write uses UTF-8 encoding."""
        original = tmp_path / "test.py"
        original.write_text("original")

        content = "# -���\ndef func():\n    '''$C=:F8O'''\n    pass"
        new_path = writer.write(original, content, "_utf8")

        # Read back and verify encoding
        assert new_path.read_text(encoding='utf-8') == content

    def test_write_handles_long_paths(self, writer, tmp_path):
        """Test write handles reasonably long paths."""
        # Create nested directories
        deep_dir = tmp_path / "a" / "b" / "c" / "d" / "e"
        deep_dir.mkdir(parents=True)

        original = deep_dir / "test.py"
        original.write_text("original")

        new_path = writer.write(original, "modified", "_new")

        assert new_path.exists()
        assert new_path.read_text() == "modified"

    def test_write_with_spaces_in_path(self, writer, tmp_path):
        """Test write handles paths with spaces."""
        subdir = tmp_path / "my test dir"
        subdir.mkdir()

        original = subdir / "test file.py"
        original.write_text("original")

        new_path = writer.write(original, "modified", "_new")

        assert new_path.exists()
        assert new_path.name == "test file_new.py"

    def test_write_with_special_chars_in_filename(self, writer, tmp_path):
        """Test write handles filenames with special characters."""
        # Use safe special characters that work on all platforms
        original = tmp_path / "test-file_v1.py"
        original.write_text("original")

        new_path = writer.write(original, "modified", "_new")

        assert new_path.exists()
        assert new_path.name == "test-file_v1_new.py"


class TestFileWriterErrorHandling:
    """Test suite for error handling."""

    @pytest.fixture
    def writer(self):
        """Create a FileWriter instance."""
        return FileWriter()

    def test_write_to_readonly_directory(self, writer, tmp_path):
        """Test write to read-only directory raises error."""
        import os
        import sys

        # Skip on Windows as permission model is different
        if sys.platform == 'win32':
            pytest.skip("Permission test not applicable on Windows")

        original = tmp_path / "test.py"
        original.write_text("original")

        # Make directory read-only
        os.chmod(tmp_path, 0o444)

        try:
            with pytest.raises(PermissionError):
                writer.write(original, "modified", "_new")
        finally:
            # Restore permissions for cleanup
            os.chmod(tmp_path, 0o755)

    def test_backup_nonexistent_file(self, writer, tmp_path):
        """Test backup of nonexistent file raises error."""
        nonexistent = tmp_path / "does_not_exist.py"

        with pytest.raises(FileNotFoundError):
            writer.backup(nonexistent)

    def test_write_original_does_not_need_to_exist(self, writer, tmp_path):
        """Test that write can work even if original doesn't exist."""
        # This tests the current implementation which doesn't check
        # if original exists - it just uses it for naming
        original = tmp_path / "test.py"
        # Don't create original file

        new_path = writer.write(original, "content", "_new")

        # Should still create the new file
        assert new_path.exists()
        assert new_path.read_text() == "content"


class TestFileWriterIntegration:
    """Integration tests for file writer."""

    @pytest.fixture
    def writer(self):
        """Create a FileWriter instance."""
        return FileWriter()

    def test_backup_then_write(self, writer, tmp_path):
        """Test backing up then writing modified file."""
        original = tmp_path / "test.py"
        original.write_text("original content")

        # Backup first
        backup_path = writer.backup(original)

        # Then modify and write
        new_path = writer.write(original, "modified content", "_modified")

        assert backup_path.read_text() == "original content"
        assert new_path.read_text() == "modified content"
        assert original.read_text() == "original content"  # Original unchanged

    def test_multiple_write_operations(self, writer, tmp_path):
        """Test multiple write operations on same file."""
        original = tmp_path / "test.py"
        original.write_text("original")

        path1 = writer.write(original, "version1", "_v1")
        path2 = writer.write(original, "version2", "_v2")
        path3 = writer.write(original, "version3", "_v3")

        assert path1.read_text() == "version1"
        assert path2.read_text() == "version2"
        assert path3.read_text() == "version3"

    def test_write_then_backup_new_file(self, writer, tmp_path):
        """Test writing new file then backing it up."""
        original = tmp_path / "test.py"
        original.write_text("original")

        new_path = writer.write(original, "modified", "_new")
        backup_of_new = writer.backup(new_path)

        assert backup_of_new.read_text() == "modified"
        assert backup_of_new.name == "test_new.py.backup"