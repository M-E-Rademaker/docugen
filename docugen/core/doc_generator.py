"""
Documentation generator module - creates compliant documentation.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


class DocGeneratorError(Exception):
    """Base exception for documentation generator errors."""
    pass


class APIKeyMissingError(DocGeneratorError):
    """Raised when API key is not provided or found."""
    pass


class DocGenerator:
    """
    Generates documentation using LLM (Claude).

    This class interfaces with Anthropic's Claude API to generate
    standards-compliant documentation for SQL, Python, and R code files.

    Parameters
    ----------
    api_key : str, optional
        Anthropic API key. If not provided, will attempt to read from
        ANTHROPIC_API_KEY environment variable.

    Raises
    ------
    APIKeyMissingError
        If no API key is provided and ANTHROPIC_API_KEY env var is not set.

    Examples
    --------
    >>> generator = DocGenerator()
    >>> docs = generator.generate(Path("script.py"), code_content)
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize generator with Claude API.

        Parameters
        ----------
        api_key : str, optional
            Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.

        Raises
        ------
        APIKeyMissingError
            If no API key is available.
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        if not self.api_key:
            raise APIKeyMissingError(
                "Anthropic API key not found. Please set the ANTHROPIC_API_KEY "
                "environment variable or pass api_key parameter.\n\n"
                "Example: export ANTHROPIC_API_KEY='your-api-key-here'"
            )

        try:
            self.client = Anthropic(api_key=self.api_key)
        except Exception as e:
            raise DocGeneratorError(f"Failed to initialize Anthropic client: {e}")

        self.console = Console()
        self.model = "claude-3-5-sonnet-20241022"

        # Language-specific prompt templates
        self._prompts = {
            'sql': self._get_sql_prompt(),
            'python': self._get_python_prompt(),
            'r': self._get_r_prompt()
        }

    def _get_file_language(self, file_path: Path) -> str:
        """
        Determine language from file extension.

        Parameters
        ----------
        file_path : Path
            Path to the file.

        Returns
        -------
        str
            Language identifier ('sql', 'python', or 'r').

        Raises
        ------
        DocGeneratorError
            If file extension is not supported.
        """
        suffix = file_path.suffix.lower()
        mapping = {
            '.sql': 'sql',
            '.py': 'python',
            '.r': 'r'
        }

        if suffix not in mapping:
            raise DocGeneratorError(
                f"Unsupported file extension: {suffix}. "
                f"Supported: {', '.join(mapping.keys())}"
            )

        return mapping[suffix]

    def _get_sql_prompt(self) -> str:
        """
        Get prompt template for SQL documentation generation.

        Returns
        -------
        str
            Prompt template for SQL markdown-style comments.
        """
        return """You are a technical documentation expert specializing in SQL.

Generate comprehensive, markdown-style documentation comments for the SQL code provided.

REQUIREMENTS:
1. Use SQL comment syntax (-- for each line)
2. Follow this exact structure:
   -- # [Function/Query Name]
   --
   -- ## Description
   -- [Clear, concise description of what the query/function does]
   --
   -- ## Parameters
   -- - `parameter_name` (TYPE): Description of parameter
   --
   -- ## Returns
   -- - TYPE: Description of return value/result set
   --
   -- ## Example
   -- ```sql
   -- [Usage example]
   -- ```

3. Be accurate and specific about:
   - What the query does
   - Input parameters and their types
   - Return types and structure
   - Any side effects (INSERT, UPDATE, DELETE operations)

4. Use professional, clear language
5. Include a realistic usage example
6. Keep descriptions concise but complete

CODE TO DOCUMENT:
{code}

Return ONLY the documentation comments (starting with --), ready to be inserted directly before the code."""

    def _get_python_prompt(self) -> str:
        """
        Get prompt template for Python documentation generation.

        Returns
        -------
        str
            Prompt template for NumPy-style docstrings.
        """
        return '''You are a technical documentation expert specializing in Python.

Generate comprehensive NumPy/SciPy-style docstrings for the Python code provided.

REQUIREMENTS:
1. Use triple-quoted docstring format
2. Follow NumPy docstring standard exactly:
   """
   Short one-line description.

   Extended description (if needed) explaining the function's purpose,
   behavior, and any important details.

   Parameters
   ----------
   param_name : type
       Description of parameter. Use 4-space indentation for
       continuation lines.
   another_param : type, optional
       Description. Include 'optional' for optional parameters.

   Returns
   -------
   return_type
       Description of return value. Be specific about type and structure.

   Raises
   ------
   ExceptionType
       When and why this exception is raised.

   Examples
   --------
   >>> function_name(arg1, arg2)
   expected_output
   """

3. Be accurate about:
   - Parameter types (use proper type hints syntax)
   - Return types
   - Exceptions that can be raised
   - Default values for optional parameters

4. Include realistic, runnable examples
5. Use proper indentation (4 spaces)
6. Keep examples concise but illustrative

CODE TO DOCUMENT:
{code}

Return ONLY the docstring content (the text between the triple quotes, including proper formatting), ready to be placed as a function/class docstring.'''

    def _get_r_prompt(self) -> str:
        """
        Get prompt template for R documentation generation.

        Returns
        -------
        str
            Prompt template for Roxygen2-style documentation.
        """
        return """You are a technical documentation expert specializing in R.

Generate comprehensive Roxygen2 documentation for the R code provided.

REQUIREMENTS:
1. Use Roxygen2 comment syntax (#' for each line)
2. Follow this exact structure:
   #' Short title (one line)
   #'
   #' Detailed description explaining what the function does,
   #' its purpose, and any important behavior.
   #'
   #' @param param_name Description of parameter. Type information should
   #'   be included in the description. Use proper indentation for
   #'   continuation lines (2 spaces).
   #' @param another_param Description of another parameter.
   #' @return Description of return value, including type and structure.
   #' @examples
   #' # Example usage
   #' result <- function_name(arg1, arg2)
   #' print(result)
   #' @export

3. Be accurate about:
   - Parameter types and expected values
   - Return value type and structure
   - When to use @export (exported functions only)

4. Include realistic, executable examples
5. Use clear, concise descriptions
6. Follow R community conventions

CODE TO DOCUMENT:
{code}

Return ONLY the Roxygen2 comments (starting with #'), ready to be inserted directly before the function definition."""

    def generate(self, file_path: Path, code_content: str) -> str:
        """
        Generate documentation for code file.

        Parameters
        ----------
        file_path : Path
            Path to the file being documented.
        code_content : str
            Content of the code file.

        Returns
        -------
        str
            Generated documentation in appropriate format for the language.

        Raises
        ------
        DocGeneratorError
            If documentation generation fails or file type is unsupported.
        APIError
            If Claude API returns an error.
        RateLimitError
            If API rate limit is exceeded.
        """
        language = self._get_file_language(file_path)
        prompt_template = self._prompts[language]
        prompt = prompt_template.format(code=code_content)

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True
            ) as progress:
                progress.add_task(
                    description=f"Generating {language.upper()} documentation...",
                    total=None
                )

                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=0.2,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )

            # Extract text content from response
            documentation = message.content[0].text

            return documentation.strip()

        except RateLimitError as e:
            raise DocGeneratorError(
                f"API rate limit exceeded. Please wait and try again.\n"
                f"Details: {e}"
            )
        except APIConnectionError as e:
            raise DocGeneratorError(
                f"Failed to connect to Anthropic API. Check your internet connection.\n"
                f"Details: {e}"
            )
        except APIError as e:
            raise DocGeneratorError(
                f"API error occurred: {e}"
            )
        except Exception as e:
            raise DocGeneratorError(
                f"Unexpected error during documentation generation: {e}"
            )

    def update(self, file_path: Path, existing_doc: Dict[str, Any],
               code_content: str) -> str:
        """
        Update existing documentation to be compliant.

        This method takes existing documentation and improves it to match
        the standards for the file's language (SQL markdown, Python NumPy,
        or R Roxygen2).

        Parameters
        ----------
        file_path : Path
            Path to the file being documented.
        existing_doc : Dict[str, Any]
            Existing parsed documentation structure. Should contain keys
            like 'content', 'type', etc.
        code_content : str
            Content of the code file.

        Returns
        -------
        str
            Updated documentation in appropriate format for the language.

        Raises
        ------
        DocGeneratorError
            If documentation update fails or file type is unsupported.
        APIError
            If Claude API returns an error.
        RateLimitError
            If API rate limit is exceeded.
        """
        language = self._get_file_language(file_path)
        base_prompt = self._prompts[language]

        # Extract existing doc content
        existing_content = existing_doc.get('content', '')

        # Create an update-specific prompt
        update_prompt = f"""You are a technical documentation expert.

TASK: Fix and improve the existing documentation to meet the required standards.

EXISTING DOCUMENTATION:
{existing_content}

CODE BEING DOCUMENTED:
{code_content}

REQUIREMENTS:
{base_prompt.split('REQUIREMENTS:')[1].split('CODE TO DOCUMENT:')[0]}

INSTRUCTIONS:
1. Review the existing documentation
2. Fix any issues with format, structure, or accuracy
3. Ensure it matches the required standard exactly
4. Keep good parts of the existing documentation
5. Add missing sections (parameters, returns, examples, etc.)
6. Make sure examples are realistic and correct

Return ONLY the corrected documentation, properly formatted and ready to use."""

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True
            ) as progress:
                progress.add_task(
                    description=f"Updating {language.upper()} documentation...",
                    total=None
                )

                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=0.2,
                    messages=[{
                        "role": "user",
                        "content": update_prompt
                    }]
                )

            # Extract text content from response
            documentation = message.content[0].text

            return documentation.strip()

        except RateLimitError as e:
            raise DocGeneratorError(
                f"API rate limit exceeded. Please wait and try again.\n"
                f"Details: {e}"
            )
        except APIConnectionError as e:
            raise DocGeneratorError(
                f"Failed to connect to Anthropic API. Check your internet connection.\n"
                f"Details: {e}"
            )
        except APIError as e:
            raise DocGeneratorError(
                f"API error occurred: {e}"
            )
        except Exception as e:
            raise DocGeneratorError(
                f"Unexpected error during documentation update: {e}"
            )