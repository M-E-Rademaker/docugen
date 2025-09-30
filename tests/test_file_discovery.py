"""
Tests for file discovery module.
"""

import pytest
from pathlib import Path
from docugen.core.file_discovery import FileDiscovery


def test_discover_single_file(tmp_path):
    """Test discovering a single file."""
    test_file = tmp_path / "test.py"
    test_file.write_text("# test")

    discovery = FileDiscovery()
    files = discovery.discover(test_file)

    assert len(files) == 1
    assert files[0] == test_file


def test_discover_directory(tmp_path):
    """Test discovering files in directory."""
    (tmp_path / "test1.py").write_text("# test1")
    (tmp_path / "test2.sql").write_text("-- test2")
    (tmp_path / "ignore.txt").write_text("ignore")

    discovery = FileDiscovery()
    files = discovery.discover(tmp_path)

    assert len(files) == 2


def test_filter_unsupported_extensions(tmp_path):
    """Test filtering of unsupported file types."""
    (tmp_path / "test.py").write_text("# test")
    (tmp_path / "test.txt").write_text("ignore")

    discovery = FileDiscovery()
    files = discovery.discover(tmp_path)

    assert len(files) == 1
    assert files[0].suffix == '.py'