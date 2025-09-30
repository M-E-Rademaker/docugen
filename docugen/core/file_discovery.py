"""
File discovery module - finds valid files to process.
"""

from pathlib import Path
from typing import List


class FileDiscovery:
    """Discovers and filters files for documentation."""

    SUPPORTED_EXTENSIONS = {'.sql', '.py', '.r'}

    def discover(self, path: Path) -> List[Path]:
        """
        Discover all supported files in path.

        Parameters
        ----------
        path : Path
            File or directory path to search

        Returns
        -------
        List[Path]
            List of valid file paths
        """
        if path.is_file():
            return [path] if self._is_valid_file(path) else []

        return [
            f for f in path.rglob('*')
            if f.is_file() and self._is_valid_file(f)
        ]

    def _is_valid_file(self, file_path: Path) -> bool:
        """Check if file has supported extension."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS