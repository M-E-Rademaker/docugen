"""
Documentation generator module - creates compliant documentation.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from docugen.utils.config import DetailLevel


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

    def _get_sql_prompt(self, detail_level: DetailLevel = DetailLevel.CONCISE) -> str:
        """
        Get prompt template for SQL documentation generation.

        Parameters
        ----------
        detail_level : DetailLevel
            Level of documentation detail (minimal, concise, or verbose).

        Returns
        -------
        str
            Prompt template for SQL markdown-style comments.
        """
        if detail_level == DetailLevel.MINIMAL:
            return """You are a technical documentation expert specializing in SQL.

Generate MINIMAL, brief documentation comments for the SQL code provided.

REQUIREMENTS:
1. Use SQL comment syntax (-- for each line)
2. Follow this structure:
   -- # [Function/Query Name]
   -- [One-line description of what it does]
   -- Parameters: [param1 (TYPE), param2 (TYPE)]
   -- Returns: [TYPE - brief description]

3. Keep it EXTREMELY brief - 2-4 lines maximum
4. Focus only on essential information
5. NO examples, NO extended descriptions

CODE TO DOCUMENT:
{code}

Return ONLY the minimal documentation comments (starting with --), ready to be inserted directly before the code."""

        elif detail_level == DetailLevel.VERBOSE:
            return """You are a technical documentation expert specializing in SQL.

Generate COMPREHENSIVE, detailed documentation comments for the SQL code provided.

REQUIREMENTS:
1. Use SQL comment syntax (-- for each line)
2. Follow this exact structure:
   -- # [Function/Query Name]
   --
   -- ## Description
   -- [Detailed, thorough description of what the query/function does]
   -- [Include purpose, use cases, and important behavior notes]
   --
   -- ## Parameters
   -- - `parameter_name` (TYPE): Detailed description of parameter,
   --   including constraints, expected values, and default behavior
   --
   -- ## Returns
   -- - TYPE: Detailed description of return value/result set,
   --   including structure, possible values, and edge cases
   --
   -- ## Side Effects
   -- - List any INSERT, UPDATE, DELETE operations
   -- - Note any transaction requirements
   --
   -- ## Performance Considerations
   -- - Index usage, query complexity notes
   --
   -- ## Examples
   -- ```sql
   -- -- Example 1: Basic usage
   -- [Usage example with output]
   --
   -- -- Example 2: Edge case
   -- [Another example]
   -- ```
   --
   -- ## Notes
   -- - Additional important information
   -- - Edge cases and gotchas

3. Be thorough and detailed about:
   - What the query does and why
   - All input parameters and their types
   - Return types and structure
   - Side effects and performance notes
   - Multiple realistic examples

4. Use professional, clear language
5. Include 2-3 realistic usage examples
6. Explain edge cases and important details

CODE TO DOCUMENT:
{code}

Return ONLY the comprehensive documentation comments (starting with --), ready to be inserted directly before the code."""

        else:  # CONCISE (default)
            return """You are a technical documentation expert specializing in SQL.

Generate concise, balanced documentation comments for the SQL code provided.

CRITICAL REQUIREMENTS:
1. Return ONLY the SQL comment lines (starting with --)
2. Do NOT include ANY explanatory text, summaries, or meta-commentary
3. Do NOT say things like "Here are the comments" or "I have documented..."
4. Just return the raw comment lines ready to be inserted

COMMENT FORMAT:
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

ACCURACY REQUIREMENTS:
- What the query does
- Input parameters and their types
- Return types and structure
- Any side effects (INSERT, UPDATE, DELETE operations)
- Use professional, clear language
- Include a realistic usage example
- Keep descriptions concise but complete

CODE TO DOCUMENT:
{code}

Return ONLY the documentation comments (starting with --), ready to be inserted directly before the code."""

    def _get_python_prompt(self, detail_level: DetailLevel = DetailLevel.CONCISE) -> str:
        """
        Get prompt template for Python documentation generation.

        Parameters
        ----------
        detail_level : DetailLevel
            Level of documentation detail (minimal, concise, or verbose).

        Returns
        -------
        str
            Prompt template for NumPy-style docstrings.
        """
        if detail_level == DetailLevel.MINIMAL:
            return '''You are a technical documentation expert specializing in Python.

Generate MINIMAL, brief docstrings for the Python code provided.

REQUIREMENTS:
1. Use triple-quoted docstring format
2. Keep it to 1-3 lines maximum:
   """
   Brief description of what the function does.
   """

3. NO parameter lists, NO return type details, NO examples
4. Just the essential purpose in one sentence
5. Be accurate but extremely concise

CODE TO DOCUMENT:
{code}

Return ONLY the minimal docstring content (the text between the triple quotes), ready to be placed as a function/class docstring.'''

        elif detail_level == DetailLevel.VERBOSE:
            return '''You are a technical documentation expert specializing in Python.

Generate COMPREHENSIVE, detailed NumPy/SciPy-style docstrings for the Python code provided.

REQUIREMENTS:
1. Use triple-quoted docstring format
2. Follow NumPy docstring standard with ALL sections:
   """
   Short one-line description.

   Detailed extended description explaining the function's purpose,
   behavior, implementation details, and any important notes.
   Include algorithm details, complexity notes, and usage guidance.

   Parameters
   ----------
   param_name : type
       Comprehensive description of parameter, including valid values,
       constraints, default behavior, and any special considerations.
       Use 4-space indentation for continuation lines.
   another_param : type, optional
       Detailed description. Include 'optional' and explain default.

   Returns
   -------
   return_type
       Detailed description of return value. Specify exact type,
       structure, possible values, and edge cases.

   Raises
   ------
   ExceptionType
       Detailed explanation of when and why this exception is raised,
       including specific conditions and error handling guidance.
   AnotherException
       Description of another possible exception.

   See Also
   --------
   related_function : Brief description of relationship.

   Notes
   -----
   Additional important information, algorithm details, complexity,
   edge cases, gotchas, and implementation considerations.

   Examples
   --------
   >>> # Example 1: Basic usage
   >>> result = function_name(arg1, arg2)
   >>> print(result)
   expected_output

   >>> # Example 2: Edge case
   >>> result = function_name(special_arg)
   >>> print(result)
   special_output

   >>> # Example 3: Error handling
   >>> try:
   ...     function_name(invalid_arg)
   ... except ValueError as e:
   ...     print(e)
   error_message
   """

3. Be thorough and detailed about:
   - Parameter types with exact type hints
   - All return types and structures
   - All possible exceptions
   - Multiple realistic, executable examples (3+)
   - Algorithm and complexity notes
   - Edge cases and gotchas

4. Include 3+ realistic, runnable examples covering different scenarios
5. Use proper indentation (4 spaces)
6. Explain edge cases and error conditions

CODE TO DOCUMENT:
{code}

Return ONLY the comprehensive docstring content (the text between the triple quotes, including proper formatting), ready to be placed as a function/class docstring.'''

        else:  # CONCISE (default)
            return '''You are a technical documentation expert specializing in Python.

Generate concise, balanced NumPy/SciPy-style docstrings for the Python code provided.

CRITICAL REQUIREMENTS:
1. Return ONLY the docstring content text (what goes between the triple quotes)
2. Do NOT include the triple quotes themselves
3. Do NOT include ANY explanatory text, summaries, or meta-commentary
4. Do NOT say things like "Here is the documentation" or "I have documented..."
5. Just return the raw docstring text ready to be inserted

DOCSTRING FORMAT:
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

ACCURACY REQUIREMENTS:
- Parameter types (use proper type hints syntax)
- Return types
- Exceptions that can be raised
- Default values for optional parameters
- Include realistic, runnable examples
- Use proper indentation (4 spaces)

CODE TO DOCUMENT:
{code}

Return ONLY the docstring text content (without triple quotes), ready to be placed inside triple quotes as a function/class docstring.'''

    def _get_r_prompt(self, detail_level: DetailLevel = DetailLevel.CONCISE) -> str:
        """
        Get prompt template for R documentation generation.

        Parameters
        ----------
        detail_level : DetailLevel
            Level of documentation detail (minimal, concise, or verbose).

        Returns
        -------
        str
            Prompt template for Roxygen2-style documentation.
        """
        if detail_level == DetailLevel.MINIMAL:
            return """You are a technical documentation expert specializing in R.

Generate MINIMAL, brief Roxygen2 documentation for the R code provided.

REQUIREMENTS:
1. Use Roxygen2 comment syntax (#' for each line)
2. Keep it to 2-3 lines maximum:
   #' Brief one-line description of function
   #' @export

3. NO parameter descriptions, NO return details, NO examples
4. Just the essential purpose and @export if applicable
5. Be accurate but extremely concise

CODE TO DOCUMENT:
{code}

Return ONLY the minimal Roxygen2 comments (starting with #'), ready to be inserted directly before the function definition."""

        elif detail_level == DetailLevel.VERBOSE:
            return """You are a technical documentation expert specializing in R.

Generate COMPREHENSIVE, detailed Roxygen2 documentation for the R code provided.

REQUIREMENTS:
1. Use Roxygen2 comment syntax (#' for each line)
2. Follow this detailed structure:
   #' Short title (one line)
   #'
   #' Comprehensive detailed description explaining what the function does,
   #' its purpose, use cases, algorithm details, and any important behavior.
   #' Include implementation notes, complexity considerations, and usage guidance.
   #'
   #' @param param_name Detailed description of parameter including type,
   #'   valid values, constraints, default behavior, and any special
   #'   considerations. Use proper indentation for continuation lines (2 spaces).
   #' @param another_param Comprehensive description of another parameter.
   #' @return Detailed description of return value, including exact type,
   #'   structure, possible values, edge cases, and any important notes about
   #'   the return behavior.
   #' @details
   #' Additional comprehensive details about the implementation, algorithm,
   #' complexity, performance considerations, and important usage notes.
   #' @section Performance:
   #' Notes about performance characteristics and complexity.
   #' @section Edge Cases:
   #' Description of edge cases and special behavior.
   #' @examples
   #' # Example 1: Basic usage
   #' result <- function_name(arg1, arg2)
   #' print(result)
   #'
   #' # Example 2: Advanced usage with edge case
   #' result2 <- function_name(special_arg)
   #' print(result2)
   #'
   #' # Example 3: Error handling
   #' tryCatch(
   #'   function_name(invalid_arg),
   #'   error = function(e) print(e)
   #' )
   #' @seealso \\code{\\link{related_function}} for related functionality.
   #' @export

3. Be thorough and detailed about:
   - Parameter types, constraints, and valid values
   - Return value type, structure, and edge cases
   - Implementation details and complexity
   - Multiple realistic, executable examples (3+)
   - Edge cases and gotchas
   - When to use @export

4. Include 3+ realistic, executable examples covering different scenarios
5. Use clear, comprehensive descriptions
6. Follow R community conventions and best practices

CODE TO DOCUMENT:
{code}

Return ONLY the comprehensive Roxygen2 comments (starting with #'), ready to be inserted directly before the function definition."""

        else:  # CONCISE (default)
            return """You are a technical documentation expert specializing in R.

Generate concise, balanced Roxygen2 documentation for the R code provided.

CRITICAL REQUIREMENTS:
1. Return ONLY the Roxygen2 comment lines (starting with #')
2. Do NOT include ANY explanatory text, summaries, or meta-commentary
3. Do NOT say things like "Here is the documentation" or "I have documented..."
4. Just return the raw Roxygen2 comment lines ready to be inserted

ROXYGEN2 FORMAT:
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

ACCURACY REQUIREMENTS:
- Parameter types and expected values
- Return value type and structure
- When to use @export (exported functions only)
- Include realistic, executable examples
- Use clear, concise descriptions
- Follow R community conventions

CODE TO DOCUMENT:
{code}

Return ONLY the Roxygen2 comments (starting with #'), ready to be inserted directly before the function definition."""

    def generate(self, file_path: Path, code_content: str,
                 detail_level: DetailLevel = DetailLevel.CONCISE) -> str:
        """
        Generate documentation for code file.

        Parameters
        ----------
        file_path : Path
            Path to the file being documented.
        code_content : str
            Content of the code file.
        detail_level : DetailLevel, optional
            Level of documentation detail (minimal, concise, or verbose).
            Default is CONCISE.

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

        # Get the appropriate prompt for language and detail level
        if language == 'sql':
            prompt_template = self._get_sql_prompt(detail_level)
        elif language == 'python':
            prompt_template = self._get_python_prompt(detail_level)
        else:  # r
            prompt_template = self._get_r_prompt(detail_level)

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
               code_content: str, detail_level: DetailLevel = DetailLevel.CONCISE) -> str:
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
        detail_level : DetailLevel, optional
            Level of documentation detail (minimal, concise, or verbose).
            Default is CONCISE.

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

        # Get the appropriate prompt for language and detail level
        if language == 'sql':
            base_prompt = self._get_sql_prompt(detail_level)
        elif language == 'python':
            base_prompt = self._get_python_prompt(detail_level)
        else:  # r
            base_prompt = self._get_r_prompt(detail_level)

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