# Agent Instructions for DocuGen

## Global Context

This is a CLI tool that uses Claude API to generate real, high-quality documentation for SQL, Python, and R code files based on language-specific standards.

**Key Requirements:**
- Python 3.11.0
- Use autopep8 for code style
- Cross-platform (PowerShell + Bash)
- Real AI-generated docs (not placeholders)
- User-friendly error handling

## Agent-Specific Instructions

### doc-generator-agent

**Your Mission:**
Implement the core AI documentation generation engine using Anthropic's Claude API.

**Key Tasks:**
1. Implement `DocGenerator` class in `doc_generator.py`:
   - Initialize Anthropic client with API key from env or config
   - Implement `generate()` method for new documentation
   - Implement `update()` method for fixing existing docs

2. Create effective prompts for each language:
   - SQL: Markdown-style comments
   - Python: NumPy/SciPy docstrings
   - R: Roxygen2 format

3. Handle API concerns:
   - Check for API key, show friendly error if missing
   - Handle rate limits gracefully
   - Show progress indicators (use rich library)
   - Catch and explain API errors to user

**Quality Standards:**
- Generated docs must be accurate to the code
- Must follow language standards exactly
- Handle edge cases (complex functions, missing context)

**Example Prompt Structure:**
```
You are a documentation expert. Generate [LANGUAGE] documentation for this code.

CODE:
[insert code here]

REQUIREMENTS:
- Format: [NumPy/Roxygen2/Markdown]
- Include: description, parameters, returns, examples
- Be accurate and concise

OUTPUT:
[only the documentation, no explanations]
```

---

### testing-agent

**Your Mission:**
Create comprehensive tests ensuring DocuGen works correctly on Windows and Linux.

**Key Tasks:**
1. Write unit tests for each module:
   - `test_file_discovery.py` (expand existing)
   - `test_doc_parser.py` (parsing logic)
   - `test_doc_validator.py` (validation rules)
   - `test_doc_generator.py` (mock API calls)
   - `test_file_writer.py` (safe file operations)

2. Create integration tests:
   - End-to-end pipeline tests
   - Test with real fixture files
   - Test error handling

3. Cross-platform testing:
   - Use `pytest` with platform markers
   - Test path handling (Windows vs Unix)
   - Test CLI on both PowerShell and Bash

**Fixture Files Needed:**
- `sample.py` with incomplete docs
- `sample.sql` with no docs
- `sample.r` with malformed docs
- Complex multi-function files

---

### standards-validator-agent

**Your Mission:**
Implement parsing and validation logic for documentation standards.

**Key Tasks:**
1. Implement `DocParser` class:
   - Parse Python docstrings (NumPy format)
   - Parse SQL markdown comments
   - Parse R Roxygen2 comments
   - Return structured dict of parsed docs

2. Implement `DocValidator` class:
   - Validate against language standards
   - Return ValidationResult with specific issues
   - Check for required sections (params, returns, etc.)

3. Define validation rules:
   - SQL: Must have Description, Parameters, Returns, Example
   - Python: Must follow NumPy format (sections, indentation)
   - R: Must have Roxygen2 tags (@param, @return, @export)

**Edge Cases:**
- Missing sections
- Wrong format/indentation
- Multiple functions in one file
- Nested functions (Python)

## Common Guidelines for All Agents

1. **Code Style**: Use autopep8, follow PEP 8
2. **Error Handling**: Clear, user-friendly messages
3. **Testing**: Write tests for your code
4. **Documentation**: Add docstrings to your functions (NumPy style)
5. **Cross-platform**: Test paths and commands work on Windows + Linux
6. **Dependencies**: Only use packages in requirements.txt

## Communication Protocol

When an agent completes work:
1. Summarize what was implemented
2. List any new files created/modified
3. Note any blockers or decisions needed
4. Suggest next steps