# Documentation Generation Prompts

This document shows the exact prompts used by DocGenerator to generate documentation for each supported language.

## SQL Prompt (Markdown-style Documentation)

```
You are a technical documentation expert specializing in SQL.

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

Return ONLY the documentation comments (starting with --), ready to be inserted directly before the code.
```

### Example SQL Output

For this code:
```sql
CREATE OR REPLACE FUNCTION get_user_orders(user_id INTEGER)
RETURNS TABLE(order_id INTEGER, order_date DATE, total DECIMAL) AS $$
BEGIN
    RETURN QUERY
    SELECT id, created_at, total_amount
    FROM orders
    WHERE customer_id = user_id
    ORDER BY created_at DESC;
END;
$$ LANGUAGE plpgsql;
```

Expected documentation:
```sql
-- # get_user_orders
--
-- ## Description
-- Retrieves all orders for a specific user, returning order details sorted by creation date in descending order.
--
-- ## Parameters
-- - `user_id` (INTEGER): The unique identifier of the customer whose orders to retrieve
--
-- ## Returns
-- - TABLE: A result set containing order information with columns:
--   - order_id (INTEGER): Unique identifier for the order
--   - order_date (DATE): Date when the order was created
--   - total (DECIMAL): Total amount of the order
--
-- ## Example
-- ```sql
-- SELECT * FROM get_user_orders(12345);
-- ```
```

## Python Prompt (NumPy-style Docstrings)

```
You are a technical documentation expert specializing in Python.

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

Return ONLY the docstring content (the text between the triple quotes, including proper formatting), ready to be placed as a function/class docstring.
```

### Example Python Output

For this code:
```python
def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count if count > 0 else 0
```

Expected documentation:
```python
"""
Calculate the arithmetic mean of a list of numbers.

Takes a sequence of numeric values and computes their average.
Returns 0 if the input list is empty to avoid division by zero.

Parameters
----------
numbers : list or tuple of int or float
    A sequence of numeric values to average. Can be empty.

Returns
-------
float
    The arithmetic mean of the input numbers. Returns 0.0 if the
    input is empty.

Examples
--------
>>> calculate_average([1, 2, 3, 4, 5])
3.0
>>> calculate_average([])
0
>>> calculate_average([10.5, 20.5])
15.5
"""
```

## R Prompt (Roxygen2 Documentation)

```
You are a technical documentation expert specializing in R.

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

Return ONLY the Roxygen2 comments (starting with #'), ready to be inserted directly before the function definition.
```

### Example R Output

For this code:
```r
calculate_mean <- function(x, na.rm = TRUE) {
    if (!is.numeric(x)) {
        stop("Input must be numeric")
    }
    sum(x, na.rm = na.rm) / length(x[!is.na(x)])
}
```

Expected documentation:
```r
#' Calculate Arithmetic Mean
#'
#' Computes the arithmetic mean of a numeric vector with optional
#' NA value handling. Validates that input is numeric before calculation.
#'
#' @param x A numeric vector. Required to be of type numeric or integer.
#' @param na.rm A logical value indicating whether NA values should be
#'   removed before computation. Default is TRUE.
#' @return A numeric value representing the arithmetic mean of the input
#'   vector. Returns NaN if the vector is empty after removing NA values.
#' @examples
#' # Basic usage
#' calculate_mean(c(1, 2, 3, 4, 5))
#'
#' # With NA values
#' calculate_mean(c(1, 2, NA, 4, 5), na.rm = TRUE)
#'
#' # Error handling
#' \dontrun{
#' calculate_mean(c("a", "b", "c"))  # Throws error
#' }
#' @export
```

## Prompt Engineering Decisions

### Temperature Setting: 0.2

We use a low temperature (0.2) to ensure:
- Consistent output format
- Predictable structure
- Less creative deviation from standards
- Reliable parsing of generated documentation

### Max Tokens: 4096

Allows for:
- Comprehensive documentation with examples
- Multi-parameter functions
- Detailed descriptions
- Multiple code examples

### Model: Claude 3.5 Sonnet

Selected for:
- Strong instruction following
- Excellent code understanding
- High quality technical writing
- Good balance of speed and quality

## Update Prompt Structure

When updating existing documentation, we use a modified prompt:

```
You are a technical documentation expert.

TASK: Fix and improve the existing documentation to meet the required standards.

EXISTING DOCUMENTATION:
{existing_content}

CODE BEING DOCUMENTED:
{code_content}

REQUIREMENTS:
{language_specific_requirements}

INSTRUCTIONS:
1. Review the existing documentation
2. Fix any issues with format, structure, or accuracy
3. Ensure it matches the required standard exactly
4. Keep good parts of the existing documentation
5. Add missing sections (parameters, returns, examples, etc.)
6. Make sure examples are realistic and correct

Return ONLY the corrected documentation, properly formatted and ready to use.
```

This update prompt:
- Preserves good existing content
- Fixes formatting issues
- Adds missing sections
- Ensures standards compliance
- Maintains author's intent where possible

## Tips for Optimal Results

1. **Provide Complete Code Context**: Include the full function/query definition
2. **Include Type Hints**: For Python, type hints help generate better docs
3. **Clear Function Names**: Descriptive names lead to better descriptions
4. **Review Generated Docs**: Always review before committing
5. **Iterate if Needed**: Can regenerate or update if first result isn't perfect

## Customization

To customize prompts, edit the methods in `DocGenerator`:
- `_get_sql_prompt()` - SQL documentation format
- `_get_python_prompt()` - Python docstring format
- `_get_r_prompt()` - R Roxygen2 format

Changes take effect immediately without recompilation.