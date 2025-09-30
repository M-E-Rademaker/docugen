"""
Python documentation standard - NumPy/SciPy-style docstrings.
"""


PYTHON_TEMPLATE = '''
"""
{short_description}

{long_description}

Parameters
----------
{parameters}

Returns
-------
{returns}

Examples
--------
{examples}
"""
'''


class PythonStandard:
    """NumPy/SciPy-style docstring standard."""

    @staticmethod
    def get_template() -> str:
        """Get Python documentation template."""
        return PYTHON_TEMPLATE

    @staticmethod
    def validate_structure(doc: str) -> bool:
        """
        Validate Python docstring structure.

        Parameters
        ----------
        doc : str
            The documentation string to validate

        Returns
        -------
        bool
            True if documentation follows NumPy docstring standard, False otherwise
        """
        if not doc or not isinstance(doc, str):
            return False

        # Check that docstring is enclosed in triple quotes
        if not (doc.strip().startswith('"""') or doc.strip().startswith("'''")):
            return False

        # Check for required NumPy sections
        required_sections = [
            'Parameters',
            '----------',
            'Returns',
            '-------'
        ]

        for section in required_sections:
            if section not in doc:
                return False

        return True