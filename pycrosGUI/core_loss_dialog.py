"""
#####################################################################
#
# Part of pycrosGUI
#
# CoreLossDialog: Core loss EELS analysis dialog.
#       - Element selection from periodic table
#       - Edge identification and fitting
#       - Background subtraction
#       - Quantification
#
#####################################################################
"""
try:
    from PyQt6 import QtWidgets, QtGui
except ImportError:
    from PyQt5 import QtWidgets, QtGui

import numpy as np


class CoreLossDialog(QtWidgets.QWidget):
    """Dialog for core loss EELS analysis."""
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        layout = self.get_sidebar()
        self.setLayout(layout)
        self.setWindowTitle("Core Loss")
        self.cl_key = ''
        self.dataset = parent.dataset if hasattr(parent, 'dataset') else None
        self.name = 'CoreLoss'
        self.model = []
        self.edges = {}
        self.count = 0
        self.low_loss = None
        self.number_of_edges = 0
        self.elements_selected = []
        self.periodic_table = parent.periodic_table if hasattr(parent, 'periodic_table') else None

    def get_sidebar(self):
        """Create the sidebar layout for the core loss dialog."""
        validfloat = QtGui.QDoubleValidator()
        validint = QtGui.QIntValidator()

        layout = QtWidgets.QGridLayout()
        row = 0

        # Dataset selection
        self.main_list = QtWidgets.QComboBox(self)
        self.main_list.addItem("None")
        layout.addWidget(self.main_list, row, 0, 1, 3)
        layout.setColumnStretch(0, 3)
        self.main_list.activated[str].connect(self.set_dataset)

        row += 1
        self.elements_button = QtWidgets.QPushButton()
        self.elements_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.elements_button.setText("Elements")
        layout.addWidget(self.elements_button, row, 0, 1, 3)
        layout.setColumnStretch(0, 3)
        self.elements_button.clicked.connect(self.find_elements)

        row += 1
        self.edge_list = QtWidgets.QComboBox(self)
        self.edge_list.addItem("Edge 1")
        self.edge_list.addItem("add Edge")
        layout.addWidget(self.edge_list, row, 0, 1, 3)
        self.edge_list.activated[str].connect(self.update)

        row += 1
        self.element_z_label = QtWidgets.QLabel("Element Z")
        self.element_z_edit = QtWidgets.QLineEdit("0")
        self.element_z_edit.setValidator(validint)
        self.element_z_edit.editingFinished.connect(self.update)
        self.element_z_unit = QtWidgets.QLabel("")
        layout.addWidget(self.element_z_label, row, 0)
        layout.addWidget(self.element_z_edit, row, 1)
        layout.addWidget(self.element_z_unit, row, 2)

        row += 1
        self.edge_label = QtWidgets.QLabel("Edge")
        self.edge_select = QtWidgets.QComboBox()
        self.edge_select.addItems(['K', 'L', 'M', 'N', 'O'])
        layout.addWidget(self.edge_label, row, 0)
        layout.addWidget(self.edge_select, row, 1, 1, 2)

        row += 1
        self.onset_label = QtWidgets.QLabel("Onset")
        self.onset_edit = QtWidgets.QLineEdit("0.0")
        self.onset_edit.setValidator(validfloat)
        self.onset_edit.editingFinished.connect(self.on_onset_enter)
        self.onset_unit = QtWidgets.QLabel("eV")
        layout.addWidget(self.onset_label, row, 0)
        layout.addWidget(self.onset_edit, row, 1)
        layout.addWidget(self.onset_unit, row, 2)

        row += 1
        self.start_label = QtWidgets.QLabel("Start Fit")
        self.start_edit = QtWidgets.QLineEdit("50.0")
        self.start_edit.setValidator(validfloat)
        self.start_edit.editingFinished.connect(self.on_start_enter)
        self.start_unit = QtWidgets.QLabel("eV")
        layout.addWidget(self.start_label, row, 0)
        layout.addWidget(self.start_edit, row, 1)
        layout.addWidget(self.start_unit, row, 2)

        row += 1
        self.end_label = QtWidgets.QLabel("End Fit")
        self.end_edit = QtWidgets.QLineEdit("100.0")
        self.end_edit.setValidator(validfloat)
        self.end_edit.editingFinished.connect(self.on_end_enter)
        self.end_unit = QtWidgets.QLabel("eV")
        layout.addWidget(self.end_label, row, 0)
        layout.addWidget(self.end_edit, row, 1)
        layout.addWidget(self.end_unit, row, 2)

        row += 1
        self.background_button = QtWidgets.QPushButton()
        self.background_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.background_button.setText("Background")
        layout.addWidget(self.background_button, row, 0, 1, 3)
        self.background_button.clicked.connect(self.fit_background)

        row += 1
        self.bgd_type_label = QtWidgets.QLabel("BGD Type")
        self.bgd_type = QtWidgets.QComboBox()
        self.bgd_type.addItems(['Power Law', 'Polynomial', 'Linear'])
        layout.addWidget(self.bgd_type_label, row, 0)
        layout.addWidget(self.bgd_type, row, 1, 1, 2)

        row += 1
        self.r_label = QtWidgets.QLabel("r")
        self.r_edit = QtWidgets.QLineEdit("3.0")
        self.r_edit.setValidator(validfloat)
        self.r_unit = QtWidgets.QLabel("")
        layout.addWidget(self.r_label, row, 0)
        layout.addWidget(self.r_edit, row, 1)
        layout.addWidget(self.r_unit, row, 2)

        row += 1
        self.quantify_button = QtWidgets.QPushButton()
        self.quantify_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.quantify_button.setText("Quantify")
        layout.addWidget(self.quantify_button, row, 0, 1, 3)
        self.quantify_button.clicked.connect(self.quantify)

        row += 1
        self.xsection_label = QtWidgets.QLabel("X-Section")
        self.xsection_edit = QtWidgets.QLineEdit("0.0")
        self.xsection_edit.setReadOnly(True)
        self.xsection_unit = QtWidgets.QLabel("barn")
        layout.addWidget(self.xsection_label, row, 0)
        layout.addWidget(self.xsection_edit, row, 1)
        layout.addWidget(self.xsection_unit, row, 2)

        row += 1
        self.areal_label = QtWidgets.QLabel("Areal Dens.")
        self.areal_edit = QtWidgets.QLineEdit("0.0")
        self.areal_edit.setReadOnly(True)
        self.areal_unit = QtWidgets.QLabel("at/nm²")
        layout.addWidget(self.areal_label, row, 0)
        layout.addWidget(self.areal_edit, row, 1)
        layout.addWidget(self.areal_unit, row, 2)

        # Add stretch to push everything up
        row += 1
        layout.setRowStretch(row, 1)

        return layout

    def set_dataset(self, text=None):
        """Set the dataset."""
        if text:
            item_text = text
        else:
            item_text = self.main_list.currentText()
        if hasattr(self.parent, 'main'):
            self.parent.main = item_text.split(':')[0]
        self.update_cl_dataset()

    def update_cl_sidebar(self):
        """Update the core loss sidebar with the current dataset information."""
        # Update the spectrum list
        spectrum_list = []
        if hasattr(self.parent, 'datasets'):
            for key, dataset in self.parent.datasets.items():
                if hasattr(dataset, 'data_type'):
                    if 'SPEC' in dataset.data_type.name:
                        spectrum_list.append(f"{key}: {dataset.title}")

        self.main_list.clear()
        if len(spectrum_list) == 0:
            self.main_list.addItem("None")
        else:
            for item in spectrum_list:
                self.main_list.addItem(item)
        
        self.update_cl_dataset()

    def update_cl_dataset(self, value=0):
        """Update the core loss dataset."""
        if hasattr(self.parent, 'dataset') and self.parent.dataset is not None:
            self.dataset = self.parent.dataset

    def update(self, value=0):
        """Update the dialog."""
        pass

    def find_elements(self):
        """Open periodic table to select elements."""
        if self.periodic_table is not None:
            self.periodic_table.show()
            result = self.periodic_table.exec()
            if result:
                self.elements_selected = self.periodic_table.elements_selected
                self.set_elements()

    def set_elements(self, value=0):
        """Set the elements based on selected elements in the periodic table."""
        if len(self.elements_selected) > 0:
            self.edge_list.clear()
            for i, elem in enumerate(self.elements_selected):
                self.edge_list.addItem(f"{elem}")
            self.edge_list.addItem("add Edge")

    def on_onset_enter(self):
        """Handle onset energy change."""
        pass

    def on_start_enter(self):
        """Handle start energy change."""
        pass

    def on_end_enter(self):
        """Handle end energy change."""
        pass

    def fit_background(self):
        """Fit background to the spectrum."""
        try:
            import pyTEMlib.eels_tools as eels
            if self.dataset is not None:
                # Fit background
                pass
        except ImportError:
            pass

    def quantify(self):
        """Quantify the elemental composition."""
        try:
            import pyTEMlib.eels_tools as eels
            if self.dataset is not None:
                # Quantify
                pass
        except ImportError:
            pass

    def get_additional_spectra(self):
        """Get additional spectra for plotting."""
        additional_spectra = {}
        return additional_spectra

    def get_additional_features(self):
        """Get additional features for plotting."""
        additional_features = {}
        return additional_features
