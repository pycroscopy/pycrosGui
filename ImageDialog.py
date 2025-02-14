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

import numpy as np
import sidpy
import scipy

from pyTEMlib import image_tools


class ImageDialog(QWidget):
    def __init__(self, parent=None):
        super(ImageDialog, self).__init__(parent)
    
        self.parent = parent
        self.set_energy = True
        layout = self.get_sidbar()
        self.setLayout(layout)    
        self.setWindowTitle("Image")

    def get_sidbar(self): 
        validfloat = QDoubleValidator()
        validint = QIntValidator()        
        
        layout = QGridLayout()
        row = 0 
        self.mainList = QComboBox(self)
        self.mainList.addItem("None")
        layout.addWidget(self.mainList,  row,0, 1, 3)
        layout.setColumnStretch(0, 3)  

        self.mainList.activated[str].connect(self.update_image_dataset)
        
        row += 1
        self.regButton = QPushButton()
        self.regButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.regButton.setText("Registration")
        layout.addWidget(self.regButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        # self.scaleButton.clicked.connect(self.cursor2energy_scale)
        
        row += 1
        self.rigid_regButton = QPushButton()
        self.rigid_regButton.setText("Rigid Reg.")
        self.rigid_regButton.setCheckable(True)
        layout.addWidget(self.rigid_regButton,  row, 0)
        #self.rigid_regButton.clicked.connect(self.rigid_registration)
        
        self.demon_regButton = QPushButton()
        self.demon_regButton.setText("Demon Reg.")
        self.demon_regButton.setCheckable(True)
        layout.addWidget(self.rigid_regButton,  row, 1)
        #self.demon_regButton.clicked.connect(self.demon_registration)
        
        self.all_regButton = QPushButton()
        self.all_regButton.setText("Both Reg.")
        self.all_regButton.setCheckable(True)
        layout.addWidget(self.all_regButton,  row, 1)
        #self.all_regButton.clicked.connect(self.all_registration)
        
        row += 1
        self.sumButton = QPushButton()
        self.sumButton.setText("Sum")
        self.sumButton.setCheckable(True)
        layout.addWidget(self.sumButton,  row, 0)
        self.sumButton.clicked.connect(self.sum_stack)
        
        self.averageButton = QPushButton()
        self.averageButton.setText("Average")
        self.averageButton.setCheckable(True)
        layout.addWidget(self.averageButton,  row, 1)
        self.averageButton.clicked.connect(self.average_stack)
        
        self.driftButton = QPushButton()
        self.driftButton.setText("Get Drift")
        self.driftButton.setCheckable(True)
        layout.addWidget(self.driftButton,  row, 2)
        #self.driftButton.clicked.connect(self.get_drift)
        
        row += 1
        self.processButton = QPushButton()
        self.processButton.setStyleSheet('QPushButton {background-color: blue; color: white;}')
        self.processButton.setText("Process")
        layout.addWidget(self.processButton,  row,0, 1, 3)
        layout.setColumnStretch(0, 3) 
        # self.scaleButton.clicked.connect(self.cursor2energy_scale)
        
        row += 1
        self.atom_sizeLabel = QLabel("atom_size")
        self.atom_sizeEdit = QLineEdit(" 100.0")
        self.atom_sizeEdit.setValidator(validfloat)
        #self.atom_sizeEdit.editingFinished.connect(self.set_energy_scale)
        self.atom_sizeUnit = QLabel("A")
        layout.addWidget(self.atom_sizeLabel,row,0)
        layout.addWidget(self.atom_sizeEdit,row,1)
        layout.addWidget(self.atom_sizeUnit,row,2)
        
        
        return layout
        
    def set_dataset(self):
        item_text = self.mainList.currentText()
        self.parent.main = item_text.split(':')[0]
        self.parent.datasets['_relationship']['image'] = self.parent.main
        self.parent.set
        self.update_sidebar()

    def update_sidebar(self):
        if '_relationship' not in self.parent.datasets:
            return
        image_list = ['None']
        image_index = 0

        if 'image' in self.parent.datasets['_relationship']:
            self.key = self.parent.datasets['_relationship']['image']
        else:
            self.key = 'None' 
            
        for index, key in enumerate(self.parent.datasets.keys()):
            if isinstance(self.parent.datasets[key], sidpy.Dataset):
                if 'IMAG' in self.parent.datasets[key].data_type.name:
                    image_list.append(f'{key}: {self.parent.datasets[key].title}')
                if key == self.key:
                    image_index = index + 1

        if image_index >len(image_list) - 1:
            image_index = len(image_list) - 1
        self.mainList.clear()
        for item in image_list:
            self.mainList.addItem(item)
        self.mainList.setCurrentIndex(image_index)
        
        self.update_image_dataset()
            
        if 'IMAG' in self.parent.dataset.data_type.name:
            dims = self.parent.dataset.get_dimensions_by_type(sidpy.DimensionType.SPATIAL, return_axis=True)
            if len(dims) <1:
                dims  = self.parent.dataset.get_dimensions_by_type(sidpy.DimensionType.RECIPROCAL, return_axis=True)
            x =dims[0]
            pixel_size_x = x[1] - x[0]
            self.atom_sizeEdit.setText(f'{pixel_size_x*4:.2f}')
            self.atom_sizeUnit.setText(x.units)
            self.atom_sizeLabel.setText('Atom size')    
        
            
        
    def update_image_dataset(self, value=0):
        self.key = self.mainList.currentText().split(':')[0]
        if self.key not in self.parent.datasets.keys():
            return
        if 'None' in self.key:
            return
        self.parent.main = self.key
        self.parent.set_dataset()
        self.dataset = self.parent.dataset
        self.parent.plotUpdate()
       
    def sum_stack(self, value=0):
        if self.dataset.data_type.name == 'IMAGE_STACK':
            dims = self.parent.dataset.get_dimensions_by_type(sidpy.DimensionType.TEMPORAL, return_axis=False)
            self.parent.datasets[f'Sum-{self.dataset.title}'] = self.parent.dataset.sum(axis=dims[0])
            self.parent.datasets[f'Sum-{self.dataset.title}'].data_type = 'image'
            self.parent.datasets['_relationship'][f'Sum-{self.parent.main}'] = f'Sum-{self.parent.dataset.title}'
            self.parent.datasets['_relationship']['image'] =f'Sum-{self.dataset.title}'
            self.update_sidebar()
           
            
    def average_stack(self, value=0):
        if self.parent.dataset.data_type.name == 'IMAGE_STACK':
            dims = self.parent.dataset.get_dimensions_by_type(sidpy.DimensionType.TEMPORAL, return_axis=False)
            self.parent.datasets[f'Average-{self.parent.dataset.title}'] = self.parent.dataset.mean(axis=dims[0])
            self.parent.datasets['_relationship'][f'Average-{self.parent.main}'] = f'Average-{self.parent.dataset.title}'
            self.parent.datasets[f'Average-{self.dataset.title}'].data_type = 'image'
            self.parent.datasets['_relationship']['image'] =f'Average-{self.dataset.title}'
            self.update_sidebar()
           
    
    def set_intensity_scale(self, checked):
        self.parent.intensity_scale = 1.0
        if checked:
            if 'experiment' in self.parent.dataset.metadata:
                if 'flux_ppm' in self.parent.dataset.metadata['experiment']:
                    if 'SPEC' in self.parent.dataset.data_type.name:
                       energy_scale = self.parent.dataset.get_spectral_dims(return_axis=True)[0]
                       atom_size = energy_scale[1]-energy_scale[0]
                    else:
                        atom_size = 1.0
                        
                    self.parent.intensity_scale = atom_size/self.parent.dataset.metadata['experiment']['flux_ppm']
        self.parent.plotUpdate()

    def get_shift(self,  value=0):
        if 'low_loss' in self.parent.datasets['_relationship']:
            low_loss = self.parent.datasets[self.parent.datasets['_relationship']['low_loss']]

            self.parent.datasets['shifted_low_loss']  = eels_tools.align_zero_loss(low_loss)
            self.parent.datasets['shifted_low_loss'].title = self.parent.dataset.title + '_shifted'
            self.parent.datasets['_relationship']['low_loss'] = 'shifted_low_loss'
            self.updateInfo()
           
        if 'low_loss' in self.parent.datasets['_relationship']:
            if 'zero_loss' in self.parent.datasets[self.parent.datasets['_relationship']['low_loss']].metadata:
                if 'shifted' in self.parent.datasets[self.parent.datasets['_relationship']['low_loss']].metadata['zero_loss'].keys():
                    self.set_shiftButton.setDisabled(False)
    
    def shift_spectrum(self,  value=0):
        shifts = self.parent.dataset.shape
        if 'low_loss' in self.parent.datasets['_relationship']:
            if 'zero_loss' in self.parent.datasets[self.parent.datasets['_relationship']['low_loss']].metadata:
                if 'shifted' in self.parent.datasets[self.parent.datasets['_relationship']['low_loss']].metadata['zero_loss'].keys():
                    shifts = self.parent.datasets[self.parent.datasets['_relationship']['low_loss']].metadata['zero_loss']['shifted']
                    shifts_new = shifts.copy()
                    if 'zero_loss' in self.parent.dataset.metadata:
                        if 'shifted' in self.parent.dataset.metadata['zero_loss'].keys():
                            shifts_new = shifts-self.parent.dataset.metadata['zero_loss']['shifted']
                    else:
                        self.parent.dataset.metadata['zero_loss'] = {}
                    
                    self.parent.dataset = eels_tools.shift_energy(self.parent.dataset, shifts_new)
                    self.parent.dataset.metadata['zero_loss']['shifted'] = shifts
                    self.parent.plotUpdate()         
   
        
    def OnExposeEnter(self):
        self.parent.dataset.metadata['experiment']['exposure_time'] = float(self.timeEdit.displayText())
       
    def OnCollEnter(self):
        self.parent.dataset.metadata['experiment']['collection_angle'] = float(self.collEdit.displayText())
       
    def OnConvEnter(self):
        self.parent.dataset.metadata['experiment']['convergence_angle']=float(self.convEdit.displayText())
        
    def OnE0Enter(self):
        self.parent.dataset.metadata['experiment']['acceleration_voltage'] = float(self.E0Edit.displayText()) * 1000.
       
    def OnConversionEnter(self):
        self.parent.dataset.metadata['experiment']['counts_conversion'] = float(self.conversionEdit.displayText())
       
    def OnFlux_ppmEnter(self):
        self.parent.dataset.metadata['experiment']['flux_ppm'] = float(self.flux_ppmEdit.displayText())
        
    def OnFluxEnter(self):
        flux = float(self.fluxEdit.displayText()) 
        self.parent.dataset.metadata['experiment']['flux'] = flux
        
        current = flux * (scipy.constants.e*1e12)
        self.VOAEdit.displayText(f"{current:.2f}")
        
    def OnVOAEnter(self):
        self.parent.dataset.metadata['experiment']['camera_current'] = float(self.VOAEdit.displayText()) 
        flux = float(self.VOAEdit.displayText())/(scipy.constants.e*1e12)
        self.fluxEdit.setText(f"{flux:.2f}")
        self.parent.dataset.metadata['experiment']['flux'] = flux