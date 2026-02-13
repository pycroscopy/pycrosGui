"""
#####################################################################
#
# Part of pycrosGui - Data Dialog with modern styling
#####################################################################
"""

try:
    from PyQt6 import QtWidgets, QtCore
    ShiftModifier = QtCore.Qt.KeyboardModifier.ShiftModifier
    ControlModifier = QtCore.Qt.KeyboardModifier.ControlModifier
except ImportError:
    from PyQt5 import QtWidgets
    from PyQt5 import QtCore
    ShiftModifier = QtCore.Qt.ShiftModifier
    ControlModifier = QtCore.Qt.ControlModifier


# Consistent color palette
COLORS = {
    'primary': '#3498db',
    'primary_hover': '#2980b9',
    'secondary': '#2c3e50',
    'background': '#f8f9fa',
    'text': '#2c3e50',
    'text_light': '#7f8c8d',
    'border': '#bdc3c7',
    'success': '#27ae60',
    'danger': '#e74c3c',
    'warning': '#f39c12',
}


class DataDialog(QtWidgets.QWidget):
    """Data dialog for displaying and managing data with modern styling."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent

        layout = self.get_sidbar()
        self.setLayout(layout)
        self.name = 'Data'
        self.setWindowTitle(self.name)
        
        # Apply modern styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
            }}
            QLabel {{
                color: {COLORS['text']};
                font-weight: bold;
                font-size: 12px;
                padding: 5px 0;
            }}
            QListWidget {{
                background-color: white;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 5px;
                color: {COLORS['text']};
                font-size: 11px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QListWidget::item:hover:!selected {{
                background-color: #ecf0f1;
            }}
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: #1f6aa5;
            }}
        """)

    def get_sidbar(self):
        """Create the sidebar layout."""
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Spectral Data section
        label = QtWidgets.QLabel("Spectral Data")
        layout.addWidget(label)
        
        self.spectrum_list = QtWidgets.QListWidget()
        self.spectrum_list.addItems(["None"])
        self.spectrum_list.setMinimumHeight(80)
        layout.addWidget(self.spectrum_list)
        self.spectrum_list.itemClicked.connect(self.plot_update)

        # Survey Data section
        label = QtWidgets.QLabel("Survey Data")
        layout.addWidget(label)
        
        self.survey_list = QtWidgets.QListWidget()
        self.survey_list.addItems(["None"])
        self.survey_list.setMinimumHeight(80)
        layout.addWidget(self.survey_list)
        self.survey_list.itemClicked.connect(self.plot_update)

        # Image Data section
        label = QtWidgets.QLabel("Image Data")
        layout.addWidget(label)
        
        self.image_list = QtWidgets.QListWidget()
        self.image_list.addItems(["None"])
        self.image_list.setMinimumHeight(80)
        layout.addWidget(self.image_list)
        self.image_list.itemClicked.connect(self.plot_update)

        # Structures section
        label = QtWidgets.QLabel("Structures")
        layout.addWidget(label)
        
        self.structure_list = QtWidgets.QListWidget()
        self.structure_list.addItems(["None"])
        self.structure_list.setMinimumHeight(80)
        layout.addWidget(self.structure_list)

        layout.addStretch()

        # Button row
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.clear_button = QtWidgets.QPushButton("Clear All")
        self.clear_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
            }}
            QPushButton:hover {{
                background-color: #c0392b;
            }}
        """)
        self.clear_button.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.clear_button)

        self.remove_button = QtWidgets.QPushButton("Remove")
        self.remove_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['warning']};
            }}
            QPushButton:hover {{
                background-color: #e67e22;
            }}
        """)
        self.remove_button.clicked.connect(self.remove)
        btn_layout.addWidget(self.remove_button)

        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
            }}
            QPushButton:hover {{
                background-color: #219a52;
            }}
        """)
        self.save_button.clicked.connect(self.parent.save_file)
        btn_layout.addWidget(self.save_button)
        
        layout.addLayout(btn_layout)
        
        return layout

    def update_sidebar(self):
        """Update the sidebar with the current dataset information."""
        pass

    def clear_all(self):
        """Clear all data from the dialog."""
        self.parent.datasets = {}
        self.spectrum_list.clear()
        self.survey_list.clear()
        self.image_list.clear()
        self.structure_list.clear()
        self.spectrum_list.addItem("None")
        self.survey_list.addItem("None")
        self.image_list.addItem("None")
        self.structure_list.addItem("None")

        self.parent.main = ""

        self.parent.update_DataDialog()
        self.spectrum_list.update()
        self.survey_list.update()
        self.image_list.update()
        self.structure_list.update()
        self.parent.plot_update()

    def remove(self):
        """Remove the selected item from the list."""
        pass

    def plot_update(self, item):
        """Update the plot based on the selected item."""
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        list_widget = item.listWidget()
        if self.parent.dataset is not None:
            if self.parent.dataset.data_type.name == 'SPECTRUM':

                if modifiers == ShiftModifier:
                    self.parent.add_spectrum.append(item.text().split(':')[0])
                    self.parent.plot_update()
                    return

        if modifiers == ControlModifier:
            del self.parent.datasets[item.text().split(':')[0]]

            row = list_widget.row(item)-1
            list_widget.clear()

            self.parent.update_DataDialog()
            if list_widget.count() == 0:
                list_widget.addItem("None")
                return
            list_widget.setCurrentRow(row)
        item = list_widget.currentItem()
        if item.text() == "None":
            return

        self.parent.add_spectrum = []
        self.parent.main = item.text().split(':')[0]
        self.parent.set_dataset()
        self.parent.plot_update()
        # self.parent.InfoDialog.updateInfo()
