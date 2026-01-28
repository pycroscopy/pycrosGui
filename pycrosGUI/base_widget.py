
"""
######## pycrosGui BaseWidget
# # part of the pycroscopy ecosystem
# #
# # by Gerd Duscher and Levi Dunn
# # Start Feb 2025
# This Base Widget is to be extended for pycroscopy GUIs
# running under python 3 using pyqt, and pyQt5 as GUI mashine
# ################################################################
"""
import os
import sys

try:
    from PyQt6 import QtCore, QtWidgets, QtGui
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets

import numpy as np
import pyqtgraph as pg

# Repository-specific imports
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

# Full 118 Element Data 
ELEMENT_DATA = {
    "H": {"name": "Hydrogen", "number": 1, "mass": 1.008}, "He": {"name": "Helium", "number": 2, "mass": 4.0026},
    "Li": {"name": "Lithium", "number": 3, "mass": 6.94}, "Be": {"name": "Beryllium", "number": 4, "mass": 9.0122},
    "B": {"name": "Boron", "number": 5, "mass": 10.81}, "C": {"name": "Carbon", "number": 6, "mass": 12.011},
    "N": {"name": "Nitrogen", "number": 7, "mass": 14.007}, "O": {"name": "Oxygen", "number": 8, "mass": 15.999},
    "F": {"name": "Fluorine", "number": 9, "mass": 18.998}, "Ne": {"name": "Neon", "number": 10, "mass": 20.180},
    "Na": {"name": "Sodium", "number": 11, "mass": 22.990}, "Mg": {"name": "Magnesium", "number": 12, "mass": 24.305},
    "Al": {"name": "Aluminum", "number": 13, "mass": 26.982}, "Si": {"name": "Silicon", "number": 14, "mass": 28.085},
    "P": {"name": "Phosphorus", "number": 15, "mass": 30.974}, "S": {"name": "Sulfur", "number": 16, "mass": 32.06},
    "Cl": {"name": "Chlorine", "number": 17, "mass": 35.45}, "Ar": {"name": "Argon", "number": 18, "mass": 39.948},
    "K": {"name": "Potassium", "number": 19, "mass": 39.098}, "Ca": {"name": "Calcium", "number": 20, "mass": 40.078},
    "Sc": {"name": "Scandium", "number": 21, "mass": 44.956}, "Ti": {"name": "Titanium", "number": 22, "mass": 47.867},
    "V": {"name": "Vanadium", "number": 23, "mass": 50.942}, "Cr": {"name": "Chromium", "number": 24, "mass": 51.996},
    "Mn": {"name": "Manganese", "number": 25, "mass": 54.938}, "Fe": {"name": "Iron", "number": 26, "mass": 55.845},
    "Co": {"name": "Cobalt", "number": 27, "mass": 58.933}, "Ni": {"name": "Nickel", "number": 28, "mass": 58.693},
    "Cu": {"name": "Copper", "number": 29, "mass": 63.546}, "Zn": {"name": "Zinc", "number": 30, "mass": 65.38},
    "Ga": {"name": "Gallium", "number": 31, "mass": 69.723}, "Ge": {"name": "Germanium", "number": 32, "mass": 72.630},
    "As": {"name": "Arsenic", "number": 33, "mass": 74.922}, "Se": {"name": "Selenium", "number": 34, "mass": 78.971},
    "Br": {"name": "Bromine", "number": 35, "mass": 79.904}, "Kr": {"name": "Krypton", "number": 36, "mass": 83.798},
    "Rb": {"name": "Rubidium", "number": 37, "mass": 85.468}, "Sr": {"name": "Strontium", "number": 38, "mass": 87.62},
    "Y": {"name": "Yttrium", "number": 39, "mass": 88.906}, "Zr": {"name": "Zirconium", "number": 40, "mass": 91.224},
    "Nb": {"name": "Niobium", "number": 41, "mass": 92.906}, "Mo": {"name": "Molybdenum", "number": 42, "mass": 95.95},
    "Tc": {"name": "Technetium", "number": 43, "mass": 98}, "Ru": {"name": "Ruthenium", "number": 44, "mass": 101.07},
    "Rh": {"name": "Rhodium", "number": 45, "mass": 102.91}, "Pd": {"name": "Palladium", "number": 46, "mass": 106.42},
    "Ag": {"name": "Silver", "number": 47, "mass": 107.87}, "Cd": {"name": "Cadmium", "number": 48, "mass": 112.41},
    "In": {"name": "Indium", "number": 49, "mass": 114.82}, "Sn": {"name": "Tin", "number": 50, "mass": 118.71},
    "Sb": {"name": "Antimony", "number": 51, "mass": 121.76}, "Te": {"name": "Tellurium", "number": 52, "mass": 127.60},
    "I": {"name": "Iodine", "number": 53, "mass": 126.90}, "Xe": {"name": "Xenon", "number": 54, "mass": 131.29},
    "Cs": {"name": "Cesium", "number": 55, "mass": 132.91}, "Ba": {"name": "Barium", "number": 56, "mass": 137.33},
    "La": {"name": "Lanthanum", "number": 57, "mass": 138.91}, "Ce": {"name": "Cerium", "number": 58, "mass": 140.12},
    "Pr": {"name": "Praseodymium", "number": 59, "mass": 140.91}, "Nd": {"name": "Neodymium", "number": 60, "mass": 144.24},
    "Pm": {"name": "Promethium", "number": 61, "mass": 145}, "Sm": {"name": "Samarium", "number": 62, "mass": 150.36},
    "Eu": {"name": "Europium", "number": 63, "mass": 151.96}, "Gd": {"name": "Gadolinium", "number": 64, "mass": 157.25},
    "Tb": {"name": "Terbium", "number": 65, "mass": 158.93}, "Dy": {"name": "Dysprosium", "number": 66, "mass": 162.50},
    "Ho": {"name": "Holmium", "number": 67, "mass": 164.93}, "Er": {"name": "Erbium", "number": 68, "mass": 167.26},
    "Tm": {"name": "Thulium", "number": 69, "mass": 168.93}, "Yb": {"name": "Ytterbium", "number": 70, "mass": 173.05},
    "Lu": {"name": "Lutetium", "number": 71, "mass": 174.97}, "Hf": {"name": "Hafnium", "number": 72, "mass": 178.49},
    "Ta": {"name": "Tantalum", "number": 73, "mass": 180.95}, "W": {"name": "Tungsten", "number": 74, "mass": 183.84},
    "Re": {"name": "Rhenium", "number": 75, "mass": 186.21}, "Os": {"name": "Osmium", "number": 76, "mass": 190.23},
    "Ir": {"name": "Iridium", "number": 77, "mass": 192.22}, "Pt": {"name": "Platinum", "number": 78, "mass": 195.08},
    "Au": {"name": "Gold", "number": 79, "mass": 196.97}, "Hg": {"name": "Mercury", "number": 80, "mass": 200.59},
    "Tl": {"name": "Thallium", "number": 81, "mass": 204.38}, "Pb": {"name": "Lead", "number": 82, "mass": 207.2},
    "Bi": {"name": "Bismuth", "number": 83, "mass": 208.98}, "Po": {"name": "Polonium", "number": 84, "mass": 209},
    "At": {"name": "Astatine", "number": 85, "mass": 210}, "Rn": {"name": "Radon", "number": 86, "mass": 222},
    "Fr": {"name": "Francium", "number": 87, "mass": 223}, "Ra": {"name": "Radium", "number": 88, "mass": 226},
    "Ac": {"name": "Actinium", "number": 89, "mass": 227}, "Th": {"name": "Thorium", "number": 90, "mass": 232.04},
    "Pa": {"name": "Protactinium", "number": 91, "mass": 231.04}, "U": {"name": "Uranium", "number": 92, "mass": 238.03},
    "Np": {"name": "Neptunium", "number": 93, "mass": 237}, "Pu": {"name": "Plutonium", "number": 94, "mass": 244},
    "Am": {"name": "Americium", "number": 95, "mass": 243}, "Cm": {"name": "Curium", "number": 96, "mass": 247},
    "Bk": {"name": "Berkelium", "number": 97, "mass": 247}, "Cf": {"name": "Californium", "number": 98, "mass": 251},
    "Es": {"name": "Einsteinium", "number": 99, "mass": 252}, "Fm": {"name": "Fermium", "number": 100, "mass": 257},
    "Md": {"name": "Mendelevium", "number": 101, "mass": 258}, "No": {"name": "Nobelium", "number": 102, "mass": 259},
    "Lr": {"name": "Lawrencium", "number": 103, "mass": 262}, "Rf": {"name": "Rutherfordium", "number": 104, "mass": 267},
    "Db": {"name": "Dubnium", "number": 105, "mass": 270}, "Sg": {"name": "Seaborgium", "number": 106, "mass": 271},
    "Bh": {"name": "Bohrium", "number": 107, "mass": 270}, "Hs": {"name": "Hassium", "number": 108, "mass": 277},
    "Mt": {"name": "Meitnerium", "number": 109, "mass": 276}, "Ds": {"name": "Darmstadtium", "number": 110, "mass": 281},
    "Rg": {"name": "Roentgenium", "number": 111, "mass": 280}, "Cn": {"name": "Copernicium", "number": 112, "mass": 285},
    "Nh": {"name": "Nihonium", "number": 113, "mass": 284}, "Fl": {"name": "Flerovium", "number": 114, "mass": 289},
    "Mc": {"name": "Moscovium", "number": 115, "mass": 288}, "Lv": {"name": "Livermorium", "number": 116, "mass": 293},
    "Ts": {"name": "Tennessine", "number": 117, "mass": 294}, "Og": {"name": "Oganesson", "number": 118, "mass": 294},
}

class ImageView(pg.ImageView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui.roiBtn.setChecked(False)

    def roiChanged(self):
        super().roiChanged()
        for i in range(len(self.roiCurves)):
            self.roiCurves[i].setPen('black')

class BaseWidget(QtWidgets.QMainWindow):
    def __init__(self, sidebar=[], filename=None):
        super().__init__()
        self.version = '2025-1-1'
        
        # KEY REPOSITORY FIXES
        self.dataset = None 
        self.datasets = {}
        self.add_spectrum = []
        
        self.main = ""
        self.tabCurrent = 1
        self.periodic_table = PeriodicTable(self)
        self.dir_name = os.getcwd()
        
        self._init_ui()
        self._init_menus()
        self._init_dialogs()
        self._connect_pt_buttons()

    def _init_menus(self):
        """Initialize menu bar with File and View menus."""
        menubar = self.menuBar()
        
        # File menu
        self.file_menu = menubar.addMenu('File')
        
        open_action = QtWidgets.QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        self.file_menu.addAction(open_action)
        
        save_action = QtWidgets.QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        self.file_menu.addAction(save_action)
        
        self.file_menu.addSeparator()
        
        exit_action = QtWidgets.QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)
        
        # View menu
        self.view = menubar.addMenu('View')
        
        # Data toggle
        self.data_visible = QtWidgets.QAction('Data', self, checkable=True)
        self.data_visible.setChecked(True)
        self.data_visible.toggled.connect(lambda checked: self.data_widget.setVisible(checked))
        self.view.addAction(self.data_visible)
        
        # PT toggle
        self.pt_visible = QtWidgets.QAction('Periodic Table', self, checkable=True)
        self.pt_visible.setChecked(True)
        self.pt_visible.toggled.connect(lambda checked: self.periodic_widget.setVisible(checked))
        self.view.addAction(self.pt_visible)
        
        # Calculator toggle
        self.calc_visible = QtWidgets.QAction('Calculator', self, checkable=True)
        self.calc_visible.setChecked(True)
        self.calc_visible.toggled.connect(lambda checked: self.calculator_widget.setVisible(checked))
        self.view.addAction(self.calc_visible)
        
        self.view.addSeparator()
        
        # Image group toggle
        self.image_visible = QtWidgets.QAction('Image', self, checkable=True)
        self.image_visible.setShortcut('Ctrl+I')
        self.image_visible.setStatusTip('Toggle image dialogs visibility')
        self.image_visible.toggled.connect(self.visible_image)
        self.view.addAction(self.image_visible)
        
        # EELS group toggle
        self.eels_visible = QtWidgets.QAction('EELS', self, checkable=True)
        self.eels_visible.setShortcut('Ctrl+E')
        self.eels_visible.setStatusTip('Toggle EELS dialogs visibility')
        self.eels_visible.toggled.connect(self.visible_eels)
        self.view.addAction(self.eels_visible)
        
        # EDS toggle
        self.eds_visible = QtWidgets.QAction('EDS', self, checkable=True)
        self.eds_visible.setShortcut('Ctrl+X')
        self.eds_visible.setStatusTip('Toggle EDS dialogs visibility')
        self.eds_visible.toggled.connect(self.visible_eds)
        self.view.addAction(self.eds_visible)

    def _init_dialogs(self):
        """Initialize all analysis dialogs."""
        # Info dialog
        self.info_dialog = InfoDialog(self)
        self.info_widget = self.add_sidebar(self.info_dialog, "Info")
        
        # Low Loss EELS dialog
        self.low_loss_dialog = LowLossDialog(self)
        self.low_loss_widget = self.add_sidebar(self.low_loss_dialog, "LowLoss")
        
        # Core Loss EELS dialog
        self.core_loss_dialog = CoreLossDialog(self)
        self.core_loss_widget = self.add_sidebar(self.core_loss_dialog, "CoreLoss")
        
        # EDS dialog
        self.eds_dialog = EDSDialog(self)
        self.eds_widget = self.add_sidebar(self.eds_dialog, "EDS")
        
        # Peak Fit dialog
        self.peak_fit_dialog = PeakFitDialog(self)
        self.peak_fit_widget = self.add_sidebar(self.peak_fit_dialog, "PeakFit")
        
        # Image dialog
        self.image_dialog = ImageDialog(self)
        self.image_widget = self.add_sidebar(self.image_dialog, "Image")
        
        # Atom dialog
        self.atom_dialog = AtomDialog(self)
        self.atom_widget = self.add_sidebar(self.atom_dialog, "Atoms")
        
        # Probe dialog
        self.probe_dialog = ProbeDialog(self)
        self.probe_widget = self.add_sidebar(self.probe_dialog, "Probe")
        
        # Tabify dialogs on the left side
        self.tabifyDockWidget(self.data_widget, self.info_widget)
        self.tabifyDockWidget(self.info_widget, self.low_loss_widget)
        self.tabifyDockWidget(self.low_loss_widget, self.core_loss_widget)
        self.tabifyDockWidget(self.core_loss_widget, self.peak_fit_widget)
        self.tabifyDockWidget(self.peak_fit_widget, self.eds_widget)
        self.tabifyDockWidget(self.eds_widget, self.image_widget)
        self.tabifyDockWidget(self.image_widget, self.atom_widget)
        self.tabifyDockWidget(self.atom_widget, self.probe_widget)
        
        # Connect visibility to updates
        self.info_widget.visibilityChanged.connect(self.info_update)
        self.low_loss_widget.visibilityChanged.connect(self.low_loss_update)
        self.core_loss_widget.visibilityChanged.connect(self.core_loss_update)
        self.eds_widget.visibilityChanged.connect(self.eds_update)
        self.peak_fit_widget.visibilityChanged.connect(self.peak_fit_update)
        self.image_widget.visibilityChanged.connect(self.image_update)
        self.atom_widget.visibilityChanged.connect(self.atom_update)
        self.probe_widget.visibilityChanged.connect(self.probe_update)
        
        # Initially hide some dialogs
        self.low_loss_widget.setVisible(False)
        self.core_loss_widget.setVisible(False)
        self.eds_widget.setVisible(False)
        self.peak_fit_widget.setVisible(False)
        self.image_widget.setVisible(False)
        self.atom_widget.setVisible(False)
        self.probe_widget.setVisible(False)
        
        # Raise data widget to front
        self.data_widget.raise_()

    def visible_eels(self, checked):
        """Toggle the visibility of the EELS widgets."""
        self.low_loss_widget.setVisible(checked)
        self.core_loss_widget.setVisible(checked)
        self.peak_fit_widget.setVisible(checked)

    def visible_eds(self, checked):
        """Toggle the visibility of the EDS widgets."""
        self.eds_widget.setVisible(checked)

    def visible_image(self, checked):
        """Toggle the visibility of the image widgets."""
        self.image_widget.setVisible(checked)
        self.atom_widget.setVisible(checked)
        self.probe_widget.setVisible(checked)

    def info_update(self, visible):
        """Update the Info dialog when it becomes visible."""
        if visible:
            self.info_dialog.update_info()

    def low_loss_update(self, visible):
        """Update the Low Loss dialog."""
        if visible:
            self.low_loss_dialog.update_ll_sidebar()

    def core_loss_update(self, visible):
        """Update the Core Loss dialog."""
        if visible:
            self.core_loss_dialog.update_cl_sidebar()

    def eds_update(self, visible):
        """Update the EDS dialog."""
        if visible:
            self.eds_dialog.update_sidebar()

    def peak_fit_update(self, visible):
        """Update the Peak Fit dialog."""
        if visible:
            self.peak_fit_dialog.update_peak_sidebar()

    def image_update(self, visible):
        """Update the Image dialog."""
        if visible:
            self.image_dialog.update_sidebar()

    def atom_update(self, visible):
        """Update the Atom dialog."""
        if visible:
            self.atom_dialog.update_sidebar()

    def probe_update(self, visible):
        """Update the Probe dialog."""
        if visible:
            self.probe_dialog.update_sidebar()

    def set_dataset(self):
        """Set the current dataset for the widget."""
        if self.main in self.datasets:
            self.dataset = self.datasets[self.main]

    def plot_update(self):
        """Update the plot based on current dataset."""
        pass

    def plot_additional_features(self, plt):
        """Adds additional features to the plot, as defined in the dialogs."""
        pass

    def show_metadata(self):
        """Show metadata dialog."""
        if self.dataset is not None:
            # Show metadata in a dialog
            pass

    def _init_ui(self):
        self.setWindowTitle(f'pycrosGUI v{self.version}')
        
        self.setDockOptions(
            QtWidgets.QMainWindow.DockOption.AllowNestedDocks | 
            QtWidgets.QMainWindow.DockOption.AllowTabbedDocks
        )

        self.setStyleSheet("""
            QMainWindow { background-color: #2c3e50; }
            QTabWidget::pane { border: 1px solid #34495e; background: #ecf0f1; border-radius: 4px; }
            QLineEdit, QTextEdit { background-color: #ffffff; color: #000000; border: 1px solid #bdc3c7; }
            QLabel { color: #ecf0f1; font-weight: bold; font-size: 10px; }
            
            QPushButton { 
                background-color: #95a5a6; color: #000000; 
                border: 1px solid #7f8c8d; border-radius: 0px; 
                font-weight: bold; font-size: 9px;
                margin: 0px; padding: 1px;
            }
            QPushButton:hover { background-color: #bdc3c7; }
            QDockWidget { color: #ecf0f1; font-weight: bold; font-size: 10px; }
            QDockWidget::title { background: #34495e; padding: 2px; }
        """)

        if self.periodic_table.layout():
            self.periodic_table.layout().setSpacing(1)
            self.periodic_table.layout().setContentsMargins(1,1,1,1)

        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        self.tab = QtWidgets.QTabWidget()
        self._setup_plots()
        self.tab.currentChanged.connect(self.updateTab)
        main_layout.addWidget(self.tab)
        self.setCentralWidget(central_widget)

        # Sidebar 1: Data (Left)
        self.data_dialog = DataDialog(self)
        self.data_widget = self.add_sidebar(
            self.data_dialog, "Data", QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
        )

        # Sidebar 2: PT (Right) - Modern periodic table in its own dock
        self.periodic_widget = QtWidgets.QDockWidget("Periodic Table", self)
        pt_container = QtWidgets.QWidget()
        pt_layout = QtWidgets.QVBoxLayout(pt_container)
        pt_layout.setContentsMargins(5, 5, 5, 5)
        pt_layout.setSpacing(5)
        
        # Open periodic table button for popup
        pt_button = QtWidgets.QPushButton("Open Full Periodic Table")
        pt_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        pt_button.clicked.connect(self.show_periodic_table)
        pt_layout.addWidget(pt_button)
        
        pt_layout.addWidget(QtWidgets.QLabel("ELEMENT INFO:"))
        self.info_box = QtWidgets.QTextEdit()
        self.info_box.setReadOnly(True)
        self.info_box.setMaximumHeight(100)
        self.info_box.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        pt_layout.addWidget(self.info_box)
        
        # Selected elements display
        pt_layout.addWidget(QtWidgets.QLabel("SELECTED ELEMENTS:"))
        self.selected_elements_label = QtWidgets.QLabel("None")
        self.selected_elements_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        self.selected_elements_label.setWordWrap(True)
        pt_layout.addWidget(self.selected_elements_label)
        
        pt_layout.addStretch()
        self.periodic_widget.setWidget(pt_container)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.periodic_widget)
        self.periodic_widget.setMinimumWidth(250)
        
        # Sidebar 3: Calculator (Right) - Separate dock widget
        self.calculator = CalculatorDialog(self)
        self.calculator_widget = self.calculator
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.calculator_widget)
        
        # Tabify PT and Calculator on the right side
        self.tabifyDockWidget(self.periodic_widget, self.calculator_widget)
        self.periodic_widget.raise_()

    def _setup_plots(self):
        self.plot1 = QtWidgets.QWidget()
        p1_lay = QtWidgets.QVBoxLayout(self.plot1)
        self.plot_param_window = pg.PlotWidget()
        p1_lay.addWidget(self.plot_param_window)
        self.tab.addTab(self.plot1, 'Spectrum')
        
        self.plot2 = QtWidgets.QWidget()
        p2_lay = QtWidgets.QGridLayout(self.plot2)
        self.si_plot = pg.PlotWidget()
        p2_lay.addWidget(self.si_plot, 0, 0)
        self.tab.addTab(self.plot2, 'Spectral Image')

        self.plot3 = QtWidgets.QWidget()
        p3_lay = QtWidgets.QVBoxLayout(self.plot3)
        self.image_item = ImageView()
        p3_lay.addWidget(self.image_item)
        self.tab.addTab(self.plot3, 'Image')

    def add_sidebar(self, widget, title=None, area=QtCore.Qt.DockWidgetArea.LeftDockWidgetArea):
        if title is None:
            title = getattr(widget, 'name', "Tools")
        dock = QtWidgets.QDockWidget(title, self)
        dock.setWidget(widget)
        self.addDockWidget(area, dock)
        return dock

    def _connect_pt_buttons(self):
        """Connect periodic table element selection signal."""
        self.periodic_table.element_selected.connect(self.display_element_info)

    def show_periodic_table(self):
        """Show the periodic table dialog."""
        result = self.periodic_table.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted if hasattr(QtWidgets.QDialog, 'DialogCode') else QtWidgets.QDialog.Accepted:
            selected = self.periodic_table.get_selected_elements()
            if selected:
                self.selected_elements_label.setText(', '.join(selected))
            else:
                self.selected_elements_label.setText("None")

    def save_file(self): pass
    def open_file(self): pass
    def remove_dataset(self): pass
    def update_DataDialog(self):
        if hasattr(self.data_dialog, 'update_sidebar'): self.data_dialog.update_sidebar()

    def updateTab(self, n):
        self.tabCurrent = n

    def display_element_info(self, symbol, data=None):
        """Display element information from periodic table selection."""
        if data is None:
            # Legacy support - look up from ELEMENT_DATA
            sym = symbol.strip().split()[-1] if symbol.strip() else ""
            if sym in ELEMENT_DATA:
                d = ELEMENT_DATA[sym]
                self.info_box.setText(f"<b>{sym}</b> ({d['number']}): {d['name']}<br>Atomic Mass: {d['mass']} u")
            else:
                self.info_box.setText(f"Selection: {sym} (No data)")
        else:
            # New format with data dict from periodic table
            from .periodic_table import CATEGORY_LABELS
            category = CATEGORY_LABELS.get(data.get('category', ''), 'Unknown')
            self.info_box.setText(
                f"<b>{data['name']}</b> ({symbol})<br>"
                f"Atomic Number: {data['number']}<br>"
                f"Atomic Mass: {data['mass']:.4f} u<br>"
                f"Category: {category}"
            )

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = BaseWidget()
    window.resize(1280, 800)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()