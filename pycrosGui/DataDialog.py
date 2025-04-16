#####################################################################
#
# Part of Quantifit
#
# SpecInfoDialog: Spectrum information dialog.
#       - Name
#       - Disperison
#       - Offset
#       - Exposure Time
#       - Acceleration Voltage
#       - Collection Angle
#       - Convergence Angle
#       - Binning
#       - Conversion Factor for CCD
#       - Flux of incident beam in #e- per second
#       - VOA: current of a secondary measure of beam current in nA
#           (here virtual objective aperture)
#           ** changed to reflect Libra and pA ** Nov 2012
#       
#####################################################################
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore

import os as os
import numpy as np

class DataDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(DataDialog, self).__init__(parent)
    
        self.parent = parent
        
        layout = self.get_sidbar()
        self.setLayout(layout)    
        self.name = 'Data'
        self.setWindowTitle(self.name)

    def get_sidbar(self): 
        layout = QtWidgets.QGridLayout()

        row = 0 
        label =  QtWidgets.QLabel("Spectral Data")
        layout.addWidget(label,  row, 0)

        row += 1
        self.spectrum_list = QtWidgets.QListWidget()
        self.spectrum_list.addItems(["None"])
        layout.addWidget(self.spectrum_list,  row, 0, 1, 3)
        self.spectrum_list.itemClicked.connect(self.plotUpdate)
        
        row += 1
        label =  QtWidgets.QLabel("Survey Data")
        layout.addWidget(label,  row, 0)
        row += 1
        self.survey_list = QtWidgets.QListWidget()
        self.survey_list.addItems(["None"])
        layout.addWidget(self.survey_list,  row, 0, 1, 3)
        self.survey_list.itemClicked.connect(self.plotUpdate)
        
        row += 1
        label =  QtWidgets.QLabel("Image Data")
        layout.addWidget(label,  row, 0)
        row += 1
        self.image_list = QtWidgets.QListWidget()
        self.image_list.addItems(["None"])
        layout.addWidget(self.image_list,  row, 0, 1, 3)
        self.image_list.itemClicked.connect(self.plotUpdate)
        
        row += 1
        label =  QtWidgets.QLabel("Structures")
        layout.addWidget(label,  row, 0)
        row += 1
        self.structure_list = QtWidgets.QListWidget()
        self.structure_list.addItems(["None"])
        layout.addWidget(self.structure_list,  row, 0, 1, 3)
        #self.structure_list.itemClicked.connect(self.plotUpdate)
        row += 1
        
        row += 1
        self.clearButton = QtWidgets.QPushButton()
        self.clearButton.setText("Clear All")
        self.clearButton.setCheckable(False)
        layout.addWidget(self.clearButton,  row, 0)
        self.clearButton.clicked.connect(self.clear_all)
        
        self.removeButton = QtWidgets.QPushButton()
        self.removeButton.setText("Remove")
        self.removeButton.setCheckable(False)
        layout.addWidget(self.removeButton,  row, 1)
        self.removeButton.clicked.connect(self.remove)

        self.saveButton = QtWidgets.QPushButton()
        self.saveButton.setText("Save")
        self.saveButton.setCheckable(False)
        layout.addWidget(self.saveButton,  row, 1)
        self.saveButton.clicked.connect(self.parent.save_file)
        return layout
    


    def update_sidebar(self):
        pass

    def clear_all(self):
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
        self.parent.plotUpdate()
        
    def remove(self):
        pass

    def plotUpdate(self, item):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        list_widget = item.listWidget()
        if self.parent.dataset is not None:
            if self.parent.dataset.data_type.name == 'SPECTRUM':
                
                if modifiers == QtGui.Qt.ShiftModifier:
                    self.parent.add_spectrum.append(item.text().split(':')[0])
                    self.parent.plotUpdate()
                    return
                
        
        if modifiers == QtCore.Qt.ControlModifier:
            del self.parent.datasets[item.text().split(':')[0]]
            
            row = list_widget.row(item)-1
            list_widget.clear()
            
            self.parent.update_DataDialog()
            if list_widget.count() == 0:
                list_widget.addItem("None")
                return
            else:
                list_widget.setCurrentRow(row)
        item = list_widget.currentItem()
        if item.text() == "None":
            return
            
        self.parent.add_spectrum = []
        self.parent.main = item.text().split(':')[0]
        self.parent.set_dataset()
        self.parent.plotUpdate()
        # self.parent.InfoDialog.updateInfo()
        
    