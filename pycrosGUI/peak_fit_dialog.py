"""
#####################################################################
#
# Part of pycrosGUI
#
# PeakFitDialog: Peak fitting dialog.
#       - Gaussian/Lorentzian peak fitting
#       - Multiple peak fitting
#       - White line ratio analysis
#
#####################################################################
"""
try:
    from PyQt6 import QtWidgets, QtGui
except ImportError:
    from PyQt5 import QtWidgets, QtGui

import numpy as np


class PeakFitDialog(QtWidgets.QWidget):
    """Dialog for peak fitting."""
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        layout = self.get_sidebar()
        self.setLayout(layout)
        self.name = "PeakFit"
        self.setWindowTitle("Peak Fit")
        self.peak_key = ''
        self.dataset = parent.dataset if hasattr(parent, 'dataset') else None

        self.model = []
        self.peaks = {}
        self.p_out = []
        self.peak_out_list = []
        self.peak_model = []
        self.core_loss = False
        self.energy_scale = []
        self.white_lines = {'ratio': {}, 'sum': {}}

    def get_sidebar(self):
        """Create the sidebar layout for the peak fit dialog."""
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
        self.fit_button = QtWidgets.QPushButton()
        self.fit_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.fit_button.setText("Fit Peaks")
        layout.addWidget(self.fit_button, row, 0, 1, 3)
        layout.setColumnStretch(0, 3)
        self.fit_button.clicked.connect(self.fit_peaks)

        row += 1
        self.peak_list = QtWidgets.QComboBox(self)
        self.peak_list.addItem("Peak 1")
        self.peak_list.addItem("add Peak")
        layout.addWidget(self.peak_list, row, 0, 1, 3)
        self.peak_list.activated[str].connect(self.update_peak)

        row += 1
        self.type_label = QtWidgets.QLabel("Type")
        self.type_select = QtWidgets.QComboBox()
        self.type_select.addItems(['Gaussian', 'Lorentzian', 'Voigt'])
        layout.addWidget(self.type_label, row, 0)
        layout.addWidget(self.type_select, row, 1, 1, 2)

        row += 1
        self.position_label = QtWidgets.QLabel("Position")
        self.position_edit = QtWidgets.QLineEdit("0.0")
        self.position_edit.setValidator(validfloat)
        self.position_edit.editingFinished.connect(self.on_position_enter)
        self.position_unit = QtWidgets.QLabel("eV")
        layout.addWidget(self.position_label, row, 0)
        layout.addWidget(self.position_edit, row, 1)
        layout.addWidget(self.position_unit, row, 2)

        row += 1
        self.width_label = QtWidgets.QLabel("Width")
        self.width_edit = QtWidgets.QLineEdit("1.0")
        self.width_edit.setValidator(validfloat)
        self.width_edit.editingFinished.connect(self.on_width_enter)
        self.width_unit = QtWidgets.QLabel("eV")
        layout.addWidget(self.width_label, row, 0)
        layout.addWidget(self.width_edit, row, 1)
        layout.addWidget(self.width_unit, row, 2)

        row += 1
        self.amplitude_label = QtWidgets.QLabel("Amplitude")
        self.amplitude_edit = QtWidgets.QLineEdit("1.0")
        self.amplitude_edit.setValidator(validfloat)
        self.amplitude_edit.editingFinished.connect(self.on_amplitude_enter)
        self.amplitude_unit = QtWidgets.QLabel("")
        layout.addWidget(self.amplitude_label, row, 0)
        layout.addWidget(self.amplitude_edit, row, 1)
        layout.addWidget(self.amplitude_unit, row, 2)

        row += 1
        self.start_label = QtWidgets.QLabel("Start Fit")
        self.start_edit = QtWidgets.QLineEdit("0.0")
        self.start_edit.setValidator(validfloat)
        self.start_unit = QtWidgets.QLabel("eV")
        layout.addWidget(self.start_label, row, 0)
        layout.addWidget(self.start_edit, row, 1)
        layout.addWidget(self.start_unit, row, 2)

        row += 1
        self.end_label = QtWidgets.QLabel("End Fit")
        self.end_edit = QtWidgets.QLineEdit("100.0")
        self.end_edit.setValidator(validfloat)
        self.end_unit = QtWidgets.QLabel("eV")
        layout.addWidget(self.end_label, row, 0)
        layout.addWidget(self.end_edit, row, 1)
        layout.addWidget(self.end_unit, row, 2)

        row += 1
        self.white_line_button = QtWidgets.QPushButton()
        self.white_line_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.white_line_button.setText("White Lines")
        layout.addWidget(self.white_line_button, row, 0, 1, 3)
        self.white_line_button.clicked.connect(self.analyze_white_lines)

        row += 1
        self.ratio_label = QtWidgets.QLabel("L3/L2 Ratio")
        self.ratio_edit = QtWidgets.QLineEdit("0.0")
        self.ratio_edit.setReadOnly(True)
        self.ratio_unit = QtWidgets.QLabel("")
        layout.addWidget(self.ratio_label, row, 0)
        layout.addWidget(self.ratio_edit, row, 1)
        layout.addWidget(self.ratio_unit, row, 2)

        row += 1
        self.clear_button = QtWidgets.QPushButton()
        self.clear_button.setText("Clear Peaks")
        layout.addWidget(self.clear_button, row, 0, 1, 3)
        self.clear_button.clicked.connect(self.clear_peaks)

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
        self.update_peak_dataset()

    def update_peak_sidebar(self):
        """Update the peak fit sidebar with the current dataset information."""
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
        
        self.update_peak_dataset()

    def update_peak_dataset(self, value=0):
        """Update the peak fit dataset."""
        if hasattr(self.parent, 'dataset') and self.parent.dataset is not None:
            self.dataset = self.parent.dataset

    def update_peak(self, value=0):
        """Update the peak parameters display."""
        pass

    def on_position_enter(self):
        """Handle position change."""
        pass

    def on_width_enter(self):
        """Handle width change."""
        pass

    def on_amplitude_enter(self):
        """Handle amplitude change."""
        pass

    def fit_peaks(self):
        """Fit peaks to the spectrum."""
        try:
            import scipy.optimize
            if self.dataset is not None:
                # Fit peaks
                pass
        except ImportError:
            pass

    def analyze_white_lines(self):
        """Analyze white line ratios."""
        pass

    def clear_peaks(self):
        """Clear all peaks."""
        self.peaks = {}
        self.peak_list.clear()
        self.peak_list.addItem("Peak 1")
        self.peak_list.addItem("add Peak")

    def get_additional_spectra(self):
        """Get additional spectra for plotting."""
        additional_spectra = {}
        return additional_spectra

    def get_additional_features(self):
        """Get additional features for plotting."""
        additional_features = {}
        return additional_features
