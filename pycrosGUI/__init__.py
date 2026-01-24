"""
pycrosGUI: A PyQt5-based GUI for viewing and analyzing microscopy data.
"""

from .base_widget import BaseWidget
from .main import main
from .version import __version__

__all__ = ['BaseWidget', '__version__', 'main']

if __name__ == '__main__':
    main()
