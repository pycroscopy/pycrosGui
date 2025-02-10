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
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os as os
import numpy as np

class DataDialog(QWidget):
    def __init__(self, parent=None):
        super(DataDialog, self).__init__(parent)
    
        self.parent = parent
        
        layout = self.get_sidbar()
        self.setLayout(layout)    
        self.setWindowTitle("Datasets")

    def get_sidbar(self): 
        layout = QGridLayout()

        row = 0 
        label =  QLabel("Spectral Data")
        layout.addWidget(label,  row, 0)

        row += 1
        self.spectrum_list = QListWidget()
        self.spectrum_list.addItems(["None"])
        layout.addWidget(self.spectrum_list,  row, 0, 1, 3)
        self.spectrum_list.itemClicked.connect(self.plotUpdate)
        
        row += 1
        label =  QLabel("Survey Data")
        layout.addWidget(label,  row, 0)
        row += 1
        self.survey_list = QListWidget()
        self.survey_list.addItems(["None"])
        layout.addWidget(self.survey_list,  row, 0, 1, 3)
        self.survey_list.itemClicked.connect(self.plotUpdate)
        
        row += 1
        label =  QLabel("Image Data")
        layout.addWidget(label,  row, 0)
        row += 1
        self.image_list = QListWidget()
        self.image_list.addItems(["None"])
        layout.addWidget(self.image_list,  row, 0, 1, 3)
        self.image_list.itemClicked.connect(self.plotUpdate)
        
        row += 1
        label =  QLabel("Structures")
        layout.addWidget(label,  row, 0)
        row += 1
        self.structure_list = QListWidget()
        self.structure_list.addItems(["None"])
        layout.addWidget(self.structure_list,  row, 0, 1, 3)
        #self.structure_list.itemClicked.connect(self.plotUpdate)
        row += 1
        
        return layout

    def plotUpdate(self, item):
        
        if self.parent.dataset is not None:
            if self.parent.dataset.data_type.name == 'SPECTRUM':
                modifiers = QApplication.keyboardModifiers()
                if modifiers == Qt.ShiftModifier:
                    self.parent.add_spectrum.append(item.text().split(':')[0])
                    self.parent.plotUpdate()
                    return
        self.parent.add_spectrum = []
        self.parent.main = item.text().split(':')[0]
        self.parent.set_dataset()
        self.parent.plotUpdate()
        # self.parent.InfoDialog.updateInfo()
        
    