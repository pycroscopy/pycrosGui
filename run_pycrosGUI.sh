#!/bin/bash
# pycrosGUI launcher script for macOS
# This script ensures Qt platform plugins are properly configured

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Determine Python executable - support both local venv and system-wide installation
if [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
else
    PYTHON_BIN="python3"
fi

# Set QT_QPA_PLATFORM_PLUGIN_PATH for macOS
export QT_QPA_PLATFORM_PLUGIN_PATH=$($PYTHON_BIN -c "import PyQt5; import os; print(os.path.dirname(PyQt5.__file__) + '/Qt/plugins')" 2>/dev/null)

# Run pycrosGUI
$PYTHON_BIN -m pycrosGUI.main "$@"
