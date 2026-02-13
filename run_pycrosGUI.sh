#!/bin/bash
# pycrosGUI launcher script for macOS
# This script ensures Qt platform plugins are properly configured

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Determine Python executable - prefer Python 3.10 venv (known Qt compatibility)
# Then try standard venv, finally fall back to system Python
if [ -f "$SCRIPT_DIR/.venv310/bin/python" ]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv310/bin/python"
elif [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
else
    PYTHON_BIN="python3"
fi

# Remove quarantine attributes from PyQt5 (macOS security fix)
PYQT5_PATH=$($PYTHON_BIN -c "import PyQt5; import os; print(os.path.dirname(PyQt5.__file__))" 2>/dev/null)
if [ -n "$PYQT5_PATH" ] && [ -d "$PYQT5_PATH" ]; then
    xattr -cr "$PYQT5_PATH" 2>/dev/null
fi

# Set QT_QPA_PLATFORM_PLUGIN_PATH for macOS
export QT_QPA_PLATFORM_PLUGIN_PATH=$($PYTHON_BIN -c "import PyQt5; import os; print(os.path.dirname(PyQt5.__file__) + '/Qt5/plugins')" 2>/dev/null)

# Run pycrosGUI
$PYTHON_BIN -m pycrosGUI.main "$@"
