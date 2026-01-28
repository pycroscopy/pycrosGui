"""
Main entry point module for pycrosGUI.
This module handles proper initialization of the PyQt5/PyQt6 GUI.
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


class Application:
    """Main application controller with homepage flow."""
    
    def __init__(self):
        # Import QtWidgets with fallback
        try:
            from PyQt6 import QtWidgets
        except ImportError:
            from PyQt5 import QtWidgets
        
        self.QtWidgets = QtWidgets
        
        # Create or get existing QApplication instance
        self.app = QtWidgets.QApplication.instance()
        if self.app is None:
            self.app = QtWidgets.QApplication(sys.argv)
        
        self.homepage = None
        self.main_window = None
        
    def show_homepage(self):
        """Show the homepage/welcome screen."""
        from .homepage import HomePage
        from .version import __version__
        
        self.homepage = HomePage(version=__version__)
        self.homepage.enter_app.connect(self.launch_main_app)
        self.homepage.resize(900, 700)
        self.homepage.show()
        
    def launch_main_app(self):
        """Launch the main application window."""
        from .base_widget import BaseWidget
        
        # Hide homepage
        if self.homepage:
            self.homepage.close()
        
        # Create and show main window
        self.main_window = BaseWidget()
        self.main_window.resize(1280, 800)
        self.main_window.show()
        
    def run(self):
        """Run the application."""
        self.show_homepage()
        sys.exit(self.app.exec() if hasattr(self.app, 'exec') else self.app.exec_())


def main():
    """Main entry point for the pycrosGUI application."""
    app = Application()
    app.run()


if __name__ == '__main__':
    main()