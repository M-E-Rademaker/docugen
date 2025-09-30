"""
File writer module - safely writes modified files.
"""

from pathlib import Path


class FileWriter:
    """Handles safe file writing operations."""

    def write(self, original_path: Path, content: str, suffix: str) -> Path:
        """
        Write modified file with suffix.

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

    def backup(self, file_path: Path) -> Path:
        """Create backup of original file."""
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        backup_path.write_bytes(file_path.read_bytes())
        return backup_path