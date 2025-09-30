# Architecture

## Overview

DocuGen follows a pipeline architecture with distinct phases:

1. **Discovery**: Find files to process
2. **Parsing**: Extract existing documentation
3. **Validation**: Check compliance with standards
4. **Generation**: Create or update documentation
5. **Writing**: Save modified files

## Components

### File Discovery
- Traverses directories
- Filters by file extension
- Returns list of valid files

### Doc Parser
- Language-specific parsing
- Extracts structured documentation
- Handles missing documentation

### Doc Validator
- Checks against language standards
- Returns validation results
- Identifies specific issues

### Doc Generator
- Uses Claude API for generation
- Maintains language-specific formats
- Handles both new and updated docs

### File Writer
- Safe file operations
- Adds suffix to filename
- Optional backup creation

## Data Flow

```
Input Path → Discovery → [Files]
                           ↓
                    For each file:
                           ↓
    Read Content ← Parser → [Existing Docs?]
         ↓                        ↓
    Validator              [Compliant?]
         ↓                        ↓
    Generator ← [Generate/Update] → New Docs
         ↓
    File Writer → Modified File
```

## Extension Points

- Add new language support in `standards/`
- Custom templates in `templates/`
- Pluggable LLM backends