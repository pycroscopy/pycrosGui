"""
Main entry point module for pycrosGUI.
This module handles proper initialization of the PyQt5/PyQt6 GUI.
"""
import sys
import os


def main():
    """Main entry point for the pycrosGUI application."""
    # Ensure QT_QPA_PLATFORM_PLUGIN_PATH is set for macOS
    if sys.platform == 'darwin':  # macOS
        try:
            # Try PyQt6 first
            try:
                import PyQt6
                plugins_path = os.path.join(
                    os.path.dirname(PyQt6.__file__), 'Qt6', 'plugins'
                )
                if os.path.exists(plugins_path):
                    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugins_path
            except ImportError:
                # Fall back to PyQt5
                import PyQt5
                plugins_path = os.path.join(
                    os.path.dirname(PyQt5.__file__), 'Qt', 'plugins'
                )
                if os.path.exists(plugins_path):
                    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugins_path
        except ImportError:
            pass

    # Import QtWidgets with fallback
    try:
        from PyQt6 import QtWidgets
    except ImportError:
        from PyQt5 import QtWidgets

    # Import BaseWidget
    from .base_widget import BaseWidget

    # Create or get existing QApplication instance
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    # Create and show main window
    window = BaseWidget()
    window.show()  # This now works because we fixed the self.show conflict

    # Start event loop
    sys.exit(app.exec() if hasattr(app, 'exec') else app.exec_())


if __name__ == '__main__':
    main()