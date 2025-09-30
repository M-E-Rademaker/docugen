#!/bin/bash
# Build Debian/Ubuntu .deb package for DocuGen

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_DIR="$SCRIPT_DIR/build-deb"
VERSION="1.0.0"
PACKAGE_NAME="docugen"

echo "Building DocuGen Debian Package"
echo "==============================="
echo ""

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/local/bin"
mkdir -p "$BUILD_DIR/usr/share/doc/$PACKAGE_NAME"

# Copy binary
echo "Copying binary..."
cp "$PROJECT_ROOT/dist/docugen" "$BUILD_DIR/usr/local/bin/"
chmod +x "$BUILD_DIR/usr/local/bin/docugen"

# Create control file
cat > "$BUILD_DIR/DEBIAN/control" <<EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Maintainer: DocuGen Team <support@docugen.dev>
Description: AI-Powered Code Documentation Tool
 DocuGen automatically generates and injects documentation into SQL, Python,
 and R code files using Anthropic's Claude AI.
 .
 Features:
  - In-file documentation injection
  - Multiple detail levels (minimal, concise, verbose)
  - Support for SQL, Python, and R
  - Validates existing documentation
Homepage: https://github.com/yourusername/docugen
EOF

# Create postinst script
cat > "$BUILD_DIR/DEBIAN/postinst" <<'EOF'
#!/bin/bash
set -e

CONFIG_DIR="$HOME/.docugen"
CONFIG_FILE="$CONFIG_DIR/config.json"

# Only run interactive setup if not installing via dpkg (which runs as root)
if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then
    # Get the actual user's home directory
    ACTUAL_HOME=$(eval echo ~$SUDO_USER)
    CONFIG_DIR="$ACTUAL_HOME/.docugen"
    CONFIG_FILE="$CONFIG_DIR/config.json"

    # Run as the actual user
    sudo -u "$SUDO_USER" bash <<'USERSCRIPT'
    CONFIG_DIR="$HOME/.docugen"
    CONFIG_FILE="$CONFIG_DIR/config.json"

    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║   DocuGen - API Key Configuration     ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    echo "DocuGen requires an Anthropic API key to generate documentation."
    echo "Get your API key from: https://console.anthropic.com/"
    echo ""
    read -p "Do you want to configure your API key now? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        read -s -p "Enter your Anthropic API key: " API_KEY
        echo ""

        if [ -n "$API_KEY" ]; then
            mkdir -p "$CONFIG_DIR"
            cat > "$CONFIG_FILE" <<CONFIGEOF
{
  "anthropic_api_key": "$API_KEY"
}
CONFIGEOF
            chmod 600 "$CONFIG_FILE"
            echo "✓ API key saved"
        fi
    else
        echo ""
        echo "You can configure your API key later by:"
        echo "  1. Setting ANTHROPIC_API_KEY environment variable"
        echo "  2. Running 'docugen' and following first-run setup"
    fi
USERSCRIPT
fi

echo ""
echo "DocuGen installed successfully!"
echo "Usage: docugen <file> [options]"
echo ""

exit 0
EOF

chmod +x "$BUILD_DIR/DEBIAN/postinst"

# Create prerm script
cat > "$BUILD_DIR/DEBIAN/prerm" <<'EOF'
#!/bin/bash
exit 0
EOF

chmod +x "$BUILD_DIR/DEBIAN/prerm"

# Create postrm script
cat > "$BUILD_DIR/DEBIAN/postrm" <<'EOF'
#!/bin/bash
set -e

if [ "$1" = "purge" ]; then
    # Remove configuration directory on purge
    if [ -d "$HOME/.docugen" ]; then
        echo "Removing DocuGen configuration..."
        rm -rf "$HOME/.docugen"
    fi
fi

exit 0
EOF

chmod +x "$BUILD_DIR/DEBIAN/postrm"

# Copy documentation
if [ -f "$PROJECT_ROOT/LICENSE" ]; then
    cp "$PROJECT_ROOT/LICENSE" "$BUILD_DIR/usr/share/doc/$PACKAGE_NAME/copyright"
fi

if [ -f "$PROJECT_ROOT/README.md" ]; then
    cp "$PROJECT_ROOT/README.md" "$BUILD_DIR/usr/share/doc/$PACKAGE_NAME/"
fi

# Create changelog
cat > "$BUILD_DIR/usr/share/doc/$PACKAGE_NAME/changelog" <<EOF
$PACKAGE_NAME ($VERSION) stable; urgency=low

  * Initial release
  * In-file documentation injection
  * Support for SQL, Python, and R
  * Multiple detail levels

 -- DocuGen Team <support@docugen.dev>  $(date -R)
EOF

gzip -9 "$BUILD_DIR/usr/share/doc/$PACKAGE_NAME/changelog"

# Build the package
echo "Building .deb package..."
dpkg-deb --build "$BUILD_DIR" "$SCRIPT_DIR/${PACKAGE_NAME}_${VERSION}_amd64.deb"

echo ""
echo "✓ Package created successfully!"
echo "  Location: $SCRIPT_DIR/${PACKAGE_NAME}_${VERSION}_amd64.deb"
echo ""
echo "To install:"
echo "  sudo dpkg -i ${PACKAGE_NAME}_${VERSION}_amd64.deb"
echo "  sudo apt-get install -f  # To install dependencies if needed"