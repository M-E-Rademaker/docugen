#!/bin/bash
# DocuGen Linux Installation Script
# Universal installer for all Linux distributions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/usr/local/bin"
CONFIG_DIR="$HOME/.docugen"
CONFIG_FILE="$CONFIG_DIR/config.json"
BINARY_URL="https://github.com/yourusername/docugen/releases/latest/download/docugen-linux"
VERSION="1.0.0"

# Check if running as root for system-wide install
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Warning: Running as root. Installing system-wide.${NC}"
    USER_INSTALL=false
else
    USER_INSTALL=true
    INSTALL_DIR="$HOME/.local/bin"
fi

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   DocuGen Linux Installer v$VERSION    ║"
echo "║   AI-Powered Code Documentation        ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Check if already installed
if [ -f "$INSTALL_DIR/docugen" ]; then
    echo -e "${YELLOW}DocuGen is already installed at $INSTALL_DIR/docugen${NC}"
    read -p "Do you want to reinstall/update? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

# Create installation directory if it doesn't exist
echo -e "${BLUE}[1/5] Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"

# Download or copy binary
echo -e "${BLUE}[2/5] Installing docugen binary...${NC}"
if [ -f "$(dirname "$0")/../../dist/docugen" ]; then
    # Local installation (from built binary)
    echo "  Installing from local build..."
    cp "$(dirname "$0")/../../dist/docugen" "$INSTALL_DIR/docugen"
elif [ -f "$(dirname "$0")/docugen" ]; then
    # Installation from release package
    echo "  Installing from release package..."
    cp "$(dirname "$0")/docugen" "$INSTALL_DIR/docugen"
else
    echo -e "${RED}Error: Binary not found. Please build the project first with PyInstaller.${NC}"
    exit 1
fi

chmod +x "$INSTALL_DIR/docugen"
echo -e "${GREEN}  ✓ Binary installed to $INSTALL_DIR/docugen${NC}"

# Add to PATH
echo -e "${BLUE}[3/5] Configuring PATH...${NC}"
add_to_path() {
    local profile_file="$1"
    local profile_name="$2"

    if [ -f "$profile_file" ]; then
        if ! grep -q "$INSTALL_DIR" "$profile_file" 2>/dev/null; then
            echo "" >> "$profile_file"
            echo "# Added by DocuGen installer" >> "$profile_file"
            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$profile_file"
            echo -e "${GREEN}  ✓ Added to $profile_name${NC}"
            return 0
        else
            echo -e "  ✓ Already in $profile_name"
            return 1
        fi
    fi
    return 1
}

PATH_UPDATED=false
add_to_path "$HOME/.bashrc" ".bashrc" && PATH_UPDATED=true
add_to_path "$HOME/.bash_profile" ".bash_profile" && PATH_UPDATED=true
add_to_path "$HOME/.zshrc" ".zshrc" && PATH_UPDATED=true
add_to_path "$HOME/.profile" ".profile" && PATH_UPDATED=true

if [ "$PATH_UPDATED" = false ]; then
    echo -e "${YELLOW}  ⚠ PATH already configured${NC}"
fi

# Ensure PATH is available in current session
export PATH="$INSTALL_DIR:$PATH"

# API Key Configuration
echo -e "${BLUE}[4/5] Configuring API key...${NC}"
echo ""
echo "DocuGen requires an Anthropic API key to generate documentation."
echo -e "Get your API key from: ${BLUE}https://console.anthropic.com/${NC}"
echo ""

read -p "Do you want to configure your API key now? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    read -s -p "Enter your Anthropic API key: " API_KEY
    echo ""

    if [ -n "$API_KEY" ]; then
        # Create config directory
        mkdir -p "$CONFIG_DIR"

        # Write config file
        cat > "$CONFIG_FILE" <<EOF
{
  "anthropic_api_key": "$API_KEY"
}
EOF

        # Set restrictive permissions
        chmod 600 "$CONFIG_FILE"

        echo -e "${GREEN}  ✓ API key saved to $CONFIG_FILE${NC}"
    else
        echo -e "${YELLOW}  ⚠ No API key provided${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠ API key configuration skipped${NC}"
    echo ""
    echo "You can configure your API key later by either:"
    echo "  1. Setting the ANTHROPIC_API_KEY environment variable:"
    echo "     export ANTHROPIC_API_KEY='your-api-key-here'"
    echo "  2. Running 'docugen' and following the first-run setup"
fi

# Verify installation
echo ""
echo -e "${BLUE}[5/5] Verifying installation...${NC}"
if command -v docugen &> /dev/null; then
    VERSION_OUTPUT=$($INSTALL_DIR/docugen --help | head -n 1 || echo "unknown")
    echo -e "${GREEN}  ✓ DocuGen is installed and accessible${NC}"
else
    echo -e "${YELLOW}  ⚠ DocuGen installed but not in PATH for this session${NC}"
    echo "  Please restart your terminal or run: source ~/.bashrc"
fi

# Installation complete
echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════╗"
echo "║   Installation Complete!               ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "Usage: docugen <file-or-directory> [options]"
echo ""
echo "Examples:"
echo "  docugen script.py"
echo "  docugen src/ --verbose"
echo "  docugen query.sql --detail-level verbose"
echo ""
if [ "$PATH_UPDATED" = true ]; then
    echo -e "${YELLOW}Note: You may need to restart your terminal or run:${NC}"
    echo "  source ~/.bashrc"
    echo ""
fi
echo "For help: docugen --help"
echo "Documentation: https://github.com/yourusername/docugen"
echo ""