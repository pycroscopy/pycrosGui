"""
#####################################################################
#
# Part of pycrosGUI
#
# ImageDialog: Image processing dialog.
#       - Image registration
#       - FFT filtering
#       - Deconvolution
#       - Stack processing
#
#####################################################################
"""
try:
    from PyQt6 import QtWidgets, QtGui
except ImportError:
    from PyQt5 import QtWidgets, QtGui

import numpy as np


class ImageDialog(QtWidgets.QWidget):
    """Image processing dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.set_energy = True
        layout = self.get_sidebar()
        self.atoms = None
        self.setLayout(layout)
        self.name = 'Image'
        self.setWindowTitle("Image")

        self.key = ''
        self.dataset = None
        self.fft_mag = None

    def get_sidebar(self):
        """Creates the sidebar layout for the image dialog."""
        validfloat = QtGui.QDoubleValidator()

        layout = QtWidgets.QGridLayout()
        row = 0

        # Dataset selection
        self.main_list = QtWidgets.QComboBox(self)
        self.main_list.addItem("None")
        layout.addWidget(self.main_list, row, 0, 1, 3)
        layout.setColumnStretch(0, 3)
        self.main_list.activated[str].connect(self.update_image_dataset)

        row += 1
        self.reg_button = QtWidgets.QPushButton()
        self.reg_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.reg_button.setText("Registration")
        layout.addWidget(self.reg_button, row, 0, 1, 3)
        layout.setColumnStretch(0, 3)

        row += 1
        self.rigid_reg_button = QtWidgets.QPushButton()
        self.rigid_reg_button.setText("Rigid Reg.")
        self.rigid_reg_button.setCheckable(True)
        layout.addWidget(self.rigid_reg_button, row, 0)
        self.rigid_reg_button.clicked.connect(self.rigid_registration)

        self.demon_reg_button = QtWidgets.QPushButton()
        self.demon_reg_button.setText("Demon Reg.")
        self.demon_reg_button.setCheckable(True)
        layout.addWidget(self.demon_reg_button, row, 1)
        self.demon_reg_button.clicked.connect(self.demon_registration)

        self.sum_button = QtWidgets.QPushButton()
        self.sum_button.setText("Sum")
        self.sum_button.setCheckable(True)
        layout.addWidget(self.sum_button, row, 2)
        self.sum_button.clicked.connect(self.sum_stack)

        row += 1
        self.average_button = QtWidgets.QPushButton()
        self.average_button.setText("Average")
        self.average_button.setCheckable(True)
        layout.addWidget(self.average_button, row, 0)
        self.average_button.clicked.connect(self.average_stack)

        row += 1
        self.fft_button = QtWidgets.QPushButton()
        self.fft_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.fft_button.setText("FFT")
        layout.addWidget(self.fft_button, row, 0, 1, 3)
        self.fft_button.clicked.connect(self.update_fft)

        row += 1
        self.resolution_label = QtWidgets.QLabel("Resolution")
        self.resolution_edit = QtWidgets.QLineEdit("0.0")
        self.resolution_edit.setValidator(validfloat)
        self.resolution_edit.editingFinished.connect(self.set_resolution)
        self.resolution_unit = QtWidgets.QLabel("Å")
        layout.addWidget(self.resolution_label, row, 0)
        layout.addWidget(self.resolution_edit, row, 1)
        layout.addWidget(self.resolution_unit, row, 2)

        row += 1
        self.decon_button = QtWidgets.QPushButton()
        self.decon_button.setText("LR Decon")
        self.decon_button.setCheckable(True)
        layout.addWidget(self.decon_button, row, 0)
        self.decon_button.clicked.connect(self.decon_lr)

        self.svd_button = QtWidgets.QPushButton()
        self.svd_button.setText("Simple Clean")
        self.svd_button.setCheckable(True)
        layout.addWidget(self.svd_button, row, 1)
        self.svd_button.clicked.connect(self.svd_clean)

        self.bgd_button = QtWidgets.QPushButton()
        self.bgd_button.setText("BGD Corr.")
        self.bgd_button.setCheckable(True)
        layout.addWidget(self.bgd_button, row, 2)
        self.bgd_button.clicked.connect(self.background_correction)

        row += 1
        self.filter_button = QtWidgets.QPushButton()
        self.filter_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.filter_button.setText("Adaptive Fourier Filter")
        layout.addWidget(self.filter_button, row, 0, 1, 3)
        self.filter_button.clicked.connect(self.adaptive_fourier_filter)

        row += 1
        self.add_mask_button = QtWidgets.QPushButton()
        self.add_mask_button.setText("Add Mask")
        self.add_mask_button.setCheckable(True)
        layout.addWidget(self.add_mask_button, row, 0)
        self.add_mask_button.clicked.connect(self.add_mask)

        self.clear_mask_button = QtWidgets.QPushButton()
        self.clear_mask_button.setText("Clear Masks")
        layout.addWidget(self.clear_mask_button, row, 1, 1, 2)
        self.clear_mask_button.clicked.connect(self.clear_masks)

        row += 1
        self.histogram_button = QtWidgets.QPushButton()
        self.histogram_button.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.histogram_button.setText("Histogram")
        layout.addWidget(self.histogram_button, row, 0, 1, 3)
        self.histogram_button.clicked.connect(self.show_histogram)

        row += 1
        self.contrast_label = QtWidgets.QLabel("Contrast")
        self.contrast_slider = QtWidgets.QSlider()
        self.contrast_slider.setOrientation(1)  # Horizontal
        self.contrast_slider.setRange(0, 100)
        self.contrast_slider.setValue(50)
        layout.addWidget(self.contrast_label, row, 0)
        layout.addWidget(self.contrast_slider, row, 1, 1, 2)

        row += 1
        self.brightness_label = QtWidgets.QLabel("Brightness")
        self.brightness_slider = QtWidgets.QSlider()
        self.brightness_slider.setOrientation(1)  # Horizontal
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(50)
        layout.addWidget(self.brightness_label, row, 0)
        layout.addWidget(self.brightness_slider, row, 1, 1, 2)

        # Add stretch to push everything up
        row += 1
        layout.setRowStretch(row, 1)

        return layout

    def update_sidebar(self):
        """Update the sidebar with the current image dataset."""
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
        """Update the image dataset based on the current selection."""
        item_text = self.main_list.currentText()
        if hasattr(self.parent, 'main'):
            self.parent.main = item_text.split(':')[0]
        if hasattr(self.parent, 'dataset') and self.parent.dataset is not None:
            self.dataset = self.parent.dataset

    def update_fft(self):
        """Update the FFT view with the current dataset."""
        if self.dataset is not None:
            try:
                self.fft_mag = np.abs(np.fft.fftshift(np.fft.fft2(self.dataset)))
            except Exception:
                pass

    def rigid_registration(self, value=0):
        """Perform rigid registration on the image stack."""
        try:
            import pyTEMlib.image_tools as image_tools
            if self.dataset is not None:
                if hasattr(self.dataset, 'data_type'):
                    if self.dataset.data_type.name == 'IMAGE_STACK':
                        # Perform rigid registration
                        pass
        except ImportError:
            pass
        self.rigid_reg_button.setChecked(False)

    def demon_registration(self, value=0):
        """Perform demon registration on the image stack."""
        try:
            import pyTEMlib.image_tools as image_tools
            if self.dataset is not None:
                if hasattr(self.dataset, 'data_type'):
                    if self.dataset.data_type.name == 'IMAGE_STACK':
                        # Perform demon registration
                        pass
        except ImportError:
            pass
        self.demon_reg_button.setChecked(False)

    def sum_stack(self, value=0):
        """Sum the image stack."""
        if self.dataset is not None:
            if hasattr(self.dataset, 'data_type'):
                if self.dataset.data_type.name == 'IMAGE_STACK':
                    # Sum stack
                    pass
        self.sum_button.setChecked(False)

    def average_stack(self, value=0):
        """Average the image stack."""
        if self.dataset is not None:
            if hasattr(self.dataset, 'data_type'):
                if self.dataset.data_type.name == 'IMAGE_STACK':
                    # Average stack
                    pass
        self.average_button.setChecked(False)

    def set_resolution(self):
        """Set the FFT resolution based on the user input."""
        pass

    def decon_lr(self):
        """Perform Lucy-Richardson deconvolution."""
        try:
            import pyTEMlib.image_tools as image_tools
            if self.dataset is not None:
                # LR deconvolution
                pass
        except ImportError:
            pass
        self.decon_button.setChecked(False)

    def svd_clean(self):
        """Perform SVD cleaning."""
        try:
            import pyTEMlib.image_tools as image_tools
            if self.dataset is not None:
                # SVD clean
                pass
        except ImportError:
            pass
        self.svd_button.setChecked(False)

    def background_correction(self):
        """Perform background correction."""
        self.bgd_button.setChecked(False)

    def adaptive_fourier_filter(self):
        """Apply an adaptive Fourier filter to the dataset."""
        try:
            import pyTEMlib.image_tools as image_tools
            if self.dataset is not None:
                # Adaptive Fourier filter
                pass
        except ImportError:
            pass

    def add_mask(self):
        """Add a mask to the FFT view."""
        pass

    def clear_masks(self):
        """Clear all masks from the FFT view."""
        pass

    def show_histogram(self):
        """Show histogram of the image."""
        pass

    def get_additional_features(self):
        """Get additional features for the plot."""
        additional_features = {}
        if self.atoms is not None:
            additional_features['atoms'] = self.atoms
        return additional_features
