"""
pycrosGUI: A PyQt5-based GUI for viewing and analyzing microscopy data.
"""

from .base_widget import BaseWidget
from .version import __version__

__all__ = ['BaseWidget', '__version__', 'main']


def main():
    """Main entry point for the pycrosGUI application."""
    import sys
    from PyQt5 import QtWidgets
    
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    
    window = BaseWidget()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
