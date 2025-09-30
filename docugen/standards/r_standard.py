"""
R documentation standard - Roxygen2.
"""


R_TEMPLATE = """
#' {title}
#'
#' {description}
#'
#' @param {param_name} {param_description}
#' @return {return_description}
#' @examples
#' {examples}
#' @export
"""


class RStandard:
    """Roxygen2 documentation standard."""

    @staticmethod
    def get_template() -> str:
        """Get R documentation template."""
        return R_TEMPLATE

    @staticmethod
    def validate_structure(doc: str) -> bool:
        """
        Validate Roxygen2 documentation structure.

        Parameters
        ----------
        doc : str
            The documentation string to validate

        Returns
        -------
        bool
            True if documentation follows Roxygen2 standard, False otherwise
        """
        if not doc or not isinstance(doc, str):
            return False

        # Check for required Roxygen2 tags
        required_tags = [
            "#'",  # Roxygen2 comment marker
            "@param",
            "@return"
        ]

        for tag in required_tags:
            if tag not in doc:
                return False

        # Check that each line with content starts with #'
        lines = doc.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#'"):
                return False

        return True