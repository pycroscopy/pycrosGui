"""
#####################################################################
#
# Part of pycrosGui
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

class DataDialog(QtWidgets.QWidget):
    """Data dialog for displaying and managing data."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent

        layout = self.get_sidbar()
        self.setLayout(layout)
        self.name = 'Data'
        self.setWindowTitle(self.name)

    def get_sidbar(self):
        """Create the sidebar layout."""
        layout = QtWidgets.QGridLayout()

        row = 0
        label = QtWidgets.QLabel("Spectral Data")
        layout.addWidget(label, row, 0)

        row += 1
        self.spectrum_list = QtWidgets.QListWidget()
        self.spectrum_list.addItems(["None"])
        layout.addWidget(self.spectrum_list, row, 0, 1, 3)
        self.spectrum_list.itemClicked.connect(self.plot_update)

        row += 1
        label = QtWidgets.QLabel("Survey Data")
        layout.addWidget(label, row, 0)
        row += 1
        self.survey_list = QtWidgets.QListWidget()
        self.survey_list.addItems(["None"])
        layout.addWidget(self.survey_list,  row, 0, 1, 3)
        self.survey_list.itemClicked.connect(self.plot_update)

        row += 1
        label =  QtWidgets.QLabel("Image Data")
        layout.addWidget(label,  row, 0)

        row += 1
        self.image_list = QtWidgets.QListWidget()
        self.image_list.addItems(["None"])
        layout.addWidget(self.image_list,  row, 0, 1, 3)
        self.image_list.itemClicked.connect(self.plot_update)

        row += 1
        label =  QtWidgets.QLabel("Structures")
        layout.addWidget(label,  row, 0)

        row += 1
        self.structure_list = QtWidgets.QListWidget()
        self.structure_list.addItems(["None"])
        layout.addWidget(self.structure_list,  row, 0, 1, 3)
        #self.structure_list.itemClicked.connect(self.plot_update)

        row += 1
        self.clear_button = QtWidgets.QPushButton()
        self.clear_button.setText("Clear All")
        self.clear_button.setCheckable(False)
        layout.addWidget(self.clear_button,  row, 0)
        self.clear_button.clicked.connect(self.clear_all)

        self.remove_button = QtWidgets.QPushButton()
        self.remove_button.setText("Remove")
        self.remove_button.setCheckable(False)
        layout.addWidget(self.remove_button,  row, 1)
        self.remove_button.clicked.connect(self.remove)

        self.save_button = QtWidgets.QPushButton()
        self.save_button.setText("Save")
        self.save_button.setCheckable(False)
        layout.addWidget(self.save_button,  row, 1)
        self.save_button.clicked.connect(self.parent.save_file)
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
