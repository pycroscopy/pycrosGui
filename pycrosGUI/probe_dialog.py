"""
#####################################################################
#
# Part of pycrosGUI
#
# ProbeDialog: Probe/aberration settings dialog.
#       - Aberration coefficients
#       - Probe simulation
#       - Ronchigram simulation
#
#####################################################################
"""
try:
    from PyQt6 import QtWidgets, QtGui
except ImportError:
    from PyQt5 import QtWidgets, QtGui

import numpy as np


class ProbeDialog(QtWidgets.QWidget):
    """Dialog for probe settings and aberration control."""
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.aberrations = {
            'C10': 0, 'C12a': 0, 'C12b': 0,
            'C21a': 0, 'C21b': 0,
            'C23a': 0, 'C23b': 0,
            'C30': 0,
            'C32a': 0, 'C32b': 0,
            'C34a': 0, 'C34b': 0,
            'C41a': 0, 'C41b': 0,
            'C43a': 0, 'C43b': 0,
            'C45a': 0, 'C45b': 0,
            'C50': 0, 'C52a': 0, 'C52b': 0, 
            'C54a': 0, 'C54b': 0,
            'C56a': 0, 'C56b': 0,
            'Cc': 0, 'dE': 0
        }

        layout = self.get_sidebar()
        self.atoms = None
        self.setLayout(layout)
        self.name = 'Probe'
        self.setWindowTitle(self.name)
        self.key = None

    def get_sidebar(self):
        """Create the sidebar layout."""
        validfloat = QtGui.QDoubleValidator()

        layout = QtWidgets.QGridLayout()
        row = 0

        # Microscope preset selection
        self.main_list = QtWidgets.QComboBox(self)
        self.main_list.addItems(['None', 'Microscope', 'Spectra300', 'Zeiss200',
                                 'Nion US200', 'Nion US100'])
        layout.addWidget(self.main_list, row, 0, 1, 4)
        layout.setColumnStretch(0, 4)

        row += 1
        self.aberration_button = QtWidgets.QPushButton()
        self.aberration_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.aberration_button.setText("Aberrations")
        layout.addWidget(self.aberration_button, row, 0, 1, 4)
        layout.setColumnStretch(0, 3)

        row += 1
        radiobutton = QtWidgets.QRadioButton("Nion")
        radiobutton.setChecked(True)
        radiobutton.convention = "Nion"
        layout.addWidget(radiobutton, row, 0, 1, 2)

        radiobutton = QtWidgets.QRadioButton("Ceos")
        radiobutton.convention = "Ceos"
        layout.addWidget(radiobutton, row, 2, 1, 2)

        row += 1
        # Add aberration coefficient inputs
        self.a_edit = []
        aberr_keys = ['C10', 'C12a', 'C12b', 'C21a', 'C21b', 'C23a', 'C23b', 
                      'C30', 'C32a', 'C32b', 'C34a', 'C34b']
        
        for i, key in enumerate(aberr_keys):
            if i % 2 == 0:
                row += 1
            col = (i % 2) * 2
            
            a_label = QtWidgets.QLabel(key)
            a_edit = QtWidgets.QLineEdit(f"{self.aberrations.get(key, 0):.1f}")
            a_edit.setValidator(validfloat)
            a_edit.editingFinished.connect(self.on_aberr_enter)
            self.a_edit.append(a_edit)
            
            layout.addWidget(a_label, row, col)
            layout.addWidget(a_edit, row, col + 1)

        row += 1
        self.process_button = QtWidgets.QPushButton()
        self.process_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.process_button.setText("Process")
        layout.addWidget(self.process_button, row, 0, 1, 4)
        layout.setColumnStretch(0, 3)

        row += 1
        self.process_list = QtWidgets.QComboBox()
        self.process_list.setEditable(False)
        self.process_list.addItems(['Gauss Probe', 'Real Probe', 'Ronchigram'])
        self.process_list.activated[str].connect(self.on_process_select)
        layout.addWidget(self.process_list, row, 0, 1, 4)

        row += 1
        self.cluster_button = QtWidgets.QPushButton()
        self.cluster_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.cluster_button.setText("Cluster Tools")
        layout.addWidget(self.cluster_button, row, 0, 1, 4)

        row += 1
        self.convergence_label = QtWidgets.QLabel("Conv. Angle")
        self.convergence_edit = QtWidgets.QLineEdit("30.0")
        self.convergence_edit.setValidator(validfloat)
        self.convergence_unit = QtWidgets.QLabel("mrad")
        layout.addWidget(self.convergence_label, row, 0)
        layout.addWidget(self.convergence_edit, row, 1, 1, 2)
        layout.addWidget(self.convergence_unit, row, 3)

        row += 1
        self.voltage_label = QtWidgets.QLabel("Acc. Voltage")
        self.voltage_edit = QtWidgets.QLineEdit("200.0")
        self.voltage_edit.setValidator(validfloat)
        self.voltage_unit = QtWidgets.QLabel("kV")
        layout.addWidget(self.voltage_label, row, 0)
        layout.addWidget(self.voltage_edit, row, 1, 1, 2)
        layout.addWidget(self.voltage_unit, row, 3)

        row += 1
        self.simulate_button = QtWidgets.QPushButton()
        self.simulate_button.setStyleSheet('QPushButton {background-color: green; color: white;}')
        self.simulate_button.setText("Simulate Probe")
        layout.addWidget(self.simulate_button, row, 0, 1, 4)
        self.simulate_button.clicked.connect(self.simulate_probe)

        # Add stretch to push everything up
        row += 1
        layout.setRowStretch(row, 1)

        return layout

    def update_sidebar(self):
        """Update the sidebar with the current image list."""
        pass

    def on_process_select(self, text):
        """Handle process selection changes."""
        pass

    def on_aberr_enter(self):
        """Handle aberration entry."""
        # Update aberration values from edit fields
        aberr_keys = ['C10', 'C12a', 'C12b', 'C21a', 'C21b', 'C23a', 'C23b', 
                      'C30', 'C32a', 'C32b', 'C34a', 'C34b']
        for i, key in enumerate(aberr_keys):
            if i < len(self.a_edit):
                try:
                    self.aberrations[key] = float(self.a_edit[i].text())
                except ValueError:
                    pass

    def simulate_probe(self):
        """Simulate the probe based on current aberrations."""
        try:
            import pyTEMlib.probe_tools as probe_tools
            convergence = float(self.convergence_edit.text())
            voltage = float(self.voltage_edit.text()) * 1000  # Convert to V
            # Simulate probe
            pass
        except ImportError:
            pass
        except ValueError:
            pass

    def copy_atoms_to(self):
        """Copy selected atoms to a new location."""
        pass

    def get_additional_features(self):
        """Get additional features for the plot."""
        additional_features = {}
        return additional_features
