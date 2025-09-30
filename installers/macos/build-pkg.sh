#!/bin/bash
# Build macOS .pkg installer for DocuGen

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"
PKG_ROOT="$BUILD_DIR/pkg-root"
SCRIPTS_DIR="$BUILD_DIR/scripts"
VERSION="1.0.0"

echo "Building DocuGen macOS Installer"
echo "================================"
echo ""

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$PKG_ROOT/usr/local/bin"
mkdir -p "$SCRIPTS_DIR"

# Copy binary
echo "Copying binary..."
cp "$PROJECT_ROOT/dist/docugen" "$PKG_ROOT/usr/local/bin/"
chmod +x "$PKG_ROOT/usr/local/bin/docugen"

# Copy postinstall script
echo "Preparing installation scripts..."
cp "$SCRIPT_DIR/postinstall.sh" "$SCRIPTS_DIR/postinstall"
chmod +x "$SCRIPTS_DIR/postinstall"

# Build the package
echo "Building package..."
pkgbuild \
    --root "$PKG_ROOT" \
    --scripts "$SCRIPTS_DIR" \
    --identifier com.docugen.app \
    --version "$VERSION" \
    --install-location / \
    "$BUILD_DIR/DocuGen-Component.pkg"

# Create distribution XML for product
cat > "$BUILD_DIR/distribution.xml" <<EOF
<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="1">
    <title>DocuGen</title>
    <organization>com.docugen</organization>
    <domains enable_localSystem="true"/>
    <options customize="never" require-scripts="true" rootVolumeOnly="true" />

    <welcome file="welcome.html" mime-type="text/html" />
    <license file="$PROJECT_ROOT/LICENSE" mime-type="text/plain" />
    <conclusion file="conclusion.html" mime-type="text/html" />

    <pkg-ref id="com.docugen.app"/>

    <options customize="never" require-scripts="false"/>

    <choices-outline>
        <line choice="default">
            <line choice="com.docugen.app"/>
        </line>
    </choices-outline>

    <choice id="default"/>

    <choice id="com.docugen.app" visible="false">
        <pkg-ref id="com.docugen.app"/>
    </choice>

    <pkg-ref id="com.docugen.app" version="$VERSION" onConclusion="none">DocuGen-Component.pkg</pkg-ref>
</installer-gui-script>
EOF

# Create welcome and conclusion HTML files
cat > "$BUILD_DIR/welcome.html" <<EOF
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
        h1 { color: #1a73e8; }
    </style>
</head>
<body>
    <h1>Welcome to DocuGen</h1>
    <p>This installer will install DocuGen v$VERSION on your system.</p>
    <p><strong>DocuGen</strong> is an AI-powered code documentation tool that automatically generates and injects documentation into your SQL, Python, and R files.</p>
    <p>This installer will:</p>
    <ul>
        <li>Install the docugen command-line tool</li>
        <li>Add docugen to your system PATH</li>
        <li>Guide you through API key configuration</li>
    </ul>
</body>
</html>
EOF

cat > "$BUILD_DIR/conclusion.html" <<EOF
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
        h1 { color: #34a853; }
        code { background-color: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>Installation Complete!</h1>
    <p>DocuGen has been successfully installed.</p>
    <p><strong>Next steps:</strong></p>
    <ol>
        <li>Restart your terminal or run: <code>source ~/.zshrc</code></li>
        <li>Run <code>docugen &lt;file&gt;</code> to start documenting your code</li>
    </ol>
    <p><strong>Examples:</strong></p>
    <ul>
        <li><code>docugen script.py</code></li>
        <li><code>docugen src/ --verbose</code></li>
        <li><code>docugen query.sql --detail-level verbose</code></li>
    </ul>
    <p>For more information, visit: <a href="https://github.com/yourusername/docugen">github.com/yourusername/docugen</a></p>
</body>
</html>
EOF

# Build the final product archive
echo "Creating product archive..."
productbuild \
    --distribution "$BUILD_DIR/distribution.xml" \
    --package-path "$BUILD_DIR" \
    --resources "$BUILD_DIR" \
    "$SCRIPT_DIR/DocuGen-v$VERSION.pkg"

echo ""
echo "✓ Package created successfully!"
echo "  Location: $SCRIPT_DIR/DocuGen-v$VERSION.pkg"
echo ""
echo "To install: double-click the .pkg file"