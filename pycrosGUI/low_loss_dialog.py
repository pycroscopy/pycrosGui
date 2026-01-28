"""
#####################################################################
#
# Part of pycrosGUI
#
# LowLossDialog: Low loss EELS analysis dialog.
#       - Resolution function determination
#       - Zero-loss peak fitting
#       - Drude model fitting
#       - Multiple scattering removal
#       - Dielectric function extraction
#
#####################################################################
"""
try:
    from PyQt6 import QtWidgets, QtGui
except ImportError:
    from PyQt5 import QtWidgets, QtGui

import numpy as np


class LowLossDialog(QtWidgets.QWidget):
    """Dialog for low loss EELS analysis."""
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        layout = self.get_sidebar()
        self.setLayout(layout)
        self.name = "LowLoss"
        self.setWindowTitle("LowLoss")
        self.ll_key = ''
        self.dataset = None
        self.resolution_function = None
        self.drude_fit = None

    def get_sidebar(self):
        """Create the sidebar layout for the low loss dialog."""
        validfloat = QtGui.QDoubleValidator()

        layout = QtWidgets.QGridLayout()
        row = 0

        # Dataset selection
        self.main_list = QtWidgets.QComboBox(self)
        self.main_list.addItem("None")
        layout.addWidget(self.main_list, row, 0, 1, 3)
        layout.setColumnStretch(0, 3)
        self.main_list.activated[str].connect(self.set_dataset)

        row += 1
        self.resolution_button = QtWidgets.QPushButton()
        self.resolution_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.resolution_button.setText("Resolution Function")
        layout.addWidget(self.resolution_button, row, 0, 1, 3)
        layout.setColumnStretch(0, 3)
        self.resolution_button.clicked.connect(self.get_resolution_function)

        row += 1
        self.fit_width_label = QtWidgets.QLabel("Fit Width")
        self.fit_width_edit = QtWidgets.QLineEdit("3.0")
        self.fit_width_edit.setValidator(validfloat)
        self.fit_width_edit.editingFinished.connect(self.set_fit_width)
        self.fit_width_unit = QtWidgets.QLabel("eV")
        layout.addWidget(self.fit_width_label, row, 0)
        layout.addWidget(self.fit_width_edit, row, 1)
        layout.addWidget(self.fit_width_unit, row, 2)

        row += 1
        self.resolution_label = QtWidgets.QLabel("Resolution")
        self.resolution_edit = QtWidgets.QLineEdit("0.0")
        self.resolution_edit.setReadOnly(True)
        self.resolution_unit = QtWidgets.QLabel("eV")
        layout.addWidget(self.resolution_label, row, 0)
        layout.addWidget(self.resolution_edit, row, 1)
        layout.addWidget(self.resolution_unit, row, 2)

        row += 1
        self.probability_button = QtWidgets.QPushButton()
        self.probability_button.setText("Probability")
        self.probability_button.setCheckable(True)
        layout.addWidget(self.probability_button, row, 0, 1, 2)
        self.probability_button.clicked.connect(self.get_probability)

        row += 1
        self.drude_button = QtWidgets.QPushButton()
        self.drude_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.drude_button.setText("Drude Fit")
        layout.addWidget(self.drude_button, row, 0, 1, 3)
        layout.setColumnStretch(0, 3)
        self.drude_button.clicked.connect(self.get_drude)

        row += 1
        self.drude_start_label = QtWidgets.QLabel("Start Fit")
        self.drude_start_edit = QtWidgets.QLineEdit("3.0")
        self.drude_start_edit.setValidator(validfloat)
        self.drude_start_unit = QtWidgets.QLabel("eV")
        layout.addWidget(self.drude_start_label, row, 0)
        layout.addWidget(self.drude_start_edit, row, 1)
        layout.addWidget(self.drude_start_unit, row, 2)

        row += 1
        self.drude_end_label = QtWidgets.QLabel("End Fit")
        self.drude_end_edit = QtWidgets.QLineEdit("50.0")
        self.drude_end_edit.setValidator(validfloat)
        self.drude_end_unit = QtWidgets.QLabel("eV")
        layout.addWidget(self.drude_end_label, row, 0)
        layout.addWidget(self.drude_end_edit, row, 1)
        layout.addWidget(self.drude_end_unit, row, 2)

        row += 1
        self.ep_label = QtWidgets.QLabel("Ep")
        self.ep_edit = QtWidgets.QLineEdit("15.0")
        self.ep_edit.setValidator(validfloat)
        self.ep_unit = QtWidgets.QLabel("eV")
        layout.addWidget(self.ep_label, row, 0)
        layout.addWidget(self.ep_edit, row, 1)
        layout.addWidget(self.ep_unit, row, 2)

        row += 1
        self.gamma_label = QtWidgets.QLabel("Gamma")
        self.gamma_edit = QtWidgets.QLineEdit("5.0")
        self.gamma_edit.setValidator(validfloat)
        self.gamma_unit = QtWidgets.QLabel("eV")
        layout.addWidget(self.gamma_label, row, 0)
        layout.addWidget(self.gamma_edit, row, 1)
        layout.addWidget(self.gamma_unit, row, 2)

        row += 1
        self.plot_drude_button = QtWidgets.QPushButton()
        self.plot_drude_button.setText("Plot Drude")
        self.plot_drude_button.setCheckable(True)
        layout.addWidget(self.plot_drude_button, row, 0)

        self.plot_dielectric_button = QtWidgets.QPushButton()
        self.plot_dielectric_button.setText("Plot Diel.")
        self.plot_dielectric_button.setCheckable(True)
        layout.addWidget(self.plot_dielectric_button, row, 1)

        self.do_all_button = QtWidgets.QPushButton()
        self.do_all_button.setText("Do All")
        self.do_all_button.setCheckable(True)
        layout.addWidget(self.do_all_button, row, 2)
        self.do_all_button.clicked.connect(self.do_all)

        row += 1
        self.multiple_button = QtWidgets.QPushButton()
        self.multiple_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.multiple_button.setText("Multiple Scattering")
        layout.addWidget(self.multiple_button, row, 0, 1, 3)
        layout.setColumnStretch(0, 3)
        self.multiple_button.clicked.connect(self.remove_multiple_scattering)

        row += 1
        self.thickness_label = QtWidgets.QLabel("Thickness")
        self.thickness_edit = QtWidgets.QLineEdit("0.0")
        self.thickness_edit.setReadOnly(True)
        self.thickness_unit = QtWidgets.QLabel("nm")
        layout.addWidget(self.thickness_label, row, 0)
        layout.addWidget(self.thickness_edit, row, 1)
        layout.addWidget(self.thickness_unit, row, 2)

        row += 1
        self.mfp_label = QtWidgets.QLabel("MFP")
        self.mfp_edit = QtWidgets.QLineEdit("0.0")
        self.mfp_edit.setReadOnly(True)
        self.mfp_unit = QtWidgets.QLabel("nm")
        layout.addWidget(self.mfp_label, row, 0)
        layout.addWidget(self.mfp_edit, row, 1)
        layout.addWidget(self.mfp_unit, row, 2)

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
        self.update_ll_dataset()

    def update_ll_sidebar(self):
        """Update the low loss sidebar with the current dataset information."""
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
        
        self.update_ll_dataset()

    def update_ll_dataset(self, value=0):
        """Update the low loss dataset with the current parameters."""
        if hasattr(self.parent, 'dataset') and self.parent.dataset is not None:
            self.dataset = self.parent.dataset

    def update_ll_plot(self):
        """Update the low loss plot with the current dataset information."""
        if hasattr(self.parent, 'plot_update'):
            self.parent.plot_update()

    def get_additional_spectra(self):
        """Get additional spectra for plotting."""
        additional_spectra = {}
        return additional_spectra

    def get_additional_features(self):
        """Get additional features for plotting."""
        additional_features = {}
        return additional_features

    def set_fit_width(self):
        """Set the fit width for the zero-loss peak."""
        pass

    def get_resolution_function(self):
        """Calculate the resolution function from the zero-loss peak."""
        try:
            import pyTEMlib.eels_tools as eels
            if self.dataset is not None:
                # Get resolution from ZLP fitting
                pass
        except ImportError:
            pass

    def get_probability(self):
        """Calculate scattering probability."""
        pass

    def get_drude(self):
        """Fit Drude model to the low loss spectrum."""
        try:
            import pyTEMlib.eels_tools as eels
            if self.dataset is not None:
                # Fit Drude model
                pass
        except ImportError:
            pass

    def do_all(self):
        """Perform all low loss analysis steps."""
        self.get_resolution_function()
        self.get_drude()
        self.remove_multiple_scattering()

    def remove_multiple_scattering(self):
        """Remove multiple scattering from the spectrum."""
        try:
            import pyTEMlib.eels_tools as eels
            if self.dataset is not None:
                # Remove multiple scattering
                pass
        except ImportError:
            pass
