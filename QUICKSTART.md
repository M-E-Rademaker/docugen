# DocuGen Quick Start Guide

This guide will help you get started with DocuGen's AI-powered documentation generation.

## Prerequisites

1. **Python 3.11+** installed
2. **Anthropic API Key** - Get one from https://console.anthropic.com/

## Setup

### 1. Install Dependencies

```bash
cd /home/vakurs006/Schreibtisch/docugen
pip install -e .
```

Or install specific dependencies:
```bash
pip install anthropic>=0.18.0 rich>=13.0.0 click>=8.1.0 pyyaml>=6.0
```

### 2. Set Your API Key

**Option A: Environment Variable (Recommended)**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Add to your `~/.bashrc` or `~/.zshrc` for persistence:
```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**Option B: Configuration File**
Create `config.yaml`:
```yaml
api_key: "your-api-key-here"
default_suffix: "__documented"
```

**Option C: Pass Directly in Code**
```python
from docugen.core.doc_generator import DocGenerator
generator = DocGenerator(api_key='your-api-key-here')
```

## Usage Examples

### Basic Usage - Generate Documentation

```python
from pathlib import Path
from docugen.core.doc_generator import DocGenerator

# Initialize
generator = DocGenerator()

# Your code to document
code = """
def calculate_total(items, tax_rate=0.08):
    subtotal = sum(item.price for item in items)
    tax = subtotal * tax_rate
    return subtotal + tax
"""

# Generate documentation
docs = generator.generate(Path("script.py"), code)
print(docs)
```

Output:
```python
"""
Calculate the total cost including tax for a list of items.

Computes the sum of all item prices and adds sales tax based on
the provided tax rate.

Parameters
----------
items : list of objects
    A list of item objects, each having a 'price' attribute.
tax_rate : float, optional
    The tax rate to apply as a decimal (e.g., 0.08 for 8%).
    Default is 0.08.

Returns
-------
float
    The total cost including tax.

Examples
--------
>>> items = [Item(price=10.0), Item(price=20.0)]
>>> calculate_total(items, tax_rate=0.1)
33.0
"""
```

### Update Existing Documentation

```python
# Existing documentation that needs improvement
existing_doc = {
    'content': '"""Calculates total."""',
    'type': 'docstring'
}

code = """
def calculate_total(items, tax_rate=0.08):
    subtotal = sum(item.price for item in items)
    tax = subtotal * tax_rate
    return subtotal + tax
"""

# Update to be standards-compliant
updated_docs = generator.update(
    file_path=Path("script.py"),
    existing_doc=existing_doc,
    code_content=code
)
print(updated_docs)
```

### SQL Documentation

```python
sql_code = """
CREATE FUNCTION calculate_discount(
    original_price DECIMAL,
    discount_percent INTEGER
)
RETURNS DECIMAL AS $$
BEGIN
    RETURN original_price * (1 - discount_percent / 100.0);
END;
$$ LANGUAGE plpgsql;
"""

docs = generator.generate(Path("function.sql"), sql_code)
print(docs)
```

Output:
```sql
-- # calculate_discount
--
-- ## Description
-- Calculates the discounted price based on original price and discount percentage.
--
-- ## Parameters
-- - `original_price` (DECIMAL): The original price before discount
-- - `discount_percent` (INTEGER): The discount percentage (0-100)
--
-- ## Returns
-- - DECIMAL: The final price after applying the discount
--
-- ## Example
-- ```sql
-- SELECT calculate_discount(100.00, 20);  -- Returns 80.00
-- ```
```

### R Documentation

```r
r_code <- """
calculate_variance <- function(x, na.rm = FALSE) {
    if (!is.numeric(x)) {
        stop("x must be numeric")
    }
    n <- length(x)
    if (n < 2) {
        return(NA)
    }
    mean_x <- mean(x, na.rm = na.rm)
    sum((x - mean_x)^2, na.rm = na.rm) / (n - 1)
}
"""

docs = generator.generate(Path("stats.r"), r_code)
print(docs)
```

Output:
```r
#' Calculate Sample Variance
#'
#' Computes the sample variance of a numeric vector using the
#' n-1 denominator. Includes NA handling and input validation.
#'
#' @param x A numeric vector for which to calculate variance.
#' @param na.rm A logical value indicating whether NA values should
#'   be removed before computation. Default is FALSE.
#' @return A numeric value representing the sample variance, or NA
#'   if the vector has fewer than 2 elements.
#' @examples
#' # Basic usage
#' calculate_variance(c(1, 2, 3, 4, 5))
#'
#' # With NA values
#' calculate_variance(c(1, 2, NA, 4, 5), na.rm = TRUE)
#' @export
```

## Error Handling

### Missing API Key

```python
from docugen.core.doc_generator import APIKeyMissingError

try:
    generator = DocGenerator()
except APIKeyMissingError as e:
    print(f"Setup Error: {e}")
    # Output: Setup Error: Anthropic API key not found. Please set...
```

### API Errors

```python
from docugen.core.doc_generator import DocGeneratorError

try:
    docs = generator.generate(file_path, code)
except DocGeneratorError as e:
    print(f"Generation Error: {e}")
```

Common errors:
- **Rate Limit**: Wait and retry
- **Connection Error**: Check internet connection
- **Invalid Code**: Check syntax of input code

## Testing Your Setup

Run the included test script:

```bash
cd /home/vakurs006/Schreibtisch/docugen
export ANTHROPIC_API_KEY='your-key'
python3 test_generator_manual.py
```

Expected output:
```
============================================================
DocGenerator Manual Test Suite
============================================================

This script tests the DocGenerator implementation.
Make sure ANTHROPIC_API_KEY is set in your environment.

============================================================
TEST 1: API Key Handling
============================================================
✓ API key found and client initialized successfully
  Using model: claude-3-5-sonnet-20241022

============================================================
TEST 2: Python Documentation Generation
============================================================

Generating documentation for Python code...
[... documentation output ...]
✓ Python documentation generated successfully

[... more tests ...]

============================================================
TEST SUMMARY
============================================================
✓ PASS: API Key Handling
✓ PASS: Python Generation
✓ PASS: SQL Generation
✓ PASS: R Generation
✓ PASS: Update Documentation

Total: 5/5 tests passed

✓ All tests passed!
```

## Configuration

### Using Config Class

```python
from pathlib import Path
from docugen.utils.config import Config
from docugen.core.doc_generator import DocGenerator

# Load from file
config = Config.from_file(Path("config.yaml"))

# Validate configuration
if config.validate():
    generator = DocGenerator(api_key=config.api_key)
else:
    print("Invalid configuration")

# Check API key status
print(config.get_api_key_status())
# Output: API key: Configured (sk-ant-a...xyz)
```

## Performance Tips

### 1. Batch Processing
Process multiple files efficiently:

```python
from pathlib import Path
from docugen.core.doc_generator import DocGenerator
from rich.progress import track

generator = DocGenerator()
files = list(Path("project/").rglob("*.py"))

for file_path in track(files, description="Documenting files..."):
    with open(file_path) as f:
        code = f.read()

    docs = generator.generate(file_path, code)
    # Write docs back to file
```

### 2. Caching Results
Avoid regenerating identical code:

```python
import hashlib
import json

cache_file = Path("doc_cache.json")
cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}

def generate_with_cache(file_path, code):
    # Create cache key from code hash
    cache_key = hashlib.sha256(code.encode()).hexdigest()

    # Check cache
    if cache_key in cache:
        return cache[cache_key]

    # Generate and cache
    docs = generator.generate(file_path, code)
    cache[cache_key] = docs
    cache_file.write_text(json.dumps(cache, indent=2))

    return docs
```

### 3. Handle Rate Limits

```python
import time
from docugen.core.doc_generator import DocGeneratorError

def generate_with_retry(generator, file_path, code, max_retries=3):
    for attempt in range(max_retries):
        try:
            return generator.generate(file_path, code)
        except DocGeneratorError as e:
            if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
```

## Integration with CLI

The DocGenerator is designed to integrate with the CLI:

```bash
# Future CLI usage (once integrated)
docugen document /path/to/project/
docugen document script.py --dry-run
docugen document --verbose
```

## Troubleshooting

### Issue: "API key not found"
**Solution**: Set ANTHROPIC_API_KEY environment variable
```bash
export ANTHROPIC_API_KEY='your-key'
```

### Issue: "Failed to connect to Anthropic API"
**Solution**: Check your internet connection and firewall settings

### Issue: "Unsupported file extension"
**Solution**: DocuGen supports .py, .sql, and .r files only

### Issue: "Rate limit exceeded"
**Solution**: Wait a moment and retry. Consider implementing exponential backoff.

### Issue: Documentation quality is poor
**Solution**:
- Ensure code is syntactically correct
- Add type hints to Python functions
- Use descriptive function/variable names
- Try regenerating (slight variations occur)

## Best Practices

1. **Review Generated Docs**: Always review AI-generated content
2. **Use Type Hints**: For Python, add type hints for better results
3. **Descriptive Names**: Use clear function/variable names
4. **Complete Code**: Provide full function definitions, not fragments
5. **Version Control**: Commit before bulk documentation changes
6. **Validate Output**: Use the validation tools to check compliance

## Cost Estimation

Claude API pricing (as of 2024):
- Input: ~$0.003 per 1K tokens
- Output: ~$0.015 per 1K tokens

Average per documentation:
- Small function: ~500 tokens in + 300 out = ~$0.006
- Large function: ~1500 tokens in + 800 out = ~$0.016

For a 100-file project:
- Estimated cost: $0.60 - $1.60

## Next Steps

1. **Integrate with CLI**: Connect to the main CLI tool
2. **Add Validation**: Validate generated docs automatically
3. **Batch Processing**: Document entire projects
4. **Custom Prompts**: Modify prompts for your team's style
5. **CI/CD Integration**: Auto-generate docs on commit

## Support

For issues or questions:
1. Check the IMPLEMENTATION_SUMMARY.md for details
2. Review PROMPT_EXAMPLES.md for prompt information
3. Run test_generator_manual.py to verify setup
4. Check API key configuration and internet connection

## Additional Resources

- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Prompt Examples**: See `PROMPT_EXAMPLES.md`
- **API Documentation**: https://docs.anthropic.com/
- **NumPy Docstring Guide**: https://numpydoc.readthedocs.io/
- **Roxygen2 Guide**: https://roxygen2.r-lib.org/
- **SQL Style Guide**: https://www.sqlstyle.guide/