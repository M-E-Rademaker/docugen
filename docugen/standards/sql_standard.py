"""
SQL documentation standard - Markdown-style.
"""


SQL_TEMPLATE = """
-- # {function_name}
--
-- ## Description
-- {description}
--
-- ## Parameters
-- {parameters}
--
-- ## Returns
-- {returns}
--
-- ## Example
-- {example}
"""


class SQLStandard:
    """SQL markdown-style documentation standard."""

    @staticmethod
    def get_template() -> str:
        """Get SQL documentation template."""
        return SQL_TEMPLATE

    @staticmethod
    def validate_structure(doc: str) -> bool:
        """
        Validate SQL documentation structure.

        Parameters
        ----------
        doc : str
            The documentation string to validate

        Returns
        -------
        bool
            True if documentation follows SQL markdown standard, False otherwise
        """
        if not doc or not isinstance(doc, str):
            return False

        # Check for required markdown headers
        required_sections = [
            '-- #',  # Function/query name header
            '-- ## Description',
            '-- ## Parameters',
            '-- ## Returns',
            '-- ## Example'
        ]

        doc_lower = doc.lower()
        for section in required_sections:
            if section.lower() not in doc_lower:
                return False

        return True