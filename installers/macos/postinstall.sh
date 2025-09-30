#!/bin/bash
# DocuGen macOS Post-Installation Script
# This script runs after the package installation to configure PATH and API key

set -e

INSTALL_DIR="/usr/local/bin"
CONFIG_DIR="$HOME/.docugen"
CONFIG_FILE="$CONFIG_DIR/config.json"

echo "DocuGen Post-Installation Setup"
echo "================================"
echo ""

# Ensure the binary is executable
chmod +x "$INSTALL_DIR/docugen"

# Add to PATH in shell profiles if not already present
add_to_path() {
    local profile_file="$1"
    local profile_name="$2"

    if [ -f "$profile_file" ]; then
        if ! grep -q "$INSTALL_DIR" "$profile_file"; then
            echo "" >> "$profile_file"
            echo "# Added by DocuGen installer" >> "$profile_file"
            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$profile_file"
            echo "✓ Added to $profile_name"
        else
            echo "✓ Already in $profile_name"
        fi
    fi
}

echo "Configuring shell PATH..."
add_to_path "$HOME/.bash_profile" ".bash_profile"
add_to_path "$HOME/.bashrc" ".bashrc"
add_to_path "$HOME/.zshrc" ".zshrc"
add_to_path "$HOME/.profile" ".profile"
echo ""

# API Key Configuration
echo "API Key Configuration"
echo "--------------------"
echo ""
echo "DocuGen requires an Anthropic API key to generate documentation."
echo "Get your API key from: https://console.anthropic.com/"
echo ""

# Use osascript to show a dialog for API key input
API_KEY=$(osascript -e 'text returned of (display dialog "Enter your Anthropic API key (or leave empty to configure later):" default answer "" with title "DocuGen API Key Setup" buttons {"Skip", "Save"} default button "Save" with hidden answer)' 2>/dev/null || echo "")

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

    echo "✓ API key saved to $CONFIG_FILE"
    echo ""
    echo "Installation complete!"
else
    echo "⚠ API key setup skipped."
    echo ""
    echo "You can configure your API key later by either:"
    echo "  1. Setting the ANTHROPIC_API_KEY environment variable:"
    echo "     export ANTHROPIC_API_KEY='your-api-key-here'"
    echo "  2. Running 'docugen' and following the first-run setup"
    echo ""
fi

echo ""
echo "================================================"
echo "DocuGen is now installed!"
echo "================================================"
echo ""
echo "Usage: docugen <file-or-directory> [options]"
echo ""
echo "Examples:"
echo "  docugen script.py"
echo "  docugen src/ --verbose"
echo "  docugen query.sql --detail-level verbose"
echo ""
echo "Note: You may need to restart your terminal or run:"
echo "  source ~/.zshrc   (or your shell's profile)"
echo ""

exit 0