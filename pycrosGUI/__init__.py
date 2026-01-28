"""
pycrosGUI: A PyQt5-based GUI for viewing and analyzing microscopy data.
"""

from .base_widget import BaseWidget
from .main import main
from .version import __version__
from .periodic_table import PeriodicTable
from .data_dialog import DataDialog
from .calculator_dialog import CalculatorDialog
from .info_dialog import InfoDialog
from .low_loss_dialog import LowLossDialog
from .core_loss_dialog import CoreLossDialog
from .eds_dialog import EDSDialog
from .peak_fit_dialog import PeakFitDialog
from .image_dialog import ImageDialog
from .atom_dialog import AtomDialog
from .probe_dialog import ProbeDialog
from .homepage import HomePage

__all__ = [
    'BaseWidget', 
    '__version__', 
    'main',
    'PeriodicTable',
    'DataDialog',
    'CalculatorDialog',
    'InfoDialog',
    'LowLossDialog',
    'CoreLossDialog',
    'EDSDialog',
    'PeakFitDialog',
    'ImageDialog',
    'AtomDialog',
    'ProbeDialog',
    'HomePage',
]

if __name__ == '__main__':
    main()
