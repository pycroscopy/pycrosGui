#!/bin/bash
# Quick pycrosGUI Setup for Current User
# This script installs pycrosGUI for the current user

set -e

echo "================================================"
echo "pycrosGUI User Installation"
echo "================================================"

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Detect Python executable
if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
else
    echo "❌ Error: Python 3 not found!"
    exit 1
fi

echo "Using Python: $($PYTHON --version)"
echo ""

# Step 1: Install dependencies
echo "Step 1: Installing dependencies..."
$PYTHON -m pip install --upgrade pip

# Step 2: Install pycrosGUI in editable mode
echo ""
echo "Step 2: Installing pycrosGUI..."
$PYTHON -m pip install -e "$SCRIPT_DIR"

# Step 3: Verify installation
echo ""
echo "Step 3: Verifying installation..."
$PYTHON -c "import pycrosGUI; print(f'✅ pycrosGUI {pycrosGUI.__version__} installed successfully!')"

# Create user-local bin if it doesn't exist
USER_BIN="$HOME/.local/bin"
if [ ! -d "$USER_BIN" ]; then
    mkdir -p "$USER_BIN"
fi

# Create a wrapper script in user's local bin
WRAPPER="$USER_BIN/pycrosGUI"
cat > "$WRAPPER" << 'WRAPPER_EOF'
#!/bin/bash
# pycrosGUI Launcher
# Auto-configures Qt environment and launches the application

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS: Set Qt plugin path
    export QT_QPA_PLATFORM_PLUGIN_PATH=$(python3 -c "import PyQt5; import os; print(os.path.dirname(PyQt5.__file__) + '/Qt/plugins')" 2>/dev/null)
fi

# Run pycrosGUI
python3 -m pycrosGUI.main "$@"
WRAPPER_EOF

chmod +x "$WRAPPER"

echo ""
echo "================================================"
echo "✅ Installation Complete!"
echo "================================================"
echo ""

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" == *":$USER_BIN:"* ]]; then
    echo "✅ $USER_BIN is in your PATH"
    echo ""
    echo "You can now run pycrosGUI from anywhere:"
    echo "  pycrosGUI"
else
    echo "⚠️  $USER_BIN is NOT in your PATH"
    echo ""
    echo "Add this line to your ~/.zshrc or ~/.bash_profile:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "Then reload your shell:"
    echo "  source ~/.zshrc"
    echo ""
    echo "Or run directly with:"
    echo "  $WRAPPER"
fi

echo ""
echo "To run pycrosGUI:"
echo "  pycrosGUI"
echo ""
echo "With a data file:"
echo "  pycrosGUI /path/to/data.h5"
echo ""
