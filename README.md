# DocuGen CLI

<div align="center">

> 🤖 AI-Powered Code Documentation using Claude

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-163%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-82%25-brightgreen.svg)](tests/)
[![Code Style](https://img.shields.io/badge/code%20style-autopep8-blue.svg)](https://github.com/hhatto/autopep8)
[![Powered by](https://img.shields.io/badge/powered%20by-Claude%20API-blueviolet.svg)](https://www.anthropic.com/)
[![Built with](https://img.shields.io/badge/built%20with-Click-blue.svg)](https://click.palletsprojects.com/)
[![Terminal UI](https://img.shields.io/badge/terminal%20UI-Rich-orange.svg)](https://rich.readthedocs.io/)

</div>

---

A command-line tool that automatically generates high-quality documentation for SQL, Python, and R code files using Anthropic's Claude API. No more placeholder docs—DocuGen analyzes your code and creates accurate, standards-compliant documentation.

<div align="center">

### Supported Languages

![SQL](https://img.shields.io/badge/SQL-Markdown-blue?logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-NumPy-yellow?logo=python&logoColor=white)
![R](https://img.shields.io/badge/R-Roxygen2-lightblue?logo=r&logoColor=white)

</div>

## ✨ Features

- 🤖 **AI-Generated Documentation** - Real documentation powered by Claude, not templates
- 📝 **Multi-Language Support** - SQL, Python, and R
- ✅ **Validates Existing Docs** - Checks if documentation meets standards
- 🔄 **Updates & Generates** - Improves incomplete docs or creates from scratch
- 📁 **Batch Processing** - Handle single files or entire directories
- 🖥️ **Cross-Platform** - Works on Windows, Linux, and macOS
- 🎨 **Beautiful CLI** - Rich terminal output with progress indicators

## 🚀 Quick Start

### Installation

Choose your platform and download the installer:

#### Windows
1. Download `DocuGen-Setup.exe` from [Releases](https://github.com/yourusername/docugen/releases)
2. Double-click to run the installer
3. Follow the setup wizard (includes API key configuration)
4. Done! Open any command prompt and type `docugen`

#### macOS
1. Download `DocuGen.pkg` from [Releases](https://github.com/yourusername/docugen/releases)
2. Double-click to install
3. Follow the installation prompts
4. Restart your terminal
5. Type `docugen` to start

#### Linux (Debian/Ubuntu)
```bash
# Download and install the .deb package
wget https://github.com/yourusername/docugen/releases/latest/download/docugen_1.0.0_amd64.deb
sudo dpkg -i docugen_1.0.0_amd64.deb
```

#### Linux (Other Distributions)
```bash
# Download the universal installer
wget https://github.com/yourusername/docugen/releases/latest/download/docugen-linux-installer.tar.gz
tar -xzf docugen-linux-installer.tar.gz
cd docugen-linux-installer
./install.sh
```

### First Run

When you first run `docugen`, you'll be prompted to enter your Anthropic API key if you didn't configure it during installation.

Get your API key from [Anthropic Console](https://console.anthropic.com/)

### Usage

```bash
# Document a single file
docugen script.py

# Document a directory
docugen src/ --verbose

# Dry run (see what would be done)
docugen query.sql --dry-run

# Choose detail level
docugen code.py --detail-level verbose
```

## 📖 Usage Examples

### ✨ See the Magic in Action

<table>
<tr>
<td width="50%">

**Before** 😞
```python
def calculate_average(numbers):
    return sum(numbers) / len(numbers) if numbers else 0
```

</td>
<td width="50%">

**After** ✨
```python
def calculate_average(numbers):
    """
    Calculate the arithmetic mean of a list of numbers.

    Parameters
    ----------
    numbers : list of float
        A list of numerical values

    Returns
    -------
    float
        The arithmetic mean, or 0 if the list is empty

    Examples
    --------
    >>> calculate_average([1, 2, 3, 4, 5])
    3.0
    """
    return sum(numbers) / len(numbers) if numbers else 0
```

</td>
</tr>
</table>

### Basic Usage

```bash
# Document a single file
docugen my_script.py
```

Documentation is injected directly into the original file! 🎉

### Batch Processing

```bash
# Document all files in a directory
docugen ./src --verbose
```

### Options

```bash
docugen --help
```

| Option | Description |
|--------|-------------|
| `--detail-level`, `-d` | Documentation detail level: `minimal`, `concise`, or `verbose` (default: concise) |
| `--dry-run` | Preview what would be done without making changes |
| `-v, --verbose` | Show detailed progress information |
| `--api-key TEXT` | Provide API key directly (overrides config and environment) |

## 📋 Requirements

### For Users (Pre-built Installers)
- **No Python installation required!** ✨
- **Anthropic API Key** ([Get one here](https://console.anthropic.com/))
- Windows 10+, macOS 10.15+, or any modern Linux distribution

### For Developers
- **Python 3.11.0+**
- **Dependencies:** `click`, `anthropic`, `rich`, `pyyaml`
- **Build tools:** `pyinstaller` (for building standalone executables)

## 📚 Documentation Standards

DocuGen generates documentation following industry standards:

| Language | Standard | Format |
|----------|----------|--------|
| **Python** | NumPy/SciPy | Triple-quoted docstrings with sections |
| **SQL** | Markdown | Comment blocks with `--` prefix |
| **R** | Roxygen2 | `#'` comments with `@tags` |

### Python (NumPy Style)
```python
"""
Short description.

Parameters
----------
param : type
    Description

Returns
-------
type
    Description

Examples
--------
>>> example()
result
"""
```

### SQL (Markdown Style)
```sql
-- # Function Name
-- ## Description
-- Brief description
-- ## Parameters
-- - param1: description
-- ## Returns
-- Return description
-- ## Example
-- SELECT example();
```

### R (Roxygen2)
```r
#' Function Title
#'
#' Function description
#'
#' @param param_name Parameter description
#' @return Return value description
#' @examples
#' example_code()
#' @export
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/docugen.git
cd docugen

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install with dev dependencies
pip install -e ".[dev]"
```

### Building Standalone Executables

```bash
# Install PyInstaller
pip install pyinstaller

# Build for your platform
pyinstaller docugen.spec

# Binary will be in dist/docugen (or dist/docugen.exe on Windows)
```

### Building Platform Installers

#### Windows Installer (NSIS)
```bash
# Install NSIS from https://nsis.sourceforge.io/
# Then run:
makensis installers/windows/installer.nsi
```

#### macOS Package
```bash
cd installers/macos
./build-pkg.sh
```

#### Linux Debian Package
```bash
cd installers/linux
./build-deb.sh
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=docugen --cov-report=html

# Run specific tests
pytest tests/test_doc_generator.py -v
```

**Test Coverage:** 82% overall (163 tests, all passing ✓)

### Code Style

```bash
# Format code with autopep8
autopep8 --in-place --recursive docugen/

# Check with flake8
flake8 docugen/

# Type check with mypy
mypy docugen/
```

## 🏗️ Architecture

```
Input → Discovery → Parser → Validator → Generator → Writer → Output
                                              ↓
                                        Claude API
```

**Core Modules:**
- `file_discovery.py` - Finds supported files (.sql, .py, .r)
- `doc_parser.py` - Extracts existing documentation
- `doc_validator.py` - Validates against standards
- `doc_generator.py` - Generates docs using Claude API
- `file_writer.py` - Safely writes modified files

See [docs/architecture.md](docs/architecture.md) for detailed design.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run tests: `pytest tests/`
5. Format code: `autopep8 --in-place --recursive docugen/`
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## ⚠️ Important Notes

- **API Costs**: Each file processed makes a Claude API call. Monitor usage in [Anthropic Console](https://console.anthropic.com/)
- **In-File Documentation**: Documentation is injected directly into your source files. Consider using version control (git) before processing
- **Network Required**: Requires internet connection for Claude API
- **Rate Limits**: Respects Anthropic API rate limits
- **No Dependencies**: Pre-built installers require no Python or dependencies—just install and use!

## 🐛 Troubleshooting

### "API Key Required" Error

If you didn't configure your API key during installation:

**Option 1: Interactive setup**
```bash
# Just run docugen and follow the prompts
docugen
```

**Option 2: Environment variable**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

**Option 3: Manual config file**
Create `~/.docugen/config.json` (Linux/macOS) or `%APPDATA%\DocuGen\config.json` (Windows):
```json
{
  "anthropic_api_key": "your-api-key-here"
}
```

### "No supported files found"

DocuGen only processes `.sql`, `.py`, and `.r` files. Check file extensions.

### "Rate limit exceeded"

Wait a moment and try again. Consider processing files in smaller batches.

### Tests Failing

```bash
# Reinstall dependencies
pip install -e ".[dev]"

# Clear cache
pytest --cache-clear
```

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [Anthropic Claude](https://www.anthropic.com/)
- CLI powered by [Click](https://click.palletsprojects.com/)
- Terminal UI by [Rich](https://rich.readthedocs.io/)

---

**Made with ❤️ and Claude**