"""
#####################################################################
#
# Part of pycrosGUI
#
# EDSDialog: Energy Dispersive Spectroscopy analysis dialog.
#       - Element selection from periodic table
#       - Peak identification
#       - Quantification with k-factors
#
#####################################################################
"""
try:
    from PyQt6 import QtWidgets, QtGui
except ImportError:
    from PyQt5 import QtWidgets, QtGui

import numpy as np


class EDSDialog(QtWidgets.QWidget):
    """Dialog for EDS (Energy Dispersive Spectroscopy) analysis."""
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        layout = self.get_sidebar()
        self.setLayout(layout)
        self.setWindowTitle("EDS")
        self.eds_key = ''
        self.dataset = parent.dataset if hasattr(parent, 'dataset') else None
        self.name = 'EDS'
        self.model = []
        self.eds_dict = {}
        self.count = 0
        self.peaks = []
        self.pp = []
        self.k_factors = None
        self.number_of_edges = 0
        self.elements_selected = []
        self.periodic_table = parent.periodic_table if hasattr(parent, 'periodic_table') else None

    def get_sidebar(self):
        """Create the sidebar layout for the EDS dialog."""
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
        self.peak_list = QtWidgets.QComboBox(self)
        self.peak_list.addItem("Peak 1")
        self.peak_list.addItem("add Peak")
        layout.addWidget(self.peak_list, row, 0, 1, 3)
        self.peak_list.activated[str].connect(self.update)

        row += 1
        self.element_label = QtWidgets.QLabel("Element")
        self.element_edit = QtWidgets.QLineEdit("")
        self.element_edit.editingFinished.connect(self.update)
        self.line_select = QtWidgets.QComboBox()
        self.line_select.addItems(['Ka', 'Kb', 'La', 'Lb', 'Ma', 'Mb'])
        layout.addWidget(self.element_label, row, 0)
        layout.addWidget(self.element_edit, row, 1)
        layout.addWidget(self.line_select, row, 2)

        row += 1
        self.energy_label = QtWidgets.QLabel("Energy")
        self.energy_edit = QtWidgets.QLineEdit("0.0")
        self.energy_edit.setValidator(validfloat)
        self.energy_unit = QtWidgets.QLabel("keV")
        layout.addWidget(self.energy_label, row, 0)
        layout.addWidget(self.energy_edit, row, 1)
        layout.addWidget(self.energy_unit, row, 2)

        row += 1
        self.fit_button = QtWidgets.QPushButton()
        self.fit_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.fit_button.setText("Fit Peaks")
        layout.addWidget(self.fit_button, row, 0, 1, 3)
        self.fit_button.clicked.connect(self.fit_peaks)

        row += 1
        self.intensity_label = QtWidgets.QLabel("Intensity")
        self.intensity_edit = QtWidgets.QLineEdit("0.0")
        self.intensity_edit.setReadOnly(True)
        self.intensity_unit = QtWidgets.QLabel("counts")
        layout.addWidget(self.intensity_label, row, 0)
        layout.addWidget(self.intensity_edit, row, 1)
        layout.addWidget(self.intensity_unit, row, 2)

        row += 1
        self.quantify_button = QtWidgets.QPushButton()
        self.quantify_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.quantify_button.setText("Quantify")
        layout.addWidget(self.quantify_button, row, 0, 1, 3)
        self.quantify_button.clicked.connect(self.quantify)

        row += 1
        self.kfactor_label = QtWidgets.QLabel("k-factors")
        self.kfactor_select = QtWidgets.QComboBox()
        self.kfactor_select.addItems(['Bruker 15keV', 'Thermo 200keV', 'Custom'])
        layout.addWidget(self.kfactor_label, row, 0)
        layout.addWidget(self.kfactor_select, row, 1, 1, 2)

        row += 1
        self.composition_label = QtWidgets.QLabel("Composition")
        layout.addWidget(self.composition_label, row, 0, 1, 3)

        row += 1
        self.composition_list = QtWidgets.QListWidget()
        self.composition_list.addItem("No data")
        layout.addWidget(self.composition_list, row, 0, 1, 3)

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
        self.update_eds_dataset()

    def update_sidebar(self):
        """Update the EDS sidebar with the current dataset information."""
        # Update the spectrum list
        spectrum_list = []
        if hasattr(self.parent, 'datasets'):
            for key, dataset in self.parent.datasets.items():
                if hasattr(dataset, 'data_type'):
                    if 'SPEC' in dataset.data_type.name:
                        if hasattr(dataset, 'modality') and dataset.modality == 'EDS':
                            spectrum_list.append(f"{key}: {dataset.title}")

        self.main_list.clear()
        if len(spectrum_list) == 0:
            self.main_list.addItem("None")
        else:
            for item in spectrum_list:
                self.main_list.addItem(item)
        
        self.update_eds_dataset()

    def update_eds_dataset(self, value=0):
        """Update the EDS dataset."""
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
            self.peak_list.clear()
            for elem in self.elements_selected:
                self.peak_list.addItem(f"{elem}")
            self.peak_list.addItem("add Peak")

    def fit_peaks(self):
        """Fit peaks in the EDS spectrum."""
        try:
            import pyTEMlib.eds_tools as eds
            if self.dataset is not None:
                # Fit peaks
                pass
        except ImportError:
            pass

    def quantify(self):
        """Quantify the elemental composition."""
        try:
            import pyTEMlib.eds_tools as eds
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
