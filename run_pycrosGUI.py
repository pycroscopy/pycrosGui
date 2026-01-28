#!/usr/bin/env python
"""
Launcher script for pycrosGUI.
This script sets up the Qt environment before importing any Qt modules.
"""
import sys
import os

# Set Qt plugin path BEFORE importing Qt - critical for macOS
if sys.platform == 'darwin':
    try:
        import PyQt5
        plugins_path = os.path.join(
            os.path.dirname(PyQt5.__file__), 'Qt5', 'plugins'
        )
        if os.path.exists(plugins_path):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugins_path
    except ImportError:
        try:
            import PyQt6
            plugins_path = os.path.join(
                os.path.dirname(PyQt6.__file__), 'Qt6', 'plugins'
            )
            if os.path.exists(plugins_path):
                os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugins_path
        except ImportError:
            pass

if __name__ == '__main__':
    from pycrosGUI.main import main
    main()
