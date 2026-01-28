"""
#####################################################################
#
# Part of pycrosGUI
#
# InfoDialog: Spectrum/dataset information dialog.
#       - Name
#       - Dimensions
#       - Offset
#       - Exposure Time
#       - Acceleration Voltage
#       - Collection Angle
#       - Convergence Angle
#       - Conversion Factor for CCD
#       - Flux of incident beam in #e- per second
#
#####################################################################
"""
try:
    from PyQt6 import QtWidgets, QtGui
except ImportError:
    from PyQt5 import QtWidgets, QtGui

import numpy as np


class InfoDialog(QtWidgets.QWidget):
    """Dialog to display and edit information about the dataset."""
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.set_energy = True
        layout = self.get_sidebar()
        self.setLayout(layout)
        self.name = 'Info'
        self.setWindowTitle(self.name)

        self.key = ''
        self.info_key = ''
        self.info_index = 0
        self.spectrum_data = np.array([])
        self.energy_scale = np.array([])

    def get_sidebar(self):
        """Create the sidebar layout for the info dialog."""
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
        self.experiment_button = QtWidgets.QPushButton()
        self.experiment_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.experiment_button.setText("Experimental Conditions")
        self.experiment_button.clicked.connect(self.show_metadata)
        layout.addWidget(self.experiment_button, row, 0, 1, 3)
        layout.setColumnStretch(0, 3)

        row += 1
        self.time_label = QtWidgets.QLabel("Exp. Time")
        self.time_edit = QtWidgets.QLineEdit("100.0")
        self.time_edit.setValidator(validfloat)
        self.time_edit.editingFinished.connect(self.on_expose_enter)
        self.time_unit = QtWidgets.QLabel("ms")
        layout.addWidget(self.time_label, row, 0)
        layout.addWidget(self.time_edit, row, 1)
        layout.addWidget(self.time_unit, row, 2)

        row += 1
        self.conv_label = QtWidgets.QLabel("Conv. Angle")
        self.conv_edit = QtWidgets.QLineEdit("30.0")
        self.conv_edit.setValidator(validfloat)
        self.conv_edit.editingFinished.connect(self.on_conv_enter)
        self.conv_unit = QtWidgets.QLabel("mrad")
        layout.addWidget(self.conv_label, row, 0)
        layout.addWidget(self.conv_edit, row, 1)
        layout.addWidget(self.conv_unit, row, 2)

        row += 1
        self.coll_label = QtWidgets.QLabel("Coll. Angle")
        self.coll_edit = QtWidgets.QLineEdit("50.0")
        self.coll_edit.setValidator(validfloat)
        self.coll_edit.editingFinished.connect(self.on_coll_enter)
        self.coll_unit = QtWidgets.QLabel("mrad")
        layout.addWidget(self.coll_label, row, 0)
        layout.addWidget(self.coll_edit, row, 1)
        layout.addWidget(self.coll_unit, row, 2)

        row += 1
        self.acc_label = QtWidgets.QLabel("Acc. Voltage")
        self.acc_edit = QtWidgets.QLineEdit("200.0")
        self.acc_edit.setValidator(validfloat)
        self.acc_edit.editingFinished.connect(self.on_acc_enter)
        self.acc_unit = QtWidgets.QLabel("kV")
        layout.addWidget(self.acc_label, row, 0)
        layout.addWidget(self.acc_edit, row, 1)
        layout.addWidget(self.acc_unit, row, 2)

        row += 1
        self.dispersion_label = QtWidgets.QLabel("Dispersion")
        self.dispersion_edit = QtWidgets.QLineEdit("0.1")
        self.dispersion_edit.setValidator(validfloat)
        self.dispersion_edit.editingFinished.connect(self.on_dispersion_enter)
        self.dispersion_unit = QtWidgets.QLabel("eV/ch")
        layout.addWidget(self.dispersion_label, row, 0)
        layout.addWidget(self.dispersion_edit, row, 1)
        layout.addWidget(self.dispersion_unit, row, 2)

        row += 1
        self.offset_label = QtWidgets.QLabel("Offset")
        self.offset_edit = QtWidgets.QLineEdit("0.0")
        self.offset_edit.setValidator(validfloat)
        self.offset_edit.editingFinished.connect(self.on_offset_enter)
        self.offset_unit = QtWidgets.QLabel("eV")
        layout.addWidget(self.offset_label, row, 0)
        layout.addWidget(self.offset_edit, row, 1)
        layout.addWidget(self.offset_unit, row, 2)

        row += 1
        self.shift_label = QtWidgets.QLabel("Shift")
        self.shift_edit = QtWidgets.QLineEdit("0.0")
        self.shift_edit.setValidator(validfloat)
        self.shift_unit = QtWidgets.QLabel("eV")
        layout.addWidget(self.shift_label, row, 0)
        layout.addWidget(self.shift_edit, row, 1)
        layout.addWidget(self.shift_unit, row, 2)

        row += 1
        self.get_shift_button = QtWidgets.QPushButton()
        self.get_shift_button.setText("Get Shift")
        self.get_shift_button.setCheckable(True)
        layout.addWidget(self.get_shift_button, row, 0)
        self.get_shift_button.clicked.connect(self.get_shift)

        self.set_shift_button = QtWidgets.QPushButton()
        self.set_shift_button.setText("Apply Shift")
        self.set_shift_button.setCheckable(False)
        layout.addWidget(self.set_shift_button, row, 1, 1, 2)
        self.set_shift_button.clicked.connect(self.shift_spectrum)

        row += 1
        self.flux_ppm_label = QtWidgets.QLabel("Relative Flux")
        self.flux_ppm_edit = QtWidgets.QLineEdit("1")
        self.flux_ppm_edit.setValidator(validfloat)
        self.flux_ppm_edit.editingFinished.connect(self.on_flux_ppm_enter)
        self.flux_ppm_unit = QtWidgets.QLabel("ppm")
        layout.addWidget(self.flux_ppm_label, row, 0)
        layout.addWidget(self.flux_ppm_edit, row, 1)
        layout.addWidget(self.flux_ppm_unit, row, 2)

        row += 1
        self.conversion_label = QtWidgets.QLabel("Conversion")
        self.conversion_edit = QtWidgets.QLineEdit("25.0")
        self.conversion_edit.setValidator(validfloat)
        self.conversion_edit.editingFinished.connect(self.on_conversion_enter)
        self.conversion_unit = QtWidgets.QLabel("e-/counts")
        layout.addWidget(self.conversion_label, row, 0)
        layout.addWidget(self.conversion_edit, row, 1)
        layout.addWidget(self.conversion_unit, row, 2)

        row += 1
        self.intensity_button = QtWidgets.QPushButton()
        self.intensity_button.setText("Intensity Scale")
        self.intensity_button.setCheckable(True)
        layout.addWidget(self.intensity_button, row, 0, 1, 3)
        self.intensity_button.clicked.connect(self.set_intensity_scale)

        # Add stretch to push everything up
        row += 1
        layout.setRowStretch(row, 1)

        return layout

    def set_dataset(self, text=None):
        """Set the main dataset."""
        if text:
            item_text = text
        else:
            item_text = self.main_list.currentText()
        if hasattr(self.parent, 'main'):
            self.parent.main = item_text.split(':')[0]
        self.update_info()

    def show_metadata(self):
        """Show metadata dialog."""
        if hasattr(self.parent, 'show_metadata'):
            self.parent.show_metadata()

    def update_sidebar(self):
        """Update the sidebar information."""
        self.update_info()

    def update_info(self):
        """Update the information displayed in the dialog."""
        if not hasattr(self.parent, 'dataset') or self.parent.dataset is None:
            return

        dataset = self.parent.dataset

        # Update exposure time if available
        if hasattr(dataset, 'metadata') and 'experiment' in dataset.metadata:
            exp = dataset.metadata['experiment']
            if 'exposure_time' in exp:
                self.time_edit.setText(f"{exp['exposure_time']:.3f}")
            if 'convergence_angle' in exp:
                self.conv_edit.setText(f"{exp['convergence_angle']:.2f}")
            if 'collection_angle' in exp:
                self.coll_edit.setText(f"{exp['collection_angle']:.2f}")
            if 'acceleration_voltage' in exp:
                self.acc_edit.setText(f"{exp['acceleration_voltage']/1000:.1f}")

    def on_expose_enter(self):
        """Handle exposure time change."""
        try:
            value = float(self.time_edit.text())
            if hasattr(self.parent, 'dataset') and self.parent.dataset is not None:
                if 'experiment' not in self.parent.dataset.metadata:
                    self.parent.dataset.metadata['experiment'] = {}
                self.parent.dataset.metadata['experiment']['exposure_time'] = value
        except ValueError:
            pass

    def on_conv_enter(self):
        """Handle convergence angle change."""
        try:
            value = float(self.conv_edit.text())
            if hasattr(self.parent, 'dataset') and self.parent.dataset is not None:
                if 'experiment' not in self.parent.dataset.metadata:
                    self.parent.dataset.metadata['experiment'] = {}
                self.parent.dataset.metadata['experiment']['convergence_angle'] = value
        except ValueError:
            pass

    def on_coll_enter(self):
        """Handle collection angle change."""
        try:
            value = float(self.coll_edit.text())
            if hasattr(self.parent, 'dataset') and self.parent.dataset is not None:
                if 'experiment' not in self.parent.dataset.metadata:
                    self.parent.dataset.metadata['experiment'] = {}
                self.parent.dataset.metadata['experiment']['collection_angle'] = value
        except ValueError:
            pass

    def on_acc_enter(self):
        """Handle acceleration voltage change."""
        try:
            value = float(self.acc_edit.text()) * 1000  # Convert kV to V
            if hasattr(self.parent, 'dataset') and self.parent.dataset is not None:
                if 'experiment' not in self.parent.dataset.metadata:
                    self.parent.dataset.metadata['experiment'] = {}
                self.parent.dataset.metadata['experiment']['acceleration_voltage'] = value
        except ValueError:
            pass

    def on_dispersion_enter(self):
        """Handle dispersion change."""
        try:
            value = float(self.dispersion_edit.text())
            if hasattr(self.parent, 'dataset') and self.parent.dataset is not None:
                # Update spectral dimension scale
                pass
        except ValueError:
            pass

    def on_offset_enter(self):
        """Handle offset change."""
        try:
            value = float(self.offset_edit.text())
            if hasattr(self.parent, 'dataset') and self.parent.dataset is not None:
                # Update spectral dimension offset
                pass
        except ValueError:
            pass

    def on_flux_ppm_enter(self):
        """Handle flux ppm change."""
        pass

    def on_conversion_enter(self):
        """Handle conversion factor change."""
        pass

    def get_shift(self, value=0):
        """Get the current shift value from cursor."""
        pass

    def shift_spectrum(self, value=0):
        """Apply shift to spectrum."""
        try:
            shift = float(self.shift_edit.text())
            if hasattr(self.parent, 'dataset') and self.parent.dataset is not None:
                # Apply shift to energy scale
                pass
        except ValueError:
            pass

    def set_intensity_scale(self, checked):
        """Set the intensity scale for the current dataset."""
        pass
