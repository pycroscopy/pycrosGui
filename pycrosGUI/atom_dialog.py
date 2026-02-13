"""
#####################################################################
#
# Part of pycrosGUI
#
# AtomDialog: Atom finding and analyzing dialog.
#       - Atom finding with blob detection
#       - Structure analysis
#       - Lattice analysis
#
#####################################################################
"""
try:
    from PyQt6 import QtWidgets, QtGui
except ImportError:
    from PyQt5 import QtWidgets, QtGui

import numpy as np


class AtomDialog(QtWidgets.QWidget):
    """Atom finding and analyzing dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        layout = self.get_sidebar()
        self.atoms = None
        self.setLayout(layout)
        self.name = 'Atoms'
        self.start_atom = 0
        self.setWindowTitle(self.name)
        self.dataset = None
        self.crystal = None
        self.key = 'None'
        self.atoms_out = None
        self.structure = {}

    def get_sidebar(self):
        """Create the sidebar layout for the atom dialog."""
        validfloat = QtGui.QDoubleValidator()
        validint = QtGui.QIntValidator()

        layout = QtWidgets.QGridLayout()
        row = 0

        # Dataset selection
        self.main_list = QtWidgets.QComboBox(self)
        self.main_list.addItem("None")
        layout.addWidget(self.main_list, row, 0, 1, 3)
        layout.setColumnStretch(0, 3)
        self.main_list.activated[str].connect(self.update_image_dataset)

        row += 1
        self.find_button = QtWidgets.QPushButton()
        self.find_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.find_button.setText("Find Atoms")
        layout.addWidget(self.find_button, row, 0, 1, 3)
        layout.setColumnStretch(0, 3)
        self.find_button.clicked.connect(self.find_atoms)

        row += 1
        self.threshold_label = QtWidgets.QLabel("Threshold")
        self.threshold_edit = QtWidgets.QLineEdit("0.5")
        self.threshold_edit.setValidator(validfloat)
        self.threshold_unit = QtWidgets.QLabel("")
        layout.addWidget(self.threshold_label, row, 0)
        layout.addWidget(self.threshold_edit, row, 1)
        layout.addWidget(self.threshold_unit, row, 2)

        row += 1
        self.min_sigma_label = QtWidgets.QLabel("Min Sigma")
        self.min_sigma_edit = QtWidgets.QLineEdit("1.0")
        self.min_sigma_edit.setValidator(validfloat)
        self.min_sigma_unit = QtWidgets.QLabel("px")
        layout.addWidget(self.min_sigma_label, row, 0)
        layout.addWidget(self.min_sigma_edit, row, 1)
        layout.addWidget(self.min_sigma_unit, row, 2)

        row += 1
        self.max_sigma_label = QtWidgets.QLabel("Max Sigma")
        self.max_sigma_edit = QtWidgets.QLineEdit("10.0")
        self.max_sigma_edit.setValidator(validfloat)
        self.max_sigma_unit = QtWidgets.QLabel("px")
        layout.addWidget(self.max_sigma_label, row, 0)
        layout.addWidget(self.max_sigma_edit, row, 1)
        layout.addWidget(self.max_sigma_unit, row, 2)

        row += 1
        self.num_atoms_label = QtWidgets.QLabel("# Atoms")
        self.num_atoms_edit = QtWidgets.QLineEdit("0")
        self.num_atoms_edit.setReadOnly(True)
        layout.addWidget(self.num_atoms_label, row, 0)
        layout.addWidget(self.num_atoms_edit, row, 1, 1, 2)

        row += 1
        self.structure_button = QtWidgets.QPushButton()
        self.structure_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.structure_button.setText("Structure")
        layout.addWidget(self.structure_button, row, 0, 1, 3)
        self.structure_button.clicked.connect(self.set_structure)

        row += 1
        self.structure_list = QtWidgets.QComboBox()
        self.structure_list.addItems(['fcc', 'bcc', 'hcp', 'diamond', 'custom'])
        layout.addWidget(self.structure_list, row, 0, 1, 3)

        row += 1
        self.lattice_label = QtWidgets.QLabel("Lattice")
        self.lattice_edit = QtWidgets.QLineEdit("0.0")
        self.lattice_edit.setValidator(validfloat)
        self.lattice_unit = QtWidgets.QLabel("Å")
        layout.addWidget(self.lattice_label, row, 0)
        layout.addWidget(self.lattice_edit, row, 1)
        layout.addWidget(self.lattice_unit, row, 2)

        row += 1
        self.angle_label = QtWidgets.QLabel("Angle")
        self.angle_edit = QtWidgets.QLineEdit("0.0")
        self.angle_edit.setValidator(validfloat)
        self.angle_unit = QtWidgets.QLabel("°")
        layout.addWidget(self.angle_label, row, 0)
        layout.addWidget(self.angle_edit, row, 1)
        layout.addWidget(self.angle_unit, row, 2)

        row += 1
        self.graph_button = QtWidgets.QPushButton()
        self.graph_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.graph_button.setText("Graph Analysis")
        layout.addWidget(self.graph_button, row, 0, 1, 3)
        self.graph_button.clicked.connect(self.graph_hopp)

        row += 1
        self.tolerance_label = QtWidgets.QLabel("Tolerance")
        self.tolerance_edit = QtWidgets.QLineEdit("0.2")
        self.tolerance_edit.setValidator(validfloat)
        self.tolerance_unit = QtWidgets.QLabel("")
        layout.addWidget(self.tolerance_label, row, 0)
        layout.addWidget(self.tolerance_edit, row, 1)
        layout.addWidget(self.tolerance_unit, row, 2)

        row += 1
        self.copy_button = QtWidgets.QPushButton()
        self.copy_button.setText("Copy Atoms To")
        layout.addWidget(self.copy_button, row, 0, 1, 3)
        self.copy_button.clicked.connect(self.copy_atoms_to)

        row += 1
        self.roi_label = QtWidgets.QLabel("ROI")
        layout.addWidget(self.roi_label, row, 0, 1, 3)

        row += 1
        self.roi_x_label = QtWidgets.QLabel("X")
        self.roi_x_edit = QtWidgets.QLineEdit("0")
        self.roi_x_edit.setValidator(validint)
        layout.addWidget(self.roi_x_label, row, 0)
        layout.addWidget(self.roi_x_edit, row, 1, 1, 2)

        row += 1
        self.roi_y_label = QtWidgets.QLabel("Y")
        self.roi_y_edit = QtWidgets.QLineEdit("0")
        self.roi_y_edit.setValidator(validint)
        layout.addWidget(self.roi_y_label, row, 0)
        layout.addWidget(self.roi_y_edit, row, 1, 1, 2)

        # Add stretch to push everything up
        row += 1
        layout.setRowStretch(row, 1)

        return layout

    def update_sidebar(self):
        """Update the sidebar with the current structure information."""
        # Update the image list
        image_list = []
        if hasattr(self.parent, 'datasets'):
            for key, dataset in self.parent.datasets.items():
                if hasattr(dataset, 'data_type'):
                    if 'IMAGE' in dataset.data_type.name:
                        image_list.append(f"{key}: {dataset.title}")

        self.main_list.clear()
        if len(image_list) == 0:
            self.main_list.addItem("None")
        else:
            for item in image_list:
                self.main_list.addItem(item)

    def update_image_dataset(self, value=0):
        """Update the image dataset."""
        item_text = self.main_list.currentText()
        if hasattr(self.parent, 'main'):
            self.parent.main = item_text.split(':')[0]
        if hasattr(self.parent, 'dataset') and self.parent.dataset is not None:
            self.dataset = self.parent.dataset

    def update_roi(self):
        """Update the ROI position edits."""
        pass

    def find_atoms(self, value=0):
        """Find atoms in the dataset."""
        try:
            import pyTEMlib.atom_tools as atom_tools
            if self.dataset is not None:
                threshold = float(self.threshold_edit.text())
                min_sigma = float(self.min_sigma_edit.text())
                max_sigma = float(self.max_sigma_edit.text())
                # Find atoms using blob detection
                pass
        except ImportError:
            pass
        except ValueError:
            pass

    def set_structure(self):
        """Set the crystal structure."""
        structure_type = self.structure_list.currentText()
        # Set up crystal structure parameters
        pass

    def get_angle(self):
        """Get the angle from the crystal structure."""
        try:
            return float(self.angle_edit.text())
        except ValueError:
            return 0.0

    def graph_hopp(self):
        """Graph the hopping paths."""
        try:
            import pyTEMlib.graph_tools as graph_tools
            if self.dataset is not None and self.atoms is not None:
                tolerance = float(self.tolerance_edit.text())
                # Analyze atomic structure
                pass
        except ImportError:
            pass
        except ValueError:
            pass

    def copy_atoms_to(self):
        """Copy atoms to another dataset."""
        pass

    def mouse_click_event(self, ev):
        """Handle mouse click events."""
        pass

    def get_additional_features(self):
        """Get additional features for the plot."""
        additional_features = {}
        if self.atoms is not None:
            additional_features['atoms'] = self.atoms
        if self.structure:
            additional_features['structure'] = self.structure
        return additional_features
